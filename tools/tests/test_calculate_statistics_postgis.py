# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles statistics
 calculation

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

import midvatten.tools.utils.db_utils as db_utils
import midvatten_utils as utils
import mock
from mock import call
from mock import MagicMock
from collections import OrderedDict
import piper
from nose.plugins.attrib import attr
import calculate_statistics

import utils_for_tests

@attr(status='on')
class TestCalculateStatistics(utils_for_tests.MidvattenTestPostgisDbSv):

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.get_selected_features_as_tuple', autospec=True)
    def test_calculate_statistics(self, mock_selected_features, mock_iface, mock_messagebar):
        dbconnection = db_utils.DbConnectionManager()
        db_utils.sql_alter_db("""INSERT INTO obs_points(obsid) VALUES('1')""")
        db_utils.sql_alter_db("""INSERT INTO obs_points(obsid) VALUES('2')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('1', '2017-01-01', '1')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('1', '2017-01-02', '3')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('1', '2017-01-03', '5')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('2', '2017-01-04', '2')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('2', '2017-01-05', '8')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('2', '2017-01-06', '9')""")
        db_utils.sql_alter_db("""INSERT INTO w_levels(obsid, date_time, meas) VALUES('2', '2017-01-07', '10')""")

        mock_selected_features.return_value = ['1', '2']
        ms = MagicMock()
        ms.settingsdict = OrderedDict()

        calc_stats = calculate_statistics.CalculateStatisticsGui(self.iface.mainWindow(), ms)
        calc_stats.db_browser.table_list = 'w_levels'
        calc_stats.db_browser.column_list = 'meas'
        calc_stats.calculate()
        ref = call.info(bar_msg='Statistics for table w_levels column meas done, see log for results.', button=True, duration=15, log_msg='Obsid;Min;Median;Average;Max;Nr of values\n1;1.0;3.0;3.0;5.0;3\n2;2.0;8.5;7.25;10.0;4')
        print(str(mock_messagebar.mock_calls))
        assert ref in mock_messagebar.mock_calls