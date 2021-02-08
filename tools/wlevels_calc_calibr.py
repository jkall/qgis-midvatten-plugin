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
from __future__ import print_function
from __future__ import absolute_import
from builtins import next
from builtins import str
from builtins import range
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import os
from functools import partial
from qgis.PyQt import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import datestr2num, num2date
import numpy as np

import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt import QtCore
from qgis.PyQt.QtGui import QCursor

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar
import datetime
import midvatten_utils as utils
from midvatten_utils import timer, fn_timer, returnunicode as ru
from date_utils import dateshift, datestring_to_date, long_dateformat
import db_utils

Calibr_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calibr_logger_dialog_integrated.ui'))[0]
Calc_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calc_lvl_dialog.ui'))[0]


class Calclvl(qgis.PyQt.QtWidgets.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    @fn_timer
    def __init__(self, parent,layerin):
        qgis.PyQt.QtWidgets.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = utils.getselectedobjectnames()
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
                    utils.pop_up_info(ru(QCoreApplication.translate('Calclvl', 'Adjustment aborted! There seems to be NULL values in your table obs_points, column h_toc.')), ru(QCoreApplication.translate('Calclvl', 'Error')))
                    return None

            else:
                obsids = [obsid for obsid in obsids if obsid not in obsid_with_h_toc_null]

            if not obsids:
                utils.pop_up_info(ru(QCoreApplication.translate('Calclvl',
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

        utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('Calclvl', 'Calculation done, see log message panel')),
                                    log_msg=ru(QCoreApplication.translate('Calclvl', 'H_toc added and level_masl calculated for\nobsid;min date;max date;calculated number of measurements: \n%s'))%(self.updated_level_masl))
        self.close()

    @fn_timer
    def calcall(self):
        obsids = db_utils.sql_load_fr_db("""SELECT DISTINCT obsid FROM w_levels""")[1]
        if obsids:
            obsids = [x[0] for x in obsids]
            self.calc(obsids)
        else:
            utils.pop_up_info(ru(QCoreApplication.translate('Calclvl',
                                                            'Adjustment aborted! No obsids in w_levels.')),
                              ru(QCoreApplication.translate('Calclvl', 'Error')))


    @fn_timer
    def calcselected(self):
        obsids = ru(utils.getselectedobjectnames(self.layer), keep_containers=True)
        if not obsids:
            utils.pop_up_info(ru(QCoreApplication.translate('Calclvl',
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
        utils.start_waiting_cursor()#show the user this may take a long time...
        self.obsid = obsid
        self.log_pos = None
        self.y_pos = None
        self.meas_ts = None
        self.head_ts = None
        self.head_ts_for_plot = None
        self.level_masl_ts = None
        self.loggerpos_masl_or_offset_state = 1

        self.settingsdict = settingsdict1
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate('Calibrlogger', "Calculate water level from logger"))) # Set the title for the dialog
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

        self.pushButtonSet.clicked.connect(lambda x: self.set_logger_pos())
        self.pushButtonAdd.clicked.connect(lambda x: self.add_to_level_masl())
        self.pushButtonFrom.clicked.connect(lambda x: self.set_from_date_from_x())
        self.pushButtonTo.clicked.connect(lambda x: self.set_to_date_from_x())
        self.L1_button.clicked.connect(lambda x: self.set_adjust_data('L1_date', 'L1_level'))
        self.L2_button.clicked.connect(lambda x: self.set_adjust_data('L2_date', 'L2_level'))
        self.M1_button.clicked.connect(lambda x: self.set_adjust_data('M1_date', 'M1_level'))
        self.M2_button.clicked.connect(lambda x: self.set_adjust_data('M2_date', 'M2_level'))
        self.pushButton_from_extent.clicked.connect(lambda: self.FromDateTime.setDateTime(num2date(self.axes.get_xbound()[0])))
        self.pushButton_to_extent.clicked.connect(lambda: self.ToDateTime.setDateTime(num2date(self.axes.get_xbound()[1])))
        self.pushButtonupdateplot.clicked.connect(lambda x: self.update_plot())
        self.pushButtonLpos.clicked.connect(lambda x: self.catch_old_level())
        self.pushButtonMpos.clicked.connect(lambda x: self.catch_new_level())
        self.pushButtonMpos.setEnabled(False)
        self.pushButtonCalcBestFit.clicked.connect(lambda x: self.logger_pos_best_fit())
        self.pushButtonCalcBestFit.setToolTip(ru(QCoreApplication.translate('Calibrlogger', 'This will calibrate all values inside the chosen period\nusing the mean difference between head_cm and w_levels measurements.\n\nThe search radius is the maximum time distance allowed\n between a logger measurement and a w_level measurement.')))
        self.pushButtonCalcBestFit2.clicked.connect(lambda x: self.level_masl_best_fit())
        self.pushButtonCalcBestFit2.setToolTip(ru(QCoreApplication.translate('Calibrlogger', 'This will calibrate all values inside the chosen period\nusing the mean difference between level_masl and w_levels measurements.\n\nThe search radius is the maximum time distance allowed\n between a logger measurement and a w_level measurement.')))
        self.pushButton_delete_logger.clicked.connect(lambda: self.delete_selected_range('w_levels_logger'))
        self.adjust_trend_button.clicked.connect(lambda x: self.adjust_trend_func())

        self.get_search_radius()

        # Populate combobox with obsid from table w_levels_logger
        self.load_obsid_from_db()

        utils.stop_waiting_cursor()#now this long process is done and the cursor is back as normal

    @property
    def selected_obsid(self):
        uncalibrated_str = ' (uncalibrated)'
        return str(self.combobox_obsid.currentText().replace(uncalibrated_str, ''))

    @fn_timer
    def get_all_obsids_in_w_levels_logger(self):
        return [row[0] for row in db_utils.sql_load_fr_db("""SELECT DISTINCT obsid FROM w_levels_logger ORDER BY obsid""")[1]]

    @fn_timer
    def get_uncalibrated_obsids(self, obsid=None):
        return [row[0] for row in db_utils.sql_load_fr_db("""SELECT DISTINCT obsid 
                                                      FROM w_levels_logger 
                                                      WHERE level_masl IS NULL AND head_cm IS NOT NULL 
                                                      {}
                                                      ORDER BY obsid""".format('' if obsid is None
                                                                                  else " AND obsid = '{}' ".format(obsid)))[1]]

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
        utils.start_waiting_cursor()
        obsid = self.selected_obsid
        if not obsid:
            try:
                print('error obsid ' + str(obsid))
            except:
                pass
            #utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "ERROR: no obsid is chosen")))
            utils.stop_waiting_cursor()
            return None

        meas_sql = r"""SELECT date_time, level_masl FROM w_levels WHERE obsid = '%s' ORDER BY date_time"""%obsid
        self.meas_ts = self.sql_into_recarray(meas_sql)

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
                    if num_level_masl_vals > 0:
                        level_masl_mean = sum(level_masl_vals) / float(num_level_masl_vals)

                        normalized_head = [(row[0], row[1] + (level_masl_mean - head_mean) if row[1] is not None else None) for row in head_list]

                        self.head_ts_for_plot = self.list_of_list_to_recarray(normalized_head)
                    else:
                        utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Calibrlogger', 'No calibrated level_masl values to normalize against.')))
                        self.head_ts_for_plot = self.head_ts
                else:
                    utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Calibrlogger', 'No head values to normalize against.')))
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
        utils.stop_waiting_cursor()
        return obsid

    @fn_timer
    def setlastcalibration(self, obsid):
        if not obsid=='':
            self.lastcalibr = self.getlastcalibration(obsid)
            text = ru(QCoreApplication.translate('Calibrlogger', """There is no earlier known position for the logger in %s"""))%self.selected_obsid
            if self.lastcalibr:
                if all([self.lastcalibr[0][0], self.lastcalibr[0][1] is not None, self.lastcalibr[0][1] != '']):
                    text = ru(QCoreApplication.translate('Calibrlogger', "Last pos. for logger in %s was %s masl at %s"))%(obsid, '{:.5f}'.format(self.lastcalibr[0][1]), str(self.lastcalibr[0][0]))

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
        if not self.LoggerPos.text() == '':
            self.calibrate(obsid)
            self.update_plot()

    @fn_timer
    def add_to_level_masl(self, obsid=None):
        self.loggerpos_masl_or_offset_state = 0
        if obsid is None:
            obsid = self.load_obsid_and_init()
        if not self.Add2Levelmasl.text() == '':
            self.calibrate(obsid)
        self.update_plot()

    @fn_timer
    def calibrate(self, obsid=None):

        if obsid is None:
            obsid = self.load_obsid_and_init()

        if not obsid=='':
            fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
            to_d_t = self.ToDateTime.dateTime().toPyDateTime()

            if self.loggerpos_masl_or_offset_state == 1:
                self.update_level_masl_from_head(obsid, fr_d_t, to_d_t, self.LoggerPos.text())
            else:
                self.update_level_masl_from_level_masl(obsid, fr_d_t, to_d_t, self.Add2Levelmasl.text())

        else:

            text = ru(QCoreApplication.translate('Calibrlogger',
                                                 "Select the observation point with logger data to be adjusted."))
            self.statusbar.showMessage(text, 0)


    @fn_timer
    def update_level_masl_from_level_masl(self, obsid, fr_d_t, to_d_t, newzref):
        utils.start_waiting_cursor()
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
        sql += """ AND %s > %s"""%(date_time_as_epoch, str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds()))
        sql += """ AND %s < %s""" % (date_time_as_epoch, str((to_d_t - datetime.datetime(1970, 1, 1)).total_seconds()))
        dummy = db_utils.sql_alter_db(sql)
        utils.stop_waiting_cursor()

    @fn_timer
    def update_level_masl_from_head(self, obsid, fr_d_t, to_d_t, newzref):
        """ Updates the level masl using newzref
        :param obsid: (str) The obsid
        :param fr_d_t: (datetime) start of calibration
        :param to_d_t: (datetime) end of calibration
        :param newzref: (int/float/str [m]) The correction that should be made against the head [m]
        :return: None
        """
        utils.start_waiting_cursor()
        sql =r"""UPDATE w_levels_logger SET level_masl = """
        sql += str(newzref)
        sql += """ + head_cm / 100 WHERE obsid = '"""
        sql += obsid
        sql += """' AND head_cm IS NOT NULL"""
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first (but now we changed to > but kept .total_seconds())
        date_time_as_epoch = db_utils.cast_date_time_as_epoch()
        sql += """ AND %s > %s"""%(date_time_as_epoch, str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds()))
        sql += """ AND %s < %s""" % (date_time_as_epoch, str((to_d_t - datetime.datetime(1970, 1, 1)).total_seconds()))
        dummy = db_utils.sql_alter_db(sql)
        try:
            print(str(dummy))
        except:
            pass
        utils.stop_waiting_cursor()

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
        utils.start_waiting_cursor()
        if obsid == None:
            self.statusbar.clearMessage()
            return
        self.axes.clear()

        p=[None]*2 # List for plot objects

        # Load manual reading (full time series) for the obsid
        if self.meas_ts.size and self.contains_more_than_nan(self.meas_ts):
            self.plot_recarray(self.axes, self.meas_ts, obsid + ru(QCoreApplication.translate('Calibrlogger', ' measurements')), 'o-', picker=5, zorder=15, color='#1f77b4ff')

        # Load Loggerlevels (full time series) for the obsid
        if self.loggerLineNodes.isChecked():
            logger_line_style = '.-'
            original_head_style = '--'
        else:
            logger_line_style = '-'
            original_head_style = '--'

        logger_time_list = self.timestring_list_to_time_list(self.a_recarray_to_timestring_list(self.level_masl_ts))
        if self.level_masl_ts.size and self.contains_more_than_nan(self.level_masl_ts):
            self.plot_recarray(self.axes, self.level_masl_ts, obsid + ru(QCoreApplication.translate('Calibrlogger', ' logger water level')), logger_line_style, picker=5, time_list=logger_time_list, zorder=10, color='#ff7f0eff')

        #Plot the original head_cm
        if self.plot_logger_head.isChecked() and self.head_ts_for_plot.size and self.contains_more_than_nan(self.head_ts_for_plot):
            self.plot_recarray(self.axes, self.head_ts_for_plot, obsid + ru(QCoreApplication.translate('Calibrlogger', ' logger head')), original_head_style, picker=5, time_list=logger_time_list, zorder=5, color='#c1c1c1ff')

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

        utils.stop_waiting_cursor()

    @fn_timer
    def plot_recarray(self, axes, a_recarray, lable, line_style, picker=5, time_list=None, zorder=None, markersize=None, color=None):
        """ Plots a recarray to the supplied axes object """
        if time_list is None:
            time_list = self.timestring_list_to_time_list(self.a_recarray_to_timestring_list(a_recarray))
        self.plot_the_recarray(axes, time_list, a_recarray, lable, line_style, picker=picker, zorder=zorder, markersize=markersize, color=color)

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
    def plot_the_recarray(self, axes, time_list, a_recarray, lable, line_style, picker=5, zorder=None, markersize=None, color=None):
        kwargs = {'label': lable, 'picker':picker}
        if zorder is not None:
            kwargs['zorder'] = zorder
        if markersize is not None:
            kwargs['markersize'] = markersize
        if color is not None:
            kwargs['color'] = color

        axes.plot_date(time_list, a_recarray.values, line_style, **kwargs) #, xdate=True)

    @fn_timer
    def set_from_date_from_x(self):
        """ Used to set the self.FromDateTime by clicking on a line node in the plot self.canvas """
        self.set_date_from_x(self.FromDateTime, ru(QCoreApplication.translate('Calibrlogger', "Select a date to use as \"from\"")))

    @fn_timer
    def set_to_date_from_x(self):
        """ Used to set the self.ToDateTime by clicking on a line node in the plot self.canvas """
        self.set_date_from_x(self.ToDateTime, ru(QCoreApplication.translate('Calibrlogger', "Select a date to use as \"to\"")))

    @fn_timer
    def set_date_from_x_onclick(self, event, date_holder, from_node=False):
        """ Sets the date_holder to a date from a line node closest to the pick event

            date_holder: a QDateTimeEdit object.
        """
        if from_node:
            found_date = self.get_node_date_from_click(event)
        else:
            found_date = num2date(event.mouseevent.xdata)
        date_holder.setDateTime(found_date)
        self.reset_plot_selects_and_calib_help()

    @fn_timer
    def reset_plot_selects_and_calib_help(self):
        """ Reset self.cid and self.calib_help """
        self.reset_cid()
        self.log_pos = None
        self.y_pos = None
        self.statusbar.clearMessage()

    @fn_timer
    def reset_settings(self):

        self.ToDateTime.setDateTime(datestring_to_date('2099-12-31 23:59:59'))
        self.Add2Levelmasl.setText('')
        self.bestFitSearchRadius.setText('10 minutes')
        #self.mpltoolbar.home()

        last_calibration = self.getlastcalibration(self.obsid)
        try:
            if last_calibration[0][1] and last_calibration[0][0]:
                self.LoggerPos.setText('{:.5f}'.format(last_calibration[0][1]))
                self.FromDateTime.setDateTime(datestring_to_date(last_calibration[0][0]))
            else:
                self.LoggerPos.setText('')
                self.FromDateTime.setDateTime(datestring_to_date('2099-12-31 23:59:59'))
        except Exception as e:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Calibrlogger', 'Getting last calibration failed for obsid %s, msg: %s'))%(self.obsid, str(e)))
            self.LoggerPos.setText('')
            self.FromDateTime.setDateTime(datestring_to_date('2099-12-31 23:59:59'))

    @fn_timer
    def reset_cid(self):
        """ Resets self.cid to an empty list and disconnects unused events """
        for x in self.cid:
            self.canvas.mpl_disconnect(x)
        self.cid = []

    @fn_timer
    def catch_old_level(self):
        """Part of adjustment method 3. adjust level_masl by clicking in plot.
        this part selects a line node and a y-position on the plot"""
        #Run init to make sure self.meas_ts and self.head_ts is updated for the current obsid.
        self.load_obsid_and_init()
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()


        text = ru(QCoreApplication.translate('Calibrlogger', "Select a logger node."))
        self.statusbar.showMessage(text, 0)
        self.cid.append(self.canvas.mpl_connect('pick_event', self.set_log_pos_from_node_date_click))

    @fn_timer
    def catch_new_level(self):
        """ Part of adjustment method 3. adjust level_masl by clicking in plot.
        this part selects a y-position from the plot (normally user would select a manual measurement)."""
        if self.log_pos is not None:
            text = ru(QCoreApplication.translate('Calibrlogger', "Select a y position to move to."))
            self.statusbar.showMessage(text, 0)
            self.cid.append(self.canvas.mpl_connect('button_press_event', self.set_y_pos_from_y_click))
            self.statusbar.clearMessage()
        else:
            text = ru(QCoreApplication.translate('Calibrlogger', "Something wrong, click \"Current\" and try again."))
            self.statusbar.showMessage(text, 0)

    @fn_timer
    def calculate_offset(self):
        """ Part of adjustment method 3. adjust level_masl by clicking in plot.
        this method extracts the head from head_ts with the same date as the line node.
            4. Calculating y-position - head (or level_masl) and setting self.LoggerPos.
            5. Run calibration.
        """
        if self.log_pos is not None and self.y_pos is not None:
            utils.start_waiting_cursor()

            logger_ts = self.level_masl_ts

            y_pos = self.y_pos
            log_pos = self.log_pos
            self.y_pos = None
            self.log_pos = None
            log_pos_date = datestring_to_date(log_pos).replace(tzinfo=None)
            logger_value = None

            #Get the value for the selected node
            for raw_date, logger_value in logger_ts:
                date = datestring_to_date(raw_date).replace(tzinfo=None)
                if date == log_pos_date:
                    break

            if logger_value is None:
                utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "No connection between level_masl dates and logger date could be made!\nTry again or choose a new logger line node!")))
            else:
                self.Add2Levelmasl.setText('{:.5f}'.format(float(y_pos) - float(logger_value)))

                utils.stop_waiting_cursor()

        self.pushButtonMpos.setEnabled(False)

    @fn_timer
    def set_log_pos_from_node_date_click(self, event):
        """ Sets self.log_pos variable to the date (x-axis) from the node nearest the pick event """
        found_date = self.get_node_date_from_click(event)
        text = ru(QCoreApplication.translate('Calibrlogger',
                                             "Logger node %s selected, click \"new\" and select new level.")
                  )%str(found_date)
        self.statusbar.showMessage(text, 0)
        self.log_pos = found_date
        self.pushButtonMpos.setEnabled(True)

    @fn_timer
    def set_y_pos_from_y_click(self, event):
        """ Sets the self.y_pos variable to the y value of the click event """
        self.y_pos = event.ydata
        self.calculate_offset()
        text = ru(QCoreApplication.translate('Calibrlogger', "Offset is calculated, now click \"add\"."))
        self.statusbar.showMessage(text, 0)
        self.reset_cid()

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
        """ Calculates the self.LoggerPos from self.meas_ts and self.head_ts

            First matches measurements from self.meas_ts to logger values from
            self.head_ts. This is done by making a mean of all logger values inside
            self.meas_ts date - search_radius and self.meas_ts date + search_radius.
            (this could probably be change to get only the closest logger value
            inside the search_radius instead)
            (search_radius is gotten from self.get_search_radius())

            Then calculates the mean of all matches and set to self.LoggerPos.
        """
        obsid = self.load_obsid_and_init()
        utils.start_waiting_cursor()
        self.reset_plot_selects_and_calib_help()
        search_radius = self.get_search_radius()
        if self.loggerpos_masl_or_offset_state == 1:# UPDATE TO RELEVANT TEXT
            logger_ts = self.head_ts
            text_field = self.LoggerPos
            calib_func = self.set_logger_pos
        else:# UPDATE TO RELEVANT TEXT
            logger_ts = self.level_masl_ts
            text_field = self.Add2Levelmasl
            calib_func = self.add_to_level_masl

        coupled_vals = self.match_ts_values(self.meas_ts, logger_ts, search_radius)
        if not coupled_vals:
            utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "There was no match found between measurements and logger values inside the chosen period.\n Try to increase the search radius!")))
        else:
            calculated_diff = str(utils.calc_mean_diff(coupled_vals))
            if not calculated_diff or calculated_diff.lower() == 'nan':
                utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "There was no matched measurements or logger values inside the chosen period.\n Try to increase the search radius!")))
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Calibrlogger', "Calculated water level from logger: utils.calc_mean_diff(coupled_vals) didn't return a useable value.")))
            else:
                text_field.setText(calculated_diff)
                calib_func(obsid)

        utils.stop_waiting_cursor()

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

        #Get the search radius, default to 10 minutes
        search_radius = int(search_radius_tuple[0])
        search_radius_period = search_radius_tuple[1]

        logger_gen = utils.ts_gen(logger_ts)
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
        """ Get the period search radius, default to 10 minutes """
        if not self.bestFitSearchRadius.text():
            search_radius = '10 minutes'
            self.bestFitSearchRadius.setText(search_radius)
        else:
            search_radius = self.bestFitSearchRadius.text()

        search_radius_splitted = ru(search_radius).split()
        if len(search_radius_splitted) != 2:
            utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "Must write time resolution also, ex. %s"))%'10 minutes')
        return tuple(search_radius_splitted)

    @fn_timer
    def deactivate_pan_zoom(self):
        """ Deactivates the NavigationToolbar pan or zoom feature if they are currently active """
        if self.mpltoolbar._active == "PAN":
            self.mpltoolbar.pan()
        elif self.mpltoolbar._active == "ZOOM":
            self.mpltoolbar.zoom()

    @fn_timer
    def delete_selected_range(self, table_name):
        """ Deletes the current selected range from the database from w_levels_logger
        :return: De
        """
        current_loaded_obsid = self.obsid
        selected_obsid = self.load_obsid_and_init()
        if current_loaded_obsid != selected_obsid:
            utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "Error!\n The obsid selection has been changed but the plot has not been updated. No deletion done.\nUpdating plot.")))
            self.update_plot()
            return
        elif selected_obsid is None:
            utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger', "Error!\n No obsid was selected. No deletion done.\nUpdating plot.")))
            self.update_plot()
            return

        fr_d_t = str((self.FromDateTime.dateTime().toPyDateTime() - datetime.datetime(1970,1,1)).total_seconds())
        to_d_t = str((self.ToDateTime.dateTime().toPyDateTime() - datetime.datetime(1970,1,1)).total_seconds())

        sql_list = []
        sql_list.append(r"""DELETE FROM "%s" """%table_name)
        sql_list.append(r"""WHERE obsid = '%s' """%selected_obsid)
        # This %s is db formatting for seconds. It is not used as python formatting!
        sql_list.append(r"""AND CAST(strftime('%s', date_time) AS NUMERIC) """)
        sql_list.append(r""" > '%s' """%fr_d_t)
        # This %s is db formatting for seconds. It is not used as python formatting!
        sql_list.append(r"""AND CAST(strftime('%s', date_time) AS NUMERIC) """)
        sql_list.append(r""" < '%s' """%to_d_t)
        sql = ''.join(sql_list)

        really_delete = utils.Askuser("YesNo", ru(QCoreApplication.translate('Calibrlogger', "Do you want to delete the period %s to %s for obsid %s from table %s?"))%(str(self.FromDateTime.dateTime().toPyDateTime()), str(self.ToDateTime.dateTime().toPyDateTime()), selected_obsid, table_name)).result
        if really_delete:
            utils.start_waiting_cursor()
            db_utils.sql_alter_db(sql)
            utils.stop_waiting_cursor()
            self.update_plot()

    @fn_timer
    def get_node_date_from_click(self, event):
        found_date = utils.find_nearest_date_from_event(event)
        self.reset_cid()
        return found_date

    @fn_timer
    def set_date_from_x(self, datetimeedit, help_msg=None, from_node=False):
        """ Used to set the self.ToDateTime by clicking on a line node in the plot self.canvas """
        self.reset_plot_selects_and_calib_help()
        self.deactivate_pan_zoom()
        if help_msg:
            self.statusbar.showMessage(help_msg, 0)
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        self.cid.append(self.canvas.mpl_connect('pick_event', lambda event: self.set_date_from_x_onclick(event, datetimeedit, from_node)))

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
                                                              AND date_time > '{adjust_start_date}'
                                                              AND date_time < '{adjust_end_date}'""".format(**{
            'obsid': data['obsid'], 'adjust_start_date': data['adjust_start_date'],
                                                         'adjust_end_date': data['adjust_end_date']})
        res = db_utils.sql_load_fr_db(sql)[1]
        if not res:
            utils.pop_up_info(ru(QCoreApplication.translate('Calibrlogger',
                                                            """Warning!\n No data found within the chosen period. No trend adjustment done!\nTry changing "from" and "to".""")))
            return

        sql = """
                UPDATE w_levels_logger SET level_masl = level_masl -
                (
                 ((({L1_level} - {L2_level}) / ({L1_date} - {L2_date}))
                 - (({M1_level} - {M2_level}) / ({M1_date} - {M2_date})))
                  * ({date_as_numeric} - {L1_date})
                )
                WHERE obsid = '{obsid}' AND date_time > '{adjust_start_date}' AND date_time < '{adjust_end_date}'
            """.format(**data)
        utils.start_waiting_cursor()
        db_utils.sql_alter_db(sql)
        utils.stop_waiting_cursor()
        self.update_plot()