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
import io
from datetime import datetime
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import midvatten_utils as utils
from date_utils import find_date_format, datestring_to_date

class midv_data_importer():  # this class is intended to be a multipurpose import class  BUT loggerdata probably needs specific importer or its own subfunction

    def __init__(self):
        self.columns = 0
        self.status= 'False'
        self.recsbefore = 0
        self.recsafter = 0
        self.recstoimport = 0
        self.recsinfile = 0
        self.temptablename = ''
        self.charsetchoosen = ('','')
        
    def obslines_import(self):
        self.prepare_import('temporary_obs_lines')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            ConnectionOK, self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]) #first two cols are expected to be WKT geometry and obsid
            cleaningok = self.SingleFieldDuplicates(6,'obs_lines',sqlremove,1) # This is where duplicates are removed  LAST ARGUMENT IS COLUMN FOR ID
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_lines'"""
                SRID = str((utils.sql_load_fr_db(sql)[1])[0][0])# THIS IS DUE TO WKT-import of geometries below
                sqlpart1 = """INSERT OR IGNORE INTO "obs_lines" (obsid, name, place, type, source, geometry) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), ST_GeomFromText("%s",%s) from %s"""%(self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[0][1],SRID,self.temptableName)#PLEASE NOTE THE SRID!
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM obs_lines""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def obsp_import(self): 
        self.prepare_import('temporary_obs_points')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = (utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName)[1])#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1]) #CHANGE HERE!!!
            cleaningok = self.SingleFieldDuplicates(26,'obs_points',sqlremove,0) # This is where duplicates are removed  LAST ARGUMENT IS COLUMN FOR ID 
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
                sqlpart1 = """INSERT OR IGNORE INTO "obs_points" (obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as integer), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1], self.columns[9][1], self.columns[10][1], self.columns[11][1], self.columns[12][1], self.columns[13][1], self.columns[14][1], self.columns[15][1], self.columns[16][1], self.columns[17][1], self.columns[18][1], self.columns[19][1], self.columns[20][1], self.columns[21][1], self.columns[22][1], self.columns[23][1], self.columns[24][1], self.columns[25][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def seismics_import(self):
        self.prepare_import('temporary_seismics')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1]) #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) # To select distinct data posts from the import table
            cleaningok = self.MultipleFieldDuplicates(6,'seismic_data',sqlremove,'obs_lines',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "seismic_data" (obsid, length, ground, bedrock, gw_table, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM seismic_data""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def strat_import(self):
        self.prepare_import('temporary_stratigraphy')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]) #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(9,'stratigraphy',sqlremove,'obs_points',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "stratigraphy" (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def vlf_import(self):
        self.prepare_import('temporary_vlf_data')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = (utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1])#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(5,'vlf_data',sqlremove,'obs_lines',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "vlf_data" (obsid, length, real_comp, imag_comp, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM vlf_data""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wflow_import(self):
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        self.wflow_import_from_csvlayer()

    def wflow_import_from_csvlayer(self): #please note the particular behaviour of adding additional flowtypes to table zz_flowtype
        """
        self.csvlayer must contain columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment"
        :return:
        """
        self.prepare_import('temporary_wflow')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(7,'w_flow',sqlremove,'obs_points',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then fix zz_flowtype and then copy data from the temporary table to the original table in the db
                #check for flowtypes and add those that are not present in db table zz_flowtype the obsid actually exists in obs_points
                FlTypesInDb = utils.sql_load_fr_db('select distinct type from zz_flowtype')[1] 
                FlTypes2BImported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[2][1],self.temptableName))[1]
                for tp in FlTypes2BImported:
                        if not tp in FlTypesInDb:
                            sql = """insert into "zz_flowtype" (type, explanation) VALUES ("%s", '');"""%str(tp[0])
                            utils.sql_alter_db(sql)
            
                sqlpart1 = """INSERT OR IGNORE INTO "w_flow" (obsid, instrumentid, flowtype, date_time, reading, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_flow""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def meteo_import(self): #please note the particular behaviour of adding additional flowtypes to table zz_meteoparam
        self.prepare_import('temporary_meteo')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(8,'meteo',sqlremove,'obs_points',sqlNoOfdistinct)#
            if cleaningok == 1: # If cleaning was OK, then fix zz_meteoparam and then copy data from the temporary table to the original table in the db
                #check for parameters and add those that are not present in db table zz_meteoparam
                FlTypesInDb = utils.sql_load_fr_db('select distinct parameter from zz_meteoparam')[1] 
                FlTypes2BImported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[2][1],self.temptableName))[1]
                for tp in FlTypes2BImported:
                        if not tp in FlTypesInDb:
                            sql = """insert into "zz_meteoparam" (parameter, explanation) VALUES ("%s", '');"""%str(tp[0])
                            utils.sql_alter_db(sql)
            
                sqlpart1 = """INSERT OR IGNORE INTO "meteo" (obsid, instrumentid, parameter, date_time, reading_num, reading_txt, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM meteo""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def wlvl_import(self):
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        self.wlvl_import_from_csvlayer()

    def wlvl_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, date_time, meas, comment"
        :return: None
        """
        self.prepare_import('temporary_wlevels')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where ("%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null) or (("%s"='' or "%s"=' ' or "%s" is null) and ("%s"='' or "%s"=' ' or "%s" is null))"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(4,'w_levels',sqlremove,'obs_points',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def wlvllogg_import(self):
        """ Method for importing diveroffice csv files """
        self.prepare_import('temporary_logg_lvl')
        
        result_info = []      
        
        existing_obsids = utils.sql_load_fr_db("""select distinct obsid from '%s'"""%'obs_points')[1]      
        existing_obsids = [str(obsid[0]) for obsid in existing_obsids]

        confirm_names = utils.askuser("YesNo", "Do you want to confirm each logger import name before import?")

        files = self.select_files()
        for selected_file in files:
            file_data = self.load_diveroffice_file(selected_file, existing_obsids, confirm_names.result)
            if file_data == 'failed':
                utils.pop_up_info("The import failed and has been stopped.")
                break
            elif file_data == 'continue':
                continue            
            with utils.tempinput(file_data) as csvpath:
                self.csvlayer = self.csv2qgsvectorlayer(csvpath)
                #Continue to next file if the file failed to import
                if not self.csvlayer:
                    continue
                    
                self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
                cleaningok = self.cleanuploggerdata() # returns 1 if cleaning went well

                #HERE IS WHERE DATA IS TRANSFERRED TO w_levels_logger
                if cleaningok == 1: # If cleaning was OK, then perform the import
                    self.goalcolumns = utils.sql_load_fr_db("""PRAGMA table_info(w_levels_logger)""")[1]
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
                    self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
                    NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                    if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                        result_info.append("""%s: In total %s measurements were not imported from the file since they would cause duplicates in the database."""%(selected_file, NoExcluded))
                        #utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
                    else:  # If some of the imported data already existed in the database, let the user know
                        result_info.append("""%s: In total %s measurements were imported."""%(selected_file,(self.RecordsAfter[0][0] - self.RecordsBefore[0][0])))
                        #utils.pop_up_info("""In total %s measurements were imported."""%(self.RecordsAfter[0][0] - self.RecordsBefore[0][0]))
                elif cleaningok == 0 and not(len(self.columns)==5 or len(self.columns)==6):
                    utils.pop_up_info("Import file must have exactly three columns!\n(Or four if conductivity is also measured.)", "Import Error for file " + selected_file)
                    self.status = 'False'
                else:
                    self.status = 'False'       #Cleaning was not ok and status is false - no import performed

                utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
        utils.pop_up_info('\n'.join(result_info))
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()        
        
    def wquallab_import(self): 
        self.prepare_import('temporary_wquallab')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or ("%s" in ('', ' ') or "%s" is null) and ("%s" in ('', ' ') or "%s" is null)and ("%s" in ('', ' ') or "%s" is null)"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[2][1],self.columns[2][1],self.columns[5][1],self.columns[5][1],self.columns[7][1],self.columns[7][1],self.columns[8][1],self.columns[8][1],self.columns[9][1],self.columns[9][1],self.columns[11][1],self.columns[11][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[2][1],self.columns[7][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(12,'w_qual_lab',sqlremove,'obs_points',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "w_qual_lab" (obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text),  (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.columns[8][1],self.columns[8][1],self.columns[9][1],self.columns[10][1],self.columns[11][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wqualfield_import(self):
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        self.wqualfield_import_from_csvlayer()

    def wqualfield_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment"
        :return:
        """
        self.prepare_import('temporary_wqualfield')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[2][1],self.columns[2][1],self.columns[4][1],self.columns[4][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[2][1],self.columns[4][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.MultipleFieldDuplicates(10,'w_qual_field',sqlremove,'obs_points',sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "w_qual_field" (obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.columns[8][1],self.columns[8][1],self.columns[9][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def fieldlogger_import(self):
        filename = self.select_files(True)[0].encode(str(self.charsetchoosen[0]))

        result_dict = {}
        with io.open(filename, 'r', encoding=str(self.charsetchoosen[0])) as f:

            #Skip header
            f.readline()

            result_dict = self.fieldlogger_import_parse_rows(f)

        for typename, obsdict in result_dict.iteritems():
            if typename == 'level':
                self.fieldlogger_level_import(dict(obsdict))
            elif typename == 'flow':
                self.fieldlogger_flow_import(dict(obsdict))
            elif typename == 'quality':
                self.fieldlogger_quality_import(dict(obsdict))
            else:
                utils.pop_up_info("Unknown type: " + typename)

    @staticmethod
    def fieldlogger_import_parse_rows(f):
        """
        Parses rows from fieldlogger format into a dict
        :param f: File_data, often an open file or a list of rows
        :return: a dict like {typename: {obsid: {date_time: {parameter: value, }}}}

        f must not have a header.
        """
        result_dict = {}
        for rownr, rawrow in enumerate(f):
            row = rawrow.rstrip('\r').rstrip('\n')
            cols = row.split(';')
            type_obsid = cols[0]
            typename = type_obsid.split('.')[-1]
            obsid = utils.rstrip('.' + typename, type_obsid)
            date = cols[1]
            time = cols[2]
            date_time = datestring_to_date(date + ' ' + time)
            value = cols[3]
            type_parameter = cols[4]
            paramtypename = type_parameter.split('.')[0]
            parameter = utils.lstrip(paramtypename + '.', type_parameter)
            result_dict.setdefault(typename, {}).setdefault(obsid, {}).setdefault(date_time, {})[parameter] = value
        return result_dict

    def fieldlogger_level_import(self, obsdict):
        """
        Produces a filestring with columns "obsid, date_time, meas, comment" and imports it
        :param obsdict: a dict like {obsid: {date_time: {parameter: value}}}
        :return: None
        """
        file_data_list = [';'.join(['obsid', 'date_time', 'meas', 'comment'])]
        for obsid, date_time_dict in obsdict.iteritems():
            for date_time, param_dict in sorted(date_time_dict.iteritems()):
                printrow = [obsid]
                printrow.append(datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S'))
                printrow.append(param_dict.get('meas', '').replace(',', '.'))
                printrow.append(param_dict.get('comment', ''))
                file_data_list.append(u';'.join(printrow))

        file_data = u'\n'.join(file_data_list)
        self.fieldlogger_send_file_data_to_importer(file_data, self.wlvl_import_from_csvlayer)

    def fieldlogger_flow_import(self, obsdict):
        """
        Produces a filestring with columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :return:
        """

        file_data_list = [';'.join(['obsid', 'instrumentid', 'flowtype', 'date_time', 'reading', 'unit', 'comment'])]

        flow_params_and_units = utils.get_flow_params_and_units()

        for obsid, date_time_dict in obsdict.iteritems():
            for date_time, param_dict in sorted(date_time_dict.iteritems()):
                _param_dict = dict(param_dict)
                datestring = datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')

                instrumentid = _param_dict.pop('instrument', '')
                comment = _param_dict.pop('comment', '')

                for flowtype, reading in _param_dict.iteritems():
                    unit = flow_params_and_units.get(flowtype, None)[0]
                    if unit is None:
                        unit = PyQt4.QtGui.QInputDialog.getText(None, 'Unit not found', 'Please submit it for ' + flowtype + '\nIt will be used for all flowtypes of type ' + flowtype + '\n', PyQt4.QtGui.QLineEdit.Normal, ' ')[0]
                        flow_params_and_units[flowtype] = unit
                    else:
                        unit = unit[0]

                    printrow = [obsid, instrumentid, flowtype, datestring, reading.replace(',', '.'), unit, comment]
                    try:
                        file_data_list.append(u';'.join(printrow))
                    except:
                        raise Exception(utils.pop_up_info(str(printrow)))

        file_data = u'\n'.join(file_data_list)
        self.fieldlogger_send_file_data_to_importer(file_data, self.wflow_import_from_csvlayer)

    def fieldlogger_quality_import(self, obsdict):
        """
        Produces a filestring with columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :return:
        """
        file_data_list = [';'.join(['obsid', 'staff', 'date_time', 'instrument', 'parameter', 'reading_num', 'reading_txt', 'unit', 'flow_lpm', 'comment'])]

        qual_params_and_units = utils.get_qual_params_and_units()

        submitted_staff =None

        for obsid, date_time_dict in obsdict.iteritems():
            for date_time, param_dict in sorted(date_time_dict.iteritems()):
                _param_dict = dict(param_dict)
                datestring = datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')

                instrument = _param_dict.pop('instrument', '')
                comment = _param_dict.pop('comment', '')
                flow_lpm = _param_dict.pop('flow_lpm', '').replace(',', '.')

                staff = _param_dict.pop('staff', None)
                if staff is None:
                    if submitted_staff is None:
                        staff = PyQt4.QtGui.QInputDialog.getText(None, 'Staff not found', 'Please submit the name or initials of the person who did the measurement.\nIt will be used for the rest of the import\n', PyQt4.QtGui.QLineEdit.Normal, ' ')[0]
                        submitted_staff = staff
                    else:
                        staff = submitted_staff

                for parameter, reading_num in _param_dict.iteritems():
                    reading_num = reading_num.replace(',', '.')
                    reading_txt = reading_num
                    unit = qual_params_and_units.get(parameter, None)
                    if unit is None:
                        unit = PyQt4.QtGui.QInputDialog.getText(None, 'Unit not found', 'Please submit unit for ' + parameter + '\nIt will be used for all parameter of type ' + parameter + '\n', PyQt4.QtGui.QLineEdit.Normal, ' ')[0]
                        qual_params_and_units[parameter] = unit
                    else:
                        unit = unit[0]

                    printrow = [obsid, staff, datestring, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment]
                    file_data_list.append(u';'.join(printrow))

        file_data = u'\n'.join(file_data_list)
        self.fieldlogger_send_file_data_to_importer(file_data, self.wqualfield_import_from_csvlayer)

    def fieldlogger_send_file_data_to_importer(self, file_data, importer):
        self.csvlayer = None
        with utils.tempinput(file_data) as csvpath:
            csvlayer = self.csv2qgsvectorlayer(csvpath)
            if not csvlayer:
                utils.pop_up_info("Creating csvlayer for " + str(importer) + " failed!")
            self.csvlayer = csvlayer
            importer()

    def prepare_import(self, temptableName):
        """ Shared stuff as preparation for the import """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.status = 'False' #True if upload to sqlite and cleaning of data succeeds 
        self.temptableName = temptableName        

    def VerifyIDInMajorTable(self,MajorTable): #for all tables with foreign key = obsid
        notinmajor = 'False'
        possibleobsids = utils.sql_load_fr_db("""select distinct obsid from %s"""%MajorTable)[1] 
        obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))[1]
        for id in obsidstobeimported:
                if not id in possibleobsids:
                    qgis.utils.iface.messageBar().pushMessage("Import Failure","""The obsid=%s do not exist in %s!"""%(str(id[0]),MajorTable),2)
                    self.status = 'False'
                    notinmajor = 'True'
        if notinmajor == 'True':
            return 0
        else:
            return 1
            
    def CheckIfOBSIDExists(self,GoalTable,idcol):#for obs_points and obs_lines where primary key = obsid
        possibleobsids = utils.sql_load_fr_db("""select distinct obsid from '%s'"""%GoalTable)[1]
        obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[idcol][1],self.temptableName))[1]
        for id in obsidstobeimported:
            if id in possibleobsids:
                qgis.utils.iface.messageBar().pushMessage("Warning","""obsid=%s do already exist in the database and will not be imported again!"""%str(id[0]),1,duration=10)

    def MultipleFieldDuplicates(self,NoCols,GoalTable,sqlremove,MajorTable,sqlNoOfdistinct): #For secondary tables linking to obs_points and obs_lines: Sanity checks and removes duplicates
        """perform some sanity checks of the imported data and removes duplicates and empty records"""
        if len(self.columns)<NoCols: 
            qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.status = 'False'
            return 0 #only to stop function
        else:    #If correct number of columns, remove empty records
            if len(self.columns) > NoCols:#Here is where the user may interrupt if there are more columns than needed for w_levels
                ManyColsQuestion = utils.askuser("YesNo", """Please note!\nThere are %s columns in your csv file which may be perfectly fine if the first %s corresponds to those needed.\n\nDo you want to proceed with the import?"""%(str(len(self.columns)),str(NoCols)),"Warning!")
                if ManyColsQuestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
            utils.sql_alter_db(sqlremove)
            #Then verify that obsid exists in MajorTable and perform statistics
            verifyok = self.VerifyIDInMajorTable(MajorTable) #Verify that all ID's exist in major table (obs_points or obs_lines)
            if verifyok == 1: #Go on with some statistics
                self.recsbefore = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%GoalTable)[1])[0][0]
                self.recstoimport = (utils.sql_load_fr_db(sqlNoOfdistinct)[1])[0][0]
                self.recsinfile = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1])[0][0]
                #qgis.utils.iface.messageBar().pushMessage("Info","The csv file had " + str(self.recsinfile) + " non-empty posts \n" + "and among these were found " + str(self.recsinfile - self.recstoimport) + " duplicates.", 0)
                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.recsinfile > self.recstoimport: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?"""%(self.recsinfile - self.recstoimport),"Warning!")
                    if duplicatequestion.result == 0:      # if the user wants to abort
                        self.status = 'False'
                        PyQt4.QtGui.QApplication.restoreOverrideCursor()
                        return 0   # return simply to stop this function
                return 1
            else:
                return 0

    def SingleFieldDuplicates(self,NoCols,GoalTable,sqlremove,idcol): #For major tables obs_points and obs_lines: Sanity checks and removes duplicates
        """perform some sanity checks of the imported data and removes duplicates and empty records"""
        if not len(self.columns)==NoCols:
            qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have exactly " + str(NoCols) + " columns!\nCheck your data and try again.",2)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.status = 'False'
            return 0 #only to stop function
        else:    #If correct number of columns, remove empty records
            utils.sql_alter_db(sqlremove)
            #Then check if any obsid already exist in GoalTable and perform statistics
            self.CheckIfOBSIDExists(GoalTable,idcol)
            #Some statistics
            self.recsbefore = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%GoalTable)[1])[0][0] 
            self.recstoimport = (utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))[1])[0][0]
            self.recsinfile = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1])[0][0]
            #qgis.utils.iface.messageBar().pushMessage("Info","The csv file had " + str(self.recsinfile) + " non-empty posts \n" + "and among these were found " + str(self.recsinfile - self.recstoimport) + " duplicates.", 0)
            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.recsinfile > self.recstoimport: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?"""%(self.recsinfile - self.recstoimport),"Warning!")
                if duplicatequestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
            return 1

    def StatsAfter(self):
        NoExcluded = self.recstoimport - (self.recsafter - self.recsbefore)
        if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
            qgis.utils.iface.messageBar().pushMessage("Warning","""In total %s posts were not imported since they would have caused duplicates in the database."""%NoExcluded, 1)

    def selectcsv(self, only_one_file=True): # general importer
        """Select the csv file, user must also tell what charset to use"""
        try:#MacOSX fix2
            localencoding = locale.getdefaultlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        except:
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal,'utf-8')
        if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
            if only_one_file:
                csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
                csvlayer = self.csv2qgsvectorlayer(csvpath)
            else:
                csvpath = PyQt4.QtGui.QFileDialog.getOpenFileNames(None, "Select Files","","csv (*.csv)")
                csvlayer = [self.csv2qgsvectorlayer(path) for path in csvpath if path]
            return csvlayer        
            
    def csv2qgsvectorlayer(self, path):
        """ Creates QgsVectorLayer from a csv file """
        if not path:
            qgis.utils.iface.messageBar().pushMessage("Failure, no csv file was selected.")
            return False
        csvlayer = QgsVectorLayer(path, "temporary_csv_layer", "ogr")
        if not csvlayer.isValid():
            qgis.utils.iface.messageBar().pushMessage("Failure","Impossible to Load File in QGis:\n" + str(path), 2)
            return False
        csvlayer.setProviderEncoding(str(self.charsetchoosen[0]))                 #Set the Layer Encoding                                        
        return csvlayer            

    def select_files(self, only_one_file=False):
        try:#MacOSX fix2
            localencoding = locale.getdefaultlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        except:
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal,'utf-8')
        if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
            if only_one_file:
                path = [PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")]
            else:
                path = PyQt4.QtGui.QFileDialog.getOpenFileNames(None, "Select Files","","csv (*.csv)")
        return path

    def load_diveroffice_file(self, path, existing_obsids=None, ask_for_names=True):
        """ Parses a diveroffice csv file into a string
        
            The Location attribute is used as obsid and added as a column.
            Values containing ',' is replaced with '.'
        """    
        filedata = []
        begin_extraction = False
        with open(path, 'r') as f:
            obsid = None
            for rawrow in f:
                row = rawrow.decode('CP1252').rstrip('\n').rstrip('\r').lstrip()
                if row.startswith('Location'):
                    obsid = row.split('=')[1].strip()
                    continue
                cols = row.split(';')
                if row.startswith('Date/time'):
                    cols.append('obsid')
                    begin_extraction = True

                    if ask_for_names:
                        obsid = PyQt4.QtGui.QInputDialog.getText(None, "Submit obsid", "The obsid " + str(obsid) + " was found for " + str(path) + ", accept the found name or change it below", PyQt4.QtGui.QLineEdit.Normal, obsid.capitalize() if obsid is not None else 'None')[0]
                    if existing_obsids is not None:
                        if obsid not in existing_obsids:
                            obsid = PyQt4.QtGui.QInputDialog.getText(None, "WARNING", "The supplied obsid '" + str(obsid) + "' did not exist in obs_points, please submit it again for " + str(path) + ".", PyQt4.QtGui.QLineEdit.Normal, 'obsid')[0]                        
                        if obsid not in existing_obsids:
                            stop_question = utils.askuser("YesNo", "Failure, the obsid '" + obsid + "' did not exist in obs_points, import will fail.\n\nDo you wan't to stop the import? (else it will continue with the next file)")
                            if stop_question.result:
                                return 'failed'
                            else:
                                return 'continue'                        
                    filedata.append(';'.join(cols))
                    continue
                if begin_extraction:
                    dateformat = find_date_format(cols[0])
                    if dateformat is not None:
                        date = datetime.strptime(cols[0], dateformat)
                        printrow = [datetime.strftime(date,
                                    '%Y-%m-%d %H:%M:%S')]
                        printrow.extend([col.replace(',', '.')
                                       for col in cols[1:]])
                        printrow.append(obsid)
                        filedata.append(';'.join(printrow))
        filestring = '\n'.join(filedata)
        return filestring

    def csv2qgsvectorlayer(self, path):
        """ Converts a csv path into a QgsVectorLayer """
        if not path:
            qgis.utils.iface.messageBar().pushMessage("Failure, no csv file was selected.")
            return False        
        csvlayer = QgsVectorLayer(path, "temporary_csv_layer", "ogr")
        if not csvlayer.isValid():
            qgis.utils.iface.messageBar().pushMessage("Failure","Impossible to Load File in QGis:\n" + str(path), 2)
            return False
        csvlayer.setProviderEncoding(str(self.charsetchoosen[0]))                 #Set the Layer Encoding                                        
        return csvlayer                
                
    def qgiscsv2sqlitetable(self): # general importer
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'."""
        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.temptableName): #if so, propose to rename the temporary import-table
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.temptableName='%s_2'%self.temptableName
                else:
                    return None
                  
        #Get all fields with corresponding types for the csv-csvlayer in qgis
        fields=[]
        fieldsNames=[]
        provider=self.csvlayer.dataProvider()
        for name in provider.fields(): #fix field names and types in temporary table
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not a .csvt file is defined beside the imported file.
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool, PyQt4.QtCore.QVariant.Int,QtCore.QVariant.LongLong, PyQt4.QtCore.QVariant.UInt, PyQt4.QtCore.QVariant.ULongLong):  # field type is integer
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
        conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis csvlayer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        for feature in self.csvlayer.getFeatures(): 
            values_perso=[]
            for attr in feature.attributes():
                values_perso.append(attr) # attr is supposed to be unicode and should be kept like that, sometimes though it ends up being a byte string, do not know why....
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #please note the usage of ? for parameter substitution - highly recommended
                #curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso]))
                try:
                    curs.execute("""INSERT INTO %s VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([value for value in values_perso])) # Assuming value is unicode, send it as such to sqlite
                except:
                    curs.execute("""INSERT INTO %s VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #in case of errors, the value must be a byte string, then try to convert to unicode
                self.status = 'True'
            else: #no attribute Datas
                qgis.utils.iface.messageBar().pushMessage("No data found!!","No data will be imported!!", 2)
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanuploggerdata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
        if len(self.columns)==4 or len(self.columns)==5:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null"""%(self.temptableName,column[1],column[1]))
            #THE METHOD ABOVE NEEDS REVISON
            # Add level_masl column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double"""%self.temptableName)
            utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """%(self.temptableName,self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
            
            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))[1]
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1]

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
        
    def SanityCheckVacuumDB(self):
        sanity = utils.askuser("YesNo","""It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""",'Vacuum the database?')
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()

""" Note, thes class below is a quickfix and should be incorporated into the a multi-import class above instead. As soon as there is time for code cleanup..."""
class wlvlloggimportclass():

    def __init__(self):
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_logg_lvl'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.columns=[]
        self.charsetchoosen = ('','')

        # Find obsid for the selected object
        self.obsid = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())     #A list of length 1! To get the acutal ID, call self.obsid[0]
        # Import the csv file as a ogr csvlayer
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            # upload the ogr csvlayer to splite db
            self.uploadLoggerdataToSplite()    # Calling similar function as uploadQgisVectorLayer
            # perform some cleaning of imported data
            cleaningok = self.cleanuploggerdata() # returns 1 if cleaning went well

            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels_logger
            if cleaningok == 1: # If cleaning was OK, then perform the import
                self.goalcolumns = utils.sql_load_fr_db("""PRAGMA table_info(w_levels_logger)""")[1]
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
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
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
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            sanity = utils.askuser("YesNo","""It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""",'Vacuum the database?')
            if sanity.result == 1:
                PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
                utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        try:#MacOSX fix2
            localencoding = locale.getdefaultlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        except:
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal,'utf-8')
        if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            if not self.csvpath or self.csvpath=='': 
                return
            else:
                csvlayer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not csvlayer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                csvlayer.setProviderEncoding(str(self.charsetchoosen[0]))
                return csvlayer
        
    def uploadLoggerdataToSplite(self):
        self.status = 'False'
        #Verify if temptableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]
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

        for name in provider.fields(): 
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
        
        #Create new table in DB
        fields=','.join(fields) 
        fields = ''.join([x for x in fields if ord(x) < 128])    # Just get rid of all non-ascii, the column names are not important anyway
        sql = """CREATE table "%s" (%s)"""%(self.temptableName, fields)
        #utils.pop_up_info(sql)      # debugging
        utils.sql_alter_db(sql) #NO PKUID, Number of fields exactly the same as imported csv file
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
        # Retreive every feature 
        for feature in self.csvlayer.getFeatures(): 
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for attr in feature.attributes():
                values_perso.append(attr) # attr is supposed to be unicode and should be kept like that, sometimes though it ends up being a byte string, do not know why....
            
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
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
        if len(self.columns)==3 or len(self.columns)==4:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null"""%(self.temptableName,column[1],column[1]))
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
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
            
            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))[1]
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1]
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
 