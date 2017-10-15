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
from tools.tests.mocks_for_tests import DummyInterface
from PyQt4 import QtCore, QtGui, QtTest
from mocks_for_tests import MockUsingReturnValue, MockQgisUtilsIface, MockReturnUsingDictIn
import mock
import w_flow_calc_aveflow
#

class TestWFlowCalcAveflow(object):
    return_int = MockUsingReturnValue(int)
    db_all_distinct_obsids = MockUsingReturnValue([True, [u'1', u'2']])
    selected_obs = MockUsingReturnValue([u'3', u'4'])
    mocked_iface = MockQgisUtilsIface()
    utilssql_load_fr_db = MockReturnUsingDictIn({'select distinct obsid, instrumentid from': (True, [(u'1', u'inst1'), (u'2', u'inst2')]),
                                                 'select date_time, reading from w_flow where flowtype': (True, [(u'2015-01-01 00:00:00', u'10'),
                                                                                                                 (u'2016-01-01 00:00:00', u'20')]),
                                                 'insert or ignore into w_flow': (True, None)},
                                                0)
    return_none = MockUsingReturnValue(None)

    def setUp(self):
        self.iface = DummyInterface()
        widget = QtGui.QWidget()
        self.calcave = w_flow_calc_aveflow.Calcave(widget)

    @mock.patch('w_flow_calc_aveflow.utils.sql_load_fr_db', db_all_distinct_obsids.get_v)
    @mock.patch('w_flow_calc_aveflow.Calcave.calculateaveflow', return_int.get_v)
    def test_calcall(self):
        self.calcave.calcall()
        result_list = self.calcave.observations
        reference_list = ['1', '2']
        assert result_list == reference_list

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('w_flow_calc_aveflow.utils.getselectedobjectnames', selected_obs.get_v)
    @mock.patch('w_flow_calc_aveflow.Calcave.calculateaveflow', return_int.get_v)
    def test_calcselected(self):
        self.calcave.calcselected()
        result_list = self.calcave.observations
        reference_list = ['3', '4']
        assert result_list == reference_list

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('w_flow_calc_aveflow.utils.sql_alter_db', return_none.get_v)
    @mock.patch('w_flow_calc_aveflow.utils.sql_load_fr_db', utilssql_load_fr_db.get_v)
    def test_calculateaveflow(self):
        self.calcave.observations = ['1', '2']
        self.calcave.calculateaveflow()
        # datestr2num('2015-01-01 00:00:00') == 735599.0
        # datestr2num('2016-01-01 00:00:00') == 735964.0
        # DeltaTime = 24*3600*(735964.0 - 735599.0) == 31536000.0
        #Aveflow = Volume/DeltaTime#L/s == 10000 / 31536000.0 = 0.000317097919838

        reference_list = [u"insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('1','inst1','Aveflow','2016-01-01 00:00:00','0.000317097919838','l/s')", u"insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('2','inst2','Aveflow','2016-01-01 00:00:00','0.000317097919838','l/s')"]
        assert self.return_none.args_called_with == reference_list
