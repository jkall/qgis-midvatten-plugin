#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is where a section plot is created 
 NOTE - if using this file, it has to be imported by midvatten_plugin.py
                             -------------------
        begin                : 2013-11-27
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/
"""
from __future__ import absolute_import

import copy
import os
import sqlite3 as sqlite  # needed since spatialite-specific sql will be used during polyline layer import
import traceback
import types
from builtins import range
from builtins import str
from builtins import zip
from operator import itemgetter

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import qgis.PyQt
from matplotlib import container, patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from qgis.PyQt import QtWidgets
# from ui.secplotdockwidget_ui import Ui_SecPlotDock
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QApplication, QDockWidget, QSizePolicy
from qgis.core import QgsProject
from qgis.core import QgsRectangle, QgsGeometry, QgsFeatureRequest, QgsWkbTypes

from midvatten.tools.utils.gui_utils import set_combobox

# try:#assume matplotlib >=1.5.1
#    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# except:
#    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar
Ui_SecPlotDock =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'secplotdockwidget.ui'))[0]

from matplotlib.widgets import Slider
from matplotlib.gridspec import GridSpec
import datetime
import matplotlib.dates as mdates

from midvatten.tools.utils import common_utils, db_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools.utils.midvatten_utils import PlotTemplates
from midvatten.tools.utils.matplotlib_replacements import NavigationToolbarWithSignal as NavigationToolbar
import midvatten.definitions.midvatten_defs as defs
from midvatten.tools.utils import matplotlib_replacements
from midvatten.tools.utils.sampledem import qchain, sampling

try:
    import pandas as pd
except:
    pandas_on = False
else:
    pandas_on = True

"""
Major parts of the code is re-used from the profiletool plugin:
# Copyright (C) 2008  Borys Jurgiel
# Copyright (C) 2012  Patrice Verchere 
Code is also re-used from the qprof plugin by Mauro Alberti, Marco Zanieri

SAKNAS:
1. (input och plottning av seismik, vlf etc längs med linjen) - efter release alpha
2. ((input och plottning av markyta från DEM)) - efter release beta
"""


class SectionPlot(qgis.PyQt.QtWidgets.QDockWidget, Ui_SecPlotDock):#the Ui_SecPlotDock  is created instantaniously as this is created
    def __init__(self, parent1, iface1):
        #super(sectionplot, self).save_settings()
        qgis.PyQt.QtWidgets.QDockWidget.__init__(self, parent1) #, PyQt4.QtCore.Qt.WindowFlags(PyQt4.QtCore.Qt.WA_DeleteOnClose))
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        #Ui_SecPlotDock.__init__(self)

        self.parent = parent1
        self.iface = iface1
        #self.location = PyQt4.QtCore.Qt.Qt.BottomDockWidgetArea#should be loaded from settings instead
        #self.location = int(self.ms.settingsdict['secplotlocation'])
        if not self.isWindow():
            self.dockLocationChanged.connect(self.set_location)#not really implemented yet

        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.setWindowTitle("Midvatten plugin - section plot") # Set the title for the dialog

        self.initUI()
        self.obsid_annotation = {}
        self.water_level_labels_duplicate_check = []
        self.template_plot_label.setText("<a href=\"https://github.com/jkall/qgis-midvatten-plugin/wiki/5.-Plots-and-reports#create-section-plot\">Templates manual</a>")
        self.template_plot_label.setOpenExternalLinks(True)

    def initUI(self):
        # connect signal
        self.pushButton.clicked.connect(lambda x: self.draw_plot())
        self.topLevelChanged.connect(lambda x: self.add_titlebar(self))
        self.settingsdockWidget.topLevelChanged.connect(lambda x: self.float_settings())
        self.include_views_checkBox.clicked.connect(lambda x: self.fill_wlvltable(self.include_views_checkBox.isChecked()))
        self.init_figure()
        self.tabWidget.currentChanged.connect(lambda: self.tabwidget_resize(self.tabWidget))
        self.tabwidget_resize(self.tabWidget)
        self.wlvl_groupbox.collapsedStateChanged.connect(lambda: self.resize_widget(self.settingsdockWidget))
        self.dem_groupbox.collapsedStateChanged.connect(lambda: self.resize_widget(self.settingsdockWidget))
        self.bar_groupbox.collapsedStateChanged.connect(lambda: self.resize_widget(self.settingsdockWidget))
        self.plots_groupbox.collapsedStateChanged.connect(lambda: self.resize_widget(self.settingsdockWidget))
        self.tabWidget.setTabBarAutoHide(True)
        self.settingsdockWidget.closeEvent = types.MethodType(self.dock_settings, self.settingsdockWidget)
        self.resize_widget(self.settingsdockWidget)
        self._waterlevel_lineplot = None
        self.resample_rule.setText('1D')
        self.resample_rule.setToolTip(defs.pandas_rule_tooltip())
        self.resample_base.setText('0')
        self.resample_base.setToolTip(defs.pandas_base_tooltip())
        self.resample_how.setText('mean')
        self.resample_how.setToolTip(defs.pandas_how_tooltip())

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
        if hasattr(self, 'figure'):
            fignum = self.figure.number
            plt.close(fignum)
        self.figure = plt.figure()

        if self.interactive_groupbox.isChecked():
            self.gridspec = GridSpec(nrows=2, ncols=2, height_ratios=[20, 1])
        else:
            self.gridspec = GridSpec(nrows=1, ncols=1)

        self.axes = self.figure.add_subplot(self.gridspec[0:2, 0:1])
        self.canvas = FigureCanvas(self.figure)

        self.canvas.mpl_connect('button_release_event', lambda event: self.update_barwidths_from_plot())
        self.canvas.mpl_connect('resize_event', lambda event: self.update_barwidths_from_plot())

        self.mpltoolbar = NavigationToolbar(self.canvas, self.widgetPlot)

        try:
            matplotlib_replacements.replace_matplotlib_backends_backend_qt5agg_NavigationToolbar2QT_set_message_xylimits(
                self.mpltoolbar)
        except Exception as e:
            common_utils.MessagebarAndLog.info(log_msg=ru(
                QCoreApplication.translate('SectionPlot', 'Could not alter NavigationToolbar, msg: %s')) % str(e))

        try:
            self.mpltoolbar.edit_parameters_used.connect(self.update_legend)
        except Exception as e:
            common_utils.MessagebarAndLog.info(log_msg=ru(
                QCoreApplication.translate('SectionPlot', 'Could not connect to edit_parameters_used signal, msg: %s')) % str(e))

        self.layoutplot.addWidget(self.canvas)
        self.layoutplot.addWidget(self.mpltoolbar)

        pick_annotator = common_utils.PickAnnotator(self.figure, canvas=self.canvas, mpltoolbar=self.mpltoolbar)

    def tabwidget_resize(self, tabwidget):
        current_index = tabwidget.currentIndex()
        for tabnr in range(tabwidget.count()):
            if tabnr != current_index:
                tabwidget.widget(tabnr).setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        tab = tabwidget.currentWidget()
        tab.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        tab.adjustSize()

    def resize_widget(self, parent):
        """

        :param parent:
        :param widget:
        :return:
        """

        parent.updateGeometry()
        parent.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        parent.adjustSize()

    def update_plot_size(self):
        if self.dynamic_plot_size.isChecked():
            self.widgetPlot.setMinimumWidth(10)
            self.widgetPlot.setMaximumWidth(16777215)
            self.widgetPlot.setMinimumHeight(10)
            self.widgetPlot.setMaximumHeight(16777215)
            #self.widgetPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        else:
            width_inches, height_inches = self.figure.get_size_inches()
            screen_dpi = QApplication.screens()[0].logicalDotsPerInch()
            width_pixels = width_inches * screen_dpi
            height_pixels = height_inches * screen_dpi
            self.canvas.setFixedSize(width_pixels, height_pixels)
            self.widgetPlot.setFixedWidth(max(self.canvas.size().width(), self.mpltoolbar.size().width()))
            self.widgetPlot.setFixedHeight(self.canvas.size().height() + self.mpltoolbar.size().height()*3)

    def add_titlebar(self, widget):
        if widget.isWindow():
            widget.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            widget.show()

    def float_settings(self):
        dockwidget = getattr(self, 'settingsdockWidget')
        if dockwidget.isWindow():
            self.add_titlebar(dockwidget)
            dockwidget.setWindowTitle(QCoreApplication.translate('SectionPlot', 'Sectionplot settings'))

            if self.tabWidget.count() > 1:
                self.tabWidget.removeTab(1)
        dockwidget.setFeatures(QDockWidget.DockWidgetClosable)

    def dock_settings(self, _self, event):
        self.tabWidget.addTab(self.settings_tab, 'Settings')
        self.old_settingsdockWidget = self.settingsdockWidget
        self.settingsdockWidget = QDockWidget()
        self.settingsdockWidget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.settingsdockWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.settingsdockWidget.topLevelChanged.connect(lambda x: self.float_settings())
        self.settingsdockWidget.closeEvent = types.MethodType(self.dock_settings, self.settingsdockWidget)
        self.settingsdockWidget.setWidget(self.dockWidgetContents_2)

        # Remove the old widget widgetitem from the old settingsdockWidget
        self.verticalLayout_4.takeAt(0)

        spacing = self.verticalLayout_4.takeAt(0)

        self.verticalLayout_4.addWidget(self.settingsdockWidget)
        self.verticalLayout_4.insertSpacerItem(-1, spacing)

        self.resize_widget(self.settingsdockWidget)
        self.tabwidget_resize(self.tabWidget)
        self.tabWidget.adjustSize()
        event.accept()

    def do_it(self, msettings, selected_obspoints, sectionlinelayer):#must recieve msettings again if this plot windows stayed open while changing qgis project
        self.obsid_annotation = {}

        #show the user this may take a long time...
        common_utils.start_waiting_cursor()
        #settings must be recieved here since plot windows may stay open (hence sectionplot instance activated) while a new qgis project is opened or midv settings are chaned 
        self.ms = msettings

        template_folder = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'definitions', 'secplot_templates')
        self.secplot_templates = PlotTemplates(self, self.template_list, self.edit_button, self.load_button,
                                               self.save_as_button, self.import_button, self.remove_button,
                                               template_folder, 'secplot_templates', 'secplot_loaded_template',
                                               defs.secplot_default_template(), self.ms)

        #Draw the widget
        self.iface.addDockWidget(max(self.ms.settingsdict['secplotlocation'],1), self)
        self.iface.mapCanvas().setRenderFlag(True)

        self.dbconnection = db_utils.DbConnectionManager()
        self.temptable_name = 'temporary_section_line'

        self.fill_check_boxes()
        self.fill_combo_boxes()
        self.show()
        #class variables
        self.geology_txt = []
        self.geoshort_txt = []
        self.capacity_txt = []
        self.hydro_explanation_txt = []
        self.development_txt = []
        self.comment_txt = []
        self.sectionlinelayer = sectionlinelayer
        
        if self.sectionlinelayer and self.sectionlinelayer.selectedFeatureCount() == 1:
            # Test that layer and feature have been selected
            # upload vector line layer as temporary table in sqlite db
            self.line_crs = self.sectionlinelayer.crs()
            # print(str(self.dbconnection.cursor().execute('select * from a.sqlite_master').fetchall()))
            ok = self.upload_qgis_vector_layer(self.sectionlinelayer, self.line_crs.postgisSrid(), True,
                                               False)  # loads qgis polyline layer into sqlite table
            if not ok:
                return None

            # get sorted obsid and distance along section from sqlite db
            if len(selected_obspoints):
                nF = len(selected_obspoints)#number of Features
                length_along_table = self.get_length_along(selected_obspoints)
                # get_length_along returns a numpy view, values are returned by
                # length_along_table.obs_id or length_along_table.length
                self.selected_obsids = length_along_table.obs_id
                self.length_along = length_along_table.length

                # hidden feature, printout to python console
                common_utils.MessagebarAndLog.info(log_msg=ru(
                    QCoreApplication.translate('SectionPlot',
                                               'Hidden features, obsids and length along section:\n%s\%s')) %
                                                                       (';'.join(self.selected_obsids),
                                                     ';'.join([str(x) for x in self.length_along])))
            else:
                self.selected_obsids = []

            self.fill_dem_list()
        else:
            self.selected_obsids = selected_obspoints

            res = self.dbconnection.execute_and_fetchall('''SELECT obsid, east, north FROM obs_points WHERE obsid IN ({})'''.format(
                common_utils.sql_unicode_list(self.selected_obsids)))
            xs = [float(row[1]) for row in res]
            ys = [float(row[2]) for row in res]
            if (max(xs) - min(xs)) > (max(ys) - min(ys)):
                # Order by x
                k = 1
            else:
                # Order by y
                k = 2
                pass
            self.selected_obsids = [row[0] for row in sorted(res, key=itemgetter(k))]

            self.length_along = range(0, 10 * len(self.selected_obsids), 10)
            self.fill_dem_list()

        common_utils.stop_waiting_cursor() #now this long process is done and the cursor is back as normal
        
        # get PlotData
        self.get_plot_data_geo()
        self.get_plot_data_seismic()
        self.get_plot_data_hydro()
        self.get_missing_obsid_labels()

        #draw plot
        self.draw_plot()

    def get_plot_data_seismic(self):
        common_utils.start_waiting_cursor()
        # Last step in get data - check if the line layer is obs_lines and if so, load seismic data if there are any
        My_format = [('obsline_x', float), ('obsline_y1', float), ('obsline_y2', float), ('obsline_y3', float)]
        obsline_x=[]
        obsline_y1=[]  # bedrock
        obsline_y2=[]  # ground surface
        obsline_y3=[] # gw_table
        x='length'
        self.y1_column='bedrock'
        self.y2_column='ground'
        self.y3_column='gw_table'
        table='seismic_data'
        if self.sectionlinelayer and self.sectionlinelayer.name()=='obs_lines':
            obsline_id = common_utils.getselectedobjectnames(self.sectionlinelayer)[0]
            sql = r"""select %s as x, %s as y1, %s as y2, %s as y3 from %s where obsid='%s'"""%(x, self.y1_column,self.y2_column, self.y3_column,table,obsline_id)
            conn_OK, recs = db_utils.sql_load_fr_db(sql, self.dbconnection)
            table = np.array(recs, dtype=My_format)  #NDARRAY
            self.obs_lines_plot_data=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write self.obs_lines_plot_data.values
        #print('debug info: ' + str(self.selected_obsids) + str(self.x_id) + str(self.z_id) + str(self.barlengths) + str(self.bottoms))#debug
        common_utils.stop_waiting_cursor()

    def get_missing_obsid_labels(self):
        for idx, obs in enumerate(self.selected_obsids):
            if obs not in self.obsid_annotation and (self.ms.settingsdict['stratigraphyplotted'] or
                                                     self.ms.settingsdict['secplothydrologyplotted']):
                if self.barlengths[idx]:
                    self.obsid_annotation[obs] = (self.x_id[idx], self.bottoms[idx] + self.barlengths[idx])

    def draw_plot(self): #replot
        self.water_level_labels_duplicate_check = []


        rcparams = self.secplot_templates.loaded_template.get('rcParams', {})
        for k, v in rcparams.items():
            try:
                mpl.rcParams[k] = v
            except KeyError:
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('SectionPlot', "rcParams key %s didn't exist")) % ru(k))


        try:
            common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('SectionPlot', 'Plotting using settings:\n%s')) % self.secplot_templates.readable_output())
        except:
            pass
        if not isinstance(self.dbconnection, db_utils.DbConnectionManager):
            self.dbconnection = db_utils.DbConnectionManager()

        self.init_figure()

        try:
            common_utils.start_waiting_cursor()#show the user this may take a long time...
            try:
                self.annotationtext.remove()
            except:
                pass
            #load user settings from the ui
            self.ms.settingsdict['secplotwlvltab'] = str(self.wlvltableComboBox.currentText())
            temporarystring = ru(self.datetimetextEdit.toPlainText()) #this needs some cleanup
            try:
                self.ms.settingsdict['secplotdates']= [x for x in temporarystring.replace('\r', '').split('\n') if x.strip()]
            except TypeError as e:
                self.ms.settingsdict['secplotdates']=''
            self.ms.settingsdict['secplottext'] = self.textcolComboBox.currentText()
            self.ms.settingsdict['secplotbw'] = self.barwidthdoubleSpinBox.value()
            self.ms.settingsdict['secplotdrillstop'] = self.drillstoplineEdit.text()
            self.ms.settingsdict['stratigraphyplotted'] = self.Stratigraphy_radioButton.isChecked()
            self.ms.settingsdict['secplothydrologyplotted'] = self.Hydrology_radioButton.isChecked()
            self.ms.settingsdict['secplotlabelsplotted'] = self.Labels_checkBox.isChecked()
            self.ms.settingsdict['secplotlegendplotted'] = self.Legend_checkBox.isChecked()
            self.get_dem_selection()
            self.ms.settingsdict['secplotselectedDEMs'] = self.rasterselection
            #fix Floating Bar Width in percents of xmax - xmin
            self.p = []
            self.labels = []

            if len(self.selected_obsids) > 0:
                xmax, xmin = float(max(self.length_along)), float(min(self.length_along))
                self.barwidth = (self.ms.settingsdict['secplotbw']/100.0)*(xmax -xmin)
                self.get_plot_data_2()

                if self.ms.settingsdict['stratigraphyplotted']:
                    #PLOT ALL MAIN GEOLOGY TYPES AS SINGLE FLOATING BAR SERIES
                    self.plot_geology()
                    # WRITE TEXT BY ALL GEOLOGY TYPES, ADJACENT TO FLOATING BAR SERIES
                    if len(self.ms.settingsdict['secplottext'])>0:
                        self.write_annotation()

                if self.ms.settingsdict['secplothydrologyplotted']:
                    # Plot all main hydrology types as single floating bar serieite ts
                    self.plot_hydrology()
                    # Write text by all hydrology types adjacent to floating bar series
                    if len(self.ms.settingsdict['secplottext']) > 0:
                        self.write_annotation()

                self.plot_water_level()

                if self.ms.settingsdict['secplotdrillstop']!='':
                    self.plot_drill_stop()

                # write obsid at top of each stratigraphy floating bar plot, also plot empty bars to show drillings without stratigraphy data
                if self.ms.settingsdict['stratigraphyplotted'] or self.ms.settingsdict['secplothydrologyplotted'] or (self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates']) > 0):
                    self.write_obsid(self.ms.settingsdict['secplotlabelsplotted'])

            else:
                self.barwidth = 0.0

            #if the line layer obs_lines is selected, then try to plot seismic data if there are any
            if self.sectionlinelayer and self.sectionlinelayer.name()=='obs_lines':
                if len(self.obs_lines_plot_data)>0:
                    self.plot_obs_lines_data()

            #if there are any DEMs selected, try to plot them
            if len(self.ms.settingsdict['secplotselectedDEMs'])>0:
                self.plot_dems()

            """
            if there is no stratigraphy data and no borehole lenght for first or last observations,
            then autscaling will fail silently since it does not consider axes.annotate (which is used for printing obsid)
            hence this special treatment to check if xlim are less than expected from lengthalong
            """
            # self.secax.autoscale(enable=True, axis='both', tight=None)

            xmin_xmax = self.secplot_templates.loaded_template['Axes_set_xlim']
            if xmin_xmax is not None:
                xmin, xmax = xmin_xmax
            else:
                if len(self.selected_obsids) > 0:
                    _xmin, _xmax = self.axes.get_xlim()
                    xmin = min(float(min(self.length_along)) - self.barwidth, _xmin)
                    xmax = max(float(max(self.length_along)) + self.barwidth, _xmax)
                else:
                    xticks = self.axes.get_xticks()
                    # shift half a step left and right
                    xmin = (3 * xticks[0] - xticks[1]) / 2.
                    xmax = (3 * xticks[-1] - xticks[-2]) / 2.
            self.axes.set_xlim(xmin, xmax)

            ymin_ymax = self.secplot_templates.loaded_template['Axes_set_ylim']
            if ymin_ymax is not None:
                ymin, ymax = ymin_ymax
            else:
                yticks = self.axes.get_yticks()
                # shift half a step up and down
                ymin = (3 * yticks[0] - yticks[1]) / 2.
                ymax = (3 * yticks[-1] - yticks[-2]) / 2.
            self.axes.set_ylim(ymin, ymax)

            #labels, grid, legend etc.
            self.finish_plot()
            self.save_settings()
            self.dbconnection.closedb()
            self.dbconnection = None
        except KeyError as e:
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('SectionPlot', 'Section plot optional settings error, press "Restore defaults"')),
                                                               log_msg=ru(QCoreApplication.translate('SectionPlot', 'Error msg: %s'))%str(traceback.format_exc()))
            common_utils.stop_waiting_cursor()
            self.dbconnection.closedb()
            self.dbconnection = None

        except:
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('SectionPlot', 'An error occured, see log message panel!')),
                                                               log_msg=ru(
                                                QCoreApplication.translate('SectionPlot', 'Error msg:\n %s')) % str(
                                                traceback.format_exc()))

            common_utils.stop_waiting_cursor()
            self.dbconnection.closedb()
            self.dbconnection = None
            raise
        else:
            common_utils.stop_waiting_cursor()#now this long process is done and the cursor is back as normal

    def execute_query(self,query,params=(),commit=False):#from qspatialite, it is only used by self.uploadQgisVectorLayer
        """Execute query (string) with given parameters (tuple) (optionnaly perform commit to save Db) and return resultset [header,data] or [flase,False] if error"""
        query=str(query)
        self.queryPb=False
        header=[]
        data=[]
        cursor=self.dbconnection.cursor
        try:
            cursor.execute(query,params)
            if (cursor.description is not None):
                header = [item[0] for item in cursor.description]
            data = [row for row in cursor]
            if commit:
                self.dbconnection.commit()
        except sqlite.OperationalError as Msg:
            self.dbconnection.rollback()
            common_utils.pop_up_info(ru(QCoreApplication.translate('SectionPlot', "The SQL query\n %s\n seems to be invalid.\n\n%s")) % (query, Msg), 'Error', None)
            self.queryPb=True #Indicates pb with current query
            
        return header,data

    def fill_check_boxes(self):  # sets checkboxes to last selection
        if self.ms.settingsdict['secplotincludeviews']:
            self.include_views_checkBox.setChecked(True)
        if self.ms.settingsdict['stratigraphyplotted']:
            self.Stratigraphy_radioButton.setChecked(True)
        else:
            self.Stratigraphy_radioButton.setChecked(False)
        if self.ms.settingsdict['secplothydrologyplotted']:
            self.Hydrology_radioButton.setChecked(True)
        else:
            self.Hydrology_radioButton.setChecked(False)
        if self.ms.settingsdict['secplotlabelsplotted']:
            self.Labels_checkBox.setChecked(True)
        else:
            self.Labels_checkBox.setChecked(False)
        if self.ms.settingsdict['secplotlegendplotted']:
            self.Legend_checkBox.setChecked(True)
        else:
            self.Legend_checkBox.setChecked(False)
        if self.ms.settingsdict['secplotwidthofplot']:
            self.width_of_plot.setChecked(True)
        else:
            self.width_of_profile.setChecked(True)

    def fill_combo_boxes(self): # This method populates all table-comboboxes with the tables inside the database
        # Execute a query in SQLite to return all available tables (sql syntax excludes some of the predefined tables)
        # start with cleaning comboboxes before filling with new entries
        # clear comboboxes etc
        #self.colorComboBox.clear()
        self.textcolComboBox.clear()  
        self.datetimetextEdit.clear()
        self.drillstoplineEdit.clear()

        #Fill comboxes, lineedits etc
        self.fill_wlvltable(self.include_views_checkBox.isChecked())

        textitems=['','geology','geoshort','capacity', 'hydroexplanation','development','comment']
        for item in textitems:
            self.textcolComboBox.addItem(item)
        self.drillstoplineEdit.setText(self.ms.settingsdict['secplotdrillstop'])
        #FILL THE LIST OF DATES AS WELL
        for datum in self.ms.settingsdict['secplotdates']:
            self.datetimetextEdit.append(datum)

        #then select what was selected last time (according to midvatten settings)
        """
        MUST FIX

        DATES - SETTINGS AND PLOT ETC
        """
        if len(str(self.ms.settingsdict['secplotwlvltab'])):#If there is a last selected wlvsl
            set_combobox(self.wlvltableComboBox, str(self.ms.settingsdict['secplotwlvltab']), add_if_not_exists=False)

        if len(str(self.ms.settingsdict['secplottext'])):#If there is a last selected field for annotation in graph
            set_combobox(self.textcolComboBox, str(self.ms.settingsdict['secplottext']), add_if_not_exists=False)

        if self.ms.settingsdict['secplotbw'] !=0:
            self.barwidthdoubleSpinBox.setValue(self.ms.settingsdict['secplotbw'])            
        else:
            self.barwidthdoubleSpinBox.setValue(2)
        self.drillstoplineEdit.setText(self.ms.settingsdict['secplotdrillstop']) 

    def fill_dem_list(self):   # This method populates the QListWidget 'inData' with all possible DEMs
        self.inData.clear()
        if not self.sectionlinelayer:
            return
        self.rastItems = {}  # dictionary - layer name : layer

        #QgsProject::layers(	)
        msg = []
        layers = [QgsProject.instance().mapLayer(_id) for _id in QgsProject.instance().mapLayers()]
        for layer in layers:
            if layer.type() == layer.RasterLayer:
                if layer.bandCount() != 1:  # only single band raster layers
                    msg.append('Sectionplot: Layer "{}" omitted due to more than one layer band.'.format(ru(layer.name())))
                elif layer.crs().authid()[5:]!= self.line_crs.authid()[5:]: #only raster layer with crs corresponding to line layer
                    msg.append('Sectionplot: Layer "{}" omitted due to wrong CRS ("{}" is required, was "{}".'.format(
                        ru(layer.name()), self.line_crs.authid(), layer.crs().authid()))
                else:
                    self.rastItems[str(layer.name())] = layer
                    self.inData.addItem(str(layer.name()))
                    item = self.inData.item(self.inData.count() - 1)
                    if item.text() in self.ms.settingsdict['secplotselectedDEMs']:
                        item.setSelected(True)
        if msg:
            common_utils.MessagebarAndLog.warning(
                bar_msg=QCoreApplication.translate('SectionPlot', "One or more layers were omitted due to unfulfilled requirements, see log message panel."),
                log_msg='\n'.join(msg),
                duration=30
            )
        self.get_dem_selection()

    def fill_wlvltable(self, include_views):
        self.ms.settingsdict['secplotincludeviews'] = include_views
        current_text = self.wlvltableComboBox.currentText()
        self.wlvltableComboBox.clear()
        skip_views = True if not include_views else False
        tabeller = [x for x in db_utils.get_tables(dbconnection=self.dbconnection, skip_views=skip_views)
                    if not x.startswith('zz_') and x not in
                    ['comments',
                                                         'obs_points',
                                                        'obs_lines',
                                                        'obs_p_w_lvl',
                                                        'obs_p_w_qual_field',
                                                        'obs_p_w_qual_lab',
                                                        'obs_p_w_strat',
                                                        'seismic_data',
                                                         'meteo',
                                                         'vlf_data',
                                                         'w_flow',
                                                         'w_qual_field_geom',
                                                         'zz_flowtype',
                                                         'w_qual_lab',
                                                         'w_qual_field',
                                                         'stratigraphy',
                                                         'about_db']]
        self.wlvltableComboBox.addItem('')
        for tabell in tabeller:
            self.wlvltableComboBox.addItem(tabell)
        set_combobox(self.wlvltableComboBox, str(current_text), add_if_not_exists=False)

    def finish_plot(self):
        self.update_legend()

        self.axes.grid(**self.secplot_templates.loaded_template['grid_Axes_grid'])
        if not self.sectionlinelayer: # Test produces simple stratigraphy plot
            self.axes.set_xticks(self.length_along)  # Places ticks where plots are
            for label in self.axes.set_xticklabels(self.selected_obsids):  # Sets tick labels as obsids
                label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])
            Axes_set_xlabel = dict(
                [(k, v) for k, v in self.secplot_templates.loaded_template.get('Axes_set_xlabel', {}).items() if
                 k != 'xlabel'])
            xlabel = self.secplot_templates.loaded_template.get('Axes_set_xlabel_stratplot', {}).get('xlabel', defs.secplot_default_template()['Axes_set_xlabel_stratplot']['xlabel'])

        else:
            self.axes.xaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
            for label in self.axes.xaxis.get_ticklabels():
                label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])
            Axes_set_xlabel = dict(
                [(k, v) for k, v in self.secplot_templates.loaded_template.get('Axes_set_xlabel', {}).items() if
                 k != 'xlabel'])
            xlabel = self.secplot_templates.loaded_template.get('Axes_set_xlabel', {}).get('xlabel', defs.secplot_default_template()['Axes_set_xlabel']['xlabel'])
        self.axes.set_xlabel(xlabel, **Axes_set_xlabel)  # Allows international characters ('åäö') as xlabel
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))

        Axes_set_ylabel = dict([(k, v) for k, v in self.secplot_templates.loaded_template.get('Axes_set_ylabel', {}).items() if k != 'ylabel'])
        ylabel = self.secplot_templates.loaded_template.get('Axes_set_ylabel', {}).get('ylabel', defs.secplot_default_template()['Axes_set_ylabel']['ylabel'])
        self.axes.set_ylabel(ylabel, **Axes_set_ylabel)  #Allows international characters ('åäö') as ylabel

        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])

        if self.secplot_templates.loaded_template['Figure_subplots_adjust']:
            self.figure.subplots_adjust(**self.secplot_templates.loaded_template['Figure_subplots_adjust'])

        if self.width_of_plot.isChecked():
            self.ms.settingsdict['secplotwidthofplot'] = True
            self.update_barwidths_from_plot()
        else:
            self.ms.settingsdict['secplotwidthofplot'] = False

        self.update_plot_size()
        #if mpl.rcParams['figure.autolayout']:
        #    self.figure.tight_layout()

        self.canvas.draw()
        self.tabWidget.setCurrentIndex(0)

        """
        The plot is shown in the canvas. 
        Now close the figure to prevent it from being plotted again by plt.show() when choosing tsplot or xyplot
        The plt.close(self.secfig) closes reference to self.secfig 
        and it will not be plotted by plt.show() - but the plot exists in self.canvas
        Please note, this do not work completely as expected under windows. 
        """

        plt.close(self.figure)#this closes reference to self.secfig

    def update_legend(self):
        if self.ms.settingsdict['secplotlegendplotted']:  # Include legend in plot
            # skipped_bars is self-variable just to make it easily available for tests.
            self.skipped_bars = [p for p in self.p if not getattr(p, 'skip_legend', False)]
            legend_kwargs = dict(self.secplot_templates.loaded_template['legend_Axes_legend'])

            leg = self.axes.legend(self.skipped_bars, self.labels, **legend_kwargs)

            try:
                leg.set_draggable(state=True)
            except AttributeError:
                # For older version of matplotlib
                leg.draggable(state=True)
            leg.set_zorder(999)
            frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor(self.secplot_templates.loaded_template['legend_Frame_set_facecolor'])
            # set the frame face color to white
            frame.set_fill(self.secplot_templates.loaded_template['legend_Frame_set_fill'])
            for t in leg.get_texts():
                t.set_fontsize(self.secplot_templates.loaded_template['legend_Text_set_fontsize'])

    def get_dem_selection(self):
        self.rasterselection = []
        for item in self.inData.selectedItems():
            self.rasterselection.append(item.text())
                
    def get_length_along(self,obsidtuple):#returns a numpy recarray with attributes obs_id and length 
        #------------First a sql clause that returns a table, but that is not what we need

        sql = """SELECT p.obsid, ST_Length((SELECT geometry FROM %s)) * ST_Line_Locate_Point((SELECT geometry FROM %s), p.geometry) AS absdist FROM obs_points AS p
                  WHERE p.obsid in %s
                  ORDER BY absdist"""%(self.temptable_name, self.temptable_name, '({})'.format(', '.join(["'{}'".format(o) for o in obsidtuple])))
        try:
            data = self.dbconnection.execute_and_fetchall(sql)
        except:
            if 'UndefinedFunction' in traceback.format_exc():
                sql = sql.replace('ST_Line_Locate_Point', 'ST_LineLocatePoint')
                data = self.dbconnection.execute_and_fetchall(sql)
            else:
                raise


        data = ru(data, keep_containers=True)
        #data = [[col.encode('utf-8') for col in row] for row in ru(data, keep_containers=True)]
        #data = midvatten_utils.sql_load_fr_db(sql)[1]
        My_format = [('obs_id', np.unicode_, 32),('length', float)] #note that here is a limit of maximum 32 characters in obsid
        npdata = np.array(data, dtype=My_format)  #NDARRAY
        LengthAlongTable=npdata.view(np.recarray)   # RECARRAY   Makes the two columns into callable objects, i.e. write self.LengthAlong.obs_id and self.LengthAlong.length
        del data, npdata
        return LengthAlongTable

    def get_plot_data_geo(self):#this is called when class is instantiated, collecting data specific for the profile line layer and the obs_points
        common_utils.start_waiting_cursor()#show the user this may take a long time...
        if len(self.selected_obsids) > 0:
            self.plotx = {}
            self.plotbottom = {}
            self.plotbarlength = {}
            l = 0  # counter fro unique obs, stratid and typ
            self.x_txt = []  # used by self.WriteAnnotation
            self.z_txt = []  # used by self.WriteAnnotation
            self.x_id = []  # used by self.write_obsid
            self.z_id = []  # used by self.write_obsid
            self.barlengths = []  # used by self.write_obsid, not to be mixed with "BarLength" used locally in this function
            self.bottoms = []  # used by self.write_obsid, not to be mixed with "Bottom" used locally in this function
            self.PlotTypes = defs.PlotTypesDict()
            # print(self.PlotTypes)  # debug
            self.ExistingPlotTypes = []
            self.Hatches = defs.PlotHatchDict()
            self.Colors = defs.PlotColorDict()
            self.hydroColors = defs.hydrocolors()
            # print(self.Colors)  # debug

            # self.ms.settingsdict['secplotbw'] = self.barwidthdoubleSpinBox.value()
            # fix Floating Bar Width in percents of xmax - xmin
            # xmax, xmin =float(max(self.LengthAlong)), float(min(self.LengthAlong))
            # self.barwidth = (self.ms.settingsdict['secplotbw']/100.0)*(xmax -xmin)

            for Typ in self.PlotTypes:  # Adding a plot for each "geoshort" that is identified
                i = 0  # counter for unique obs and stratid
                k = 0  # counter for unique Typ
                q = 0  # counter for unique obsid (only used in first Typ-loop)
                x = []
                z_gs = []
                BarLength = []  # stratigraphy bar length
                Bottom = []  # stratigraphy bottom
                Capacity = '0'
                for obs in self.selected_obsids:
                    if k <= len(self.selected_obsids):  # in first Typ-loop, get obs_points data - used for plotting obsid
                        self.x_id.append(float(self.length_along[q]))
                        sql = "SELECT h_toc, h_gs, length FROM obs_points WHERE obsid = '%s'"%obs
                        recs = db_utils.sql_load_fr_db(sql, self.dbconnection)[1]
                        if common_utils.isfloat(str(recs[0][1])) and recs[0][1]>-999:
                            self.z_id.append(recs[0][1])
                        elif common_utils.isfloat(str(recs[0][0])) and recs[0][0]>-999:
                            self.z_id.append(recs[0][0])
                            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('SectionPlot',
                                    "Obsid %s: using h_gs '%s' failed, using '%s' instead.")) % (
                                    obs, str(recs[0][1]), 'h_toc'))
                        else:
                            self.z_id.append(0)
                            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('SectionPlot',
                                "Obsid %s: using h_gs %s or h_toc %s failed, using 0 instead.")) % (
                                                                       obs, str(recs[0][1]), str(recs[0][0])))

                        if common_utils.isfloat(str(recs[0][2])):
                            self.barlengths.append(recs[0][2])
                        else:
                            self.barlengths.append(0)
                        self.bottoms.append(self.z_id[q]-self.barlengths[q])

                        q +=1
                        del recs

                    sql="""SELECT depthbot - depthtop, stratid, geology, geoshort, capacity, development, comment FROM stratigraphy WHERE obsid = '%s' AND lower(geoshort) %s ORDER BY stratid"""%(obs, self.PlotTypes[Typ])
                    _recs = db_utils.sql_load_fr_db(sql, self.dbconnection)[1]
                    if _recs:
                        recs = _recs
                        j=0#counter for unique stratid
                        Capacity = '0'
                        for rec in recs:#loop cleanup
                            BarLength.append(rec[0])#loop cleanup
                            x.append(float(self.length_along[k]))# - self.barwidth/2)
                            sql01 = "select h_gs from obs_points where obsid = '%s'"%obs
                            sql01_result = db_utils.sql_load_fr_db(sql01, self.dbconnection)[1][0][0]
                            sql02 = "select h_toc from obs_points where obsid = '%s'"%obs
                            sql02_result = db_utils.sql_load_fr_db(sql02, self.dbconnection)[1][0][0]
                            # print('h_gs for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql01)[1])[0][0]))#debug
                            # print('h_toc for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql02)[1])[0][0]))#debug

                            if common_utils.isfloat(str(sql01_result)) and sql01_result >-999:
                                z_gs.append(float(str(sql01_result)))
                            elif common_utils.isfloat(str(sql02_result)) and sql02_result>-999:
                                z_gs.append(float(str(sql02_result)))
                            else:
                                z_gs.append(0)
                            Bottom.append(z_gs[i] - float(str((
                                                              db_utils.sql_load_fr_db("""SELECT depthbot FROM stratigraphy WHERE obsid = '%s' AND stratid = %s AND lower(geoshort) %s""" % (obs, str(recs[j][1]), self.PlotTypes[Typ]), self.dbconnection)[1])[0][0])))
                            #lists for plotting annotation
                            self.x_txt.append(x[i])#+ self.barwidth/2)#x-coord for text
                            self.z_txt.append(Bottom[i] + recs[j][0]/2)#Z-value for text
                            self.geology_txt.append(common_utils.null_2_empty_string(ru(recs[j][2])))
                            self.geoshort_txt.append(common_utils.null_2_empty_string(ru(recs[j][3])))
                            self.capacity_txt.append(common_utils.null_2_empty_string(ru(recs[j][4])))
                            self.development_txt.append(common_utils.null_2_empty_string(ru(recs[j][5])))
                            self.comment_txt.append(common_utils.null_2_empty_string(ru(recs[j][6])))
                            # print obs + " " + Typ + " " + self.geology_txt[l] + " "
                            # + self.geoshort_txt[l] + " " + self.capacity_txt[l] + " "
                            # + self.development_txt[l] + " " + self.comment_txt[l]  # debug

                            self.hydro_explanation_txt = []
                            for capacity_txt in self.capacity_txt:
                                if capacity_txt is None or capacity_txt == '':
                                    self.hydro_explanation_txt.append('')
                                else:
                                    self.hydro_explanation_txt.append(self.hydroColors.get(capacity_txt, [' '])[0])

                            i += 1
                            j += 1
                            l += 1
                        del recs
                        self.obsid_annotation[obs] = (self.x_id[-1], self.z_id[-1])
                    k +=1
                if len(x)>0:
                    self.ExistingPlotTypes.append(Typ)
                    self.plotx[Typ] = x
                    self.plotbottom[Typ] = Bottom
                    self.plotbarlength[Typ] = BarLength

        common_utils.stop_waiting_cursor()#now this long process is done and the cursor is back as normal

    def get_plot_data_2(self):
        self.obsid_wlid = []  # if no stratigr plot, obsid will be plotted close to water level instead of toc or gs
        self.x_id_wwl = []
        self.z_id_wwl = []
        self.obs_p_w_drill_stops = []
        self.drill_stops = []
        self.x_ds = []
        self.z_ds = []

        if self.ms.settingsdict['secplotdrillstop']!='':
            query = """select obsid from obs_points where lower(drillstop) like '%s'"""%ru(self.ms.settingsdict['secplotdrillstop'])
            result = db_utils.sql_load_fr_db(query, self.dbconnection)
            if result[1]:
                for item in result[1]:
                    self.obs_p_w_drill_stops.append(item[0])

        q=0

        # The priority should be like this:
        # 1. If stratigraphy exists, then plot obsid at h_toc or h-gs
        # 2. If only waterlevel exist, then plot obsid at waterlevel

        for obs in self.selected_obsids:#Finally adding obsid at top of stratigraphy
            labellevel = None
            if self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates'])>0 and self.ms.settingsdict['secplotwlvltab']:
                query = """select avg(level_masl) from """ + self.ms.settingsdict['secplotwlvltab'] + r""" where obsid = '""" + obs + r"""' and ((date_time >= '""" + min(self.ms.settingsdict['secplotdates']) + r"""' and date_time <= '""" + max(self.ms.settingsdict['secplotdates']) + r"""') or (date_time like '""" + min(self.ms.settingsdict['secplotdates']) + r"""%' or date_time like '""" + max(self.ms.settingsdict['secplotdates']) + r"""%'))"""
                #print(query)#debug
                worked, recs = db_utils.sql_load_fr_db(query, self.dbconnection)
                if worked and recs:
                    if common_utils.isfloat(str(recs[0][0])) and recs[0][0]>-999:
                        labellevel = recs[0][0]
                del recs

            if labellevel is None:
                worked, recs = db_utils.sql_load_fr_db('''SELECT h_toc, h_gs, h_tocags FROM obs_points WHERE obsid = '{}' '''.format(obs), self.dbconnection)
                if worked and recs:
                    row = recs[0]
                    try:
                        labellevel = float(row[1])
                    except (ValueError, TypeError):
                        if row[0] is not None and row[2] is not None:
                            try:
                                labellevel = float(row[0]) - float(row[2])
                            except (ValueError, TypeError):
                                if row[0] is not None:
                                    try:
                                        labellevel = float(row[0])
                                    except (ValueError, TypeError):
                                        pass

            if labellevel is None:
                labellevel = 0

            self.z_id_wwl.append(labellevel)
            self.obsid_wlid.append(obs)
            self.x_id_wwl.append(float(self.length_along[q]))
                    
            if obs in self.obs_p_w_drill_stops:
                self.x_ds.append(float(self.length_along[q]))
                self.z_ds.append(float(self.bottoms[q]))
            q += 1

    def get_plot_data_hydro(self):  # called when class is instantiated collecting data for profile line layer & obs_points
        common_utils.start_waiting_cursor()

        if len(self.selected_obsids) > 0:
            self.plotx_h = {}
            self.plotbottom_h = {}
            self.plotbarlength_h = {}
            l = 0  # counter fro unique obs, stratid and typ
            self.ExistingHydroTypes = []
            self.hydroColors = defs.hydrocolors()

            for capacity in self.hydroColors.keys():  # Adding a plot for each "capacity" that is identified
                i = 0  # counter for unique obs and stratid
                k = 0  # counter for unique Typ
                q = 0  # counter for unique obsid (only used in first Typ-loop)

                x = []
                z_gs = []
                BarLength = []  # stratigraphy bar length
                Bottom = []  # stratigraphy bottom

                for obs in self.selected_obsids:
                    if k <= len(self.selected_obsids):  # in first Typ-loop, get obs_points data - used for plotting obsid
                        q += 1

                    #   del recs
                    if capacity is None or capacity == '':
                        sql = u"""SELECT depthbot - depthtop, stratid, capacity FROM stratigraphy WHERE obsid = '%s' AND capacity is NULL ORDER BY stratid""" % obs
                    else:
                        sql = u"""SELECT depthbot - depthtop, stratid, capacity FROM stratigraphy WHERE obsid = '%s' AND capacity = '%s' ORDER BY stratid""" % (obs, capacity)

                    _recs = db_utils.sql_load_fr_db(sql, self.dbconnection)[1]
                    if _recs:
                        recs = _recs
                        j = 0  # counter for unique stratid

                        for rec in recs:  # loop cleanup
                            BarLength.append(rec[0])  # loop cleanup
                            x.append(float(self.length_along[k]))  # - self.barwidth/2)

                            sql01 = u"select h_gs from obs_points where obsid = '%s'" % obs
                            sql01_result = db_utils.sql_load_fr_db(sql01, self.dbconnection)[1][0][0]
                            sql02 = u"select h_toc from obs_points where obsid = '%s'" % obs
                            sql02_result = db_utils.sql_load_fr_db(sql02, self.dbconnection)[1][0][0]

                            # print('h_gs for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql01)[1])[0][0]))#debug

                            # print('h_toc for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql02)[1])[0][0]))#debug

                            if common_utils.isfloat(str(sql01_result)) and sql01_result > -999:
                                z = float(str(sql01_result))
                            elif common_utils.isfloat(str(sql02_result)) and sql02_result > -999:
                                z = float(str(sql02_result))
                            else:
                                z = 0
                            z_gs.append(z)

                            if capacity is None or capacity == '':
                                Bottom.append(z_gs[i] - float(str((

                                                                      db_utils.sql_load_fr_db(

                                                                          """SELECT depthbot FROM stratigraphy WHERE obsid = '%s' AND stratid = %s AND capacity is NULL""" % (

                                                                              obs, str(recs[j][1])),

                                                                          self.dbconnection)[1])[0][0])))

                            else:

                                Bottom.append(z_gs[i] - float(str((

                                                                  db_utils.sql_load_fr_db(

                             """SELECT depthbot FROM stratigraphy WHERE obsid = '%s' AND stratid = %s AND capacity = '%s'""" % (

                                                                      obs, str(recs[j][1]), capacity),

                                                                      self.dbconnection)[1])[0][0])))

                            # lists for plotting annotation

                            self.x_txt.append(x[i])  # + self.barwidth/2)#x-coord for text

                            self.z_txt.append(Bottom[i] + recs[j][0] / 2)  # Z-value for text

                            self.capacity_txt.append(common_utils.null_2_empty_string(ru(recs[j][2])))

                            self.hydro_explanation_txt = []

                            for capacity_txt in self.capacity_txt:

                                if capacity_txt is None or capacity_txt == '':

                                    self.hydro_explanation_txt.append('')

                                else:

                                    self.hydro_explanation_txt.append(self.hydroColors.get(capacity_txt, [' '])[0])

                            i += 1

                            j += 1

                            l += 1

                        del recs
                    k += 1

                if len(x) > 0:

                    self.ExistingHydroTypes.append(capacity)

                    self.plotx_h[capacity] = x

                    self.plotbottom_h[capacity] = Bottom

                    self.plotbarlength_h[capacity] = BarLength

        common_utils.stop_waiting_cursor()

    def get_selected_dems_params(self, dialog):
        selected_dems = []
        selected_dem_colors = [] 
        for dem_qgis_ndx in range( dialog.listDEMs_treeWidget.topLevelItemCount () ):
            curr_DEM_item = dialog.listDEMs_treeWidget.topLevelItem ( dem_qgis_ndx ) 
            if curr_DEM_item.checkState(0) == 2:
                selected_dems.append( dialog.singleband_raster_layers_in_project[ dem_qgis_ndx ] )
                selected_dem_colors.append(dialog.listDEMs_treeWidget.itemWidget( curr_DEM_item, 1 ).currentText() )
        return selected_dems, selected_dem_colors

    def plot_dems(self):
        try:
            if self.ms.settingsdict['secplotselectedDEMs'] and len(self.ms.settingsdict['secplotselectedDEMs'])>0:    # Adding a plot for each selected raster
                for layername in self.ms.settingsdict['secplotselectedDEMs']:
                    #TODO: This should be a setting in the gui for each dem layer instead of hardcoded
                    distance = self.barwidth / 2.0
                    if not distance:
                        distance = max([feat for feat in self.sectionlinelayer.getSelectedFeatures()][0].geometry().length()/ 5000, 1)

                    temp_memorylayer, xarray = qchain(self.sectionlinelayer, distance)
                    DEMdata = sampling(temp_memorylayer,self.rastItems[str(layername)])
                    plotlable = self.get_plot_label_name(layername, self.labels)
                    settings = self.secplot_templates.loaded_template['dems_Axes_plot'].get(plotlable,
                                                                                     self.secplot_templates.loaded_template['dems_Axes_plot']['DEFAULT'])
                    self.secplot_templates.loaded_template['dems_Axes_plot'][plotlable] = copy.deepcopy(settings)
                    settings = self.secplot_templates.loaded_template['dems_Axes_plot'][plotlable]
                    settings['label'] = settings.get('label', plotlable)
                    self.labels.append(settings['label'])
                    settings['picker'] = 2
                    lineplot, = self.axes.plot(xarray, DEMdata, **settings)  # The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1
                    self.p.append(lineplot)

                    #TODO: This feature should have settings in gui to activate grading for the current layer.
                    grade_layer = False
                    if grade_layer:
                        #TODO: These settings should be in gui in some way.
                        polylayer_name = 'polylager_with_color'
                        alpha_max = 0.5
                        alpha_min = 0
                        number_of_plots = 20
                        graded_depth_m = 2
                        skip_labels = []
                        self.plot_graded_dems(temp_memorylayer, xarray, DEMdata, polylayer_name, alpha_max=alpha_max, alpha_min=alpha_min, number_of_plots=number_of_plots, graded_depth_m=graded_depth_m, skip_labels=skip_labels)
                    QgsProject.instance().removeMapLayer(temp_memorylayer.id())
        except:
            raise
        finally:
            try:
                QgsProject.instance().removeMapLayer(temp_memorylayer.id())
            except:
                pass

    def plot_graded_dems(self, temp_memorylayer, xarray, DEMdata, poly_layer_name, alpha_max=0.5, alpha_min=0, number_of_plots=20, graded_depth_m=2, skip_labels=None):
        poly_layer = common_utils.find_layer(poly_layer_name)
        points_srid = temp_memorylayer.crs().authid()
        poly_layer_srid = poly_layer.crs().authid()
        if points_srid != poly_layer_srid:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('SectionPlot', "Grade dem: Layer %s had wrong srid! Had '%s' but should have '%s'.")) % (poly_layer_name, str(poly_layer_srid), str(points_srid)))
            return None
        polylabels_colors = self.sample_polygon(temp_memorylayer, poly_layer)

        plot_spec = []
        _x = []
        _y = []
        prev_label = None
        for idx, polylabel_color in enumerate(polylabels_colors):
            polylabel = polylabel_color[0]
            _x.append(xarray[idx])
            _y.append(DEMdata[idx])
            if prev_label is not None and prev_label != polylabel:
                plot_spec.append([prev_label, _x, _y])
                _x = [xarray[idx]]
                _y = [DEMdata[idx]]
            prev_label = polylabel
        else:
            plot_spec.append([prev_label, _x, _y])

        labels_colors = {lbl: color for lbl, color in polylabels_colors}

        plotted_polylabels = set()
        for label, x_vals, y_vals in plot_spec:
            if skip_labels and label in skip_labels:
                continue

            plotlable = self.get_plot_label_name('{} {}'.format(poly_layer_name, label), self.labels)
            graded_plot_height = float(graded_depth_m) / float(number_of_plots)
            color = labels_colors[label]

            gradients = np.linspace(alpha_max, alpha_min, number_of_plots)
            for grad_idx, grad in enumerate(gradients):
                y1 = [_y - graded_plot_height for _y in y_vals]
                theplot = self.axes.fill_between(x_vals, y1, y_vals, alpha=grad, facecolor=color, linewidth=0)

                if label not in plotted_polylabels:
                    self.p.append(theplot)
                    self.labels.append(plotlable)
                    plotted_polylabels.add(label)
                y_vals = list(y1)

    def plot_drill_stop(self):
        settings = copy.deepcopy(self.secplot_templates.loaded_template['drillstop_Axes_plot'])
        label = settings.get('label', None)
        if label is None:
            label = 'drillstop like ' + self.ms.settingsdict['secplotdrillstop']
        self.labels.append(label)
        settings['label'] = label
        settings['picker'] = 2
        lineplot,=self.axes.plot(self.x_ds, self.z_ds, **settings)
        self.p.append(lineplot)

    def get_plot_label_name(self, label, labels):
        label_occurence = labels.count(label)
        if not label_occurence:
            return label
        else:
            return label + '_' + str(label_occurence + 1)

    def plot_geology(self):
        for Typ in self.ExistingPlotTypes:#Adding a plot for each "geoshort" that is identified
            #Try to get one setting per geoshort.
            _settings = copy.deepcopy(self.secplot_templates.loaded_template['geology_Axes_bar'])
            try:
                settings = _settings[Typ]
            except KeyError:
                try:
                    settings = _settings['DEFAULT']
                except KeyError:
                    settings = _settings

            for _Typ in self.ExistingPlotTypes:
                try:
                    del settings[_Typ]
                except KeyError:
                    pass
            try:
                del settings['DEFAULT']
            except KeyError:
                pass

            settings['width'] = settings.get('width', self.barwidth)
            settings['color'] = settings.get('color', self.Colors[Typ])
            settings['hatch'] = settings.get('hatch', self.Hatches[Typ])

            plotxleftbarcorner = [float(i) - float(settings['width'])/2.0 for i in self.plotx[Typ]]#subtract half bar width from x position (x position is stored as bar center in self.plotx)
            self.p.append(self.axes.bar(plotxleftbarcorner, self.plotbarlength[Typ], bottom=self.plotbottom[Typ], align='edge', **settings))#matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)
            self.labels.append(Typ)

    def plot_hydrology(self):
        for capacity_txt in self.ExistingHydroTypes:  # Adding a plot for each "capacity" that is identified
            # Try to get one setting per capacity.
            _settings = copy.deepcopy(self.secplot_templates.loaded_template['geology_Axes_bar'])
            try:
                settings = _settings[capacity_txt]
            except KeyError:
                try:
                    settings = _settings['DEFAULT']
                except KeyError:
                    settings = _settings

            for _capacity_txt in self.ExistingHydroTypes:
                try:
                    del settings[_capacity_txt]
                except KeyError:
                    pass

            try:
                del settings['DEFAULT']
            except KeyError:
                pass

            settings['width'] = settings.get('width', self.barwidth)
            settings['color'] = settings.get('color_qt', self.hydroColors[capacity_txt][1])

            plotx_hleftbarcorner = [float(i) - float(settings['width']) / 2.0 for i in self.plotx_h[capacity_txt]] #subtract half bar width from x position (x position is stored as bar center in self.plotx)
            try:
                self.p.append(self.axes.bar(plotx_hleftbarcorner, self.plotbarlength_h[capacity_txt], bottom=self.plotbottom_h[capacity_txt], align='edge', **settings))#matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)
            except Exception as e:
                common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('Sectionplot', 'Capacity %s color %s could not be plotted. Default to white!. See message log')) % (str(capacity_txt), settings['color']),
                                                               log_msg=str(e))
                settings['color'] = 'white'
                self.p.append(self.axes.bar(plotx_hleftbarcorner, self.plotbarlength_h[capacity_txt], bottom=self.plotbottom_h[capacity_txt], align='edge', **settings))  # matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)

            self.labels.append(capacity_txt)

    def plot_obs_lines_data(self):
        plotlable = self.get_plot_label_name(self.y1_column, self.labels)
        self.labels.append(self.y1_column)

        def remove_nones(xdata, ydata):
            x_y = [(xdata[idx], row) for idx, row in enumerate(ydata) if not np.isnan(row)]
            x = [row[0] for row in x_y]
            y = [row[1] for row in x_y]
            return x, y

        x, y = remove_nones(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y1)
        lineplot, = self.axes.plot(x, y, picker=2, marker ='+', linestyle ='-', label=plotlable)# PLOT!!
        self.p.append(lineplot)

        plotlable = self.get_plot_label_name(self.y2_column, self.labels)
        self.labels.append(self.y2_column)
        x, y = remove_nones(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y2)
        lineplot, = self.axes.plot(x, y, picker=2, marker ='+', linestyle ='-', label=plotlable)# PLOT!!
        self.p.append(lineplot)

        plotlable = self.get_plot_label_name(self.y3_column, self.labels)
        self.labels.append(self.y3_column)
        x, y = remove_nones(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y3)
        lineplot, = self.axes.plot(x, y, picker=2, marker ='+', linestyle ='-', label=plotlable)# PLOT!!
        self.p.append(lineplot)

    def plot_water_level(self):   # Adding a plot for each water level date identified
        if not self.ms.settingsdict['secplotwlvltab']:
            return
        if self.specific_dates_groupbox.isChecked():
            if self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates']) > 0:  # PLOT Water Levels
                self.plot_specific_water_level()
        if self.interactive_groupbox.isChecked():
            self.plot_water_level_interactive()

    def plot_water_level_interactive(self):
        sql = '''SELECT date_time, level_masl, obsid FROM {} WHERE obsid IN ({})'''.format(self.ms.settingsdict['secplotwlvltab'], common_utils.sql_unicode_list(self.selected_obsids))
        self.df = pd.read_sql(sql,
                         self.dbconnection.conn, index_col='date_time', coerce_float=True, params=None, parse_dates=['date_time'],
                         columns=None,
                         chunksize=None)

        if isinstance(self.df, pd.Series):
            self.df = self.df.to_frame()

        self.df = self.df.reset_index()
        self.df = self.df.pivot(index='date_time', columns='obsid', values='level_masl')

        resample_kwargs = {'how': self.resample_how.text(), 'axis': 0, 'convention': 'start',
                           'base': int(self.resample_base.text())}

        self.df = resample(self.df, None, self.resample_rule.text(), resample_kwargs)

        if self.skip_nan.isChecked():
            self.df = self.df.dropna()

        #The slider should update after user pan.
        valuemin = 0
        valuemax = len(self.df)-1
        valinit = valuemin
        #valstep = 1
        self.wlvl_axes = self.figure.add_subplot(self.gridspec[0:1, 1:2])
        self.df.plot(ax=self.wlvl_axes, picker=2)
        self.wlvl_axes.set_xlabel('')

        #Axes_set_ylabel = dict([(k, v) for k, v in self.secplot_templates.loaded_template.get('Axes_set_ylabel', {}).items() if k != 'ylabel'])
        #ylabel = self.secplot_templates.loaded_template.get('Axes_set_ylabel', {}).get('ylabel', defs.secplot_default_template()['Axes_set_ylabel']['ylabel'])
        #self.wlvl_axes.set_ylabel(ylabel, **Axes_set_ylabel)  #Allows international characters ('åäö') as ylabel
        self.wlvl_axes.set_ylabel('')

        for label in self.wlvl_axes.yaxis.get_ticklabels():
            label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])

        for label in self.wlvl_axes.xaxis.get_ticklabels():
            label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])

        self.sliderax = self.figure.add_subplot(self.gridspec[1:2, 1:2])
        self.date_slider = Slider(self.sliderax, 'Date', valuemin, valuemax, valinit=valinit, valfmt='%1.0f')

        self.axvline = self.wlvl_axes.axvline(df_idx_as_datetime(self.df, valinit), color='black', linewidth=2, linestyle='--') # mdates.date2num(df_idx_as_datetime(self.df, valinit)))

        self.date_slider.on_changed(self.update_animation)
        current_idx = self.get_slider_idx()
        x_wl, WL = self.get_water_levels_from_df(self.df, current_idx, self.selected_obsids, self.length_along)
        self.animation_label_idx = len(self.labels)
        self.waterlevel_lineplot(x_wl, WL, longdateformat(df_idx_as_datetime(self.df, current_idx)))

        self.canvas.mpl_connect('draw_event', self.update_slider)

    def get_slider_idx(self):
        return int(round(self.date_slider.val, 0))

    def get_water_levels_from_df(self, df, idx, columns, length_along):
        WL = []
        x_wl = []
        for k, col in enumerate(columns):

            try:
                val = df.iloc[[idx]][col]
            except KeyError:
                continue
            except TypeError:
                try:
                    _col = col.encode('utf8').decode('utf8')
                except Exception as e:
                    common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate("Sectionplot: Encoding string failed for %s")) % ru(col))
                    continue
                else:
                    try:
                        val = df.iloc[[idx]][_col]
                    except KeyError:
                        continue

            WL.append(val)
            x_wl.append(float(length_along[k]))
            if col not in self.obsid_annotation or not any([self.ms.settingsdict['stratigraphyplotted'],
                                                            self.ms.settingsdict['secplothydrologyplotted']]):
                self.obsid_annotation[col] = (x_wl[-1], WL[-1])
        return x_wl, WL

    def update_animation(self, datevalue):
        current_idx = self.get_slider_idx()
        x_wl, WL = self.get_water_levels_from_df(self.df, current_idx, self.selected_obsids, self.length_along)
        if self._waterlevel_lineplot is not None and self.df is not None:
            self._waterlevel_lineplot.set_ydata(WL)
            self.axvline.set_xdata(df_idx_as_datetime(self.df, current_idx))
            self.canvas.draw_idle()
            self.labels[self.animation_label_idx] = longdateformat(df_idx_as_datetime(self.df, current_idx))
            self.update_legend()

    def update_slider(self, event):
        xmin, xmax = self.wlvl_axes.get_xlim()
        # For some reason, matplotlib gives me days from 1970 instead of from 1900.
        _1970 = mdates.date2num(datetime.date(1970, 1, 1))
        xmin_1970 = _1970 + int(round(xmin, 0))
        xmax_1970 = _1970 + int(round(xmax, 0))

        min_date = mdates.num2date(xmin_1970).replace(tzinfo=None)
        max_date = mdates.num2date(xmax_1970).replace(tzinfo=None)
        min_idx = self.df.index.get_loc(min_date, method='backfill')
        max_idx = self.df.index.get_loc(max_date, method='pad')

        prev_val = self.date_slider.val
        self.date_slider.valmin = min_idx
        self.date_slider.valmax = max_idx
        if prev_val > max_idx:
            newval = max_idx
        elif prev_val < min_idx:
            newval = min_idx
        else:
            newval = prev_val
        self.date_slider.valinit = newval
        self.date_slider.reset()
        self.sliderax.set_xlim(left=min_idx, right=max_idx)

    def plot_specific_water_level(self):

        for _datum in self.ms.settingsdict['secplotdates']:
            datum_obsids = _datum.split(';')
            datum = datum_obsids[0]
            WL = []
            x_wl = []
            for k, obs in enumerate(self.selected_obsids):
                if len(datum_obsids) > 1:
                    if obs not in datum_obsids[1:]:
                        continue

                # TODO: There should probably be a setting for using avg(level_masl)
                query = """SELECT level_masl FROM {} WHERE obsid = '{}' AND date_time like '{}%'""".format(
                    self.ms.settingsdict['secplotwlvltab'], obs, datum)
                # query = """SELECT avg(level_masl) FROM {} WHERE obsid = '{}' AND date_time like '{}%'""".format(self.ms.settingsdict['secplotwlvltab'], obs, datum)
                res = db_utils.sql_load_fr_db(query, self.dbconnection)[1]
                try:
                    val = res[0][0]
                except IndexError:
                    continue
                if val is None:
                    continue

                WL.append(val)
                x_wl.append(float(self.length_along[k]))
                if obs not in self.obsid_annotation or not any([self.ms.settingsdict['stratigraphyplotted'],
                                                                self.ms.settingsdict['secplothydrologyplotted']]):
                    self.obsid_annotation[obs] = (x_wl[-1], WL[-1])
            self.waterlevel_lineplot(x_wl, WL, datum)


    def waterlevel_lineplot(self, x_wl, WL, datum):
        plotlable = self.get_plot_label_name(datum, self.water_level_labels_duplicate_check)
        self.water_level_labels_duplicate_check.append(plotlable)
        settings = self.secplot_templates.loaded_template['wlevels_Axes_plot'].get(plotlable,
                                                                            self.secplot_templates.loaded_template[
                                                                           'wlevels_Axes_plot']['DEFAULT'])
        self.secplot_templates.loaded_template['wlevels_Axes_plot'][plotlable] = copy.deepcopy(settings)
        settings = self.secplot_templates.loaded_template['wlevels_Axes_plot'][plotlable]
        settings['label'] = settings.get('label', plotlable)
        self.labels.append(settings['label'])
        settings['picker'] = 2
        lineplot, = self.axes.plot(x_wl, WL, **settings)  # The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1
        self._waterlevel_lineplot = lineplot
        self.p.append(lineplot)

    def save_settings(self):# This is a quick-fix, should use the midvsettings class instead.
        self.ms.save_settings('secplotwlvltab')
        self.ms.save_settings('secplotdates')
        self.ms.save_settings('secplottext')
        self.ms.save_settings('secplotdrillstop')
        self.ms.save_settings('secplotbw')
        self.ms.save_settings('secplotlocation')
        self.ms.save_settings('secplotselectedDEMs')
        self.ms.save_settings('stratigraphyplotted')
        self.ms.save_settings('secplotlabelsplotted')
        self.ms.save_settings('secplotwidthofplot')
        self.ms.save_settings('secplotincludeviews')
        self.ms.save_settings('secplotlegendplotted')

        #Don't save plot min/max for next plot. If a specific is to be used, it should be set in a saved template file.
        loaded_template = copy.deepcopy(self.secplot_templates.loaded_template)
        loaded_template["Axes_set_xlim"] = None
        loaded_template["Axes_set_ylim"] = None
        common_utils.save_stored_settings(self.ms, loaded_template, 'secplot_loaded_template')
        self.ms.save_settings('secplot_templates')
        
    def set_location(self):#not ready
        dockarea = self.parent.dockWidgetArea(self)
        self.ms.settingsdict['secplotlocation']=dockarea

    def upload_qgis_vector_layer(self, layer, srid=None,selected=False, mapinfo=True,Attributes=False): #from qspatialite, with a few  changes LAST ARGUMENT IS USED TO SKIP ARGUMENTS SINCE WE ONLY WANT THE GEOMETRY TO CALCULATE DISTANCES
        """Upload layer (QgsMapLayer) (optionnaly only selected values ) into current DB, in self.temptable_name (string) with desired SRID (default layer srid if None) - user can desactivate mapinfo compatibility Date importation. Return True if operation succesfull or false in all other cases"""

        #Upload a selected feature into a table. If spatialite, make it a memory table, if postgis make it temporary.
        #upload two fields only, one id field set to dummy and one geometry field.

        selected_features = [f for f in layer.getSelectedFeatures()]
        if len(selected_features) != 1:
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('SectionPlot', "Must select only one feature in qgis layer: %s)")) % layer.name())
            return False

        """
        qgis geometry types:
        0 = MULTIPOINT,
        1 = MULTILINESTRING,
        2 = MULTIPOLYGON,
        3 = UnknownGeometry,
        4 = ?
        """
        try:
            if layer.geometryType() != 1:
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('SectionPlot', "Layer %s is missing geometry type MULTILINESTRING, had %s")) % (layer.name(), str(layer.geometryType())))
                return False
        except:
            common_utils.MessagebarAndLog.critical(
                bar_msg=ru(QCoreApplication.translate('SectionPlot', "Layer %s is not MultiLineString geometry")) % layer.name())
            return False

        self.temptable_name = self.dbconnection.create_temporary_table_for_import(self.temptable_name, ['dummyfield TEXT'], ['geometry', 'LINESTRING', srid])

        feature = selected_features[0]

        geom = feature.geometry()
        geom_linestring = geom.convertToType(1)
        wkt = geom_linestring.asWkt()
        sql = """INSERT INTO %s (dummyfield, geometry) VALUES ('0', ST_GeomFromText('%s', %s))"""%(self.temptable_name, wkt, srid)
        self.dbconnection.execute(sql)
        return True

    def write_annotation(self):
        if self.ms.settingsdict['secplottext'] == 'geology':
            annotate_txt = self.geology_txt
        elif self.ms.settingsdict['secplottext'] == 'geoshort':
            annotate_txt = self.geoshort_txt
        elif self.ms.settingsdict['secplottext'] == 'capacity':
            annotate_txt = self.capacity_txt
        elif self.ms.settingsdict['secplottext'] == 'hydroexplanation':
            annotate_txt = self.hydro_explanation_txt
        elif self.ms.settingsdict['secplottext'] == 'development':
            annotate_txt = self.development_txt
        else:
            annotate_txt = self.comment_txt
        for m, n, o in zip(self.x_txt, self.z_txt, annotate_txt):  # change last arg to the one to be written in plot
            self.annotationtext = self.axes.annotate(o, xy=(m, n), **self.secplot_templates.loaded_template['layer_Axes_annotate'])#textcoords = 'offset points' makes the text being written xytext points from the data point xy (xy positioned with respect to axis values and then the text is offset a specific number of points from that point

    def write_obsid(self, plot_labels=True):  # annotation, and also empty bars to show drillings without stratigraphy data
        if self.ms.settingsdict['stratigraphyplotted'] or self.ms.settingsdict['secplothydrologyplotted']:
            # if stratigr plot, then obsid written close to toc or gs
            plotxleftbarcorner = [i - self.barwidth/2 for i in self.x_id]#x-coord for bars at each obs

            indexes_barlength_not_0 = [idx for idx, length in enumerate(self.barlengths) if length]

            plotxleftbarcorner = [plotxleftbarcorner[idx] for idx in indexes_barlength_not_0]
            bottoms = [self.bottoms[idx] for idx in indexes_barlength_not_0]
            barlengths = [self.barlengths[idx] for idx in indexes_barlength_not_0]

            obsid_Axes_bar = copy.deepcopy(self.secplot_templates.loaded_template['obsid_Axes_bar'])
            obsid_Axes_bar['width'] = obsid_Axes_bar.get('width', self.barwidth)
            obsid_Axes_bar['bottom'] = obsid_Axes_bar.get('bottom', bottoms)
            #plot empty bars
            p = self.axes.bar(plotxleftbarcorner, barlengths, align='edge', **obsid_Axes_bar)
            p.skip_legend = True
            self.p.append(p)



        if plot_labels:
            for o, m_n in self.obsid_annotation.items():
                m, n = m_n
                #for m,n,o in zip(self.x_id,self.z_id,self.selected_obsids):#change last arg to the one to be written in plot
                text = self.axes.annotate(o, xy=(m, n), **self.secplot_templates.loaded_template['obsid_Axes_annotate'])

    def update_barwidths_from_plot(self):
        if not all((self.width_of_plot.isChecked(), len(self.selected_obsids) > 0)):
            return
        used_xmin, used_xmax = self.axes.get_xlim()
        total_width = float(used_xmax) - float(used_xmin)
        barwidth = total_width * float(self.ms.settingsdict['secplotbw']) * 0.01
        for p in self.p:
            if isinstance(p, container.BarContainer):
                children = p.get_children()
                for child in children:
                    if isinstance(child, patches.Rectangle):
                        prev_middle = child.get_x() + child.get_width()/2
                        child.set_width(barwidth)
                        child.set_x(prev_middle - child.get_width()/2)

    def sample_polygon(self, pointLayer, polyLayer):
        """
        Code reused from PointSamplingTool

        Hard coded to use the last intersecting feature if there are multiple.
        Hard coded to use the color from the bottom symbol layer if there are multiple.

        :param pointLayer:
        :param polyLayer:
        :return:
        """
        #Styles
        polyProvider = polyLayer.dataProvider()
        renderer = polyLayer.renderer()
        category_column = renderer.classAttribute()
        categories = renderer.categories()

        # Category values are returned as strings.
        categoryvalue_symbol = {cat.value(): (cat.symbol(), cat.label()) for cat in categories}

        pointProvider = pointLayer.dataProvider()
        sampled_values = []

        for pointFeat in pointProvider.getFeatures():
            pointGeom = pointFeat.geometry()
            if pointGeom.wkbType() == QgsWkbTypes.MultiPoint:
                pointPoint = pointGeom.asMultiPoint()[0]
            else:
                pointPoint = pointGeom.asPoint()
            bBox = QgsRectangle(pointPoint.x() - 0.001, pointPoint.y() - 0.001, pointPoint.x() + 0.001,
                                pointPoint.y() + 0.001)  # reuseable rectangle buffer around the point feature

            pointGeom = QgsGeometry().fromPointXY(pointPoint)
            features = polyProvider.getFeatures(QgsFeatureRequest().setFilterRect(bBox))
            intersections = [iFeat for iFeat in features
                             if pointGeom.intersects(iFeat.geometry())]

            if len(intersections) == 0:
                sampled_values.append(None)
                continue
            else:
                # If there is two intersecting polygon features, then the last one will be used!
                feat = intersections[-1]
                feat_category_value = str(feat.attributes()[polyProvider.fieldNameIndex(category_column)])
                symbol = categoryvalue_symbol[feat_category_value][0]
                label = ru(categoryvalue_symbol[feat_category_value][1])
                symbol_layers = symbol.symbolLayers()
                #Use the bottom layer color
                _color = symbol_layers[0].properties()['color']
                color = tuple([float(c)/float(255) for c in _color.split(',')])
                sampled_values.append((label, color))

        return sampled_values


def resample(df, valuecol, rule, resample_kwargs):
    how = resample_kwargs.get('how', 'mean')
    del resample_kwargs['how']
    df = df if valuecol is None else df[valuecol]
    df = getattr(df.resample(rule, **resample_kwargs), how)()
    return df


def groupby(df, indexcol, filters):
    df = df.reset_index()
    df = df.set_index(indexcol)
    if filters is not None:
        df = df.groupby(by=filters)
    return df

def longdateformat(adate):
    return adate.strftime('%Y-%m-%d %H:%M:%S')

def df_idx_as_datetime64(df, idx):
    return df.iloc[[idx]].index.values[0]

def df_idx_as_datetime(df, idx):
    return pd.to_datetime(str(df_idx_as_datetime64(df, idx)))