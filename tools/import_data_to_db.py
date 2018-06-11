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

import sys
from operator import itemgetter

import PyQt4
from PyQt4.QtCore import QCoreApplication

import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from midvatten_utils import UserInterruptError


class midv_data_importer():  # this class is intended to be a multipurpose import class  BUT loggerdata probably needs specific importer or its own subfunction

    def __init__(self):
        self.columns = 0
        self.recsbefore = 0
        self.recsafter = 0
        self.recstoimport = 0
        self.recsinfile = 0
        self.temptable_name = ''
        self.charsetchoosen = ''
        self.csvlayer = None
        self.foreign_keys_import_question = None

    def general_import(self, goal_table, file_data, allow_obs_fk_import=False, _dbconnection=None):
        """General method for importing an sqlite table into a goal_table

            self.temptableName must be the name of the table containing the new data to import.

        :param goal_table:
        :return:
        """
        try:
            if file_data is None or not file_data:
                return
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'\nImport to %s starting\n--------------------'))%goal_table)

            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)

            self.temptable_name = goal_table + u'_temp'

            if not isinstance(_dbconnection, db_utils.DbConnectionManager):
                dbconnection = db_utils.DbConnectionManager()
            else:
                dbconnection = _dbconnection

            db_utils.activate_foreign_keys(activated=True, dbconnection=dbconnection)

            recsinfile = len(file_data[1:])
            table_info = db_utils.db_tables_columns_info(table=goal_table, dbconnection=dbconnection)
            if not table_info:
                raise MidvDataImporterError(ru(QCoreApplication.translate(u'midv_data_importer', u'The table %s did not exist. Update the database to latest version.')) % goal_table)
            else:
                table_info = table_info[goal_table]
            #POINT and LINESTRING must be cast as BLOB. So change the type to BLOB.
            column_headers_types = db_utils.change_cast_type_for_geometry_columns(dbconnection, table_info, goal_table)
            primary_keys = [row[1] for row in table_info if int(row[5])]        #Not null columns are allowed if they have a default value.
            not_null_columns = [row[1] for row in table_info if int(row[3]) and row[4] is None]
            #Only use the columns that exists in the goal table.
            existing_columns_in_goal_table = [col for col in file_data[0] if col in column_headers_types]
            existing_columns_in_temptable = file_data[0]
            missing_columns = [column for column in not_null_columns if column not in existing_columns_in_goal_table]

            if missing_columns:
                raise MidvDataImporterError(ru(QCoreApplication.translate(u'midv_data_importer', u'Required columns %s are missing for table %s')) % (u', '.join(missing_columns), goal_table))

            primary_keys_for_concat = [pk for pk in primary_keys if pk in existing_columns_in_temptable]

            self.list_to_table(dbconnection, file_data, primary_keys_for_concat)

            #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
            nr_before = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % (self.temptable_name))[0][0]
            if u'date_time' in primary_keys:
                self.delete_existing_date_times_from_temptable(primary_keys, goal_table, dbconnection)
            nr_after = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % (self.temptable_name))[0][0]

            nr_same_date = nr_after - nr_before
            if nr_same_date > 0:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported. %s rows remain.'))%(str(nr_same_date), str(nr_after)))
            if not nr_after > 0:
                utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Nothing imported to %s after deleting duplicate date_times'))%goal_table)
                return

            #Special cases for some tables
            if goal_table == u'stratigraphy':
                self.check_and_delete_stratigraphy(existing_columns_in_goal_table, dbconnection)
            if goal_table in (u'obs_lines', u'obs_points'):
                self.calculate_geometry(existing_columns_in_goal_table, goal_table, dbconnection)

            # Import foreign keys in some special cases
            foreign_keys = db_utils.get_foreign_keys(goal_table, dbconnection=dbconnection)
            if foreign_keys:
                if not allow_obs_fk_import:
                    for table in [u'obs_points', u'obs_lines']:
                        if table in foreign_keys:
                            del foreign_keys[table]

                if foreign_keys:
                    if self.foreign_keys_import_question is None:
                        msg = ru(QCoreApplication.translate(u'midv_data_importer', u"""Please note!\nForeign keys will be imported silently into "%s" if needed. \n\nProceed?""")) % (u', '.join(foreign_keys.keys()))
                        utils.MessagebarAndLog.info(log_msg=msg)
                        stop_question = utils.Askuser(u"YesNo", msg, ru(QCoreApplication.translate(u'midv_data_importer', u"Info!")))
                        if stop_question.result == 0:      # if the user wants to abort
                            raise UserInterruptError()
                        else:
                            self.foreign_keys_import_question = 1
                    if self.foreign_keys_import_question == 1:
                        nr_before = nr_after
                        self.import_foreign_keys(dbconnection, goal_table, self.temptable_name, foreign_keys, existing_columns_in_temptable)
                        nr_after = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % (self.temptable_name))[0][0]
                        nr_after_foreign_keys = nr_before - nr_after
                        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'In total "%s" rows were deleted due to foreign keys restrictions and "%s" rows remain.'))%(str(nr_after_foreign_keys), str(nr_after)))

            if not nr_after > 0:
                raise MidvDataImporterError(ru(QCoreApplication.translate(u'midv_data_importer', u'Nothing imported, see log message panel')))

            #Finally import data:
            nr_failed_import = recsinfile - nr_after
            if nr_failed_import > 0:
                msg = ru(QCoreApplication.translate(u'midv_data_importer', u"""Please note!\nThere are %s rows in your data that can not be imported!\nDo you really want to import the rest?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?""" ))% (str(nr_failed_import))
                utils.MessagebarAndLog.info(log_msg=msg)
                stop_question = utils.Askuser(u"YesNo", msg, ru(QCoreApplication.translate(u'midv_data_importer', u"Warning!")))
                if stop_question.result == 0:      # if the user wants to abort
                    raise UserInterruptError()

            sql = u"""INSERT INTO %s ("""%goal_table
            sql += u', '.join(sorted(existing_columns_in_goal_table))
            sql += u""") SELECT """
            sql += u', '.join([u"""(CASE WHEN (%s !='' AND %s !=' ' AND %s IS NOT NULL) THEN CAST(%s AS %s) ELSE %s END)""" % (colname, colname, colname, colname, column_headers_types[colname], db_utils.cast_null(column_headers_types[colname], dbconnection)) for colname in sorted(existing_columns_in_goal_table)])
            sql += u"""FROM %s""" % (self.temptable_name)
            if not_null_columns:
                sql += u""" WHERE %s"""%u' AND '.join([u'%s IS NOT NULL'%notnullcol for notnullcol in sorted(not_null_columns)])

            recsbefore = dbconnection.execute_and_fetchall(u'select count(*) from %s' % (goal_table))[0][0]
            try:
                dbconnection.execute(sql)
            except Exception, e:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'INSERT failed while importing to %s. Using INSERT OR IGNORE instead. Msg:\n')) % goal_table + ru(str(e)))
                sql = db_utils.add_insert_or_ignore_to_sql(sql, dbconnection)
                try:
                    dbconnection.execute(sql)
                except Exception as e:
                    try:
                        str(e)
                    except UnicodeDecodeError:
                        utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Import failed, see log message panel')),
                                                        log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Sql\n%s  failed.')) % (sql), duration=999)
                    else:
                        utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Import failed, see log message panel')),
                                                        log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Sql\n%s  failed.\nMsg:\n%s')) % (sql, str(e)), duration=999)

            recsafter = dbconnection.execute_and_fetchall(u'select count(*) from %s' % (goal_table))[0][0]

            nr_imported = recsafter - recsbefore
            nr_excluded = recsinfile - nr_imported

            utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'%s rows imported and %s excluded for table %s. See log message panel for details'))%(nr_imported, nr_excluded, goal_table))
            utils.MessagebarAndLog.info(log_msg=u'--------------------')

            #If an external dbconnection is supplied, do not close it.
            if _dbconnection is None:
                dbconnection.commit_and_closedb()
            else:
                dbconnection.commit()
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        except:
            exc_info = sys.exc_info()
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            try:
                # If an external dbconnection is supplied, do not close it.
                if _dbconnection is None:
                    dbconnection.closedb()
                else:
                    pass
            except NameError():
                pass
            except:
                utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Closing database failed!')))
            raise exc_info[0], exc_info[1], exc_info[2]

    def list_to_table(self, dbconnection, file_data, primary_keys_for_concat):
        fieldnames_types = [u'{} TEXT'.format(field_name) for field_name in file_data[0]]
        self.temptable_name = dbconnection.create_temporary_table_for_import(self.temptable_name, fieldnames_types)

        placeholder_sign = db_utils.placeholder_sign(dbconnection)

        concat_cols = [file_data[0].index(pk) for pk in primary_keys_for_concat]
        added_rows = set()
        numskipped = 0
        sql = u"""INSERT INTO %s VALUES (%s)""" % (self.temptable_name, u', '.join([placeholder_sign for x in xrange(len(file_data[0]))]))
        for row in file_data[1:]:
            if  primary_keys_for_concat:
                concatted = u'|'.join([row[idx] for idx in concat_cols])
                if concatted in added_rows:
                    numskipped += 1
                    continue
                else:
                    added_rows.add(concatted)
            args = tuple([None if any([r is None, not r.strip() if r is not None else None]) else r for r in row])
            dbconnection.cursor.execute(sql, args)

        #TODO: Let's see what happens without commit
        #dbconnection.commit()
        if numskipped:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Import warning, duplicates skipped')), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u"%s nr of duplicate rows in file was skipped while importing."))%str(numskipped))

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

    def calculate_geometry(self, existing_columns, table_name, dbconnection):
        # Calculate the geometry
        # THIS IS DUE TO WKT-import of geometries below
        srid = dbconnection.execute_and_fetchall(u"""SELECT srid FROM geometry_columns WHERE f_table_name = '%s'""" % table_name)[0][0]
        if u'WKT' in existing_columns:
            geocol = u'WKT'
        elif u'geometry' in existing_columns:
            geocol = u'geometry'
        else:
            return None

        sql = u"""UPDATE %s SET geometry = ST_GeomFromText(%s, %s)"""%(self.temptable_name, geocol, srid)
        dbconnection.execute(sql)

    def check_and_delete_stratigraphy(self, existing_columns, dbconnection):
        if all([u'stratid' in existing_columns, u'depthtop' in existing_columns, u'depthbot' in existing_columns]):
            skip_obsids = []
            obsid_strat = db_utils.get_sql_result_as_dict(u'select obsid, stratid, depthtop, depthbot from %s' % self.temptable_name, dbconnection)[1]
            for obsid, stratid_depthbot_depthtop  in obsid_strat.iteritems():
                #Turn everything to float
                try:
                    strats = [[float(x) for x in y] for y in stratid_depthbot_depthtop]
                except ValueError as e:
                    raise MidvDataImporterError(ru(QCoreApplication.translate(u'midv_data_importer', u'ValueError: %s. Obsid "%s", stratid: "%s", depthbot: "%s", depthtop: "%s"')) % (str(e), obsid, stratid_depthbot_depthtop[0], stratid_depthbot_depthtop[1], stratid_depthbot_depthtop[2]))
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
                dbconnection.execute(u'delete from %s where obsid in (%s)' % (self.temptable_name, u', '.join([u"'{}'".format(obsid) for obsid in skip_obsids])))

    def import_foreign_keys(self, dbconnection, goal_table, temptablename, foreign_keys, existing_columns_in_temptable):
        #TODO: Empty foreign keys are probably imported now. Must add "case when...NULL" to a couple of sql questions here

        #What I want to do:
        # import all foreign keys from temptable that doesn't already exist in foreign key table
        # insert into fk_table (to1, to2) select distinct from1(cast as), from2(cast as) from temptable where concatted_from_and_case_when_null not in concatted_to_and_case_when_null

        for fk_table, from_to_fields in foreign_keys.iteritems():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]
            if not all([_from in existing_columns_in_temptable for _from in from_list]):
                utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Import of foreign keys failed, see log message panel')), log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'There were keys missing for importing to fk_table %s, so no import was done.'))%fk_table)
                continue

            nr_fk_before = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % fk_table)[0][0]
            table_info = db_utils.db_tables_columns_info(table=fk_table, dbconnection=dbconnection)[fk_table]
            column_headers_types = dict([(row[1], row[2]) for row in table_info])

            concatted_from_string = u'||'.join([u"CASE WHEN %s is NULL then '0' ELSE %s END"%(x, x) for x in from_list])
            concatted_to_string = u'||'.join([u"CASE WHEN %s is NULL then '0' ELSE %s END"%(x, x) for x in to_list])
            sql = u'INSERT INTO %s (%s) SELECT DISTINCT %s FROM %s AS b WHERE %s NOT IN (SELECT %s FROM %s) AND %s'%(fk_table,
                                                                                                         u', '.join([u'"{}"'.format(k) for k in to_list]),
                                                                                                         u', '.join([u'''CAST("b"."%s" as "%s")'''%(k, column_headers_types[to_list[idx]]) for idx, k in enumerate(from_list)]),
                                                                                                         temptablename,
                                                                                                         concatted_from_string,
                                                                                                         concatted_to_string,
                                                                                                         fk_table,
                                                                                                         u' AND '.join([u''' b.{} IS NOT NULL and b.{} != '' '''.format(k, k, k) for k in from_list]))
            dbconnection.execute(sql)

            nr_fk_after = dbconnection.execute_and_fetchall(u'''select count(*) from %s''' % fk_table)[0][0]
            if nr_fk_after > nr_fk_before:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'In total %s rows were imported to foreign key table %s while importing to %s.'))%(str(nr_fk_after - nr_fk_before), fk_table, goal_table))

    def SanityCheckVacuumDB(self, dbconnection=None):
        if dbconnection is None:
            dbconnection = db_utils.DbConnectionManager()
        sanity = utils.Askuser("YesNo", ru(QCoreApplication.translate(u'midv_data_importer', """It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""")), ru(QCoreApplication.translate(u'midv_data_importer', 'Vacuum the database?')))
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            dbconnection.vacuum()    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def import_error_msg(self):
        return ru(QCoreApplication.translate(u'midv_data_importer', u'Import error, see log message panel'))


class MidvDataImporterError(Exception):
    pass


def import_exception_handler(func):
    def new_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except MidvDataImporterError as e:
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'midv_data_importer', u'Import error, see log message panel')),
                                            log_msg=str(e))
        else:
            return result
    return new_func
