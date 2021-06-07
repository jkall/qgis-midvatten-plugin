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
from __future__ import absolute_import

import mock

from nose.plugins.attrib import attr
from qgis.PyQt import QtWidgets

from midvatten.tools.utils import common_utils, date_utils, db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools import w_flow_calc_aveflow


@attr(status='on')
class TestWFlowCalcAveflow(utils_for_tests.MidvattenTestSpatialiteDbSv):


    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calcall(self, mock_messagebar):

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('2')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-02 00:00', 2.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-01 00:00', 1.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-04 00:00', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-03 00:00', 5.0, 'm3')''')

        widget = QtWidgets.QWidget()
        calcave = w_flow_calc_aveflow.Calcave(widget)
        calcave.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calcave.calcall(use_pandas=False)
        print(str(mock_messagebar.mock_calls))
        #insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('%s','%s','Aveflow','%s','%s','l/s')
        res = db_utils.sql_load_fr_db('''SELECT obsid, instrumentid, flowtype, date_time, ROUND(reading, 4), unit FROM w_flow ORDER BY obsid, flowtype, date_time''')[1]
        test = common_utils.anything_to_string_representation(res)



        print(test)
        reference = '[("1", "inst1", "Accvol", "2019-02-01 00:00", 1.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-02 00:00", 2.0, "m3", ), ("1", "inst1", "Aveflow", "2019-02-02 00:00", 0.0116, "l/s", ), ("2", "inst2", "Accvol", "2019-02-03 00:00", 5.0, "m3", ), ("2", "inst2", "Accvol", "2019-02-04 00:00", 10.0, "m3", ), ("2", "inst2", "Aveflow", "2019-02-04 00:00", 0.0579, "l/s", )]'
        #result_list = self.calcave.observations
        #reference_list = ['1', '2']
        assert test == reference

    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.getselectedobjectnames', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calselected(self, mock_messagebar, mock_getselectedobjectnames, mock_iface):
        mock_getselectedobjectnames.return_value = ['1']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('2')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-02 00:00', 2.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-01 00:00', 1.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-04 00:00', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-03 00:00', 5.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-04 00:00', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-03 00:00', 5.0, 'm3')''')

        widget = QtWidgets.QWidget()
        calcave = w_flow_calc_aveflow.Calcave(widget)
        calcave.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calcave.calcselected(use_pandas=False)
        print(str(mock_messagebar.mock_calls))
        #insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('%s','%s','Aveflow','%s','%s','l/s')
        res = db_utils.sql_load_fr_db('''SELECT obsid, instrumentid, flowtype, date_time, ROUND(reading, 4), unit FROM w_flow ORDER BY obsid, flowtype, date_time''')[1]
        test = common_utils.anything_to_string_representation(res)


        print(test)
        reference = '[("1", "inst1", "Accvol", "2019-02-01 00:00", 1.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-02 00:00", 2.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-03 00:00", 5.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-04 00:00", 10.0, "m3", ), ("1", "inst1", "Aveflow", "2019-02-02 00:00", 0.0116, "l/s", ), ("1", "inst1", "Aveflow", "2019-02-03 00:00", 0.0347, "l/s", ), ("1", "inst1", "Aveflow", "2019-02-04 00:00", 0.0579, "l/s", ), ("2", "inst2", "Accvol", "2019-02-03 00:00", 5.0, "m3", ), ("2", "inst2", "Accvol", "2019-02-04 00:00", 10.0, "m3", )]'
        #result_list = self.calcave.observations
        #reference_list = ['1', '2']
        assert test == reference

    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.getselectedobjectnames', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calselected_pandas_one_selected(self, mock_messagebar, mock_getselectedobjectnames, mock_iface):
        """
        Pandas removes the
        :param mock_messagebar:
        :param mock_getselectedobjectnames:
        :param mock_iface:
        :return:
        """
        mock_getselectedobjectnames.return_value = ['1']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('2')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-02 00:00', 2.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-01 00:00', 1.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-04 00:00', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-03 00:00', 5.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-04 00:00', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-03 00:00', 5.0, 'm3')''')

        widget = QtWidgets.QWidget()
        calcave = w_flow_calc_aveflow.Calcave(widget)
        calcave.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calcave.calcselected(use_pandas=True)
        print(str(mock_messagebar.mock_calls))
        #insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('%s','%s','Aveflow','%s','%s','l/s')
        res = db_utils.sql_load_fr_db('''SELECT obsid, instrumentid, flowtype, date_time, ROUND(reading, 4), unit FROM w_flow ORDER BY obsid, flowtype, date_time''')[1]
        test = common_utils.anything_to_string_representation(res)


        reference = '[("1", "inst1", "Accvol", "2019-02-01 00:00", 1.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-02 00:00", 2.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-03 00:00", 5.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-04 00:00", 10.0, "m3", ), ("1", "inst1", "Aveflow", "2019-02-02", 0.0116, "l/s", ), ("1", "inst1", "Aveflow", "2019-02-03", 0.0347, "l/s", ), ("1", "inst1", "Aveflow", "2019-02-04", 0.0579, "l/s", ), ("2", "inst2", "Accvol", "2019-02-03 00:00", 5.0, "m3", ), ("2", "inst2", "Accvol", "2019-02-04 00:00", 10.0, "m3", )]'
        #result_list = self.calcave.observations
        #reference_list = ['1', '2']
        print("Ref:\n" + str(reference))
        print("Test:\n" + str(test))
        assert test == reference

    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.getselectedobjectnames', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calselected_pandas_two_selected(self, mock_messagebar, mock_getselectedobjectnames, mock_iface):
        mock_getselectedobjectnames.return_value = ['1', '2']

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('2')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-02 23:59', 2.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-01 23:59', 1.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-04 23:59', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('1', 'inst1', 'Accvol', '2019-02-03 23:59', 5.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-04 23:59', 10.0, 'm3')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, reading, unit) VALUES ('2', 'inst2', 'Accvol', '2019-02-03 23:59', 5.0, 'm3')''')

        widget = QtWidgets.QWidget()
        calcave = w_flow_calc_aveflow.Calcave(widget)
        calcave.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calcave.calcselected(use_pandas=True)
        print(str(mock_messagebar.mock_calls))
        #insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('%s','%s','Aveflow','%s','%s','l/s')
        res = db_utils.sql_load_fr_db('''SELECT obsid, instrumentid, flowtype, date_time, ROUND(reading, 4), unit FROM w_flow ORDER BY obsid, flowtype, date_time''')[1]
        test = common_utils.anything_to_string_representation(res)


        #print(test)
        reference = '[("1", "inst1", "Accvol", "2019-02-01 23:59", 1.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-02 23:59", 2.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-03 23:59", 5.0, "m3", ), ("1", "inst1", "Accvol", "2019-02-04 23:59", 10.0, "m3", ), ("1", "inst1", "Aveflow", "2019-02-02 23:59:00", 0.0116, "l/s", ), ("1", "inst1", "Aveflow", "2019-02-03 23:59:00", 0.0347, "l/s", ), ("1", "inst1", "Aveflow", "2019-02-04 23:59:00", 0.0579, "l/s", ), ("2", "inst2", "Accvol", "2019-02-03 23:59", 5.0, "m3", ), ("2", "inst2", "Accvol", "2019-02-04 23:59", 10.0, "m3", ), ("2", "inst2", "Aveflow", "2019-02-04 23:59:00", 0.0579, "l/s", )]'
        print("Ref:\n" + str(reference))
        print("Test:\n" + str(test))
        #result_list = self.calcave.observations
        #reference_list = ['1', '2']
        assert test == reference