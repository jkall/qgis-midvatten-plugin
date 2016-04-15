# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module w_flow_calc_aveflow.py.

                             -------------------
        begin                : 2016-04-15
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
from qgis.core import QgsApplication, QgsProviderRegistry
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from PyQt4 import QtCore, QtGui, QtTest
from export_fieldlogger import ExportToFieldLogger
from mocks_for_tests import MockUsingReturnValue, MockQgisUtilsIface
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
from utils_for_tests import dict_to_sorted_list
from midvatten import midvatten
import w_flow_calc_aveflow
#

class TestWFlowCalcAveflow(object):
    return_int = MockUsingReturnValue(int)
    db_all_distinct_obsids = MockUsingReturnValue([True, [u'1', u'2']])
    selected_obs = MockUsingReturnValue([u'3', u'4'])
    mocked_iface = MockQgisUtilsIface()
    def setUp(self):
        self.iface = DummyInterface()
        widget = QtGui.QWidget()
        self.calcave = w_flow_calc_aveflow.calcave(widget)

    @mock.patch('w_flow_calc_aveflow.utils.sql_load_fr_db', db_all_distinct_obsids.get_v)
    @mock.patch('w_flow_calc_aveflow.calcave.calculateaveflow', return_int.get_v)
    def test_calcall(self):
        self.calcave.calcall()
        result_list = self.calcave.observations
        reference_list = ['1', '2']
        assert result_list == reference_list

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('w_flow_calc_aveflow.utils.getselectedobjectnames', selected_obs.get_v)
    @mock.patch('w_flow_calc_aveflow.calcave.calculateaveflow', return_int.get_v)
    def test_calcselected(self):
        self.calcave.calcselected()
        result_list = self.calcave.observations
        reference_list = ['3', '4']
        assert result_list == reference_list

    @mock.patch('qgis.utils.iface', mocked_iface)
    def test_calculateaveflow(self):
        self.calcave.observations = ['1', '2']
        self.calcave.calculateaveflow()
