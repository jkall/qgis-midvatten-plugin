# -*- coding: utf-8 -*-
"""
/***************************************************************************
 midvsettings
                                 A part of the QGIS plugin Midvatten
 This part of the plugin lets the user select a SQLite Database, some tables and
 columns with data of interest
                             -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency  
import os.path
import qgis.utils
from functools import partial # only to get combobox signals to work
from ui.midvsettingsdialog_ui import Ui_Dialog
#import midvatten_utils as utils   #only during developing
import locale

class midvsettings(QDialog, Ui_Dialog): #THE CLASS IS ONLY TO DEAL WITH THE SETTINGS DIALOG
    def __init__(self, parent, s_dict):
        QDialog.__init__(self)  
        self.setupUi(self) # Required by Qt4 to initialize the UI

        self.setWindowTitle("Midvatten toolset settings") # Set the title for the dialog
        self.btnAccept = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnAccept.setEnabled( True )  # It  must be possbile to store empty values as well

        self.s_dict = s_dict    # The dictionary with all settings

        # Some  instance helper variables
        self.database = '' # a string is stored whenever len(s_dict['database']), see below
        self.dbTables = {} # the list is filled with databasetables whenever len(s_dict['database']), see below

        # The settings dialog is cleared, filled with relevant information and then the last settings are selected
        self.ListOfTables.clear()    
        self.ListOfTables_2.clear()    
        self.ListOfTables_3.clear()
        self.ListOfTables_WQUAL.clear()

        self.tabWidget.setCurrentIndex(int(self.s_dict['tabwidget']))# widget is opened with the last choosen tab #MacOSX fix1

        if len(self.s_dict['database'])>0:    # If there is a stored database, show it and fill the table-comboboxes with a list of all tables #MacOSX fix1
            self.database = self.s_dict['database'] #MacOSX fix1
            self.txtpath.setText(self.database)
            self.loadTablesFromDB()        # All ListOfTables are filled with relevant information

        if len(str(self.s_dict['tstable'])):#If there is a last selected tstable. #MacOSX fix1
            notfound=0 
            i=0
            while notfound==0:    # Loop until the last selected tstable is found
                self.ListOfTables.setCurrentIndex(i)
                if unicode(self.ListOfTables.currentText()) == unicode(self.s_dict['tstable']):#The index count stops when last selected table is found #MacOSX fix1
                    notfound=1
                    self.TSTableUpdated()        # Fill the given combobox with columns from the given table and also perform a sanity check of table
                    if len(self.s_dict['tscolumn']):#If there is a last selected tsColumn #MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:    # loop until the last selected tscolumn is found
                            self.ListOfColumns.setCurrentIndex(j)
                            if unicode(self.ListOfColumns.currentText()) == unicode(self.s_dict['tscolumn']):# index count stops when column found #MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns):
                                notfound2=1
                            j = j + 1
                elif i> len(self.ListOfTables):
                    notfound=1
                i = i + 1
            
        if self.s_dict['tsdotmarkers']==2:#If the TSPlot dot markers checkbox was checked last time it will be so now #MacOSX fix1
            self.checkBoxDataPoints.setChecked(True)
        else:
            self.checkBoxDataPoints.setChecked(False)
        if self.s_dict['tsstepplot']==2: #If the TSPlot stepplot checkbox was checked last time it will be so now #MacOSX fix1
            self.checkBoxStepPlot.setChecked(True)
        else:
            self.checkBoxStepPlot.setChecked(False)

        if len(self.s_dict['xytable']):#If there is a last selected xytable #MacOSX fix1
            notfound=0 
            i=0
            while notfound==0: #looping through ListOfTables_2 looking for last selected xytable
                self.ListOfTables_2.setCurrentIndex(i)
                if unicode(self.ListOfTables_2.currentText()) == unicode(self.s_dict['xytable']):    #when last selected xytable found, it is selected in list and a lot of columns is searced for #MacOSX fix1
                    notfound=1
                    self.XYTableUpdated()    # Fill the given combobox with columns from the given table and performs a test
                    if len(self.s_dict['xy_xcolumn']):# Show the last selected xyplot x-column in the ListOfColumns_2 #MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_2.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_2.currentText()) == unicode(self.s_dict['xy_xcolumn']):#MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_2):
                                notfound2=1
                            j = j + 1
                    if len(self.s_dict['xy_y1column']):# Show the last selected xyplot y1-column in the ListOfColumns_3 #MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_3.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_3.currentText()) == unicode(self.s_dict['xy_y1column']): #MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_3):
                                notfound2=1
                            j = j + 1
                    if len(self.s_dict['xy_y2column']):# Show the last selected xyplot y2-column in the ListOfColumns_4 #MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_4.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_4.currentText()) == unicode(self.s_dict['xy_y2column']):#MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_4):
                                notfound2=1
                            j = j + 1
                    if len(self.s_dict['xy_y3column']):#MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_5.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_5.currentText()) == unicode(self.s_dict['xy_y3column']):#MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_5):
                                notfound2=1
                            j = j + 1
                elif i> len(self.ListOfTables_2):
                    notfound=1
                i = i + 1

        if self.s_dict['xydotmarkers']==2:# If the XYPlot dot markers checkbox was checked last time it will be so now #MacOSX fix1
            self.checkBoxDataPoints_2.setChecked(True)
        else:
            self.checkBoxDataPoints_2.setChecked(False)
                
        if len(self.s_dict['stratigraphytable']):#If there is a last selected stratigraphytable, then it is selected again in the combobox ListOfTables #MacOSX fix1
            notfound=0 
            i=0
            while notfound==0:
                self.ListOfTables_3.setCurrentIndex(i)
                if unicode(self.ListOfTables_3.currentText()) == unicode(self.s_dict['stratigraphytable']):#MacOSX fix1
                    self.StratigraphyTableUpdated()        # Perform a sanity check of the table
                    notfound=1
                elif i> len(self.ListOfTables_3):
                    notfound=1
                i = i + 1
                
        if len(self.s_dict['wqualtable']):# If there is a last selected table, then it is selected again in the combobox ListOfTables #MacOSX fix1
            notfound=0 
            i=0
            while notfound==0:
                self.ListOfTables_WQUAL.setCurrentIndex(i)
                if unicode(self.ListOfTables_WQUAL.currentText()) == unicode(self.s_dict['wqualtable']):#MacOSX fix1
                    notfound=1
                    self.WQUALTableUpdated()    # Fill the given combobox with columns from the given table and performs a test
                    if len(self.s_dict['wqual_paramcolumn']):#MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_WQUALPARAM.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_WQUALPARAM.currentText()) == unicode(self.s_dict['wqual_paramcolumn']):#MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_WQUALPARAM):
                                notfound2=1
                            j = j + 1
                    if len(self.s_dict['wqual_valuecolumn']):# Show the last selected xyplot y2-column in the ListOfColumns_4 #MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_WQUALVALUE.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_WQUALVALUE.currentText()) == unicode(self.s_dict['wqual_valuecolumn']):#MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_WQUALVALUE):
                                notfound2=1
                            j = j + 1
                    if len(self.s_dict['wqual_unitcolumn']):#MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_WQUALUNIT.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_WQUALUNIT.currentText()) == unicode(self.s_dict['wqual_unitcolumn']):#MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_WQUALUNIT):
                                notfound2=1
                            j = j + 1
                    if len(self.s_dict['wqual_sortingcolumn']):# Show the last selected xyplot y3-column in the ListOfColumns_5 #MacOSX fix1
                        notfound2=0 
                        j=0
                        while notfound2==0:
                            self.ListOfColumns_WQUALSORTING.setCurrentIndex(j)
                            if unicode(self.ListOfColumns_WQUALSORTING.currentText()) == unicode(self.s_dict['wqual_sortingcolumn']): #MacOSX fix1
                                notfound2=1
                            elif j> len(self.ListOfColumns_WQUALSORTING):
                                notfound2=1
                            j = j + 1
                elif i> len(self.ListOfTables_WQUAL):
                    notfound=1
                i = i + 1
                
        # SIGNALS
        self.connect(self.btnSetDB, SIGNAL("clicked()"), self.selectFile)
        # whenever Time Series Table is changed, the column-combobox must be updated and TableCheck must be performed (function partial due to problems with currentindexChanged and Combobox)
        self.connect(self.ListOfTables, SIGNAL("currentIndexChanged(int)"), partial(self.TSTableUpdated)) 
         # whenever XY Table is changed, the columns-comboboxes must be updated (function partial due to problems with currentindexChanged and Combobox)
        self.connect(self.ListOfTables_2, SIGNAL("currentIndexChanged(int)"), partial(self.XYTableUpdated))  
        self.connect(self.ListOfTables_3, SIGNAL("activated(int)"), partial(self.StratigraphyTableUpdated))  
        self.connect(self.ListOfTables_WQUAL, SIGNAL("currentIndexChanged(int)"), partial(self.WQUALTableUpdated))  
        QObject.connect( self.buttonBox, SIGNAL( "accepted()" ), self.accept)
        QObject.connect( self.buttonBox, SIGNAL( "rejected()" ), self.reject)
    
    def selectFile(self):
        """ Open a dialog to locate the sqlite file and some more..."""        
        path = QFileDialog.getOpenFileName(None,str("Select database:"),"*.sqlite")
        if path: 
            self.database = path # To make possible cancel the FileDialog and continue loading a predefined db
        self.openDBFile()

    def openDBFile( self ):
        """ Open the SpatiaLite file to extract info about tables 
            and populate the table-QComboBoxes with all the tables"""
        if os.path.isfile( self.database ):
            self.txtpath.setText( self.database)
            self.ListOfTables.clear()
            self.ListOfTables_2.clear()
            self.ListOfTables_3.clear()
            self.ListOfTables_WQUAL.clear()
            self.ListOfColumns.clear()
            self.ListOfColumns_2.clear()
            self.ListOfColumns_3.clear()
            self.ListOfColumns_4.clear()
            self.ListOfColumns_5.clear()
            self.ListOfColumns_WQUALPARAM.clear()
            self.ListOfColumns_WQUALVALUE.clear()
            self.ListOfColumns_WQUALUNIT.clear()
            self.ListOfColumns_WQUALSORTING.clear()
            self.loadTablesFromDB()

            if len(unicode(self.s_dict['tstable'])):#If there is a last selected tstable. #MacOSX fix1
                notfound=0 
                i=0
                while notfound==0:    # Loop until the last selected tstable is found
                    self.ListOfTables.setCurrentIndex(i)
                    if unicode(self.ListOfTables.currentText()) == unicode(self.s_dict['tstable']):#The index count stops when last selected table is found #MacOSX fix1
                        notfound=1
                        self.TSTableUpdated()        # Fill the given combobox with columns from the given table and also perform a sanity check of table
                        if len(self.s_dict['tscolumn']):#If there is a last selected tsColumn #MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:    # loop until the last selected tscolumn is found
                                self.ListOfColumns.setCurrentIndex(j)
                                if unicode(self.ListOfColumns.currentText()) == unicode(self.s_dict['tscolumn']):# index count stops when column found #MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns):
                                    notfound2=1
                                j = j + 1
                    elif i> len(self.ListOfTables):
                        notfound=1
                    i = i + 1
                
            if self.s_dict['tsdotmarkers']==2:#If the TSPlot dot markers checkbox was checked last time it will be so now #MacOSX fix1
                self.checkBoxDataPoints.setChecked(True)
            else:
                self.checkBoxDataPoints.setChecked(False)
            if self.s_dict['tsstepplot']==2: #If the TSPlot stepplot checkbox was checked last time it will be so now #MacOSX fix1
                self.checkBoxStepPlot.setChecked(True)
            else:
                self.checkBoxStepPlot.setChecked(False)

            if len(self.s_dict['xytable']):#If there is a last selected xytable #MacOSX fix1
                notfound=0 
                i=0
                while notfound==0: #looping through ListOfTables_2 looking for last selected xytable
                    self.ListOfTables_2.setCurrentIndex(i)
                    if unicode(self.ListOfTables_2.currentText()) == unicode(self.s_dict['xytable']):    #when last selected xytable found, it is selected in list and a lot of columns is searced for #MacOSX fix1
                        notfound=1
                        self.XYTableUpdated()    # Fill the given combobox with columns from the given table and performs a test
                        if len(self.s_dict['xy_xcolumn']):# Show the last selected xyplot x-column in the ListOfColumns_2 #MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_2.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_2.currentText()) == unicode(self.s_dict['xy_xcolumn']):#MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_2):
                                    notfound2=1
                                j = j + 1
                        if len(self.s_dict['xy_y1column']):# Show the last selected xyplot y1-column in the ListOfColumns_3 #MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_3.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_3.currentText()) == unicode(self.s_dict['xy_y1column']): #MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_3):
                                    notfound2=1
                                j = j + 1
                        if len(self.s_dict['xy_y2column']):# Show the last selected xyplot y2-column in the ListOfColumns_4 #MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_4.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_4.currentText()) == unicode(self.s_dict['xy_y2column']):#MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_4):
                                    notfound2=1
                                j = j + 1
                        if len(self.s_dict['xy_y3column']):#MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_5.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_5.currentText()) == unicode(self.s_dict['xy_y3column']):#MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_5):
                                    notfound2=1
                                j = j + 1
                    elif i> len(self.ListOfTables_2):
                        notfound=1
                    i = i + 1

            if self.s_dict['xydotmarkers']==2:# If the XYPlot dot markers checkbox was checked last time it will be so now #MacOSX fix1
                self.checkBoxDataPoints_2.setChecked(True)
            else:
                self.checkBoxDataPoints_2.setChecked(False)
                
            if len(self.s_dict['stratigraphytable']):#If there is a last selected stratigraphytable, then it is selected again in the combobox ListOfTables #MacOSX fix1
                notfound=0 
                i=0
                while notfound==0:
                    self.ListOfTables_3.setCurrentIndex(i)
                    if unicode(self.ListOfTables_3.currentText()) == unicode(self.s_dict['stratigraphytable']):#MacOSX fix1
                        self.StratigraphyTableUpdated()        # Perform a sanity check of the table
                        notfound=1
                    elif i> len(self.ListOfTables_3):
                        notfound=1
                    i = i + 1
                
            if len(self.s_dict['wqualtable']):# If there is a last selected table, then it is selected again in the combobox ListOfTables #MacOSX fix1
                notfound=0 
                i=0
                while notfound==0:
                    self.ListOfTables_WQUAL.setCurrentIndex(i)
                    if unicode(self.ListOfTables_WQUAL.currentText()) == unicode(self.s_dict['wqualtable']):#MacOSX fix1
                        notfound=1
                        self.WQUALTableUpdated()    # Fill the given combobox with columns from the given table and performs a test
                        if len(self.s_dict['wqual_paramcolumn']):#MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_WQUALPARAM.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_WQUALPARAM.currentText()) == unicode(self.s_dict['wqual_paramcolumn']):#MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_WQUALPARAM):
                                    notfound2=1
                                j = j + 1
                        if len(self.s_dict['wqual_valuecolumn']):# Show the last selected xyplot y2-column in the ListOfColumns_4 #MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_WQUALVALUE.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_WQUALVALUE.currentText()) == unicode(self.s_dict['wqual_valuecolumn']):#MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_WQUALVALUE):
                                    notfound2=1
                                j = j + 1
                        if len(self.s_dict['wqual_unitcolumn']):#MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_WQUALUNIT.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_WQUALUNIT.currentText()) == unicode(self.s_dict['wqual_unitcolumn']):#MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_WQUALUNIT):
                                    notfound2=1
                                j = j + 1
                        if len(self.s_dict['wqual_sortingcolumn']):# Show the last selected xyplot y3-column in the ListOfColumns_5 #MacOSX fix1
                            notfound2=0 
                            j=0
                            while notfound2==0:
                                self.ListOfColumns_WQUALSORTING.setCurrentIndex(j)
                                if unicode(self.ListOfColumns_WQUALSORTING.currentText()) == unicode(self.s_dict['wqual_sortingcolumn']): #MacOSX fix1
                                    notfound2=1
                                elif j> len(self.ListOfColumns_WQUALSORTING):
                                    notfound2=1
                                j = j + 1
                    elif i> len(self.ListOfTables_WQUAL):
                        notfound=1
                    i = i + 1

    def loadTablesFromDB(self): # This method populates all table-comboboxes with the tables inside the database
        # Execute a query in SQLite to return all available tables (sql syntax excludes some of the predefined tables)
        # start with cleaning comboboxes before filling with new entries
        self.ListOfTables.clear()    
        self.ListOfTables_2.clear()    
        self.ListOfTables_3.clear()    
        self.ListOfTables_WQUAL.clear()    

        conn = sqlite.connect(self.database)#encoding cleanup
        cursor = conn.cursor()
        rs=cursor.execute(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name in('geom_cols_ref_sys','geometry_columns','geometry_columns_auth','spatial_ref_sys','spatialite_history','sqlite_sequence','sqlite_stat1','views_geometry_columns','virts_geometry_columns','geometry_columns_statistics','views_geometry_columns_statistics','virts_geometry_columns_statistics' ,'geometry_columns','spatialindex','SpatialIndex','geometry_columns_fields_infos','geometry_columns_time','sql_statements_log','vector_layers','vector_layers_auth','vector_layers_field_infos','vector_layers_statistics','views_geometry_columns_auth','views_geometry_columns_field_infos','geometry_columns_field_infos','virts_geometry_columns_auth','virts_geometry_columns_field_infos' )) ORDER BY tbl_name""" )  #SQL statement to get the relevant tables in the spatialite database
        #self.dbTables = {} 
        self.ListOfTables.addItem('')
        self.ListOfTables_2.addItem('')
        self.ListOfTables_3.addItem('')
        self.ListOfTables_WQUAL.addItem('')
        
        for row in cursor:
            #self.dbTables[ row[ 0 ] ] = row # Load the table info into the dictionary
        #if len( self.dbTables ):  # If there are any tables, load them all into the comboboxes
        #    self.ListOfTables.addItem('')
        #    self.ListOfTables_2.addItem('')
            self.ListOfTables.addItem(row[0])
            self.ListOfTables_2.addItem(row[0])
            self.ListOfTables_3.addItem(row[0])
            self.ListOfTables_WQUAL.addItem(row[0])
            #for tableName in self.dbTables:
            #    self.ListOfTables.addItem(tableName)
            #    self.ListOfTables_2.addItem(tableName)
        #else:
        #    QMessageBox.critical(None, "Warning", "The SQLite database \n do not contain any tables!")
        rs.close()
        conn.close()

    def ColumnsToComboBox(self, comboboxname='', table=None):
        getattr(self, comboboxname).clear()
        """This method fills comboboxes with columns for selected tool and table"""
        columns = self.LoadColumnsFromTable(table)    # Load all columns into a list 'columns'
        if len(columns)>0:    # Transfer information from list 'columns' to the combobox
            getattr(self, comboboxname).addItem('')
            for columnName in columns:
                getattr(self, comboboxname).addItem(columnName)  # getattr is to combine a function and a string to a combined function

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

    def TSTableUpdated(self):
        """This method is called whenever time series table is changed"""
        # First, update combobox with columns
        self.ColumnsToComboBox('ListOfColumns', self.ListOfTables.currentText())  # For some reason it is not possible to send currentText with the SIGNAL-trigger
        # Second, Make sure that columns obsid and date_time exists
        columns = self.LoadColumnsFromTable(self.ListOfTables.currentText())     # For some reason it is not possible to send currentText with the SIGNAL-trigger
        if ('obsid' in columns) and ('date_time' in columns):
            text = "<font color=green>Correct table, both obsid and date_time columns have been found.</font>"
        else:
            text = "<font color=red>Wrong table! obsid and/or date_time is missing.</font>"
        self.InfoTxtTSPlot.setText(text)

    def XYTableUpdated(self):
        """This method is called whenever xy table is changed"""
        # First, update comboboxes with columns
        self.XYColumnsToComboBox(self.ListOfTables_2.currentText())   # For some reason it is not possible to send currentText with the SIGNAL-trigger
        # Second, Make sure that column obsid exists
        columns = self.LoadColumnsFromTable(self.ListOfTables_2.currentText())     # For some reason it is not possible to send currentText with the SIGNAL-trigger
        if 'obsid' in columns:    
            text = "<font color=green>Correct table! obsid column is found.</font>"
        else:
            text = "<font color=red>Wrong table! obsid is missing.</font>"
        self.InfoTxtXYPlot.setText(text)

    def WQUALTableUpdated(self):
        """This method is called whenever water quality table is changed and fils comboboxes with columns for wqual report"""
        self.ListOfColumns_WQUALPARAM.clear()
        self.ListOfColumns_WQUALVALUE.clear()
        self.ListOfColumns_WQUALUNIT.clear()
        self.ListOfColumns_WQUALSORTING.clear()
        columns = self.LoadColumnsFromTable(self.ListOfTables_WQUAL.currentText())    # Load all columns into a list (dict?) 'columns'
        if len(columns):    # Transfer information from list 'columns' to the combobox
            self.ListOfColumns_WQUALPARAM.addItem('')
            self.ListOfColumns_WQUALVALUE.addItem('')
            self.ListOfColumns_WQUALUNIT.addItem('')
            self.ListOfColumns_WQUALSORTING.addItem('')
            for columnName in columns:
                self.ListOfColumns_WQUALPARAM.addItem(columnName)
                self.ListOfColumns_WQUALVALUE.addItem(columnName)
                self.ListOfColumns_WQUALUNIT.addItem(columnName)
                self.ListOfColumns_WQUALSORTING.addItem(columnName)

    def StratigraphyTableUpdated(self):
        """This method is called whenever stratigraphy table is changed"""
        # Make sure that columns obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, comment exists
        Needed_columns = ('comment', 'capacity', 'geology', 'geoshort', 'depthtop', 'depthbot', 'obsid', 'stratid')
        columns = self.LoadColumnsFromTable(self.ListOfTables_3.currentText())     # For some reason it is not possible to send currentText with the SIGNAL-trigger
        text = "<font color=green>Correct table! all the expected columns obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, comment have been found.</font>"
        for column in Needed_columns:
            if not column in columns:
                text = "<font color=red>Wrong table! Column " + str(column) + " is missing.</font>"
        self.InfoTxtStratigraphy.setText(text)
        
    def LoadColumnsFromTable(self, table=''):
        """ This method returns a list with all the columns in the table"""
        if len(table)>0 and len(self.database)>0:            # Should not be needed since the function never should be called without existing table...
            conn = sqlite.connect(self.database) #encoding cleanup
            curs = conn.cursor()
            sql = r"""SELECT * FROM '"""
            sql += str(table)
            sql += """'"""     
            rs = curs.execute(sql)  #Send the SQL statement to get the columns in the table            
            columns = {} 
            columns = [tuple[0] for tuple in curs.description]
            rs.close()
            conn.close()
        else:
            columns = {}
        return columns        # This method returns a list with all the columns in the table
