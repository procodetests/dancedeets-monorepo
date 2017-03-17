# -*-*- encoding: utf-8 -*-*-

import time

import base_servlet
import app
import logging
import fb_api
from util import mr
from . import thing_db
from . import potential_events
from . import event_pipeline

class LookupSearchEvents(fb_api.LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-search-events')

    @classmethod
    def get_lookups(cls, query):
        return [
            ('results', cls.url('search', type='event', q=query, fields=['id', 'name'], limit=1000)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fb_api.USERLESS_UID, object_id, 'OBJ_SEARCH')

def two(w):
    a, b = w.split(' ')
    keywords = [
        '%s %s' % (a, b),
        '%s%s' % (a, b),
    ]
    return keywords

def search_fb(fbl):
    obvious_keywords = ([
        'bboy', 'bboys', 'bboying', 'bgirl', 'bgirls', 'bgirling', 'breakdance', 'breakdancing', 'breakdancers',
        'hiphop', 'hip hop', 'new style',
        'house dance', 'house danse',
        'poppers', 'poplock',
        'tutting', 'bopping', 'boppers',
        'lockers', 'locking',
        'waacking', 'waackers', 'waack', 'whacking', 'whackers',
        'bebop', 'jazzrock', 'jazz rock', 'jazz-rock',
        'dancehall', 'ragga jam',
        'krump', 'krumperz', 'krumping',
        'street jazz', 'street-jazz', 'streetjazz',
        'house dance',
        'house danse',
        'hiphop dance',
        'hip hop dance',
        'hiphop danse',
        'hip hop danse',
        'tous style',
        'urban dance',
        'afro house',
        'urban style',
        'turfing',
        'baile urbano',
        'soul dance',
        'footwork',
        '7 to smoke',
        u'ストリートダンス',
        u'ブレックダンス',
        'cypher',
    ] + two('street dance')
      + two('electro dance')
      + two('lite feet')
    )
    too_popular_keywords = ([
        'breaking',
        # 'house workshop'....finds auto-add events we don't want labelled as house or as dance events
        # so we don't want to list it here..
        #'waving',
        #'boogaloo',
        # 'uk jazz', 'uk jazz', 'jazz fusion',
        # 'flexing',
        'lock',
        'popping',
        'dance', 'choreo', 'choreography',
        #'kpop', 'k pop',
        'vogue',
        'all styles',
        'freestyle',
    ] + two('hip hop')
      + two('new style')
      + two('all styles')
    )
    event_types = [
        'session',

        'workshop',
        'class', 'taller', 'stage',

        'battle',
        'jam',
        'competition', 'competición', 'competencia',
        'contest', 'concours',
        'tournaments',

        'performance', 'spectacle',

        'audition', 'audiciones',
        'bonnie and clyde',
    ]
    all_keywords = obvious_keywords[:]
    for x in too_popular_keywords:
        for y in event_types:
            all_keywords.append('%s %s' % (x, y))

    logging.info('Looking up %s search queries', len(all_keywords))

    all_ids = set()
    for query in all_keywords:
        search_results = fbl.get(LookupSearchEvents, query, allow_cache=False)
        ids = [x['id'] for x in search_results['results']['data']]
        all_ids.update(ids)
        logging.info('Keyword %r returned %s results:', query, len(ids))
        # Debug code
        for x in search_results['results']['data']:
            logging.info('Found %s: %s', x['id'], x.get('name'))
        time.sleep(3)

    return
    # Run these all_ids in a queue of some sort...to process later, in groups?
    discovered_list = [potential_events.DiscoveredEvent(id, None, thing_db.FIELD_SEARCH) for id in sorted(all_ids)]

    event_pipeline.process_discovered_events(fbl, discovered_list)



@app.route('/tools/search_fb_for_events')
class ByBaseHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        search_fb(self.fbl)
