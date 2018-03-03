import importlib

from dancedeets.nlp import all_styles_raw
from dancedeets.nlp import grammar

STYLE_NAMES = [
    'aerial_pole',
    'african',
    'ballet',
    'ballroom',
    'belly',
    'bhangra',
    'biodanza',
    'bollywood',
    'bugg',
    'burlesque',
    'butoh',
    'capoeira',
    'contact',
    'contemporary',
    'country',
    'dancehall',
    'discofox',
    'exotic',
    'five_rhythms',
    'flamenco',
    'folk',
    'forro',
    'hulahoop',
    'hustle',
    'indian',
    'irish',
    'jazz',
    'kizomba',
    'kompa',
    'kpop',
    'latin',
    'modern',
    'musical_theater',
    'northern_soul',
    'lion',
    'partner_fusion',
    'rockabilly',
    'soulline',
    'street',
    'swing',
    'tango',
    'tap',
    'wcs',
    'zapateado',
    'zouk',
    'zumba',
    'zydeco',
]

_STYLE_LIST = []

# TODO: decide on Style vs Vertical
# Each import must have a Style that fits the base_styles.Style API
for style_name in STYLE_NAMES:
    module = importlib.import_module('dancedeets.nlp.styles.%s' % style_name)
    _STYLE_LIST.append(module.Style)

# Generate a keyed lookup of styles (for any name-dependent lookups from URLs)
# and ensure they are all unique.
STYLES = {}
for style in _STYLE_LIST:
    if style.get_name() in STYLES:
        raise ImportError('Style name duplicated: %s' % style.get_name())
    STYLES[style.get_name()] = style

misc_keyword_sets = [
    all_styles_raw.DANCE_STYLE_CLASSICAL,
    all_styles_raw.DANCE_STYLE_MISC,
]


def all_styles_except(vertical):
    regexes = set()
    for regex_style in _STYLE_LIST:
        if regex_style != vertical:
            regexes.add(regex_style.get_basic_regex())
    regexes.update(misc_keyword_sets)
    return grammar.Any(*regexes)


# Classifiers need to generate a BAD_KEYWORDS of "other" styles of dance,
# which are dependent on having access to all the other styles of dance.
#
# So let's generate a regex of "other dance styles" for each style,
# and use it to construct a Classifer once (and all its associated regexes).
#
CLASSIFIERS = {}
for style in _STYLE_LIST:
    other_style_regex = all_styles_except(style.get_name())
    CLASSIFIERS[style.get_name()] = style.get_classifier(other_style_regex)
