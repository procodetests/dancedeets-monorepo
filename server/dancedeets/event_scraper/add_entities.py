import logging

from dancedeets import event_types
from dancedeets import fb_api
from dancedeets.events import eventdata
from dancedeets.events import event_emails_sending
from dancedeets.events import event_locations
from dancedeets.events import event_updates
from dancedeets.pubsub import pubsub
from dancedeets.nlp import event_classifier
from dancedeets.util import deferred
from dancedeets.util import fb_events
from dancedeets.util import runtime
from . import potential_events
from . import thing_db


class AddEventException(Exception):
    pass


def add_update_web_event(json_body, allow_posting=True):
    event_id = eventdata.DBEvent.generate_id(json_body['namespace'], json_body['namespaced_id'])
    e = eventdata.DBEvent.get_or_insert(event_id)
    newly_created = (e.creating_method is None)
    e.creating_method = eventdata.CM_WEB_SCRAPE

    event_updates.update_and_save_web_events([(e, json_body)])

    post_pubsub = newly_created and allow_posting
    send_email = newly_created
    deferred.defer(after_add_event, e.id, None, send_email, post_pubsub)


def add_update_fb_event(
    fb_event,
    fbl,
    creating_uid=None,
    visible_to_fb_uids=None,
    remapped_address=None,
    override_address=None,
    creating_method=None,
    allow_posting=True,
    verticals=None,
):
    if not fb_events.is_public_ish(fb_event):
        raise AddEventException('Cannot add secret/closed events to dancedeets!')

    if remapped_address is not None:
        event_locations.update_remapped_address(fb_event, remapped_address)

    event_id = fb_event['info']['id']
    e = eventdata.DBEvent.get_or_insert(event_id)
    newly_created = (e.creating_method is None)
    if override_address is not None:
        e.address = override_address

    if e.creating_method is None:
        e.creating_method = creating_method or eventdata.CM_UNKNOWN
    # Allow an override if we get a user or admin taking a human action
    if creating_method in eventdata.ALL_CM_HUMAN_CREATED:
        e.creating_method = creating_method or e.creating_method
    # Don't override the original creating_fb_uid
    if not e.creating_fb_uid:
        #STR_ID_MIGRATE
        e.creating_fb_uid = long(creating_uid) if creating_uid else None
        if e.creating_fb_uid:
            user = fbl.get(fb_api.LookupUser, creating_uid)
            e.creating_name = user['profile']['name']

    if visible_to_fb_uids is None:
        if creating_uid is not None:
            visible_to_fb_uids = [creating_uid]
        else:
            visible_to_fb_uids = []
    e.visible_to_fb_uids = visible_to_fb_uids

    e.verticals = verticals or []

    try:
        fb_event_attending_maybe = fbl.get(fb_api.LookupEventAttendingMaybe, event_id)
    except fb_api.NoFetchedDataException as error:
        logging.warning('Error loading fb-event-attending-maybe in add_update_fb_event: %s', error)
        fb_event_attending_maybe = None

    # Updates and saves the event
    event_updates.update_and_save_fb_events([(e, fb_event, fb_event_attending_maybe)])

    post_pubsub = newly_created and allow_posting and event_types.should_show(e)

    # Trigger lookup requests (these will be refreshed later, but we want them populated here at least)
    fbl.request(fb_api.LookupEventWall, event_id)
    fbl.request(fb_api.LookupEventAttending, event_id)
    fbl.batch_fetch()

    fbl.clear_local_cache()
    send_email = newly_created and event_types.should_show(e)
    deferred.defer(after_add_event, e.id, fbl, send_email, post_pubsub)
    return e


def after_add_event(event_id, fbl, send_email, post_pubsub):
    logging.info("New event, publishing to twitter/facebook")
    if post_pubsub:
        pubsub.eventually_publish_event(event_id)
    if fbl:
        crawl_event_source(fbl, event_id)
    if send_email and not runtime.is_local_appengine():
        # This has to occur *after* the event sources have been crawled (and the sources' emails are saved)
        event_emails_sending.send_event_add_emails(event_id, should_send=True)


def crawl_event_source(fbl, event_id):
    logging.info('Crawling sources for event %s', event_id)
    fb_event = fbl.get(fb_api.LookupEvent, event_id)
    if fb_event['empty']:
        logging.error('No FB Event found: %s', event_id)
        return
    e = eventdata.DBEvent.get_by_id(fb_event['info']['id'])
    thing_db.create_sources_from_event(fbl, e)

    potential_event = potential_events.make_potential_event_without_source(e.fb_event_id)
    classified_event = event_classifier.get_classified_event(fb_event, potential_event.language)
    if potential_event:
        for source_id in potential_event.source_ids_only():
            s = thing_db.Source.get_by_key_name(source_id)
            if not s:
                logging.warning("Couldn't find source %s when updating event %s", source_id, e.fb_event_id)
                continue
            # TODO(lambert): doesn't handle the case of the match score increasing from <0 to >0 in the future
            if not classified_event.is_dance_event():
                s.num_false_negatives = (s.num_false_negatives or 0) + 1
            s.num_real_events = (s.num_real_events or 0) + 1
            s.put()
