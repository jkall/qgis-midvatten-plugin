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

import qgis.utils
from pyspatialite import dbapi2 as sqlite  
import numpy as np
import matplotlib
import matplotlib.pyplot as plt  # THIS LINE may cause conflict with plugins "statist" and "chartmaker"  - THE ISSUE IS NOT SOLVED. May be due to matplotlib.pyplot assumes other backend by default  
#from matplotlib.dates import datestr2num
#import datetime
import matplotlib.ticker as tick
import midvatten_utils as utils
import locale

class XYPlot:

    def __init__(self, layer=None, settingsdict={}):    # Might need revision of variables and method for loading default variables
        self.settingsdict = settingsdict
        self.table = settingsdict['xytable']
        self.xcol = settingsdict['xy_xcolumn']
        self.y1col = settingsdict['xy_y1column']
        self.y2col = settingsdict['xy_y2column']
        self.y3col = settingsdict['xy_y3column']
        self.markers = settingsdict['xydotmarkers']
        self.showtheplot(layer)


    def showtheplot(self, layer):            # PlotTS method that, at the moment, performs all the real work
        provider = layer.dataProvider()  #Something with OGR
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        if kolumnindex == -1:
            kolumnindex = provider.fieldNameIndex('OBSID') # backwards compatibility
        if(layer):
            nF = layer.selectedFeatureCount()
            if (nF > 0):
                myconnection = utils.dbconnection()
                if myconnection.connect2db() == True:
                    # skapa en cursor
                    curs = myconnection.conn.cursor()
                    # Load all selected observation points
                    ob = layer.selectedFeatures()

                    # Create a plot window with one single subplot
                    fig = plt.figure()  # causes conflict with plugins "statist" and "chartmaker"
                    ax = fig.add_subplot(111)

                    if len(self.y3col):
                        nY = 3
                    elif len(self.y2col):
                        nY = 2
                    else:
                        nY = 1
                    p=[None]*nF*nY # List for plot objects
                    plabel=[None]*nF*nY # List for label strings
                    
                    i=0
                    j=0
                    for k in ob:    # Loop through all selected objects, a plot is added for each one of the observation points (i.e. selected objects)
                        attributes = ob[i]
                        obsid = attributes[kolumnindex] # Copy value in column obsid in the attribute list 
                        # Load all observations (full time series) for the object [i] (i.e. selected observation point no i)
                        sql =r"""SELECT """ 
                        sql += unicode(self.xcol) #MacOSX fix1
                        sql += r""" as 'x'"""
                        if len(self.y1col):
                            sql += r""", """
                            sql += unicode(self.y1col) #MacOSX fix1
                            sql += r""" as 'y1'"""
                        if len(self.y2col):
                            sql += r""", """
                            sql += unicode(self.y2col) #MacOSX fix1
                            sql += r""" as 'y2'"""
                        if len(self.y3col):
                            sql += r""", """
                            sql += unicode(self.y3col) #MacOSX fix1
                            sql += r""" as 'y3'"""
                        sql += """ FROM """
                        sql += unicode(self.table) #MacOSX fix1
                        sql += r""" WHERE obsid = '"""    
                        sql += obsid   
                        sql += """' ORDER BY """
                        sql += unicode(self.xcol) #MacOSX fix1
                        rs = curs.execute(sql) #Send SQL-syntax to cursor
                        recs = rs.fetchall()  # All data are stored in recs
                        """Transform data to a numpy.recarray"""
                        if len(self.y1col):
                            My_format = [('x', float), ('y1', float)]
                        if len(self.y2col):
                            My_format.append(('y2', float))
                        if len(self.y3col):
                            My_format.append(('y3', float))
                        table = np.array(recs, dtype=My_format)  #NDARRAY
                        table2=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write table2.values
                                        
                        if self.markers==2: # If the checkbox is checked - markers will be plotted, just a line #MacOSX fix1
                            p[j], = ax.plot(table2.x, table2.y1, marker = 'o', linestyle = '-', label=obsid)    # PLOT!!
                        else:
                            p[j], = ax.plot(table2.x, table2.y1, marker = 'None', linestyle = '-', label=obsid)    # PLOT!!
                        plabel[j] = obsid + unicode(self.y1col) #+ str(j)# Label for the plot #MacOSX fix1
                        if len(self.y2col):
                            j = j + 1
                            if self.markers==2:# If the checkbox is checked - markers will be plotted, just a line #MacOSX fix1
                                p[j], = ax.plot(table2.x, table2.y2, marker = 'o', linestyle = '-', label=obsid)    # PLOT!!
                            else:
                                p[j], = ax.plot(table2.x, table2.y2, marker = 'None', linestyle = '-', label=obsid)    # PLOT!!
                            plabel[j] = obsid + unicode(self.y2col) #+ str(j)# Label for the plot #MacOSX fix1
                        if len(self.y3col):
                            j = j + 1
                            if self.markers==2: # If the checkbox is checked - markers will be plotted, just a line #MacOSX fix1
                                p[j], = ax.plot(table2.x, table2.y3, marker = 'o', linestyle = '-', label=obsid)    # PLOT!!
                            else:
                                p[j], = ax.plot(table2.x, table2.y3, marker = 'None', linestyle = '-', label=obsid)    # PLOT!!
                            plabel[j] = obsid + unicode(self.y3col) #+ str(j)# Label for the plot #MacOSX fix1
                        j = j + 1
                        i = i+1

                    """ Close SQLite-connections """
                    myconnection.closedb()# then close the database

                    """ Finish plot """
                    ax.grid(True)
                    ax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
                    ax.set_xlabel(self.xcol) #MacOSX fix1
                    ylabel = unicode(self.y1col) + ", \n" + unicode(self.y2col) + ", \n" + unicode(self.y3col) #MacOSX fix1
                    ax.set_ylabel(ylabel)
                    ax.set_title(self.settingsdict['xytable']) #MacOSX fix1
                    leg = fig.legend(p, plabel, loc=0)
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
                    plt.show() # causes conflict with plugins "statist" and "chartmaker"
            else:
                utils.pop_up_info("Please select at least one point with xy data")
        else:
            utils.pop_up_info("Please select a layer containing observations with xy data")
