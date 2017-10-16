import json
import urllib


def fetch_bboy_lite(namespace, url):
    url = url
    data = urllib.urlopen(url).read()
    json_data = json.loads(data)['data']

    item = {}
    item['country'] = 'CN'
    item['namespace'] = namespace
    item['namespaced_id'] = json_data['id']
    item['name'] = json_data['title']

    item['description'] = 'Phone Number: %(phone)s\n\n%(contents)s' % json_data
    item['photo'] = json_data['pic']

    # Save the raw data, for use later if desired
    item['raw'] = json_data
    # TODO: handle all images in json_data['jam_gallery'], so they can be proxied correctly

    item['start_time'] = json_data['startDate']
    item['end_time'] = json_data['endDate']

    item['latitude'], item['longitude'] = json_data['location'].split(',')
    item['location_address'] = json_data['address']

    # Only return our item if it has 'good' data
    if item['name'] and item['start_time'] and item['photo']:
        return item
    else:
        return None


def reload_bboy_lite_jam(web_event):
    item = fetch_bboy_lite('bboylite-jam', 'http://jamyo.jamyooo.com/Lite/Jam/jam_detail?id=%s' % web_event.namespaced_id)
    return item or web_event.web_event


def reload_bboy_lite_course(web_event):
    item = fetch_bboy_lite('bboylite-course', 'https://jamyo.jamyooo.com/Lite/Course/course_details?course_id=%s' % web_event.namespaced_id)
    return item or web_event.web_event
