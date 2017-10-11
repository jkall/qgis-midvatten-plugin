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
import PyQt4.QtCore
import PyQt4.QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

import os
import numpy as np
import math
import matplotlib.pyplot as plt   
import matplotlib.ticker as tick
from matplotlib.dates import datestr2num, num2date
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import datetime
from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import midvatten_utils as utils
from midvatten_utils import fn_timer
from date_utils import dateshift, datestring_to_date, long_dateformat

#from ui.calibr_logger_dialog import Ui_Dialog as Calibr_Ui_Dialog
#from ui.calc_lvl_dialog import Ui_Dialog as Calc_Ui_Dialog

Calibr_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calibr_logger_dialog_integrated.ui'))[0]
Calc_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calc_lvl_dialog.ui'))[0]


class calclvl(PyQt4.QtGui.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    @fn_timer
    def __init__(self, parent,layerin):
        PyQt4.QtGui.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = utils.getselectedobjectnames()
        self.setWindowTitle("Calculate levels") # Set the title for the dialog
        self.connect(self.pushButton_All, PyQt4.QtCore.SIGNAL("clicked()"), self.calcall)
        self.connect(self.pushButton_Selected, PyQt4.QtCore.SIGNAL("clicked()"), self.calcselected)
        self.connect(self.pushButton_Cancel, PyQt4.QtCore.SIGNAL("clicked()"), self.close)
        self.layer = layerin

    @fn_timer
    def calcall(self):
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
        to_d_t = self.ToDateTime.dateTime().toPyDateTime()
        
#        sanity1 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.h_toc""")[1]
        sanity1 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid""")[1]
        sanity2 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.h_toc NOT NULL""")[1]
        
        if len(sanity1) == len(sanity2): #only if h_toc exists for all objects!!
            sql1 = """UPDATE OR IGNORE w_levels SET h_toc = (SELECT obs_points.h_toc FROM obs_points WHERE w_levels.obsid = obs_points.obsid) WHERE """
            sql1 += """date_time >= '"""
            sql1 += str(fr_d_t)
            sql1 += """' AND date_time <= '"""
            sql1 += str(to_d_t)
            sql1 += """' """
            utils.sql_alter_db(sql1)
            sql2 = """UPDATE OR IGNORE w_levels SET level_masl = h_toc - meas WHERE """
            sql2 += """date_time >= '"""
            sql2 += str(fr_d_t)
            sql2 += """' AND date_time <= '"""
            sql2 += str(to_d_t)
            sql2 += """' """        
            utils.sql_alter_db(sql2)
            self.close()
        else:
            utils.pop_up_info('Adjustment aborted! There seems to be NULL values in your table obs_points, column h_toc.','Error')
            self.close()
            
    def calcselected(self):
        obsar = utils.getselectedobjectnames(self.layer)
        observations = obsar
        i=0
        for obs in obsar:
                observations[i] = obs.encode('utf-8') #turn into a list of python byte strings
                i += 1        
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
        to_d_t = self.ToDateTime.dateTime().toPyDateTime()

        sanity1 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.obsid IN """ + (str(observations)).encode('utf-8').replace('[','(').replace(']',')'))[1]
        sanity2 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.h_toc NOT NULL  AND obs_points.obsid IN """ + (str(observations)).encode('utf-8').replace('[','(').replace(']',')'))[1]

        if len(sanity1) == len(sanity2): #only if h_toc exists for all objects
            sql1 = """UPDATE OR IGNORE w_levels SET h_toc = (SELECT obs_points.h_toc FROM obs_points WHERE w_levels.obsid = obs_points.obsid) WHERE obsid IN """
            sql1 += str(observations)
            sql1 += """ AND date_time >= '"""
            sql1 += str(fr_d_t)
            sql1 += """' AND date_time <= '"""
            sql1 += str(to_d_t)
            sql1 += """' """   
            utils.sql_alter_db(sql1.replace("[","(").replace("]",")"))
            sql2 = """UPDATE OR IGNORE w_levels SET level_masl = h_toc - meas WHERE obsid IN """
            sql2 += str(observations)
            sql2 += """ AND date_time >= '"""
            sql2 += str(fr_d_t)
            sql2 += """' AND date_time <= '"""
            sql2 += str(to_d_t)
            sql2 += """' and meas is not null and h_toc is not null """
            utils.sql_alter_db(sql2.replace("[","(").replace("]",")"))
            self.close()        
        else:
            utils.pop_up_info('Calculation aborted! There seems to be NULL values in your table obs_points, column h_toc.','Error')
            self.close()


class calibrlogger(PyQt4.QtGui.QMainWindow, Calibr_Ui_Dialog): # An instance of the class Calibr_Ui_Dialog is created same time as instance of calibrlogger is created

    @fn_timer
    def __init__(self, parent, settingsdict1={}, obsid=''):
        PyQt4.QtGui.QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))#show the user this may take a long time...
        self.obsid = obsid
        self.log_pos = None
        self.y_pos = None
        self.meas_ts = None
        self.head_ts = None
        self.head_ts_for_plot = None
        self.level_masl_ts = None
        self.loggerpos_masl_or_offset_state = 1

        self.settingsdict = settingsdict1
        PyQt4.QtGui.QDialog.__init__(self, parent)        
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle("Calculate water level from logger") # Set the title for the dialog
        self.INFO.setText("Select the observation point with logger data to be adjusted.")
        self.log_calc_manual.setText("<a href=\"https://github.com/jkall/qgis-midvatten-plugin/wiki/4.-Edit-data\">Midvatten manual</a>")
      
        # Create a plot window with one single subplot
        self.calibrplotfigure = plt.figure() 
        self.axes = self.calibrplotfigure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.calibrplotfigure )
        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot )
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )
        self.calibrplotfigure.tight_layout()
        self.show()

        self.cid =[]
                
        self.connect(self.pushButtonSet, PyQt4.QtCore.SIGNAL("clicked()"), self.set_logger_pos)
        self.connect(self.pushButtonAdd, PyQt4.QtCore.SIGNAL("clicked()"), self.add_to_level_masl)
        self.connect(self.pushButtonFrom, PyQt4.QtCore.SIGNAL("clicked()"), self.set_from_date_from_x)
        self.connect(self.pushButtonTo, PyQt4.QtCore.SIGNAL("clicked()"), self.set_to_date_from_x)
        self.connect(self.pushButton_from_extent, PyQt4.QtCore.SIGNAL("clicked()"), lambda: self.FromDateTime.setDateTime(num2date(self.axes.get_xbound()[0])))
        self.connect(self.pushButton_to_extent, PyQt4.QtCore.SIGNAL("clicked()"), lambda: self.ToDateTime.setDateTime(num2date(self.axes.get_xbound()[1])))
        self.connect(self.pushButtonupdateplot, PyQt4.QtCore.SIGNAL("clicked()"), self.update_plot)
        #self.connect(self.loggerpos_masl_or_offset, PyQt4.QtCore.SIGNAL("clicked()"), self.loggerpos_masl_or_offset_change)
        #self.connect(self.pushButtonLpos, PyQt4.QtCore.SIGNAL("clicked()"), self.calibrate_from_plot_selection)
        self.connect(self.pushButtonLpos, PyQt4.QtCore.SIGNAL("clicked()"), self.catch_old_level)
        self.connect(self.pushButtonMpos, PyQt4.QtCore.SIGNAL("clicked()"), self.catch_new_level)
        self.pushButtonMpos.setEnabled(False)
        self.connect(self.pushButtonCalcBestFit, PyQt4.QtCore.SIGNAL("clicked()"), self.logger_pos_best_fit)
        self.pushButtonCalcBestFit.setToolTip(u'This will calibrate all values inside the chosen period\nusing the mean difference between head_cm and w_levels measurements.\n\nThe search radius is the maximum time distance allowed\n between a logger measurement and a w_level measurement.')
        self.connect(self.pushButtonCalcBestFit2, PyQt4.QtCore.SIGNAL("clicked()"), self.level_masl_best_fit)
        self.pushButtonCalcBestFit2.setToolTip(u'This will calibrate all values inside the chosen period\nusing the mean difference between level_masl and w_levels measurements.\n\nThe search radius is the maximum time distance allowed\n between a logger measurement and a w_level measurement.')
        self.connect(self.pushButton_delete_logger, PyQt4.QtCore.SIGNAL("clicked()"), lambda: self.delete_selected_range(u'w_levels_logger'))

        self.get_search_radius()

        # Populate combobox with obsid from table w_levels_logger
        self.load_obsid_from_db()

        PyQt4.QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    @property
    def selected_obsid(self):
        uncalibrated_str = u' (uncalibrated)'
        return unicode(self.combobox_obsid.currentText().replace(uncalibrated_str, u''))

    @fn_timer
    def load_obsid_from_db(self):
        self.combobox_obsid.clear()
        res = utils.sql_load_fr_db("""SELECT DISTINCT obsid, CASE WHEN level_masl IS NULL THEN 'uncalibrated' ELSE 'calibrated' END AS 'status' FROM w_levels_logger ORDER BY obsid""")[1]
        all_obsids = {}
        for row in res:
            all_obsids.setdefault(row[0], []).append(row[1])

        self.combobox_obsid.addItems(sorted(all_obsids))
        obsids_with_uncalibrated_data = [_obsid for _obsid, status in all_obsids.iteritems() if 'uncalibrated' in status]
        self.update_combobox_with_calibration_info(_obsids_with_uncalibrated_data=obsids_with_uncalibrated_data)

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
        uncalibrated_str = u' (uncalibrated)'

        num_entries = self.combobox_obsid.count()

        if obsid is None and _obsids_with_uncalibrated_data is None:
            obsids_with_uncalibrated_data = [row[0] for row in utils.sql_load_fr_db("""SELECT DISTINCT obsid FROM w_levels_logger WHERE level_masl IS NULL""")[1]]
        elif _obsids_with_uncalibrated_data is not None:
            obsids_with_uncalibrated_data = _obsids_with_uncalibrated_data

        for idx in xrange(num_entries):
            current_obsid = self.combobox_obsid.itemText(idx).replace(uncalibrated_str, u'')

            if obsid is not None:
                #If obsid was given, only continue loop for that one:
                if current_obsid != obsid:
                    continue
                if obsids_with_uncalibrated_data is None:
                    obsids_with_uncalibrated_data = [row[0] for row in utils.sql_load_fr_db("""SELECT DISTINCT obsid FROM w_levels_logger WHERE obsid = '%s' AND level_masl IS NULL"""%current_obsid)[1]]

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
        obsid = self.selected_obsid
        if not obsid:
            utils.pop_up_info("ERROR: no obsid is chosen")
            return None

        meas_sql = r"""SELECT date_time as 'date [datetime]', level_masl FROM w_levels WHERE obsid = '%s' ORDER BY date_time"""%obsid
        self.meas_ts = self.sql_into_recarray(meas_sql)

        head_level_masl_sql = r"""SELECT date_time as 'date [datetime]', head_cm / 100, level_masl FROM w_levels_logger WHERE obsid = '%s' ORDER BY date_time"""%obsid
        head_level_masl_list = utils.sql_load_fr_db(head_level_masl_sql)[1]
        head_list = [(row[0], row[1]) for row in head_level_masl_list]
        level_masl_list = [(row[0], row[2]) for row in head_level_masl_list]

        self.head_ts = self.list_of_list_to_recarray(head_list)

        if self.plot_logger_head.isChecked():
            if self.normalize_head.isChecked():
                head_vals = [row[1] for row in head_list if row[1] is not None]
                head_mean = sum(head_vals) / float(len(head_vals))

                level_masl_vals = [row[1] for row in level_masl_list if row[1] is not None]
                num_level_masl_vals = len(level_masl_vals)
                if num_level_masl_vals > 0:
                    level_masl_mean = sum(level_masl_vals) / float(num_level_masl_vals)

                    normalized_head = [(row[0], row[1] + (level_masl_mean - head_mean) if row[1] is not None else None) for row in head_list]

                    self.head_ts_for_plot = self.list_of_list_to_recarray(normalized_head)
                else:
                    utils.MessagebarAndLog.warning(bar_msg=u'No calibrated level_masl values to normalize against.')
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

        return obsid

    @fn_timer
    def setlastcalibration(self, obsid):
        if not obsid=='':
            self.lastcalibr = self.getlastcalibration(obsid)
            if self.lastcalibr[0][1] and self.lastcalibr[0][0]:
                text = """Last pos. for logger in """
                text += obsid
                text += """ was """ + str(self.lastcalibr[0][1]) + """ masl at """ +  str(self.lastcalibr[0][0])
            else:
                text = """There is no earlier known position for the logger in """ + self.selected_obsid #self.obsid[0]
            self.INFO.setText(text)

    @fn_timer
    def getlastcalibration(self, obsid):
        sql = """SELECT MAX(date_time), loggerpos FROM (SELECT date_time, (level_masl - (head_cm/100)) as loggerpos FROM w_levels_logger WHERE level_masl is not Null and level_masl > -990 AND obsid = '%s')"""%obsid
        lastcalibr = utils.sql_load_fr_db(sql)[1]
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
        self.calib_help.setText("Calibrating")

        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
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
            self.INFO.setText("Select the observation point with logger data to be calibrated.")
        self.calib_help.setText("")
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    @fn_timer
    def update_level_masl_from_level_masl(self, obsid, fr_d_t, to_d_t, newzref):
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
        sql += """' AND level_masl IS NOT NULL AND level_masl !='' """
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first.
        sql += """ AND CAST(strftime('%s', date_time) AS NUMERIC) > """
        sql += str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ AND CAST(strftime('%s', date_time) AS NUMERIC) < """
        sql += str((to_d_t - datetime.datetime(1970,1,1)).total_seconds())
        dummy = utils.sql_alter_db(sql)

    @fn_timer
    def update_level_masl_from_head(self, obsid, fr_d_t, to_d_t, newzref):
        """ Updates the level masl using newzref
        :param obsid: (str) The obsid
        :param fr_d_t: (datetime) start of calibration
        :param to_d_t: (datetime) end of calibration
        :param newzref: (int/float/str [m]) The correction that should be made against the head [m]
        :return: None
        """
        sql =r"""UPDATE w_levels_logger SET level_masl = """
        sql += str(newzref)
        sql += """ + head_cm / 100 WHERE obsid = '"""
        sql += obsid
        sql += """' AND head_cm IS NOT NULL AND head_cm !='' """
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first (but now we changed to > but kept .total_seconds())
        sql += """ AND CAST(strftime('%s', date_time) AS NUMERIC) > """
        sql += str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ AND CAST(strftime('%s', date_time) AS NUMERIC) < """
        sql += str((to_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ """
        dummy = utils.sql_alter_db(sql)

    @fn_timer
    def sql_into_recarray(self, sql):
        """ Converts and runs an sql-string and turns the answer into an np.recarray and returns it""" 
        list_of_lists = utils.sql_load_fr_db(sql)[1]
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
        self.calib_help.setText("Updating plot")
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        last_used_obsid = self.obsid
        obsid = self.load_obsid_and_init()
        if obsid == None:
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.calib_help.setText("")
            return
        self.axes.clear()
        
        p=[None]*2 # List for plot objects
    
        # Load manual reading (full time series) for the obsid
        if self.meas_ts.size:
            self.plot_recarray(self.axes, self.meas_ts, obsid, 'o-', 5)
        
        # Load Loggerlevels (full time series) for the obsid
        if self.loggerLineNodes.isChecked():
            logger_line_style = '.-'
        else:
            logger_line_style = '-'                

        logger_time_list = self.timestring_list_to_time_list(self.a_recarray_to_timestring_list(self.level_masl_ts))
        self.plot_recarray(self.axes, self.level_masl_ts, obsid + unicode(' logger', 'utf-8'), logger_line_style, picker=5, time_list=logger_time_list)

        #Plot the original head_cm
        if self.plot_logger_head.isChecked():
            self.plot_recarray(self.axes, self.head_ts_for_plot, obsid + unicode(' original logger head', 'utf-8'), logger_line_style, picker=5, time_list=logger_time_list)

        """ Finish plot """
        self.axes.grid(True)
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.calibrplotfigure.autofmt_xdate()
        self.axes.set_ylabel(unicode('Level (masl)', 'utf-8'))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        self.axes.set_title(unicode('Plot for ', 'utf-8') + str(obsid))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        for label in self.axes.xaxis.get_ticklabels():
            label.set_fontsize(10)
        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(10)
        #plt.show()
        self.calibrplotfigure.tight_layout()
        self.canvas.draw()
        plt.close(self.calibrplotfigure)#this closes reference to self.calibrplotfigure
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.calib_help.setText("")

        if last_used_obsid == self.obsid:
            self.mpltoolbar.forward()
        else:
            #Clear choices
            self.reset_settings()

    @fn_timer
    def plot_recarray(self, axes, a_recarray, lable, line_style, picker=5, time_list=None):
        """ Plots a recarray to the supplied axes object """
        if time_list is None:
            time_list = self.timestring_list_to_time_list(self.a_recarray_to_timestring_list(a_recarray))
        self.plot_the_recarray(axes, time_list, a_recarray, lable, line_style, picker=5)
        
    @fn_timer
    def a_recarray_to_timestring_list(self, a_recarray):
        return [a_recarray.date_time[idx] for idx in xrange(len(a_recarray))]
        
    @fn_timer
    def timestring_list_to_time_list(self, timestring_list):
        """Get help from function datestr2num to get date and time into float"""
        return datestr2num(timestring_list)
        
    @fn_timer
    def plot_the_recarray(self, axes, time_list, a_recarray, lable, line_style, picker=5):
        axes.plot_date(time_list, a_recarray.values, line_style, label=lable, picker=picker)

    @fn_timer
    def set_from_date_from_x(self):
        """ Used to set the self.FromDateTime by clicking on a line node in the plot self.canvas """
        self.reset_plot_selects_and_calib_help()
        self.calib_help.setText("Select a date to use as \"from\"")
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()   
        self.cid.append(self.canvas.mpl_connect('pick_event', lambda event: self.set_date_from_x_onclick(event, self.FromDateTime)))

    @fn_timer
    def set_to_date_from_x(self):
        """ Used to set the self.ToDateTime by clicking on a line node in the plot self.canvas """    
        self.reset_plot_selects_and_calib_help()
        self.calib_help.setText("Select a date to use as \"to\"")
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()   
        self.cid.append(self.canvas.mpl_connect('pick_event', lambda event: self.set_date_from_x_onclick(event, self.ToDateTime)))

    @fn_timer
    def set_date_from_x_onclick(self, event, date_holder):
        """ Sets the date_holder to a date from a line node closest to the pick event

            date_holder: a QDateTimeEdit object.
        """
        found_date = num2date(event.mouseevent.xdata)
        date_holder.setDateTime(found_date)           
        self.reset_plot_selects_and_calib_help()
    
    @fn_timer
    def reset_plot_selects_and_calib_help(self):
        """ Reset self.cid and self.calib_help """
        self.reset_cid()
        self.log_pos = None
        self.y_pos = None
        self.calib_help.setText("")

    @fn_timer
    def reset_settings(self):

        self.ToDateTime.setDateTime(datestring_to_date(u'2099-12-31 23:59:59'))
        self.Add2Levelmasl.setText('')
        self.bestFitSearchRadius.setText('10 minutes')
        self.mpltoolbar._views.clear()

        last_calibration = self.getlastcalibration(self.obsid)
        try:
            if last_calibration[0][1] and last_calibration[0][0]:
                self.LoggerPos.setText(str(last_calibration[0][1]))
                self.FromDateTime.setDateTime(datestring_to_date(last_calibration[0][0]))
            else:
                self.LoggerPos.setText('')
                self.FromDateTime.setDateTime(datestring_to_date(u'2099-12-31 23:59:59'))
        except Exception as e:
            utils.MessagebarAndLog.info(log_msg=u'Getting last calibration failed for obsid %s, msg: %s'%(self.obsid, str(e)))
            self.LoggerPos.setText('')
            self.FromDateTime.setDateTime(datestring_to_date(u'2099-12-31 23:59:59'))

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

        self.calib_help.setText("Select a logger node.")
        self.cid.append(self.canvas.mpl_connect('pick_event', self.set_log_pos_from_node_date_click))
            
    @fn_timer
    def catch_new_level(self):
        """ Part of adjustment method 3. adjust level_masl by clicking in plot.
        this part selects a y-position from the plot (normally user would select a manual measurement)."""
        if self.log_pos is not None:
            self.calib_help.setText("Select a y position to move to.")
            self.cid.append(self.canvas.mpl_connect('button_press_event', self.set_y_pos_from_y_click))
            self.calib_help.setText("")
        else:
            self.calib_help.setText("Something wrong, click \"Current\" and try again.")

    @fn_timer
    def calculate_offset(self):
        """ Part of adjustment method 3. adjust level_masl by clicking in plot.
        this method extracts the head from head_ts with the same date as the line node.
            4. Calculating y-position - head (or level_masl) and setting self.LoggerPos.
            5. Run calibration.
        """            
        if self.log_pos is not None and self.y_pos is not None:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)

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
                utils.pop_up_info("No connection between level_masl dates and logger date could be made!\nTry again or choose a new logger line node!")
            else:
                self.Add2Levelmasl.setText(str(float(y_pos) - float(logger_value)))

                PyQt4.QtGui.QApplication.restoreOverrideCursor()

        self.pushButtonMpos.setEnabled(False)
        
    @fn_timer
    def set_log_pos_from_node_date_click(self, event):
        """ Sets self.log_pos variable to the date (x-axis) from the node nearest the pick event """
        found_date = utils.find_nearest_date_from_event(event)
        #self.calib_help.setText("Logger node " + str(found_date) + " selected, click button \"Calibrate by selection in plot\" again.")
        self.calib_help.setText("Logger node " + str(found_date) + " selected, click \"new\" and select new level.")
        self.log_pos = found_date
        self.reset_cid()
        self.pushButtonMpos.setEnabled(True)
 
    @fn_timer
    def set_y_pos_from_y_click(self, event):
        """ Sets the self.y_pos variable to the y value of the click event """
        self.y_pos = event.ydata
        #self.calib_help.setText("Y position set, click button \"Calibrate by selection in plot\" again for calibration.")
        self.calculate_offset()
        self.calib_help.setText("Offset is calculated, now click \"add\".")
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

        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)

        coupled_vals = self.match_ts_values(self.meas_ts, logger_ts, search_radius)
        if not coupled_vals:
            utils.pop_up_info("There was no match found between measurements and logger values inside the chosen period.\n Try to increase the search radius!")
        else:
            calculated_diff = str(utils.calc_mean_diff(coupled_vals))
            if not calculated_diff or calculated_diff.lower() == 'nan':
                utils.pop_up_info("There was no matched measurements or logger values inside the chosen period.\n Try to increase the search radius!")
                utils.MessagebarAndLog.info(log_msg="Calculated water level from logger: utils.calc_mean_diff(coupled_vals) didn't return a useable value.")
            else:
                text_field.setText(calculated_diff)
                calib_func(obsid)

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
     
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

        search_radius_splitted = search_radius.split()
        if len(search_radius_splitted) != 2:
            utils.pop_up_info("Must write time resolution also, ex. 10 minutes")
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
            utils.pop_up_info("Error!\n The obsid selection has been changed but the plot has not been updated. No deletion done.\nUpdating plot.")
            self.update_plot()
            return
        elif selected_obsid is None:
            utils.pop_up_info("Error!\n No obsid was selected. No deletion done.\nUpdating plot.")
            self.update_plot()
            return

        fr_d_t = str((self.FromDateTime.dateTime().toPyDateTime() - datetime.datetime(1970,1,1)).total_seconds())
        to_d_t = str((self.ToDateTime.dateTime().toPyDateTime() - datetime.datetime(1970,1,1)).total_seconds())

        sql_list = []
        sql_list.append(r"""delete from "%s" """%table_name)
        sql_list.append(r"""where obsid = '%s' """%selected_obsid)
        sql_list.append(r"""AND CAST(strftime('%s', date_time) AS NUMERIC) """)
        sql_list.append(r""" > '%s' """%fr_d_t)
        sql_list.append(r"""AND CAST(strftime('%s', date_time) AS NUMERIC) """)
        sql_list.append(r""" < '%s' """%to_d_t)
        sql = ''.join(sql_list)

        really_delete = utils.askuser("YesNo", "Do you want to delete the period " +
                                      str(self.FromDateTime.dateTime().toPyDateTime()) + " to " +
                                      str(self.ToDateTime.dateTime().toPyDateTime()) +
                                      " for obsid " + selected_obsid + " from table " + table_name + "?").result
        if really_delete:
            utils.sql_alter_db(sql)
            self.update_plot()


