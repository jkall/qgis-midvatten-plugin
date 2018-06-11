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
        super(self.__class__, self).setUp()
        self.importinstance = Interlab4Import(self.iface.mainWindow(), self.ms)

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_interlab4_full_test_to_db(self):

        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('DV')''')

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('anobsid')''')

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
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            @mock.patch('import_data_to_db.utils.Askuser', mocks_for_tests.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileNames')
            def _test(self, filename, mock_filenames, mock_skippopup, mock_iface, mock_not_found_question):
                mock_not_found_question.return_value.answer = u'ok'
                mock_not_found_question.return_value.value = u'anobsid'
                mock_not_found_question.return_value.reuse_column = u'obsid'
                mock_filenames.return_value = [filename]
                importer = Interlab4Import(self.iface.mainWindow(), self.ms)
                importer.parse_observations_and_populate_gui()
                importer.start_import(importer.all_lab_results, importer.metadata_filter.get_selected_lablitteras())

            _test(self, filename)

        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT * FROM w_qual_lab'''))
        reference_string = ur'''(True, [(anobsid, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Kalium, 1.0, <1, mg/l Pt, provtagningsorsak: Dricksvatten enligt SLVFS 2001:30. provtyp: Utgående. provtypspecifikation: Nej. bedömning: Tjänligt. provplatsid: Demo1 vattenverk. specifik provplats: Föreskriven regelbunden undersökning enligt SLVFS 2001:30)])'''
        assert test_string == reference_string


