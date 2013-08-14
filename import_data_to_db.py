# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of data to the database. 
 
 This part is to a big extent based on QSpatialite plugin.
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
import PyQt4.QtCore
import PyQt4.QtGui

from qgis.core import *
from qgis.gui import *
import qgis.utils
import locale
import os
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import midvatten_utils as utils    
   

class midv_data_importer():  # this class is intended to be a multipurpose import class  BUT loggerdata probably needs specific importer or its own subfunction

    def obslines_import(self): 
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_obs_lines'
        self.status = 'False' #Changes to True if qgiscsv2sqlitetable succeeds
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #function name was earlier uploadQgisVectorLayer with args csvlayer and srid  
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==6:    #only  if correct number of columns
                """And then simply remove all empty records (i.e. where the column obsid '', ' ' or null)"""
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]))
                #Then check if any obsid already exist in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_lines') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if id in possibleobsids:
                            utils.pop_up_info("""An observation line with obsid=%s do already exist in table obs_lines!\n%s in the database will remain unchanged and the new observation line with same obsid will not be imported."""%(str(id[0]),str(id[0])),"Information")
                            self.status = 'False'
                            PyQt4.QtGui.QApplication.restoreOverrideCursor()
                            return 0 # return simply to stop this function
                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM obs_lines""") #------CHANGE HERE!!
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty observation lines \n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")#--- CHANGE HERE!!!!!!

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data! (You have several identical obs_id.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate obs_id.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")#--- CHANGE HERE!!!!!!
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        PyQt4.QtGui.QApplication.restoreOverrideCursor()
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO 'tablename'
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_lines'"""
                SRID = str(utils.sql_load_fr_db(sql)[0][0])# THIS IS DUE TO WKT-import of geometries below
    
                sqlpart1 = """INSERT OR IGNORE INTO "obs_lines" (obsid, name, place, type, source, geometry) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), ST_GeomFromText("%s",%s) from %s"""%(self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[0][1],SRID,self.temptableName)#PLEASE NOTE THE SRID!
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM obs_lines""") #general import fix
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s observation lines were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0:
                utils.pop_up_info("Import file must have exactly 6 columns!\nCheck your data and try again.", "Import Error")
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def obsp_import(self): # was earlier found in __init__ and cleanupimportedata functions of specific importer class
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_obs_points'
        self.status = 'False' #Changes to True if qgiscsv2sqlitetable succeeds
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #function name was earlier uploadQgisVectorLayer with args csvlayer and srid  
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==26:    #only  if correct number of columns
                """And then simply remove all empty records (i.e. where the column obsid '', ' ' or null)"""
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1]))
                #Then check if any obsid already exist in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if id in possibleobsids:
                            utils.pop_up_info("""An observation point with obsid=%s do already exist in table obs_points!\n%s in the database will remain unchanged and the new observation point with same obsid will not be imported."""%(str(id[0]),str(id[0])),"Information")
                            self.status = 'False'
                            PyQt4.QtGui.QApplication.restoreOverrideCursor()
                            return 0 # return simply to stop this function
                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""") #------CHANGE HERE!!
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty observation points \n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")#--- CHANGE HERE!!!!!!

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data! (You have several identical obs_id.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate obs_id.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")#--- CHANGE HERE!!!!!!
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        PyQt4.QtGui.QApplication.restoreOverrideCursor()
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO 'tablename'
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db 
                sqlpart1 = """INSERT OR IGNORE INTO "obs_points" (obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as integer), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1], self.columns[9][1], self.columns[10][1], self.columns[11][1], self.columns[12][1], self.columns[13][1], self.columns[14][1], self.columns[15][1], self.columns[16][1], self.columns[17][1], self.columns[18][1], self.columns[19][1], self.columns[20][1], self.columns[21][1], self.columns[22][1], self.columns[23][1], self.columns[24][1], self.columns[25][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""") #general import fix
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s observation points were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0:
                utils.pop_up_info("Import file must have exactly 26 columns!\nCheck your data and try again.", "Import Error")
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def seismics_import(self):#NOT READY AT ALL, JUST A COPY OF WFLOW
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_seismics'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==7:    #only  if correct number of columns
                #And then simply remove all empty records
                sql = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1])
                utils.sql_alter_db(sql)
                #Then check whether the obsid actually exists in obs_lines
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_lines') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_lines!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM seismic_data""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one interpreted data for the same obs line and length.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO seismic_Data
            if cleaningok == 1  and len(self.columns)==7: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "seismic_data" (obsid, length, east, north, ground, bedrock, gw_table) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM seismic_data""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==7):
                utils.pop_up_info("Import file must have exactly seven columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def strat_import(self): # was earlier found in __init__ and cleanupimportedata functions of specific importer class
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_stratigraphy'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==9:    #only  if correct number of columns
                """And then simply remove all empty records (i.e. where either of the columns obsid or stratid is '', ' ' or null)"""
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]))
                
                #Then check whether the obsid actually exists in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(Each pair of obsid+stratid must be unique!)\nDo you still want to import these data?\nAnswering yes will start, from top of the imported\nfile and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO stratigraphy
            if cleaningok == 1  and len(self.columns)==9: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "stratigraphy" (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==9):
                utils.pop_up_info("Import file must have exactly nine columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def vlf_import(self):#NOT READY AT ALL, JUST A COPY OF WFLOW
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_vlf_data'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==6:    #only  if correct number of columns
                #And then simply remove all empty records
                sql = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1])
                utils.sql_alter_db(sql)
                #Then check whether the obsid actually exists in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_lines') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_lines!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM vlf_data""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same length for the same profile.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO vlf_data
            if cleaningok == 1  and len(self.columns)==6: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "vlf_data" (obsid, length, east, north, real_comp, imag_comp) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM vlf_data""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s vlf data were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==6):
                utils.pop_up_info("Import file must have exactly six columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wflow_import(self):#please note the particular behaviour of adding additional flowtypes to table zz_flowtype
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_wflow'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==7:    #only  if correct number of columns
                #And then simply remove all empty records
                sql = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])
                utils.sql_alter_db(sql)
                utils.pop_up_info(sql)#DEBUG
                #Then check whether the obsid actually exists in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Then check for flowtypes and add those that are not present in db table zz_flowtype the obsid actually exists in obs_points
                FlTypesInDb = utils.sql_load_fr_db('select distinct type from zz_flowtype') 
                FlTypes2BImported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[2][1],self.temptableName))
                for tp in FlTypes2BImported:
                        if not tp in FlTypesInDb:
                            sql = """insert into "zz_flowtype" (type, explanation) VALUES ("%s", '');"""%str(tp[0])
                            utils.sql_alter_db(sql)

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_flow""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time for the same obsid.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO w_flow
            if cleaningok == 1  and len(self.columns)==7: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "w_flow" (obsid, instrumentid, flowtype, date_time, reading, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_flow""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==7):
                utils.pop_up_info("Import file must have exactly seven columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wlvl_import(self): # was earlier found in __init__ and cleanupimportedata functions of specific importer class
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_w_lvl'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==4:    #only  if correct number of columns
                #And then simply remove all empty records
                utils.sql_alter_db("""DELETE FROM "%s" where ("%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null) or (("%s"='' or "%s"=' ' or "%s" is null) and ("%s"='' or "%s"=' ' or "%s" is null))"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1]))
                
                #Then check whether the obsid actually exists in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time for the same obsid.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels
            if cleaningok == 1  and len(self.columns)==4: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                #utils.sql_alter_db("""INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) SELECT CAST(obsid as text), CAST(date_time as text), CAST(MEAS as double), CAST(comment as text) FROM %s"""%self.temptableName)     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==4):
                utils.pop_up_info("Import file must have exactly four columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wquallab_import(self): # was earlier found in __init__ and cleanupimportedata functions of specific importer class
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_w_qual'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==12:    #only  if correct number of columns
                #And then simply remove all empty records (i.e. where any of columns obsid, report, date_time, parameter or (reading_num and reading_txt) is '', ' ' or null)
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or ("%s" in ('', ' ') or "%s" is null) and ("%s" in ('', ' ') or "%s" is null)"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[2][1],self.columns[2][1],self.columns[5][1],self.columns[5][1],self.columns[7][1],self.columns[7][1],self.columns[8][1],self.columns[8][1],self.columns[9][1],self.columns[9][1]))
                
                #Then check whether the obsid actually exists in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[2][1],self.columns[7][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(Each pair of 'report' and 'parameter' is not unique.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate analyses.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels
            if cleaningok == 1  and len(self.columns)==12: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "w_qual_lab" (obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.columns[8][1],self.columns[9][1],self.columns[10][1],self.columns[11][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                #utils.sql_alter_db("""INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) SELECT CAST(obsid as text), CAST(date_time as text), CAST(MEAS as double), CAST(comment as text) FROM %s"""%self.temptableName)     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==12):
                utils.pop_up_info("Import file must have exactly 12 columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wqualfield_import(self): # was earlier found in __init__ and cleanupimportedata functions of specific importer class
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_w_qual_field'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            self.qgiscsv2sqlitetable()
            """perform some sanity checks of the imported data and removes duplicates and empty records"""
            #First load column names
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            if len(self.columns)==10:    #only  if correct number of columns
                #And then simply remove all empty records (i.e. where any of columns obsid, date_time or parameter is '', ' ' or null)
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[2][1],self.columns[2][1],self.columns[4][1],self.columns[4][1]))
                
                #Then check whether the obsid actually exists in obs_points
                possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
                obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))
                for id in obsidstobeimported:
                        if not id in possibleobsids:
                            utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                            self.status = 'False'
                            return 0 # return simply to stop this function

                #Some statistics
                self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")
                self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[2][1],self.columns[7][1],self.temptableName))
                self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
                utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(Each set of 'obsid', 'date_time' and 'parameter' is not unique.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                    #utils.pop_up_info(duplicatequestion.result)    #debug
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        return 0   # return simply to stop this function
                cleaningok = 1
            else:
                cleaningok = 0
            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels
            if cleaningok == 1  and len(self.columns)==10: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "w_qual_field" (obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.columns[8][1],self.columns[9][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0 and not(len(self.columns)==10):
                utils.pop_up_info("Import file must have exactly 10 columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def selectcsv(self): # general importer - ready, no fix needed
        """Select the csv file, user must also tell what charset to use"""
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            if not self.csvpath or self.csvpath=='': # SIP API UPDATE 2.0
                return
            else:
                csvlayer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not csvlayer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                csvlayer.setProviderEncoding(str(charsetchoosen[0]))                 #Set the Layer Encoding
                return csvlayer

    def qgiscsv2sqlitetable(self): # general importer - NOTE! csvlayer and srid no longer sent as args! Comment out one debugging-line later
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'."""
        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.temptableName): #if so, propose to rename the temporary import-table
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your w_qual_lab table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.temptableName='%s_2'%self.temptableName
                else:
                    return None
                  
        #Get all fields with corresponding types for the csv-csvlayer in qgis
        fields=[]
        fieldsNames=[]
        provider=self.csvlayer.dataProvider()
        for name in provider.fields(): 
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names in temporary table in sqlite
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            #print "field " + str(fldName) + " has type " + str(fldTypeName) # debugging
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not .csvt file is defined beside the imported file.
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool,PyQt4.QtCore.QVariant.Int,QtCore.QVariant.LongLong,PyQt4.QtCore.QVariant.UInt,PyQt4.QtCore.QVariant.ULongLong): # field type is integer
                fldType='integer'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is double
                fldType='real'
            else: # if field type is not recognized by qgis
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())
        
        #Create the import-table in DB
        fields=','.join(fields) 
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.temptableName, fields)) # Create a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis csvlayer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        for feature in self.csvlayer.getFeatures(): 
            values_perso=[]
            for attr in feature.attributes(): 
                values_perso.append(str(attr)) 
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) 
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()


""" Note, thes class below is a quickfix and should be incorporated into the a multi-import class above instead. As soon as there is time for code cleanup..."""
                     
class wlvlloggimportclass():

    def __init__(self):
        self.csvpath = ''
        self.temptableName = 'temporary_logg_lvl'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.columns=[]

        # Find obsid for the selected object
        self.obsid = utils.getselectedobjectnames()     #A list of length 1! To get the acutal ID, call self.obsid[0]
        # Import the csv file as a ogr csvlayer
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            # upload the ogr csvlayer to splite db
            self.uploadLoggerdataToSplite()    # Calling similar function as uploadQgisVectorLayer
            # perform some cleaning of imported data
            cleaningok = self.cleanuploggerdata() # returns 1 if cleaning went well

            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels_logger
            if cleaningok == 1: # If cleaning was OK, then perform the import
                self.goalcolumns = utils.sql_load_fr_db("""PRAGMA table_info(w_levels_logger)""")
                if len(self.columns) == 5: #No conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[3][1],self.columns[0][1],self.columns[1][1],self.columns[2][1])     
                    sqlpart3 = """ FROM %s"""%(self.temptableName)    
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    utils.sql_alter_db(sql)     
                    #utils.pop_up_info(sql, "debug") #debug                
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                elif len(self.columns) ==6: #Including conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1],self.goalcolumns[4][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[4][1],self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1])     
                    sqlpart3 = """ FROM %s"""%(self.temptableName)    
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    utils.sql_alter_db(sql)     
                    #utils.pop_up_info(sql, "debug") #debug
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
                else:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were imported."""%(self.RecordsAfter[0][0] - self.RecordsBefore[0][0]))
            elif cleaningok == 0 and not(len(self.columns)==5 or len(self.columns)==6):
                utils.pop_up_info("Import file must have exactly three columns!\n(Or four if conductivity is also measured.)", "Import Error")
                self.status = 'False'
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed

            
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming

        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\nutf-8, cp1250, cp1252 or iso-8859-15.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            #if self.csvpath.isEmpty() or self.csvpath=='':
            if not self.csvpath or self.csvpath=='': # SIP API UPDATE 2.0
                return
            else:
                csvlayer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not csvlayer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                csvlayer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayer(csvlayer)      # only for debugging
                return csvlayer

        
    def uploadLoggerdataToSplite(self):
        self.status = 'False'
        #Verify if temptableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.temptableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_levels table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.temptableName='%s_2'%self.temptableName
                else:
                    return None
                  
        #Get fields in loaded csv-file with corresponding types
        provider=self.csvlayer.dataProvider()       # The loaded csv-file
        fields=[]
        fieldsNames=[]
        #for id,name in provider.fields().iteritems():
        for name in provider.fields(): # SIP API UPDATE 2.0
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool,PyQt4.QtCore.QVariant.Int,QtCore.QVariant.LongLong,PyQt4.QtCore.QVariant.UInt,PyQt4.QtCore.QVariant.ULongLong): # field type is integer
                fldType='integer'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is double
                fldType='real'
            else: # field type is not recognized by SQLITE
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())
        
        #select attributes to import :
        #allAttrs = provider.attributeIndexes() # REMOVED DUE TO SIP API UPDATE 2.0
        #provider.select(allAttrs) # REMOVED DUE TO SIP API UPDATE 2.0
        
        #Create new table in BD
        fields=','.join(fields) 
        fields = ''.join([x for x in fields if ord(x) < 128])    # Just get rid of all non-ascii, the column names are not important anyway
        sql = """CREATE table "%s" (%s)"""%(self.temptableName, fields)
        #utils.pop_up_info(sql)      # debugging
        utils.sql_alter_db(sql) #NO PKUID, Number of fields exactly the same as imported csv file
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
        # Retreive every feature 
        #feat = QgsFeature()  # REMOVED DUE TO SIP API UPDATE 2.0
        for feature in self.csvlayer.getFeatures(): #SIP API UDPDATE 2.0
        #while provider.nextFeature(feat): # REMOVED DUE TO SIP API UPDATE 2.0
            #attrs = feat.attributeMap()  # REMOVED DUE TO SIP API UPDATE 2.0
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for attr in feature.attributes(): #SIP API UDPDATE 2.0
            #for (k,attr) in attrs.iteritems():  # REMOVED DUE TO SIP API UPDATE 2.0
                values_perso.append(str(attr)) # SIP API UPDATE 2.0
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USET utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.execute("PRAGMA foreign_keys = OFF")
        curs.close()
        conn.close()

    def cleanuploggerdata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
        if len(self.columns)==3 or len(self.columns)==4:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null"""%(self.temptableName,column[1],column[1]))
            #utils.pop_up_info(str(self.columns[0][1])) # Big Debugski
            #THE METHOD ABOVE NEEDS REVISON

            #Fix date_time format from "yyyy/mm/dd hh:mm:ss" to "yyyy-mm-dd hh:mm:ss"
            utils.sql_alter_db("""UPDATE "%s" SET "%s" = REPLACE("%s",'/','-')"""%(self.temptableName,str(self.columns[0][1]),str(self.columns[0][1])))
            # Add obsid column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN obsid text"""%self.temptableName)
            utils.sql_alter_db("""UPDATE "%s" SET obsid = "%s" """%(self.temptableName,self.obsid[0]))
            # Add level_masl column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double"""%self.temptableName)
            utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """%(self.temptableName,self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )
            
            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")
            #utils.pop_up_info("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName)) #debug
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0
