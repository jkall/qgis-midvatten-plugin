# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed

myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog, possibleobsids        #
    myDialog = dialog
    possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points')        
    #global level_masl_field # Not necessary since level_masl only used within this single function
    #obsid_field = dialog.findChild(QLineEdit,"obsid")
    #obsid_field.setText("Unique ID")

    #date_time_field = dialog.findChild(QLineEdit,"date_time")
    #date_time_field.setText("yyyy-mm-dd hh:mm:ss")

    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"date_time").text()) == 0):  # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    dialog.findChild(QLineEdit,"date_time").textChanged.connect(date_time_FieldTextChanged)
    
    if (myDialog.findChild(QLineEdit,"level_masl").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"level_masl").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False):
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
    obsidisok = 0
    for id in possibleobsids:
            if str(myDialog.findChild(QLineEdit,"obsid").text())==str(id[0]).encode('utf-8'):
                obsidisok= 1
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsidisok==1): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def date_time_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"date_time").text()) ==0): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def level_masl_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"level_masl").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"level_masl").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"level_masl").text())==False): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"level_masl").setStyleSheet("")        

def validate():  # Make sure mandatory fields are not empty.
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"date_time").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"level_masl").text()) > 0): # SIP API UPDATE 2.0
        utils.pop_up_info("obsid, date_time and level_masl must not be empty!")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL' or
                myDialog.findChild(QLineEdit,"date_time").text()=='NULL' or 
                myDialog.findChild(QLineEdit,"level_masl").text()=='NULL'):
        utils.pop_up_info("obsid, date_time and level_masl must not be NULL!")
    else:
        # Return the form as accpeted to QGIS.
        myDialog.accept()
