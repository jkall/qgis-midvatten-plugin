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
from __future__ import absolute_import

from builtins import object
from builtins import range
from builtins import str
from operator import itemgetter

from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools.utils import common_utils, db_utils
from midvatten.tools.utils.common_utils import returnunicode as ru, UserInterruptError


class midv_data_importer(object):  # this class is intended to be a multipurpose import class  BUT loggerdata probably needs specific importer or its own subfunction

    def __init__(self):
        self.columns = 0
        self.recsbefore = 0
        self.recsafter = 0
        self.recstoimport = 0
        self.recsinfile = 0
        self.temptable_name = None
        self.csvlayer = None
        self.foreign_keys_import_question = None

    def general_import(self, dest_table, file_data, allow_obs_fk_import=False,
                       _dbconnection=None, dump_temptable=False, source_srid=None,
                       skip_confirmation=False, binary_geometry=False):
        """General method for importing a list of list to a table

            self.temptableName must be the name of the table containing the new data to import.

        :param dest_table: The destination table
        :param file_data: a list of list with a header list as first row
        :param allow_obs_fk_import: True to allow creation of obsids in obs_points and obs_lines.
        :param _dbconnection: A db_utils.DbConnectionManager-instance if other than the currently selected in the midvatten
                              settings dialog.
        :param dump_temptable: True to create a csvfile from internal temporary table.
        :param source_srid: The srid of the source geometry column if the geometry is a WKT or WKB
        :param skip_confirmation: True to not ask the user to import foreign keys.
        :param binary_geometry: True if the source geometry column should be parsed as a WKB, else it's parsed as WKT.
        :return:
        """

        self.temptable_name = None

        if skip_confirmation:
            self.foreign_keys_import_question = 1

        try:
            if file_data is None or not file_data:
                return
            common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('midv_data_importer', '\nImport to %s starting\n--------------------')) % dest_table)

            common_utils.start_waiting_cursor()

            if not isinstance(_dbconnection, db_utils.DbConnectionManager):
                dbconnection = db_utils.DbConnectionManager()
            else:
                dbconnection = _dbconnection

            db_utils.activate_foreign_keys(activated=True, dbconnection=dbconnection)

            recsinfile = len(file_data[1:])
            table_info = db_utils.db_tables_columns_info(table=dest_table, dbconnection=dbconnection)
            if not table_info:
                raise MidvDataImporterError(ru(QCoreApplication.translate('midv_data_importer', 'The table %s did not exist. Update the database to latest version.')) % dest_table)
            else:
                table_info = table_info[dest_table]
            #POINT and LINESTRING must be cast as BLOB. So change the type to BLOB.
            column_headers_types = db_utils.change_cast_type_for_geometry_columns(dbconnection, table_info, dest_table)
            primary_keys = [row[1] for row in table_info if int(row[5])]        #Not null columns are allowed if they have a default value.
            not_null_columns = [row[1] for row in table_info if int(row[3]) and row[4] is None]
            #Only use the columns that exists in the goal table.
            existing_columns_in_dest_table = [col for col in file_data[0] if col in column_headers_types]
            existing_columns_in_temptable = file_data[0]
            missing_columns = [column for column in not_null_columns if column not in existing_columns_in_dest_table]

            if missing_columns:
                raise MidvDataImporterError(ru(QCoreApplication.translate('midv_data_importer', 'Required columns %s are missing for table %s')) % (', '.join(missing_columns), dest_table))

            primary_keys_for_concat = [pk for pk in primary_keys if pk in existing_columns_in_temptable]

            self.list_to_table(dbconnection, dest_table, file_data, primary_keys_for_concat)

            #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
            nr_before = dbconnection.execute_and_fetchall('''select count(*) from %s''' % (self.temptable_name))[0][0]
            if 'date_time' in primary_keys:
                self.delete_existing_date_times_from_temptable(primary_keys, dest_table, dbconnection)
            nr_after = dbconnection.execute_and_fetchall('''select count(*) from %s''' % (self.temptable_name))[0][0]

            nr_same_date = nr_after - nr_before
            if nr_same_date > 0:
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('midv_data_importer', 'In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported. %s rows remain.')) % (str(nr_same_date), str(nr_after)))
            if not nr_after > 0:
                common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('midv_data_importer', 'Nothing imported to %s after deleting duplicate date_times')) % dest_table)
                return

            #Special cases for some tables
            if dest_table == 'stratigraphy':
                self.check_and_delete_stratigraphy(existing_columns_in_dest_table, dbconnection)
            elif dest_table == 'w_qual_field':
                self.convert_null_unit_to_empty_string(self.temptable_name, 'unit', dbconnection)

            # Dump temptable to csv for debugging
            if dump_temptable:
                dbconnection.dump_table_2_csv(self.temptable_name)

            # Import foreign keys in some special cases
            foreign_keys = db_utils.get_foreign_keys(dest_table, dbconnection=dbconnection)
            if foreign_keys:
                if not allow_obs_fk_import:
                    for table in ['obs_points', 'obs_lines']:
                        if table in foreign_keys:
                            del foreign_keys[table]

                if foreign_keys:
                    if self.foreign_keys_import_question is None:
                        msg = ru(QCoreApplication.translate('midv_data_importer', """Please note!\nForeign keys will be imported silently into "%s" if needed. \n\nProceed?""")) % (', '.join(list(foreign_keys.keys())))
                        common_utils.MessagebarAndLog.info(log_msg=msg)
                        stop_question = common_utils.Askuser("YesNo", msg, ru(QCoreApplication.translate('midv_data_importer', "Info!")))
                        if stop_question.result == 0:      # if the user wants to abort
                            raise UserInterruptError()
                        else:
                            self.foreign_keys_import_question = 1
                    if self.foreign_keys_import_question == 1:
                        nr_before = nr_after
                        self.import_foreign_keys(dbconnection, dest_table, self.temptable_name, foreign_keys, existing_columns_in_temptable)
                        nr_after = dbconnection.execute_and_fetchall('''select count(*) from %s''' % (self.temptable_name))[0][0]
                        nr_after_foreign_keys = nr_before - nr_after
                        common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('midv_data_importer', 'In total "%s" rows were deleted due to foreign keys restrictions and "%s" rows remain.')) % (str(nr_after_foreign_keys), str(nr_after)))

            if not nr_after > 0:
                raise MidvDataImporterError(ru(QCoreApplication.translate('midv_data_importer', 'Nothing imported, see log message panel')))

            #Finally import data:
            nr_failed_import = recsinfile - nr_after
            if nr_failed_import > 0:
                msg = ru(QCoreApplication.translate('midv_data_importer', """Please note!\nThere are %s rows in your data that can not be imported!\nDo you really want to import the rest?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?""" ))% (str(nr_failed_import))
                common_utils.MessagebarAndLog.info(log_msg=msg)
                stop_question = common_utils.Askuser("YesNo", msg, ru(QCoreApplication.translate('midv_data_importer', "Warning!")))
                if stop_question.result == 0:      # if the user wants to abort
                    raise UserInterruptError()

            # Check if current table has geometry:
            geom_columns = db_utils.get_geometry_types(dbconnection, dest_table)
            sourcecols = []
            for colname in sorted(existing_columns_in_dest_table):
                null_replacement = db_utils.cast_null(column_headers_types[colname], dbconnection)
                if colname in list(geom_columns.keys()) and colname in existing_columns_in_temptable:
                    sourcecols.append(self.create_geometry_sql(colname, dest_table, dbconnection, source_srid,
                                                               null_replacement, binary_geometry))
                else:
                    sourcecols.append(
                        """(CASE WHEN {colname} IS NOT NULL\n    THEN CAST({colname} AS {type}) ELSE {null} END)""".format(
                            colname=colname,
                            type=column_headers_types[colname],
                            null=null_replacement))

            sql = """INSERT INTO {dest_table} ({dest_columns})\nSELECT {source_columns}\nFROM {source_table}\n"""
            kwargs = {'dest_table': dest_table,
                      'dest_columns': ', '.join(sorted(existing_columns_in_dest_table)),
                      'source_table': self.temptable_name,
                      'source_columns': u',\n    '.join(sourcecols)
                      }
            if not_null_columns:
                sql += """WHERE {notnullcheck}"""
                kwargs['notnullcheck'] = ' AND '.join(['%s IS NOT NULL'%notnullcol
                                                       for notnullcol in sorted(not_null_columns)])
            sql = sql.format(**kwargs)
            recsbefore = dbconnection.execute_and_fetchall('select count(*) from %s' % (dest_table))[0][0]
            try:
                dbconnection.execute(sql)
            except Exception as e:
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('midv_data_importer', 'INSERT failed while importing to %s. Using INSERT OR IGNORE instead. Msg:\n')) % dest_table + ru(str(e)))
                sql = db_utils.add_insert_or_ignore_to_sql(sql, dbconnection)
                try:
                    dbconnection.execute(sql)
                except Exception as e:
                    try:
                        str(e)
                    except UnicodeDecodeError:
                        common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('midv_data_importer', 'Import failed, see log message panel')),
                                                                           log_msg=ru(QCoreApplication.translate('midv_data_importer', 'Sql\n%s  failed.')) % (sql), duration=999)
                    else:
                        common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('midv_data_importer', 'Import failed, see log message panel')),
                                                                           log_msg=ru(QCoreApplication.translate('midv_data_importer', 'Sql\n%s  failed.\nMsg:\n%s')) % (sql, ru(str(e))), duration=999)

            recsafter = dbconnection.execute_and_fetchall('select count(*) from %s' % (dest_table))[0][0]
            nr_imported = recsafter - recsbefore
            nr_excluded = recsinfile - nr_imported

            common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('midv_data_importer', '%s rows imported and %s excluded for table %s. See log message panel for details')) % (nr_imported, nr_excluded, dest_table),
                                                           log_msg='--------------------')

        except:
            # If an external dbconnection is supplied, do not close it.
            if _dbconnection is None:
                try:
                    dbconnection.closedb()
                except:
                    pass
            else:
                if self.temptable_name is not None:
                    #try:
                    dbconnection.drop_temporary_table(self.temptable_name)
                    #except:
                    #    pass
            common_utils.stop_waiting_cursor()
            raise
        else:
            dbconnection.commit()
            # If an external dbconnection is supplied, do not close it.
            if _dbconnection is None:
                try:
                    dbconnection.closedb()
                except:
                    pass
            else:
                if self.temptable_name is not None:
                    #try:
                    dbconnection.drop_temporary_table(self.temptable_name)
                    #except:
                    #    pass
            common_utils.stop_waiting_cursor()

    def list_to_table(self, dbconnection, destination_table, file_data, primary_keys_for_concat):
        fieldnames_types = ['{} TEXT'.format(field_name) for field_name in file_data[0]]
        self.temptable_name = dbconnection.create_temporary_table_for_import(destination_table + '_temp', fieldnames_types)

        placeholder_sign = db_utils.placeholder_sign(dbconnection)
        concat_cols = [file_data[0].index(pk) for pk in primary_keys_for_concat]
        added_rows = set()
        numskipped = 0
        sql = """INSERT INTO %s VALUES (%s)""" % (self.temptable_name, ', '.join([placeholder_sign for x in range(len(file_data[0]))]))
        for row in file_data[1:]:
            if primary_keys_for_concat:
                concatted = '|'.join([ru(row[idx]) for idx in concat_cols])
                if concatted in added_rows:
                    numskipped += 1
                    continue
                else:
                    added_rows.add(concatted)

            args = tuple([self.sanitize(r) for r in row])

            dbconnection.cursor.execute(sql, args)
        #TODO: Let's see what happens without commit
        #dbconnection.commit()
        if numskipped:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('midv_data_importer', 'Import warning, duplicates skipped')), log_msg=ru(QCoreApplication.translate('midv_data_importer', "%s nr of duplicate rows in file was skipped while importing.")) % str(numskipped))

    def sanitize(self, value):
        if isinstance(value, str):
            value = value.strip() if value.strip() else None
        return value

    def delete_existing_date_times_from_temptable(self, primary_keys, dest_table, dbconnection):
        """
        Deletes duplicate times
        :param primary_keys: a table like ['obsid', 'date_time', ...]
        :param dest_table: a string like 'w_levels'
        :return: None. Alters the temptable self.temptableName

        If date 2016-01-01 00:00:00 exists for obsid1, then 2016-01-01 00:00 will not be imported for obsid1.
        (and 2016-01-01 00 will block 2016-01-01 00:00)

        If date 2016-01-01 00:00 exists for obsid1, then 2016-01-01 00:00:XX will not be imported for obsid1.
        (and 2016-01-01 00 will block 2016-01-01 00:XX)
        (but 2016-01-01 00 will not block 2016-01-01 00:00:XX, inconsistently)

        The function uses all primary keys to identify unique combinations, so different parameters will not block each other.
        """
        pks = [pk for pk in primary_keys if pk != 'date_time']
        pks.append('date_time')

        #TODO: Maybe the length should be checked so that the test is only made for 2016-01-01 00:00 and 2016-01-01 00:00:00?

        #Delete records that have the same date_time but with :00 at the end. (2016-01-01 00:00 will not be imported if 2016-01-01 00:00:00 exists
        pks_and_00 = list(pks)
        pks_and_00.append("':00'")
        sql = '''delete from %s where %s in (select %s from %s)'''%(self.temptable_name,
                                                                                          ' || '.join(pks_and_00),
                                                                                          ' || '.join(pks),
                                                                                          dest_table)
        dbconnection.execute(sql)

        # Delete records from temptable that have date_time yyyy-mm-dd HH:MM:XX when yyyy-mm-dd HH:MM exist.
        #delete from temptable where SUBSTR("obsid" || "date_time", 1, length("obsid" || "date_time") - 3) in (select "obsid" || "date_time" from goaltable)
        sql = '''delete from %s where SUBSTR(%s, 1, length(%s) - 3) in (select %s from %s)'''%(self.temptable_name,
                                                                                          ' || '.join(pks),
                                                                                          ' || '.join(pks),
                                                                                          ' || '.join(pks),
                                                                                          dest_table)
        dbconnection.execute(sql)

    def create_geometry_sql(self, geom_col, table_name, dbconnection, source_srid, null_replacement,
                            binary_geometry=False):
        # Calculate the geometry
        # THIS IS DUE TO WKT-import of geometries below
        dest_srid = dbconnection.get_srid(table_name)

        convert_func = '''ST_GeomFromWKB''' if binary_geometry else '''ST_GeomFromText'''

        sql = """(CASE WHEN ({colname} !='' AND {colname} !=' ' AND {colname} IS NOT NULL)\n    THEN {to_geometry} ELSE {null} END)"""
        kwargs = {'colname': geom_col, 'null': null_replacement}

        if source_srid is None or int(source_srid) == int(dest_srid):
            to_geometry = """{convert_func}({geometry}, {dest_srid})""".format(geometry=geom_col,
                                                                               convert_func=convert_func,
                                                                               dest_srid=dest_srid)
        else:
            to_geometry = """ST_Transform({convert_func}({geometry}, {source_srid}), {dest_srid})""".format(
                geometry=geom_col,
                convert_func=convert_func,
                dest_srid=dest_srid,
                source_srid=source_srid)
        kwargs['to_geometry'] = to_geometry
        return sql.format(**kwargs)

    def check_and_delete_stratigraphy(self, existing_columns, dbconnection):
        if all(['stratid' in existing_columns, 'depthtop' in existing_columns, 'depthbot' in existing_columns]):
            skip_obsids = []
            obsid_strat = db_utils.get_sql_result_as_dict('select obsid, stratid, depthtop, depthbot from %s' % self.temptable_name, dbconnection)[1]
            for obsid, stratid_depthbot_depthtop  in obsid_strat.items():
                #Turn everything to float
                try:
                    strats = [[float(x) for x in y] for y in stratid_depthbot_depthtop]
                except (ValueError, TypeError) as e:
                    raise MidvDataImporterError(ru(QCoreApplication.translate('midv_data_importer', 'ValueError: %s. Obsid "%s", stratid: "%s", depthbot: "%s", depthtop: "%s"')) % (str(e), obsid, stratid_depthbot_depthtop[0], stratid_depthbot_depthtop[1], stratid_depthbot_depthtop[2]))
                sorted_strats = sorted(strats, key=itemgetter(0))
                stratid_idx = 0
                depthtop_idx = 1
                depthbot_idx = 2
                for index in range(len(sorted_strats)):
                    if index == 0:
                        continue
                    #Check that there is no gap in the stratid:
                    if float(sorted_strats[index][stratid_idx]) - float(sorted_strats[index - 1][stratid_idx]) != 1:
                        common_utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate('midv_data_importer', 'The obsid %s will not be imported due to gaps in stratid')) % obsid)
                        skip_obsids.append(obsid)
                        break
                    #Check that the current depthtop is equal to the previous depthbot
                    elif sorted_strats[index][depthtop_idx] != sorted_strats[index - 1][depthbot_idx]:
                        common_utils.MessagebarAndLog.warning(bar_msg=self.import_error_msg(), log_msg=ru(QCoreApplication.translate('midv_data_importer', 'The obsid %s will not be imported due to gaps in depthtop/depthbot')) % obsid)
                        skip_obsids.append(obsid)
                        break
            if skip_obsids:
                dbconnection.execute('delete from %s where obsid in (%s)' % (self.temptable_name, ', '.join(["'{}'".format(obsid) for obsid in skip_obsids])))

    def convert_null_unit_to_empty_string(self, temptable_name, column, dbconnection):
        dbconnection.execute('''UPDATE {table} 
                                SET {column} = TRIM(COALESCE({column}, ''))'''.format(
                             table=temptable_name, column=column))

    def import_foreign_keys(self, dbconnection, dest_table, temptablename, foreign_keys, existing_columns_in_temptable):
        #TODO: Empty foreign keys are probably imported now. Must add "case when...NULL" to a couple of sql questions here

        #What I want to do:
        # import all foreign keys from temptable that doesn't already exist in foreign key table
        # insert into fk_table (to1, to2) select distinct from1(cast as), from2(cast as) from temptable where concatted_from_and_case_when_null not in concatted_to_and_case_when_null

        for fk_table, from_to_fields in foreign_keys.items():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]
            if not all([_from in existing_columns_in_temptable for _from in from_list]):
                common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('midv_data_importer', 'Import of foreign keys failed, see log message panel')), log_msg=ru(QCoreApplication.translate('midv_data_importer', 'There were keys missing for importing to fk_table %s, so no import was done.')) % fk_table)
                continue

            nr_fk_before = dbconnection.execute_and_fetchall('''select count(*) from %s''' % fk_table)[0][0]
            table_info = db_utils.db_tables_columns_info(table=fk_table, dbconnection=dbconnection)[fk_table]
            column_headers_types = dict([(row[1], row[2]) for row in table_info])

            null_replacement_string = 'NULL_NULL_NULL_NULL_NULL_NULL_NULL_NULL_NULL_NULL'
            concatted_from_string = '||'.join(["CASE WHEN %s is NULL THEN '%s' ELSE %s END"%(x, null_replacement_string, x) for x in from_list])
            concatted_to_string = '||'.join(["CASE WHEN %s is NULL THEN '%s' ELSE %s END"%(x, null_replacement_string, x) for x in to_list])
            sql = u'INSERT INTO %s (%s) SELECT DISTINCT %s FROM %s AS b WHERE %s NOT IN (SELECT %s FROM %s) AND %s'%(fk_table,
                                                                                                         u', '.join([u'"{}"'.format(k) for k in to_list]),
                                                                                                         u', '.join([u'''CAST("b"."%s" as "%s")'''%(k, column_headers_types[to_list[idx]]) for idx, k in enumerate(from_list)]),
                                                                                                         temptablename,
                                                                                                         concatted_from_string,
                                                                                                         concatted_to_string,
                                                                                                         fk_table,
                                                                                                         ' AND '.join([''' b.{} IS NOT NULL and b.{} != '' '''.format(k, k, k) for k in from_list]))
            dbconnection.execute(sql)

            nr_fk_after = dbconnection.execute_and_fetchall('''select count(*) from %s''' % fk_table)[0][0]
            if nr_fk_after > nr_fk_before:
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('midv_data_importer', 'In total %s rows were imported to foreign key table %s while importing to %s.')) % (str(nr_fk_after - nr_fk_before), fk_table, dest_table))

    def import_error_msg(self):
        return ru(QCoreApplication.translate('midv_data_importer', 'Import error, see log message panel'))


class MidvDataImporterError(Exception):
    pass


def import_exception_handler(func):
    def new_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except MidvDataImporterError as e:
            common_utils.stop_waiting_cursor()
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('midv_data_importer', 'Import error, see log message panel')),
                                                               log_msg=str(e))
        else:
            return result
    return new_func
