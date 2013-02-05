# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
#from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed

myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog, possibleflowtypes, possibleobsids        #
    myDialog = dialog
    possibleflowtypes = utils.sql_load_fr_db('select distinct type from zz_flowtype')
    possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points')
    
    #reading_FIELD = dialog.findChild(QLineEdit,"reading")
    #reading_FIELD.setText("0")
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (myDialog.findChild(QLineEdit,"obsid").text().length() == 0):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (myDialog.findChild(QLineEdit,"date_time").text().length() == 0):
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")
    dialog.findChild(QLineEdit,"date_time").textChanged.connect(date_time_FieldTextChanged)
    
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (myDialog.findChild(QLineEdit,"instrumentid").text().length() == 0):
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")
    dialog.findChild(QLineEdit,"instrumentid").textChanged.connect(instrumentid_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"flowtype").text()=='NULL') or (myDialog.findChild(QLineEdit,"flowtype").text().length() == 0):
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")
    dialog.findChild(QLineEdit,"flowtype").textChanged.connect(flowtype_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (myDialog.findChild(QLineEdit,"reading").text().length() == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")
    dialog.findChild(QLineEdit,"reading").textChanged.connect(reading_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (myDialog.findChild(QLineEdit,"unit").text().length() == 0):
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("")
    dialog.findChild(QLineEdit,"unit").textChanged.connect(unit_FieldTextChanged)
    
    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def obsid_FieldTextChanged():
    obsidisok = 0
    for id in possibleobsids:
            if str(myDialog.findChild(QLineEdit,"obsid").text())==str(id[0]).encode('utf-8'):
                obsidisok= 1
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (myDialog.findChild(QLineEdit,"obsid").text().length() ==0) or not (obsidisok==1):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def date_time_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"date_time").text()=='NULL') or (myDialog.findChild(QLineEdit,"date_time").text().length() ==0):
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"date_time").setStyleSheet("")        

def instrumentid_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL') or (myDialog.findChild(QLineEdit,"instrumentid").text().length() ==0):
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"instrumentid").setStyleSheet("")        

def flowtype_FieldTextChanged():
    typeisok = 0
    for type in possibleflowtypes:
            if str(myDialog.findChild(QLineEdit,"flowtype").text())==str(type[0]).encode('utf-8'):
                typeisok= 1
    if (myDialog.findChild(QLineEdit,"flowtype").text()=='NULL') or (myDialog.findChild(QLineEdit,"flowtype").text().length() ==0) or not (typeisok==1):
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"flowtype").setStyleSheet("")        

def reading_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"reading").text()=='NULL') or (myDialog.findChild(QLineEdit,"reading").text().length() == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"reading").text())==False):
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"reading").setStyleSheet("")  
        

def unit_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"unit").text()=='NULL') or (myDialog.findChild(QLineEdit,"unit").text().length() ==0):
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"unit").setStyleSheet("") 
        
def validate():  # Make sure mandatory fields are not empty.
    if not (myDialog.findChild(QLineEdit,"obsid").text().length() > 0 and 
            myDialog.findChild(QLineEdit,"instrumentid").text().length() > 0 and 
            myDialog.findChild(QLineEdit,"flowtype").text().length() > 0 and 
            myDialog.findChild(QLineEdit,"date_time").text().length() > 0 and 
            myDialog.findChild(QLineEdit,"reading").text().length() > 0 and
            myDialog.findChild(QLineEdit,"unit").text().length() > 0):
        utils.pop_up_info("obsid, instrumentid, flowtype, date_time, reading and unit must not be empty!")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"instrumentid").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"flowtype").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"date_time").text()=='NULL' or 
            myDialog.findChild(QLineEdit,"reading").text()=='NULL' or
            myDialog.findChild(QLineEdit,"unit").text()=='NULL'):
        utils.pop_up_info("obsid, instrumentid, flowtype, date_time, reading and unit must not be NULL!")
    else:
        # make sure flowtype is within allowed data domain
        for type in possibleflowtypes:
            #utils.pop_up_info(str(myDialog.findChild(QLineEdit,"flowtype").text())) #debugging
            #utils.pop_up_info(str(type[0]).encode('utf-8')) #debugging
            if str(myDialog.findChild(QLineEdit,"flowtype").text())==str(type[0]).encode('utf-8'):
                # Return the form as accpeted to QGIS.
                #utils.pop_up_info("yes")    #debugging
                myDialog.accept()