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
from pyspatialite import dbapi2 as sqlite 
import midvatten_utils as utils    
   
""" Note, these classes are quickfixes and they should be replaced by a multi-import class instead. As soon as there is time for code cleanup..."""
class obspointimportclass():  

    def __init__(self):
        self.csvpath = ''
        self.tableName = 'temporary_obs_points'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.layer = self.selectcsv()
        if self.layer:
            self.uploadQgisVectorLayer(self.layer, 0)   
            cleaningok = self.cleanupimporteddata() 
            #utils.pop_up_info("return from cleaning is " + str(cleaningok)) # debug
            
            #HERE IS WHERE DATA IS TRANSFERRED TO w_qual_lab
            if cleaningok == 1: # If cleaning was OK, then perform the import  # CHECK THIS ROW AND ONWARDS
                sqlpart1 = """INSERT OR IGNORE INTO "obs_points" (obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as integer), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1], self.columns[9][1], self.columns[10][1], self.columns[11][1], self.columns[12][1], self.columns[13][1], self.columns[14][1], self.columns[15][1], self.columns[16][1], self.columns[17][1], self.columns[18][1], self.columns[19][1], self.columns[20][1], self.columns[21][1], self.columns[22][1], self.columns[23][1], self.columns[24][1], self.columns[25][1],self.tableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s observation points were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0:
                utils.pop_up_info("Import file must have exactly 26 columns!\nCheck your data and try again.", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.tableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            if self.csvpath.isEmpty() or self.csvpath=='':
                return
            else:
                layer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not layer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                layer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayer(layer)      # only for debugging
                return layer

    def uploadQgisVectorLayer(self, layer, srid=None):
        """Upload layer (QgsMapLayer) into current DB, in tableName (string) with desired SRID (default layer srid if None). Return True if operation succesfull or false in all other cases"""
        self.status = 'False'
        #Verify if tableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.tableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_qual_lab table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.tableName,self.tableName,self.tableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.tableName='%s_2'%self.tableName
                else:
                    return None
                  
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        for id,name in provider.fields().iteritems():
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names in temporary table in sqlite
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not .csvt file is defined beside the imported file.
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
        
        #select attributes to import 
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        
        #Create new table in DB
        fields=','.join(fields) 
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.tableName, fields)) # At this moment, creating a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis layer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrs = feat.attributeMap()
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for (k,attr) in attrs.iteritems():
                values_perso.append(attr.toString())
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #curs.execute("""INSERT INTO "%s" VALUES (%s,%s)"""%(self.tableName,'Null',','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #with PKUID
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.tableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanupimporteddata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
        if len(self.columns)==26:    #only  if correct number of columns
            """And then simply remove all empty records (i.e. where the column obsid '', ' ' or null)"""
            sql = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null"""%(self.tableName,self.columns[0][1],self.columns[0][1])
            #utils.pop_up_info(sql) #DEBUGGING
            utils.sql_alter_db(sql)
            
            #Then check whether the obsid actually exists in obs_points
            possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
            obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.tableName))
            for id in obsidstobeimported:
                    if id in possibleobsids:
                        utils.pop_up_info("""An observation point with obsid=%s do already exist in table obs_points!\n%s in the database will remain unchanged and the new observation point with same obsid will not be imported."""%(str(id[0]),str(id[0])),"Information")

            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""")
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.tableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.tableName)
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty observation points \n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data! (You have several identical obs_id.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate obs_id.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0

class stratigraphyimportclass():  

    def __init__(self):
        self.csvpath = ''
        self.tableName = 'temporary_stratigraphy'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.layer = self.selectcsv()
        if self.layer:
            self.uploadQgisVectorLayer(self.layer, 0)   
            cleaningok = self.cleanupimporteddata() 
            #utils.pop_up_info("return from cleaning is " + str(cleaningok)) # debug
            
            if cleaningok == 1: # If cleaning was OK, then perform the import  # CHECK THIS ROW AND ONWARDS
                sqlpart1 = """INSERT OR IGNORE INTO "stratigraphy" (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1],self.tableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s stratigraphy layers were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0:
                utils.pop_up_info("Import file must have exactly 9 columns!\nCheck your data and try again.", "Import Error")
                self.status = 'False'
            elif cleaningok == 2:
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.tableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            if self.csvpath.isEmpty() or self.csvpath=='':
                return
            else:
                layer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not layer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                layer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayer(layer)      # only for debugging
                return layer

    def uploadQgisVectorLayer(self, layer, srid=None):
        """Upload layer (QgsMapLayer) into current DB, in tableName (string) with desired SRID (default layer srid if None). Return True if operation succesfull or false in all other cases"""
        self.status = 'False'
        #Verify if tableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.tableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_qual_lab table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.tableName,self.tableName,self.tableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.tableName='%s_2'%self.tableName
                else:
                    return None
                  
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        for id,name in provider.fields().iteritems():
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names in temporary table in sqlite
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not .csvt file is defined beside the imported file.
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
        
        #select attributes to import 
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        
        #Create new table in DB
        fields=','.join(fields) 
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.tableName, fields)) # At this moment, creating a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis layer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrs = feat.attributeMap()
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for (k,attr) in attrs.iteritems():
                values_perso.append(attr.toString())
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #curs.execute("""INSERT INTO "%s" VALUES (%s,%s)"""%(self.tableName,'Null',','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #with PKUID
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.tableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanupimporteddata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
        if len(self.columns)==9:    #only  if correct number of columns
            """And then simply remove all empty records (i.e. where the column obsid '', ' ' or null)"""
            sql = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.tableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1])
            #utils.pop_up_info(sql) #DEBUGGING
            utils.sql_alter_db(sql)
            
            #Then check whether the obsid actually exists in obs_points
            possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
            obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.tableName))
            for id in obsidstobeimported:
                    if not id in possibleobsids:
                        utils.pop_up_info("""The obsid=%s do not exist in obs_points! Import will abort."""%str(id[0]),"Error")
                        return 2

            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.tableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.tableName)
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(Each pair of obsid+stratid must be unique!)\nDo you still want to import these data?\nAnswering yes will start, from top of the imported\nfile and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 2    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0
            
class wlvlimportclass():

    def __init__(self):
        self.csvpath = ''
        self.tableName = 'temporary_w_lvl'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.layer = self.selectcsv()
        if self.layer:
            self.uploadQgisVectorLayer(self.layer, 0)
            cleaningok = self.cleanupimporteddata()
            #utils.pop_up_info("return from cleaning is " + str(cleaningok)) # debug
            
            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels
            if cleaningok == 1  and len(self.columns)==4: # If cleaning was OK, then perform the import
                sqlpart1 = """INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.tableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                #utils.sql_alter_db("""INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) SELECT CAST(obsid as text), CAST(date_time as text), CAST(MEAS as double), CAST(comment as text) FROM %s"""%self.tableName)     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
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
            utils.sql_alter_db("DROP table %s"%self.tableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\nutf-8, cp1250, cp1252 or iso-8859-15.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            if self.csvpath.isEmpty() or self.csvpath=='':
                return
            else:
                layer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not layer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                layer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayer(layer)      # only for debugging
                return layer

    def uploadQgisVectorLayer(self, layer, srid=None):
        """Upload layer (QgsMapLayer) into current DB, in tableName (string) with desired SRID (default layer srid if None). Return True if operation succesfull or false in all other cases"""
        self.status = 'False'
        #Verify if tableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.tableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_levels table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.tableName,self.tableName,self.tableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.tableName='%s_2'%self.tableName
                else:
                    return None
                  
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        for id,name in provider.fields().iteritems():
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
        
        #select attributes to import (remove Pkuid if exists):
        allAttrs = provider.attributeIndexes()
        fldDesc = provider.fieldNameIndex("pkuid")
        if fldDesc != -1:
            print "Pkuid exists and will not be used for import!"
            del allAttrs[fldDesc] #remove pkuid Field
            del fields[fldDesc] #remove pkuid Field
        provider.select(allAttrs)
        
        #Create new table in DB
        fields=','.join(fields) 
        #if len(fields)>0:   # ONLY WHEN PKUID FIRST
        #    fields=', %s'%fields    # ONLY WHEN PKUID FIRST
        #utils.pop_up_info("""CREATE table "%s" (%s)"""%(self.tableName, fields))   #DEBUGGING
        #utils.sql_alter_db("""CREATE table "%s" ( PKUID integer PRIMARY KEY AUTOINCREMENT %s )"""%(self.tableName, fields)) #ONLY WHEN PKUID FIRST
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.tableName, fields)) #NO PKUID
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrs = feat.attributeMap()
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for (k,attr) in attrs.iteritems():
                values_perso.append(attr.toString())
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USET utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #curs.execute("""INSERT INTO "%s" VALUES (%s,%s)"""%(self.tableName,'Null',','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #with PKUID
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.tableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanupimporteddata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
        if len(self.columns)==4:    #only  if correct number of columns
            #And then simply remove all empty records
            utils.sql_alter_db("""DELETE FROM "%s" where ("%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null) or (("%s"='' or "%s"=' ' or "%s" is null) and ("%s"='' or "%s"=' ' or "%s" is null))"""%(self.tableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1]))
            #THE METHOD ABOVE NEEDS REVISON
            
            #Then check whether the obsid actually exists in obs_points
            possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
            obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.tableName))
            for id in obsidstobeimported:
                    if not id in possibleobsids:
                        utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                        return 0

            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels""")
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.tableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.tableName)
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time for the same obsid.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0
            
class wlvlloggimportclass():

    def __init__(self):
        self.csvpath = ''
        self.tableName = 'temporary_logg_lvl'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.columns=[]

        # Find obsid for the selected object
        self.obsid = utils.getselectedobjectnames()     #A list of length 1! To get the acutal ID, call self.obsid[0]
        # Import the csv file as a ogr layer
        self.layer = self.selectcsv()
        if self.layer:
            # upload the ogr layer to splite db
            self.uploadLoggerdataToSplite()    # Calling similar function as uploadQgisVectorLayer
            # perform some cleaning of imported data
            cleaningok = self.cleanuploggerdata() # returns 1 if cleaning went well

            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels
            if cleaningok == 1: # If cleaning was OK, then perform the import
                self.goalcolumns = utils.sql_load_fr_db("""PRAGMA table_info(w_levels_logger)""")
                if len(self.columns) == 5: #No conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[3][1],self.columns[0][1],self.columns[1][1],self.columns[2][1])     
                    sqlpart3 = """ FROM %s"""%(self.tableName)    
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    utils.sql_alter_db(sql)     
                    #utils.pop_up_info(sql, "debug") #debug                
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                elif len(self.columns) ==6: #Including conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1],self.goalcolumns[4][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[4][1],self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1])     
                    sqlpart3 = """ FROM %s"""%(self.tableName)    
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

            
            utils.sql_alter_db("DROP table %s"%self.tableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming

        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\nutf-8, cp1250, cp1252 or iso-8859-15.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            if self.csvpath.isEmpty() or self.csvpath=='':
                return
            else:
                layer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not layer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                layer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayer(layer)      # only for debugging
                return layer

        
    def uploadLoggerdataToSplite(self):
        self.status = 'False'
        #Verify if tableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.tableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_levels table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.tableName,self.tableName,self.tableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.tableName='%s_2'%self.tableName
                else:
                    return None
                  
        #Get fields in loaded csv-file with corresponding types
        provider=self.layer.dataProvider()       # The loaded csv-file
        fields=[]
        fieldsNames=[]
        for id,name in provider.fields().iteritems():
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
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        
        #Create new table in BD
        fields=','.join(fields) 
        fields = ''.join([x for x in fields if ord(x) < 128])    # Just get rid of all non-ascii, the column names are not important anyway
        sql = """CREATE table "%s" (%s)"""%(self.tableName, fields)
        #utils.pop_up_info(sql)      # debugging
        utils.sql_alter_db(sql) #NO PKUID, Number of fields exactly the same as imported csv file
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrs = feat.attributeMap()
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for (k,attr) in attrs.iteritems():
                values_perso.append(attr.toString())
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USET utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.tableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
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
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
        if len(self.columns)==3 or len(self.columns)==4:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null"""%(self.tableName,column[1],column[1]))
            #utils.pop_up_info(str(self.columns[0][1])) # Big Debugski
            #THE METHOD ABOVE NEEDS REVISON

            #Fix date_time format from "yyyy/mm/dd hh:mm:ss" to "yyyy-mm-dd hh:mm:ss"
            utils.sql_alter_db("""UPDATE "%s" SET "%s" = REPLACE("%s",'/','-')"""%(self.tableName,str(self.columns[0][1]),str(self.columns[0][1])))
            # Add obsid column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN obsid text"""%self.tableName)
            utils.sql_alter_db("""UPDATE "%s" SET obsid = "%s" """%(self.tableName,self.obsid[0]))
            # Add level_masl column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double"""%self.tableName)
            utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """%(self.tableName,self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
            
            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")
            #utils.pop_up_info("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.tableName)) #debug
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.tableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.tableName)
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

class wqualimportclass():  

    def __init__(self):
        self.csvpath = ''
        self.tableName = 'temporary_w_qual'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.layer = self.selectcsv()
        if self.layer:
            self.uploadQgisVectorLayer(self.layer, 0)   
            cleaningok = self.cleanupimporteddata() 
            #utils.pop_up_info("return from cleaning is " + str(cleaningok)) # debug
            
            #HERE IS WHERE DATA IS TRANSFERRED TO w_qual_lab
            if cleaningok == 1: # If cleaning was OK, then perform the import  # CHECK THIS ROW AND ONWARDS
                sqlpart1 = """INSERT OR IGNORE INTO "w_qual_lab" (obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.columns[8][1],self.columns[9][1],self.columns[10][1],self.columns[11][1],self.tableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s analyses were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0:
                utils.pop_up_info("Import file must have exactly 12 columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.tableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            if self.csvpath.isEmpty() or self.csvpath=='':
                return
            else:
                layer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not layer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                layer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayers([layer])      # only for debugging
                return layer

    def uploadQgisVectorLayer(self, layer, srid=None):
        """Upload layer (QgsMapLayer) into current DB, in tableName (string) with desired SRID (default layer srid if None). Return True if operation succesfull or false in all other cases"""
        self.status = 'False'
        #Verify if tableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.tableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_qual_lab table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.tableName,self.tableName,self.tableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.tableName='%s_2'%self.tableName
                else:
                    return None
                  
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        for id,name in provider.fields().iteritems():
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names in temporary table in sqlite
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not .csvt file is defined beside the imported file.
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
        
        #select attributes to import 
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        
        #Create new table in DB
        fields=','.join(fields) 
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.tableName, fields)) # At this moment, creating a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis layer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrs = feat.attributeMap()
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for (k,attr) in attrs.iteritems():
                values_perso.append(attr.toString())
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #curs.execute("""INSERT INTO "%s" VALUES (%s,%s)"""%(self.tableName,'Null',','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #with PKUID
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.tableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanupimporteddata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
        if len(self.columns)==12:    #only  if correct number of columns
            """And then simply remove all empty records (i.e. where any of columns obsid, report, date_time, parameter or (reading_num and reading_txt) is '', ' ' or null)"""
            sql = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or ("%s" in ('', ' ') or "%s" is null) and ("%s" in ('', ' ') or "%s" is null)"""%(self.tableName,self.columns[0][1],self.columns[0][1],self.columns[2][1],self.columns[2][1],self.columns[5][1],self.columns[5][1],self.columns[7][1],self.columns[7][1],self.columns[8][1],self.columns[8][1],self.columns[9][1],self.columns[9][1])
            #utils.pop_up_info(sql) #DEBUGGING
            utils.sql_alter_db(sql)
            
            #Then check whether the obsid actually exists in obs_points
            possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
            obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.tableName))
            for id in obsidstobeimported:
                    if not id in possibleobsids:
                        utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                        return 0

            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[2][1],self.columns[7][1],self.tableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.tableName)
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(Each pair of 'report' and 'parameter' is not unique.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate analyses.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0

class wqualfieldimportclass():  

    def __init__(self):
        self.csvpath = ''
        self.tableName = 'temporary_w_qual_field'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.layer = self.selectcsv()
        if self.layer:
            self.uploadQgisVectorLayer(self.layer, 0)   
            cleaningok = self.cleanupimporteddata() 
            #utils.pop_up_info("return from cleaning is " + str(cleaningok)) # debug
            
            #HERE IS WHERE DATA IS TRANSFERRED TO w_qual_field
            if cleaningok == 1: # If cleaning was OK, then perform the import  # CHECK THIS ROW AND ONWARDS
                sqlpart1 = """INSERT OR IGNORE INTO "w_qual_field" (obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.columns[8][1],self.columns[9][1],self.tableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
            elif cleaningok == 0:
                utils.pop_up_info("Import file must have exactly 10 columns!\n(Perhaps you had commas in the comment field?)", "Import Error")
                self.status = 'False'
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.tableName) # finally drop the temporary table
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + locale.getdefaultlocale()[1] + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            #utils.pop_up_info(self.csvpath) #debugging
            if self.csvpath.isEmpty() or self.csvpath=='':
                return
            else:
                layer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not layer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                layer.setProviderEncoding(str(charsetchoosen[0]))
                #utils.pop_up_info(str(charsetchoosen[0]))      # only for debugging
                #QgsMapLayerRegistry.instance().addMapLayer(layer)      # only for debugging
                return layer

    def uploadQgisVectorLayer(self, layer, srid=None):
        """Upload layer (QgsMapLayer) into current DB, in tableName (string) with desired SRID (default layer srid if None). Return True if operation succesfull or false in all other cases"""
        self.status = 'False'
        #Verify if tableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.tableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_qual_lab table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.tableName,self.tableName,self.tableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.tableName='%s_2'%self.tableName
                else:
                    return None
                  
        #Get data charset
        provider=layer.dataProvider()
        #charset=provider.encoding()
    
        #Get fields with corresponding types
        fields=[]
        fieldsNames=[]
        for id,name in provider.fields().iteritems():
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names in temporary table in sqlite
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not .csvt file is defined beside the imported file.
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
        
        #select attributes to import 
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        
        #Create new table in DB
        fields=','.join(fields) 
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.tableName, fields)) # At this moment, creating a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis layer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrs = feat.attributeMap()
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for (k,attr) in attrs.iteritems():
                values_perso.append(attr.toString())
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #curs.execute("""INSERT INTO "%s" VALUES (%s,%s)"""%(self.tableName,'Null',','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #with PKUID
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.tableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanupimporteddata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.tableName )
        if len(self.columns)==10:    #only  if correct number of columns
            """And then simply remove all empty records (i.e. where any of columns obsid, date_time or parameter is '', ' ' or null)"""
            sql = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.tableName,self.columns[0][1],self.columns[0][1],self.columns[2][1],self.columns[2][1],self.columns[4][1],self.columns[4][1])
            utils.pop_up_info(sql) #DEBUGGING
            utils.sql_alter_db(sql)
            #THE METHOD ABOVE NEEDS REVISON
            
            #Then check whether the obsid actually exists in obs_points
            possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points') 
            obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.tableName))
            for id in obsidstobeimported:
                    if not id in possibleobsids:
                        utils.pop_up_info("""The obsid=%s do not exist in obs_points!"""%str(id[0]),"Error")
                        return 0

            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[2][1],self.columns[4][1],self.tableName))
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.tableName)
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(Each set of 'obsid', 'date_time' and 'parameter' is not unique.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0
                        
