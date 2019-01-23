# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that enables quick export of data from the database
                              -------------------
        begin                : 2015-08-30
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
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
import csv, codecs, io, os, os.path
import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from definitions import midvatten_defs as defs
import qgis.utils
from qgis.PyQt.QtCore import QCoreApplication

class ExportData(object):

    def __init__(self, OBSID_P, OBSID_L):
        self.ID_obs_points = OBSID_P
        self.ID_obs_lines = OBSID_L

    def export_2_csv(self,exportfolder):
        dbconnection = db_utils.DbConnectionManager()
        dbconnection.connect2db() #establish connection to the current midv db
        self.curs = dbconnection.cursor#get a cursor
        self.exportfolder = exportfolder
        self.write_data(self.to_csv, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='obs_points'),
                        lambda x: db_utils.verify_table_exists(x, dbconnection=dbconnection))
        self.write_data(self.to_csv, self.ID_obs_lines, defs.get_subset_of_tables_fr_db(category='obs_lines'),
                        lambda x: db_utils.verify_table_exists(x, dbconnection=dbconnection))
        self.write_data(self.zz_to_csv, 'no_obsids', defs.get_subset_of_tables_fr_db(category='data_domains'),
                        lambda x: db_utils.verify_table_exists(x, dbconnection=dbconnection))
        dbconnection.closedb()

    def export_2_splite(self,target_db, EPSG_code):
        """
        Exports a datagbase to a new spatialite database file
        :param target_db: The name of the new database file
        :param EPSG_code:
        :return:

        """
        dbconnection = db_utils.DbConnectionManager()
        source_db = dbconnection.dbpath
        dbconnection.closedb()

        conn = db_utils.connect_with_spatialite_connect(target_db)
        self.curs = conn.cursor()
        self.curs.execute("PRAGMA foreign_keys = ON")
        self.curs.execute(r"""ATTACH DATABASE '%s' AS a"""%source_db)
        conn.commit()  # commit sql statements so far

        old_table_column_srid = self.get_table_column_srid(prefix='a')
        self.write_data(self.to_sql, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='obs_points'), self.verify_table_in_attached_db, 'a.')
        conn.commit()
        self.write_data(self.to_sql, self.ID_obs_lines, defs.get_subset_of_tables_fr_db(category='obs_lines'), self.verify_table_in_attached_db, 'a.')
        conn.commit()
        self.write_data(self.zz_to_sql, 'no_obsids', defs.get_subset_of_tables_fr_db(category='data_domains'), self.verify_table_in_attached_db, 'a.')
        conn.commit()

        db_utils.delete_srids(self.curs, EPSG_code)

        conn.commit()

        #Statistics
        statistics = self.get_table_rows_with_differences()

        self.curs.execute(r"""DETACH DATABASE a""")
        self.curs.execute('vacuum')

        utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ExportData', "Export done, see differences in log message panel")), log_msg=ru(QCoreApplication.translate('ExportData', "Tables with different number of rows:\n%s"))%statistics)

        conn.commit()
        conn.close()

    def get_table_column_srid(self, prefix=None):
        """

        :return: A dict of tuples like {tablename: (columnname, srid), ...)
        """

        if prefix is None:
            sql = '''select "f_table_name", "f_geometry_column", "srid" from geometry_columns'''
        else:
            sql = '''select "f_table_name", "f_geometry_column", "srid" from "%s".geometry_columns'''%(prefix)

        table_column_srid_dict = {}
        for x in self.curs.execute(sql).fetchall():
            table_column_srid_dict.setdefault(x[0], {})[x[1]] = x[2]

        """
        try:
            self.curs.execute(sql)
        except Exception, e:
            utils.MessagebarAndLog.critical(
                "Export warning: sql failed. See message log.",
                sql + "\nmsg: " + str(e))
        """
        return table_column_srid_dict

    def get_create_statement(self, tname):

        sql_list = []
        sql_list.append("""SELECT sql FROM (""")
        sql_list.append("""SELECT sql sql, type type, tbl_name tbl_name, name name """)
        sql_list.append("""FROM sqlite_master""")
        sql_list.append("""UNION ALL """)
        sql_list.append("""SELECT sql, type, tbl_name, name """)
        sql_list.append("""FROM sqlite_temp_master) """)
        sql_list.append("""WHERE type != 'meta' """)
        sql_list.append("""AND sql NOTNULL """)
        sql_list.append("""AND name NOT LIKE 'sqlite_%' """)
        sql_list.append("""AND tbl_name = '%s' """%(tname))
        sql_list.append("""ORDER BY substr(type, 2, 1), name""")
        sql = ''.join(sql_list)
        result = self.curs.execute(sql).fetchall()
        return result

    def format_obsids(self, obsids):
        formatted_obsids = ''.join(['(', ', '.join(["'{}'".format(k) for k in ru(obsids, True)]), ')'])
        return formatted_obsids

    def get_number_of_obsids(self, obsids, tname):
        sql = "select count(obsid) from %s"%tname
        if obsids:
            sql += " WHERE obsid IN %s"%self.format_obsids(obsids)
        self.curs.execute(sql)
        no_of_obs = self.curs.fetchall()
        return no_of_obs

    def write_data(self, to_writer, obsids, ptabs, verify_table_exists, tname_prefix=''):
        for tname in ptabs:
            tname_with_prefix = tname_prefix + tname
            if not verify_table_exists(tname):
                utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ExportData', "Table %s didn't exist. Skipping it."))%tname)
                continue
            if obsids != 'no_obsids':
                if not obsids:
                    to_writer(tname, tname_with_prefix, obsids)
                else:
                    no_of_obs = self.get_number_of_obsids(obsids, tname_with_prefix)
                    if no_of_obs[0][0] > 0:#only go on if there are any observations for this obsid
                        to_writer(tname, tname_with_prefix, obsids)
            else:
                to_writer(tname, tname_with_prefix)

    def to_csv(self, tname, tname_with_prefix, obsids):
        """
        Write to csv
        :param tname: The destination database
        :param tname_with_prefix: The source database
        :param obsids:
        :return:
        """
        sql = "SELECT * FROM %s"%tname
        if obsids:
            sql += " WHERE obsid IN %s"%self.format_obsids(obsids)
        self.curs.execute(sql)
        printlist = [[col[0] for col in self.curs.description]]
        printlist.extend(self.curs.fetchall())
        filename = os.path.join(self.exportfolder, tname + ".csv")
        utils.write_printlist_to_file(filename, printlist)

    def to_sql(self, tname, tname_with_prefix, obsids):
        """
        Write to new sql database
        :param tname: The destination database
        :param tname_with_prefix: The source database
        :param obsids:
        :return:
        """
        column_names = self.get_and_check_existing_column_names(tname, tname_with_prefix)
        if column_names is None:
            return None

        foreign_keys = self.get_foreign_keys(tname)

        for reference_table, from_to_fields in foreign_keys.items():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]

            #If the current table contains obsid, filter only the chosen ones.
            sql = """INSERT OR IGNORE INTO %s (%s) SELECT DISTINCT %s FROM  %s """ % (reference_table, ', '.join(to_list), ', '.join(from_list), tname_with_prefix)
            if obsids:
                sql += """ WHERE obsid IN %s""" % self.format_obsids(obsids)
            try:
                self.curs.execute(sql)
            except Exception as e:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('ExportData', 'INSERT failed while importing to %s.\nMsg:%s'))%(tname, str(e)))

        #Make a transformation for column names that are geometries #Transformation doesn't work yet.
        old_table_column_srid_dict = self.get_table_column_srid(prefix='a')
        new_table_column_srid_dict = self.get_table_column_srid()

        if tname in old_table_column_srid_dict and tname in new_table_column_srid_dict:
            transformed_column_names = self.transform_geometries(tname, column_names, old_table_column_srid_dict, new_table_column_srid_dict) #Transformation doesn't work since east, north is not updated.
        else:
            transformed_column_names = column_names

        sql = """INSERT INTO %s (%s) SELECT %s FROM %s"""%(tname, ', '.join(column_names), ', '.join(transformed_column_names), tname_with_prefix)
        if obsids:
            sql += """ WHERE obsid IN %s""" % self.format_obsids(obsids)
        try:
            self.curs.execute(sql)
        except Exception as e:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportData', "Export warning: sql failed. See message log.")), log_msg=ru(QCoreApplication.translate('ExportData', '%s\nmsg:\n%s'))%(sql, str(e)))

    @staticmethod
    def transform_geometries(tname, column_names, old_table_column_srid_dict, new_table_column_srid_dict, geom_as_text=False):
        r"""
        Transform geometry columns to new chosen SRID

        The transformation is only done if the chosen srid is not the same as the old srid,
        and if the geometry column in question exists in both the old and the new database

        :param tname: The table name
        :param column_names: a list of columns that will be copied from the old table/database to the new table/database
        :param old_table_column_srid_dict: a dict like  {'testt': {'geom': 3006}}. A dict with tables that have geometries. The inner dict is the column and the srid.
        :param new_table_column_srid_dict: a dict like  {'testt': {'geom': 3006}}. A dict with tables that have geometries. The inner dict is the column and the srid.
        :return: A list of columns where the geometry columns are Transformed.

        >>> ExportData.transform_geometries('testt', ['notgeom', 'geom'], {'testt': {'geom': 3006}}, {'testt': {'geom': 3006}})
        ['notgeom', 'geom']
        >>> ExportData.transform_geometries('testt', ['notgeom', 'geom'], {'testt': {'geom': 3006}}, {'testt': {'geom': 3010}})
        ['notgeom', 'ST_Transform(geom, 3010)']
        >>> ExportData.transform_geometries('obs_points', ['obsid', 'east', 'north', 'geom'], {'obs_points': {'geom': 3006}}, {'obs_points': {'geom': 3010}})
        ['obsid', 'X(ST_Transform(geom, 3010))', 'Y(ST_Transform(geom, 3010))', 'ST_Transform(geom, 3010)']
        """
        transformed = False
        #Make a transformation for column names that are geometries

        if tname in new_table_column_srid_dict and tname in old_table_column_srid_dict:
            transformed_column_names = []
            for column in column_names:
                new_srid = new_table_column_srid_dict.get(tname, {}).get(column, None)
                old_srid = old_table_column_srid_dict.get(tname, {}).get(column, None)
                # Fix for old databases where geometry sometimes was spelled Geometry
                if old_srid is None:
                    old_srid = old_table_column_srid_dict.get(tname, {}).get(column.capitalize(), None)
                    if old_srid is not None:
                        column = column.capitalize()
                if old_srid is not None and new_srid is not None and old_srid != new_srid:
                    if geom_as_text:
                        transformed_column_names.append('ST_AsText(ST_Transform({}, {}))'.format(column, ru(new_srid)))
                    else:
                        transformed_column_names.append('ST_Transform({}, {})'.format(column, ru(new_srid)))

                    utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('ExportData', 'Transformation for table %s column %s from %s to %s"'))%(tname, column, str(old_srid), str(new_srid)))
                    transformed = True
                else:
                    transformed_column_names.append(column)
        else:
            transformed_column_names = column_names

        #Special case for obs_points because of the very special columns east/north
        if tname == 'obs_points' and transformed:
            old_geocol_srids = [(k, v) for k, v in old_table_column_srid_dict.get(tname, {}).items()]
            new_geocol_srids = [(k, v) for k, v in new_table_column_srid_dict.get(tname, {}).items()]
            if len(old_geocol_srids) != 1 and len(new_geocol_srids) != 1:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportData', 'Export warning!, see Log Message Panel')), log_msg=ru(QCoreApplication.translate('ExportData', 'Transformation of east/north for table obs_points failed! The number of geometry columns was not == 1!')))
            else:
                new_srid = new_geocol_srids[0][1]
                old_geometry_column = old_geocol_srids[0][0]

                res = []
                for column in transformed_column_names:
                    if column == 'east':
                        res.append('X(ST_Transform(%s, %s))'%(old_geometry_column, new_srid))
                    elif column == 'north':
                        res.append('Y(ST_Transform(%s, %s))'%(old_geometry_column, new_srid))
                    else:
                        res.append(column)
                transformed_column_names = res

        return transformed_column_names

    def zz_to_csv(self, tname, tname_with_prefix):
        self.curs.execute("select * from %s"%(tname))
        printlist = [[col[0] for col in self.curs.description]]
        printlist.extend(self.curs.fetchall())
        filename = os.path.join(self.exportfolder, tname + ".csv")
        utils.write_printlist_to_file(filename, printlist)

    def zz_to_sql(self, tname, tname_with_prefix):
        column_names = self.get_and_check_existing_column_names(tname, tname_with_prefix)
        if column_names is None:
            return None

        #Null-values as primary keys don't equal each other and can therefore cause duplicates.
        #This part concatenates the primary keys to make a string comparison for equality instead.
        primary_keys = self.get_primary_keys(tname)
        ifnull_primary_keys = [''.join(["ifnull(", pk, ",'')"]) for pk in primary_keys]
        concatenated_primary_keys = ' || '.join(ifnull_primary_keys)

        sql = """INSERT INTO %s (%s) select %s from %s """ % (tname, ', '.join(column_names), ', '.join(column_names), tname_with_prefix) #where %s not in (select %s from %s)"""%(tname, ', '.join(column_names), ', '.join(column_names), tname_with_prefix, concatenated_primary_keys, concatenated_primary_keys, tname)
        try:
            self.curs.execute(sql)
        except Exception as e:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('ExportData', 'INSERT failed while importing to %s. Using INSERT OR REPLACE instead.\nMsg:%s'))%(tname, str(e)))
            sql = sql.replace('INSERT', 'INSERT OR REPLACE')
            try:
                self.curs.execute(sql)
            except Exception as e:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportData', "Export warning: sql failed. See message log.")), log_msg=ru(QCoreApplication.translate('ExportData', '%s\nmsg:\n%s'))%(sql, str(e)))

    def get_foreign_keys(self, tname):
        result_list = self.curs.execute("""PRAGMA foreign_key_list('%s')"""%(tname)).fetchall()
        foreign_keys = {}
        for row in result_list:
            foreign_keys.setdefault(row[2], []).append((row[3], row[4]))
        return foreign_keys

    def get_primary_keys(self, tname):
        result_list = self.curs.execute("""PRAGMA table_info('%s')"""%(tname)).fetchall()
        primary_keys = [column_tuple[1] for column_tuple in result_list if column_tuple[5] != 0]
        return primary_keys

    def verify_table_in_attached_db(self, tname):
        result = self.curs.execute("""SELECT name FROM a.sqlite_master WHERE type='table' AND name='%s'"""%(tname)).fetchall()
        if result:
            return True
        else:
            return False

    def get_and_check_existing_column_names(self, tname, tname_with_prefix):

        new_column_names = self.get_column_names(tname)
        if new_column_names is None:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportData', 'Export warning!, see Log Message Panel')), log_msg=ru(QCoreApplication.translate('ExportData', "Table %s export failed!"))%tname)
            return None

        prefix = tname_with_prefix.split('.')[0]
        tname_with_prefix_without_prefix = tname_with_prefix.replace(prefix + '.', '')
        old_column_names = self.get_column_names(tname_with_prefix_without_prefix, prefix)
        if old_column_names is None:
            utils.MessagebarAndLog.critical(bar_msg='Export warning!, see Log Message Panel', log_msg="Table " + tname + " export failed!")
            return None

        #Check which columns that doesn't exist from in old and new database and write a log msg about it.
        old_columns_missing_in_new = [col for col in old_column_names if col not in new_column_names]
        new_columns_missing_in_old = [col for col in new_column_names if col not in old_column_names]

        """
        #TODO: Temporary msg:
        utils.MessagebarAndLog.info(log_msg='Table ' + tname)
        utils.MessagebarAndLog.info(log_msg="old_column_names " + str(old_column_names))
        utils.MessagebarAndLog.info(log_msg="new_column_names " + str(new_column_names))
        utils.MessagebarAndLog.info(log_msg="old_columns_missing_in_new " + str(old_columns_missing_in_new))
        utils.MessagebarAndLog.info(log_msg="new_columns_missing_in_old " + str(new_columns_missing_in_old))
        """

        missing_columns_msg = [ru(QCoreApplication.translate('ExportData', 'Table %s:'))%tname]
        if new_columns_missing_in_old:
            missing_columns_msg.append(ru(QCoreApplication.translate('ExportData', '\nNew columns missing in old database: %s'))%', '.join(new_columns_missing_in_old))
        if old_columns_missing_in_new:
            missing_columns_msg.append(ru(QCoreApplication.translate('ExportData', '\nOld columns missing in new database: %s'))%', '.join(old_columns_missing_in_new))
        if len(missing_columns_msg) > 1:
                utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('ExportData', 'Export warning, see Log Message Panel')), log_msg=''.join(missing_columns_msg))

        #Check if a primary key in the new database is missing in the old database and skip the table if there are missing primary keys.
        primary_keys = self.get_primary_keys(tname)
        missing_primary_keys = [col for col in primary_keys if col in new_columns_missing_in_old]
        if missing_primary_keys:
            missing_pk_msg = ru(QCoreApplication.translate('ExportData', 'Table %s:\nPrimary keys %s are missing in old database. The table will not be exported!!!'))%(tname, '", "'.join(missing_primary_keys))
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportData', 'Export warning!, see Log Message Panel')), log_msg=missing_pk_msg)
            return None

        #Only copy columns from old to new database that exist in old database.
        column_names = [col for col in new_column_names if col in old_column_names]
        return column_names

    def get_column_names(self, tname, prefix=None):

        if prefix is None:
            sql = """PRAGMA table_info('%s')"""%tname
        else:
            sql = '''PRAGMA "%s".table_info('%s')'''%(prefix, tname)

        try:
            result_list = self.curs.execute(sql).fetchall()
        except Exception as e:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportData', "Export warning: sql failed. See message log.")), log_msg=ru(QCoreApplication.translate('ExportData', '%s\nmsg:\n%s'))%(sql, str(e)))
            return None

        columns = [col[1] for col in result_list] #Load column names from sqlite table
        return columns

    def get_table_rows_with_differences(self, db_aliases_and_prefixes=[('exported_db', ''), ('source_db', 'a.')]):
        """
        Counts rows for all tables in new and old database and returns those that differ.
        self.cursor is required where the new database is the regular one and the old database is the attached one
        :param db_aliases_and_prefixes: A list of tuples like ('new', '')
        :return:  a printable list of nr of rows for all tables
        """
        results = {}
        for alias, prefix in db_aliases_and_prefixes:
            sql = """SELECT name FROM %s WHERE type='table';"""%(prefix + 'sqlite_master')
            tablenames = self.curs.execute(sql).fetchall()
            for tablename in tablenames:
                tablename = tablename[0]
                sql = """SELECT count(*) FROM %s"""%(prefix + tablename)
                try:
                    nr_of_rows = self.curs.execute(sql).fetchall()[0][0]
                except:
                    utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('ExportData', 'Sql failed while getting table row differences: %s'))%sql)
                else:
                    results.setdefault(tablename, {})[alias] = str(nr_of_rows)

        printable_results = []

        #Create header
        header = ['tablename']
        db_aliases = sorted([_x[0] for _x in db_aliases_and_prefixes])
        header.extend(db_aliases)
        printable_results.append(header)

        #Create table result rows
        for tablename, dbdict in sorted(results.items()):
            vals = [tablename]
            vals.extend([str(dbdict.get(alias, 'table_missing')) for alias in sorted(db_aliases)])
            if vals[1] != vals[2]:
                printable_results.append(vals)

        printable_msg = '\n'.join(['{0:40}{1:15}{2:15}'.format(result_row[0], result_row[1], result_row[2]) for result_row in printable_results])
        return printable_msg





