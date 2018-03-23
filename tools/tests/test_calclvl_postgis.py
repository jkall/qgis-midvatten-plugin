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

from PyQt4 import QtGui

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
        widget = QtGui.QWidget()
        self.calclvl = Calclvl(widget, 1)

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calcall(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db(u'''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        self.calclvl.FromDateTime = QtGui.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date(u'2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtGui.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date(u'2010-01-01 00:00:00'))
        self.calclvl.calcall()

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels'))
        reference_string = u'(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0)])'
        assert test_string == reference_string

    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_calc_selected(self, mock_selected_obsids):
        mock_selected_obsids.return_value = [u'rb1']
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb1', 1)''')
        db_utils.sql_alter_db(u'''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('rb2', 4)''')
        db_utils.sql_alter_db(u'''INSERT into w_levels (obsid, meas, date_time) VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        self.calclvl.FromDateTime = QtGui.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date(u'2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtGui.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date(u'2010-01-01 00:00:00'))
        self.calclvl.calcselected()

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'SELECT obsid, date_time, meas, h_toc, level_masl FROM w_levels ORDER BY obsid'))
        reference_string = u'(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0), (rb2, 2005-01-01 00:00:00, 444.0, None, None)])'

        assert test_string == reference_string