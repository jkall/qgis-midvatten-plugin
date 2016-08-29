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

import os
import locale
from pyspatialite import dbapi2 as sqlite# pyspatialite is absolutely necessary (sqlite3 not enough) due to InitSpatialMetaData()
import datetime
#plugin modules
import midvatten_utils as utils

class newdb():

    def __init__(self, verno, logfile,user_select_CRS='y', EPSG_code=u'4326', set_locale=False):
        self.logfile = logfile
        self.dbpath = ''
        self.create_new_db(verno,user_select_CRS,EPSG_code, set_locale)  #CreateNewDB(verno)
        
    def create_new_db(self, verno, user_select_CRS='y', EPSG_code=u'4326', set_locale=False):  #CreateNewDB(self, verno):
        """Open a new DataBase (create an empty one if file doesn't exists) and set as default DB"""
        if user_select_CRS=='y':
            EPSGID=str(self.ask_for_CRS(set_locale)[0])
        else:
            EPSGID=EPSG_code
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        if EPSGID=='0' or not EPSGID:
            utils.pop_up_info("Cancelling...")
        else: # If a CRS is selectd, go on and create the database
            #path and name of new db
            self.dbpath = PyQt4.QtGui.QFileDialog.getSaveFileName(None, "New DB","midv_obsdb.sqlite","Spatialite (*.sqlite)")
            if not self.dbpath:
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return ''
            #create Spatialite database
            else:
                #delete the file if exists
                if os.path.exists(self.dbpath):
                    try:
                        os.remove(self.dbpath)
                    except OSError, e:
                        qgis.utils.iface.messageBar().pushMessage("sqlite error, see logfile %s"%self.logfile.name, 2,duration=10)
                        self.logfile.write("%s - %s." % (e.filename,e.strerror))
                        self.logfile.flush()
                        #utils.pop_up_info("Error: %s - %s." % (e.filename,e.strerror))
                        PyQt4.QtGui.QApplication.restoreOverrideCursor()
                        return ''
                try:
                    # creating/connecting the test_db
                    self.conn = sqlite.connect(self.dbpath) 
                    # creating a Cursor
                    self.cur = self.conn.cursor()
                    self.cur.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
                except:
                    qgis.utils.iface.messageBar().pushMessage("Impossible to connect to selected DataBase", 2,duration=3)
                    #utils.pop_up_info("Impossible to connect to selected DataBase")
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return ''
                #First, find spatialite version
                versionstext = self.cur.execute('select spatialite_version()').fetchall()
                # load sql syntax to initialise spatial metadata, automatically create GEOMETRY_COLUMNS and SPATIAL_REF_SYS
                # then the syntax defines a Midvatten project db according to the loaded .sql-file
                if not int(versionstext[0][0][0]) > 3: # which file to use depends on spatialite version installed
                    utils.pop_up_info("Midvatten plugin needs spatialite4.\nDatabase can not be created")
                    return ''

                filenamestring = "create_db.sql"

                SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring)
                qgisverno = QGis.QGIS_VERSION#We want to store info about which qgis-version that created the db
                with open(SQLFile, 'r') as f:
                    f.readline()  # first line is encoding info....
                    try:                        
                        for line in f:
                            if not line:
                                continue
                            if line.startswith("#"):
                                continue
                            for replace_word, replace_with in [('CHANGETORELEVANTEPSGID', str(EPSGID)),
                                                               ('CHANGETOPLUGINVERSION', str(verno)),
                                                               ('CHANGETOQGISVERSION',qgisverno),
                                                               ('CHANGETOSPLITEVERSION', str(versionstext[0][0]))]:
                                line = line.replace(replace_word, replace_with)
                            self.cur.execute(line)  # use tags to find and replace SRID and versioning info
                    except Exception, e:
                        #utils.pop_up_info('Failed to create DB! sql failed:\n' + line + '\n\nerror msg:\n' + str(e))
                        qgis.utils.iface.messageBar().pushMessage("sqlite error, see logfile %s"%self.logfile.name, 2,duration=5)
                        self.logfile.write('Failed to create DB! sql failed: \n%serror msg: %s\n\n'%(line ,str(e)))
                        self.logfile.flush()
                    except:
                        qgis.utils.iface.messageBar().pushMessage("Failed to create database", 2,duration=3)
                        #utils.pop_up_info('Failed to create DB!')

                self.insert_datadomains(set_locale)

                self.add_triggers_to_obs_points()


                #FINISHED WORKING WITH THE DATABASE, CLOSE CONNECTIONS
                self.conn.commit()
                self.conn.close()
                #create SpatiaLite Connection in QGIS QSettings
                settings=PyQt4.QtCore.QSettings()
                settings.beginGroup('/SpatiaLite/connections')
                settings.setValue(u'%s/sqlitepath'%os.path.basename(self.dbpath),'%s'%self.dbpath)
                settings.endGroup()

                """
                #The intention is to keep layer styles in the database by using the class AddLayerStyles but due to limitations in how layer styles are stored in the database, I will put this class on hold for a while. 

                #Finally add the layer styles info into the data base
                AddLayerStyles(self.dbpath)
                """
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def ask_for_CRS(self, set_locale):
        # USER MUST SELECT CRS FIRST!! 
        if set_locale == u'sv_SE':
            default_crs = 3006
        else:
            default_crs = 4326
        EPSGID = PyQt4.QtGui.QInputDialog.getInteger(None, "Select CRS", "Give EPSG-ID (integer) corresponding to\nthe CRS you want to use in the database:",default_crs)
        return EPSGID

    def insert_datadomains(self, set_locale=False):
        filenamestring = 'insert_datadomain'
        if set_locale == u'sv_SE':
            filenamestring += "_sv.sql"
        else:
            filenamestring += ".sql"
        self.excecute_sqlfile(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filenamestring))

    def add_triggers_to_obs_points(self):
        self.excecute_sqlfile(os.path.join(os.sep,os.path.dirname(__file__), "..", "definitions", "insert_obs_points_triggers.sql"))

    def excecute_sqlfile(self, sqlfilename):
        with open(sqlfilename, 'r') as f:
            f.readline()  # first line is encoding info....
            for line in f:
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                try:
                    self.cur.execute(line)  # use tags to find and replace SRID and versioning info
                except Exception, e:
                    #utils.pop_up_info('Failed to create DB! sql failed:\n' + line + '\n\nerror msg:\n' + str(e))
                    qgis.utils.iface.messageBar().pushMessage("Error","sql failed, see logfile %s"%self.logfile.name, 2,duration=5)
                    self.logfile.write('sql failed:\n%s\nerror msg:\n%s\n'%(line ,str(e)))
                    self.logfile.flush()

class AddLayerStyles():
    """ currently this class is not used although it should be, when storing layer styles in the database works better """
    def __init__(self, dbpath):
        self.dbpath = dbpath
        # creating/connecting the test_db
        self.conn = sqlite.connect(self.dbpath) 
        # creating a Cursor
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
        
        #add layer styles
        self.add_layer_styles_2_db()

        #load style from file and set it as value into the layer styles table
        """
        self.style_from_file_into_db('obs_lines', 'obs_lines_tablayout.qml','obs_lines_tablayout.sld')
        self.style_from_file_into_db('obs_p_w_strat', 'obs_p_w_strat.qml','obs_p_w_strat.sld')
        self.style_from_file_into_db('obs_p_w_lvl', 'obs_p_w_lvl.qml','obs_p_w_lvl.sld')
        #osv
        """
        self.style_from_file_into_db('obs_points', 'obs_points_tablayout.qml','obs_points_tablayout.sld')
        self.style_from_file_into_db('stratigraphy', 'stratigraphy_tablayout.qml','stratigraphy_tablayout.sld')

        self.cur.execute("PRAGMA foreign_keys = OFF")
        #FINISHED WORKING WITH THE DATABASE, CLOSE CONNECTIONS
        self.rs.close()
        self.conn.close()
    
    def add_layer_styles_2_db(self):
        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions","add_layer_styles_2_db.sql")
        datetimestring = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open(SQLFile, 'r')
        linecounter = 1
        for line in f:
            if linecounter > 1:    # first line is encoding info....
                self.rs = self.cur.execute(line.replace('CHANGETOCURRENTDATETIME',datetimestring).replace('CHANGETODBPATH',self.dbpath)) # use tags to find and replace SRID and versioning info
            linecounter += 1

    def style_from_file_into_db(self,layer,qml_file, sld_file):
        with open(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",qml_file), 'r') as content_file:
            content = content_file.read()
        self.cur.execute("update layer_styles set styleQML=? where f_table_name=?",(content,layer))#Use parameterized arguments to allow sqlite3 to escape the quotes for you. (It also helps prevent SQL injection.
        #"UPDATE posts SET html = ? WHERE id = ?", (html ,temp[i][1])
        with open(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",sld_file), 'r') as content_file:
            content = content_file.read()
        self.cur.execute("update layer_styles set styleSLD=? where f_table_name=?",(content,layer))#Use parameterized arguments to allow sqlite3 to escape the quotes for you. (It also helps prevent SQL injection.
