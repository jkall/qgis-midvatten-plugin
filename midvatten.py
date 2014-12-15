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
import os.path
import sys
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED
import datetime
from tsplot import TimeSeriesPlot
from stratigraphy import Stratigraphy
from xyplot import XYPlot
from wqualreport import wqualreport
from loaddefaultlayers import loadlayers
import midvatten_utils as utils 
from definitions import midvatten_defs
from sectionplot import SectionPlot
import customplot
from midvsettings import midvsettings
import midvsettingsdialog
from piper import PiperPlot
#import profilefromdem

class midvatten:
    def __init__(self, iface): # Might need revision of variables and method for loading default variables
        sys.path.append(os.path.dirname(os.path.abspath(__file__))) #add midvatten plugin directory to pythonpath
        self.iface = iface
        self.ms = midvsettings()#self.ms.settingsdict is created when ms is imported
        
    def initGui(self): # Creates actions that will start plugin configuration
        self.actionNewDB = QAction(QIcon(":/plugins/midvatten/icons/create_new.xpm"), "Create a new Midvatten project DB", self.iface.mainWindow())
        QObject.connect(self.actionNewDB, SIGNAL("triggered()"), self.NewDB)
        
        self.actionloadthelayers = QAction(QIcon(":/plugins/midvatten/icons/loaddefaultlayers.png"), "Load default db-layers to qgis", self.iface.mainWindow())
        self.actionloadthelayers.setWhatsThis("Load default layers from the selected database")
        self.iface.registerMainWindowAction(self.actionloadthelayers, "F7")   # The function should also be triggered by the F7 key
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
        
        self.action_import_wlvl = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_manual.png"), "Import w level measurements", self.iface.mainWindow())
        QObject.connect(self.action_import_wlvl , SIGNAL("triggered()"), self.import_wlvl)
        
        self.action_import_wflow = QAction(QIcon(":/plugins/midvatten/icons/load_wflow.png"), "Import w flow measurements", self.iface.mainWindow())
        QObject.connect(self.action_import_wflow , SIGNAL("triggered()"), self.import_wflow)
        
        self.action_import_seismics = QAction(QIcon(":/plugins/midvatten/icons/load_seismics.png"), "Import seismic data", self.iface.mainWindow())
        QObject.connect(self.action_import_seismics , SIGNAL("triggered()"), self.import_seismics)
        
        self.action_import_vlf = QAction(QIcon(":/plugins/midvatten/icons/load_vlf.png"), "Import vlf data", self.iface.mainWindow())
        QObject.connect(self.action_import_vlf , SIGNAL("triggered()"), self.import_vlf)
        
        self.action_import_obs_lines = QAction(QIcon(":/plugins/midvatten/icons/import_obs_lines.png"), "Import obs lines table", self.iface.mainWindow())
        QObject.connect(self.action_import_obs_lines , SIGNAL("triggered()"), self.import_obs_lines)
        
        self.action_wlvlcalculate = QAction(QIcon(":/plugins/midvatten/icons/calc_level_masl.png"), "Calculate w level above sea level", self.iface.mainWindow())
        QObject.connect(self.action_wlvlcalculate , SIGNAL("triggered()"), self.wlvlcalculate)
        
        self.action_aveflowcalculate = QAction(QIcon(":/plugins/midvatten/icons/import_wflow.png"), "Calculate Aveflow from Accvol", self.iface.mainWindow())
        QObject.connect(self.action_aveflowcalculate , SIGNAL("triggered()"), self.aveflowcalculate)
        
        self.action_import_wlvllogg = QAction(QIcon(":/plugins/midvatten/icons/load_wlevels_logger.png"), "Import w level from logger", self.iface.mainWindow())
        QObject.connect(self.action_import_wlvllogg , SIGNAL("triggered()"), self.import_wlvllogg)
        
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
        
        self.actionimport_meteo = QAction(QIcon(":/plugins/midvatten/icons/import_wqual_field.png"), "Import meteorological observations", self.iface.mainWindow())
        QObject.connect(self.actionimport_meteo, SIGNAL("triggered()"), self.import_meteo)
        
        self.actionPlotTS = QAction(QIcon(":/plugins/midvatten/icons/PlotTS.png"), "Time series plot", self.iface.mainWindow())
        self.actionPlotTS.setWhatsThis("Plot time series for selected objects")
        self.iface.registerMainWindowAction(self.actionPlotTS, "F8")   # The function should also be triggered by the F8 key
        QObject.connect(self.actionPlotTS, SIGNAL("triggered()"), self.PlotTS)
        
        self.actionPlotXY = QAction(QIcon(":/plugins/midvatten/icons/PlotXY.png"), "Scatter plot", self.iface.mainWindow())
        self.actionPlotXY.setWhatsThis("Plot XY scatter data (e.g. seismic profile) for the selected objects")
        self.iface.registerMainWindowAction(self.actionPlotXY, "F9")   # The function should also be triggered by the F9 key
        QObject.connect(self.actionPlotXY, SIGNAL("triggered()"), self.PlotXY)
        
        self.actionPlotPiper = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons","Piper.png")), "Piper diagram", self.iface.mainWindow())
        self.actionPlotPiper.setWhatsThis("Plot a rectangular Piper diagram for selected objects")
        QObject.connect(self.actionPlotPiper, SIGNAL("triggered()"), self.PlotPiper)
                
        self.actionPlotSQLite = QAction(QIcon(os.path.join(os.path.dirname(__file__),"icons","plotsqliteicon.png")), "Custom plots", self.iface.mainWindow())
        self.actionPlotSQLite.setWhatsThis("Create custom plots for your reports")
        QObject.connect(self.actionPlotSQLite, SIGNAL("triggered()"), self.PlotSQLite)
        
        self.actionPlotStratigraphy = QAction(QIcon(":/plugins/midvatten/icons/PlotStratigraphy.png"), "Stratigraphy plot", self.iface.mainWindow())
        self.actionPlotStratigraphy.setWhatsThis("Show stratigraphy for selected objects (modified ARPAT)")
        self.iface.registerMainWindowAction(self.actionPlotStratigraphy, "F10")   # The function should also be triggered by the F10 key
        QObject.connect(self.actionPlotStratigraphy, SIGNAL("triggered()"), self.PlotStratigraphy)
        
        self.actiondrillreport = QAction(QIcon(":/plugins/midvatten/icons/drill_report.png"), "General report", self.iface.mainWindow())
        self.actiondrillreport.setWhatsThis("Show a general report for the selected obs point")
        self.iface.registerMainWindowAction(self.actiondrillreport, "F11")   # The function should also be triggered by the F11 key
        QObject.connect(self.actiondrillreport, SIGNAL("triggered()"), self.drillreport)

        self.actionwqualreport = QAction(QIcon(":/plugins/midvatten/icons/wqualreport.png"), "Water quality report", self.iface.mainWindow())
        self.actionwqualreport.setWhatsThis("Show water quality for the selected obs point")
        self.iface.registerMainWindowAction(self.actionwqualreport, "F12")   # The function should also be triggered by the F12 key
        QObject.connect(self.actionwqualreport, SIGNAL("triggered()"), self.waterqualityreport)

        self.actionPlotSection = QAction(QIcon(":/plugins/midvatten/icons/PlotSection.png"), "Section plot", self.iface.mainWindow())
        self.actionPlotSection.setWhatsThis("Plot a section with stratigraphy and water levels")
        #self.iface.registerMainWindowAction(self.actionChartMaker, "F12")   # The function should also be triggered by the F12 key
        QObject.connect(self.actionPlotSection, SIGNAL("triggered()"), self.PlotSection)
        
        self.actionChartMaker = QAction(QIcon(":/plugins/midvatten/icons/ChartMakerSQLite.png"), "ChartMaker for Midvatten DB", self.iface.mainWindow())
        self.actionChartMaker.setWhatsThis("Start ChartMaker for SQLite data")
        #self.iface.registerMainWindowAction(self.actionChartMaker, "F12")   # The function should also be triggered by the F12 key
        QObject.connect(self.actionChartMaker, SIGNAL("triggered()"), self.ChartMaker)

        self.actionVacuumDB = QAction(QIcon(":/plugins/midvatten/icons/vacuum.png"), "Vacuum the database", self.iface.mainWindow())
        self.actionVacuumDB.setWhatsThis("Perform database vacuuming")
        QObject.connect(self.actionVacuumDB, SIGNAL("triggered()"), self.VacuumDB)

        self.actionZipDB = QAction(QIcon(":/plugins/midvatten/icons/zip.png"), "Backup the database", self.iface.mainWindow())
        self.actionZipDB.setWhatsThis("A compressed copy of the database will be placed in same directory as the db.")
        QObject.connect(self.actionZipDB, SIGNAL("triggered()"), self.ZipDB)

        # Add toolbar with buttons 
        self.toolBar = self.iface.addToolBar("Midvatten")
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
        self.menu = QMenu("Midvatten")
        self.menu.import_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Import data to database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.import_data_menu)
        self.menu.import_data_menu.addAction(self.actionimport_obs_points)   
        self.menu.import_data_menu.addAction(self.action_import_wlvl)   
        self.menu.import_data_menu.addAction(self.action_import_wlvllogg)   
        self.menu.import_data_menu.addAction(self.actionimport_wqual_lab)
        self.menu.import_data_menu.addAction(self.actionimport_wqual_field)   
        self.menu.import_data_menu.addAction(self.action_import_wflow)   
        self.menu.import_data_menu.addAction(self.actionimport_stratigraphy)
        self.menu.import_data_menu.addAction(self.actionimport_meteo)
        self.menu.import_data_menu.addAction(self.action_import_obs_lines)   
        self.menu.import_data_menu.addAction(self.action_import_seismics)   
        self.menu.import_data_menu.addAction(self.action_import_vlf)   

        self.menu.add_data_menu = QMenu(QCoreApplication.translate("Midvatten", "&Edit data in database"))
        #self.iface.addPluginToMenu("&Midvatten", self.menu.add_data_menu.menuAction())
        self.menu.addMenu(self.menu.add_data_menu)
        self.menu.add_data_menu.addAction(self.action_wlvlcalculate)   
        self.menu.add_data_menu.addAction(self.action_wlvlloggcalibrate)   
        self.menu.add_data_menu.addAction(self.actionupdatecoord)   
        self.menu.add_data_menu.addAction(self.actionupdateposition)   
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
        self.menu.report_menu.addAction(self.actionwqualreport)

        self.menu.db_manage_menu = QMenu(QCoreApplication.translate("Midvatten", "&Database management"))
        self.menu.addMenu(self.menu.db_manage_menu)
        self.menu.db_manage_menu.addAction(self.actionNewDB)
        self.menu.db_manage_menu.addAction(self.actionVacuumDB)
        self.menu.db_manage_menu.addAction(self.actionZipDB)
        
        self.menu.addSeparator()

        self.menu.addAction(self.actionloadthelayers)   
        self.menu.addAction(self.actionsetup)
        self.menu.addAction(self.actionresetSettings)
        self.menu.addAction(self.actionabout)
        #self.iface.addPluginToMenu("&Midvatten", self.actionsetup)
        #self.iface.addPluginToMenu("&Midvatten", self.actionresetSettings)
        #self.iface.addPluginToMenu("&Midvatten", self.actionabout)
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.addMenu(self.menu)

        # QGIS iface connections
        self.iface.projectRead.connect(self.ProjectOpened)
        self.iface.newProjectCreated.connect(self.ProjectCreated)
        
    def unload(self):    
        # Remove the plugin menu items and icons
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
        self.iface.unregisterMainWindowAction(self.actionChartMaker)
        sys.path.remove(os.path.dirname(os.path.abspath(__file__))) #Clean up python environment

    def about(self):   
        #filenamepath = os.path.dirname(__file__) + "/metadata.txt"
        filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
        iniText = QSettings(filenamepath , QSettings.IniFormat)#This method seems to return a list of unicode strings BUT it seems as if the encoding from the byte strings in the file is not utf-8, hence there is need for special encoding, see below
        verno = str(iniText.value('version'))
        author = iniText.value('author').encode('cp1252')#.encode due to encoding probs
        email = str(iniText.value('email'))
        homepage = str(iniText.value('homepage'))

        ABOUT_templatefile = os.path.join(os.sep,os.path.dirname(__file__),"about","about_template.htm")
        ABOUT_outputfile = os.path.join(os.sep,os.path.dirname(__file__),"about","about.htm")
        f_in = open(ABOUT_templatefile, 'r')
        f_out = open(ABOUT_outputfile, 'w')
        wholefile = f_in.read()
        changedfile = wholefile.replace('VERSIONCHANGETHIS',verno).replace('AUTHORCHANGETHIS',author).replace('EMAILCHANGETHIS',email).replace('HOMEPAGECHANGETHIS',homepage)
        f_out.write(changedfile)
        f_in.close()
        f_out.close()
        dlg = utils.HtmlDialog("About Midvatten plugin for QGIS",QUrl.fromLocalFile(ABOUT_outputfile))
        dlg.exec_()

    def aveflowcalculate(self):            
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    
            
        allcritical_layers = ('obs_points', 'w_flow')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before calculating water level.", "Warning")
                    errorsignal = 1

        if self.ms.settingsdict['database'] == '': #Check that database is selected
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
            from w_flow_calc_aveflow import calcave
            dlg = calcave(self.iface.mainWindow()) 
            dlg.exec_()

    def ChartMaker(self): #  - Not ready - 
        if self.ms.settingsareloaded == False:    # If this is the first thing the user does, then load settings from project file
            self.ms.loadSettings()    
        utils.pop_up_info("not yet implemented") #for debugging

    def drillreport(self):             
        if self.ms.settingsareloaded == False:    # If this is the first thing user does - then load settings from project file
            self.ms.loadSettings()    
        allcritical_layers = ('obs_points', 'w_levels', 'w_qual_lab')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:    # A warning if some of the layers are in editing mode
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease consider exiting this mode before generating a report.", "Warning")

        if not (self.ms.settingsdict['database'] == ''):
            if qgis.utils.iface.activeLayer():
                if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok': #only one selected object
                    obsid = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())  # selected obs_point is now found in obsid[0]
                    from drillreport import drillreport
                    drillreport(obsid[0],self.ms.settingsdict) 
                else:
                    utils.pop_up_info("You have to select exactly one observation point!","Attention")
            else:
                utils.pop_up_info("You have to select the obs_points layer and the observation point (just one!) for which to generate a general report!", "Attention")
        else: 
            self.iface.messageBar().pushMessage("Error","Please check your Midvatten Settings and select a database! Reset if needed.", 2)

    def import_obs_lines(self):
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_lines')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import observation lines data, from a text file which must have one header row and 6 columns (see plugin web page for further explanation):\nWKT;obsid;name;place;type;source\n\nPlease note that:\nThere must be WKT geometries of type LINESTRING in the first column.\nThe LINESTRING geometries must correspond to SRID in the dataabse.\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in string fields.\nEmpty or null values are not allowed for obsid and there must not be any duplicates of obsid\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
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
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import observation points data, from a text file which must have one header row and 26 columns (see plugin web page for further explanation):\n\n1. obsid, 2. name, 3. place, 4. type, 5. length, 6. drillstop, 7. diam, 8. material, 9. screen, 10. capacity, 11. drilldate, 12. wmeas_yn, 13. wlogg_yn, 14. east, 15. north, 16. ne_accur, 17. ne_source, 18. h_toc, 19. h_tocags, 20. h_gs, 21. h_accur, 22. h_syst, 23. h_source, 24. source, 25. com_onerow, 26. com_html\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in string fields.\nEmpty or null values are not allowed for obsid and there must not be any duplicates of obsid.\nEast and north values must correspond to the database SRID.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.obsp_import()
                #utils.pop_up_info(returnvalue) #debugging
                #utils.pop_up_info(importinstance.status) #debugging
                if importinstance.status=='True':      # 
                    utils.pop_up_info("%s observation points were imported to the database.\nTo display the imported points on map, select them in\nthe obs_points attribute table then update map position:\nMidvatten - Edit data in database - Update map position from coordinates"%str(importinstance.recsafter - importinstance.recsbefore))
                    #self.iface.messageBar().pushMessage("Info","%s observation points were imported to the database.\nTo display the imported points on map, select them in\nthe obs_points attribute table then update map position:\nMidvatten - Edit data in database - Update map position from coordinates"%str(importinstance.recsafter - importinstance.recsbefore), 0)                    
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_seismics(self):
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    
        allcritical_layers = ('obs_lines', 'seismic_data')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0: 
            sanity = utils.askuser("YesNo","""You are about to import interpreted seismic data, from a text file which must have one header row and 6 columns:\n\nobsid, length, ground, bedrock, gw_table, comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nEmpty or null values are not allowed for obsid or length.\nEach combination of obsid and length must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
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
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points', 'stratigraphy')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import stratigraphy data, from a text file which must have one header row and 9 columns:\n1. obsid\n2. stratid - integer starting from ground surface and increasing downwards\n3. depth_top - depth to top of stratigraphy layer\n4. depth_bot - depth to bottom of stratigraphy layer\n5. geology - full description of layer geology\n6. geoshort - shortname for layer geology (see dicionary)\n7. capacity\n8. development - well development\n9. comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid or stratid, such rows will be excluded from the import.\nEach combination of obsid and stratid must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
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
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_lines', 'vlf_data')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # om ingen av de kritiska lagren är i editeringsmode
            sanity = utils.askuser("YesNo","""You are about to import raw data from vlf measurements, from a text file which must have one header row and 5 columns:\n\nobsid; length; real_comp; imag_comp, comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\nDecimal separator must be point (.)\nEmpty or null values are not allowed for obsid or length.\nEach combination of obsid and length must be unique.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
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
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points', 'w_flow')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # om ingen av de kritiska lagren är i editeringsmode
            sanity = utils.askuser("YesNo","""You are about to import water flow reading, from a text file which must have one header row and 7 columns:\n\n1. obsid\n2. instrumentid\n3. flowtype\n4. date_time\n5. reading\n6. unit\n7. comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nBe sure to use a limited number of flowtypes since all new flowtypes will silently be added to the database table zz_flowtype during import.\nEmpty or null values are not allowed for obsid, instrumentid, flowtype or date_time.\nEach combination of obsid, instrumentid, flowtype and date_time must be unique.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.wflow_import()
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s water flow readings were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_wlvl(self):    
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points', 'w_levels')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:
            sanity = utils.askuser("YesNo","""You are about to import water level measurements, from a text file which must have one header row and 4 columns:\n\nobsid;date_time;meas;comment\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid or date_time, such rows will be excluded from the import.\nEmpty or null values are not accepted at the same time in both the columns meas and comment.\nEach combination of obsid and date_time must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.wlvl_import()
                if importinstance.status=='True': 
                    self.iface.messageBar().pushMessage("Info","%s water level measurements were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass
                    
    def import_wlvllogg(self):#  - should be rewritten 
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first thing user does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points', 'w_levels_logger')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:   
            if not (self.ms.settingsdict['database'] == ''):
                if qgis.utils.iface.activeLayer():
                    if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok':                
                        obsid = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())                    
                        longmessage = """You are about to import water head data, recorded with a\nLevel Logger (e.g. Diver), for """
                        longmessage += obsid[0]
                        longmessage +=u""".\nData is supposed to be imported from a semicolon or comma\nseparated text file. The text file must have one header row and columns:\n\nDate/time,Water head[cm],Temperature[°C]\nor\nDate/time,Water head[cm],Temperature[°C],1:Conductivity[mS/cm]\n\nColumn names are unimportant although column order is.\nAlso, date-time must have format yyyy-mm-dd hh:mm(:ss) and\nthe other columns must be real numbers with point(.) as decimal separator and no separator for thousands.\nRemember to not use comma in the comment field!\n\nAlso, records where any fields are empty will be excluded from the report!\n\nContinue?"""
                        sanity = utils.askuser("YesNo",utils.returnunicode(longmessage),'Are you sure?')
                        if sanity.result == 1:
                            from import_data_to_db import wlvlloggimportclass
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
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points', 'w_qual_field')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import water quality data from field measurements, from a text file which must have one header row and the following 10 columns:\n\n1. obsid\n2. staff\n3. date_time - on format yyyy-mm-dd hh:mm(:ss)\n4. instrument\n5. parameter - water quality parameter name\n6. reading_num - param. value (real number, decimal separator=point(.))\n7. reading_txt - parameter value as text, including <, > etc\n8. unit\n9. flow_lpm - sampling flow in litres/minute\n10. comment - text string\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid, date_time or parameter, such rows will be excluded from the import.\nEach combination of obsid, date_time and parameter must be unique.\n\nContinue?""",'Are you sure?')
            #utils.pop_up_info(sanity.result)   #debugging
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.wqualfield_import()
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s water quality paramters were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass
                    
    def import_wqual_lab(self):
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

        allcritical_layers = ('obs_points', 'w_qual_lab')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if errorsignal == 0:        # unless none of the critical layers are in editing mode
            sanity = utils.askuser("YesNo","""You are about to import water quality data from laboratory analysis, from a text file which must have one header row and the following 12 columns:\n\n1. obsid - must exist in obs_points table\n2. depth - sample depth (real number)\n3. report - each pair of 'report' & 'parameter' must be unique!\n4. project\n5. staff\n6. date_time - on format yyyy-mm-dd hh:mm(:ss)\n7. analysis_method\n8. parameter - water quality parameter name\n9. reading_num - param. value (real number, decimal separator=point(.))\n10. reading_txt - parameter value as text, including <, > etc\n11. unit\n12. comment - text string, avoid semicolon and commas\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nEmpty or null values are not allowed for obsid, report or parameter, such rows will be excluded from the import.\nEach combination of report and parameter must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.wquallab_import()
                if importinstance.status=='True':      # 
                    self.iface.messageBar().pushMessage("Info","%s water quality parameters were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass

    def import_meteo(self):
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()

        if utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master where tbl_name = 'meteo'""")[0]==True and len(utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master where tbl_name = 'meteo'""")[1])==0: #verify there actually is a meteo table (introduced in midv plugin version 1.1)
            errorsignal = 1
            utils.pop_up_info("There is no table for meteorological data in your database! Perhaps your database was created with a previous version of Midvatten plugin? Contact plugin author for advice!", "Error")
        
        allcritical_layers = ('obs_points')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before importing data.", "Warning")
                    errorsignal = 1

        if utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master where tbl_name = 'meteo'""")[0]==False: 
            errorsignal = 1
            utils.pop_up_info("Database error! Try resetting midvatten plugin settings. Then select database again.", "Error")

        if errorsignal == 0:        # unless none of the critical layers are in editing mode or the database is so old no meteo table exist
            sanity = utils.askuser("YesNo","""You are about to import meteorological data from, from a text file which must have one header row and 8 columns:\n\n"obsid", "instrumentid", "parameter", "date_time", "reading_num", "reading_txt", "unit", "comment"\n\nPlease note that:\nThe file must be either comma, or semicolon-separated.\ndate_time must be of format 'yyyy-mm-dd hh:mm(:ss)'.\nDecimal separator must be point (.)\nComma or semicolon is not allowed in the comments.\nBe sure to use a limited number of parameters since all new parameters will silently be added to the database table zz_meteoparam during import.\nEmpty or null values are not allowed for obsid, instrumentid, parameter or date_time.\nEach combination of obsid, instrumentid, parameter and date_time must be unique.\n\nContinue?""",'Are you sure?')
            if sanity.result == 1:
                from import_data_to_db import midv_data_importer
                importinstance = midv_data_importer()
                importinstance.meteo_import()
                if importinstance.status=='True': 
                    self.iface.messageBar().pushMessage("Info","%s meteorological readings were imported to the database"%str(importinstance.recsafter - importinstance.recsbefore), 0)
                    try:
                        self.midvsettingsdialog.ClearEverything()
                        self.midvsettingsdialog.LoadAndSelectLastSettings()
                    except:
                        pass
            
    def loadthelayers(self):            
        if self.ms.settingsareloaded == False:    # If this is the first thing the user does, then load settings from project file
            self.ms.loadSettings()    
        if not self.ms.settingsdict['database'] == '':
            sanity = utils.askuser("YesNo","""This operation will load default layers ( with predefined layout, edit forms etc.) from your selected database to your qgis project.\n\nIf any default Midvatten DB layers already are loaded into your qgis project, then those layers first will be removed from your qgis project.\n\nProceed?""",'Warning!')
            if sanity.result == 1:
                loadlayers(qgis.utils.iface, self.ms.settingsdict)
                self.iface.mapCanvas().zoomToFullExtent()#zoom to full extent to let user see what was loaded
                self.iface.mapCanvas().refresh()  # to redraw after loaded symbology
        else:   
            utils.pop_up_info("You have to select a database in Midvatten settings first!")

    def NewDB(self): 
        sanity = utils.askuser("YesNo","""This will create a new empty\nMidvatten DB with predefined design.\n\nContinue?""",'Are you sure?')
        if sanity.result == 1:
            filenamepath = os.path.join(os.path.dirname(__file__),"metadata.txt" )
            iniText = QSettings(filenamepath , QSettings.IniFormat)
            verno = str(iniText.value('version')) 
            from create_db import newdb
            newdbinstance = newdb(verno)
            if not newdbinstance.dbpath=='':
                db = newdbinstance.dbpath
                self.ms.settingsdict['database'] = db
                self.ms.save_settings()

    def PlotPiper(self):
        if self.ms.settingsareloaded == False:
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == '' or self.ms.settingsdict['database'] == ' '):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok':
                    dlg = PiperPlot(self.ms,qgis.utils.iface.activeLayer())
            else:
                self.iface.messageBar().pushMessage("Error","You have to select a layer first!",2,duration=15)        
        else:
            self.iface.messageBar().pushMessage("Error","Specify database and w_qual_lab parameters for Piper plot. (Check Midvatten Settings.)",2,duration=15)
                 
    def PlotTS(self):
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to plot time series, then load settings from project file    
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == '' or self.ms.settingsdict['tstable'] =='' or self.ms.settingsdict['tscolumn'] == ''):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok':
                    dlg = TimeSeriesPlot(layer, self.ms.settingsdict)
            else:
                self.iface.messageBar().pushMessage("Error","You have to select a layer first!",2,duration=15)        
        else:
            self.iface.messageBar().pushMessage("Error","Please check your Midvatten Settings and select database, table and column for time series plot. Reset if needed.", 2,duration=15)
            
    def PlotStratigraphy(self):            
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to plot stratigraphy, then load settings from project file
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == '') and not (self.ms.settingsdict['stratigraphytable']==''):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok' and utils.strat_selection_check(layer) == 'ok':
                        dlg = Stratigraphy(self.iface, layer, self.ms.settingsdict)
                        dlg.showSurvey()
                        self.dlg = dlg        # only to prevent the Qdialog from closing.
            else:
                utils.pop_up_info("You have to select a layer first!")
        else: 
            self.iface.messageBar().pushMessage("Error","Please check your Midvatten Settings and select database and stratigraphy table. Reset if needed.", 2)

    def PlotSection(self):
        if self.ms.settingsareloaded == False:    # Perhaps settings should always be loaded, to 
            self.ms.loadSettings()
            
        if self.ms.settingsdict['database'] == '':#perhaps there is no database defined
            self.iface.messageBar().pushMessage("Error","No database found. Please check your Midvatten Settings. Reset if needed.", 2)
            return
        SectionLineLayer = qgis.utils.iface.mapCanvas().currentLayer()#MUST BE LINE VECTOR LAYER WITH SAME EPSG as MIDV_OBSDB AND THERE MUST BE ONLY ONE SELECTED FEATURE
        msg = None
        if SectionLineLayer.selectedFeatureCount()==1:#First verify only one feature is selected in the active layer...
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
            i=0
            for id in selectedobspoints:
                obsidlist.append(str(id))#we cannot send unicode as string to sql because it would include the u'
                i+=1
            OBSID = tuple(obsidlist)#because module sectionplot depends on obsid being a tuple
        else:
            msg = 'You must select at least two objects in the obs_points layer'
        
        if msg:#if something went wrong
            self.iface.messageBar().pushMessage("Error",msg, 2,duration =15)
        else:#otherwise go
            try:
                self.myplot.do_it(self.ms,OBSID,SectionLineLayer)
            except:
                self.myplot = SectionPlot(self.iface.mainWindow(), self.iface)
                self.myplot.do_it(self.ms,OBSID,SectionLineLayer)

    def PlotXY(self):            
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to plot xy data, then load settings from project file
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == '' or self.ms.settingsdict['xytable'] =='' or self.ms.settingsdict['xy_xcolumn'] == '' or (self.ms.settingsdict['xy_y1column'] == '' and self.ms.settingsdict['xy_y2column'] == '' and self.ms.settingsdict['xy_y3column'] == '')):
            layer = qgis.utils.iface.activeLayer()
            if layer:
                if utils.selection_check(layer) == 'ok':
                    dlg = XYPlot(layer, self.ms.settingsdict)
            else:
                utils.pop_up_info("You have to select a layer first!")
        else:
            self.iface.messageBar().pushMessage("Error","Please check your Midvatten Settings and select database, table and columns for x and y data!. Reset if needed.", 2)

    def PlotSQLite(self):
        if self.ms.settingsdict['database'] == '':
            self.iface.messageBar().pushMessage("Error","A database is needed to create custom plots. Please check your Midvatten Settings. Reset if needed.", 2,duration=15)
            return

        try:
            self.customplot.activateWindow()
        except:
            self.customplot = customplot.plotsqlitewindow(self.iface.mainWindow(), self.ms)#self.iface as arg?

    def ProjectCreated(self):
        self.resetSettings()
        
    def ProjectOpened(self):
        self.ms.resetSettings()
        self.ms.loadSettings()
        try:#if midvsettingsdock is shown, then it must be reloaded
            self.midvsettingsdialog.activateWindow()
            self.midvsettingsdialog.ClearEverything()
            self.midvsettingsdialog.LoadAndSelectLastSettings()
        except:
            pass

    def resetSettings(self):
        self.ms.resetSettings()
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

    def updatecoord(self):
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to update coordinates, then load settings from project file    
            self.ms.loadSettings()    
        layer = self.iface.activeLayer()
        if not layer:           #check there is actually a layer selected
            utils.pop_up_info("You have to select/activate obs_points layer!")
        elif layer.isEditable():
            utils.pop_up_info("The selected layer is currently in editing mode.\nPlease exit this mode before updating coordinates.", "Warning")
        else:
            if not (self.ms.settingsdict['database'] == ''):
                layer = qgis.utils.iface.activeLayer()
                if layer.name()==u'obs_points':     #IF LAYER obs_points IS SELECTED
                    sanity = utils.askuser("AllSelected","""Do you want to update coordinates\nfor All or Selected objects?""")
                    if sanity.result == 0:      #IF USER WANT ALL OBJECTS TO BE UPDATED
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
                            if utils.selection_check(layer) == 'ok':    #Checks that there are some objects selected at all!
                                observations = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())#a list of unicode strings is returned
                                from coords_and_position import updatecoordinates
                                updatecoordinates(observations)                        
                else:
                    utils.pop_up_info("You have to select/activate obs_points layer!")
            else:
                utils.pop_up_info("Check settings! \nSelect database first!")        

    def updateposition(self):
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to update coordinates, then load settings from project file    
            self.ms.loadSettings()    
        layer = self.iface.activeLayer()
        if not layer:           #check there is actually a layer selected
            utils.pop_up_info("You have to select/activate obs_points layer!")
        elif layer.isEditable():
            utils.pop_up_info("The selected layer is currently in editing mode.\nPlease exit this mode before updating position.", "Warning")
        else:
            if not (self.ms.settingsdict['database'] == ''):
                layer = qgis.utils.iface.activeLayer()
                if layer.name()==u'obs_points':     #IF LAYER obs_points IS SELECTED
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
                                observations = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())
                                from coords_and_position import updateposition
                                updateposition(observations)
                                layer.updateExtents()
                else:
                    utils.pop_up_info("You have to select/activate obs_points layer!")
            else:
                utils.pop_up_info("Check settings! \nSelect database first!")        

    def VacuumDB(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to vacuum, then load settings from project file    
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == ''):
            utils.sql_alter_db('vacuum')
        else:
            self.iface.messageBar().pushMessage("Error","You need to specify database in Midvatten Settings. Reset if needed.", 2,duration=15)
        QApplication.restoreOverrideCursor()

    def waterqualityreport(self):
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to plot time series, then load settings from project file
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == '') and not (self.ms.settingsdict['wqualtable']=='') and not (self.ms.settingsdict['wqual_paramcolumn']=='')  and not (self.ms.settingsdict['wqual_valuecolumn']==''):
            if qgis.utils.iface.activeLayer():
                if utils.selection_check(qgis.utils.iface.activeLayer()) == 'ok':#there is a field obsid and at least one object is selected
                    fail = 0
                    for k in utils.getselectedobjectnames(qgis.utils.iface.activeLayer()):#all selected objects
                        if not utils.sql_load_fr_db("select obsid from %s where obsid = '%s'"%(self.ms.settingsdict['wqualtable'],str(k)))[1]:#if there is a selected object without water quality data
                            self.iface.messageBar().pushMessage("Error","No water quality data for %s"%str(k), 2)
                            fail = 1
                    if not fail == 1:#only if all objects has data
                        wqualreport(qgis.utils.iface.activeLayer(),self.ms.settingsdict)            #TEMPORARY FOR GVAB
            else:
                utils.pop_up_info("You have to select a layer and the object with water quality first!")
        else: 
            utils.pop_up_info("Check Midvatten settings! \nSomething is wrong in the 'W quality report' tab!")

    def wlvlcalculate(self):             
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    
            
        allcritical_layers = ('obs_points', 'w_levels')     #Check that none of these layers are in editing mode
        for layername in allcritical_layers:
            layerexists = utils.find_layer(str(layername))
            if layerexists:
                if layerexists.isEditable():
                    utils.pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before calculating water level.", "Warning")
                    errorsignal = 1

        if self.ms.settingsdict['database'] == '': #Check that database is selected
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
            dlg = calclvl(self.iface.mainWindow(),qgis.utils.iface.activeLayer())  # dock is an instance of calibrlogger
            dlg.exec_()

    def wlvlloggcalibrate(self):             
        errorsignal = 0
        if self.ms.settingsareloaded == False:    # If this is the first does - then load settings from project file
            self.ms.loadSettings()    

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
            if not (self.ms.settingsdict['database'] == ''):
                if qgis.utils.iface.activeLayer():
                    if utils.selection_check(qgis.utils.iface.activeLayer(),1) == 'ok':
                        obsid = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())
                        sanity1sql = """select count(obsid) from w_levels_logger where obsid = '""" +  obsid[0] + """'"""
                        sanity2sql = """select count(obsid) from w_levels_logger where head_cm not null and head_cm !='' and obsid = '""" +  obsid[0] + """'"""
                        if utils.sql_load_fr_db(sanity1sql)[1] == utils.sql_load_fr_db(sanity2sql)[1]: # This must only be done if head_cm exists for all data
                            from wlevels_calc_calibr import calibrlogger
                            dlg = calibrlogger(self.iface.mainWindow(),obsid, self.ms.settingsdict)  # dock is an instance of calibrlogger
                            dlg.exec_()
                        else:
                            utils.pop_up_info("""There must not be empty cells or null values in the 'head_cm' column!\nFix head_cm data problem and try again.""", "Error") 
                else:
                    utils.pop_up_info("You have to select the obs_points layer and the object (just one!) for which logger data is to be imported!")
            else: 
                utils.pop_up_info("Check settings! \nYou have to select database first!")

    def ZipDB(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.ms.settingsareloaded == False:    # If the first thing the user does is to ZipDB, then load settings from project file    
            self.ms.loadSettings()    
        if not (self.ms.settingsdict['database'] == ''):
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
        else:
            self.iface.messageBar().pushMessage("Error","You need to specify database in Midvatten Settings. Reset if needed.", 2,duration=15)
        QApplication.restoreOverrideCursor()

    def cleaning2(self):        #clean up after closing section plot Dock dialog --TO BE REMOVED SINCE THIS IS NEVER USED!!!
                print 'cleaning the dock house'
                self.mdl = None
                self.secplotdockOpened = False
                self.wdg = None
