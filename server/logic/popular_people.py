import json
import logging

from google.appengine.ext import ndb

import app
import base_servlet
import event_types
from loc import math
from rankings import cities
from util import runtime

TOP_N = 100

class PeopleRanking(ndb.Model):
    person_type = ndb.StringProperty()
    city = ndb.StringProperty()
    category = ndb.StringProperty()
    created_date = ndb.DateTimeProperty(auto_now=True)
    top_people_json = ndb.JsonProperty()
    # top_people_json is [['id: name', count], ...]

    @property
    def human_category(self):
        # '' represents 'Overall'
        return event_types.CATEGORY_LOOKUP.get(self.category, '')

    def worthy_top_people(self, person_index=10, cutoff=0.5):
        return self.top_people_json
        cutoff = self.get_worthy_cutoff(person_index, cutoff)
        return [x for x in self.top_people_json if x[1] >= cutoff]

    def get_worthy_cutoff(self, person_index, cutoff):
        # If a scene doesn't have "enough people", then the top-person
        # will be drastically different relative to the remainder in the scene.
        # So let's filter people out to ensure they're close to the top-person.
        if self.person_type == 'ATTENDEE':
            minimum = 3
        elif self.person_type == 'ADMIN':
            minimum = 2
        else:
            logging.error('Unknown person type: %s', self.person_type)
        top_person = self.top_people_json[person_index]
        top_person_unique_events = top_person[1]
        return max([int(top_person_unique_events * cutoff), minimum])

STYLES_SET = set(x.index_name for x in event_types.STYLES)

def get_people_rankings_for_city_names(city_names, attendees_only=False):
    if runtime.is_local_appengine():
        people_rankings = load_from_dev(city_names, attendees_only=attendees_only)
    else:
        args = []
        if attendees_only:
            args = [PeopleRanking.person_type=='ATTENDEE']
        people_rankings = PeopleRanking.query(
            PeopleRanking.city.IN(city_names),
            *args
        )
    return people_rankings

def load_from_dev(city_names, attendees_only):
    from google.cloud import datastore

    rankings = []
    client = datastore.Client()

    for city_name in city_names:
        q = client.query(kind='PeopleRanking')
        q.add_filter('city', '=', city_name)
        if attendees_only:
            q.add_filter('person_type', '=', 'ATTENDEE')

        for result in q.fetch(100):
            ranking = PeopleRanking()
            ranking.key = ndb.Key('PeopleRanking', result.key.name)
            ranking.person_type = result['person_type']
            ranking.city = result['city']
            ranking.category = result['category']
            ranking.top_people_json = json.loads(result.get('top_people_json', '[]'))
            rankings.append(ranking)
    return rankings

def _get_city_names_within(bounds):
    if bounds == None:
        return []
    logging.info('Looking up nearby cities to %s', bounds)
    included_cities = cities.get_nearby_cities(bounds, only_populated=True)
    logging.info('Found %s cities', len(included_cities))
    biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
    city_names = [city.display_name() for city in biggest_cities]
    return city_names

def get_attendees_within(bounds):
    city_names = _get_city_names_within(bounds)
    logging.info('Loading PeopleRanking for top 10 cities: %s', city_names)
    if not city_names:
        return {}
    try:
        people_rankings = get_people_rankings_for_city_names(city_names, attendees_only=True)
        logging.info('Loaded People Rankings')
        if runtime.is_local_appengine():
            for x in people_rankings:
                logging.info(x.key)
                for person in x.worthy_top_people():
                    logging.info('  - %s' % person)
        groupings = combine_rankings(people_rankings)
    except:
        logging.exception('Error creating combined people rankings')
        return {}
    return groupings.get('ATTENDEE', {})

def combine_rankings(rankings):
    groupings = {}
    for r in rankings:
        top_people = r.worthy_top_people()
        if not top_people:
            continue
        #logging.info(r.key)
        key = (r.person_type, r.human_category)
        # Make sure we use setdefault....we can have key repeats due to rankings from different cities
        groupings.setdefault(key, {})
        # Use this version below, and avoid the lookups
        people = groupings[key]
        for person_name, count in top_people:
            if person_name in people:
                people[person_name] += count
            else:
                people[person_name] = count
    for key in groupings:
        person_type, category = key
        if person_type == 'ATTENDEE':
            limit = 3
        elif person_type == 'ADMIN':
            limit = 2
        else:
            logging.error('Unknown person type: %s', person_type)
        # Remove low/bad frequency data
        groupings[key] = dict(kv for kv in groupings[key].iteritems() if kv[1] >= limit)

    groupings = dict(kv for kv in groupings.iteritems() if len(kv[1]))

    final_groupings = {}
    for key in groupings:
        person_type, category = key
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
        if category not in final_groupings[person_type]:
            final_groupings[person_type][category] = {}
        final_groupings[person_type][category] = sorted(dicts, key=lambda x: -x['count'])
    return final_groupings

@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # TODO: can we somehow trigger the Dataflow job?
        pass
