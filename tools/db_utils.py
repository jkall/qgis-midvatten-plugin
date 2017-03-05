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
from operator import itemgetter
from pyspatialite import dbapi2 as sqlite
from pyspatialite.dbapi2 import OperationalError, IntegrityError
from psycopg2 import IntegrityError as PostGisIntegrityError

from PyQt4.QtCore import QSettings
import midvatten_utils as utils
from definitions.midvatten_defs import SQLiteInternalTables
from qgis._core import QgsProject, QgsDataSourceURI
import db_manager.db_plugins.postgis.connector as postgis_connector
import db_manager.db_plugins.spatialite.connector as spatialite_connector

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

        if db_settings is None:
            db_settings = QgsProject.instance().readEntry("Midvatten", "database")[0]

        if isinstance(db_settings, basestring):
            db_settings = ast.literal_eval(db_settings)
        elif isinstance(db_settings, dict):
            pass
        else:
            raise Exception(u"DbConnectionManager error: db_settings must be either a dict like {u'spatialite': {u'dbpath': u'x'} or a string representation of it. Was: "+ str(db_settings))

        utils.returnunicode(db_settings, keep_containers=True)

        self.dbtype = db_settings.keys()[0]
        self.connection_settings = db_settings.values()[0]

        self.uri = QgsDataSourceURI()

        if self.dbtype == u'spatialite':
            self.dbpath = utils.returnunicode(self.connection_settings[u'dbpath'])
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
            self.postgis_settings = get_postgis_connections()[connection_name]
            self.uri.setConnection(self.postgis_settings[u'host'], self.postgis_settings[u'port'], self.postgis_settings[u'database'], self.postgis_settings[u'username'], self.postgis_settings[u'password'])
            self.connector = postgis_connector.PostGisDBConnector(self.uri)
            self.conn = self.connector.connection
            self.cursor = self.connector._get_cursor()

    def connect2db(self):
        if self.cursor:
            return True

    def execute(self, sql):
        if isinstance(sql, basestring):
            sql = [sql]
        elif not isinstance(sql, (list, tuple)):
            raise TypeError(u'DbConnectionManager.execute: sql must be type string or a list/tuple of strings')
        for line in sql:
            self.cursor.execute(line)

    def execute_and_fetchall(self, sql):
        self.cursor.execute(sql)
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
        self.conn.close()


def check_connection_ok():
    connection = DbConnectionManager()
    connection_ok = connection.connect2db()
    connection.closedb()
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

def sql_load_fr_db(sql):

    try:
        connection = DbConnectionManager()
        result = connection.execute_and_fetchall(sql)
    except Exception as e:
        textstring = u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""" % (
        utils.returnunicode(sql), utils.returnunicode(str(e)))
        utils.MessagebarAndLog.warning(
            bar_msg=u'Some sql failure, see log for additional info.',
            log_msg=textstring, duration=4)
        print(str(textstring))
        print(str(e))
        return False, []
    else:
        return True, result

def sql_alter_db(sql):
    connection = DbConnectionManager()
    try:
        connection.execute(u'PRAGMA foreign_keys = ON')
    except:
        pass
    try:
        connection.execute_and_commit(sql)
    except Exception as e:
        textstring = u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""" % (
        utils.returnunicode(sql), utils.returnunicode(str(e)))
        utils.MessagebarAndLog.warning(
            bar_msg=u'Some sql failure, see log for additional info.',
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
    if dbconnection is None:
        dbconnection = DbConnectionManager()

    if table is None:
        if dbconnection.dbtype == u'spatialite':
            tables_sql = (u"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name in""" + utils.returnunicode(SQLiteInternalTables()) + u""") ORDER BY tbl_name""")
        else:
            tables_sql = u"SELECT table_name FROM information_schema.tables WHERE table_schema='%s'"%dbconnection.schemas()
        tables = dbconnection.execute_and_fetchall(tables_sql)
        tablenames = [col[0] for col in tables]
    elif not isinstance(table, (list, tuple)):
        tablenames = [table]
    else:
        tablenames = table

    tables_dict = {}

    for tablename in tablenames:
        if dbconnection.dbtype == u'spatialite':
            columns_sql = """PRAGMA table_info (%s)""" % tablename
        else:
            columns_sql = u"SELECT * FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s'"%(dbconnection.schemas(), tablename)
        columns = dbconnection.execute_and_fetchall(columns_sql)
        tables_dict[tablename] = tuple(sorted(tuple(columns), key=itemgetter(1)))

    return tables_dict