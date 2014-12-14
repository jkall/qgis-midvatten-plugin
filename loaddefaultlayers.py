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

from PyQt4.QtCore import *  
from PyQt4.QtGui import *  
from qgis.core import *  
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
        self.remove_layers()
        self.add_layers()

    def add_layers(self):
        """
        #if I ever choose to store layer_styles in the database, then this is the way to go:
        self.selection_layer_in_db_or_not()
        """
        self.add_layers_new_method()

    def add_layers_new_method(self):
        MyGroup = self.legend.addGroup ("Midvatten_OBS_DB",1,-1)
        uri = QgsDataSourceURI()
        uri.setDatabase(self.settingsdict['database'])

        layer_list = []
        map_canvas_layer_list=[]

        for tablename in self.default_nonspatlayers: #first load all non-spatial layers
            uristring= 'dbname="' + self.settingsdict['database'] + '" table="' + tablename + '"'
            layer = QgsVectorLayer(uristring,tablename, 'spatialite')
            layer_list.append(layer)

        for tablename in self.default_layers:    # then all the spatial ones
            uri.setDataSource('',tablename, 'Geometry')
            layer = QgsVectorLayer(uri.uri(), tablename, 'spatialite') # Adding the layer as 'spatialite' instead of ogr vector layer is preferred
            layer_list.append(layer)

        for layer in layer_list:#now loop over all the layers and set styles etc
            if not layer.isValid():
                print(layer.name() + ' is not valid layer')
                pass
            else:
                map_canvas_layer_list.append(QgsMapCanvasLayer(layer))

                QgsMapLayerRegistry.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB') 
                self.legend.moveLayer (self.legend.layers()[0],group_index)

                #preparing search paths for qml file and form logics
                layer.setEditorLayout(1)#perhaps this is unnecessary since it gets set from the loaded qml below?
                if  locale.getdefaultlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
                    filename = layer.name() + "_tablayout_sv.qml"
                    formlogic = "form_logics_sv." + layer.name() + "_form_open"
                else:
                    filename = layer.name() + "_tablayout.qml"
                    formlogic = "form_logics." + layer.name() + "_form_open"

                #now try to load the style file
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"definitions",filename)
                try:
                    layer.loadNamedStyle(stylefile)
                except:
                    pass
                #and then the form logics
                try:
                    layer.setEditFormInit(formlogic)
                except:
                    pass

                if layer.name() == 'obs_points':#zoom to obs_points extent
                    QgsMapCanvas().setExtent(layer.extent())
                elif layer.name() == 'w_lvls_last_geom':#we do not want w_lvls_last_geom to be visible by default
                    self.legend.setLayerVisible(layer,False)
                else:
                    pass

        
    def add_layers_old_method(self):
        """
        this method is depreceated and should no longer be used
        """
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
                qgis.utils.iface.messageBar().pushMessage("Error","""Failed to load layer %s!"""%tablename,2)
            else:
                QgsMapLayerRegistry.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB') 
                self.legend.moveLayer (self.legend.layers()[0],group_index)
                filename = tablename + ".qml"       #  load styles
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"definitions",filename)
                layer.loadNamedStyle(stylefile)
                if tablename in ('w_levels','w_flow','stratigraphy'):
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
                    formlogic = "form_logics." + tablename + "_form_open"
                    layer.setEditFormInit(formlogic)
        for tablename in self.default_layers:    # then the spatial ones, NOT ALL HAVE CUSTOM UI FORMS
            uri.setDataSource('',tablename, 'Geometry')
            layer = QgsVectorLayer(uri.uri(), tablename, 'spatialite') # Adding the layer as 'spatialite' instead of ogr vector layer is preferred
            if not layer.isValid():
                qgis.utils.iface.messageBar().pushMessage("Error","""Failed to load layer %s!"""%tablename,2)                
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
                        formlogic = "form_logics." + tablename + "_form_open"
                        layer.setEditFormInit(formlogic)     
                QgsMapLayerRegistry.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB')   # SIPAPI UPDATE 2.0
                self.legend.moveLayer (self.legend.layers()[0],group_index)
                if tablename == 'obs_points':#zoom to obs_points extent
                    qgis.utils.iface.mapCanvas().setExtent(layer.extent())
                elif tablename == 'w_lvls_last_geom':#we do not want w_lvls_last_geom to be visible by default
                    self.legend.setLayerVisible(layer,False)

    def remove_layers(self):
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

    def selection_layer_in_db_or_not(self): #this is not used, it might be if using layer_styles stored in the db
        sql = r"""select name from sqlite_master where name = 'layer_styles'"""
        result = utils.sql_load_fr_db(sql)[1]
        if len(result)==0:#if it is an old database w/o styles
            update_db = utils.askuser("YesNo","""Your database was created with plugin version < 1.1 when layer styles were not stored in the database. You can update this database to the new standard with layer styles (symbols, colors, labels, input forms etc) stored in the database. This will increase plugin stability and multi-user experience but it will also change the layout of all your forms for entering data into the database. Anyway, an update of the database is recommended. Do you want to add these layer styles now?""",'Update database with layer styles?')
            if update_db.result == 1:
                from create_db import AddLayerStyles
                AddLayerStyles(self.settingsdict['database'])
                self.add_layers_new_method()
            else:
                self.add_layers_old_method()
        else:
            self.add_layers_new_method()
