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

from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
"""
from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import numpy as np

import db_utils
import matplotlib
import matplotlib.pyplot as plt 
#plt.ion() #interactive mode immediately to prevent pyplot plots from blocking application
from matplotlib.dates import datestr2num
import datetime
import matplotlib.ticker as tick
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
import locale

from PyQt4.QtCore import QCoreApplication

class TimeSeriesPlot:

    def __init__(self, layer=None, settingsdict={}):    # Might need revision of variables and method for loading default variables
        self.settingsdict = settingsdict
        self.showtheplot(layer)

    @db_utils.if_connection_ok
    def showtheplot(self, layer):            # PlotTS method that, at the moment, performs all the real work
        provider = layer.dataProvider()  #Something with OGR
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        if kolumnindex == -1:
            kolumnindex = provider.fieldNameIndex('OBSID') # backwards compatibility
        if(layer):
            nF = layer.selectedFeatureCount()
            if (nF > 0):
                # Load all selected observation points
                ob = layer.selectedFeatures()

                # Create a plot window with one single subplot
                fig = plt.figure()  # causes conflict with plugins "statist" and "chartmaker"
                ax = fig.add_subplot(111)

                p=[None]*nF # List for plot objects
                plabel=[None]*nF # List for label strings

                for i, k in enumerate(ob):    # Loop through all selected objects, a plot is added for each one of the observation points (i.e. selected objects)
                    obsid = unicode(ob[i][kolumnindex])
                    # Load all observations (full time series) for the object [i] (i.e. selected observation point no i)
                    sql =r"""SELECT date_time as 'date [datetime]', """
                    sql += unicode(self.settingsdict['tscolumn']) #MacOSX fix1
                    sql += """ FROM """
                    sql += unicode(self.settingsdict['tstable']) #MacOSX fix1
                    sql += r""" WHERE obsid = '"""
                    sql += obsid
                    sql += """' ORDER BY date_time """
                    connection_ok, recs = db_utils.sql_load_fr_db(sql)
                    """Transform data to a numpy.recarray"""
                    My_format = [('date_time', datetime.datetime), ('values', float)] #Define format with help from function datetime
                    table = np.array(recs, dtype=My_format)  #NDARRAY
                    table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values

                    """ Get help from function datestr2num to get date and time into float"""
                    myTimestring = []  #LIST
                    for j, row in enumerate(table2):
                        myTimestring.append(table2.date_time[j])
                    numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
                    if self.settingsdict['tsdotmarkers']==2: # If the checkbox is checked - markers will be plotted #MacOSX fix1
                        if self.settingsdict['tsstepplot']==2: # If the checkbox is checked - draw a step plot #MacOSX fix1
                            p[i], = ax.plot_date(numtime, table2.values, marker = 'o', linestyle = '-',  drawstyle='steps-pre', label=obsid)    # PLOT!!
                        else:
                            p[i], = ax.plot_date(numtime, table2.values, 'o-',  label=obsid)
                    else:                                                                        # NO markers wil be plotted, , just a line
                        if self.settingsdict['tsstepplot']==2: # If the checkbox is checked - draw a step plot #MacOSX fix1
                            p[i], = ax.plot_date(numtime, table2.values, marker = 'None', linestyle = '-',  drawstyle='steps-pre', label=obsid)    # PLOT!!
                        else:
                            p[i], = ax.plot_date(numtime, table2.values, '-',  label=obsid)
                    plabel[i] = obsid # Label for the plot

                    """ Finish plot """
                    ax.grid(True)
                    ax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
                    fig.autofmt_xdate()
                    ax.set_ylabel(self.settingsdict['tscolumn']) #MacOSX fix1
                    ax.set_title(self.settingsdict['tstable'])#MacOSX fix1
                    leg = fig.legend(p, plabel, loc=0)#leg = fig.legend(p, plabel, 'right')
                    leg.draggable(state=True)
                    frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                    frame.set_facecolor('0.80')    # set the frame face color to light gray
                    frame.set_fill(False)    # set the frame face color transparent                
                    
                    for t in leg.get_texts():
                        t.set_fontsize(10)    # the legend text fontsize
                    for label in ax.xaxis.get_ticklabels():
                        label.set_fontsize(10)
                    for label in ax.yaxis.get_ticklabels():
                        label.set_fontsize(10)
                    #plt.ion()#force interactivity to prevent the plot window from blocking the qgis app
                    plt.show() 
                    #plt.draw()
            else:
                utils.pop_up_info(ru(QCoreApplication.translate(u'TimeSeriesPlot', u"Please select at least one point with time series data")))
        else:
            utils.pop_up_info(ru(QCoreApplication.translate(u'TimeSeriesPlot', u"Please select a layer with time series observation points")))
