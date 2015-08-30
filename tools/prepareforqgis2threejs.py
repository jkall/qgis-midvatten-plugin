# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that prepares a number of spatial views 
 in your spatialite midvatten database that are suitable for creating 3D plots with qgis2threejs.
 The spatial views are added into your qgis project group "stratigraphy_layers_for_qgis2threejs" 
                              -------------------
        begin                : 20150129
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
import midvatten_utils as utils
from definitions import midvatten_defs as defs

class PrepareForQgis2Threejs():        
    def __init__(self, iface, settingsdict={}): 
        self.settingsdict = settingsdict
        self.strat_layers_dict =  defs.PlotTypesDict('english') 
        self.symbolcolors_dict = defs.PlotColorDict() # This is not used yet
        for key, v in self.strat_layers_dict.items():#make all the keys only ascii and only lower case and also add 'strat_' as prefix
            newkey = 'strat_' + utils.return_lower_ascii_string(key)
            self.strat_layers_dict[newkey] = self.strat_layers_dict[key] 
            del self.strat_layers_dict[key]
        for key, v in self.symbolcolors_dict.items():#THIS IS NOT USED YET make all the keys only ascii and only lower case and also add 'strat_' as prefix
            newkey = 'strat_' + utils.return_lower_ascii_string(key)
            self.symbolcolors_dict[newkey] = self.symbolcolors_dict[key] 
            del self.symbolcolors_dict[key]
        self.iface = iface
        self.root = QgsProject.instance().layerTreeRoot()
        self.legend = self.iface.legendInterface()
        self.remove_views()
        self.drop_db_views()
        self.create_db_views()
        self.add_layers()

    def add_layers(self):#not tested and not ready, must fix basic styles (preferrably colors based on some definition dicitonary
        MyGroup = self.root.insertGroup(0, "stratigraphy_layers_for_qgis2threejs")#verify this is inserted at top
        
        uri = QgsDataSourceURI()
        uri.setDatabase(self.settingsdict['database'])
        canvas = self.iface.mapCanvas()
        layer_list = []
        map_canvas_layer_list=[]
        
        list_with_all_strat_layer = []
        for key in self.strat_layers_dict:
            list_with_all_strat_layer.append(key)
        #print list_with_all_strat_layer#debug

        list_with_all_strat_layer.append('strat_obs_p_for_qgsi2threejs')

        for strat_layer_view in list_with_all_strat_layer: 
            uri.setDataSource('',strat_layer_view, 'Geometry')
            layer = QgsVectorLayer(uri.uri(), strat_layer_view, 'spatialite') # Adding the layer as 'spatialite' instead of ogr vector layer is preferred
            layer_list.append(layer)

        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        renderer = QgsSingleSymbolRendererV2(symbol)

        for layer in layer_list:#now loop over all the layers, add them to canvas and set colors
            if not layer.isValid():
                print(layer.name() + ' is not valid layer')
                pass
            else:
                map_canvas_layer_list.append(QgsMapCanvasLayer(layer))

                #now try to load the style file
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",layer.name() + ".qml")
                try:
                    layer.loadNamedStyle(stylefile)
                except:
                    pass

                QgsMapLayerRegistry.instance().addMapLayers([layer],False)
                MyGroup.insertLayer(0,layer)
                                
            #finally refresh canvas
            canvas.refresh()

    def create_db_views(self):
        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions","add_spatial_views_for_gis2threejs.sql") 

        myconnection = utils.dbconnection()
        myconnection.connect2db()
        curs = myconnection.conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        sqliteline = r"""create view strat_obs_p_for_qgsi2threejs as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."geometry" as "geometry" from "obs_points" as "a" JOIN "stratigraphy" as "b" using ("obsid") where (typeof("a"."h_toc") in ('integer', 'real') or typeof("a"."h_gs") in ('integer', 'real'))"""
        curs.execute(sqliteline)
        sqliteline = r"""insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('strat_obs_p_for_qgsi2threejs', 'geometry', 'rowid', 'obs_points', 'geometry',1);"""
        curs.execute(sqliteline)
        
        for key in self.strat_layers_dict:
            f = open(SQLFile, 'r')
            linecounter = 1
            for line in f:
                if linecounter > 1:    # first line is encoding info....
                    sqliteline = line.replace('CHANGETOVIEWNAME',key).replace('CHANGETOPLOTTYPESDICTVALUE',self.strat_layers_dict[key])
                    #print(sqliteline)#debug
                    curs.execute(sqliteline) 
                linecounter += 1

        curs.execute("PRAGMA foreign_keys = OFF")
        myconnection.closedb()

    def drop_db_views(self):
        sql1="delete from views_geometry_columns where view_name = 'strat_obs_p_for_qgsi2threejs'"
        sql2="drop view if exists strat_obs_p_for_qgsi2threejs"
        utils.sql_alter_db(sql1) 
        utils.sql_alter_db(sql2) 
        
        sql1="delete from views_geometry_columns where view_name = ?"
        sql2="drop view if exists "
        for key in self.strat_layers_dict:
            utils.sql_alter_db_by_param_subst(sql1,(key,)) 
            utils.sql_alter_db(sql2 + key) 

    def remove_views(self):
        remove_group = self.root.findGroup("stratigraphy_layers_for_qgis2threejs")
        self.root.removeChildNode(remove_group)
        
