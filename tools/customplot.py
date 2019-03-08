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
import matplotlib as mpl
import os
import db_utils
from qgis.PyQt import QtGui, QtCore, uic, QtWidgets  # , QtSql
from qgis.PyQt.QtCore import QCoreApplication
from functools import partial  # only to get combobox signals to work
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import datestr2num

import numpy as np

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
except:
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg
import datetime
import matplotlib.ticker as tick

from qgis.PyQt.QtWidgets import QApplication
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

utils.MessagebarAndLog.info(log_msg="Python pandas: " + str(pandas_on))
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
        self.matplotlib_style_sheet_reference.setText("""<a href="https://matplotlib.org/gallery/style_sheets/style_sheets_reference.html">Matplotlib style sheet reference</a>""")
        self.matplotlib_style_sheet_reference.setOpenExternalLinks(True)

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
        self.plot_settings_1.clicked.connect( partial(self.set_groupbox_children_visibility, self.plot_settings_1))
        self.plot_settings_2.clicked.connect( partial(self.set_groupbox_children_visibility, self.plot_settings_2))
        self.plot_settings_3.clicked.connect( partial(self.set_groupbox_children_visibility, self.plot_settings_3))
        self.chart_settings.clicked.connect( partial(self.set_groupbox_children_visibility, self.chart_settings))
        self.styles_settings.clicked.connect(partial(self.set_groupbox_children_visibility, self.styles_settings))
        self.plot_tabwidget.currentChanged.connect(self.uncheck_settings)
        self.plot_tabwidget.currentChanged.connect(lambda : self.tabwidget_resize(self.plot_tabwidget))
        self.tabWidget.currentChanged.connect(lambda :self.tabwidget_resize(self.tabWidget))

        self.select_button_t1f1.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_1, self.Filter1_ComboBox_1))
        self.select_button_t1f2.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_1, self.Filter2_ComboBox_1))
        self.select_button_t2f1.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_2, self.Filter1_ComboBox_2))
        self.select_button_t2f2.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_2, self.Filter2_ComboBox_2))
        self.select_button_t3f1.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_3, self.Filter1_ComboBox_3))
        self.select_button_t3f2.clicked.connect( partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_3, self.Filter2_ComboBox_3))

        self.listfilter_1_1.editingFinished.connect( partial(self.filter_filterlist, self.Filter1_QListWidget_1, self.listfilter_1_1))
        self.listfilter_2_1.editingFinished.connect( partial(self.filter_filterlist, self.Filter2_QListWidget_1, self.listfilter_2_1))
        self.listfilter_1_2.editingFinished.connect( partial(self.filter_filterlist, self.Filter1_QListWidget_2, self.listfilter_1_2))
        self.listfilter_2_2.editingFinished.connect( partial(self.filter_filterlist, self.Filter2_QListWidget_2, self.listfilter_2_2))
        self.listfilter_1_3.editingFinished.connect( partial(self.filter_filterlist, self.Filter1_QListWidget_3, self.listfilter_1_3))
        self.listfilter_2_3.editingFinished.connect( partial(self.filter_filterlist, self.Filter2_QListWidget_3, self.listfilter_2_3))
        self.filtersettings1.clicked.connect( partial(self.set_groupbox_children_visibility, self.filtersettings1))
        self.filtersettings2.clicked.connect( partial(self.set_groupbox_children_visibility, self.filtersettings2))
        self.filtersettings3.clicked.connect( partial(self.set_groupbox_children_visibility, self.filtersettings3))

        self.PlotChart_QPushButton.clicked.connect(lambda x: self.drawplot_with_styles())
        self.Redraw_pushButton.clicked.connect(lambda x: self.redraw())

        self.custplot_last_used_style_settingskey = 'custplot_last_used_template'
        self.styles = utils.MatplotlibStyles(self,
                                             self.template_list,
                                             self.import_button,
                                             self.open_folder_button,
                                             self.available_settings_button,
                                             self.save_as_button,
                                             self.custplot_last_used_style_settingskey,
                                             defs.custplot_default_style(),
                                             msettings=self.ms)
        self.styles.select_style_in_list(defs.custplot_default_style()[1])

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

        self.plot_tabwidget.setCurrentIndex(0)
        for group_box in [self.plot_settings_1, self.plot_settings_2, self.plot_settings_3,
                          self.filtersettings1, self.filtersettings2, self.filtersettings3,
                          self.chart_settings, self.styles_settings]:
            group_box.setChecked(False)
            self.set_groupbox_children_visibility(group_box)
        self.uncheck_settings(0)

        self.title = None
        self.xaxis_label = None
        self.yaxis_label = None

        self.init_figure()
        self.tabwidget_resize(self.tabWidget)
        self.tabwidget_resize(self.plot_tabwidget)
        self.show()


    def init_figure(self):
        try:
            self.title = self.axes.get_title()
            self.xaxis_label = self.axes.get_xlabel()
            self.yaxis_label = self.axes.get_ylabel()
        except:
            pass

        if hasattr(self, 'mpltoolbar'):
            self.layoutplot.removeWidget(self.mpltoolbar)
            self.mpltoolbar.close()
        if hasattr(self, 'canvas'):
            self.layoutplot.removeWidget(self.canvas)
            self.canvas.close()
        if hasattr(self, 'custplotfigure'):
            fignum = self.custplotfigure.number
            plt.close(fignum)

        self.custplotfigure = plt.figure()

        self.axes = self.custplotfigure.add_subplot(111)

        self.canvas = FigureCanvas(self.custplotfigure)

        self.mpltoolbar = NavigationToolbar(self.canvas, self.widgetPlot)
        self.layoutplot.addWidget(self.canvas)
        self.layoutplot.addWidget(self.mpltoolbar)

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

    def drawplot_with_styles(self):
        self.styles.load(self.drawPlot_all, (self, 'mpltoolbar'))

    @utils.general_exception_handler
    def drawPlot_all(self):
        utils.start_waiting_cursor()  # show the user this may take a long time...

        continous_color = True
        if continous_color:
            self.used_style_color_combo = set()
            color_cycler = mpl.rcParams['axes.prop_cycle']
            color_cycle_len = len(color_cycler)
            color_cycle = color_cycler()
            self.line_cycler = utils.ContinousColorCycle(color_cycle, color_cycle_len, mpl.rcParams['axes.midv_line_cycle'], self.used_style_color_combo)
            self.marker_cycler = utils.ContinousColorCycle(color_cycle, color_cycle_len, mpl.rcParams['axes.midv_marker_cycle'], self.used_style_color_combo)
            self.line_and_marker_cycler = utils.ContinousColorCycle(color_cycle, color_cycle_len,
                                                                    mpl.rcParams['axes.midv_marker_cycle'] * mpl.rcParams['axes.midv_line_cycle'],
                                                                    self.used_style_color_combo)
        else:
            ccycler = mpl.rcParams['axes.prop_cycle']
            self.line_cycler = (mpl.rcParams['axes.midv_line_cycle'] * ccycler)()
            self.marker_cycler = (mpl.rcParams['axes.midv_marker_cycle'] * ccycler)()
            self.line_and_marker_cycler = (
            mpl.rcParams['axes.midv_marker_cycle'] * mpl.rcParams['axes.midv_line_cycle'] * ccycler)()

        self.init_figure()

        self.used_format = None

        if self.title:
            self.axes.set_title(self.title)
        if self.xaxis_label:
            self.axes.set_xlabel(self.xaxis_label)
        if self.yaxis_label:
            self.axes.set_ylabel(self.yaxis_label)

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

        try:
            self.xaxis_formatters[1].__dict__['intervald'][3] = [1, 2, 4, 8, 16]  # Fix to not have the date ticks overlap at month end/start
        except Exception as e:
            utils.MessagebarAndLog.warning(log_msg=ru(
                QCoreApplication.translate('Customplot', 'Setting intervald failed! msg:\n%s ')) % str(e))

        self.drawn = True

        self.refreshPlot()
    
        utils.stop_waiting_cursor()  # now this long process is done and the cursor is back as normal

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
            utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('plotsqlitewindow', 'Plotting date_time failed, msg: %s'))%str(e))
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('plotsqlitewindow', "Customplot, transforming to recarray with date_time as x-axis failed, msg: %s"))%ru(str(e)))
            #recs = [x for x in recs if all(x)]

            table = np.array(recs, dtype=[('numx', float), ('values', float)])  #NDARRAY #define a format for xy-plot (to use if not datetime on x-axis)

            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects

            FlagTimeXY = 'XY'
            numtime = list(table2.numx)

        if self.used_format is None:
            self.used_format = FlagTimeXY
        else:
            if self.used_format != FlagTimeXY:
                raise utils.UsageError(ru(QCoreApplication.translate('CustomPlot', "Plotting both xy and time plot at the same time doesn't work! Check the x-y axix settings in all tabs!")))

        # from version 0.2 there is a possibility to make discontinuous plot if timestep bigger than maxtstep
        if self.spnmaxtstep.value() > 0: # if user selected a time step bigger than zero than thre may be discontinuous plots
            pos = np.where(np.abs(np.diff(numtime)) >= self.spnmaxtstep.value())[0] + 1
            numtime = np.insert(numtime, pos, np.nan)
            table2 = np.insert(table2, pos, np.nan)

        if FlagTimeXY == "time" and plottype == "frequency":
            if len(table2) < 2:
                utils.MessagebarAndLog.warning(bar_msg=ru(
                    QCoreApplication.translate('plotsqlitewindow', 'Frequency plot failed for %s. The timeseries must be longer than 1 value!')) % ru(self.plabels[i]),
                                                duration=30)
                table2.values[:] = [None] * len(table2)
            else:
                table2.values[:] = self.calc_frequency(table2)[:]

        if remove_mean:
            table2.values[:] = utils.remove_mean_from_nparray(table2.values)[:]

        if any([factor != 1 and factor, offset,]):
            table2.values[:] = utils.scale_nparray(table2.values, factor, offset)[:]

        if pandas_calc and FlagTimeXY == "time":
            if pandas_calc.use_pandas():
                df = pd.DataFrame.from_records(table2, columns=['values'], exclude=['date_time'])
                df.set_index(pd.DatetimeIndex(table2.date_time, name='date_time'), inplace=True)
                df.columns = ['values']

                df = pandas_calc.calculate(df)
                if df is not None:
                    try:
                        table = np.array(list(zip(df.index, df['values'])), dtype=My_format)
                    except TypeError:
                        utils.MessagebarAndLog.info(log_msg=str(df))
                        raise
                    table2 = table.view(np.recarray)  # RECARRAY transform the 2 cols into callable objects
                    numtime = table2.date_time
                else:
                    utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('plotsqlitewindow', "Pandas calculate failed.")))

        if FlagTimeXY == "time":
            plotfunc = self.axes.plot_date
        elif FlagTimeXY == "XY":
            plotfunc = self.axes.plot
        else:
            raise Exception('Programming error. Must be time or XY!')

        if plottype == "step-pre":
            self.p[i], = plotfunc(numtime, table2.values, '', drawstyle='steps-pre', marker='None', label=self.plabels[i], **next(self.line_cycler))# 'steps-pre' best for precipitation and flowmeters, optional types are 'steps', 'steps-mid', 'steps-post'
        elif plottype == "step-post":
            self.p[i], = plotfunc(numtime, table2.values, '', drawstyle='steps-post', marker='None', label=self.plabels[i], **next(self.line_cycler))
        elif plottype == "line and cross":
            self.p[i], = plotfunc(numtime, table2.values, '', marker='x', label=self.plabels[i], **next(self.line_cycler))
        elif plottype == "marker":
            self.p[i], = plotfunc(numtime, table2.values, '', linestyle='None', label=self.plabels[i], **next(self.marker_cycler))
        elif plottype == "line":
            self.p[i], = plotfunc(numtime, table2.values, '', marker='None', label=self.plabels[i], **next(self.line_cycler))
        elif plottype == "frequency" and FlagTimeXY == "time":
            try:
                self.p[i], = plotfunc(numtime, table2.values, '', marker='None', label='frequency '+str(self.plabels[i]), **next(self.line_cycler))
                self.plabels[i]='frequency '+str(self.plabels[i])
            except:
                self.p[i], = plotfunc(np.array([]),np.array([]), '', marker='None', label='frequency '+str(self.plabels[i]), **next(self.line_cycler))
                self.plabels[i]='frequency '+str(self.plabels[i])
        else:
            # line and marker
            self.p[i], = plotfunc(numtime, table2.values, '', label=self.plabels[i], **next(self.line_and_marker_cycler))


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

        self.Legend_checkBox.setChecked(self.ms.settingsdict['custplot_legend'])
        self.regular_xaxis_interval.setChecked(self.ms.settingsdict['custplot_regular_xaxis_interval'])
        self.Grid_checkBox.setChecked(self.ms.settingsdict['custplot_grid'])
    
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
        words = lineedit.text().split(';')

        listcount = filterlist.count()
        if words:
            [filterlist.item(idx).setHidden(False) if any([word.lower() in filterlist.item(idx).text().lower() for word in words]) else filterlist.item(idx).setHidden(True) for idx in range(listcount)]
        else:
            [filterlist.item(idx).setHidden(False) for idx in range(listcount)]

    def LoadTablesFromDB( self, tables_columns ):    # Open the SpatiaLite file to extract info about tables
        tables = sorted([table for table in list(tables_columns.keys()) if table not in db_utils.nonplot_tables(as_tuple=True) and not table.startswith('zz_')])
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
                sql = "SELECT DISTINCT {} FROM {} WHERE {} IN ({}) ORDER BY {}".format(
                                                                                str(filtercolumn),
                                                                                table,
                                                                                other_filtercolumn,
                                                                                ', '.join(["'{}'".format(item)
                                                                                            for item in selected]),
                                                                                str(filtercolumn),)

        ConnectionOK, list_data= db_utils.sql_load_fr_db(sql)
        for post in list_data:
            item = QtWidgets.QListWidgetItem(str(post[0]))
            getattr(self, QListWidgetname).addItem(item)

    @utils.general_exception_handler
    def redraw(self):
        self.styles.load(self.refreshPlot, (self, 'mpltoolbar'))

    @utils.general_exception_handler
    def refreshPlot( self):
        #If the user has not pressed "draw" before, do nothing
        utils.MessagebarAndLog.info(
            log_msg=ru(QCoreApplication.translate('Customplot', 'Loaded style:\n%s ')) % (
            self.styles.rcparams()))

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

            try:
                if self.regular_xaxis_interval.isChecked():
                    self.xaxis_formatters[1].__dict__['interval_multiples'] = False
                else:
                    self.xaxis_formatters[1].__dict__['interval_multiples'] = True
            except Exception as e:
                utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('Customplot', 'Setting regular xaxis interval failed! msg:\n%s '))%str(e))

        self.axes.grid(self.Grid_checkBox.isChecked()) # grid

        for label in self.axes.xaxis.get_ticklabels():
            label.set_rotation(20)

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

            leg.set_zorder(999)
            leg.draggable(state=True)
        else:
            self.axes.legend_ = None

        self.update_plot_size()

        self.canvas.draw()

        self.plot_tabwidget.setCurrentIndex(0)
        #plt.close(self.custplotfigure)#this closes reference to self.custplotfigure

    def update_plot_size(self):
        if self.dynamic_plot_size.isChecked():
            self.widgetPlot.setMinimumWidth(10)
            self.widgetPlot.setMaximumWidth(16777215)
            self.widgetPlot.setMinimumHeight(10)
            self.widgetPlot.setMaximumHeight(16777215)
            #self.widgetPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        else:
            width_inches, height_inches = mpl.rcParams['figure.figsize']
            screen_dpi = QApplication.screens()[0].logicalDotsPerInch()
            width_pixels = width_inches * screen_dpi
            height_pixels = height_inches * screen_dpi
            self.canvas.setFixedSize(width_pixels, height_pixels)
            self.widgetPlot.setFixedWidth(max(self.canvas.size().width(), self.mpltoolbar.size().width()))
            self.widgetPlot.setFixedHeight(self.canvas.size().height() + self.mpltoolbar.size().height()*3)

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
        self.ms.settingsdict['custplot_legend']=self.Legend_checkBox.isChecked()
        self.ms.settingsdict['custplot_grid']=self.Grid_checkBox.isChecked()
        #self.ms.settingsdict['custplot_title'] = unicode(self.axes.get_title())
        #self.ms.settingsdict['custplot_xtitle'] = unicode(self.axes.get_xlabel())
        #self.ms.settingsdict['custplot_ytitle'] = unicode(self.axes.get_ylabel())
        self.ms.settingsdict['custplot_tabwidget'] = self.tabWidget.currentIndex()
        self.ms.settingsdict['custplot_regular_xaxis_interval'] = self.regular_xaxis_interval.isChecked()
        self.ms.save_settings()

        self.ms.save_settings(self.custplot_last_used_style_settingskey)

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

    def uncheck_settings(self, current_index):
        if current_index == 0:
            self.chart_settings.setChecked(False)
            self.styles_settings.setChecked(False)
            pass
        elif current_index == 1:
            self.chart_settings.setChecked(True)
            self.styles_settings.setChecked(True)

        self.set_groupbox_children_visibility(self.styles_settings)
        self.set_groupbox_children_visibility(self.chart_settings)

    def tabwidget_resize(self, tabwidget):
        current_index = tabwidget.currentIndex()
        for tabnr in range(tabwidget.count()):
            if tabnr != current_index:
                tabwidget.widget(tabnr).setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        tab = tabwidget.currentWidget()
        tab.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        tab.adjustSize()







class PandasCalculations(object):
    def __init__(self, gridlayout):

        self.widget = qgis.PyQt.QtWidgets.QWidget()

        #General settings
        self.rule_label = qgis.PyQt.QtWidgets.QLabel('Resample rule')
        self.rule = qgis.PyQt.QtWidgets.QLineEdit()
        for wid in [self.rule_label, self.rule]:
            wid.setToolTip(ru(QCoreApplication.translate('PandasCalculations',
                           'Steplength for resampling, ex:\n'
                           '"10S" = 10 seconds\n'
                           '"20T" = 20 minutes\n'
                           '"1h" = 1 hour\n'
                           '"24h" = 24 hours\n'
                           '(D = calendar day, M = month end, MS = month start, W = weekly, AS = year start, A = year end, ...)\n'
                           'No resampling if field is empty\n'
                           'See pandas pandas.DataFrame.resample documentation for more info.')))

        self.base_label = qgis.PyQt.QtWidgets.QLabel('Resample base')
        self.base = qgis.PyQt.QtWidgets.QLineEdit()
        for wid in [self.base_label, self.base]:
            wid.setToolTip(ru(QCoreApplication.translate('PandasCalculations',
                           'The hour to start each timestep when rule "evenly subdivide 1 day" (for example Rule = 24h)\n'
                           'Ex: 7 (= 07:00). Default is 0 (00:00)\n'
                           'See pandas pandas.DataFrame.resample documentation for more info:\n'
                           'For frequencies that evenly subdivide 1 day, the "origin" of the aggregated intervals.\n'
                           'For example, for "5min" frequency, base could range from 0 through 4. Defaults to 0.')))

        self.how_label = qgis.PyQt.QtWidgets.QLabel('Resample how')
        self.how = qgis.PyQt.QtWidgets.QLineEdit()
        for wid in [self.how_label, self.how]:
            wid.setToolTip(ru(QCoreApplication.translate('PandasCalculations',
                           'How to make the resample, ex. "mean" (default), "first", "last", "sum".\n'
                           'See pandas pandas.DataFrame.resample documentation for more info\n'
                           '(though "how" is not explained a lot)')))

        #Moving average:
        self.window_label = qgis.PyQt.QtWidgets.QLabel('Rolling mean window')
        self.window = qgis.PyQt.QtWidgets.QLineEdit('')
        self.center_label = qgis.PyQt.QtWidgets.QLabel('Rolling mean center')
        self.center = qgis.PyQt.QtWidgets.QCheckBox()
        self.center.setChecked(True)
        for wid in [self.window_label, self.window]:
            wid.setToolTip(ru(QCoreApplication.translate('PandasCalculations',
                           'The number of timesteps in each moving average (rolling mean) mean\n'
                           'The result is stored at the center timestep of each mean.\n'
                           'See Pandas pandas.DataFrame.rolling documentation for more info.\n'
                           'No rolling mean if field is empty.')))

        for wid in [self.center_label, self.center]:
            wid.setToolTip(ru(QCoreApplication.translate('PandasCalculations',
                           'Check (default) to store the rolling mean at the center timestep.\n'
                           'Uncheck to store the rolling mean at the last timestep.\n'
                           'See Pandas pandas.rolling_mean documentation for more info.')))


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
        how = self.how.text() if self.how.text() else 'mean'
        if rule:
            try:
                base = int(base)
            except ValueError:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('PandasCalculations', 'Resample base must be an integer')))
            else:
                if pd.__version__ > '0.18.0':
                    # new api for pandas >=0.18
                    df = getattr(df.resample(rule,base=int(base)),how)()
                else:
                    #old pandas
                    df = df.resample(rule, how=how, base=int(base))
        #Rolling mean
        window = self.window.text()
        if window:
            try:
                window = int(window)
            except ValueError:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('PandasCalculations', 'Rolling mean window must be an integer')))
            else:
                try:
                    # Pandas version >= '0.18.0'
                    df = df.rolling(window, center=self.center.isChecked()).mean()
                except AttributeError:
                    df = pd.rolling_mean(df, window=window, center=self.center.isChecked())

        return df

def horizontal_line():
    line = qgis.PyQt.QtWidgets.QFrame()
    line.setGeometry(qgis.PyQt.QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(qgis.PyQt.QtWidgets.QFrame.HLine)
    line.setFrameShadow(qgis.PyQt.QtWidgets.QFrame.Sunken)
    return line






