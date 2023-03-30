# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles calibration
 of logger data.

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
from __future__ import print_function

from decimal import Decimal

import mock
from nose.plugins.attrib import attr

from midvatten.tools.wlevels_calc_calibr import Calibrlogger
from midvatten.tools.utils import db_utils, date_utils, gui_utils
from midvatten.tools.tests import utils_for_tests


@attr(status='on')
class TestCalibrlogger(utils_for_tests.MidvattenTestSpatialiteDbSv):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_last_calibration(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 50, 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 100, NULL)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()
        test = utils_for_tests.create_test_string(calibrlogger.getlastcalibration(calibrlogger.selected_obsid))
        ref = '[(2017-02-01 00:00, 99.5)]'
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_set_log_pos(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm) VALUES ('rb1', '2017-02-01 00:00', 100)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()

        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calibrlogger.logger_elevation.setText('2')
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')

        calibrlogger.set_logger_pos()

        test = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('SELECT * FROM w_levels_logger'))
        ref = '(True, [(rb1, 2017-02-01 00:00, 100.0, None, None, 3.0, None)])'
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_add_to_level_masl(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()

        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calibrlogger.offset.setText('50')
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')

        calibrlogger.add_to_level_masl()

        test = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('SELECT * FROM w_levels_logger'))
        ref = '(True, [(rb1, 2017-02-01 00:00, None, None, None, 150.0, None)])'
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.wlevels_calc_calibr.common_utils.pop_up_info', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_calc_best_fit_add_out_of_radius(self, mock_messagebar, skip_popup):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-03-01 00:00', 50)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()

        calibrlogger.loggerpos_masl_or_offset_state = 2
        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')

        calibrlogger.calc_best_fit()

        test = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('SELECT * FROM w_levels_logger'))
        ref = '(True, [(rb1, 2017-03-01 00:00, None, None, None, 50.0, None)])'
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.wlevels_calc_calibr.common_utils.pop_up_info', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_calc_best_fit_add(self, mock_messagebar, skip_popup):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 01:00', 50)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()

        calibrlogger.loggerpos_masl_or_offset_state = 2
        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')
        calibrlogger.bestFitSearchRadius.setText('2 hours')

        calibrlogger.calc_best_fit()

        test = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('SELECT * FROM w_levels_logger'))
        ref = '(True, [(rb1, 2017-02-01 01:00, None, None, None, 100.0, None)])'
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.wlevels_calc_calibr.common_utils.pop_up_info', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_calc_best_fit_add_matches_same_from_date(self, mock_messagebar, skip_popup):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 01:00', 50)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()

        calibrlogger.loggerpos_masl_or_offset_state = 2
        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2017-02-01 01:00'))
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')
        calibrlogger.bestFitSearchRadius.setText('2 hours')

        calibrlogger.calc_best_fit()

        test = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('SELECT * FROM w_levels_logger'))
        ref = '(True, [(rb1, 2017-02-01 01:00, None, None, None, 100.0, None)])'
        print(test)
        print(ref)
        assert test == ref

    @mock.patch('midvatten.tools.wlevels_calc_calibr.common_utils.pop_up_info', autospec=True)
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_calc_best_fit_add_matches_same_to_date(self, mock_messagebar, skip_popup):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 01:00', 50)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        calibrlogger.update_plot()

        calibrlogger.loggerpos_masl_or_offset_state = 2
        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2010-02-01 01:00'))
        calibrlogger.ToDateTime.setDateTime(date_utils.datestring_to_date('2017-02-01 01:00'))
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')
        calibrlogger.bestFitSearchRadius.setText('2 hours')

        calibrlogger.calc_best_fit()

        test = utils_for_tests.create_test_string(db_utils.sql_load_fr_db('SELECT * FROM w_levels_logger'))
        ref = '(True, [(rb1, 2017-02-01 01:00, None, None, None, 100.0, None)])'
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_adjust_trend(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-10 00:00', 200)")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 200)")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-10 00:00', 100)")

        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')
        calibrlogger.update_plot()
        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2000-01-01 00:00:00'))
        calibrlogger.L1_date.setDateTime(date_utils.datestring_to_date('2017-02-01 00:00'))
        calibrlogger.L2_date.setDateTime(date_utils.datestring_to_date('2017-02-10 00:00'))
        calibrlogger.M1_date.setDateTime(date_utils.datestring_to_date('2017-02-01 00:00'))
        calibrlogger.M2_date.setDateTime(date_utils.datestring_to_date('2017-02-10 00:00'))
        calibrlogger.L1_level.setText('100')
        calibrlogger.L2_level.setText('200')
        calibrlogger.M1_level.setText('200')
        calibrlogger.M2_level.setText('100')

        calibrlogger.adjust_trend_func()
        res = db_utils.sql_load_fr_db('SELECT obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment FROM w_levels_logger')
        l = list(res[1][1])
        l[5] = '%.11e'%Decimal(l[5])
        res[1][1] = tuple(l)
        test = utils_for_tests.create_test_string(res)
        print(mock_messagebar.mock_calls)

        ref = '(True, [(rb1, 2017-02-01 00:00, None, None, None, 100.0, None), (rb1, 2017-02-10 00:00, None, None, None, -2.84217094304e-14, None)])'
        print("Ref")

        print(ref)
        print("Test")
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_set_last_calibration(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 50, 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 100, NULL)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        """(level_masl - (head_cm/100))"""

        calibrlogger.update_plot()
        res = calibrlogger.getlastcalibration(calibrlogger.selected_obsid)
        test = utils_for_tests.create_test_string(calibrlogger.INFO.text())
        ref = 'Last pos. for logger in rb1 was 99.500 masl at 2017-02-01 00:00'

        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_set_last_calibration_zero(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100, 1)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 100, NULL)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)

        """(level_masl - (head_cm/100))"""

        calibrlogger.update_plot()
        res = calibrlogger.getlastcalibration(calibrlogger.selected_obsid)
        test = utils_for_tests.create_test_string(calibrlogger.INFO.text())
        ref = 'Last pos. for logger in rb1 was 0.000 masl at 2017-02-01 00:00'
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_calibrinfolast_calibration(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb2')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 50, 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 100, NULL)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 200, 300)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        test = utils_for_tests.create_test_string(calibrlogger.get_uncalibrated_obsids())
        ref = '[rb1]'
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_delete_range(self, mock_messagebar, askuser):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-10 00:00', 200)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, level_masl) VALUES ('rb1', '2017-01-28 00:00', 200)")

        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1 (uncalibrated)')
        calibrlogger.update_plot()
        calibrlogger.FromDateTime.setDateTime(date_utils.datestring_to_date('2017-01-30 00:00'))
        calibrlogger.ToDateTime.setDateTime(date_utils.datestring_to_date('2017-02-02 00:00'))
        askuser.return_value.result = True

        calibrlogger.delete_selected_range('w_levels_logger')

        res = db_utils.sql_load_fr_db('SELECT date_time FROM w_levels_logger ORDER BY date_time')
        test = utils_for_tests.create_test_string(res)
        print(mock_messagebar.mock_calls)


        ref = '(True, [(2017-01-28 00:00), (2017-02-10 00:00)])'
        print("Ref")

        print(ref)
        print("Test")
        print(test)
        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_change_timezone_no_w_levels_tz(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100, 1)")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels (obsid, date_time, meas, level_masl) VALUES ('rb1', '2017-02-01 00:00', 200, 2)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1', add_if_not_exists=False)
        calibrlogger.load_obsid_and_init()
        assert tuple(calibrlogger.meas_ts.tolist()) == (('2017-02-01 00:00', 2.0),)

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_change_timezone_w_levels_tz_no_conversion(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100, 1)")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels (obsid, date_time, meas, level_masl) VALUES ('rb1', '2017-02-01 00:00', 200, 2)")

        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (UTC+1)'
                                 WHERE tablename = 'w_levels_logger';""")
        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (Europe/Stockholm)'
                                 WHERE tablename = 'w_levels';""")

        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1', add_if_not_exists=False)
        calibrlogger.load_obsid_and_init()
        assert tuple(calibrlogger.meas_ts.tolist()) == (('2017-02-01 00:00', 2.0),)

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_change_timezone_w_levels_tz_convert(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100, 1)")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels (obsid, date_time, meas, level_masl) VALUES ('rb1', '2017-05-01 00:00', 200, 2)")

        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (UTC+1)'
                                 WHERE tablename = 'w_levels_logger';""")
        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (Europe/Stockholm)'
                                 WHERE tablename = 'w_levels';""")

        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1', add_if_not_exists=False)
        calibrlogger.load_obsid_and_init()
        assert tuple(calibrlogger.meas_ts.tolist()) == (('2017-04-30 23:00', 2.0),)

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_change_timezone_no_w_levels_logger_tz(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 100, 1)")
        db_utils.sql_alter_db(
            "INSERT INTO w_levels (obsid, date_time, meas, level_masl) VALUES ('rb1', '2017-05-01 00:00', 200, 2)")

        db_utils.sql_alter_db("""UPDATE about_db SET description = ''
                                 WHERE tablename = 'w_levels_logger';""")
        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (Europe/Stockholm)'
                                 WHERE tablename = 'w_levels';""")

        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1', add_if_not_exists=False)
        calibrlogger.load_obsid_and_init()
        assert tuple(calibrlogger.meas_ts.tolist()) == (('2017-05-01 00:00', 2.0),)

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_normalize_against_logger(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 20)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 50, 100)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 100, NULL)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        calibrlogger.plot_logger_head.setChecked(True)
        calibrlogger.normalize_head.setChecked(True)

        """(level_masl - (head_cm/100))"""
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1', add_if_not_exists=False)
        calibrlogger.load_obsid_and_init()

        #calibrlogger.update_plot()
        print(str(mock_messagebar.mock_calls))
        test = tuple(calibrlogger.head_ts_for_plot.values)

        print(test)
        ref = (99.75, 100.25)

        assert test == ref

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_calibrlogger_normalize_against_meas(self, mock_messagebar):
        db_utils.sql_alter_db("INSERT INTO obs_points (obsid) VALUES ('rb1')")
        db_utils.sql_alter_db("INSERT INTO w_levels (obsid, date_time, level_masl) VALUES ('rb1', '2017-02-01 00:00', 20)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-02-01 00:00', 50, NULL)")
        db_utils.sql_alter_db("INSERT INTO w_levels_logger (obsid, date_time, head_cm, level_masl) VALUES ('rb1', '2017-03-01 00:00', 100, NULL)")
        calibrlogger = Calibrlogger(self.iface.mainWindow(), self.midvatten.ms)
        calibrlogger.plot_logger_head.setChecked(True)
        calibrlogger.normalize_head.setChecked(True)

        """(level_masl - (head_cm/100))"""
        gui_utils.set_combobox(calibrlogger.combobox_obsid, 'rb1', add_if_not_exists=False)
        calibrlogger.load_obsid_and_init()

        #calibrlogger.update_plot()
        print(str(mock_messagebar.mock_calls))
        test = tuple(calibrlogger.head_ts_for_plot.values)

        print(test)
        ref = (19.75, 20.25)

        assert test == ref