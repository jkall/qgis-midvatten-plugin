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
import PyQt4.QtCore
import PyQt4.QtGui
from qgis.core import QGis
import qgis.utils
import timeit
import re

import os
import locale
from pyspatialite import dbapi2 as sqlite# pyspatialite is absolutely necessary (sqlite3 not enough) due to InitSpatialMetaData()
import db_utils
import datetime
#plugin modules
import midvatten_utils as utils

tr = PyQt4.QtCore.QCoreApplication.translate

class NewDb():
    def __init__(self):
        self.db_settings = u''

    def create_new_spatialite_db(self, verno, user_select_CRS='y', EPSG_code=u'4326', delete_srids=True):  #CreateNewDB(self, verno):
        """Open a new DataBase (create an empty one if file doesn't exists) and set as default DB"""

        set_locale = self.ask_for_locale()
        if set_locale == u'cancel':
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return utils.Cancel()

        if user_select_CRS=='y':
            EPSGID=str(self.ask_for_CRS(set_locale)[0])
        else:
            EPSGID=EPSG_code
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        if EPSGID=='0' or not EPSGID:
            utils.pop_up_info(tr(u'NewDb', u"Cancelling..."))
            return utils.Cancel()
        # If a CRS is selectd, go on and create the database

        #path and name of new db
        dbpath = utils.returnunicode(PyQt4.QtGui.QFileDialog.getSaveFileName(None, "New DB","midv_obsdb.sqlite","Spatialite (*.sqlite)"))
        if not dbpath:
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return ''
        #create Spatialite database

        #delete the file if exists
        if os.path.exists(dbpath):
            try:
                os.remove(dbpath)
            except OSError, e:
                utils.MessagebarAndLog.critical(tr(u'NewDb', u"sqlite error, see lLog message panel", u"%s - %s." % (e.filename,e.strerror), duration=10))
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return ''
        utils.MessagebarAndLog.critical(tr(u'NewDb', u"sqlite error, see lLog message panel", u"%s - %s."% (u'a', u'e')), duration=10)

        self.db_settings = utils.returnunicode(utils.anything_to_string_representation({u'spatialite': {u'dbpath': dbpath}}))
        #dbconnection = db_utils.DbConnectionManager(self.db_settings)
        try:
            # creating/connecting the test_db
            dbconnection = db_utils.DbConnectionManager(self.db_settings)
            dbconnection.execute(u"PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database dbconnection separately.
        except Exception as e:
            print(tr(u'NewDb', u"Creation of db failed"))
            utils.MessagebarAndLog.critical(bar_msg=tr(u'NewDb', u"Impossible to connect to selected DataBase, see log message panel"), log_msg=tr(u'NewDb', u'Msg:\n') + str(e))
            #utils.pop_up_info("Impossible to connect to selected DataBase")
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return ''

        #First, find spatialite version
        versionstext = dbconnection.execute_and_fetchall('select spatialite_version()')[0]
        # load sql syntax to initialise spatial metadata, automatically create GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        # then the syntax defines a Midvatten project db according to the loaded .sql-file
        if not int(versionstext[0][0]) > 3: # which file to use depends on spatialite version installed
            utils.pop_up_info(tr(u'NewDb', u"Midvatten plugin needs spatialite4.\nDatabase can not be created"))
            return ''

        filenamestring = "create_db.sql"

        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
        qgisverno = QGis.QGIS_VERSION#We want to store info about which qgis-version that created the db

        replace_word_replace_with = [('CHANGETORELEVANTEPSGID', str(EPSGID)),
                                    ('CHANGETOPLUGINVERSION', str(verno)),
                                    ('CHANGETOQGISVERSION', qgisverno),
                                    ('CHANGETOSPLITEVERSION', str(versionstext[0][0])),
                                    ('CHANGETOLOCALE', str(set_locale)),
                                    (('SPATIALITE ', ''))]

        with open(SQLFile, 'r') as f:
            f.readline()  # first line is encoding info....
            lines = [utils.returnunicode(line) for line in f]
        sql_lines = [u'{};'.format(l) for l in u' '.join(lines).split(u';') if l]
        for line in sql_lines:
            if all([line, not line.startswith("#"), u'POSTGIS' not in line]):
                sql = self.replace_words(line, replace_word_replace_with)
                try:
                    dbconnection.execute(sql)
                except:
                    print(str(sql))
                    raise

        if delete_srids:
            #utils.MessagebarAndLog.info(bar_msg=u"epsgid: " + utils.returnunicode(EPSGID))
            delete_srid_sql = r"""delete from spatial_ref_sys where srid NOT IN ('%s', '4326')""" % EPSGID
            try:
                dbconnection.execute(delete_srid_sql)
            except:
                utils.MessagebarAndLog.info(log_msg=tr(u'NewDb', u'Removing srids failed using: ') + str(delete_srid_sql))

        self.insert_datadomains(set_locale, dbconnection)

        self.add_triggers_to_obs_points("insert_obs_points_triggers.sql", dbconnection)

        self.add_metadata_to_about_db(dbconnection)

        dbconnection.execute('vacuum')

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
        set_locale = self.ask_for_locale()
        if set_locale == u'cancel':
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return utils.Cancel()

        if user_select_CRS=='y':
            EPSGID=str(self.ask_for_CRS(set_locale)[0])
        else:
            EPSGID=EPSG_code
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        if EPSGID=='0' or not EPSGID:
            return utils.Cancel()

        dbconnection = db_utils.DbConnectionManager()
        dbconnection.execute(u'CREATE EXTENSION IF NOT EXISTS postgis;')
        result = dbconnection.execute_and_fetchall(u'select version(), PostGIS_full_version();')
        versionstext = u', '.join(result[0])

        filenamestring = "create_db.sql"

        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
        qgisverno = QGis.QGIS_VERSION#We want to store info about which qgis-version that created the db

        replace_word_replace_with = [
            ('CHANGETORELEVANTEPSGID', str(EPSGID)),
            ('CHANGETOPLUGINVERSION', str(verno)),
            ('CHANGETOQGISVERSION', qgisverno),
            ('CHANGETOSPLITEVERSION', str(versionstext[0][0])),
            ('CHANGETOLOCALE', str(set_locale)),
            ('double', 'double precision'),
            ('"', ''),
            ('rowid as rowid', 'CTID as rowid'),
            ('POSTGIS ', '')]

        with open(SQLFile, 'r') as f:
            f.readline()  # first line is encoding info....
            lines = [utils.returnunicode(line) for line in f]
        sql_lines = [u'{};'.format(l) for l in u' '.join(lines).split(u';') if l]
        for line in sql_lines:
            if all([line, not line.startswith("#"), u'InitSpatialMetadata' not in line, u'SPATIALITE' not in line]):
                sql = self.replace_words(line, replace_word_replace_with)
                try:
                    dbconnection.execute(sql)
                except:
                    print(str(sql))
                    raise

            #lines = [self.replace_words(line.decode('utf-8').rstrip('\n').rstrip('\r'), replace_word_replace_with) for line in f if all([line,not line.startswith("#"), u'InitSpatialMetadata' not in line])]
        #db_utils.sql_alter_db(lines)

        self.insert_datadomains(set_locale, dbconnection)

        self.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql', dbconnection)

        dbconnection.execute(u'vacuum')

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
        question = utils.NotFoundQuestion(dialogtitle=tr(u'NewDb', u'User input needed'),
                                    msg=tr(u'NewDb', u'Supply locale for the database.\nCurrently, only locale sv_SE has special meaning,\nall other locales will use english.'),
                                    existing_list=locale_names,
                                    default_value=u'',
                                    button_names=[tr(u'NewDb', u'Cancel'), tr(u'NewDb', u'Ok')])
        answer = question.answer
        submitted_value = utils.returnunicode(question.value)
        if answer == u'cancel':
            return answer
        elif answer == u'ok':
            return submitted_value

    def ask_for_CRS(self, set_locale):
        # USER MUST SELECT CRS FIRST!! 
        if set_locale == u'sv_SE':
            default_crs = 3006
        else:
            default_crs = 4326
        EPSGID = PyQt4.QtGui.QInputDialog.getInteger(None, tr(u'NewDb', "Select CRS"), tr(u'NewDb', "Give EPSG-ID (integer) corresponding to\nthe CRS you want to use in the database:"),default_crs)
        return EPSGID

    def insert_datadomains(self, set_locale=False, dbconnection=None):
        filenamestring = 'insert_datadomain'
        if set_locale == u'sv_SE':
            filenamestring += "_sv.sql"
        else:
            filenamestring += ".sql"
        self.excecute_sqlfile(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring), dbconnection)

    def add_triggers_to_obs_points(self, filename, dbconnection):
        self.excecute_sqlfile(os.path.join(os.sep,os.path.dirname(__file__), "..", "definitions", filename), dbconnection)

    def add_metadata_to_about_db(self, dbconnection):
        tables = dbconnection.execute_and_fetchall(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table') and not (name in""" + dbconnection.internal_tables() + r""") ORDER BY tbl_name""")

        #Matches comment inside /* */
        #create_table_sql CREATE TABLE meteo /*meteorological observations*/(
        table_descr_reg = re.compile(ur'/\*(.+)\*/', re.MULTILINE)
        #Matches comment after --:
        # strata text NOT NULL --clay etc
        #, color_mplot text NOT NULL --color codes for matplotlib plots
        column_descr_reg = re.compile(ur'([A-Za-z_]+)[ ]+[A-Za-z ]*--(.+)', re.MULTILINE)

        for table in tables:
            table = table[0]

            #Get table and column comments
            table_descr_sql = (u"SELECT name, sql from sqlite_master WHERE name = '%s';"%table)
            create_table_sql = dbconnection.execute_and_fetchall(table_descr_sql)[0][1]
            table_descr = table_descr_reg.findall(create_table_sql)
            try:
                table_descr = table_descr[0]
            except IndexError:
                table_descr = None
            else:
                table_descr = table_descr.replace(u"'", u"''")

            columns_descr = dict(column_descr_reg.findall(create_table_sql))

            table_info = dbconnection.execute_and_fetchall(u'''PRAGMA table_info(%s)''' % table)

            foreign_keys = dbconnection.execute_and_fetchall(u"""PRAGMA foreign_key_list(%s)""" %(table))
            #table = idx 2, from = idx 3, to = idx 4
            foreign_keys_dict = {}
            #dict like {from: (table, to)}
            for _row in foreign_keys:
                _from = _row[3]
                _to = _row[4]
                _table = _row[2]
                foreign_keys_dict[_from] = (_table, _to)

            sql = ur"""INSERT INTO about_db (tablename, columnname, description) VALUES """
            sql +=  ur'({});'.format(u', '.join([u"""(CASE WHEN '%s' != '' or '%s' != ' ' or '%s' IS NOT NULL THEN '%s' else NULL END)"""%(col, col, col, col) for col in [table, ur'*', table_descr]]))
            dbconnection.execute(sql)

            for column in table_info:
                colname = column[1]
                data_type = column[2]
                not_null = column[3] if column[3] == u'1' else u''
                default_value = column[4] if column[4] else u''
                primary_key = column[5] if column[5] == u'1' else u''
                _foreign_keys = u''
                if colname in foreign_keys_dict:
                    _foreign_keys = u'%s(%s)'%(foreign_keys_dict[colname])
                column_descr = columns_descr.get(colname, None)
                if column_descr:
                    column_descr = column_descr.replace(u"'", u"''")
                sql = u'INSERT INTO about_db (tablename, columnname, data_type, not_null, default_value, primary_key, foreign_key, description) VALUES '
                sql += u'({});'.format(u', '.join([u"""CASE WHEN '%s' != '' or '%s' != ' ' or '%s' IS NOT NULL THEN '%s' else NULL END"""%(col, col, col, col) for col in [table, colname, data_type, not_null, default_value, primary_key, _foreign_keys, column_descr]]))
                try:
                    dbconnection.execute(sql)
                except:
                    print(sql)
                    raise

    def excecute_sqlfile(self, sqlfilename, dbconnection):
        with open(sqlfilename, 'r') as f:
            f.readline()  # first line is encoding info....
            for line in f:
                if all([line,not line.startswith("#")]):
                    dbconnection.execute(line)


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
