# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin creates a new "midvatten project plugin". 
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
import datetime
import locale
import os
import re
from qgis.core import QGis

import PyQt4
from PyQt4.QtCore import QCoreApplication

import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru


class NewDb():
    def __init__(self):
        self.db_settings = u''

    def create_new_spatialite_db(self, verno, user_select_CRS='y', EPSG_code=u'4326', delete_srids=True):  #CreateNewDB(self, verno):
        """Open a new DataBase (create an empty one if file doesn't exists) and set as default DB"""

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        set_locale = self.ask_for_locale()
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)

        if user_select_CRS=='y':
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            EPSGID=str(self.ask_for_CRS(set_locale)[0])
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        else:
            EPSGID=EPSG_code

        if EPSGID=='0' or not EPSGID:
            raise utils.UserInterruptError()
        # If a CRS is selectd, go on and create the database

        #path and name of new db
        dbpath = ru(PyQt4.QtGui.QFileDialog.getSaveFileName(None, "New DB","midv_obsdb.sqlite","Spatialite (*.sqlite)"))
        if not dbpath:
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return u''
        #create Spatialite database

        #delete the file if exists
        if os.path.exists(dbpath):
            utils.MessagebarAndLog.critical(
                bar_msg=ru(QCoreApplication.translate(u'NewDb', u'A database with the chosen name already existed. Cancelling...')))
            return u''

        self.db_settings = ru(utils.anything_to_string_representation({u'spatialite': {u'dbpath': dbpath}}))

        #dbconnection = db_utils.DbConnectionManager(self.db_settings)
        try:
            # creating/connecting the test_db
            dbconnection = db_utils.DbConnectionManager(self.db_settings)
            dbconnection.execute(u"PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database dbconnection separately.
        except Exception as e:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'NewDb', u"Impossible to connect to selected DataBase, see log message panel")), log_msg=ru(QCoreApplication.translate(u'NewDb', u'Msg:\n') + str(e)))
            #utils.pop_up_info("Impossible to connect to selected DataBase")
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return ''

        #First, find spatialite version
        versionstext = dbconnection.execute_and_fetchall('select spatialite_version()')[0][0]
        # load sql syntax to initialise spatial metadata, automatically create GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        # then the syntax defines a Midvatten project db according to the loaded .sql-file
        if not int(versionstext[0][0]) > 3: # which file to use depends on spatialite version installed
            utils.pop_up_info(ru(QCoreApplication.translate(u'NewDb', u"Midvatten plugin needs spatialite4.\nDatabase can not be created")))
            return ''

        filenamestring = "create_db.sql"

        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
        qgisverno = QGis.QGIS_VERSION#We want to store info about which qgis-version that created the db
        replace_word_replace_with = [('CHANGETORELEVANTEPSGID', ru(EPSGID)),
                                    ('CHANGETOPLUGINVERSION', ru(verno)),
                                    ('CHANGETOQGISVERSION', ru(qgisverno)),
                                    ('CHANGETODBANDVERSION', 'SpatiaLite version %s'%ru(versionstext)),
                                    ('CHANGETOLOCALE', ru(set_locale)),
                                    (('SPATIALITE ', ''))]

        with open(SQLFile, 'r') as f:
            f.readline()  # first line is encoding info....
            lines = [ru(line) for line in f]
        sql_lines = [u'{};'.format(l) for l in u' '.join(lines).split(u';') if l]
        for line in sql_lines:
            if all([line, not line.startswith("#"), u'POSTGIS' not in line]):
                sql = self.replace_words(line, replace_word_replace_with)
                try:
                    dbconnection.execute(sql)
                except:
                    try:
                        print(str(sql))
                    except:
                        pass
                    raise

        if delete_srids:
            db_utils.delete_srids(dbconnection, EPSGID)


        self.insert_datadomains(set_locale, dbconnection)

        self.execute_sqlfile(self.get_full_filename("insert_obs_points_triggers.sql"), dbconnection)

        self.add_metadata_to_about_db(dbconnection)

        dbconnection.vacuum()

        #FINISHED WORKING WITH THE DATABASE, CLOSE CONNECTIONS
        dbconnection.commit_and_closedb()
        #create SpatiaLite Connection in QGIS QSettings
        settings=PyQt4.QtCore.QSettings()
        settings.beginGroup('/SpatiaLite/dbconnections')
        settings.setValue(u'%s/sqlitepath'%os.path.basename(dbpath),'%s'%dbpath)
        settings.endGroup()

        """
        #The intention is to keep layer styles in the database by using the class AddLayerStyles but due to limitations in how layer styles are stored in the database, I will put this class on hold for a while.

        #Finally add the layer styles info into the data base
        AddLayerStyles(dbpath)
        """

        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def populate_postgis_db(self, verno, user_select_CRS='y', EPSG_code=u'4326'):

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        set_locale = self.ask_for_locale()
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)

        if user_select_CRS=='y':
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            EPSGID=str(self.ask_for_CRS(set_locale)[0])
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        else:
            EPSGID=EPSG_code

        if EPSGID=='0' or not EPSGID:
            raise utils.UserInterruptError()

        dbconnection = db_utils.DbConnectionManager()
        db_settings = dbconnection.db_settings
        if not isinstance(db_settings, basestring):
            self.db_settings = ru(utils.anything_to_string_representation(dbconnection.db_settings))
        else:
            self.db_settings = ru(db_settings)

        dbconnection.execute(u'CREATE EXTENSION IF NOT EXISTS postgis;')

        result = dbconnection.execute_and_fetchall(u'select version(), PostGIS_full_version();')

        versionstext = u', '.join(result[0])

        filenamestring = "create_db.sql"

        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
        qgisverno = QGis.QGIS_VERSION#We want to store info about which qgis-version that created the db
        replace_word_replace_with = [
            ('CHANGETORELEVANTEPSGID', ru(EPSGID)),
            ('CHANGETOPLUGINVERSION', ru(verno)),
            ('CHANGETOQGISVERSION', ru(qgisverno)),
            ('CHANGETODBANDVERSION', 'PostGIS version %s' % ru(versionstext)),
            ('CHANGETOLOCALE', ru(set_locale)),
            ('double', 'double precision'),
            ('"', ''),
            ('rowid as rowid', 'CTID as rowid'),
            ('POSTGIS ', '')]

        created_tables_sqls = {}
        with open(SQLFile, 'r') as f:
            f.readline()  # first line is encoding info....
            lines = [ru(line) for line in f]
        sql_lines = [u'{};'.format(l) for l in u' '.join(lines).split(u';') if l]
        for line in sql_lines:
            if all([line, not line.startswith("#"), u'InitSpatialMetadata' not in line, u'SPATIALITE' not in line]):
                sql = self.replace_words(line, replace_word_replace_with)
                try:
                    dbconnection.execute(sql)
                except:
                    try:
                        print(str(sql))
                    except:
                        pass
                    raise
                else:
                    _sql = sql.lstrip(u'\r').lstrip(u'\n').lstrip()
                    if _sql.startswith(u'CREATE TABLE'):
                        tablename = u' '.join(_sql.split()).split()[2]
                        created_tables_sqls[tablename] = sql

            #lines = [self.replace_words(line.decode('utf-8').rstrip('\n').rstrip('\r'), replace_word_replace_with) for line in f if all([line,not line.startswith("#"), u'InitSpatialMetadata' not in line])]
        #db_utils.sql_alter_db(lines)

        self.insert_datadomains(set_locale, dbconnection)

        self.execute_sqlfile(self.get_full_filename(u'insert_obs_points_triggers_postgis.sql'), dbconnection)

        self.execute_sqlfile(self.get_full_filename(u'insert_functions_postgis.sql'), dbconnection)

        self.add_metadata_to_about_db(dbconnection, created_tables_sqls)

        dbconnection.vacuum()

        dbconnection.commit_and_closedb()

        """
        #The intention is to keep layer styles in the database by using the class AddLayerStyles but due to limitations in how layer styles are stored in the database, I will put this class on hold for a while.

        #Finally add the layer styles info into the data base
        AddLayerStyles(dbpath)
        """
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def replace_words(self, line, replace_word_replace_with):
        for replace_word, replace_with in replace_word_replace_with:
            line = line.replace(replace_word, replace_with)
        return line

    def ask_for_locale(self):
        locales = [PyQt4.QtCore.QLocale(PyQt4.QtCore.QLocale.Swedish, PyQt4.QtCore.QLocale.Sweden), PyQt4.QtCore.QLocale(PyQt4.QtCore.QLocale.English, PyQt4.QtCore.QLocale.UnitedStates)]
        locale_names = [localeobj.name() for localeobj in locales]
        locale_names.append(locale.getdefaultlocale()[0])
        locale_names = list(set(locale_names))
        question = utils.NotFoundQuestion(dialogtitle=ru(QCoreApplication.translate(u'NewDb', u'User input needed')),
                                    msg=ru(QCoreApplication.translate(u'NewDb', u'Supply locale for the database.\nCurrently, only locale sv_SE has special meaning,\nall other locales will use english.')),
                                    existing_list=locale_names,
                                    default_value=u'',
                                    combobox_label=ru(QCoreApplication.translate(u'newdb', u'Locales')),
                                    button_names=[u'Cancel', u'Ok'])
        answer = question.answer
        submitted_value = ru(question.value)
        if answer == u'cancel':
            raise utils.UserInterruptError()
        elif answer == u'ok':
            return submitted_value

    def ask_for_CRS(self, set_locale):
        # USER MUST SELECT CRS FIRST!! 
        if set_locale == u'sv_SE':
            default_crs = 3006
        else:
            default_crs = 4326
        EPSGID = PyQt4.QtGui.QInputDialog.getInteger(None, ru(QCoreApplication.translate(u'NewDb', "Select CRS")), ru(QCoreApplication.translate(u'NewDb', "Give EPSG-ID (integer) corresponding to\nthe CRS you want to use in the database:")),default_crs)
        if not EPSGID[1]:
            raise utils.UserInterruptError()
        return EPSGID

    def insert_datadomains(self, set_locale=False, dbconnection=None):
        filenamestring = 'insert_datadomain'
        if set_locale == u'sv_SE':
            filenamestring += "_sv.sql"
        else:
            filenamestring += ".sql"
        self.execute_sqlfile(os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions", filenamestring), dbconnection)

    def get_full_filename(self, filename):
        return os.path.join(os.sep,os.path.dirname(__file__), "..", "definitions", filename)

    def add_metadata_to_about_db(self, dbconnection, created_tables_sqls=None):
        tables = sorted(db_utils.get_tables(dbconnection=dbconnection, skip_views=True))

        #Matches comment inside /* */
        #create_table_sql CREATE TABLE meteo /*meteorological observations*/(
        table_descr_reg = re.compile(ur'/\*(.+)\*/', re.MULTILINE)
        #Matches comment after --:
        # strata text NOT NULL --clay etc
        #, color_mplot text NOT NULL --color codes for matplotlib plots
        column_descr_reg = re.compile(ur'([A-Za-z_]+)[ ]+[A-Za-z ]*--(.+)', re.MULTILINE)

        table_name_reg = re.compile(ur'([A-Za-z_]+)[ ]+[A-Za-z ]*--(.+)', re.MULTILINE)
        for table in tables:

            #Get table and column comments
            if created_tables_sqls is None:
                table_descr_sql = (u"SELECT name, sql from sqlite_master WHERE name = '%s';"%table)
                create_table_sql = dbconnection.execute_and_fetchall(table_descr_sql)[0][1]
            else:
                create_table_sql = created_tables_sqls[table]
            table_descr = table_descr_reg.findall(create_table_sql)
            try:
                table_descr = table_descr[0]
            except IndexError:
                table_descr = None
            else:
                table_descr = table_descr.rstrip(u'\n').rstrip(u'\r').replace(u"'", u"''")

            columns_descr = dict(column_descr_reg.findall(create_table_sql))

            table_info = db_utils.get_table_info(table, dbconnection)

            foreign_keys_dict = {}
            foreign_keys = db_utils.get_foreign_keys(table, dbconnection)
            for _table, _from_to in foreign_keys.iteritems():
                _from = _from_to[0][0]
                _to = _from_to[0][1]
                foreign_keys_dict[_from] = (_table, _to)

            sql = ur"""INSERT INTO about_db (tablename, columnname, description, data_type, not_null, default_value, primary_key, foreign_key) VALUES """
            sql +=  ur'({});'.format(u', '.join([u"""(CASE WHEN '%s' != '' or '%s' != ' ' or '%s' IS NOT NULL THEN '%s' else NULL END)"""%(col, col, col, col) for col in [table, ur'*', table_descr, ur'', ur'', ur'', ur'', ur'']]))
            dbconnection.execute(sql)

            for column in table_info:
                colname = column[1]
                data_type = column[2]
                not_null = str(column[3]) if str(column[3]) == u'1' else u''
                default_value = column[4] if column[4] else u''
                primary_key = str(column[5]) if str(column[5]) != u'0' else u''
                _foreign_keys = u''
                if colname in foreign_keys_dict:
                    _foreign_keys = u'%s(%s)'%(foreign_keys_dict[colname])
                column_descr = columns_descr.get(colname, None)
                if column_descr:
                    column_descr = column_descr.rstrip(u'\n').rstrip(u'\r').replace(u"'", u"''")
                sql = u'INSERT INTO about_db (tablename, columnname, data_type, not_null, default_value, primary_key, foreign_key, description) VALUES '
                sql += u'({});'.format(u', '.join([u"""CASE WHEN '%s' != '' or '%s' != ' ' or '%s' IS NOT NULL THEN '%s' else NULL END"""%(col, col, col, col) for col in [table, colname, data_type, not_null, default_value, primary_key, _foreign_keys, column_descr]]))
                try:
                    dbconnection.execute(sql)
                except:
                    try:
                        print(sql)
                    except:
                        pass
                    raise

    def execute_sqlfile(self, sqlfilename, dbconnection, merge_newlines=False):
        with open(sqlfilename, 'r') as f:
            lines = [ru(line).rstrip(u'\r').rstrip(u'\n') for rownr, line in enumerate(f) if rownr > 0]
        lines = [line for line in lines if all([line.strip(), not line.strip().startswith(u"#")])]

        if merge_newlines:
            lines = [u'{};'.format(line) for line in u''.join(lines).split(u';') if line.strip()]

        for line in lines:
            if line:
                try:
                    dbconnection.execute(line)
                except Exception, e:
                    utils.MessagebarAndLog.critical(bar_msg=utils.sql_failed_msg(), log_msg=ru(QCoreApplication.translate(u'NewDb', u'sql failed:\n%s\nerror msg:\n%s\n'))%(ru(line), str(e)))


class AddLayerStyles():
    """ currently this class is not used although it should be, when storing layer styles in the database works better """
    def __init__(self):

        dbconnection = db_utils.DbConnectionManager()
        self.dbpath = dbconnection.dbpath

        try:
            dbconnection.execute(u"PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database dbconnection separately.
        except:
            pass

        #add layer styles
        self.add_layer_styles_2_db(dbconnection)

        #load style from file and set it as value into the layer styles table
        """
        self.style_from_file_into_db('obs_lines', 'obs_lines_tablayout.qml','obs_lines_tablayout.sld')
        self.style_from_file_into_db('obs_p_w_strat', 'obs_p_w_strat.qml','obs_p_w_strat.sld')
        self.style_from_file_into_db('obs_p_w_lvl', 'obs_p_w_lvl.qml','obs_p_w_lvl.sld')
        #osv
        """
        self.style_from_file_into_db('obs_points', 'obs_points_tablayout.qml','obs_points_tablayout.sld', dbconnection)
        self.style_from_file_into_db('stratigraphy', 'stratigraphy_tablayout.qml','stratigraphy_tablayout.sld', dbconnection)

        try:
            dbconnection.execute(u"PRAGMA foreign_keys = OFF")
        except:
            pass
        dbconnection.commit_and_closedb()

    def add_layer_styles_2_db(self, dbconnection):
        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions","add_layer_styles_2_db.sql")
        datetimestring = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open(SQLFile, 'r')
        for linecounter, line in enumerate(f):
            if linecounter > 1:    # first line is encoding info....
                dbconnection.execute(line.replace('CHANGETOCURRENTDATETIME',datetimestring).replace('CHANGETODBPATH',self.dbpath)) # use tags to find and replace SRID and versioning info

    def style_from_file_into_db(self,layer,qml_file, sld_file, dbconnection):
        with open(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",qml_file), 'r') as content_file:
            content = content_file.read()
        dbconnection.execute("update layer_styles set styleQML=? where f_table_name=?",(content,layer))#Use parameterized arguments to allow sqlite3 to escape the quotes for you. (It also helps prevent SQL injection.
        #"UPDATE posts SET html = ? WHERE id = ?", (html ,temp[i][1])
        with open(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",sld_file), 'r') as content_file:
            content = content_file.read()
        dbconnection.execute("update layer_styles set styleSLD=? where f_table_name=?",(content,layer))#Use parameterized arguments to allow sqlite3 to escape the quotes for you. (It also helps prevent SQL injection.
