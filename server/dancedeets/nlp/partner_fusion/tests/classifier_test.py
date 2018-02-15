# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.partner_fusion import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestFusion(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_fusion_event)

    def runTest(self):
        self.assertEvents(
            0.93, [
                '669291039861387',
                '921918057981374',
                '1274685369328652',
                '366520323793999',
                '1704450649591890',
                '530327094004152',
                '777869959071385',
                '522263024802045',
                '163835200882490',
                '120359225407566',
                '1416306395159253',
                '464867677243117',
                '356659561412890',
                '198854417327065',
                '198807857353008',
                '147499972552635',
                '146253669351450',
                '788956521288509',
                '956856397802115',
                '635842639919250',
                '1353578974748324',
                '131095320922148',
                '337888313381378',
                '1908908989419817',
                '1745981548775054',
                '129259031095673',
                '179363709310596',
                '372408219876500',
                '328543634323377',
                '743925259140118',
                '320692741742454',
                '165510697524780',
                '395136370936138',
                '103421377110501',
                '328786227622525',
                '934071360075748',
                '1948697122123709',
                '1710926742308356',
                '1899408790370750',
                '160598261339638',
                '241746583027333',
                '1892736177721748',
                '387834014975157',
                '843849372464309',
                '2018320591826655',
                '337517366729305',
                '132269517489108',
                '382460805524420',
                '737655156426468',
                '175664483201548',
                '514784775558935',
                '2031306733758134',
                '140081309999898',
                '941033559384259',
                '401153043672740',
                '179674846139312',
                '1932864880362590',
                '421757851570470',
                '206030839976033',
                '209572349593475',
                '433250297093562',
                '2066639276938879',
                '170641603548736',
                '147667212566415',
                '156392945154222',
                '1801702406515919',
                '150897055719394',
                '169822873649116',
                '1770774363232099',
                '2017064405236871',
                '2412609952297797',
                '331299494057757',
                '198281320755826',
                '336018070232864',
                '1235166026626754',
                '296936274161034',
                '152791872040827',
                '1834531303285019',
                '1245166475615211',
                '1854936231214121',
                '146489779326155',
                '153490011950870',
                '203804883520616',
                '1609633815785935',
                '1983313448618857',
                '331403377361547',
                '2001140266794754',
                '1818853918125910',
                '235291273681676',
                '2050757501876328',
                '877482735746071',
                '332474957234495',
                '290842081444283',
                '253161648548831',
                '179740579437887',
                '175523573066935',
                '528793264152783',
                '1771981623104588',
                '1710643318997028',
                '159790367988442',
                '542821766083502',
                '167634703967147',
                '125933364872188',
                '2131630390390235',
                '135663083793273',
                '173948063357861',
                '1608731172639141',
                '567547486928008',
                '136152070413562',
                '926935077469427',
                '159888537967876',
                '1800050453621535',
                '1231902996914127',
                '407588336254399',
                '169466343615268',
                '1249503761848877',
                '151510035570958',
                '1811120129187817',
                '217213602080048',
                '392748684485053',
                '189240514950282',
                '173856499893960',
                '152143275320332',
                '146986832555552',
                '956753574476512',
                '2111989162360678',
                '306365529875588',
                '2002661000022082',
                '123335485034796',
                '174406646475362',
                '132245747497921',
                '1691607424230275',
                '162575627677581',
                '290559168103731',
                '525285451159627',
                '141928936448464',
                '298023824045435',
                '764498020418020',
                '382320325564036',
                '177848639637532',
                '2159658440937852',
                '139391853381573',
                '511764899191032',
                '155785855080836',
                '167142230562236',
                '119190055460535',
                '191139558119494',
                '2113347708934949',
                '252805505247566',
                '228195031047673',
                '394966317607181',
                '1514981101953831',
                '918100448348956',
                '557400121287779',
                '1386556731453387',
                '315267632325634',
                '318414968651209',
                '160705201221264',
                '336109873464354',
                '546042809071428',
                '351520348649784',
                '398654557258116',
                '222824961596059',
                '869131236589818',
                '135567780472031',
                '158936024832716',
                '1698337713550011',
                '315690698917879',
                '155088018474875',
                '2213194408706342',
                '875209692649140',
                '318772255308105',
                '2040008852922835',
                '1699563710102092',
                '384517011991699',
                '549429798740676',
                '1728786450504901',
                '342742552872828',
                '333606077121031',
                '513804558987696',
                '2005155776419763',
                '365690413902348',
                '1997286870483455',
                '801471623374300',
                '1974795582843935',
                '544615709223791',
                '333461607132071',
                '1328905023922907',
                '280824899111357',
                '761419604048564',
                '341264306352640',
                '312581292586541',
                '1535344149852818',
                '157984911401845',
                '175903539677128',
                '818271505026022',
                '189196971664425',
                '198463950709678',
                '312850602559963',
                '150628378992154',
                '911539372348599',
                '2074807879414956',
                '134731790539195',
                '935638306612261',
                '140418576672877',
                '181148415805042',
                '465745767160479',
                '135974163764680',
                '200307043859712',
                '381338702308757',
                '1532526843529008',
                '1394719723984475',
                '148139209118558',
                '148651395783042',
                '662970627241175',
                '1847216548635388',
                '575306642806469',
                '446000445814749',
                '711364472396005',
                '777582045775131',
                '415634935539707',
                '1432929270089495',
                '1923776667938223',
                '1285276881573492',
                '151750528963955',
                '1698019203574262',
                '809246192596321',
                '537118666655354',
                '363231830817846',
                '1675619105835104',
                '169869820315470',
                '655173041324514',
                '1699732913404867',
                '1986971898235678',
                '1300043146806244',
                '1736631849715492',
                '1802821303346657',
            ]
        )


class TestNotWCS(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_fusion_event)

    def runTest(self):
        self.assertNotEvents(
            1.0, [
                '428716634230940',
                '1848632995169087',
                '164627797487415',
                '152662678784726',
                '297555000769021',
                '2085889528312870',
                '2012528535636130',
                '176628439612825',
                '553048008393134',
                '184896292244181',
                '1565847783535667',
                '284063248789034',
                '2070121633221005',
                '1926367237679774',
                '917395385098944',
                '921157954705802',
                '1871411686507766',
            ]
        )


if __name__ == '__main__':
    print unittest.main()
