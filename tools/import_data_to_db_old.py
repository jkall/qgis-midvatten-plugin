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
import io
import os
import locale
import qgis.utils
import copy
from collections import OrderedDict
from datetime import datetime
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
from qgis.core import *

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4

import db_utils
import midvatten_utils as utils
from definitions import midvatten_defs as defs

from date_utils import find_date_format, datestring_to_date, dateshift

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
        self.fieldlogger_staff = None

    def default_import(self, importer):
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        importer()
        self.SanityCheckVacuumDB()

    def obslines_import(self):
        self.prepare_import('temporary_obs_lines')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            ConnectionOK, self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]) #first two cols are expected to be WKT geometry and obsid
            cleaningok = self.SingleFieldDuplicates(6,'obs_lines',sqlremove,1) # This is where duplicates are removed  LAST ARGUMENT IS COLUMN FOR ID
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_lines'"""
                SRID = str((db_utils.sql_load_fr_db(sql)[1])[0][0])# THIS IS DUE TO WKT-import of geometries below
                sqlpart1 = """INSERT OR IGNORE INTO "obs_lines" (obsid, name, place, type, source, geometry) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), ST_GeomFromText("%s",%s) from %s"""%(self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[0][1],SRID,self.temptableName)#PLEASE NOTE THE SRID!
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM obs_lines""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def obsp_import(self):
        self.prepare_import('temporary_obs_points')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = (db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1])#Load column names from sqlite table

            NoCols = 26
            try:
                obsid = self.columns[0][1]
                name = self.columns[1][1]
                place = self.columns[2][1]
                atype = self.columns[3][1]
                length = self.columns[4][1]
                drillstop = self.columns[5][1]
                diam = self.columns[6][1]
                material = self.columns[7][1]
                screen = self.columns[8][1]
                capacity = self.columns[9][1]
                drilldate = self.columns[10][1]
                wmeas_yn = self.columns[11][1]
                wlogg_yn = self.columns[12][1]
                east = self.columns[13][1]
                north = self.columns[14][1]
                ne_accur = self.columns[15][1]
                ne_source = self.columns[16][1]
                h_toc = self.columns[17][1]
                h_tocags = self.columns[18][1]
                h_gs = self.columns[19][1]
                h_accur = self.columns[20][1]
                h_syst = self.columns[21][1]
                h_source = self.columns[22][1]
                source = self.columns[23][1]
                com_onerow = self.columns[24][1]
                com_html = self.columns[25][1]
            except IndexError:
                qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                cleaningok = 0
                self.status = 'False'
            else:
                sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null"""%(self.temptableName, obsid, obsid) #CHANGE HERE!!!
                cleaningok = self.SingleFieldDuplicates(NoCols,'obs_points',sqlremove,0) # This is where duplicates are removed  LAST ARGUMENT IS COLUMN FOR ID

            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql_list = []
                sql_list.append(r"""INSERT OR IGNORE INTO "obs_points" (obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html) """)
                sql_list.append(r"""SELECT CAST("%s" as text)"""%obsid)
                sql_list.append(r""", CAST("%s" as text)"""%name)
                sql_list.append(r""", CAST("%s" as text)"""%place)
                sql_list.append(r""", CAST("%s" as text)"""%atype)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(length, length))
                sql_list.append(r""", CAST("%s" as text)"""%drillstop)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(diam, diam))
                sql_list.append(r""", CAST("%s" as text)"""%material)
                sql_list.append(r""", CAST("%s" as text)"""%screen)
                sql_list.append(r""", CAST("%s" as text)"""%capacity)
                sql_list.append(r""", CAST("%s" as text)"""%drilldate)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as integer) else null end)"""%(wmeas_yn, wmeas_yn))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as integer) else null end)"""%(wlogg_yn, wlogg_yn))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(east, east))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(north, north))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(ne_accur, ne_accur))
                sql_list.append(r""", CAST("%s" as text)"""%ne_source)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_toc, h_toc))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_tocags, h_tocags))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_gs, h_gs))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_accur, h_accur))
                sql_list.append(r""", CAST("%s" as text)"""%h_syst)
                sql_list.append(r""", CAST("%s" as text)"""%h_source)
                sql_list.append(r""", CAST("%s" as text)"""%source)
                sql_list.append(r""", CAST("%s" as text)"""%com_onerow)
                sql_list.append(r""", CAST("%s" as text)"""%com_html)
                sql_list.append(r"""FROM %s"""%self.temptableName)
                sql = ''.join(sql_list)
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (
                db_utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def seismics_import(self):
        self.prepare_import('temporary_seismics')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1]) #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) # To select distinct data posts from the import table
            cleaningok = self.multiple_field_duplicates(6, 'seismic_data', sqlremove, 'obs_lines', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "seismic_data" (obsid, length, ground, bedrock, gw_table, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM seismic_data""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def strat_import(self):
        self.prepare_import('temporary_stratigraphy')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]) #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(9, 'stratigraphy', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "stratigraphy" (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def vlf_import(self):
        self.prepare_import('temporary_vlf_data')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = (db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1])#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(5, 'vlf_data', sqlremove, 'obs_lines', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "vlf_data" (obsid, length, real_comp, imag_comp, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM vlf_data""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wflow_import_from_csvlayer(self): #please note the particular behaviour of adding additional flowtypes to table zz_flowtype
        """
        self.csvlayer must contain columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment"
        :return:
        """
        self.prepare_import('temporary_wflow')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(7, 'w_flow', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then fix zz_flowtype and then copy data from the temporary table to the original table in the db
                #check for flowtypes and add those that are not present in db table zz_flowtype the obsid actually exists in obs_points
                FlTypesInDb = db_utils.sql_load_fr_db('select distinct type from zz_flowtype')[1]
                FlTypes2BImported = db_utils.sql_load_fr_db("""select distinct "%s" from %s""" % (self.columns[2][1], self.temptableName))[1]

                try:
                    for tp in FlTypes2BImported:
                        if tp not in FlTypesInDb:
                            sql = """insert into "zz_flowtype" (type, explanation) VALUES ("%s", '');"""%(str(tp[0]))
                            db_utils.sql_alter_db(sql)
                except TypeError:
                    qgis.utils.iface.messageBar().pushMessage("Import warning","""Flow type could not be updated. Table zz_flowtype needs to be upgraded to latest version.""")

                sqlpart1 = """INSERT OR IGNORE INTO "w_flow" (obsid, instrumentid, flowtype, date_time, reading, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (
                db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_flow""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def meteo_import(self): #please note the particular behaviour of adding additional flowtypes to table zz_meteoparam
        self.prepare_import('temporary_meteo')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(8, 'meteo', sqlremove, 'obs_points', sqlNoOfdistinct)#
            if cleaningok == 1: # If cleaning was OK, then fix zz_meteoparam and then copy data from the temporary table to the original table in the db
                #check for parameters and add those that are not present in db table zz_meteoparam
                FlTypesInDb = db_utils.sql_load_fr_db('select distinct parameter from zz_meteoparam')[1]
                FlTypes2BImported = db_utils.sql_load_fr_db("""select distinct "%s" from %s""" % (self.columns[2][1], self.temptableName))[1]
                for tp in FlTypes2BImported:
                        if not tp in FlTypesInDb:
                            sql = """insert into "zz_meteoparam" (parameter, explanation) VALUES ("%s", '');"""%str(tp[0])
                            db_utils.sql_alter_db(sql)

                sqlpart1 = """INSERT OR IGNORE INTO "meteo" (obsid, instrumentid, parameter, date_time, reading_num, reading_txt, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM meteo""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wlvl_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, date_time, meas, comment"
        :return: None
        """
        self.prepare_import('temporary_wlevels')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table
            if len(self.columns) < 4:
                qgis.utils.iface.messageBar().pushMessage("Import Failure","""The file had less than the required 4 columns""")
                cleaningok = 0
            else:
                sqlremove = """DELETE FROM "%s" where ("%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null) or (("%s"='' or "%s"=' ' or "%s" is null) and ("%s"='' or "%s"=' ' or "%s" is null))"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
                sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
                cleaningok = self.multiple_field_duplicates(4, 'w_levels', sqlremove, 'obs_points', sqlNoOfdistinct)

            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wquallab_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        :return: None
        """
        self.prepare_import('temporary_wquallab')

        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table

            NoCols = 12
            try:
                obsid = self.columns[0][1]
                depth = self.columns[1][1]
                report = self.columns[2][1]
                project = self.columns[3][1]
                staff = self.columns[4][1]
                date_time = self.columns[5][1]
                anameth = self.columns[6][1]
                parameter = self.columns[7][1]
                reading_num = self.columns[8][1]
                reading_txt = self.columns[9][1]
                unit = self.columns[10][1]
                comment = self.columns[11][1]
            except IndexError:
                qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                cleaningok = 0
                self.status = 'False'
            else:
                #Delete empty records from the import table!!!
                sqlremove_list = []
                sqlremove_list.append(r"""DELETE FROM "%s" """%(self.temptableName))
                sqlremove_list.append(r"""where "%s" in ('', ' ') or "%s" is null """%(obsid, obsid))
                sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(report, report))
                sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(date_time, date_time))
                sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(parameter, parameter))
                sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(reading_num, reading_num))
                sqlremove_list.append(r"""and ("%s" in ('', ' ') or "%s" is null) """%(reading_txt, reading_txt))
                sqlremove_list.append(r"""and ("%s" in ('', ' ') or "%s" is null)"""%(comment, comment))
                sqlremove = ''.join(sqlremove_list)

                sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(report,parameter,self.temptableName) #Number of distinct data posts in the import table
                cleaningok = self.multiple_field_duplicates(NoCols, 'w_qual_lab', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db

                if db_utils.verify_table_exists('zz_staff'):
                    #Add staffs that does not exist in db
                    staffs = set([x[0] for x in db_utils.sql_load_fr_db("""select distinct staff from %s""" % self.temptableName)[1]])
                    self.staff_import(staffs)

                sql_list = []
                sql_list.append(r"""INSERT OR IGNORE INTO "w_qual_lab" (obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment) """)
                sql_list.append(r"""SELECT CAST("%s" as text), """%obsid)
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(depth, depth))
                sql_list.append(r"""CAST("%s" as text), """%(report))
                sql_list.append(r"""CAST("%s" as text), """%(project))
                sql_list.append(r"""CAST("%s" as text), """%(staff))
                sql_list.append(r"""CAST("%s" as text), """%(date_time))
                sql_list.append(r"""CAST("%s" as text), """%(anameth))
                sql_list.append(r"""CAST("%s" as text), """%(parameter))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(reading_num, reading_num))
                sql_list.append(r"""CAST("%s" as text), """%(reading_txt))
                sql_list.append(r"""CAST("%s" as text), """%(unit))
                sql_list.append(r"""CAST("%s" as text)           """%(comment))
                sql_list.append(r"""FROM %s"""%(self.temptableName))
                sql = ''.join(sql_list)

                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (
                db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wqualfield_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment"
        :return:
        """
        self.prepare_import('temporary_wqualfield')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]#Load column names from sqlite table

            NoCols = 10
            try:
                obsid = self.columns[0][1]
                staff = self.columns[1][1]
                date_time = self.columns[2][1]
                instrument = self.columns[3][1]
                parameter = self.columns[4][1]
                reading_num = self.columns[5][1]
                reading_txt = self.columns[6][1]
                unit = self.columns[7][1]
                depth = self.columns[8][1]
                comment = self.columns[9][1]
            except IndexError:
                qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                cleaningok = 0
                self.status = 'False'
            else:
                sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName, obsid, obsid, date_time, date_time, parameter, parameter)#Delete empty records from the import table!!!
                sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(obsid, date_time, parameter, unit, self.temptableName) #Number of distinct data posts in the import table
                cleaningok = self.multiple_field_duplicates(NoCols, 'w_qual_field', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db

                if db_utils.verify_table_exists('zz_staff'):
                    #Add staffs that does not exist in db
                    staffs = set([x[0] for x in db_utils.sql_load_fr_db("""select distinct staff from %s""" % self.temptableName)[1]])
                    self.staff_import(staffs)

                sql_list = []
                sql_list.append(r"""INSERT OR IGNORE INTO "w_qual_field" (obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment) """)
                sql_list.append(r"""SELECT CAST("%s" as text), """%(obsid))
                sql_list.append(r"""CAST("%s" as text), """%(staff))
                sql_list.append(r"""CAST("%s" as text), """%(date_time))
                sql_list.append(r"""CAST("%s" as text), """%(instrument))
                sql_list.append(r"""CAST("%s" as text), """%(parameter))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(reading_num, reading_num))
                sql_list.append(r"""CAST("%s" as text), """%(reading_txt))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as text) else null end), """%(unit, unit))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(depth, depth))
                sql_list.append(r"""CAST("%s" as text) """%(comment))
                sql_list.append(r"""FROM %s"""%(self.temptableName))
                sql = ''.join(sql_list)

                db_utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")[1])[0][0] #for the statistics

                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def ask_for_staff(self):
        existing_staff = defs.staff_list()[1]

        if self.fieldlogger_staff is None:
            question = utils.NotFoundQuestion(dialogtitle=u'Submit field staff',
                                           msg=u'Submit the field staff who made the FieldLogger measurements.\nIt will be used for the rest of the import',
                                           existing_list=existing_staff)
            answer = question.answer
            if answer == u'cancel':
                return u'cancel'

            self.fieldlogger_staff = utils.returnunicode(question.value)
        return self.fieldlogger_staff

    def send_file_data_to_importer(self, file_data, importer, cleaning_function=None):
        self.csvlayer = None
        if len(file_data) < 2:
            return

        if cleaning_function is not None:
            file_data = cleaning_function(file_data)

        file_string = utils.lists_to_string(file_data)

        with utils.tempinput(file_string, charset=u'utf_8') as csvpath:
            self.charsetchoosen = u'UTF-8'
            csvlayer = self.csv2qgsvectorlayer(csvpath)
            if not csvlayer:
                utils.pop_up_info("Creating csvlayer for " + str(importer) + " failed!")
                return
            self.csvlayer = csvlayer
            importer()

    def staff_import(self, staff):
        """ Inserts initials if they don't exist in table staff
        :param initials: a string with initials, or a list of strings with initials
        :return:
        """
        name = u''

        if isinstance(staff, basestring):
            staff = [staff]

        for _staff in staff:
            _staff = utils.returnunicode(_staff)
            existing_staff = [utils.returnunicode(x) for x in defs.staff_list()[1]]
            if _staff in existing_staff:
                continue
            else:
                sql = u"""insert into "zz_staff" (staff, name) VALUES ("%s", "%s");"""%(_staff, name)
                db_utils.sql_alter_db(sql.encode('utf-8'))

    def prepare_import(self, temptableName):
        """ Shared stuff as preparation for the import """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.status = 'False' #True if upload to sqlite and cleaning of data succeeds
        self.temptableName = temptableName

    def VerifyIDInMajorTable(self,MajorTable): #for all tables with foreign key = obsid
        notinmajor = 'False'
        possibleobsids = db_utils.sql_load_fr_db("""select distinct obsid from %s""" % MajorTable)[1]
        #obsidstobeimported = []
        obsidstobeimported = db_utils.sql_load_fr_db("""select distinct "%s" from %s""" % (self.columns[0][1], self.temptableName))[1]
        #obsidstobeimported.append(tuple([x.toPyObject() if isinstance(x, PyQt4.QtCore.QVariant) else x for y in utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))[1] for x in y]))
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
        possibleobsids = db_utils.sql_load_fr_db("""select distinct obsid from '%s'""" % GoalTable)[1]
        obsidstobeimported = db_utils.sql_load_fr_db("""select distinct "%s" from %s""" % (self.columns[idcol][1], self.temptableName))[1]
        for id in obsidstobeimported:
            if id in possibleobsids:
                qgis.utils.iface.messageBar().pushMessage("Warning","""obsid=%s do already exist in the database and will not be imported again!"""%str(id[0]),1,duration=10)

    def multiple_field_duplicates(self, NoCols, GoalTable, sqlremove, MajorTable, sqlNoOfdistinct, ):  #For secondary tables linking to obs_points and obs_lines: Sanity checks and removes duplicates
        """perform some sanity checks of the imported data and removes duplicates and empty records"""
        if len(self.columns)<NoCols:
            qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.status = 'False'
            return 0 #only to stop function
        else:    #If correct number of columns, remove empty records
            if len(self.columns) > NoCols:#Here is where the user may interrupt if there are more columns than needed for w_levels
                ManyColsQuestion = utils.Askuser("YesNo", """Please note!\nThere are %s columns in your csv file which may be perfectly fine if the first %s corresponds to those needed.\n\nDo you want to proceed with the import?""" % (str(len(self.columns)), str(NoCols)), "Warning!")
                if ManyColsQuestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
            db_utils.sql_alter_db(sqlremove)
            #Then verify that obsid exists in MajorTable and perform statistics
            verifyok = self.VerifyIDInMajorTable(MajorTable) #Verify that all ID's exist in major table (obs_points or obs_lines)
            if verifyok == 1: #Go on with some statistics
                self.recsbefore = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM %s""" % GoalTable)[1])[0][0]
                self.recstoimport = (
                db_utils.sql_load_fr_db(sqlNoOfdistinct)[1])[0][0]
                self.recsinfile = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM %s""" % self.temptableName)[1])[0][0]
                #qgis.utils.iface.messageBar().pushMessage("Info","The csv file had " + str(self.recsinfile) + " non-empty posts \n" + "and among these were found " + str(self.recsinfile - self.recstoimport) + " duplicates.", 0)
                #Then check wether there are duplicates in the imported file and if so, ask user what to do
                if self.recsinfile > self.recstoimport: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                    duplicatequestion = utils.Askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?""" % (self.recsinfile - self.recstoimport), "Warning!")
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
            db_utils.sql_alter_db(sqlremove)
            #Then check if any obsid already exist in GoalTable and perform statistics
            self.CheckIfOBSIDExists(GoalTable,idcol)
            #Some statistics
            self.recsbefore = (
            db_utils.sql_load_fr_db("""SELECT Count(*) FROM %s""" % GoalTable)[1])[0][0]
            self.recstoimport = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)""" % (self.columns[0][1], self.temptableName))[1])[0][0]
            self.recsinfile = (db_utils.sql_load_fr_db("""SELECT Count(*) FROM %s""" % self.temptableName)[1])[0][0]
            #qgis.utils.iface.messageBar().pushMessage("Info","The csv file had " + str(self.recsinfile) + " non-empty posts \n" + "and among these were found " + str(self.recsinfile - self.recstoimport) + " duplicates.", 0)
            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.recsinfile > self.recstoimport: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.Askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?""" % (self.recsinfile - self.recstoimport), "Warning!")
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
            localencoding = utils.getcurrentlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,utils.getcurrentlocale()[1])
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

    def select_files(self, only_one_file=False, should_ask_for_charset=True):

        def get_path(only_one_file):
            if only_one_file:
                path = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            else:
                path = PyQt4.QtGui.QFileDialog.getOpenFileNames(None, "Select Files","","csv (*.csv)")
            if not isinstance(path, (list, tuple)):
                path = [path]
            return path

        path = []

        if not should_ask_for_charset:
            path = get_path(only_one_file)
        else:
            try:#MacOSX fix2
                localencoding = utils.getcurrentlocale()[1]
                self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,utils.getcurrentlocale()[1])
            except:
                self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal, 'utf-8')
            if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
                path = get_path(only_one_file)
        #Filter all empty strings
        path = [p for p in path if p]
        return path

    @staticmethod
    def parse_diveroffice_file(path, charset, existing_obsids=None, ask_for_names=True, begindate=None, enddate=None):
        """ Parses a diveroffice csv file into a string

        :param path: The file name
        :param existing_obsids: A list or tuple with the obsids that exist in the db.
        :param ask_for_names: (True/False) True to ask for obsid name for every obsid. False to only ask if the obsid is not found in existing_obsids.
        :return: A string representing a table file. Including '\n' for newlines.

        Assumptions and limitations:
        * The Location attribute is used as obsid and added as a column.
        * Values containing ',' is replaced with '.'
        * Rows with missing "Water head[cm]"-data is skipped.

        """
        #These can be set to paritally import files.
        #begindate = datetime.strptime(u'2016-06-08 20:00:00',u'%Y-%m-%d %H:%M:%S')
        #enddate = datetime.strptime(u'2016-06-08 19:00:00',u'%Y-%m-%d %H:%M:%S')

        filedata = []
        begin_extraction = False
        delimiter = u';'
        num_cols = None
        with io.open(path, u'r', encoding=str(charset)) as f:
            obsid = None
            for rawrow in f:
                row = rawrow.rstrip(u'\n').rstrip(u'\r').lstrip()

                #Try to get obsid
                if row.startswith(u'Location'):
                    obsid = row.split(u'=')[1].strip()
                    continue

                cols = row.split(delimiter)

                #Parse header
                if row.startswith(u'Date/time'):
                    #Check that the delimitor is ; or try , or stop.
                    if not 3 <= len(cols) <= 4:
                        if 3 <= len(row.split(u',')) <= 4:
                            delimiter = u','
                        else:
                            return utils.ask_user_about_stopping("Failure, delimiter did not match ';' or ',' or there was less than 3 or more than 4 columns in the file " + path + "\nDo you want to stop the import? (else it will continue with the next file)")

                    cols = row.split(delimiter)
                    num_cols = len(cols)

                    header = cols
                    begin_extraction = True
                    continue

                #Parse data
                if begin_extraction:
                    dateformat = find_date_format(cols[0])
                    if dateformat is not None:
                        if len(cols) != num_cols:
                            return utils.ask_user_about_stopping("Failure: The number of data columns in file " + path + " was not equal to the header.\nIs the decimal separator the same as the delimiter?\nDo you want to stop the import? (else it will continue with the next file)")

                        #Skip rows without flow value
                        try:
                            float(cols[1].replace(u',', u'.'))
                        except ValueError:
                            continue

                        date = datetime.strptime(cols[0], dateformat)

                        #TODO: These checks are not implemented as a dialog yet.
                        if begindate is not None:
                            if date < begindate:
                                continue
                        if enddate is not None:
                            if date > enddate:
                                continue

                        printrow = [datetime.strftime(date,u'%Y-%m-%d %H:%M:%S')]
                        printrow.extend([col.replace(u',', u'.') for col in cols[1:]])
                        filedata.append(printrow)

        if len(filedata) == 0:
            return utils.ask_user_about_stopping("Failure, parsing failed for file " + path + "\nNo valid data found!\nDo you want to stop the import? (else it will continue with the next file)")

        answer = None
        if ask_for_names:
            answer = utils.filter_nonexisting_values_and_ask([[u'obsid'], [obsid]], u'obsid', existing_obsids, try_capitalize=False)
        else:
            if obsid not in existing_obsids:
                answer = utils.filter_nonexisting_values_and_ask([[u'obsid'], [obsid]], u'obsid', existing_obsids, try_capitalize=True)

        if answer == u'cancel':
            return answer

        if answer is not None:
            if isinstance(answer, (list, tuple)):
                if len(answer) > 1:
                    obsid = answer[1][0]
                else:
                    return u'skip'

        header.append(u'obsid')
        for row in filedata:
            row.append(obsid)

        if u'Conductivity[mS/cm]' not in header:
            header.append(u'Conductivity[mS/cm]')
            for row in filedata:
                row.append(u'')

        translation_dict_in_order = OrderedDict([(u'obsid', u'obsid'),
                                                 (u'Date/time', u'date_time'),
                                                 (u'Water head[cm]', u'head_cm'),
                                                 (u'Temperature[°C]', u'temp_degc'),
                                                 (u'Conductivity[mS/cm]', u'cond_mscm')])

        try:
            translated_header = [translation_dict_in_order[headername] for headername in header]
        except KeyError:
            utils.MessagebarAndLog.critical(bar_msg=u"Failure during import. See log for more information", log_msg=u"Failure, the file " + utils.returnunicode(path) + u"\ndid not have the correct headers and will not be imported.\nMake sure its barocompensated!\nSupported headers are obsid, Date/time, Water head[cm], Temperature[°C] and optionally Conductivity[mS/cm].")
            return u'skip'

        filedata.reverse()
        filedata.append(translated_header)
        filedata.reverse()

        sorted_filedata = [[row[translated_header.index(v)] for v in translation_dict_in_order.values()] for row in filedata]

        return sorted_filedata

    @staticmethod
    def filter_dates_from_filedata(file_data, obsid_last_imported_dates, obsid_header_name=u'obsid', date_time_header_name=u'date_time'):
        """
        :param file_data: a list of lists like [[u'obsid', u'date_time', ...], [obsid1, date_time1, ...]]
        :param obsid_last_imported_dates: a dict like {u'obsid1': last_date_in_db, ...}
        :param obsid_header_name: the name of the obsid header
        :param date_time_header_name: the name of the date_time header
        :return: A filtered list with only dates after last date is included for each obsid.

        >>> midv_data_importer.filter_dates_from_filedata([['obsid', 'date_time'], ['obs1', '2016-09-28'], ['obs1', '2016-09-29']], {'obs1': [('2016-09-28', )]})
        [['obsid', 'date_time'], ['obs1', '2016-09-29']]
        """
        if len(file_data) == 1:
            return file_data

        obsid_idx = file_data[0].index(obsid_header_name)
        date_time_idx = file_data[0].index(date_time_header_name)
        filtered_file_data = [row for row in file_data[1:] if datestring_to_date(row[date_time_idx]) > datestring_to_date(obsid_last_imported_dates.get(row[obsid_idx], [(u'0001-01-01 00:00:00',)])[0][0])]
        filtered_file_data.reverse()
        filtered_file_data.append(file_data[0])
        filtered_file_data.reverse()
        return filtered_file_data

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

    def qgiscsv2sqlitetable(self): # general importer
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'."""
        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        ExistingNames= db_utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]
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
        db_utils.sql_alter_db("""CREATE table "%s" (%s)""" % (self.temptableName, fields)) # Create a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis csvlayer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        for feature in self.csvlayer.getFeatures():
            values_perso=[]
            for attr in feature.attributes():
                #If automatic convertion from PyQt4.QtCore.QVariant did not work, it must be done manually
                if isinstance(attr, PyQt4.QtCore.QVariant):
                    attr = attr.toPyObject()
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
        self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]
        if len(self.columns)==4 or len(self.columns)==5:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                db_utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null""" % (self.temptableName, column[1], column[1]))
            #THE METHOD ABOVE NEEDS REVISON
            # Add level_masl column and fill with data
            db_utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double""" % self.temptableName)
            db_utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """ % (self.temptableName, self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]

            #Some statistics
            self.RecordsBefore = db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
            self.RecordsToImport = db_utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)""" % (self.columns[0][1], self.temptableName))[1]
            self.RecordsInFile = db_utils.sql_load_fr_db("""SELECT Count(*) FROM %s""" % self.temptableName)[1]

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.Askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?""" % (self.RecordsInFile[0][0] - self.RecordsToImport[0][0]), "Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates
            return 1
        else:
            return 0

    def SanityCheckVacuumDB(self):
        sanity = utils.Askuser("YesNo", """It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""", 'Vacuum the database?')
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            db_utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()


class wlvlloggimportclass():
    """ Note, thes class is a quickfix and have been incorporated into the multi-import class as wlvllogg_import"""
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
                self.goalcolumns = db_utils.sql_load_fr_db("""PRAGMA table_info(w_levels_logger)""")[1]
                if len(self.columns) == 5: #No conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[3][1],self.columns[0][1],self.columns[1][1],self.columns[2][1])
                    sqlpart3 = """ FROM %s"""%(self.temptableName)
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    db_utils.sql_alter_db(sql)
                    #utils.pop_up_info(sql, "debug") #debug
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                elif len(self.columns) ==6: #Including conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1],self.goalcolumns[4][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[4][1],self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1])
                    sqlpart3 = """ FROM %s"""%(self.temptableName)
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    db_utils.sql_alter_db(sql)
                    #utils.pop_up_info(sql, "debug") #debug
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
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

            db_utils.sql_alter_db("DROP table %s" % self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            sanity = utils.Askuser("YesNo", """It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""", 'Vacuum the database?')
            if sanity.result == 1:
                PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
                db_utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
                PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def selectcsv(self):
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!!
        try:#MacOSX fix2
            localencoding = utils.getcurrentlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,utils.getcurrentlocale()[1])
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
        ExistingNames= db_utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]
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
        db_utils.sql_alter_db(sql) #NO PKUID, Number of fields exactly the same as imported csv file
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
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value.toString()) for value in values_perso])) # NO PKUID
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
        self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]
        if len(self.columns)==3 or len(self.columns)==4:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                db_utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null""" % (self.temptableName, column[1], column[1]))
            #THE METHOD ABOVE NEEDS REVISON

            #Fix date_time format from "yyyy/mm/dd hh:mm:ss" to "yyyy-mm-dd hh:mm:ss"
            db_utils.sql_alter_db("""UPDATE "%s" SET "%s" = REPLACE("%s",'/','-')""" % (self.temptableName, str(self.columns[0][1]), str(self.columns[0][1])))
            # Add obsid column and fill with data
            db_utils.sql_alter_db("""ALTER table "%s" ADD COLUMN obsid text""" % self.temptableName)
            db_utils.sql_alter_db("""UPDATE "%s" SET obsid = "%s" """ % (self.temptableName, self.obsid[0]))
            # Add level_masl column and fill with data
            db_utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double""" % self.temptableName)
            db_utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """ % (self.temptableName, self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = db_utils.sql_load_fr_db("""PRAGMA table_info(%s)""" % self.temptableName)[1]

            #Some statistics
            self.RecordsBefore = db_utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
            self.RecordsToImport = db_utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)""" % (self.columns[0][1], self.temptableName))[1]
            self.RecordsInFile = db_utils.sql_load_fr_db("""SELECT Count(*) FROM %s""" % self.temptableName)[1]
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.Askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?""" % (self.RecordsInFile[0][0] - self.RecordsToImport[0][0]), "Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates
            return 1
        else:
            return 0













