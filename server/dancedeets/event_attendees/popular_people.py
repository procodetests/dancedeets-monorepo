import hashlib
import json
import logging
import re
import time

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.cloud import datastore

from dancedeets import app
from dancedeets import base_servlet
from dancedeets import event_types
from dancedeets.rankings import cities_db
from dancedeets.util import runtime
from . import popular_people_sqlite

TOP_N = 100

SUMMED_AREA = 'Summed-Area'
SUMMED_AREA_CITY_DELIM = '|||'


def is_summed_area(city):
    return city.startswith(SUMMED_AREA)


def get_summed_area_cities(city):
    if is_summed_area(city):
        match = re.search(r'\((.*)\)', city)
        if match:
            return match.group(1).split(SUMMED_AREA_CITY_DELIM)
        else:
            raise ValueError('Unknown Summed Area: %s' % city)
    else:
        return [city]


class PRDebugAttendee(ndb.Model):
    created_date = ndb.DateTimeProperty(auto_now=True)

    city = ndb.StringProperty()
    person_id = ndb.StringProperty()
    grouped_event_ids = ndb.JsonProperty()

    @staticmethod
    def generate_key(city, person_id):
        # TODO: sync with dataflow
        return '%s: %s' % (city, person_id)


class PRCityCategory(ndb.Model):
    # key = city + other things
    created_date = ndb.DateTimeProperty(auto_now=True)

    person_type = ndb.StringProperty()
    geoname_id = ndb.StringProperty()
    category = ndb.StringProperty()
    top_people_json = ndb.JsonProperty()
    # top_people_json is [['id: name', count], ...]


class PeopleRanking(object):
    def __init__(self, geoname_id, category, person_type, top_people_json):
        self.geoname_id = geoname_id
        self.category = category
        self.person_type = person_type
        self.top_people_json = top_people_json

    def name(self):
        return 'PeopleRanking(geoname=%s, category=%s, person_type=%s)' % (self.geoname_id, self.category, self.person_type)

    def __repr__(self):
        return 'PeopleRanking(%s, %s, %s,\n%s\n)' % (self.geoname_id, self.category, self.person_type, self.top_people_json)

    @property
    def human_category(self):
        return event_types.CATEGORY_LOOKUP.get(self.category)

    def worthy_top_people(self, person_index=10, cutoff=0.0):
        results = self._worthy_top_people(person_index, cutoff)
        return [('%s: %s' % (x['person_id'], x['person_name']), x['count']) for x in results]

    def _worthy_top_people(self, person_index, cutoff):
        #return self.top_people_json
        if cutoff > 0:
            cutoff = self.get_worthy_cutoff(person_index, cutoff)
            return [x for x in self.top_people_json if x[1] >= cutoff]
        else:
            return self.top_people_json

    def get_worthy_cutoff(self, person_index, cutoff):
        # If a scene doesn't have "enough people", then the top-person
        # will be drastically different relative to the remainder in the scene.
        # So let's filter people out to ensure they're close to the top-person.
        if self.person_type == 'ATTENDEE':
            minimum = 0.5
        elif self.person_type == 'ADMIN':
            minimum = 0.25
        else:
            logging.error('Unknown person type: %s', self.person_type)
        top_person = self.top_people_json[person_index]
        top_person_unique_events = top_person[1]
        return max([int(top_person_unique_events * cutoff), minimum])


def get_people_rankings_for_city_names(geoname_ids, attendees_only=False):
    start = time.time()
    pr_city_categories = get_people_rankings_for_city_names_sqlite(geoname_ids, attendees_only)
    category_list = ', '.join(sorted(set(x.category for x in pr_city_categories)))
    logging.info('Loading PRCityCategory took %0.3f seconds: %s', time.time() - start, category_list)

    results = []
    for city_category in pr_city_categories:
        results.append(
            PeopleRanking(city_category.geoname_id, city_category.category, city_category.person_type, city_category.top_people_json)
        )

    return results


def get_people_rankings_for_city_names_sqlite(geoname_ids, attendees_only):
    return popular_people_sqlite.get_people_rankings_for_city_names_sqlite(geoname_ids, attendees_only)


def get_people_rankings_for_city_names_datastore(geoname_ids, attendees_only):
    args = []
    if attendees_only:
        args = [PRCityCategory.person_type == 'ATTENDEE']
    return PRCityCategory.query(PRCityCategory.city.IN(geoname_ids), *args).fetch(100)


def get_people_rankings_for_city_names_dev_remote(geoname_ids, attendees_only):
    rankings = []
    client = datastore.Client('dancedeets-hrd')

    for city_name in geoname_ids:
        q = client.query(kind='PRCityCategory')
        q.add_filter('city', '=', city_name)
        if attendees_only:
            q.add_filter('person_type', '=', 'ATTENDEE')

        for result in q.fetch(100):
            ranking = PRCityCategory()
            ranking.key = ndb.Key('PRCityCategory', result.key.name)
            ranking.person_type = result['person_type']
            ranking.geoname_id = result['geoname_id']
            ranking.category = result['category']
            ranking.top_people_json = json.loads(result.get('top_people_json', '[]'))
            rankings.append(ranking)
    return rankings


def _get_geoname_ids_within(bounds):
    if bounds == None:
        return []
    logging.info('Looking up nearby cities to %s', bounds)
    included_cities = cities_db.get_contained_cities(bounds)
    logging.info('Found %s cities', len(included_cities))
    city_names = [city.geoname_id for city in included_cities]
    return city_names


def get_attendees_within(bounds, max_attendees):
    geoname_ids = _get_geoname_ids_within(bounds)
    logging.info('Loading PRCityCategory for top 10 cities: %s', geoname_ids)
    if not geoname_ids:
        return {}
    memcache_key = 'AttendeeCache: %s' % hashlib.md5('\n'.join(str(x) for x in geoname_ids).encode('utf-8')).hexdigest()
    memcache_result = memcache.get(memcache_key)
    if memcache_result:
        logging.info('Reading memcache key %s with value length: %s', memcache_key, len(memcache_result))
        result = json.loads(memcache_result)
    else:
        people_rankings = get_people_rankings_for_city_names(geoname_ids, attendees_only=True)
        logging.info('Loaded %s People Rankings', len(people_rankings))
        if runtime.is_local_appengine() and False:
            for x in people_rankings:
                logging.info(x.key)
                for person in x.worthy_top_people():
                    logging.info('  - %s' % person)
        groupings = combine_rankings(people_rankings, max_people=max_attendees)
        result = groupings.get('ATTENDEE', {})
        # Trim out the unnecessary names
        for category_city, people in result.iteritems():
            for person in people:
                del person['name']
        json_dump = json.dumps(result)
        try:
            logging.info('Writing memcache key %s with value length: %s', memcache_key, len(json_dump))
            memcache.set(memcache_key, json_dump, time=24 * 60 * 60)
        except ValueError:
            logging.warning('Error writing memcache key %s with value length: %s', memcache_key, len(json_dump))
            logging.warning('Tried to write: %s', json.dumps(result, indent=2))
    return result


def combine_rankings(rankings, max_people=0):
    groupings = {}
    cities = sorted(set(r.geoname_id for r in rankings))
    summed_area_key = '%s (%s)' % (SUMMED_AREA, SUMMED_AREA_CITY_DELIM.join(cities))
    for r in rankings:
        top_people = r.worthy_top_people()
        if not top_people:
            continue
        #logging.info(r.key)
        for key in (
            (summed_area_key, r.person_type, r.category),
            (r.geoname_id, r.person_type, r.category),
        ):
            # Make sure we use setdefault....we can have key repeats due to rankings from different cities
            groupings.setdefault(key, {})
            # Use this version below, and avoid the lookups
            people = groupings[key]
            people_list = top_people[:max_people] if max_people else top_people
            for person_name, count in people_list[:TOP_N]:
                if person_name in people:
                    people[person_name] += count
                else:
                    people[person_name] = count
    for key in groupings:
        city, person_type, category = key
        if person_type == 'ATTENDEE':
            limit = 0.5
        elif person_type == 'ADMIN':
            limit = 0.25
        else:
            logging.error('Unknown person type: %s', person_type)
        # Remove low/bad frequency data
        groupings[key] = dict(kv for kv in groupings[key].iteritems() if kv[1] >= limit)

    groupings = dict(kv for kv in groupings.iteritems() if len(kv[1]))

    final_groupings = {}
    for key in groupings:
        geoname_id, person_type, category = key
        secondary_key = '%s: %s' % (category, geoname_id)
        orig = groupings[key]
        dicts = []
        for name, count in orig.iteritems():
            split_name = name.split(': ', 1)
            dicts.append({
                'id': split_name[0],
                'name': split_name[1],
                'count': count,
            })
        if person_type not in final_groupings:
            final_groupings[person_type] = {}
        if secondary_key not in final_groupings[person_type]:
            final_groupings[person_type][secondary_key] = {}
        # Sort by count, then by name (for stable sorting)
        final_groupings[person_type][secondary_key] = sorted(dicts, key=lambda x: (-x['count'], x['id']))
    return final_groupings


@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # TODO: can we somehow trigger the Dataflow job?
        pass
