import logging

import fb_api

from events import eventdata
from events import event_locations
from logic import popular_people
from nlp import event_auto_classifier
from nlp import event_classifier
from util import fb_mapreduce
from util import mr
from . import add_entities
from . import potential_events


def is_good_event_by_text(fb_event):
    classified_event = event_classifier.classified_event_from_fb_event(fb_event)
    classified_event.classify()
    auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
    return classified_event, auto_add_result

def is_good_event_by_attendees(fbl, pe, fb_event):
    try:
        fb_event_attending = fbl.get(fb_api.LookupEventAttending, pe.fb_event_id)
    except fb_api.NoFetchedDataException:
        logging.info('Event %s could not fetch event attendees, aborting.', pe.fb_event_id)
        return False
    if fb_event_attending['empty']:
        logging.info('Event %s has no attendees, skipping attendee-based classification.', pe.fb_event_id)
        return False

    event_attendee_ids = [attendee['id'] for attendee in fb_event_attending['attending']['data']]
    if not event_attendee_ids:
        return False

    location_info = event_locations.LocationInfo(fb_event)
    dance_attendee_ids = popular_people.get_attendee_ids_near(location_info)

    intersection_ids = set(event_attendee_ids).intersection(dance_attendee_ids)
    num_intersection = len(intersection_ids)
    fraction_known = 100.0 * num_intersection / len(event_attendee_ids)

    logging.info('Attendee-Detection: Event %s has %s ids, intersection is %s ids (%.0f%%)', pe.fb_event_id, len(event_attendee_ids), num_intersection, fraction_known)

    if (fraction_known > 5 and num_intersection > 1) or num_intersection > 3:
        logging.info('Attendee-Detection: Event %s has an attendee-based classifier result!', pe.fb_event_id)
        return True
    else:
        return False

def classify_events(fbl, pe_list, fb_list):
    results = []
    for pe, fb_event in zip(pe_list, fb_list):
        if fb_event and fb_event['empty']:
            fb_event = None

        # Get these past events out of the way, saved, then continue.
        # Next time through this mapreduce, we shouldn't need to process them.
        if pe.set_past_event(fb_event):
            pe.put()
        if not fb_event:
            continue

        # Don't process events we've already looked at, or don't need to look at.
        # This doesn't happen with the mapreduce that pre-filters them out,
        # but it does happen when we scrape users potential events and throw them all in here.
        if not pe.should_look_at or pe.looked_at:
            continue

        classified_event, auto_add_result = is_good_event_by_text(fb_event)
        good_event = False
        if auto_add_result and auto_add_result[0]:
            good_event = auto_add_result[0]
            method = eventdata.CM_AUTO
        else:
            good_event = is_good_event_by_attendees(fbl, pe, fb_event)
            method = eventdata.CM_AUTO_ATTENDEE
        if good_event:
            logging.info("Found event %s, looking up location", pe.fb_event_id)
            location_info = event_locations.LocationInfo(fb_event)
            result = '+%s\n' % '\t'.join(unicode(x) for x in (pe.fb_event_id, True, location_info.final_city, location_info.final_city is not None, location_info.fb_address, fb_event['info'].get('name', '')))
            try:
                logging.info('VTFI %s: Adding event %s, due to pe-invite-ids: %s', pe.fb_event_id, pe.fb_event_id, pe.get_invite_uids())
                add_entities.add_update_event(fb_event, fbl, visible_to_fb_uids=pe.get_invite_uids(), creating_method=method)
                pe2 = potential_events.PotentialEvent.get_by_key_name(pe.fb_event_id)
                pe2.looked_at = True
                pe2.auto_looked_at = True
                pe2.put()
                # TODO(lambert): handle un-add-able events differently
                results.append(result)
                mr.increment('auto-added-dance-events')
            except fb_api.NoFetchedDataException as e:
                logging.error("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
            except add_entities.AddEventException as e:
                logging.warning("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
        auto_notadd_result = event_auto_classifier.is_auto_notadd_event(classified_event, auto_add_result=auto_add_result)
        if auto_notadd_result[0]:
            pe2 = potential_events.PotentialEvent.get_by_key_name(pe.fb_event_id)
            pe2.looked_at = True
            pe2.auto_looked_at = True
            pe2.put()
            result = '-%s\n' % '\t'.join(unicode(x) for x in (pe.fb_event_id, fb_event['info'].get('name', '')))
            results.append(result)
            mr.increment('auto-notadded-dance-events')
    return results


def classify_events_with_yield(fbl, pe_list):
    assert fbl.allow_cache
    fb_list = fbl.get_multi(fb_api.LookupEvent, [x.fb_event_id for x in pe_list], allow_fail=True)
    # DISABLE_ATTENDING
    results = classify_events(fbl, pe_list, fb_list)
    yield ''.join(results).encode('utf-8')

map_classify_events = fb_mapreduce.mr_wrap(classify_events_with_yield)


def mr_classify_potential_events(fbl, past_event):
    filters = [('looked_at', '=', None), ('should_look_at', '=', True)]
    if past_event is not None:
        filters.append(('past_event', '=', past_event))
    fb_mapreduce.start_map(
        fbl,
        'Auto-Add Events',
        'event_scraper.auto_add.map_classify_events',
        'event_scraper.potential_events.PotentialEvent',
        filters=filters,
        handle_batch_size=20,
        queue='fast-queue',
        output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        output_writer={
            'mime_type': 'text/plain',
            'bucket_name': 'dancedeets-hrd.appspot.com',
        },
    )
