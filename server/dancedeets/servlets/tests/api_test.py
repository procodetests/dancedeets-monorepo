import urllib

from webtest import TestApp
from webtest import utils

from dancedeets import fb_api
import main
from dancedeets.test_utils import fixtures
from dancedeets.test_utils import unittest
from dancedeets.users import users

app = TestApp(main.application)


class TestEvent(unittest.TestCase):
    def runTest(self):
        event = fixtures.create_event()
        result = app.get('/api/v1.0/events/%s' % event.fb_event_id)
        if 'success' in result.json and not result.json['success']:
            self.fail(result.json)
        self.assertEqual(result.json['id'], event.fb_event_id)


class TestAuth(unittest.TestCase):
    def runTest(self):
        fields_str = '%2C'.join(fb_api.OBJ_USER_FIELDS)
        url = '/v2.9/me?fields=%s' % fields_str

        me_uid = '701004'
        access_token = 'BlahToken'
        new_access_token = 'BlahToken2'
        fb_api.FBAPI.get_results = {
            'me': {
                'id': me_uid
            },
        }
        fb_api.FBAPI.results = {
            url: (200, {
                'id': me_uid,
                'name': 'Mike Lambert'
            }),
            '/v2.9/me/events?since=yesterday&fields=id,rsvp_status&limit=3000': (200, {}),
            '/v2.9/me/friends': (200, {}),
            '/v2.9/me/permissions': (200, {}),
            '/v2.9/debug_token?input_token=BlahToken': (200, {
                'data': {
                    'expires_at': 0
                }
            }),
            '/v2.9/debug_token?input_token=BlahToken2': (200, {
                'data': {
                    'expires_at': 0
                }
            }),
        }

        auth_request = {
            'access_token': access_token,
            'access_token_expires': '2014-12-12T12:00:00-0500',
            'location': 'New Location',
            'client': 'android',
        }
        print 1
        self.assertEqual(users.User.get_by_id(me_uid), None)
        result = app.post_json('/api/v1.0/auth', auth_request)
        print 2
        self.assertEqual(result.json, {'success': True})
        self.assertNotEqual(users.User.get_by_id(me_uid), None)
        self.assertEqual(users.User.get_by_id(me_uid).fb_access_token, access_token)
        print 3

        # Now again, but with fully-urlquoted string.
        # This time it will update the token, but not create a new user.
        old_dumps = utils.dumps
        try:
            utils.dumps = lambda *args, **kwargs: urllib.quote(old_dumps(*args, **kwargs))
            auth_request['access_token'] = new_access_token
            print 4
            result = app.post_json('/api/v1.0/auth', auth_request)
            print 5
            self.assertEqual(result.json, {'success': True})
        finally:
            utils.dumps = old_dumps

        self.assertNotEqual(users.User.get_by_id(me_uid), None)
        self.assertEqual(users.User.get_by_id(me_uid).fb_access_token, new_access_token)
