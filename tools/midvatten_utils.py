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
from PyQt4 import QtCore, QtGui, QtWebKit, uic
import PyQt4
from qgis.core import *
from qgis.gui import *
import csv
import codecs
import cStringIO
import difflib
import datetime
import copy
import qgis.utils
import sys
import locale
import os
import math
import numpy as np
import tempfile
from contextlib import contextmanager
from pyspatialite import dbapi2 as sqlite #must use pyspatialite since spatialite-specific sql clauses may be sent by sql_alter_db and sql_load_fr_db
from pyspatialite.dbapi2 import IntegrityError
from matplotlib.dates import datestr2num, num2date
import time
from collections import OrderedDict
import re

not_found_dialog = uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'not_found_gui.ui'))[0]

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
        elif question == 'DateShift':
            supported_units = [u'microseconds', u'milliseconds', u'seconds', u'minutes', u'hours', u'days', u'weeks']
            while True:
                answer = str(PyQt4.QtGui.QInputDialog.getText(None, "User input needed", "Give needed adjustment of date/time for the data.\nSupported format: +- X <resolution>\nEx: 1 hours, -1 hours, -1 days\nSupported units:\n" + ', '.join(supported_units), PyQt4.QtGui.QLineEdit.Normal, u'0 hours')[0])
                if not answer:
                    self.result = u'cancel'
                    break
                else:
                    adjustment_unit = answer.split()
                    if len(adjustment_unit) == 2:
                        if adjustment_unit[1] in supported_units:
                            self.result = adjustment_unit
                            break
                        else:
                            pop_up_info("Failure:\nOnly support resolutions\n " + ', '.join(supported_units))
                    else:
                        pop_up_info("Failure:\nMust write time resolution also.\n")


class NotFoundQuestion(QtGui.QDialog, not_found_dialog):
    def __init__(self, dialogtitle=u'Warning', msg=u'', existing_list=None, default_value=u'', parent=None, button_names=[u'Ignore', u'Cancel', u'Ok']):
        QtGui.QDialog.__init__(self, parent)
        self.answer = None
        self.setupUi(self)
        self.setWindowTitle(dialogtitle)
        self.label.setText(msg)
        self.comboBox.addItem(default_value)
        if existing_list is not None:
            for existing in existing_list:
                self.comboBox.addItem(existing)

        for button_name in button_names:
            button = QtGui.QPushButton(button_name)
            button.setObjectName(button_name.lower())
            self.buttonBox.addButton(button, QtGui.QDialogButtonBox.ActionRole)
            self.connect(button, PyQt4.QtCore.SIGNAL("clicked()"), self.button_clicked)

        self.exec_()

    def button_clicked(self):
        button = self.sender()
        button_object_name = button.objectName()
        self.set_answer_and_value(button_object_name)
        self.close()

    def set_answer_and_value(self, answer):
        self.answer = answer
        self.value = self.comboBox.currentText()

    def closeEvent(self, event):
        if self.answer == None:
            self.set_answer_and_value(u'cancel')
        super(NotFoundQuestion, self).closeEvent(event)

        #self.close()


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


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def read(self):
        self.next()

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def ask_user_about_stopping(question):
    """
    Asks the user a question and returns 'failed' or 'continue' as yes or no
    :param question: A string to write at the dialog box.
    :return: The string 'failed' or 'continue' as yes/no
    """
    answer = askuser("YesNo", question)
    if answer.result:
        return 'cancel'
    else:
        return 'ignore'

def create_dict_from_db_2_cols(params):#params are (col1=keys,col2=values,db-table)
    #print(params)#debug
    sqlstring = r"""select %s, %s from %s"""%(params)
    #print(sqlstring)
    connection_ok, list_of_tuples= sql_load_fr_db(sqlstring)

    if not connection_ok:
        textstring = """Cannot create dictionary from columns %s and %s in table %s!"""%(params)#col1,col2,table)
        qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=10)        
        return False, {'':''}

    #print(list_of_tuples)#debug
    #k=[]
    #v=[]
    #for tuple_item in list_of_tuples:
    #    k.append(tuple_item[0])
    #    v.append(tuple_item[1])
    #return True, dict(zip(k, v))

    adict = dict([(k, v) for k, v in list_of_tuples])
    return True, adict

def find_layer(layer_name):
    for name, search_layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
        if search_layer.name() == layer_name:
            return search_layer

    return None

def get_all_obsids():
    """ Returns all obsids from obs_points
    :return: All obsids from obs_points
    """
    myconnection = dbconnection()
    obsids = []
    if myconnection.connect2db() == True:
        # skapa en cursor
        curs = myconnection.conn.cursor()
        rs=curs.execute("""select distinct obsid from obs_points order by obsid""")

        obsids = [row[0] for row in curs]
        rs.close()
        myconnection.closedb()
    return obsids

def get_selected_features_as_tuple(layername):
    """ Returns all selected features from layername
     
        Returns a tuple of obsids stored as unicode
    """
    obs_points_layer = find_layer(layername)
    selected_obs_points = getselectedobjectnames(obs_points_layer)
    #module midv_exporting depends on obsid being a tuple
    #we cannot send unicode as string to sql because it would include the u' so str() is used
    obsidtuple = tuple([returnunicode(id) for id in selected_obs_points])
    return obsidtuple      
        
def getselectedobjectnames(thelayer='default'):
    """ Returns a list of obsid as unicode
    
        thelayer is an optional argument, if not given then activelayer is used
    """
    if thelayer == 'default':
        thelayer = get_active_layer()
    if not thelayer:
        return []
    selectedobs = thelayer.selectedFeatures()
    kolumnindex = thelayer.dataProvider().fieldNameIndex('obsid')  #OGR data provier is used to find index for column named 'obsid'
    if kolumnindex == -1:
        kolumnindex = thelayer.dataProvider().fieldNameIndex('OBSID')  #backwards compatibility
    observations = [obs[kolumnindex] for obs in selectedobs] # value in column obsid is stored as unicode
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

def null_2_empty_string(input_string):
    return(input_string.replace('NULL','').replace('null',''))

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

def returnunicode(anything, keep_containers=False): #takes an input and tries to return it as unicode
    ur"""

    >>> returnunicode('b')
    u'b'
    >>> returnunicode(int(1))
    u'1'
    >>> returnunicode(None)
    u''
    >>> returnunicode([])
    u'[]'
    >>> returnunicode(['a', u'b'])
    u"[u'a', u'b']"
    >>> returnunicode(['a', 'b'])
    u"[u'a', u'b']"
    >>> returnunicode(['ä', 'ö'])
    u"[u'\\xe4', u'\\xf6']"
    >>> returnunicode(float(1))
    u'1.0'
    >>> returnunicode(None)
    u''
    >>> returnunicode([(1, ), {2: 'a'}], True)
    [(u'1',), {u'2': u'a'}]

    :param anything: just about anything
    :return: hopefully a unicode converted anything
    """
    text = None
    for charset in [u'ascii', u'utf-8', u'utf-16', u'cp1252', u'iso-8859-1']:
        try:
            if anything == None:
                text = u''
            elif isinstance(anything, list):
                text = [returnunicode(x, keep_containers) for x in anything]
            elif isinstance(anything, tuple):
                text = tuple([returnunicode(x, keep_containers) for x in anything])
            elif isinstance(anything, dict):
                text = dict([(returnunicode(k, keep_containers), returnunicode(v, keep_containers)) for k, v in anything.iteritems()])
            else:
                text = anything

            if isinstance(text, (list, tuple, dict)):
                if not keep_containers:
                    text = unicode(text)
            elif isinstance(text, str):
                text = unicode(text, charset)
            elif isinstance(text, unicode):
                pass
            else:
                text = unicode(text)

        except UnicodeEncodeError:
            continue
        except UnicodeDecodeError:
            continue
        else:
            break

    if text is None:
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
            #pop_up_info("Could not connect to DB, please reset Midvatten settings!\n\nDB call causing this error (debug info):\n"+sql)
            textstring = """DB error, you may need to reset Midvatten settings!\nDB call causing this error:%s\n"""%(sql)
            qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=15) 
            ConnectionOK = False
            result = ''
    else:
        #pop_up_info("Could not connect to the database, please reset Midvatten settings!\n\nDB call causing this error (debug info):\n"+sql)
        textstring = """DB error, you may need to reset Midvatten settings!\nDB call causing this error:%s\n"""%(sql)
        qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=15) 
        ConnectionOK = False
        result = ''
    return ConnectionOK, result

def sql_alter_db(sql=''):
    dbpath = QgsProject.instance().readEntry("Midvatten","database")
    conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    curs = conn.cursor()
    sql2 = sql 
    curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

    if isinstance(sql2, basestring):
        try:
            resultfromsql = curs.execute(sql2) #Send SQL-syntax to cursor
        except IntegrityError, e:
            raise IntegrityError("The sql failed:\n" + sql2 + "\nmsg:\n" + str(e))
    else:
        try:
            resultfromsql = curs.executemany(sql2[0], sql2[1])
        except IntegrityError, e:
            raise IntegrityError(str(e))

    result = resultfromsql.fetchall()
    conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
    resultfromsql.close()
    conn.close()

    return result

def sql_alter_db_by_param_subst(sql='',*subst_params):
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

def unicode_2_utf8(anything): #takes an unicode and tries to return it as utf8
    ur"""

    :param anything: just about anything
    :return: hopefully a utf8 converted anything
    """
    #anything = returnunicode(anything)
    text = None
    try:
        if type(anything) == type(None):
            text = (u'').encode('utf-8')
        elif isinstance(anything, unicode):
            text = anything.encode('utf-8')
        elif isinstance(anything, list):
            text = ([unicode_2_utf8(x) for x in anything])
        elif isinstance(anything, tuple):
            text = (tuple([unicode_2_utf8(x) for x in anything]))
        elif isinstance(anything, float):
            text = anything.encode('utf-8')
        elif isinstance(anything, int):
            text = anything.encode('utf-8')
        elif isinstance(anything, dict):
            text = (dict([(unicode_2_utf8(k), unicode_2_utf8(v)) for k, v in anything.iteritems()]))
        elif isinstance(anything, str):
            text = anything
        elif isinstance(anything, bool):
            text = anything.encode('utf-8')
    except:
        pass

    if text is None:
        text = 'data type unknown, check database'.encode('utf-8')
    return text

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
    layer = get_active_layer()
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

def get_active_layer():
    iface = qgis.utils.iface
    if iface is not None:
        return iface.activeLayer()
    else:
        return False

def verify_this_layer_selected_and_not_in_edit_mode(errorsignal,layername):
    layer = get_active_layer()
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

def verify_table_exists(tablename):
    tablename = returnunicode(tablename)
    sql = u"""SELECT name FROM sqlite_master WHERE type='table' AND name='%s'"""%(tablename)
    sql_result = sql_load_fr_db(sql.encode('utf-8'))
    connection_ok, result_list = sql_result

    if not connection_ok:
        return False

    if result_list:
        return True
    else:
        return False

@contextmanager
def tempinput(data, charset=u'UTF-8'):
    """ Creates and yields a temporary file from data
    
        The file can't be deleted in windows for some strange reason.
        There shouldn't be so many temporary files using this function
        for it to be a major problem though. Relying on windows temp file
        cleanup instead.
    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    unicode_data = returnunicode(data)
    encoded_data = unicode_data.encode(charset)
    temp.write(encoded_data)
    temp.close()
    yield temp.name
    #os.unlink(temp.name) #TODO: This results in an error: WindowsError: [Error 32] Det går inte att komma åt filen eftersom den används av en annan process: 'c:\\users\\dator\\appdata\\local\\temp\\tmpxvcfna.csv'

def find_nearest_date_from_event(event): 
    """ Returns the nearest date from a picked list event artist from mouse click
    
        The x-axis of the artist is assumed to be a date as float or int.
        The found date float is then converted into datetime and returned.
    """
    line_nodes = np.array(zip(event.artist.get_xdata(), event.artist.get_ydata()))
    xy_click = np.array((event.mouseevent.xdata, event.mouseevent.ydata))
    nearest_xy = find_nearest_using_pythagoras(xy_click, line_nodes)    
    nearest_date = num2date(nearest_xy[0])
    return nearest_date 

def find_nearest_using_pythagoras(xy_point, xy_array):
    """ Finds the point in xy_array that is nearest xy_point

        xy_point: tuple with two floats representing x and y
        xy_array: list of tuples with floats representing x and y points 
    
        The search is using pythagoras theorem.
        If the search becomes very slow when the xy_array gets long,
        it could probably we rewritten using numpy methods.

        >>> find_nearest_using_pythagoras((1, 2), ((4, 5), (3, 5), (-1, 1)))
        (-1, 1)
    """    
    distances = [math.sqrt((float(xy_point[0]) - float(xy_array[x][0]))**2 + (float(xy_point[1]) - float(xy_array[x][1]))**2) for x in xrange(len(xy_array))]
    min_index = distances.index(min(distances))
    return xy_array[min_index]
    
def ts_gen(ts):
    """ A generator that supplies one tuple from a list of tuples at a time

        ts: a list of tuples where the tuple contains two positions.
        
        Usage:
        a = ts_gen(ts)
        b = next(a)

        >>> for x in ts_gen(((1, 2), ('a', 'b'))): print x
        (1, 2)
        ('a', 'b')
    """        
    for idx in xrange(len(ts)):
        yield (ts[idx][0], ts[idx][1])  
  
def calc_mean_diff(coupled_vals):
    """ Calculates the mean difference for all value couples in a list of tuples 
    
        Nan-values are excluded from the mean.
    """
    return np.mean([float(m) - float(l) for m, l in coupled_vals if not math.isnan(m) or math.isnan(l)])

def get_latlon_for_all_obsids():
    """
    Returns lat, lon for all obsids
    :return: A dict of tuples with like {'obsid': (lat, lon)} for all obsids in obs_points
    """
    latlon_dict = get_sql_result_as_dict('SELECT obsid, Y(Transform(geometry, 4326)) as lat, X(Transform(geometry, 4326)) as lon from obs_points')[1]
    latlon_dict = dict([(obsid, lat_lon[0]) for obsid, lat_lon in latlon_dict.iteritems()])
    return latlon_dict

def get_last_used_flow_instruments():
    """ Returns flow instrumentids
    :return: A dict like {obsid: (flowtype, instrumentid, last date used for obsid)
    """
    return get_sql_result_as_dict('SELECT obsid, flowtype, instrumentid, max(date_time) FROM w_flow GROUP BY obsid, flowtype, instrumentid')

def get_last_logger_dates():
    ok_or_not, obsid_last_imported_dates = get_sql_result_as_dict('select obsid, max(date_time) from w_levels_logger group by obsid')
    return returnunicode(obsid_last_imported_dates, True)

def get_quality_instruments():
    """
    Returns quality instrumentids
    :return: A tuple with instrument ids from w_qual_field
    """
    sql = 'SELECT distinct instrument from w_qual_field'
    sql_result = sql_load_fr_db(sql)
    connection_ok, result_list = sql_result

    if not connection_ok:
        textstring = """Failed to get quality instruments from from sql """ + sql
        qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=10)
        return False, tuple()

    return True, returnunicode([x[0] for x in result_list], True)

def get_last_used_quality_instruments():
    """
    Returns quality instrumentids
    :return: A tuple with instrument ids from w_qual_field
    """
    sql = 'select parameter, unit, instrument, staff, max(date_time) from w_qual_field group by parameter, unit, instrument, staff'
    connection_ok, result_dict = get_sql_result_as_dict(sql)
    return returnunicode(result_dict, True)

def get_sql_result_as_dict(sql):
    """
    Runs sql and returns result as dict
    :param sql: The sql command to run
    :return: A dict with the first column as key and the rest in a tuple as value
    """
    sql_result = sql_load_fr_db(sql)
    connection_ok, result_list = sql_result

    if not connection_ok:
        textstring = """Cannot create dictionary from sql """ + sql
        qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=10)
        return False, {}

    result_dict = {}
    for res in result_list:
        result_dict.setdefault(res[0], []).append(tuple(res[1:]))
    return True, result_dict

def lstrip(word, from_string):
    """
    Strips word from the start of from_string
    :param word: a string to strip
    :param from_string: the string to strip from
    :return: the new string or the old string if word was not at the beginning of from_string.

    >>> lstrip('123', '123abc')
    'abc'
    >>> lstrip('1234', '123abc')
    '123abc'
    """
    new_word = from_string
    if from_string.startswith(word):
        new_word = from_string[len(word):]
    return new_word

def rstrip(word, from_string):
    """
    Strips word from the end of from_string
    :param word: a string to strip
    :param from_string: the string to strip from
    :return: the new string or the old string if word was not at the end of from_string.

    >>> rstrip('abc', '123abc')
    '123'
    >>> rstrip('abcd', '123abc')
    '123abc'
    """
    new_word = from_string
    if from_string.endswith(word):
        new_word = from_string[0:-len(word)]
    return new_word

def select_files(only_one_file=True, extension="csv (*.csv)", should_ask_for_charset=True):
    """Asks users to select file(s) and charset for the file(s)"""
    if should_ask_for_charset:
        charsetchoosen = ask_for_charset()
    else:
        charsetchoosen = 'nocharsetchosen'
    if charsetchoosen and not (charsetchoosen[0]==0 or charsetchoosen[0]==''):
        if only_one_file:
            csvpath = QtGui.QFileDialog.getOpenFileName(None, "Select File","", extension)
        else:
            csvpath = QtGui.QFileDialog.getOpenFileNames(None, "Select Files","", extension)
        if not isinstance(csvpath, (list, tuple)):
            csvpath = [csvpath]
        csvpath = [p for p in csvpath if p]
        return csvpath, charsetchoosen

def ask_for_charset(default_enchoding=None):
    try:#MacOSX fix2
        localencoding = locale.getdefaultlocale()[1]
        if default_enchoding is None:
            charsetchoosen = QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        else:
            charsetchoosen = QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",QtGui.QLineEdit.Normal,default_enchoding)
    except:
        if default_enchoding is None:
            default_enchoding = 'utf-8'
        charsetchoosen = QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",QtGui.QLineEdit.Normal,default_enchoding)
    return str(charsetchoosen[0])

def lists_to_string(alist_of_lists):
    ur"""

    :param alist_of_lists:
    :return: A string with '\n' separating rows and ; separating columns.

    >>> lists_to_string([1])
    u'1'
    >>> lists_to_string([('a', 'b'), (1, 2)])
    u'a;b\n1;2'
    """
    if isinstance(alist_of_lists, list) or isinstance(alist_of_lists, tuple):
        return_string = u'\n'.join([u';'.join([returnunicode(y) for y in x]) if isinstance(x, list) or isinstance(x, tuple) else returnunicode(x) for x in alist_of_lists])
    else:
        return_string = returnunicode(alist_of_lists)

    return return_string

def find_similar(word, wordlist, hits=5):
    ur"""

    :param word: the word to find similar words for
    :param wordlist: the word list to find similar in
    :param hits: the number of hits in first match (more hits will be added than this)
    :return:  a set with the matches

    >>> find_similar(u'rb1203', [u'Rb1203', u'rb 1203', u'gert', u'rb', u'rb1203', u'b1203', u'rb120', u'rb11', u'rb123', u'rb1203_bgfgf'], 5)
    [u'rb 1203', u'b1203', u'rb120', u'Rb1203', u'rb1203_bgfgf', u'rb123', u'rb1203']
    >>> find_similar(u'1', [u'2', u'3'], 5)
    [u'']
    >>> find_similar(None, [u'2', u'3'], 5)
    [u'']
    >>> find_similar(None, None, 5)
    [u'']
    >>> find_similar(u'1', [], 5)
    [u'']
    >>> find_similar(u'1', False, 5)
    [u'']
    >>> find_similar(False, [u'2', u'3'], 5)
    [u'']

    """
    if None in [word, wordlist] or not wordlist or not word:
        return [u'']

    matches = set(difflib.get_close_matches(word, wordlist, hits))
    matches.update([x for x in wordlist if any((x.startswith(word.lower()), x.startswith(word.upper()), x.startswith(word.capitalize())))])
    nr_of_hits = len(matches)
    if nr_of_hits == 0:
        return [u'']
    #Sort again to get best hit first
    matches = list(set(difflib.get_close_matches(word, matches, nr_of_hits)))
    return matches

def filter_nonexisting_values_and_ask(file_data, header_value, existing_values=[], try_capitalize=False):
    header_value = returnunicode(header_value)
    filtered_data = []
    data_to_ask_for = []
    for rownr, row in enumerate(file_data):
        if rownr == 0:
            try:
                index = row.index(header_value)
            except ValueError:
                #The header_value did not exist, returning file_data as it is.
                return file_data
            else:
                filtered_data.append(row)
            continue

        value = row[index]
        if value not in existing_values:
            data_to_ask_for.append(row)
        else:
            filtered_data.append(row)

    already_asked_values = {}

    for rownr, row in enumerate(data_to_ask_for):

        #First check if the current value already has been asked for and if so
        # use the same answer again.
        try:
            row[index] = already_asked_values[row[index]]
        except KeyError:
            current_value = row[index]
        else:
            if row[index] is not None:
                filtered_data.append(row)
            continue

        similar_values = find_similar(current_value, existing_values, hits=5)

        not_tried_capitalize = True

        answer = None
        while current_value not in existing_values:
            if try_capitalize and not_tried_capitalize:
                try:
                    current_value = current_value.capitalize()
                except AttributeError:
                    not_tried_capitalize = False
                else:
                    not_tried_capitalize = False
                    continue

            question = NotFoundQuestion(dialogtitle=u'WARNING',
                                        msg=u'(Message ' + unicode(rownr + 1) + u' of ' + unicode(len(data_to_ask_for)) + u')\n\nThe supplied ' + header_value + u' "' + current_value + u'" on row:\n"' + u', '.join(row) + u'".\ndid not exist in db.\n\nPlease submit it again!\nIt will be used for all occurences of the same ' + header_value + u'\n',
                                        existing_list=similar_values,
                                        default_value=similar_values[0],
                                        button_names=[u'Ignore', u'Cancel', u'Ok', u'Skip'])
            answer = question.answer
            submitted_value = returnunicode(question.value)
            if answer == u'cancel':
                return answer
            elif answer == u'ignore':
                current_value = submitted_value
                break
            elif answer == u'ok':
                current_value = submitted_value
            elif answer == u'skip':
                break

        if answer == u'skip':
            if row[index] not in already_asked_values:
                already_asked_values[row[index]] = None
        else:
            if row[index] not in already_asked_values:
                already_asked_values[row[index]] = current_value
            row[index] = current_value
            filtered_data.append(row)

    return filtered_data

def add_triggers_to_obs_points():
    """
    /*
    * These are quick-fixes for updating coords from geometry and the other way around
    * Please notice that these are AFTER insert/update although BEFORE should be preferrable?
    * Also, srid is not yet read from the
    */

    -- geometry updated after coordinates are inserted
    CREATE TRIGGER "after_insert_obs_points_geom_fr_coords" AFTER INSERT ON "obs_points"
    WHEN (0 < (select count() from obs_points where ((NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL))))
    BEGIN
        UPDATE obs_points
        SET  geometry = MakePoint(east, north, (select srid from geometry_columns where f_table_name = 'obs_points'))
        WHERE (NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL);
    END;

    -- coordinates updated after geometries are inserted
    CREATE TRIGGER "after_insert_obs_points_coords_fr_geom" AFTER INSERT ON "obs_points"
    WHEN (0 < (select count() from obs_points where ((NEW.east is null) AND (NEW.north is null) AND (NEW.geometry is not NULL))))
    BEGIN
        UPDATE obs_points
        SET  east = X(geometry), north = Y(geometry)
        WHERE (NEW.east is null) AND (NEW.north is null) AND (NEW.geometry is not NULL);
    END;

    -- coordinates updated after geometries are updated
    CREATE TRIGGER "after_update_obs_points_coords_fr_geom" AFTER UPDATE ON "obs_points"
    WHEN (0 < (select count() from obs_points where NEW.geometry != OLD.geometry) )
    BEGIN
        UPDATE obs_points
        SET  east = X(geometry), north = Y(geometry)
        WHERE (NEW.geometry != OLD.geometry);
    END;

    -- geometry updated after coordinates are updated
    CREATE TRIGGER "after_update_obs_points_geom_fr_coords" AFTER UPDATE ON "obs_points"
    WHEN (0 < (select count() from obs_points where ((NEW.east != OLD.east) OR (NEW.north != OLD.north))) )
    BEGIN
        UPDATE obs_points
        SET  geometry = MakePoint(east, north, (select srid from geometry_columns where f_table_name = 'obs_points'))
        WHERE ((NEW.east != OLD.east) OR (NEW.north != OLD.north));
    END;
    :return:
    """
    excecute_sqlfile(os.path.join(os.sep,os.path.dirname(__file__),"..","definitions","insert_obs_points_triggers.sql"), sql_alter_db)

def excecute_sqlfile(sqlfilename, function=sql_alter_db):
    with open(sqlfilename, 'r') as f:
        f.readline()  # first line is encoding info....
        for line in f:
            if not line:
                continue
            if line.startswith("#"):
                continue
            function(line)

def sql_to_parameters_units_tuple(sql):
    parameters_from_table = returnunicode(sql_load_fr_db(sql)[1], True)
    parameters_dict = {}
    for parameter, unit in parameters_from_table:
        parameters_dict.setdefault(parameter, []).append(unit)
    parameters = tuple([(k, tuple(v)) for k, v in sorted(parameters_dict.iteritems())])
    return parameters

def scale_nparray(x, a=1, b=0):
    """
    Scales a 1d numpy array using linear equation
    :param x: A numpy 1darray, x in y=kx+m
    :param a: k in y=ax+b
    :param b: m in y=ax+b
    :return: A numpy 1darray, y in y=ax+b

    >>> scale_nparray(np.array([2,3,1,0]), b=10)
    array([12, 13, 11, 10])
    >>> scale_nparray(np.array([2,3,1,0]), b=10, a=4)
    array([18, 22, 14, 10])
    >>> scale_nparray(np.array([2,3,1,0]), 2)
    array([4, 6, 2, 0])
    >>> scale_nparray(np.array([2,3,1,0]), 2, -5)
    array([-1,  1, -3, -5])
    >>> scale_nparray(np.array([2,3,1,0]), -2, -5)
    array([ -9, -11,  -7,  -5])
    """
    return a * copy.deepcopy(x) + b

def getcurrentlocale():
    current_locale = QgsProject.instance().readEntry("Midvatten", "locale")[0]
    return current_locale
