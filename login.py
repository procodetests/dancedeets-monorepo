#!/usr/bin/env python

import datetime
import urllib

import base_servlet
from events import users
from google.appengine.api.labs import taskqueue

        
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        next = self.request.get('next') or '/'
        # once they have a login token, do initial signin stuff, and redirect them
        if self.fb_uid:
            #TODO(lambert): do a transaction around this?
            user = users.get_user(self.fb_uid)
            if not user.fb_access_token: # brand new user!
                user.creation_time = datetime.datetime.now()
                user_friends = users.UserFriendsAtSignup()
                user_friends.fb_uid = self.fb_uid
                user_friends.put()
                taskqueue.add(url='/tasks/track_newuser_friends', params={'user_id': self.fb_uid})
            user.fb_access_token = self.fb_graph.access_token
            user.put()
            self.redirect(next)
        else:
            # Explicitly do not preload anything from facebook for this servlet
            # self.finish_preload()
            self.display['next'] = '/login?%s' % urllib.urlencode({'next': next})
            self.display['api_key'] = base_servlet.FACEBOOK_CONFIG['api_key']
            self.render_template('login')

