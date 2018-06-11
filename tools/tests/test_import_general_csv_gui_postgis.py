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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
import qgis.PyQt
import datetime
#
import timeit
from collections import OrderedDict

import db_utils
import midvatten_utils as utils
import mock
from date_utils import datestring_to_date
from import_general_csv_gui import GeneralCsvImportGui
from mock import MagicMock
from nose.plugins.attrib import attr

import utils_for_tests
from .mocks_for_tests import MockUsingReturnValue


@attr(status='on')
class TestGeneralCsvGui(utils_for_tests.MidvattenTestPostgisDbSv):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_obs_points(self):
        file = [u'obsid,testcol',
                 u'rb1,test']

        #utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'obs_points'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid FROM obs_points'''))
                    reference_string = r'''(True, [(rb1)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_obsid_not_in_db(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfound):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        mock_notfound.return_value.answer = u'ok'
                        mock_notfound.return_value.value = u'rb2'
                        mock_notfound.return_value.reuse_column = u'obsid'

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb2, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_vlf_data_obsid_not_in_db(self):
        file = [u'obsid,length2,real_comp,imag_comp,comment',
                u'obsid2,500,2,10,acomment']

        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid) VALUES ('obsid1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfound):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        mock_notfound.return_value.answer = u'ok'
                        mock_notfound.return_value.value = u'obsid1'
                        mock_notfound.return_value.reuse_column = u'obsid'

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'vlf_data'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'length': u'length2', u'real_comp': u'real_comp', u'imag_comp': u'imag_comp', u'comment': u'comment'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT * FROM vlf_data'''))
                    reference_string = u'''(True, [(obsid1, 500.0, 2.0, 10.0, acomment)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_no_header(self):
        file = [u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 0
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'Column 0', u'date_time': u'Column 1', u'meas': u'Column 2'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_many_rows(self):
        file = [u'obsid,date_time,meas']
        base = datestring_to_date(u'1900-01-01 00:01:01')
        date_list = [base + datetime.timedelta(days=x) for x in range(0, 10000)]
        file.extend([u'rb1,' + datetime.datetime.strftime(adate, u'%Y%m%d %H%M') + u',0.5' for adate in date_list])

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        import_time = timeit.timeit(importer.start_import, number=1)
                        return import_time

                    import_time = _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT count(*) FROM w_levels'''))
                    reference_string = r'''(True, [(10000)])'''
                    assert import_time < 10
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_obsid_from_selection_obsidcol_existed(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.get_selected_features_as_tuple')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_selectedobsids):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        mock_selectedobsids.return_value = (u'rb2', )

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]
                            if column.db_column == u'obsid':
                                column.obsids_from_selection.setChecked(True)

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb2, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_obsid_from_selection(self):
        file = [u'date_time,meas',
                 u'2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.get_selected_features_as_tuple')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_selectedobsids):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        mock_selectedobsids.return_value = (u'rb1', )

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]
                            if column.db_column == u'obsid':
                                column.obsids_from_selection.setChecked(True)

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_meteo_two_header_columns_same_name(self):
        file = [u'obsid,instrumentid,parameter,date_time,reading_num,reading_num,aunit',
                 u'rb1,inst1,precip,2016-03-15 10:30:00,5.0,6.0,cm(H2O)']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'meteo'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'instrumentid': u'instrumentid', u'parameter': u'parameter', u'date_time': u'date_time', u'reading_num': u'reading_num', u'reading_txt': u'reading_num', u'unit': u'aunit'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''select obsid, instrumentid, parameter, date_time, reading_num, reading_txt, unit, comment from meteo'''))
                    reference_string = u'''(True, [(rb1, inst1, precip, 2016-03-15 10:30:00, 5.0, 5.0, cm(H2O), None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_comma_decimal_separator(self):
        file = [u'obsid;date_time;meas',
                 u'rb1;2016-03-15 10:30:00;5,0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_convert_comma_to_point(self):
        file = [u'obsid;date_time;meas',
                 u'rb1;2016-03-15 10:30:00;5,0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_static_value(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas', u'comment': u'a comment' }
                            if column.db_column in names:
                                if column.db_column == u'comment':
                                    column.static_checkbox.setChecked(True)
                                column.file_column_name = names[column.db_column]


                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, a comment)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_slash_in_date_time(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016/03/15 10:30,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_remove_preceeding_trailing_spaces_tabs(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00 ,\t5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_file_twice(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.MessagebarAndLog')
                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_messagebar):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.close_after_import.setChecked(False)
                        importer.start_import()
                        importer.start_import()

                        print(str(mock_messagebar.mock_calls))

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_w_levels_factor(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if u'msg' in kwargs:
                                if kwargs[u'msg'].startswith(u'Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith(u'Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith(u'Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith(u'It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = u'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {u'obsid': u'obsid', u'date_time': u'date_time', u'meas': u'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]
                            if column.db_column == u'meas':
                                column.factor = 2.5

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 12.5, None, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string