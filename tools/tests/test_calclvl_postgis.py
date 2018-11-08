# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles exports to
  fieldlogger format.

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

from qgis.PyQt import QtGui

import db_utils
import mock
from date_utils import datestring_to_date
from nose.plugins.attrib import attr
from wlevels_calc_calibr import Calclvl

import utils_for_tests


@attr(status='on')
class TestCalclvl(utils_for_tests.MidvattenTestPostgisDbSv):
    def setUp(self):
        super(self.__class__, self).setUp()
        widget = QtWidgets.QWidget()
        self.calclvl = Calclvl(widget, 1)

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calcall(self):
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        self.calclvl.FromDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date('2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date('2010-01-01 00:00:00'))
        self.calclvl.calcall()

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels'))
        reference_string = '(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0)])'
        assert test_string == reference_string

    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calc_selected(self, mock_selected_obsids):
        mock_selected_obsids.return_value = ['rb1']
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb2', 4)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        self.calclvl.FromDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date('2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date('2010-01-01 00:00:00'))
        self.calclvl.calcselected()

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels ORDER BY obsid'))
        reference_string = '(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0), (rb2, 2005-01-01 00:00:00, 444.0, None, None)])'

        assert test_string == reference_string

    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calc_selected_overwrite(self, mock_selected_obsids):
        mock_selected_obsids.return_value = ['rb1', 'rb2']
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb2', 4)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, level_masl, date_time) VALUES ('rb2', 555, 667, '2005-01-02 00:00:00')''')
        self.calclvl.FromDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date('2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date('2010-01-01 00:00:00'))
        self.calclvl.calcselected()

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels ORDER BY obsid'))
        reference_string = '(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0), (rb2, 2005-01-01 00:00:00, 444.0, 4.0, -440.0), (rb2, 2005-01-02 00:00:00, 555.0, 4.0, -551.0)])'
        print(test_string)
        assert test_string == reference_string

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calc_selected_dont_overwrite(self, mock_selected_obsids, mock_messagebar):
        mock_selected_obsids.return_value = ['rb1', 'rb2']
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb2', 4)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, level_masl, date_time) VALUES ('rb2', 555, 667, '2005-01-02 00:00:00')''')
        self.calclvl.FromDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date('2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date('2010-01-01 00:00:00'))
        self.calclvl.checkBox_overwrite_prev.setChecked(False)
        self.calclvl.calcselected()
        #self.checkBox_skipnulls

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels ORDER BY obsid, date_time'))
        reference_string = '(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0), (rb2, 2005-01-01 00:00:00, 444.0, 4.0, -440.0), (rb2, 2005-01-02 00:00:00, 555.0, None, 667.0)])'
        print(str(mock_messagebar.mock_calls))
        print(test_string)
        assert test_string == reference_string

    @mock.patch('wlevels_calc_calibr.utils.pop_up_info', autospec=True)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calc_selected_dont_overwrite_dont_skip_nulls(self, mock_selected_obsids, mock_messagebar, mock_skippopup):
        mock_selected_obsids.return_value = ['rb1', 'rb2']
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb2', NULL)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, level_masl, date_time) VALUES ('rb2', 555, 667, '2005-01-02 00:00:00')''')
        self.calclvl.FromDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date('2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date('2010-01-01 00:00:00'))
        self.calclvl.checkBox_overwrite_prev.setChecked(False)

        self.calclvl.calcselected()
        #self.checkBox_skipnulls

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels ORDER BY obsid, date_time'))
        reference_string = '(True, [(rb1, 2005-01-01 00:00:00, 222.0, None, None), (rb2, 2005-01-01 00:00:00, 444.0, None, None), (rb2, 2005-01-02 00:00:00, 555.0, None, 667.0)])'
        print(str(mock_messagebar.mock_calls))
        print(test_string)
        assert test_string == reference_string

    @mock.patch('wlevels_calc_calibr.utils.pop_up_info', autospec=True)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calc_selected_dont_overwrite_skip_nulls(self, mock_selected_obsids, mock_messagebar, mock_skippopup):
        mock_selected_obsids.return_value = ['rb1', 'rb2']
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb2', NULL)''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT into w_levels (obsid, meas, level_masl, date_time) VALUES ('rb2', 555, 667, '2005-01-02 00:00:00')''')
        self.calclvl.FromDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date('2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtWidgets.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date('2010-01-01 00:00:00'))
        self.calclvl.checkBox_overwrite_prev.setChecked(False)
        self.calclvl.checkBox_stop_if_null.setChecked(False)

        self.calclvl.calcselected()
        #self.checkBox_skipnulls

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels ORDER BY obsid, date_time'))
        reference_string = '(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0), (rb2, 2005-01-01 00:00:00, 444.0, None, None), (rb2, 2005-01-02 00:00:00, 555.0, None, 667.0)])'
        print(str(mock_messagebar.mock_calls))
        print(test_string)
        assert test_string == reference_string

    def tearDown(self):
        if hasattr(self.calclvl, 'updated_h_tocs') and hasattr(self.calclvl, 'updated_level_masl'):
            # Must be equal for all tests
            assert self.calclvl.updated_h_tocs == self.calclvl.updated_level_masl
        super(self.__class__, self).tearDown()