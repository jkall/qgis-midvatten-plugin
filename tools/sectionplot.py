#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is where a section plot is created 
 NOTE - if using this file, it has to be imported by midvatten.py
                             -------------------
        begin                : 2013-11-27
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/
"""
"""
Major parts of the code is re-used from the profiletool plugin:
# Copyright (C) 2008  Borys Jurgiel
# Copyright (C) 2012  Patrice Verchere 
Code is also re-used from the qprof plugin by Mauro Alberti, Marco Zanieri

SAKNAS:
1. (input och plottning av seismik, vlf etc längs med linjen) - efter release alpha
2. ((input och plottning av markyta från DEM)) - efter release beta
"""
import copy
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import os
from functools import partial
from matplotlib import container, patches
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from qgis.core import QgsCoordinateReferenceSystem, QgsMapLayerRegistry

import PyQt4
import numpy as np

import db_utils

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import sqlite3 as sqlite #needed since spatialite-specific sql will be used during polyline layer import
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from midvatten_utils import PlotTemplates

from PyQt4.QtCore import QCoreApplication

#from ui.secplotdockwidget_ui import Ui_SecPlotDock
from PyQt4 import uic
Ui_SecPlotDock =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'secplotdockwidget_ui.ui'))[0]

import definitions.midvatten_defs as defs
from sampledem import qchain, sampling

class SectionPlot(PyQt4.QtGui.QDockWidget, Ui_SecPlotDock):#the Ui_SecPlotDock  is created instantaniously as this is created
    def __init__(self, parent1, iface1):
        #super(sectionplot, self).save_settings()
        PyQt4.QtGui.QDockWidget.__init__(self, parent1) #, PyQt4.QtCore.Qt.WindowFlags(PyQt4.QtCore.Qt.WA_DeleteOnClose))
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        #Ui_SecPlotDock.__init__(self)

        self.parent = parent1
        self.iface = iface1
        #self.location = PyQt4.QtCore.Qt.Qt.BottomDockWidgetArea#should be loaded from settings instead
        #self.location = int(self.ms.settingsdict['secplotlocation'])
        self.connect(self, PyQt4.QtCore.SIGNAL("dockLocationChanged(Qt::DockWidgetArea)"), self.set_location)#not really implemented yet

        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.setWindowTitle("Midvatten plugin - section plot") # Set the title for the dialog

        self.initUI()
        self.template_plot_label.setText("<a href=\"https://github.com/jkall/qgis-midvatten-plugin/wiki/5.-Plots-and-reports#create-section-plot\">Templates manual</a>")
        self.template_plot_label.setOpenExternalLinks(True)


    def do_it(self,msettings,OBSIDtuplein,SectionLineLayer):#must recieve msettings again if this plot windows stayed open while changing qgis project

        #show the user this may take a long time...
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))
        #settings must be recieved here since plot windows may stay open (hence sectionplot instance activated) while a new qgis project is opened or midv settings are chaned 
        self.ms = msettings
        #Draw the widget
        self.iface.addDockWidget(max(self.ms.settingsdict['secplotlocation'],1), self)
        self.iface.mapCanvas().setRenderFlag(True)

        self.dbconnection = db_utils.DbConnectionManager()
        self.temptable_name = 'temporary_section_line'

        self.fill_combo_boxes()
        self.fill_check_boxes()
        self.show()
        #class variables
        self.geology_txt = []
        self.geoshort_txt = []
        self.capacity_txt = []
        self.development_txt = []
        self.comment_txt = []
        self.sectionlinelayer = SectionLineLayer       
        self.obsids_w_wl = []
        
        #upload vector line layer as temporary table in sqlite db
        self.line_crs = self.sectionlinelayer.crs()
        #print(str(self.dbconnection.cursor().execute('select * from a.sqlite_master').fetchall()))
        ok = self.upload_qgis_vector_layer(self.sectionlinelayer, self.line_crs.postgisSrid(), True, False)#loads qgis polyline layer into sqlite table
        if not ok:
            return None

        #print(str(self.dbconnection.cursor().execute('select * from %s'%self.temptable_name).fetchall()))
        # get sorted obsid and distance along section from sqlite db
        nF = len(OBSIDtuplein)#number of Features
        LengthAlongTable = self.get_length_along(OBSIDtuplein)#get_length_along returns a numpy view, values are returned by LengthAlongTable.obs_id or LengthAlongTable.length
        self.selected_obsids = LengthAlongTable.obs_id
        self.LengthAlong = LengthAlongTable.length

        # hidden feature, printout to python console
        utils.MessagebarAndLog.info(log_msg=ru(
            QCoreApplication.translate(u'SectionPlot',
                                       u'Hidden features, obsids and length along section:\n%s\%s'))%
                                            (u';'.join(self.selected_obsids),
                                             u';'.join([str(x) for x in self.LengthAlong])))

        self.fill_dem_list()

        
        PyQt4.QtGui.QApplication.restoreOverrideCursor() #now this long process is done and the cursor is back as normal
        
        #get PlotData
        self.get_plot_data()

        template_folder = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'definitions', 'secplot_templates')
        self.secplot_templates = PlotTemplates(self, self.template_list, self.edit_button, self.load_button,
                                               self.save_as_button, self.import_button, self.remove_button,
                                               template_folder, 'secplot_templates', 'secplot_loaded_template',
                                               defs.secplot_default_template(), self.ms)




        #draw plot
        self.draw_plot()

    def draw_plot(self): #replot
        try:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'SectionPlot', u'Plotting using settings:\n%s'))%self.secplot_templates.readable_output())
        except:
            pass
        if not isinstance(self.dbconnection, db_utils.DbConnectionManager):
            self.dbconnection = db_utils.DbConnectionManager()

        # Only set to stored xlim if the plot has been drawn before
        if self.secax.get_xlim()[0] and self.secax.get_xlim()[1] != 1:
            self.secplot_templates.loaded_template["Axes_set_xlim"] = self.secax.get_xlim()
            self.secplot_templates.loaded_template["Axes_set_ylim"] = self.secax.get_ylim()

        width = self.secplot_templates.loaded_template.get('plot_width', None)
        height = self.secplot_templates.loaded_template.get('plot_height', None)
        self.change_plot_size(width, height)

        try:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))#show the user this may take a long time...
            try:
                self.annotationtext.remove()
            except:
                pass
            self.secax.clear()
            #load user settings from the ui
            self.ms.settingsdict['secplotwlvltab'] = unicode(self.wlvltableComboBox.currentText())
            temporarystring = ru(self.datetimetextEdit.toPlainText()) #this needs some cleanup
            try:
                self.ms.settingsdict['secplotdates']= [x for x in temporarystring.replace(u'\r', u'').split(u'\n') if x.strip()]
            except TypeError as e:
                self.ms.settingsdict['secplotdates']=u''
            self.ms.settingsdict['secplottext'] = self.textcolComboBox.currentText()
            self.ms.settingsdict['secplotbw'] = self.barwidthdoubleSpinBox.value()
            self.ms.settingsdict['secplotdrillstop'] = self.drillstoplineEdit.text()
            self.ms.settingsdict['stratigraphyplotted'] = self.Stratigraphy_checkBox.checkState()
            self.ms.settingsdict['secplotlabelsplotted'] = self.Labels_checkBox.checkState()
            self.get_dem_selection()
            self.ms.settingsdict['secplotselectedDEMs'] = self.rasterselection
            #fix Floating Bar Width in percents of xmax - xmin
            xmax, xmin =float(max(self.LengthAlong)), float(min(self.LengthAlong))
            self.barwidth = (self.ms.settingsdict['secplotbw']/100.0)*(xmax -xmin)

            self.get_plot_data_2()

            self.p=[]
            self.Labels=[]

            if self.ms.settingsdict['stratigraphyplotted'] ==2:
                #PLOT ALL MAIN GEOLOGY TYPES AS SINGLE FLOATING BAR SERIES
                self.plot_geology()
                #WRITE TEXT BY ALL GEOLOGY TYPES, ADJACENT TO FLOATING BAR SERIES
                if len(self.ms.settingsdict['secplottext'])>0:
                    self.write_annotation()
            if self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates'])>0: #PLOT Water Levels
                self.plot_water_level()
            if self.ms.settingsdict['secplotdrillstop']!='':
                self.plot_drill_stop()

            #if the line layer obs_lines is selected, then try to plot seismic data if there are any
            if self.sectionlinelayer.name()=='obs_lines':
                if len(self.obs_lines_plot_data)>0:
                    self.plot_obs_lines_data()

            #if there are any DEMs selected, try to plot them
            if len(self.ms.settingsdict['secplotselectedDEMs'])>0:
                self.plot_dems()

            #write obsid at top of each stratigraphy floating bar plot, also plot empty bars to show drillings without stratigraphy data
            if self.ms.settingsdict['stratigraphyplotted'] ==2 or (self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates'])>0):
                self.write_obsid(self.ms.settingsdict['secplotlabelsplotted'])#if argument is 2, then labels will be plotted, otherwise only empty bars

            #labels, grid, legend etc.
            self.finish_plot()
            self.save_settings()
            self.dbconnection.closedb()
            self.dbconnection = None
        except KeyError as e:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'SectionPlot', u'Section plot optional settings error, press "Restore defaults"')),
                                            log_msg=ru(QCoreApplication.translate(u'SectionPlot', u'Error msg: %s'))%e)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.dbconnection.closedb()
            self.dbconnection = None

        except:
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.dbconnection.closedb()
            self.dbconnection = None
            raise
        else:
            PyQt4.QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def execute_query(self,query,params=(),commit=False):#from qspatialite, it is only used by self.uploadQgisVectorLayer
        """Execute query (string) with given parameters (tuple) (optionnaly perform commit to save Db) and return resultset [header,data] or [flase,False] if error"""
        query=unicode(query)
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
        except sqlite.OperationalError, Msg:
            self.dbconnection.rollback()
            utils.pop_up_info(ru(QCoreApplication.translate(u'SectionPlot', "The SQL query\n %s\n seems to be invalid.\n\n%s")) %(query,Msg), 'Error', None)
            self.queryPb=True #Indicates pb with current query
            
        return header,data

    def fill_check_boxes(self):#sets checkboxes to last selection
        if self.ms.settingsdict['stratigraphyplotted']==2:
            self.Stratigraphy_checkBox.setChecked(True)
        else:
            self.Stratigraphy_checkBox.setChecked(False)        
        if self.ms.settingsdict['secplotlabelsplotted']==2:
            self.Labels_checkBox.setChecked(True)
        else:
            self.Labels_checkBox.setChecked(False)

        if self.ms.settingsdict['secplotwidthofplot'] == 2:
            self.width_of_plot.setChecked(True)
        else:
            self.width_of_profile.setChecked(True)

    def fill_combo_boxes(self): # This method populates all table-comboboxes with the tables inside the database
        # Execute a query in SQLite to return all available tables (sql syntax excludes some of the predefined tables)
        # start with cleaning comboboxes before filling with new entries
        # clear comboboxes etc
        self.wlvltableComboBox.clear()  
        #self.colorComboBox.clear()
        self.textcolComboBox.clear()  
        self.datetimetextEdit.clear()
        self.drillstoplineEdit.clear()

        #Fill comboxes, lineedits etc
        tabeller = [x for x in db_utils.get_tables(dbconnection=self.dbconnection, skip_views=True)
                           if not x.startswith(u'zz_') and x not in
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
        textitems=['','geology','geoshort','capacity','development','comment']
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
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.wlvltableComboBox.setCurrentIndex(i)
                if unicode(self.wlvltableComboBox.currentText()) == unicode(self.ms.settingsdict['secplotwlvltab']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                elif i> len(self.wlvltableComboBox):
                    notfound=1
                i = i + 1
        if len(str(self.ms.settingsdict['secplottext'])):#If there is a last selected field for annotation in graph
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.textcolComboBox.setCurrentIndex(i)
                if unicode(self.textcolComboBox.currentText()) == unicode(self.ms.settingsdict['secplottext']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                elif i> len(self.textcolComboBox):
                    notfound=1
                i = i + 1
        if self.ms.settingsdict['secplotbw'] !=0:
            self.barwidthdoubleSpinBox.setValue(self.ms.settingsdict['secplotbw'])            
        else:
            self.barwidthdoubleSpinBox.setValue(2)
        self.drillstoplineEdit.setText(self.ms.settingsdict['secplotdrillstop']) 

    def fill_dem_list(self): # This method populates the QListWidget 'inData' with all possible DEMs
        self.inData.clear()
        self.rastItems = {} #dictionary - layer name : layer
        mc = self.iface.mapCanvas()
        msg=''
        for i in range(mc.layerCount()):#find the raster layers
            layer = mc.layer(i)
            if layer.type() == layer.RasterLayer:
                msg=ru(QCoreApplication.translate(u'SectionPlot', u'please notice that DEM(s) must be single band rasters and have same crs as your selected vector line layer'))
                if layer.bandCount()==1:#only single band raster layers
                    #print('raster layer '  + layer.name() + ' has crs '+str(layer.crs().authid()[5:]))#debug
                    #print('polyline layer ' + self.sectionlinelayer.name() + ' has crs '+str(self.line_crs.authid()[5:]))#debug
                    if layer.crs().authid()[5:] == self.line_crs.authid()[5:]:#only raster layer with crs corresponding to line layer
                        self.rastItems[unicode(layer.name())] = layer
                        self.inData.addItem(unicode(layer.name()))
        if msg !='':
            self.iface.messageBar().pushMessage(ru(QCoreApplication.translate(u'SectionPlot', u"Info")),msg, 0,duration=10)
        self.get_dem_selection()

    def finish_plot(self):
        leg = self.secax.legend(self.p, self.Labels, **self.secplot_templates.loaded_template['legend_Axes_legend'])
        leg.draggable(state=True)
        frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
        frame.set_facecolor(self.secplot_templates.loaded_template['legend_Frame_set_facecolor'])    # set the frame face color to white
        frame.set_fill(self.secplot_templates.loaded_template['legend_Frame_set_fill'])
        for t in leg.get_texts():
            t.set_fontsize(self.secplot_templates.loaded_template['legend_Text_set_fontsize'])

        self.secax.grid(**self.secplot_templates.loaded_template['grid_Axes_grid'])

        self.secax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.secax.xaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))

        Axes_set_ylabel = dict([(k, v) for k, v in self.secplot_templates.loaded_template.get('Axes_set_ylabel', {}).iteritems() if k != 'ylabel'])
        ylabel = self.secplot_templates.loaded_template.get('Axes_set_ylabel', {}).get('ylabel', defs.secplot_default_template()['Axes_set_ylabel']['ylabel'])
        self.secax.set_ylabel(ylabel, **Axes_set_ylabel)  #Allows international characters ('åäö') as ylabel

        Axes_set_xlabel = dict([(k, v) for k, v in self.secplot_templates.loaded_template.get('Axes_set_xlabel', {}).iteritems() if k != 'xlabel'])
        xlabel = self.secplot_templates.loaded_template.get('Axes_set_xlabel', {}).get('xlabel', defs.secplot_default_template()['Axes_set_xlabel']['xlabel'])
        self.secax.set_xlabel(xlabel, **Axes_set_xlabel)  #Allows international characters ('åäö') as xlabel

        for label in self.secax.xaxis.get_ticklabels():
            label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])
        for label in self.secax.yaxis.get_ticklabels():
            label.set_fontsize(**self.secplot_templates.loaded_template['ticklabels_Text_set_fontsize'])
        """
        if there is no stratigraphy data and no borehole lenght for first or last observations,
        then autscaling will fail silently since it does not consider axes.annotate (which is used for printing obsid)
        hence this special treatment to check if xlim are less than expected from lengthalong
        """
        #self.secax.autoscale(enable=True, axis='both', tight=None)
        xmin_xmax = self.secplot_templates.loaded_template['Axes_set_xlim']
        if xmin_xmax is None:
            _xmin, _xmax = self.secax.get_xlim()
            xmin = min(float(min(self.LengthAlong))-self.barwidth,_xmin)
            xmax = max(float(max(self.LengthAlong))+self.barwidth, _xmax)
        else:
            xmin, xmax = xmin_xmax
        self.secax.set_xlim(xmin, xmax)

        ymin_ymax = self.secplot_templates.loaded_template['Axes_set_ylim']
        if ymin_ymax is not None:
            ymin, ymax = ymin_ymax
            self.secax.set_ylim(ymin, ymax)

        if self.secplot_templates.loaded_template['Figure_subplots_adjust']:
            self.secfig.subplots_adjust(**self.secplot_templates.loaded_template['Figure_subplots_adjust'])

        if self.width_of_plot.isChecked():
            self.ms.settingsdict['secplotwidthofplot'] = 2
            self.update_barwidths_from_plot()
        else:
            self.ms.settingsdict['secplotwidthofplot'] = 1

        self.canvas.draw()
        """
        The plot is shown in the canvas. 
        Now close the figure to prevent it from being plotted again by plt.show() when choosing tsplot or xyplot
        The plt.close(self.secfig) closes reference to self.secfig 
        and it will not be plotted by plt.show() - but the plot exists in self.canvas
        Please note, this do not work completely as expected under windows. 
        """

        plt.close(self.secfig)#this closes reference to self.secfig

    def get_dem_selection(self):
        self.rasterselection = []
        for item in self.inData.selectedItems():
            self.rasterselection.append(item.text())
                
    def get_length_along(self,obsidtuple):#returns a numpy recarray with attributes obs_id and length 
        #------------First a sql clause that returns a table, but that is not what we need

        sql = u"""SELECT p.obsid, ST_Length((SELECT geometry FROM %s)) * ST_Line_Locate_Point((SELECT geometry FROM %s), p.geometry) AS absdist FROM obs_points AS p
                  WHERE p.obsid in %s
                  ORDER BY absdist"""%(self.temptable_name, self.temptable_name, u'({})'.format(u', '.join([u"'{}'".format(o) for o in obsidtuple])))

        data = self.dbconnection.execute_and_fetchall(sql)
        data = ru(data, keep_containers=True)
        #data = [[col.encode('utf-8') for col in row] for row in ru(data, keep_containers=True)]
        #data = utils.sql_load_fr_db(sql)[1]
        My_format = [('obs_id', np.unicode_, 32),('length', float)] #note that here is a limit of maximum 32 characters in obsid
        npdata = np.array(data, dtype=My_format)  #NDARRAY
        LengthAlongTable=npdata.view(np.recarray)   # RECARRAY   Makes the two columns into callable objects, i.e. write self.LengthAlong.obs_id and self.LengthAlong.length
        del data, npdata
        return LengthAlongTable

    def get_plot_data(self):#this is called when class is instantiated, collecting data specific for the profile line layer and the obs_points
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))#show the user this may take a long time...
        self.plotx = {}
        self.plotbottom = {}
        self.plotbarlength = {}
        l=0 #counter fro unique obs, stratid and typ
        self.x_txt = []#used by self.WriteAnnotation
        self.z_txt = []#used by self.WriteAnnotation
        self.x_id = []#used by self.write_obsid
        self.z_id=[]#used by self.write_obsid
        self.barlengths=[]#used by self.write_obsid, not to be mixed with "BarLength" used locally in this function
        self.bottoms=[]#used by self.write_obsid, not to be mixed with "Bottom" used locally in this function
        self.PlotTypes = defs.PlotTypesDict()
        #print(self.PlotTypes)#debug
        self.ExistingPlotTypes = []
        self.Hatches = defs.PlotHatchDict()
        self.Colors = defs.PlotColorDict()
        #print(self.Colors)#debug

        #self.ms.settingsdict['secplotbw'] = self.barwidthdoubleSpinBox.value()
        ##fix Floating Bar Width in percents of xmax - xmin
        #xmax, xmin =float(max(self.LengthAlong)), float(min(self.LengthAlong))
        #self.barwidth = (self.ms.settingsdict['secplotbw']/100.0)*(xmax -xmin)
        
        for Typ in self.PlotTypes:#Adding a plot for each "geoshort" that is identified
            i=0 #counter for unique obs and stratid
            k=0 #counter for unique Typ
            q=0 #counter for unique obsid (only used in first Typ-loop)
            x = []
            z_gs=[]
            BarLength=[]#stratigraphy bar length
            Bottom = []#stratigraphy bottom
            for obs in self.selected_obsids:
                if k<=len(self.selected_obsids):#in first Typ-loop, get some basic obs_points data - to be used for plotting obsid, empty bars etc
                    self.x_id.append(float(self.LengthAlong[q]))
                    sql = u"SELECT h_toc, h_gs, length FROM obs_points WHERE obsid = '%s'"%obs
                    recs = db_utils.sql_load_fr_db(sql, self.dbconnection)[1]
                    if utils.isfloat(str(recs[0][1])) and recs[0][1]>-999:
                        self.z_id.append(recs[0][1])
                    elif utils.isfloat(str(recs[0][0])) and recs[0][0]>-999:
                        self.z_id.append(recs[0][0])
                    else:
                        self.z_id.append(0)
                    if utils.isfloat(str(recs[0][2])):
                        self.barlengths.append(recs[0][2])
                    else:
                        self.barlengths.append(0)
                    self.bottoms.append(self.z_id[q]-self.barlengths[q])

                    q +=1
                    del recs
                    
                sql=u"""SELECT depthbot - depthtop, stratid, geology, geoshort, capacity, development, comment FROM stratigraphy WHERE obsid = '%s' AND lower(geoshort) %s ORDER BY stratid"""%(obs, self.PlotTypes[Typ])
                _recs = db_utils.sql_load_fr_db(sql, self.dbconnection)[1]
                if _recs:
                    recs = _recs
                    j=0#counter for unique stratid
                    for rec in recs:#loop cleanup
                        BarLength.append(rec[0])#loop cleanup
                        x.append(float(self.LengthAlong[k]))# - self.barwidth/2)
                        sql01 = u"select h_gs from obs_points where obsid = '%s'"%obs
                        sql01_result = db_utils.sql_load_fr_db(sql01, self.dbconnection)[1][0][0]
                        sql02 = u"select h_toc from obs_points where obsid = '%s'"%obs
                        sql02_result = db_utils.sql_load_fr_db(sql02, self.dbconnection)[1][0][0]
                        #print('h_gs for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql01)[1])[0][0]))#debug
                        #print('h_toc for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql02)[1])[0][0]))#debug
                        
                        if utils.isfloat(str(sql01_result)) and sql01_result >-999:
                            z_gs.append(float(str(sql01_result)))
                        elif utils.isfloat(str(sql02_result)) and sql02_result>-999:
                            z_gs.append(float(str(sql02_result)))
                        else:
                            z_gs.append(0)
                        Bottom.append(z_gs[i] - float(str((
                                                          db_utils.sql_load_fr_db(u"""SELECT depthbot FROM stratigraphy WHERE obsid = '%s' AND stratid = %s AND lower(geoshort) %s"""%(obs, str(recs[j][1]), self.PlotTypes[Typ]), self.dbconnection)[1])[0][0])))
                        #lists for plotting annotation 
                        self.x_txt.append(x[i])#+ self.barwidth/2)#x-coord for text
                        self.z_txt.append(Bottom[i] + recs[j][0]/2)#Z-value for text
                        self.geology_txt.append(utils.null_2_empty_string(ru(recs[j][2])))
                        self.geoshort_txt.append(utils.null_2_empty_string(ru(recs[j][3])))
                        self.capacity_txt.append(utils.null_2_empty_string(ru(recs[j][4])))
                        self.development_txt.append(utils.null_2_empty_string(ru(recs[j][5])))
                        self.comment_txt.append(utils.null_2_empty_string(ru(recs[j][6])))
                        #print obs + " " + Typ + " " + self.geology_txt[l] + " " + self.geoshort_txt[l] + " " + self.capacity_txt[l] + " " + self.development_txt[l] + " " + self.comment_txt[l]#debug
                        
                        i +=1
                        j +=1
                        l +=1
                    del recs
                k +=1
            if len(x)>0:
                self.ExistingPlotTypes.append(Typ)
                self.plotx[Typ] = x
                self.plotbottom[Typ] = Bottom
                self.plotbarlength[Typ] = BarLength

        #Last step in get data - check if the line layer is obs_lines and if so, load seismic data if there are any 
        My_format = [('obsline_x', float), ('obsline_y1', float), ('obsline_y2', float)]
        obsline_x=[]
        obsline_y1=[]#bedrock
        obsline_y2=[]#ground surface
        x='length'
        self.y1_column='bedrock'
        self.y2_column='ground'
        table='seismic_data'
        if self.sectionlinelayer.name()=='obs_lines':
            obsline_id = utils.getselectedobjectnames(self.sectionlinelayer)[0]
            sql = r"""select %s as x, %s as y1, %s as y2 from %s where obsid='%s'"""%(x, self.y1_column,self.y2_column,table,obsline_id)
            conn_OK, recs = db_utils.sql_load_fr_db(sql, self.dbconnection)
            table = np.array(recs, dtype=My_format)  #NDARRAY
            self.obs_lines_plot_data=table.view(np.recarray)   # RECARRAY   Makes the two columns inte callable objects, i.e. write self.obs_lines_plot_data.values
        #print('debug info: ' + str(self.selected_obsids) + str(self.x_id) + str(self.z_id) + str(self.barlengths) + str(self.bottoms))#debug
        PyQt4.QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def get_plot_data_2(self):#collecting data depending on a number of selections in left side panel
        self.obsid_wlid=[]#if no stratigr plot, then obsid will be plotted close to water level instead of toc or gs
        self.x_id_wwl=[]
        self.z_id_wwl=[]
        self.obs_p_w_drill_stops=[]
        self.drill_stops=[]
        self.x_ds=[]
        self.z_ds=[]

        if self.ms.settingsdict['secplotdrillstop']!='':
            query = u"""select obsid from obs_points where lower(drillstop) like '%s'"""%ru(self.ms.settingsdict['secplotdrillstop'])
            result = db_utils.sql_load_fr_db(query, self.dbconnection)
            if result[1]:
                for item in result[1]:
                    self.obs_p_w_drill_stops.append(item[0])

        q=0
        for obs in self.selected_obsids:#Finally adding obsid at top of stratigraphy
            if obs in self.obsids_w_wl and self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates'])>0:
                query = u"""select avg(level_masl) from """ + self.ms.settingsdict['secplotwlvltab'] + r""" where obsid = '""" + obs + r"""' and ((date_time >= '""" + min(self.ms.settingsdict['secplotdates']) + r"""' and date_time <= '""" + max(self.ms.settingsdict['secplotdates']) + r"""') or (date_time like '""" + min(self.ms.settingsdict['secplotdates']) + r"""%' or date_time like '""" + max(self.ms.settingsdict['secplotdates']) + r"""%'))"""
                #print(query)#debug
                recs = db_utils.sql_load_fr_db(query, self.dbconnection)[1]
                if recs:
                    self.obsid_wlid.append(obs)
                    self.x_id_wwl.append(float(self.LengthAlong[q]))
                    if utils.isfloat(str(recs[0][0])) and recs[0][0]>-999:
                        self.z_id_wwl.append(recs[0][0])
                    else:
                        self.z_id_wwl.append(0)
                del recs

                    
            if obs in self.obs_p_w_drill_stops:
                self.x_ds.append(float(self.LengthAlong[q]))
                self.z_ds.append(float(self.bottoms[q]))
            q +=1

    def get_selected_dems_params( self, dialog ):   
        selected_dems = []
        selected_dem_colors = [] 
        for dem_qgis_ndx in range( dialog.listDEMs_treeWidget.topLevelItemCount () ):
            curr_DEM_item = dialog.listDEMs_treeWidget.topLevelItem ( dem_qgis_ndx ) 
            if curr_DEM_item.checkState ( 0 ) == 2:
                selected_dems.append( dialog.singleband_raster_layers_in_project[ dem_qgis_ndx ] )
                selected_dem_colors.append( dialog.listDEMs_treeWidget.itemWidget( curr_DEM_item, 1 ).currentText() )  
        return selected_dems, selected_dem_colors

    def initUI(self): 
        #connect signal
        self.pushButton.clicked.connect(self.draw_plot)
        self.redraw.clicked.connect(self.finish_plot)
        self.connect(self.chart_settings, PyQt4.QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.chart_settings))
        self.set_groupbox_children_visibility(self.chart_settings)
        
        # Create a plot window with one single subplot
        self.secfig = plt.figure()
        self.secax = self.secfig.add_subplot( 111 )
        self.canvas = FigureCanvas( self.secfig )
        
        self.mpltoolbar = NavigationToolbar( self.canvas, self.plotareawidget )
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.mplplotlayout.addWidget( self.canvas )
        self.mplplotlayout.addWidget( self.mpltoolbar )

    def plot_dems(self):
        if self.ms.settingsdict['secplotselectedDEMs'] and len(self.ms.settingsdict['secplotselectedDEMs'])>0:    # Adding a plot for each selected raster
            temp_memorylayer, xarray = qchain(self.sectionlinelayer,self.barwidth/2)
            for layername in self.ms.settingsdict['secplotselectedDEMs']:
                DEMdata = sampling(temp_memorylayer,self.rastItems[unicode(layername)])

                plotlable = self.get_plot_label_name(layername, self.Labels)

                settings = self.secplot_templates.loaded_template['dems_Axes_plot'].get(plotlable,
                                                                                 self.secplot_templates.loaded_template['dems_Axes_plot']['DEFAULT'])
                self.secplot_templates.loaded_template['dems_Axes_plot'][plotlable] = copy.deepcopy(settings)
                settings = self.secplot_templates.loaded_template['dems_Axes_plot'][plotlable]
                settings['label'] = settings.get('label', plotlable)
                self.Labels.append(settings['label'])

                lineplot, = self.secax.plot(xarray, DEMdata, **settings)  # The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1
                self.p.append(lineplot)

            QgsMapLayerRegistry.instance().removeMapLayer(temp_memorylayer.id())

    def plot_drill_stop(self):
        settings = copy.deepcopy(self.secplot_templates.loaded_template['drillstop_Axes_plot'])
        label = settings.get('label', None)
        if label is None:
            label = 'drillstop like ' + self.ms.settingsdict['secplotdrillstop']
        self.Labels.append(label)
        settings['label'] = label
        lineplot,=self.secax.plot(self.x_ds, self.z_ds, **settings)
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

            plotxleftbarcorner = [i - self.barwidth/2 for i in self.plotx[Typ]]#subtract half bar width from x position (x position is stored as bar center in self.plotx)
            self.p.append(self.secax.bar(plotxleftbarcorner, self.plotbarlength[Typ], bottom=self.plotbottom[Typ], **settings))#matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)
            self.Labels.append(Typ)

    def plot_obs_lines_data(self):
        plotlable = self.get_plot_label_name(self.y1_column, self.Labels)
        self.Labels.append(self.y1_column)
        lineplot, = self.secax.plot(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y1, marker = 'None', linestyle = '-', label=plotlable)# PLOT!!
        self.p.append(lineplot)

        plotlable = self.get_plot_label_name(self.y2_column, self.Labels)
        self.Labels.append(self.y2_column)
        lineplot, = self.secax.plot(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y2, marker = 'None', linestyle = '-', label=plotlable)# PLOT!!
        self.p.append(lineplot)

    def plot_water_level(self):   # Adding a plot for each water level date identified
        self.obsids_w_wl = []
        for _datum in self.ms.settingsdict['secplotdates']:
            datum_obsids = _datum.split(u';')
            datum = datum_obsids[0]

            WL = []
            x_wl=[]
            for k, obs in enumerate(self.selected_obsids):
                if len(datum_obsids) > 1:
                    if obs not in datum_obsids[1:]:
                        continue
                query = u"""SELECT level_masl FROM {} WHERE obsid = '{}' AND date_time like '{}%'""".format(self.ms.settingsdict['secplotwlvltab'], obs, datum)
                res = db_utils.sql_load_fr_db(query, self.dbconnection)[1]
                if res:
                    WL.append(res[0][0])
                    x_wl.append(float(self.LengthAlong[k]))
                    if obs not in self.obsids_w_wl:
                        self.obsids_w_wl.append(obs)

            plotlable = self.get_plot_label_name(datum, self.Labels)

            settings = self.secplot_templates.loaded_template['wlevels_Axes_plot'].get(plotlable,
                                                                                self.secplot_templates.loaded_template[
                                                                               'wlevels_Axes_plot']['DEFAULT'])
            self.secplot_templates.loaded_template['wlevels_Axes_plot'][plotlable] = copy.deepcopy(settings)
            settings = self.secplot_templates.loaded_template['wlevels_Axes_plot'][plotlable]
            settings['label'] = settings.get('label', plotlable)
            self.Labels.append(settings['label'])
            lineplot, = self.secax.plot(x_wl, WL, **settings)  # The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1

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

        #Don't save plot min/max for next plot. If a specific is to be used, it should be set in a saved template file.
        loaded_template = copy.deepcopy(self.secplot_templates.loaded_template)
        loaded_template["Axes_set_xlim"] = None
        loaded_template["Axes_set_ylim"] = None
        utils.save_stored_settings(self.ms, loaded_template, 'secplot_loaded_template')
        self.ms.save_settings('secplot_templates')
        
    def set_location(self):#not ready
        dockarea = self.parent.dockWidgetArea(self)
        self.ms.settingsdict['secplotlocation']=dockarea

    def upload_qgis_vector_layer(self, layer, srid=None,selected=False, mapinfo=True,Attributes=False): #from qspatialite, with a few  changes LAST ARGUMENT IS USED TO SKIP ARGUMENTS SINCE WE ONLY WANT THE GEOMETRY TO CALCULATE DISTANCES
        """Upload layer (QgsMapLayer) (optionnaly only selected values ) into current DB, in self.temptable_name (string) with desired SRID (default layer srid if None) - user can desactivate mapinfo compatibility Date importation. Return True if operation succesfull or false in all other cases"""

        #Upload a selected feature into a table. If spatialite, make it a memory table, if postgis make it temporary.
        #upload two fields only, one id field set to dummy and one geometry field.

        selected_features = layer.selectedFeatures()
        if len(selected_features) != 1:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'SectionPlot', "Must select only one feature in qgis layer: %s)"))%layer.name())
            return False

        if not layer.hasGeometryType():
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'SectionPlot', u"Layer %s is missing geometry"))%layer.name())
            return False

        """
        qgis geometry types:
        0 = MULTIPOINT,
        1 = MULTILINESTRING,
        2 = MULTIPOLYGON,
        3 = UnknownGeometry,
        4 = ?
        """

        if layer.geometryType() != 1:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'SectionPlot', u"Layer %s is missing geometry type MULTILINESTRING, had %s"))%(layer.name(), str(layer.geometryType())))
            return False

        self.temptable_name = self.dbconnection.create_temporary_table_for_import(self.temptable_name, [u'dummyfield TEXT'], [u'geometry', u'LINESTRING', srid])
        #self.dbconnection.execute("INSERT into %s VALUES ('test')"%self.temptable_name)

        Qsrid = QgsCoordinateReferenceSystem()
        Qsrid.createFromId(srid)
        if not Qsrid.isValid():  # check if crs is ok
            utils.pop_up_info(ru(QCoreApplication.translate(u'SectionPlot', "Destination SRID isn't valid for table %s")) % layer.name(), self.parent)

            return False
        layer.setCrs(Qsrid)

        feature = selected_features[0]
        geom = feature.geometry()
        wkt = geom.exportToWkt()
        self.dbconnection.execute(u"""INSERT INTO %s (dummyfield, geometry) VALUES ('0', ST_GeomFromText('%s', %s))"""%(self.temptable_name, wkt, srid))

        #Test without commit
        #self.dbconnection.commit()

        return True

    def write_annotation(self):
        if self.ms.settingsdict['secplottext'] == 'geology':
            annotate_txt = self.geology_txt
        elif self.ms.settingsdict['secplottext'] == 'geoshort':
            annotate_txt = self.geoshort_txt
        elif self.ms.settingsdict['secplottext'] == 'capacity':
            annotate_txt = self.capacity_txt
        elif self.ms.settingsdict['secplottext'] == 'development':
            annotate_txt = self.development_txt
        else:
            annotate_txt = self.comment_txt
        for m,n,o in zip(self.x_txt,self.z_txt,annotate_txt):#change last arg to the one to be written in plot
            self.annotationtext = self.secax.annotate(o, xy=(m,n), **self.secplot_templates.loaded_template['layer_Axes_annotate'])#textcoords = 'offset points' makes the text being written xytext points from the data point xy (xy positioned with respect to axis values and then the text is offset a specific number of points from that point

    def write_obsid(self, plot_labels=2):#annotation, and also empty bars to show drillings without stratigraphy data
        if self.ms.settingsdict['stratigraphyplotted'] ==2:#if stratigr plot, then obsid written close to toc or gs
            plotxleftbarcorner = [i - self.barwidth/2 for i in self.x_id]#x-coord for bars at each obs

            indexes_barlength_not_0 = [idx for idx, length in enumerate(self.barlengths) if length]

            plotxleftbarcorner = [plotxleftbarcorner[idx] for idx in indexes_barlength_not_0]
            bottoms = [self.bottoms[idx] for idx in indexes_barlength_not_0]
            barlengths = [self.barlengths[idx] for idx in indexes_barlength_not_0]

            obsid_Axes_bar = copy.deepcopy(self.secplot_templates.loaded_template['obsid_Axes_bar'])
            obsid_Axes_bar['width'] = obsid_Axes_bar.get('width', self.barwidth)
            obsid_Axes_bar['bottom'] = obsid_Axes_bar.get('bottom', bottoms)
            self.p.append(self.secax.bar(plotxleftbarcorner, barlengths, **obsid_Axes_bar))#matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)#plot empty bars
            if plot_labels==2:#only plot the obsid as annotation if plot_labels is 2, i.e. if checkbox is activated
                for m,n,o in zip(self.x_id,self.z_id,self.selected_obsids):#change last arg to the one to be written in plot
                    text = self.secax.annotate(o, xy=(m,n), **self.secplot_templates.loaded_template['obsid_Axes_annotate'])
        else: #obsid written close to average water level (average of all water levels between given min and max date) 
            if plot_labels==2:#only plot the obsid as annotation if plot_labels is 2, i.e. if checkbox is activated            
                for m,n,o in zip(self.x_id_wwl,self.z_id_wwl,self.obsid_wlid):#change last arg to the one to be written in plot
                    text = self.secax.annotate(o, xy=(m,n), **self.secplot_templates.loaded_template['obsid_Axes_annotate'])

    def set_groupbox_children_visibility(self, groupbox_widget):
        children = groupbox_widget.findChildren(PyQt4.QtGui.QWidget)
        for child in children:
            child.setVisible(groupbox_widget.isChecked())

    def change_plot_size(self, width, height):
        try:
            width = int(width)
        except:
            #self.layoutplot.setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Extended)
            #self.widgetPlot.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Expanding)
            self.widget.setMinimumWidth(0)
            self.widget.setMaximumWidth(16777215)
            #self.widgetPlot.adjustSize()
        else:
            #self.widgetPlot.setMinimum
            #self.widgetPlot.setFixedWidth(width)
            self.widget.setMinimumWidth(width)
            self.widget.setMaximumWidth(width)

        try:
            height = int(height)
        except:
            #self.widgetPlot.sizePolicy().setVerticalPolicy(PyQt4.QtGui.QSizePolicy.Expanding)
            self.widget.setMinimumHeight(0)
            self.widget.setMaximumHeight(16777215)
        else:
            self.widget.setMinimumHeight(height)
            self.widget.setMaximumHeight(height)

    def update_barwidths_from_plot(self):
        used_xmin, used_xmax = self.secax.get_xlim()
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
