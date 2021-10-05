# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles the db connections

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-11-27
        copyright            : (C) 2016 by HenrikSpa (and joskal)
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

import ast
import os
import traceback
import zipfile
from builtins import object
from builtins import str

import qgis.PyQt
from PyQt5.QtCore import QCoreApplication

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

import datetime
import psycopg2
import re
import tempfile
from collections import OrderedDict
import sqlite3 as sqlite

import  qgis.core
from qgis.PyQt.QtCore import QCoreApplication, QSettings

from qgis.utils import spatialite_connect
from qgis.core import QgsProject, QgsDataSourceUri, QgsCredentials
import db_manager.db_plugins.connector
import db_manager.db_plugins.spatialite.connector as spatialite_connector

from midvatten.tools.utils.common_utils import MessagebarAndLog, returnunicode as ru, UsageError, UserInterruptError, \
    sql_failed_msg, write_printlist_to_file


class PostGisDBConnectorMod(db_manager.db_plugins.postgis.connector.PostGisDBConnector):
    """
    Based on db_manager.db_plugins.postgis.connector.PostGisDBConnector
    """
    def __init__(self, uri):
        self.connection = None

        self.host = uri.host() or os.environ.get('PGHOST')
        self.port = uri.port() or os.environ.get('PGPORT')

        username = uri.username() or os.environ.get('PGUSER')
        password = uri.password() or os.environ.get('PGPASSWORD')

        # Do not get db and user names from the env if service is used
        if not uri.service():
            if username is None:
                username = os.environ.get('USER')
            self.dbname = uri.database() or os.environ.get('PGDATABASE') or username
            uri.setDatabase(self.dbname)

        expandedConnInfo = str(uri.connectionInfo(True))
        try:
            self.connection = psycopg2.connect(expandedConnInfo)
        except self.connection_error_types() as e:
            # get credentials if cached or asking to the user no more than 3 times
            err = str(e)
            conninfo = uri.connectionInfo(False)

            for i in range(3):
                (ok, username, password) = QgsCredentials.instance().get(conninfo, username, password, err)
                if not ok:
                    raise ConnectionError(e)

                if username:
                    uri.setUsername(username)

                if password:
                    uri.setPassword(password)

                newExpandedConnInfo = uri.connectionInfo(True)
                try:
                    self.connection = psycopg2.connect(newExpandedConnInfo)
                    QgsCredentials.instance().put(conninfo, username, password)
                except self.connection_error_types() as e:
                    if i == 2:
                        raise ConnectionError(e)
                    err = str(e)
                finally:
                    # clear certs for each time trying to connect
                    self._clearSslTempCertsIfAny(newExpandedConnInfo)
        finally:
            # clear certs of the first connection try
            self._clearSslTempCertsIfAny(expandedConnInfo)

        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)


class DbConnectionManager(object):
    def __init__(self, db_settings=None):
        """
        Manuals for db connectors:
        https://github.com/qgis/QGIS/blob/master/python/plugins/db_manager/db_plugins/connector.py
        https://github.com/qgis/QGIS/blob/master/python/plugins/db_manager/db_plugins/postgis/connector.py
        https://github.com/qgis/QGIS/blob/master/python/plugins/db_manager/db_plugins/spatialite/connector.py
        """
        self.conn = None
        self.cursor = None
        self.connector = None

        if db_settings is None:
            db_settings = QgsProject.instance().readEntry("Midvatten", "database")[0]

        if isinstance(db_settings, str):
            #Test if the db_setting is an old database
            if os.path.isfile(db_settings):
                db_settings = {'spatialite': {'dbpath': db_settings}}
            else:
                if not db_settings:
                    raise UsageError(ru(QCoreApplication.translate('DbConnectionManager', 'Database setting was empty. Check DB tab in Midvatten settings.')))
                else:
                    try:
                        db_settings = ast.literal_eval(db_settings)
                    except:
                        raise UsageError(ru(QCoreApplication.translate('DbConnectionManager', 'Database could not be set. Check DB tab in Midvatten settings.')))

        elif isinstance(db_settings, dict):
            # Assume it the dict is a valid db_settings dict.
            pass
        else:
            raise Exception(ru(QCoreApplication.translate('DbConnectionManager', "DbConnectionManager programming error: db_settings must be either a dict like {'spatialite': {'dbpath': 'x'} or a string representation of it. Was: %s"))%ru(db_settings))

        db_settings = ru(db_settings, keep_containers=True)

        self.db_settings = db_settings

        self.dbtype = list(self.db_settings.keys())[0]
        self.connection_settings = list(self.db_settings.values())[0]

        self.uri = QgsDataSourceUri()

        if self.dbtype == 'spatialite':
            self.dbpath = ru(self.connection_settings['dbpath'])

            if not os.path.isfile(self.dbpath):
                raise UsageError(ru(QCoreApplication.translate('DbConnectionManager', 'Database error! File "%s" not found! Check db tab in Midvatten settings!')) % self.dbpath)

            self.check_db_is_locked()

            #Create the database if it's not existing
            self.uri.setDatabase(self.dbpath)

            try:
                self.connector = spatialite_connector.SpatiaLiteDBConnector(self.uri)
            except Exception as e:

                MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('DbConnectionManager', 'Connecting to spatialite db %s failed! Check that the file or path exists.')) % self.dbpath,
                                                                   log_msg=ru(QCoreApplication.translate('DbConnectionManager', 'msg %s'))%str(e))
                raise

        elif self.dbtype == 'postgis':
            connection_name = self.connection_settings['connection'].split('/')[0]
            self.postgis_settings = get_postgis_connections()[connection_name]
            self.uri.setConnection(self.postgis_settings['host'], self.postgis_settings['port'], self.postgis_settings['database'], self.postgis_settings['username'], self.postgis_settings['password'])
            try:
                self.connector = PostGisDBConnectorMod(self.uri)
            except Exception as e:
                if 'no password supplied' in str(e):
                    MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('DbConnectionManager', 'No password supplied for postgis connection')))
                    raise UserInterruptError()
                else:
                    raise

        if self.connector is not None:
            self.conn = self.connector.connection
            self.cursor = self.conn.cursor()

    def connect2db(self):
        self.check_db_is_locked()
        if self.cursor:
            return True

    def execute(self, sql, all_args=None):
        """

        :param sql:
        :param all_args: A list of lists of equal lenght to sql (if sql is a list) containing arguments for ? in the
        corresponding sql.
        :return:
        """
        if isinstance(sql, str):
            sql = [sql]
        elif not isinstance(sql, (list, tuple)):
            raise TypeError(ru(QCoreApplication.translate('DbConnectionManager', 'DbConnectionManager.execute: sql must be type string or a list/tuple of strings. Was %s'))%ru(type(sql)))
        for idx, line in enumerate(sql):
            if all_args is None:
                try:
                    self.cursor.execute(line)
                except Exception as e:
                    textstring = ru(QCoreApplication.translate('sql_load_fr_db', """DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (ru(line), ru(str(e)))
                    MessagebarAndLog.warning(
                        bar_msg=sql_failed_msg(),
                        log_msg=textstring)
                    raise
            elif isinstance(all_args, (list, tuple)):
                args = all_args[idx]
                try:
                    self.cursor.execute(line, args)
                except Exception as e:
                    textstring = ru(QCoreApplication.translate('sql_load_fr_db', """DB error!\n SQL causing this error:%s\nusing args %s\nMsg:\n%s""")) % (ru(line), ru(args), ru(str(e)))
                    MessagebarAndLog.warning(
                        bar_msg=sql_failed_msg(),
                        log_msg=textstring)
                    raise
            else:
                raise TypeError(ru(QCoreApplication.translate('DbConnectionManager', 'DbConnectionManager.execute: all_args must be a list/tuple. Was %s')) % ru(type(all_args)))

    def execute_and_fetchall(self, sql):
        try:
            self.cursor.execute(sql)
        except (sqlite.OperationalError, Exception) as e:
            textstring = ru(QCoreApplication.translate('sql_load_fr_db',
                                                                        """DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (
                         ru(sql), ru(str(e)))
            MessagebarAndLog.warning(
                bar_msg=sql_failed_msg(),
                log_msg=textstring)
            raise

        return self.cursor.fetchall()

    def execute_and_commit(self, sql, all_args=None):
        self.execute(sql, all_args=all_args)
        self.commit()

    def commit(self):
        self.conn.commit()

    def commit_and_closedb(self):
        self.commit()
        self.closedb()

    def schemas(self):
        """Only supports schema public
        """
        return 'public'

    def closedb(self):
        self.conn.close()

    def internal_tables(self):
        if self.dbtype == 'spatialite':
            return sqlite_internal_tables()
        else:
            return postgis_internal_tables()

    def check_db_is_locked(self):
        if self.dbtype == 'spatialite':
            for ext in ('journal', 'wal'):
                if os.path.exists('%s-%s'%(self.dbpath, ext)):
                    raise DatabaseLockedError(ru(QCoreApplication.translate('DbConnectionManager', "Error, The database is already in use (a %s-file was found)".format(ext))))

    def vacuum(self):
        if self.dbtype == 'spatialite':
            self.execute('VACUUM')
        else:
            self.execute('VACUUM ANALYZE')

    def create_temporary_table_for_import(self, temptable_name, fieldnames_types, geometry_colname_type_srid=None):

        if not temptable_name.startswith('temp_'):
            temptable_name = 'temp_%s'%temptable_name
        existing_names = list(tables_columns(dbconnection=self).keys())
        while temptable_name in existing_names: #this should only be needed if an earlier import failed. if so, propose to rename the temporary import-table
            reponse = qgis.PyQt.QtWidgets.QMessageBox.question(None, ru(QCoreApplication.translate('DbConnectionManager', "Warning - Table name confusion!")),ru(QCoreApplication.translate('midv_data_importer', '''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''))%(self.temptable_name, self.temptable_name, self.temptable_name), qgis.PyQt.QtWidgets.QMessageBox.Yes | qgis.PyQt.QtWidgets.QMessageBox.No)
            if reponse == qgis.PyQt.QtWidgets.QMessageBox.Yes:
                self.temptable_name = '%s_2' % self.temptable_name
            else:
                raise UserInterruptError()

        if self.dbtype == 'spatialite':
            temptable_name = 'mem.' + temptable_name
            try:
                self.cursor.execute("""ATTACH DATABASE ':memory:' AS mem""")
            except:
                #Assume mem already exist.
                pass

            if geometry_colname_type_srid is not None:
                geom_column = geometry_colname_type_srid[0]
                geom_type = geometry_colname_type_srid[1]
                srid = geometry_colname_type_srid[2]
                fieldnames_types.append('geometry %s'%geometry_colname_type_srid[0])
                sql = """CREATE table %s (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, %s)"""%(temptable_name, ', '.join(fieldnames_types))
                self.execute(sql)
                self.conn.commit()

                # This sql doesnt work for some reason, error msg "RecoverGeometryColumn() error: table 'mem.temp_temporary_section_line' does not exist"
                # Doesn't seem to work with memory databases. It doesn't seem to be needed for us though.
                try:
                    sql = """SELECT RecoverGeometryColumn('%s','%s',%s,'%s',2) from %s AS a"""%(temptable_name, geom_column, srid, geom_type, temptable_name)
                    self.execute(sql)
                except:
                    pass
            else:
                sql = """CREATE table %s (%s)""" % (temptable_name, ', '.join(fieldnames_types))
                self.execute(sql)
        else:
            self.execute("""CREATE TEMPORARY table %s (%s)""" % (temptable_name, ', '.join(fieldnames_types)))
            if geometry_colname_type_srid is not None:
                geom_column = geometry_colname_type_srid[0]
                geom_type = geometry_colname_type_srid[1]
                srid = geometry_colname_type_srid[2]
                sql = """ALTER TABLE %s ADD COLUMN %s geometry(%s, %s);""" % (temptable_name, geom_column, geom_type, srid)
                self.execute(sql)
        return temptable_name

    def drop_temporary_table(self, temptable_name):
        if self.dbtype == 'spatialite':
            self.execute('''DROP TABLE {}'''.format(temptable_name))
        else:
            self.execute('''DROP TEMPORARY TABLE IF EXISTS {}'''.format(temptable_name))

    def dump_table_2_csv(self, table_name=None):
        self.cursor.execute(u'select * from {}'.format(table_name))
        header = [col[0] for col in self.cursor.description]
        rows = self.cursor.fetchall()
        if rows:
            filename = os.path.join(tempfile.gettempdir(), '{}.csv'.format(table_name))
            printlist = [header]
            printlist.extend(rows)
            write_printlist_to_file(filename, printlist)

    def get_srid(self, table_name, geometry_column='geometry'):
        srid = None
        if self.dbtype == 'spatialite':
            srid = self.execute_and_fetchall("""SELECT srid FROM geometry_columns WHERE f_table_name = '%s'""" % table_name)
            if not srid:
                srid = None
            else:
                srid = srid[0][0]
        else:
            try:
                self.cursor.execute("""SELECT Find_SRID('{}', '{}', '{}');""".format(self.schemas(), table_name,
                                                                                     geometry_column))
            except:
                #Assume that the column doesn't have a srid/is a geometry.
                srid = None
            else:

                srid = self.cursor.fetchall()[0][0]
        if srid is not None:
            srid = int(srid)
        return srid

def connect_with_spatialite_connect(dbpath):
    conn = spatialite_connect(dbpath, detect_types=sqlite.PARSE_DECLTYPES | sqlite.PARSE_COLNAMES)
    return conn


def check_connection_ok(write_error_msg=True):
    try:
        dbconnection = DbConnectionManager()
        connection_ok = dbconnection.connect2db()
        dbconnection.closedb()
    except Exception as e:
        if write_error_msg:
            MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('check_connection_ok', 'Could not connect to db: %s')) % str(e),
                                                               duration=30)
        connection_ok = False
    return connection_ok


def if_connection_ok(func):
    def func_wrapper(*args, **kwargs):
        if check_connection_ok():
            ret = func(*args, **kwargs)
        else:
            ret = None
        return ret
    return func_wrapper


def get_postgis_connections():
    qs = QSettings()
    postgresql_connections = {}
    for k in sorted(qs.allKeys()):
        k = ru(k)
        if k.startswith('PostgreSQL'):
            cols = k.split('/')
            conn_name = cols[2]
            try:
                setting = cols[3]
            except IndexError:
                #utils.MessagebarAndLog.info(log_msg='Postgresql connection info: Setting ' + str(k) + " couldn't be read")
                continue
            value = qs.value(k)
            postgresql_connections.setdefault(conn_name, {})[setting] = value

    postgresql_connections= ru(postgresql_connections, keep_containers=True)
    return postgresql_connections


def sql_load_fr_db(sql, dbconnection=None, print_error_message_in_bar=True):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    try:
        result = dbconnection.execute_and_fetchall(sql)
    except Exception as e:
        textstring = ru(QCoreApplication.translate('sql_load_fr_db', """DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (ru(sql), ru(str(e)))
        if print_error_message_in_bar:
            MessagebarAndLog.warning(bar_msg=sql_failed_msg(), duration=4)
        MessagebarAndLog.warning(log_msg=textstring)
        res = (False, [])
    else:
        res = (True, result)

    if dbconnection_created:
        dbconnection.closedb()

    return res


def sql_alter_db(sql, dbconnection=None, all_args=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        try:
            dbconnection.execute('PRAGMA foreign_keys = ON')
        except:
            pass
    try:
        dbconnection.execute_and_commit(sql, all_args=all_args)
    except Exception as e:
        textstring = ru(QCoreApplication.translate('sql_alter_db', """DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (
        ru(sql), ru(str(e)))
        MessagebarAndLog.warning(
            bar_msg=ru(QCoreApplication.translate('sql_alter_db', 'Some sql failure, see log for additional info.')),
            log_msg=textstring, duration=4)

    if dbconnection_created:
        dbconnection.closedb()

def execute_sqlfile_using_func(sqlfilename, function=sql_alter_db):
    with open(sqlfilename, 'r') as f:
        f.readline()  # first line is encoding info....
        for line in f:
            if not line:
                continue
            if line.startswith("#"):
                continue
            function(line)

def execute_sqlfile(sqlfilename, dbconnection, merge_newlines=False):
    with open(sqlfilename, 'r') as f:
        lines = [line.rstrip('\n') for rownr, line in enumerate(f) if rownr > 0]
    lines = [line for line in lines if all([line.strip(), not line.strip().startswith("#")])]

    if merge_newlines:
        lines = ['{};'.format(line) for line in ' '.join(lines).split(';') if line.strip()]

    for line in lines:
        if line:
            try:
                dbconnection.execute(line)
            except Exception as e:
                MessagebarAndLog.critical(bar_msg=sql_failed_msg(), log_msg=ru(QCoreApplication.translate('NewDb', 'sql failed:\n%s\nerror msg:\n%s\n')) % (
                ru(line), str(e)))



def tables_columns(table=None, dbconnection=None):
    return dict([(k, [col[1] for col in v]) for k, v in db_tables_columns_info(table=table, dbconnection=dbconnection).items()])


def db_tables_columns_info(table=None, dbconnection=None):
    """Returns a dict like {'tablename': (ordernumber, name, type, notnull, defaultvalue, primarykey)}"""
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    existing_tablenames = get_tables(dbconnection=dbconnection)


    if table is not None:
        if table not in existing_tablenames:
            if dbconnection_created:
                dbconnection.closedb()
            return {}
    if table is None:
        tablenames = existing_tablenames
    elif not isinstance(table, (list, tuple)):
        tablenames = [table]
    else:
        tablenames = table

    tables_dict = {}

    for tablename in tablenames:
        try:
            columns = get_table_info(tablename, dbconnection=dbconnection)
        except:
            columns = None

        if columns is None:
            MessagebarAndLog.warning(log_msg=ru(
                QCoreApplication.translate('db_tables_columns_info', 'Getting columns from table %s failed!')) % (tablename))
            continue
        tables_dict[tablename] = columns

    if dbconnection_created:
        dbconnection.closedb()

    return tables_dict


def get_tables(dbconnection=None, skip_views=False):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        if skip_views:
            tabletype = "type='table'"
        else:
            tabletype = "type = 'table' or type = 'view'"
        tables_sql = (
        """SELECT tbl_name FROM sqlite_master WHERE (%s) AND tbl_name NOT IN %s ORDER BY tbl_name""" % (tabletype, sqlite_internal_tables()))
    else:
        if skip_views:
            tabletype = "AND table_type='BASE TABLE'"
        else:
            tabletype = ''
        tables_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='%s' %s AND table_name NOT IN %s ORDER BY table_name"%(dbconnection.schemas(), tabletype, postgis_internal_tables())
    tables = dbconnection.execute_and_fetchall(tables_sql)
    tablenames = [col[0] for col in tables]

    if dbconnection_created:
        dbconnection.closedb()

    return tablenames


def get_table_info(tablename, dbconnection=None):

    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        columns_sql = """PRAGMA table_info ('%s')""" % (tablename)
        try:
            columns = dbconnection.execute_and_fetchall(columns_sql)
        except Exception as e:
            MessagebarAndLog.warning(bar_msg=sql_failed_msg(), log_msg=ru(
                QCoreApplication.translate('get_table_info', 'Sql failed: %s\msg:%s')) % (columns_sql, str(e)))
            return None

    else:
        columns_sql = "SELECT ordinal_position, column_name, data_type, CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END AS notnull, column_default, 0 AS primary_key FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s'"%(dbconnection.schemas(), tablename)
        columns = [list(x) for x in dbconnection.execute_and_fetchall(columns_sql)]
        primary_keys = [x[0] for x in dbconnection.execute_and_fetchall("SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = '%s'::regclass AND i.indisprimary;"%tablename)]
        for column in columns:
            if column[1] in primary_keys:
                column[5] = 1
        columns = [tuple(column) for column in columns]

    if dbconnection_created:
        dbconnection.closedb()

    return columns


def get_foreign_keys(table, dbconnection=None):
    """Get foreign keys for table.
       Returns a dict like {foreign_key_table: (colname in table, colname in foreign_key_table)}
    sql code from
    http://stackoverflow.com/questions/1152260/postgres-sql-to-list-table-foreign-keys
    and
    https://stackoverflow.com/questions/39379939/how-to-access-information-schema-foreign-key-constraints-with-read-only-user-in
    """
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    foreign_keys = {}
    if dbconnection.dbtype == 'spatialite':
        result_list = dbconnection.execute_and_fetchall("""PRAGMA foreign_key_list('%s')"""%table)
        for row in result_list:
            foreign_keys.setdefault(row[2], []).append((row[3], row[4]))
    else:
        #Only works as administrator in postgresql
        '''
        sql = """
                SELECT
                    tc.constraint_name, tc.table_name, kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='%s';""" % table
        '''

        #Works for non-administrators also!
        sql = """
                SELECT 
                  conrelid::regclass AS table_from,
                  conname,
                  pg_get_constraintdef(c.oid) AS cdef 
                FROM pg_constraint c 
                JOIN pg_namespace n 
                  ON n.oid = c.connamespace 
                WHERE contype IN ('f') 
                AND n.nspname = 'public' 
                AND conrelid::regclass::text = '%s'
                ORDER BY conrelid::regclass::text, contype DESC;
                """%table

        result_list = dbconnection.execute_and_fetchall(sql)
        for row in result_list:
            info = row[2]
            m = re.search(r'FOREIGN KEY \(([a-zA-ZåäöÅÄÖ0-9\-\_]+)\) REFERENCES ([a-zA-ZåäöÅÄÖ0-9\-\_]+)\(([a-zA-ZåäöÅÄÖ0-9\-\_]+)\)', info)
            res = m.groups()
            if res:
                foreign_keys.setdefault(res[1], []).append((res[0], res[2]))

    if dbconnection_created:
        dbconnection.closedb()

    return foreign_keys


def sqlite_internal_tables(as_tuple=False):
    astring = """('ElementaryGeometries',
                'geom_cols_ref_sys',
                'geometry_columns',
                'geometry_columns_time',
                'spatial_ref_sys',
                'spatial_ref_sys_aux',
                'spatial_ref_sys_all',
                'spatialite_history',
                'vector_layers',
                'views_geometry_columns',
                'virts_geometry_columns',
                'geometry_columns_auth',
                'geometry_columns_fields_infos',
                'geometry_columns_field_infos',
                'geometry_columns_statistics',
                'sql_statements_log',
                'layer_statistics',
                'sqlite_sequence',
                'sqlite_stat1',
                'sqlite_stat3',
                'views_layer_statistics',
                'virts_layer_statistics',
                'vector_layers_auth',
                'vector_layers_field_infos',
                'vector_layers_statistics',
                'views_geometry_columns_auth',
                'views_geometry_columns_field_infos',
                'views_geometry_columns_statistics',
                'virts_geometry_columns_auth',
                'virts_geometry_columns_field_infos',
                'virts_geometry_columns_statistics' ,
                'geometry_columns',
                'spatialindex',
                'SpatialIndex')"""
    if as_tuple:
        return ast.literal_eval(astring)
    else:
        return astring


def postgis_internal_tables(as_tuple=False):
    astring = """('geography_columns',
               'geometry_columns',
               'spatial_ref_sys',
               'raster_columns',
               'raster_overviews')"""
    if as_tuple:
        return ast.literal_eval(astring)
    else:
        return astring


def get_sql_result_as_dict(sql, dbconnection=None):
    """
    Runs sql and returns result as dict
    :param sql: The sql command to run
    :param dbconnection:
    :return: A dict with the first column as key and the rest in a tuple as value
    """
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    connection_ok, result_list = sql_load_fr_db(sql, dbconnection=dbconnection)
    if not connection_ok:
        return False, OrderedDict()

    result_dict = OrderedDict()
    for res in result_list:
        result_dict.setdefault(res[0], []).append(tuple(res[1:]))

    if dbconnection_created:
        dbconnection.closedb()

    return True, result_dict


def verify_table_exists(tablename, dbconnection=None):
    return tablename in get_tables(dbconnection=dbconnection)


def change_cast_type_for_geometry_columns(dbconnection, table_info, tablename):
    if dbconnection.dbtype == 'spatialite':
        newtype = 'BLOB'
        geometry_columns_types = get_geometry_types(dbconnection, tablename)
    else:
        newtype = 'geometry'
        geometry_columns_types = get_geometry_types(dbconnection, tablename)

    column_headers_types = dict([(row[1], row[2]) if row[1] not in geometry_columns_types else (row[1], newtype) for row in table_info])
    return column_headers_types


def get_geometry_types(dbconnection, tablename):
    if dbconnection.dbtype == 'spatialite':
        sql = """SELECT f_geometry_column, geometry_type FROM geometry_columns WHERE f_table_name = '%s'""" % tablename
    else:
        sql = """SELECT f_geometry_column, type
                FROM geometry_columns
                WHERE f_table_schema = '%s'
                AND f_table_name = '%s';"""%(dbconnection.schemas(), tablename)
    result = get_sql_result_as_dict(sql, dbconnection=dbconnection)[1]
    return result


def delete_duplicate_values(dbconnection, tablename, primary_keys):
    if dbconnection.dbtype == 'spatialite':
        rowid = 'rowid'
    else:
        rowid = 'ctid'
    dbconnection.execute("""DELETE FROM %s WHERE %s NOT IN (SELECT MIN(%s) FROM %s GROUP BY %s);"""%(tablename, rowid, rowid, tablename, ', '.join(primary_keys)))


def activate_foreign_keys(activated=True, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        if activated:
            _activated = 'ON'
        else:
            _activated = 'OFF'
        dbconnection.execute('PRAGMA foreign_keys=%s'%_activated)

    if dbconnection_created:
        dbconnection.closedb()


def add_insert_or_ignore_to_sql(sql, dbconnection):
    if dbconnection.dbtype == 'spatialite':
        sql = sql.replace('INSERT', 'INSERT OR IGNORE')
    else:
        sql = sql + ' ON CONFLICT DO NOTHING'
    return sql


class DatabaseLockedError(Exception):
    pass


def placeholder_sign(dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    signs = {'spatialite': '?',
             'postgis': '%s'}
    sign = signs.get(dbconnection.dbtype, '%s')

    if dbconnection_created:
        dbconnection.closedb()

    return sign


def get_dbtype(dbtype):
    """
    For QgsVectorLayer, dbtype has to be postgres instead of postgis
    :param dbtype:
    :return:
    """
    if dbtype == 'postgis':
        return 'postgres'
    else:
        return dbtype


def cast_date_time_as_epoch(dbconnection=None, date_time=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if date_time is None:
        date_time = 'date_time'
    else:
        date_time = "'{}'".format(date_time)
    if dbconnection.dbtype == 'spatialite':
        sql = """CAST(strftime('%s', {}) AS NUMERIC)""".format(date_time)
    else:
        sql = """extract(epoch from {}::timestamp)""".format(date_time)

    if dbconnection_created:
        dbconnection.closedb()

    return sql




def backup_db(dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        curs = dbconnection.cursor
        curs.execute("begin immediate")
        bkupname = dbconnection.dbpath + datetime.datetime.now().strftime('%Y%m%dT%H%M') + '.zip'
        zf = zipfile.ZipFile(bkupname, mode='w')
        zf.write(dbconnection.dbpath,
                 compress_type=compression)  # compression will depend on if zlib is found or not
        zf.close()
        dbconnection.conn.rollback()
        MessagebarAndLog.info(
            bar_msg=ru(QCoreApplication.translate("backup_db", "Database backup was written to %s ")) % bkupname,
            duration=15)
    else:
        MessagebarAndLog.info(
            bar_msg=ru(
                QCoreApplication.translate("backup_db", "Backup of PostGIS database not supported yet!")),
            duration=15)

    if dbconnection_created:
        dbconnection.closedb()


def cast_null(data_type, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        sql = 'NULL'
    else:
        sql = 'NULL::%s'%data_type

    if dbconnection_created:
        dbconnection.closedb()

    return sql


def test_not_null_and_not_empty_string(table, column, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        sql = """%s IS NOT NULL AND %s !='' """%(column, column)
    else:
        table_info = [col for col in get_table_info(table) if col[1] == column][0]
        data_type = table_info[2]
        if data_type in postgresql_numeric_data_types():
            sql = '''%s IS NOT NULL'''%(column)
        else:
            sql = '''%s IS NOT NULL AND %s !='' ''' % (column, column)

    if dbconnection_created:
        dbconnection.closedb()

    return sql


def postgresql_numeric_data_types():
    #Skipped these:
    # u'smallserial',
    # u'serial',
    # u'bigserial'
    return ['smallint',
            'integer',
            'bigint',
            'decimal',
            'numeric',
            'real',
            'double precision']


def sqlite_numeric_data_types():
    #Skipped these:
    # u'smallserial',
    # u'serial',
    # u'bigserial'
    return ['integer',
            'double']


def get_srid_name(srid, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        ref_sys_name = dbconnection.execute_and_fetchall("""SELECT ref_sys_name FROM spatial_ref_sys WHERE srid = '%s'"""%srid)[0][0]
    else:
        try:
            ref_sys_name = dbconnection.execute_and_fetchall("""SELECT split_part(srtext, '"', 2) AS "name"
                                                                FROM spatial_ref_sys
                                                                WHERE srid IN ({});""".format(srid))[0][0]
        except:
            MessagebarAndLog.info(log_msg=traceback.format_exc())
            ref_sys_name = ''

    if dbconnection_created:
        dbconnection.closedb()

    return ref_sys_name


def test_if_numeric(column, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        sql = """(typeof(%s)=typeof(0.01) OR typeof(%s)=typeof(1))"""%(column, column)
    else:
        sql = """pg_typeof(%s) in (%s)"""%(column, ', '.join(["'%s'"%data_type for data_type in postgresql_numeric_data_types()]))

    if dbconnection_created:
        dbconnection.closedb()

    return sql


def numeric_datatypes(dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        res = sqlite_numeric_data_types()
    else:
        res = postgresql_numeric_data_types()

    if dbconnection_created:
        dbconnection.closedb()

    return  res


def calculate_median_value(table, column, obsid, dbconnection=None):
    """
    Code from https://stackoverflow.com/questions/15763965/how-can-i-calculate-the-median-of-values-in-sqlite
    :param table:
    :param column:
    :param obsid:
    :param dbconnection:
    :return:
    """
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':

        data = {'column': column,
                'table': table,
                'obsid': obsid}

        sql = '''SELECT AVG({column})
                    FROM (SELECT {column}
                          FROM {table}
                          WHERE obsid = '{obsid}'
                          ORDER BY {column}
                          LIMIT 2 - (SELECT COUNT(*) FROM {table} WHERE obsid = '{obsid}') % 2 
                          OFFSET (SELECT (COUNT(*) - 1) / 2
                          FROM {table} WHERE obsid = '{obsid}'))'''.format(**data).replace('\n', ' ')

        # median value old variant
        #sql = r"""SELECT x.obsid, x.""" + column + r""" as median from (select obsid, """ + column + r""" FROM %s WHERE obsid = '"""%table
        #sql += obsid
        #sql += r"""' and (typeof(""" + column + r""")=typeof(0.01) or typeof(""" + column + r""")=typeof(1))) as x, (select obsid, """ + column + r""" FROM %s WHERE obsid = '"""%table
        #sql += obsid
        #sql += r"""' and (typeof(""" + column + r""")=typeof(0.01) or typeof(""" + column + r""")=typeof(1))) as y GROUP BY x.""" + column + r""" HAVING SUM(CASE WHEN y.""" + column + r""" <= x.""" + column + r""" THEN 1 ELSE 0 END)>=(COUNT(*)+1)/2 AND SUM(CASE WHEN y.""" + column + r""" >= x.""" + column + r""" THEN 1 ELSE 0 END)>=(COUNT(*)/2)+1"""

        ConnectionOK, median_value = sql_load_fr_db(sql, dbconnection)
        try:
            median_value = median_value[0][0]
        except IndexError:
            MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('calculate_median_value',
                                                                                 'Median calculation error, see log message panel')),
                                                              log_msg=ru(QCoreApplication.translate('calculate_median_value',
                                                                                 'Sql failed: %s')) % sql)
            median_value = None


    else:
        if sql_load_fr_db('''SELECT {column} FROM {table} WHERE obsid = '{obsid}' AND {column} IS NOT NULL LIMIT 1'''.format(table=table, obsid=obsid, column=column), dbconnection)[1]:
            sql = """SELECT median({column}) FROM {table} t1 WHERE obsid = '{obsid}';""".format(column=column, table=table, obsid=obsid)
            ConnectionOK, median_value = sql_load_fr_db(sql, dbconnection)
            try:
                median_value = median_value[0][0]
            except IndexError:
                MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('calculate_median_value',
                                                                                     'Median calculation error, see log message panel')),
                                                                  log_msg=ru(QCoreApplication.translate('calculate_median_value',
                                                                                     'Sql failed: %s')) % sql)
                median_value = None
        else:
            median_value = None

    if dbconnection_created:
        dbconnection.closedb()

    return median_value


def rowid_string(dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
        dbconnection_created = True
    else:
        dbconnection_created = False

    if dbconnection.dbtype == 'spatialite':
        res = 'ROWID'
    else:
        res = 'ctid'

    if dbconnection_created:
        dbconnection.closedb()

    return res


def delete_srids(execute_able_object, keep_epsg_code):
    if isinstance(execute_able_object, DbConnectionManager):
        if not execute_able_object.dbtype == 'spatialite':
            return None

    delete_srid_sql_aux = r"""delete from spatial_ref_sys_aux where srid NOT IN ('%s', '4326');""" % keep_epsg_code
    try:
        execute_able_object.execute(delete_srid_sql_aux)
    except:
        pass

    delete_srid_sql = r"""delete from spatial_ref_sys where srid NOT IN ('%s', '4326');""" % keep_epsg_code
    try:
        execute_able_object.execute(delete_srid_sql)
    except:
        MessagebarAndLog.info(
            log_msg=ru(QCoreApplication.translate('delete_srids', 'Removing srids failed using: %s')) % str(
                delete_srid_sql))


def get_spatialite_db_path_from_dbsettings_string(db_settings):
    if isinstance(db_settings, str):
        # Test if the db_setting is an old database
        if os.path.isfile(db_settings):
            return db_settings
        else:
            try:
                db_settings = ast.literal_eval(db_settings)
            except Exception as e:
                try:
                    msg = str(e)
                except:
                    msg = ru(QCoreApplication.translate('get_spatialite_db_path_from_dbsettings_string', 'Error message failed! Could not be converted to string!'))
                MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('get_spatialite_db_path_from_dbsettings_string', '%s error msg from db_settings string "%s": %s')) % ('get_spatialite_db_path_from_dbsettings_string', db_settings, msg))
                return ''
            else:
                return db_settings.get('spatialite', {}).get('dbpath', '')
    elif isinstance(db_settings, dict):
        return db_settings.get('spatialite', {}).get('dbpath', '')
    else:
        return ''


def nonplot_tables(as_tuple=False):
    tables = ('about_db',
                'comments',
                'zz_flowtype',
                'zz_meteoparam',
                'zz_strat',
                'zz_hydro')
    if not as_tuple:
        tables = "({})".format(', '.join(["'{}'".format(x) for x in tables]))
    return tables


def create_dict_from_db_2_cols(params):#params are (col1=keys,col2=values,db-table)
    sqlstring = r"""select %s, %s from %s"""%(params)
    connection_ok, list_of_tuples= sql_load_fr_db(sqlstring)

    if not connection_ok:
        textstring = ru(QCoreApplication.translate('create_dict_from_db_2_cols', """Cannot create dictionary from columns %s and %s in table %s!"""))%(params)#col1,col2,table)
        #qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=10)
        MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('create_dict_from_db_2_cols', 'Some sql failure, see log for additional info.'), log_msg=textstring, duration=4,button=True)
        return False, {'':''}

    adict = dict([(k, v) for k, v in list_of_tuples])
    return True, adict


def get_all_obsids(table='obs_points'):
    """ Returns all obsids from obs_points
    :return: All obsids from obs_points
    """
    obsids = []
    connection_ok, result = sql_load_fr_db('''SELECT DISTINCT obsid FROM %s ORDER BY OBSID''' % table)
    if connection_ok:
        obsids = [row[0] for row in result]
    return obsids