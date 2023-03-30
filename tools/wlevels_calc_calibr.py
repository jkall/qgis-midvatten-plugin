# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of water level measurements
 to the database. Also some calculations and calibrations. 

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
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

import math
import os
from builtins import next
from builtins import range
from builtins import str

import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import qgis.PyQt
from matplotlib.backend_bases import MouseButton, PickEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import datestr2num, num2date
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import QCoreApplication, Qt

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar

from matplotlib.widgets import RectangleSelector

import datetime

from midvatten.tools.utils import common_utils, db_utils
from midvatten.tools.utils.common_utils import returnunicode as ru, fn_timer
from midvatten.tools.utils.date_utils import dateshift, datestring_to_date, long_dateformat, change_timezone
from midvatten.tools.utils.gui_utils import add_action_to_navigation_toolbar


Calibr_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calibr_logger_dialog_integrated.ui'))[0]
Calc_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calc_lvl_dialog.ui'))[0]


class Calclvl(qgis.PyQt.QtWidgets.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    @fn_timer
    def __init__(self, parent,layerin):
        qgis.PyQt.QtWidgets.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = midvatten_utils.getselectedobjectnames()
        self.setWindowTitle(ru(QCoreApplication.translate('Calclvl', "Calculate levels"))) # Set the title for the dialog
        self.pushButton_All.clicked.connect(lambda x: self.calcall())
        self.pushButton_Selected.clicked.connect(lambda x: self.calcselected())
        self.pushButton_Cancel.clicked.connect(lambda x: self.close())
        self.layer = layerin

    def calc(self, obsids):
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
        to_d_t = self.ToDateTime.dateTime().toPyDateTime()
        sql = """SELECT obsid FROM obs_points WHERE obsid IN ({}) AND h_toc IS NULL""".format(', '.join(["'{}'".format(x) for x in obsids]))

        obsid_with_h_toc_null = db_utils.sql_load_fr_db(sql)[1]
        if obsid_with_h_toc_null:
            obsid_with_h_toc_null = [x[0] for x in obsid_with_h_toc_null]
            if self.checkBox_stop_if_null.isChecked():
                any_nulls = [obsid for obsid in obsids if obsid in obsid_with_h_toc_null]
                if any_nulls:
                    common_utils.pop_up_info(ru(QCoreApplication.translate('Calclvl', 'Adjustment aborted! There seems to be NULL values in your table obs_points, column h_toc.')), ru(QCoreApplication.translate('Calclvl', 'Error')))
                    return None

            else:
                obsids = [obsid for obsid in obsids if obsid not in obsid_with_h_toc_null]

            if not obsids:
                common_utils.pop_up_info(ru(QCoreApplication.translate('Calclvl',
                                                                'Adjustment aborted! All h_tocs were NULL.')),
                                                     ru(QCoreApplication.translate('Calclvl', 'Error')))
                return None

        formatted_obsids = ', '.join(["'{}'".format(x) for x in obsids])
        where_args = {'fr_dt': str(fr_d_t), 'to_dt': str(to_d_t), 'obsids': formatted_obsids}
        where_sql = """meas IS NOT NULL AND date_time >= '{fr_dt}' AND date_time <= '{to_dt}' AND obsid IN ({obsids})""".format(**where_args)
        if not self.checkBox_overwrite_prev.isChecked():
            where_sql += """ AND level_masl IS NULL """

        sql1 = """UPDATE w_levels SET h_toc = (SELECT obs_points.h_toc FROM obs_points WHERE w_levels.obsid = obs_points.obsid) WHERE {}""".format(where_sql)
        self.updated_h_tocs = self.log_msg(where_sql)
        db_utils.sql_alter_db(sql1)

        where_sql += """ AND h_toc IS NOT NULL"""
        sql2 = """UPDATE w_levels SET level_masl = h_toc - meas WHERE h_toc IS NOT NULL AND {}""".format(where_sql)
        self.updated_level_masl = self.log_msg(where_sql)
        db_utils.sql_alter_db(sql2)

        common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('Calclvl', 'Calculation done, see log message panel')),
                                                       log_msg=ru(QCoreApplication.translate('Calclvl', 'H_toc added and level_masl calculated for\nobsid;min date;max date;calculated number of measurements: \n%s'))%(self.updated_level_masl))
        self.close()

    @fn_timer
    def calcall(self):
        obsids = db_utils.sql_load_fr_db("""SELECT DISTINCT obsid FROM w_levels""")[1]
        if obsids:
            obsids = [x[0] for x in obsids]
            self.calc(obsids)
        else:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calclvl',
                                                            'Adjustment aborted! No obsids in w_levels.')),
                                                 ru(QCoreApplication.translate('Calclvl', 'Error')))


    @fn_timer
    def calcselected(self):
        obsids = ru(common_utils.getselectedobjectnames(self.layer), keep_containers=True)
        if not obsids:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calclvl',
                                                            'Adjustment aborted! No obsids selected.')),
                                                 ru(QCoreApplication.translate('Calclvl', 'Error')))
        else:
            self.calc(obsids)

    def log_msg(self, where_sql):
        res_sql = """SELECT DISTINCT obsid, min(date_time), max(date_time), count(obsid) FROM w_levels WHERE {} GROUP BY obsid"""
        log_msg = '\n'.join([';'.join(ru(row, keep_containers=True)) for row in db_utils.sql_load_fr_db(res_sql.format(where_sql))[1]])
        return log_msg


class Calibrlogger(qgis.PyQt.QtWidgets.QMainWindow, Calibr_Ui_Dialog): # An instance of the class Calibr_Ui_Dialog is created same time as instance of calibrlogger is created

    @fn_timer
    def __init__(self, parent, settingsdict1={}, obsid=''):
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate('Calibrlogger',
                                                          "Edit water level logger (w_levels_logger) data")))  # Set the title for the dialog
        common_utils.start_waiting_cursor()#show the user this may take a long time...
        self.obsid = obsid
        self.meas_ts = None
        self.head_ts = None
        self.head_ts_for_plot = None
        self.level_masl_ts = None
        self.logger_artist = None
        self.loggerpos_masl_or_offset_state = 1
        self.selected_line = None
        self.moving_idx = None

        self.settingsdict = settingsdict1

        text = ru(QCoreApplication.translate('Calibrlogger',
                                             "Select the observation point with logger data to be adjusted."))
        self.statusbar.showMessage(text, 0)
        self.log_calc_manual.setText("<a href=\"https://github.com/jkall/qgis-midvatten-plugin/wiki/4.-Edit-data\">Midvatten manual</a>")

        # Create a plot window with one single subplot
        self.calibrplotfigure = plt.figure()
        self.axes = self.calibrplotfigure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.calibrplotfigure )
        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )

        self.show()

        self.cid =[]

        self.button_calculate.clicked.connect(lambda x: self.set_logger_pos())
        self.button_add_offset.clicked.connect(lambda x: self.add_to_level_masl())
        self.pushButtonFrom.clicked.connect(lambda x: self.set_from_date_from_x())
        self.pushButtonTo.clicked.connect(lambda x: self.set_to_date_from_x())
        self.L1_button.clicked.connect(lambda x: self.set_adjust_data('L1_date', 'L1_level'))
        self.L2_button.clicked.connect(lambda x: self.set_adjust_data('L2_date', 'L2_level'))
        self.M1_button.clicked.connect(lambda x: self.set_adjust_data('M1_date', 'M1_level'))
        self.M2_button.clicked.connect(lambda x: self.set_adjust_data('M2_date', 'M2_level'))
        self.pushButton_from_extent.clicked.connect(lambda: self.update_date_from_extent(self.FromDateTime, self.axes.get_xbound()[0]))
        self.pushButton_to_extent.clicked.connect(lambda: self.update_date_from_extent(self.ToDateTime, self.axes.get_xbound()[1]))
        self.pushButtonupdateplot.clicked.connect(lambda x: self.update_plot())
        self.button_auto_calculate.clicked.connect(lambda x: self.logger_pos_best_fit())
        self.button_auto_fit.clicked.connect(lambda x: self.level_masl_best_fit())
        self.pushButton_delete_logger.clicked.connect(lambda: self.delete_selected_range('w_levels_logger'))
        self.adjust_trend_button.clicked.connect(lambda x: self.adjust_trend_func())

        try:
            #Support for older version of Matplotlib
            self.period_selector = RectangleSelector(self.axes, self.line_select_callback,
                                   drawtype='box', useblit=True, button=[1],
                                   minspanx=0, minspany=0, spancoords='data',
                                   interactive=False,
                                   #lineprops=dict(color="black", linestyle="-", linewidth=2, alpha=0.5),
                                   rectprops=dict(facecolor=None, edgecolor="black", alpha=0.5, fill=False))
        except:
            self.period_selector = RectangleSelector(self.axes, self.line_select_callback, useblit=True, button=[1],
                                                     minspanx=0, minspany=0, spancoords='data',
                                                     interactive=False,
                                                     # lineprops=dict(color="black", linestyle="-", linewidth=2, alpha=0.5),
                                                     props=dict(facecolor=None, edgecolor="black", alpha=0.5,
                                                                    fill=False))
        self.period_selector.set_active(False)

        self.select_nodes_button = SelectNodesButton(self, self.calibrplotfigure)
        self.move_nodes_button = MoveNodesButton(self, self.calibrplotfigure)

        self.FromDateTime.dateTimeChanged.connect(lambda: self.plot_or_update_selected_line())
        self.ToDateTime.dateTimeChanged.connect(lambda: self.plot_or_update_selected_line())
        self.get_search_radius()

        # Populate combobox with obsid from table w_levels_logger
        self.load_obsid_from_db()
        common_utils.stop_waiting_cursor()#now this long process is done and the cursor is back as normal

        self.w_levels_logger_tz = db_utils.get_timezone_from_db('w_levels_logger')
        self.w_levels_tz = db_utils.get_timezone_from_db('w_levels')

    def update_date_from_extent(self, date_time_edit, xbound_min_or_max):
        date_time_edit.setDateTime(num2date(xbound_min_or_max))

    @property
    def selected_obsid(self):
        uncalibrated_str = ' (uncalibrated)'
        return str(self.combobox_obsid.currentText().replace(uncalibrated_str, ''))

    @fn_timer
    def get_all_obsids_in_w_levels_logger(self):
        return [row[0] for row in db_utils.sql_load_fr_db("""SELECT DISTINCT obsid FROM w_levels_logger ORDER BY obsid""")[1]]

    @fn_timer
    def get_uncalibrated_obsids(self, obsid=None):
        return [row[0] for row in db_utils.sql_load_fr_db("""
                                                      SELECT obsid FROM obs_points a 
                                                      WHERE {}
                                                      EXISTS (SELECT obsid FROM w_levels_logger b 
                                                                    WHERE b.obsid = a.obsid AND
                                                                    level_masl IS NULL AND head_cm IS NOT NULL 
                                                                    LIMIT 1)
                                                      ORDER BY a.obsid""".format('' if obsid is None
                                                                                  else " obsid = '{}' AND ".format(obsid)))[1]]

    @fn_timer
    def load_obsid_from_db(self):
        self.combobox_obsid.clear()
        self.combobox_obsid.addItems(self.get_all_obsids_in_w_levels_logger())
        self.update_combobox_with_calibration_info(_obsids_with_uncalibrated_data=self.get_uncalibrated_obsids())

    @fn_timer
    def update_combobox_with_calibration_info(self, obsid=None, _obsids_with_uncalibrated_data=None):
        """
        Adds an " (uncalibrated)" suffix after each obsid containing NULL-values in the column level_masl or removes it
        if there is no NULL-values.

        :param obsid: If obsid is given, only that obsid is checked. If not given then all obsids are checked.
        :param _obsids_with_uncalibrated_data: A list of obsids which are uncalibrated.

        If only obsid is given, calibration status will be read from database for that obsid.
        If only _obsids_with_uncalibrated_data is given, all obsids will update status based on that list.
        If both obsid and _obsids_with_uncalibrated_data are given, only status for that obsid will be updated based _obsids_with_uncalibrated_data.
        If none is given, all obsids will update status based on result from database.
        :return:
        """
        uncalibrated_str = ' (uncalibrated)'

        num_entries = self.combobox_obsid.count()

        if obsid is None and _obsids_with_uncalibrated_data is None:
            obsids_with_uncalibrated_data = self.get_uncalibrated_obsids()
        elif _obsids_with_uncalibrated_data is not None:
            obsids_with_uncalibrated_data = _obsids_with_uncalibrated_data

        for idx in range(num_entries):
            current_obsid = self.combobox_obsid.itemText(idx).replace(uncalibrated_str, '')

            if obsid is not None:
                #If obsid was given, only continue loop for that one:
                if current_obsid != obsid:
                    continue
                if obsids_with_uncalibrated_data is None:
                    obsids_with_uncalibrated_data = self.get_uncalibrated_obsids(current_obsid)

            if current_obsid in obsids_with_uncalibrated_data:
                new_text = current_obsid + uncalibrated_str
            else:
                new_text = current_obsid

            self.combobox_obsid.setItemText(idx, new_text)

    @fn_timer
    def load_obsid_and_init(self):
        """ Checks the current obsid and reloads all ts.
        :return: obsid

        Info: Before, some time series was only reloaded when the obsid was changed, but this caused a problem if the
        data was changed in the background in for example spatialite gui. Now all time series are reloaded always.
        It's rather fast anyway.
        """
        common_utils.start_waiting_cursor()
        obsid = self.selected_obsid
        if not obsid:
            try:
                print('error obsid ' + str(obsid))
            except:
                pass
            #utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "ERROR: no obsid is chosen")))
            common_utils.stop_waiting_cursor()
            return None

        meas_sql = r"""SELECT date_time, level_masl FROM w_levels WHERE obsid = '%s' ORDER BY date_time"""%obsid
        self.meas_ts = self.sql_into_recarray(meas_sql)
        if self.w_levels_logger_tz and self.w_levels_tz:
            self.meas_ts.date_time = [change_timezone(x, self.w_levels_tz, self.w_levels_logger_tz)
                                      for x in self.meas_ts.date_time]

        head_level_masl_sql = r"""SELECT date_time, head_cm / 100, level_masl FROM w_levels_logger WHERE obsid = '%s' ORDER BY date_time"""%obsid
        head_level_masl_list = db_utils.sql_load_fr_db(head_level_masl_sql)[1]
        head_list = [(row[0], row[1]) for row in head_level_masl_list]
        level_masl_list = [(row[0], row[2]) for row in head_level_masl_list]

        self.head_ts = self.list_of_list_to_recarray(head_list)
        if self.plot_logger_head.isChecked():
            if self.normalize_head.isChecked():
                head_vals = [row[1] for row in head_list if row[1] is not None]
                num_head = len(head_vals)

                if num_head > 0:
                    head_mean = sum(head_vals) / float(len(head_vals))

                    level_masl_vals = [row[1] for row in level_masl_list if row[1] is not None]
                    num_level_masl_vals = len(level_masl_vals)
                    meas_vals = [x for x in self.meas_ts.values if x is not None]
                    num_meas_vals = len(meas_vals)
                    if num_level_masl_vals or num_meas_vals:
                        if num_level_masl_vals:
                            level_masl_mean = sum(level_masl_vals) / float(num_level_masl_vals)
                        else:
                            level_masl_mean = sum(meas_vals) / float(num_meas_vals)

                        normalized_head = [(row[0], row[1] + (level_masl_mean - head_mean) if row[1] is not None else None) for row in head_list]

                        self.head_ts_for_plot = self.list_of_list_to_recarray(normalized_head)
                    else:
                        common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Calibrlogger', 'No calibrated level_masl values to normalize against.')))
                        self.head_ts_for_plot = self.head_ts
                else:
                    common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Calibrlogger', 'No head values to normalize against.')))
                    self.head_ts_for_plot = self.head_ts
            else:
                self.head_ts_for_plot = self.head_ts
        else:
            self.head_ts_for_plot = None

        self.obsid = obsid

        self.level_masl_ts = self.list_of_list_to_recarray(level_masl_list)

        calibration_status = [obsid] if [row[1] for row in level_masl_list if row[1] is None] else []
        self.update_combobox_with_calibration_info(obsid=obsid, _obsids_with_uncalibrated_data=calibration_status)

        self.setlastcalibration(obsid)
        common_utils.stop_waiting_cursor()
        return obsid

    @fn_timer
    def setlastcalibration(self, obsid):
        if not obsid=='':
            self.lastcalibr = self.getlastcalibration(obsid)
            text = ru(QCoreApplication.translate('Calibrlogger', """There is no earlier known position for the logger in %s"""))%self.selected_obsid
            if self.lastcalibr:
                if all([self.lastcalibr[0][0], self.lastcalibr[0][1] is not None, self.lastcalibr[0][1] != '']):
                    text = ru(QCoreApplication.translate('Calibrlogger', "Last pos. for logger in %s was %s masl at %s"))%(obsid, '{:.3f}'.format(self.lastcalibr[0][1]), str(self.lastcalibr[0][0]))

            self.INFO.setText(text)

    @fn_timer
    def getlastcalibration(self, obsid):
        sql = "SELECT date_time, (level_masl - (head_cm/100)) AS loggerpos FROM w_levels_logger WHERE date_time = (SELECT max(date_time) AS date_time FROM w_levels_logger WHERE obsid = '%s' AND (CASE WHEN level_masl IS NULL THEN -1000 ELSE level_masl END) > -990 AND level_masl IS NOT NULL AND head_cm IS NOT NULL) AND obsid = '%s' "%(obsid, obsid)
        lastcalibr = db_utils.sql_load_fr_db(sql)[1]
        return lastcalibr

    @fn_timer
    def set_logger_pos(self, obsid=None):
        self.loggerpos_masl_or_offset_state = 1
        if obsid is None:
            obsid = self.load_obsid_and_init()
        if not self.logger_elevation.text() == '':
            self.calibrate(obsid)
            self.update_plot()

    @fn_timer
    def add_to_level_masl(self, obsid=None):
        self.loggerpos_masl_or_offset_state = 0
        if obsid is None:
            obsid = self.load_obsid_and_init()
        if not self.offset.text() == '':
            self.calibrate(obsid)
        self.update_plot()

    @fn_timer
    def calibrate(self, obsid=None):

        if obsid is None:
            obsid = self.load_obsid_and_init()

        if not obsid =='':
            fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
            to_d_t = self.ToDateTime.dateTime().toPyDateTime()

            if self.loggerpos_masl_or_offset_state == 1:
                self.update_level_masl_from_head(obsid, fr_d_t, to_d_t, self.logger_elevation.text())
            else:
                self.update_level_masl_from_level_masl(obsid, fr_d_t, to_d_t, self.offset.text())

        else:

            text = ru(QCoreApplication.translate('Calibrlogger',
                                                 "Select the observation point with logger data to be adjusted."))
            self.statusbar.showMessage(text, 0)

    @fn_timer
    def update_level_masl_from_level_masl(self, obsid, fr_d_t, to_d_t, newzref):
        common_utils.start_waiting_cursor()
        """ Updates the level masl using newzref
        :param obsid: (str) The obsid
        :param fr_d_t: (datetime) start of calibration
        :param to_d_t: (datetime) end of calibration
        :param newzref: (int/float/str [m]) The correction that should be made against the head [m]
        :return: None
        """
        sql =r"""UPDATE w_levels_logger SET level_masl = """
        sql += str(newzref)
        sql += """ + level_masl WHERE obsid = '"""
        sql += obsid
        sql += """' AND level_masl IS NOT NULL"""
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first.
        date_time_as_epoch = db_utils.cast_date_time_as_epoch()
        sql += """ AND %s >= %s"""%(date_time_as_epoch, str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds()))
        sql += """ AND %s <= %s""" % (date_time_as_epoch, str((to_d_t - datetime.datetime(1970, 1, 1)).total_seconds()))
        dummy = db_utils.sql_alter_db(sql)
        common_utils.stop_waiting_cursor()

    @fn_timer
    def update_level_masl_from_head(self, obsid, fr_d_t, to_d_t, newzref):
        """ Updates the level masl using newzref
        :param obsid: (str) The obsid
        :param fr_d_t: (datetime) start of calibration
        :param to_d_t: (datetime) end of calibration
        :param newzref: (int/float/str [m]) The correction that should be made against the head [m]
        :return: None
        """
        common_utils.start_waiting_cursor()
        sql =r"""UPDATE w_levels_logger SET level_masl = """
        sql += str(newzref)
        sql += """ + head_cm / 100 WHERE obsid = '"""
        sql += obsid
        sql += """' AND head_cm IS NOT NULL"""
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first (but now we changed to > but kept .total_seconds())
        date_time_as_epoch = db_utils.cast_date_time_as_epoch()
        sql += """ AND %s >= %s"""%(date_time_as_epoch, str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds()))
        sql += """ AND %s <= %s""" % (date_time_as_epoch, str((to_d_t - datetime.datetime(1970, 1, 1)).total_seconds()))
        dummy = db_utils.sql_alter_db(sql)
        try:
            print(str(dummy))
        except:
            pass
        common_utils.stop_waiting_cursor()

    @fn_timer
    def sql_into_recarray(self, sql):
        """ Converts and runs an sql-string and turns the answer into an np.recarray and returns it"""
        list_of_lists = db_utils.sql_load_fr_db(sql)[1]
        return self.list_of_list_to_recarray(list_of_lists)

    @fn_timer
    def list_of_list_to_recarray(self, list_of_lists):
        my_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array
        table = np.array(list_of_lists, dtype=my_format)  #NDARRAY
        table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values
        return table2

    @fn_timer
    def update_plot(self):
        """ Plots self.level_masl_ts, self.meas_ts and maybe self.head_ts """
        self.reset_plot_selects_and_calib_help()
        self.statusbar.showMessage(ru(QCoreApplication.translate('Calibrlogger', "Updating plot...")), 0)
        last_used_obsid = self.obsid
        obsid = self.load_obsid_and_init()
        common_utils.start_waiting_cursor()
        if obsid == None:
            self.statusbar.clearMessage()
            return
        self.selected_line = None
        self.axes.clear()

        p=[None]*2 # List for plot objects

        # Load manual reading (full time series) for the obsid
        if self.meas_ts.size and self.contains_more_than_nan(self.meas_ts):
            self.plot_recarray(self.axes, self.meas_ts, obsid + ru(QCoreApplication.translate('Calibrlogger', ' measurements')),
                               style=dict(linestyle='-',
                                          marker='o',
                                          zorder=50,
                                          color='#1f77b4ff',
                                          markersize=10,
                                          markerfacecolor="None",
                                          markeredgecolor='#1f77b4ff',
                                          markeredgewidth=3
                                          ))


        if self.loggerLineNodes.isChecked():
            marker = 'o'
        else:
            marker = ''

        logger_time_list = self.timestring_list_to_time_list(self.a_recarray_to_timestring_list(self.level_masl_ts))
        if self.level_masl_ts.size and self.contains_more_than_nan(self.level_masl_ts):
            self.logger_artist = self.plot_recarray(self.axes, self.level_masl_ts,
                                                    obsid + ru(QCoreApplication.translate('Calibrlogger',
                                                                                          ' logger water level')),
                                                    time_list=logger_time_list,
                                                    style=dict(linestyle='-', picker=5, markersize=3, marker=marker,
                                                    zorder=10, color='#ff7f0eff'))[0]
        else:
            self.logger_artist = None

        if self.plot_logger_head.isChecked() and self.head_ts_for_plot.size and self.contains_more_than_nan(self.head_ts_for_plot):
            self.plot_recarray(self.axes, self.head_ts_for_plot, obsid + ru(QCoreApplication.translate('Calibrlogger', ' logger head')),
                               style=dict(linestyle='--', zorder=5, color='#c1c1c1ff', marker=''), time_list=logger_time_list,)

        self.plot_or_update_selected_line()

        """ Finish plot """
        self.axes.grid(True)
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.calibrplotfigure.autofmt_xdate()
        self.axes.set_ylabel(ru(QCoreApplication.translate('Calibrlogger', 'Level (masl)')))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        self.axes.set_title(ru(QCoreApplication.translate('Calibrlogger', 'Plot for ')) + str(obsid))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        for label in self.axes.xaxis.get_ticklabels():
            label.set_fontsize(8)
        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(8)

        self.calibrplotfigure.tight_layout()

        if self.axes.legend_ is None:
            leg = self.axes.legend()

        self.canvas.draw()
        #plt.close(self.calibrplotfigure)#this closes reference to self.calibrplotfigure
        self.statusbar.clearMessage()

        if last_used_obsid == self.obsid:
            self.mpltoolbar.forward()
        else:
            #Clear choices
            self.reset_settings()
            self.mpltoolbar.update()

        common_utils.stop_waiting_cursor()

        self.toggle_move_nodes(self.move_nodes_button.button().isChecked())
        self.toggle_select_nodes(self.select_nodes_button.button().isChecked())

    @fn_timer
    def plot_recarray(self, axes, a_recarray, label, time_list=None, style=None):
        """ Plots a recarray to the supplied axes object """
        if time_list is None:
            time_list = self.timestring_list_to_time_list(self.a_recarray_to_timestring_list(a_recarray))
        return self.plot_the_recarray(axes, time_list, a_recarray, label, style=style)

    @fn_timer
    def a_recarray_to_timestring_list(self, a_recarray):
        return [a_recarray.date_time[idx] for idx in range(len(a_recarray))]

    @fn_timer
    def timestring_list_to_time_list(self, timestring_list):
        """Get help from function datestr2num to get date and time into float"""
        return datestr2num(timestring_list)

    @fn_timer
    def contains_more_than_nan(self, a_recarray):
        try:
            not_nan = self.list_of_list_to_recarray(list(filter(lambda v: v == v, a_recarray)))
        except TypeError:
            print("Error in contains_more_than_nan, recarray: " + str(a_recarray))
            raise
        if not_nan.size:
            return True
        else:
            return False

    @fn_timer
    def plot_the_recarray(self, axes, time_list, a_recarray, label, style=None):
        if style is None:
            style = {}
        return axes.plot_date(time_list, a_recarray.values, label=label, **style) #, xdate=True)

    @fn_timer
    def set_from_date_from_x(self):
        """ Used to set the self.FromDateTime by clicking on a line node in the plot self.canvas """
        self.set_date_from_x(self.FromDateTime, ru(QCoreApplication.translate('Calibrlogger', "Select a date to use as \"from\"")),
                             from_node=False)

    @fn_timer
    def set_to_date_from_x(self):
        """ Used to set the self.ToDateTime by clicking on a line node in the plot self.canvas """
        self.set_date_from_x(self.ToDateTime, ru(QCoreApplication.translate('Calibrlogger', "Select a date to use as \"to\"")),
                             from_node=False)

    @fn_timer
    def set_date_from_x_onclick(self, event, date_holder, from_node=False):
        """ Sets the date_holder to a date from a line node closest to the pick event

            date_holder: a QDateTimeEdit object.
        """
        if from_node:
            found_date = num2date(event.artist.get_xdata()[event.ind[0]])
        else:
            found_date = num2date(event.xdata)

        self.reset_plot_selects_and_calib_help()
        date_holder.setDateTime(found_date)

    @fn_timer
    def reset_plot_selects_and_calib_help(self):
        """ Reset self.cid and self.calib_help """
        self.reset_cid()
        self.statusbar.clearMessage()

    @fn_timer
    def reset_settings(self):

        self.ToDateTime.setDateTime(datestring_to_date('2099-12-31 23:59:59'))
        self.offset.setText('')
        self.bestFitSearchRadius.setText('60 minutes')
        #self.mpltoolbar.home()

        last_calibration = self.getlastcalibration(self.obsid)
        try:
            if last_calibration[0][1] and last_calibration[0][0]:
                self.logger_elevation.setText('{:.5f}'.format(last_calibration[0][1]))
                self.FromDateTime.setDateTime(datestring_to_date(last_calibration[0][0]) + datetime.timedelta(milliseconds=1))
            else:
                self.logger_elevation.setText('')
                self.FromDateTime.setDateTime(datestring_to_date('2099-12-31 23:59:59'))
        except Exception as e:
            common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Calibrlogger', 'Getting last calibration failed for obsid %s, msg: %s')) % (self.obsid, str(e)))
            self.logger_elevation.setText('')
            self.FromDateTime.setDateTime(datestring_to_date('2099-12-31 23:59:59'))

    @fn_timer
    def reset_cid(self):
        """ Resets self.cid to an empty list and disconnects unused events """
        for x in self.cid:
            self.canvas.mpl_disconnect(x)
        self.cid = []

    @fn_timer
    def logger_pos_best_fit(self):
        self.loggerpos_masl_or_offset_state = 1
        self.calc_best_fit()

    @fn_timer
    def level_masl_best_fit(self):
        self.loggerpos_masl_or_offset_state = 0
        self.calc_best_fit()

    @fn_timer
    def calc_best_fit(self):
        """ Calculates the self.logger_elevation from self.meas_ts and self.head_ts

            First matches measurements from self.meas_ts to logger values from
            self.head_ts. This is done by making a mean of all logger values inside
            self.meas_ts date - search_radius and self.meas_ts date + search_radius.
            (this could probably be change to get only the closest logger value
            inside the search_radius instead)
            (search_radius is gotten from self.get_search_radius())

            Then calculates the mean of all matches and set to self.logger_elevation.
        """
        obsid = self.load_obsid_and_init()
        common_utils.start_waiting_cursor()
        self.reset_plot_selects_and_calib_help()
        search_radius = self.get_search_radius()
        if self.loggerpos_masl_or_offset_state == 1:# UPDATE TO RELEVANT TEXT
            logger_ts = self.head_ts
            text_field = self.logger_elevation
            calib_func = self.set_logger_pos
        else:# UPDATE TO RELEVANT TEXT
            logger_ts = self.level_masl_ts
            text_field = self.offset
            calib_func = self.add_to_level_masl

        coupled_vals = self.match_ts_values(self.meas_ts, logger_ts, search_radius)
        if not coupled_vals:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "There was no match found between measurements and logger values inside the chosen period.\n Try to increase the search radius or adjust the period!")))
        else:
            calculated_diff = str(common_utils.calc_mean_diff(coupled_vals))
            if not calculated_diff or calculated_diff.lower() == 'nan':
                common_utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "There was no matched measurements or logger values inside the chosen period.\n Try to increase the search radius!")))
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Calibrlogger', "Calculated water level from logger: midvatten_utils.calc_mean_diff(coupled_vals) didn't return a useable value.")))
            else:
                text_field.setText(calculated_diff)
                calib_func(obsid)

        common_utils.stop_waiting_cursor()

    @fn_timer
    def match_ts_values(self, meas_ts, logger_ts, search_radius_tuple):
        """ Matches two timeseries values for shared timesteps

            For every measurement point, a mean of logger values inside
            measurementpoint + x minutes to measurementpoint - x minutes
            is coupled together.

            At the first used measurement, only logger values greater than
            the set start date is used.
            At the last measurement, only logger values lesser than the set end
            date is used.
            This is done so that values from another logger reposition is not
            mixed with the chosen logger positioning. (Hard to explain).
        """
        coupled_vals = []

        #Get the search radius, default to 60 minutes
        search_radius = int(search_radius_tuple[0])
        search_radius_period = search_radius_tuple[1]

        logger_gen = common_utils.ts_gen(logger_ts)
        try:
            l = next(logger_gen)
        except StopIteration:
            return None
        log_vals = []

        all_done = False
        #The .replace(tzinfo=None) is used to remove info about timezone. Needed for the comparisons. This should not be a problem though as the date scale in the plot is based on the dates from the database.
        outer_begin = self.FromDateTime.dateTime().toPyDateTime().replace(tzinfo=None)
        outer_end = self.ToDateTime.dateTime().toPyDateTime().replace(tzinfo=None)
        logger_step = datestring_to_date(l[0]).replace(tzinfo=None)
        for m in meas_ts:
            if logger_step is None:
                break
            meas_step = datestring_to_date(m[0]).replace(tzinfo=None)

            step_begin = dateshift(meas_step, -search_radius, search_radius_period)
            step_end = dateshift(meas_step, search_radius, search_radius_period)

            if step_end < outer_begin:
                continue
            if step_begin > outer_end:
                break

            #Skip logger steps that are earlier than the chosen begin date or are not inside the measurement period.
            while logger_step <= step_begin or logger_step <= outer_begin:
                try:
                    l = next(logger_gen)
                except StopIteration:
                    all_done = True
                    break
                logger_step = datestring_to_date(l[0]).replace(tzinfo=None)

            log_vals = []

            while logger_step is not None and step_begin <= logger_step <= step_end and outer_begin <= logger_step <= outer_end:
                if not math.isnan(float(l[1])) or l[1] in ('nan', 'NULL'):
                    log_vals.append(float(l[1]))
                try:
                    l = next(logger_gen)
                except StopIteration:
                    all_done = True
                    break
                logger_step = datestring_to_date(l[0]).replace(tzinfo=None)

            if log_vals:
                mean = np.mean(log_vals)
                if not math.isnan(mean):
                    coupled_vals.append((m[1], mean))
            if all_done:
                break
        return coupled_vals

    @fn_timer
    def get_search_radius(self):
        """ Get the period search radius, default to 60 minutes """
        if not self.bestFitSearchRadius.text():
            search_radius = '60 minutes'
            self.bestFitSearchRadius.setText(search_radius)
        else:
            search_radius = self.bestFitSearchRadius.text()

        search_radius_splitted = ru(search_radius).split()
        if len(search_radius_splitted) != 2:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "Must write time resolution also, ex. %s")) % '60 minutes')
        return tuple(search_radius_splitted)

    @fn_timer
    def deactivate_pan_zoom(self):
        """ Deactivates the NavigationToolbar pan or zoom feature if they are currently active """
        try:
            a = self.mpltoolbar._active
        except AttributeError:
            # Adjustment for matplotlib ~3.5
            a = self.mpltoolbar.mode.name
        if a.upper() == "PAN":
            self.mpltoolbar.pan()
        elif a.upper() == "ZOOM":
            self.mpltoolbar.zoom()

    @fn_timer
    def delete_selected_range(self, table_name):
        """ Deletes the current selected range from the database from w_levels_logger
        :return: De
        """
        current_loaded_obsid = self.obsid
        selected_obsid = self.load_obsid_and_init()
        if current_loaded_obsid != selected_obsid:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "Error!\n The obsid selection has been changed but the plot has not been updated. No deletion done.\nUpdating plot.")))
            self.update_plot()
            return
        elif selected_obsid is None:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "Error!\n No obsid was selected. No deletion done.\nUpdating plot.")))
            self.update_plot()
            return

        fr_d_t = str((self.FromDateTime.dateTime().toPyDateTime() - datetime.datetime(1970,1,1)).total_seconds())
        to_d_t = str((self.ToDateTime.dateTime().toPyDateTime() - datetime.datetime(1970,1,1)).total_seconds())

        dbconnection = db_utils.DbConnectionManager()
        dbtype = dbconnection.dbtype
        dbconnection.closedb()
        if dbtype == 'spatialite':
            sql = f"""DELETE FROM "{table_name}" 
                      WHERE obsid = '{selected_obsid}'
                         AND CAST(strftime('%s', date_time) AS NUMERIC) >= '{fr_d_t}'
                         AND CAST(strftime('%s', date_time) AS NUMERIC) <= '{to_d_t}'"""
        else:
            sql = f"""DELETE FROM "{table_name}" 
                      WHERE obsid = '{selected_obsid}'
                      AND EXTRACT(EPOCH FROM date_time::timestamp) >= '{fr_d_t}'
                      AND EXTRACT(EPOCH FROM date_time::timestamp) <= '{to_d_t}'"""

        really_delete = common_utils.Askuser("YesNo", ru(QCoreApplication.translate('Calibrlogger', "Do you want to delete the period %s to %s for obsid %s from table %s?")) % (str(self.FromDateTime.dateTime().toPyDateTime()), str(self.ToDateTime.dateTime().toPyDateTime()), selected_obsid, table_name)).result
        if really_delete:
            common_utils.start_waiting_cursor()
            db_utils.sql_alter_db(sql)
            common_utils.stop_waiting_cursor()
            self.update_plot()

    @fn_timer
    def set_date_from_x(self, datetimeedit, help_msg=None, from_node=False):
        """ Used to set the self.ToDateTime by clicking on a line node in the plot self.canvas """
        self.reset_plot_selects_and_calib_help()
        self.deactivate_pan_zoom()
        if help_msg:
            self.statusbar.showMessage(help_msg, 0)
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        if from_node:
            event = 'pick_event'
        else:
            event = 'button_press_event'
        self.cid.append(self.canvas.mpl_connect(event, lambda event: self.set_date_from_x_onclick(event, datetimeedit, from_node)))

    @fn_timer
    def set_adjust_data(self, date_holder, level_holder):
        self.reset_cid()
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        self.cid.append(self.canvas.mpl_connect('button_press_event', lambda event: self.set_adjust_data_on_click(event, date_holder, level_holder)))

    @fn_timer
    def set_adjust_data_on_click(self, event, date_var, level_var):
        getattr(self, level_var).setText('{:.5f}'.format(event.ydata))
        getattr(self, date_var).setDateTime(num2date(float(event.xdata)))
        self.reset_cid()

    @fn_timer
    def adjust_trend_func(self):

        obsid = self.load_obsid_and_init()
        if obsid is None:
            return None

        data = {'obsid': obsid,
                'adjust_start_date': long_dateformat(self.FromDateTime.dateTime().toPyDateTime()),
                'adjust_end_date': long_dateformat(self.ToDateTime.dateTime().toPyDateTime()),
                'L1_date': db_utils.cast_date_time_as_epoch(date_time=long_dateformat(self.L1_date.dateTime().toPyDateTime())),
                'L2_date': db_utils.cast_date_time_as_epoch(date_time=long_dateformat(self.L2_date.dateTime().toPyDateTime())),
                'M1_date': db_utils.cast_date_time_as_epoch(date_time=long_dateformat(self.M1_date.dateTime().toPyDateTime())),
                'M2_date': db_utils.cast_date_time_as_epoch(date_time=long_dateformat(self.M2_date.dateTime().toPyDateTime())),
                'L1_level': str(float(self.L1_level.text())),
                'L2_level': str(float(self.L2_level.text())),
                'M1_level': str(float(self.M1_level.text())),
                'M2_level': str(float(self.M2_level.text())),
                'date_as_numeric': db_utils.cast_date_time_as_epoch()}

        sql = """SELECT level_masl FROM w_levels_logger WHERE level_masl IS NOT NULL AND obsid = '{obsid}'
                                                              AND date_time >= '{adjust_start_date}'
                                                              AND date_time <= '{adjust_end_date}'""".format(**{
            'obsid': data['obsid'], 'adjust_start_date': data['adjust_start_date'],
                                                         'adjust_end_date': data['adjust_end_date']})
        res = db_utils.sql_load_fr_db(sql)[1]
        if not res:
            common_utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger',
                                                            """Warning!\n No data found within the chosen period. No trend adjustment done!\nTry changing "from" and "to".""")))
            return

        sql = """
                UPDATE w_levels_logger SET level_masl = level_masl -
                (
                 ((({L1_level} - {L2_level}) / ({L1_date} - {L2_date}))
                 - (({M1_level} - {M2_level}) / ({M1_date} - {M2_date})))
                  * ({date_as_numeric} - {L1_date})
                )
                WHERE obsid = '{obsid}' AND date_time >= '{adjust_start_date}' AND date_time <= '{adjust_end_date}'
            """.format(**data)
        common_utils.start_waiting_cursor()
        db_utils.sql_alter_db(sql)
        common_utils.stop_waiting_cursor()
        self.update_plot()

    def plot_or_update_selected_line(self):
        if self.logger_artist is None:
            return
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime().replace(tzinfo=None)
        to_d_t = self.ToDateTime.dateTime().toPyDateTime().replace(tzinfo=None)
        xdata = self.logger_artist.get_xdata()
        ydata = [y if fr_d_t <= num2date(xdata[idx]).replace(tzinfo=None) <= to_d_t else None for idx, y in
                 enumerate(self.logger_artist.get_ydata())]

        if self.selected_line is None:
            self.selected_line = self.axes.plot(xdata, ydata, linestyle='none',
                                            marker='o',
                                            markerfacecolor="None",
                                            markeredgecolor='black',
                                            markeredgewidth=1,
                                            markersize=4,
                                            zorder=30,
                                            label=ru(QCoreApplication.translate('Calibrlogger', "Selected nodes")))[0]
        else:
            self.selected_line.set_ydata(ydata)
        self.canvas.draw_idle()

    def connect_selected_line_move(self):
        self.cid.append(self.canvas.mpl_connect('pick_event', self.node_pressed))
        self.cid.append(self.canvas.mpl_connect('motion_notify_event', self.node_moving))
        self.cid.append(self.canvas.mpl_connect('button_release_event', self.node_released))

    def node_pressed(self, event):
        if isinstance(event, PickEvent) and event.mouseevent.button is MouseButton.LEFT:
            if self.logger_artist is not None and event.artist is self.logger_artist:
                self.moving_idx = event.ind[0]

    def node_moving(self, event):
        if self.moving_idx is not None and self.selected_line is not None:
            ydata = self.selected_line.get_ydata()
            _y = ydata[self.moving_idx]
            if _y is None:
                return
            diff = event.ydata - _y
            new_ydata = [y+diff if y is not None else None for y in ydata]
            self.selected_line.set_ydata(new_ydata)
            self.canvas.draw_idle()

    def node_released(self, event=None):
        if self.moving_idx is not None:
            logger_y = self.logger_artist.get_ydata()[self.moving_idx]
            selected_y = self.selected_line.get_ydata()[self.moving_idx]
            if logger_y is not None and selected_y is not None:
                offset = self.selected_line.get_ydata()[self.moving_idx] - self.logger_artist.get_ydata()[self.moving_idx]
                self.moving_idx = None
                if offset:
                    self.loggerpos_masl_or_offset_state = 1
                    self.offset.setText('{:.5f}'.format(offset))
                    self.add_to_level_masl()
            self.moving_idx = None

    def line_select_callback(self, eclick, erelease):
        """
        https://matplotlib.org/stable/gallery/widgets/rectangle_selector.html
        https://matplotlib.org/stable/gallery/widgets/rectangle_selector.html?highlight=rectangle%20selector

        :param eclick:
        :param erelease:
        :return:
        """
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        self.logger_artist.get_xdata()
        y_idx = [idx for idx, y in enumerate(self.logger_artist.get_ydata()) if min(y1, y2) <= y <= max(y1, y2)]
        x_idx = [idx for idx, x in enumerate(self.logger_artist.get_xdata()) if min(x1, x2) <= x <= max(x1, x2)]
        found_idx = [idx for idx in x_idx if idx in y_idx]
        if found_idx:
            self.FromDateTime.setDateTime(num2date(self.logger_artist.get_xdata()[min(found_idx)]))
            self.ToDateTime.setDateTime(num2date(self.logger_artist.get_xdata()[max(found_idx)]))

    def toggle_move_nodes(self, on):
        if on:
            self.reset_cid()
            self.deactivate_pan_zoom()
            self.period_selector.set_active(False)
            self.select_nodes_button.uncheck()
            self.connect_selected_line_move()

    def toggle_select_nodes(self, on):
        if on:
            self.reset_cid()
            self.deactivate_pan_zoom()
            self.move_nodes_button.uncheck()
        self.period_selector.set_active(on)


class NavigationButton(QtWidgets.QWidget):
    def __init__(self, parent, fig):
        super().__init__(parent)
        self.parent = parent
        self.fig = fig
        self.actions = {}

    def connect_toolbar(self):
        self.canvas = self.fig.canvas
        self.mpltoolbar = self.canvas.toolbar
        self._add_buttons_to_toolbar()

    def uncheck(self):
        for v in self.actions.values():
            v.setChecked(False)

    def _add_buttons_to_toolbar(self):
        self.actions = {}
        for text, callback, tooltip_text, icon in self._button_setup:
            self.actions[text] = add_action_to_navigation_toolbar(self.mpltoolbar, text, callback, tooltip_text, icon,
                                                                  set_checkable=True)


class SelectNodesButton(NavigationButton):
    def __init__(self, parent, fig):
        super().__init__(parent, fig)
        self._button_setup = [("select nodes", self.clicked, "Select nodes",
                               os.path.join(os.path.dirname(__file__), '..', 'icons', 'select_nodes.png'))]
        self.connect_toolbar()

    def button(self):
        return list(self.actions.values())[0]

    def clicked(self):
        if not self.button().isChecked():
            self.parent.reset_cid()
        self.parent.toggle_select_nodes(self.button().isChecked())


class MoveNodesButton(NavigationButton):
    def __init__(self, parent, fig):
        super().__init__(parent, fig)
        self._button_setup = [("move nodes", self.clicked, "Move nodes",
                               os.path.join(os.path.dirname(__file__), '..', 'icons', 'move_nodes.png'))]
        self.connect_toolbar()

    def button(self):
        return list(self.actions.values())[0]

    def clicked(self):
        if not self.button().isChecked():
            self.parent.reset_cid()
        self.parent.toggle_move_nodes(self.button().isChecked())




