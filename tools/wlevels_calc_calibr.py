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
#TODO: cleanup pyqt imports
import PyQt4.QtCore
import PyQt4.QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import qgis

import locale
import os
import time
import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt   
import matplotlib.ticker as tick
from matplotlib.dates import datestr2num, num2date
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import datetime
from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import midvatten_utils as utils
from date_utils import dateshift, datestring_to_date

#from ui.calibr_logger_dialog import Ui_Dialog as Calibr_Ui_Dialog
#from ui.calc_lvl_dialog import Ui_Dialog as Calc_Ui_Dialog

Calibr_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calibr_logger_dialog_integrated.ui'))[0]
Calc_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calc_lvl_dialog.ui'))[0]


class calclvl(PyQt4.QtGui.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    def __init__(self, parent,layerin):
        PyQt4.QtGui.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = utils.getselectedobjectnames()
        self.setWindowTitle("Calculate levels") # Set the title for the dialog
        self.connect(self.pushButton_All, PyQt4.QtCore.SIGNAL("clicked()"), self.calcall)
        self.connect(self.pushButton_Selected, PyQt4.QtCore.SIGNAL("clicked()"), self.calcselected)
        self.connect(self.pushButton_Cancel, PyQt4.QtCore.SIGNAL("clicked()"), self.close)
        self.layer = layerin

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
            utils.pop_up_info('Calculation aborted! There seems to be NULL values in your table obs_points, column h_toc.','Error')
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
            sql2 += """' """        
            utils.sql_alter_db(sql2.replace("[","(").replace("]",")"))
            self.close()        
        else:
            utils.pop_up_info('Calculation aborted! There seems to be NULL values in your table obs_points, column h_toc.','Error')
            self.close()
        
class calibrlogger(PyQt4.QtGui.QMainWindow, Calibr_Ui_Dialog): # An instance of the class Calibr_Ui_Dialog is created same time as instance of calibrlogger is created

    def __init__(self, parent, settingsdict1={}, obsid=''):
        self.obsid = obsid
        self.log_pos = None
        self.y_pos = None
        self.meas_ts = None
        self.head_ts = None
        self.level_masl_ts = None
        self.loggerpos_masl_or_offset_state = 1

        self.settingsdict = settingsdict1
        PyQt4.QtGui.QDialog.__init__(self, parent)        
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle("Calibrate logger") # Set the title for the dialog
        self.connect(self.pushButton, PyQt4.QtCore.SIGNAL("clicked()"), self.calibrateandplot)
        self.INFO.setText("Select the observation point with logger data to be calibrated.")
        self.log_calc_manual.setText("<a href=\"https://sites.google.com/site/midvattenpluginforqgis/usage/3-edit-data?pli=1#TOC-Calibrate-water-level-measurements-from-data-logger-\">Midvatten manual</a>")
      
        # Create a plot window with one single subplot
        self.calibrplotfigure = plt.figure() 
        self.axes = self.calibrplotfigure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.calibrplotfigure )
        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot )
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )
        self.show()

        self.cid =[]
                
        self.connect(self.pushButtonFrom, PyQt4.QtCore.SIGNAL("clicked()"), self.set_from_date_from_x)
        self.connect(self.pushButtonTo, PyQt4.QtCore.SIGNAL("clicked()"), self.set_to_date_from_x)
        self.connect(self.pushButtonupdateplot, PyQt4.QtCore.SIGNAL("clicked()"), self.update_plot)
        self.connect(self.loggerpos_masl_or_offset, PyQt4.QtCore.SIGNAL("clicked()"), self.loggerpos_masl_or_offset_change)
        self.connect(self.pushButtonLpos, PyQt4.QtCore.SIGNAL("clicked()"), self.calibrate_from_plot_selection)
        self.connect(self.pushButtonCalcBestFit, PyQt4.QtCore.SIGNAL("clicked()"), self.calc_best_fit)

        self.get_tolerance()

        # Populate combobox with obsid from table w_levels_logger
        self.load_obsid_from_db()

    def load_obsid_from_db(self):
        self.combobox_obsid.clear()
        myconnection = utils.dbconnection()
        if myconnection.connect2db() == True:
            # skapa en cursor
            curs = myconnection.conn.cursor()
            rs=curs.execute("""select distinct obsid from w_levels_logger order by obsid""")
            self.combobox_obsid.addItem('')
            for row in curs:
                self.combobox_obsid.addItem(row[0])
            rs.close()
            myconnection.closedb()

    def load_obsid_and_init(self, update_level_masl=True):
        obsid = unicode(self.combobox_obsid.currentText())
        if not obsid:
            utils.pop_up_info("ERROR: no obsid is chosen")
        if self.obsid != obsid:
            meas_sql = r"""SELECT date_time, level_masl FROM w_levels WHERE obsid = '""" + obsid + """' ORDER BY date_time"""
            self.meas_ts = self.sql_into_recarray(meas_sql)
            head_sql = r"""SELECT date_time as 'date [datetime]', head_cm / 100 FROM w_levels_logger WHERE obsid = '""" + obsid + """' ORDER BY date_time"""
            self.head_ts = self.sql_into_recarray(head_sql)
            self.obsid = obsid
        if update_level_masl:
            level_masl_ts_sql = r"""SELECT date_time as 'date [datetime]', level_masl FROM w_levels_logger WHERE obsid = '""" + self.obsid + """' ORDER BY date_time"""
            self.level_masl_ts = self.sql_into_recarray(level_masl_ts_sql)
        return obsid

    def getlastcalibration(self):
        obsid = self.load_obsid_and_init()
        if not obsid=='':
            sql = """SELECT MAX(date_time), loggerpos FROM (SELECT date_time, (level_masl - (head_cm/100)) as loggerpos FROM w_levels_logger WHERE level_masl > -990 AND obsid = '"""
            sql += obsid
            sql += """')"""
            self.lastcalibr = utils.sql_load_fr_db(sql)[1]
            if self.lastcalibr[0][1] and self.lastcalibr[0][0]:
                text = """Last pos. for logger in """
                text += obsid
                text += """\nwas """ + str(self.lastcalibr[0][1]) + """ masl\nat """ +  str(self.lastcalibr[0][0])
            else:
                text = """There is no earlier known\nposition for the logger\nin """ + unicode(self.combobox_obsid.currentText())#self.obsid[0]
            self.INFO.setText(text)

    def calibrateandplot(self):
        obsid = self.load_obsid_and_init()
        if not self.LoggerPos.text() == '':
            self.calibrate()
        self.update_plot()
        
#    def calibrate(self, fr_d_t=self.FromDateTime.dateTime().toPyDateTime(), to_d_t=self.ToDateTime.dateTime().toPyDateTime()):
    def calibrate(self):
        self.calib_help.setText("Calibrating")
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        obsid = self.load_obsid_and_init(False)
        if not obsid=='':        
            sanity1sql = """select count(obsid) from w_levels_logger where obsid = '""" +  obsid[0] + """'"""
            sanity2sql = """select count(obsid) from w_levels_logger where head_cm not null and head_cm !='' and obsid = '""" +  obsid[0] + """'"""
            if utils.sql_load_fr_db(sanity1sql)[1] == utils.sql_load_fr_db(sanity2sql)[1]: # This must only be done if head_cm exists for all data
                fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
                to_d_t = self.ToDateTime.dateTime().toPyDateTime()

                if self.loggerpos_masl_or_offset_state == 1:
                    self.update_level_masl_from_head(obsid, fr_d_t, to_d_t, self.LoggerPos.text())
                else:
                    self.update_level_masl_from_level_masl(obsid, fr_d_t, to_d_t, self.LoggerPos.text())

                self.getlastcalibration()
            else:
                utils.pop_up_info("Calibration aborted!!\nThere must not be empty cells or\nnull values in the 'head_cm' column!")
        else:
            self.INFO.setText("Select the observation point with logger data to be calibrated.")
        self.calib_help.setText("")
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

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
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first.
        sql += """' AND CAST(strftime('%s', date_time) AS NUMERIC) >= """
        sql += str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ AND CAST(strftime('%s', date_time) AS NUMERIC) <= """
        sql += str((to_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ """
        dummy = utils.sql_alter_db(sql)

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
        # Sqlite seems to have problems with date comparison date_time >= a_date, so they have to be converted into total seconds first.
        sql += """' AND CAST(strftime('%s', date_time) AS NUMERIC) >= """
        sql += str((fr_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ AND CAST(strftime('%s', date_time) AS NUMERIC) <= """
        sql += str((to_d_t - datetime.datetime(1970,1,1)).total_seconds())
        sql += """ """
        dummy = utils.sql_alter_db(sql)

    def sql_into_recarray(self, sql):
        """ Converts and runs an sql-string and turns the answer into an np.recarray and returns it""" 
        my_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array     
        recs = utils.sql_load_fr_db(sql)[1]
        table = np.array(recs, dtype=my_format)  #NDARRAY
        table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values 
        return table2        

    def update_plot(self):
        """ Plots self.level_masl_ts, self.meas_ts and maybe self.head_ts """
        self.reset_plot_selects_and_calib_help()
        self.calib_help.setText("Updating plot")
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        obsid = self.load_obsid_and_init()
        self.axes.clear()
        
        p=[None]*2 # List for plot objects
    
        # Load manual reading (full time series) for the obsid
        self.plot_recarray(self.axes, self.meas_ts, obsid, 'o-', 0)
        
        # Load Loggerlevels (full time series) for the obsid
        if self.loggerLineNodes.isChecked():
            logger_line_style = '.-'
        else:
            logger_line_style = '-'                
        self.plot_recarray(self.axes, self.level_masl_ts, obsid + unicode(' logger', 'utf-8'), logger_line_style, 10)

        #Plot the original head_cm
        if self.plot_logger_head.isChecked():
            self.plot_recarray(self.axes, self.head_ts, obsid + unicode(' original logger head', 'utf-8'), '-', 0)

        """ Finish plot """
        self.axes.grid(True)
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.calibrplotfigure.autofmt_xdate()
        self.axes.set_ylabel(unicode('Level (masl)', 'utf-8'))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        self.axes.set_title(unicode('Calibration plot for ', 'utf-8') + str(obsid))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        for label in self.axes.xaxis.get_ticklabels():
            label.set_fontsize(10)
        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(10)
        #plt.show()
        self.canvas.draw()
        plt.close(self.calibrplotfigure)#this closes reference to self.calibrplotfigure
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.calib_help.setText("")

    def plot_recarray(self, axes, a_recarray, lable, line_style, picker=10):
        """ Plots a recarray to the supplied axes object """
        # Get help from function datestr2num to get date and time into float
        myTimestring = [a_recarray.date_time[idx] for idx in xrange(len(a_recarray))]
        numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        axes.plot_date(numtime, a_recarray.values, line_style, label=lable, picker=picker)

    def set_from_date_from_x(self):
        """ Used to set the self.FromDateTime by clicking on a line node in the plot self.canvas """
        self.reset_plot_selects_and_calib_help()
        self.calib_help.setText("Select a node to use as \"from\"")
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()   
        self.cid.append(self.canvas.mpl_connect('pick_event', lambda event: self.set_date_from_x_onclick(event, self.FromDateTime)))

    def set_to_date_from_x(self):
        """ Used to set the self.ToDateTime by clicking on a line node in the plot self.canvas """    
        self.reset_plot_selects_and_calib_help()
        self.calib_help.setText("Select a node to use as \"to\"")
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()   
        self.cid.append(self.canvas.mpl_connect('pick_event', lambda event: self.set_date_from_x_onclick(event, self.ToDateTime)))

    def set_date_from_x_onclick(self, event, date_holder):
        """ Sets the date_holder to a date from a line node closest to the pick event

            date_holder: a QDateTimeEdit object.
        """
        found_date = utils.find_nearest_date_from_event(event)
        date_holder.setDateTime(found_date)           
        self.reset_plot_selects_and_calib_help()
    
    def reset_plot_selects_and_calib_help(self):
        """ Reset self.cid and self.calib_help """
        self.reset_cid()
        self.log_pos = None
        self.y_pos = None
        self.calib_help.setText("")

    def reset_cid(self):
        """ Resets self.cid to an empty list and disconnects unused events """
        for x in self.cid:
            self.canvas.mpl_disconnect(x)
        self.cid = []

    def calibrate_from_plot_selection(self):
        """ Calibrates by selecting a line node and a y-position on the plot

            The user have to click on the button three times and follow instructions.
        
            The process:
            1. Selecting a line node.
            2. Selecting a selecting a y-position from the plot.
            3. Extracting the head from head_ts with the same date as the line node.
            4. Calculating y-position - head (or level_masl) and setting self.LoggerPos.
            5. Run calibration.
        """            
        #Run init to make sure self.meas_ts and self.head_ts is updated for the current obsid.           
        self.load_obsid_and_init()
        self.deactivate_pan_zoom()
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()

        if self.log_pos is None:
            self.calib_help.setText("Select a logger node.")
            self.cid.append(self.canvas.mpl_connect('pick_event', self.set_log_pos_from_node_date_click))  
        
        if self.log_pos is not None and self.y_pos is None:
            self.calib_help.setText("Select a y position to move to.")
            self.cid.append(self.canvas.mpl_connect('button_press_event', self.set_y_pos_from_y_click))
            
        if self.log_pos is not None and self.y_pos is not None:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)

            if self.loggerpos_masl_or_offset_state == 1:
                logger_ts = self.head_ts
            else:
                logger_ts = self.level_masl_ts
            
            y_pos = self.y_pos
            log_pos = self.log_pos
            self.y_pos = None
            self.log_pos = None
            log_pos_date = datestring_to_date(log_pos).replace(tzinfo=None)
            logger_value = None

            #Get the value for the selected node
            for idx, date_value_tuple in enumerate(logger_ts):
                raw_date, logger_value = date_value_tuple
                date = datestring_to_date(raw_date).replace(tzinfo=None)
                if date == log_pos_date:
                    break

            if logger_value is None:
                utils.pop_up_info("No connection between head_ts dates and logger date could be made!\nTry again or choose a new logger line node!")   
            else:
                self.LoggerPos.setText(str(float(y_pos) - float(logger_value)))

                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                self.calibrateandplot()

            self.calib_help.setText("")
        
    def set_log_pos_from_node_date_click(self, event):
        """ Sets self.log_pos variable to the date (x-axis) from the node nearest the pick event """
        found_date = utils.find_nearest_date_from_event(event)
        self.calib_help.setText("Logger node " + str(found_date) + " selected, click button \"Calibrate by selection in plot\" again.")
        self.log_pos = found_date
        self.reset_cid()
 
    def set_y_pos_from_y_click(self, event):
        """ Sets the self.y_pos variable to the y value of the click event """
        self.y_pos = event.ydata
        self.calib_help.setText("Y position set, click button \"Calibrate by selection in plot\" again for calibration.")
        self.reset_cid()
        
    def calc_best_fit(self):
        """ Calculates the self.LoggerPos from self.meas_ts and self.head_ts
        
            First matches measurements from self.meas_ts to logger values from
            self.head_ts. This is done by making a mean of all logger values inside
            self.meas_ts date - tolerance and self.meas_ts date + tolerance.
            (this could probably be change to get only the closest logger value
            inside the tolerance instead)
            (Tolerance is gotten from self.get_tolerance())
            
            Then calculates the mean of all matches and set to self.LoggerPos.
        """
        obsid = self.load_obsid_and_init()
        self.reset_plot_selects_and_calib_help()
        tolerance = self.get_tolerance()
        really_calibrate_question = utils.askuser("YesNo", """This will calibrate all values inside the chosen period\nusing the mean difference between logger values and measurements.\n\nTime tolerance for matching logger and measurement nodes set to '""" + ' '.join(tolerance) + """'\n\nContinue?""")
        if really_calibrate_question.result == 0: # if the user wants to abort
            return

        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        if self.loggerpos_masl_or_offset_state == 1:
            logger_ts = self.head_ts
        else:
            logger_ts = self.level_masl_ts



        coupled_vals = self.match_ts_values(self.meas_ts, logger_ts, tolerance)
        if not coupled_vals:
            utils.pop_up_info("There was no matched measurements or logger values inside the chosen period.\n Try to increase the tolerance!")
        else:            
            self.LoggerPos.setText(str(utils.calc_mean_diff(coupled_vals)))
            self.calibrateandplot()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
     
    def match_ts_values(self, meas_ts, logger_ts, tolerance):
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
        
        #Get the tolerance, default to 10 minutes
        tol = int(tolerance[0])
        tol_period = tolerance[1]
  
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

            step_begin = dateshift(meas_step, -tol, tol_period)
            step_end = dateshift(meas_step, tol, tol_period)

            if step_end < outer_begin:
                continue
            if step_begin > outer_end:
                break

            #Skip logger steps that are earlier than the chosen begin date or are not inside the measurement period.
            while logger_step < step_begin or logger_step < outer_begin:
                try:
                    l = next(logger_gen)
                except StopIteration:
                    all_done = True
                    break
                logger_step = datestring_to_date(l[0]).replace(tzinfo=None)

            log_vals = []

            while logger_step is not None and logger_step <= step_end and logger_step <= outer_end:
                if not math.isnan(float(l[1])) or l[1] == 'nan' or l[1] == 'NULL':
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
                      
    def get_tolerance(self):
        """ Get the period tolerance, default to 10 minutes """
        if not self.bestFitTolerance.text():
            tol = '10 minutes'
            self.bestFitTolerance.setText(tol)
        else:
            tol = self.bestFitTolerance.text()

        tol_splitted = tol.split()
        if len(tol_splitted) != 2:
            utils.pop_up_info("Must write time resolution also, ex. 10 minutes")
        return tuple(tol_splitted)

    def loggerpos_masl_or_offset_change(self):
        if self.loggerpos_masl_or_offset_state == 1:
            self.label_11.setText("Offset relative to calibrated values:")
            self.loggerpos_masl_or_offset.setText("Change to logger position")
            self.label_adjustment_info.setText("Adjustments made from calibrated values")
            self.loggerpos_masl_or_offset_state = 0
        else:
            self.label_11.setText("Logger position, masl:")
            self.loggerpos_masl_or_offset.setText("Change to offset")
            self.label_adjustment_info.setText("Adjustments made from head")
            self.loggerpos_masl_or_offset_state = 1

    def deactivate_pan_zoom(self):
        """ Deactivates the NavigationToolbar pan or zoom feature if they are currently active """
        if self.mpltoolbar._active == "PAN":
            self.mpltoolbar.pan()
        elif self.mpltoolbar._active == "ZOOM":
            self.mpltoolbar.zoom()

        