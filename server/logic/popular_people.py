import logging

from google.appengine.ext import ndb
from mapreduce import mapreduce_pipeline
from mapreduce import operation

import app
import base_servlet
import event_types
import fb_api
from util import fb_mapreduce

"""
MAP
for each event:
    for each nearby city of event:
        for each attendee of event:
            export (cityname, attendee): event_id

REDDUCE:
foreach (cityname, attendee): event_ids:
    export cityname: (attendee, len(event_ids)1)


foreach cityname: (attendee, event_count):
    get top_N(attendee by event_count) in cityname:
        export top_N
"""

class PeopleRanking(ndb.Model):
    person_type = ndb.StringProperty()
    city = ndb.StringProperty()
    category = ndb.StringProperty()
    top_people = ndb.StringProperty(repeated=True, indexed=False)

STYLES_SET = set(x.index_name for x in event_types.STYLES)

def track_person(person_type, db_event, person):
    person_name = ('%s: %s' % (person['id'], person.get('name'))).encode('utf-8')
    for city in db_event.nearby_city_names:
        key = '%s: %s: %s' % (person_type, '', city)
        yield (key, person_name)
        for category in STYLES_SET.intersection(db_event.auto_categories):
            key = '%s: %s: %s' % (person_type, category, city)
            yield (key, person_name)
            logging.info('%s', (key, person_name))

BATCH_SIZE = 20
def output_people(db_events):
    db_events = [x for x in db_events if x.is_fb_event]

    fbl = fb_mapreduce.get_fblookup()
    fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()

    for db_event in db_events:
        try:
            fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, db_event.id)
        except fb_api.NoFetchedDataException:
            logging.warning('No attending found for %s', db_event.id)
            continue
        if fb_event_attending['empty']:
            continue

        for admin in db_event.admins:
            for y in track_person('ADMIN', db_event, admin):
                yield y
        for attendee in fb_event_attending['attending']['data']:
            for y in track_person('ATTENDEE', db_event, attendee):
                yield y

def reduce_popular_people(type_city_category, people):
    person_type, category, city = type_city_category.split(': ', 2)
    counts = {}
    for person in people:
        if person in counts:
            counts[person] += 1
        else:
            counts[person] = 1
    sorted_counts = sorted(counts.items(), key=lambda kv: -kv[1])

    # Yes, key is the same as type_city_category above.
    # But we're declaring our key explicitly, here.
    key = '%s: %s: %s' % (person_type, city, category)
    ranking = PeopleRanking.get_or_insert(key)
    ranking.person_type = person_type
    ranking.city = city
    ranking.category = category
    ranking.top_people = ['%s: %s' % kv for kv in sorted_counts[:20]]
    yield operation.db.Put(ranking)

def mr_popular_people_per_city(fbl):
    mapper_params = {
        'entity_kind': 'events.eventdata.DBEvent',
        'handle_batch_size': BATCH_SIZE,
    }
    mapper_params.update(fb_mapreduce.get_fblookup_params(fbl, randomize_tokens=True))
    mrp = mapreduce_pipeline.MapreducePipeline(
        'popular_people',
        'logic.popular_people.output_people',
        'logic.popular_people.reduce_popular_people',
        'mapreduce.input_readers.DatastoreInputReader',
        'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        mapper_params=mapper_params,
        reducer_params={
            'output_writer': {
                'mime_type': 'text/plain',
                'bucket_name': 'dancedeets-hrd.appspot.com',
            },
        },
        shards=8,
    )
    mrp.start()
    return mrp

@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_popular_people_per_city(self.fbl)
