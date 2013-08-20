# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed

myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog

    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0)  or not (obsidexists(myDialog.findChild(QLineEdit,"obsid").text())): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    dialog.findChild(QLineEdit,"date_time").textChanged.connect(date_time_FieldTextChanged)
    
    if utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")
    dialog.findChild(QLineEdit,"level_masl").textChanged.connect(level_masl_FieldTextChanged)

    level_masl_field = dialog.findChild(QLineEdit,"level_masl")
    level_masl_field.setText("-999")
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def obsid_FieldTextChanged():
    if not obsidexists(myDialog.findChild(QLineEdit,"obsid").text()):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def date_time_FieldTextChanged():
    if utils.isdate(myDialog.findChild(QLineEdit,"date_time").text())==False:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def level_masl_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"level_masl").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"level_masl").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")        

def obsidexists(obsid):  # Check if obsid exists in database.
    sql = r"""SELECT obsid FROM obs_points where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)
    if len(result)>0:
        return 'True'
                
def validate():  # Make sure mandatory fields are not empty.
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"date_time").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"level_masl").text()) > 0): # SIP API UPDATE 2.0
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
