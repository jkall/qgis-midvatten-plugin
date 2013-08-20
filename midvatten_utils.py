# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the place to store some global (for the Midvatten plugin) utility functions. 
 NOTE - if using this file, it has to be imported by midvatten.py
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
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
import qgis.utils
import sys
from pyspatialite import dbapi2 as sqlite #must use pyspatialite since spatialite-specific sql clauses may be sent by sql_alter_db and sql_load_fr_db
import time

class askuser(QtGui.QDialog):
    def __init__(self, question="YesNo", msg = '', dialogtitle='User input needed', parent=None):
        #pop_up_info("question = " + question + " and msg = " + msg)        #DEBUGGING
        self.result = ''
        if question == 'YesNo':         #  Yes/No dialog 
            reply = QtGui.QMessageBox.information(parent, dialogtitle, msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if reply==QtGui.QMessageBox.Yes:
                self.result = 1 #1 = "yes"
            else:
                self.result = 0  #0="no"
        elif question == 'AllSelected': # All or Selected Dialog
            btnAll = QtGui.QPushButton("All")   # = "0"
            btnSelected = QtGui.QPushButton("Selected")     # = "1"
            #btnAll.clicked.connect(self.DoForAll)
            #btnSelected.clicked.connect(self.DoForSelected)
            msgBox = QtGui.QMessageBox(parent)
            msgBox.setText(msg)
            msgBox.setWindowTitle(dialogtitle)
            #msgBox.setWindowModality(Qt.ApplicationModal)
            msgBox.addButton(btnAll, QtGui.QMessageBox.ActionRole)
            msgBox.addButton(btnSelected, QtGui.QMessageBox.ActionRole)
            msgBox.addButton(QtGui.QMessageBox.Cancel)
            reply = msgBox.exec_()
            self.result = reply # ALL=0, SELECTED=1
    
def find_layer(layer_name):
    for name, search_layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
        if search_layer.name() == layer_name:
            return search_layer

    return None

def getselectedobjectnames():
    selectedobs = qgis.utils.iface.activeLayer().selectedFeatures()
    kolumnindex = qgis.utils.iface.activeLayer().dataProvider().fieldNameIndex('obsid')  #OGR data provier is used to find index for column named 'obsid'
    if kolumnindex == -1:
            kolumnindex = qgis.utils.iface.activeLayer().dataProvider().fieldNameIndex('OBSID')  #backwards compatibility
    observations = [None]*(qgis.utils.iface.activeLayer().selectedFeatureCount())
    i=0
    for k in selectedobs:    # Loop through all selected objects, a plot is added for each one of the observation points (i.e. selected objects)
        #<CHANGE FOR QGIS 2.0>:
        if hasattr(selectedobs[i], "attributeMap"): #duck typing scheme to test depreceated method, see http://hub.qgis.org/wiki/quantum-gis/API_changes_for_version_20
            attributes=selectedobs[i].attributeMap() #Copy attributes, for the i:th object, to a list
        else: #new method since API change http://lists.osgeo.org/pipermail/qgis-developer/2013-February/024278.html
            attributes = selectedobs[i]
        #</CHANGE FOR QGIS 2.0>:
                        
        observations[i] = str(attributes[kolumnindex]) # Copy value in column obsid in the attribute list # SIP API UPDATE 2.0
        i+=1
    return observations
    
def getQgisVectorLayers():
    """Return list of all valid QgsVectorLayer in QgsMapLayerRegistry"""
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    layerlist = []
    for name, layer in layermap.iteritems():
        if layer.isValid() and layer.type() == QgsMapLayer.VectorLayer:
                layerlist.append( layer )
    return layerlist
    
def isfloat(str):
    try: float(str)
    except ValueError: return False
    return True

def isinteger(str):
    try: int(str)
    except ValueError: return False
    return True

def isdate(str):
    result = False
    formats = ['%Y-%m-%d','%Y-%m-%d %H','%Y-%m-%d %H:%M','%Y-%m-%d %H:%M:%S']
    for fmt in formats:
        try:
            time.strptime(str, fmt)
            result = True
        except ValueError:
            pass
    return result

def pop_up_info(msg='',title='Information',parent=None):
    """Display an info message via Qt box"""
    QtGui.QMessageBox.information(parent, title, '%s' % (msg))

def sql_load_fr_db(sql=''):
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    #utils.pop_up_info(str(dbpath[0]))   # debugging
    conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    curs = conn.cursor()
    sql2 = str(sql).encode('utf-8') 
    resultfromsql = curs.execute(sql2) #Send SQL-syntax to cursor
    result = resultfromsql.fetchall()
    resultfromsql.close()
    conn.close()
    return result

def sql_alter_db(sql=''):
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    #utils.pop_up_info(str(dbpath[0]))   # debugging
    conn = sqlite.connect(str(dbpath[0]),detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    curs = conn.cursor()
    sql2 = str(sql).encode('utf-8') 
    curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
    resultfromsql = curs.execute(sql2) #Send SQL-syntax to cursor
    result = resultfromsql.fetchall()
    conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
    resultfromsql.close()
    conn.close()
    return result
    
def selection_check(layer='', selectedfeatures=0):  #defaultvalue selectedfeatures=0 is for a check if any features are selected at all, the number is unimportant
    if layer.dataProvider().fieldNameIndex('obsid')  > -1 or layer.dataProvider().fieldNameIndex('OBSID')  > -1: # 'OBSID' to get backwards compatibility
        #pop_up_info(" It should be  = " + str(selectedfeatures) + " and it is " + str(layer.selectedFeatureCount()))    #DEBUG
        if selectedfeatures == 0 and layer.selectedFeatureCount() > 0:
            return 'ok'        
        elif not(selectedfeatures==0) and layer.selectedFeatureCount()==selectedfeatures:
            return 'ok'
        elif selectedfeatures == 0 and not(layer.selectedFeatureCount() > 0):
            pop_up_info("Select at least one object in the qgis layer!")
        else:
            pop_up_info("""Select exactly %s object in the qgis layer!"""%str(selectedfeatures))
    else:
        pop_up_info("Select a qgis layer that has a field obsid!")
        
def strat_selection_check(layer=''):
    if layer.dataProvider().fieldNameIndex('h_gs')  > -1 or layer.dataProvider().fieldNameIndex('h_toc')  > -1  or layer.dataProvider().fieldNameIndex('SURF_LVL')  > -1: # SURF_LVL to enable backwards compatibility
            return 'ok'        
    else:
        pop_up_info("Select a qgis layer with field h_gs!")

        
