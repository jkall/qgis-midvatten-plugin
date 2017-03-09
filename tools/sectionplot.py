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
import PyQt4.QtCore
import PyQt4.QtGui
from qgis.core import *

import numpy as np
import sys, os
import locale
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import pyspatialite.dbapi2 as sqlite #needed since spatialite-specific sql will be used during polyline layer import
import midvatten_utils as utils

#from ui.secplotdockwidget_ui import Ui_SecPlotDock
from PyQt4 import uic
Ui_SecPlotDock =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'secplotdockwidget_ui.ui'))[0]

import definitions.midvatten_defs as defs
from sampledem import qchain, create_points_at, points_along_line, sampling 

class SectionPlot(PyQt4.QtGui.QDockWidget, Ui_SecPlotDock):#the Ui_SecPlotDock  is created instantaniously as this is created
    def __init__(self, parent1, iface1):#Please note, self.selected_obsids must be a tuple
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

    def connection(self):#from qspatialite, it is only used by self.uploadQgisVectorLayer
        """ Create connexion if not yet connected and Return connexion object for the current DB"""
        try:
            return self.connectionObject
        except:
            try:
                #self.conn = sqlite.connect(':memory:')
                dbpath = QgsProject.instance().readEntry("Midvatten","database")
                self.connectionObject=sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
                curs = self.connectionObject.cursor()
                curs.execute(u"""ATTACH DATABASE ':memory:' AS a""")
                #self.connectionObject = sqlite.connect(':memory:')
                return self.connectionObject
            except sqlite.OperationalError, Msg:
                utils.pop_up_info("Can't connect to DataBase: %s\nError %s"%(self.path,Msg))

    def do_it(self,msettings,OBSIDtuplein,SectionLineLayer):#must recieve msettings again if this plot windows stayed open while changing qgis project
        #show the user this may take a long time...
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))
        #settings must be recieved here since plot windows may stay open (hence sectionplot instance activated) while a new qgis project is opened or midv settings are chaned 
        self.ms = msettings
        #Draw the widget
        self.iface.addDockWidget(max(self.ms.settingsdict['secplotlocation'],1), self)
        self.iface.mapCanvas().setRenderFlag(True)        

        self.fill_combo_boxes()
        self.fill_check_boxes()
        self.show()
        #class variables
        self.geology_txt = []
        self.geoshort_txt = []
        self.capacity_txt = []
        self.development_txt = []
        self.comment_txt = []
        self.temptableName = 'temporary_section_line'
        self.connection()
        self.sectionlinelayer = SectionLineLayer       
        self.obsids_w_wl = []
        
        #upload vector line layer as temporary table in sqlite db
        self.line_crs = self.sectionlinelayer.crs()
        #print(str(self.connectionObject.cursor().execute('select * from a.sqlite_master').fetchall()))
        ok = self.upload_qgis_vector_layer(self.sectionlinelayer, self.line_crs.postgisSrid(), True, False)#loads qgis polyline layer into sqlite table
        #print(str(self.connectionObject.cursor().execute('select * from %s'%self.temptableName).fetchall()))
        # get sorted obsid and distance along section from sqlite db
        nF = len(OBSIDtuplein)#number of Features
        LengthAlongTable = self.get_length_along(OBSIDtuplein)#get_length_along returns a numpy view, values are returned by LengthAlongTable.obs_id or LengthAlongTable.length
        self.selected_obsids = LengthAlongTable.obs_id
        self.LengthAlong = LengthAlongTable.length

        # hidden feature, printout to python console
        #print([x for x in self.selected_obsids])
        #print([x for x in self.LengthAlong])
        
        self.fill_dem_list()
        
        #drop temporary table
        #sql = r"""DROP TABLE %s"""%self.temptableName
        #ok = utils.sql_alter_db(sql)
        #sql = r"""DELETE FROM geometry_columns WHERE "f_table_name"='%s'"""%self.temptableName
        #ok = utils.sql_alter_db(sql)
        #sql = r"""DELETE FROM spatialite_history WHERE "table_name"='%s'"""%self.temptableName
        #ok = utils.sql_alter_db(sql)
        
        PyQt4.QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal
        
        #get PlotData
        self.get_plot_data()
        #draw plot
        self.draw_plot()

    def draw_plot(self): #replot
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))#show the user this may take a long time...
        try:
            self.annotationtext.remove()
        except:
            pass
        self.secax.clear()
        #load user settings from the ui
        self.ms.settingsdict['secplotwlvltab'] = unicode(self.wlvltableComboBox.currentText())
        temporarystring = self.datetimetextEdit.toPlainText() #this needs some cleanup
        try:
            self.ms.settingsdict['secplotdates']=temporarystring.split()
        except TypeError:
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
        PyQt4.QtGui.QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def execute_query(self,query,params=(),commit=False):#from qspatialite, it is only used by self.uploadQgisVectorLayer
        """Execute query (string) with given parameters (tuple) (optionnaly perform commit to save Db) and return resultset [header,data] or [flase,False] if error"""
        query=unicode(query)
        self.queryPb=False
        header=[]
        data=[]
        cursor=self.connectionObject.cursor()
        try:
            cursor.execute(query,params)
            if (cursor.description is not None):
                header = [item[0] for item in cursor.description]
            data = [row for row in cursor]
            if commit:
                self.connectionObject.commit()
        except sqlite.OperationalError, Msg:
            self.connectionObject.rollback()
            utils.pop_up_info("The SQL query\n %s\n seems to be invalid.\n\n%s" %(query,Msg), 'Error', None)
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
        query = (r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name in('obs_points',
        'obs_lines',
        'obs_p_w_lvl',
        'obs_p_w_qual_field',
        'obs_p_w_qual_lab',
        'obs_p_w_strat',
        'seismic_data',
        'sqlite_stat3',
        'vlf_data',
        'w_flow',
        'w_qual_field_geom',
        'zz_flowtype',
        'w_qual_lab',
        'w_qual_field',
        'stratigraphy',
        'about_db',
        'geom_cols_ref_sys',
        'geometry_columns',
        'geometry_columns_time',
        'spatial_ref_sys',
        'spatialite_history',
        'vector_layers',
        'views_geometry_columns',
        'virts_geometry_columns',
        'geometry_columns_auth',
        'geometry_columns_fields_infos',
        'geometry_columns_statistics',
        'sql_statements_log',
        'layer_statistics',
        'sqlite_sequence',
        'sqlite_stat1' ,
        'views_layer_statistics',
        'virts_layer_statistics',
        'vector_layers_auth',
        'vector_layers_field_infos',
        'vector_layers_statistics',
        'views_geometry_columns_auth',
        'views_geometry_columns_field_infos',
        'views_geometry_columns_statistics',
        'virts_geometry_columns_auth',
        'virts_geometry_columns_field_infos',
        'virts_geometry_columns_statistics' ,
        'geometry_columns',
        'spatialindex',
        'SpatialIndex')) ORDER BY tbl_name""" )  #SQL statement to get the relevant tables in the spatialite database
        tabeller = utils.sql_load_fr_db(query)[1]
        #self.dbTables = {} 
        self.wlvltableComboBox.addItem('')         
        for tabell in tabeller:
            self.wlvltableComboBox.addItem(tabell[0])
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
                msg='please notice that DEM(s) must be single band rasters and have same crs as your selected vector line layer'
                if layer.bandCount()==1:#only single band raster layers
                    #print('raster layer '  + layer.name() + ' has crs '+str(layer.crs().authid()[5:]))#debug
                    #print('polyline layer ' + self.sectionlinelayer.name() + ' has crs '+str(self.line_crs.authid()[5:]))#debug
                    if layer.crs().authid()[5:] == self.line_crs.authid()[5:]:#only raster layer with crs corresponding to line layer
                        self.rastItems[unicode(layer.name())] = layer
                        self.inData.addItem(unicode(layer.name()))
        if msg !='':
            self.iface.messageBar().pushMessage("Info",msg, 0,duration=10)
        self.get_dem_selection()

    def finish_plot(self):
        leg = self.secax.legend(self.p, self.Labels,loc=0 )
        leg.draggable(state=True)
        frame  = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
        frame.set_facecolor('1')    # set the frame face color to white                
        frame.set_fill(False)    # set the frame face color to white                
        for t in leg.get_texts():
            t.set_fontsize(10) 

        self.secax.grid(b=True, which='both', color='0.65',linestyle='-')
        self.secax.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.secax.xaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))
        self.secax.set_ylabel(unicode("Level, masl",'utf-8'))  #Allows international characters ('åäö') as ylabel
        self.secax.set_xlabel(unicode("Distance along section",'utf-8'))  #Allows international characters ('åäö') as xlabel
        for label in self.secax.xaxis.get_ticklabels():
            label.set_fontsize(10)
        for label in self.secax.yaxis.get_ticklabels():
            label.set_fontsize(10)
        """
        if there is no stratigraphy data and no borehole lenght for first or last observations,
        then autscaling will fail silently since it does not consider axes.annotate (which is used for printing obsid)
        hence this special treatment to check if xlim are less than expected from lengthalong
        """
        #self.secax.autoscale(enable=True, axis='both', tight=None)
        xmin, xmax = self.secax.get_xlim()
        self.secax.set_xlim(min(float(min(self.LengthAlong))-self.barwidth,xmin), max(float(max(self.LengthAlong))+self.barwidth,xmax))
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
        sql = r"""SELECT obsid AS "obsid",
        GLength(l.geometry)*ST_Line_Locate_Point(l.geometry, p.geometry) AS "abs_dist"
        FROM a.%s AS l, (select * from obs_points where obsid in %s) AS p
        GROUP BY obsid ORDER BY ST_Line_Locate_Point(l.geometry, p.geometry);"""%(self.temptableName,obsidtuple)
        data = self.connectionObject.cursor().execute(sql).fetchall()
        #data = utils.sql_load_fr_db(sql)[1]
        My_format = [('obs_id', np.str_, 32),('length', float)] #note that here is a limit of maximum 32 characters in obsid
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
                    sql = u'select h_toc, h_gs, length from obs_points where obsid = "' + obs + u'"'
                    recs = utils.sql_load_fr_db(sql)[1]
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
                    
                sql=u'select "depthbot"-"depthtop", stratid, geology, geoshort, capacity, development, comment from stratigraphy where obsid = "' + obs + u'" and lower(geoshort) ' + self.PlotTypes[Typ] + u" order by stratid"
                if utils.sql_load_fr_db(sql)[1]:
                    recs = utils.sql_load_fr_db(sql)[1]#[0][0]
                    j=0#counter for unique stratid
                    for rec in recs:#loop cleanup
                        BarLength.append(rec[0])#loop cleanup
                        x.append(float(self.LengthAlong[k]))# - self.barwidth/2)
                        sql01 = u'select "h_gs" from obs_points where obsid = "' + obs + u'"'
                        sql02 = u'select "h_toc" from obs_points where obsid = "' + obs + u'"'
                        #print('h_gs for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql01)[1])[0][0]))#debug
                        #print('h_toc for ' + obs + ' is ' + str((utils.sql_load_fr_db(sql02)[1])[0][0]))#debug
                        
                        if utils.isfloat(str((utils.sql_load_fr_db(sql01)[1])[0][0])) and (utils.sql_load_fr_db(sql01)[1])[0][0]>-999:
                            z_gs.append(float(str((utils.sql_load_fr_db(sql01)[1])[0][0])))
                        elif utils.isfloat(str((utils.sql_load_fr_db(sql02)[1])[0][0])) and (utils.sql_load_fr_db(sql02)[1])[0][0]>-999:
                            z_gs.append(float(str((utils.sql_load_fr_db(sql02)[1])[0][0])))
                        else:
                            z_gs.append(0)
                        Bottom.append(z_gs[i]- float(str((utils.sql_load_fr_db(u'select "depthbot" from stratigraphy where obsid = "' + obs + u'" and stratid = ' + str(recs[j][1])+ u' and lower(geoshort) ' + self.PlotTypes[Typ])[1])[0][0])))
                        #lists for plotting annotation 
                        self.x_txt.append(x[i])#+ self.barwidth/2)#x-coord for text
                        self.z_txt.append(Bottom[i] + recs[j][0]/2)#Z-value for text
                        self.geology_txt.append(utils.null_2_empty_string(utils.returnunicode(recs[j][2])))
                        self.geoshort_txt.append(utils.null_2_empty_string(utils.returnunicode(recs[j][3])))
                        self.capacity_txt.append(utils.null_2_empty_string(utils.returnunicode(recs[j][4])))
                        self.development_txt.append(utils.null_2_empty_string(utils.returnunicode(recs[j][5])))
                        self.comment_txt.append(utils.null_2_empty_string(utils.returnunicode(recs[j][6])))
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
            sql = r"""select "%s" as x, "%s" as y1, "%s" as y2 from "%s" where obsid='%s'"""%(x, self.y1_column,self.y2_column,table,obsline_id)
            conn_OK, recs = utils.sql_load_fr_db(sql)
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
            query = r"""select obsid from obs_points where lower(drillstop) like '""" +self.ms.settingsdict['secplotdrillstop'] +r"""'"""
            result = utils.sql_load_fr_db(query)
            if result[1]:
                for item in result[1]:
                    self.obs_p_w_drill_stops.append(item[0])

        q=0
        for obs in self.selected_obsids:#Finally adding obsid at top of stratigraphy
            if obs in self.obsids_w_wl and self.ms.settingsdict['secplotdates'] and len(self.ms.settingsdict['secplotdates'])>0:
                query = r"""select avg("level_masl") from """ + self.ms.settingsdict['secplotwlvltab'] + r""" where obsid = '""" + obs + r"""' and ((date_time >= '""" + min(self.ms.settingsdict['secplotdates']) + r"""' and date_time <= '""" + max(self.ms.settingsdict['secplotdates']) + r"""') or (date_time like '""" + min(self.ms.settingsdict['secplotdates']) + r"""%' or date_time like '""" + max(self.ms.settingsdict['secplotdates']) + r"""%'))"""
                #print(query)#debug
                recs = utils.sql_load_fr_db(query)[1]
                if utils.sql_load_fr_db(query)[1]:
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
                lineplot,=self.secax.plot(xarray, DEMdata, marker = 'None', linestyle = '-')#The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1
                self.p.append(lineplot)
                self.Labels.append(layername)
            QgsMapLayerRegistry.instance().removeMapLayer(temp_memorylayer.id())

    def plot_drill_stop(self): 
        lineplot,=self.secax.plot(self.x_ds, self.z_ds,  '^', markersize = 8,color='black')
        self.p.append(lineplot)
        self.Labels.append('drillstop like ' + self.ms.settingsdict['secplotdrillstop'])

    def plot_geology(self):
        for Typ in self.ExistingPlotTypes:#Adding a plot for each "geoshort" that is identified
            plotxleftbarcorner = [i - self.barwidth/2 for i in self.plotx[Typ]]#subtract half bar width from x position (x position is stored as bar center in self.plotx)
            self.p.append(self.secax.bar(plotxleftbarcorner,self.plotbarlength[Typ], color=self.Colors[Typ], edgecolor='black', hatch=self.Hatches[Typ], width = self.barwidth, bottom=self.plotbottom[Typ]))#matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)
            self.Labels.append(Typ)

    def plot_obs_lines_data(self):
        lineplot, = self.secax.plot(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y1, marker = 'None', linestyle = '-')# PLOT!!
        self.p.append(lineplot)
        self.Labels.append(self.y1_column)
        lineplot, = self.secax.plot(self.obs_lines_plot_data.obsline_x, self.obs_lines_plot_data.obsline_y2, marker = 'None', linestyle = '-')# PLOT!!
        self.p.append(lineplot)
        self.Labels.append(self.y2_column)
        
    def plot_water_level(self):   # Adding a plot for each water level date identified
        self.obsids_w_wl = []
        for datum in self.ms.settingsdict['secplotdates']:
            WL = []
            x_wl=[]
            k=0
            for obs in self.selected_obsids:
                query = u'select level_masl from ' + self.ms.settingsdict['secplotwlvltab'] + ' where obsid = "' + obs + '" and date_time like "' + datum  +'%"' 
                if utils.sql_load_fr_db(query)[1]:
                    WL.append((utils.sql_load_fr_db(query)[1])[0][0])
                    x_wl.append(float(self.LengthAlong[k]))
                    if obs not in self.obsids_w_wl:
                        self.obsids_w_wl.append(obs)
                k += 1
            lineplot,=self.secax.plot(x_wl, WL,  'v-', markersize = 6)#The comma is terribly annoying and also different from a bar plot, see http://stackoverflow.com/questions/11983024/matplotlib-legends-not-working and http://stackoverflow.com/questions/10422504/line-plotx-sinx-what-does-comma-stand-for?rq=1
            self.p.append(lineplot)
            self.Labels.append(datum)

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
        
    def set_location(self):#not ready
        dockarea = self.parent.dockWidgetArea(self)
        self.ms.settingsdict['secplotlocation']=dockarea

    def upload_qgis_vector_layer(self, layer, srid=None,selected=False, mapinfo=True,Attributes=False): #from qspatialite, with a few  changes LAST ARGUMENT IS USED TO SKIP ARGUMENTS SINCE WE ONLY WANT THE GEOMETRY TO CALCULATE DISTANCES
        """Upload layer (QgsMapLayer) (optionnaly only selected values ) into current DB, in self.temptableName (string) with desired SRID (default layer srid if None) - user can desactivate mapinfo compatibility Date importation. Return True if operation succesfull or false in all other cases"""
        selected_ids=[]
        if selected==True :
            if layer.selectedFeatureCount()==0:
                utils.pop_up_info("No selected item in Qgis layer: %s)"%layer.name(),self.parent)
                return False
            select_ids=layer.selectedFeaturesIds()
        #Create name for table if not provided by user
        if self.temptableName in (None,''):
            self.temptableName=layer.name()
        #Verify if self.temptableName already exists in DB
        ExistingNames=self.connectionObject.cursor().execute(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""").fetchall()
        ExistingNames_attached = self.connectionObject.cursor().execute(r"""SELECT tbl_name FROM a.sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""").fetchall()
        #ExistingNames=[table.name for table in self.tables]
        #Propose user to automatically rename DB
        for _ExistingNames in [ExistingNames, ExistingNames_attached]:
            for existingname in _ExistingNames:  #this should only be needed if an earlier import failed
                if str(existingname[0]) == str(self.temptableName):
                    self.temptableName = '%s_2' % self.temptableName
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        mapinfoDAte=[]
        for id,name in enumerate(provider.fields().toList()):
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldTypeName=='DATE' and unicode(provider.storageType()).lower()==u'mapinfo file'and mapinfo==True: # Mapinfo DATE compatibility
                fldType='DATE'
                mapinfoDAte.append([id,fldName]) #stock id and name of DATE field for MAPINFO layers
            elif fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is TEXT
                fldLength=name.length()
                fldType='TEXT(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool,PyQt4.QtCore.QVariant.Int,PyQt4.QtCore.QVariant.LongLong,PyQt4.QtCore.QVariant.UInt,PyQt4.QtCore.QVariant.ULongLong): # field type is INTEGER
                fldType='INTEGER'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is DOUBLE
                fldType='REAL'
            else: # field type is not recognized by SQLITE
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())

        # is it a geometric table ?
        geometry=False
        if layer.hasGeometryType():
            #Get geometry type
            geom=['MULTIPOINT','MULTILINESTRING','MULTIPOLYGON','UnknownGeometry']
            geometry=geom[layer.geometryType()]
            #Project to new SRID if specified by user:
            if srid==None:
                srid=layer.crs().postgisSrid()
            else:
                Qsrid = QgsCoordinateReferenceSystem()
                Qsrid.createFromId(srid)
                if not Qsrid.isValid(): #check if crs is ok
                    utils.pop_up_info("Destination SRID isn't valid for table %s"%layer.name(),self.parent)
                    return False
                layer.setCrs(Qsrid)

        #select attributes to import (remove Pkuid if already exists):
        allAttrs = provider.attributeIndexes()
        fldDesc = provider.fieldNameIndex("PKUID")
        if fldDesc != -1:
            print "Pkuid already exists and will be replaced!"
            del allAttrs[fldDesc] #remove pkuid Field
            del fields[fldDesc] #remove pkuid Field
        #provider.select(allAttrs)
        #request=QgsFeatureRequest()
        #request.setSubsetOfAttributes(allAttrs).setFlags(QgsFeatureRequest.SubsetOfAttributes)
        
        #Create new table in DB
        if Attributes == False:
            fields=[]
        if geometry:
            fields.insert(0,"Geometry %s"%geometry)
        
        fields=','.join(fields)
        if len(fields)>0:
            fields=', %s'%fields

        self.connection()
        query="""CREATE TABLE "a"."%s" ( PKUID INTEGER PRIMARY KEY AUTOINCREMENT %s )"""%(self.temptableName, fields)
        header,data=self.execute_query(query)
        if self.queryPb:
            return
        self.connectionObject.commit()
    
        #Recover Geometry Column:
        if geometry:
            header,data=self.execute_query("""SELECT RecoverGeometryColumn('a.%s','Geometry',%s,'%s',2) from %s AS a"""%(self.temptableName,srid,geometry, self.temptableName))
        
        # Retreive every feature
        for feat in layer.getFeatures():
            # selected features:
            if selected and feat.id()not in select_ids:
                continue 
        
            #PKUID and Geometry        
            values_auto=['NULL'] #PKUID value
            if geometry:
                geom = feat.geometry()
                #WKB=geom.asWkb()
                WKT=geom.exportToWkt()
                values_auto.append('CastToMulti(GeomFromText("%s",%s))'%(WKT,srid))
        
            # show all attributes and their values
            values_perso=[]
            for val in allAttrs: # All except PKUID
                values_perso.append(feat[val])
            
            #Create line in DB table         ---------------------SOME PROBLEMS HERE WHEN THERE ARE NO ATTRIBUTES , GÅR BRA OM MAN HAR MINST ETT PAR ATTRIBUT
            #MEN VI KAN LIKA GÄRNA STRUNTA I ATTRIBUTEN
            if Attributes == True:
                if len(fields)>0:
                    query="""INSERT INTO "a"."%s" VALUES (%s,%s)"""%(self.temptableName,','.join([unicode(value).encode('utf-8') for value in values_auto]),','.join('?'*len(values_perso)))
                    header,data=self.execute_query(query,tuple([unicode(value) for value in values_perso]))
                else: #no attribute Datas
                    query="""INSERT INTO "a"."%s" VALUES (%s)"""%(self.temptableName,','.join([unicode(value).encode('utf-8') for value in values_auto]))
                    header,data=self.execute_query(query)
            else:
                query="""INSERT INTO "a"."%s" VALUES (%s)"""%(self.temptableName,','.join([unicode(value).encode('utf-8') for value in values_auto]))
                header,data=self.execute_query(query)
        for date in mapinfoDAte: #mapinfo compatibility: convert date in SQLITE format (2010/02/11 -> 2010-02-11 ) or rollback if any error
            header,data=self.execute_query("""UPDATE OR ROLLBACK "a"."%s" set '%s'=replace( "%s", '/' , '-' )  """%(self.temptableName,date[1],date[1]))

        #Commit DB connection:
        self.connectionObject.commit()
        #utils.MessagebarAndLog.info(log_msg=u'Data in new table:' + utils.returnunicode(self.execute_query(u'select * from "a".%s'%self.temptableName)[1]))
        #self.connectionObject.close()#THIS WAS NOT IN QSPATIALITE CODE!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # reload tables
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
            self.annotationtext = self.secax.annotate(o,xy=(m,n),xytext=(5,0), textcoords='offset points',ha = 'left', va = 'center',fontsize=9,bbox = dict(boxstyle = 'square,pad=0.05', fc = 'white', edgecolor='white', alpha = 0.6))#textcoords = 'offset points' makes the text being written xytext points from the data point xy (xy positioned with respect to axis values and then the text is offset a specific number of points from that point

    def write_obsid(self, plot_labels=2):#annotation, and also empty bars to show drillings without stratigraphy data
        if self.ms.settingsdict['stratigraphyplotted'] ==2:#if stratigr plot, then obsid written close to toc or gs
            plotxleftbarcorner = [i - self.barwidth/2 for i in self.x_id]#x-coord for bars at each obs
            self.p.append(self.secax.bar(plotxleftbarcorner,self.barlengths, fill=False, edgecolor='black', width = self.barwidth, bottom=self.bottoms))#matplotlib.pyplot.bar(left, height, width=0.8, bottom=None, hold=None, **kwargs)#plot empty bars
            if plot_labels==2:#only plot the obsid as annotation if plot_labels is 2, i.e. if checkbox is activated
                for m,n,o in zip(self.x_id,self.z_id,self.selected_obsids):#change last arg to the one to be written in plot
                    self.secax.annotate(o,xy=(m,n),xytext=(0,10), textcoords='offset points',ha = 'center', va = 'top',fontsize=9,bbox = dict(boxstyle = 'square,pad=0.05', fc = 'white', edgecolor='white', alpha = 0.4))
        else: #obsid written close to average water level (average of all water levels between given min and max date) 
            if plot_labels==2:#only plot the obsid as annotation if plot_labels is 2, i.e. if checkbox is activated            
                for m,n,o in zip(self.x_id_wwl,self.z_id_wwl,self.obsid_wlid):#change last arg to the one to be written in plot
                        self.secax.annotate(o,xy=(m,n),xytext=(0,10), textcoords='offset points',ha = 'center', va = 'top',fontsize=9,bbox = dict(boxstyle = 'square,pad=0.05', fc = 'white', edgecolor='white', alpha = 0.4))        
