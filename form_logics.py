# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsFeature

from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import qgis.utils # for error/debug messages to messagebar

myDialog = None


def obs_lines_form_open(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog

    """
    if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_lines'):#if obsid in database, then blank background
         myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#red bg if obsid not set
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved - so background is set red
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        #utils.pop_up_info("obsid is not null nor empty - but it also is not in db!")#debug
    """
    #dialog.findChild(QLineEdit,"obsid").textChanged.connect(obs_lines_obsid_field_text_changed)
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    #buttonBox.accepted.connect(obs_lines_validate)
    myDialog.attributeChanged.connect(attr_changed)
    buttonBox.rejected.connect(myDialog.reject)

def obs_points_form_open(dialog,layerid,featureid):
    global myDialog        
    myDialog = dialog
    try:#if it is an old form with a CRS label field, then update CRS label field and also try to update check boxes etc
        sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
        result = utils.sql_load_fr_db(sql)[1]
        CRS_field = myDialog.findChild(QLabel,"CRS")
        CRS_field.setText("EPSG:" + str(result[0][0]))
        if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_points'):#if it is an obsid which already exists in database, then fill wmeas_yn and wlogg_yn fields
            sql = r"""SELECT wmeas_yn FROM obs_points where obsid = '"""
            sql += myDialog.findChild(QLineEdit,"obsid").text()
            sql += """'"""
            result = utils.sql_load_fr_db(sql)[1]
            if result:
                if str(result[0][0]) == '1':
                    wmeas_yn_field = dialog.findChild(QCheckBox,"wmeas_yn")
                    wmeas_yn_field.setChecked(True)
            sql = r"""SELECT wlogg_yn FROM obs_points where obsid = '"""
            sql += myDialog.findChild(QLineEdit,"obsid").text()
            sql += """'"""
            result = utils.sql_load_fr_db(sql)[1]
            if str(result[0][0]) == '1':
                wlogg_yn_field = dialog.findChild(QCheckBox,"wlogg_yn")
                wlogg_yn_field.setChecked(True)
    except:
        pass

    """
    if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(), 'obs_points'):
        pass
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#RED bg if NULL or empty 
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    """
    """
    # connecting signal for myDialog.attributeChanged.
    # but this signal is triggered way too often when using attribute table dual view  and therefore, from plugin version 1.1, 
    # skip most parts of checking obsid duplicates in database 
    #dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    """
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    #buttonBox.accepted.connect(obs_points_validate)
    myDialog.attributeChanged.connect(attr_changed)
    buttonBox.rejected.connect(myDialog.reject)

def w_levels_form_open(dialog,layerid,featureid):#not ready
    global myDialog        #
    myDialog = dialog
    """
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0)  or not (obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_levels')):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(w_levels_obsid_field_text_changed)
    
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    dialog.findChild(QLineEdit,"date_time").textChanged.connect(w_levels_date_time_field_text_changed)
    
    if utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")
    dialog.findChild(QLineEdit,"level_masl").textChanged.connect(w_levels_level_masl_field_text_changed)
    """
    level_masl_field = dialog.findChild(QLineEdit,"level_masl")
    level_masl_field.setText("-999")
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    myDialog.attributeChanged.connect(attr_changed)
    buttonBox.rejected.connect(myDialog.reject)

def stratigraphy_form_open(dialog,layerid,featureid):
    global myDialog, myLayer
    myDialog = dialog
    myLayer = layerid
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)
    # Wire up our own signals.
    #buttonBox.accepted.connect(stratigraphy_validate)
    myDialog.attributeChanged.connect(attr_changed)
    buttonBox.rejected.connect(myDialog.reject)
    #the last one is very useful but not ready yet
    #layerid.featureAdded.connect(stratigraphy_feature_added)
    
def w_flow_form_open(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)
    """
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_flow')):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(w_flow_obsid_field_text_changed)
    
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    dialog.findChild(QLineEdit,"date_time").textChanged.connect(w_flow_date_time_field_text_changed)
    
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"instrumentid").text()) == 0):
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")
    dialog.findChild(QLineEdit,"instrumentid").textChanged.connect(w_flow_instrumentid_field_text_changed)

    if (myDialog.findChild(QLineEdit,"flowtype").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"flowtype").text()) == 0) or not (flowtype_exists(myDialog.findChild(QLineEdit,"flowtype").text(),'w_flow')):
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")
    dialog.findChild(QLineEdit,"flowtype").textChanged.connect(w_flow_flowtype_field_text_changed)

    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False): 
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")
    dialog.findChild(QLineEdit,"reading").textChanged.connect(w_flow_reading_field_text_changed)

    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"unit").text()) == 0): 
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("")
    dialog.findChild(QLineEdit,"unit").textChanged.connect(w_flow_unit_field_text_changed)
    """
    # Wire up our own signals.
    myDialog.attributeChanged.connect(attr_changed)
    buttonBox.rejected.connect(myDialog.reject)

def attr_changed(attr,value):#background is set red if values do not fulfill simple validity checks
    """
    this one will mainly color field backgrounds to red in case of database inconsistencies or not yet saved edits
    the message handling is commented out since it is not very useful - there is way too many attr_changed signals
    """
    #bg color for field obsid - if obsid exists in db or not
    if attr == "obsid":
        if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_points') or obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_lines'):#if obsid in database, then blank background, and try some table specific field updates
            myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
        #elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#red bg if obsid not set
        #    myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved - so background is set red
            myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    """
    elif attr!="obsid":#is there any use for changing background color for obsid when other fields are changed?
        if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_points') or obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_lines'):#if obsid in database, then blank background
             myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
        elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#red bg if obsid not set
            myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved - so background is set red
            myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
            qgis.utils.iface.messageBar().pushMessage("Info",myDialog.findChild(QLineEdit,"obsid").text()+" does not seem to exist in the database yet!",0,duration=2)
    """
    
    # then attribute-specific checks - note that they are only performed for strings, the other ones are having constraints from the qgis editor
    if attr=="unit":
        if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"unit").text()) ==0):
            myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"unit").setStyleSheet("") 
    elif attr=="instrumentid":
        if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"instrumentid").text()) ==0): 
            myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);") 
        else:
            myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")
    elif attr=="flowtype":
        if not flowtype_exists(myDialog.findChild(QLineEdit,"flowtype").text()): 
            myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")
    #If qgis edit widget types were more flexible (number of decimal places etc) then the following ones would not be needed, keep on to-do-list 
    elif attr=="stratid":
        if utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False:
            myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")   
    elif attr=="depthtop":
        if utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False:
            myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            try:
                if not (float(myDialog.findChild(QLineEdit,"depthtop").text()) < float(myDialog.findChild(QLineEdit,"depthbot").text())):
                    myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
                    myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
                    #qgis.utils.iface.messageBar().pushMessage("Error","depthbot must be greated than depthtop!",2,duration=2)
                else:
                    myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  
                    myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")
            except:
                myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")
    elif attr=="depthbot":
        if utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False:
            myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            try:
                if not (float(myDialog.findChild(QLineEdit,"depthtop").text()) < float(myDialog.findChild(QLineEdit,"depthbot").text())):
                    myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
                    myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
                    #qgis.utils.iface.messageBar().pushMessage("Error","depthbot must be greated than depthtop!",2,duration=2)
                else:
                    myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")
                    myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")
            except:
                myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")
    elif attr=="level_masl":
        if utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False:
            myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")
    elif attr=="reading":
        if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
            myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"reading").setStyleSheet("")  
    elif attr=="reading_num":
        if (myDialog.findChild(QLineEdit,"reading_num").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading_num").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
            myDialog.findChild(QLineEdit,"reading_num").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"reading_num").setStyleSheet("")  
    elif attr=="reading, numerical":
        if (myDialog.findChild(QLineEdit,"reading, numerical").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading, numerical").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
            myDialog.findChild(QLineEdit,"reading, numerical").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"reading, numerical").setStyleSheet("")  
    elif attr=="report":
        if (myDialog.findChild(QLineEdit,"report").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"report").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
            myDialog.findChild(QLineEdit,"report").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"report").setStyleSheet("") 
    elif attr=="parameter":
        if (myDialog.findChild(QLineEdit,"parameter").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"parameter").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
            myDialog.findChild(QLineEdit,"parameter").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"parameter").setStyleSheet("") 
            
            
    """
    elif attr=="date_time":#using date/time edit widgets instead
        if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
            myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        else:
            myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    """

def obsid_exists(obsid, tablename):
    sql = r"""SELECT obsid FROM """ + tablename + """ where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'

def flowtype_exists(flowtype):  # Check if obsid exists in database.
    sql = r"""SELECT type FROM zz_flowtype where type = '""" + flowtype + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'
                
def stratigraphy_feature_added(fid):# - NOT READY whenever a new feature is added, then wait for obsid and preset stratid to next number and preset depthtop to latest depthbot.
    """
    This is not ready and do not work as expected
    """
    
    #prompt user to tell which observation point he/she is about to give stratigraphy layer info for
    obsidstring = QInputDialog.getText(None, "Set obsid", "What observation point (obsid) are you about to give stratigraphy info for?",QLineEdit.Normal,'')
    print('debug obsidstring[0] = ' + obsidstring[0])#debug
    print('debug fid-type is ' + str(type(fid)))#debug
    #charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
    if obsidstring and not (obsidstring[0]==0 or obsidstring[0]==''):
        if not obsid_exists(obsidstring[0],'obs_points'):
            qgis.utils.iface.messageBar().pushMessage("Error","The obsid " + obsidstring[0] + " does not exist in database table obs_points!",2,duration=10)
        else:
            qgis.utils.iface.messageBar().pushMessage("Info","Suggested values for " + obsidstring[0] + " fields stratid, depthtop, depthbot will be set!",0,duration=5)
            """
            feat = QgsFeature()
            myLayer.featureAtId(fid, feat)
            """
            #print('debug show fid obsid value : ' + str(thisfeat['obsid']))#debug
            #thisfeat['obsid'] = str(obsidstring[0])
            myLayer.dataProvider().changeAttributeValues({ fid :  { 'obsid' : str(obsidstring[0])} })
            sql = r"""select max(stratid) from stratigraphy WHERE obsid = '"""
            sql += obsidstring[0]
            sql += r"""'"""
            maxstratid = utils.sql_load_fr_db(sql)[1]
            if utils.isinteger(str(maxstratid[0][0]).encode('utf-8'))==True:
                #fid['stratid'] = int(maxstratid[0][0])+1 # stratid is preset to max(stratid) + 1 in db
                myLayer.dataProvider().changeAttributeValues({ fid :  { 'stratid' : int(maxstratid[0][0])+1} })
                sql = r"""select max(depthbot) from stratigraphy WHERE obsid = '"""
                sql +=obsidstring[0]
                sql += r"""'"""
                maxdepthbot = utils.sql_load_fr_db(sql)[1]
                if utils.isfloat(str(maxdepthbot[0][0]).encode('utf-8'))==True:
                    #fid['depthtop'] = maxdepthbot[0][0] #depthtop is preset to max(depthbot) in db
                    myLayer.dataProvider().changeAttributeValues({ fid :  { 'depthtop' : maxdepthbot[0][0]} })
            else:#if it is the first layer for this obsid, assume it is from depth 0
                #fid['stratid'] = 1
                myLayer.dataProvider().changeAttributeValues({ fid :  { 'stratid' : 1} })
                #fid['depthtop'] = 0 
                myLayer.dataProvider().changeAttributeValues({ fid :  { 'depthtop' : 0} })
        


def w_flow_validate():   #This is not used anymore!

    if not (obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_flow')):
        utils.pop_up_info("obsid must exist in database table obs_points!")
    elif utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        utils.pop_up_info("Invalid date!")
    elif not (flowtype_exists(myDialog.findChild(QLineEdit,"flowtype").text(),'w_flow')):
        utils.pop_up_info("flowtype must exist in database table zz_flowtypes!")
    elif not utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==True:
        utils.pop_up_info("reading must be a floating-point number!")
    elif not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"instrumentid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"flowtype").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"date_time").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"reading").text()) > 0 and
            len(myDialog.findChild(QLineEdit,"unit").text()) > 0): 
        utils.pop_up_info("obsid, instrumentid, flowtype, date_time, reading and unit must not be empty!")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"flowtype").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"date_time").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"reading").text()=='NULL' or
            myDialog.findChild(QLineEdit,"unit").text()=='NULL'):
        utils.pop_up_info("obsid, instrumentid, flowtype, date_time, reading and unit must not be NULL!")
    else:
        myDialog.accept()

def w_levels_validate():  #This is not used anymore!
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"date_time").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"level_masl").text()) > 0): 
        utils.pop_up_info("obsid, date_time and level_masl must not be empty!")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL' or
                myDialog.findChild(QLineEdit,"date_time").text()=='NULL' or 
                myDialog.findChild(QLineEdit,"level_masl").text()=='NULL'):
        utils.pop_up_info("obsid, date_time and level_masl must not be NULL!")
    elif utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        utils.pop_up_info("Invalid date!")
    elif not utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==True:
        utils.pop_up_info("level_masl must be a floating-point number!")
    else:
        # Return the form as accpeted to QGIS.
        myDialog.accept()

def stratigraphy_obsid_field_text_changed():#this was called when a new object was created - not used anymore
    """
    #Warning - this method will corrupt the stratigraphy table when used with dual view!!!
    
    print ('debug info - called function stratigraphy_obsid_field_text_changed')#debug
    # Must find another trigger: new feature/object/record!
    # no no, just check if stratid field is empty, then it is considered a new feature and a default value should be added!!
    if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_points') and (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0): #if stratid is empty, then it is considered to be a new record and preset values should be suggested, otherwise, do not suggest anything!
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
        sql = u"select max(stratid) from stratigraphy WHERE obsid = '"
        sql += myDialog.findChild(QLineEdit,"obsid").text()
        sql += u"'"
        maxstratid = utils.sql_load_fr_db(sql)[1]
        if utils.isinteger(str(maxstratid[0][0]).encode('utf-8'))==True:
            myDialog.findChild(QLineEdit,"stratid").setText(str(int(maxstratid[0][0])+1)) #form stratid is preset to max(stratid) + 1 in db
            sql = u"select max(depthbot) from stratigraphy WHERE obsid = '"
            sql +=myDialog.findChild(QLineEdit,"obsid").text()
            sql += u"'"
            maxdepthbot = utils.sql_load_fr_db(sql)[1]
            if utils.isfloat(str(maxdepthbot[0][0]).encode('utf-8'))==True:
                myDialog.findChild(QLineEdit,"depthtop").setText(str(maxdepthbot[0][0])) #form depthtop is preset to max(depthbot) in db
        else:
            myDialog.findChild(QLineEdit,"stratid").setText("1")
            myDialog.findChild(QLineEdit,"depthtop").setText("0") 
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    """
    pass

def stratigraphy_stratid_field_text_changed():#this was called when a new object was created - not used anymore
    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False): 
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")  

def stratigraphy_depthtop_field_text_changed():#this was called when a new object was created - not used anymore
    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")

    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  

def stratigraphy_depthbot_field_text_changed():#this was called when a new object was created - not used anymore
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")  

def w_flow_obsid_field_text_changed():#This is not used anymore!
    if not obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_flow'):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def w_flow_date_time_field_text_changed():#This is not used anymore!
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"date_time").text()) ==0) or utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False: 
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def w_flow_instrumentid_field_text_changed():#This is not used anymore!
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"instrumentid").text()) ==0): 
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")        

def w_flow_flowtype_field_text_changed():#This is not used anymore!
    if not flowtype_exists(myDialog.findChild(QLineEdit,"flowtype").text(),'w_flow'): 
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")        

def w_flow_reading_field_text_changed():#This is not used anymore!
    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")  
        
def w_flow_unit_field_text_changed():#This is not used anymore!
    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"unit").text()) ==0):
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("") 

def w_levels_obsid_field_text_changed():#This is not used anymore!
    if not obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_levels'):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def w_levels_date_time_field_text_changed():#This is not used anymore!
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def w_levels_level_masl_field_text_changed():#This is not used anymore!
    if (myDialog.findChild(QLineEdit,"level_masl").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"level_masl").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False): 
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")        
