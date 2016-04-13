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
import csv
import codecs
import cStringIO

import qgis.utils
import sys
import os
import math
import numpy as np
import tempfile
from contextlib import contextmanager
from pyspatialite import dbapi2 as sqlite #must use pyspatialite since spatialite-specific sql clauses may be sent by sql_alter_db and sql_load_fr_db
from pyspatialite.dbapi2 import IntegrityError
from matplotlib.dates import datestr2num, num2date
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

def ask_user_about_stopping(question):
    """
    Asks the user a question and returns 'failed' or 'continue' as yes or no
    :param question: A string to write at the dialog box.
    :return: The string 'failed' or 'continue' as yes/no
    """
    answer = askuser("YesNo", question)
    if answer.result:
        return 'failed'
    else:
        return 'continue'

def create_dict_from_db_2_cols(params):#col1, col2, table):#params are (col1=keys,col2=values,db-table)
    print(params)
    sqlstring = r"""select %s, %s from %s"""%(params)
    #print(sqlstring)
    ConnectionOK, list_of_tuples= sql_load_fr_db(sqlstring)
    if ConnectionOK==True:
        #print(list_of_tuples)#debug
        k=[]
        v=[]
        for tuple_item in list_of_tuples:
            k.append(tuple_item[0])
            v.append(tuple_item[1])
        return True, dict(zip(k, v))
    else:
        textstring = """Cannot create dictionary from columns %s and %s in table %s!"""%(params)#col1,col2,table)
        qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=10)        
        return False, {'':''}

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
    ur"""

    >>> returnunicode('b')
    u'b'
    >>> returnunicode(1)
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

    :param anything: just about anything
    :return: hopefully a unicode converted anything
    """
    text = None
    for charset in ['ascii', 'utf-8', 'utf-16', 'cp1252', 'iso-8859-1']:
        try:
            if type(anything) == type(None):
                text = unicode('')
            elif isinstance(anything, unicode):
                text = anything
            elif isinstance(anything, list):
                text = unicode([returnunicode(x) for x in anything])
            elif isinstance(anything, tuple):
                text = unicode(tuple([returnunicode(x) for x in anything]))
            elif isinstance(anything, float):
                text = unicode(anything, charset)
            elif isinstance(anything, str):
                text = unicode(anything, charset)
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
            raise IntegrityError(str(e) + "\nAn obsid chosen for import probably didn't exist in the obs_point table")
    else:
        try:
            resultfromsql = curs.executemany(sql2[0], sql2[1])
        except IntegrityError, e:
            raise IntegrityError(str(e) + "\nAn obsid chosen for import probably didn't exist in the obs_point table")

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
    
@contextmanager
def tempinput(data, charset='UTF-8'):
    """ Creates and yields a temporary file from data
    
        The file can't be deleted in windows for some strange reason.
        There shouldn't be so many temporary files using this function
        for it to be a major problem though. Relying on windows temp file
        cleanup instead.
    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    temp.write(returnunicode(data).encode(charset))
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
    latlon_dict = get_sql_result_as_dict('SELECT obsid, Y(Transform(geometry, 4326)) as lat, X(Transform(geometry, 4326)) as lon from obs_points')
    return latlon_dict

def get_qual_params_and_units():
    """
    Returns water quality parameters and their units as tuples
    :return: Tuple with quality parameter names and their units for all parameters in w_qual_field
    """
    wqual_dict = get_sql_result_as_dict('SELECT distinct parameter, unit FROM w_qual_field')
    return wqual_dict

def get_flow_params_and_units():
    """
    Return flow parameters and their units as tuples
    :return: Tuple with water flow parameter name and their units.
    """
    flow_dict = get_sql_result_as_dict('SELECT distinct flowtype, unit from w_flow')
    return flow_dict

def get_sql_result_as_dict(sql):
    """
    Runs sql and returns result as dict
    :param sql: The sql command to run
    :return: A dict with the first column as key and the rest in a tuple as value
    """
    sql_result = sql_load_fr_db(sql)
    connection_ok, result_list = sql_result

    if not connection_ok:
        pop_up_info("Getting data from db failed!")
        return

    result_dict = dict([(res[0], tuple(res[1:])) for res in result_list])
    return result_dict

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
        return csvpath, charsetchoosen

def ask_for_charset():
    try:#MacOSX fix2
        localencoding = locale.getdefaultlocale()[1]
        charsetchoosen = QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
    except:
        charsetchoosen = QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",QtGui.QLineEdit.Normal,'utf-8')
    return str(charsetchoosen[0])
