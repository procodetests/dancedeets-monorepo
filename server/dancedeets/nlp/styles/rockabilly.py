# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.street import keywords
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'jive\W?bop',
    'jive\W?freestyle',
    commutative_connected(Any('barn'), keywords.DANCE),
)

AMBIGUOUS_DANCE = Any(
    'jive',
    'boogie\W?woogie',
    'rock\W?\W?(?:n|and|&|\+)\W?\W?roll\w*',
    'rockabilly',
    'r\Wn\Wr',
    'boogie',
    'boogie\w*',
    u'ロッカビリー',
    u'ブギウギ',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'ball',
        u'バール',
        'festival',
    )
    OTHER_DANCE = Any('modern jive',)
    GOOD_BAD_PAIRINGS = [
        (Any('jive'), Any('modern jive')),
    ]

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'ROCKABILLY'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'rockabilly',
            'jive',
            'boogie woogie',
            'rock n roll',
            'rock and roll',
            'rock n roll dance',
            'rock and roll dance',
            'r n r',
            'boogie',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(REAL_DANCE, AMBIGUOUS_DANCE)