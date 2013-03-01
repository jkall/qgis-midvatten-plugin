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

from qgis.core import *
from qgis.gui import *

import os
import locale
from pyspatialite import dbapi2 as sqlite
import midvatten_utils as utils    

class newdb():

    def __init__(self, verno):
        self.dbpath = ''
        self.CreateNewDB(verno)
        
    def CreateNewDB(self, verno):
        """Open a new DataBase (create an empty one if file doesn't exists) and set as default DB"""
        # USER MUST SELECT CRS FIRST!! 
        default_crs = 4326
        if locale.getdefaultlocale()[0]=='sv_SE':
            default_crs = 3006
        EPSGID = PyQt4.QtGui.QInputDialog.getInteger(None, "Select CRS", "Give EPSG-ID (integer) corresponding to\nthe CRS you want to use in the database:",default_crs)
        #uitls.pop_up_info(str(EPSGID[0]))
        if EPSGID[0]==0 or not EPSGID:
            utils.pop_up_info("Cancelling...")
        else:
            # If a CRS is selectd, go on and create the database
            #path and name of new db
            self.dbpath = PyQt4.QtGui.QFileDialog.getSaveFileName(None, "New DB","Midv_obsdb.sqlite","Spatialite (*.sqlite)")
            #utils.pop_up_info(self.dbpath + " was returned from getsavefilename") #debugging
            if self.dbpath.isEmpty():
                return ''
            #create Spatialite database
            else:
                try:
                    # creating/connecting the test_db
                    conn = sqlite.connect(str(self.dbpath)) 
                    # creating a Cursor
                    cur = conn.cursor()
                    cur.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
                except:
                    utils.pop_up_info("Impossible to connect to selected DataBase")
                    return ''
                # load sql syntax to initialise spatial metadata, automatically create GEOMETRY_COLUMNS and SPATIAL_REF_SYS
                # then the syntax defines a Midvatten project db according to the loaded .sql-file
                SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"definitions","create_db.sql")
                #PyQt4.QtGui.QMessageBox.information(None, "Info", SQLFile) # ONLY FOR DEBUGGING
                f = open(SQLFile, 'r')
                linecounter = 1
                for line in f:
                    if linecounter > 1:    # first line is encoding info....
                        rs = cur.execute(line.replace('CHANGETORELEVANTEPSGID',str(EPSGID[0])).replace('CHANGETOPLUGINVERSION',str(verno)))   # Replacing "CHANGETORELEVANTEPSGID" and "CHANGETOPLUGINVERSION" that is found in the create_db.sql  file 
                    linecounter += 1
                
                cur.execute("PRAGMA foreign_keys = OFF")
                #FINISHED WORKING WITH THE DATABASE, CLOSE CONNECTIONS
                rs.close()
                conn.close()
                #create SpatiaLite Connection in QGIS QSettings
                settings=PyQt4.QtCore.QSettings()
                settings.beginGroup('/SpatiaLite/connections')
                settings.setValue(u'%s/sqlitepath'%os.path.basename(str(self.dbpath)),'%s'%self.dbpath)
                #settings.setValue(u'%s/sqlitepath'%os.path.basename(str(path)),'%s'%path)
                settings.endGroup()
