# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog, possibleobsids        
    myDialog = dialog
    possibleobsids = utils.sql_load_fr_db('select distinct obsid from obs_points')
    
    #stratid_field = dialog.findChild(QLineEdit,"stratid")
    #stratid_field.setText("1")
    #depthtop_FIELD = dialog.findChild(QLineEdit,"depthtop")
    #depthtop_FIELD.setText("0")
    #depthbot_FIELD = dialog.findChild(QLineEdit,"depthbot")
    #depthbot_FIELD.setText("0")

    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsidisok==1):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")
    dialog.findChild(QLineEdit,"stratid").textChanged.connect(stratid_FieldTextChanged)

    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  
    dialog.findChild(QLineEdit,"depthtop").textChanged.connect(depthtop_FieldTextChanged)
        
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):# SIP API UPDATE 2.0
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

def obsid_FieldTextChanged():
    obsidisok = 0
    for id in possibleobsids:
        if str(myDialog.findChild(QLineEdit,"obsid").text())==str(id[0]).encode('utf-8'):
            obsidisok= 1
            sql = r"""select max(stratid) from stratigraphy WHERE obsid = '"""
            sql += str(id[0]).encode('utf-8')
            sql += r"""'"""
            maxstratid = utils.sql_load_fr_db(sql)
            #utils.pop_up_info(str(maxstratid[0][0]).encode('utf-8'))   # DEBUGGING
            if utils.isinteger(str(maxstratid[0][0]).encode('utf-8'))==True:
                myDialog.findChild(QLineEdit,"stratid").setText(str(int(maxstratid[0][0])+1).encode('utf-8'))
                
                sql = r"""select max(depthbot) from stratigraphy WHERE obsid = '"""
                sql += str(id[0]).encode('utf-8')
                sql += r"""'"""
                maxdepthbot = utils.sql_load_fr_db(sql)
                #utils.pop_up_info(str(maxdepthbot[0][0]).encode('utf-8'))   # DEBUGGING
                if utils.isfloat(str(maxdepthbot[0][0]).encode('utf-8'))==True:
                    myDialog.findChild(QLineEdit,"depthtop").setText(str(maxdepthbot[0][0]).encode('utf-8'))                                   
            else:
                myDialog.findChild(QLineEdit,"stratid").setText("1")
                myDialog.findChild(QLineEdit,"depthtop").setText("0") 

    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) ==0) or not (obsidisok==1):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

def stratid_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"stratid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"stratid").text()) == 0) or (utils.isinteger(myDialog.findChild(QLineEdit,"stratid").text())==False): # SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"stratid").setStyleSheet("")  

def depthtop_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"depthtop").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthtop").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthtop").text())==False):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthtop").setStyleSheet("")  

def depthbot_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"depthbot").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"depthbot").text()) == 0) or (utils.isfloat(myDialog.findChild(QLineEdit,"depthbot").text())==False):# SIP API UPDATE 2.0
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"depthbot").setStyleSheet("")  
        
def validate():  # Make sure mandatory fields are not empty.
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"stratid").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"depthtop").text()) > 0 and 
            len(myDialog.findChild(QLineEdit,"depthbot").text()) > 0):# SIP API UPDATE 2.0
        utils.pop_up_info("obsid, stratid, depthtop and depthbot must not be empty!")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL' or
                myDialog.findChild(QLineEdit,"stratid").text()=='NULL' or 
                myDialog.findChild(QLineEdit,"depthtop").text()=='NULL' or 
                myDialog.findChild(QLineEdit,"depthbot").text()=='NULL'):
        utils.pop_up_info("obsid, stratid, depthtop and depthbot must not be NULL!")
    else:
        # Return the form as accpeted to QGIS.
        myDialog.accept()
