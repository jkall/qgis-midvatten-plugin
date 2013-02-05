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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
import resources  # Initialize Qt resources from file resources.py
import os.path # Just to be able to read from metadata.txt in the same directory
from midvsettings import midvsettings  # Import the code for the settings dialog
from tsplot import TimeSeriesPlot
from stratigraphy import Stratigraphy
from xyplot import XYPlot
from wqualreport import wqualreport
from loaddefaultlayers import loadlayers
import midvatten_utils as utils         # Whenever some global midvatten_utilities are needed
from definitions import midvatten_defs as defs
#from about.AboutDialog import AboutDialog
from HtmlDialog import HtmlDialog
import sys
#sys.path.append(os.path.dirname(os.path.abspath(__file__))) # To enable loading of modules from inside the plugin directory

class midvatten:
    def __init__(self, iface):    # Might need revision of variables and method for loading default variables
        sys.path.append(os.path.dirname(os.path.abspath(__file__))) #add midvatten plugin directory to pythonpath
        self.iface = iface
        # settings...
        self.readingSettings = False # To enable resetsettings
        self.settingsdict = self.createsettingsdict()# calling for thee method that defines an empty dictionary of settings
        #self.loadSettings()    # stored settings are loaded  NOTE: From ver 0.3.2 it is no longer possible to load settings here
        #The settings are stored in the qgis project file and thus cannot be loaded when qgis is starting (and plugni initialized) 
        #The settings must be loaded after the qgis project is loaded - thus settings is loaded when needed (and this is checked in several methods below)
        self.settingsareloaded = False # To make sure settings are loaded once and only once
        
    def initGui(self):   # Creates actions that will start plugin configuration
        self.actionNewDB = QAction(QIcon(":/plugins/midvatten/icons/create_new.xpm"), "Create a new Midvatten project DB", self.iface.mainWindow())
        QObject.connect(self.actionNewDB, SIGNAL("triggered()"), self.NewDB)
        
        self.actionloadthelayers = QAction(QIcon(":/plugins/midvatten/icons/loaddefaultlayers.png"), "Load default db-layers to qgis", self.iface.mainWindow())
        self.actionloadthelayers.setWhatsThis("Load default layers from the selected database")
        QObject.connect(self.actionloadthelayers, SIGNAL("activated()"), self.loadthelayers)

        self.actionsetup = QAction(QIcon(":/plugins/midvatten/icons/MidvSettings.png"), "Midvatten Settings", self.iface.mainWindow())
        self.actionsetup.setWhatsThis("Configuration for Midvatten toolset")
        self.iface.registerMainWindowAction(self.actionsetup, "F6")   # The function should also be triggered by the F6 key
        QObject.connect(self.actionsetup, SIGNAL("activated()"), self.setup)
        
        self.actionresetSettings = QAction(QIcon(":/plugins/midvatten/icons/ResetSettings.png"), "Reset Settings", self.iface.mainWindow())
        QObject.connect(self.actionresetSettings, SIGNAL("triggered()"), self.resetSettings)
        
        self.actionabout = QAction(QIcon(":/plugins/midvatten/icons/about.png"), "About", self.iface.mainWindow())
        QObject.connect(self.actionabout, SIGNAL("triggered()"), self.about)
        
        self.actionupdatecoord = QAction(QIcon(":/plugins/midvatten/icons/updatecoordfrpos.png"), "Update coordinates from map position", self.iface.mainWindow())
        QObject.connect(self.actionupdatecoord , SIGNAL("triggered()"), self.updatecoord)
        
        self.actionupdateposition = QAction(QIcon(":/plugins/midvatten/icons/updateposfrcoord.png"), "Update map position from coordinates", self.iface.mainWindow())
        QObject.connect(self.actionupdateposition , SIGNAL("triggered()"), self.updateposition)
        
        self.action_wlvlimport = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_manual.png"), "Import w level measurements", self.iface.mainWindow())
        QObject.connect(self.action_wlvlimport , SIGNAL("triggered()"), self.wlvlimport)
        
        self.action_wlvlcalculate = QAction(QIcon(":/plugins/midvatten/icons/calc_level_masl.png"), "Calculate w level above sea level", self.iface.mainWindow())
        QObject.connect(self.action_wlvlcalculate , SIGNAL("triggered()"), self.wlvlcalculate)
        
        self.action_wlvlloggimport = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_logger.png"), "Import w level from logger", self.iface.mainWindow())
        QObject.connect(self.action_wlvlloggimport , SIGNAL("triggered()"), self.wlvlloggimport)
        
        self.action_wlvlloggcalibrate = QAction(QIcon(":/plugins/midvatten/icons/calibr_level_logger_masl.png"), "Calibrate w level from logger", self.iface.mainWindow())
        QObject.connect(self.action_wlvlloggcalibrate , SIGNAL("triggered()"), self.wlvlloggcalibrate)

        self.actionimport_wqual_lab = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_lab.png"), "Import w quality from lab", self.iface.mainWindow())
        QObject.connect(self.actionimport_wqual_lab, SIGNAL("triggered()"), self.import_wqual_lab)
        
        self.actionimport_wqual_field = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_field.png"), "Import w quality from field", self.iface.mainWindow())
        QObject.connect(self.actionimport_wqual_field, SIGNAL("triggered()"), self.import_wqual_field)
        
        self.actionimport_stratigraphy = QAction(QIcon(":/plugins/midvatten/icons/import_stratigraphy.png"), "Import stratigraphy data", self.iface.mainWindow())
        QObject.connect(self.actionimport_stratigraphy, SIGNAL("triggered()"), self.import_stratigraphy)
        
        self.actionimport_obs_points = QAction(QIcon(":/plugins/midvatten/icons/import_obs_points.png"), "Import obs points table", self.iface.mainWindow())
        QObject.connect(self.actionimport_obs_points, SIGNAL("triggered()"), self.import_obs_points)
        
        self.actionimport_wflow = QAction(QIcon(":/plugins/midvatten/icons/import_wflow.png"), "Import w flow measurements", self.iface.mainWindow())
        QObject.connect(self.actionimport_wflow, SIGNAL("triggered()"), self.import_wflow)
        
        self.actionPlotTS = QAction(QIcon(":/plugins/midvatten/icons/PlotTS.png"), "Time series plot", self.iface.mainWindow())
        self.actionPlotTS.setWhatsThis("Plot time series for selected objects")
        self.iface.registerMainWindowAction(self.actionPlotTS, "F7")   # The function should also be triggered by the F7 key
        QObject.connect(self.actionPlotTS, SIGNAL("triggered()"), self.PlotTS)
        
        self.actionPlotXY = QAction(QIcon(":/plugins/midvatten/icons/PlotXY.png"), "Scatter plot", self.iface.mainWindow())
        self.actionPlotXY.setWhatsThis("Plot XY scatter data (e.g. seismic profiel) for the selected objects")
        self.iface.registerMainWindowAction(self.actionPlotXY, "F8")   # The function should also be triggered by the F8 key
        QObject.connect(self.actionPlotXY, SIGNAL("triggered()"), self.PlotXY)
        
        self.actionPlotStratigraphy = QAction(QIcon(":/plugins/midvatten/icons/PlotStratigraphy.png"), "Plot stratigraphy", self.iface.mainWindow())
        self.actionPlotStratigraphy.setWhatsThis("Show stratigraphy for selected objects (modified ARPAT)")
        self.iface.registerMainWindowAction(self.actionPlotStratigraphy, "F9")   # The function should also be triggered by the F9 key
        QObject.connect(self.actionPlotStratigraphy, SIGNAL("triggered()"), self.PlotStratigraphy)
        
        self.actiondrillreport = QAction(QIcon(":/plugins/midvatten/icons/drill_report.png"), "General Report", self.iface.mainWindow())
        self.actiondrillreport.setWhatsThis("Show a general report for the selected obs point")
        self.iface.registerMainWindowAction(self.actiondrillreport, "F10")   # The function should also be triggered by the F10 key
        QObject.connect(self.actiondrillreport, SIGNAL("triggered()"), self.drillreport)

        self.actionwqualreport = QAction(QIcon(":/plugins/midvatten/icons/wqualreport.png"), "Water Quality Report", self.iface.mainWindow())
        self.actionwqualreport.setWhatsThis("Show water quality for the selected obs point")
        self.iface.registerMainWindowAction(self.actionwqualreport, "F11")   # The function should also be triggered by the F11 key
        QObject.connect(self.actionwqualreport, SIGNAL("triggered()"), self.waterqualityreport)

        self.actionChartMaker = QAction(QIcon(":/plugins/midvatten/icons/ChartMakerSQLite.png"), "ChartMaker for Midvatten DB", self.iface.mainWindow())
        self.actionChartMaker.setWhatsThis("Start ChartMaker for SQLite data")
        self.iface.registerMainWindowAction(self.actionChartMaker, "F12")   # The function should also be triggered by the F12 key
        QObject.connect(self.actionChartMaker, SIGNAL("triggered()"), self.ChartMaker)

        # Add toolbar with buttons 
        self.toolBar = self.iface.addToolBar("Midvatten")
        self.toolBar.addAction(self.actionsetup)
        #self.toolBar.addAction(self.actionloadthelayers)
        self.toolBar.addAction(self.actionPlotTS)
        self.toolBar.addAction(self.actionPlotXY)
        self.toolBar.addAction(self.actionPlotStratigraphy)
        self.toolBar.addAction(self.actiondrillreport)
        self.toolBar.addAction(self.actionwqualreport)
        #self.toolBar.addAction(self.actionChartMaker)
        
        # Add plugins menu items
        self.menu = QMenu("Midvatten")
        self.menu.import_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Import data to database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.import_data_menu)
        self.menu.import_data_menu.addAction(self.action_wlvlimport)   
        self.menu.import_data_menu.addAction(self.action_wlvlloggimport)   
        self.menu.import_data_menu.addAction(self.actionimport_wqual_lab)
        self.menu.import_data_menu.addAction(self.actionimport_wqual_field)   
        self.menu.import_data_menu.addAction(self.actionimport_stratigraphy)   
        #self.menu.import_data_menu.addAction(self.actionimport_wflow)   
        self.menu.import_data_menu.addAction(self.actionimport_obs_points)   

        self.menu.add_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Edit data in database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.add_data_menu)
        self.menu.add_data_menu.addAction(self.action_wlvlcalculate)   
        self.menu.add_data_menu.addAction(self.action_wlvlloggcalibrate)   
        self.menu.add_data_menu.addAction(self.actionupdatecoord)   
        self.menu.add_data_menu.addAction(self.actionupdateposition)   

        self.menu.plot_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&View plot"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.plot_data_menu.menuAction())
        self.menu.addMenu(self.menu.plot_data_menu)
        self.menu.plot_data_menu.addAction(self.actionPlotTS) 
        self.menu.plot_data_menu.addAction(self.actionPlotXY)
        self.menu.plot_data_menu.addAction(self.actionPlotStratigraphy)
        #self.menu.plot_data_menu.addAction(self.actionChartMaker)          #Not until implemented!

        self.menu.report_menu = QMenu(QCoreApplication.translate("Midvatten", "&View report"))
        self.menu.addMenu(self.menu.report_menu)
        self.menu.report_menu.addAction(self.actiondrillreport)
        self.menu.report_menu.addAction(self.actionwqualreport)

        self.menu.addSeparator()
        self.menu.addAction(self.actionNewDB)
        self.menu.addAction(self.actionloadthelayers)   
        self.menu.addAction(self.actionsetup)
        self.menu.addAction(self.actionresetSettings)
        self.menu.addAction(self.actionabout)
        #self.iface.addPluginToMenu("&Midvatten", self.actionsetup)
        #self.iface.addPluginToMenu("&Midvatten", self.actionresetSettings)
        #self.iface.addPluginToMenu("&Midvatten", self.actionabout)
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)
        
    def unload(self):    
        # Remove the plugin menu items and icons
        self.menu.deleteLater()
        #self.iface.removePluginMenu("&Midvatten", self.add_data_menu.menuAction())
        #self.iface.removePluginMenu("&Midvatten", self.plot_data_menu.menuAction())
        #self.iface.removePluginMenu("&Midvatten", self.actionsetup)
        #self.iface.removePluginMenu("&Midvatten", self.actionresetSettings)
        #self.iface.removePluginMenu("&Midvatten", self.actionabout)
        
        # remove tool bar
        del self.toolBar
        
        # Also remove F6 - F12 key triggers
        self.iface.unregisterMainWindowAction(self.actionsetup)
        self.iface.unregisterMainWindowAction(self.actionPlotTS)
        self.iface.unregisterMainWindowAction(self.actionPlotXY)
        self.iface.unregisterMainWindowAction(self.actionPlotStratigraphy)
        self.iface.unregisterMainWindowAction(self.actiondrillreport)
        self.iface.unregisterMainWindowAction(self.actionwqualreport)
        self.iface.unregisterMainWindowAction(self.actionChartMaker)
        sys.path.remove(os.path.dirname(os.path.abspath(__file__))) #Clean up python environment

    def about(self):   
        #filenamepath = os.path.dirname(__file__) + "/metadata.txt"
        filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
        iniText = QSettings(filenamepath , QSettings.IniFormat)
        verno = iniText.value('version').toString()
        author = iniText.value('author').toString()
        email = iniText.value('email').toString()
        homepage = iniText.value('homepage').toString()

        ABOUT_templatefile = os.path.join(os.sep,os.path.dirname(__file__),"about","about_template.htm")
        ABOUT_outputfile = os.path.join(os.sep,os.path.dirname(__file__),"about","about.htm")
        f_in = open(ABOUT_templatefile, 'r')
        f_out = open(ABOUT_outputfile, 'w')
        wholefile = f_in.read()
        changedfile = wholefile.replace('VERSIONCHANGETHIS',verno).replace('AUTHORCHANGETHIS',author).replace('EMAILCHANGETHIS',email).replace('HOMEPAGECHANGETHIS',homepage)
        f_out.write(changedfile)
        f_in.close()
        f_out.close()
        #infoString = QString("This is the Midvatten toolset for QGIS. ")
        #infoString = infoString.append(QString("\n<a href=\'" + homepage + "'></a>"))
        #infoString = infoString.append("\n\n" + verno)
        #infoString = infoString.append("\nAuthor: " + author)
        #infoString = infoString.append("\nEmail: " + email)
        #QMessageBox.information(self.iface.mainWindow(), "About the Midvatten toolset", infoString)
        dlg = HtmlDialog("About Midvatten plugin for QGIS",QUrl.fromLocalFile(ABOUT_outputfile))
        dlg.exec_()

    def ChartMaker(self):            #  - Not ready - let this method import another 'ChartMaker-file' with necessary classes and methods
        if self.settingsareloaded == False:    # If the first thing the user does is to plot time series, then load settings from project file
            self.loadSettings()    
        utils.pop_up_info("not yet implemented") #for debugging

    def createsettingsdict(self):    # Here is where an empty settings dictionary is defined
        dictionary = defs.settingsdict()
        return dictionary

    def drillreport(self):             
        if self.settingsareloaded == False:    # If this is the first thing user does - then load settings from project file
            self.loadSettings()    
        allcritical_layers = ('obs_points', 'w_levels', 'w_qual_lab')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:    # A warning if some of the layers are in editing mode
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease consider exiting this mode before generating a report.", "Warning")

        if not (self.settingsdict['database'] == ''):
            if qgis.utils.iface.activeLayer():
                if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok': #only one selected object
                    obsid = utils.getselectedobjectnames()  # selected obs_point is now found in obsid[0]
                    from drillreport import drillreport
                    drillreport(obsid[0],self.settingsdict) 
                else:
                    utils.pop_up_info("You have to select exactly one observation point!","Attention")
            else:
                utils.pop_up_info("You have to select the obs_points layer and the observation point (just one!) for which to generate a general report!", "Attention")
        else: 
            utils.pop_up_info("Check settings! \nYou have to select database first!")
        
    def import_obs_points(self):            #  - Not ready - let this method import another 'ChartMaker-file' with necessary classes and methods
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('obs_points')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import observation points data, from a semicolon or comma separated ascii file (see plugin documentation for more information about the obs_points table).\n\nThe import file must have one header row and the following 26 columns:\n1. obsid, 2. name, 3. place, 4. type, 5. length, 6. drillstop\n7. diam, 8. material, 9. screen, 10. capacity, 11. drilldate, 12. wmeas_yn\n13. wlogg_yn, 14. east, 15. north, 16. ne_accur, 17. ne_source, 18. h_toc\n19. h_tocags, 20. h_gs, 21. h_accur, 22. h_syst, 23. h_source, 24. source\n25. com_onerow, 26. com_html\n\n                Continue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import obspointimportclass
                importinstance = obspointimportclass()
                if not importinstance.status=='True':      # 
                    utils.pop_up_info("Something failed during import") #for debugging
                else:  
                    utils.pop_up_info("%s observation points were imported to the database.\nTo display the imported points on map, select them in\nthe obs_points attribute table then update map position:\nMidvatten - Edit data in database - Update map position from coordinates"%str(importinstance.RecordsAfter[0][0] - importinstance.RecordsBefore[0][0]))            

    def import_stratigraphy(self):            #  - Not ready - let this method import another 'ChartMaker-file' with necessary classes and methods
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('obs_points', 'stratigraphy')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import stratigraphy data from a semicolon or comma separated ascii file (see plugin documentation for more information about the stratigraphy table).\n\nThe import file must have one header row and the following 9 columns:\n1. obsid\n2. stratigraphy_id\n3. depth_top\n4. depth_bot\n5. geology\n6. geoshort\n7. capacity\n8. well_development\n9. comment\n\n                Continue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import stratigraphyimportclass
                importinstance = stratigraphyimportclass()
                if not importinstance.status=='True':      # 
                    utils.pop_up_info("Something failed during import") #for debugging
                else:  
                    utils.pop_up_info("%s stratigraphy layers were imported to the database."%str(importinstance.RecordsAfter[0][0] - importinstance.RecordsBefore[0][0]))
                    
    def import_wflow(self):            #  - Not ready - let this method import another 'ChartMaker-file' with necessary classes and methods
        if self.settingsareloaded == False:    # If the first thing the user does is to plot time series, then load settings from project file
            self.loadSettings()    
        utils.pop_up_info("not yet implemented") #for debugging
            
    def import_wqual_field(self):            #  - Not ready - let this method import another 'ChartMaker-file' with necessary classes and methods
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('obs_points', 'w_qual_field')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import, from a semicolon or comma separated ascii file, water quality data from field measurements. The text file must have one header row and the following 10 columns (the column order is important, column names are not):\n\n1. obsid - must exist in obs_points table\n2. staff\n3. date_time - on format yyyy-mm-dd hh:mm(:ss)\n4. instrument\n5. parameter - water quality parameter name\n6. reading_num - param. value (real number, decimal separator=point(.))\n7. reading_txt - parameter value as text, including <, > etc\n8. unit\n9. flow_lpm - sampling flow in litres/minute\n10. comment - text string, avoid semicolon and commas\n\nNote! Each set of obsid, date_time and parameter must be unique!\n\n                Continue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import wqualfieldimportclass
                importinstance = wqualfieldimportclass()
                if not importinstance.status=='True':      #W
                    utils.pop_up_info("Something failed during import") #for debugging
                else:  
                    utils.pop_up_info("%s water quality parameter values were imported to the database"%str(importinstance.RecordsAfter[0][0] - importinstance.RecordsBefore[0][0]))
                    
    def import_wqual_lab(self):            #  - Not ready - let this method import another 'ChartMaker-file' with necessary classes and methods
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('obs_points', 'w_qual_lab')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import, from a semicolon or comma separated ascii file, water quality data from laboratory analysis. The text file must have one header row and the following 12 columns (the column order is important, column names are not):\n\n1. obsid - must exist in obs_points table\n2. depth - sample depth (real number)\n3. report - each pair of 'report' & 'parameter' must be unique!\n4. project\n5. staff\n6. date_time - on format yyyy-mm-dd hh:mm(:ss)\n7. analysis_method\n8. parameter - water quality parameter name\n9. reading_num - param. value (real number, decimal separator=point(.))\n10. reading_txt - parameter value as text, including <, > etc\n11. unit\n12. comment - text string, avoid semicolon and commas\n\n                Continue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import wqualimportclass
                importinstance = wqualimportclass()
                if not importinstance.status=='True':      #
                    utils.pop_up_info("Something failed during import") #for debugging
                else:  
                    utils.pop_up_info("%s water quality parameter values were imported to the database"%str(importinstance.RecordsAfter[0][0] - importinstance.RecordsBefore[0][0]))
            
    def loadSettings(self):   # settingsdict is a dictionary belonging to instance midvatten. Must be stored and loaded here.
        """read plugin settings from QgsProject instance"""
        self.readingSettings = True  
        # map data types to function names
        prj = QgsProject.instance()
        functions = { 'str' : prj.readEntry,
                     'QString' : prj.readEntry,
                     'int' : prj.readNumEntry,
                     'float' : prj.readDoubleEntry,
                     'bool' : prj.readBoolEntry,
                     'datetime' : prj.readDoubleEntry, # we converted datetimes to float in writeSetting()
                     'QStringList' : prj.readListEntry,
                     'pyqtWrapperType' : prj.readListEntry # strange name for QStringList
                     }
        output = {}
        for (key, value) in self.settingsdict.items():
            dataType = type(value).__name__
            try:
                func = functions[dataType]
                output[key] = func("Midvatten", key)
            except KeyError:
                utils.pop_up_info("Settings key does not exist: "+key)        
        for (key, value) in output.items():
            self.settingsdict[key] = output[key][0]
            #utils.pop_up_info("in self.settingsdict is loaded Key: "+key+"\n and value : "+str(output[key]))        # DEBUGGING
        self.readingSettings = False
        self.settingsareloaded = True

    def loadthelayers(self):            
        if self.settingsareloaded == False:    # If this is the first thing the user does, then load settings from project file
            self.loadSettings()    
        if not self.settingsdict['database'] == '':
            sanity = utils.askuser("YesNo","""This operation will load default layers ( with predefined layout, edit forms etc.) from your selected database to your qgis project.\n\nIf any default Midvatten DB layers already are loaded into your qgis project,\nthen those layers first will be removed from your qgis project.\n\nProceed?""",'Warning!')
            if sanity.result == 1:
                loadlayers(qgis.utils.iface, self.settingsdict)
                self.iface.mapCanvas().refresh()  # to redraw after loaded symbology
        else:   
            utils.pop_up_info("You have to select a database in Mivatten settings first!")

    def NewDB(self):            # NewDB - Calls function CreateNewDB
        sanity = utils.askuser("YesNo","""This will create a new empty\nMidvatten DB with predefined design.\n\nContinue?""",'Are you sure?')
        if sanity.result == 1:
            filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
            iniText = QSettings(filenamepath , QSettings.IniFormat)
            verno = iniText.value('version').toString()
            from create_db import newdb
            newdbinstance = newdb(verno)
            if not newdbinstance.dbpath=='':
                db = newdbinstance.dbpath
                self.settingsdict['database'] = db
                self.saveSettings()

    def PlotTS(self):            # PlotTS -
        if self.settingsareloaded == False:    # If the first thing the user does is to plot time series, then load settings from project file    
            #utils.pop_up_info("reading from .qgs file")    #debugging
            self.loadSettings()    
        if not (self.settingsdict['database'] == '' or self.settingsdict['tstable'] =='' or self.settingsdict['tscolumn'] == ''):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok':
                    dlg = TimeSeriesPlot(self.iface, layer, self.settingsdict)
            else:
                utils.pop_up_info("You have to select a layer first!")
        else:
            utils.pop_up_info("Check Midvatten settings! \nSelect database, table and column for time series plot!")
            
    def PlotStratigraphy(self):            
        if self.settingsareloaded == False:    # If the first thing the user does is to plot stratigraphy, then load settings from project file
            self.loadSettings()    
        if not (self.settingsdict['database'] == '') and not (self.settingsdict['stratigraphytable']==''):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok' and utils.strat_selection_check(layer) == 'ok':
                        dlg = Stratigraphy(self.iface, layer, self.settingsdict)
                        dlg.showSurvey()
                        self.dlg = dlg        # only to prevent the Qdialog from closing.
            else:
                utils.pop_up_info("You have to select a layer first!")
        else: 
            utils.pop_up_info("Check Midvatten settings! \nYou have to select database and stratigraphy table first!")

    def PlotXY(self):            
        if self.settingsareloaded == False:    # If the first thing the user does is to plot xy data, then load settings from project file
            self.loadSettings()    
        if not (self.settingsdict['database'] == '' or self.settingsdict['xytable'] =='' or self.settingsdict['xy_xcolumn'] == '' or (self.settingsdict['xy_y1column'] == '' and self.settingsdict['xy_y2column'] == '' and self.settingsdict['xy_y3column'] == '')):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok':
                    dlg = XYPlot(self.iface, layer, self.settingsdict)
            else:
                utils.pop_up_info("You have to select a layer first!")
        else:
            utils.pop_up_info("Check Midvatten settings! \nSelect database, table and columns for x and y data!")

    def resetSettings(self):    
        self.settingsdict = self.createsettingsdict()    # calling for the method that defines an empty dictionary of settings
        self.saveSettings()        # the empty settings dictionary is stored

    def saveSettings(self):   # settingsdict is a dictionary belonging to instance midvatten. Must be stored and loaded here.
        if not self.readingSettings:
            for (key, value) in self.settingsdict.items():        # For storing in project file, as Time Manager plugin
                try: # write plugin settings to QgsProject # For storing in project file, as Time Manager plugin
                    QgsProject.instance().writeEntry("Midvatten",key, value ) # For storing in project file, as Time Manager plugin
                except TypeError: # For storing in project file, as Time Manager plugin
                    utils.pop_up_info("Wrong type for "+key+"!\nType: "+str(type(value))) #For storing in project file, as Time Manager plugin
        
    def setup(self):    #
        """Choose spatialite database and relevant table"""
        if self.settingsareloaded == False:    # If the first thing the user does is to check settings, then load settings from project file
            self.loadSettings()    
        dlg = midvsettings(self.iface.mainWindow(), self.settingsdict)  # dlg is an instance of midvsettings (Probably not needed to send QDialog and Ui_Dialog as arguments)
        if dlg.exec_() == QDialog.Accepted:      # When the settins dialog is closed, all settings are stored in the dictionary
            self.settingsdict['database'] = dlg.txtpath.text()    
            self.settingsdict['tstable'] = dlg.ListOfTables.currentText()
            self.settingsdict['tscolumn'] = dlg.ListOfColumns.currentText()
            self.settingsdict['tsdotmarkers'] = dlg.checkBoxDataPoints.checkState()
            self.settingsdict['tsstepplot'] = dlg.checkBoxStepPlot.checkState()
            self.settingsdict['xytable']  = dlg.ListOfTables_2.currentText()
            self.settingsdict['xy_xcolumn'] = dlg.ListOfColumns_2.currentText()
            self.settingsdict['xy_y1column'] = dlg.ListOfColumns_3.currentText()
            self.settingsdict['xy_y2column'] = dlg.ListOfColumns_4.currentText()
            self.settingsdict['xy_y3column'] = dlg.ListOfColumns_5.currentText()
            self.settingsdict['xydotmarkers'] =  dlg.checkBoxDataPoints_2.checkState()
            self.settingsdict['wqualtable']  = dlg.ListOfTables_WQUAL.currentText()
            self.settingsdict['wqual_paramcolumn'] = dlg.ListOfColumns_WQUALPARAM.currentText()
            self.settingsdict['wqual_valuecolumn'] = dlg.ListOfColumns_WQUALVALUE.currentText()
            self.settingsdict['wqual_unitcolumn'] = dlg.ListOfColumns_WQUALUNIT.currentText()
            self.settingsdict['wqual_sortingcolumn'] = dlg.ListOfColumns_WQUALSORTING.currentText()
            self.settingsdict['stratigraphytable'] = dlg.ListOfTables_3.currentText()
            self.settingsdict['tabwidget'] = dlg.tabWidget.currentIndex()
            self.saveSettings()            # Since the SelectTSDialog has saved all settings they should be reached by loading them here...

    def updatecoord(self):
        if self.settingsareloaded == False:    # If the first thing the user does is to update coordinates, then load settings from project file    
            self.loadSettings()    
        layer = self.iface.activeLayer()
        if not layer:           #check there is actually a layer selected
            utils.pop_up_info("You have to select/activate obs_points layer!")
        elif layer.isEditable():
            utils.pop_up_info("The selected layer is currently in editing mode.\nPlease exit this mode before updating coordinates.", "Warning")
        else:
            if not (self.settingsdict['database'] == ''):
                layer = qgis.utils.iface.activeLayer()
                if str(layer.name()).encode('utf-8')=='obs_points':     #IF LAYER obs_points IS SELECTED
                    sanity = utils.askuser("AllSelected","""Do you want to update coordinates\nfor All or Selected objects?""")
                    if sanity.result == 0:      #IF USER WANT ALL OBJECTS TO BE UPDATED
                        sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nCoordinates will be written in fields east and north\nfor ALL objects in the obs_points table.\nProceed?""")
                        if sanity.result==1:
                            ALL_OBS = utils.sql_load_fr_db("select distinct obsid from obs_points")
                            observations = [None]*len(ALL_OBS)
                            i = 0
                            for obs in ALL_OBS:
                                observations[i] = str(obs[0]).encode('utf-8')
                                #utils.pop_up_info(str(observations[i])) #DEBUGGING
                                i+=1
                            #utils.pop_up_info(str(observations)) #DEBUGGING
                            from coords_and_position import updatecoordinates
                            updatecoordinates(observations)
                    elif sanity.result == 1:    #IF USER WANT ONLY SELECTED OBJECTS TO BE UPDATED
                        sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nCoordinates will be written in fields east and north\nfor SELECTED objects in the obs_points table.\nProceed?""")
                        if sanity.result==1:
                            if utils.selection_check(layer) == 'ok':    #Checks that there are some objects selected at all!
                                observations = utils.getselectedobjectnames()
                                from coords_and_position import updatecoordinates
                                updatecoordinates(observations)                        
                else:
                    utils.pop_up_info("You have to select/activate obs_points layer!")
            else:
                utils.pop_up_info("Check settings! \nSelect database first!")        

    def updateposition(self):
        if self.settingsareloaded == False:    # If the first thing the user does is to update coordinates, then load settings from project file    
            self.loadSettings()    
        layer = self.iface.activeLayer()
        if not layer:           #check there is actually a layer selected
            utils.pop_up_info("You have to select/activate obs_points layer!")
        elif layer.isEditable():
            utils.pop_up_info("The selected layer is currently in editing mode.\nPlease exit this mode before updating position.", "Warning")
        else:
            if not (self.settingsdict['database'] == ''):
                layer = qgis.utils.iface.activeLayer()
                if str(layer.name()).encode('utf-8')=='obs_points':     #IF LAYER obs_points IS SELECTED
                    sanity = utils.askuser("AllSelected","""Do you want to update position\nfor All or Selected objects?""")
                    if sanity.result == 0:      #IF USER WANT ALL OBJECTS TO BE UPDATED
                        sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nALL objects in obs_points will be moved to positions\ngiven by their coordinates in fields east and north.\nProceed?""")
                        if sanity.result==1:
                            ALL_OBS = utils.sql_load_fr_db("select distinct obsid from obs_points")
                            observations = [None]*len(ALL_OBS)
                            i = 0
                            for obs in ALL_OBS:
                                observations[i] = str(obs[0]).encode('utf-8')
                                #utils.pop_up_info(str(observations[i])) #DEBUGGING
                                i+=1
                            #utils.pop_up_info(str(observations)) #DEBUGGING
                            from coords_and_position import updateposition
                            updateposition(observations)
                    elif sanity.result == 1:    #IF USER WANT ONLY SELECTED OBJECTS TO BE UPDATED
                        sanity = utils.askuser("YesNo","""Sanity check! This will alter the database.\nSELECTED objects in obs_points will be moved to positions\ngiven by their coordinates in fields east and north.\nProceed?""")
                        if sanity.result==1:
                            if utils.selection_check(layer) == 'ok':    #Checks that there are some objects selected at all!
                                observations = utils.getselectedobjectnames()
                                from coords_and_position import updateposition
                                updateposition(observations)                        
                else:
                    utils.pop_up_info("You have to select/activate obs_points layer!")
            else:
                utils.pop_up_info("Check settings! \nSelect database first!")        
            
    def waterqualityreport(self):
        if self.settingsareloaded == False:    # If the first thing the user does is to plot time series, then load settings from project file
            self.loadSettings()    
        if not (self.settingsdict['database'] == '') and not (self.settingsdict['wqualtable']=='') and not (self.settingsdict['wqual_paramcolumn']=='')  and not (self.settingsdict['wqual_valuecolumn']==''):
            if qgis.utils.iface.activeLayer():
                if utils.selection_check(qgis.utils.iface.activeLayer()) == 'ok':
                    wqualreport(qgis.utils.iface.activeLayer(),self.settingsdict)            #TEMPORARY FOR GVAB
            else:
                utils.pop_up_info("You have to select a layer and the object with water quality first!")
        else: 
            utils.pop_up_info("Check Midvatten settings! \nSomething is wrong in the 'W quality report' tab!")

    def wlvlcalculate(self):             
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    
            
        allcritical_layers = ('obs_points', 'w_levels')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before calculating water level.", "Warning")
                    errorsignal = 1

        if self.settingsdict['database'] == '': #Check that database is selected
            utils.pop_up_info("Check settings! \nSelect database first!")        
            errorsignal = 1

        layer = qgis.utils.iface.activeLayer()
        if layer:
            if utils.selection_check(layer) == 'ok':
                pass
            else:
                errorsignal = 1
        else:
            utils.pop_up_info("You have to select a relevant layer!")
            errorsignal = 1

        if not(errorsignal == 1):     
            from wlevels_calc_calibr import calclvl
            dlg = calclvl(self.iface.mainWindow())  # dock is an instance of calibrlogger
            dlg.exec_()

    def wlvlimport(self):            #  - To import (from a csv file) manual water level measurements 
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('obs_points', 'w_levels')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # om ingen av de kritiska lagren är i editeringsmode
            sanity = utils.askuser("YesNo","""You are about to import water level measurements\nfrom a semicolon or comma separated ascii text file.\nThe text file must have one header row and columns:\n\nobsid;date_time;meas;comment\n\nColumn names are unimportant although column\norder is, as well as format:\n\nobsid: string\ndate_time: yyyy-mm-dd hh:mm(:ss)\nMEAS: real number, decimal sep=point(.), No thousand sep.\ncomment: string, no commas!!!\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import wlvlimportclass
                importinstance = wlvlimportclass()
                if not importinstance.status=='True':      #Why is this if statement? Nothing more is to be done! 
                    utils.pop_up_info("Something failed during import") #for debugging
                else:  
                    utils.pop_up_info("%s water level measurements were imported to the database"%str(importinstance.RecordsAfter[0][0] - importinstance.RecordsBefore[0][0]))

    def wlvlloggcalibrate(self):             
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('w_levels_logger', 'w_levels')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before calibrating logger data.", "Warning")
                    errorsignal = 1

        layer = qgis.utils.iface.activeLayer()
        if layer:
            if utils.selection_check(layer) == 'ok':
                pass
            else:
                errorsignal = 1
        else:
            utils.pop_up_info("You have to select a relevant layer!")
            errorsignal = 1
            
        if errorsignal == 0:
            if not (self.settingsdict['database'] == ''):
                if qgis.utils.iface.activeLayer():
                    if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok':
                        obsid = utils.getselectedobjectnames()
                        sanity1sql = """select count(obsid) from w_levels_logger where obsid = '""" +  obsid[0] + """'"""
                        sanity2sql = """select count(obsid) from w_levels_logger where head_cm not null and head_cm !='' and obsid = '""" +  obsid[0] + """'"""
                        if utils.sql_load_fr_db(sanity1sql) == utils.sql_load_fr_db(sanity2sql): # This must only be done if head_cm exists for all data
                            from wlevels_calc_calibr import calibrlogger
                            dlg = calibrlogger(self.iface.mainWindow(),obsid)  # dock is an instance of calibrlogger
                            dlg.exec_()
                        else:
                            utils.pop_up_info("""There must not be empty cells or null values in the 'head_cm' column!\nFix head_cm data problem and try again.""", "Error") 
                else:
                    utils.pop_up_info("You have to select the obs_points layer and the object (just one!) for which logger data is to be imported!")
            else: 
                utils.pop_up_info("Check settings! \nYou have to select database first!")

    def wlvlloggimport(self):            #  - Not ready 
        errorsignal = 0
        if self.settingsareloaded == False:    # If this is the first thing user does - then load settings from project file
            self.loadSettings()    

        allcritical_layers = ('obs_points', 'w_levels_logger')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # om ingen av de kritiska lagren är i editeringsmode
            if not (self.settingsdict['database'] == ''):
                if qgis.utils.iface.activeLayer():
                    if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok':
                
                        obsid = utils.getselectedobjectnames()
                    
                        longmessage = """You are about to import water head data, recorded with a\nLevel Logger (e.g. Diver), for """
                        longmessage += obsid[0]
                        longmessage +=""".\nData is supposed to be imported from a semicolon or comma\nseparated ascii text file. The text file must have one header row\nand columns:\n\nDate/time,Water head[cm],Temperature[°C]\nor\nDate/time,Water head[cm],Temperature[°C],1:Conductivity[mS/cm]\n\nColumn names are unimportant although column order is.\nAlso, date-time must have format yyyy-mm-dd hh:mm(:ss) and\nthe other columns must be real numbers with point(.) as decimal\nseparator and no separator for thousands.\nRemember to not use comma in the comment field!\n\nContinue?"""
                        sanity = utils.askuser("YesNo",unicode(longmessage,'utf-8'),'Are you sure?')
                        if sanity.result == 1:
                            from import_data_to_db import wlvlloggimportclass
                            importinstance = wlvlloggimportclass()
                            if not importinstance.status=='True':      
                                utils.pop_up_info("Something failed during import") #for debugging

                else:
                    utils.pop_up_info("You have to select the obs_points layer and the object (just one!) for which logger data is to be imported!")
            else: 
                utils.pop_up_info("Check settings! \nYou have to select database first!")

