# -*-*- encoding: utf-8 -*-*-

import codecs
import logging
import math
import re
import time
from util import re_flatten
from util import cjk_detect
from spitfire.runtime.filters import skip_filter

# TODO: translate to english before we try to apply the keyword matches
# TODO: if event creator has created dance events previously, give it some weight
# TODO: 

# TODO: for each style-keyword, give it some weight. don't be a requirement but yet-another-bayes-input
# TODO: add a bunch of classifier logic
# TODO: for iffy events, assume @ in the title means its a club event. same with monday(s) tuesday(s) etc.
# TODO: house class, house workshop, etc, etc. since 'house' by itself isn't sufficient
# maybe feed keywords into auto-classifying event type? bleh.

# street dance.* ?
# 'crew' biases dance one way, 'company' biases it another
easy_dance_keywords = [
    'dance style[sz]',
    'dances?', 'dancing', 'dancers?',
    u'ダンサー', # japanese dance
    u'ダンス', # japanese dance
    u'춤.?', # korean dance
    u'추고.?.?', # korean dancing
    u'댄서.?.?', # korean dancers
    u'踊り', # japanese dance
    u'רוקד', # hebrew dance
    u'רקדם', # hebrew dancers
    u'רוקדים', # hebrew dance
    u'רקדנים', # hebrew dancers
    u'舞者', # chinese dancer
    u'舞技', # chinese dancing
    u'舞', # chinese dance
    u'舞蹈', # chinese dance
    u'舞蹈的', # chinese dance
    u'排舞', # chinese dance
    u'เต้น', # dance thai
    u'กเต้น', # dancers thai
    'danse\w*', # french
    'taniec', # dance polish
    u'zatanč\w*', # dance czech
    'tan[ec][ec]\w*', # dance polish
    'tanca', # dance slovak
    u'tancujú', # dance slovak
    u'tanečno', # dance slovak
    u'danç\w*', # dance portuguese
    u'tańc\w*', # dance polish
    u'taneč\w*', # dance czech
    'tancovat', # dance czech
    'danza\w*', # dance italian
    u'šok\w*', # dance lithuanian
    'tanz\w*', # dance german
    'tanssi\w*', # finnish dance
    'bail[ae]\w*', # dance spanish
    'danzas', # dance spanish
    'ballerino', # dancer italian
    u'tänzern', # dancer german
    u'танчер', # dancer macedonian
    u'танцовиот', # dance macedonian
    'footwork',
    'plesa', # dance croatian
    'plesu', # dancing croatian
    u'nhảy', # dance vietnamese
    u'tänzer', # dancer german
]
easy_choreography_keywords = [
    u'(?:ch|k|c)oe?re[o|ó]gra(?:ph|f)\w*', #english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese
    'choreo',
    u'chorée', # french choreo
    u'chorégraph\w*', # french choreographer
    u'кореограф', # macedonian
]

# if somehow has funks, hiphop, and breaks, and house. or 3/4? call it a dance event?

dance_and_music_keywords = [
    'hip\W?hop',
    u'ההיפ הופ', # hebrew hiphop
    u'хипхоп', # macedonian hiphop
    u'ヒップホップ', # hiphop japanese
    u'힙합', # korean hiphop
    'hip\W?hop\w*', # lithuanian, polish hiphop
    'all\W?style[zs]?',
    'tout\W?style[zs]?', # french all-styles
    'tutti gli stili', # italian all-styles
    'swag',
    'funk',
    'dance\W?hall',
    'ragga',
    'hype',
    'new\W?jack\W?swing',
    'breaks',
    'boogaloo',
    'breaking?', 'breakers?',
    'free\W?style',
    'jerk',
    'kpop',
    'rnb',
    'hard\Whitting',
    'old\W?school hip\W?hop',
    '90\W?s hip\W?hop',
    u'フリースタイル', # japanese freestyle
]

# hiphop dance. hiphop dans?
dance_keywords = [
    'music video',
    'freestylers?',
    'breakingu', #breaking polish
    u'breaktánc', # breakdance hungarian
    'jazz rock',
    'poppers?', 'popp?i?ng?',
    'poppeurs?',
    'commercial hip\W?hop',
    'jerk(?:ers?|ing?)',
    'street\W?dancing?',
    u'스트릿', # street korean
    u'ストリートダンス', # japanese streetdance
    u'街舞', # chinese streetdance / hiphop
    u'gatvės šokių', # lithuanian streetdance
    'katutanssi\w*', # finnish streetdance
    'street\W?dance', 'bre?ak\W?dance', 'bre?ak\W?dancing?', 'brea?ak\W?dancers?',
    'turfing?', 'turf danc\w+', 'flexing?', 'bucking?', 'jooking?',
    'b\W?boy[sz]?', 'b\W?boying?', 'b\W?girl[sz]?', 'b\W?girling?', 'power\W?moves?', 'footworking?',
    'b\W?boy\w*', # 'bboyev' in slovak
    u'파워무브', # powermove korean
    'breakeuse', # french bgirl
    'footworks', # spanish footworks
    'top\W?rock(?:s|er[sz]?|ing?)?', 'up\W?rock(?:s|er[sz]?|ing?|)?',
    'houser[sz]?', 'house ?danc\w*',
    'dance house', # seen in italian
    'lock(?:er[sz]?|ing?)?', 'lock dance',
    u'ロッカーズ', # japanese lockers
    u'ロッカ', # japanese lock
    '[uw]h?aa?c?c?k(?:er[sz]?|inn?g?)', # waacking
    'paa?nc?king?', # punking
    'locking4life',
    'dance crew[sz]?',
    'waving?', 'wavers?',
    'bott?ing?',
    'robott?ing?',
    'shuffle', 'melbourne shuffle',
    'jump\W?style[sz]?',
    'strutter[sz]?', 'strutting',
    'glides?', 'gliding', 
    'tuts?', 'tutting?', 'tutter[sz]?',
    'mj\W+style', 'michael jackson style',
    'mtv\W?style', 'mtv\W?dance', 'videoclip\w+', 'videodance',
    'l\W?a\W?\Wstyle', 'l\W?a\W?\Wdance',
    'n(?:ew|u)\W?styles?',
    'mix(?:ed)?\W?style[sz]?', 'open\W?style[sz]',
    'me against the music',
    'krump', 'krumping?', 'krumper[sz]?',
    'girl\W?s\W?hip\W?hop',
    'hip\W?hopp?er[sz]?',
    'street\W?jazz', 'street\W?funk', 'jazz\W?funk', 'boom\W?crack',
    'hype danc\w*',
    'social hip\W?hop', 'hip\W?hop social dance[sz]',
    '(?:new|nu|middle)\W?s(?:ch|k)ool hip\W?hop', 'hip\W?hop (?:old|new|nu|middle)\W?s(?:ch|k)ool',
    'newstyleurs?',
    'vogue', 'voguer[sz]?', 'vogue?ing', 'vogue fem', 'voguin',
    'mini\W?ball', 'realness',
    'urban danc\w*',
    'dan\w+ urban\w+', # spanish urban dance
    'baile urban\w+', # spanish urban dance
    'pop\W{0,3}lock(?:ing?|er[sz]?)?'
]

easy_event_keywords = [
    'jams?', 'club', 'after\Wparty', 'pre\Wparty',
    u'クラブ',  # japanese club
    'open sessions?', 'training',
]
club_and_event_keywords = [
    'sesja', # polish session
    'sessions', 'practice',
    # international sessions are handled down below
    'shows?', 'performances?', 'contests?',
    'concours', # french contest
    'showcase',
    u'ショーケース', # japanese showcase
    u'秀', # chinese show
    u'的表演', # chinese performance
    u'表演', # chinese performance
    u'パフォーマンス', # japanese performance
    'konkurrencer', # danish contest
    'dancecontests', # dance contests german
    'esibizioni', #italian performance/exhibition
]

club_only_keywords = [
    'club',
    'bottle service',
    'table service',
    'coat check',
    #'rsvp',
    'free before',
    #'dance floor',
    #'bar',
    #'live',
    #'and up',
    'vip',
    'guest\W?list',
    'drink specials?',
    'resident dj\W?s?',
    'dj\W?s?',
    'techno', 'trance', 'indie', 'glitch',
    'bands?',
    'dress to',
    'mixtape',
    'decks',
    'r&b',
    'local dj\W?s?',
    'all night',
    'lounge',
    'live performances?',
    'doors', # doors open at x
    'restaurant',
    'hotel',
    'music shows?',
    'a night of',
    'dance floor',
    'beer',
    'blues',
    'bartenders?',
    'waiters?',
    'waitress(?:es)?',
    'go\Wgo',
    'gogo',
]

#TODO(lambert): use these
anti_dance_keywords  = [
    'jerk chicken',
    'poker tournaments?',
    'fashion competition',
    'wrestling competition',
    't?shirt competition',
    'shaking competition',
    'costume competition',
    'bottles? popping?',
    'poppin.? bottles?',
    'dance fitness',
    'lock down',
]
# lock up
# battle freestyle ?
# dj battle
# battle royale
# http://www.dancedeets.com/events/admin_edit?event_id=208662995897296
# mc performances
# beatbox performances
# beat 
# 'open cyphers'
# freestyle
# go\W?go\W?danc(?:ers?|ing?)
#in\Whouse  ??
# 'brad houser'
# world class
# 1st class
# whack music
# wack music

# open mic
# Marvellous dance crew (uuugh)

#dj.*bboy
#dj.*bgirl

# 'vote for xx' in the subject
# 'vote on' 'vote for' in body, but small body of text
# release party

# methodology
# cardio
# fitness

# sometimes dance performances have Credits with a bunch of other performers, texts, production, etc. maybe remove these?

# HIP HOP INTERNATIONAL

# bad words in title of club events
# DJ
# Live
# Mon/Tue/Wed/Thu/Fri/Sat
# Guests?
# 21+ 18+

# boogiezone if not contemporary?
# free style if not salsa?


#TODO(lambert): use these to filter out shows we don't really care about
other_show_keywords = [
    'comedy',
    'poetry',
    'poets?',
    'spoken word',
    'painting',
    'juggling',
    'magic',
    'singing',
    'acting',
]

event_keywords = [
    'street\W?jam',
    'camp',
    'kamp',
    'kemp',
    'crew battle[sz]?', 'exhibition battle[sz]?',
    'apache line',
    'battle of the year', 'boty', 'compete', 'competitions?',
    'competencia', # spanish competition
    u'compétition', # french competition
    u'thi nhảy', # dance competition vietnam
    'kilpailu\w*' # finish competition
    'konkursams', # lithuanian competition
    'verseny', # hungarian competition
    u'čempionatams', # lithuanian championship
    'campeonato', # spanish championship
    'meisterschaft', # german championship
    'concorsi', # italian competition
    u'danstävling', # swedish dance competition
    'battles?',
    u'バトル', # japanese battle
    'batallas', # battles spanish
    'zawody', # polish battle/contest
    'walki', # polish battle/fight
    u'walkę', # polish battle/fight
    'bitwa', # polish battle
    u'bitwę', # polish battle
    'bitwach', # polish battle
    u'バトル', # japanese battle
    'tournaments?',
    u'大会', # japanese tournament
    u'トーナメント', # japanese tournament
    'turnie\w*', # tournament polish/german
    u'giải đấu', # tournament vietnamese
    'turneringer', # danish tournament
    'preselections?',
    u'présélections?', # preselections french
    'jurys?',
    'jurados?', # spanish jury
    'judge[sz]?',
    'giudici', # italian judges
    u'השופט', # hebrew judge
    u'השופטים', # hebrew judges
    u'teisėjai', # lithuanian judges
    'tuomaristo', # jury finnish
    'jueces', # spanish judges
    'giuria', # jury italian
    'show\W?case',
    r'(?:seven|7)\W*(?:to|two|2)\W*(?:smoke|smook)',
    'c(?:y|i)ph(?:a|ers?)',
    u'サイファ', # japanese cypher
    u'サイファー', # japanese cypher
    'cerchi', # italian circle/cypher
    u'ไซเฟอร์', # thai cypher
    u'싸이퍼.?', # korean cypher
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    u'セッション', # japanese session
    'formazione', # training italian
    u'トレーニング', # japanese training
    'workshop\W?s?',
    'cursillo', # spanish workshop
    'ateliers', # french workshop
    'workshopy', # czech workshop
    u'סדנאות', # hebrew workshops
    u'סדנה', # hebew workshop
    # 'taller', # workshop spanish
    'delavnice', # workshop slovak
    'talleres', # workshops spanish
    'radionicama', # workshop croatian
    'warsztaty', # polish workshop
    u'warsztatów', # polish workshop
    u'seminarų', # lithuanian workshop
    'class with', 'master\W?class(?:es)?',
    'auditions?',
    'audicija', # audition croatia
    'audiciones', # spanish audition
    'konkurz', # audition czech
    u'試鏡', # chinese audition
    'audizione', # italian audition
    'naborem', # polish recruitment/audition
    'try\W?outs?', 'class(?:es)?', 'lessons?', 'courses?',
    'klass(?:EN)?', # slovakian class
    u'수업', # korean class
    u'수업을', # korean classes
    'lekc[ie]', # czech lesson
    u'課程', # course chinese
    u'課', # class chinese
    u'堂課', # lesson chinese
    u'コース', # course japanese
    'concorso', # course italian
    'kurs(?:y|en)?', # course german/polish
    'aulas?', # portuguese class(?:es)?
    u'특강', # korean lecture
    'lekcie', # slovak lessons
    'dansklasser', # swedish dance classes
    'lekcja', # polish lesson
    'eigoje', # lithuanian course
    'pamokas', # lithuanian lesson
    'kursai', # course lithuanian
    'lezione', # lesson italian
    'lezioni', # lessons italian
    u'zajęciach', # class polish
    u'zajęcia', # classes polish
    u'คลาส', # class thai
    'classi',
    'cours', 'clases?',
    'corso',  # lesson italian
    'abdc', 'america\W?s best dance crew',
    'crew\W?v[sz]?\W?crew',
    'prelims?',
    u'初賽', # chinese preliminaries
    'bonnie\s*(?:and|&)\s*clyde',
] + [u'%s[ -]?(?:v/s|vs?\\.?|x|×|on)[ -]?%s' % (i, i) for i in range(12)]
event_keywords += [r'%s[ -]?na[ -]?%s' % (i, i) for i in range(12)] # polish x vs x

french_event_keywords = [
    'spectacle',
    'stage',
]

italian_event_keywords = [
    'stage',
]

dance_wrong_style_keywords = [
    'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba',
    'waltz',
    'salsy', # salsa czech
    'milonga',
    'dance partner',
    'cha cha',
    'hula',
    'tumbling',
    'exotic',
    'cheer',
    'barre',
    'contact improv',
    'contact improv\w*',
    'contratto mimo', # italian contact mime
    'musical theat(?:re|er)',
    'pole dance', 'flirt dance',
    'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar',
    'indienne',
    'persiana?',
    'arabe', 'arabic',
    'oriental\w*', 'oriente', 
    'capoeira',
    'tahitian dancing',
    'folkloric',
    'kizomba',
    'burlesque',
    'technique', 'limon',
    'clogging',
    'zouk',
    'afro mundo',
    'class?ic[ao]',
    # Sometimes used in studio name even though it's still a hiphop class:
    #'ballroom',
    #'ballet',
    #'yoga',
    'acroyoga',
    'kirtan',
    'modern dance',
    'pilates',
    'tribal',
    'jazz', 'tap', 'contemporary',
    'contempor\w*', # contemporary italian, french
    'african',
    'sabar',
    'silk',
    'aerial',
    'zumba', 'belly\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance',
    'soca',
    'flamenco',
]

all_regexes = {}

#TODO(lambert): maybe handle 'byronom coxom' in slovakian with these keywords
def get_manual_dance_keywords():
    manual_dance_keywords = []
    import os
    if os.getcwd().endswith('mapreduce'): #TODO(lambert): what is going on with appengine sticking me in the wrong starting directory??
        base_dir = '..'
    else:
        base_dir = '.'
    for filename in ['bboy_crews', 'bboys', 'choreo_crews', 'choreo_dancers', 'choreo_keywords', 'competitions', 'freestyle_crews', 'freestyle_dancers', 'freestyle_keywords']:
        f = codecs.open('%s/dance_keywords/%s.txt' % (base_dir, filename), encoding='utf-8')
        for line in f.readlines():
            line = re.sub('\s*#.*', '', line.strip())
            if not line:
                continue
            if line.endswith(',0'):
                line = line[:-2]
            else:
                manual_dance_keywords.append(line)
    return manual_dance_keywords

def build_regexes():
    if 'good_capturing_keyword_regex' in all_regexes:
        return

    manual_dance_keywords = get_manual_dance_keywords()

    if manual_dance_keywords:
        all_regexes['manual_dance_keywords_regex'] = make_regexes(manual_dance_keywords)
    else:
        all_regexes['manual_dance_keywords_regex'] = re.compile(r'NEVER_MATCH_BLAGSDFSDFSEF')

    all_regexes['good_capturing_keyword_regex'] = make_regexes(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords + club_and_event_keywords + dance_and_music_keywords + easy_choreography_keywords + manual_dance_keywords, matching=True)

def special_word(x):
    if re.search(r'[\(\)\\\*\+\?\[\]]', x):
        return True
    return False

def make_regex(strings, matching=False, word_boundaries=True):
    # flatten out all the simple regexes that we can
    not_special = [x for x in strings if not special_word(x)]

    try:
        special = [x for x in strings if special_word(x)]
        strings = [re_flatten.construct_regex(not_special)] + special
        u = u'|'.join(strings)
        if matching:
            regex = u'(?ui)(' + u + u')'
        else:
            regex = u'(?ui)(?:' + u + u')'
        if word_boundaries:
            regex = r'\b%s\b' % regex
        return re.compile(regex)
    except UnicodeDecodeError:
        for line in strings:
            try:
                re.compile(u'|'.join([line]))
            except UnicodeDecodeError:
                logging.error("failed to compile: %r: %s", line, line)
        logging.fatal("Error constructing regexes")

WORD_BOUNDARIES = 0
NO_WORD_BOUNDARIES = 1
def make_regexes(strings, matching=False):
    a = [None] * 2
    a[NO_WORD_BOUNDARIES] = make_regex(strings, matching=matching, word_boundaries=False)
    a[WORD_BOUNDARIES] = make_regex(strings, matching=matching, word_boundaries=True)
    return tuple(a)

all_regexes['dance_wrong_style_regex'] = make_regexes(dance_wrong_style_keywords)
all_regexes['dance_and_music_regex'] = make_regexes(dance_and_music_keywords)
all_regexes['club_and_event_regex'] = make_regexes(club_and_event_keywords)
all_regexes['easy_choreography_regex'] = make_regexes(easy_choreography_keywords)
all_regexes['club_only_regex'] = make_regexes(club_only_keywords)

all_regexes['easy_dance_regex'] = make_regexes(easy_dance_keywords)
all_regexes['easy_event_regex'] = make_regexes(easy_event_keywords)
all_regexes['dance_regex'] = make_regexes(dance_keywords)
all_regexes['event_regex'] = make_regexes(event_keywords)
all_regexes['french_event_regex'] = make_regexes(event_keywords + french_event_keywords)
all_regexes['italian_event_regex'] = make_regexes(event_keywords + italian_event_keywords)

all_regexes['bad_capturing_keyword_regex'] = make_regexes(club_only_keywords + dance_wrong_style_keywords, matching=True)

all_regexes['italian'] = make_regexes(['di', 'i', 'e', 'con'])
all_regexes['french'] = make_regexes(["l'\w*", 'le', 'et', 'une', 'avec', u'à', 'pour'])

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def get_relevant_text(fb_event):
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    return search_text

class ClassifiedEvent(object):
    def __init__(self, fb_event, language=None):
        if 'name' not in fb_event['info']:
            logging.info("fb event id is %s has no name, with value %s", fb_event['info']['id'], fb_event)
            self.search_text = ''
        else:
            self.search_text = get_relevant_text(fb_event)
        self.language = language
        self.times = {}

    def classify(self):
        build_regexes()
        start = time.time()

        #self.language not in ['ja', 'ko', 'zh-CN', 'zh-TW', 'th']:
        if cjk_detect.cjk_regex.search(self.search_text):
            idx = NO_WORD_BOUNDARIES
        else:
            idx = WORD_BOUNDARIES

        a = time.time()
        b = time.time()
        manual_dance_keywords_matches = all_regexes['manual_dance_keywords_regex'][idx].findall(self.search_text)
        self.times['manual_regex'] = time.time() - b
        easy_dance_matches = all_regexes['easy_dance_regex'][idx].findall(self.search_text)
        easy_event_matches = all_regexes['easy_event_regex'][idx].findall(self.search_text)
        dance_matches = all_regexes['dance_regex'][idx].findall(self.search_text)
        if all_regexes['french'][idx].search(self.search_text):
            event_matches = all_regexes['french_event_regex'][idx].findall(self.search_text)
        elif all_regexes['italian'][idx].search(self.search_text):
            event_matches = all_regexes['italian_event_regex'][idx].findall(self.search_text)
        else:
            event_matches = all_regexes['event_regex'][idx].findall(self.search_text)
        dance_wrong_style_matches = all_regexes['dance_wrong_style_regex'][idx].findall(self.search_text)
        dance_and_music_matches = all_regexes['dance_and_music_regex'][idx].findall(self.search_text)
        club_and_event_matches = all_regexes['club_and_event_regex'][idx].findall(self.search_text)
        easy_choreography_matches = all_regexes['easy_choreography_regex'][idx].findall(self.search_text)
        club_only_matches = all_regexes['club_only_regex'][idx].findall(self.search_text)
        self.times['all_regexes'] = time.time() - a

        self.found_dance_matches = dance_matches + easy_dance_matches + dance_and_music_matches + manual_dance_keywords_matches + easy_choreography_matches
        self.found_event_matches = event_matches + easy_event_matches + club_and_event_matches
        self.found_wrong_matches = dance_wrong_style_matches + club_only_matches

        combined_matches = self.found_dance_matches + self.found_event_matches
        fraction_matched = 1.0 * len(combined_matches) / len(re.split(r'\W+', self.search_text))
        if not fraction_matched:
            self.calc_inverse_keyword_density = 100
        else:
            self.calc_inverse_keyword_density = -int(math.log(fraction_matched, 2))

        if len(manual_dance_keywords_matches) >= 1:
            self.dance_event = 'obvious dancer or dance crew or battle'
        # one critical dance keyword
        elif len(dance_matches) >= 1:
            self.dance_event = 'obvious dance style'
        elif len(dance_and_music_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif len(easy_dance_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and len(dance_wrong_style_matches) == 0 and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'dance event thats not a bad-style'
        elif len(easy_dance_matches) >= 1 and len(club_and_event_matches) >= 1 and len(dance_wrong_style_matches) == 0 and len(club_only_matches) == 0:
            self.dance_event = 'dance show thats not a club'
        else:
            self.dance_event = False
        self.times['all_match'] = time.time() - a

    def is_dance_event(self):
        return bool(self.dance_event)
    def reason(self):
        return self.dance_event
    def dance_matches(self):
        return set(self.found_dance_matches)
    def event_matches(self):
        return set(self.found_event_matches)
    def wrong_matches(self):
        return set(self.found_wrong_matches)
    def match_score(self):
        if self.is_dance_event():
            combined_matches = self.found_dance_matches + self.found_event_matches
            return len(combined_matches)
        else:
            return 0
    def inverse_keyword_density(self):
        return self.calc_inverse_keyword_density


def get_classified_event(fb_event, language):
    classified_event = ClassifiedEvent(fb_event, language)
    classified_event.classify()
    return classified_event

def relevant_keywords(fb_event):
    build_regexes()
    text = get_relevant_text(fb_event)
    #TODO(lambert): add language-support to this so we do better on foreign ones
    good_keywords = all_regexes['good_capturing_keyword_regex'][NO_WORD_BOUNDARIES].findall(text)
    bad_keywords = all_regexes['bad_capturing_keyword_regex'][NO_WORD_BOUNDARIES].findall(text)
    return sorted(set(good_keywords).union(bad_keywords))

@skip_filter
def highlight_keywords(text):
    build_regexes()
    #TODO(lambert): add language-support to this so we do better on foreign ones
    text = all_regexes['good_capturing_keyword_regex'][WORD_BOUNDARIES].sub('<span class="matched-text">\\1</span>', text)
    text = all_regexes['bad_capturing_keyword_regex'][WORD_BOUNDARIES].sub('<span class="bad-matched-text">\\1</span>', text)
    return text

