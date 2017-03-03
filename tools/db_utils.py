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
from pyspatialite import dbapi2 as sqlite

from PyQt4.QtCore import QSettings
import midvatten_utils as utils
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
            self.dbpath = self.connection_settings[u'dbpath']
            self.uri.setDatabase(self.dbpath)
        elif self.dbtype == u'postgis':
            connection_name = self.connection_settings[u'connection'].split(u'/')[0]
            self.postgis_settings = get_postgis_connections()[connection_name]
            self.uri.setConnection(self.postgis_settings[u'host'], self.postgis_settings[u'port'], self.postgis_settings[u'database'], self.postgis_settings[u'username'], self.postgis_settings[u'password'])

    def connect2db(self):
        ConnectionOK = False
        try:#verify this is an existing sqlite database
            if self.dbtype == u'postgis':
                self.connector = postgis_connector.PostGisDBConnector(self.uri)
                self.conn = self.connector.connection
                #self.conn = psycopg2.connect("host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(self.postgis_settings[u'host'], self.postgis_settings[u'port'], self.postgis_settings[u'database'], self.postgis_settings[u'username'], self.uri.password()))
                self.cursor = self.conn.cursor()
            elif self.dbtype == u'spatialite':
                self.conn = sqlite.connect(self.dbpath,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
                self.cursor = self.conn.cursor()
                self.cursor.execute("select count(*) from sqlite_master")
                self.connector = spatialite_connector.SpatiaLiteDBConnector(self.uri)
            ConnectionOK = True
        except:
            utils.MessagebarAndLog.critical(bar_msg=u"Could not connect to database\nYou might have to reset Midvatten settings for this project!")
        return ConnectionOK

    def closedb(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            pass

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


def check_connection_ok():
    connection = DbConnectionManager()
    connection_ok = connection.connect2db()
    try:
        connection.closedb()
    except:
        pass
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

def sql_load_fr_db(sql=''):
    ConnectionOK, result = execute_sql(sql)
    return ConnectionOK, result

def sql_alter_db(sql=''):
    ConnectionOK, result = execute_sql(sql, foreign_keys=True, commit=True, fetchall=False)
    return result

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
    ConnectionOK, result = execute_sql(sql, foreign_keys=True, commit=True, fetchall=True, *subst_params)
    return ConnectionOK, result

def execute_sql(sql='', foreign_keys=False, commit=False, fetchall=True, *subst_params):
    ConnectionOK = False
    result = ''
    connection = DbConnectionManager()
    connection_ok = connection.connect2db()

    wrong_type_msg = u"""DB Error!\n Sql must be string or list/tuple. If string/tuple,\n"""\
                     u"""then index 1 is assumed to be the sql question, and index 2 a list of\n"""\
                     u"""lists containing variables for excecutemany.\nSQL causing this error:%s\n""" %utils.returnunicode(sql)

    if connection_ok:
        if foreign_keys:
            try:
                connection.cursor.execute("PRAGMA foreign_keys = ON")
            except:
                pass

        if subst_params and isinstance(sql, basestring):
            try:
                resultfromsql = connection.cursor.execute(sql, subst_params[0])
            except Exception as e:
                textstring = u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""" % (utils.returnunicode(sql), utils.returnunicode(str(e)))
                utils.MessagebarAndLog.warning(bar_msg=u'Some sql failure, see log for additional info.', log_msg=textstring, duration=4)
            else:
                ConnectionOK = True
        elif isinstance(sql, basestring):
            try:
                resultfromsql = connection.cursor.execute(sql)  # Send SQL-syntax to cursor
            except Exception as e:
                textstring = u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""" % (utils.returnunicode(sql), utils.returnunicode(str(e)))
                utils.MessagebarAndLog.warning(bar_msg=u'Some sql failure, see log for additional info.', log_msg=textstring, duration=4)
            else:
                ConnectionOK = True

        #Assume the user whats to execute many sqls in a row
        elif isinstance(sql, (tuple, list)):
            for line in sql:
                try:
                    resultfromsql = connection.cursor.execute(line)
                except Exception as e:
                    textstring = u"""DB error!\n SQL causing this error:%s\nMsg:\n%s""" %(utils.returnunicode(sql), utils.returnunicode(str(e)))
                    utils.MessagebarAndLog.warning(bar_msg=u'Some sql failure, see log for additional info.', log_msg=textstring, duration=4)
                    break
            else:
                ConnectionOK = True
        else:
            utils.MessagebarAndLog.warning(bar_msg=u'Some sql failure, see log for additional info.', log_msg=wrong_type_msg, duration=4)
    else:
        ConnectionOK = False
        connection.closedb()

    if ConnectionOK and fetchall:
        result = connection.cursor.fetchall()
    else:
        result = None

    if commit:
        try:
            connection.conn.commit()
        except:
            pass

    try:
        connection.closedb()
    except:
        pass
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