# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin originates from the PlotSQLite application which plots . 
        Name                 : PlotSQLite
        Description          : Plots charts from data stored in a SQLite database
        Date                 : 2012-12-03 
        Author               : Josef Källgården
        copyright            : (C) 2011 by Josef Källgården
        email                : groundwatergis [at] gmail.com

The PlotSQLite application version 0.2.6 was merged into Midvatten plugin at 2014-05-06
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
import sys, os, locale
from PyQt4 import QtGui, QtCore, uic#, QtSql
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from functools import partial # only to get combobox signals to work

from sqlite3 import dbapi2 as sqlite
import numpy as np
import matplotlib.pyplot as plt   
from matplotlib.dates import datestr2num
from matplotlib import ticker
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
import datetime
import matplotlib.ticker as tick
#import midvatten_utils as utils
import midvatten_utils as utils
from definitions import midvatten_defs

customplot_ui_class =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..', 'ui', 'customplotdialog.ui'))[0]

class plotsqlitewindow(QtGui.QMainWindow, customplot_ui_class):
    def __init__(self, parent, msettings):#, parent as second arg?
        self.ms = msettings
        self.ms.loadSettings()
        QtGui.QDialog.__init__(self, parent)        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi( self )#due to initialisation of Ui_MainWindow instance
        self.initUI()
        self.LoadTablesFromDB()
        self.LastSelections()#fill comboboxes etc with last selected values
        #on close:
        #del self.axes.collections[:]#this should delete all plot objects related to axes and hence not intefere with following tsplots
        self.drawn = False
        
    def initUI(self):
        self.table_ComboBox_1.clear()  
        self.table_ComboBox_2.clear()  
        self.table_ComboBox_3.clear()  
        for i in range (1,3):
            self.clearthings(1)
        # function partial due to problems with currentindexChanged and Combobox
        #self.connect(self.table_ComboBox_1, QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.Table1Changed))#currentIndexChanged caused unnecessary signals when scrolling in combobox
        self.connect(self.table_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.Table1Changed))  
        self.connect(self.Filter1_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.Filter1_1Changed))
        #self.connect(self.Filter1_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.FilterChanged(1,1)))
        self.connect(self.Filter2_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.Filter2_1Changed)) 
        self.connect(self.table_ComboBox_2, QtCore.SIGNAL("activated(int)"), partial(self.Table2Changed)) 
        self.connect(self.Filter1_ComboBox_2, QtCore.SIGNAL("activated(int)"), partial(self.Filter1_2Changed))
        self.connect(self.Filter2_ComboBox_2, QtCore.SIGNAL("activated(int)"), partial(self.Filter2_2Changed)) 
        self.connect(self.table_ComboBox_3, QtCore.SIGNAL("activated(int)"), partial(self.Table3Changed)) 
        self.connect(self.Filter1_ComboBox_3, QtCore.SIGNAL("activated(int)"), partial(self.Filter1_3Changed))
        self.connect(self.Filter2_ComboBox_3, QtCore.SIGNAL("activated(int)"), partial(self.Filter2_3Changed)) 
        self.PlotChart_QPushButton.clicked.connect(self.drawPlot)
        self.Redraw_pushButton.clicked.connect( self.refreshPlot )
        
        # Create a plot window with one single subplot
        self.custplotfigure = plt.figure() 
        self.axes = self.custplotfigure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.custplotfigure )
        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )

        self.show()

    def calc_frequency(self,table2):
        freqs = np.zeros(len(table2.values),dtype=float)
        for j, row in enumerate(table2):                
            if j>0:#we can not calculate frequency for first row
                try:
                    diff = (table2.values[j] - table2.values[j-1])
                    """ Get help from function datestr2num to get date and time into float"""
                    delta_time = 24*3600*(datestr2num(table2.date_time[j]) - datestr2num(table2.date_time[j-1]))#convert to seconds since numtime is days
                except:
                    pass #just skip inaccurate data values and use previous frequency
                freqs[j] = diff/delta_time
        freqs[0]=freqs[1]#assuming start frequency to get a nicer plot
        return freqs 
        
    def drawPlot(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))#show the user this may take a long time...

        self.axes.clear()
        self.axes.legend_ = None
        My_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array
        
        myconnection = utils.dbconnection()
        myconnection.connect2db()
        curs = myconnection.conn.cursor()

        i = 0
        nop=0# nop=number of plots
        self.p=[]
        self.plabels=[]
                
        if not (self.table_ComboBox_1.currentText() == '' or self.table_ComboBox_1.currentText()==' ') and not (self.xcol_ComboBox_1.currentText()== '' or self.xcol_ComboBox_1.currentText()==' ') and not (self.ycol_ComboBox_1.currentText()== '' or self.ycol_ComboBox_1.currentText()==' '): #if anything is to be plotted from tab 1
            self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()   # if user selected a time step bigger than zero than thre may be discontinuous plots
            plottable1='y'
            filter1 = unicode(self.Filter1_ComboBox_1.currentText())
            filter1list = []
            filter2list = []
            filter1list = self.Filter1_QListWidget_1.selectedItems()
            filter2 = unicode(self.Filter2_ComboBox_1.currentText())
            filter2list= self.Filter2_QListWidget_1.selectedItems()
            nop += max(len(filter1list),1)*max(len(filter2list),1)
            #self.p= [None]*nop#list for plot objects
            self.p.extend([None]*nop)#list for plot objects
            self.plabels.extend([None]*nop)# List for plot labels
            try:
                factor1 = float(self.lineEditFactor1.text())
            except ValueError:
                factor1 = 1.0

            while i < len(self.p):
                if not (filter1 == '' or filter1==' ' or filter1list==[]) and not (filter2== '' or filter2==' ' or filter2list==[]):
                    for item1 in filter1list:
                        for item2 in filter2list:
                            sql = r""" select """ + unicode(self.xcol_ComboBox_1.currentText()) + """, """ + unicode(self.ycol_ComboBox_1.currentText()) + """ from """ + unicode(self.table_ComboBox_1.currentText()) + """ where """ + filter1 + """='""" + unicode(item1.text())+ """' and """ + filter2 + """='""" + unicode(item2.text())+ """' order by """ + unicode(self.xcol_ComboBox_1.currentText())
                            self.plabels[i] = unicode(item1.text()) + """, """ + unicode(item2.text())
                            self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_1.currentText(), factor1)
                            i += 1
                elif not (filter1 == '' or filter1==' ' or filter1list==[]):
                    for item1 in filter1list:
                        sql = r""" select """ + unicode(self.xcol_ComboBox_1.currentText()) + """, """ + unicode(self.ycol_ComboBox_1.currentText()) + """ from """ + unicode(self.table_ComboBox_1.currentText()) + """ where """ + filter1 + """='""" + unicode(item1.text())+ """' order by """ + unicode(self.xcol_ComboBox_1.currentText())
                        self.plabels[i] = unicode(item1.text()) 
                        self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_1.currentText(), factor1)
                        i += 1
                elif not (filter2 == '' or filter2==' ' or filter2list==[]):
                    for item2 in filter2list:
                        sql = r""" select """ + unicode(self.xcol_ComboBox_1.currentText()) + """, """ + unicode(self.ycol_ComboBox_1.currentText()) + """ from """ + unicode(self.table_ComboBox_1.currentText()) + """ where """ + filter2 + """='""" + unicode(item2.text())+ """' order by """ + unicode(self.xcol_ComboBox_1.currentText())
                        self.plabels[i] = unicode(item2.text())
                        self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_1.currentText(), factor1)
                        i += 1            
                else:
                    sql = r""" select """ + unicode(self.xcol_ComboBox_1.currentText()) + """, """ + unicode(self.ycol_ComboBox_1.currentText()) + """ from """ + unicode(self.table_ComboBox_1.currentText()) + """ order by """ + unicode(self.xcol_ComboBox_1.currentText())
                    self.plabels[i] = unicode(self.ycol_ComboBox_1.currentText())+""", """+unicode(self.table_ComboBox_1.currentText())
                    self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_1.currentText(), factor1)
                    i += 1

        if not (self.table_ComboBox_2.currentText() == '' or self.table_ComboBox_2.currentText()==' ') and not (self.xcol_ComboBox_2.currentText()== '' or self.xcol_ComboBox_2.currentText()==' ') and not (self.ycol_ComboBox_2.currentText()== '' or self.ycol_ComboBox_2.currentText()==' '):#if anything is to be plotted from tab 2
            self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()   # if user selected a time step bigger than zero than thre may be discontinuous plots
            plottable2='y'
            filter1 = unicode(self.Filter1_ComboBox_2.currentText())
            filter1list = []
            filter2list = []
            filter1list = self.Filter1_QListWidget_2.selectedItems()
            filter2 = unicode(self.Filter2_ComboBox_2.currentText())
            filter2list= self.Filter2_QListWidget_2.selectedItems()
            nop =+ max(len(filter1list),1)*max(len(filter2list),1)
            self.p.extend([None]*nop)#list for plot objects
            self.plabels.extend([None]*nop)# List for plot labels
            try:
                factor2 = float(self.lineEditFactor2.text())
            except ValueError:
                factor2 = 1.0

            while i < len(self.p):
                if not (filter1 == '' or filter1==' ' or filter1list==[]) and not (filter2== '' or filter2==' ' or filter2list==[]):
                    for item1 in filter1list:
                        for item2 in filter2list:
                            sql = r""" select """ + unicode(self.xcol_ComboBox_2.currentText()) + """, """ + unicode(self.ycol_ComboBox_2.currentText()) + """ from """ + unicode(self.table_ComboBox_2.currentText()) + """ where """ + filter1 + """='""" + unicode(item1.text())+ """' and """ + filter2 + """='""" + unicode(item2.text())+ """' order by """ + unicode(self.xcol_ComboBox_2.currentText())
                            self.plabels[i] = unicode(item1.text()) + """, """ + unicode(item2.text())
                            self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_2.currentText(), factor2)
                            i += 1
                elif not (filter1 == '' or filter1==' ' or filter1list==[]):
                    for item1 in filter1list:
                        sql = r""" select """ + unicode(self.xcol_ComboBox_2.currentText()) + """, """ + unicode(self.ycol_ComboBox_2.currentText()) + """ from """ + unicode(self.table_ComboBox_2.currentText()) + """ where """ + filter1 + """='""" + unicode(item1.text())+ """' order by """ + unicode(self.xcol_ComboBox_2.currentText())
                        self.plabels[i] = unicode(item1.text()) 
                        self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_2.currentText(), factor2)
                        i += 1
                elif not (filter2 == '' or filter2==' ' or filter2list==[]):
                    for item2 in filter2list:
                        sql = r""" select """ + unicode(self.xcol_ComboBox_2.currentText()) + """, """ + unicode(self.ycol_ComboBox_2.currentText()) + """ from """ + unicode(self.table_ComboBox_2.currentText()) + """ where """ + filter2 + """='""" + unicode(item2.text())+ """' order by """ + unicode(self.xcol_ComboBox_2.currentText())
                        self.plabels[i] = unicode(item2.text())
                        self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_2.currentText(), factor2)
                        i += 1            
                else:
                    sql = r""" select """ + unicode(self.xcol_ComboBox_2.currentText()) + """, """ + unicode(self.ycol_ComboBox_2.currentText()) + """ from """ + unicode(self.table_ComboBox_2.currentText()) + """ order by """ + unicode(self.xcol_ComboBox_2.currentText())
                    self.plabels[i] = unicode(self.ycol2)+""", """+unicode(self.table_ComboBox_2.currentText())
                    self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_2.currentText(), factor2)
                    i += 1
            
        if not (self.table_ComboBox_3.currentText() == '' or self.table_ComboBox_3.currentText()==' ') and not (self.xcol_ComboBox_3.currentText()== '' or self.xcol_ComboBox_3.currentText()==' ') and not (self.ycol_ComboBox_3.currentText()== '' or self.ycol_ComboBox_3.currentText()==' '):#if anything is to be plotted from tab 3
            self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()   # if user selected a time step bigger than zero than thre may be discontinuous plots
            plottable3='y'
            filter1 = unicode(self.Filter1_ComboBox_3.currentText())
            filter1list = []
            filter2list = []
            filter1list = self.Filter1_QListWidget_3.selectedItems()
            filter2 = unicode(self.Filter2_ComboBox_3.currentText())
            filter2list= self.Filter2_QListWidget_3.selectedItems()
            nop =+ max(len(filter1list),1)*max(len(filter2list),1)
            self.p.extend([None]*nop)#list for plot objects
            self.plabels.extend([None]*nop)# List for plot labels
            try:
                factor3 = float(self.lineEditFactor3.text())
            except ValueError:
                factor3 = 1.0

            while i < len(self.p):
                if not (filter1 == '' or filter1==' ' or filter1list==[]) and not (filter2== '' or filter2==' ' or filter2list==[]):
                    for item1 in filter1list:
                        for item2 in filter2list:
                            sql = r""" select """ + unicode(self.xcol_ComboBox_3.currentText()) + """, """ + unicode(self.ycol_ComboBox_3.currentText()) + """ from """ + unicode(self.table_ComboBox_3.currentText()) + """ where """ + filter1 + """='""" + unicode(item1.text())+ """' and """ + filter2 + """='""" + unicode(item2.text())+ """' order by """ + unicode(self.xcol_ComboBox_3.currentText())
                            self.plabels[i] = unicode(item1.text()) + """, """ + unicode(item2.text())
                            self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_3.currentText(), factor3)
                            i += 1
                elif not (filter1 == '' or filter1==' ' or filter1list==[]):
                    for item1 in filter1list:
                        sql = r""" select """ + unicode(self.xcol_ComboBox_3.currentText()) + """, """ + unicode(self.ycol_ComboBox_3.currentText()) + """ from """ + unicode(self.table_ComboBox_3.currentText()) + """ where """ + filter1 + """='""" + unicode(item1.text())+ """' order by """ + unicode(self.xcol_ComboBox_3.currentText())
                        self.plabels[i] = unicode(item1.text()) 
                        self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_3.currentText(), factor3)
                        i += 1
                elif not (filter2 == '' or filter2==' ' or filter2list==[]):
                    for item2 in filter2list:
                        sql = r""" select """ + unicode(self.xcol_ComboBox_3.currentText()) + """, """ + unicode(self.ycol_ComboBox_3.currentText()) + """ from """ + unicode(self.table_ComboBox_3.currentText()) + """ where """ + filter2 + """='""" + unicode(item2.text())+ """' order by """ + unicode(self.xcol_ComboBox_3.currentText())
                        self.plabels[i] = unicode(item2.text())
                        self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_3.currentText(), factor3)
                        i += 1            
                else:
                    sql = r""" select """ + unicode(self.xcol_ComboBox_3.currentText()) + """, """ + unicode(self.ycol_ComboBox_3.currentText()) + """ from """ + unicode(self.table_ComboBox_3.currentText()) + """ order by """ + unicode(self.xcol_ComboBox_3.currentText())
                    self.plabels[i] = unicode(self.ycol_ComboBox_3.currentText())+""", """+unicode(self.table_ComboBox_3.currentText())
                    self.createsingleplotobject(sql,i,My_format,curs,self.PlotType_comboBox_3.currentText(), factor3)
                    i += 1

        #rs.close() # close the cursor
        myconnection.closedb()  # close the database

        self.xaxis_formatters = (self.axes.xaxis.get_major_formatter(), self.axes.xaxis.get_major_locator())

        self.axes.set_title(self.ms.settingsdict['custplot_title'])
        self.axes.set_xlabel(self.ms.settingsdict['custplot_xtitle'])
        self.axes.set_ylabel(self.ms.settingsdict['custplot_ytitle'])

        self.drawn = True

        self.refreshPlot()

        QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def createsingleplotobject(self,sql,i,My_format,curs,plottype='line', factor=1.0):
        rs = curs.execute(sql) #Send SQL-syntax to cursor
        recs = rs.fetchall()  # All data are stored in recs
        # late fix for xy-plots

        #Transform data to a numpy.recarray
        try:
            table = np.array(recs, dtype=My_format)  #NDARRAY

            table = utils.scale_nparray_column(table, 1, factor)

            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects
            FlagTimeXY = 'time'
            myTimestring = list(table2.date_time)
            numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        except:
            table = np.array(recs, dtype=[('numx', float), ('values', float)])  #NDARRAY #define a format for xy-plot (to use if not datetime on x-axis)

            table = utils.scale_nparray_column(table, 1, factor)

            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects
            FlagTimeXY = 'XY'
            numtime = list(table2.numx)

        # from version 0.2 there is a possibility to make discontinuous plot if timestep bigger than maxtstep
        if self.spnmaxtstep.value() > 0: # if user selected a time step bigger than zero than thre may be discontinuous plots
            pos = np.where(np.abs(np.diff(numtime)) >= self.spnmaxtstep.value())[0]
            numtime[pos] = np.nan
            table2.values[pos] = np.nan

        if plottype == "marker":
            MarkVar = 'o'  
        elif plottype in ("line","frequency"):
            MarkVar = '-'  
        elif plottype  == "line and cross":
            MarkVar = '+-'  
        else:
            MarkVar = 'o-'  

        if FlagTimeXY == "time" and plottype == "step-pre":
            self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',c=np.random.rand(3,1),label=self.plabels[i])# 'steps-pre' best for precipitation and flowmeters, optional types are 'steps', 'steps-mid', 'steps-post'  
        elif FlagTimeXY == "time" and plottype == "step-post":
            self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',c=np.random.rand(3,1),label=self.plabels[i])
        elif FlagTimeXY == "time" and plottype == "line and cross":
            self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,markersize = 6, label=self.plabels[i])
        elif FlagTimeXY == "time" and plottype == "frequency":
            try:
                freqs = self.calc_frequency(table2)
                self.p[i], = self.axes.plot_date(numtime, freqs,  MarkVar,markersize = 6, label='frequency '+str(self.plabels[i]))
                self.plabels[i]='frequency '+str(self.plabels[i])
            except:
                self.p[i], = self.axes.plot_date(np.array([]),np.array([]),  MarkVar,markersize = 6, label='frequency '+str(self.plabels[i]))
                self.plabels[i]='frequency '+str(self.plabels[i])
        elif FlagTimeXY == "time":
            self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,label=self.plabels[i])
        elif FlagTimeXY == "XY" and plottype == "step-pre":
            self.p[i], = self.axes.plot(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',c=np.random.rand(3,1),label=self.plabels[i]) 
        elif FlagTimeXY == "XY" and plottype == "step-post":
            self.p[i], = self.axes.plot(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',c=np.random.rand(3,1),label=self.plabels[i]) 
        elif FlagTimeXY == "XY" and plottype == "line and cross":
            self.p[i], = self.axes.plot(numtime, table2.values,  MarkVar,markersize = 6, label=self.plabels[i])
        else: 
            self.p[i], = self.axes.plot(numtime, table2.values,  MarkVar,label=self.plabels[i])

    def LastSelections(self):#set same selections as last plot

        last_selection_arg_tuples = [(self.table_ComboBox_1, self.xcol_ComboBox_1, self.ycol_ComboBox_1, 'custplot_table1', 'custplot_xcol1', 'custplot_ycol1', self.Table1Changed),
                                     (self.table_ComboBox_2, self.xcol_ComboBox_2, self.ycol_ComboBox_2, 'custplot_table2', 'custplot_xcol2', 'custplot_ycol2', self.Table2Changed),
                                     (self.table_ComboBox_3, self.xcol_ComboBox_3, self.ycol_ComboBox_3, 'custplot_table3', 'custplot_xcol3', 'custplot_ycol3', self.Table3Changed)]

        for table_combobox, xcol_combobox, ycol_combobox, custplot_table, custplot_xcol, custplot_ycol, table_changed in last_selection_arg_tuples:
            self.set_last_selection(table_combobox, xcol_combobox, ycol_combobox, custplot_table, custplot_xcol, custplot_ycol, table_changed)

        #table2
        self.tabWidget.setCurrentIndex(int(self.ms.settingsdict['custplot_tabwidget']))

        filter_tuples = [(self.Filter1_ComboBox_1, 'custplot_filter1_1', 1, 1),
                         (self.Filter2_ComboBox_1, 'custplot_filter2_1', 2, 1),
                         (self.Filter1_ComboBox_2, 'custplot_filter1_2', 1, 2),
                         (self.Filter2_ComboBox_2, 'custplot_filter2_2', 2, 2),
                         (self.Filter1_ComboBox_3, 'custplot_filter1_3', 1, 3),
                         (self.Filter2_ComboBox_3, 'custplot_filter2_3', 2, 3)]

        for filter_combobox, custplot_filter, filterno1, filterno2 in filter_tuples:
            self.set_filters(filter_combobox, custplot_filter, filterno1, filterno2)

        filter_selection_tuples = [(self.Filter1_QListWidget_1, 'custplot_filter1_1_selection'),
                                   (self.Filter2_QListWidget_1, 'custplot_filter2_1_selection'),
                                   (self.Filter1_QListWidget_2, 'custplot_filter1_2_selection'),
                                   (self.Filter2_QListWidget_2, 'custplot_filter2_2_selection'),
                                   (self.Filter1_QListWidget_3, 'custplot_filter1_3_selection'),
                                   (self.Filter2_QListWidget_3, 'custplot_filter2_3_selection')]

        for filter_qlistwidget, custplot_filter_selection in filter_selection_tuples:
            self.filter_selections(filter_qlistwidget, custplot_filter_selection)

        #plottype1
        searchindex = self.PlotType_comboBox_1.findText(self.ms.settingsdict['custplot_plottype1'])
        if searchindex >= 0:
            self.PlotType_comboBox_1.setCurrentIndex(searchindex)
        #plottype2
        searchindex = self.PlotType_comboBox_2.findText(self.ms.settingsdict['custplot_plottype2'])
        if searchindex >= 0:
            self.PlotType_comboBox_2.setCurrentIndex(searchindex)
        #plottype3
        searchindex = self.PlotType_comboBox_3.findText(self.ms.settingsdict['custplot_plottype3'])
        if searchindex >= 0:
            self.PlotType_comboBox_3.setCurrentIndex(searchindex)
        #max time step, titles, grid, legend
        self.spnmaxtstep.setValue(self.ms.settingsdict['custplot_maxtstep'])

        if self.ms.settingsdict['custplot_legend']==2:
            self.Legend_checkBox.setChecked(True)
        else:
            self.Legend_checkBox.setChecked(False)
        if self.ms.settingsdict['custplot_grid']==2:
            self.Grid_checkBox.setChecked(True)
        else:
            self.Grid_checkBox.setChecked(False)

    def set_last_selection(self, table_combobox, xcol_combobox, ycol_combobox, custplot_table, custplot_xcol, custplot_ycol, table_changed):
        searchindex = table_combobox.findText(self.ms.settingsdict[custplot_table])
        if searchindex >= 0:
            table_combobox.setCurrentIndex(searchindex)
            table_changed()
            searchindex = xcol_combobox.findText(self.ms.settingsdict[custplot_xcol])
            if searchindex >= 0:
                xcol_combobox.setCurrentIndex(searchindex)
            searchindex = ycol_combobox.findText(self.ms.settingsdict[custplot_ycol])
            if searchindex >= 0:
                ycol_combobox.setCurrentIndex(searchindex)

    def set_filters(self, filter_combobox, custplot_filter, filterno1, filterno2):
        #filtre1_1
        searchindex = filter_combobox.findText(self.ms.settingsdict[custplot_filter])
        if searchindex >= 0:
            filter_combobox.setCurrentIndex(searchindex)
            self.FilterChanged(filterno1, filterno2)

    def filter_selections(self, filter_qlistwidget, custplot_filter_selection):
        #filtre1_1_selection
        for index in xrange(filter_qlistwidget.count()):
            for item in self.ms.settingsdict[custplot_filter_selection]:
                if filter_qlistwidget.item(index).text()==item:#earlier str(item) but that caused probs for non-ascii
                     filter_qlistwidget.item(index).setSelected(True)
            
    def LoadTablesFromDB( self ):    # Open the SpatiaLite file to extract info about tables 
        self.table_ComboBox_1.clear()  
        self.table_ComboBox_2.clear()  
        self.table_ComboBox_3.clear()  
        for i in range (1,3):
            self.clearthings(i)
        myconnection = utils.dbconnection()
        if myconnection.connect2db() == True:
            # skapa en cursor
            curs = myconnection.conn.cursor()
            rs=curs.execute(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name in""" + midvatten_defs.SQLiteInternalTables() + r""")  and not (name in""" + midvatten_defs.sqlite_nonplot_tables() + r""") ORDER BY tbl_name""")  #SQL statement to get the relevant tables in the spatialite database
            #self.dbTables = {} 
            self.table_ComboBox_1.addItem('')
            self.table_ComboBox_2.addItem('')
            self.table_ComboBox_3.addItem('')
    
            for row in curs:
                self.table_ComboBox_1.addItem(row[0])
                self.table_ComboBox_2.addItem(row[0])
                self.table_ComboBox_3.addItem(row[0])
            
            rs.close()
            myconnection.closedb()        

    def LoadColumnsFromTable(self, table=''):
        """ This method returns a list with all the columns in the table"""
        if len(table)>0:            # Should not be needed since the function never should be called without existing table...
            myconnection = utils.dbconnection()
            if myconnection.connect2db() == True:
                # skapa en cursor
                curs = myconnection.conn.cursor()
                sql = r"""SELECT * FROM '"""
                sql += unicode(table)
                sql += """'"""     
                rs=curs.execute(sql)
                columns = {} 
                columns = [tuple[0] for tuple in curs.description]
                rs.close()
                myconnection.closedb()        
        else:
            #QMessageBox.information(None,"info","no table is loaded")    # DEBUGGING
            columns = {}
        return columns        # This method returns a list with all the columns in the table

    def clearthings(self,tabno=1):   #clear xcol,ycol,filter1,filter2
        xcolcombobox = 'xcol_ComboBox_' + str(tabno)
        ycolcombobox = 'ycol_ComboBox_' + str(tabno)
        filter1combobox = 'Filter1_ComboBox_' + str(tabno)
        filter2combobox = 'Filter2_ComboBox_' + str(tabno)
        filter1qlistwidget = 'Filter1_QListWidget_' + str(tabno)
        filter2qlistwidget = 'Filter2_QListWidget_' + str(tabno)
        getattr(self,xcolcombobox).clear()
        getattr(self,ycolcombobox).clear()
        getattr(self,filter1combobox).clear()
        getattr(self,filter2combobox).clear()
        getattr(self,filter1qlistwidget).clear()
        getattr(self,filter2qlistwidget).clear()

    def Table1Changed(self):     #This method is called whenever table1 is changed
        # First, update combobox with columns
        self.clearthings(1)
        #self.ms.settingsdict['custplot_table1'] = self.table_ComboBox_1.currentText()
        self.PopulateComboBox('xcol_ComboBox_1', self.table_ComboBox_1.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox_1', self.table_ComboBox_1.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox_1', self.table_ComboBox_1.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox_1', self.table_ComboBox_1.currentText())  # See GeneralNote

    def Table2Changed(self):     #This method is called whenever table2 is changed
        # First, update combobox with columns
        self.clearthings(2)
        #self.ms.settingsdict['custplot_table2'] = self.table_ComboBox_2.currentText()
        self.PopulateComboBox('xcol_ComboBox_2', self.table_ComboBox_2.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox_2', self.table_ComboBox_2.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox_2', self.table_ComboBox_2.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox_2', self.table_ComboBox_2.currentText())  # See GeneralNote

    def Table3Changed(self):     #This method is called whenever table3 is changed
        # First, update combobox with columns
        self.clearthings(3)
        #self.ms.settingsdict['custplot_table2'] = self.table_ComboBox_3.currentText()
        self.PopulateComboBox('xcol_ComboBox_3', self.table_ComboBox_3.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox_3', self.table_ComboBox_3.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox_3', self.table_ComboBox_3.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox_3', self.table_ComboBox_3.currentText())  # See GeneralNote

    def PopulateComboBox(self, comboboxname='', table=None):
        """This method fills comboboxes with columns for selected tool and table"""
        columns = self.LoadColumnsFromTable(table)    # Load all columns into a list 'columns'
        if len(columns)>0:    # Transfer information from list 'columns' to the combobox
            getattr(self, comboboxname).addItem('')
            for columnName in columns:
                getattr(self, comboboxname).addItem(columnName)  # getattr is to combine a function and a string to a combined function

    def FilterChanged(self, filterno, tabno):
        TableCombobox = 'table_ComboBox_' + str(tabno)
        FilterCombobox = 'Filter' + str(filterno) + '_ComboBox_' + str(tabno)
        FilterQListWidget = 'Filter' + str(filterno) + '_QListWidget_' + str(tabno)
        getattr(self,FilterQListWidget).clear()
        if not getattr(self,FilterCombobox).currentText()=='':
            self.PopulateFilterList(getattr(self,TableCombobox).currentText(),FilterQListWidget,getattr(self,FilterCombobox).currentText())
        
    def Filter1_1Changed(self):
        self.FilterChanged(1,1)
    
    def Filter2_1Changed(self):
        self.FilterChanged(2,1)

    def Filter1_2Changed(self):
        self.FilterChanged(1,2)
            
    def Filter2_2Changed(self):
        self.FilterChanged(2,2)

    def Filter1_3Changed(self):
        self.FilterChanged(1,3)
        
    def Filter2_3Changed(self):
        self.FilterChanged(2,3)
                        
    def PopulateFilterList(self, table, QListWidgetname='', filtercolumn=None):
        sql = "select distinct " + unicode(filtercolumn) + " from " + table + " order by " + unicode(filtercolumn)
        ConnectionOK, list_data=utils.sql_load_fr_db(sql)
        for post in list_data:
            item = QtGui.QListWidgetItem(unicode(post[0]))
            getattr(self, QListWidgetname).addItem(item)

    def refreshPlot( self ):
        #If the user has not pressed "draw" before, do nothing
        if not self.drawn:
            return None

        self.storesettings()    #all custom plot related settings are stored when plotting data (or pressing "redraw")
        datemin = self.spnMinX.dateTime().toPyDateTime()
        datemax = self.spnMaxX.dateTime().toPyDateTime()
        if datemin == datemax: #xaxis-limits
            pass
        else:
            self.axes.set_xlim(min(datemin, datemax),max(datemin, datemax))            
        if self.spnMinY.value() == self.spnMaxY.value(): #yaxis-limits
            pass
        else:
            self.axes.set_ylim(min(self.spnMaxY.value(), self.spnMinY.value()),max(self.spnMaxY.value(), self.spnMinY.value()))            
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))#yaxis-format
        self.axes.xaxis.set_major_formatter(self.xaxis_formatters[0])
        self.axes.xaxis.set_major_locator(self.xaxis_formatters[1])

        self.axes.grid(self.Grid_checkBox.isChecked() )#grid

        self.ms.settingsdict['custplot_title'] = self.axes.get_title()
        self.ms.settingsdict['custplot_xtitle'] = self.axes.get_xlabel()
        self.ms.settingsdict['custplot_ytitle'] = self.axes.get_ylabel()

        for label in self.axes.xaxis.get_ticklabels():
            label.set_fontsize(10)
            try:
                label.set_rotation(10)
            except:
                pass
        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(10)

        #The legend
        if self.Legend_checkBox.isChecked():
            if self.axes.legend_ is None:
                if (self.spnLegX.value() ==0 ) and (self.spnLegY.value() ==0):
                    leg = self.axes.legend(self.p, self.plabels)
                else:
                    leg = self.axes.legend(self.p, self.plabels, bbox_to_anchor=(self.spnLegX.value(),self.spnLegY.value()),loc=10)
            else:
                if (self.spnLegX.value() ==0 ) and (self.spnLegY.value() ==0):
                    leg = self.axes.legend()
                else:
                    leg = self.axes.legend(bbox_to_anchor=(self.spnLegX.value(),self.spnLegY.value()),loc=10)
            leg.draggable(state=True)
            frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor('1')    # set the frame face color to white
            frame.set_fill(False)    # set the frame face color to white
            for t in leg.get_texts():
                t.set_fontsize(10)    # the legend text fontsize
        else:
            self.axes.legend_ = None

        self.canvas.draw()
        plt.close(self.custplotfigure)#this closes reference to self.custplotfigure

    def storesettings(self):
        self.ms.settingsdict['custplot_table1'] = unicode(self.table_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_xcol1'] = unicode(self.xcol_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_ycol1'] = unicode(self.ycol_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_table2'] = unicode(self.table_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_xcol2'] = unicode(self.xcol_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_ycol2'] = unicode(self.ycol_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_table3'] = unicode(self.table_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_xcol3'] = unicode(self.xcol_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_ycol3'] = unicode(self.ycol_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter1_1']=unicode(self.Filter1_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_filter2_1']=unicode(self.Filter2_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_filter1_2']=unicode(self.Filter1_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_filter2_2']=unicode(self.Filter2_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_filter1_3']=unicode(self.Filter1_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter2_3']=unicode(self.Filter2_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter1_1_selection']=[]
        self.ms.settingsdict['custplot_filter2_1_selection']=[]
        self.ms.settingsdict['custplot_filter1_2_selection']=[]
        self.ms.settingsdict['custplot_filter2_2_selection']=[]
        self.ms.settingsdict['custplot_filter1_3_selection']=[]
        self.ms.settingsdict['custplot_filter2_3_selection']=[]
        for item in self.Filter1_QListWidget_1.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_1_selection'].append(unicode(item.text()))
        for item in self.Filter2_QListWidget_1.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_1_selection'].append(unicode(item.text()))
        for item in self.Filter1_QListWidget_2.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_2_selection'].append(unicode(item.text()))
        for item in self.Filter2_QListWidget_2.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_2_selection'].append(unicode(item.text()))
        for item in self.Filter1_QListWidget_3.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_3_selection'].append(unicode(item.text()))
        for item in self.Filter2_QListWidget_3.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_3_selection'].append(unicode(item.text()))
        self.ms.settingsdict['custplot_plottype1']=unicode(self.PlotType_comboBox_1.currentText())
        self.ms.settingsdict['custplot_plottype2']=unicode(self.PlotType_comboBox_2.currentText())
        self.ms.settingsdict['custplot_plottype3']=unicode(self.PlotType_comboBox_3.currentText())
        self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()
        self.ms.settingsdict['custplot_legend']=self.Legend_checkBox.checkState()
        self.ms.settingsdict['custplot_grid']=self.Grid_checkBox.checkState()
        self.ms.settingsdict['custplot_title'] = unicode(self.axes.get_title())
        self.ms.settingsdict['custplot_xtitle'] = unicode(self.axes.get_xlabel())
        self.ms.settingsdict['custplot_ytitle'] = unicode(self.axes.get_ylabel())
        self.ms.settingsdict['custplot_tabwidget'] = self.tabWidget.currentIndex()
        self.ms.save_settings()
