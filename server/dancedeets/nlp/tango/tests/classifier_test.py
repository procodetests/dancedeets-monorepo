# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.tango import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestTangoDance(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_tango_dance)

    def runTest(self):
        self.assertEvents(
            0.87,
            [
                '143395409622891',
                '1110602889040187',
                '154425685338767',
                '1768609653173211',
                '1795395450753458',
                '1939882822896194',
                '1958566194428479',
                '314567282383023',
                '1733936033581274',
                '183166825610163',
                '893547427477612',
                # doesn't have any dance-y-ness at all! so the title isn't enough
                '1675186629181954',
                '2031277610490215',
                '471332453012659',
                '1381854911924583',
                '1645742078825977',
                '203509450215943',
                '120417521960522',
                '589415014740047',
                '152319068869229',
                '155930024972826',
                '554468734898619',
                '366107440507680',
                '144203722953024',
                '201890927041540',
                '884092541723706',
                '641712289553231',
                '279073359276682',
                '1868902670029843',
                '280874332418976',
                '1490916200967324',
                '140768826682017',
                '1770409336596386',
                '488986861471590',
                '402168950212377',
                '320654788409187',
                '135222610436790',
                '1912290175697561',
                '2039538666319576',
                '732014236999086',
                '128842934466947',
                '519225605100169',
                '671954232928731',
                '2025672621094244',
                '131336354229579',
                '597103427133871',
                '177823876301174',
                '312908442528533',
                # really hard to tell, except for photos of the organizing page, that this is music party for dancers
                '160964504647924',
                '382848595479056',
                '1512109815529415',
                # cataniatangofestival in title, not strong enough body
                '938497682985096',
                '1278733645565059',
                '1617098248328561',
                # Lab esperienziale di Tangoterapia
                '865790983558775',
                '1817810721843804',
                '1309855745826392',
                '1740313445980066',
                '170071393611277',
                '1204345789697231',
                '2000208013601622',
                '190416948203173',
                # tango festival, but again nothing dance-y in the event itself
                '876688962514053',
                '504934906552950',
                '1415618191840257',
                '1635662776472165',
                '374722229642055',
                '136686173722565',
                '128674884512809',
                '1939984272902083',
                '1666219917013457',
                '333216153837127',
                '1801455586815385',
                '461013824259227',
                '1570077399706605',
                '103354760490626',
                '114633285919267',
            ]
        )


class TestArgentineTango(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_tango_dance)

    def runTest(self):
        self.assertEvents(
            1.0, [
                '1988917208036138',
                '161987814529460',
                '1618437668195235',
                '163467564301076',
                '345849422559031',
                '207031189831219',
                '661294880742633',
                '540346496327966',
                '361068981025325',
                '415585438867545',
                '2018056105076758',
                '369364133533907',
                '1570039023031190',
                '190914161460195',
                '519581475043484',
                '354544864980505',
                '517019348660388',
                '205927519957377',
                '167022180713629',
                '577046809305088',
                '207120679859051',
                '137263203611032',
                '141717939839047',
                '1566093160152306',
                '137385440272954',
                '722946267914515',
                '2064851073531964',
                '408214136300462',
                '194881994579572',
                '1962899960693657',
                '363083704153070',
                '147449452628146',
                '1897893373578581',
                '142737973081719',
                '170655500370398',
                '398310127274829',
                '777687052421368',
                '182622422342420',
                '176644656425243',
                '135222610436790',
                '994139454081857',
                '2156956197663257',
                '1804618809836720',
                '1961537790833052',
                '168163770486298',
                '163739854384888',
                '578235019189151',
                '141585269837562',
                '172948923296724',
                '199927777243344',
                '157747401677747',
                '376020766176602',
                '314721802374703',
                '460977857650490',
                '2044151515860449',
                '412813429151908',
                '162858147678068',
                '135742947221926',
                '163739870922564',
                '1965457390385555',
                '536022233440818',
                '485642495166306',
                '1986761204904702',
                '586606811680086',
                '1742140045836917',
                '552681225112416',
                '433518107051236',
                '1989696861272180',
                '216430198922935',
                '154577188500607',
                '142265256456892',
                '137808076846889',
                '1589618871121383',
                '931456513683428',
                '2018061455075217',
                '184437952147705',
                '613511422374020',
                '904749786346126',
            ]
        )


class TestNotArgentineTango(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_tango_dance)

    def runTest(self):
        self.assertNotEvents(
            1.0, [
                '207098266513986',
                '901694419980766',
                '2022928017926728',
                '1133278066779245',
                '533868250332853',
                '155402755240933',
                '142595719749818',
                '1531816326866465',
                '430708153999029',
                '133944810734911',
                '142406879806062',
                '746228675571972',
                '180451169374287',
                '263874720812469',
                '1823315074633311',
                '563811870620783',
                '1787101678027290',
                '146457449307847',
                '343819066027335',
                '877613112409798',
                '352308918579075',
                '1499257383526774',
            ]
        )


if __name__ == '__main__':
    print unittest.main()