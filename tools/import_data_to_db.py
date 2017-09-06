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
import PyQt4
import copy
import io
import os
import qgis.utils
from collections import OrderedDict
from datetime import datetime
from functools import partial
from operator import itemgetter
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
from qgis.core import *

import PyQt4.QtCore
import PyQt4.QtGui
from PyQt4.QtCore import QCoreApplication

import midvatten_utils as utils
from midvatten_utils import Cancel, returnunicode as ru

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
        self.charsetchoosen = ''
        self.csvlayer = None
        self.foreign_keys_import_question = None

    def general_csv_import(self, goal_table=None):
        """General method for importing an sqlite table into a goal_table

            self.temptablename must be the name of the table containing the new data to import.

        :param goal_table:
        :return:
        """
        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'\nImport to %s starting\n--------------------'))%goal_table)

        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.status = 'False' #True if upload to sqlite and cleaning of data succeeds
        self.temptablename = goal_table + u'_temp'

        if goal_table is None:
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate(u'midv_data_importer', u'Import error: No goal table given!'))
            self.status = 'False'
            self.drop_temptable()
            return

        if not self.csvlayer:
            self.csvlayer = self.get_csvlayer()  # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer == u'cancel' or not self.csvlayer:
            self.status = 'True'
            self.drop_temptable()
            return

        upload = self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
        if isinstance(upload, Cancel):
            self.status = 'False'
            self.drop_temptable()
            return
            
        recsinfile = utils.sql_load_fr_db(u'select count(*) from "%s"'%self.temptablename)[1][0][0]

        table_info = utils.sql_load_fr_db(u'''PRAGMA table_info("%s")'''%goal_table)[1]
        if not table_info:
            utils.MessagebarAndLog.critical(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'The table %s did not exist. Update the database to latest version.'))%goal_table)
            self.status = 'False'
            self.drop_temptable()
            return

        #POINT and LINESTRING must be cast as BLOB. So change the type to BLOB.
        column_headers_types = dict([(row[1], row[2]) if row[2] not in (u'POINT', u'LINESTRING') else (row[1], u'BLOB') for row in table_info])
        primary_keys = [row[1] for row in table_info if int(row[5])]        #Not null columns are allowed if they have a default value.
        not_null_columns = [row[1] for row in table_info if int(row[3]) and row[4] is None]
        #Only use the columns that exists in the goal table.
        existing_columns = [x[1] for x in utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptablename)[1] if x[1] in column_headers_types]
        missing_columns = [column for column in not_null_columns if column not in existing_columns]

        if missing_columns:
            utils.MessagebarAndLog.critical(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Required columns %s are missing for table %s'))%(u', '.join(missing_columns), goal_table), duration=999)
            self.status = 'False'
            self.drop_temptable()
            return

        #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
        nr_before = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptablename))[1][0][0]
        if u'date_time' in primary_keys:
            self.delete_existing_date_times_from_temptable(primary_keys, goal_table)
        nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptablename))[1][0][0]

        nr_same_date = nr_after - nr_before
        if nr_same_date > 0:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported. %s rows remain.'))%(str(nr_same_date), str(nr_after)))
        if not nr_after > 0:
            utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg())
            self.status = 'False'
            self.drop_temptable()
            return

        # Import foreign keys in some special cases
        nr_before = nr_after
        foreign_keys = utils.get_foreign_keys(goal_table)
        force_import_of_foreign_keys_tables = [u'zz_flowtype', u'zz_staff', u'zz_meteoparam']

        for fk_table, from_to_fields in foreign_keys.iteritems():
            if self.foreign_keys_import_question is None:
                stop_question = utils.askuser(u"YesNo",
                                              ru(QCoreApplication.translate(u'midv_data_importer', u"""Please note!\nForeign keys will be imported silently into "%s" if needed. \n\nProceed?""")) % (
                                              u', '.join(
                                                  force_import_of_foreign_keys_tables)),
                                              ru(QCoreApplication.translate(u'midv_data_importer', u"Info!")))
                if stop_question.result == 0:  # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    self.drop_temptable()
                    return Cancel()
                else:
                    self.foreign_keys_import_question = 1

            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]
            if fk_table in force_import_of_foreign_keys_tables:
                if not all([_from in existing_columns for _from in from_list]):
                    continue
                nr_fk_before = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%fk_table)[1][0][0]
                _table_info = utils.sql_load_fr_db(u'''PRAGMA table_info("%s")'''% fk_table)[1]
                _column_headers_types = dict([(row[1], row[2]) for row in _table_info])
                sql = ur"""INSERT OR IGNORE INTO %s (%s) select distinct %s from %s as b where %s"""%(fk_table,
                                                                                             u', '.join([u'"{}"'.format(k) for k in to_list]),
                                                                                             u', '.join([u'''CAST("b"."%s" as "%s")'''%(k, _column_headers_types[to_list[idx]]) for idx, k in enumerate(from_list)]),
                                                                                             self.temptablename,
                                                                                             u' and '.join([u''' "b"."{}" IS NOT NULL and "b"."{}" != '' and "b"."{}" != ' ' '''.format(k, k, k) for k in from_list]))

                utils.sql_alter_db(sql)

                nr_fk_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%fk_table)[1][0][0]

                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'In total %s rows were imported to foreign key table %s while importing to %s.'))%(str(nr_fk_after - nr_fk_before), fk_table, goal_table))
            else:
                #Else check if there are foreign keys blocking the import and skip those rows
                existing_keys = utils.sql_load_fr_db(u'select distinct "%s" from "%s"'%(u', '.join(to_list),
                                                                                        fk_table))[1]
                new_keys = utils.sql_load_fr_db(u'select distinct "%s" from "%s"'%(u', '.join(from_list),
                                                                                   self.temptablename))[1]
                missing_keys = [keys for keys in new_keys if keys not in existing_keys]

                if missing_keys:
                    utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg(),
                                                   log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'There was %s entries where foreign keys were missing from %s which will not be imported:\n%s'))%(str(len(missing_keys)), fk_table, u'\n'.join([u', '.join(f) for f in missing_keys])),
                                                   duration=999)

                    utils.sql_alter_db(u'delete from "%s" where %s in (%s)'%(self.temptablename,
                                                                             u' || '.join(from_list),
                                                                             u', '.join([u"'{}'".format(u''.join([u'NULL' if k is None else k for k in mk])) for mk in missing_keys])))

        nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"''' % (self.temptablename))[1][0][0]
        nr_after_foreign_keys = nr_before - nr_after
        if nr_after_foreign_keys > 0:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer',u'In total "%s" rows were deleted due to foreign keys restrictions and "%s" rows remain.'))%(str(nr_after_foreign_keys), str(nr_after)))
            
        if not nr_after > 0:
            utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg())
            self.status = 'False'
            self.drop_temptable()
            return

        #Special cases for some tables
        if goal_table == u'stratigraphy':
            self.check_and_delete_stratigraphy(existing_columns)
        if goal_table in (u'obs_lines', u'obs_points'):
            self.calculate_geometry(existing_columns, goal_table)
        if self.status == 'False':
            self.drop_temptable()
            return

        #Finally import data:
        nr_failed_import = recsinfile - nr_after
        if nr_failed_import > 0:
            stop_question = utils.askuser(u"YesNo", ru(QCoreApplication.translate(u'midv_data_importer', u"""Please note!\nThere are %s rows in your data that can not be imported!\nDo you really want to import the rest?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?"""))%(str(nr_failed_import)), ru(QCoreApplication.translate(u'midv_data_importer', "Warning!")))
            if stop_question.result == 0:      # if the user wants to abort
                self.status = 'False'
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                self.drop_temptable()
                return Cancel()   # return simply to stop this function

        sql_list = [u"""INSERT INTO "%s" ("""%goal_table]
        sql_list.append(u', '.join([u'"{}"'.format(k) for k in sorted(existing_columns)]))
        sql_list.append(u""") SELECT """)
        sql_list.append(u', '.join([u"""(case when ("%s"!='' and "%s"!=' ' and "%s" IS NOT NULL) then CAST("%s" as "%s") else null end)"""%(colname, colname, colname, colname, column_headers_types[colname]) for colname in sorted(existing_columns)]))
        sql_list.append(u"""FROM %s"""%(self.temptablename))
        sql = u''.join(sql_list)

        recsbefore = utils.sql_load_fr_db(u'select count(*) from "%s"' % (goal_table))[1][0][0]

        try:
            utils.sql_alter_db(sql.encode(u'utf-8'))
        except Exception, e:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'INSERT failed while importing to %s. Using INSERT OR IGNORE instead. Msg:\n'))%goal_table + str(e))
            sql = sql.replace(u'INSERT', u'INSERT OR IGNORE')
            try:
                utils.sql_alter_db(sql.encode(u'utf-8'))
            except Exception, e:
                utils.MessagebarAndLog.critical(
                    bar_msg=self.import_error_msg(),
                    log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Sql\n%s  failed.\nMsg:\n%s'))%(sql, str(e)),
                    duration=999)
                self.status = 'False'
                self.drop_temptable()
                return

        recsafter = utils.sql_load_fr_db(u'select count(*) from "%s"' % (goal_table))[1][0][0]
        nr_imported = recsafter - recsbefore
        nr_excluded = recsinfile - nr_imported

        utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'%s rows imported and %s excluded for table %s. See log message panel for details'))%(nr_imported, nr_excluded, goal_table))
        utils.MessagebarAndLog.info(log_msg=u'--------------------')
        self.status = 'True'
        self.drop_temptable() # finally drop the temporary table
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def send_file_data_to_importer(self, file_data, importer, cleaning_function=None):
        self.csvlayer = None
        if len(file_data) < 2:
            utils.MessagebarAndLog.info(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Import failed only a header was sent to importer')))
            return

        if cleaning_function is not None:
            file_data = cleaning_function(file_data)

        #QgsVectorLayer(path, "temporary_csv_layer", "ogr") doesn't work if the file only has one column, so an empty column has to be added
        if len(file_data[0]) == 1:
            [row.append(u'') for row in file_data]

        file_string = utils.lists_to_string(file_data, quote=True)

        with utils.tempinput(file_string, charset=u'utf_8') as csvpath:
            self.charsetchoosen = u'UTF-8'
            csvlayer = self.csv2qgsvectorlayer(csvpath)
            if not csvlayer:
                utils.MessagebarAndLog.critical(ru(QCoreApplication.translate(u'midv_data_importer', u"Import error: Creating csvlayer failed!")))
                return
            self.csvlayer = csvlayer
            answer = importer()
            return answer

    def get_csvlayer(self): # general importer
        """Select the csv file, user must also tell what charset to use"""
        self.charsetchoosen = utils.ask_for_charset()
        if not self.charsetchoosen:
            return u'cancel'

        csvpath = utils.select_files(only_one_file=True, extension="csv (*.csv)")
        if not csvpath:
            return u'cancel'

        return self.csv2qgsvectorlayer(csvpath[0])

    def csv2qgsvectorlayer(self, path):
        """ Creates QgsVectorLayer from a csv file """
        if not path:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Failure, no csv file was selected.')))
            return False

        csvlayer = QgsVectorLayer(path, "temporary_csv_layer", "ogr")

        if not csvlayer.isValid():
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Failure, Impossible to Load File in QGis:\n%s'))%str(path))
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return False
        csvlayer.setProviderEncoding(str(self.charsetchoosen))
        return csvlayer

    def qgiscsv2sqlitetable(self): # general importer
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'.

        :param column_header_translation_dict: a dict like {u'column_name_in_csv: column_name_in_db}

        """

        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        existing_names= [str(existing_name[0]) for existing_name in utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]]
        while self.temptablename in existing_names: #this should only be needed if an earlier import failed. if so, propose to rename the temporary import-table
            reponse = PyQt4.QtGui.QMessageBox.question(None, ru(QCoreApplication.translate(u'midv_data_importer', "Warning - Table name confusion!")), ru(QCoreApplication.translate(u'midv_data_importer', '''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''))%(self.temptablename,self.temptablename,self.temptablename), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
            if reponse == PyQt4.QtGui.QMessageBox.Yes:
                self.temptablename = '%s_2'%self.temptablename
            else:
                return Cancel()

        #Get all fields with corresponding types for the csv-csvlayer in qgis
        fields=[]
        fieldsNames=[]
        provider=self.csvlayer.dataProvider()
        for name in provider.fields(): #fix field names and types in temporary table
            fldName = unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName = '%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not a .csvt file is defined beside the imported file.
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool, PyQt4.QtCore.QVariant.Int, PyQt4.QtCore.QVariant.LongLong, PyQt4.QtCore.QVariant.UInt, PyQt4.QtCore.QVariant.ULongLong):  # field type is integer
                fldType='integer'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is double
                fldType='real'
            else: # if field type is not recognized by qgis
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())

        #Create the import-table in DB
        fields=','.join(fields)
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.temptablename, fields)) # Create a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
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
                #curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptablename,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso]))
                try:
                    curs.execute("""INSERT INTO %s VALUES (%s)"""%(self.temptablename,','.join('?'*len(values_perso))),tuple([value for value in values_perso])) # Assuming value is unicode, send it as such to sqlite
                except:
                    curs.execute("""INSERT INTO %s VALUES (%s)"""%(self.temptablename,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #in case of errors, the value must be a byte string, then try to convert to unicode
                self.status = 'True'
            else: #no attribute Datas
                utils.MessagebarAndLog.critical(bar_msg=u'No data found!! No data will be imported!!')
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def delete_existing_date_times_from_temptable(self, primary_keys, goal_table):
        """
        Deletes duplicate times
        :param primary_keys: a table like ['obsid', 'date_time', ...]
        :param goal_table: a string like 'w_levels'
        :return: None. Alters the temptable self.temptablename

        If date 2016-01-01 00:00:00 exists for obsid1, then 2016-01-01 00:00 will not be imported for obsid1.
        (and 2016-01-01 00 will block 2016-01-01 00:00)

        If date 2016-01-01 00:00 exists for obsid1, then 2016-01-01 00:00:XX will not be imported for obsid1.
        (and 2016-01-01 00 will block 2016-01-01 00:XX)
        (but 2016-01-01 00 will not block 2016-01-01 00:00:XX, inconsistently)

        The function uses all primary keys to identify unique combinations, so different parameters will not block each other.
        """
        pks = [pk for pk in primary_keys if pk != u'date_time']
        pks.append(u'date_time')

        #TODO: Maybe the length should be checked so that the test is only made for 2016-01-01 00:00 and 2016-01-01 00:00:00?

        #Delete records that have the same date_time but with :00 at the end. (2016-01-01 00:00 will not be imported if 2016-01-01 00:00:00 exists
        pks_and_00 = [u'"{}"'.format(pk) for pk in pks]
        pks_and_00.append(u"':00'")
        sql = u'''delete from "%s" where %s in (select %s from "%s")'''%(self.temptablename,
                                                                                          u' || '.join(pks_and_00),
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          goal_table)
        utils.sql_alter_db(sql)

        # Delete records from temptable that have date_time yyyy-mm-dd HH:MM:XX when yyyy-mm-dd HH:MM exist.
        #delete from temptable where SUBSTR("obsid" || "date_time", 1, length("obsid" || "date_time") - 3) in (select "obsid" || "date_time" from goaltable)
        sql = u'''delete from "%s" where SUBSTR(%s, 1, length(%s) - 3) in (select %s from "%s")'''%(self.temptablename,
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          goal_table)
        utils.sql_alter_db(sql)

    def calculate_geometry(self, existing_columns, table_name):
        # Calculate the geometry
        sql = r"""SELECT srid FROM geometry_columns where f_table_name = '%s'"""%table_name
        SRID = str((utils.sql_load_fr_db(sql)[1])[0][0])  # THIS IS DUE TO WKT-import of geometries below
        if u'WKT' in existing_columns:
            geocol = u'WKT'
        elif u'geometry' in existing_columns:
            geocol = u'geometry'
        else:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'%s without geometry imported'))%table_name)
            return None

        sql = u"""update "%s" set geometry=GeomFromText(%s,%s)"""%(self.temptablename, geocol, SRID)
        utils.sql_alter_db(sql)

    def check_and_delete_stratigraphy(self, existing_columns):
        if all([u'stratid' in existing_columns, u'depthtop' in existing_columns, u'depthbot' in existing_columns]):
            skip_obsids = []
            obsid_strat = utils.get_sql_result_as_dict(u'select obsid, stratid, depthtop, depthbot from "%s"'%self.temptablename)[1]
            for obsid, stratid_depthbot_depthtop  in obsid_strat.iteritems():
                #Turn everything to float
                try:
                    strats = [[float(x) for x in y] for y in stratid_depthbot_depthtop]
                except ValueError as e:
                    utils.MessagebarAndLog.critical(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'ValueError: %s. Obsid "%s", stratid: "%s", depthbot: "%s", depthtop: "%s"'))%(str(e), obsid, stratid_depthbot_depthtop[0], stratid_depthbot_depthtop[1], stratid_depthbot_depthtop[2]))
                    self.status = 'False'
                    return

                sorted_strats = sorted(strats, key=itemgetter(0))
                stratid_idx = 0
                depthtop_idx = 1
                depthbot_idx = 2
                for index in xrange(len(sorted_strats)):
                    if index == 0:
                        continue
                    #Check that there is no gap in the stratid:
                    if float(sorted_strats[index][stratid_idx]) - float(sorted_strats[index - 1][stratid_idx]) != 1:
                        utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'The obsid %s will not be imported due to gaps in stratid'))%obsid)
                        skip_obsids.append(obsid)
                        break
                    #Check that the current depthtop is equal to the previous depthbot
                    elif sorted_strats[index][depthtop_idx] != sorted_strats[index - 1][depthbot_idx]:
                        utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'The obsid %s will not be imported due to gaps in depthtop/depthbot'))%obsid)
                        skip_obsids.append(obsid)
                        break
            if skip_obsids:
                utils.sql_alter_db(u'delete from "%s" where obsid in (%s)'%(self.temptablename, u', '.join([u'"{}"'.format(obsid) for obsid in skip_obsids]) ))

    def drop_temptable(self):
        try:
            utils.sql_alter_db(u"DROP table %s" % self.temptablename)  # finally drop the temporary table
        except:
            pass

    def SanityCheckVacuumDB(self):
        sanity = utils.askuser("YesNo",ru(QCoreApplication.translate(u'midv_data_importer', """It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""")), ru(QCoreApplication.translate(u'midv_data_importer', 'Vacuum the database?')))
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            
    def import_error_msg(self):
        return ru(QCoreApplication.translate(u'midv_data_importer', u'Import error, see log message panel'))







