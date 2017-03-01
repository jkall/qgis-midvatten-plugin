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
import timeit
import datetime
import utils_for_tests
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from utils_for_tests import init_test
from tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch, MagicMock, call
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
from midvatten.midvatten import midvatten
import os
import PyQt4
from collections import OrderedDict
from import_data_to_db import midv_data_importer
from import_general_csv_gui import GeneralCsvImportGui

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)

class TestGeneralCsvGui(object):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
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
    def test_import_w_levels(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, meas, h_toc, level_masl, comment from w_levels'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_obs_points(self):
        file = [u'obsid,testcol',
                 u'rb1,test']

        #utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid from obs_points'''))
                    reference_string = ur'''(True, [(rb1)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_w_levels_obsid_not_in_db(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfound):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        mock_notfound.return_value.answer = u'ok'
                        mock_notfound.return_value.value = u'rb2'
                        mock_notfound.return_value.reuse_question = u'obsid'

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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, meas, h_toc, level_masl, comment from w_levels'''))
                    reference_string = ur'''(True, [(rb2, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_vlf_data_obsid_not_in_db(self):
        file = [u'obsid,length2,real_comp,imag_comp,comment',
                u'obsid2,500,2,10,acomment']

        utils.sql_alter_db(u'INSERT INTO obs_lines ("obsid") VALUES ("obsid1")')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfound):

                        mock_filename.return_value = filename
                        mock_encoding.return_value = [u'utf-8', True]

                        mock_notfound.return_value.answer = u'ok'
                        mock_notfound.return_value.value = u'obsid1'
                        mock_notfound.return_value.reuse_question = u'obsid'

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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select * from vlf_data'''))
                    reference_string = u'''(True, [(obsid1, 500.0, 2.0, 10.0, acomment)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_w_levels_no_header(self):
        file = [u'rb1,2016-03-15 10:30:00,5.0']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, meas, h_toc, level_masl, comment from w_levels'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_w_levels_many_rows(self):
        file = [u'obsid,date_time,meas']
        base = datestring_to_date(u'1900-01-01 00:01:01')
        date_list = [base + datetime.timedelta(days=x) for x in range(0, 10000)]
        file.extend([u'rb1,' + datetime.datetime.strftime(adate, u'%Y%m%d %H%M') + u',0.5' for adate in date_list])

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select count(*) from w_levels'''))
                    reference_string = ur'''(True, [(10000)])'''
                    assert import_time < 10
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_w_levels_obsid_from_selection_obsidcol_existed(self):
        file = [u'obsid,date_time,meas',
                 u'rb1,2016-03-15 10:30:00,5.0']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.get_selected_features_as_tuple')
                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, meas, h_toc, level_masl, comment from w_levels'''))
                    reference_string = ur'''(True, [(rb2, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_w_levels_obsid_from_selection(self):
        file = [u'date_time,meas',
                 u'2016-03-15 10:30:00,5.0']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.get_selected_features_as_tuple')
                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, meas, h_toc, level_masl, comment from w_levels'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 5.0, None, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_meteo_two_header_columns_same_name(self):
        file = [u'obsid,instrumentid,parameter,date_time,reading_num,reading_num,aunit',
                 u'rb1,inst1,precip,2016-03-15 10:30:00,5.0,6.0,cm(H2O)']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
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
                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, instrumentid, parameter, date_time, reading_num, reading_txt, unit, comment from meteo'''))
                    reference_string = u'''(True, [(rb1, inst1, precip, 2016-03-15 10:30:00, 5.0, 5.0, cm(H2O), None)])'''
                    assert test_string == reference_string


class TestStaticMethods(object):

    def test_translate_and_reorder_file_data(self):
        file_data = [[u'obsid', u'acol', u'acol2'],
                    [u'rb1', u'1', u'2']]

        translation_dict = {u'obsid': [u'obsid'], u'acol': [u'num', u'txt'], u'acol2': [u'comment']}

        test_string = utils_for_tests.create_test_string(GeneralCsvImportGui.translate_and_reorder_file_data(file_data, translation_dict))
        reference_string = u'[[num, txt, comment, obsid], [1, 1, 2, rb1]]'
        assert test_string == reference_string
