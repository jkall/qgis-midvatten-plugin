# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed
import qgis.utils # for error/debug messages to messagebar


myDialog = None

def formOpen(dialog,layerid,featureid):
    sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
    result = utils.sql_load_fr_db(sql)
    CRS_field = dialog.findChild(QLabel,"CRS")
    CRS_field.setText("EPSG:" + str(result[0][0]))

    global myDialog        
    myDialog = dialog

    if obsidexists(myDialog.findChild(QLineEdit,"obsid").text()):#if it is an obsid which already exists in database, then fill wmeas_yn and wlogg_yn fields
        sql = r"""SELECT wmeas_yn FROM obs_points where obsid = '"""
        sql += myDialog.findChild(QLineEdit,"obsid").text()
        sql += """'"""
        result = utils.sql_load_fr_db(sql)
        if result:
            if str(result[0][0]) == '1':
                wmeas_yn_field = dialog.findChild(QCheckBox,"wmeas_yn")
                wmeas_yn_field.setChecked(True)
        sql = r"""SELECT wlogg_yn FROM obs_points where obsid = '"""
        sql += myDialog.findChild(QLineEdit,"obsid").text()
        sql += """'"""
        result = utils.sql_load_fr_db(sql)
        if str(result[0][0]) == '1':
            wlogg_yn_field = dialog.findChild(QCheckBox,"wlogg_yn")
            wlogg_yn_field.setChecked(True)
    elif (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myDialog.findChild(QLineEdit,"obsid").text()) == 0):#RED bg if NULL or empty 
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
    if not (len(myDialog.findChild(QLineEdit,"obsid").text()) > 0): # If obsid is empty
        utils.pop_up_info("obsid must not be empty!")
    elif myDialog.findChild(QLineEdit,"obsid").text()=='NULL': # or myDialog.findChild(QLineEdit,"h_gs").text()=='NULL'):
        utils.pop_up_info("obsid must not be NULL!")
    else:
        myDialog.accept()# Return the form as accepted to QGIS.
        
def obsidexists(obsid):  # Both to see if a new obsid already exists in database but also, in case of opening form for an already exising obs_point, to see if form logics should load some data for the obsid.
    sql = r"""SELECT obsid FROM obs_points where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)
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
