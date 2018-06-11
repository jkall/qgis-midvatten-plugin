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
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
import matplotlib.pyplot as plt
import os
import db_utils
from qgis.PyQt import QtGui, QtCore, uic, QtWidgets  # , QtSql
from qgis.PyQt.QtCore import QCoreApplication
from functools import partial  # only to get combobox signals to work
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import datestr2num

import numpy as np

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT    
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
import datetime
import matplotlib.ticker as tick

import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from definitions import midvatten_defs as defs
import qgis.PyQt

try:
    import pandas as pd
except:
    pandas_on = False
else:
    pandas_on = True

utils.MessagebarAndLog.info(log_msg=u"Python pandas: " + str(pandas_on))
customplot_ui_class =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..', 'ui', 'customplotdialog.ui'))[0]


class plotsqlitewindow(QtWidgets.QMainWindow, customplot_ui_class):
    def __init__(self, parent, msettings):#, parent as second arg?
        self.ms = msettings
        self.ms.loadSettings()
        QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi( self )#due to initialisation of Ui_MainWindow instance
        self.initUI()
        self.tables_columns = db_utils.tables_columns()
        self.LoadTablesFromDB(self.tables_columns)
        self.LastSelections()#fill comboboxes etc with last selected values
        #on close:
        #del self.axes.collections[:]#this should delete all plot objects related to axes and hence not intefere with following tsplots
        self.drawn = False
        self.used_format = None
        
    def initUI(self):
        self.table_ComboBox_1.clear()  
        self.table_ComboBox_2.clear()  
        self.table_ComboBox_3.clear()  
        for i in range(1,3):
            self.clearthings(i)
        # function partial due to problems with currentindexChanged and Combobox
        #self.table_ComboBox_1, QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.Table1Changed))#currentIndexChanged caused unnecessary signals when scrolling in combobox
        self.table_ComboBox_1.currentIndexChanged.connect( partial(self.Table1Changed))
        self.Filter1_ComboBox_1.currentIndexChanged.connect( partial(self.Filter1_1Changed))
        #self.Filter1_ComboBox_1.currentIndexChanged.connect( partial(self.FilterChanged(1,1)))
        self.Filter2_ComboBox_1.currentIndexChanged.connect( partial(self.Filter2_1Changed))
        self.table_ComboBox_2.currentIndexChanged.connect( partial(self.Table2Changed))
        self.Filter1_ComboBox_2.currentIndexChanged.connect( partial(self.Filter1_2Changed))
        self.Filter2_ComboBox_2.currentIndexChanged.connect( partial(self.Filter2_2Changed))
        self.table_ComboBox_3.currentIndexChanged.connect( partial(self.Table3Changed))
        self.Filter1_ComboBox_3.currentIndexChanged.connect( partial(self.Filter1_3Changed))
        self.Filter2_ComboBox_3.currentIndexChanged.connect( partial(self.Filter2_3Changed))
        self.plot_width.editingFinished.connect( partial(self.change_plot_size))
        self.plot_height.editingFinished.connect( partial(self.change_plot_size))
        self.plot_settings_1.clicked.connect( partial(self.set_groupbox_children_visibility, self.plot_settings_1))
        self.plot_settings_2.clicked.connect( partial(self.set_groupbox_children_visibility, self.plot_settings_2))
        self.plot_settings_3.clicked.connect( partial(self.set_groupbox_children_visibility, self.plot_settings_3))
        self.chart_settings.clicked.connect( partial(self.set_groupbox_children_visibility, self.chart_settings))
        self.template_wid.clicked.connect(partial(self.set_groupbox_children_visibility, self.template_wid))

        self.select_button_t1f1.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_1, self.Filter1_ComboBox_1))
        self.select_button_t1f2.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_1, self.Filter2_ComboBox_1))
        self.select_button_t2f1.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_2, self.Filter1_ComboBox_2))
        self.select_button_t2f2.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_2, self.Filter2_ComboBox_2))
        self.select_button_t3f1.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_3, self.Filter1_ComboBox_3))
        self.select_button_t3f2.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_3, self.Filter2_ComboBox_3))

        self.save_to_eps_button.clicked.connect( self.save_to_eps)

        self.listfilter_1_1.editingFinished.connect( partial(self.filter_filterlist, self.Filter1_QListWidget_1, self.listfilter_1_1))
        self.listfilter_2_1.editingFinished.connect( partial(self.filter_filterlist, self.Filter2_QListWidget_1, self.listfilter_2_1))
        self.listfilter_1_2.editingFinished.connect( partial(self.filter_filterlist, self.Filter1_QListWidget_2, self.listfilter_1_2))
        self.listfilter_2_2.editingFinished.connect( partial(self.filter_filterlist, self.Filter2_QListWidget_2, self.listfilter_2_2))
        self.listfilter_1_3.editingFinished.connect( partial(self.filter_filterlist, self.Filter1_QListWidget_3, self.listfilter_1_3))
        self.listfilter_2_3.editingFinished.connect( partial(self.filter_filterlist, self.Filter2_QListWidget_3, self.listfilter_2_3))
        self.filtersettings1.clicked.connect( partial(self.set_groupbox_children_visibility, self.filtersettings1))
        self.filtersettings2.clicked.connect( partial(self.set_groupbox_children_visibility, self.filtersettings2))
        self.filtersettings3.clicked.connect( partial(self.set_groupbox_children_visibility, self.filtersettings3))

        self.PlotChart_QPushButton.clicked.connect(self.drawPlot_all)
        self.Redraw_pushButton.clicked.connect( self.refreshPlot )

        self.custplotfigure = plt.figure()

        self.axes = self.custplotfigure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.custplotfigure )

        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )

        #Validator for QlineEdit that should contain only floats, any number of decimals with either point(.) or comma(,) as a decimal separater
        regexp = QtCore.QRegExp('[+-]?\\d*[\\.,]?\\d+') 
        validator = QtGui.QRegExpValidator(regexp)
        self.LineEditFactor1.setValidator(validator)
        self.LineEditFactor2.setValidator(validator)
        self.LineEditFactor3.setValidator(validator)
        self.LineEditOffset1.setValidator(validator)
        self.LineEditOffset2.setValidator(validator)
        self.LineEditOffset3.setValidator(validator)

        self.pandas_calc_1 = None
        self.pandas_calc_2 = None
        self.pandas_calc_3 = None
        if pandas_on:
            self.pandas_calc_1 = PandasCalculations(self.gridLayout_16)
            self.pandas_calc_2 = PandasCalculations(self.gridLayout_14)
            self.pandas_calc_3 = PandasCalculations(self.gridLayout_19)

        #self.custplotfigure.tight_layout()

        self.templates = utils.PlotTemplates(self,
                                             self.template_list,
                                             self.edit_button,
                                             self.load_button,
                                             self.save_as_button,
                                             self.import_button,
                                             self.remove_button,
                                             os.path.join(os.path.split(os.path.dirname(__file__))[0], 'definitions',
                                                          'custplot_templates'),
                                             'custplot_templates',
                                             'custplot_loaded_template',
                                             defs.custplot_default_template(),
                                             msettings=self.ms)

        self.chart_settings.setChecked(False)
        self.template_wid.setChecked(False)
        self.filtersettings1.setChecked(False)
        self.filtersettings2.setChecked(False)
        self.filtersettings3.setChecked(False)
        self.set_groupbox_children_visibility(self.chart_settings)
        self.set_groupbox_children_visibility(self.filtersettings1)
        self.set_groupbox_children_visibility(self.filtersettings2)
        self.set_groupbox_children_visibility(self.filtersettings3)
        for plot_item_settings in [self.plot_settings_1, self.plot_settings_2, self.plot_settings_3]:
            plot_item_settings.setChecked(False)
            self.set_groupbox_children_visibility(plot_item_settings)

        self.set_groupbox_children_visibility(self.template_wid)

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

    def change_plot_size(self):
        width = self.plot_width.text()
        height = self.plot_height.text()
        self.templates.loaded_template['plot_width'] = width
        self.templates.loaded_template['plot_height'] = height

        try:
            width = float(width)
        except ValueError:
            #self.layoutplot.setHorizontalPolicy(PyQt4.QtWidgets.QSizePolicy.Extended)
            #self.widgetPlot.sizePolicy().setHorizontalPolicy(PyQt4.QtWidgets.QSizePolicy.Expanding)
            self.widgetPlot.setMinimumWidth(100)
            self.widgetPlot.setMaximumWidth(16777215)
            #self.widgetPlot.adjustSize()
        else:
            #self.widgetPlot.setMinimum
            #self.widgetPlot.setFixedWidth(width)
            self.widgetPlot.setMinimumWidth(width)
            self.widgetPlot.setMaximumWidth(width)

        try:
            height = float(height)
        except ValueError:
            #self.widgetPlot.sizePolicy().setVerticalPolicy(PyQt4.QtWidgets.QSizePolicy.Expanding)
            self.widgetPlot.setMinimumHeight(100)
            self.widgetPlot.setMaximumHeight(16777215)
        else:
            self.widgetPlot.setMinimumHeight(height)
            self.widgetPlot.setMaximumHeight(height)

    @utils.general_exception_handler
    def drawPlot_all(self, *args):
        """

        :param args: Needed when using general_exception_handler for some reason?!?
        :return:
        """

        self.used_format = None

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))#show the user this may take a long time...

        self.axes.clear()
        self.axes.legend_ = None
        My_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array

        dbconnection = db_utils.DbConnectionManager()

        i = 0
        nop=0# nop=number of plots
        self.p=[]
        self.plabels=[]
                
        nop, i = self.drawPlot(dbconnection, nop, i, My_format, self.table_ComboBox_1, self.xcol_ComboBox_1, self.ycol_ComboBox_1, self.Filter1_ComboBox_1, self.Filter1_QListWidget_1, self.Filter2_ComboBox_1, self.Filter2_QListWidget_1, self.PlotType_comboBox_1, self.pandas_calc_1, self.checkBox_remove_mean1, self.LineEditFactor1, self.LineEditOffset1)
        nop, i = self.drawPlot(dbconnection, nop, i, My_format, self.table_ComboBox_2, self.xcol_ComboBox_2, self.ycol_ComboBox_2, self.Filter1_ComboBox_2, self.Filter1_QListWidget_2, self.Filter2_ComboBox_2, self.Filter2_QListWidget_2, self.PlotType_comboBox_2, self.pandas_calc_2, self.checkBox_remove_mean2, self.LineEditFactor2, self.LineEditOffset2)
        nop, i = self.drawPlot(dbconnection, nop, i, My_format, self.table_ComboBox_3, self.xcol_ComboBox_3, self.ycol_ComboBox_3, self.Filter1_ComboBox_3, self.Filter1_QListWidget_3, self.Filter2_ComboBox_3, self.Filter2_QListWidget_3, self.PlotType_comboBox_3, self.pandas_calc_3, self.checkBox_remove_mean3, self.LineEditFactor3, self.LineEditOffset3)
        if not self.p:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('CustomPlot', 'Plot not updated.')))
            return None
        self.xaxis_formatters = (self.axes.xaxis.get_major_formatter(), self.axes.xaxis.get_major_locator())

        title = self.templates.loaded_template['Axes_set_title']
        if 'label' in title:
            self.axes.set_title(**title)
        xlabel = self.templates.loaded_template['Axes_set_xlabel']
        if 'xlabel' in xlabel:
            self.axes.set_xlabel(**xlabel)
        ylabel = self.templates.loaded_template['Axes_set_ylabel']
        if 'ylabel' in ylabel:
            self.axes.set_ylabel(**ylabel)
    
        self.drawn = True
    
        self.refreshPlot()
    
        QtWidgets.QApplication.restoreOverrideCursor()  # now this long process is done and the cursor is back as normal

    def drawPlot(self, dbconnection, nop, i, My_format, table_ComboBox, xcol_ComboBox, ycol_ComboBox, Filter1_ComboBox, Filter1_QListWidget, Filter2_ComboBox, Filter2_QListWidget, PlotType_comboBox, pandas_calc, checkBox_remove_mean, LineEditFactor, LineEditOffset):
                
        if not (table_ComboBox.currentText() == '' or table_ComboBox.currentText()==' ') and not (xcol_ComboBox.currentText()== '' or xcol_ComboBox.currentText()==' ') and not (ycol_ComboBox.currentText()== '' or ycol_ComboBox.currentText()==' '): #if anything is to be plotted from tab 1
            self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()   # if user selected a time step bigger than zero than thre may be discontinuous plots
            plottable1='y'
            filter1 = str(Filter1_ComboBox.currentText())
            filter1list = []
            filter2list = []
            filter1list = Filter1_QListWidget.selectedItems()
            filter2 = str(Filter2_ComboBox.currentText())
            filter2list= Filter2_QListWidget.selectedItems()
            nop = max(len(filter1list),1)*max(len(filter2list),1)
            #self.p= [None]*nop#list for plot objects
            self.p.extend([None]*nop)#list for plot objects
            self.plabels.extend([None]*nop)# List for plot labels
            try:
                factor = float(LineEditFactor.text().replace(',','.'))
            except ValueError:
                factor = 1.0
            try:
                offset = float(LineEditOffset.text().replace(',','.'))
            except ValueError:
                offset = 0.0

            remove_mean = checkBox_remove_mean.isChecked()

            _sql = r"""SELECT %s, %s FROM %s """% (str(xcol_ComboBox.currentText()), str(ycol_ComboBox.currentText()), str(table_ComboBox.currentText()))
            _sql += r"""WHERE %s """ % db_utils.test_not_null_and_not_empty_string(str(table_ComboBox.currentText()), str(xcol_ComboBox.currentText()), dbconnection)
            _sql += r"""AND %s """ % db_utils.test_not_null_and_not_empty_string(str(table_ComboBox.currentText()), str(ycol_ComboBox.currentText()), dbconnection)

            while i < len(self.p):
                #Both filters empty
                if (not filter1.strip() or not filter1list) and (not filter2.strip() or not filter2list):
                    sql = _sql + r""" ORDER BY %s"""%str(xcol_ComboBox.currentText())
                    recs = dbconnection.execute_and_fetchall(sql)
                    label = str(ycol_ComboBox.currentText())+""", """+str(table_ComboBox.currentText())
                    if not recs:
                        i += 1
                        continue
                    self.plabels[i] = label
                    self.createsingleplotobject(recs, i, My_format, PlotType_comboBox.currentText(), factor, offset, remove_mean, pandas_calc)
                    i += 1
                #Both filters in use
                elif all((filter1.strip(), filter1list, filter2.strip(), filter2list)):
                    for item1 in filter1list:
                        for item2 in filter2list:
                            sql = _sql + r""" AND %s = '%s' AND %s = '%s' ORDER BY %s"""%(filter1, str(item1.text()), filter2, str(item2.text()), str(xcol_ComboBox.currentText()))
                            recs = dbconnection.execute_and_fetchall(sql)
                            label = str(item1.text()) + """, """ + str(item2.text())
                            if not recs:
                                utils.MessagebarAndLog.info(log_msg=ru(
                                    QCoreApplication.translate('CustomPlot', 'No plottable data for %s.')) % label)
                                i += 1
                                continue
                            self.plabels[i] = label
                            self.createsingleplotobject(recs, i, My_format, PlotType_comboBox.currentText(), factor, offset, remove_mean, pandas_calc)
                            i += 1
                #One filter in use
                else:
                    for filter, filterlist in [(filter1, filter1list), (filter2, filter2list)]:
                        if not filter.strip() or not filterlist:
                            continue
                        else:
                            for item in filterlist:
                                sql = _sql + r""" AND %s = '%s' ORDER BY %s"""%(filter, str(item.text()), str(xcol_ComboBox.currentText()))
                                recs = dbconnection.execute_and_fetchall(sql)
                                label = str(item.text())
                                if not recs:
                                    utils.MessagebarAndLog.warning(log_msg=ru(
                                        QCoreApplication.translate('CustomPlot', 'No plottable data for %s.')) % label)
                                    i += 1
                                    continue
                                self.plabels[i] = label
                                self.createsingleplotobject(recs, i, My_format, PlotType_comboBox.currentText(), factor, offset, remove_mean, pandas_calc)
                                i += 1


        return nop, i

    def createsingleplotobject(self,recs,i,My_format,plottype='line', factor=1.0, offset=0.0, remove_mean=False, pandas_calc=None):

        #Transform data to a numpy.recarray
        try:
            table = np.array(recs, dtype=My_format)  #NDARRAY
            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects
            FlagTimeXY = 'time'
            myTimestring = list(table2.date_time)
            numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        except Exception as e:
            utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate(u'plotsqlitewindow', u'Plotting date_time failed, msg: %s'))%str(e))
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'plotsqlitewindow', u"Customplot, transforming to recarray with date_time as x-axis failed, msg: %s"))%ru(str(e)))
            #recs = [x for x in recs if all(x)]

            table = np.array(recs, dtype=[('numx', float), ('values', float)])  #NDARRAY #define a format for xy-plot (to use if not datetime on x-axis)

            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects

            FlagTimeXY = 'XY'
            numtime = list(table2.numx)

        if self.used_format is None:
            self.used_format = FlagTimeXY
        else:
            if self.used_format != FlagTimeXY:
                raise utils.UsageError(ru(QCoreApplication.translate(u'CustomPlot', u"Plotting both xy and time plot at the same time doesn't work! Check the x-y axix settings in all tabs!")))

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

        if FlagTimeXY == "time" and plottype == "frequency":
            table2.values[:] = self.calc_frequency(table2)[:]

        if remove_mean:
            table2.values[:] = utils.remove_mean_from_nparray(table2.values)[:]

        if any([factor != 1 and factor, offset,]):
            table2.values[:] = utils.scale_nparray(table2.values, factor, offset)[:]

        if pandas_calc and FlagTimeXY == "time":
            if pandas_calc.use_pandas():
                df = pd.DataFrame.from_records(table2, columns=[u'values'], exclude=[u'date_time'])
                df.set_index(pd.DatetimeIndex(table2.date_time, name=u'date_time'), inplace=True)
                df.columns = [u'values']

                df = pandas_calc.calculate(df)
                if df is not None:
                    try:
                        table = np.array(list(zip(df.index, df[u'values'])), dtype=My_format)
                    except TypeError:
                        utils.MessagebarAndLog.info(log_msg=str(df))
                        raise
                    table2 = table.view(np.recarray)  # RECARRAY transform the 2 cols into callable objects
                    numtime = table2.date_time
                else:
                    utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'plotsqlitewindow', u"Pandas calculate failed.")))

        color_list = [_num[0] for _num in np.random.rand(3,1).tolist()]

        plot_date_settings = self.templates.loaded_template['dates_Axes_plot_date']['DEFAULT']
        plot_settings = self.templates.loaded_template['xyplot_Axes_plot']['DEFAULT']

        if FlagTimeXY == "time" and plottype == "step-pre":
            self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',c=color_list,label=self.plabels[i], **plot_date_settings)# 'steps-pre' best for precipitation and flowmeters, optional types are 'steps', 'steps-mid', 'steps-post'
        elif FlagTimeXY == "time" and plottype == "step-post":
            self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',c=color_list,label=self.plabels[i], **plot_date_settings)
        elif FlagTimeXY == "time" and plottype == "line and cross":
            self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,markersize = 6, label=self.plabels[i], **plot_date_settings)
        elif FlagTimeXY == "time" and plottype == "frequency":
            try:
                self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,markersize = 6, label='frequency '+str(self.plabels[i]), **plot_date_settings)
                self.plabels[i]='frequency '+str(self.plabels[i])
            except:
                self.p[i], = self.axes.plot_date(np.array([]),np.array([]),  MarkVar,markersize = 6, label='frequency '+str(self.plabels[i]))
                self.plabels[i]='frequency '+str(self.plabels[i])
        elif FlagTimeXY == "time":
            self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,label=self.plabels[i], **plot_date_settings)
        elif FlagTimeXY == "XY" and plottype == "step-pre":
            self.p[i], = self.axes.plot(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',c=color_list,label=self.plabels[i], **plot_settings)
        elif FlagTimeXY == "XY" and plottype == "step-post":
            self.p[i], = self.axes.plot(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',c=color_list,label=self.plabels[i], **plot_settings)
        elif FlagTimeXY == "XY" and plottype == "line and cross":
            self.p[i], = self.axes.plot(numtime, table2.values,  MarkVar,markersize = 6, label=self.plabels[i], **plot_settings)
        else: 
            self.p[i], = self.axes.plot(numtime, table2.values,  MarkVar,label=self.plabels[i], **plot_settings)

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

        if self.templates.loaded_template['grid_Axes_grid']:
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
        for index in range(filter_qlistwidget.count()):
            for item in self.ms.settingsdict[custplot_filter_selection]:
                if filter_qlistwidget.item(index).text()==item:#earlier str(item) but that caused probs for non-ascii
                     filter_qlistwidget.item(index).setSelected(True)

    def filter_filterlist(self, filterlist, lineedit):
        words = lineedit.text().split(u';')

        listcount = filterlist.count()
        if words:
            [filterlist.item(idx).setHidden(False) if any([word.lower() in filterlist.item(idx).text().lower() for word in words]) else filterlist.item(idx).setHidden(True) for idx in range(listcount)]
        else:
            [filterlist.item(idx).setHidden(False) for idx in range(listcount)]

    def LoadTablesFromDB( self, tables_columns ):    # Open the SpatiaLite file to extract info about tables
        tables = sorted([table for table in list(tables_columns.keys()) if table not in db_utils.nonplot_tables(as_tuple=True) and not table.startswith(u'zz_')])
        for i, table_combobox in enumerate([self.table_ComboBox_1, self.table_ComboBox_2, self.table_ComboBox_3], 1):
            table_combobox.clear()
            self.clearthings(i)
            table_combobox.addItem('')
            try:
                table_combobox.addItems(tables)
            except:
                for table in tables:
                    table_combobox.addItem(table)

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
        columns = self.tables_columns.get(table, [])    # Load all columns into a list 'columnsä
        if len(columns)>0:    # Transfer information from list 'columns' to the combobox
            getattr(self, comboboxname).addItem('')
            try:
                getattr(self, comboboxname).addItems(columns)
            except:
                for column in columns:
                    getattr(self, comboboxname).addItem(column)

    def FilterChanged(self, filterno, tabno):
        TableCombobox = 'table_ComboBox_' + str(tabno)
        FilterCombobox = 'Filter' + str(filterno) + '_ComboBox_' + str(tabno)
        FilterQListWidget = 'Filter' + str(filterno) + '_QListWidget_' + str(tabno)

        other_filterno = {2:1, 1:2}[filterno]
        other_FilterCombobox = 'Filter' + str(other_filterno) + '_ComboBox_' + str(tabno)
        other_FilterQListWidget = 'Filter' + str(other_filterno) + '_QListWidget_' + str(tabno)

        dependent_filtering_box = getattr(self, 'dependent_filtering' + str(tabno), None)

        getattr(self,FilterQListWidget).clear()
        if not getattr(self,FilterCombobox).currentText()=='':
            self.PopulateFilterList(getattr(self,TableCombobox).currentText(), FilterQListWidget,
                                    getattr(self,FilterCombobox).currentText(),
                                    other_FilterQListWidget,
                                    getattr(self,other_FilterCombobox).currentText(),
                                    dependent_filtering_box)
        
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
                        
    def PopulateFilterList(self, table, QListWidgetname='', filtercolumn=None, other_QListWidget=None,
                           other_filtercolumn=None, dependent_filtering_box=None):

        sql = "select distinct " + str(filtercolumn) + " from " + table + " order by " + str(filtercolumn)

        if dependent_filtering_box is not None:
            dependent_filtering = dependent_filtering_box.isChecked()
        else:
            dependent_filtering = False


        if other_QListWidget is not None and other_filtercolumn and dependent_filtering:
            other_QListWidget_wid = getattr(self, other_QListWidget)
            selected = ru([item.text() for item in other_QListWidget_wid.selectedItems() if item.text()], keep_containers=True)
            if selected:
                sql = u"SELECT DISTINCT {} FROM {} WHERE {} IN ({}) ORDER BY {}".format(
                                                                                str(filtercolumn),
                                                                                table,
                                                                                other_filtercolumn,
                                                                                u', '.join([u"'{}'".format(item)
                                                                                            for item in selected]),
                                                                                str(filtercolumn),)

        ConnectionOK, list_data= db_utils.sql_load_fr_db(sql)
        for post in list_data:
            item = QtWidgets.QListWidgetItem(str(post[0]))
            getattr(self, QListWidgetname).addItem(item)

    @utils.general_exception_handler
    def refreshPlot( self, *args):
        """

        :param args: Needed when using general_exception_handler for some reason?!?
        :return:
        """
        #If the user has not pressed "draw" before, do nothing
        if not self.drawn:
            return None

        self.storesettings()    #all custom plot related settings are stored when plotting data (or pressing "redraw")

        if self.used_format == 'time':
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

        if self.Grid_checkBox.isChecked():
            self.templates.loaded_template['grid_Axes_grid']['b'] = True
        else:
            self.templates.loaded_template['grid_Axes_grid']['b'] = False

        self.axes.grid(**self.templates.loaded_template['grid_Axes_grid'])#grid

        self.templates.loaded_template['Axes_set_title']['label'] = self.axes.get_title()
        self.templates.loaded_template['Axes_set_xlabel']['xlabel'] = self.axes.get_xlabel()
        self.templates.loaded_template['Axes_set_ylabel']['ylabel'] = self.axes.get_ylabel()

        for tick_params in [self.templates.loaded_template.get('Axes_tick_param', None),
                            self.templates.loaded_template.get('x_Axes_tick_param', None),
                            self.templates.loaded_template.get('y_Axes_tick_param', None)]:
            if tick_params is not None and tick_params:
                try:
                    self.axes.tick_params(**tick_params)
                except ValueError:
                    tp = {k: v for k, v in tick_params.items() if k != 'labelrotation'}
                    self.axes.tick_params(**tp)

                    if 'labelrotation' in tick_params:
                        if tp['axis'] in ('both', 'x'):
                            for label in self.axes.xaxis.get_ticklabels():
                                label.set_rotation(tick_params['labelrotation'])
                        if tp['axis'] in ('both', 'y'):
                            for label in self.axes.yaxis.get_ticklabels():
                                label.set_rotation(tick_params['labelrotation'])

        #The legend
        if self.Legend_checkBox.isChecked():
            leg_settings = self.templates.loaded_template.get('legend_Axes_legend', None)
            if leg_settings is not None:
                leg = self.axes.legend(self.p, self.plabels, **leg_settings)
            else:
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

            frame.set_facecolor(self.templates.loaded_template['legend_Frame_set_facecolor'])    # set the frame face color to white
            frame.set_fill(self.templates.loaded_template['legend_Frame_set_fill'])    # set the frame face color to white
            for t in leg.get_texts():
                t.set_fontsize(float(self.templates.loaded_template['legend_Text_set_fontsize']))
        else:
            self.axes.legend_ = None

        if self.templates.loaded_template['Figure_subplots_adjust']:
            self.custplotfigure.subplots_adjust(**self.templates.loaded_template['Figure_subplots_adjust'])

        w = self.templates.loaded_template.get('plot_width', None)
        if w is not None:
            self.plot_width.setText(str(w))

        h = self.templates.loaded_template.get('plot_height', None)
        if h is not None:
            self.plot_height.setText(str(h))

        self.change_plot_size()

        self.canvas.draw()
        #plt.close(self.custplotfigure)#this closes reference to self.custplotfigure

    def storesettings(self):
        self.ms.settingsdict['custplot_table1'] = str(self.table_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_xcol1'] = str(self.xcol_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_ycol1'] = str(self.ycol_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_table2'] = str(self.table_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_xcol2'] = str(self.xcol_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_ycol2'] = str(self.ycol_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_table3'] = str(self.table_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_xcol3'] = str(self.xcol_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_ycol3'] = str(self.ycol_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter1_1']=str(self.Filter1_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_filter2_1']=str(self.Filter2_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_filter1_2']=str(self.Filter1_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_filter2_2']=str(self.Filter2_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_filter1_3']=str(self.Filter1_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter2_3']=str(self.Filter2_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter1_1_selection']=[]
        self.ms.settingsdict['custplot_filter2_1_selection']=[]
        self.ms.settingsdict['custplot_filter1_2_selection']=[]
        self.ms.settingsdict['custplot_filter2_2_selection']=[]
        self.ms.settingsdict['custplot_filter1_3_selection']=[]
        self.ms.settingsdict['custplot_filter2_3_selection']=[]
        for item in self.Filter1_QListWidget_1.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_1_selection'].append(str(item.text()))
        for item in self.Filter2_QListWidget_1.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_1_selection'].append(str(item.text()))
        for item in self.Filter1_QListWidget_2.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_2_selection'].append(str(item.text()))
        for item in self.Filter2_QListWidget_2.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_2_selection'].append(str(item.text()))
        for item in self.Filter1_QListWidget_3.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_3_selection'].append(str(item.text()))
        for item in self.Filter2_QListWidget_3.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_3_selection'].append(str(item.text()))
        self.ms.settingsdict['custplot_plottype1']=str(self.PlotType_comboBox_1.currentText())
        self.ms.settingsdict['custplot_plottype2']=str(self.PlotType_comboBox_2.currentText())
        self.ms.settingsdict['custplot_plottype3']=str(self.PlotType_comboBox_3.currentText())
        self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()
        self.ms.settingsdict['custplot_legend']=self.Legend_checkBox.checkState()
        #self.ms.settingsdict['custplot_grid']=self.Grid_checkBox.checkState()
        #self.ms.settingsdict['custplot_title'] = unicode(self.axes.get_title())
        #self.ms.settingsdict['custplot_xtitle'] = unicode(self.axes.get_xlabel())
        #self.ms.settingsdict['custplot_ytitle'] = unicode(self.axes.get_ylabel())
        self.ms.settingsdict['custplot_tabwidget'] = self.tabWidget.currentIndex()
        self.ms.save_settings()

        utils.save_stored_settings(self.ms, self.templates.loaded_template, 'custplot_loaded_template')
        self.ms.save_settings('custplot_templates')

    def set_groupbox_children_visibility(self, groupbox_widget):
        children = groupbox_widget.findChildren(qgis.PyQt.QtWidgets.QWidget)
        for child in children:
            child.setVisible(groupbox_widget.isChecked())

    def select_in_filterlist_from_selection(self, filter_listwidget, filter_combobox):
        current_column = ru(filter_combobox.currentText())
        if not current_column:
            return
        selected_values = utils.getselectedobjectnames(column_name=current_column)
        [filter_listwidget.item(nr).setSelected(True) for nr in range(filter_listwidget.count()) if ru(filter_listwidget.item(nr).text()) in selected_values]

    def save_to_eps(self):
        filename = qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName(parent=None, caption=ru(
            QCoreApplication.translate(u'CustomPlot', u'Choose a file name, extension sets format')), directory='')
        if not filename:
            return
        name, ext = os.path.splitext(filename)
        self.custplotfigure.savefig(filename, format=ext.lstrip(u'.'), dpi=float(self.figure_dpi.text()))


class PandasCalculations(object):
    def __init__(self, gridlayout):

        self.widget = qgis.PyQt.QtWidgets.QWidget()

        #General settings
        self.rule_label = qgis.PyQt.QtWidgets.QLabel(u'Resample rule')
        self.rule = qgis.PyQt.QtWidgets.QLineEdit()
        for wid in [self.rule_label, self.rule]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'Steplength for resampling, ex:\n'
                           u'"10S" = 10 seconds\n'
                           u'"20T" = 20 minutes\n'
                           u'"1h" = 1 hour\n'
                           u'"24h" = 24 hours\n'
                           u'(D = calendar day, M = month end, MS = month start, W = weekly, AS = year start, A = year end, ...)\n'
                           u'No resampling if field is empty\n'
                           u'See pandas pandas.DataFrame.resample documentation for more info.')))

        self.base_label = qgis.PyQt.QtWidgets.QLabel(u'Resample base')
        self.base = qgis.PyQt.QtWidgets.QLineEdit()
        for wid in [self.base_label, self.base]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'The hour to start each timestep when rule "evenly subdivide 1 day" (for example Rule = 24h)\n'
                           u'Ex: 7 (= 07:00). Default is 0 (00:00)\n'
                           u'See pandas pandas.DataFrame.resample documentation for more info:\n'
                           u'For frequencies that evenly subdivide 1 day, the "origin" of the aggregated intervals.\n'
                           u'For example, for "5min" frequency, base could range from 0 through 4. Defaults to 0.')))

        self.how_label = qgis.PyQt.QtWidgets.QLabel(u'Resample how')
        self.how = qgis.PyQt.QtWidgets.QLineEdit()
        for wid in [self.how_label, self.how]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'How to make the resample, ex. "mean" (default), "first", "last", "sum".\n'
                           u'See pandas pandas.DataFrame.resample documentation for more info\n'
                           u'(though "how" is not explained a lot)')))

        #Moving average:
        self.window_label = qgis.PyQt.QtWidgets.QLabel(u'Rolling mean window')
        self.window = qgis.PyQt.QtWidgets.QLineEdit(u'')
        self.center_label = qgis.PyQt.QtWidgets.QLabel(u'Rolling mean center')
        self.center = qgis.PyQt.QtWidgets.QLineEdit(u'')
        for wid in [self.window_label, self.window]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'The number of timesteps in each moving average (rolling mean) mean\n'
                           u'The result is stored at the center timestep of each mean.\n'
                           u'See Pandas pandas.rolling_mean documentation for more info.\n'
                           u'No rolling mean if field is empty.')))

        for wid in [self.center_label, self.center]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'1/True (default) to store the rolling mean at the center timestep.\n'
                           u'0/False to store the rolling mean at the last timestep.\n'
                           u'See Pandas pandas.rolling_mean documentation for more info.\n'
                           u'center=True if field is empty.')))


        for lineedit in [self.rule, self.base, self.how, self.window, self.center]:
            #lineedit.sizeHint()setFixedWidth(122)
            lineedit.sizePolicy().setHorizontalPolicy(qgis.PyQt.QtWidgets.QSizePolicy.Preferred)

        maximumwidth = 0
        for label in [self.rule_label, self.base_label, self.how_label, self.window_label, self.center_label]:
            testlabel = qgis.PyQt.QtWidgets.QLabel()
            testlabel.setText(label.text())
            maximumwidth = max(maximumwidth, testlabel.sizeHint().width())
        testlabel = None
        for label in [self.rule_label, self.base_label, self.how_label, self.window_label, self.center_label]:
            label.setFixedWidth(maximumwidth)
            #label.setMinimumWidth(maximumwidth)
            label.sizePolicy().setHorizontalPolicy(qgis.PyQt.QtWidgets.QSizePolicy.Fixed)

        hline = horizontal_line()
        hline.sizePolicy().setHorizontalPolicy(qgis.PyQt.QtWidgets.QSizePolicy.Fixed)
        gridlayout.addWidget(hline)
        for col1, col2 in [(self.rule_label, self.rule),
                           (self.base_label, self.base),
                           (self.how_label, self.how),
                           (self.window_label, self.window),
                           (self.center_label, self.center)]:
            current_row = gridlayout.rowCount()

            try:
                col1.setMaximumHeight(27)
                col2.setMaximumHeight(27)
            except:
                pass

            gridlayout.addWidget(col1, current_row, 0)
            gridlayout.addWidget(col2, current_row, 1)

    def use_pandas(self):
        if self.rule.text() or self.window.text():
            return True
        else:
            return False

    def calculate(self, df):
        #Resample
        rule = self.rule.text()
        base = self.base.text() if self.base.text() else 0
        how = self.how.text() if self.how.text() else u'mean'
        if rule:
            try:
                base = int(base)
            except ValueError:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'PandasCalculations', u'Resample base must be an integer')))
            else:
                # new api for pandas >=0.18
                try:
                    df = getattr(df.resample(rule,base=int(base)),how)()
                # old pandas
                except:
                    df = df.resample(rule, how=how, base=int(base))

        #Rolling mean
        window = self.window.text()
        if window:
            try:
                window = int(window)
            except ValueError:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'PandasCalculations', u'Rolling mean window must be an integer')))
            else:
                if self.center.text() in (u'0', u'False'):
                    center=False
                else:
                    center=True
                df = pd.rolling_mean(df, window=window, center=center)
        return df


def horizontal_line():
    line = qgis.PyQt.QtWidgets.QFrame()
    line.setGeometry(qgis.PyQt.QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(qgis.PyQt.QtWidgets.QFrame.HLine)
    line.setFrameShadow(qgis.PyQt.QtWidgets.QFrame.Sunken)
    return line
