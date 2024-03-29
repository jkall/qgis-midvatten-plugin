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
from __future__ import absolute_import

from builtins import str

import mock
from mock import call
from nose.plugins.attrib import attr

from midvatten.tools.utils import db_utils, midvatten_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.tests.utils_for_tests import create_test_string


@attr(status='on')
class TestGetFunctions(utils_for_tests.MidvattenTestSpatialiteDbSv):

    def test_get_last_logger_dates(self):
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time) VALUES ('rb1', '2015-01-01 00:00')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time) VALUES ('rb1', '2015-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time) VALUES ('rb1', '2014-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time) VALUES ('rb2', '2013-01-01 00:00:00')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels_logger (obsid, date_time) VALUES ('rb2', '2016-01-01 00:00')''')

        test_string = create_test_string(midvatten_utils.get_last_logger_dates())
        reference_string = '''{rb1: [(2015-01-01 00:00:00)], rb2: [(2016-01-01 00:00)]}'''
        assert test_string == reference_string

@attr(status='on')
class TestCalculateDbTableRows(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten.tools.utils.midvatten_utils.MessagebarAndLog')
    def test_get_db_statistics(self, mock_messagebar):
        """
        Test that calculate_db_table_rows can be run without major error
        :param mock_iface:
        :return:
        """
        midvatten_utils.calculate_db_table_rows()

        assert len(str(mock_messagebar.mock_calls[0])) > 1500 and 'about_db' in str(mock_messagebar.mock_calls[0])

@attr(status='on')
class TestWarnAboutOldDatabase(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten.tools.utils.midvatten_utils.latest_database_version')
    @mock.patch('midvatten.tools.utils.midvatten_utils.MessagebarAndLog')
    def test_warn_about_old_database(self, mock_messagebar, mock_latest_version):
        mock_latest_version.return_value = '999.999.999'
        midvatten_utils.warn_about_old_database()
        print(str(mock_messagebar.mock_calls))
        assert call.info(bar_msg='The database version appears to be older than 999.999.999. An upgrade is suggested! See https://github.com/jkall/qgis-midvatten-plugin/wiki/6.-Database-management#upgrade-database', duration=4) in mock_messagebar.mock_calls

    @mock.patch('midvatten.tools.utils.midvatten_utils.latest_database_version')
    @mock.patch('midvatten.tools.utils.midvatten_utils.MessagebarAndLog')
    def test_warn_about_old_database_not_old(self, mock_messagebar, mock_latest_version):
        mock_latest_version.return_value = '0.0.1'
        midvatten_utils.warn_about_old_database()
        print(str(mock_messagebar.mock_calls))
        assert not mock_messagebar.mock_calls

