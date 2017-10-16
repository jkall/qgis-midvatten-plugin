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
from pyspatialite import dbapi2 as sqlite
import csv, codecs, cStringIO, os, os.path
import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from definitions import midvatten_defs as defs
import qgis.utils
from qgis.core import QgsMessageLog
from PyQt4.QtCore import QCoreApplication

class ExportData():

    def __init__(self, OBSID_P, OBSID_L):
        self.ID_obs_points = OBSID_P
        self.ID_obs_lines = OBSID_L

    def export_2_csv(self,exportfolder):
        database = db_utils.DbConnectionManager()
        database.connect2db() #establish connection to the current midv db
        self.curs = database.cursor#get a cursor

        self.exportfolder = exportfolder
        self.write_data(self.to_csv, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='obs_points'),
                        db_utils.verify_table_exists)
        self.write_data(self.to_csv, self.ID_obs_lines, defs.get_subset_of_tables_fr_db(category='obs_lines'),
                        db_utils.verify_table_exists)
        self.write_data(self.zz_to_csv, u'no_obsids', defs.get_subset_of_tables_fr_db(category='data_domains'),
                        db_utils.verify_table_exists)
        database.closedb()

    def export_2_splite(self,target_db,source_db, EPSG_code):
        """
        Exports a datagbase to a new spatialite database file
        :param target_db: The name of the new database file
        :param source_db: The name of the source database file
        :param EPSG_code:
        :return:

        """
        conn = sqlite.connect(target_db,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.curs = conn.cursor()
        self.curs.execute("PRAGMA foreign_keys = ON")
        self.curs.execute(r"""ATTACH DATABASE '%s' AS a"""%source_db)
        conn.commit()  # commit sql statements so far

        old_table_column_srid = self.get_table_column_srid(prefix='a')
        self.write_data(self.to_sql, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='obs_points'), self.verify_table_in_attached_db, 'a.')
        conn.commit()
        self.write_data(self.to_sql, self.ID_obs_lines, defs.get_subset_of_tables_fr_db(category='obs_lines'), self.verify_table_in_attached_db, 'a.')
        conn.commit()
        self.write_data(self.zz_to_sql, u'no_obsids', defs.get_subset_of_tables_fr_db(category='data_domains'), self.verify_table_in_attached_db, 'a.')
        conn.commit()

        delete_srid_sql = r"""delete from spatial_ref_sys where srid NOT IN ('%s', '4326')""" % EPSG_code
        try:
            self.curs.execute(delete_srid_sql)
        except:
            utils.MessagebarAndLog.info(
                log_msg=ru(QCoreApplication.translate(u'ExportData', u'Removing srids failed using: %s'))%str(delete_srid_sql))

        conn.commit()

        #Statistics
        statistics = self.get_table_rows_with_differences()

        self.curs.execute(r"""DETACH DATABASE a""")
        self.curs.execute('vacuum')

        utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'ExportData', u"Export done, see differences in log message panel")), log_msg=ru(QCoreApplication.translate(u'ExportData', u"Tables with different number of rows:\n%s"))%statistics)

        conn.commit()
        conn.close()

    def get_table_column_srid(self, prefix=None):
        """

        :return: A tuple of tuples like ((tablename, columnname, srid), ...)
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
        formatted_obsids = u''.join([u'(', u', '.join([u"'{}'".format(k) for k in ru(obsids, True)]), u')'])
        return formatted_obsids

    def get_number_of_obsids(self, obsids, tname):
        no_of_obs_cursor = self.curs.execute(u"select count(obsid) from %s where obsid in %s" %(tname, self.format_obsids(obsids)))
        no_of_obs = no_of_obs_cursor.fetchall()
        return no_of_obs

    def write_data(self, to_writer, obsids, ptabs, verify_table_exists, tname_prefix=''):
        if len(obsids) > 0 or obsids == u'no_obsids':#only if there are any obs_points selected at all
            for tname in ptabs:
                tname_with_prefix = tname_prefix + tname
                if not verify_table_exists(tname):
                    continue

                if obsids != u'no_obsids':
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
        output = UnicodeWriter(file(os.path.join(self.exportfolder, tname + ".csv"), 'w'))
        self.curs.execute(u"select * from %s where obsid in %s"%(tname, self.format_obsids(obsids)))
        output.writerow([col[0] for col in self.curs.description])
        filter(None, (output.writerow(row) for row in self.curs))

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

        for reference_table, from_to_fields in foreign_keys.iteritems():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]

            #If the current table contains obsid, filter only the chosen ones.
            try:
                sql = u"""INSERT OR IGNORE INTO %s (%s) select distinct %s from  %s where obsid in %s"""%(reference_table, ', '.join(to_list), ', '.join(from_list), tname_with_prefix, self.format_obsids(obsids))
            except:
                sql = u"""INSERT OR IGNORE INTO %s (%s) select distinct %s from  %s"""%(reference_table, ', '.join(to_list), ', '.join(from_list), tname_with_prefix)
            try:
                self.curs.execute(sql)
            except Exception, e:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'ExportData', u'INSERT failed while importing to %s.\nMsg:%s'))%(tname, str(e)))

        #Make a transformation for column names that are geometries #Transformation doesn't work yet.
        old_table_column_srid_dict = self.get_table_column_srid(prefix='a')
        new_table_column_srid_dict = self.get_table_column_srid()

        if tname in old_table_column_srid_dict and tname in new_table_column_srid_dict:
            transformed_column_names = self.transform_geometries(tname, column_names, old_table_column_srid_dict, new_table_column_srid_dict) #Transformation doesn't work since east, north is not updated.
        else:
            transformed_column_names = column_names

        sql = u"""INSERT INTO %s (%s) SELECT %s FROM %s WHERE obsid IN %s"""%(tname, u', '.join(column_names), u', '.join(transformed_column_names), tname_with_prefix, self.format_obsids(obsids))
        try:
            self.curs.execute(sql)
        except Exception, e:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'ExportData', u"Export warning: sql failed. See message log.")), log_msg=ru(QCoreApplication.translate(u'ExportData', u'%s\nmsg:\n%s'))%(sql, str(e)))

    @staticmethod
    def transform_geometries(tname, column_names, old_table_column_srid_dict, new_table_column_srid_dict):
        ur"""
        Transform geometry columns to new chosen SRID

        The transformation is only done if the chosen srid is not the same as the old srid,
        and if the geometry column in question exists in both the old and the new database

        :param tname: The table name
        :param column_names: a list of columns that will be copied from the old table/database to the new table/database
        :param old_table_column_srid_dict: a dict like  {u'testt': {u'geom': 3006}}. A dict with tables that have geometries. The inner dict is the column and the srid.
        :param new_table_column_srid_dict: a dict like  {u'testt': {u'geom': 3006}}. A dict with tables that have geometries. The inner dict is the column and the srid.
        :return: A list of columns where the geometry columns are Transformed.

        >>> ExportData.transform_geometries(u'testt', [u'notgeom', u'geom'], {u'testt': {u'geom': 3006}}, {u'testt': {u'geom': 3006}})
        [u'notgeom', u'geom']
        >>> ExportData.transform_geometries(u'testt', [u'notgeom', u'geom'], {u'testt': {u'geom': 3006}}, {u'testt': {u'geom': 3010}})
        [u'notgeom', u'ST_Transform(geom, 3010)']
        >>> ExportData.transform_geometries(u'obs_points', [u'obsid', u'east', u'north', u'geom'], {u'obs_points': {u'geom': 3006}}, {u'obs_points': {u'geom': 3010}})
        [u'obsid', u'X(ST_Transform(geom, 3010))', u'Y(ST_Transform(geom, 3010))', u'ST_Transform(geom, 3010)']
        """
        transformed = False
        #Make a transformation for column names that are geometries
        if tname in new_table_column_srid_dict and tname in old_table_column_srid_dict:
            transformed_column_names = []
            for column in column_names:
                new_srid = new_table_column_srid_dict.get(tname, {}).get(column, None)
                old_srid = old_table_column_srid_dict.get(tname, {}).get(column, None)
                if old_srid is not None and new_srid is not None and old_srid != new_srid:
                    transformed_column_names.append(u'ST_Transform({}, {})'.format(column, ru(new_srid)))
                    utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'ExportData', u'Transformation for table %s column %s from %s to %s"'))%(tname, column, str(old_srid), str(new_srid)))
                    transformed = True
                else:
                    transformed_column_names.append(column)
        else:
            transformed_column_names = column_names

        #Special case for obs_points because of the very special columns east/north
        if tname == u'obs_points' and transformed:
            old_geocol_srids = [(k, v) for k, v in old_table_column_srid_dict.get(tname, {}).iteritems()]
            new_geocol_srids = [(k, v) for k, v in new_table_column_srid_dict.get(tname, {}).iteritems()]
            if len(old_geocol_srids) != 1 and len(new_geocol_srids) != 1:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'ExportData', u'Export warning!, see Log Message Panel')), log_msg=ru(QCoreApplication.translate(u'ExportData', u'Transformation of east/north for table obs_points failed! The number of geometry columns was not == 1!')))
            else:
                new_srid = new_geocol_srids[0][1]
                old_geometry_column = old_geocol_srids[0][0]

                res = []
                for column in transformed_column_names:
                    if column == u'east':
                        res.append(u'X(ST_Transform(%s, %s))'%(old_geometry_column, new_srid))
                    elif column == u'north':
                        res.append(u'Y(ST_Transform(%s, %s))'%(old_geometry_column, new_srid))
                    else:
                        res.append(column)
                transformed_column_names = res

        return transformed_column_names

    def zz_to_csv(self, tname, tname_with_prefix):
        output = UnicodeWriter(file(os.path.join(self.exportfolder, tname + ".csv"), 'w'))
        self.curs.execute(r"select * from %s"%(tname))
        output.writerow([col[0] for col in self.curs.description])
        filter(None, (output.writerow(row) for row in self.curs))

    def zz_to_sql(self, tname, tname_with_prefix):
        column_names = self.get_and_check_existing_column_names(tname, tname_with_prefix)
        if column_names is None:
            return None

        #Null-values as primary keys don't equal each other and can therefore cause duplicates.
        #This part concatenates the primary keys to make a string comparison for equality instead.
        primary_keys = self.get_primary_keys(tname)
        ifnull_primary_keys = [''.join(["ifnull(", pk, ",'')"]) for pk in primary_keys]
        concatenated_primary_keys = ' || '.join(ifnull_primary_keys)

        sql = u"""INSERT INTO %s (%s) select %s from %s where %s not in (select %s from %s)"""%(tname, ', '.join(column_names), ', '.join(column_names), tname_with_prefix, concatenated_primary_keys, concatenated_primary_keys, tname)
        try:
            self.curs.execute(sql)
        except Exception, e:
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'ExportData', u'INSERT failed while importing to %s. Using INSERT OR IGNORE instead.\nMsg:%s'))%(tname, str(e)))
            sql = sql.replace(u'INSERT', u'INSERT OR IGNORE')
            try:
                self.curs.execute(sql)
            except Exception, e:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'ExportData', u"Export warning: sql failed. See message log.")), log_msg=ru(QCoreApplication.translate(u'ExportData', u'%s\nmsg:\n%s'))%(sql, str(e)))

    def get_foreign_keys(self, tname):
        result_list = self.curs.execute("""PRAGMA foreign_key_list(%s)"""%(tname)).fetchall()
        foreign_keys = {}
        for row in result_list:
            foreign_keys.setdefault(row[2], []).append((row[3], row[4]))
        return foreign_keys

    def get_primary_keys(self, tname):
        result_list = self.curs.execute("""PRAGMA table_info(%s)"""%(tname)).fetchall()
        primary_keys = [column_tuple[1] for column_tuple in result_list if column_tuple[5] != 0]
        return primary_keys

    def verify_table_in_attached_db(self, tname):
        result = self.curs.execute(u"""SELECT name FROM a.sqlite_master WHERE type='table' AND name='%s'"""%(tname)).fetchall()
        if result:
            return True
        else:
            return False

    def get_and_check_existing_column_names(self, tname, tname_with_prefix):

        new_column_names = self.get_column_names(tname)
        if new_column_names is None:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'ExportData', u'Export warning!, see Log Message Panel')), log_msg=ru(QCoreApplication.translate(u'ExportData', u"Table %s export failed!"))%tname)
            return None

        prefix = tname_with_prefix.split(u'.')[0]
        tname_with_prefix_without_prefix = tname_with_prefix.replace(prefix + u'.', u'')
        old_column_names = self.get_column_names(tname_with_prefix_without_prefix, prefix)
        if old_column_names is None:
            utils.MessagebarAndLog.critical(bar_msg=u'Export warning!, see Log Message Panel', log_msg=u"Table " + tname + u" export failed!")
            return None

        #Check which columns that doesn't exist from in old and new database and write a log msg about it.
        old_columns_missing_in_new = [col for col in old_column_names if col not in new_column_names]
        new_columns_missing_in_old = [col for col in new_column_names if col not in old_column_names]

        """
        #TODO: Temporary msg:
        utils.MessagebarAndLog.info(log_msg=u'Table ' + tname)
        utils.MessagebarAndLog.info(log_msg=u"old_column_names " + str(old_column_names))
        utils.MessagebarAndLog.info(log_msg=u"new_column_names " + str(new_column_names))
        utils.MessagebarAndLog.info(log_msg=u"old_columns_missing_in_new " + str(old_columns_missing_in_new))
        utils.MessagebarAndLog.info(log_msg=u"new_columns_missing_in_old " + str(new_columns_missing_in_old))
        """

        missing_columns_msg = [ru(QCoreApplication.translate(u'ExportData', u'Table %s:'))%tname]
        if new_columns_missing_in_old:
            missing_columns_msg.append(ru(QCoreApplication.translate(u'ExportData', u'\nNew columns missing in old database: %s'))%u', '.join(new_columns_missing_in_old))
        if old_columns_missing_in_new:
            missing_columns_msg.append(ru(QCoreApplication.translate(u'ExportData', u'\nOld columns missing in new database: %s'))%u', '.join(old_columns_missing_in_new))
        if len(missing_columns_msg) > 1:
                utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'ExportData', u'Export warning, see Log Message Panel')), log_msg=u''.join(missing_columns_msg))

        #Check if a primary key in the new database is missing in the old database and skip the table if there are missing primary keys.
        primary_keys = self.get_primary_keys(tname)
        missing_primary_keys = [col for col in primary_keys if col in new_columns_missing_in_old]
        if missing_primary_keys:
            missing_pk_msg = ru(QCoreApplication.translate(u'ExportData', u'Table %s:\nPrimary keys are missing in old database. The table will not be exported!!!'))%(tname, u'", "'.join(missing_primary_keys))
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'ExportData', u'Export warning!, see Log Message Panel')), log_msg=missing_pk_msg)
            return None

        #Only copy columns from old to new database that exist in old database.
        column_names = [col for col in new_column_names if col in old_column_names]
        return column_names

    def get_column_names(self, tname, prefix=None):

        if prefix is None:
            sql = """PRAGMA table_info(%s)"""%tname
        else:
            sql = '''PRAGMA "%s".table_info(%s)'''%(prefix, tname)

        try:
            result_list = self.curs.execute(sql).fetchall()
        except Exception, e:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'ExportData', u"Export warning: sql failed. See message log.")), log_msg=ru(QCoreApplication.translate(u'ExportData', u'%s\nmsg:\n%s'))%(sql, str(e)))
            return None

        columns = [col[1] for col in result_list] #Load column names from sqlite table
        return columns

    def get_table_rows_with_differences(self, db_aliases_and_prefixes=[(u'exported_db', u''), (u'source_db', u'a.')]):
        """
        Counts rows for all tables in new and old database and returns those that differ.
        self.cursor is required where the new database is the regular one and the old database is the attached one
        :param db_aliases_and_prefixes: A list of tuples like ('new', '')
        :return:  a printable list of nr of rows for all tables
        """
        results = {}
        for alias, prefix in db_aliases_and_prefixes:
            sql = u"""SELECT name FROM %s WHERE type='table';"""%(prefix + u'sqlite_master')
            tablenames = self.curs.execute(sql).fetchall()
            for tablename in tablenames:
                tablename = tablename[0]
                sql = u"""SELECT count(*) FROM %s"""%(prefix + tablename)
                try:
                    nr_of_rows = self.curs.execute(sql).fetchall()[0][0]
                except:
                    utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate(u'ExportData', u'Sql failed while getting table row differences: %s'))%sql)
                else:
                    results.setdefault(tablename, {})[alias] = str(nr_of_rows)

        printable_results = []

        #Create header
        header = [u'tablename']
        db_aliases = sorted([_x[0] for _x in db_aliases_and_prefixes])
        header.extend(db_aliases)
        printable_results.append(header)

        #Create table result rows
        for tablename, dbdict in sorted(results.iteritems()):
            vals = [tablename]
            vals.extend([str(dbdict.get(alias, u'table_missing')) for alias in sorted(db_aliases)])
            if vals[1] != vals[2]:
                printable_results.append(vals)

        printable_msg = '\n'.join(['{0:40}{1:15}{2:15}'.format(result_row[0], result_row[1], result_row[2]) for result_row in printable_results])
        return printable_msg


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    Source: http://docs.python.org/library/csv.html#csv-examples
    Modified to cope with non-string columns.
    """

    def __init__(self, f, dialect=csv.excel, delimiter=';', encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, delimiter=delimiter,**kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def encodeone(self, item):
        if type(item) == unicode:
            return self.encoder.encode(item)
        else:
            return item

    def writerow(self, row):
        self.writer.writerow([self.encodeone(s) for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
