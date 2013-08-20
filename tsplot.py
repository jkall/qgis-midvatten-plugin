# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin originates from the TimeSeriesPlot plugin. 
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
from PyQt4.QtGui import *    # Needed for QMessageBox
from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import numpy as np
import matplotlib
import matplotlib.pyplot as plt  # THIS LINE may cause conflict with plugins "statist" and "chartmaker"  - THE ISSUE IS NOT SOLVED. May be due to matplotlib.pyplot assumes other backend by default  
from matplotlib.dates import datestr2num
import datetime
import matplotlib.ticker as tick
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import locale

class TimeSeriesPlot:

    def __init__(self, iface, layer=None, settingsdict={}):    # Might need revision of variables and method for loading default variables
        self.iface = iface
        self.settingsdict = settingsdict
        self.showtheplot(layer)


    def showtheplot(self, layer):            # PlotTS method that, at the moment, performs all the real work
        provider = layer.dataProvider()  #Something with OGR
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        if kolumnindex == -1:
            kolumnindex = provider.fieldNameIndex('OBSID') # backwards compatibility
        if(layer):
            nF = layer.selectedFeatureCount()
            if (nF > 0):
                conn = sqlite.connect(str(self.settingsdict['database']).encode(locale.getdefaultlocale()[1]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
                # skapa en cursor
                curs = conn.cursor()
                # Load all selected observation points
                ob = layer.selectedFeatures()

                # Create a plot window with one single subplot
                fig = plt.figure()  # causes conflict with plugins "statist" and "chartmaker"
                ax = fig.add_subplot(111)
                
                p=[None]*nF # List for plot objects
                plabel=[None]*nF # List for label strings
                
                i=0
                for k in ob:    # Loop through all selected objects, a plot is added for each one of the observation points (i.e. selected objects)
                    obsid = str(ob[i][kolumnindex]) 
                    # Load all observations (full time series) for the object [i] (i.e. selected observation point no i)
                    sql =r"""SELECT date_time as 'date [datetime]', """
                    sql += str(self.settingsdict['tscolumn']).encode(locale.getdefaultlocale()[1])
                    sql += """ FROM """
                    sql += str(self.settingsdict['tstable']).encode(locale.getdefaultlocale()[1])
                    sql += r""" WHERE obsid = '"""    
                    sql += obsid   # The result has format 'Qstring' - no good
                    sql += """' ORDER BY date_time """
                    sql2 = str(sql).encode(locale.getdefaultlocale()[1])  #To get back to uniciode-string
                    rs = curs.execute(sql2) #Send SQL-syntax to cursor
                    recs = rs.fetchall()  # All data are stored in recs
                    """Transform data to a numpy.recarray"""
                    My_format = [('date_time', datetime.datetime), ('values', float)] #Define format with help from function datetime
                    table = np.array(recs, dtype=My_format)  #NDARRAY
                    table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values
                    
                    """ Get help from function datestr2num to get date and time into float""" 
                    myTimestring = []  #LIST
                    j = 0
                    for row in table2:
                        myTimestring.append(table2.date_time[j])
                        j = j + 1
                    numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
                    if str(self.settingsdict['tsdotmarkers']).encode(locale.getdefaultlocale()[1])=='2':            # If the checkbox is checked - markers will be plotted
                        if str(self.settingsdict['tsstepplot']).encode(locale.getdefaultlocale()[1])=='2':    # If the checkbox is checked - draw a step plot
                            p[i], = ax.plot_date(numtime, table2.values, marker = 'o', linestyle = '-',  drawstyle='steps-pre', label=obsid)    # PLOT!!
                        else:
                            p[i], = ax.plot_date(numtime, table2.values, 'o-',  label=obsid)
                    else:                                                                        # NO markers wil be plotted, , just a line
                        if str(self.settingsdict['tsstepplot']).encode(locale.getdefaultlocale()[1])=='2':    # If the checkbox is checked - draw a step plot
                            #utils.pop_up_info("stepplot")        #debugging
                            p[i], = ax.plot_date(numtime, table2.values, marker = 'None', linestyle = '-',  drawstyle='steps-pre', label=obsid)    # PLOT!!
                        else:
                            #utils.pop_up_info("no steps")        #debugging
                            p[i], = ax.plot_date(numtime, table2.values, '-',  label=obsid)
                    plabel[i] = obsid # Label for the plot
                    
                    i = i+1

                """ Close SQLite-connections """
                rs.close() # First close the table 
                conn.close()  # then close the database

                """ Finish plot """
                ax.grid(True)
                ax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
                fig.autofmt_xdate()
                ax.set_ylabel(str(self.settingsdict['tscolumn']).encode(locale.getdefaultlocale()[1]))
                ax.set_title(str(self.settingsdict['tstable']).encode(locale.getdefaultlocale()[1]))  
                leg = fig.legend(p, plabel, 'right')
                frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_facecolor('0.80')    # set the frame face color to light gray
                for t in leg.get_texts():
                    t.set_fontsize(10)    # the legend text fontsize
                for label in ax.xaxis.get_ticklabels():
                    label.set_fontsize(10)
                for label in ax.yaxis.get_ticklabels():
                    label.set_fontsize(10)
                plt.show() # causes conflict with plugins "statist" and "chartmaker"
            else:
                utils.pop_up_info("Please select at least one point with time series data")
        else:
            utils.pop_up_info("Please select a layer with time series observation points")
