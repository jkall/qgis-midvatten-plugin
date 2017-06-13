# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  measurements.
 
 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-03-08
        copyright            : (C) 2016 by joskal (HenrikSpa)
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#

import utils_for_tests
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from tools.midvatten_utils import get_foreign_keys
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch, call, MagicMock
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
from midvatten.midvatten import midvatten
import os
import PyQt4
from collections import OrderedDict
from import_data_to_db import midv_data_importer
from import_interlab4 import Interlab4Import

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)


class TestInterlab4Importer():
    def setUp(self):
        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        ms = MagicMock()
        ms.settingsdict = OrderedDict()
        self.importinstance = Interlab4Import(self.iface.mainWindow(), ms)

    def test_interlab4_parse_filesettings_utf16(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-16",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsn",
                        )
        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-16') as testfile:
            result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_filesettings(testfile)))

        reference_string = "['False', '4.0', 'utf-16', ',', 'False']"

        assert result_string == reference_string

    def test_interlab4_parse_filesettings_utf8(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-8",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsn",
                        )
        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_filesettings(testfile)))

        reference_string = "['False', '4.0', 'utf-8', ',', 'False']"

        assert result_string == reference_string

    def test_parse_interlab4_utf16(self):

        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-16",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-16') as testfile:
            result = self.importinstance.parse([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_iso_8859_1(self):

        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=ISO-8859-1",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'iso-8859-1') as testfile:
            result = self.importinstance.parse([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_utf8(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-8",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_ignore_bland_line(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-8",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u'',
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_quotechar(self):
        interlab4_lines = (
                    u'#Interlab',
                    u'#Version=4.0',
                    u'#Tecken=UTF-8',
                    u'#Textavgränsare=Ja',
                    u'#Decimaltecken=,',
                    u'#Provadm',
                    u'"Lablittera";"Namn";"Adress";"Postnr";"Ort";',
                    u'"DM-990908-2773";"MFR";"PG Vejdes väg 15";"351 96";"Växjö";',
                    u'#Provdat',
                    u'"Lablittera";"Metodbeteckning";"Parameter";"Mätvärdetext";"Mätvärdetal";',
                    u'"DM-990908-2773";"SS-EN ISO 7887-1/4";"Färgtal";;"5";',
                    u'#Slut'
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;metadata;adress;PG Vejdes väg 15;lablittera;DM-990908-2773;namn;MFR;ort;Växjö;postnr;351 96'
        assert result_string == reference_string

    def test_parse_interlab4_quotechar_semicolon(self):
        interlab4_lines = (
                    u'#Interlab',
                    u'#Version=4.0',
                    u'#Tecken=UTF-8',
                    u'#Textavgränsare=Ja',
                    u'#Decimaltecken=,',
                    u'#Provadm',
                    u'"Lablittera";"Namn";"Adress";"Postnr";"Ort";',
                    u'"DM-990908-2773";"MFR";"PG ;Vejdes väg 15";"351 96";"Växjö";',
                    u'#Provdat',
                    u'"Lablittera";"Metodbeteckning";"Parameter";"Mätvärdetext";"Mätvärdetal";',
                    u'"DM-990908-2773";"SS-EN ISO 7887-1/4";"Färgtal";;"5";',
                    u'#Slut'
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse([testfile])
        result_string = '|'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse([testfile])))
        reference_string = 'DM-990908-2773|Färgtal|lablittera|DM-990908-2773|metodbeteckning|SS-EN ISO 7887-1/4|mätvärdetal|5|parameter|Färgtal|metadata|adress|PG ;Vejdes väg 15|lablittera|DM-990908-2773|namn|MFR|ort|Växjö|postnr|351 96'

        assert result_string == reference_string

    def test_interlab4_to_table(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Färgtal, 5, 5, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30]]'
        assert result_string == reference_string

    def test_interlab4_to_table_kalium_above_2_5(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;5;5;;mg/l Pt;;;;;;;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;4;4;;mg/l Pt;;;;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 4, 4, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30]]'
        assert result_string == reference_string

    def test_interlab4_to_table_kalium_between_1_and_2_5(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;1,5;1,5;;mg/l Pt;;;;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 1.5, 1,5, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30]]'
        assert result_string == reference_string

    def test_interlab4_to_table_kalium_below_1(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 1, <1, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30]]'
        assert result_string == reference_string

    def test_interlab4_to_table_kalium_using_resolution(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;3;3;;mg/l Pt;;;±1;;;;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;10;10;;mg/l Pt;;;±0.1;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 10, 10, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30. mätosäkerhet: ±0.1]]'
        assert result_string == reference_string

    def test_interlab4_to_table_kalium_using_resolution_same_resolution_use_last_one(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;3;3;;mg/l Pt;;;±1;;;;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;10;10;;mg/l Pt;;;±1;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 10, 10, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30. mätosäkerhet: ±1]]'
        assert result_string == reference_string

    def test_interlab4_to_table_matvardetalanm(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;<;mg/l Pt;;;±1;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Färgtal, 5, <5, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30. mätosäkerhet: ±1]]'
        assert result_string == reference_string

    def test_interlab4_to_table_matvardetext_matvardetalanm_no_matvardetal(self):
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;obsid',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;anobsid',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;5;;<;mg/l Pt;;;±1;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse([testfile])

        result_string = utils_for_tests.create_test_string(self.importinstance.to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Färgtal, 5, <5, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30. mätosäkerhet: ±1]]'
        assert result_string == reference_string
        
    def tearDown(self):
        self.importinstance = None
        pass


class TestInterlab4ImporterDB(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)

        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        
    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_interlab4_full_test_to_db(self):

        utils.sql_alter_db(u'''insert into zz_staff (staff) values ('DV')''')

        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("anobsid")')

        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as filename:
            @mock.patch('midvatten_utils.NotFoundQuestion')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.askuser', TestInterlab4ImporterDB.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                mock_not_found_question.return_value.answer = u'ok'
                mock_not_found_question.return_value.value = u'anobsid'
                mock_not_found_question.return_value.reuse_column = u'obsid'
                mock_filenames.return_value = [filename]
                self.mock_iface = mock_iface
                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = Interlab4Import(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select * from w_qual_lab'''))
        reference_string = ur'''(True, [(anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 1.0, <1, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30)])'''
        assert test_string == reference_string


