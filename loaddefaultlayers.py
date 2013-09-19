# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that (removes) and loads default qgis layers for the selected database. 
                              -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt libraries
from PyQt4.QtCore import *  
from PyQt4.QtGui import *  
from qgis.core import *   # Necessary for the QgsFeature()
from qgis.gui import *
import qgis.utils
import os
import locale
import midvatten_utils as utils
from definitions import midvatten_defs as defs

class loadlayers():        
    def __init__(self, iface, settingsdict={}):
        self.settingsdict = settingsdict
        self.default_layers =  defs.default_layers() 
        self.default_nonspatlayers = defs.default_nonspatlayers()
        self.iface = iface
        self.legend = self.iface.legendInterface()
        self.removelayers()
        self.addlayers()

    def removelayers(self):
        """ FIRST search for and try to remove old layers """
        ALL_LAYERS = self.iface.mapCanvas().layers() 
        for lyr in ALL_LAYERS:         
            name = lyr.name()
            if (name in self.default_layers) or (name in self.default_nonspatlayers):
                QgsMapLayerRegistry.instance().removeMapLayers( [lyr.id()] )
                
        """ THEN remove old group """
        while 'Midvatten_OBS_DB' in self.legend.groups():
            group_index = self.legend.groups().index('Midvatten_OBS_DB') 
            self.legend.removeGroup(group_index)

    def addlayers(self):
        try:    #newstyle
            MyGroup = self.legend.addGroup ("Midvatten_OBS_DB",1,-1)
        except: #olddstyle
            MyGroup = self.legend.addGroup ("Midvatten_OBS_DB")
        uri = QgsDataSourceURI()
        uri.setDatabase(self.settingsdict['database'])#MacOSX fix1 #earlier sent byte string, now intending to send unicode string
        for tablename in self.default_nonspatlayers:    # first the non-spatial tables, THEY DO NOT ALL HAVE CUSTOM UI FORMS
            firststring= 'dbname="' + self.settingsdict['database'] + '" table="' + tablename + '"'#MacOSX fix1  #earlier sent byte string, now unicode
            layer = QgsVectorLayer(firststring,tablename, 'spatialite')   # Adding the layer as 'spatialite' and not ogr vector layer is preferred
            if not layer.isValid():
                utils.pop_up_info("failed to load layer " + tablename) #debugging
            else:
                QgsMapLayerRegistry.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB') 
                self.legend.moveLayer (self.legend.layers()[0],group_index)
                if tablename in ('w_levels','w_flow','stratigraphy'):
                    filename = tablename + ".qml"       #  load styles
                    stylefile = os.path.join(os.sep,os.path.dirname(__file__),"definitions",filename)
                    layer.loadNamedStyle(stylefile)
                    if  locale.getdefaultlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
                        filename = tablename + ".ui"
                    else:
                        filename = tablename + "_en.ui"
                    try: # python bindings for setEditorLayout were introduced in qgis-master commit 9183adce9f257a097fc54e5a8a700e4d494b2962 november 2012
                        layer.setEditorLayout(2)
                    except:
                        pass
                    uifile = os.path.join(os.sep,os.path.dirname(__file__),"ui",filename)
                    layer.setEditForm(uifile)
                    formlogic = tablename + "_form_logic.formOpen"     
                    layer.setEditFormInit(formlogic)
        for tablename in self.default_layers:    # then the spatial ones, NOT ALL HAVE CUSTOM UI FORMS
            uri.setDataSource('',tablename, 'Geometry')
            layer = QgsVectorLayer(uri.uri(), tablename, 'spatialite') # Adding the layer as 'spatialite' instead of ogr vector layer is preferred
            if not layer.isValid():
                utils.pop_up_info("failed to load layer " + tablename) #debugging
            else:
                filename = tablename + ".qml"
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"definitions",filename)
                layer.loadNamedStyle(stylefile)
                if tablename in defs.default_layers_w_ui():        #=   THE ONES WITH CUSTOM UI FORMS
                    if locale.getdefaultlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
                        filename = tablename + ".ui"
                    else:
                        filename = tablename + "_en.ui"
                    uifile = os.path.join(os.sep,os.path.dirname(__file__),"ui",filename)
                    try: # python bindings for setEditorLayout were introduced in qgis-master commit 9183adce9f257a097fc54e5a8a700e4d494b2962 november 2012
                        layer.setEditorLayout(2)  
                    except:
                        pass
                    layer.setEditForm(uifile)
                    if tablename in ('obs_points','obs_lines'):
                        formlogic = tablename + "_form_logic.formOpen"      
                        layer.setEditFormInit(formlogic)     
                QgsMapLayerRegistry.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB')   # SIPAPI UPDATE 2.0
                self.legend.moveLayer (self.legend.layers()[0],group_index)
                if tablename == 'obs_points':#zoom to obs_points extent
                    qgis.utils.iface.mapCanvas().setExtent(layer.extent())
                elif tablename == 'w_lvls_last_geom':#we do not want w_lvls_last_geom to be visible by default
                    self.legend.setLayerVisible(layer,False)

    def getGroupIndex(self, iface, groupName):      #This function only due to old limitations in qgis version <1.9.0-65  No longer used!!
        relationList = iface.legendInterface().groupLayerRelationship()
        i = 0
        for item in relationList:
            if item[0] == groupName:
                return i
            i = i + 1
        return 0
