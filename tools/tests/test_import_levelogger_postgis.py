# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  levelogger files.

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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
#

from collections import OrderedDict

import db_utils
import midvatten_utils as utils
import mock
from import_levelogger import LeveloggerImport
from mock import MagicMock
from nose.plugins.attrib import attr

import utils_for_tests
from .mocks_for_tests import MockUsingReturnValue


@attr(status='on')
class TestWlvllogImportFromLeveloggerFiles(utils_for_tests.MidvattenTestPostgisDbSv):
    """ Test to make sure levelogger goes all the way to the end without errors
    """
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files(self):

        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebar):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        try:
                            importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)
                        except:
                            print(str(mock_messagebar.mock_calls))
                            raise

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_skip_duplicate_datetimes(self):
        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:30', '5.0')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_filter_dates(self):
        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_all_dates(self):
        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_try_capitalize(self):
        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
            @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = u'ok'
                mock_notfoundquestion.return_value.value = u'rb1'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = LeveloggerImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()
                importer.import_all_data.checked = False
                importer.confirm_names.checked = False
                importer.start_import(importer.files,
                                      importer.skip_rows.checked,
                                      importer.confirm_names.checked,
                                      importer.import_all_data.checked)

            _test_wlvllogg_import_from_levelogger_files(self, filenames)

            test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
            reference_string = r'''(True, [(Rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (Rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None)])'''
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_cancel(self):

        files = [
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-03-15;10:30:00;0;1;20',
                  u'2016-03-15;11:00:00;0;11;101'),
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
            @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = u'cancel'
                mock_notfoundquestion.return_value.value = u'rb1'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = LeveloggerImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()
                importer.import_all_data.checked = True
                importer.confirm_names.checked = False
                answer = importer.start_import(importer.files,
                                      importer.skip_rows.checked,
                                      importer.confirm_names.checked,
                                      importer.import_all_data.checked)

                return answer

            answer = _test_wlvllogg_import_from_levelogger_files(self, filenames)


            test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
            reference_string = r'''(True, [])'''
            print(str(test_string))
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_skip_missing_water_level(self):

        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(),
                                                     ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.skip_rows.checked = True
                        importer.start_import(importer.files,
                                              importer.skip_rows.checked,
                                              importer.confirm_names.checked,
                                              importer.import_all_data.checked)

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    print(str(test_string))
                    print(reference_string)
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_not_skip_missing_water_level(self):
        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(),
                                                     ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.skip_rows.checked = False
                        importer.start_import(importer.files,
                                              importer.skip_rows.checked,
                                              importer.confirm_names.checked,
                                              importer.import_all_data.checked)

                    _test_wlvllogg_import_from_levelogger_files(self,
                                                                 filenames)

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))

                    reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, None, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_datetime_filter(self):
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

        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101',
                    u'2016-06-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:

                filenames = [f1, f2]


                @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                @mock.patch('import_data_to_db.utils.Askuser')
                @mock.patch('qgis.utils.iface', autospec=True)
                @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                @mock.patch('import_data_to_db.utils.select_files')
                def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                    mock_notfoundquestion.return_value.answer = u'ok'
                    mock_notfoundquestion.return_value.value = u'rb1'
                    mock_notfoundquestion.return_value.reuse_column = u'location'
                    mock_filenames.return_value = filenames
                    mock_encoding.return_value = [u'utf-8']

                    ms = MagicMock()
                    ms.settingsdict = OrderedDict()
                    importer = LeveloggerImport(self.iface.mainWindow(), ms)
                    importer.select_files_and_load_gui()
                    importer.import_all_data.checked = True
                    importer.confirm_names.checked = False
                    importer.date_time_filter.from_date = u'2016-03-15 11:00:00'
                    importer.date_time_filter.to_date = u'2016-04-15 10:30:00'
                    importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked,  importer.date_time_filter.from_date, importer.date_time_filter.to_date)

                _test_wlvllogg_import_from_levelogger_files(self, filenames)

                test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                reference_string = r'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None)])'''
                print(str(test_string))
                assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_skip_obsid(self):
        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: cm;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch("midvatten_utils.MessagebarAndLog")
                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebarandlog):

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
                        importer = LeveloggerImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                        print(u'\n'.join([str(x) for x in mock_messagebarandlog.mock_calls]))


                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None)])'''
                    print(test_string)
                    print(reference_string)
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_level_as_m(self):

        files = [(u'Serial_number:;;;;;;',
                    u'123;;;;;;',
                    u'Project ID:;;;;;;',
                    u'Projname;;;;;;',
                    u'Location:;;;;;;',
                    u'rb1;;;;;;',
                    u'LEVEL;;;;;;',
                    u'UNIT: m;;;;;;',
                    u'Offset: 0.000000 m;;;;;;',
                    u'Altitude: 0.000000 m;;;;;;',
                    u'Density: 1.000000 kg/L;;;;;;',
                    u'TEMPERATURE;;;;;;',
                    u'UNIT: Deg C;;;;;;',
                    u'Date;Time;ms;LEVEL;TEMPERATURE',
                    u'2016-03-15;10:30:00;0;1;10',
                    u'2016-03-15;11:00:00;0;11;101'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb2;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE',
                  u'2016-04-15;10:30:00;0;2;20',
                  u'2016-04-15;11:00:00;0;21;201'),
                 (u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (mS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5',
                  u'2016-05-15;11:00:00;0;31;301;6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), LeveloggerImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), LeveloggerImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebar):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = LeveloggerImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        try:
                            importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)
                        except:
                            print(str(mock_messagebar.mock_calls))
                            raise

                    _test_wlvllogg_import_from_levelogger_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 100.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 1100.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_wlvllogg_import_from_levelogger_files_cond_as_uscm(self):

        files = [(u'Serial_number:;;;;;;',
                  u'123;;;;;;',
                  u'Project ID:;;;;;;',
                  u'Projname;;;;;;',
                  u'Location:;;;;;;',
                  u'rb3;;;;;;',
                  u'LEVEL;;;;;;',
                  u'UNIT: cm;;;;;;',
                  u'Offset: 0.000000 m;;;;;;',
                  u'Altitude: 0.000000 m;;;;;;',
                  u'Density: 1.000000 kg/L;;;;;;',
                  u'TEMPERATURE;;;;;;',
                  u'UNIT: Deg C;;;;;;',
                  u'Date;Time;ms;LEVEL;TEMPERATURE;spec. conductivity (uS/cm)',
                  u'2016-05-15;10:30:00;0;3;30;5000',
                  u'2016-05-15;11:00:00;0;31;301;6000')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')

        LeveloggerImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), LeveloggerImport.charsetchoosen) as f1:


            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
            @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtWidgets.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_levelogger_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebar):
                mock_notfoundquestion.return_value.answer = u'ok'
                mock_notfoundquestion.return_value.value = u'rb3'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = LeveloggerImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()

                try:
                    importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)
                except:
                    print(str(mock_messagebar.mock_calls))
                    raise

            _test_wlvllogg_import_from_levelogger_files(self, filenames)

            test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger'''))
            reference_string = r'''(True, [(rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
            print(str(test_string))
            assert test_string == reference_string