# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles often used
 utilities.

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
import midvatten_utils as utils
import mock
from mock import call
from midvatten.midvatten import midvatten
from import_data_to_db import midv_data_importer
import utils_for_tests
from utils_for_tests import create_test_string
from mocks_for_tests import MockNotFoundQuestion, MockUsingReturnValue, MockQgsProjectInstance, MockQgisUtilsIface, MockReturnUsingDictIn, DummyInterface2, mock_answer
import io
import os

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]
MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)


class TestFilterNonexistingObsidsAndAsk(object):
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_ok(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'ok'
            mock_notfound.return_value.value = 10
            mock_notfound.return_value.reuse_column = u'obsid'
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'10', u'b'], [u'10', u'h']]
            assert filtered_file_data == reference_list

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_cancel(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'cancel'
            mock_notfound.return_value.value = 10
            mock_notfound.return_value.reuse_column = u'obsid'
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            assert filtered_file_data == u'cancel'

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_skip(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'skip'
            mock_notfound.return_value.value = 10
            mock_notfound.return_value.reuse_column = u'obsid'
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g']]
            assert filtered_file_data == reference_list

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_none_value_skip(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'skip'
            mock_notfound.return_value.value = 10
            mock_notfound.return_value.reuse_column = u'obsid'
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [None, u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g']]
            assert filtered_file_data == reference_list

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_header_not_found(self, mock_notfound, mock_iface):
        """If a asked for header column is not found, it's added to the end of the rows."""
        mock_notfound.return_value.answer = u'ok'
        mock_notfound.return_value.value = 10
        mock_notfound.return_value.reuse_column = u'obsid'
        file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
        existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
        filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'header_that_should_not_exist', existing_obsids)
        reference_list = [[u'obsid', u'ae', u'header_that_should_not_exist'], [u'1', u'b', u'10'], [u'2', u'c', u'10'], [u'3', u'd', u'10'], [u'10', u'e', u'10'], [u'1_g', u'f', u'10'], [u'1 a', u'g', u'10'], [u'21', u'h', u'10']]
        assert filtered_file_data == reference_list

    @mock.patch('qgis.utils.iface', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_header_capitalize(self, mock_iface):
            file_data = [[u'obsid', u'ae'], [u'a', u'b'], [u'2', u'c']]
            existing_obsids = [u'A', u'2']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data=file_data, header_value=u'obsid', existing_values=existing_obsids, try_capitalize=True, always_ask_user=False)
            reference_list = [[u'obsid', u'ae'], [u'A', u'b'], [u'2', u'c']]
            assert filtered_file_data == reference_list

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_only_ask_once(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'ok'
            mock_notfound.return_value.value = 10
            mock_notfound.return_value.reuse_column = u'obsid'
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h'], [u'1', u'i']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'10', u'b'], [u'10', u'h'], [u'10', u'i']]
            assert filtered_file_data == reference_list
            #The mock should only be called twice. First for 1, then for 21, and then 1 again should use the already given answer.
            assert len(mock_notfound.mock_calls) == 2

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.NotFoundQuestion', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_skip_only_ask_once(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'skip'
            mock_notfound.return_value.value = 10
            mock_notfound.return_value.reuse_column = u'obsid'
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h'], [u'1', u'i']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g']]
            assert filtered_file_data == reference_list
            #The mock should only be called twice. First for 1, then for 21, and then 1 again should use the already given answer.
            assert len(mock_notfound.mock_calls) == 2


class TestTempinput(object):
    def test_tempinput(self):
        rows = u'543\n21'
        with utils.tempinput(rows) as filename:
            with io.open(filename, 'r', encoding=u'utf-8') as f:
                res = f.readlines()
        reference_list = [u'543\n', u'21']
        assert res == reference_list


class TestAskUser(object):
    PyQt4_QtGui_QInputDialog_getText = MockUsingReturnValue([u'-1 hours'])
    cancel = MockUsingReturnValue([u''])

    @mock.patch('PyQt4.QtGui.QInputDialog.getText', PyQt4_QtGui_QInputDialog_getText.get_v)
    def test_askuser_dateshift(self):
        question = utils.askuser('DateShift')
        assert question.result == ['-1', 'hours']

    @mock.patch('PyQt4.QtGui.QInputDialog.getText', cancel.get_v)
    def test_askuser_dateshift_cancel(self):
        question = utils.askuser('DateShift')
        assert question.result == u'cancel'


class TestGetFunctions(object):
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
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
        mock_qgsproject_instance.return_value.instance.readEntry.return_value = [u'en_US']

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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_get_last_logger_dates(self):
        utils.sql_alter_db('''insert into obs_points (obsid) values ('rb1')''')
        utils.sql_alter_db('''insert into obs_points (obsid) values ('rb2')''')
        utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb1', '2015-01-01 00:00')''')
        utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb1', '2015-01-01 00:00:00')''')
        utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb1', '2014-01-01 00:00:00')''')
        utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb2', '2013-01-01 00:00:00')''')
        utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb2', '2016-01-01 00:00')''')

        test_string = create_test_string(utils.get_last_logger_dates())
        reference_string = u'''{rb1: [(2015-01-01 00:00:00)], rb2: [(2016-01-01 00:00)]}'''
        assert test_string == reference_string


class TestSqlToParametersUnitsTuple(object):
    @mock.patch('midvatten_utils.sql_load_fr_db', autospec=True)
    def test_sql_to_parameters_units_tuple(self, mock_sqlload):
        mock_sqlload.return_value = (True, [(u'par1', u'un1'), (u'par2', u'un2')])

        test_string = create_test_string(utils.sql_to_parameters_units_tuple(u'sql'))
        reference_string = u'''((par1, (un1)), (par2, (un2)))'''
        assert test_string == reference_string


class TestCalculateDbTableRows(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_get_db_statistics(self, mock_iface):
        """
        Test that calculate_db_table_rows can be run without major error
        :param mock_iface:
        :return:
        """
        utils.calculate_db_table_rows()

        calls = [str(call) for call in mock_iface.mock_calls]

        assert """call.messageBar().createMessage(u'Some sql failure, see log for additional info.')""" not in calls
        assert """call.messageBar().createMessage(u'Calculation done, see log for results.')""" in calls


class TestGetCurrentLocale(object):
    @mock.patch('locale.getdefaultlocale')
    @mock.patch('midvatten_utils.get_locale_from_db')
    def test_getcurrentlocale(self, mock_get_locale, mock_default_locale):
        mock_get_locale.return_value = u'a_lang'
        mock_default_locale.return_value = [None, u'an_enc']

        test_string = create_test_string(utils.getcurrentlocale())
        reference_string = u'[a_lang, an_enc]'
        assert test_string == reference_string
        

class TestGetDelimiter(object):
    def test_get_delimiter_only_one_column(self):
        file = [u'obsid',
                 u'rb1']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('midvatten_utils.ask_for_delimiter')
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface, mock_delimiter_question):
                mock_delimiter_question.return_value = (u';', True)
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert delimiter == u';'
            _test(filename)

    def test_get_delimiter_delimiter_not_found(self):
        file = [u'obsid;acol,acol2',
                 u'rb1;1,2']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('midvatten_utils.ask_for_delimiter')
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface, mock_delimiter_question):
                mock_delimiter_question.return_value = (u',', True)
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert delimiter == u','
            _test(filename)

    def test_get_delimiter_semicolon(self):
        file = [u'obsid;acol;acol2',
                 u'rb1;1;2']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('midvatten_utils.ask_for_delimiter')
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface, mock_delimiter_question):
                mock_delimiter_question.return_value = (u';', True)
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert delimiter == u';'
            _test(filename)

    def test_get_delimiter_comma(self):
        file = [u'obsid,acol,acol2',
                 u'rb1,1,2']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('midvatten_utils.ask_for_delimiter')
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface, mock_delimiter_question):
                mock_delimiter_question.return_value = (u',', True)
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert delimiter == u','
            _test(filename)
