# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  diveroffice files.

 This part is to a big extent based on QPostgis plugin.
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
from __future__ import print_function

from builtins import str
from collections import OrderedDict

import mock

from mock import MagicMock
from nose.plugins.attrib import attr

from midvatten.tools.utils import common_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.tests.mocks_for_tests import MockUsingReturnValue
from midvatten.tools.import_diveroffice import DiverofficeImport


#


@attr(status='on')
class TestWlvllogImportFromDiverofficeFiles(utils_for_tests.MidvattenTestPostgisDbSv):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """


    def test_wlvllogg_import_from_diveroffice_files(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = 'ok'
                        mock_notfoundquestion.return_value.value = 'rb1'
                        mock_notfoundquestion.return_value.reuse_column = 'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)


                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_skip_duplicate_datetimes(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:30', '5.0')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = 'ok'
                        mock_notfoundquestion.return_value.value = 'rb1'
                        mock_notfoundquestion.return_value.reuse_column = 'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_filter_dates(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = 'ok'
                        mock_notfoundquestion.return_value.value = 'rb1'
                        mock_notfoundquestion.return_value.reuse_column = 'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_all_dates(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = 'ok'
                        mock_notfoundquestion.return_value.value = 'rb1'
                        mock_notfoundquestion.return_value.reuse_column = 'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_try_capitalize(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('Rb1')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
            @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
            @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
            @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
            def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = 'ok'
                mock_notfoundquestion.return_value.value = 'rb1'
                mock_notfoundquestion.return_value.reuse_column = 'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = ['utf-8']

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

            test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
            reference_string = r'''(True, [(Rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (Rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None)])'''
            assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_cancel(self):
        files = [('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('Rb1')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
            @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
            @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
            @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
            def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = 'cancel'
                mock_notfoundquestion.return_value.value = 'rb1'
                mock_notfoundquestion.return_value.reuse_column = 'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = ['utf-8']

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

            test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
            reference_string = r'''(True, [])'''
            assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_skip_missing_water_level(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = 'ok'
                        mock_notfoundquestion.return_value.value = 'rb1'
                        mock_notfoundquestion.return_value.reuse_column = 'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

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

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_not_skip_missing_water_level(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = 'ok'
                        mock_notfoundquestion.return_value.value = 'rb1'
                        mock_notfoundquestion.return_value.reuse_column = 'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

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

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))

                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, None, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_datetime_filter(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101',
                '2016/06/15 11:00:00,11,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:

                filenames = [f1, f2]


                @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                @mock.patch('qgis.utils.iface', autospec=True)
                @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                    mock_notfoundquestion.return_value.answer = 'ok'
                    mock_notfoundquestion.return_value.value = 'rb1'
                    mock_notfoundquestion.return_value.reuse_column = 'location'
                    mock_filenames.return_value = filenames
                    mock_encoding.return_value = ['utf-8']

                    ms = MagicMock()
                    ms.settingsdict = OrderedDict()
                    importer = DiverofficeImport(self.iface.mainWindow(), ms)
                    importer.select_files_and_load_gui()
                    importer.import_all_data.checked = True
                    importer.confirm_names.checked = False
                    importer.date_time_filter.from_date = '2016-03-15 11:00:00'
                    importer.date_time_filter.to_date = '2016-04-15 10:30:00'
                    importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked,  importer.date_time_filter.from_date, importer.date_time_filter.to_date)

                _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None)])'''
                assert test_string == reference_string


    def test_wlvllogg_import_from_diveroffice_files_skip_obsid(self):
        files = [('Location=rb1',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/03/15 10:30:00,1,10',
                '2016/03/15 11:00:00,11,101'),
                ('Location=rb2',
                'Date/time,Water head[cm],Temperature[°C]',
                '2016/04/15 10:30:00,2,20',
                '2016/04/15 11:00:00,21,201'),
                ('Location=rb3',
                'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                '2016/05/15 10:30:00,3,30,5',
                '2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')

        DiverofficeImport.charsetchoosen = 'utf-8'
        with common_utils.tempinput('\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with common_utils.tempinput('\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with common_utils.tempinput('\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch("midvatten_utils.MessagebarAndLog")
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.NotFoundQuestion')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('midvatten.tools.import_data_to_db.common_utils.pop_up_info', autospec=True)
                    @mock.patch('midvatten.tools.import_diveroffice.midvatten_utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebarandlog):

                        mocks_notfoundquestion = []
                        for answer, value in [['ok', 'rb1'],
                                              ['ok', 'rb2'],
                                              ['skip', 'rb3']]:
                            a_mock = MagicMock()
                            a_mock.answer = answer
                            a_mock.value = value
                            a_mock.reuse_column = 'location'
                            mocks_notfoundquestion.append(a_mock)

                        mock_notfoundquestion.side_effect = mocks_notfoundquestion

                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = ['utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                        print('\n'.join([str(x) for x in mock_messagebarandlog.mock_calls]))


                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None)])'''
                    print(test_string)
                    print(reference_string)
                    assert test_string == reference_string