# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import qgis.utils # for error/debug messages to messagebar

myDialog = None


def obs_lines_form_open(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog

    if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_lines'):#if it is an obsid which already exists in database, then no particular highlightning
         myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        #utils.pop_up_info("obsid is not null nor empty - but it also is not in db!")#debug

    #dialog.findChild(QLineEdit,"obsid").textChanged.connect(obs_lines_obsid_field_text_changed)
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(obs_lines_validate)
    buttonBox.rejected.connect(myDialog.reject)

def obs_points_form_open(dialog,layerid,featureid):
    #sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
    #result = utils.sql_load_fr_db(sql)[1]
    #CRS_field = dialog.findChild(QLabel,"CRS")
    #CRS_field.setText("EPSG:" + str(result[0][0]))
    global myDialog        
    myDialog = dialog

    if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(), 'obs_points'):
        pass
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#RED bg if NULL or empty 
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")

    # Connect signal for obsid text changed - this signal is triggered way too often when using attribute table dual view -
    # therefore, from plugin version 1.1, suppressing form logic control for checking obsid duplicates in database 
    #dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_field_text_changed)
    # Connect signal for obsid text changed - from plugin version 1.1 only watching for empty obsid fields
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obs_points_obsid_new_object_red_color)    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(obs_points_validate)
    buttonBox.rejected.connect(myDialog.reject)

def obs_points_tab_layout_form_open(dialog,layerid,featureid):
    #sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
    #result = utils.sql_load_fr_db(sql)[1]
    #CRS_field = dialog.findChild(QLabel,"CRS")
        #CRS_field.setText("EPSG:" + str(result[0][0]))

    global myDialog        
    myDialog = dialog

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
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#RED bg if NULL or empty 
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        #utils.pop_up_info("obsid is not null nor empty - but it also is not in db!")#debug

    # Connect signal for obsid text changed - this signal is triggered way too often when using attribute table dual view -
    # therefore, from plugin version 1.1, suppressing form logic control for checking obsid duplicates in database 
    #dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    # Connect signal for obsid text changed - from plugin version 1.1 only watching for empty obsid fields
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_new_object_red_color)
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(obs_points_validate)
    buttonBox.rejected.connect(myDialog.reject)

def w_levels_form_open(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog

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

    level_masl_field = dialog.findChild(QLineEdit,"level_masl")
    level_masl_field.setText("-999")
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(w_levels_validate)
    buttonBox.rejected.connect(myDialog.reject)

def stratigraphy_form_open(dialog,layerid,featureid):
    global myDialog
    myDialog = dialog
    stratigraphy_obsid_field_text_changed()
    
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'stratigraphy')):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(stratigraphy_obsid_field_text_changed)

    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False):
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")
    dialog.findChild(QLineEdit,"stratid").textChanged.connect(stratigraphy_stratid_field_text_changed)

    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  
    dialog.findChild(QLineEdit,"depthtop").textChanged.connect(stratigraphy_depthtop_field_text_changed)
        
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")     
    dialog.findChild(QLineEdit,"depthbot").textChanged.connect(stratigraphy_depthbot_field_text_changed)
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(stratigraphy_validate)
    buttonBox.rejected.connect(myDialog.reject)

def w_flow_form_open(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

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
    
    # Wire up our own signals.
    buttonBox.accepted.connect(w_flow_validate)
    buttonBox.rejected.connect(myDialog.reject)

def obsid_exists(obsid, tablename):
    sql = r"""SELECT obsid FROM """ + tablename + """ where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'

def obs_points_obsid_new_object_red_color():
    """if obsid text changes and the field is empty, then it is a new object and background should be red"""
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or len(myDialog.findChild(QLineEdit,"obsid").text()) ==0:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def obs_lines_validate():  # Make sure mandatory fields are not empty.
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0): 
        utils.pop_up_info("obsid must not be empty!")
    elif myDialog.findChild(QLineEdit,"obsid").text()=='NULL':
        utils.pop_up_info("obsid must not be NULL!")
    else:
        # make sure flowtype is within allowed data domain
        myDialog.accept()

def obs_points_validate():  # Make sure mandatory fields are not empty.
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0): # If obsid is empty
        utils.pop_up_info("obsid must not be empty!")
    elif myDialog.findChild(QLineEdit,"obsid").text()=='NULL': # or myDialog.findChild(QLineEdit,"h_gs").text()=='NULL'):
        utils.pop_up_info("obsid must not be NULL!")
    else:
        myDialog.accept()# Return the form as accepted to QGIS.
                
def stratigraphy_validate():  # Make sure mandatory fields are not empty.
    if not (obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'stratigraphy')):
        utils.pop_up_info("obsid must exist in database table obs_points!")
    elif not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"stratid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"depthtop").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"depthbot").text()) > 0):
        utils.pop_up_info("obsid, stratid, depthtop and depthbot must not be empty!")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL' or
                myDialog.findChild(QLineEdit,"stratid").text()=='NULL' or 
                myDialog.findChild(QLineEdit,"depthtop").text()=='NULL' or 
                myDialog.findChild(QLineEdit,"depthbot").text()=='NULL'):
        utils.pop_up_info("obsid, stratid, depthtop and depthbot must not be NULL!")
    elif not utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==True:
        utils.pop_up_info("stratid must be an integer!")
    elif not (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==True and utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==True):
        utils.pop_up_info("both depthtop and depthbot must be a floating-point numbers!")
    elif not (float(myDialog.findChild(QLineEdit,"depthtop").text()) < float(myDialog.findChild(QLineEdit,"depthbot").text())):
        utils.pop_up_info("depthbot must be greater than depthtop!")
    else:
        # Return the form as accpeted to QGIS.
        myDialog.accept()

def w_flow_validate():  # Make sure mandatory fields are not empty.

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

def w_levels_validate():  # Make sure mandatory fields are not empty.
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
        
"""
def obs_lines_obsid_field_text_changed():
    #qgis.utils.iface.messageBar().pushMessage("Debug",myDialog.findChild(QLineEdit,"obsid").text(),0)#debug
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or len(myDialog.findChild(QLineEdit,"obsid").text()) ==0:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    elif obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_lines'):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        #qgis.utils.iface.messageBar().pushMessage("Warning",myDialog.findChild(QLineEdit,"obsid").text()+" alredy exists!",1)
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
"""

"""        
def obs_points_obsid_field_text_changed():
    #qgis.utils.iface.messageBar().pushMessage("Debug",myDialog.findChild(QLineEdit,"obsid").text(),0)#debug
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or len(myDialog.findChild(QLineEdit,"obsid").text()) ==0:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    elif obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'obs_points'):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        #qgis.utils.iface.messageBar().pushMessage("Warning",myDialog.findChild(QLineEdit,"obsid").text()+" alredy exists!",1)
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
"""

def stratigraphy_obsid_field_text_changed():#whenever a new obsid is given, then preset stratid to next number and preset depthtop to latest depthbot.
    """ Must find another trigger: new feature/object/record!"""
    """ no no, just check if stratid field is empty, then it is considered a new feature and a default value should be added!!"""
    if obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'stratigraphy') and (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0): #if stratid is empty, then it is considered to be a new record and preset values should be suggested, otherwise, do not suggest anything!
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
        sql = r"""select max(stratid) from stratigraphy WHERE obsid = '"""
        sql += myDialog.findChild(QLineEdit,"obsid").text()
        sql += r"""'"""
        maxstratid = utils.sql_load_fr_db(sql)[1]
        if utils.isinteger(str(maxstratid[0][0]).encode('utf-8'))==True:
            myDialog.findChild(QLineEdit,"stratid").setText(str(int(maxstratid[0][0])+1)) #form stratid is preset to max(stratid) + 1 in db
            sql = r"""select max(depthbot) from stratigraphy WHERE obsid = '"""
            sql +=myDialog.findChild(QLineEdit,"obsid").text()
            sql += r"""'"""
            maxdepthbot = utils.sql_load_fr_db(sql)[1]
            if utils.isfloat(str(maxdepthbot[0][0]).encode('utf-8'))==True:
                myDialog.findChild(QLineEdit,"depthtop").setText(str(maxdepthbot[0][0])) #form depthtop is preset to max(depthbot) in db
        else:
            myDialog.findChild(QLineEdit,"stratid").setText("1")
            myDialog.findChild(QLineEdit,"depthtop").setText("0") 
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")

def stratigraphy_stratid_field_text_changed():
    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False): 
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")  

def stratigraphy_depthtop_field_text_changed():
    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")

    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  

def stratigraphy_depthbot_field_text_changed():
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")  

def w_flow_obsid_field_text_changed():
    if not obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_flow'):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def w_flow_date_time_field_text_changed():
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"date_time").text()) ==0) or utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False: 
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def w_flow_instrumentid_field_text_changed():
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"instrumentid").text()) ==0): 
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")        

def w_flow_flowtype_field_text_changed():
    if not flowtype_exists(myDialog.findChild(QLineEdit,"flowtype").text(),'w_flow'): 
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")        

def w_flow_reading_field_text_changed():
    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")  
        
def w_flow_unit_field_text_changed():
    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"unit").text()) ==0):
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("") 

def w_levels_obsid_field_text_changed():
    if not obsid_exists(myDialog.findChild(QLineEdit,"obsid").text(),'w_levels'):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def w_levels_date_time_field_text_changed():
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def w_levels_level_masl_field_text_changed():
    if (myDialog.findChild(QLineEdit,"level_masl").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"level_masl").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False): 
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")        
