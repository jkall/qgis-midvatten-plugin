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

# THIS MODULE IS A TEMPORARY ATTEMPT TO OVERCOME ISSUES WITH PYPLOT PLOTS BLOCKING THE QGIS WINDOW
# THESE ISSUES ONLY OCCUR ON A FEW MACHINES, THE MODULE IS NOT TO BE INCLUDED IN FUTURE RELEASES OF MIDVATTEN PLUGIN
import PyQt4.QtGui

from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import matplotlib
import matplotlib.pyplot as plt 
import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from ui.simpleplotdialog import Ui_Dialog
from qgis.utils import iface

from matplotlib.figure import Figure
from matplotlib.dates import datestr2num
import datetime
import matplotlib.ticker as tick
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import locale

class TimeSeriesPlot(PyQt4.QtGui.QDialog, Ui_Dialog):
    def __init__(self, layer=None, settingsdict={}):
        self.settingsdict = settingsdict
        provider = layer.dataProvider()  #Something with OGR
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        if kolumnindex == -1:
            kolumnindex = provider.fieldNameIndex('OBSID') # backwards compatibility
        if(layer):
            nF = layer.selectedFeatureCount()
            if (nF > 0):
                #self.mpl = PlotMplQt(nF,kolumnindex,layer,self.settingsdict)
                #self.mpl.show()
                PyQt4.QtGui.QDialog.__init__(self)
                self.setupUi(self)
                self.setWindowTitle("Midvatten time series plot")
                self.settingsdict = settingsdict
                conn = sqlite.connect(self.settingsdict['database'],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES) #MacOSX fix1
                # skapa en cursor
                curs = conn.cursor()
                # Load all selected observation points
                ob = layer.selectedFeatures()
                self.fig = Figure()
                self.ax = self.fig.add_subplot(111)

                self.canvas = FigureCanvas( self.fig )
                self.mpltoolbar = NavigationToolbar( self.canvas, self.plotareawidget )
                lstActions = self.mpltoolbar.actions()
                self.mpltoolbar.removeAction( lstActions[ 7 ] )
                self.mplplotlayout.addWidget( self.canvas )
                self.mplplotlayout.addWidget( self.mpltoolbar )
                #Draw the widget
                #self.iface.addDockWidget(self.location, self)
                #self.iface.mapCanvas().setRenderFlag(True)

                
                self.p=[None]*nF # List for plot objects
                self.plabel=[None]*nF # List for label strings
                
                i=0
                for k in ob:    # Loop through all selected objects, a plot is added for each one of the observation points (i.e. selected objects)
                    obsid = unicode(ob[i][kolumnindex]) 
                    # Load all observations (full time series) for the object [i] (i.e. selected observation point no i)
                    sql =r"""SELECT date_time as 'date [datetime]', """
                    sql += unicode(self.settingsdict['tscolumn']) #MacOSX fix1
                    sql += """ FROM """
                    sql += unicode(self.settingsdict['tstable']) #MacOSX fix1
                    sql += r""" WHERE obsid = '"""    
                    sql += obsid  
                    sql += """' ORDER BY date_time """
                    rs = curs.execute(sql) #Send SQL-syntax to cursor
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
                    if self.settingsdict['tsdotmarkers']==2: # If the checkbox is checked - markers will be plotted #MacOSX fix1
                        if self.settingsdict['tsstepplot']==2: # If the checkbox is checked - draw a step plot #MacOSX fix1
                            self.p[i], = self.ax.plot_date(numtime, table2.values, marker = 'o', linestyle = '-',  drawstyle='steps-pre', label=obsid)    # PLOT!!
                        else:
                            self.p[i], = self.ax.plot_date(numtime, table2.values, 'o-',  label=obsid)
                    else:                                                                        # NO markers wil be plotted, , just a line
                        if self.settingsdict['tsstepplot']==2: # If the checkbox is checked - draw a step plot #MacOSX fix1
                            self.p[i], = self.ax.plot_date(numtime, table2.values, marker = 'None', linestyle = '-',  drawstyle='steps-pre', label=obsid)    # PLOT!!
                        else:
                            self.p[i], = self.ax.plot_date(numtime, table2.values, '-',  label=obsid)
                    self.plabel[i] = obsid # Label for the plot
                    
                    i = i+1

                """ Close SQLite-connections """
                rs.close() # First close the table 
                conn.close()  # then close the database

                """ Finish plot """
                self.ax.grid(True)
                self.ax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
                self.fig.autofmt_xdate()
                self.ax.set_ylabel(self.settingsdict['tscolumn']) #MacOSX fix1
                self.ax.set_title(self.settingsdict['tstable'])#MacOSX fix1
                leg = self.fig.legend(self.p, self.plabel, 'right')
                frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
                frame.set_facecolor('0.80')    # set the frame face color to light gray
                for t in leg.get_texts():
                    t.set_fontsize(10)    # the legend text fontsize
                for label in self.ax.xaxis.get_ticklabels():
                    label.set_fontsize(10)
                for label in self.ax.yaxis.get_ticklabels():
                    label.set_fontsize(10)
            else:
                utils.pop_up_info("Please select at least one point with time series data")
        else:
            utils.pop_up_info("Please select a layer with time series observation points")
