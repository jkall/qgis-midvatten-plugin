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
import ast
import os
import zipfile
import PyQt4
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

import datetime
from collections import OrderedDict
from pyspatialite import dbapi2 as sqlite

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtCore import QSettings

from qgis._core import QgsProject, QgsDataSourceURI
import db_manager.db_plugins.postgis.connector as postgis_connector
import db_manager.db_plugins.spatialite.connector as spatialite_connector

import midvatten_utils as utils

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
        self.temptables = []

        if db_settings is None:
            db_settings = QgsProject.instance().readEntry("Midvatten", "database")[0]

        if isinstance(db_settings, basestring):
            #Test if the db_setting is an old database
            if os.path.isfile(db_settings):
                db_settings = {u'spatialite': {u'dbpath': db_settings}}
            else:
                try:
                    db_settings = ast.literal_eval(db_settings)
                except:
                    #TODO: Something feels off here. It should not return None, as that will just cause other hard to solve errors.
                    #TODO An exception feels better but is uglier for the user.
                    utils.MessagebarAndLog.critical(bar_msg=utils.returnunicode(QCoreApplication.translate(u'DbConnectionManager', u'Database connection failed. Try reset settings.')))
                    return None
        elif isinstance(db_settings, dict):
            pass
        else:
            raise Exception(utils.returnunicode(QCoreApplication.translate(u'DbConnectionManager', u"DbConnectionManager error: db_settings must be either a dict like {u'spatialite': {u'dbpath': u'x'} or a string representation of it. Was: %s"))%utils.returnunicode(db_settings))

        db_settings = utils.returnunicode(db_settings, keep_containers=True)

        self.dbtype = db_settings.keys()[0]
        self.connection_settings = db_settings.values()[0]

        self.uri = QgsDataSourceURI()

        if self.dbtype == u'spatialite':
            self.dbpath = utils.returnunicode(self.connection_settings[u'dbpath'])
            self.check_db_is_locked()

            #Create the database if it's not existing
            self.uri.setDatabase(self.dbpath)
            self.conn = sqlite.connect(self.dbpath, detect_types=sqlite.PARSE_DECLTYPES | sqlite.PARSE_COLNAMES)
            try:
                self.connector = spatialite_connector.SpatiaLiteDBConnector(self.uri)
            except:
                pass
            self.cursor = self.conn.cursor()
        elif self.dbtype == u'postgis':
            connection_name = self.connection_settings[u'connection'].split(u'/')[0]
            #print(str(get_postgis_connections().mock_calls))

            self.postgis_settings = get_postgis_connections()[connection_name]
            self.uri.setConnection(self.postgis_settings[u'host'], self.postgis_settings[u'port'], self.postgis_settings[u'database'], self.postgis_settings[u'username'], self.postgis_settings[u'password'])
            self.connector = postgis_connector.PostGisDBConnector(self.uri)
            self.conn = self.connector.connection
            self.cursor = self.connector._get_cursor()

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
        if isinstance(sql, basestring):
            sql = [sql]
        elif not isinstance(sql, (list, tuple)):
            raise TypeError(utils.returnunicode(QCoreApplication.translate(u'DbConnectionManager', u'DbConnectionManager.execute: sql must be type string or a list/tuple of strings. Was %s'))%utils.returnunicode(type(sql)))
        for idx, line in enumerate(sql):
            if all_args is None:
                try:
                    self.cursor.execute(line)
                except Exception as e:
                    textstring = utils.returnunicode(QCoreApplication.translate(u'sql_load_fr_db', u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (utils.returnunicode(line), utils.returnunicode(str(e)))
                    utils.MessagebarAndLog.warning(
                        bar_msg=utils.sql_failed_msg(),
                        log_msg=textstring)
                    raise
            elif isinstance(all_args, (list, tuple)):
                args = all_args[idx]
                try:
                    self.cursor.execute(line, args)
                except Exception as e:
                    textstring = utils.returnunicode(QCoreApplication.translate(u'sql_load_fr_db', u"""DB error!\n SQL causing this error:%s\nusing args %s\nMsg:\n%s""")) % (utils.returnunicode(line), utils.returnunicode(args), utils.returnunicode(str(e)))
                    utils.MessagebarAndLog.warning(
                        bar_msg=utils.sql_failed_msg(),
                        log_msg=textstring)
                    raise
            else:
                raise TypeError(utils.returnunicode(QCoreApplication.translate(u'DbConnectionManager', u'DbConnectionManager.execute: all_args must be a list/tuple. Was %s')) % utils.returnunicode(type(all_args)))

    def execute_and_fetchall(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            textstring = utils.returnunicode(QCoreApplication.translate(u'sql_load_fr_db',
                                                                        u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (
                         utils.returnunicode(sql), utils.returnunicode(str(e)))
            utils.MessagebarAndLog.warning(
                bar_msg=utils.sql_failed_msg(),
                log_msg=textstring)
            raise
        return self.cursor.fetchall()

    def execute_and_commit(self, sql):
        self.execute(sql)
        self.commit()

    def commit(self):
        self.conn.commit()

    def commit_and_closedb(self):
        self.commit()
        self.closedb()

    def schemas(self):
        """Postgis schemas look like this:
        Schemas: [(2200, u'public', u'postgres', '{postgres=UC/postgres,=UC/postgres}', u'standard public schema')]
        This function only returns the first schema.
        """

        schemas = self.connector.getSchemas()
        if schemas is None:
            return ''
        else:
            if len(schemas) > 1:
                utils.MessagebarAndLog.info(bar_msg=u'Found more than one schema. Using the first.')
            return schemas[0][1]

    def closedb(self):
        for table in self.temptables:
            if table.startswith(u'temp_'):
                self.execute(u'DROP TABLE IF EXISTS %s'%table)
                self.execute(u"""DELETE FROM geometry_columns WHERE f_table_name = '%s'"""%table)
                # sql = r"""DELETE FROM spatialite_history WHERE "table_name"='%s'"""%self.temptable_name
                # ok = utils.sql_alter_db(sql)


        self.conn.close()

    def internal_tables(self):
        if self.dbtype == u'spatialite':
            return sqlite_internal_tables()
        else:
            return postgis_internal_tables()

    def check_db_is_locked(self):
        if self.dbtype == u'spatialite':
            if os.path.exists(u'%s-journal'%self.dbpath):
                raise DatabaseLockedError(utils.returnunicode(QCoreApplication.translate(u'DbConnectionManager', u"Error, The database is already in use (a journal-file was found)")))

    def vacuum(self):
        if self.dbtype == u'spatialite':
            self.execute(u'VACUUM')
        else:
            self.execute(u'VACUUM ANALYZE')

    def create_temporary_table_for_import(self, temptable_name, fieldnames_types, geometry_colname_type_srid=None):

        if not temptable_name.startswith(u'temp_'):
            temptable_name = u'temp_%s'%temptable_name
        existing_names = tables_columns(dbconnection=self).keys()
        while temptable_name in existing_names: #this should only be needed if an earlier import failed. if so, propose to rename the temporary import-table
            reponse = PyQt4.QtGui.QMessageBox.question(None, utils.returnunicode(QCoreApplication.translate(u'DbConnectionManager', u"Warning - Table name confusion!")),utils.returnunicode(QCoreApplication.translate(u'midv_data_importer', u'''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''))%(self.temptable_name, self.temptable_name, self.temptable_name), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
            if reponse == PyQt4.QtGui.QMessageBox.Yes:
                self.temptable_name = '%s_2' % self.temptable_name
            else:
                raise utils.UserInterruptError()

        if self.dbtype == u'spatialite':
            temptable_name = u'mem.' + temptable_name
            self.execute(u"""ATTACH DATABASE ':memory:' AS mem""")
            if geometry_colname_type_srid is not None:
                geom_column = geometry_colname_type_srid[0]
                geom_type = geometry_colname_type_srid[1]
                srid = geometry_colname_type_srid[2]
                fieldnames_types.append(u'geometry %s'%geometry_colname_type_srid[0])
                sql = u"""CREATE table %s (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, %s)"""%(temptable_name, u', '.join(fieldnames_types))
                self.execute(sql)
                sql = u"""SELECT RecoverGeometryColumn('%s','%s',%s,'%s',2) from %s AS a"""%(temptable_name, geom_column, srid, geom_type, temptable_name)
                self.execute(sql)
            else:
                sql = u"""CREATE table %s (%s)""" % (temptable_name, u', '.join(fieldnames_types))
                self.execute(sql)
        else:
            self.execute(u"""CREATE TEMPORARY table %s (%s)""" % (temptable_name, u', '.join(fieldnames_types)))
            self.temptables.append(temptable_name)
            if geometry_colname_type_srid is not None:
                geom_column = geometry_colname_type_srid[0]
                geom_type = geometry_colname_type_srid[1]
                srid = geometry_colname_type_srid[2]
                sql = u"""ALTER TABLE %s ADD COLUMN %s geometry(%s, %s);""" % (temptable_name, geom_column, geom_type, srid)
                self.execute(sql)
        return temptable_name


def check_connection_ok():
    dbconnection = DbConnectionManager()
    connection_ok = dbconnection.connect2db()
    dbconnection.closedb()
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
        k = utils.returnunicode(k)
        if k.startswith(u'PostgreSQL'):
            cols = k.split(u'/')
            conn_name = cols[2]
            try:
                setting = cols[3]
            except IndexError:
                #utils.MessagebarAndLog.info(log_msg=u'Postgresql connection info: Setting ' + str(k) + u" couldn't be read")
                continue
            value = qs.value(k)
            postgresql_connections.setdefault(conn_name, {})[setting] = value

    postgresql_connections= utils.returnunicode(postgresql_connections, keep_containers=True)
    return postgresql_connections


def sql_load_fr_db(sql, dbconnection=None):
    try:
        if not isinstance(dbconnection, DbConnectionManager):
            dbconnection = DbConnectionManager()
        result = dbconnection.execute_and_fetchall(sql)
    except Exception as e:
        textstring = utils.returnunicode(QCoreApplication.translate(u'sql_load_fr_db', u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (utils.returnunicode(sql), utils.returnunicode(str(e)))
        utils.MessagebarAndLog.warning(
            bar_msg=utils.sql_failed_msg(),
            log_msg=textstring, duration=4)
        return False, []
    else:
        return True, result


def sql_alter_db(sql, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    try:
        dbconnection.execute(u'PRAGMA foreign_keys = ON')
    except:
        pass
    try:
        dbconnection.execute_and_commit(sql)
    except Exception as e:
        textstring = utils.returnunicode(QCoreApplication.translate(u'sql_alter_db', u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""")) % (
        utils.returnunicode(sql), utils.returnunicode(str(e)))
        utils.MessagebarAndLog.warning(
            bar_msg=utils.returnunicode(QCoreApplication.translate(u'sql_alter_db', u'Some sql failure, see log for additional info.')),
            log_msg=textstring, duration=4)


def sql_alter_db_by_param_subst(sql='', *subst_params):
    """
    sql sent as unicode, result from db returned as list of unicode strings, the subst_paramss is a tuple of parameters to be substituted into the sql

    #please note that the argument, subst_paramss, must be a tuple with the parameters to be substituted with ? inside the sql string
    #simple example:
    sql = 'select ?, ? from w_levels where obsid=?)
    subst_params = ('date_time', 'level_masl', 'well01')
    #and since it is a tuple, then one single parameter must be given with a tailing comma:
    sql = 'select * from obs_points where obsid = ?'
    subst_params = ('well01',)
    """
    ConnectionOK, result = execute_sql(sql=sql, foreign_keys_on=True, commit=True, fetchall=True, db_connection_manager_connection=None, *subst_params)
    return ConnectionOK, result


def execute_sqlfile(sqlfilename, function=sql_alter_db):
    with open(sqlfilename, 'r') as f:
        f.readline()  # first line is encoding info....
        for line in f:
            if not line:
                continue
            if line.startswith("#"):
                continue
            function(line)


def tables_columns(table=None, dbconnection=None):
    return dict([(k, [col[1] for col in v]) for k, v in db_tables_columns_info(table=table, dbconnection=dbconnection).iteritems()])


def db_tables_columns_info(table=None, dbconnection=None):
    """Returns a dict like {u'tablename': (ordernumber, name, type, notnull, defaultvalue, primarykey)}"""
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()

    existing_tablenames = get_tables(dbconnection=dbconnection)
    if table is not None:
        if table not in existing_tablenames:
            return {}

    if table is None:
        tablenames = existing_tablenames
    elif not isinstance(table, (list, tuple)):
        tablenames = [table]
    else:
        tablenames = table

    tables_dict = {}

    for tablename in tablenames:
        columns = get_table_info(tablename)
        tables_dict[tablename] = columns
    return tables_dict


def get_tables(dbconnection=None, skip_views=False):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()

    if dbconnection.dbtype == u'spatialite':
        if skip_views:
            tabletype = u"type='table'"
        else:
            tabletype = u"type = 'table' or type = 'view'"
        tables_sql = (
        u"""SELECT tbl_name FROM sqlite_master WHERE (%s) AND tbl_name NOT IN %s ORDER BY tbl_name""" % (tabletype, sqlite_internal_tables()))
    else:
        if skip_views:
            tabletype = u"AND table_type='BASE TABLE'"
        else:
            tabletype = u''
        tables_sql = u"SELECT table_name FROM information_schema.tables WHERE table_schema='%s' %s AND table_name NOT IN %s ORDER BY table_name"%(dbconnection.schemas(), tabletype, postgis_internal_tables())
    tables = dbconnection.execute_and_fetchall(tables_sql)
    tablenames = [col[0] for col in tables]
    return tablenames


def get_table_info(tablename, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()

    if dbconnection.dbtype == u'spatialite':
        columns_sql = """PRAGMA table_info (%s)""" % tablename
        columns = dbconnection.execute_and_fetchall(columns_sql)
    else:
        columns_sql = u"SELECT ordinal_position, column_name, data_type, CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END AS notnull, column_default, 0 AS primary_key FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s'"%(dbconnection.schemas(), tablename)
        columns = [list(x) for x in dbconnection.execute_and_fetchall(columns_sql)]
        primary_keys = [x[0] for x in dbconnection.execute_and_fetchall(u"SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = '%s'::regclass AND i.indisprimary;"%tablename)]
        for column in columns:
            if column[1] in primary_keys:
                column[5] = 1
        columns = [tuple(column) for column in columns]
    return columns


def get_foreign_keys(table, dbconnection=None):
    """Get foreign keys for table.
       Returns a dict like {foreign_key_table: (colname in table, colname in foreign_key_table)}
    code from http://stackoverflow.com/questions/1152260/postgres-sql-to-list-table-foreign-keys"""
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    foreign_keys = {}
    if dbconnection.dbtype == u'spatialite':
        result_list = dbconnection.execute_and_fetchall(u"""PRAGMA foreign_key_list(%s)"""%table)
        for row in result_list:
            foreign_keys.setdefault(row[2], []).append((row[3], row[4]))
    else:
        sql = u"""
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
        result_list = dbconnection.execute_and_fetchall(sql)
        for row in result_list:
            foreign_keys.setdefault(row[3], []).append((row[2], row[4]))

    return foreign_keys


def sqlite_internal_tables(as_tuple=False):
    astring = u"""('ElementaryGeometries',
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
    astring = u"""('geography_columns',
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
        connection_ok, result_list = sql_load_fr_db(sql)
    else:
        result_list = dbconnection.execute_and_fetchall(sql)

    result_dict = {}
    for res in result_list:
        result_dict.setdefault(res[0], []).append(tuple(res[1:]))
    return True, OrderedDict(result_dict)


def verify_table_exists(tablename):
    return tablename in get_tables()


def change_cast_type_for_geometry_columns(dbconnection, table_info, tablename):
    if dbconnection.dbtype == u'spatialite':
        newtype = u'BLOB'
        geometry_columns_types = get_geometry_types(dbconnection, tablename)
    else:
        newtype = u'geometry'
        geometry_columns_types = get_geometry_types(dbconnection, tablename)

    column_headers_types = dict([(row[1], row[2]) if row[1] not in geometry_columns_types else (row[1], newtype) for row in table_info])
    return column_headers_types


def get_geometry_types(dbconnection, tablename):
    if dbconnection.dbtype == u'spatialite':
        sql = u"""SELECT f_geometry_column, geometry_type FROM geometry_columns WHERE f_table_name = '%s'""" % tablename
    else:
        sql = u"""SELECT f_geometry_column, type
                FROM geometry_columns
                WHERE f_table_schema = '%s'
                AND f_table_name = '%s';"""%(dbconnection.schemas(), tablename)
    result = get_sql_result_as_dict(sql, dbconnection=dbconnection)[1]
    return result


def delete_duplicate_values(dbconnection, tablename, primary_keys):
    if dbconnection.dbtype == u'spatialite':
        rowid = u'rowid'
    else:
        rowid = u'ctid'
    dbconnection.execute(u"""DELETE FROM %s WHERE %s NOT IN (SELECT MIN(%s) FROM %s GROUP BY %s);"""%(tablename, rowid, rowid, tablename, u', '.join(primary_keys)))


def activate_foreign_keys(activated=True, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    if dbconnection.dbtype == u'spatialite':
        if activated:
            _activated = u'ON'
        else:
            _activated = u'OFF'
        dbconnection.execute('PRAGMA foreign_keys=%s'%_activated)


def add_insert_or_ignore_to_sql(sql, dbconnection):
    if dbconnection.dbtype == u'spatialite':
        sql = sql.replace(u'INSERT', u'INSERT OR IGNORE')
    else:
        sql = sql + u' ON CONFLICT DO NOTHING'
    return sql


class DatabaseLockedError(Exception):
    pass


def placeholder_sign(dbconnection):
    if dbconnection.dbtype == u'spatialite':
        return u'?'
    else:
        return u'%s'


def get_dbtype(dbtype):
    """
    For QgsVectorLayer, dbtype has to be postgres instead of postgis
    :param dbtype:
    :return:
    """
    if dbtype == u'postgis':
        return u'postgres'
    else:
        return dbtype


def cast_date_time_as_epoch(dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    if dbconnection.dbtype == u'spatialite':
        return u"""CAST(strftime('%s', date_time) AS NUMERIC)"""
    else:
        return u"""extract(epoch from date_time::timestamp)"""


def backup_db(dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()

    if dbconnection.dbtype == u'spatialite':
        curs = dbconnection.cursor
        curs.execute("begin immediate")
        bkupname = dbconnection.dbpath + datetime.datetime.now().strftime('%Y%m%dT%H%M') + '.zip'
        zf = zipfile.ZipFile(bkupname, mode='w')
        zf.write(dbconnection.dbpath,
                 compress_type=compression)  # compression will depend on if zlib is found or not
        zf.close()
        dbconnection.conn.rollback()
        utils.MessagebarAndLog.info(
            bar_msg=utils.returnunicode(QCoreApplication.translate("backup_db", "Database backup was written to %s ")) % bkupname,
            duration=15)
    dbconnection.closedb()


def cast_null(data_type, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()

    if dbconnection.dbtype == u'spatialite':
        return u'NULL'
    else:
        return u'NULL::%s'%data_type


def test_not_null_and_not_empty_string(table, column, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()

    if dbconnection.dbtype == u'spatialite':
        return u'''%s IS NOT NULL AND %s !='''''%(column, column)
    else:
        table_info = [col for col in get_table_info(table) if col[1] == column][0]
        data_type = table_info[2]
        if data_type in postgresql_numeric_data_types():
            return u'''%s IS NOT NULL'''%(column)
        else:
            return u'''%s IS NOT NULL AND %s !='' ''' % (column, column)


def postgresql_numeric_data_types():
    #Skipped these:
    # u'smallserial',
    # u'serial',
    # u'bigserial'
    return [u'smallint',
            u'integer',
            u'bigint',
            u'decimal',
            u'numeric',
            u'real',
            u'double precision']


def get_srid_name(srid, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    if dbconnection.dbtype == u'spatialite':
        ref_sys_name = dbconnection.execute_and_fetchall(u"""SELECT ref_sys_name FROM spatial_ref_sys WHERE srid = '%s'"""%srid)[0][0]
    else:
        #I haven't found the location of the name yet for postgis. It's not in spatial_ref_sys
        ref_sys_name = u''
    return ref_sys_name


def test_if_numeric(column, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    if dbconnection.dbtype == u'spatialite':
        return u"""(typeof(%s)=typeof(0.01) OR typeof(%s)=typeof(1))"""%(column, column)
    else:
        return u"""pg_typeof(%s) in (%s)"""%(column, u', '.join([u"'%s'"%data_type for data_type in postgresql_numeric_data_types()]))


def calculate_median_value(table, column, obsid, dbconnection=None):
    if not isinstance(dbconnection, DbConnectionManager):
        dbconnection = DbConnectionManager()
    if dbconnection.dbtype == u'spatialite':
        # median value
        sql = r"""SELECT x.obsid, x.""" + column + r""" as median from (select obsid, """ + column + r""" FROM %s WHERE obsid = '"""%table
        sql += obsid
        sql += r"""' and (typeof(""" + column + r""")=typeof(0.01) or typeof(""" + column + r""")=typeof(1))) as x, (select obsid, """ + column + r""" FROM %s WHERE obsid = '"""%table
        sql += obsid
        sql += r"""' and (typeof(""" + column + r""")=typeof(0.01) or typeof(""" + column + r""")=typeof(1))) as y GROUP BY x.""" + column + r""" HAVING SUM(CASE WHEN y.""" + column + r""" <= x.""" + column + r""" THEN 1 ELSE 0 END)>=(COUNT(*)+1)/2 AND SUM(CASE WHEN y.""" + column + r""" >= x.""" + column + r""" THEN 1 ELSE 0 END)>=(COUNT(*)/2)+1"""
        ConnectionOK, median_value = sql_load_fr_db(sql, dbconnection)
        try:
            median_value = median_value[0][1]
        except IndexError:
            utils.MessagebarAndLog.warning(bar_msg=utils.returnunicode(QCoreApplication.translate(u'calculate_median_value',
                                                                                 u'Median calculation error, see log message panel')),
                                           log_msg=utils.returnunicode(QCoreApplication.translate(u'calculate_median_value',
                                                                                 u'Sql failed: %s')) % sql)
            median_value = None

    else:
        sql = u"""SELECT median(u.%s) AS median_value FROM (SELECT %s FROM %s WHERE obsid = '%s') AS u;"""%(column, column, table, obsid)
        ConnectionOK, median_value = sql_load_fr_db(sql, dbconnection)
        try:
            median_value = median_value[0][0]
        except IndexError:
            utils.MessagebarAndLog.warning(bar_msg=utils.returnunicode(QCoreApplication.translate(u'calculate_median_value',
                                                                                 u'Median calculation error, see log message panel')),
                                           log_msg=utils.returnunicode(QCoreApplication.translate(u'calculate_median_value',
                                                                                 u'Sql failed: %s')) % sql)
            median_value = None
    return median_value
