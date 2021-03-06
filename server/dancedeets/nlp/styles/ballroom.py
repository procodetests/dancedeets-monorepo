# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom_keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BALLROOM_STYLES = Any(*ballroom_keywords.BALLROOM_STYLES)
LATIN_STYLES = Any(*ballroom_keywords.LATIN_STYLES)

BALLROOM = Any(
    'ballroom',
    'ballsaal',  # german
    u'tane\w+ sál',  # czech
    'salle de bal',  # french
    u'salón de baile',  # spanish
    u'towarzyski\w*',  # polish
    u'бальный',  # russian
    u'phòng khiêu vũ',  # vietnamese
    u'舞廳',
    u'ボールルーム',
    u'사교',
)

BALLROOM_DANCE = commutative_connected(BALLROOM, dance_keywords.EASY_DANCE)
BALLROOM_KEYWORDS = Any(
    BALLROOM_DANCE,
    'dance\W?sport',
    'international ballroom',
    'international latin',
    'american smooth',
    u'американ смус',
    'american rhythm',
    'collegiate ballroom',
    'world dancesport federation',
    'world dance council',
)
EASY_BALLROOM_KEYWORDS = Any(
    BALLROOM,
    'wdsf',
    'wdc',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    COMBINED_KEYWORDS = Any(
        BALLROOM_KEYWORDS,
        BALLROOM_STYLES,
    )

    @base_auto_classifier.log_to_bucket('has_any_relevant_keywords')
    def _has_any_relevant_keywords(self):
        # Override this here.
        # Don't use the other_bad_regex and GOOD/AMBIGUOUS keywords
        return self._has(self.COMBINED_KEYWORDS)

    @classmethod
    def finalize_class(cls, other_style_regexes):
        super(Classifier, cls).finalize_class(other_style_regexes)
        pass

    @base_auto_classifier.log_to_bucket('is_dance_event')
    def is_dance_event(self):
        self._log('Starting %s classifier', self.vertical)

        if not self._has_any_relevant_keywords():
            self._log('does not have any relevant keywords for this style')
            return False

        all_styles = set(self._get(BALLROOM_STYLES))
        all_latin_styles = set(self._get(LATIN_STYLES))

        all_hard_keywords = set(self._get(BALLROOM_KEYWORDS))
        all_easy_keywords = set(self._get(EASY_BALLROOM_KEYWORDS))
        all_keyword_score = 2 * len(all_hard_keywords) + len(all_easy_keywords)

        self._log(
            'ballroom classifier: event %s found styles %s, keywords %s', self._classified_event.fb_event['info']['id'], all_styles,
            all_hard_keywords.union(all_easy_keywords)
        )
        if self._title_has(BALLROOM_DANCE):
            return 'obviously ballroom dance event'

        if all_keyword_score >= 2:
            return 'Found many ballroom styles'

        if len(all_styles) >= 1 and all_keyword_score >= 2:
            return 'Found many ballroom styles and keywords'

        if len(all_styles) >= 5:
            return 'Found many overall ballroom styles'

        non_latin_styles = all_styles.difference(all_latin_styles)
        self._log('found non-latin styles %s and latin styles %s', non_latin_styles, all_latin_styles)

        if len(non_latin_styles) >= 2 and len(all_latin_styles):
            return 'Found non-latin and latin ballroom styles together'

        if len(non_latin_styles) >= 3:
            return 'Found many non-latin ballroom styles'

        if len(all_latin_styles) >= 3 and self._has(BALLROOM):
            return 'Found enough latin ballroom styles, and the word ballroom too'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BALLROOM'

    @classmethod
    def get_rare_search_keywords(cls):
        return ballroom_keywords.BALLROOM

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'ballroom dance',
            'latin ballroom',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
