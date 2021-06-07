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
from __future__ import print_function

import datetime
import timeit
from builtins import range
from builtins import str
from collections import OrderedDict

import mock
import qgis.PyQt
from mock import MagicMock
from nose.plugins.attrib import attr
from qgis.core import QgsProject, QgsVectorLayer

from midvatten.tools.utils import common_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.tests.mocks_for_tests import MockUsingReturnValue
from midvatten.tools.utils.date_utils import datestring_to_date
from midvatten.tools.import_general_csv_gui import GeneralCsvImportGui


@attr(status='on')
class TestGeneralCsvGui(utils_for_tests.MidvattenTestSpatialiteDbSv):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """

    def test_import_w_levels(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string


    def test_import_obs_points(self):
        file = ['obsid,testcol',
                 'rb1,test']

        #utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'obs_points'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid FROM obs_points'''))
                    reference_string = r'''(True, [(rb1)])'''
                    assert test_string == reference_string


    def test_import_w_levels_obsid_not_in_db(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('midvatten.tools.utils.midvatten_utils.NotFoundQuestion', autospec=True)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfound):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        mock_notfound.return_value.answer = 'ok'
                        mock_checkbox = mock.Mock()
                        mock_checkbox.return_value.isChecked.return_value = True
                        mock_notfound.return_value.ignore_checkbox = mock_checkbox
                        mock_notfound.return_value.value = 'rb2'
                        mock_notfound.return_value.reuse_column = 'obsid'

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb2, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_vlf_data_obsid_not_in_db(self):
        file = ['obsid,length2,real_comp,imag_comp,comment',
                'obsid2,500,2,10,acomment']

        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('obsid1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('midvatten.tools.utils.midvatten_utils.NotFoundQuestion', autospec=True)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfound):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        mock_notfound.return_value.answer = 'ok'
                        mock_checkbox = mock.Mock()
                        mock_checkbox.return_value.isChecked.return_value = True
                        mock_notfound.return_value.ignore_checkbox = mock_checkbox
                        mock_notfound.return_value.value = 'obsid1'
                        mock_notfound.return_value.reuse_column = 'obsid'

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'vlf_data'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'length': 'length2', 'real_comp': 'real_comp', 'imag_comp': 'imag_comp', 'comment': 'comment'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT * FROM vlf_data'''))
                    reference_string = '''(True, [(obsid1, 500.0, 2.0, 10.0, acomment)])'''
                    assert test_string == reference_string


    def test_import_w_levels_no_header(self):
        file = ['rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 0
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'Column 0', 'date_time': 'Column 1', 'meas': 'Column 2'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_many_rows(self):
        file = ['obsid,date_time,meas']
        base = datestring_to_date('1900-01-01 00:01:01')
        date_list = [base + datetime.timedelta(days=x) for x in range(0, 10000)]
        file.extend(['rb1,' + datetime.datetime.strftime(adate, '%Y%m%d %H%M') + ',0.5' for adate in date_list])

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        import_time = timeit.timeit(importer.start_import, number=1)
                        return import_time

                    import_time = _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT count(*) FROM w_levels'''))
                    reference_string = r'''(True, [(10000)])'''
                    assert import_time < 10
                    assert test_string == reference_string


    def test_import_w_levels_obsid_from_selection_obsidcol_existed(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple')
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_selectedobsids):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        mock_selectedobsids.return_value = ('rb2', )

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]
                            if column.db_column == 'obsid':
                                column.obsids_from_selection.setChecked(True)

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb2, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_obsid_from_selection(self):
        file = ['date_time,meas',
                 '2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple')
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_selectedobsids):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        mock_selectedobsids.return_value = ('rb1', )

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]
                            if column.db_column == 'obsid':
                                column.obsids_from_selection.setChecked(True)

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_meteo_two_header_columns_same_name(self):
        file = ['obsid,instrumentid,parameter,date_time,reading_num,reading_num,aunit',
                 'rb1,inst1,precip,2016-03-15 10:30:00,5.0,6.0,cm(H2O)']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'meteo'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'instrumentid': 'instrumentid', 'parameter': 'parameter', 'date_time': 'date_time', 'reading_num': 'reading_num', 'reading_txt': 'reading_num', 'unit': 'aunit'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''select obsid, instrumentid, parameter, date_time, reading_num, reading_txt, unit, comment from meteo'''))
                    reference_string = '''(True, [(rb1, inst1, precip, 2016-03-15 10:30:00, 5.0, 5.0, cm(H2O), None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_comma_decimal_separator(self):
        file = ['obsid;date_time;meas',
                 'rb1;2016-03-15 10:30:00;5,0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_convert_comma_to_point(self):
        file = ['obsid;date_time;meas',
                 'rb1;2016-03-15 10:30:00;5,0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_static_value(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas', 'comment': 'a comment' }
                            if column.db_column in names:
                                if column.db_column == 'comment':
                                    column.static_checkbox.setChecked(True)
                                column.file_column_name = names[column.db_column]


                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, a comment)])'''
                    assert test_string == reference_string


    def test_import_w_levels_slash_in_date_time(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016/03/15 10:30,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_remove_preceeding_trailing_spaces_tabs(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00 ,\t5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string


    def test_import_w_levels_file_twice(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_messagebar):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]

                        importer.close_after_import.setChecked(False)
                        importer.start_import()
                        importer.start_import()

                        print(str(mock_messagebar.mock_calls))

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string


    def test_import_w_levels_factor(self):
        file = ['obsid,date_time,meas',
                 'rb1,2016-03-15 10:30:00,5.0']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        with common_utils.tempinput('\n'.join(file), 'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('qgis.PyQt.QtWidgets.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(qgis.PyQt.QtWidgets.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):

                        mock_filename.return_value = [filename]
                        mock_encoding.return_value = ['utf-8', True]

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if 'msg' in kwargs:
                                if kwargs['msg'].startswith('Does the file contain a header?'):
                                    mock_result.result = 1
                                    return mock_result
                            if len(args) > 1:
                                if args[1].startswith('Do you want to confirm'):
                                    mock_result.result = 0
                                    return mock_result
                                    #mock_askuser.return_value.result.return_value = 0
                                elif args[1].startswith('Do you want to import all'):
                                    mock_result.result = 0
                                    return mock_result
                                elif args[1].startswith('Please note!\nForeign keys'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('Please note!\nThere are'):
                                    mock_result.result = 1
                                    return mock_result
                                elif args[1].startswith('It is a strong recommendation'):
                                    mock_result.result = 0
                                    return mock_result
                        mock_askuser.side_effect = side_effect

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
                        importer.load_gui()

                        importer.load_files()
                        importer.table_chooser.import_method = 'w_levels'

                        for column in importer.table_chooser.columns:
                            names = {'obsid': 'obsid', 'date_time': 'date_time', 'meas': 'meas'}
                            if column.db_column in names:
                                column.file_column_name = names[column.db_column]
                            if column.db_column == 'meas':
                                column.factor = 2.5

                        importer.start_import()

                    _test(self, filename)
                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db('''SELECT obsid, date_time, meas, h_toc, level_masl, comment FROM w_levels'''))
                    reference_string = r'''(True, [(rb1, 2016-03-15 10:30:00, 12.5, None, None, None)])'''
                    print(str(test_string))
                    assert test_string == reference_string


@attr(status='on')
class TestGeneralCsvGuiFromLayer(utils_for_tests.MidvattenTestSpatialiteDbSv):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """

    def create_and_select_vlayer(self):


        self.midvatten.ms.settingsdict['secplotdrillstop'] = "%berg%"

        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource('', 'obs_points', 'geometry', '', 'obsid')
        dbtype = db_utils.get_dbtype(dbconnection.dbtype)
        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', dbtype)

        features = self.vlayer.getFeatures()
        feature_ids = [feature.id() for feature in features]
        self.vlayer.selectByIds(feature_ids)
        print("1. feature_ids: " + str(feature_ids))
        print("2. QgsVectorLayer.selectedFeatureIds: " + str(self.vlayer.selectedFeatureIds()))
        print("3. QgsVectorLayer.getSelectedFeatures: " + str([x.id() for x in self.vlayer.getSelectedFeatures()]))
        print("4. QgsVectorLayer.getFeature(): " + str([self.vlayer.getFeature(x).id() for x in feature_ids]))
        print("5. QgsVectorLayer.getFeature() type: " + str([str(type(self.vlayer.getFeature(x))) for x in feature_ids]))
        print("6. QgsVectorLayer.getFeatures(): " + str([x.id() for x in self.vlayer.getFeatures(feature_ids)]))



    def test_import_obs_points_from_layer(self):
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        self.create_and_select_vlayer()

        utils_askuser_answer_no_obj = MockUsingReturnValue(None)
        utils_askuser_answer_no_obj.result = 0
        utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
        @mock.patch('import_data_to_db.utils.Askuser')
        @mock.patch('qgis.utils.iface', autospec=True)
        @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
        def _test(self, mock_skippopup, mock_iface, mock_askuser):

            def side_effect(*args, **kwargs):
                mock_result = mock.MagicMock()
                if 'msg' in kwargs:
                    if kwargs['msg'].startswith('Does the file contain a header?'):
                        mock_result.result = 1
                        return mock_result
                if len(args) > 1:
                    if args[1].startswith('Do you want to confirm'):
                        mock_result.result = 0
                        return mock_result
                        #mock_askuser.return_value.result.return_value = 0
                    elif args[1].startswith('Do you want to import all'):
                        mock_result.result = 0
                        return mock_result
                    elif args[1].startswith('Please note!\nForeign keys'):
                        mock_result.result = 1
                        return mock_result
                    elif args[1].startswith('Please note!\nThere are'):
                        mock_result.result = 1
                        return mock_result
                    elif args[1].startswith('It is a strong recommendation'):
                        mock_result.result = 0
                        return mock_result
            mock_askuser.side_effect = side_effect

            mock_iface.activeLayer.return_value = self.vlayer

            ms = MagicMock()
            ms.settingsdict = OrderedDict()
            importer = GeneralCsvImportGui(self.iface.mainWindow(), ms)
            importer.load_gui()

            importer.import_all_features()
            importer.table_chooser.import_method = 'obs_points'

            for column in importer.table_chooser.columns:
                if column.db_column == 'obsid':
                    column.static_checkbox.setChecked(True)
                    column.file_column_name = '2'
                elif column.db_column in ('east', 'north'):
                    column.file_column_name = None

            importer.start_import()

        _test(self)
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('''SELECT obsid, ST_AsText(geometry) FROM obs_points'''))
        reference_string = r'''(True, [(1, POINT(633466 711659)), (2, POINT(633466 711659))])'''
        print(str(test_string))
        print(str(reference_string))
        assert test_string == reference_string

    def tearDown(self):
        QgsProject.instance().addMapLayer(self.vlayer)
        QgsProject.instance().removeMapLayer(self.vlayer.id())
        super(self.__class__, self).tearDown()