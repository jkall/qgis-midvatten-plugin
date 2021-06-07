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
from __future__ import absolute_import

import os
from builtins import object

import qgis.utils
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer

from midvatten.definitions import midvatten_defs as defs
from midvatten.tools.utils import common_utils, db_utils, midvatten_utils
from midvatten.tools.utils.midvatten_utils import add_layers_to_list


class LoadLayers(object):
    def __init__(self, iface, settingsdict={},group_name='Midvatten_OBS_DB'):
        self.settingsdict = settingsdict
        self.group_name = group_name
        self.default_layers =  defs.get_subset_of_tables_fr_db(category='default_layers') 
        self.default_nonspatlayers = defs.get_subset_of_tables_fr_db(category='default_nonspatlayers')
        self.iface = iface
        self.root = QgsProject.instance().layerTreeRoot()
        self.remove_layers()
        self.add_layers()

    def add_layers(self):
        """
        #if I ever choose to store layer_styles in the database, then this is the way to go:
        self.selection_layer_in_db_or_not()
        """
        self.add_layers_new_method()

    def add_layers_new_method(self):
        if self.group_name == 'Midvatten_OBS_DB':
            position_index = 0
        else:
            position_index = 1
        MyGroup = qgis.core.QgsLayerTreeGroup(name=self.group_name, checked=True)
        self.root.insertChildNode(position_index, MyGroup)
        dbconnection = db_utils.DbConnectionManager()

        canvas = self.iface.mapCanvas()
        layer_list = []
        if self.group_name == 'Midvatten_OBS_DB':
            add_layers_to_list(layer_list, self.default_nonspatlayers, dbconnection=dbconnection)
            add_layers_to_list(layer_list, self.default_layers, geometrycolumn='geometry',
                               dbconnection=dbconnection)

        elif self.group_name == 'Midvatten_data_domains': #if self.group_name == 'Midvatten_data_domains':
            tables_columns = db_utils.tables_columns()
            d_domain_tables = [x for x in list(tables_columns.keys()) if x.startswith('zz_')]
            add_layers_to_list(layer_list, d_domain_tables, dbconnection=dbconnection)

        elif self.group_name == 'Midvatten_data_tables':
            data_tables = defs.data_tables()
            add_layers_to_list(layer_list, data_tables, dbconnection=dbconnection)

        #now loop over all the layers and set styles etc
        for layer in layer_list:
            # TODO: Made this a comment, but there might be some hidden feature thats still needed!
            #map_canvas_layer_list.append(QgsMapCanvasLayer(layer))

            QgsProject.instance().addMapLayers([layer],False)
            MyGroup.insertLayer(0,layer)
            #MyGroup.addLayer(layer)

            #TODO: Check if this isn't needed.
            #if self.group_name == 'Midvatten_OBS_DB':
            #    layer.setEditorLayout(1) #perhaps this is unnecessary since it gets set from the loaded qml below?

            #now try to load the style file
            stylefile_sv = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",layer.name() + "_sv.qml")
            stylefile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",layer.name() + ".qml")
            if  midvatten_utils.getcurrentlocale()[0] == 'sv_SE' and os.path.isfile( stylefile_sv ): #swedish forms are loaded only if locale settings indicate sweden
                try:
                    layer.loadNamedStyle(stylefile_sv)
                except:
                    try:
                        layer.loadNamedStyle(stylefile)
                    except:
                        pass
            else:
                try:
                    layer.loadNamedStyle(stylefile)
                except:
                    pass

            if layer.name() == 'obs_points':#zoom to obs_points extent
                obsp_lyr = layer
                canvas.setExtent(layer.extent())
            elif layer.name() in ('w_lvls_last_geom', 'obs_p_w_lvl_logger'):
                MyGroup.findLayer(layer).setItemVisibilityCheckedRecursive(False)

        #finally refresh canvas
        dbconnection.closedb()
        canvas.refresh()

    def remove_layers(self):
        remove_group = self.root.findGroup(self.group_name)
        self.root.removeChildNode(remove_group)

    def add_layers_old_method(self):
        """
        this method is depreceated and should no longer be used
        """
        try:    #newstyle
            MyGroup = self.legend.addGroup ("Midvatten_OBS_DB",1,-1)
        except: #olddstyle
            MyGroup = self.legend.addGroup ("Midvatten_OBS_DB")
        uri = QgsDataSourceUri()
        uri.setDatabase(self.settingsdict['database'])#MacOSX fix1 #earlier sent byte string, now intending to send unicode string
        for tablename in self.default_nonspatlayers:    # first the non-spatial tables, THEY DO NOT ALL HAVE CUSTOM UI FORMS
            firststring= 'dbname="' + self.settingsdict['database'] + '" table="' + tablename + '"'#MacOSX fix1  #earlier sent byte string, now unicode
            layer = QgsVectorLayer(firststring,self.dbtype)   # Adding the layer as 'spatialite' and not ogr vector layer is preferred
            if not layer.isValid():
                common_utils.MessagebarAndLog.critical(bar_msg='Error, Failed to load layer %s!' % tablename)
            else:
                QgsProject.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB')
                self.legend.moveLayer (self.legend.layers()[0],group_index)
                filename = tablename + ".qml"       #  load styles
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filename)
                layer.loadNamedStyle(stylefile)
                if tablename in ('w_levels','w_flow','stratigraphy'):
                    if  midvatten_utils.getcurrentlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
                        filename = tablename + ".ui"
                    else:
                        filename = tablename + "_en.ui"
                    try: # python bindings for setEditorLayout were introduced in qgis-master commit 9183adce9f257a097fc54e5a8a700e4d494b2962 november 2012
                        layer.setEditorLayout(2)
                    except:
                        pass
                    uifile = os.path.join(os.sep,os.path.dirname(__file__),"..","ui",filename)
                    layer.setEditForm(uifile)
                    formlogic = "form_logics." + tablename + "_form_open"
                    layer.setEditFormInit(formlogic)
        for tablename in self.default_layers:    # then the spatial ones, NOT ALL HAVE CUSTOM UI FORMS
            uri.setDataSource('',tablename, 'Geometry')
            layer = QgsVectorLayer(uri.uri(), self.dbtype) # Adding the layer as 'spatialite' instead of ogr vector layer is preferred
            if not layer.isValid():
                common_utils.MessagebarAndLog.critical(bar_msg='Error, Failed to load layer %s!' % tablename)
            else:
                filename = tablename + ".qml"
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",filename)
                layer.loadNamedStyle(stylefile)
                if tablename in defs.get_subset_of_tables_fr_db(category='default_layers_w_ui'):        #=   THE ONES WITH CUSTOM UI FORMS
                    if midvatten_utils.getcurrentlocale()[0] == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
                        filename = tablename + ".ui"
                    else:
                        filename = tablename + "_en.ui"
                    uifile = os.path.join(os.sep,os.path.dirname(__file__),"..","ui",filename)
                    try: # python bindings for setEditorLayout were introduced in qgis-master commit 9183adce9f257a097fc54e5a8a700e4d494b2962 november 2012
                        layer.setEditorLayout(2)
                    except:
                        pass
                    layer.setEditForm(uifile)
                    if tablename in ('obs_points','obs_lines'):
                        formlogic = "form_logics." + tablename + "_form_open"
                        layer.setEditFormInit(formlogic)
                QgsProject.instance().addMapLayers([layer])
                group_index = self.legend.groups().index('Midvatten_OBS_DB')   # SIPAPI UPDATE 2.0
                self.legend.moveLayer (self.legend.layers()[0],group_index)
                if tablename == 'obs_points':#zoom to obs_points extent
                    qgis.utils.iface.mapCanvas().setExtent(layer.extent())
                elif tablename == 'w_lvls_last_geom':#we do not want w_lvls_last_geom to be visible by default
                    self.legend.setLayerVisible(layer,False)

    def selection_layer_in_db_or_not(self): #this is not used, it might be if using layer_styles stored in the db
        sql = r"""select name from sqlite_master where name = 'layer_styles'"""
        result = db_utils.sql_load_fr_db(sql)[1]
        if len(result)==0:#if it is an old database w/o styles
            update_db = common_utils.Askuser("YesNo", """Your database was created with plugin version < 1.1 when layer styles were not stored in the database. You can update this database to the new standard with layer styles (symbols, colors, labels, input forms etc) stored in the database. This will increase plugin stability and multi-user experience but it will also change the layout of all your forms for entering data into the database. Anyway, an update of the database is recommended. Do you want to add these layer styles now?""", 'Update database with layer styles?')
            if update_db.result == 1:
                from .create_db import AddLayerStyles
                AddLayerStyles()
                self.add_layers_new_method()
            else:
                self.add_layers_old_method()
        else:
            self.add_layers_new_method()
