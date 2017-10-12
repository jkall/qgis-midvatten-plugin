# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  diveroffice files.

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

import os
from collections import OrderedDict

import midvatten_utils as utils
import mock
from date_utils import datestring_to_date
from import_diveroffice import DiverofficeImport
from midvatten.midvatten import midvatten
from mock import MagicMock
import db_utils
from nose.plugins.attrib import attr

import utils_for_tests
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDictIn, MockQgisUtilsIface, MockQgsProjectInstance, \
    DummyInterface2, mock_answer


class TestWlvllogImportFromDiverofficeFiles(utils_for_tests.MidvattenTestSpatialiteDbSvImportInstance):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """

    @attr(status='on')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)


                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_skip_duplicate_datetimes(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:30', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_filter_dates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_all_dates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_try_capitalize(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = u'ok'
                mock_notfoundquestion.return_value.value = u'rb1'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = DiverofficeImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()
                importer.import_all_data.checked = False
                importer.confirm_names.checked = False
                importer.start_import(importer.files,
                                      importer.skip_rows.checked,
                                      importer.confirm_names.checked,
                                      importer.import_all_data.checked)

            _test_wlvllogg_import_from_diveroffice_files(self, filenames)

            test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
            reference_string = ur'''(True, [(Rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (Rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None)])'''
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_cancel(self):
        files = [(u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = u'cancel'
                mock_notfoundquestion.return_value.value = u'rb1'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = DiverofficeImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()
                importer.import_all_data.checked = True
                importer.confirm_names.checked = False
                answer = importer.start_import(importer.files,
                                      importer.skip_rows.checked,
                                      importer.confirm_names.checked,
                                      importer.import_all_data.checked)

                return answer

            answer = _test_wlvllogg_import_from_diveroffice_files(self, filenames)
            assert isinstance(answer, utils.Cancel)

            test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
            reference_string = ur'''(True, [])'''
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_skip_missing_water_level(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(),
                                                     ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.skip_rows.checked = True
                        importer.start_import(importer.files,
                                              importer.skip_rows.checked,
                                              importer.confirm_names.checked,
                                              importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_not_skip_missing_water_level(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(),
                                                     ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.skip_rows.checked = False
                        importer.start_import(importer.files,
                                              importer.skip_rows.checked,
                                              importer.confirm_names.checked,
                                              importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self,
                                                                 filenames)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))

                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, None, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_datetime_filter(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101',
                u'2016/06/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:

                filenames = [f1, f2]


                @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                @mock.patch('import_data_to_db.utils.Askuser')
                @mock.patch('qgis.utils.iface', autospec=True)
                @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                @mock.patch('import_data_to_db.utils.select_files')
                def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                    mock_notfoundquestion.return_value.answer = u'ok'
                    mock_notfoundquestion.return_value.value = u'rb1'
                    mock_notfoundquestion.return_value.reuse_column = u'location'
                    mock_filenames.return_value = filenames
                    mock_encoding.return_value = [u'utf-8']

                    ms = MagicMock()
                    ms.settingsdict = OrderedDict()
                    importer = DiverofficeImport(self.iface.mainWindow(), ms)
                    importer.select_files_and_load_gui()
                    importer.import_all_data.checked = True
                    importer.confirm_names.checked = False
                    importer.date_time_filter.from_date = u'2016-03-15 11:00:00'
                    importer.date_time_filter.to_date = u'2016-04-15 10:30:00'
                    importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked,  importer.date_time_filter.from_date, importer.date_time_filter.to_date)

                _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None)])'''
                assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_skip_obsid(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch("midvatten_utils.MessagebarAndLog")
                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebarandlog):

                        mocks_notfoundquestion = []
                        for answer, value in [[u'ok', u'rb1'],
                                              [u'ok', u'rb2'],
                                              [u'skip', u'rb3']]:
                            a_mock = MagicMock()
                            a_mock.answer = answer
                            a_mock.value = value
                            a_mock.reuse_column = u'location'
                            mocks_notfoundquestion.append(a_mock)

                        mock_notfoundquestion.side_effect = mocks_notfoundquestion

                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                        print(u'\n'.join([str(x) for x in mock_messagebarandlog.mock_calls]))


                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None)])'''
                    print(test_string)
                    print(reference_string)
                    assert test_string == reference_string