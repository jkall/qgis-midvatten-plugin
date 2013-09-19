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

from qgis.core import *
from qgis.gui import *
import qgis.utils

#import csv
#import codecs
import locale
import os
import numpy as np
import matplotlib.pyplot as plt   
from matplotlib.dates import datestr2num
import datetime
import matplotlib.ticker as tick
from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import midvatten_utils as utils    
from ui.calibr_logger_dialog import Ui_Dialog as Calibr_Ui_Dialog
from ui.calc_lvl_dialog import Ui_Dialog as Calc_Ui_Dialog
   
class calclvl(PyQt4.QtGui.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    def __init__(self, parent):
        PyQt4.QtGui.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = utils.getselectedobjectnames()
        self.setWindowTitle("Calculate levels") # Set the title for the dialog
        self.connect(self.pushButton_All, PyQt4.QtCore.SIGNAL("clicked()"), self.calcall)
        self.connect(self.pushButton_Selected, PyQt4.QtCore.SIGNAL("clicked()"), self.calcselected)
        self.connect(self.pushButton_Cancel, PyQt4.QtCore.SIGNAL("clicked()"), self.close)

    def calcall(self):
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
        to_d_t = self.ToDateTime.dateTime().toPyDateTime()
        
#        sanity1 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.h_toc""")
        sanity1 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid""")
        sanity2 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.h_toc NOT NULL""")
        
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
        observations = utils.getselectedobjectnames()
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
        to_d_t = self.ToDateTime.dateTime().toPyDateTime()

        sanity1 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.obsid IN """ + str(observations).replace('[','(').replace(']',')'))
        sanity2 = utils.sql_load_fr_db("""SELECT obs_points.h_toc FROM obs_points LEFT JOIN w_levels WHERE w_levels.obsid = obs_points.obsid AND obs_points.h_toc NOT NULL  AND obs_points.obsid IN """ + str(observations).replace('[','(').replace(']',')'))

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
        
class calibrlogger(PyQt4.QtGui.QDialog, Calibr_Ui_Dialog): # An instance of the class Calibr_Ui_Dialog is created same time as instance of calibrlogger is created

    def __init__(self, parent, obsid=''):
        PyQt4.QtGui.QDialog.__init__(self)
        self.obsid = obsid
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle("Calibrate logger") # Set the title for the dialog
        self.getlastcalibration()
        self.connect(self.pushButton, PyQt4.QtCore.SIGNAL("clicked()"), self.calibrateandplot)
        
    def getlastcalibration(self):
        sql = """SELECT MAX(date_time), loggerpos FROM (SELECT date_time, (level_masl - (head_cm/100)) as loggerpos FROM w_levels_logger WHERE level_masl > 0 AND obsid = '"""
        sql += self.obsid[0]  
        sql += """')"""
        self.lastcalibr = utils.sql_load_fr_db(sql)
        if self.lastcalibr[0][1] and self.lastcalibr[0][0]:
            text = """Last pos. for logger in """
            text += self.obsid[0]
            text += """\nwas """ + str(self.lastcalibr[0][1]) + """ masl\nat """ +  str(self.lastcalibr[0][0])
        else:
            text = """There is no earlier known\nposition for the logger\nin """ + self.obsid[0]
        self.INFO.setText(text)

    def calibrateandplot(self):
        fr_d_t = self.FromDateTime.dateTime().toPyDateTime()
        to_d_t = self.ToDateTime.dateTime().toPyDateTime()
        newzref = self.LoggerPos.text()
        if len(newzref)>0:
            sql =r"""UPDATE w_levels_logger SET level_masl = """
            sql += str(newzref)
            sql += """ + head_cm / 100 WHERE obsid = '"""
            sql += self.obsid[0]   
            sql += """' AND date_time >= '"""
            sql += str(fr_d_t)
            sql += """' AND date_time <= '"""
            sql += str(to_d_t)
            sql += """' """
            dummy = utils.sql_alter_db(sql)
        self.CalibrationPlot(self.obsid[0])
        self.getlastcalibration()

    def CalibrationPlot(self,obsid):            # 
        dbPath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(dbPath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        # skapa en cursor
        curs = conn.cursor()
        # Create a plot window with one single subplot
        fig = plt.figure()  # causes conflict with plugins "statist" and "chartmaker"
        ax = fig.add_subplot(111)
        
        p=[None]*2 # List for plot objects
        My_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array 
        
        # Load manual reading (full time series) for the obsid
        sql =r"""SELECT date_time, level_masl FROM w_levels WHERE obsid = '"""
        sql += obsid   
        sql += """' ORDER BY date_time"""
        rs = curs.execute(sql) #Send SQL-syntax to cursor
        recs = rs.fetchall()  # All data are stored in recs
        #Transform data to a numpy.recarray
        table = np.array(recs, dtype=My_format)  #NDARRAY
        table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values    
        # Get help from function datestr2num to get date and time into float
        myTimestring = []  #LIST
        j = 0
        for row in table2:
            myTimestring.append(table2.date_time[j])
            j = j + 1
        numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        p[0] = ax.plot_date(numtime, table2.values, 'o-', label=obsid)    # LINEPLOT WITH DOTS!!
        
        # Load Loggerlevels (full time series) for the obsid
        sql =r"""SELECT date_time as 'date [datetime]', level_masl FROM w_levels_logger WHERE obsid = '"""
        sql += obsid   # The result has format 'Qstring' - no good
        sql += """' ORDER BY date_time"""
        rs = curs.execute(sql) #Send SQL-syntax to cursor
        recs = rs.fetchall()  # All data are stored in recs
        #Transform data to a numpy.recarray
        table = np.array(recs, dtype=My_format)  #NDARRAY
        table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values    
        # Get help from function datestr2num to get date and time into float
        myTimestring = []  #LIST
        j = 0
        for row in table2:
            myTimestring.append(table2.date_time[j])
            j = j + 1
        numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        p[1] = ax.plot_date(numtime, table2.values, '-', label = obsid + unicode(' logger', 'utf-8'))    # LINEPLOT WITH DOTS!!

        """ Close SQLite-connections """
        rs.close() # First close the table 
        conn.close()  # then close the database

        """ Finish plot """
        ax.grid(True)
        ax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        fig.autofmt_xdate()                               
        ax.set_ylabel(unicode('Level (masl)', 'utf-8'))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        ax.set_title(unicode('Calibration plot for ', 'utf-8') + str(obsid))  #This is the method that accepts even national characters ('åäö') in matplotlib axes labels
        for label in ax.xaxis.get_ticklabels():
            label.set_fontsize(10)
        for label in ax.yaxis.get_ticklabels():
            label.set_fontsize(10)
        plt.show()

