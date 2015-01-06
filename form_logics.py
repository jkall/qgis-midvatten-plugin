# -*- coding: utf-8 -*-
"""
/***************************************************************************

------>This module is not ready but only a framework for future development<-----------
------>Those functions that do exist are not working correctly<-------------------

 This is the part of the Midvatten plugin that includes som logics for the
 custom user forms.

                              -------------------
        begin                : 2015-01-05
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsFeature

from sqlite3 import dbapi2 as sqlite
import midvatten_utils as utils# Whenever some global midvatten_utilities are needed
import qgis.utils # for error/debug messages to messagebar
#global variables, layers and dialogs must be specific for each form
myDialog = None
myLayer = None
myObsPDialog = None
myObsPLayer = None
myStratDialog = None
myStratLayer = None
myWFlowDialog = None
myWFlowLayer = None
myWLevelsDialog = None
myWLevelsLayer = None

"""
Memo:

These signals were used in plugin < 1.1. (for qgis < 2.4) but they cause problems nowadays with attribute table dual view and some other changes in qgis:
    # Disconnect the signal that QGIS has wired up for the dialog to the button box.
    buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")
    buttonBox.accepted.disconnect(myDialog.accept)

    # Wire up our own signals.
    buttonBox.accepted.connect(validate)
    buttonBox.rejected.connect(myDialog.reject)
    dialog.findChild(QLineEdit,"obsid").textChanged.connect(obsid_FieldTextChanged)

These are the useful signals for plugin >=1.1 (qgis >=2.4):
    myDialog.attributeChanged.connect(obsid_duplicates)
    myLayer.featureAdded.connect(obs_added)
    myLayer.beforeCommitChanges.connect(before_layer_commit_change)
    
"""
#form open functions
def obs_lines_form_open(dialog,the_layer,the_feature):#dummy
    pass
    
def obs_points_form_open(dialog,the_layer,the_feature):#just trying to keep some of the old form logics
    global myObsPDialog, myObsPLayer
    myObsPDialog = dialog
    #myObsPLayer = the_layer
    try:#if it is an old form with a CRS label field, then update CRS label field and also try to update check boxes etc
        sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
        result = utils.sql_load_fr_db(sql)[1]
        CRS_field = myObsPDialog.findChild(QLabel,"CRS")
        CRS_field.setText("EPSG:" + str(result[0][0]))
        if obsid_exists(myObsPDialog.findChild(QLineEdit,"obsid").text(),'obs_points'):#if it is an obsid which already exists in database, then fill wmeas_yn and wlogg_yn fields
            sql = r"""SELECT wmeas_yn FROM obs_points where obsid = '"""
            sql += myObsPDialog.findChild(QLineEdit,"obsid").text()
            sql += """'"""
            result = utils.sql_load_fr_db(sql)[1]
            if result:
                if str(result[0][0]) == '1':
                    wmeas_yn_field = dialog.findChild(QCheckBox,"wmeas_yn")
                    wmeas_yn_field.setChecked(True)
            sql = r"""SELECT wlogg_yn FROM obs_points where obsid = '"""
            sql += myObsPDialog.findChild(QLineEdit,"obsid").text()
            sql += """'"""
            result = utils.sql_load_fr_db(sql)[1]
            if str(result[0][0]) == '1':
                wlogg_yn_field = dialog.findChild(QCheckBox,"wlogg_yn")
                wlogg_yn_field.setChecked(True)
    except:
        pass

def obs_p_w_lvl_form_open(dialog,the_layer,the_feature):#dummy
    pass

def obs_p_w_qual_lab_form_open(dialog,the_layer,the_feature):#dummy
    pass

def obs_p_w_qual_field_form_open(dialog,the_layer,the_feature):#dummy
    pass

def obs_p_w_strat_form_open(dialog,the_layer,the_feature):#dummy
    pass

def stratigraphy_form_open(dialog,the_layer,the_feature):#not ready and not working
    global myStratDialog, myStratLayer
    myStratDialog = dialog
    myStratLayer = the_layer
    """
    try:#force a check of some attributes since this is not done automatically when form opened
        myStratDialog, myStratLayer = check_and_color_QLineEdit(myStratDialog, myStratLayer,'obsid',the_feature.attributes()[the_layer.fieldNameIndex('obsid')])
        myStratDialog, myStratLayer = check_and_color_QLineEdit(myStratDialog, myStratLayer,'stratid',the_feature.attributes()[the_layer.fieldNameIndex('stratid')])
        myStratDialog, myStratLayer = check_and_color_QLineEdit(myStratDialog, myStratLayer,'depthtop',the_feature.attributes()[the_layer.fieldNameIndex('depthtop')])
        myStratDialog, myStratLayer = check_and_color_QLineEdit(myStratDialog, myStratLayer,'depthbot',the_feature.attributes()[the_layer.fieldNameIndex('depthbot')])
    except:
        print('failed to check some stratigraphy attributes')#debug
    """
    myStratDialog.attributeChanged.connect(strat_attr_changed)

def w_flow_form_open(dialog,the_layer,the_feature):#not ready and not working
    global myWFlowDialog, myWFlowLayer
    myWFlowDialog = dialog
    myWFlowLayer = the_layer
    """
    try:#force a some checks since this is not done automatically when form opened
        myWFlowDialog, myWFlowLayer = check_and_color_QLineEdit(myWFlowDialog, myWFlowLayer,'obsid',the_feature.attributes()[the_layer.fieldNameIndex('obsid')])
        myWFlowDialog, myWFlowLayer = check_and_color_QLineEdit(myWFlowDialog, myWFlowLayer,'instrumentid',the_feature.attributes()[the_layer.fieldNameIndex('instrumentid')])
        myWFlowDialog, myWFlowLayer = check_and_color_QLineEdit(myWFlowDialog, myWFlowLayer,'reading',the_feature.attributes()[the_layer.fieldNameIndex('reading')])
        myWFlowDialog, myWFlowLayer = check_and_color_QLineEdit(myWFlowDialog, myWFlowLayer,'flowtype',the_feature.attributes()[the_layer.fieldNameIndex('flowtype')])
        myWFlowDialog, myWFlowLayer = check_and_color_QLineEdit(myWFlowDialog, myWFlowLayer,'unit',the_feature.attributes()[the_layer.fieldNameIndex('unit')])
    except:
        print('failed to check some w_flow attributes')#debug
    """
    myWFlowDialog.attributeChanged.connect(w_flow_attr_changed)

def w_levels_form_open(dialog,the_layer,the_feature):#not ready and not working
    global myWLevelsDialog, myWLevelsLayer
    myWLevelsDialog = dialog
    myWLevelsLayer = the_layer
    """
    try:#force a some checks since this is not done automatically when form opened
        myWLevelsDialog, myWLevelsLayer = check_and_color_QLineEdit(myWLevelsDialog, myWLevelsLayer,'obsid',the_feature.attributes()[the_layer.fieldNameIndex('obsid')])
    except:
        print('failed to check some w_level attributes')#debug
    """
    myWLevelsDialog.attributeChanged.connect(w_levels_attr_changed)

def w_lvls_last_geom_form_open(dialog,the_layer,the_feature):#dummy
    pass

def w_qual_field_form_open(dialog,the_layer,the_feature):#dummy
    pass

def w_qual_lab_form_open(dialog,the_layer,the_feature):#dummy
    pass


#various helper functions called from the form open inits
#helper functions for stratigraphy form
def strat_attr_changed(attr,value):#background is set red if values do not fulfill simple validity checks
    attribute_name_string = attr.lower()
    try:
        myStratDialog, myStratLayer = check_and_color_QLineEdit(myStratDialog, myStratLayer,attribute_name_string,value)
        return myStratDialog, myStratLayer
    except:
        return False

def w_flow_attr_changed(attr,value):#background is set red if values do not fulfill simple validity checks
    attribute_name_string = attr.lower()
    attr_value = value
    try:
        myWFlowDialog, myWFlowLayer = check_and_color_QLineEdit(myWFlowDialog, myWFlowLayer,attribute_name_string,attr_value)
    except:
        pass
def w_levels_attr_changed(attr,value):#background is set red if values do not fulfill simple validity checks
    attribute_name_string = attr.lower()
    attr_value = value
    try:
        myWLevelsDialog, myWLevelsLayer = check_and_color_QLineEdit(myWLevelsDialog, myWLevelsLayer,attribute_name_string,attr_value)
    except:
        pass

def check_and_color_QLineEdit(dialog, layer,attribute_name_string,attr_value):#this is a common function, called by different form_open with corresponding attr_changed
    style_error ="background-color: rgba(255, 107, 107, 150);"
    style_ok = ""
    if attribute_name_string == "obsid":#bg color for field obsid - if obsid exists in db or not
        #if obsid_exists(myWFlowDialog.findChild(QLineEdit,"obsid").text(),'obs_points'):
        if obsid_exists(attr_value,'obs_points'):
            dialog.findChild(QLineEdit,"obsid").setStyleSheet(style_ok)
        #elif (not(myWFlowDialog.findChild(QLineEdit,"obsid").text())) or (myWFlowDialog.findChild(QLineEdit,"obsid").text()=='NULL') or (len(myWFlowDialog.findChild(QLineEdit,"obsid").text()) == 0):#red bg if obsid not set
        elif not(attr_value) or (attr_value=='NULL') or (len(attr_value) == 0):#red bg if obsid not set
            dialog.findChild(QLineEdit,"obsid").setStyleSheet(style_error)
        else:#If obsid not in db - then it must be a new one, not yet saved - so background is set red
            dialog.findChild(QLineEdit,"obsid").setStyleSheet(style_error)
    elif attribute_name_string in ("depthtop","depth to top of layer","från djup under my (m)"):
        lang=''
        style_sheet_top = style_error#pessimistic approach
        style_sheet_bot = 'none'
        if utils.isfloat(dialog.findChild(QLineEdit,attribute_name_string).text())==False:#if depthtop is not float
            style_sheet_top = style_error
        else:
            #first just get the depthbotstring and find what language is used for the forms
            try:
                depthbotstring = dialog.findChild(QLineEdit,"till djup under my (m)").text()
                lang = 'sv'
            except:
                lang = 'eng'
                try:
                    depthbotstring = dialog.findChild(QLineEdit,"depthbot").text()
                except:
                    depthbotstring = dialog.findChild(QLineEdit,"depth to bottom of layer").text()
            #then try to convert also depthbotstring to float and make comparison to se if depthtop<depthbot
            try:
                dbot = float(depthbotstring)
                if not  (float(dialog.findChild(QLineEdit,attribute_name_string).text()) < float(dbot)):
                    style_sheet_top=style_error
                    style_sheet_bot=style_error
                else:
                    style_sheet_top=""
                    style_sheet_bot=""
            except:#if depthbot is not float
                style_sheet_top=""
                style_sheet_bot=style_error
        #finally apply the stylesheets
        dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_sheet_top)#set depthtop depending on depthtop-depthbot relation
        if style_sheet_bot !='none':
            if lang == 'sv':
                dialog.findChild(QLineEdit,"till djup under my (m)").setStyleSheet(style_sheet_bot)
            elif lang =='eng':
                try:
                    dialog.findChild(QLineEdit,"depthbot").setStyleSheet(style_sheet_bot)
                except:
                    dialog.findChild(QLineEdit,"depth to bottom of layer").setStyleSheet(style_sheet)
    elif attribute_name_string in ("depthbot","depth to bottom of layer","till djup under my (m)"):
        lang=''
        style_sheet_top = 'none'
        style_sheet_bot = style_error#pessimistic approach
        if utils.isfloat(dialog.findChild(QLineEdit,attribute_name_string).text())==False:#if depthbot is not float
            style_sheet_bot = style_error
        else:
            #first just get the depthtopstring and find what language is used for the forms
            try:
                depthtopstring = dialog.findChild(QLineEdit,"från djup under my (m)").text()
                lang = 'sv'
            except:
                lang = 'eng'
                try:
                    depthtopstring = dialog.findChild(QLineEdit,"depthtop").text()
                except:
                    depthtopstring = dialog.findChild(QLineEdit,"depth to top of layer").text()
            #then try to convert also depthbotstring to float and make comparison to se if depthtop<depthbot
            try:
                dtop = float(depthtopstring)
                if not  (float(dtop) < float(dialog.findChild(QLineEdit,attribute_name_string).text())):
                    style_sheet_top=style_error
                    style_sheet_bot=style_error
                else:
                    style_sheet_top=""
                    style_sheet_bot=""
            except:#if depthtop is not float
                style_sheet_top=style_error
                style_sheet_bot=""
        #finally apply the stylesheets
        dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_sheet_top)#set depthbot depending on depthtop-depthbot relation
        if style_sheet_top !='none':
            if lang == 'sv':
                dialog.findChild(QLineEdit,"från djup under my (m)").setStyleSheet(style_sheet_bot)
            elif lang =='eng':
                try:
                    dialog.findChild(QLineEdit,"depthtop").setStyleSheet(style_sheet_bot)
                except:
                    dialog.findChild(QLineEdit,"depth to top of layer").setStyleSheet(style_sheet)
    elif attribute_name_string in ("stratid", "lager nr"):
        if utils.isinteger(dialog.findChild(QLineEdit,attribute_name_string).text())==False:
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
        else:
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_ok)   
    elif attribute_name_string in ("flowtype","flödestyp"):
        if flowtype_exists(attr_value):
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_ok)
        elif not(attr_value) or (attr_value=='NULL') or (len(attr_value) == 0):
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
        else:#If flowtype not in db - then it must be a new one, not yet saved - so background is set red
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
    elif attribute_name_string in ("instrumentid"):
        if (attr_value=='NULL') or (len(attr_value) == 0):
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
        else:
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
    elif attribute_name_string in ("reading","reading, num","reading_num","reading, numerical", "mätvärde numeriskt"):
        if not(attr_value) or (attr_value=='NULL') or (len(attr_value) == 0) or (not utils.isfloat(attr_value)):
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
        else:
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
    elif attribute_name_string in ("unit", "enhet"):
        if not(attr_value) or (attr_value=='NULL') or (len(attr_value) == 0):
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)
        else:
            dialog.findChild(QLineEdit,attribute_name_string).setStyleSheet(style_error)

    return dialog, layer

def obsid_exists(obsid, tablename):
    sql = r"""SELECT obsid FROM """ + tablename + """ where obsid = '""" + obsid + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'

def flowtype_exists(flowtype):
    sql = r"""SELECT type FROM zz_flowtype where type = '""" + flowtype + """'"""
    result = utils.sql_load_fr_db(sql)[1]
    if len(result)>0:
        return 'True'
