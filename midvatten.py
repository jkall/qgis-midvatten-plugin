# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the main part of the Midvatten plugin. 
 Mainly controlling user interaction and calling for other classes. 
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtCore import QDir
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
import shutil
import resources  # Initialize Qt resources from file resources.py

# Import some general python modules
import os.path
import sys
import datetime
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED
from tempfile import NamedTemporaryFile

#add midvatten plugin directory to pythonpath (needed here to allow importing modules from subfolders)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/tools'))

# Add translate
import util_translate

# Import Midvatten tools and modules
from tsplot import TimeSeriesPlot
from stratigraphy import Stratigraphy
from xyplot import XYPlot
from wqualreport import wqualreport
from loaddefaultlayers import LoadLayers
from prepareforqgis2threejs import PrepareForQgis2Threejs
import midvatten_utils as utils 
from definitions import midvatten_defs
from sectionplot import SectionPlot
import customplot
from midvsettings import midvsettings
import midvsettingsdialog
from piper import PiperPlot
from export_data import ExportData
import PyQt4
#import profilefromdem

tr = PyQt4.QtCore.QCoreApplication.translate

class midvatten:
    def __init__(self, iface): # Might need revision of variables and method for loading default variables
        #sys.path.append(os.path.dirname(os.path.abspath(__file__))) #add midvatten plugin directory to pythonpath
        self.iface = iface
        self.ms = midvsettings()#self.ms.settingsdict is created when ms is imported
        import util_translate
        self.translator = util_translate.getTranslate( 'midvatten' )
        
    def initGui(self):
        # Create actions that will start plugin configuration
        self.actionNewDB = QAction(QIcon(":/plugins/midvatten/icons/create_new.xpm"), tr("Midvatten","Create a new Midvatten project DB"), self.iface.mainWindow())
        QObject.connect(self.actionNewDB, SIGNAL("triggered()"), self.new_db)
        
        self.actionloadthelayers = QAction(QIcon(":/plugins/midvatten/icons/loaddefaultlayers.png"), tr("Midvatten","Load default db-layers to qgis"), self.iface.mainWindow())
        self.actionloadthelayers.setWhatsThis(tr("Midvatten","Load default layers from the selected database"))
        self.iface.registerMainWindowAction(self.actionloadthelayers, "F7")   # The function should also be triggered by the F7 key
        QObject.connect(self.actionloadthelayers, SIGNAL("activated()"), self.loadthelayers)

        self.actionsetup = QAction(QIcon(":/plugins/midvatten/icons/MidvSettings.png"), tr("Midvatten","Midvatten Settings"), self.iface.mainWindow())
        self.actionsetup.setWhatsThis(tr("Midvatten","Configuration for Midvatten toolset"))
        self.iface.registerMainWindowAction(self.actionsetup, "F6")   # The function should also be triggered by the F6 key
        QObject.connect(self.actionsetup, SIGNAL("activated()"), self.setup)
        
        self.actionresetSettings = QAction(QIcon(":/plugins/midvatten/icons/ResetSettings.png"), tr("Midvatten","Reset Settings"), self.iface.mainWindow())
        QObject.connect(self.actionresetSettings, SIGNAL("triggered()"), self.reset_settings)
        
        self.actionabout = QAction(QIcon(":/plugins/midvatten/icons/about.png"), tr("Midvatten","About"), self.iface.mainWindow())
        QObject.connect(self.actionabout, SIGNAL("triggered()"), self.about)
        
        #self.actionupdatecoord = QAction(QIcon(":/plugins/midvatten/icons/updatecoordfrpos.png"), "Update coordinates from map position", self.iface.mainWindow())
        #QObject.connect(self.actionupdatecoord , SIGNAL("triggered()"), self.updatecoord)
        
        #self.actionupdateposition = QAction(QIcon(":/plugins/midvatten/icons/updateposfrcoord.png"), "Update map position from coordinates", self.iface.mainWindow())
        #QObject.connect(self.actionupdateposition , SIGNAL("triggered()"), self.updateposition)
        
        self.action_import_wlvl = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_manual.png"), tr("Midvatten","Import w level measurements"), self.iface.mainWindow())
        QObject.connect(self.action_import_wlvl , SIGNAL("triggered()"), self.import_wlvl)
        
        self.action_import_wflow = QAction(QIcon(":/plugins/midvatten/icons/load_wflow.png"), tr("Midvatten","Import w flow measurements"), self.iface.mainWindow())
        QObject.connect(self.action_import_wflow , SIGNAL("triggered()"), self.import_wflow)
        
        self.action_import_seismics = QAction(QIcon(":/plugins/midvatten/icons/load_seismics.png"), tr("Midvatten","Import seismic data"), self.iface.mainWindow())
        QObject.connect(self.action_import_seismics , SIGNAL("triggered()"), self.import_seismics)
        
        self.action_import_vlf = QAction(QIcon(":/plugins/midvatten/icons/load_vlf.png"), tr("Midvatten","Import vlf data"), self.iface.mainWindow())
        QObject.connect(self.action_import_vlf , SIGNAL("triggered()"), self.import_vlf)
        
        self.action_import_obs_lines = QAction(QIcon(":/plugins/midvatten/icons/import_obs_lines.png"), tr("Midvatten","Import obs lines table"), self.iface.mainWindow())
        QObject.connect(self.action_import_obs_lines , SIGNAL("triggered()"), self.import_obs_lines)
        
        self.action_wlvlcalculate = QAction(QIcon(":/plugins/midvatten/icons/calc_level_masl.png"), tr("Midvatten","Calculate w level from manual measurements"), self.iface.mainWindow())
        QObject.connect(self.action_wlvlcalculate , SIGNAL("triggered()"), self.wlvlcalculate)
        
        self.action_aveflowcalculate = QAction(QIcon(":/plugins/midvatten/icons/import_wflow.png"), tr("Midvatten","Calculate Aveflow from Accvol"), self.iface.mainWindow())
        QObject.connect(self.action_aveflowcalculate , SIGNAL("triggered()"), self.aveflowcalculate)
        
        self.action_import_wlvllogg = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_logger.png"), tr("Midvatten","Import w level from logger"), self.iface.mainWindow())
        QObject.connect(self.action_import_wlvllogg , SIGNAL("triggered()"), self.import_wlvllogg)

        self.action_import_diverofficedata = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_logger.png"), tr("Midvatten","Import logger data using Diver-Office format"), self.iface.mainWindow())
        QObject.connect(self.action_import_diverofficedata, SIGNAL("triggered()"), self.import_diverofficedata)
        
        self.action_wlvlloggcalibrate = QAction(QIcon(":/plugins/midvatten/icons/calibr_level_logger_masl.png"), tr("Midvatten","Calcultate logger w level from logger water head"), self.iface.mainWindow())
        QObject.connect(self.action_wlvlloggcalibrate , SIGNAL("triggered()"), self.wlvlloggcalibrate)

        self.actionimport_wqual_lab = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_lab.png"), tr("Midvatten","Import w quality from lab"), self.iface.mainWindow())
        QObject.connect(self.actionimport_wqual_lab, SIGNAL("triggered()"), self.import_wqual_lab)

        self.actionimport_wqual_lab_from_interlab4 = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_lab.png"), tr("Midvatten","Import w quality from lab data using interlab4 format"), self.iface.mainWindow())
        QObject.connect(self.actionimport_wqual_lab_from_interlab4, SIGNAL("triggered()"), self.import_wqual_lab_from_interlab4)
        
        self.actionimport_wqual_field = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_field.png"), tr("Midvatten","Import w quality from field"), self.iface.mainWindow())
        QObject.connect(self.actionimport_wqual_field, SIGNAL("triggered()"), self.import_wqual_field)
        
        self.actionimport_stratigraphy = QAction(QIcon(":/plugins/midvatten/icons/import_stratigraphy.png"), tr("Midvatten","Import stratigraphy data"), self.iface.mainWindow())
        QObject.connect(self.actionimport_stratigraphy, SIGNAL("triggered()"), self.import_stratigraphy)
        
        self.actionimport_obs_points = QAction(QIcon(":/plugins/midvatten/icons/import_obs_points.png"), tr("Midvatten","Import obs points table"), self.iface.mainWindow())
        QObject.connect(self.actionimport_obs_points, SIGNAL("triggered()"), self.import_obs_points)
        
        self.actionimport_wflow = QAction(QIcon(":/plugins/midvatten/icons/import_wflow.png"), tr("Midvatten","Import w flow measurements"), self.iface.mainWindow())
        QObject.connect(self.actionimport_wflow, SIGNAL("triggered()"), self.import_wflow)
        
        self.actionimport_meteo = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_field.png"), tr("Midvatten","Import meteorological observations"), self.iface.mainWindow())
        QObject.connect(self.actionimport_meteo, SIGNAL("triggered()"), self.import_meteo)

        self.actionimport_fieldlogger = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_field.png"), tr("Midvatten","Import data using FieldLogger format"), self.iface.mainWindow())
        QObject.connect(self.actionimport_fieldlogger, SIGNAL("triggered()"), self.import_fieldlogger)

        self.actiongeneral_import_csv = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_field.png"), tr("Midvatten","Import data using general csv format"), self.iface.mainWindow())
        QObject.connect(self.actiongeneral_import_csv, SIGNAL("triggered()"), self.import_csv)

        self.actionPlotTS = QAction(QIcon(":/plugins/midvatten/icons/PlotTS.png"), tr("Midvatten","Time series plot"), self.iface.mainWindow())
        self.actionPlotTS.setWhatsThis(tr("Midvatten","Plot time series for selected objects"))
        self.iface.registerMainWindowAction(self.actionPlotTS, "F8")   # The function should also be triggered by the F8 key
        QObject.connect(self.actionPlotTS, SIGNAL("triggered()"), self.plot_timeseries)
        
        self.actionPlotXY = QAction(QIcon(":/plugins/midvatten/icons/PlotXY.png"), tr("Midvatten","Scatter plot"), self.iface.mainWindow())
        self.actionPlotXY.setWhatsThis(tr("Midvatten","Plot XY scatter data (e.g. seismic profile) for the selected objects"))
        self.iface.registerMainWindowAction(self.actionPlotXY, "F9")   # The function should also be triggered by the F9 key
        QObject.connect(self.actionPlotXY, SIGNAL("triggered()"), self.plot_xy)
        
        self.actionPlotPiper = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons","Piper.png")), tr("Midvatten","Piper diagram"), self.iface.mainWindow())
        self.actionPlotPiper.setWhatsThis(tr("Midvatten","Plot a rectangular Piper diagram for selected objects"))
        QObject.connect(self.actionPlotPiper, SIGNAL("triggered()"), self.plot_piper)
                
        self.actionPlotSQLite = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons","plotsqliteicon.png")), tr("Midvatten","Custom plots"), self.iface.mainWindow())
        self.actionPlotSQLite.setWhatsThis(tr("Midvatten","Create custom plots for your reports"))
        QObject.connect(self.actionPlotSQLite, SIGNAL("triggered()"), self.plot_sqlite)
        
        self.actionPlotStratigraphy = QAction(QIcon(":/plugins/midvatten/icons/PlotStratigraphy.png"), tr("Midvatten","Stratigraphy plot"), self.iface.mainWindow())
        self.actionPlotStratigraphy.setWhatsThis(tr("Midvatten","Show stratigraphy for selected objects (modified ARPAT)"))
        self.iface.registerMainWindowAction(self.actionPlotStratigraphy, "F10")   # The function should also be triggered by the F10 key
        QObject.connect(self.actionPlotStratigraphy, SIGNAL("triggered()"), self.plot_stratigraphy)
        
        self.actiondrillreport = QAction(QIcon(":/plugins/midvatten/icons/drill_report.png"), tr("Midvatten","General report"), self.iface.mainWindow())
        self.actiondrillreport.setWhatsThis(tr("Midvatten","Show a general report for the selected obs point"))
        self.iface.registerMainWindowAction(self.actiondrillreport, "F11")   # The function should also be triggered by the F11 key
        QObject.connect(self.actiondrillreport, SIGNAL("triggered()"), self.drillreport)

        self.actionwqualreport = QAction(QIcon(":/plugins/midvatten/icons/wqualreport.png"), tr("Midvatten","Water quality report"), self.iface.mainWindow())
        self.actionwqualreport.setWhatsThis(tr("Midvatten","Show water quality for the selected obs point"))
        self.iface.registerMainWindowAction(self.actionwqualreport, "F12")   # The function should also be triggered by the F12 key
        QObject.connect(self.actionwqualreport, SIGNAL("triggered()"), self.waterqualityreport)

        self.actionPlotSection = QAction(QIcon(":/plugins/midvatten/icons/PlotSection.png"), tr("Midvatten","Section plot"), self.iface.mainWindow())
        self.actionPlotSection.setWhatsThis(tr("Midvatten","Plot a section with stratigraphy and water levels"))
        #self.iface.registerMainWindowAction(self.actionChartMaker, "F12")   # The function should also be triggered by the F12 key
        QObject.connect(self.actionPlotSection, SIGNAL("triggered()"), self.plot_section)
        
        self.actionPrepareFor2Qgis2ThreeJS = QAction(QIcon(":/plugins/midvatten/icons/qgis2threejs.png"), tr("Midvatten","Prepare 3D-data for Qgis2threejs plugin"), self.iface.mainWindow())
        self.actionPrepareFor2Qgis2ThreeJS.setWhatsThis(tr("Midvatten","Add spatialite views to be used by Qgis2threejs plugin to create a 3D plot"))
        QObject.connect(self.actionPrepareFor2Qgis2ThreeJS, SIGNAL("triggered()"), self.prepare_layers_for_qgis2threejs)

        self.actionloaddatadomains = QAction(QIcon(":/plugins/midvatten/icons/loaddatadomains.png"), tr("Midvatten","Load data domain tables to qgis"), self.iface.mainWindow())
        self.actionloadthelayers.setWhatsThis(tr("Midvatten","Load the data domain tables from the database"))
        QObject.connect(self.actionloaddatadomains, SIGNAL("activated()"), self.load_data_domains)

        self.actionVacuumDB = QAction(QIcon(":/plugins/midvatten/icons/vacuum.png"), tr("Midvatten","Vacuum the database"), self.iface.mainWindow())
        self.actionVacuumDB.setWhatsThis(tr("Midvatten","Perform database vacuuming"))
        QObject.connect(self.actionVacuumDB, SIGNAL("triggered()"), self.vacuum_db)

        self.actionZipDB = QAction(QIcon(":/plugins/midvatten/icons/zip.png"), tr("Midvatten","Backup the database"), self.iface.mainWindow())
        self.actionZipDB.setWhatsThis(tr("Midvatten","A compressed copy of the database will be placed in same directory as the db."))
        QObject.connect(self.actionZipDB, SIGNAL("triggered()"), self.zip_db)

        self.action_export_csv = QAction(QIcon(":/plugins/midvatten/icons/export_csv.png"), tr("Midvatten","Export to a set of csv files"), self.iface.mainWindow())
        self.action_export_csv.setWhatsThis(tr("Midvatten","All data for the selected objects (obs_points and obs_lines) will be exported to a set of csv files."))
        QObject.connect(self.action_export_csv, SIGNAL("triggered()"), self.export_csv)

        self.action_export_spatialite = QAction(QIcon(":/plugins/midvatten/icons/export_spatialite.png"), tr("Midvatten","Export to another spatialite db"), self.iface.mainWindow())
        self.action_export_spatialite.setWhatsThis(tr("Midvatten","All data for the selected objects (obs_points and obs_lines) will be exported to another spatialite db."))
        QObject.connect(self.action_export_spatialite, SIGNAL("triggered()"), self.export_spatialite)

        self.action_export_fieldlogger = QAction(QIcon(":/plugins/midvatten/icons/export_csv.png"), tr("Midvatten","Export to FieldLogger format"), self.iface.mainWindow())
        self.action_export_fieldlogger.setWhatsThis(self.export_fieldlogger.__doc__)
        QObject.connect(self.action_export_fieldlogger, SIGNAL("triggered()"), self.export_fieldlogger)

        self.action_calculate_statistics_for_all_w_logger_data = QAction(QIcon(":/plugins/midvatten/icons/calc_statistics.png"), tr("Midvatten","Calculate statistics for all w logger data"), self.iface.mainWindow())
        self.action_calculate_statistics_for_all_w_logger_data.setWhatsThis(self.calculate_statistics_for_all_w_logger_data.__doc__)
        QObject.connect(self.action_calculate_statistics_for_all_w_logger_data, SIGNAL("triggered()"), self.calculate_statistics_for_all_w_logger_data)

        self.action_calculate_db_table_rows = QAction(QIcon(":/plugins/midvatten/icons/calc_statistics.png"), tr("Midvatten","Calculate database table rows"), self.iface.mainWindow())
        self.action_calculate_statistics_for_all_w_logger_data.setWhatsThis(self.calculate_db_table_rows.__doc__)
        QObject.connect(self.action_calculate_db_table_rows, SIGNAL("triggered()"), self.calculate_db_table_rows)

        # Add toolbar with buttons 
        self.toolBar = self.iface.addToolBar("Midvatten")
        self.toolBar.setObjectName("Midvatten")
        self.toolBar.addAction(self.actionsetup)
        #self.toolBar.addAction(self.actionloadthelayers)
        self.toolBar.addAction(self.actionPlotTS)
        self.toolBar.addAction(self.actionPlotXY)
        self.toolBar.addAction(self.actionPlotStratigraphy)
        self.toolBar.addAction(self.actionPlotSection)
        self.toolBar.addAction(self.actionPlotSQLite)
        self.toolBar.addAction(self.actionPlotPiper)
        self.toolBar.addAction(self.actiondrillreport)
        self.toolBar.addAction(self.actionwqualreport)
        #self.toolBar.addAction(self.actionChartMaker)
        
        # Add plugins menu items
        #self.menu = QMenu("Midvatten")
        self.menu = None
        # Check if the menu exists and get it
        for child in self.iface.mainWindow().menuBar().children(): 
            if isinstance(child,QMenu):
                if child.title() == "Midvatten": 
                    self.menu = child
        # If the menu does not exist, create it!
        self.owns_midv_menu = False #indicator that this plugin must not clean up the midvatten menu
        if not self.menu:
            self.owns_midv_menu = True #indicator that this plugin must clean up the midvatten menu
            self.menu = QMenu( "Midvatten", self.iface.mainWindow().menuBar() )
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)

        self.menu.import_data_menu = QMenu(tr("Midvatten", "&Import data to database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.import_data_menu)

        self.menu.import_data_menu_old = QMenu(tr("Midvatten", "&Old csv imports"))
        self.menu.import_data_menu.addMenu(self.menu.import_data_menu_old)
        self.menu.import_data_menu_old.addAction(self.actionimport_obs_points)
        self.menu.import_data_menu_old.addAction(self.action_import_wlvl)
        self.menu.import_data_menu_old.addAction(self.action_import_wlvllogg)
        self.menu.import_data_menu_old.addAction(self.actionimport_wqual_lab)
        self.menu.import_data_menu_old.addAction(self.actionimport_wqual_field)
        self.menu.import_data_menu_old.addAction(self.action_import_wflow)
        self.menu.import_data_menu_old.addAction(self.actionimport_stratigraphy)
        self.menu.import_data_menu_old.addAction(self.actionimport_meteo)
        self.menu.import_data_menu_old.addAction(self.action_import_obs_lines)
        self.menu.import_data_menu_old.addAction(self.action_import_seismics)
        self.menu.import_data_menu_old.addAction(self.action_import_vlf)

        self.menu.import_data_menu.addAction(self.actiongeneral_import_csv)
        self.menu.import_data_menu.addAction(self.action_import_diverofficedata)     
        self.menu.import_data_menu.addAction(self.actionimport_wqual_lab_from_interlab4)
        self.menu.import_data_menu.addAction(self.actionimport_fieldlogger)
        
        self.menu.export_data_menu = QMenu(tr("Midvatten", "&Export data from database"))
        self.menu.addMenu(self.menu.export_data_menu)
        self.menu.export_data_menu.addAction(self.action_export_csv)   
        self.menu.export_data_menu.addAction(self.action_export_spatialite)
        self.menu.export_data_menu.addAction(self.action_export_fieldlogger)
        
        self.menu.add_data_menu = QMenu(tr("Midvatten", "&Edit data in database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.add_data_menu)
        self.menu.add_data_menu.addAction(self.action_wlvlcalculate)   
        self.menu.add_data_menu.addAction(self.action_wlvlloggcalibrate)   
        #self.menu.add_data_menu.addAction(self.actionupdatecoord)   
        #self.menu.add_data_menu.addAction(self.actionupdateposition)   
        self.menu.add_data_menu.addAction(self.action_aveflowcalculate)   

        self.menu.plot_data_menu = QMenu(tr("Midvatten", "&View plot"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.plot_data_menu.menuAction())
        self.menu.addMenu(self.menu.plot_data_menu)
        self.menu.plot_data_menu.addAction(self.actionPlotTS) 
        self.menu.plot_data_menu.addAction(self.actionPlotXY)
        self.menu.plot_data_menu.addAction(self.actionPlotStratigraphy)
        self.menu.plot_data_menu.addAction(self.actionPlotSection)
        self.menu.plot_data_menu.addAction(self.actionPlotSQLite)
        self.menu.plot_data_menu.addAction(self.actionPlotPiper)

        self.menu.report_menu = QMenu(tr("Midvatten", "&View report"))
        self.menu.addMenu(self.menu.report_menu)
        self.menu.report_menu.addAction(self.actiondrillreport)
        self.menu.report_menu.addAction(self.actionwqualreport)
        
        self.menu.db_manage_menu = QMenu(tr("Midvatten", "&Database management"))
        self.menu.addMenu(self.menu.db_manage_menu)
        self.menu.db_manage_menu.addAction(self.actionNewDB)
        self.menu.db_manage_menu.addAction(self.actionVacuumDB)
        self.menu.db_manage_menu.addAction(self.actionZipDB)

        self.menu.utils = QMenu(tr("Midvatten", "&Utilities"))
        self.menu.addMenu(self.menu.utils)
        self.menu.utils.addAction(self.actionloaddatadomains)
        self.menu.utils.addAction(self.actionPrepareFor2Qgis2ThreeJS)
        self.menu.utils.addAction(self.actionresetSettings)
        self.menu.utils.addAction(self.action_calculate_statistics_for_all_w_logger_data)
        self.menu.utils.addAction(self.action_calculate_db_table_rows)

        self.menu.addSeparator()

        self.menu.addAction(self.actionloadthelayers)   
        self.menu.addAction(self.actionsetup)
        self.menu.addAction(self.actionabout)

        #menuBar = self.iface.mainWindow().menuBar()
        #menuBar.addMenu(self.menu)

        # QGIS iface connections
        self.iface.projectRead.connect(self.project_opened)
        self.iface.newProjectCreated.connect(self.project_created)

        #Connect message log to logfile.
        #Log file name must be set as env. variable QGIS_LOG_FILE in
        # settings > options > system > environment.
        QgsMessageLog.instance().messageReceived.connect(utils.write_qgs_log_to_file)


    def unload(self):    
        try:
            self.menu.removeAction(self.actionloadthelayers)
            self.menu.removeAction(self.actionsetup)
            self.menu.removeAction(self.actionabout)
        except:
            pass

        if self.owns_midv_menu: #indicator that this plugin must clean up the midvatten menu
            menubar = self.menu.parentWidget()
            menubar.removeAction(self.menu.menuAction())
            self.menu.deleteLater()
        
        # remove tool bar
        del self.toolBar
        
        # Also remove F5 - F12 key triggers
        self.iface.unregisterMainWindowAction(self.actionloadthelayers)
        self.iface.unregisterMainWindowAction(self.actionsetup)
        self.iface.unregisterMainWindowAction(self.actionPlotTS)
        self.iface.unregisterMainWindowAction(self.actionPlotXY)
        self.iface.unregisterMainWindowAction(self.actionPlotStratigraphy)
        self.iface.unregisterMainWindowAction(self.actiondrillreport)
        self.iface.unregisterMainWindowAction(self.actionwqualreport)
        sys.path.remove(os.path.dirname(os.path.abspath(__file__))) #Clean up python environment

    def about(self):   
        filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
        iniText = QSettings(filenamepath , QSettings.IniFormat)#This method seems to return a list of unicode strings BUT it seems as if the encoding from the byte strings in the file is not utf-8, hence there is need for special encoding, see below
        verno = str(iniText.value('version'))
        author = ', '.join(iniText.value('author'))
        email = str(iniText.value('email'))
        homepage = str(iniText.value('homepage'))

        ABOUT_templatefile = os.path.join(os.sep,os.path.dirname(__file__),"templates","about_template.htm")
        ABOUT_outpath = os.path.join(QDir.tempPath(), 'midvatten_about')
        if not os.path.exists(ABOUT_outpath):
            os.makedirs(ABOUT_outpath)
        ABOUT_outputfile = os.path.join(ABOUT_outpath, "about.htm")
        shutil.copy2(os.path.join(os.path.dirname(ABOUT_templatefile), 'midvatten_logga.png'), os.path.join(ABOUT_outpath, 'midvatten_logga.png'))

        f_in = open(ABOUT_templatefile, 'r')
        f_out = open(ABOUT_outputfile, 'w')
        wholefile = f_in.read().decode('cp1252')
        changedfile = wholefile.replace('VERSIONCHANGETHIS',verno).replace('AUTHORCHANGETHIS',author).replace('EMAILCHANGETHIS',email).replace('HOMEPAGECHANGETHIS',homepage)
        f_out.write(changedfile.encode('cp1252'))
        f_in.close()
        f_out.close()
        dlg = utils.HtmlDialog("About Midvatten plugin for QGIS",QUrl.fromLocalFile(ABOUT_outputfile))
        dlg.exec_()

    def aveflowcalculate(self):
        allcritical_layers = ('obs_points', 'w_flow') #none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some feature(s) is selected
        if err_flag == 0:     
            from w_flow_calc_aveflow import calcave
            dlg = calcave(self.iface.mainWindow()) 
            dlg.exec_()

    def drillreport(self):
        allcritical_layers = ('obs_points', 'w_levels', 'w_qual_lab')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        err_flag = utils.verify_layer_selection(err_flag,1)#verify the selected layer has attribute "obsid" and that exactly one feature is selected
        if err_flag == 0:
            obsids = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())  # selected obs_point is now found in obsid[0]
            from drillreport import drillreport
            drillreport(obsids,self.ms.settingsdict)

    def export_csv(self):
        allcritical_layers = tuple(midvatten_defs.get_subset_of_tables_fr_db('obs_points') + midvatten_defs.get_subset_of_tables_fr_db('obs_lines') + midvatten_defs.get_subset_of_tables_fr_db('data_domains') + midvatten_defs.get_subset_of_tables_fr_db('default_layers') +  midvatten_defs.get_subset_of_tables_fr_db('default_nonspatlayers') )#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if err_flag == 0:     
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))#show the user this may take a long time...
            
            #Get two lists (OBSID_P and OBSID_L) with selected obs_points and obs_lines           
            OBSID_P = utils.get_selected_features_as_tuple('obs_points')
            OBSID_L = utils.get_selected_features_as_tuple('obs_lines')

            #sanity = utils.askuser("YesNo","""You are about to export data for the selected obs_points and obs_lines into a set of csv files. \n\nContinue?""",'Are you sure?')
            #exportfolder =    QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QtGui.QFileDialog.ShowDirsOnly)
            exportfolder = QFileDialog.getExistingDirectory(None, 'Select a folder where the csv files will be created:', '.',QFileDialog.ShowDirsOnly)
            if len(exportfolder) > 0:
                exportinstance = ExportData(OBSID_P, OBSID_L)
                exportinstance.export_2_csv(exportfolder)
                
            QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def export_spatialite(self):
        allcritical_layers = tuple(midvatten_defs.get_subset_of_tables_fr_db('obs_points') + midvatten_defs.get_subset_of_tables_fr_db('obs_lines') + midvatten_defs.get_subset_of_tables_fr_db('data_domains') + midvatten_defs.get_subset_of_tables_fr_db('default_layers') +  midvatten_defs.get_subset_of_tables_fr_db('default_nonspatlayers') )#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if err_flag == 0:
            #Get two lists (OBSID_P and OBSID_L) with selected obs_points and obs_lines
            OBSID_P = utils.get_selected_features_as_tuple('obs_points')
            OBSID_L = utils.get_selected_features_as_tuple('obs_lines')

            sanity = utils.askuser("YesNo","""This will create a new empty Midvatten DB with predefined design\nand fill the database with data from selected obs_points and obs_lines.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))#show the user this may take a long time...
                obsp_layer = utils.find_layer('obs_points')
                try:
                    CRS = obsp_layer.crs()
                except AttributeError:
                    utils.pop_up_info("Export error!\n\nMust use \"load default db-layers to qgis\" from Midvatten menu (or key F7) first!")
                    QApplication.restoreOverrideCursor()  # now this long process is done and the cursor is back as normal
                    return None
                EPSG_code = str(CRS.authid()[5:])

                #Let the user chose an EPSG-code for the exported database
                user_chosen_EPSG_code = utils.ask_for_export_crs(EPSG_code) #Transformation to new epsg doesn't work yet.
                if not user_chosen_EPSG_code:
                    QApplication.restoreOverrideCursor()
                    return None
                #user_chosen_EPSG_code = EPSG_code

                filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
                iniText = QSettings(filenamepath , QSettings.IniFormat)
                verno = str(iniText.value('version'))
                from create_db import newdb
                newdbinstance = newdb(verno, user_select_CRS='n', EPSG_code=user_chosen_EPSG_code, delete_srids=False)
                if not newdbinstance.dbpath=='':
                    newdb = newdbinstance.dbpath
                    exportinstance = ExportData(OBSID_P, OBSID_L)
                    exportinstance.export_2_splite(newdb,self.ms.settingsdict['database'],user_chosen_EPSG_code)
            
                QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def export_fieldlogger(self):
        """
        Exports data to FieldLogger android app format
        :return: None 
        """
        allcritical_layers = ('obs_points') #none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if err_flag == 0:
            from export_fieldlogger2 import ExportToFieldLogger
            try:
                self.export_to_field_logger.activateWindow()
            except:
                self.export_to_field_logger = ExportToFieldLogger(self.iface.mainWindow(), self.ms)
        else:
            utils.MessagebarAndLog.warning(
                bar_msg='Error! Verify Midvatten settings. Verify that no layer is in edit mode.',
                duration=15, button=False)

    def import_obs_lines(self):
        allcritical_layers = ('obs_lines')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import observation lines data, from a text file which must have one header row and 6 columns (see plugin web page for further explanation):\nWKT;obsid;name;place;type;source\n\nPlease note that:\nThere must be WKT geometries of type LINESTRING in the first column.\nThe LINESTRING geometries must correspond to SRID in the dataabse.\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in string fields.\nEmpty or null values are not allowed for obsid and there must not be any duplicates of obsid\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.obslines_import()
                if importinstance.status=='True': 
                    self.iface.messageBar().pushMessage("Info","%s observation lines were imported to the database."%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_obs_points(self):
        allcritical_layers = ('obs_points')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import observation points data, from a text file which must have one header row and 26 columns (see plugin web page for further explanation):\n\n1. obsid, 2. name, 3. place, 4. type, 5. length, 6. drillstop, 7. diam, 8. material, 9. screen, 10. capacity, 11. drilldate, 12. wmeas_yn, 13. wlogg_yn, 14. east, 15. north, 16. ne_accur, 17. ne_source, 18. h_toc, 19. h_tocags, 20. h_gs, 21. h_accur, 22. h_syst, 23. h_source, 24. source, 25. com_onerow, 26. com_html\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in string fields.\nEmpty or null values are not allowed for obsid and there must not be any duplicates of obsid.\nEast and north values must correspond to the database SRID.\nIf the East and north values are missing, the corresponding point will assigned a position at coordinate 0,0.  \n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.obsp_import()
                #utils.pop_up_info(returnvalue) #debugging
                #utils.pop_up_info(importinstance.status) #debugging
                if importinstance.status=='True':
                    utils.pop_up_info("%s observation points were imported to the database.\nGeometries (map position) were automatically created based on east and north coordinates."%str(importinstance.recsafter - importinstance.recsbefore))
                    #self.iface.messageBar().pushMessage("Info","%s observation points were imported to the database.\nTo display the imported points on map, select them in\nthe obs_points attribute table then update map position:\nMidvatten - Edit data in database - Update map position from coordinates"%str(importinstance.recsafter - importinstance.recsbefore), 0)                    
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_seismics(self):
        allcritical_layers = ('obs_lines', 'seismic_data')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0: 
            sanity = utils.askuser("YesNo","""You are about to import interpreted seismic data, from a text file which must have one header row and 6 columns:\n\nobsid, length, ground, bedrock, gw_table, comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nEmpty or null values are not allowed for obsid or length.\nEach combination of obsid and length must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.seismics_import()
                if importinstance.status=='True':  
                    self.iface.messageBar().pushMessage("Info","%s interpreted seismic data values were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_stratigraphy(self):
        allcritical_layers = ('obs_points', 'stratigraphy')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import stratigraphy data, from a text file which must have one header row and 9 columns:\n1. obsid\n2. stratid - integer starting from ground surface and increasing downwards\n3. depth_top - depth to top of stratigraphy layer\n4. depth_bot - depth to bottom of stratigraphy layer\n5. geology - full description of layer geology\n6. geoshort - shortname for layer geology (see dicionary)\n7. capacity\n8. development - well development\n9. comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid or stratid, such rows will be excluded from the import.\nEach combination of obsid and stratid must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.strat_import()
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s stratigraphy layers were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_vlf(self):
        allcritical_layers = ('obs_lines', 'vlf_data')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # om ingen av de kritiska lagren är i editeringsmode
            sanity = utils.askuser("YesNo","""You are about to import raw data from vlf measurements, from a text file which must have one header row and 5 columns:\n\nobsid; length; real_comp; imag_comp, comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nEmpty or null values are not allowed for obsid or length.\nEach combination of obsid and length must be unique.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.vlf_import()
                if importinstance.status=='True': 
                    self.iface.messageBar().pushMessage("Info","%s raw values of vlf measurements were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_wflow(self):
        allcritical_layers = ('obs_points', 'w_flow')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # om ingen av de kritiska lagren är i editeringsmode
            sanity = utils.askuser("YesNo","""You are about to import water flow reading, from a text file which must have one header row with \nmandatory columns: obsid, instrumentid, flowtype, date_time\n and at least one optional column: reading, unit, comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nBe sure to use a limited number of flowtypes since all new flowtypes will silently be added to the database table zz_flowtype during import.\nEmpty or null values are not allowed for obsid, instrumentid, flowtype or date_time.\nEach combination of obsid, instrumentid, flowtype and date_time must be unique.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.default_import(importinstance.wflow_import_from_csvlayer)
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s water flow readings were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        importinstance.SanityCheckVacuumDB()
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_wlvl(self):    
        allcritical_layers = ('obs_points', 'w_levels')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            sanity = utils.askuser("YesNo","""You are about to import water level measurements, from a text file which must have one header row with \nmandatory columns: obsid, datetime\n and at least one optional column: head_cm, level_masl, comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid or date_time, such rows will be excluded from the import.\nEmpty or null values are not accepted at the same time in both the columns meas and comment.\nEach combination of obsid and date_time must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.default_import(importinstance.wlvl_import_from_csvlayer)
                if importinstance.status=='True': 
                    self.iface.messageBar().pushMessage("Info","%s water level measurements were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        importinstance.SanityCheckVacuumDB()
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_wlvllogg(self):#  - should be rewritten 
        allcritical_layers = ('obs_points', 'w_levels_logger')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:   
            if not (self.ms.settingsdict['database'] == ''):
                if qgis.utils.iface.activeLayer():
                    if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok':                
                        obsid = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())                    
                        longmessage = """You are about to import water head data, recorded with a\nLevel Logger (e.g. Diver), for """
                        longmessage += obsid[0]
                        longmessage +=u""".\nData is supposed to be imported from a semicolon or comma\nseparated text file. The text file must have one header row and columns:\n\nDate/time,Water head[cm],Temperature[°C]\nor\nDate/time,Water head[cm],Temperature[°C],1:Conductivity[mS/cm]\n\nColumn names are unimportant although column order is.\nAlso, date-time must have format yyyy-mm-dd hh:mm(:ss) and\nthe other columns must be real numbers with point(.) as decimal separator and no separator for thousands.\nRemember to not use comma in the comment field!\n\nAlso, records where any fields are empty will be excluded from the report!\n\nContinue?"""
                        sanity = utils.askuser("YesNo",utils.returnunicode(longmessage),'Are you sure?')
                        if sanity.result == 1:
                            from import_data_to_db_old import wlvlloggimportclass
                            importinstance = wlvlloggimportclass()
                            if not importinstance.status=='True':      
                                self.iface.messageBar().pushMessage("Warning","Something failed during import", 1)
                            else:
                                try:
                                    self.midvsettingsdialog.ClearEverything()
                                    self.midvsettingsdialog.LoadAndSelectLastSettings()
                                except:
                                    pass                            
                else:
                    self.iface.messageBar().pushMessage("Critical","You have to select the obs_points layer and the object (just one!) for which logger data is to be imported!", 2)
            else: 
                self.iface.messageBar().pushMessage("Check settings","You have to select database first!",2)

    def import_wqual_field(self):
        allcritical_layers = ('obs_points', 'w_qual_field')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import water quality data from field measurements, from a text file which must have one header must have one header with\nmandatory columns: obsid, date_time, parameter, unit"                    \n\n1. obsid\n2. staff\n3. date_time - on format yyyy-mm-dd hh:mm(:ss)\n4. instrument\n5. parameter - water quality parameter name\n6. reading_num - param. value (real number, decimal separator=point(.))\n7. reading_txt - parameter value as text, including <, > etc\n8. unit\n9. depth\n10. comment - text string\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid, date_time or parameter, such rows will be excluded from the import.\nEach combination of obsid, date_time and parameter must be unique.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.default_import(importinstance.wqualfield_import_from_csvlayer)
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s water quality parameters were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_wqual_lab(self):
        allcritical_layers = ('obs_points', 'w_qual_lab')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import water quality data from laboratory analysis, from a text file which must have one header row and the following 12 columns:\n\n1. obsid - must exist in obs_points table\n2. depth - sample depth (real number)\n3. report - each pair of 'report' & 'parameter' must be unique!\n4. project\n5. staff\n6. date_time - on format yyyy-mm-dd hh:mm(:ss)\n7. analysis_method\n8. parameter - water quality parameter name\n9. reading_num - param. value (real number, decimal separator=point(.))\n10. reading_txt - parameter value as text, including <, > etc\n11. unit\n12. comment - text string, avoid semicolon and commas\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid, report or parameter, such rows will be excluded from the import.\nEach combination of report and parameter must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.default_import(importinstance.wquallab_import_from_csvlayer)
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s water quality parameters were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_meteo(self):
        allcritical_layers = ('obs_points')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if (utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master where tbl_name = 'meteo'""")[0]==True and len(utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master where tbl_name = 'meteo'""")[1])==0) or (utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master where tbl_name = 'meteo'""")[0]==False): #verify there actually is a meteo table (introduced in midv plugin version 1.1)
            err_flag += 1
            self.iface.messageBar().pushMessage("Error","There is no table for meteorological data in your database! Perhaps your database was created with an earlier version of Midvatten plugin?",2,duration=15)
        
        if err_flag == 0:        # unless none of the critical layers are in editing mode or the database is so old no meteo table exist
            sanity = utils.askuser("YesNo","""You are about to import meteorological data from, from a text file which must have one header row and 8 columns:\n\n"obsid", "instrumentid", "parameter", "date_time", "reading_num", "reading_txt", "unit", "comment"\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nBe sure to use a limited number of parameters since all new parameters will silently be added to the database table zz_meteoparam during import.\nEmpty or null values are not allowed for obsid, instrumentid, parameter or date_time.\nEach combination of obsid, instrumentid, parameter and date_time must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db_old import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.meteo_import()
                if importinstance.status=='True': 
                    self.iface.messageBar().pushMessage("Info","%s meteorological readings were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_fieldlogger(self):
        """
        Imports data from FieldLogger android app format.
        :return: Writes to db.
        """
        allcritical_layers = ('obs_points', 'w_qual_field', 'w_levels', 'w_flow', 'comments')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            if not (self.ms.settingsdict['database'] == ''):
                longmessage = "You are about to import water head data, water flow or water quality from FieldLogger format."
                sanity = utils.askuser("YesNo",utils.returnunicode(longmessage),'Are you sure?')
                if sanity.result == 1:
                    from import_fieldlogger import FieldloggerImport
                    importinstance = FieldloggerImport(self.iface.mainWindow(), self.ms)
                    importinstance.parse_observations_and_populate_gui()
                    if not importinstance.status == 'True' and not importinstance.status:
                        self.iface.messageBar().pushMessage("Warning","Something failed during import", 1)
                    else:
                        try:
                            self.midvsettingsdialog.ClearEverything()
                            self.midvsettingsdialog.LoadAndSelectLastSettings()
                        except:
                            pass
            else:
                self.iface.messageBar().pushMessage("Check settings","You have to select database first!",2)
        QApplication.restoreOverrideCursor()

    def import_csv(self):
        """
        Imports data from a csv file
        :return: Writes to db.
        """
        #TODO: Add all layers here
        allcritical_layers = ('obs_points', 'obs_lines', 'zz_flowtype', 'staff') #Editing mode is checked when selecting table
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            if not (self.ms.settingsdict['database'] == ''):
                from import_general_csv_gui import GeneralCsvImportGui
                importinstance = GeneralCsvImportGui(self.iface.mainWindow(), self.ms)
                importinstance.load_gui()
                if not importinstance.status == 'True' and not importinstance.status:
                    self.iface.messageBar().pushMessage("Warning","Something failed during import", 1)
                else:
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass
            else:
                self.iface.messageBar().pushMessage("Check settings","You have to select database first!",2)
        QApplication.restoreOverrideCursor()

    def import_wqual_lab_from_interlab4(self):
        allcritical_layers = ('obs_points', 'w_qual_lab')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import water quality data from laboratory analysis, from a textfile using interlab4 format.\nSpecifications http://www.svensktvatten.se/globalassets/dricksvatten/riskanalys-och-provtagning/interlab-4-0.pdf\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_interlab4 import Interlab4Import
                importinstance = Interlab4Import(self.iface.mainWindow(), self.ms)
                importinstance.parse_observations_and_populate_gui()
                if importinstance.status=='True':      #
                    self.iface.messageBar().pushMessage("Info","%s water quality parameters were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass
                    
    def import_diverofficedata(self): 
        allcritical_layers = ('obs_points', 'w_levels_logger')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:   
            if not (self.ms.settingsdict['database'] == ''):
                longmessage = (u"""You are about to import water head data, recorded with a Level Logger (e.g. Diver).\n""" +
                               u"""Data is supposed to be imported from a diveroffice file and obsid will be read from the attribute 'Location'.\n""" +
                               u"""The data is supposed to be semicolon or comma separated.\n""" +
                               u"""The header for the data should have column Date/time and at least one of the columns:\n""" +
                               u"""Water head[cm], Temperature[°C], Level[cm], Conductivity[mS/cm], 1:Conductivity[mS/cm], 2:Spec.cond.[mS/cm].\n\n""" +
                               u"""The column order is unimportant but the column names are.\n""" +
                               u"""The data columns must be real numbers with point (.) or comma (,) as decimal separator and no separator for thousands.\n""" +
                               u"""The charset is usually cp1252!\n\n""" +
                               u"""Continue?""")
                sanity = utils.askuser("YesNo",utils.returnunicode(longmessage),'Are you sure?')
                if sanity.result == 1:
                    from import_diveroffice import DiverofficeImport
                    importinstance = DiverofficeImport(self.iface.mainWindow(), self.ms)
                    importinstance.select_files_and_load_gui()

                    if not importinstance.status:
                        self.iface.messageBar().pushMessage("Warning","Something failed during import", 1)
                    else:
                        try:
                            self.midvsettingsdialog.ClearEverything()
                            self.midvsettingsdialog.LoadAndSelectLastSettings()
                        except:
                            pass
            else: 
                self.iface.messageBar().pushMessage("Check settings","You have to select database first!",2)
        QApplication.restoreOverrideCursor()         

    def load_data_domains(self):
        #utils.pop_up_info(msg='This feature is not yet implemented',title='Hold on...')
        #return
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(qgis.utils.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            conn_ok, dd_tables = utils.sql_load_fr_db("select name from sqlite_master where name like 'zz_%'")
            if not conn_ok:
                return
            d_domain_tables = [str(dd_table[0]) for dd_table in dd_tables]
            print d_domain_tables#debug
            err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(qgis.utils.iface, self.ms, d_domain_tables)#verify none of the tables are already loaded and in edit mode
            if err_flag == 0:
                LoadLayers(qgis.utils.iface, self.ms.settingsdict,'Midvatten_data_domains')
        QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def loadthelayers(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            sanity = utils.askuser("YesNo","""This operation will load default layers ( with predefined layout, edit forms etc.) from your selected database to your qgis project.\n\nIf any default Midvatten DB layers already are loaded into your qgis project, then those layers first will be removed from your qgis project.\n\nProceed?""",'Warning!')
            if sanity.result == 1:
                #show the user this may take a long time...
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                LoadLayers(qgis.utils.iface, self.ms.settingsdict)
                QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def new_db(self):
        sanity = utils.askuser("YesNo","""This will create a new empty\nMidvatten DB with predefined design.\n\nContinue?""",'Are you sure?')
        if sanity.result == 1:
            filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
            iniText = QSettings(filenamepath , QSettings.IniFormat)
            _verno = iniText.value('version')
            if isinstance(_verno, PyQt4.QtCore.QVariant):
                verno = _verno.toString()
            else:
                verno = str(_verno)
            from create_db import newdb
            newdbinstance = newdb(verno)
            if not newdbinstance.dbpath=='':
                db = newdbinstance.dbpath
                self.ms.settingsdict['database'] = db
                self.ms.save_settings()

            #The markdown table is for gitlab. Run the rows below when there is a change in create_db
            #markdowntable = utils.create_markdown_table_from_table(u'about_db', transposed=False, only_description=True)
            #print(markdowntable)

    def plot_piper(self):
        allcritical_layers = ('w_qual_lab', 'w_qual_field')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        if err_flag == 0:
            dlg = PiperPlot(self.ms,qgis.utils.iface.activeLayer())

    def plot_timeseries(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        if (self.ms.settingsdict['tstable'] =='' or self.ms.settingsdict['tscolumn'] == ''):
            err_flag += 1
            self.iface.messageBar().pushMessage("Error","Please set time series table and column in Midvatten settings.", 2,duration =15)
        if err_flag == 0:
            dlg = TimeSeriesPlot(qgis.utils.iface.activeLayer(), self.ms.settingsdict)

    def plot_stratigraphy(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        #TODO: remove all "settingsdict['stratigraphytable']" in version 1.4
        """
        if self.ms.settingsdict['stratigraphytable']=='':
            err_flag += 1
            self.iface.messageBar().pushMessage("Error","Please set stratigraphy table in Midvatten settings.", 2,duration =15)
        """
        if err_flag == 0 and utils.strat_selection_check(qgis.utils.iface.activeLayer()) == 'ok':
            dlg = Stratigraphy(self.iface, qgis.utils.iface.activeLayer(), self.ms.settingsdict)
            dlg.showSurvey()
            self.dlg = dlg# only to prevent the Qdialog from closing.

    def plot_section(self):
        all_critical_layers=('obs_points')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, all_critical_layers)#verify midv settings are loaded
        if not(err_flag == 0):
            self.iface.messageBar().pushMessage("Error","Verify Midvatten settings and make sure 'obs_points' layer is not in editing mode.", 2, duration=10)
            return

        SectionLineLayer = qgis.utils.iface.mapCanvas().currentLayer()#MUST BE LINE VECTOR LAYER WITH SAME EPSG as MIDV_OBSDB AND THERE MUST BE ONLY ONE SELECTED FEATURE
        msg = None
        nrofselected = SectionLineLayer.selectedFeatureCount()
        if nrofselected == 1:#First verify only one feature is selected in the active layer...
            for feat in SectionLineLayer.getFeatures():
                geom = feat.geometry()
                if geom.wkbType() == QGis.WKBLineString:#...and that the active layer is a line vector layer
                    pass
                else:
                    msg = 'You must activate the vector line layer that defines the section.'
        else:
            msg = 'You must activate the vector line layer and select exactly one feature that defines the section'
        
        #Then verify that at least two feature is selected in obs_points layer, and get a list (OBSID) of selected obs_points
        obs_points_layer = utils.find_layer('obs_points')
        selectedobspoints = utils.getselectedobjectnames(obs_points_layer)
        obsidlist = []
        if len(selectedobspoints)>1:
            # We cannot send unicode as string to sql because it would include the u'
            # Made into tuple because module sectionplot depends on obsid being a tuple
            OBSID = utils.returnunicode(selectedobspoints, keep_containers=True)
        else:
            msg = 'You must select at least two objects in the obs_points layer'
        
        if msg:#if something went wrong
            utils.MessagebarAndLog.critical(bar_msg=u'Error, %s'%msg)
        else:#otherwise go
            try:
                self.myplot.do_it(self.ms,OBSID,SectionLineLayer)
            except:
                self.myplot = SectionPlot(self.iface.mainWindow(), self.iface)
                self.myplot.do_it(self.ms,OBSID,SectionLineLayer)

    def plot_xy(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        if (self.ms.settingsdict['xytable'] =='' or self.ms.settingsdict['xy_xcolumn'] == '' or (self.ms.settingsdict['xy_y1column'] == '' and self.ms.settingsdict['xy_y2column'] == '' and self.ms.settingsdict['xy_y3column'] == '')):
            err_flag += 1
            self.iface.messageBar().pushMessage("Error","Please set xy series table and columns in Midvatten settings.", 2,duration =15)
        if err_flag == 0:
            dlg = XYPlot(qgis.utils.iface.activeLayer(), self.ms.settingsdict)

    def plot_sqlite(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if not(err_flag == 0):
            return
        try:
            self.customplot.activateWindow()
        except:
            self.customplot = customplot.plotsqlitewindow(self.iface.mainWindow(), self.ms)#self.iface as arg?

    def prepare_layers_for_qgis2threejs(self):
        allcritical_layers = ('obs_points', 'stratigraphy')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms,allcritical_layers)#verify midv settings are loaded
        if err_flag == 0:     
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))#show the user this may take a long time...
            PrepareForQgis2Threejs(qgis.utils.iface, self.ms.settingsdict)
            QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

    def project_created(self):
        self.reset_settings()

    def project_opened(self):
        self.ms.reset_settings()
        self.ms.loadSettings()
        try:#if midvsettingsdock is shown, then it must be reloaded
            self.midvsettingsdialog.activateWindow()
            self.midvsettingsdialog.ClearEverything()
            self.midvsettingsdialog.LoadAndSelectLastSettings()
        except:
            pass

    def reset_settings(self):
        self.ms.reset_settings()
        self.ms.save_settings()
        try:#if midvsettingsdock is shown, then it must be reset
            self.midvsettingsdialog.activateWindow()
            self.midvsettingsdialog.ClearEverything()
        except:
            pass

    def setup(self):
        try:
            self.midvsettingsdialog.activateWindow()
        except:
            self.midvsettingsdialog = midvsettingsdialog.midvsettingsdialogdock(self.iface.mainWindow(),self.iface, self.ms)#self.iface as arg?

    def updatecoord(self):# no longer used, to be removed
        all_critical_layers=('obs_points')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, all_critical_layers)#verify midv settings are loaded
        layername = 'obs_points'
        err_flag = utils.verify_this_layer_selected_and_not_in_edit_mode(err_flag, layername)
        if err_flag == 0:
            sanity = utils.askuser("AllSelected","""Do you want to update coordinates\nfor All or Selected objects?""")
            if sanity.result == 0:  #IF USER WANT ALL OBJECTS TO BE UPDATED
                sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nCoordinates will be written in fields east and north\nfor ALL objects in the obs_points table.\nProceed?""")
                if sanity.result==1:
                    ALL_OBS = utils.sql_load_fr_db("select distinct obsid from obs_points")[1]#a list of unicode strings is returned
                    observations = [None]*len(ALL_OBS)
                    i = 0
                    for obs in ALL_OBS:
                        observations[i] = obs[0]
                        i+=1
                    from coords_and_position import updatecoordinates
                    updatecoordinates(observations)
            elif sanity.result == 1:    #IF USER WANT ONLY SELECTED OBJECTS TO BE UPDATED
                sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nCoordinates will be written in fields east and north\nfor SELECTED objects in the obs_points table.\nProceed?""")
                if sanity.result==1:
                    layer = self.iface.activeLayer()
                    if utils.selection_check(layer) == 'ok':    #Checks that there are some objects selected at all!
                        observations = utils.getselectedobjectnames(layer)#a list of unicode strings is returned
                        from coords_and_position import updatecoordinates
                        updatecoordinates(observations)

    def updateposition(self):# no longer used, to be removed
        all_critical_layers=('obs_points')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, all_critical_layers)#verify midv settings are loaded
        layername = 'obs_points'
        err_flag = utils.verify_this_layer_selected_and_not_in_edit_mode(err_flag, layername)
        if err_flag == 0:
            layer = self.iface.activeLayer()
            sanity = utils.askuser("AllSelected","""Do you want to update position\nfor All or Selected objects?""")
            if sanity.result == 0:      #IF USER WANT ALL OBJECTS TO BE UPDATED
                sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nALL objects in obs_points will be moved to positions\ngiven by their coordinates in fields east and north.\nProceed?""")
                if sanity.result==1:
                    ALL_OBS = utils.sql_load_fr_db("select distinct obsid from obs_points")[1]
                    observations = [None]*len(ALL_OBS)
                    i = 0
                    for obs in ALL_OBS:
                        observations[i] = obs[0]
                        i+=1
                    from coords_and_position import updateposition
                    updateposition(observations)
                    layer.updateExtents()
            elif sanity.result == 1:    #IF USER WANT ONLY SELECTED OBJECTS TO BE UPDATED
                sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nSELECTED objects in obs_points will be moved to positions\ngiven by their coordinates in fields east and north.\nProceed?""")
                if sanity.result==1:
                    if utils.selection_check(layer) == 'ok':    #Checks that there are some objects selected at all!
                        observations = utils.getselectedobjectnames(layer)
                        from coords_and_position import updateposition
                        updateposition(observations)
                        layer.updateExtents()

    def vacuum_db(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            utils.sql_alter_db('vacuum')
            QApplication.restoreOverrideCursor()

    def waterqualityreport(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag)#verify the selected layer has attribute "obsid" and that some feature(s) is selected
        if self.ms.settingsdict['database'] == '' or self.ms.settingsdict['wqualtable']=='' or self.ms.settingsdict['wqual_paramcolumn']=='' or self.ms.settingsdict['wqual_valuecolumn']=='':
            err_flag += 1
            self.iface.messageBar().pushMessage("Error","Check Midvatten settings! \nSomething is probably wrong in the 'W quality report' tab!", 2,duration =15)
        if err_flag == 0:
            fail = 0
            for k in utils.getselectedobjectnames(qgis.utils.iface.activeLayer()):#all selected objects
                if not utils.sql_load_fr_db("select obsid from %s where obsid = '%s'"%(self.ms.settingsdict['wqualtable'],str(k)))[1]:#if there is a selected object without water quality data
                    self.iface.messageBar().pushMessage("Error","No water quality data for %s"%str(k), 2)
                    fail = 1
            if not fail == 1:#only if all objects has data
                wqualreport(qgis.utils.iface.activeLayer(),self.ms.settingsdict)#TEMPORARY FOR GVAB

    def wlvlcalculate(self):
        allcritical_layers = ('obs_points', 'w_levels')     #Check that none of these layers are in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms,allcritical_layers)#verify midv settings are loaded
        layername='obs_points'
        err_flag = utils.verify_this_layer_selected_and_not_in_edit_mode(err_flag,layername)#verify selected layername and not in edit mode
        if err_flag == 0:
            from wlevels_calc_calibr import calclvl
            dlg = calclvl(self.iface.mainWindow(),qgis.utils.iface.activeLayer())  # dock is an instance of calibrlogger
            dlg.exec_()

    def wlvlloggcalibrate(self):
        allcritical_layers = ('w_levels_logger', 'w_levels')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms,allcritical_layers)#verify midv settings are loaded
        if err_flag == 0:
            from wlevels_calc_calibr import calibrlogger
            try:
                self.calibrplot.activateWindow()
            except:
                self.calibrplot = calibrlogger(self.iface.mainWindow(), self.ms.settingsdict)#,obsid)

    def zip_db(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            connection = utils.dbconnection()
            connection.connect2db()
            connection.conn.cursor().execute("begin immediate")
            bkupname = self.ms.settingsdict['database'] + datetime.datetime.now().strftime('%Y%m%dT%H%M') + '.zip'
            zf = zipfile.ZipFile(bkupname, mode='w')
            zf.write(self.ms.settingsdict['database'], compress_type=compression) #compression will depend on if zlib is found or not
            zf.close()
            connection.conn.rollback()
            connection.closedb()
            self.iface.messageBar().pushMessage("Information","Database backup was written to " + bkupname, 1,duration=15)
            QApplication.restoreOverrideCursor()

    def calculate_statistics_for_all_w_logger_data(self):
        """ Calculates min, median, nr of values and max for all obsids and writes to file

            Uses GetStatistics from drillreport for the calculations
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        myconnection = utils.dbconnection()
        if myconnection.connect2db() == True:
            curs = myconnection.conn.cursor()
            rs=curs.execute("""select distinct obsid from w_levels_logger order by obsid""")
            obsids = [row[0] for row in rs]
            rs.close()
            myconnection.closedb()

            from drillreport import GetStatistics
            dbname = unicode(self.ms.settingsdict['database'])
            printlist = [obsid + "\t" + '\t'.join([str(x) for x in GetStatistics(obsid)[1]]) for obsid in sorted(obsids)]
            printlist.reverse()
            printlist.append('Obsid\tMin\tMedian\tNr of values\tMax')
            printlist.reverse()
            utils.MessagebarAndLog.info(
                bar_msg='Statistics done, see log for results.',
                log_msg='\n'.join(printlist), duration=15, button=True)

        QApplication.restoreOverrideCursor()

    def calculate_db_table_rows(self):
        """ Counts the number of rows for all tables in the database """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        utils.calculate_db_table_rows()
        QApplication.restoreOverrideCursor()
