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
import io

import db_utils
import midvatten_utils as utils
import mock
import utils_for_tests
from mock import call
from mocks_for_tests import MockUsingReturnValue
from utils_for_tests import create_test_string


class _TestFilterNonexistingObsidsAndAsk(object):
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
    def test_filter_nonexisting_obsids_and_ask_ignore(self, mock_notfound, mock_iface):
            mock_notfound.return_value.answer = u'ignore'
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
    def test_filter_nonexisting_obsids_and_ask_header_not_found(self, mock_iface):
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'header_that_should_not_exist', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            assert filtered_file_data == reference_list

    @mock.patch('qgis.utils.iface', autospec=True)
    def test_filter_nonexisting_obsids_and_ask_header_capitalize(self, mock_iface):
            file_data = [[u'obsid', u'ae'], [u'a', u'b'], [u'2', u'c']]
            existing_obsids = [u'A', u'2']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids, True)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'A', u'b']]
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


class _TestTempinput(object):
    def test_tempinput(self):
        rows = u'543\n21'
        with utils.tempinput(rows) as filename:
            with io.open(filename, 'r', encoding=u'utf-8') as f:
                res = f.readlines()
        reference_list = [u'543\n', u'21']
        assert res == reference_list


class _TestAskUser(object):
    PyQt4_QtGui_QInputDialog_getText = MockUsingReturnValue([u'-1 hours'])
    cancel = MockUsingReturnValue([u''])

    @mock.patch('PyQt4.QtGui.QInputDialog.getText', PyQt4_QtGui_QInputDialog_getText.get_v)
    def test_askuser_dateshift(self):
        question = utils.Askuser('DateShift')
        assert question.result == ['-1', 'hours']

    @mock.patch('PyQt4.QtGui.QInputDialog.getText', cancel.get_v)
    def test_askuser_dateshift_cancel(self):
        question = utils.Askuser('DateShift')
        assert question.result == u'cancel'


class _TestGetFunctions(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_get_last_logger_dates(self, mocked_instance):
        mocked_instance.return_value.readEntry.return_value = self.SETTINGS_DATABASE
        db_utils.sql_alter_db('''insert into obs_points (obsid) values ('rb1')''')
        db_utils.sql_alter_db('''insert into obs_points (obsid) values ('rb2')''')
        db_utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb1', '2015-01-01 00:00')''')
        db_utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb1', '2015-01-01 00:00:00')''')
        db_utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb1', '2014-01-01 00:00:00')''')
        db_utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb2', '2013-01-01 00:00:00')''')
        db_utils.sql_alter_db('''insert into w_levels_logger (obsid, date_time) values ('rb2', '2016-01-01 00:00')''')

        test_string = create_test_string(utils.get_last_logger_dates())
        reference_string = u'''{rb1: [(2015-01-01 00:00:00)], rb2: [(2016-01-01 00:00)]}'''
        assert test_string == reference_string


class _TestSqlToParametersUnitsTuple(object):
    @mock.patch('db_utils.sql_load_fr_db', autospec=True)
    def test_sql_to_parameters_units_tuple(self, mock_sqlload):
        mock_sqlload.return_value = (True, [(u'par1', u'un1'), (u'par2', u'un2')])

        test_string = create_test_string(utils.sql_to_parameters_units_tuple(u'sql'))
        reference_string = u'''((par1, (un1)), (par2, (un2)))'''
        assert test_string == reference_string


class _TestCalculateDbTableRows(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_get_db_statistics(self, mocked_instance, mock_messagebar):
        """
        Test that calculate_db_table_rows can be run without major error
        :param mock_iface:
        :return:
        """
        mocked_instance.return_value.readEntry.return_value = self.SETTINGS_DATABASE
        utils.calculate_db_table_rows()
        assert mock.call.info(bar_msg='Calculation done, see log for results.', button=True, duration=15, log_msg='Tablename                               Nr of rows\n    SpatialIndex                            0              \nabout_db                                147            \ncomments                                0              \ngeometry_columns                        2              \ngeometry_columns_auth                   2              \ngeometry_columns_field_infos            0              \ngeometry_columns_statistics             2              \ngeometry_columns_time                   2              \nmeteo                                   0              \nobs_lines                               0              \nobs_points                              0              \nseismic_data                            0              \nspatial_ref_sys                         2              \nspatialite_history                      14             \nsql_statements_log                      0              \nsqlite_sequence                         1              \nstratigraphy                            0              \nviews_geometry_columns                  8              \nviews_geometry_columns_auth             0              \nviews_geometry_columns_field_infos      0              \nviews_geometry_columns_statistics       0              \nvirts_geometry_columns                  0              \nvirts_geometry_columns_auth             0              \nvirts_geometry_columns_field_infos      0              \nvirts_geometry_columns_statistics       0              \nvlf_data                                0              \nw_flow                                  0              \nw_levels                                0              \nw_levels_logger                         0              \nw_qual_field                            0              \nw_qual_lab                              0              \nzz_capacity                             24             \nzz_capacity_plots                       24             \nzz_flowtype                             3              \nzz_meteoparam                           2              \nzz_staff                                0              \nzz_strat                                55             \nzz_stratigraphy_plots                   14             ') in mock_messagebar.mock_calls


class _TestGetCurrentLocale(object):
    @mock.patch('locale.getdefaultlocale')
    @mock.patch('midvatten_utils.get_locale_from_db')
    def test_getcurrentlocale(self, mock_get_locale, mock_default_locale):
        mock_get_locale.return_value = u'a_lang'
        mock_default_locale.return_value = [None, u'an_enc']

        test_string = create_test_string(utils.getcurrentlocale())
        reference_string = u'[a_lang, an_enc]'
        assert test_string == reference_string
        

class _TestGetDelimiter(object):
    def test_get_delimiter_only_one_column(self):
        file = [u'obsid',
                 u'rb1']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface):
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert call.messageBar().createMessage(u'Warning, only one column found, see log message panel') in mock_iface.mock_calls
            _test(filename)

    def test_get_delimiter_delimiter_not_found(self):
        file = [u'obsid;acol,acol2',
                 u'rb1;1,2']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface):
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert call.messageBar().createMessage(u'File error, delimiter not found, see log message panel') in mock_iface.mock_calls
                assert delimiter is None
            _test(filename)

    def test_get_delimiter_semicolon(self):
        file = [u'obsid;acol;acol2',
                 u'rb1;1;2']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface):
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert call.messageBar().createMessage(u'File error, delimiter not found, see log message panel') not in mock_iface.mock_calls
                assert delimiter == u';'
            _test(filename)

    def test_get_delimiter_comma(self):
        file = [u'obsid,acol,acol2',
                 u'rb1,1,2']

        with utils.tempinput(u'\n'.join(file), u'utf-8') as filename:
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test(filename, mock_iface):
                delimiter = utils.get_delimiter(filename, u'utf-8')
                assert call.messageBar().createMessage(u'File error, delimiter not found, see log message panel') not in mock_iface.mock_calls
                assert delimiter == u','
            _test(filename)
