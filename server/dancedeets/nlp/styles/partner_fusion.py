# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any('modern jive', 'ceroc', 'leroc', 'le-roc')

FUSION = Any(
    'fusion',
    u'fusión?',
)

AMBIGUOUS_DANCE = Any(commutative_connected(FUSION, dance_keywords.EASY_DANCE),)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    @classmethod
    def finalize_class(cls, other_style_regexes):
        super(Classifier, cls).finalize_class(other_style_regexes)
        # Don't allow "dancehall / reggae fusion dance"
        cls.GOOD_BAD_PAIRINGS = [
            (FUSION, commutative_connected(FUSION, Any(dance_keywords.MUSIC, *other_style_regexes))),
        ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'PARTNER_FUSION'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'modern jive',
            'ceroc',
            'leroc',
            'le-roc',
            'fusion',
            'fusion dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
