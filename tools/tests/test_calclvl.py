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
import os
from qgis.core import QgsApplication, QgsProviderRegistry
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from date_utils import datestring_to_date
from PyQt4 import QtCore, QtGui, QtTest
from mocks_for_tests import MockUsingReturnValue, MockQgsProjectInstance
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
from utils_for_tests import dict_to_sorted_list
from wlevels_calc_calibr import calclvl
from midvatten.midvatten import midvatten
import utils_for_tests


class _TestCalclvl(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    selected_obsids = MockUsingReturnValue([u'rb1'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def setUp(self, mock_locale):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TestCalclvl.temp_db_path)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        widget = QtGui.QWidget()
        self.calclvl = calclvl(widget, 1)

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_calcall(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "h_toc") VALUES ('rb1', 1)''')
        utils.sql_alter_db(u'''INSERT into w_levels ("obsid", "meas", "date_time") VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        self.calclvl.FromDateTime = QtGui.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date(u'2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtGui.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date(u'2010-01-01 00:00:00'))
        self.calclvl.calcall()

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, date_time, meas, h_toc, level_masl from w_levels'))
        reference_string = u'(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0)])'
        assert test_string == reference_string

    @mock.patch('wlevels_calc_calibr.utils.getselectedobjectnames', selected_obsids.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_calcall(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "h_toc") VALUES ('rb1', 1)''')
        utils.sql_alter_db(u'''INSERT into w_levels ("obsid", "meas", "date_time") VALUES ('rb1', 222, '2005-01-01 00:00:00')''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "h_toc") VALUES ('rb2', 4)''')
        utils.sql_alter_db(u'''INSERT into w_levels ("obsid", "meas", "date_time") VALUES ('rb2', 444, '2005-01-01 00:00:00')''')
        self.calclvl.FromDateTime = QtGui.QDateTimeEdit()
        self.calclvl.FromDateTime.setDateTime(datestring_to_date(u'2000-01-01 00:00:00'))
        self.calclvl.ToDateTime = QtGui.QDateTimeEdit()
        self.calclvl.ToDateTime.setDateTime(datestring_to_date(u'2010-01-01 00:00:00'))
        self.calclvl.calcselected()

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, date_time, meas, h_toc, level_masl from w_levels'))
        reference_string = u'(True, [(rb1, 2005-01-01 00:00:00, 222.0, 1.0, -221.0), (rb2, 2005-01-01 00:00:00, 444.0, None, None)])'
        assert test_string == reference_string

    def tearDown(self):
        #Delete database
        os.remove(TestCalclvl.temp_db_path)