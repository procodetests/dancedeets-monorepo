import datetime
import logging

from events import eventdata
from util import fb_events
from .facebook import event as facebook_event
from .twitter import event as twitter_event
from . import db

def should_post_event_to_account(auth_token, db_event):
    geocode = db_event.get_geocode()
    if not geocode:
        # Don't post events without a location. It's too confusing...
        return False
    event_country = geocode.country()
    if auth_token.country_filters and event_country not in auth_token.country_filters:
        logging.info("Skipping event due to country filters")
        return False
    return True

def should_post_on_event_wall(auth_token, db_event):
    if not should_post_event_to_account(auth_token, db_event):
        return False
    # Additional filtering for FB Wall postings, since they are heavily-rate-limited by FB.
    if not db_event.is_fb_event:
        logging.info("Event is not FB event")
        return False
    if db_event.is_page_owned:
        logging.info("Event is not owned by page")
        return False
    if not db_event.public:
        logging.info("Event is not public")
        return False
    if db_event.attendee_count < 20:
        logging.warning("Skipping event due to <20 attendees: %s", db_event.attendee_count)
        return False
    if db_event.attendee_count > 600:
        logging.warning("Skipping event due to 600+ attendees: %s", db_event.attendee_count)
        return False
    invited = fb_events.get_all_members_count(db_event.fb_event)
    if invited < 200:
        logging.warning("Skipping event due to <200 invitees: %s", invited)
        return False
    if invited > 2000:
        logging.warning("Skipping event due to 2000+ invitees: %s", invited)
        return False


def post_event(auth_token, data):
    event_id = data['event_id']
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if _should_still_post_about_event(auth_token, db_event):
        return _post_event(auth_token, db_event)
    else:
        return False

def _should_still_post_about_event(auth_token, db_event):
    if not db_event:
        logging.warning("Failed to post event: %s, dbevent deleted in dancedeets", db_event)
        return False
    if not db_event.has_content():
        logging.warning("Failed to post event: %s, due to %s", db_event.id, db_event.empty_reason)
        return False
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        logging.info('Not publishing %s because it is in the past.', db_event.id)
        return False
    return True

def _post_event(auth_token, db_event):
    if auth_token.application == db.APP_TWITTER:
        twitter_event.twitter_post(auth_token, db_event)
    elif auth_token.application == db.APP_FACEBOOK:
        result = facebook_event.facebook_post(auth_token, db_event)
        if 'error' in result:
            if result.get('code') == 368 and result.get('error_subcode') == 1390008:
                logging.error('We are posting too fast to the facebook wall, so wait a day and try again later')
                next_post_time = datetime.datetime.now() + datetime.timedelta(days=1)
                auth_token = auth_token.key.get()
                auth_token.next_post_time = next_post_time
                # And space things out a tiny bit more!
                auth_token.time_between_posts += 1
                auth_token.put()
                return False
            logging.error("Facebook Post Error: %r", result)
        else:
            logging.info("Facebook result was %r", result)
    elif auth_token.application == db.APP_FACEBOOK_WALL:
        result = facebook_event.post_on_event_wall(db_event)
        if result:
            if 'error' in result:
                logging.error("Facebook WallPost Error: %r", result)
            else:
                logging.info("Facebook result was %r", result)
    else:
        logging.error("Unknown application for OAuthToken: %s", auth_token.application)
        return False
    return True
