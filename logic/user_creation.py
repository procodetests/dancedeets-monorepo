import datetime
import logging
import urllib

from google.appengine.api import taskqueue

import fb_api
from events import users
from logic import backgrounder

def create_user_with_fbuser():
    pass

def create_user(access_token, access_token_expires, city, referer=None, client=None):
        # Build a cache-less lookup
        fbl = fb_api.FBLookup(None, access_token)
        fb_user = fbl.get(fb_api.LookupUser, 'me')
        fb_uid = fb_user['info']['id']

        fbl = fb_api.FBLookup(fb_uid, access_token)
        fb_user = fbl.get(fb_api.LookupUser, fb_uid)

        user = users.User(key_name=str(fb_uid))
        user.fb_access_token = access_token
        user.fb_access_token_expires = access_token_expires
        user.location = city
        
        # grab the cookie to figure out who referred this user
        logging.info("Referer was: %s", referer)
        if referer:
            user.inviting_fb_uid = int(referer)
        #TODO(lambert): use the client field, either storing the creating client, or storing all-clients-seen

        user.send_email = True
        user.distance = '50'
        user.distance_units = 'miles'
        user.min_attendees = 0

        user.creation_time = datetime.datetime.now()

        user.login_count = 1
        user.last_login_time = user.creation_time

        user.compute_derived_properties(fb_user)
        logging.info("Saving user with name %s", user.full_name)
        user.put()

        logging.info("Requesting background load of user's friends")
        # Must occur after User is put with fb_access_token
        taskqueue.add(method='GET', url='/tasks/track_newuser_friends?' + urllib.urlencode({'user_id': fb_uid}), queue_name='slow-queue')
        # Now load their potential events, to make "add event page" faster (and let us process/scrape their events)
        #fb_reloading.load_potential_events_for_user_ids(fbl, [fb_uid])
        backgrounder.load_potential_events_for_users([fb_uid])

