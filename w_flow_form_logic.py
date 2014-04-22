# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed

myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsidexists(myDialog.findChild(QLineEdit,"obsid").text())):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    dialog.findChild(QLineEdit,"date_time").textChanged.connect(date_time_FieldTextChanged)
    
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"instrumentid").text()) == 0):
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")
    dialog.findChild(QLineEdit,"instrumentid").textChanged.connect(instrumentid_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"flowtype").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"flowtype").text()) == 0) or not (flowtypeexists(myDialog.findChild(QLineEdit,"flowtype").text())):
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")
    dialog.findChild(QLineEdit,"flowtype").textChanged.connect(flowtype_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False): 
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")
    dialog.findChild(QLineEdit,"reading").textChanged.connect(reading_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"unit").text()) == 0): 
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("")
    dialog.findChild(QLineEdit,"unit").textChanged.connect(unit_FieldTextChanged)
    
    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def obsid_FieldTextChanged():
    if not obsidexists(myDialog.findChild(QLineEdit,"obsid").text()):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def date_time_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"date_time").text()) ==0) or utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False: 
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def instrumentid_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"instrumentid").text()) ==0): 
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")        

def flowtype_FieldTextChanged():
    if not flowtypeexists(myDialog.findChild(QLineEdit,"flowtype").text()): 
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")        

def reading_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"reading").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")  
        
def unit_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"unit").text()) ==0):
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("") 

def obsidexists(obsid):  # Check if obsid exists in database.
    sql = r"""SELECT obsid FROM obs_points where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'
                
def flowtypeexists(flowtype):  # Check if obsid exists in database.
    sql = r"""SELECT type FROM zz_flowtype where type = '""" + flowtype + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'
                        
def validate():  # Make sure mandatory fields are not empty.

    if not (obsidexists(myDialog.findChild(QLineEdit,"obsid").text())):
        utils.pop_up_info("obsid must exist in database table obs_points!")
    elif utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        utils.pop_up_info("Invalid date!")
    elif not (flowtypeexists(myDialog.findChild(QLineEdit,"flowtype").text())):
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
