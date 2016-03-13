# -*-*- encoding: utf-8 -*-*-

import datetime
import re

from loc import gmaps

open_time_re = ur'OPEN\W+\b(\d\d?):(\d\d)\b|(\d\d?):(\d\d)\W*OPEN|(\d\d?):(\d\d)\s*～'
close_time_re = ur'CLOSE(?:\s*予定)?\W+\b(\d+):(\d\d)\b'
open_close_time_re = ur'(\d\d?):(\d\d)\s*[～\-]\s*(\d\d?):(\d\d)'


def _intall(lst):
    return [None if x is None else int(x) for x in lst]


def setup_location(venue, addresses, item):
    # TODO: needs caching
    if venue:
        item['location_name'] = venue
    if addresses:
        address = addresses[0]
        item['location_address'] = address
    else:
        address = None

    if venue and not address:
        # Let's look it up on Google...we probably need to delay this until we get to the appengine side!
        results = {'status': 'FAIL'}
        #results = gmaps.fetch_places_raw(query='%s, japan' % address)
        if results['status'] == 'ZERO_RESULTS':
            results = gmaps.fetch_places_raw(query=address)

        if results['status'] == 'OK':
            item['location_address'] = results['results'][0]['formatted_address']
            latlng = results['results'][0]['geometry']['location']
            item['latitude'] = latlng['lat']
            item['longitude'] = latlng['lng']


def parse_date_times(start_date, date_str):
    date_str = date_str.upper()
    open_time = None
    close_time = None

    open_match = re.search(open_time_re, date_str)
    if open_match:
        open_time = _intall(open_match.groups())
        # Keep trimming off groups of 2 until we find valid values
        while open_time[0] is None:
            open_time = open_time[2:]
        close_match = re.search(close_time_re, date_str)
        if close_match:
            close_time = _intall(close_match.groups())

    open_close_match = re.search(open_close_time_re, date_str)
    if open_close_match:
        open_close_time = _intall(open_close_match.groups())
        open_time = open_close_time[0:2]
        close_time = open_close_time[2:4]

    start_datetime = start_date
    if open_time:
        # We use timedelta instead of time, so that we can handle hours=24 or hours=25 as is sometimes used in Japan
        start_timedelta = datetime.timedelta(hours=open_time[0], minutes=open_time[1])
        start_datetime = datetime.datetime.combine(start_date, datetime.time()) + start_timedelta

    end_datetime = None
    if close_time:
        end_timedelta = datetime.timedelta(hours=close_time[0], minutes=close_time[1])
        end_datetime = datetime.datetime.combine(start_date, datetime.time()) + end_timedelta
        if end_datetime < start_datetime:
            end_datetime += datetime.timedelta(days=1)

    return start_datetime, end_datetime
