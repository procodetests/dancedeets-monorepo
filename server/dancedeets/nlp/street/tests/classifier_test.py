# -*-*- encoding: utf-8 -*-*-

from dancedeets import fb_api
from dancedeets.nlp import event_classifier
from dancedeets.nlp.street import classifier
from dancedeets.nlp.street import rules
from dancedeets.test_utils import classifier_util
from dancedeets.test_utils import unittest


class TestSimpleMatches(unittest.TestCase):
    def runTest(self):
        self.assertTrue(rules.GOOD_DANCE.hack_double_regex()[1].findall('streetdance'))


class TestClassifier(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_street_event)

    def runTest(self):
        self.assertEvents(
            1.0, [
                '292568747504427',
                '113756888764413',
                '127125550747109',
                '325581104622156',
                '143209149694745',
                '143476793020106',
                '325703667950295',
                '326022244533717',
                '909714409183458',
                '1782771868686871',
                '332248927262403',
                '169440200445682',
                '145615122782143',
                '400609753700846',
                '1965152173740750',
                '1965090387036995',
                '2011958438820853',
                '220081321869278',
                '165666180746504',
                '552531505124927',
                '1943670062551799',
            ]
        )


class TestNotClassifier(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_street_event)

    def runTest(self):
        self.assertNotEvents(
            1.0,
            [
                '101883956566382',
                '194555360659913',
                '149083330948',
                '170007276417905',
                # main stacks voting...that points at a 'dancecontest'
                # '278853778841357',
                '901700663331339',
                '554735341564904',
                '176887729575922',
                '1769223556485010',
                '177022449727288',
                '386740331775797',
                '1769813053313447',
                '792479097623824',
                '305217459985869',
                '388285338262510',
                '1778462405509729',
                '155880198518860',
                '1187974821335295',
                '132446687422361',
                '1684989498212675',
                '392724404512595',
                '1954481071234585',
                '396693130787178',
                '947664685402950',
                '1569291073190990',
                '949597751864441',
                '1792957450997359',
                '1794309113922348',
                '402129570221472',
                '405283409910644',
                '356425948165435',
                '203939923425424',
                '2023796427905414',
                '202362010313553',
                '1993007464315651',
                '162101577755754',
                '162172367751971',
                '186902728532414',
                '1513319265389448',
                '1882660975096074',
                '2023759237883108',
                '2032292537014651',
                '2069034736659677',
                '2070935579807331',
                '1980686068839329',
                '1981960805414280',
                '1739239369470185',
                '1985782251745120',
                '1490079221290562',
                '160941114518853',
                '1609974032443450',
                '184827455444735',
                '1975387172781604',
                '147341605965140',
                '415367488900020',
                '1977572032527415',
                '146408459500248',
                '409195176178323',
                '172097530230470',
                '1587540748028464',
                '197513587664560',
                '214921812399494',
                '2124426937584474',
                '1861205767502832',
                '153661115337308',
                '197655364304266',
                '1245166475615211',
                '613996642265599',
                '1849637235076609',
                '426865667730859',
                '1587621647972231',
                '2063372853951857',
                '892166080960187',
                '323508834809998',
                '1623010711249152',
                '1753703991591351',
            ]
        )


# shoudld be breakdance event
# '114633285919267'

if __name__ == '__main__':
    print unittest.main()
