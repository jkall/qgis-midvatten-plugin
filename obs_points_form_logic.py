# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils        # Whenever some global midvatten_utilities are needed

myDialog = None

def formOpen(dialog,layerid,featureid):
    sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
    result = utils.sql_load_fr_db(sql)
    CRS_field = dialog.findChild(QLabel,"CRS")
    CRS_field.setText("EPSG:" + str(result[0][0]))

    global myDialog        
    myDialog = dialog

    if not(myDialog.findChild(QLineEdit,"obsid").text()=='NULL'):
        sql = r"""SELECT wmeas_yn FROM obs_points where obsid = '"""
        sql += myDialog.findChild(QLineEdit,"obsid").text()
        sql += """'"""
        result = utils.sql_load_fr_db(sql)
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
    
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (myDialog.findChild(QLineEdit,"obsid").text().length() == 0):
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)
    
    #    myDialog.findChild(QLineEdit,"h_gs").setStyleSheet("background-color: rgba(255, 107, 107, 150);")


    #if (myDialog.findChild(QLineEdit,"h_gs").text()=='NULL') or (myDialog.findChild(QLineEdit,"h_gs").text().length() == 0) or utils.isfloat(myDialog.findChild(QLineEdit,"h_gs").text())==False:
    #    myDialog.findChild(QLineEdit,"h_gs").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    #else:
    #    myDialog.findChild(QLineEdit,"h_gs").setStyleSheet("")
    #dialog.findChild(QLineEdit,"h_gs").textChanged.connect(h_gs_FieldTextChanged)
    
    #h_gs_field = dialog.findChild(QLineEdit,"h_gs")        # Does not work as expected when viewing feature form
    #h_gs_field.setText("0")
    
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)

def validate():  # Make sure mandatory fields are not empty.
    if not (myDialog.findChild(QLineEdit,"obsid").text().length() > 0): # If obsid is empty
        utils.pop_up_info("obsid must not be empty!")
    elif myDialog.findChild(QLineEdit,"obsid").text()=='NULL': # or myDialog.findChild(QLineEdit,"h_gs").text()=='NULL'):
        utils.pop_up_info("obsid must not be NULL!")
#    elif (myDialog.findChild(QLineEdit,"h_gs").text().length() == 0) or utils.isfloat(myDialog.findChild(QLineEdit,"h_gs").text())==False: #If h_gs is empty or non-real number
#        sanity = utils.askuser("YesNo","h_gs must be real number!\nSet h_gs=0?")
#        if sanity.result == 1:
#            h_gs_field = myDialog.findChild(QLineEdit,"h_gs")
#            h_gs_field.setText("0")
#            #utils.pop_up_info("user accepted") #debugging
    else:
        # Return the form as accpeted to QGIS.
        myDialog.accept()
        

def obsid_FieldTextChanged():
    if (myDialog.findChild(QLineEdit,"obsid").text()=='NULL') or myDialog.findChild(QLineEdit,"obsid").text().length() ==0:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
    else:
        myDialog.findChild(QLineEdit,"obsid").setStyleSheet("")

#def h_gs_FieldTextChanged():
#    if (myDialog.findChild(QLineEdit,"h_gs").text()=='NULL') or myDialog.findChild(QLineEdit,"h_gs").text().length() ==0 or utils.isfloat(myDialog.findChild(QLineEdit,"h_gs").text())==False:
#        myDialog.findChild(QLineEdit,"h_gs").setStyleSheet("background-color: rgba(255, 107, 107, 150);")
#    else:
#        myDialog.findChild(QLineEdit,"h_gs").setStyleSheet("")