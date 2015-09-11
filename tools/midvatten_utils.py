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
from PyQt4 import QtCore, QtGui, QtWebKit
from qgis.core import *
from qgis.gui import *

import qgis.utils
import sys
import os
from pyspatialite import dbapi2 as sqlite #must use pyspatialite since spatialite-specific sql clauses may be sent by sql_alter_db and sql_load_fr_db
import time

class dbconnection():
    def __init__(self, db=''):
        if db == '':
            self.dbpath = QgsProject.instance().readEntry("Midvatten","database")[0]
        else:
            self.dbpath = db
    
    def connect2db(self):
        if os.path.exists(self.dbpath):
            try:#verify this is an existing sqlite database
                self.conn = sqlite.connect(self.dbpath,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
                self.conn.cursor().execute("select count(*) from sqlite_master") 
                ConnectionOK = True
            except:
                pop_up_info("Could not connect to  " + self.dbpath + "\nYou will have to reset Midvatten settings for this project!")
                ConnectionOK = False
        else:
            pop_up_info("The file " + self.dbpath + " do not exist.\nYou will have to reset Midvatten settings for this project!")
            ConnectionOK = False
        return ConnectionOK
        
    def closedb(self):
            self.conn.close()
    
class askuser(QtGui.QDialog):
    def __init__(self, question="YesNo", msg = '', dialogtitle='User input needed', parent=None):
        self.result = ''
        if question == 'YesNo':         #  Yes/No dialog 
            reply = QtGui.QMessageBox.information(parent, dialogtitle, msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
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

class HtmlDialog(QtGui.QDialog):

    def __init__(self, title='', filepath=''):
        QtGui.QDialog.__init__(self)
        self.setModal(True)
        self.setupUi(title, filepath)

    def setupUi(self, title, filepath):
        self.resize(600, 500)
        self.webView = QtWebKit.QWebView()
        self.setWindowTitle(title)
        self.verticalLayout= QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.addWidget(self.webView)
        self.closeButton = QtGui.QPushButton()
        self.closeButton.setText("Close")
        self.closeButton.setMaximumWidth(150)
        self.horizontalLayout= QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.addStretch(1000)
        self.horizontalLayout.addWidget(self.closeButton)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self.closeWindow)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setLayout(self.verticalLayout)
        url = QtCore.QUrl(filepath)
        self.webView.load(url)

    def closeWindow(self):
        self.close()
    
def find_layer(layer_name):
    for name, search_layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
        if search_layer.name() == layer_name:
            return search_layer

    return None

def getselectedobjectnames(thelayer = qgis.utils.iface.activeLayer()):#returns a list of obsid (as unicode) - thelayer is an optional argument, if not given then activelayer is used
    selectedobs = thelayer.selectedFeatures()
    kolumnindex = thelayer.dataProvider().fieldNameIndex('obsid')  #OGR data provier is used to find index for column named 'obsid'
    if kolumnindex == -1:
            kolumnindex = thelayer.dataProvider().fieldNameIndex('OBSID')  #backwards compatibility
    observations = [None]*(thelayer.selectedFeatureCount())
    i=0
    for k in selectedobs:
        attributes = selectedobs[i]
        observations[i] = attributes[kolumnindex] # value in column obsid is stored as unicode
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

def return_lower_ascii_string(textstring):
    def onlyascii(char):
        if ord(char) < 48 or ord(char) > 127: 
            return ''
        else: 
            return char
    filtered_string=filter(onlyascii, textstring)
    filtered_string = filtered_string.lower()
    return filtered_string

def returnunicode(anything): #takes an input and tries to return it as unicode
    if type(anything) == type(None):
        text = unicode('')
    elif type(anything) == type(unicode('unicodetextstring')):
        text = anything 
    elif (type(anything) == type (1)) or (type(anything) == type (1.1)):
        text = unicode(str(anything))
    elif type(anything) == type('ordinary_textstring'):
        text = unicode(anything)
    else:
        try:
            text = unicode(str(anything))
        except:
            text = unicode('data type unknown, check database')
    return text

def sql_load_fr_db(sql=''):#sql sent as unicode, result from db returned as list of unicode strings
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    if os.path.exists(dbpath[0]):
        try:
            conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)#dbpath[0] is unicode already #MacOSC fix1 
            curs = conn.cursor()
            resultfromsql = curs.execute(sql) #Send SQL-syntax to cursor #MacOSX fix1
            result = resultfromsql.fetchall()
            resultfromsql.close()
            conn.close()
            ConnectionOK = True
        except:
            pop_up_info("Could not connect to the database, please reset Midvatten settings!\n\nDB call causing this error (debug info):\n"+sql)
            ConnectionOK = False
            result = ''
    else:
        pop_up_info("Could not connect to the database, please reset Midvatten settings!\n\nDB call causing this error (debug info):\n"+sql)
        ConnectionOK = False
        result = ''
    return ConnectionOK, result

def sql_alter_db(sql=''):
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    curs = conn.cursor()
    sql2 = sql 
    curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
    resultfromsql = curs.execute(sql2) #Send SQL-syntax to cursor
    result = resultfromsql.fetchall()
    conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
    resultfromsql.close()
    conn.close()
    return result

def sql_alter_db_by_param_subst(sql='',*subst_params):#sql sent as unicode, result from db returned as list of unicode strings, the subst_paramss is a tuple of parameters to be substituted into the sql
    """
    #please note that the argument, subst_paramss, must be a tuple with the parameters to be substituted with ? inside the sql string
    #simple example:
    sql = 'select ?, ? from w_levels where obsid=?)
    subst_params = ('date_time', 'level_masl', 'well01')
    #and since it is a tuple, then one single parameter must be given with a tailing comma:
    sql = 'select * from obs_points where obsid = ?'
    subst_params = ('well01',) 
    """ 
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    if os.path.exists(dbpath[0]):
        #print('debug info about the tuple %s'%(subst_params[0],))#debug
        try:
            conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            curs = conn.cursor()
            try:
                curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
                
                resultfromsql = curs.execute(sql,subst_params[0])#please note, index 0 is pointing to the first optional argument, not index in tuple 
                #det får antagligen inte vara något annat än själva värdena i subst_params, strängen som anger kolumner och obsid-namn osv för select är nog string-concatenation som vanligt, det är alltså bara input värdena som ska använda parameter substs            
            
            except:#in case it is an sql without parameter substitution
                print('debugging info: failed loading with parameter substitution, trying the sql without any parameters at all')#debug
                resultfromsql = curs.execute(sql) 
            result = resultfromsql.fetchall()
            conn.commit()
            
            resultfromsql.close()
            conn.close()
            ConnectionOK = True
        except:
            pop_up_info("Could not connect to the database, please reset Midvatten settings!\n\nDB call causing this error (debug info):\n"+sql)
            ConnectionOK = False
            result = ''
    else:
        pop_up_info("Could not connect to the database, please reset Midvatten settings!\n\nDB call causing this error (debug info):\n"+sql)
        ConnectionOK = False
        result = ''
    return ConnectionOK, result
    
def selection_check(layer='', selectedfeatures=0):  #defaultvalue selectedfeatures=0 is for a check if any features are selected at all, the number is unimportant
    if layer.dataProvider().fieldNameIndex('obsid')  > -1 or layer.dataProvider().fieldNameIndex('OBSID')  > -1: # 'OBSID' to get backwards compatibility
        if selectedfeatures == 0 and layer.selectedFeatureCount() > 0:
            return 'ok'        
        elif not(selectedfeatures==0) and layer.selectedFeatureCount()==selectedfeatures:
            return 'ok'
        elif selectedfeatures == 0 and not(layer.selectedFeatureCount() > 0):
            qgis.utils.iface.messageBar().pushMessage("Error","Select at least one object in the qgis layer!", 2,duration=15)
        else:
            textstring = """Select exactly %s object in the qgis layer!"""%str(selectedfeatures)
            qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=15)
    else:
        pop_up_info("Select a qgis layer that has a field obsid!")
        
def strat_selection_check(layer=''):
    if layer.dataProvider().fieldNameIndex('h_gs')  > -1 or layer.dataProvider().fieldNameIndex('h_toc')  > -1  or layer.dataProvider().fieldNameIndex('SURF_LVL')  > -1: # SURF_LVL to enable backwards compatibility
            return 'ok'        
    else:
        qgis.utils.iface.messageBar().pushMessage("Error","Select a qgis layer with field h_gs!", 2,duration=15)

def verify_msettings_loaded_and_layer_edit_mode(iface, mset, allcritical_layers=('')):
    errorsignal = 0
    if mset.settingsareloaded == False:
        mset.loadSettings()    
        
    for layername in allcritical_layers:
        layerexists = find_layer(str(layername))
        if layerexists:
            if layerexists.isEditable():
                iface.messageBar().pushMessage("Error","Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before proceeding with this operation.", 2)
                #pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before proceeding with this operation.", "Warning")
                errorsignal += 1

    if mset.settingsdict['database'] == '': #Check that database is selected
        iface.messageBar().pushMessage("Error","No database found. Please check your Midvatten Settings. Reset if needed.", 2)
        #pop_up_info("Check settings! \nSelect database first!")        
        errorsignal += 1
    return errorsignal    

def verify_layer_selection(errorsignal,selectedfeatures=0):
    layer = qgis.utils.iface.activeLayer()
    if layer:
        if not(selection_check(layer) == 'ok'):
            errorsignal += 1
            if selectedfeatures==0:
                qgis.utils.iface.messageBar().pushMessage("Error","You have to select some features!", 2,duration=10)
            else:
                qgis.utils.iface.messageBar().pushMessage("Error","You have to select exactly %s features!"%str(selectedfeatures), 2,duration=10)
    else:
        qgis.utils.iface.messageBar().pushMessage("Error","You have to select a relevant layer!", 2,duration=10)
        errorsignal += 1
    return errorsignal

def verify_this_layer_selected_and_not_in_edit_mode(errorsignal,layername):
    layer = qgis.utils.iface.activeLayer()
    if not layer:#check there is actually a layer selected
        errorsignal += 1
        qgis.utils.iface.messageBar().pushMessage("Error","You have to select/activate %s layer!"%layername, 2,duration=10)
    elif layer.isEditable():
        errorsignal += 1
        qgis.utils.iface.messageBar().pushMessage("Error","The selected layer is currently in editing mode. Please exit this mode before updating coordinates.", 2,duration=10)
    elif not(layer.name() == layername):
        errorsignal += 1
        qgis.utils.iface.messageBar().pushMessage("Error","You have to select/activate %s layer!"%layername, 2,duration=10)
    return errorsignal
    
