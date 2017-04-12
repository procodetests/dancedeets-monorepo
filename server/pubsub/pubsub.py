# -*-*- encoding: utf-8 -*-*-

import datetime
import json
import logging
import re
import time

from google.appengine.ext import ndb

from events import eventdata
from util import taskqueue
from . import db
from . import event
from . import weekly

EVENT_PULL_QUEUE = 'event-publishing-pull-queue'

SHOULD_POST_EVENT_TO = {
    db.APP_FACEBOOK: event.should_post_event_to_account,
    db.APP_TWITTER: event.should_post_event_to_account,
    db.APP_FACEBOOK_WALL: event.should_post_on_event_wall,
}

POST_DATA = {
    'event': event.post_event,
    'weekly': weekly.facebook_weekly_post
}
def eventually_publish_event(event_id, token_nickname=None):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event.has_content():
        logging.info('Not publishing %s because it has no content.', db_event.id)
        return
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        logging.info('Not publishing %s because it is in the past.', db_event.id)
        return

    data = {
        'type': 'event',
        'event_id': event_id,
    }

    def should_post(auth_token):
        return _should_queue_event_for_posting(auth_token, db_event)
    return _eventually_publish_data(data, should_post, token_nickname)

def eventually_publish_city_key(city_key):
    data = {
        'type': 'weekly',
        'city': city_key,
    }
    def should_post(auth_token):
        return auth_token.application == db.APP_FACEBOOK_WEEKLY
    return _eventually_publish_data(data, should_post)

def _sanitize(x):
    return re.sub(r'[^a-zA-Z0-9_-]', '-', x)

def _get_type_and_data_names(data):
    data_type = data['type']
    new_data = data.copy()
    del new_data['type']
    data_rest = json.dumps(new_data, sort_keys=True)
    return _sanitize(data_type), _sanitize(data_rest)

def _eventually_publish_data(data, should_post, token_nickname=None):
    args = []
    if token_nickname:
        args.append(db.OAuthToken.token_nickname == token_nickname)
    oauth_tokens = db.OAuthToken.query(db.OAuthToken.valid_token == True, *args).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Evaluating token %s", token)
        if should_post(token):
            logging.info("Adding task for posting!")
            # Names are limited to r"^[a-zA-Z0-9_-]{1,500}$"
            time_add = int(time.time()) if token.allow_reposting else 0
            # "Event" here is a misnamer...but we leave it for now.

            datatype, extra = _get_type_and_data_names(data)
            name = 'Token_%s__%s__%s__TimeAdd_%s' % (token.queue_id(), datatype, extra, time_add)
            logging.info("Adding task with name %s", name)
            try:
                q.add(taskqueue.Task(name=name, payload=json.dumps(data), method='PULL', tag=token.queue_id()))
            except (taskqueue.TombstonedTaskError, taskqueue.TaskAlreadyExistsError):
                # Ignore publishing requests we've already decided to publish (multi-task concurrency)
                pass

def _should_queue_event_for_posting(auth_token, db_event):
    func = SHOULD_POST_EVENT_TO.get(auth_token.application)
    result = func(auth_token, db_event)
    if result:
        logging.info("Publishing event %s", db_event.id)
    return True

def pull_and_publish_event():
    oauth_tokens = db.OAuthToken.query(
        db.OAuthToken.valid_token == True,
        ndb.OR(
            db.OAuthToken.next_post_time < datetime.datetime.now(),
            db.OAuthToken.next_post_time == None
        )
    ).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Can post to OAuthToken: %s", token)
        tasks = q.lease_tasks_by_tag(120, 1, token.queue_id())
        logging.info("Fetching %d tasks with queue id %s", len(tasks), token.queue_id())
        if tasks:
            # Should only be one task
            if len(tasks) != 1:
                logging.error('Found too many tasks in our lease_tasks_by_tag: %s', len(tasks))
            task = tasks[0]
            # Backwards compatibility for items in the queue
            if '{' not in task.payload:
                data = {
                    'type': 'event',
                    'event_id': task.payload,
                }
            else:
                data = json.loads(task.payload)
            posted = _post_data_with_authtoken(data, token)
            q.delete_tasks(task)

            # Only mark it up for delay, if we actually posted...
            if posted:
                next_post_time = datetime.datetime.now() + datetime.timedelta(seconds=token.time_between_posts)
                token = token.key.get()
                token.next_post_time = next_post_time
                token.put()

def _post_data_with_authtoken(data, auth_token):
    try:
        func = POST_DATA[data['type']]
        return func(auth_token, data)
    except Exception as e:
        logging.exception("Post Exception: %s", e)
        # Just in case there's something failing-after-posting,
        # we don't want to trigger rapid-fire posts in a loop.
        return True

