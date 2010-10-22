#!/usr/bin/env python

import datetime
import logging
import re
import sys
import urllib

from google.appengine.ext.webapp import RequestHandler
from django.utils import simplejson

from events import users
import facebook
import fb_api
import locations
import template
from util import text

#TODO(lambert): show event info, queries without login?? P2

class _ValidationError(Exception):
    pass

FACEBOOK_CONFIG = None

class BaseRequestHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseRequestHandler, self).__init__(*args, **kwargs)

    def initialize(self, request, response):
        super(BaseRequestHandler, self).initialize(request, response)
        params = dict(next=self.request.url)
        referer = self.request.get('referer')
        if referer:
            params['referer'] = referer
        login_url = 'login?%s' % urllib.urlencode(params)
        args = facebook.get_user_from_cookie(request.cookies, FACEBOOK_CONFIG['api_key'], FACEBOOK_CONFIG['secret_key'])
        if args:
            self.fb_uid = int(args['uid'])
            self.fb_graph = facebook.GraphAPI(args['access_token'])
            self.user = users.User.get_cached(self.fb_uid)
            logging.info("Logged in uid %s", self.fb_uid)
        else:
            self.fb_uid = None
            self.fb_graph = facebook.GraphAPI(None)
            self.user = None
        if self.requires_login() and (not self.fb_uid or not self.user):
            self.redirect(login_url)
            return True
        if self.fb_uid: # if they have a fb_uid, let's do lookups on that behalf (does not require a user)
            self.batch_lookup = fb_api.CommonBatchLookup(self.fb_uid, self.fb_graph)
            # Always look up the user's information for every page view...?
            self.batch_lookup.lookup_user(self.fb_uid)
        else:
            self.batch_lookup = fb_api.CommonBatchLookup(None, self.fb_graph)
        self.display = {}
        self._errors = []
        # We can safely do this since there are very few ways others can modify self._errors
        #TODO(lambert): print errors in the template, and make sure to $format_html them
        self.display['errors'] = self._errors
        # functions, add these to some base display setup
        self.display['format_html'] = text.format_html
        self.display['format_js'] = text.format_js
        if self.user:
            self.display['date_human_format'] = lambda x: users.date_human_format(x, user=self.user)
            self.display['messages'] = self.user.get_and_purge_messages()
        else:
            self.display['date_human_format'] = users.date_human_format
            self.display['login_url'] = login_url
        self.display['date_format'] = text.date_format
        self.display['format'] = text.format
        self.display['request'] = request
        self.display['api_key'] = FACEBOOK_CONFIG['api_key']
        self.display['prod_mode'] = self.prod_mode
        return False

    def requires_login(self):
        return True

    def add_error(self, error):
        self._errors.append(error)

    def fatal_error(self, error):
        self.add_error(error)
        self.errors_are_fatal()

    def errors_are_fatal(self):
        if self._errors:
            raise _ValidationError(self._errors)

    def handle_exception(self, e, debug):
        handled = False
        if isinstance(e, _ValidationError):
            handled = self.handle_error_response(self._errors)
        if not handled:
            super(BaseRequestHandler, self).handle_exception(e, debug)

    def handle_error_response(self, errors):
        if self.request.method == 'POST':
            self.get() # call get response handler if we have post validation errors
            return True
        else:
            return False # let exception handling code operate normally

    def write_json_response(self, arg):
        self.response.out.write(simplejson.dumps(arg))

    def render_template(self, name):
        if self.fb_uid: # show fb user if we're logged in. we only need fb_uid to get a fb_user
            self.display['fb_user'] = self.current_user()
        else:
            self.display['fb_user'] = None
        rendered = template.render_template(name, self.display)
        self.response.out.write(rendered)

    def current_user(self):
        return self.batch_lookup.data_for_user(self.fb_uid)

    def finish_preload(self):
        self.batch_lookup.finish_loading()

