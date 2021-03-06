import logging

from dancedeets import fb_api
from dancedeets import app
from dancedeets import base_servlet
from dancedeets.nlp import event_classifier
from dancedeets.test_utils import classifier_util
from dancedeets.test_utils import unittest

# TODO: Ensure our loading/changing test_data files doesn't cause the server to restart. Move test_data outside the watch dirs?
@app.route('/tests/nlp')
class TestNlpHandler(base_servlet.BaseRequestHandler):
    def get(self):
        from dancedeets.nlp.soulline.tests import classifier_test

        tb = classifier_test.TestSoulLine()
        tb.fbl = fb_api.FBLookup("dummyid", unittest.get_local_access_token_for_testing())

        event_runs = []

        good_ids = set(classifier_test.GOOD_IDS)

        all_ids = classifier_test.GOOD_IDS + classifier_test.BAD_IDS
        for event_id in all_ids:
            fb_event = tb.get_event(event_id)
            classified_event = event_classifier.get_classified_event(fb_event)
            data = classifier_test.FUNC(classified_event)
            event_runs.append({
                'id': event_id,
                'event': fb_event,
                'desired_result': event_id in good_ids,
                'result': bool(data[0]),
                'result_string': data[0],
                'reasons': data[1],
            })

        self.display['false_negatives'] = len([x for x in event_runs if not x['result'] and x['desired_result']])
        self.display['false_positives'] = len([x for x in event_runs if x['result'] and not x['desired_result']])
        self.display['vertical'] = 'soul line'
        self.display['event_runs'] = event_runs
        self.render_template('test_nlp_results')
