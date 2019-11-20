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
from __future__ import absolute_import
from builtins import str
from builtins import object
# Import some general python modules
import os.path
import qgis.utils
import shutil
import sys
import io
# Import the PyQt and QGIS libraries
from qgis.core import Qgis, QgsApplication
import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication, QDir, QObject, QSettings, QUrl, Qt
from qgis.PyQt.QtWidgets import QAction, QApplication, QFileDialog, QMenu
from qgis.PyQt.QtGui import QCursor, QIcon

#add midvatten plugin directory to pythonpath (needed here to allow importing modules from subfolders)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/tools'))

# Add translate
import util_translate

# Import Midvatten tools and modules
from tsplot import TimeSeriesPlot
from stratigraphy import Stratigraphy
from xyplot import XYPlot
from wqualreport import Wqualreport
from wqualreport_compact import CompactWqualReportUi
from column_values_from_selected_features import ValuesFromSelectedFeaturesGui
from calculate_statistics import CalculateStatisticsGui
from loaddefaultlayers import LoadLayers
from prepareforqgis2threejs import PrepareForQgis2Threejs
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from definitions import midvatten_defs
from sectionplot import SectionPlot
import customplot
from midvsettings import midvsettings
import midvsettingsdialog
from piper import PiperPlot
from export_data import ExportData
import db_utils
from qgis.core import QgsWkbTypes, QgsVectorLayer
import matplotlib_replacements
from strat_symbology import StratSymbology
#import profilefromdem


class Midvatten(object):
    def __init__(self, iface): # Might need revision of variables and method for loading default variables
        matplotlib_replacements.perform_all_replacements()
        #sys.path.append(os.path.dirname(os.path.abspath(__file__))) #add midvatten plugin directory to pythonpath
        self.iface = iface
        self.ms = midvsettings()#self.ms.settingsdict is created when ms is imported
        import util_translate
        self.translator = util_translate.getTranslate( 'midvatten' )

    def initGui(self):
        # Create actions that will start plugin configuration
        self.actionNewDB = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "create_new.xpm")), ru(QCoreApplication.translate("Midvatten","Create a new Midvatten project DB")), self.iface.mainWindow())
        self.actionNewDB.triggered.connect(lambda x: self.new_db())

        self.actionNewPostgisDB = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "create_new.xpm")), ru(QCoreApplication.translate("Midvatten", "Populate a postgis database to a new Midvatten project DB")), self.iface.mainWindow())
        self.actionNewPostgisDB.triggered.connect(lambda x: self.new_postgis_db())

        self.actionloadthelayers = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "loaddefaultlayers.png")), QCoreApplication.translate("Midvatten","Load default db-layers to qgis"), self.iface.mainWindow())
        self.actionloadthelayers.setWhatsThis(QCoreApplication.translate("Midvatten","Load default layers from the selected database"))
        self.iface.registerMainWindowAction(self.actionloadthelayers, "F7")   # The function should also be triggered by the F7 key
        self.actionloadthelayers.triggered.connect(lambda x: self.loadthelayers())

        self.actionsetup = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "MidvSettings.png")), QCoreApplication.translate("Midvatten","Midvatten Settings"), self.iface.mainWindow())
        self.actionsetup.setWhatsThis(QCoreApplication.translate("Midvatten","Configuration for Midvatten toolset"))
        self.iface.registerMainWindowAction(self.actionsetup, "F6")   # The function should also be triggered by the F6 key
        self.actionsetup.triggered.connect(lambda x: self.setup())
        
        self.actionresetSettings = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "ResetSettings.png")), QCoreApplication.translate("Midvatten","Reset Settings"), self.iface.mainWindow())
        self.actionresetSettings.triggered.connect(lambda x: self.reset_settings())

        self.actionabout = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "about.png")), QCoreApplication.translate("Midvatten","About"), self.iface.mainWindow())
        self.actionabout.triggered.connect(lambda x: self.about())

        self.action_wlvlcalculate = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "calc_level_masl.png")), ru(QCoreApplication.translate("Midvatten", "Calculate w level from manual measurements")), self.iface.mainWindow())
        self.action_wlvlcalculate.triggered.connect(lambda x: self.wlvlcalculate())
        
        self.action_aveflowcalculate = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "import_wflow.png")), QCoreApplication.translate("Midvatten","Calculate Aveflow from Accvol"), self.iface.mainWindow())
        self.action_aveflowcalculate.triggered.connect(lambda x: self.aveflowcalculate())

        self.action_import_diverofficedata = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "load_wlevels_logger.png")), QCoreApplication.translate("Midvatten","Import logger data using Diver-Office csv-format"), self.iface.mainWindow())
        self.action_import_diverofficedata.triggered.connect(lambda x: self.import_diverofficedata())
        
        self.action_import_leveloggerdata = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "load_wlevels_logger.png")), QCoreApplication.translate("Midvatten","Import logger data using Levelogger csv-format"), self.iface.mainWindow())
        self.action_import_leveloggerdata.triggered.connect(lambda x: self.import_leveloggerdata())

        self.action_import_hobologgerdata = QAction(QIcon(os.path.join(os.path.dirname(__file__), "icons", "load_wlevels_logger.png")), QCoreApplication.translate("Midvatten", "Import logger data using HOBO logger csv-format"), self.iface.mainWindow())
        self.action_import_hobologgerdata.triggered.connect(lambda x: self.import_hobologgerdata())

        self.action_wlvlloggcalibrate = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "calibr_level_logger_masl.png")), QCoreApplication.translate("Midvatten","Calculate logger w level from logger water head"), self.iface.mainWindow())
        self.action_wlvlloggcalibrate.triggered.connect(lambda x: self.wlvlloggcalibrate())

        self.actionimport_wqual_lab_from_interlab4 = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "import_wqual_lab.png")), QCoreApplication.translate("Midvatten","Import w quality from lab data using interlab4 format"), self.iface.mainWindow())
        self.actionimport_wqual_lab_from_interlab4.triggered.connect(lambda x: self.import_wqual_lab_from_interlab4())

        self.actionimport_fieldlogger = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "import_wqual_field.png")), QCoreApplication.translate("Midvatten","Import data using FieldLogger format"), self.iface.mainWindow())
        self.actionimport_fieldlogger.triggered.connect(lambda x: self.import_fieldlogger())

        self.actiongeneral_import_csv = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "import_wqual_field.png")), QCoreApplication.translate("Midvatten","Import data using general csv format"), self.iface.mainWindow())
        self.actiongeneral_import_csv.triggered.connect(lambda x: self.import_csv())

        self.actionPlotTS = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "PlotTS.png")), QCoreApplication.translate("Midvatten","Time series plot"), self.iface.mainWindow())
        self.actionPlotTS.setWhatsThis(QCoreApplication.translate("Midvatten","Plot time series for selected objects"))
        self.iface.registerMainWindowAction(self.actionPlotTS, "F8")   # The function should also be triggered by the F8 key
        self.actionPlotTS.triggered.connect(lambda x: self.plot_timeseries())
        
        self.actionPlotXY = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "PlotXY.png")), QCoreApplication.translate("Midvatten","Scatter plot"), self.iface.mainWindow())
        self.actionPlotXY.setWhatsThis(QCoreApplication.translate("Midvatten","Plot XY scatter data (e.g. seismic profile) for the selected objects"))
        self.iface.registerMainWindowAction(self.actionPlotXY, "F9")   # The function should also be triggered by the F9 key
        self.actionPlotXY.triggered.connect(lambda x: self.plot_xy())
        
        self.actionPlotPiper = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons","Piper.png")), QCoreApplication.translate("Midvatten","Piper diagram"), self.iface.mainWindow())
        self.actionPlotPiper.setWhatsThis(QCoreApplication.translate("Midvatten","Plot a rectangular Piper diagram for selected objects"))
        self.actionPlotPiper.triggered.connect(lambda x: self.plot_piper())
                
        self.actionPlotSQLite = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons","plotsqliteicon.png")), QCoreApplication.translate("Midvatten","Custom plots"), self.iface.mainWindow())
        self.actionPlotSQLite.setWhatsThis(QCoreApplication.translate("Midvatten","Create custom plots for your reports"))
        self.actionPlotSQLite.triggered.connect(lambda x: self.plot_sqlite())
        
        self.actionPlotStratigraphy = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "PlotStratigraphy.png")), QCoreApplication.translate("Midvatten","Stratigraphy plot"), self.iface.mainWindow())
        self.actionPlotStratigraphy.setWhatsThis(QCoreApplication.translate("Midvatten","Show stratigraphy for selected objects (modified ARPAT)"))
        self.iface.registerMainWindowAction(self.actionPlotStratigraphy, "F10")   # The function should also be triggered by the F10 key
        self.actionPlotStratigraphy.triggered.connect(lambda x: self.plot_stratigraphy())
        
        self.actiondrillreport = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "drill_report.png")), QCoreApplication.translate("Midvatten","General report"), self.iface.mainWindow())
        self.actiondrillreport.setWhatsThis(QCoreApplication.translate("Midvatten","Show a general report for the selected obs point"))
        self.iface.registerMainWindowAction(self.actiondrillreport, "F11")   # The function should also be triggered by the F11 key
        self.actiondrillreport.triggered.connect(lambda x: self.drillreport())

        self.action_custom_drillreport = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "drill_report.png")), QCoreApplication.translate("Midvatten", "Custom general report"), self.iface.mainWindow())
        self.action_custom_drillreport.setWhatsThis(QCoreApplication.translate("Midvatten", "Create a user adjustable general report"))
        self.action_custom_drillreport.triggered.connect(lambda x: self.custom_drillreport())

        self.actionwqualreport = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "wqualreport.png")), QCoreApplication.translate("Midvatten","Water quality report"), self.iface.mainWindow())
        self.actionwqualreport.setWhatsThis(QCoreApplication.translate("Midvatten","Show water quality for the selected obs point"))
        self.iface.registerMainWindowAction(self.actionwqualreport, "F12")   # The function should also be triggered by the F12 key
        self.actionwqualreport.triggered.connect(lambda x: self.waterqualityreport())

        self.actionwqualreportcompact = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "wqualreport.png")), QCoreApplication.translate("Midvatten","Compact water quality report for report attachments"), self.iface.mainWindow())
        self.actionwqualreportcompact.setWhatsThis(QCoreApplication.translate("Midvatten","Show water quality for the selected obs point"))
        self.actionwqualreportcompact.triggered.connect(lambda x: self.waterqualityreportcompact())

        self.actionPlotSection = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "PlotSection.png")), QCoreApplication.translate("Midvatten","Section plot"), self.iface.mainWindow())
        self.actionPlotSection.setWhatsThis(QCoreApplication.translate("Midvatten","Plot a section with stratigraphy and water levels"))
        #self.iface.registerMainWindowAction(self.actionChartMaker, "F12")   # The function should also be triggered by the F12 key
        self.actionPlotSection.triggered.connect(lambda x: self.plot_section())
        
        self.actionPrepareFor2Qgis2ThreeJS = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "qgis2threejs.png")), QCoreApplication.translate("Midvatten","Prepare 3D-data for Qgis2threejs plugin"), self.iface.mainWindow())
        self.actionPrepareFor2Qgis2ThreeJS.setWhatsThis(QCoreApplication.translate("Midvatten","Add spatialite views to be used by Qgis2threejs plugin to create a 3D plot"))
        self.actionPrepareFor2Qgis2ThreeJS.triggered.connect(lambda x: self.prepare_layers_for_qgis2threejs())

        self.actionloaddatadomains = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "loaddatadomains.png")), QCoreApplication.translate("Midvatten","Load data domain tables to qgis"), self.iface.mainWindow())
        self.actionloaddatadomains.setWhatsThis(QCoreApplication.translate("Midvatten","Load the data domain tables from the database"))
        self.actionloaddatadomains.triggered.connect(lambda x: self.load_data_domains())

        self.actionloaddatatables = QAction(QIcon(os.path.join(os.path.dirname(__file__), "icons", "loaddatadomains.png")), QCoreApplication.translate("Midvatten", "Load data tables to qgis"), self.iface.mainWindow())
        self.actionloaddatatables.setWhatsThis(QCoreApplication.translate("Midvatten", "Load the remaining data tables from the database"))
        self.actionloaddatatables.triggered.connect(lambda x: self.load_data_tables())
        
        self.actionloadstratsymbology = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "loaddatadomains.png")), QCoreApplication.translate("Midvatten","Load stratigraphy symbology to qgis"), self.iface.mainWindow())
        self.actionloadstratsymbology.setWhatsThis(QCoreApplication.translate("Midvatten","Load stratiraphy symbology from database"))
        self.actionloadstratsymbology.triggered.connect(lambda x: self.load_strat_symbology())

        self.actionVacuumDB = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "vacuum.png")), QCoreApplication.translate("Midvatten","Vacuum the database"), self.iface.mainWindow())
        self.actionVacuumDB.setWhatsThis(QCoreApplication.translate("Midvatten","Perform database vacuuming"))
        self.actionVacuumDB.triggered.connect(lambda x: self.vacuum_db())

        self.actionZipDB = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "zip.png")), QCoreApplication.translate("Midvatten","Backup the database"), self.iface.mainWindow())
        self.actionZipDB.setWhatsThis(QCoreApplication.translate("Midvatten","A compressed copy of the database will be placed in same directory as the db."))
        self.actionZipDB.triggered.connect(lambda x: self.zip_db())

        self.action_export_csv = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "export_csv.png")), QCoreApplication.translate("Midvatten","Export to a set of csv files"), self.iface.mainWindow())
        self.action_export_csv.setWhatsThis(QCoreApplication.translate("Midvatten","All data for the selected objects (obs_points and obs_lines) will be exported to a set of csv files."))
        self.action_export_csv.triggered.connect(lambda x: self.export_csv())

        self.action_export_spatialite = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "export_spatialite.png")), QCoreApplication.translate("Midvatten","Export to another spatialite db"), self.iface.mainWindow())
        self.action_export_spatialite.setWhatsThis(QCoreApplication.translate("Midvatten","All data for the selected objects (obs_points and obs_lines) will be exported to another spatialite db."))
        self.action_export_spatialite.triggered.connect(lambda x: self.export_spatialite())

        self.action_export_fieldlogger = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "export_csv.png")), QCoreApplication.translate("Midvatten","Export to FieldLogger format"), self.iface.mainWindow())
        self.action_export_fieldlogger.setWhatsThis(self.export_fieldlogger.__doc__)
        self.action_export_fieldlogger.triggered.connect(lambda x: self.export_fieldlogger())

        self.action_calculate_statistics_for_selected_obsids = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "calc_statistics.png")), QCoreApplication.translate("Midvatten", "Calculate statistics for selected obsids"), self.iface.mainWindow())
        self.action_calculate_statistics_for_selected_obsids.setWhatsThis(self.calculate_statistics_for_selected_obsids.__doc__)
        self.action_calculate_statistics_for_selected_obsids.triggered.connect(lambda x: self.calculate_statistics_for_selected_obsids())

        self.action_calculate_db_table_rows = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "calc_statistics.png")), QCoreApplication.translate("Midvatten","Calculate database table rows"), self.iface.mainWindow())
        self.action_calculate_db_table_rows.setWhatsThis(self.calculate_db_table_rows.__doc__)
        self.action_calculate_db_table_rows.triggered.connect(lambda x: self.calculate_db_table_rows())

        self.action_list_of_obsids_from_selected_features = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "calc_statistics.png")), QCoreApplication.translate("Midvatten","List of values from selected features"), self.iface.mainWindow())
        self.action_list_of_obsids_from_selected_features.setWhatsThis(self.list_of_values_from_selected_features.__doc__)
        self.action_list_of_obsids_from_selected_features.triggered.connect(lambda x: self.list_of_values_from_selected_features())

        self.action_add_view_obs_points_lines = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons", "create_new.xpm")), QCoreApplication.translate("Midvatten","Add view_obs_points as workaround for qgis bug #20633"), self.iface.mainWindow())
        self.action_add_view_obs_points_lines.setWhatsThis(QCoreApplication.translate("Midvatten","Add editable views view_obs_points and view_obs_lines to the database. These views replace obs_points and obs_lines in QGIS layer list."))
        self.action_add_view_obs_points_lines.triggered.connect(lambda x: self.add_view_obs_points_lines())


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

        self.menu.import_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Import data to database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.import_data_menu)

        self.menu.import_data_menu.addAction(self.actiongeneral_import_csv)
        self.menu.import_data_menu.addAction(self.action_import_diverofficedata)
        self.menu.import_data_menu.addAction(self.action_import_leveloggerdata)
        self.menu.import_data_menu.addAction(self.action_import_hobologgerdata)
        self.menu.import_data_menu.addAction(self.actionimport_wqual_lab_from_interlab4)
        self.menu.import_data_menu.addAction(self.actionimport_fieldlogger)
        
        self.menu.export_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Export data from database"))
        self.menu.addMenu(self.menu.export_data_menu)
        self.menu.export_data_menu.addAction(self.action_export_csv)   
        self.menu.export_data_menu.addAction(self.action_export_spatialite)
        self.menu.export_data_menu.addAction(self.action_export_fieldlogger)
        
        self.menu.add_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Edit data in database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.add_data_menu)
        self.menu.add_data_menu.addAction(self.action_wlvlcalculate)   
        self.menu.add_data_menu.addAction(self.action_wlvlloggcalibrate)   
        #self.menu.add_data_menu.addAction(self.actionupdatecoord)   
        #self.menu.add_data_menu.addAction(self.actionupdateposition)   
        self.menu.add_data_menu.addAction(self.action_aveflowcalculate)   

        self.menu.plot_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&View plot"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.plot_data_menu.menuAction())
        self.menu.addMenu(self.menu.plot_data_menu)
        self.menu.plot_data_menu.addAction(self.actionPlotTS) 
        self.menu.plot_data_menu.addAction(self.actionPlotXY)
        self.menu.plot_data_menu.addAction(self.actionPlotStratigraphy)
        self.menu.plot_data_menu.addAction(self.actionPlotSection)
        self.menu.plot_data_menu.addAction(self.actionPlotSQLite)
        self.menu.plot_data_menu.addAction(self.actionPlotPiper)

        self.menu.report_menu = QMenu(QCoreApplication.translate("Midvatten", "&View report"))
        self.menu.addMenu(self.menu.report_menu)
        self.menu.report_menu.addAction(self.actiondrillreport)
        self.menu.report_menu.addAction(self.action_custom_drillreport)
        self.menu.report_menu.addAction(self.actionwqualreport)
        self.menu.report_menu.addAction(self.actionwqualreportcompact)
        
        self.menu.db_manage_menu = QMenu(QCoreApplication.translate("Midvatten", "&Database management"))
        self.menu.addMenu(self.menu.db_manage_menu)
        self.menu.db_manage_menu.addAction(self.actionNewDB)
        self.menu.db_manage_menu.addAction(self.actionNewPostgisDB)
        self.menu.db_manage_menu.addAction(self.actionVacuumDB)
        self.menu.db_manage_menu.addAction(self.actionZipDB)
        self.menu.db_manage_menu.addAction(self.action_add_view_obs_points_lines)

        self.menu.utils = QMenu(QCoreApplication.translate("Midvatten", "&Utilities"))
        self.menu.addMenu(self.menu.utils)
        self.menu.utils.addAction(self.actionloaddatadomains)
        self.menu.utils.addAction(self.actionloaddatatables)
        self.menu.utils.addAction(self.actionloadstratsymbology)
        self.menu.utils.addAction(self.actionPrepareFor2Qgis2ThreeJS)
        self.menu.utils.addAction(self.actionresetSettings)
        self.menu.utils.addAction(self.action_calculate_statistics_for_selected_obsids)
        self.menu.utils.addAction(self.action_calculate_db_table_rows)
        self.menu.utils.addAction(self.action_list_of_obsids_from_selected_features)

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
        QgsApplication.messageLog().messageReceived.connect(utils.write_qgs_log_to_file)

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
        util_translate.getTranslate('midvatten')
        filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt")
        iniText = QSettings(filenamepath , QSettings.IniFormat)#This method seems to return a list of unicode strings BUT it seems as if the encoding from the byte strings in the file is not utf-8, hence there is need for special encoding, see below
        verno = iniText.value('version')
        author = ', '.join(iniText.value('author'))
        email = iniText.value('email')
        homepage = iniText.value('homepage')

        ABOUT_templatefile = os.path.join(os.sep,os.path.dirname(__file__),"templates","about_template.htm")
        ABOUT_outpath = os.path.join(QDir.tempPath(), 'midvatten_about')
        if not os.path.exists(ABOUT_outpath):
            os.makedirs(ABOUT_outpath)
        ABOUT_outputfile = os.path.join(ABOUT_outpath, "about.htm")
        shutil.copy2(os.path.join(os.path.dirname(ABOUT_templatefile), 'midvatten_logga.png'), os.path.join(ABOUT_outpath, 'midvatten_logga.png'))

        with io.open(ABOUT_templatefile, 'rt', encoding='cp1252') as infile:
            rows = [row.replace('VERSIONCHANGETHIS',verno).replace('AUTHORCHANGETHIS',author).replace('EMAILCHANGETHIS',email).replace('HOMEPAGECHANGETHIS',homepage)
                    for row in infile]
        with io.open(ABOUT_outputfile, 'w', encoding='cp1252') as outfile:
            outfile.write('\n'.join(rows))
        dlg = utils.HtmlDialog("About Midvatten plugin for QGIS",QUrl.fromLocalFile(ABOUT_outputfile))
        dlg.exec_()

    def aveflowcalculate(self):
        allcritical_layers = ('obs_points', 'w_flow') #none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some feature(s) is selected
        if err_flag == 0:     
            from w_flow_calc_aveflow import Calcave
            dlg = Calcave(self.iface.mainWindow())
            dlg.exec_()

    def drillreport(self):
        allcritical_layers = ('obs_points', 'w_levels', 'w_qual_lab')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that exactly one feature is selected
        if err_flag == 0:
            obsids = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())  # selected obs_point is now found in obsid[0]
            from drillreport import Drillreport
            Drillreport(obsids,self.ms.settingsdict)

    def custom_drillreport(self):
        allcritical_layers = ('obs_points', 'w_levels', 'w_qual_lab')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            from custom_drillreport import DrillreportUi
            DrillreportUi(self.iface.mainWindow(), self.ms)

    def export_csv(self):
        allcritical_layers = tuple(midvatten_defs.get_subset_of_tables_fr_db('obs_points') + midvatten_defs.get_subset_of_tables_fr_db('obs_lines') + midvatten_defs.get_subset_of_tables_fr_db('data_domains') + midvatten_defs.get_subset_of_tables_fr_db('default_layers') +  midvatten_defs.get_subset_of_tables_fr_db('default_nonspatlayers') )#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if err_flag == 0:     
            utils.start_waiting_cursor()#show the user this may take a long time...
            
            #Get two lists (OBSID_P and OBSID_L) with selected obs_points and obs_lines           
            OBSID_P = utils.get_selected_features_as_tuple('obs_points')
            OBSID_L = utils.get_selected_features_as_tuple('obs_lines')

            #sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate("Midvatten", """You are about to export data for the selected obs_points and obs_lines into a set of csv files. \n\nContinue?""")), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
            #exportfolder =    QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)
            utils.stop_waiting_cursor()
            exportfolder = QFileDialog.getExistingDirectory(None, ru(QCoreApplication.translate("Midvatten", 'Select a folder where the csv files will be created:')), '.',QFileDialog.ShowDirsOnly)
            utils.start_waiting_cursor()
            if len(exportfolder) > 0:
                exportinstance = ExportData(OBSID_P, OBSID_L)
                exportinstance.export_2_csv(exportfolder)
                
            utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def export_spatialite(self):
        #, *args, **kwargs
        #print("export args: '{}' kwargs: '{}' ".format(str(args), str(kwargs)))

        allcritical_layers = tuple(midvatten_defs.get_subset_of_tables_fr_db('obs_points') + midvatten_defs.get_subset_of_tables_fr_db('obs_lines') + midvatten_defs.get_subset_of_tables_fr_db('data_domains') + midvatten_defs.get_subset_of_tables_fr_db('default_layers') +  midvatten_defs.get_subset_of_tables_fr_db('default_nonspatlayers') )#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if err_flag == 0:
            utils.start_waiting_cursor()  # show the user this may take a long time..
            dbconnection = db_utils.DbConnectionManager()
            dbtype = dbconnection.dbtype
            dbconnection.closedb()
            if dbtype != 'spatialite':
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('export_spatialite', 'Export to spatialite only works when source db is spatialite.')))
                utils.stop_waiting_cursor()
                return

            #Get two lists (OBSID_P and OBSID_L) with selected obs_points and obs_lines
            OBSID_P = utils.get_selected_features_as_tuple('obs_points')
            OBSID_L = utils.get_selected_features_as_tuple('obs_lines')
            try:
                print(str(OBSID_P))
                print(str(OBSID_L))
            except:
                pass
            utils.stop_waiting_cursor()

            selected_all = ru(QCoreApplication.translate("Midvatten", 'selected')) if any([OBSID_P, OBSID_L]) else ru(QCoreApplication.translate("Midvatten", 'all'))

            sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate("Midvatten", """This will create a new empty Midvatten DB with predefined design\nand fill the database with data from %s obs_points and obs_lines.\n\nContinue?"""))%(selected_all), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
            if sanity.result == 1:
                utils.start_waiting_cursor()#show the user this may take a long time...
                EPSG_code = db_utils.sql_load_fr_db('''SELECT srid FROM geometry_columns WHERE f_table_name = 'obs_points';''')[1][0][0]

                #Let the user chose an EPSG-code for the exported database
                utils.stop_waiting_cursor()
                user_chosen_EPSG_code = utils.ask_for_export_crs(EPSG_code)
                utils.start_waiting_cursor()

                if not user_chosen_EPSG_code:
                    utils.stop_waiting_cursor()
                    return None

                filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
                iniText = QSettings(filenamepath , QSettings.IniFormat)
                verno = str(iniText.value('version'))
                from create_db import NewDb
                newdbinstance = NewDb()
                newdbinstance.create_new_spatialite_db(verno,user_select_CRS='n', EPSG_code=user_chosen_EPSG_code, delete_srids=False)
                utils.start_waiting_cursor()
                if newdbinstance.db_settings:
                    new_dbpath = db_utils.get_spatialite_db_path_from_dbsettings_string(newdbinstance.db_settings)
                    if not new_dbpath:
                        utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('export_spatialite', 'Export to spatialite failed, see log message panel')),
                                                        button=True)
                        utils.stop_waiting_cursor()
                        return
                    exportinstance = ExportData(OBSID_P, OBSID_L)
                    exportinstance.export_2_splite(new_dbpath, user_chosen_EPSG_code)
            
                utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def export_fieldlogger(self):
        """
        Exports data to FieldLogger android app format
        :return: None 
        """
        allcritical_layers = ('obs_points') #none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode

        if err_flag == 0:
            from export_fieldlogger import ExportToFieldLogger
            try:
                self.export_to_field_logger.activateWindow()
            except:
                self.export_to_field_logger = ExportToFieldLogger(self.iface.mainWindow(), self.ms)
        else:
            utils.MessagebarAndLog.warning(
                bar_msg=ru(QCoreApplication.translate("Midvatten", 'Error! Verify Midvatten settings. Verify that no layer is in edit mode.')),
                duration=15, button=False)

    @utils.general_exception_handler
    def import_fieldlogger(self):
        """
        Imports data from FieldLogger android app format.
        :return: Writes to db.
        """
        allcritical_layers = ('obs_points', 'w_qual_field', 'w_levels', 'w_flow', 'comments')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            if not (self.ms.settingsdict['database'] == ''):
                longmessage = ru(QCoreApplication.translate("Midvatten", "You are about to import water head data, water flow or water quality from FieldLogger format."))
                sanity = utils.Askuser("YesNo", ru(longmessage), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
                if sanity.result == 1:
                    from import_fieldlogger import FieldloggerImport
                    importinstance = FieldloggerImport(self.iface.mainWindow(), self.ms)
                    importinstance.parse_observations_and_populate_gui()
                    if not importinstance.status == 'True' and not importinstance.status:
                        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Something failed during import"))
                    else:
                        try:
                            self.midvsettingsdialog.ClearEverything()
                            self.midvsettingsdialog.LoadAndSelectLastSettings()
                        except:
                            pass
            else:
                utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "You have to select database first!"))
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def import_csv(self):
        """
        Imports data from a csv file
        :return: Writes to db.
        """
        #TODO: Add all layers here
        allcritical_layers = ('obs_points', 'obs_lines', 'zz_flowtype', 'zz_staff') #Editing mode is checked when selecting table
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            if not (self.ms.settingsdict['database'] == ''):
                from import_general_csv_gui import GeneralCsvImportGui
                importinstance = GeneralCsvImportGui(self.iface.mainWindow(), self.ms)
                importinstance.load_gui()
                if not importinstance.status == 'True' and not importinstance.status:
                    utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Something failed during import"))
                else:
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass
            else:
                utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "You have to select database first!"))
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def import_wqual_lab_from_interlab4(self):
        allcritical_layers = ('obs_points', 'w_qual_lab')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate("Midvatten", """You are about to import water quality data from laboratory analysis, from a textfile using interlab4 format.\nSpecifications http://www.svensktvatten.se/globalassets/dricksvatten/riskanalys-och-provtagning/interlab-4-0.pdf\n\nContinue?""")), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
            if sanity.result == 1:
                from import_interlab4 import Interlab4Import
                importinstance = Interlab4Import(self.iface.mainWindow(), self.ms)
                importinstance.parse_observations_and_populate_gui()
                if importinstance.status=='True':      #
                    utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate("Midvatten", "%s water quality parameters were imported to the database"))%str(importinstance.recsafter - importinstance.recsbefore))
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    @utils.general_exception_handler
    def import_diverofficedata(self): 
        allcritical_layers = ('obs_points', 'w_levels_logger')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:   
            if not (self.ms.settingsdict['database'] == ''):
                longmessage = ru(QCoreApplication.translate("Midvatten",
                               """You are about to import water head data, recorded with a Level Logger (e.g. Diver).\n"""
                               """Data is supposed to be imported from a diveroffice file and obsid will be read from the attribute 'Location'.\n"""
                               """The data is supposed to be semicolon or comma separated.\n"""
                               """The header for the data should have column Date/time and at least one of the columns:\n"""
                               """Water head[cm], Temperature[°C], Level[cm], Conductivity[mS/cm], 1:Conductivity[mS/cm], 2:Spec.cond.[mS/cm].\n\n"""
                               """The column order is unimportant but the column names are.\n"""
                               """The data columns must be real numbers with point (.) or comma (,) as decimal separator and no separator for thousands.\n"""
                               """The charset is usually cp1252!\n\n"""
                               """Continue?"""))
                sanity = utils.Askuser("YesNo", ru(longmessage), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
                if sanity.result == 1:
                    from import_diveroffice import DiverofficeImport
                    importinstance = DiverofficeImport(self.iface.mainWindow(), self.ms)
                    importinstance.select_files_and_load_gui()

                    if not importinstance.status:
                        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Something failed during import"))
                    else:
                        try:
                            self.midvsettingsdialog.ClearEverything()
                            self.midvsettingsdialog.LoadAndSelectLastSettings()
                        except:
                            pass
            else: 
                utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "You have to select database first!"))
        utils.stop_waiting_cursor()
        
    @utils.general_exception_handler
    def import_leveloggerdata(self): 
        allcritical_layers = ('obs_points', 'w_levels_logger')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:   
            if not (self.ms.settingsdict['database'] == ''):
                longmessage = ru(QCoreApplication.translate("Midvatten",
                               """You are about to import water head data, recorded with a Levelogger.\n"""
                               """Data is supposed to be imported from a csv file exported from the levelogger data wizard and obsid will be read from the attribute 'Location'.\n"""
                               """The data is supposed to be semicolon or comma separated.\n"""
                               """The header for the data should have column Date, Time and at least one of the columns:\n"""
                               """LEVEL, TEMPERATURE, spec. conductivity (uS/cm), spec. conductivity (mS/cm).\n\n"""
                               """The unit for LEVEL must be cm or m and the unit must be given as the "UNIT: " argument one row after "LEVEL" argument.\n"""
                               """The unit for spec. conductivity is read from the spec. conductivity column head and must be mS/cm or uS/cm.\n"""
                               """The column order is unimportant but the column names are.\n"""
                               """The data columns must be real numbers with point (.) or comma (,) as decimal separator and no separator for thousands.\n"""
                               """The charset is usually cp1252!\n\n"""
                               """Continue?"""))
                sanity = utils.Askuser("YesNo", ru(longmessage), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
                if sanity.result == 1:
                    from import_levelogger import LeveloggerImport
                    importinstance = LeveloggerImport(self.iface.mainWindow(), self.ms)
                    importinstance.select_files_and_load_gui()

                    if not importinstance.status:
                        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Something failed during import"))
                    else:
                        try:
                            self.midvsettingsdialog.ClearEverything()
                            self.midvsettingsdialog.LoadAndSelectLastSettings()
                        except:
                            pass
            else: 
                utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "You have to select database first!"))
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def import_hobologgerdata(self):
        allcritical_layers = ('obs_points', 'w_levels_logger')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        if err_flag == 0:
            if not (self.ms.settingsdict['database'] == ''):
                longmessage = ru(QCoreApplication.translate("Midvatten",
                               """You are about to import water head data, recorded with a HOBO temperature logger.\n"""
                               """Data is supposed to be in utf-8 and using this format:\n"""
                               '''"Plot Title: temp_aname"\n'''
                               '''"#","Date Time, GMT+02:00","Temp, °C (LGR S/N: 1234, SEN S/N: 1234, LBL: obsid)",...\n'''
                               '''1,07/19/18 11:00:00 fm,7.654,...\n'''
                               """The data columns must be real numbers with point (.) or comma (,) as decimal separator and no separator for thousands.\n"""
                               """The charset is usually utf8!\n\n"""
                               """Continue?"""))
                sanity = utils.Askuser("YesNo", ru(longmessage), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
                if sanity.result == 1:
                    from import_hobologger import HobologgerImport
                    importinstance = HobologgerImport(self.iface.mainWindow(), self.ms)
                    importinstance.select_files_and_load_gui()

                    if not importinstance.status:
                        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Something failed during import"))
                    else:
                        try:
                            self.midvsettingsdialog.ClearEverything()
                            self.midvsettingsdialog.LoadAndSelectLastSettings()
                        except:
                            pass
            else:
                utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "You have to select database first!"))
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def load_data_domains(self):
        #utils.pop_up_info(msg='This feature is not yet implemented',title='Hold on...')
        #return
        utils.start_waiting_cursor()
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(qgis.utils.iface, self.ms)#verify midv settings are loaded
        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate("Midvatten", 'load_data_domains err_flag: %s'))%str(err_flag))
        if err_flag == 0:
            LoadLayers(qgis.utils.iface, self.ms.settingsdict,'Midvatten_data_domains')
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def load_data_tables(self):
        utils.start_waiting_cursor()
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(qgis.utils.iface, self.ms)#verify midv settings are loaded
        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate("Midvatten", 'load_data_tables err_flag: %s'))%str(err_flag))
        if err_flag == 0:
            LoadLayers(qgis.utils.iface, self.ms.settingsdict, 'Midvatten_data_tables')
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def load_strat_symbology(self):
        utils.start_waiting_cursor()
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(qgis.utils.iface, self.ms)#verify midv settings are loaded
        if err_flag:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate("Midvatten", 'load_strat_symbology err_flag: %s'))%str(err_flag))
        else:
            self.strat_symbology = StratSymbology(qgis.utils.iface, self.iface.mainWindow())
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def loadthelayers(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate("Midvatten", """This operation will load default layers ( with predefined layout, edit forms etc.) from your selected database to your qgis project.\n\nIf any default Midvatten DB layers already are loaded into your qgis project, then those layers first will be removed from your qgis project.\n\nProceed?""")), ru(QCoreApplication.translate("Midvatten", 'Warning!')))
            if sanity.result == 1:
                #show the user this may take a long time...
                utils.start_waiting_cursor()
                LoadLayers(qgis.utils.iface, self.ms.settingsdict)
                utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def new_db(self, *args):
        sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate("Midvatten", """This will create a new empty\nMidvatten DB with predefined design.\n\nContinue?""")), ru(QCoreApplication.translate("Midvatten", 'Are you sure?')))
        if sanity.result == 1:
            filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
            iniText = QSettings(filenamepath , QSettings.IniFormat)
            _verno = iniText.value('version')
            if isinstance(_verno, qgis.PyQt.QtCore.QVariant):
                verno = _verno.toString()
            else:
                verno = str(_verno)
            from create_db import NewDb
            newdbinstance = NewDb()
            newdbinstance.create_new_spatialite_db(verno)

            if newdbinstance.db_settings:
                self.ms.settingsdict['database'] = newdbinstance.db_settings
                self.ms.save_settings('database')
                try:
                    self.midvsettingsdialog.LoadAndSelectLastSettings()
                except AttributeError:
                    pass

            #about_db = db_utils.sql_load_fr_db('select * from about_db')

            #The markdown table is for gitlab. Run the rows below when there is a change in create_db
            #markdowntable = utils.create_markdown_table_from_table('about_db', transposed=False, only_description=True)
            #print(markdowntable)

    @db_utils.if_connection_ok
    @utils.general_exception_handler
    def new_postgis_db(self):
        sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate("Midvatten", """This will update the selected postgis database to a \nMidvatten Postgis DB with predefined design.\n\nContinue?""")), ru(QCoreApplication.translate("Midvatten",  'Are you sure?')))
        if sanity.result == 1:
            filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
            iniText = QSettings(filenamepath , QSettings.IniFormat)
            verno = str(iniText.value('version'))
            from create_db import NewDb
            newdbinstance = NewDb()
            newdbinstance.populate_postgis_db(verno)
            if newdbinstance.db_settings:
                self.ms.settingsdict['database'] = newdbinstance.db_settings
                self.ms.save_settings('database')
                try:
                    self.midvsettingsdialog.LoadAndSelectLastSettings()
                except AttributeError:
                    pass

            #The markdown table is for gitlab. Run the rows below when there is a change in create_db
            #markdowntable = utils.create_markdown_table_from_table('about_db', transposed=False, only_description=True)
            #print(markdowntable)

    @utils.general_exception_handler
    def plot_piper(self):
        allcritical_layers = ('w_qual_lab', 'w_qual_field')#none of these layers must be in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms, allcritical_layers)#verify midv settings are loaded and the critical layers are not in editing mode
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        if err_flag == 0:
            piperplot = PiperPlot(self.ms,qgis.utils.iface.activeLayer())
            dlg = piperplot.get_data_and_make_plot()

    @utils.general_exception_handler
    def plot_timeseries(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        if (self.ms.settingsdict['tstable'] =='' or self.ms.settingsdict['tscolumn'] == ''):
            err_flag += 1
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "Please set time series table and column in Midvatten settings."), duration =15)
        if err_flag == 0:
            dlg = TimeSeriesPlot(qgis.utils.iface.activeLayer(), self.ms.settingsdict)

    @utils.general_exception_handler
    def plot_stratigraphy(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        #TODO: remove all "settingsdict['stratigraphytable']" in version 1.4
        """
        if self.ms.settingsdict['stratigraphytable']=='':
            err_flag += 1
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "Please set stratigraphy table in Midvatten settings."), duration =15)
        """
        if err_flag == 0 and utils.strat_selection_check(qgis.utils.iface.activeLayer()) == 'ok':
            dlg = Stratigraphy(self.iface, qgis.utils.iface.activeLayer(), self.ms.settingsdict)
            dlg.showSurvey()
            self.dlg = dlg# only to prevent the Qdialog from closing.

    @utils.general_exception_handler
    def plot_section(self):
        selected_layer = qgis.utils.iface.mapCanvas().currentLayer() #MUST BE LINE VECTOR LAYER WITH SAME EPSG as MIDV_OBSDB AND THERE MUST BE ONLY ONE SELECTED FEATURE
        if not selected_layer:
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", 'You must select at least one layer and one feature!'), duration=10)
            raise utils.UsageError()

        nrofselected = selected_layer.selectedFeatureCount()
        if not isinstance(selected_layer, QgsVectorLayer):
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", 'You must activate the vector line layer that defines the section.'),
                                            log_msg=ru(QCoreApplication.translate("Midvatten", 'The layer must be of type QgsVectorLayer, but was  "%s".'))%str(type(selected_layer)))
            raise utils.UsageError()
        selected_obspoints = None
        for feat in selected_layer.getFeatures():
            geom = feat.geometry()
            if geom.wkbType() == QgsWkbTypes.LineString or geom.wkbType() == QgsWkbTypes.MultiLineString:
                if nrofselected != 1:
                    utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", 'You must select only one line feature that defines the section'))
                    raise utils.UsageError()
                else:
                    try:
                        obs_points_layer = utils.find_layer('obs_points')
                    except utils.UsageError:
                        utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "Layer obs_points is not found. Plotting without observations!"))
                        break
                    else:
                        if obs_points_layer.isEditable():
                            utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Layer obs_points is in editing mode! Plotting without observations!"))
                            break
                        else:
                            selected_obspoints = utils.getselectedobjectnames(obs_points_layer)
            else:
                selected_layer = None
                #utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", 'Reverting to simple stratigraphy plot. For section plot, you must activate the vector line layer and select exactly one feature that defines the section'))
                # Then verify that at least two feature is selected in obs_points layer,
                # and get a list (selected_obspoints) of selected obs_points
                selected_obspoints = utils.getselectedobjectnames()  # Finding obsid from currently selected layer
                if not selected_obspoints:
                    utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "The current layer had no selected obsids. Trying to plot from layer obs_points!"))
                    try:
                        obs_points_layer = utils.find_layer('obs_points')
                    except utils.UsageError:
                        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Layer obs_points is not found. Plotting without observations!"))
                        break
                    else:
                        if obs_points_layer.isEditable():
                            utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate("Midvatten", "Layer obs_points is in editing mode! Plotting without observations!"))
                            break
                        else:
                            selected_obspoints = utils.getselectedobjectnames(obs_points_layer)

        if not selected_layer and not selected_obspoints:
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", 'You must select at least one feature!'), duration=10)
            raise utils.UsageError()
        elif not selected_layer:
            utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate("Midvatten", 'No line layer was selected. The stratigraphy bars will be lined up from south-north or west-east and no DEMS will be plotted.'), duration=10)

        if selected_obspoints is not None and len(selected_obspoints) > 0:
            selected_obspoints = ru(selected_obspoints, keep_containers=True)
        else:
            selected_obspoints = []
        #Then verify that at least two feature is selected in obs_points layer, and get a list (selected_obspoints) of selected obs_points
        #if len(selected_obspoints)>1:
        #    # We cannot send unicode as string to sql because it would include the '
        #    # Made into tuple because module sectionplot depends on obsid being a tuple
        #    selected_obspoints = ru(selected_obspoints, keep_containers=True)
        #else:
        #    utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate("Midvatten", 'You must select at least two objects in the obs_points layer')))
        #    raise utils.UsageError()

        try:
            self.myplot.do_it(self.ms,selected_obspoints,selected_layer)
        except:
            self.myplot = SectionPlot(self.iface.mainWindow(), self.iface)
            self.myplot.do_it(self.ms,selected_obspoints,selected_layer)

    @utils.general_exception_handler
    def plot_xy(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag,0)#verify the selected layer has attribute "obsid" and that some features are selected
        if (self.ms.settingsdict['xytable'] =='' or self.ms.settingsdict['xy_xcolumn'] == '' or (self.ms.settingsdict['xy_y1column'] == '' and self.ms.settingsdict['xy_y2column'] == '' and self.ms.settingsdict['xy_y3column'] == '')):
            err_flag += 1
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "Please set xy series table and columns in Midvatten settings."), duration =15)
        if err_flag == 0:
            dlg = XYPlot(qgis.utils.iface.activeLayer(), self.ms.settingsdict)

    @utils.general_exception_handler
    def plot_sqlite(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if not(err_flag == 0):
            return
        try:
            self.customplot.activateWindow()
        except:
            self.customplot = customplot.plotsqlitewindow(self.iface.mainWindow(), self.ms)#self.iface as arg?

    @utils.general_exception_handler
    def prepare_layers_for_qgis2threejs(self):
        allcritical_layers = ('obs_points', 'stratigraphy')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms,allcritical_layers)#verify midv settings are loaded
        if err_flag == 0:
            dbconnection = db_utils.DbConnectionManager()
            dbtype = dbconnection.dbtype
            dbconnection.closedb()
            if dbtype != 'spatialite':
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('prepare_layers_for_qgis2threejs', 'Only supported for spatialite.')))
                return

            utils.start_waiting_cursor()#show the user this may take a long time...
            PrepareForQgis2Threejs(qgis.utils.iface, self.ms.settingsdict)
            utils.stop_waiting_cursor()

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
        utils.warn_about_old_database()

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

    def vacuum_db(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            db_utils.sql_alter_db('vacuum')
            utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def waterqualityreport(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        err_flag = utils.verify_layer_selection(err_flag)#verify the selected layer has attribute "obsid" and that some feature(s) is selected
        if self.ms.settingsdict['database'] == '' or self.ms.settingsdict['wqualtable']=='' or self.ms.settingsdict['wqual_paramcolumn']=='' or self.ms.settingsdict['wqual_valuecolumn']=='':
            err_flag += 1
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate("Midvatten", "Check Midvatten settings! \nSomething is probably wrong in the 'W quality report' tab!"), duration =15)
        if err_flag == 0:
            fail = 0
            for k in utils.getselectedobjectnames(qgis.utils.iface.activeLayer()):#all selected objects
                if not db_utils.sql_load_fr_db("select obsid from %s where obsid = '%s'"%(self.ms.settingsdict['wqualtable'], str(k)))[1]:#if there is a selected object without water quality data
                    utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate("Midvatten", "No water quality data for %s")) % str(k))
                    fail = 1
            if not fail == 1:#only if all objects has data
                Wqualreport(qgis.utils.iface.activeLayer(),self.ms.settingsdict)#TEMPORARY FOR GVAB

    @utils.general_exception_handler
    def waterqualityreportcompact(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            CompactWqualReportUi(self.iface.mainWindow(), self.ms)

    @utils.general_exception_handler
    def wlvlcalculate(self):
        allcritical_layers = ('obs_points', 'w_levels')     #Check that none of these layers are in editing mode
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms,allcritical_layers)#verify midv settings are loaded
        layername='obs_points'
        err_flag = utils.verify_this_layer_selected_and_not_in_edit_mode(err_flag,layername)#verify selected layername and not in edit mode
        if err_flag == 0:
            from wlevels_calc_calibr import Calclvl
            dlg = Calclvl(self.iface.mainWindow(),qgis.utils.iface.activeLayer())  # dock is an instance of calibrlogger
            dlg.exec_()

    @utils.general_exception_handler
    def wlvlloggcalibrate(self):
        allcritical_layers = ('w_levels_logger', 'w_levels')
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms,allcritical_layers)#verify midv settings are loaded
        if err_flag == 0:
            from wlevels_calc_calibr import Calibrlogger
            try:
                self.calibrplot.activateWindow()
            except:
                self.calibrplot = Calibrlogger(self.iface.mainWindow(), self.ms.settingsdict)#,obsid)

    @utils.waiting_cursor
    def zip_db(self):
        err_flag = utils.verify_msettings_loaded_and_layer_edit_mode(self.iface, self.ms)#verify midv settings are loaded
        if err_flag == 0:
            dbconnection = db_utils.DbConnectionManager()
            connection_ok = dbconnection.connect2db()
            if connection_ok:
                db_utils.backup_db(dbconnection)

    @utils.general_exception_handler
    def calculate_statistics_for_selected_obsids(self):
        """ Calculates min, median, nr of values and max for all obsids and writes to file

            Uses GetStatistics from drillreport for the calculations
        """
        stats_gui = CalculateStatisticsGui(self.iface.mainWindow(), self.ms)

    @utils.general_exception_handler
    def calculate_db_table_rows(self):
        """ Counts the number of rows for all tables in the database """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        utils.calculate_db_table_rows()
        utils.stop_waiting_cursor()

    @utils.general_exception_handler
    def list_of_values_from_selected_features(self):
        """ Writes a concatted list of values from selected column from selected features
            The list could be used in other layer filters or selections.
        """

        ValuesFromSelectedFeaturesGui(self.iface.mainWindow())

    @utils.general_exception_handler
    def add_view_obs_points_lines(self):
        utils.add_view_obs_points_obs_lines()
