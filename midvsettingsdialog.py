# -*- coding: utf-8 -*-
"""
/***************************************************************************
 midvsettingsdialog
 A part of the QGIS plugin Midvatten
 
 This part of the plugin handles the user interaction with midvsettingsdock and propagates any changes to midvattensettings
 
                             -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/"""
from builtins import str
from builtins import object
import qgis.PyQt
import ast
import os.path
from qgis.PyQt import uic, QtCore
from functools import partial  # only to get combobox signals to work
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QComboBox, QDockWidget, QFileDialog

from midvatten.tools.utils import common_utils, gui_utils, db_utils, midvatten_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools.utils.midvatten_utils import warn_about_old_database

#from ui.midvsettingsdock_ui import Ui_MidDockSettings


midvsettingsdock_ui_class =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui', 'midvsettingsdock.ui'))[0]


class midvsettingsdialogdock(QDockWidget, midvsettingsdock_ui_class): #THE CLASS IS ONLY TO DEAL WITH THE SETTINGS DIALOG
    def __init__(self, parent,iface,msettings):
        self.parent = parent
        self.iface=iface
        #midvsettings instance
        self.ms = msettings
        self.ms.loadSettings()
        #initiate the dockwidget
        QDockWidget.__init__(self, self.parent)        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi( self )#Required by Qt4 to initialize the UI
        self.initUI()

    def initUI(self):
        # The settings dialog is cleared, filled with relevant information and the last selected settings are preset
        self.database_settings = DatabaseSettings(self, self.gridLayout_db)
        self.ClearEverything()

        self.MarkerComboBox.addItems(['obsid', 'type', 'date_time', 'obsid but no legend', 'simple marker'])

        if len(self.ms.settingsdict['database'])>0:
            self.LoadAndSelectLastSettings()

        #Load general settings
        #self.load_and_select_general_settings() # TODO: remove in version 1.4

        # SIGNALS
        #move dockwidget
        self.dockLocationChanged.connect(self.set_location)

        #tab TS
        self.ListOfTables.currentIndexChanged.connect(partial(self.TSTableUpdated))
        self.ListOfColumns.currentIndexChanged.connect(partial(self.ChangedListOfColumns))
        self.checkBoxDataPoints.stateChanged.connect(self.ChangedCheckBoxDataPoints)
        self.checkBoxStepPlot.stateChanged.connect(self.ChangedCheckBoxStepPlot)
        #tab XY
        self.ListOfTables_2.currentIndexChanged.connect(partial(self.XYTableUpdated))
        self.ListOfColumns_2.currentIndexChanged.connect(partial(self.ChangedListOfColumns2))
        self.ListOfColumns_3.currentIndexChanged.connect(partial(self.ChangedListOfColumns3))
        self.ListOfColumns_4.currentIndexChanged.connect(partial(self.ChangedListOfColumns4))
        self.ListOfColumns_5.currentIndexChanged.connect(partial(self.ChangedListOfColumns5))
        self.checkBoxDataPoints_2.stateChanged.connect(self.ChangedCheckBoxDataPoints2)
        #tab wqualreport
        self.ListOfTables_WQUAL.currentIndexChanged.connect(partial(self.WQUALTableUpdated))
        self.ListOfColumns_WQUALPARAM.currentIndexChanged.connect(partial(self.ChangedListOfColumnsWQualParam))
        self.ListOfColumns_WQUALVALUE.currentIndexChanged.connect(partial(self.ChangedListOfColumnsWQualValue))
        self.ListOfdate_time_format.currentIndexChanged.connect(partial(self.ChangedListOfdate_time_format))
        self.ListOfColumns_WQUALUNIT.currentIndexChanged.connect(partial(self.ChangedListOfColumnsWQualUnit))
        self.ListOfColumns_WQUALSORTING.currentIndexChanged.connect(partial(self.ChangedListOfColumnsWQualSorting))

        #tab piper
        self.paramCl.currentIndexChanged.connect(partial(self.ChangedParamCl))
        self.paramHCO3.currentIndexChanged.connect(partial(self.ChangedParamHCO3))
        self.paramSO4.currentIndexChanged.connect(partial(self.ChangedParamSO4))
        self.paramNa.currentIndexChanged.connect(partial(self.ChangedParamNa))
        self.paramK.currentIndexChanged.connect(partial(self.ChangedParamK))
        self.paramCa.currentIndexChanged.connect(partial(self.ChangedParamCa))
        self.paramMg.currentIndexChanged.connect(partial(self.ChangedParamMg))
        self.MarkerComboBox.currentIndexChanged.connect(partial(self.ChangedPiperMarkerComboBox))

        #Draw the widget
        self.iface.addDockWidget(max(self.ms.settingsdict['settingslocation'],1), self)
        self.iface.mapCanvas().setRenderFlag(True)

    def ChangedCheckBoxDataPoints(self):
        self.ms.settingsdict['tsdotmarkers']=self.checkBoxDataPoints.checkState()
        self.ms.save_settings('tsdotmarkers')

    def ChangedCheckBoxDataPoints2(self):
        self.ms.settingsdict['xydotmarkers']=self.checkBoxDataPoints_2.checkState()
        self.ms.save_settings('xydotmarkers')

    def ChangedCheckBoxStepPlot(self):
        self.ms.settingsdict['tsstepplot']=self.checkBoxStepPlot.checkState()
        self.ms.save_settings('tsstepplot')

    def ChangedListOfColumns(self):
        self.ms.settingsdict['tscolumn']=self.ListOfColumns.currentText()
        self.ms.save_settings('tscolumn')

    def ChangedListOfColumns2(self):
        self.ms.settingsdict['xy_xcolumn']=self.ListOfColumns_2.currentText()
        self.ms.save_settings('xy_xcolumn')

    def ChangedListOfColumns3(self):
        self.ms.settingsdict['xy_y1column']=self.ListOfColumns_3.currentText()
        self.ms.save_settings('xy_y1column')

    def ChangedListOfColumns4(self):
        self.ms.settingsdict['xy_y2column']=self.ListOfColumns_4.currentText()
        self.ms.save_settings('xy_y2column')

    def ChangedListOfColumns5(self):
        self.ms.settingsdict['xy_y3column']=self.ListOfColumns_5.currentText()
        self.ms.save_settings('xy_y3column')
                
    def ChangedListOfColumnsWQualParam(self):
        self.ms.settingsdict['wqual_paramcolumn']=self.ListOfColumns_WQUALPARAM.currentText()
        self.ms.save_settings('wqual_paramcolumn')
                
    def ChangedListOfColumnsWQualValue(self):
        self.ms.settingsdict['wqual_valuecolumn']=self.ListOfColumns_WQUALVALUE.currentText()
        self.ms.save_settings('wqual_valuecolumn')        

    def ChangedListOfColumnsWQualUnit(self):
        self.ms.settingsdict['wqual_unitcolumn']=self.ListOfColumns_WQUALUNIT.currentText()
        self.ms.save_settings('wqual_unitcolumn')

    def ChangedListOfColumnsWQualSorting(self):
        self.ms.settingsdict['wqual_sortingcolumn']=self.ListOfColumns_WQUALSORTING.currentText()
        self.ms.save_settings('wqual_sortingcolumn')

    def ChangedListOfdate_time_format(self):
        self.ms.settingsdict['wqual_date_time_format']=self.ListOfdate_time_format.currentText()
        self.ms.save_settings('wqual_date_time_format')

    def ChangedParamCl(self):
        self.ms.settingsdict['piper_cl']=self.paramCl.currentText()
        self.ms.save_settings('piper_cl')

    def ChangedParamHCO3(self):
        self.ms.settingsdict['piper_hco3']=self.paramHCO3.currentText()
        self.ms.save_settings('piper_hco3')

    def ChangedParamSO4(self):
        self.ms.settingsdict['piper_so4']=self.paramSO4.currentText()
        self.ms.save_settings('piper_so4')

    def ChangedParamNa(self):
        self.ms.settingsdict['piper_na']=self.paramNa.currentText()
        self.ms.save_settings('piper_na')

    def ChangedParamK(self):
        self.ms.settingsdict['piper_k']=self.paramK.currentText()
        self.ms.save_settings('piper_k')

    def ChangedParamCa(self):
        self.ms.settingsdict['piper_ca']=self.paramCa.currentText()
        self.ms.save_settings('piper_ca')

    def ChangedParamMg(self):
        self.ms.settingsdict['piper_mg']=self.paramMg.currentText()
        self.ms.save_settings('piper_mg')

    def ChangedPiperMarkerComboBox(self):
        self.ms.settingsdict['piper_markers']=self.MarkerComboBox.currentText()
        self.ms.save_settings('piper_markers')

    def changed_combobox(self, combobox, settings_string):
        """All "ChangedX" that are comboboxed should be replaced to this one
        Usage:
        self.paramHCO3, SIGNAL("activated(int)"), partial(self.changed_combobox, self.paramHCO3, 'piper_hco3'))
        """
        self.ms.settingsdict[settings_string] = combobox.currentText()
        self.ms.save_settings(settings_string)

    def ClearColumnLists(self):
        self.ListOfColumns.clear()
        self.ListOfColumns_2.clear()
        self.ListOfColumns_3.clear()
        self.ListOfColumns_4.clear()
        self.ListOfColumns_5.clear()
        self.ListOfColumns_WQUALPARAM.clear()
        self.ListOfColumns_WQUALVALUE.clear()
        self.ListOfColumns_WQUALUNIT.clear()
        self.ListOfColumns_WQUALSORTING.clear()

    def ClearEverything(self):
        self.database_settings.clear()
        self.ClearTableLists()
        self.ClearColumnLists()
        self.ClearPiperParams()

    def ClearTableLists(self):
        self.ListOfTables.clear()    
        self.ListOfTables_2.clear()
        self.ListOfTables_WQUAL.clear()

    def ClearPiperParams(self):
        self.paramCl.clear()
        self.paramHCO3.clear()
        self.paramSO4.clear()
        self.paramNa.clear()
        self.paramK.clear()
        self.paramCa.clear()
        self.paramMg.clear()

    def ColumnsToComboBox(self, comboboxname='', table=None):
        getattr(self, comboboxname).clear()
        """This method fills comboboxes with columns for selected tool and table"""
        columns = self.LoadColumnsFromTable(table)    # Load all columns into a list 'columns'
        if len(columns)>0:    # Transfer information from list 'columns' to the combobox
            getattr(self, comboboxname).addItem('')
            for columnName in columns:
                getattr(self, comboboxname).addItem(columnName)  # getattr is to combine a function and a string to a combined function

    @db_utils.if_connection_ok
    def LoadAndSelectLastSettings(self):
        #self.ms.save_settings('database')
        self.database_settings.update_settings(self.ms.settingsdict['database'])
        self.load_plot_settings()

    @common_utils.general_exception_handler
    def load_plot_settings(self):
        self.loadTablesFromDB()        # All ListOfTables are filled with relevant information
        self.LoadDistinctPiperParams()

        #TS plot settings
        self.load_and_select_last_ts_plot_settings()

        #XY plot settings
        self.load_and_select_last_xyplot_settings()

        #Water Quality Reports settings
        self.load_and_select_last_wqual_settings()

        #piper diagram settings
        self.load_and_select_last_piper_settings()

        # finally, set dockwidget to last choosen tab
        self.tabWidget.setCurrentIndex(int(self.ms.settingsdict['tabwidget']))

    def load_and_select_last_piper_settings(self):
        searchindex = self.paramCl.findText(self.ms.settingsdict['piper_cl'])
        if searchindex >= 0:
            self.paramCl.setCurrentIndex(searchindex)
        searchindex = self.paramHCO3.findText(self.ms.settingsdict['piper_hco3'])
        if searchindex >= 0:
            self.paramHCO3.setCurrentIndex(searchindex)
        searchindex = self.paramSO4.findText(self.ms.settingsdict['piper_so4'])
        if searchindex >= 0:
            self.paramSO4.setCurrentIndex(searchindex)
        searchindex = self.paramNa.findText(self.ms.settingsdict['piper_na'])
        if searchindex >= 0:
            self.paramNa.setCurrentIndex(searchindex)
        searchindex = self.paramK.findText(self.ms.settingsdict['piper_k'])
        if searchindex >= 0:
            self.paramK.setCurrentIndex(searchindex)
        searchindex = self.paramCa.findText(self.ms.settingsdict['piper_ca'])
        if searchindex >= 0:
            self.paramCa.setCurrentIndex(searchindex)
        searchindex = self.paramMg.findText(self.ms.settingsdict['piper_mg'])
        if searchindex >= 0:
            self.paramMg.setCurrentIndex(searchindex)
        searchindex = self.MarkerComboBox.findText(self.ms.settingsdict['piper_markers'])
        if searchindex >= 0:
            self.MarkerComboBox.setCurrentIndex(searchindex)

    def load_and_select_last_ts_plot_settings(self):
        if len(str(self.ms.settingsdict['tstable'])):#If there is a last selected tstable. #MacOSX fix1
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.ListOfTables.setCurrentIndex(i)
                if str(self.ListOfTables.currentText()) == str(self.ms.settingsdict['tstable']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                    self.TSTableUpdated()        # Fill the given combobox with columns from the given table and also perform a sanity check of table
                    searchindex = self.ListOfColumns.findText(self.ms.settingsdict['tscolumn'])
                    if searchindex >= 0:
                        self.ListOfColumns.setCurrentIndex(searchindex)
                elif i> len(self.ListOfTables):
                    notfound=1
                i = i + 1
            
        if self.ms.settingsdict['tsdotmarkers']==2:#If the TSPlot dot markers checkbox was checked last time it will be so now #MacOSX fix1
            self.checkBoxDataPoints.setChecked(True)
        else:
            self.checkBoxDataPoints.setChecked(False)
        if self.ms.settingsdict['tsstepplot']==2: #If the TSPlot stepplot checkbox was checked last time it will be so now #MacOSX fix1
            self.checkBoxStepPlot.setChecked(True)
        else:
            self.checkBoxStepPlot.setChecked(False)

    def load_and_select_last_wqual_settings(self):
        searchindexouter = self.ListOfTables_WQUAL.findText(self.ms.settingsdict['wqualtable'])
        if searchindexouter >= 0:
            self.ListOfTables_WQUAL.setCurrentIndex(searchindexouter)
            self.WQUALTableUpdated()
            #and then check all possible last selected columns for parameters, values etc.
            searchindex = self.ListOfColumns_WQUALPARAM.findText(self.ms.settingsdict['wqual_paramcolumn'])
            if searchindex >= 0:
                self.ListOfColumns_WQUALPARAM.setCurrentIndex(searchindex)
            searchindex = self.ListOfColumns_WQUALVALUE.findText(self.ms.settingsdict['wqual_valuecolumn'])
            if searchindex >= 0:
                self.ListOfColumns_WQUALVALUE.setCurrentIndex(searchindex)
            searchindex = self.ListOfdate_time_format.findText(self.ms.settingsdict['wqual_date_time_format'])
            if searchindex == -1:
                searchindex = 1
            self.ListOfdate_time_format.setCurrentIndex(searchindex)
            searchindex = self.ListOfColumns_WQUALUNIT.findText(self.ms.settingsdict['wqual_unitcolumn'])
            if searchindex >= 0:
                self.ListOfColumns_WQUALUNIT.setCurrentIndex(searchindex)
            searchindex = self.ListOfColumns_WQUALSORTING.findText(self.ms.settingsdict['wqual_sortingcolumn'])
            if searchindex >= 0:
                self.ListOfColumns_WQUALSORTING.setCurrentIndex(searchindex)

    def load_and_select_last_xyplot_settings(self):
        if len(self.ms.settingsdict['xytable']):#If there is a last selected xytable #MacOSX fix1
            notfound=0 
            i=0
            while notfound==0: #looping through ListOfTables_2 looking for last selected xytable
                self.ListOfTables_2.setCurrentIndex(i)
                if str(self.ListOfTables_2.currentText()) == str(self.ms.settingsdict['xytable']):    #when last selected xytable found, it is selected in list and a lot of columns is searced for #MacOSX fix1
                    notfound=1
                    self.XYTableUpdated()    # Fill the given combobox with columns from the given table and performs a test
                    searchindex = self.ListOfColumns_2.findText(self.ms.settingsdict['xy_xcolumn'])
                    if searchindex >= 0:
                        self.ListOfColumns_2.setCurrentIndex(searchindex)
                    searchindex = self.ListOfColumns_3.findText(self.ms.settingsdict['xy_y1column'])
                    if searchindex >= 0:
                        self.ListOfColumns_3.setCurrentIndex(searchindex)
                    searchindex = self.ListOfColumns_4.findText(self.ms.settingsdict['xy_y2column'])
                    if searchindex >= 0:
                        self.ListOfColumns_4.setCurrentIndex(searchindex)
                    searchindex = self.ListOfColumns_5.findText(self.ms.settingsdict['xy_y3column'])
                    if searchindex >= 0:
                        self.ListOfColumns_5.setCurrentIndex(searchindex)
                elif i> len(self.ListOfTables_2):
                    notfound=1
                i = i + 1

        if self.ms.settingsdict['xydotmarkers']==2:# If the XYPlot dot markers checkbox was checked last time it will be so now #MacOSX fix1
            self.checkBoxDataPoints_2.setChecked(True)
        else:
            self.checkBoxDataPoints_2.setChecked(False)

    def LoadColumnsFromTable(self, table=''):
        return db_utils.tables_columns().get(table, [])

    def loadTablesFromDB(self): # This method populates all table-comboboxes with the tables inside the database
        # Execute a query in SQLite to return all available tables (sql syntax excludes some of the predefined tables)
        # start with cleaning comboboxes before filling with new entries
        tables = list(db_utils.tables_columns().keys())

        self.ListOfTables.addItem('')
        self.ListOfTables_2.addItem('')
        self.ListOfTables_WQUAL.addItem('')

        for table in sorted(tables):
            self.ListOfTables.addItem(table)
            self.ListOfTables_2.addItem(table)
            self.ListOfTables_WQUAL.addItem(table)

    def LoadDistinctPiperParams(self):
        self.ClearPiperParams()

        #Dict not implemented yet.
        lab_parameters = {}
        if lab_parameters:
            for param_list in [self.paramCl,
                          self.paramHCO3,
                          self.paramSO4,
                          self.paramNa,
                          self.paramK,
                          self.paramCa,
                          self.paramMg]:
                new_list = ['']
                new_list.extend(sorted(lab_parameters.keys()))
                param_list.addItems(new_list)
        else:
            connection_ok, result = db_utils.sql_load_fr_db(r"""SELECT DISTINCT parameter FROM w_qual_lab ORDER BY parameter""")
            if connection_ok:
                self.paramCl.addItem('')
                self.paramHCO3.addItem('')
                self.paramSO4.addItem('')
                self.paramNa.addItem('')
                self.paramK.addItem('')
                self.paramCa.addItem('')
                self.paramMg.addItem('')
                for row in result:
                    self.paramCl.addItem(row[0])
                    self.paramHCO3.addItem(row[0])
                    self.paramSO4.addItem(row[0])
                    self.paramNa.addItem(row[0])
                    self.paramK.addItem(row[0])
                    self.paramCa.addItem(row[0])
                    self.paramMg.addItem(row[0])

    def PiperClUpdated(self):
        self.ms.settingsdict['piper_cl']= str(self.paramCl.currentText())
        self.ms.save_settings('piper_cl')#save this specific setting

    def PiperHCO3Updated(self):
        self.ms.settingsdict['piper_hco3']= str(self.paramHCO3.currentText())
        self.ms.save_settings('piper_hco3')#save this specific setting

    def PiperSO4Updated(self):
        self.ms.settingsdict['piper_so4']= str(self.paramSO4.currentText())
        self.ms.save_settings('piper_so4')#save this specific setting

    def PiperNaUpdated(self):
        self.ms.settingsdict['piper_na']= str(self.paramNa.currentText())
        self.ms.save_settings('piper_na')#save this specific setting

    def PiperKUpdated(self):
        self.ms.settingsdict['piper_k']= str(self.paramK.currentText())
        self.ms.save_settings('piper_k')#save this specific setting

    def PiperCaUpdated(self):
        self.ms.settingsdict['piper_ca']= str(self.paramCa.currentText())
        self.ms.save_settings('piper_ca')#save this specific setting

    def PiperMgUpdated(self):
        self.ms.settingsdict['piper_mg']= str(self.paramMg.currentText())
        self.ms.save_settings('piper_mg')#save this specific setting

    def set_location(self):
        dockarea = self.parent.dockWidgetArea(self)
        self.ms.settingsdict['settingslocation']=dockarea
        self.ms.save_settings('settingslocation')
                
    def TSTableUpdated(self):
        """This method is called whenever time series table is changed"""
        # First, update combobox with columns
        self.ColumnsToComboBox('ListOfColumns', self.ListOfTables.currentText())  # For some reason it is not possible to send currentText with the SIGNAL-trigger
        # Second, Make sure that columns obsid and date_time exists
        columns = self.LoadColumnsFromTable(self.ListOfTables.currentText())     # For some reason it is not possible to send currentText with the SIGNAL-trigger
        if ('obsid' in columns) and ('date_time' in columns):
            text = "<font color=green>%s</font>"%ru(QCoreApplication.translate('midvsettingsdialogdock', 'Correct table, both obsid and date_time columns have been found.'))
        else:
            text = "<font color=red>%s</font>"%ru(QCoreApplication.translate('midvsettingsdialogdock', 'Wrong table! obsid and/or date_time is missing.'))
        self.InfoTxtTSPlot.setText(text)
        #finally, save to qgis project settings
        self.ms.settingsdict['tstable']=self.ListOfTables.currentText()
        self.ms.save_settings('tstable')#save this specific setting

    def WQUALTableUpdated(self):
        """This method is called whenever water quality table is changed and fils comboboxes with columns for wqual report"""
        self.ListOfColumns_WQUALPARAM.clear()
        self.ListOfColumns_WQUALVALUE.clear()
        self.ListOfdate_time_format.clear()
        self.ListOfColumns_WQUALUNIT.clear()
        self.ListOfColumns_WQUALSORTING.clear()
        columns = self.LoadColumnsFromTable(self.ListOfTables_WQUAL.currentText())    # Load all columns into a list (dict?) 'columns'
        if len(columns):    # Transfer information from list 'columns' to the combobox
            self.ListOfColumns_WQUALPARAM.addItem('')
            self.ListOfColumns_WQUALVALUE.addItem('')
            self.ListOfdate_time_format.addItem('YYYY')
            self.ListOfColumns_WQUALUNIT.addItem('')
            self.ListOfColumns_WQUALSORTING.addItem('')
            for columnName in columns:
                self.ListOfColumns_WQUALPARAM.addItem(columnName)
                self.ListOfColumns_WQUALVALUE.addItem(columnName)
                self.ListOfColumns_WQUALUNIT.addItem(columnName)
                self.ListOfColumns_WQUALSORTING.addItem(columnName)
        self.ListOfdate_time_format.addItem('YYYY-MM')
        self.ListOfdate_time_format.addItem('YYYY-MM-DD')
        self.ListOfdate_time_format.addItem('YYYY-MM-DD hh')
        self.ListOfdate_time_format.addItem('YYYY-MM-DD hh:mm')
        self.ListOfdate_time_format.addItem('YYYY-MM-DD hh:mm:ss')
        #self.ChangedListOfColumnsWQualParam()
        #self.ChangedListOfColumnsWQualValue()
        #self.ChangedListOfdate_time_format()
        #self.ChangedListOfColumnsWQualUnit()
        #self.ChangedListOfColumnsWQualSorting()
        self.ms.settingsdict['wqualtable']=self.ListOfTables_WQUAL.currentText()
        self.ms.save_settings('wqualtable')#save this specific setting

    def XYColumnsToComboBox(self, table=None):
        """This method fills comboboxes with columns for xyplot"""
        self.ListOfColumns_2.clear()
        self.ListOfColumns_3.clear()
        self.ListOfColumns_4.clear()
        self.ListOfColumns_5.clear()
        columns = self.LoadColumnsFromTable(table)    # Load all columns into a list (dict?) 'columns'
        if len(columns):    # Transfer information from list 'columns' to the combobox
            self.ListOfColumns_2.addItem('')
            self.ListOfColumns_3.addItem('')
            self.ListOfColumns_4.addItem('')
            self.ListOfColumns_5.addItem('')
            for columnName in columns:
                self.ListOfColumns_2.addItem(columnName)  
                self.ListOfColumns_3.addItem(columnName)  
                self.ListOfColumns_4.addItem(columnName)  
                self.ListOfColumns_5.addItem(columnName)  

    def XYTableUpdated(self):
        """This method is called whenever xy table is changed"""
        # First, update comboboxes with columns
        self.XYColumnsToComboBox(self.ListOfTables_2.currentText())   # For some reason it is not possible to send currentText with the SIGNAL-trigger
        # Second, Make sure that column obsid exists
        columns = self.LoadColumnsFromTable(self.ListOfTables_2.currentText())     # For some reason it is not possible to send currentText with the SIGNAL-trigger
        if 'obsid' in columns:    
            text = "<font color=green>%s</font>"%ru(QCoreApplication.translate('midvsettingsdialogdock', 'Correct table! obsid column is found.'))
        else:
            text = "<font color=red>%s</font>"%ru(QCoreApplication.translate('midvsettingsdialogdock', 'Wrong table! obsid is missing.'))
        self.InfoTxtXYPlot.setText(text)
        self.ms.settingsdict['xytable']=self.ListOfTables_2.currentText()
        self.ms.save_settings('xytable')#save this specific setting


class DatabaseSettings(object):
    def __init__(self, midvsettingsdialogdock, gridLayout_db):
        self.midvsettingsdialogdock = midvsettingsdialogdock
        self.layout = gridLayout_db
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.db_settings_obj = None
        self.label_width = self.maximum_label_width()

        self._label = qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('DatabaseSettings', 'Database type')))
        self._label.setFixedWidth(self.label_width)
        self._dbtype_combobox = qgis.PyQt.QtWidgets.QComboBox()
        self._dbtype_combobox.addItems(['', 'spatialite', 'postgis'])

        self.grid = gui_utils.RowEntryGrid()
        self.grid.layout.addWidget(self._label, 0, 0)
        self.grid.layout.addWidget(self._dbtype_combobox, 0, 1)
        self.layout.addWidget(self.grid.widget)

        self.child_widgets = []

        self._dbtype_combobox.currentIndexChanged.connect(self.choose_dbtype)


        #self.layout.setRowStretch(self.layout.rowCount(), 1)

    @property
    def dbtype_combobox(self):
        return common_utils.returnunicode(self._dbtype_combobox.currentText())

    @dbtype_combobox.setter
    def dbtype_combobox(self, value):
        index = self._dbtype_combobox.findText(tools.utils.common_utils.returnunicode(value))
        if index != -1:
            self._dbtype_combobox.setCurrentIndex(index)

    def choose_dbtype(self):
        #Remove stretch
        #self.layout.setRowStretch(self.layout.rowCount(), 0)
        for widget in self.child_widgets:
            try:
                widget.clear_widgets()
            except:
                pass
            try:
                self.layout.removeWidget(widget)
            except:
                pass
            try:
                widget.deleteLater()
            except:
                pass
            try:
                widget.close()
            except:
                pass
        self.child_widgets = []

        dbclasses = {'spatialite': SpatialiteSettings,
                     'postgis': PostgisSettings}

        dbclass = dbclasses.get(self.dbtype_combobox, None)

        if dbclass is None:
            self.db_settings_obj = None
            return

        self.db_settings_obj = dbclass(self.midvsettingsdialogdock, self.label_width)
        self.layout.addWidget(self.db_settings_obj.widget, self.layout.rowCount(), 0)
        self.child_widgets.append(self.db_settings_obj.widget)

        #self.layout.setRowStretch(self.layout.rowCount(), 1)

    def update_settings(self, _db_settings):
        db_settings = None
        if not _db_settings or _db_settings is None:
            return

        try:
            db_settings = ast.literal_eval(_db_settings)
        except:
            common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('DatabaseSettings', 'Reading db_settings failed using string %s')) % _db_settings)
        else:
            pass

        for setting in [db_settings, _db_settings]:
            if isinstance(setting, str):
                # Assume that the db_settings is an old spatialite database
                if os.path.isfile(setting) and setting.endswith('.sqlite'):
                    db_settings = {'spatialite': {'dbpath': setting}}
                    break

        if isinstance(db_settings, dict):
            for dbtype, settings in db_settings.items():
                self.dbtype_combobox = dbtype
                self.choose_dbtype()

                for setting_name, value in settings.items():
                    try:
                        if hasattr(self.db_settings_obj, str(setting_name)):
                            setattr(self.db_settings_obj, str(setting_name), value)
                        else:
                            common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('DatabaseSettings', "Databasetype %s didn' t have setting %s")) % (dbtype, setting_name))
                    except:
                        print(str(setting_name))
                        raise
        else:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('DatabaseSettings', "Could not load database settings. Select database again!")), log_msg=ru(QCoreApplication.translate('DatabaseSettings', 'Tried to load db_settings string %s')) % _db_settings)

    def clear(self):
        self.dbtype_combobox = ''
        self.choose_dbtype()

    def maximum_label_width(self):
        maximumwidth = 0
        for label_name in [ru(QCoreApplication.translate('DatabaseSettings', 'Database type')), ru(QCoreApplication.translate('DatabaseSettings', 'Select db')), ru(QCoreApplication.translate('DatabaseSettings', 'Connections'))]:
            testlabel = qgis.PyQt.QtWidgets.QLabel(label_name)
            maximumwidth = max(maximumwidth, testlabel.sizeHint().width())
        testlabel = None
        return maximumwidth


class SpatialiteSettings(gui_utils.RowEntryGrid):
    def __init__(self, midvsettingsdialogdock, label_width):
        super(SpatialiteSettings, self).__init__()
        self.midvsettingsdialogdock = midvsettingsdialogdock
        self.btnSetDB = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('SpatialiteSettings', 'Select db')))
        self.btnSetDB.setFixedWidth(label_width)
        self.layout.addWidget(self.btnSetDB, 0, 0)
        self._dbpath = qgis.PyQt.QtWidgets.QLineEdit('')
        self._dbpath.textChanged.connect(lambda: self.database_chosen())
        self._dbpath.editingFinished.connect(self.database_chosen)
        self.layout.addWidget(self._dbpath, 0, 1)

        #select file
        self.btnSetDB.clicked.connect(lambda x: self.select_file())

    @property
    def dbpath(self):
        return common_utils.returnunicode(self._dbpath.text())

    @dbpath.setter
    def dbpath(self, value):
        self._dbpath.setText(tools.utils.common_utils.returnunicode(value))

    def select_file(self):
        """ Open a dialog to locate the sqlite file and some more..."""
        dbpath, __ = QFileDialog.getOpenFileName(None, str("Select database:"), "*.sqlite")
        if dbpath:  # Only get new db name if not cancelling the FileDialog
            self.dbpath = dbpath

        else:  # debug
            common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('SpatialiteSettings', "DB selection cancelled and still using database path %s")) % common_utils.returnunicode(self.midvsettingsdialogdock.ms.settingsdict['database']))

    def database_chosen(self):
        if self._dbpath.hasFocus():
            return

        dbpath = self.dbpath
        self.midvsettingsdialogdock.ms.settingsdict['database'] = common_utils.anything_to_string_representation(
            {'spatialite': {'dbpath': dbpath}})
        self.midvsettingsdialogdock.ms.save_settings('database')
        self.midvsettingsdialogdock.load_plot_settings()
        warn_about_old_database()

class PostgisSettings(gui_utils.RowEntryGrid):
    """Using a guide from http://gis.stackexchange.com/questions/180427/retrieve-available-postgis-connections-in-pyqgis"""
    def __init__(self, midvsettingsdialogdock, label_width):
        super(PostgisSettings, self).__init__()
        self.midvsettingsdialogdock = midvsettingsdialogdock

        postgis_connections = db_utils.get_postgis_connections()

        self.label = qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('PostgisSettings', 'Connections')))
        self.label.setFixedWidth(label_width)
        self._connection = qgis.PyQt.QtWidgets.QComboBox()
        self._connection.addItem('')
        connection_names = ['/'.join([k, ':'.join([v.get('host', ''), v.get('port', '')]), v.get('database', '')]) for k, v in postgis_connections.items()]
        self._connection.addItems(sorted(connection_names))

        self._connection.currentIndexChanged.connect(self.set_db)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self._connection, 0, 1)

    @property
    def connection(self):
        return common_utils.returnunicode(self._connection.currentText())

    @connection.setter
    def connection(self, value):
        index = self._connection.findText(tools.utils.common_utils.returnunicode(value))
        if index != -1:
            self._connection.setCurrentIndex(index)

    def set_db(self):
        if self.connection:
            self.midvsettingsdialogdock.ms.settingsdict['database'] = common_utils.anything_to_string_representation({'postgis': {'connection': self.connection}})
            self.midvsettingsdialogdock.ms.save_settings('database')
            self.midvsettingsdialogdock.load_plot_settings()
            warn_about_old_database()



