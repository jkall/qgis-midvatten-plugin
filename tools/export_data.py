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
import os, os.path
from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools.utils import common_utils, db_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.definitions import midvatten_defs as defs, db_defs

from midvatten.tools.import_data_to_db import midv_data_importer


class ExportData(object):

    def __init__(self, OBSID_P, OBSID_L):
        self.ID_obs_points = OBSID_P
        self.ID_obs_lines = OBSID_L
        self.dest_dbconnection = None
        self.source_dbconnection = None

    def export_2_csv(self,exportfolder):
        self.source_dbconnection = db_utils.DbConnectionManager()
        self.source_dbconnection.connect2db() #establish connection to the current midv db
        self.exportfolder = exportfolder
        self.write_data(self.to_csv, None, defs.get_subset_of_tables_fr_db(category='data_domains'))
        self.write_data(self.to_csv, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='obs_points'))
        self.write_data(self.to_csv, self.ID_obs_lines, defs.get_subset_of_tables_fr_db(category='obs_lines'))
        self.write_data(self.to_csv, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='extra_data_tables'))
        self.write_data(self.to_csv, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='interlab4_import_table'))

        self.source_dbconnection.closedb()

    def export_2_splite(self, target_db, dest_srid):
        """
        Exports a datagbase to a new spatialite database file
        :param target_db: The name of the new database file
        :param dest_srid:
        :return:

        """
        self.source_dbconnection = db_utils.DbConnectionManager()
        self.source_dbconnection.connect2db() #establish connection to the current midv db
        self.dest_dbconnection = db_utils.DbConnectionManager(target_db)
        self.dest_dbconnection.connect2db()

        self.midv_data_importer = midv_data_importer()

        self.write_data(self.to_sql, None, defs.get_subset_of_tables_fr_db(category='data_domains'), replace=True)
        self.dest_dbconnection.commit()
        self.write_data(self.to_sql, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='obs_points'))
        self.dest_dbconnection.commit()
        self.write_data(self.to_sql, self.ID_obs_lines, defs.get_subset_of_tables_fr_db(category='obs_lines'))
        self.dest_dbconnection.commit()
        self.write_data(self.to_sql, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='extra_data_tables'))
        self.dest_dbconnection.commit()
        self.write_data(self.to_sql, self.ID_obs_points, defs.get_subset_of_tables_fr_db(category='interlab4_import_table'))
        self.dest_dbconnection.commit()

        db_utils.delete_srids(self.dest_dbconnection.cursor, dest_srid)
        self.dest_dbconnection.commit()

        #Statistics
        statistics = self.get_table_rows_with_differences()

        self.dest_dbconnection.cursor.execute('vacuum')

        common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ExportData', "Export done, see differences in log message panel")), log_msg=ru(QCoreApplication.translate('ExportData', "Tables with different number of rows:\n%s")) % statistics)

        self.dest_dbconnection.commit_and_closedb()
        self.source_dbconnection.closedb()

    def get_number_of_rows(self, obsids, tname):
        sql = "select count(obsid) from %s"%tname
        if obsids:
            sql += " WHERE obsid IN ({})".format(common_utils.sql_unicode_list(obsids))
        nr_of_rows = self.source_dbconnection.execute_and_fetchall(sql)[0][0]
        return nr_of_rows

    def write_data(self, to_writer, obsids, ptabs, replace=False):
        for tname in ptabs:
            if not db_utils.verify_table_exists(tname, dbconnection=self.source_dbconnection):
                common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ExportData', "Table %s didn't exist. Skipping it.")) % tname)
                continue
            if self.dest_dbconnection is not None:
                if not db_utils.verify_table_exists(tname, dbconnection=self.dest_dbconnection):
                    if tname in defs.get_subset_of_tables_fr_db('extra_data_tables'):
                        sqlfile = db_defs.extra_datatables_sqlfile()
                        if not os.path.isfile(sqlfile):
                            common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ExportData',
                               'Programming error, file path not existing: %s. Skipping table %s'))%(sqlfile,
                                                                                                     tname))
                            continue
                        else:
                            db_utils.execute_sqlfile(sqlfile, self.dest_dbconnection, merge_newlines=True)
                            self.dest_dbconnection.commit()
                    else:
                        common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ExportData',
                                          'Programming error, table missing in new database: %s.')) %tname)

            if not obsids:
                to_writer(tname, obsids, replace)
            else:
                nr_of_rows = self.get_number_of_rows(obsids, tname)
                if nr_of_rows > 0: #only go on if there are any observations for this obsid
                    to_writer(tname, obsids, replace)

    def to_csv(self, tname, obsids=None, replace=False):
        """
        Write to csv
        :param tname: The destination database
        :param obsids:
        :return:
        """
        sql = "SELECT * FROM %s"%tname
        if obsids:
            sql += " WHERE obsid IN ({})".format(common_utils.sql_unicode_list(obsids))
        data = self.source_dbconnection.execute_and_fetchall(sql)
        printlist = [[col[0] for col in self.source_dbconnection.cursor.description]]
        printlist.extend(data)
        filename = os.path.join(self.exportfolder, tname + ".csv")
        common_utils.write_printlist_to_file(filename, printlist)

    def to_sql(self, tname, obsids=None, replace=False):
        """
        Write to new sql database
        :param tname: The destination database
        :param tname_with_prefix: The source database
        :param obsids:
        :return:
        """

        dest_data = None

        source_srid = self.source_dbconnection.get_srid(tname)
        dest_srid = self.dest_dbconnection.get_srid(tname)

        if source_srid is dest_srid or source_srid == dest_srid:
            file_data_srid = dest_srid
        else:
            file_data_srid = 4326

        source_data = self.get_table_data(tname, obsids, self.source_dbconnection, file_data_srid)
        if replace:
            self.dest_dbconnection.execute('''PRAGMA foreign_keys = OFF;''')
            dest_data = self.get_table_data(tname, obsids, self.dest_dbconnection, file_data_srid)
            if dest_data:
                print("Here replace " + tname + str(dest_data))
                print("Replace with " + str(source_data))
                self.dest_dbconnection.execute('''DELETE FROM {}'''.format(tname))

        if tname == 'obs_points':
            geom_column = list(db_utils.get_geometry_types(self.source_dbconnection, tname).keys())[0]
            source_data = [set_east_north_to_null(row, source_data[0], geom_column) if rownr > 0
                           else row
                           for rownr, row in enumerate(source_data)]

        self.midv_data_importer.general_import(tname, source_data,
                                               _dbconnection=self.dest_dbconnection,
                                               source_srid=file_data_srid,
                                               skip_confirmation=True,
                                               binary_geometry=True)

        if replace and dest_data is not None:
            self.midv_data_importer.general_import(tname, dest_data,
                                                   _dbconnection=self.dest_dbconnection,
                                                   source_srid=file_data_srid,
                                                   skip_confirmation=True)
            self.dest_dbconnection.execute('''PRAGMA foreign_keys = ON;''')

    def get_table_data(self, tname, obsids, dbconnection, file_data_srid):
        dbconnection.execute("SELECT * FROM %s LIMIT 1"%tname)
        columns = [x[0] for x in dbconnection.cursor.description]


        if file_data_srid:
            astext = 'ST_AsBinary(ST_Transform({}, %s))'%str(file_data_srid)
        else:
            astext = 'ST_AsBinary({})'

        geom_columns = list(db_utils.get_geometry_types(dbconnection, tname).keys())
        #Transform to 4326 just to be sure that both the source and dest database has support for the srid.
        select_columns = [astext.format(col)
                          if (col.lower() in geom_columns and dbconnection.get_srid(tname, col))
                          else col
                          for col in columns]

        sql = '''SELECT {} FROM {}'''.format(u', '.join(select_columns), tname)
        if obsids:
            sql += " WHERE obsid IN ({})".format(common_utils.sql_unicode_list(obsids))
        dbconnection.execute(sql)
        print(str(sql))
        table_data = [[x.lower() for x in columns]]
        table_data.extend([row for row in dbconnection.execute_and_fetchall(sql)])
        if len(table_data) < 2:
            return None
        else:
            return table_data

    def get_table_rows_with_differences(self):
        """
        Counts rows for all tables in new and old database and returns those that differ.
        self.cursor is required where the new database is the regular one and the old database is the attached one
        :param db_aliases_and_prefixes: A list of tuples like ('new', '')
        :return:  a printable list of nr of rows for all tables
        """
        results = {}
        db_aliases_and_connections = [('exported_db', self.dest_dbconnection), ('source_db', self.source_dbconnection)]
        for alias, dbconnection in db_aliases_and_connections:
            tablenames = db_utils.get_tables(dbconnection, skip_views=True)
            for tablename in tablenames:
                sql = """SELECT count(*) FROM %s"""%(tablename)
                try:
                    nr_of_rows = dbconnection.execute_and_fetchall(sql)[0][0]
                except:
                    common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('ExportData', 'Sql failed while getting table row differences: %s')) % sql)
                else:
                    results.setdefault(tablename, {})[alias] = str(nr_of_rows)

        printable_results = []

        #Create header
        header = ['tablename']
        db_aliases = sorted([_x[0] for _x in db_aliases_and_connections])
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


def set_east_north_to_null(row, header, geometry):
    res = list(row)
    if res[header.index(geometry)]:
        res[header.index('east')] = None
        res[header.index('north')] = None
    return res