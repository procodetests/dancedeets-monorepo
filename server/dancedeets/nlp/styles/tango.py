# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import ballroom_keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

ARGENTINE = Any(
    u'argent[iy]\w*',
    u'αργεντίνικο ταγκό',  # greek
    u'аргентин\w*',  # russian, macedonian
    u'аргентинский',
    u'ארגנטינאי',  # hebrew
    u'อาร์เจนตินา',  # thai
    u'アルゼンチン',
    u'阿根廷',
    u'아르헨티나',
)

TANGO = Any(u'tango\w+', *ballroom_keywords.TANGO)

MILONGA = Any(
    u'milongas?',
    u'милонга',  # macedonian, russian
    u'מילונגה',  # hebrew
    u'ミロンガ',
    u'舞会',  # chinese simplified
    u'舞會',  # chinese traditional
    u'밀롱가',
)

TANGO_TYPES = Any(
    MILONGA,
    u'traditional',
    u'nuevo',
    u'ヌオーバ',
    u'새로운',
    u'vals',
    u'вальс',
    u'バルス',
    u'왈츠',
    u'alternative',
)
REAL_DANCE = commutative_connected(ARGENTINE, TANGO)

AMBIGUOUS_WORDS = Any(
    MILONGA,
    # 'traditional dance' or 'alternative dance' would trigger...
    #TANGO_TYPES,
    TANGO,
    commutative_connected(TANGO_TYPES, TANGO),
)

EXTRAS = Any(ARGENTINE, TANGO_TYPES, dance_keywords.EASY_DANCE)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any('meeting', 'incontro', 'festival', 'marathon', 'milongas?')
    GOOD_BAD_PAIRINGS = [
        (TANGO, Any('whiskey tango')),
    ]

    def _quick_is_dance_event(self):
        ballroom_classifier = ballroom.Style.get_classifier()(self._classified_event, debug=self._debug)
        result = ballroom_classifier.is_dance_event()
        for log in ballroom_classifier.debug_info():
            self._log(log)
        if result:
            return False
        return True

    def perform_extra_checks(self):
        result = self.is_tango()
        if result:
            return result

        return False

    def is_tango(self):
        if (self._title_has(TANGO) or self._title_has(MILONGA)) and len(list(self._get(EXTRAS))) >= 2:
            return 'has tango title and tango/dance keywords'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'TANGO'

    @classmethod
    def get_rare_search_keywords(cls):
        return ballroom_keywords.TANGO

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'argentine tango',
            'tango',
            'milonga',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES + [
            'milonga',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier
