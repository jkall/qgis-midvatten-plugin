# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import qgis.utils # for error/debug messages to messagebar

myDialog = None

def formOpen(dialog,layerid,featureid):
    global myDialog        #
    myDialog = dialog

    if obsidexists(myDialog.findChild(QLineEdit,"obsid").text()):#if it is an obsid which already exists in database, then no particular highlightning
         myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:#If not empty nor null and obsid not in db - then it must be a new one, not yet saved
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        #utils.pop_up_info("obsid is not null nor empty - but it also is not in db!")#debug

    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def validate():  # Make sure mandatory fields are not empty.
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0): 
        utils.pop_up_info("obsid must not be empty!")
    elif myDialog.findChild(QLineEdit,"obsid").text()=='NULL':
        utils.pop_up_info("obsid must not be NULL!")
    else:
        # make sure flowtype is within allowed data domain
        myDialog.accept()

def obsidexists(obsid):  # Both to see if a new obsid already exists in database.
    sql = r"""SELECT obsid FROM obs_lines where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'

        
def obsid_FieldTextChanged():
    #qgis.utils.iface.messageBar().pushMessage("Debug",myDialog.findChild(QLineEdit,"obsid").text(),0)#debug
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or len(myDialog.findChild(QLineEdit,"obsid").text()) ==0:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    elif obsidexists(myDialog.findChild(QLineEdit,"obsid").text()):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
        qgis.utils.iface.messageBar().pushMessage("Warning",myDialog.findChild(QLineEdit,"obsid").text()+" alredy exists!",1)
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
