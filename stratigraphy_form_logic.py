# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import qgis.utils # for debug messages to messagebar
myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog
    myDialog = dialog
    obsid_FieldTextChanged()
    
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsidexists(myDialog.findChild(QLineEdit,"obsid").text())):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False):
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")
    dialog.findChild(QLineEdit,"stratid").textChanged.connect(stratid_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  
    dialog.findChild(QLineEdit,"depthtop").textChanged.connect(depthtop_FieldTextChanged)
        
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")     
    dialog.findChild(QLineEdit,"depthbot").textChanged.connect(depthbot_FieldTextChanged)
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def obsid_FieldTextChanged():#whenever a new obsid is given, then preset stratid to next number and preset depthtop to latest depthbot.
    """ Must find another trigger: new feature/object/record!"""
    """ no no, just check if stratid field is empty, then it is considered a new feature and a default value should be added!!"""
    if obsidexists(myDialog.findChild(QLineEdit,"obsid").text()) and (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0): #if stratid is empty, then it is considered to be a new record and preset values should be suggested, otherwise, do not suggest anything!
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
        sql = r"""select max(stratid) from stratigraphy WHERE obsid = '"""
        sql += myDialog.findChild(QLineEdit,"obsid").text()
        sql += r"""'"""
        maxstratid = utils.sql_load_fr_db(sql)
        if utils.isinteger(str(maxstratid[0][0]).encode('utf-8'))==True:
            myDialog.findChild(QLineEdit,"stratid").setText(str(int(maxstratid[0][0])+1)) #form stratid is preset to max(stratid) + 1 in db
            sql = r"""select max(depthbot) from stratigraphy WHERE obsid = '"""
            sql +=myDialog.findChild(QLineEdit,"obsid").text()
            sql += r"""'"""
            maxdepthbot = utils.sql_load_fr_db(sql)
            if utils.isfloat(str(maxdepthbot[0][0]).encode('utf-8'))==True:
                myDialog.findChild(QLineEdit,"depthtop").setText(str(maxdepthbot[0][0])) #form depthtop is preset to max(depthbot) in db
        else:
            myDialog.findChild(QLineEdit,"stratid").setText("1")
            myDialog.findChild(QLineEdit,"depthtop").setText("0") 
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")

def stratid_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False): 
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")  

def depthtop_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")

    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  

def depthbot_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")  

def obsidexists(obsid):  # Check if obsid exists in database.
    sql = r"""SELECT obsid FROM obs_points where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)
    if len(result)>0:
        return 'True'
                
def validate():  # Make sure mandatory fields are not empty.
    if not (obsidexists(myDialog.findChild(QLineEdit,"obsid").text())):
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
