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
from __future__ import absolute_import
#

import db_utils
import midvatten_utils as utils
import mock
from import_interlab4 import Interlab4Import
from nose.plugins.attrib import attr

import mocks_for_tests
import utils_for_tests


@attr(status='on')
class TestInterlab4ImporterDB(utils_for_tests.MidvattenTestSpatialiteDbSv):
    def setUp(self):
        super().setUp()
        self.importinstance = Interlab4Import(self.iface.mainWindow(), self.midvatten.ms)

    def test_interlab4_full_test_to_db(self):

        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('DV')''')

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('anobsid')''')

        interlab4_lines = (
            '#Interlab',
            '#Version=4.0',
            '#Tecken=UTF-8',
            '#Textavgränsare=Nej',
            '#Decimaltecken=,',
            '#Provadm',
            'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            '#Provdat',
            'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            '#Slut'
                )

        with utils.tempinput('\n'.join(interlab4_lines), 'utf-8') as filename:
            @mock.patch('midvatten_utils.NotFoundQuestion')
            @mock.patch('import_data_to_db.utils.Askuser', mocks_for_tests.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.qgis.PyQt.QtWidgets.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                mock_not_found_question.return_value.answer = 'ok'
                mock_not_found_question.return_value.value = 'anobsid'
                mock_not_found_question.return_value.reuse_column = 'obsid'
                mock_filenames.return_value = [[filename]]
                importer = Interlab4Import(self.iface.mainWindow(), self.midvatten.ms)
                importer.parse_observations_and_populate_gui()
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT * FROM w_qual_lab'''))
        reference_string = r'''(True, [(anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 2.5, <2,5, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30), (anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium (dubblett 1), 1.0, <1, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30)])'''
        print(reference_string)
        print(test_string)
        assert test_string == reference_string


    def test_interlab4_full_test_to_db_staff_0(self):

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('anobsid')''')

        interlab4_lines = (
            '#Interlab',
            '#Version=4.0',
            '#Tecken=UTF-8',
            '#Textavgränsare=Nej',
            '#Decimaltecken=,',
            '#Provadm',
            'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;0;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            '#Provdat',
            'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            '#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as filename:
            @mock.patch('midvatten_utils.NotFoundQuestion')
            @mock.patch('import_data_to_db.utils.Askuser', mocks_for_tests.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.qgis.PyQt.QtWidgets.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                mock_not_found_question.return_value.answer = 'ok'
                mock_not_found_question.return_value.value = 'anobsid'
                mock_not_found_question.return_value.reuse_column = 'obsid'
                mock_filenames.return_value = [[filename]]
                importer = Interlab4Import(self.iface.mainWindow(), self.midvatten.ms)
                importer.parse_observations_and_populate_gui()
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT * FROM w_qual_lab'''))
        reference_string = '''(True, [(anobsid, None, DM-990908-2773, Demoproj, 0, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 2.5, <2,5, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30), (anobsid, None, DM-990908-2773, Demoproj, 0, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium (dubblett 1), 1.0, <1, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30)])'''
        print(reference_string)
        print(test_string)
        assert test_string == reference_string

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT * FROM zz_staff'''))
        reference_string = '(True, [(0, None)])'
        assert test_string == reference_string


    def test_interlab4_connection_table(self):

        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('DV')''')

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('obsid1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('obsid2')''')

        db_utils.sql_alter_db('''INSERT INTO interlab4_obsid_assignment (specifik_provplats, provplatsnamn, obsid) VALUES ('Demo', 'Demo1 vattenverk', 'obsid1')''')
        db_utils.sql_alter_db('''INSERT INTO interlab4_obsid_assignment (specifik_provplats, provplatsnamn, obsid) VALUES ('Demo', 'Demo2 vattenverk', 'obsid2')''')



        interlab4_lines = (
            '#Interlab',
            '#Version=4.0',
            '#Tecken=UTF-8',
            '#Textavgränsare=Nej',
            '#Decimaltecken=,',
            '#Provadm',
            'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;;Demo1 vattenverk;Demo;;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            'DM-990908-2774;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;;Demo2 vattenverk;Demo;;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            '#Provdat',
            'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            'DM-990908-2774;SS-EN ISO 7887-1/4;Kalium;<15;15;;mg/l Pt;;;;;;;',
            '#Slut'
                )

        with utils.tempinput('\n'.join(interlab4_lines), 'utf-8') as filename:
            @mock.patch('midvatten_utils.NotFoundQuestion')
            @mock.patch('import_data_to_db.utils.Askuser', mocks_for_tests.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.qgis.PyQt.QtWidgets.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                #mock_not_found_question.return_value.answer = 'ok'
                #mock_not_found_question.return_value.value = 'anobsid'
                #mock_not_found_question.return_value.reuse_column = 'obsid'
                mock_filenames.return_value = [[filename]]
                importer = Interlab4Import(self.iface.mainWindow(), self.midvatten.ms)
                importer.parse_observations_and_populate_gui()
                importer.use_obsid_assignment_table.setChecked(True)
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT * FROM w_qual_lab'''))

        reference_string = r'''(True, [(obsid1, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 2.5, <2,5, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo1 vattenverk. specifik provplats: Demo), (obsid1, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium (dubblett 1), 1.0, <1, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo1 vattenverk. specifik provplats: Demo), (obsid2, None, DM-990908-2774, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 15.0, <15, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo2 vattenverk. specifik provplats: Demo)])'''
        print(reference_string)
        print(test_string)
        assert test_string == reference_string


    def test_interlab4_connection_table_with_provtagningsorsak(self):

        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('DV')''')

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('obsid1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('obsid2')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('anobsid')''')

        db_utils.sql_alter_db('''INSERT INTO interlab4_obsid_assignment (specifik_provplats, provplatsnamn, obsid) VALUES ('Demo', 'Demo1 vattenverk', 'obsid1')''')
        db_utils.sql_alter_db('''INSERT INTO interlab4_obsid_assignment (specifik_provplats, provplatsnamn, obsid) VALUES ('Demo', 'Demo1 vattenverk', 'obsid2')''')


        interlab4_lines = (
            '#Interlab',
            '#Version=4.0',
            '#Tecken=UTF-8',
            '#Textavgränsare=Nej',
            '#Decimaltecken=,',
            '#Provadm',
            'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;;Demo1 vattenverk;Demo;;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            'DM-990908-2774;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;;Demo2 vattenverk;Demo;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            '#Provdat',
            'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            'DM-990908-2774;SS-EN ISO 7887-1/4;Kalium;<15;15;;mg/l Pt;;;;;;;',
            '#Slut'
                )

        with utils.tempinput('\n'.join(interlab4_lines), 'utf-8') as filename:
            @mock.patch('midvatten_utils.NotFoundQuestion')
            @mock.patch('import_data_to_db.utils.Askuser', mocks_for_tests.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.qgis.PyQt.QtWidgets.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                mock_not_found_question.return_value.answer = 'ok'
                mock_not_found_question.return_value.value = 'anobsid'
                mock_not_found_question.return_value.reuse_column = 'obsid'
                mock_filenames.return_value = [[filename]]
                importer = Interlab4Import(self.iface.mainWindow(), self.midvatten.ms)
                importer.parse_observations_and_populate_gui()
                importer.use_obsid_assignment_table.setChecked(True)
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT * FROM w_qual_lab'''))

        reference_string = r'''(True, [(obsid1, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 2.5, <2,5, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo1 vattenverk. specifik provplats: Demo), (obsid1, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium (dubblett 1), 1.0, <1, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo1 vattenverk. specifik provplats: Demo), (anobsid, None, DM-990908-2774, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 15.0, <15, mg/l Pt, provtagningsorsak: Föreskriven regelbunden undersökning enligt SLVFS 2001:30. provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo2 vattenverk. specifik provplats: Demo)])'''
        print(reference_string)
        print(test_string)
        assert test_string == reference_string


    def test_interlab4_connection_table_only_1(self):

        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('DV')''')

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('obsid1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('obsid2')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('anobsid')''')

        db_utils.sql_alter_db('''INSERT INTO interlab4_obsid_assignment (specifik_provplats, provplatsnamn, obsid) VALUES ('Demo', 'Demo1 vattenverk', 'obsid1')''')


        interlab4_lines = (
            '#Interlab',
            '#Version=4.0',
            '#Tecken=UTF-8',
            '#Textavgränsare=Nej',
            '#Decimaltecken=,',
            '#Provadm',
            'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;;Demo1 vattenverk;Demo;;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            'DM-990908-2774;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;;Demo2 vattenverk;Demo;;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            '#Provdat',
            'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<2,5;2,5;;mg/l Pt;;;;;;;',
            'DM-990908-2773;SS-EN ISO 7887-1/4;Kalium;<1;1;;mg/l Pt;;;;;;;',
            'DM-990908-2774;SS-EN ISO 7887-1/4;Kalium;<15;15;;mg/l Pt;;;;;;;',
            '#Slut'
                )

        with utils.tempinput('\n'.join(interlab4_lines), 'utf-8') as filename:
            @mock.patch('midvatten_utils.NotFoundQuestion')
            @mock.patch('import_data_to_db.utils.Askuser', mocks_for_tests.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.qgis.PyQt.QtWidgets.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                mock_not_found_question.return_value.answer = 'ok'
                mock_not_found_question.return_value.value = 'anobsid'
                mock_not_found_question.return_value.reuse_column = 'obsid'
                mock_filenames.return_value = [[filename]]
                importer = Interlab4Import(self.iface.mainWindow(), self.midvatten.ms)
                importer.parse_observations_and_populate_gui()
                importer.use_obsid_assignment_table.setChecked(True)
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT * FROM w_qual_lab'''))

        reference_string = r'''(True, [(obsid1, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 2.5, <2,5, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo1 vattenverk. specifik provplats: Demo), (obsid1, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium (dubblett 1), 1.0, <1, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo1 vattenverk. specifik provplats: Demo), (anobsid, None, DM-990908-2774, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 15.0, <15, mg/l Pt, provtyp: Dricksvatten enligt SLVFS 2001:30. provtypspecifikation: Utgående. bedömning: Nej. kemisk bedömning: Tjänligt. provplatsnamn: Demo2 vattenverk. specifik provplats: Demo)])'''
        print(reference_string)
        print(test_string)
        assert test_string == reference_string

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT * FROM interlab4_obsid_assignment'''))
        reference_string = '(True, [(Demo, Demo1 vattenverk, obsid1), (Demo, Demo2 vattenverk, anobsid)])'
        assert test_string == reference_string



