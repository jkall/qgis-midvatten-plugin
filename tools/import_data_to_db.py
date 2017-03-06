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
import qgis.utils
from collections import OrderedDict
from datetime import datetime
from functools import partial
from operator import itemgetter
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
from qgis.core import *
from pyspatialite.dbapi2 import OperationalError, IntegrityError
from psycopg2 import IntegrityError as PostGisIntegrityError

import PyQt4.QtCore
import PyQt4.QtGui
import db_utils

import midvatten_utils as utils
from midvatten_utils import Cancel
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

    def general_import(self, goal_table=None, file_data=None):
        """General method for importing an sqlite table into a goal_table

            self.temptableName must be the name of the table containing the new data to import.

        :param goal_table:
        :return:
        """
        if file_data is None or not file_data:
            self.status = 'True'
            return
        utils.MessagebarAndLog.info(log_msg=u'\nImport to %s starting\n--------------------'%goal_table)
        detailed_msg_list = []
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.status = 'False' #True if upload to sqlite and cleaning of data succeeds
        self.temptable_name = goal_table + u'_temp'
        if goal_table is None:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error: No goal table given!')
            self.status = 'False'
            return
        dbconnection = db_utils.DbConnectionManager()
        self.list_to_table(dbconnection, file_data)
        #self.qgiscsv2sqlitetable(dbconnection) #loads qgis csvlayer into sqlite table
        recsinfile = dbconnection.execute_and_fetchall(sql=u'select count(*) from %s'%self.temptable_name)[0][0]
        table_info = db_utils.db_tables_columns_info(table=goal_table, dbconnection=dbconnection)[goal_table]
        #POINT and LINESTRING must be cast as BLOB. So change the type to BLOB.
        column_headers_types = db_utils.convert_some_types_to_byte(dbconnection, table_info)
        primary_keys = [row[1] for row in table_info if int(row[5])]        #Not null columns are allowed if they have a default value.
        not_null_columns = [row[1] for row in table_info if int(row[3]) and row[4] is None]
        #Only use the columns that exists in the goal table.
        existing_columns = [col for col in file_data[0] if col in column_headers_types]
        missing_columns = [column for column in not_null_columns if column not in existing_columns]

        if missing_columns:
            utils.MessagebarAndLog.critical(bar_msg=u'Error: Import failed, see log message panel', log_msg=u'Required columns ' + u', '.join(missing_columns) + u' are missing for table ' + goal_table, duration=999)
            self.status = False
            return

        #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
        nr_before = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % (self.temptable_name))[0][0]
        if u'date_time' in primary_keys:
            self.delete_existing_date_times_from_temptable(primary_keys, goal_table, dbconnection)
        nr_after = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % (self.temptable_name))[0][0]

        nr_same_date = nr_after - nr_before
        self.check_remaining(nr_before, nr_after, u"Import warning, see log message panel", u'In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported.'%(str(nr_same_date)))
        if not self.status:
            return

        # Import foreign keys in some special cases
        nr_before = nr_after
        foreign_keys = db_utils.get_foreign_keys(goal_table, dbconnection=dbconnection)
        force_import_of_foreign_keys_tables = [u'zz_flowtype', u'zz_staff', u'zz_meteoparam']
        if self.foreign_keys_import_question is None:
            stop_question = utils.Askuser(u"YesNo", u"""Please note!\nForeign keys will be imported silently into "%s" if needed. \n\nProceed?""" % (u', '.join(force_import_of_foreign_keys_tables)), u"Info!")
            if stop_question.result == 0:      # if the user wants to abort
                self.status = 'False'
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                dbconnection.closedb()
                return Cancel()   # return simply to stop this function
            else:
                self.foreign_keys_import_question = 1

        for fk_table, from_to_fields in foreign_keys.iteritems():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]
            if fk_table in force_import_of_foreign_keys_tables:
                if not all([_from in existing_columns for _from in from_list]):
                    continue
                nr_fk_before = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % fk_table)[0][0]
                _table_info = db_utils.db_tables_columns_info(table=fk_table, dbconnection=dbconnection)
                _column_headers_types = dict([(row[1], row[2]) for row in _table_info])
                sql = ur"""INSERT INTO %s (%s) select distinct %s from %s as b where %s"""%(fk_table,
                                                                                             u', '.join(to_list),
                                                                                             u', '.join([u'''CAST(b.%s as %s)'''%(k, _column_headers_types[to_list[idx]]) for idx, k in enumerate(from_list)]),
                                                                                             self.temptable_name,
                                                                                             u' and '.join([u''' b.{} IS NOT NULL and b.{} != '' and b.{} != ' ' '''.format(k, k, k) for k in from_list]))
                try:
                    dbconnection.execute(sql)
                except Exception, e:
                    sql = db_utils.replace_insert_sql_on_conflict(dbconnection, sql)
                    detailed_msg_list.append(u'INSERT failed while importing to %s. Using INSERT OR IGNORE instead.\nMsg: '%fk_table + str(e))
                    dbconnection.execute(sql)

                nr_fk_after = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % fk_table)[0][0]

                detailed_msg_list.append(u'In total ' + str(nr_fk_after - nr_fk_before) + u' rows were imported to foreign key table ' + fk_table + u' while importing to ' + goal_table + u'.')
            else:
                #Else check if there are foreign keys blocking the import and skip those rows
                existing_keys = dbconnection.execute_and_fetchall(u'select distinct %s from %s' % (u', '.join(to_list), fk_table))
                new_keys = dbconnection.execute_and_fetchall(u'select distinct "%s" from %s' % (u', '.join(from_list), self.temptable_name))
                missing_keys = [keys for keys in new_keys if keys not in existing_keys]

                if missing_keys:
                    utils.MessagebarAndLog.warning(bar_msg=u'Import error, see log message panel',
                                                   log_msg=u'There was ' + str(len(missing_keys)) +
                                                   u'entries where foreign keys were missing from ' + fk_table +
                                                   u' which will not be imported:\n' + u'\n'.join([u', '.join(f) for f in missing_keys]),
                                                   duration=999)

                    dbconnection.execute(u'delete from %s where %s in (%s)' % (self.temptable_name,
                                                                             u' || '.join(from_list),
                                                                             u', '.join([u"'{}'".format(u''.join([u'NULL' if k is None else k for k in mk])) for mk in missing_keys])))

        nr_after = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % (self.temptable_name))[0][0]
        nr_after_foreign_keys = nr_before - nr_after
        self.check_remaining(nr_before, nr_after, u"Import warning, see log message panel", u'In total "%s" rows were deleted due to foreign keys restrictions and "%s" rows remain.'%(str(nr_after_foreign_keys), str(nr_after)))
        if not self.status:
            return

        #Special cases for some tables
        if goal_table == u'stratigraphy':
            self.check_and_delete_stratigraphy(existing_columns, dbconnection)
        if goal_table in (u'obs_lines', u'obs_points'):
            self.calculate_geometry(existing_columns, goal_table, dbconnection)

        #Finally import data:
        nr_failed_import = recsinfile - nr_after
        if nr_failed_import > 0:
            stop_question = utils.Askuser(u"YesNo", u"""Please note!\nThere are %s rows in your data that can not be imported!\nDo you really want to import the rest?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?""" % (str(nr_failed_import)), "Warning!")
            if stop_question.result == 0:      # if the user wants to abort
                self.status = 'False'
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return Cancel()   # return simply to stop this function

        sql_list = [u"""INSERT INTO %s ("""%goal_table]
        sql_list.append(u', '.join(sorted(existing_columns)))
        sql_list.append(u""") SELECT """)
        sql_list.append(u', '.join([u"""(CASE WHEN (%s !='' AND %s !=' ' AND %s IS NOT NULL) THEN CAST(%s AS %s) ELSE NULL END)"""%(colname, colname, colname, colname, column_headers_types[colname]) for colname in sorted(existing_columns)]))
        sql_list.append(u"""FROM %s""" % (self.temptable_name))
        sql = u''.join(sql_list)
        recsbefore = dbconnection.execute_and_fetchall(u'select count(*) from %s' % (goal_table))[0][0]

        try:
            dbconnection.execute(sql) #.encode(u'utf-8'))
        except Exception, e:
            detailed_msg_list.append(u'INSERT failed while importing to %s. Using INSERT OR IGNORE instead.\nMsg: '%goal_table + str(e))
            sql = db_utils.replace_insert_sql_on_conflict(dbconnection, sql)
            try:
                dbconnection.execute(sql) #.encode(u'utf-8'))
            except Exception, e:
                utils.MessagebarAndLog.critical(
                    bar_msg=u'Error, import failed, see log message panel',
                    log_msg=u'Sql\n' + sql + u' failed.\nMsg:\n' + str(e),
                    duration=999)
                self.status = 'False'
                return
        recsafter = dbconnection.execute_and_fetchall(u'select count(*) from %s' % (goal_table))[0][0]

        nr_imported = recsafter - recsbefore

        #Stats and messages after import
        if recsinfile is None:
            recsinfile = self.recstoimport
        if recsafter is None:
            recsafter = self.recsafter
        if recsbefore is None:
            recsbefore = self.recsbefore
        NoExcluded = recsinfile - (recsafter - recsbefore)

        if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
            detailed_msg_list.append(u'In total %s rows were not imported to %s. Probably due to a primary key combination already existing in the database.'%(str(NoExcluded), goal_table))

        detailed_msg_list.append(u'--------------------')
        detailed_msg = u'\n'.join(detailed_msg_list)
        utils.MessagebarAndLog.info(bar_msg=u'%s rows imported and %s excluded for table %s. See log message panel for details'%(nr_imported, NoExcluded, goal_table), log_msg=detailed_msg)
        self.status = 'True'
        dbconnection.commit_and_closedb()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def list_to_table(self, dbconnection, file_data):
        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        existing_names = db_utils.tables_columns(dbconnection=dbconnection).keys()
        while self.temptable_name in existing_names: #this should only be needed if an earlier import failed. if so, propose to rename the temporary import-table
            reponse = PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?''' % (self.temptable_name, self.temptable_name, self.temptable_name), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
            if reponse == PyQt4.QtGui.QMessageBox.Yes:
                self.temptable_name = '%s_2' % self.temptable_name
            else:
                return None
        fieldnames_types = [u'{} TEXT'.format(field_name) for field_name in file_data[0]]
        if dbconnection.dbtype == u'spatialite':
            self.temptable_name = u'mem.' + self.temptable_name
            dbconnection.execute(u"""ATTACH DATABASE ':memory:' AS mem""")
            dbconnection.execute(u"""CREATE table %s (%s)""" % (self.temptable_name, u', '.join(fieldnames_types)))
        else:
            dbconnection.execute(u"""CREATE TEMPORARY table %s (%s)"""%(self.temptable_name, u', '.join(fieldnames_types)))

        for row in file_data[1:]:
            if dbconnection.dbtype == u'spatialite':
                dbconnection.cursor.execute(u"""INSERT INTO %s VALUES (%s)""" % (self.temptable_name, u', '.join(u'?' * len(row))), tuple(row))
            else:
                dbconnection.cursor.execute(u"""INSERT INTO %s VALUES (%s)""" % (self.temptable_name, u', '.join([u'%s' for x in xrange(len(row))])), tuple(row))
        dbconnection.commit()

    def delete_existing_date_times_from_temptable(self, primary_keys, goal_table, dbconnection):
        """
        Deletes duplicate times
        :param primary_keys: a table like ['obsid', 'date_time', ...]
        :param goal_table: a string like 'w_levels'
        :return: None. Alters the temptable self.temptableName

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
        pks_and_00 = list(pks)
        pks_and_00.append(u"':00'")
        sql = u'''delete from %s where %s in (select %s from %s)'''%(self.temptable_name,
                                                                                          u' || '.join(pks_and_00),
                                                                                          u' || '.join(pks),
                                                                                          goal_table)
        dbconnection.execute(sql)

        # Delete records from temptable that have date_time yyyy-mm-dd HH:MM:XX when yyyy-mm-dd HH:MM exist.
        #delete from temptable where SUBSTR("obsid" || "date_time", 1, length("obsid" || "date_time") - 3) in (select "obsid" || "date_time" from goaltable)
        sql = u'''delete from %s where SUBSTR(%s, 1, length(%s) - 3) in (select %s from %s)'''%(self.temptable_name,
                                                                                          u' || '.join(pks),
                                                                                          u' || '.join(pks),
                                                                                          u' || '.join(pks),
                                                                                          goal_table)
        dbconnection.execute(sql)

    def check_remaining(self, nr_before, nr_after, bar_msg, log_msg):
        if nr_after == 0:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, nothing imported.')
            self.status = False
        elif nr_before > nr_after:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)

    def calculate_geometry(self, existing_columns, table_name, dbconnection):
        # Calculate the geometry
        # THIS IS DUE TO WKT-import of geometries below
        SRID = dbconnection.execute_and_fetchall(u"""SELECT srid FROM geometry_columns where f_table_name = '%s'""" % table_name)[0][0]
        if u'WKT' in existing_columns:
            geocol = u'WKT'
        elif u'geometry' in existing_columns:
            geocol = u'geometry'
        else:
            utils.MessagebarAndLog.warning(bar_msg=u'%s without geometry imported'%table_name)
            return None

        sql = u"""update %s set geometry=ST_GeomFromText(%s,%s)"""%(self.temptable_name, geocol, SRID)
        dbconnection.execute(sql)

    def check_and_delete_stratigraphy(self, existing_columns, dbconnection):
        if all([u'stratid' in existing_columns, u'depthtop' in existing_columns, u'depthbot' in existing_columns]):
            skip_obsids = []
            obsid_strat = db_utils.get_sql_result_as_dict(u'select obsid, stratid, depthtop, depthbot from %s' % self.temptable_name, dbconnection)[1]
            for obsid, stratid_depthbot_depthtop  in obsid_strat.iteritems():
                #Turn everything to float
                strats = [[float(x) for x in y] for y in stratid_depthbot_depthtop]
                sorted_strats = sorted(strats, key=itemgetter(0))
                stratid_idx = 0
                depthtop_idx = 1
                depthbot_idx = 2
                for index in xrange(len(sorted_strats)):
                    if index == 0:
                        continue
                    #Check that there is no gap in the stratid:
                    if float(sorted_strats[index][stratid_idx]) - float(sorted_strats[index - 1][stratid_idx]) != 1:
                        utils.MessagebarAndLog.warning(bar_msg=u'Import error, see log message panel', log_msg=u'The obsid ' + obsid + u' will not be imported due to gaps in stratid')
                        skip_obsids.append(obsid)
                        break
                    #Check that the current depthtop is equal to the previous depthbot
                    elif sorted_strats[index][depthtop_idx] != sorted_strats[index - 1][depthbot_idx]:
                        utils.MessagebarAndLog.warning(bar_msg=u'Import error, see log message panel', log_msg=u'The obsid ' + obsid + u' will not be imported due to gaps in depthtop/depthbot')
                        skip_obsids.append(obsid)
                        break
            if skip_obsids:
                dbconnection.execute(u'delete from %s where obsid in (%s)' % (self.temptable_name, u', '.join([u"'{}'".format(obsid) for obsid in skip_obsids])))
        
    def wlvllogg_import_from_diveroffice_files(self):
        """ Method for importing diveroffice csv files
        :return: None
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...
        existing_obsids = utils.get_all_obsids()
        confirm_names = utils.Askuser("YesNo", "Do you want to confirm each logger import name before import?")
        import_all_data = utils.Askuser("YesNo", "Do you want to import all data?\n\n" +
                                        "'No' = only new data after the latest date in the database,\n" +
                                        "for each observation point, will be imported.\n\n" +
                                        "'Yes' = any data not matching an exact datetime in the database\n" +
                                        " for the corresponding obs_point will be imported.")
        self.charsetchoosen = utils.ask_for_charset(default_charset='cp1252')
        if not self.charsetchoosen:
            self.status = 'True'
            return u'cancel'

        files = utils.select_files(only_one_file=False, extension="csv (*.csv)")
        if not files:
            self.status = 'True'
            return u'cancel'
        parsed_files = []
        for selected_file in files:
            file_data = self.parse_diveroffice_file(selected_file, self.charsetchoosen, existing_obsids, confirm_names.result)
            if file_data == u'cancel':
                self.status = True
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return u'cancel'
            elif file_data == u'skip':
                continue
            elif not isinstance(file_data, list):
                utils.MessagebarAndLog.critical(bar_msg="Import Failure: Something went wrong with file " + str(selected_file))
                continue
            elif len(file_data) == 0:
                utils.MessagebarAndLog.warning(bar_msg="Import warning: No rows could be parsed from " + str(selected_file))

            parsed_files.append(file_data)
        if len(parsed_files) == 0:
            utils.MessagebarAndLog.critical(bar_msg="Import Failure: No files imported""")
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return
        #Header
        file_to_import_to_db =  [parsed_files[0][0]]
        file_to_import_to_db.extend([row for parsed_file in parsed_files for row in parsed_file[1:]])

        if not import_all_data.result:
            file_to_import_to_db = self.filter_dates_from_filedata(file_to_import_to_db, utils.get_last_logger_dates())
        answer = self.general_import(file_data=file_to_import_to_db, goal_table=u'w_levels_logger')
        if isinstance(answer, Cancel):
            self.status = True
            return answer

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

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
        with io.open(path, u'rt', encoding=str(charset)) as f:
            obsid = None
            for rawrow in f:
                rawrow = utils.returnunicode(rawrow)
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
                    #This skips the last line.
                    if len(cols) < 2:
                        continue
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

    def SanityCheckVacuumDB(self, dbconnection=None):
        if dbconnection is None:
            dbconnection = db_utils.DbConnectionManager()
        sanity = utils.Askuser("YesNo", """It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""", 'Vacuum the database?')
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            dbconnection.execute(u'vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()









