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
from __future__ import absolute_import
from __future__ import print_function

import datetime
import locale
import os
import re
from builtins import object
from builtins import str

import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import Qgis

from midvatten.tools.utils import common_utils, db_utils
from midvatten.tools.utils.common_utils import returnunicode as ru, get_full_filename, format_timezone_string
from midvatten.tools.utils.db_utils import execute_sqlfile
from midvatten.tools.utils.date_utils import get_pytz_timezones

class NewDb(object):
    def __init__(self):
        self.db_settings = ''

    def create_new_spatialite_db(self, verno, user_select_CRS='y', EPSG_code='4326', delete_srids=True, w_levels_logger_timezone=None,
                                 w_levels_timezone=None):  #CreateNewDB(self, verno):
        """Open a new DataBase (create an empty one if file doesn't exists) and set as default DB"""

        common_utils.stop_waiting_cursor()
        set_locale = self.ask_for_locale()
        common_utils.start_waiting_cursor()
        print("Got locale " + str(set_locale))

        if user_select_CRS=='y':
            common_utils.stop_waiting_cursor()
            EPSGID=str(self.ask_for_CRS(set_locale)[0])
            common_utils.start_waiting_cursor()
        else:
            EPSGID=EPSG_code

        if EPSGID=='0' or not EPSGID:
            raise common_utils.UserInterruptError()
        # If a CRS is selectd, go on and create the database

        #path and name of new db

        if w_levels_logger_timezone is None:
            common_utils.stop_waiting_cursor()
            default_ts = 'UTC+1' if set_locale.lower() == 'sv_se' else ''
            w_levels_logger_timezone = self.ask_for_timezone('w_levels_logger', default_ts)
            print("Got timezone:" + str(w_levels_logger_timezone))
            common_utils.start_waiting_cursor()

        if w_levels_timezone is None:
            common_utils.stop_waiting_cursor()
            default_ts = 'Europe/Stockholm' if set_locale.lower() == 'sv_se' else ''
            w_levels_timezone = self.ask_for_timezone('w_levels', default_ts)
            print("Got timezone:" + str(w_levels_timezone))
            common_utils.start_waiting_cursor()

        common_utils.stop_waiting_cursor()
        dbpath = ru(common_utils.get_save_file_name_no_extension(parent=None, caption="New DB",
                                                                             directory="midv_obsdb.sqlite",
                                                                             filter="Spatialite (*.sqlite)"))

        common_utils.start_waiting_cursor()

        if os.path.exists(dbpath):
            common_utils.MessagebarAndLog.critical(
                bar_msg=ru(QCoreApplication.translate('NewDb', 'A database with the chosen name already existed. Cancelling...')))
            common_utils.stop_waiting_cursor()
            return ''

        #Create the database
        conn = db_utils.connect_with_spatialite_connect(dbpath)
        conn.close()

        self.db_settings = ru(
            common_utils.anything_to_string_representation({'spatialite': {'dbpath': dbpath}}))

        #dbconnection = db_utils.DbConnectionManager(self.db_settings)
        try:
            # creating/connecting the test_db
            dbconnection = db_utils.DbConnectionManager(self.db_settings)
            dbconnection.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database dbconnection separately.
        except Exception as e:
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('NewDb', "Impossible to connect to selected DataBase, see log message panel")), log_msg=ru(QCoreApplication.translate('NewDb', 'Msg:\n') + str(e)))
            #utils.pop_up_info("Impossible to connect to selected DataBase")
            common_utils.stop_waiting_cursor()
            return ''
        d = dbconnection.connector
        #First, find spatialite version
        versionstext = dbconnection.execute_and_fetchall('select spatialite_version()')[0][0]
        # load sql syntax to initialise spatial metadata, automatically create GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        # then the syntax defines a Midvatten project db according to the loaded .sql-file
        if not int(versionstext[0][0]) > 3: # which file to use depends on spatialite version installed
            common_utils.pop_up_info(ru(QCoreApplication.translate('NewDb', "Midvatten plugin needs spatialite4.\nDatabase can not be created")))
            common_utils.stop_waiting_cursor()
            return ''

        filenamestring = "create_db.sql"

        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
        qgisverno = Qgis.QGIS_VERSION#We want to store info about which qgis-version that created the db
        replace_word_replace_with = [('CHANGETORELEVANTEPSGID', ru(EPSGID)),
                                    ('CHANGETOPLUGINVERSION', ru(verno)),
                                    ('CHANGETOQGISVERSION', ru(qgisverno)),
                                    ('CHANGETODBANDVERSION', 'SpatiaLite version %s'%ru(versionstext)),
                                    ('CHANGETOLOCALE', ru(set_locale)),
                                    (('SPATIALITE ', ''))]

        with open(SQLFile, 'r') as f:
            f.readline()  # first line is encoding info....
            lines = [ru(line) for line in f]

        sql_lines = [common_utils.lstrip('SPATIALITE', l) for l in lines if all([l,
                                              not l.startswith("#"),
                                              not l.startswith('--'),
                                              'POSTGIS' not in l,
                                              l.replace(';', '').strip().replace(
                                                 '\n', '').replace('\r', '')])]
        sql_lines = ['{};'.format(l.strip()) for l in ' '.join(sql_lines).split(';') if l.strip()]
        for line in sql_lines:
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

        execute_sqlfile(get_full_filename("insert_obs_points_triggers.sql"), dbconnection)

        execute_sqlfile(get_full_filename('qgis3_obsp_fix.sql'), dbconnection)

        self.add_metadata_to_about_db(dbconnection, w_levels_logger_timezone=w_levels_logger_timezone,
                                      w_levels_timezone=w_levels_timezone)

        #FINISHED WORKING WITH THE DATABASE, CLOSE CONNECTIONS

        dbconnection.commit()
        dbconnection.vacuum()
        dbconnection.commit_and_closedb()

        #create SpatiaLite Connection in QGIS QSettings
        settings=qgis.PyQt.QtCore.QSettings()
        settings.beginGroup('/SpatiaLite/dbconnections')
        settings.setValue('%s/sqlitepath'%os.path.basename(dbpath),'%s'%dbpath)
        settings.endGroup()

        """
        #The intention is to keep layer styles in the database by using the class AddLayerStyles but due to limitations in how layer styles are stored in the database, I will put this class on hold for a while.

        #Finally add the layer styles info into the data base
        AddLayerStyles(dbpath)
        """

        common_utils.stop_waiting_cursor()

    def populate_postgis_db(self, verno, user_select_CRS='y', EPSG_code='4326', w_levels_logger_timezone=None,
                            w_levels_timezone=None):

        dbconnection = db_utils.DbConnectionManager()
        db_settings = dbconnection.db_settings
        if not isinstance(db_settings, str):
            self.db_settings = ru(common_utils.anything_to_string_representation(dbconnection.db_settings))
        else:
            self.db_settings = ru(db_settings)
        if dbconnection.dbtype != 'postgis':
            raise common_utils.UsageError('Database type postgis not selected, check Midvatten settings!')

        dbconnection.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

        result = dbconnection.execute_and_fetchall('select version(), PostGIS_full_version();')

        versionstext = ', '.join(result[0])

        common_utils.stop_waiting_cursor()
        supplied_locale = self.ask_for_locale()
        common_utils.start_waiting_cursor()

        if user_select_CRS=='y':
            common_utils.stop_waiting_cursor()
            epsg_id = str(self.ask_for_CRS(supplied_locale)[0])
            common_utils.start_waiting_cursor()
        else:
            epsg_id=EPSG_code

        if epsg_id=='0' or not epsg_id:
            raise common_utils.UserInterruptError()

        if w_levels_logger_timezone is None:
            common_utils.stop_waiting_cursor()
            default_ts = 'UTC+1' if supplied_locale.lower() == 'sv_se' else ''
            w_levels_logger_timezone = self.ask_for_timezone('w_levels_logger', default_ts)
            print("Got timezone:" + str(w_levels_logger_timezone))
            common_utils.start_waiting_cursor()

        if w_levels_timezone is None:
            common_utils.stop_waiting_cursor()
            default_ts = 'Europe/Stockholm' if supplied_locale.lower() == 'sv_se' else ''
            w_levels_timezone = self.ask_for_timezone('w_levels', default_ts)
            print("Got timezone:" + str(w_levels_timezone))
            common_utils.start_waiting_cursor()

        filenamestring = "create_db.sql"

        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
        qgisverno = Qgis.QGIS_VERSION#We want to store info about which qgis-version that created the db
        replace_word_replace_with = [
            ('CHANGETORELEVANTEPSGID', ru(epsg_id)),
            ('CHANGETOPLUGINVERSION', ru(verno)),
            ('CHANGETOQGISVERSION', ru(qgisverno)),
            ('CHANGETODBANDVERSION', 'PostGIS version %s' % ru(versionstext)),
            ('CHANGETOLOCALE', ru(supplied_locale)),
            ('double', 'double precision'),
            ('"', ''),
            ('rowid as rowid', 'CTID as rowid'),
            ('POSTGIS ', '')]

        created_tables_sqls = {}
        with open(SQLFile, 'r') as f:
            f.readline()  # first line is encoding info....
            lines = [ru(line) for line in f]
        sql_lines = [common_utils.lstrip('POSTGIS', l).lstrip() for l in lines if all([l.strip(),
                                                                                 not l.startswith("#"),
                                                                                 not l.startswith('--'),
                                                                                 'SPATIALITE' not in l,
                                                                                 'InitSpatialMetadata' not in l,
                                                                                 l.replace(';', '').strip().replace(
                                                                                     '\n', '').replace('\r', '')])]
        sql_lines = ['{};'.format(l.strip()) for l in ' '.join(sql_lines).split(';') if l.strip()]
        for linenr, line in enumerate(sql_lines):
            sql = self.replace_words(line, replace_word_replace_with)
            try:
                dbconnection.execute(sql)
            except:
                try:
                    print(str(sql))
                    print("numlines: " + str(len(sql_lines)))
                    print("Error on line nr {}".format(str(linenr)))
                    print("before " + sql_lines[linenr - 1])
                    if linenr + 1 < len(sql_lines):
                        print("after " + sql_lines[linenr + 1 ])
                except:
                    pass
                raise
            else:
                _sql = sql.lstrip('\r').lstrip('\n').lstrip()
                if _sql.startswith('CREATE TABLE'):
                    tablename = ' '.join(_sql.split()).split()[2]
                    created_tables_sqls[tablename] = sql

            #lines = [self.replace_words(line.decode('utf-8').rstrip('\n').rstrip('\r'), replace_word_replace_with) for line in f if all([line,not line.startswith("#"), 'InitSpatialMetadata' not in line])]
        #db_utils.sql_alter_db(lines)

        self.insert_datadomains(supplied_locale, dbconnection)

        execute_sqlfile(get_full_filename('insert_obs_points_triggers_postgis.sql'), dbconnection)

        execute_sqlfile(get_full_filename('insert_functions_postgis.sql'), dbconnection)

        self.add_metadata_to_about_db(dbconnection, created_tables_sqls,
                                      w_levels_logger_timezone=w_levels_logger_timezone,
                                      w_levels_timezone=w_levels_timezone)

        dbconnection.vacuum()

        dbconnection.commit_and_closedb()

        """
        #The intention is to keep layer styles in the database by using the class AddLayerStyles but due to limitations in how layer styles are stored in the database, I will put this class on hold for a while.

        #Finally add the layer styles info into the data base
        AddLayerStyles(dbpath)
        """
        common_utils.stop_waiting_cursor()

    def replace_words(self, line, replace_word_replace_with):
        for replace_word, replace_with in replace_word_replace_with:
            line = line.replace(replace_word, replace_with)
        return line

    def ask_for_locale(self):
        locales = [qgis.PyQt.QtCore.QLocale(qgis.PyQt.QtCore.QLocale.Swedish, qgis.PyQt.QtCore.QLocale.Sweden), qgis.PyQt.QtCore.QLocale(qgis.PyQt.QtCore.QLocale.English, qgis.PyQt.QtCore.QLocale.UnitedStates)]
        locale_names = [localeobj.name() for localeobj in locales]
        locale_names.append(locale.getdefaultlocale()[0])
        locale_names = list(set(locale_names))
        question = common_utils.NotFoundQuestion(dialogtitle=ru(QCoreApplication.translate('NewDb', 'User input needed')),
             msg=ru(QCoreApplication.translate('NewDb', 'Supply locale for the database.\nCurrently, only locale sv_SE has special meaning,\nall other locales will use english.')),
             existing_list=locale_names,
             default_value='',
             combobox_label=ru(QCoreApplication.translate('newdb', 'Locales')),
             button_names=['Cancel', 'Ok'])
        answer = question.answer
        submitted_value = ru(question.value)
        if answer == 'cancel':
            raise common_utils.UserInterruptError()
        elif answer == 'ok':
            return submitted_value

    def ask_for_CRS(self, supplied_locale):
        # USER MUST SELECT CRS FIRST!! 
        if supplied_locale == 'sv_SE':
            default_crs = 3006
        else:
            default_crs = 4326
        epsg_id = qgis.PyQt.QtWidgets.QInputDialog.getInt(None, ru(QCoreApplication.translate('NewDb', "Select CRS")), 
              ru(QCoreApplication.translate('NewDb', 
                                            "Give EPSG-ID (integer) corresponding to\nthe CRS you want to use in the database:")),
              default_crs)
        if not epsg_id[1]:
            raise common_utils.UserInterruptError()
        return epsg_id

    def ask_for_timezone(self, table, default_tz=''):
        timezone_list = ['']
        if table == 'w_levels_logger':
            msg = ru(QCoreApplication.translate('NewDb',
                 'Supply preferred timezone for logger data for table w_levels_logger (use as default timezone for some logger data imports).'))
            timezone_list.extend([format_timezone_string(hour) for hour in range(-12, 15)])
        elif table == 'w_levels':
            msg = ru(QCoreApplication.translate('NewDb',
                                                'Supply preferred timezone for level data for table w_levels (on-the-fly conversion during logger data editing).'))
            timezone_list.extend(get_pytz_timezones())

        question = common_utils.NotFoundQuestion(
            dialogtitle=ru(QCoreApplication.translate('NewDb', 'User input needed')),
            msg=msg,
            existing_list=timezone_list,
            default_value=default_tz,
            combobox_label=ru(QCoreApplication.translate('newdb', 'Timezone')),
            button_names=['Cancel', 'Ok'])
        answer = question.answer
        submitted_value = ru(question.value)
        if answer == 'cancel':
            raise common_utils.UserInterruptError()
        elif answer == 'ok':
            return submitted_value

    def insert_datadomains(self, set_locale=False, dbconnection=None):
        filenamestring = 'insert_datadomain'
        if set_locale == 'sv_SE':
            filenamestring += "_sv.sql"
        else:
            filenamestring += ".sql"
        execute_sqlfile(os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions", filenamestring), dbconnection)

    def add_metadata_to_about_db(self, dbconnection, created_tables_sqls=None, w_levels_logger_timezone=None,
                                 w_levels_timezone=None):
        tables = sorted(db_utils.get_tables(dbconnection=dbconnection, skip_views=True))

        #Matches comment inside /* */
        #create_table_sql CREATE TABLE meteo /*meteorological observations*/(
        table_descr_reg = re.compile(r'/\*(.+)\*/', re.MULTILINE)
        #Matches comment after --:
        # strata text NOT NULL --clay etc
        #, color_mplot text NOT NULL --color codes for matplotlib plots
        column_descr_reg = re.compile(r'([A-Za-z_]+)[ ]+[A-Za-z ]*--(.+)', re.MULTILINE)

        table_name_reg = re.compile(r'([A-Za-z_]+)[ ]+[A-Za-z ]*--(.+)', re.MULTILINE)
        for table in tables:
            #Get table and column comments
            if created_tables_sqls is None:
                table_descr_sql = ("SELECT name, sql from sqlite_master WHERE name = '%s';"%table)
                create_table_sql = dbconnection.execute_and_fetchall(table_descr_sql)[0][1]
            else:
                create_table_sql = created_tables_sqls[table]
            table_descr = table_descr_reg.findall(create_table_sql)
            try:
                table_descr = table_descr[0]
            except IndexError:
                table_descr = None
            else:
                table_descr = table_descr.rstrip('\r').replace("'", "''")

            columns_descr = dict(column_descr_reg.findall(create_table_sql))

            table_info = db_utils.get_table_info(table, dbconnection)

            foreign_keys_dict = {}
            foreign_keys = db_utils.get_foreign_keys(table, dbconnection)
            for _table, _from_to in foreign_keys.items():
                _from = _from_to[0][0]
                _to = _from_to[0][1]
                foreign_keys_dict[_from] = (_table, _to)

            sql = r"""INSERT INTO about_db (tablename, columnname, description, data_type, not_null, default_value, primary_key, foreign_key) VALUES """
            sql +=  r'({});'.format(', '.join(["""(CASE WHEN '%s' != '' or '%s' != ' ' or '%s' IS NOT NULL THEN '%s' else NULL END)"""%(col, col, col, col) for col in [table, r'*', table_descr, r'', r'', r'', r'', r'']]))

            dbconnection.execute(sql)

            for column in table_info:
                colname = column[1]
                data_type = column[2]
                not_null = str(column[3]) if str(column[3]) == '1' else ''
                default_value = column[4] if column[4] else ''
                primary_key = str(column[5]) if str(column[5]) != '0' else ''
                _foreign_keys = ''
                if colname in foreign_keys_dict:
                    _foreign_keys = '%s(%s)'%(foreign_keys_dict[colname])
                column_descr = columns_descr.get(colname, None)
                if column_descr:
                    column_descr = column_descr.rstrip('\r').replace("'", "''")
                sql = 'INSERT INTO about_db (tablename, columnname, data_type, not_null, default_value, primary_key, foreign_key, description) VALUES '
                sql += '({});'.format(', '.join(["""CASE WHEN '%s' != '' or '%s' != ' ' or '%s' IS NOT NULL THEN '%s' else NULL END"""%(col, col, col, col) for col in [table, colname, data_type, not_null, default_value.replace("'", "''"), primary_key, _foreign_keys, column_descr]]))
                try:
                    dbconnection.execute(sql)
                except:
                    try:
                        print(sql)
                    except:
                        pass
                    raise
        for tz, tname in [(w_levels_logger_timezone, 'w_levels_logger'),
                          (w_levels_timezone, 'w_levels')]:
            if tz:
                dbconnection.execute(f"""UPDATE about_db SET description = 
                                         CASE WHEN description IS NULL THEN '({tz})'
                                         ELSE description || ' ({tz})' END
                                         WHERE tablename = '{tname}' and columnname = 'date_time';""")


class AddLayerStyles(object):
    """ currently this class is not used although it should be, when storing layer styles in the database works better """
    def __init__(self):

        dbconnection = db_utils.DbConnectionManager()
        self.dbpath = dbconnection.dbpath

        try:
            dbconnection.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database dbconnection separately.
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
            dbconnection.execute("PRAGMA foreign_keys = OFF")
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
