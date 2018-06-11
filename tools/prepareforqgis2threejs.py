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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
import db_utils
import matplotlib as mpl
import os
from qgis.core import QgsProject, QgsSingleSymbolRenderer, QgsSymbol, QgsVectorLayer

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor

import midvatten_utils as utils
from definitions import midvatten_defs as defs
from .midvatten_utils import returnunicode as ru


class PrepareForQgis2Threejs(object):        
    def __init__(self, iface, settingsdict={}):

        self.dbconnection = db_utils.DbConnectionManager()

        self.settingsdict = settingsdict
        self.strat_layers_dict =  defs.PlotTypesDict('english') 
        self.symbolcolors_dict = defs.PlotColorDict() # This is not used yet
        for key, v in list(self.strat_layers_dict.items()):#make all the keys only ascii and only lower case and also add 'strat_' as prefix
            newkey = 'strat_' + utils.return_lower_ascii_string(key)
            self.strat_layers_dict[newkey] = self.strat_layers_dict[key]
            del self.strat_layers_dict[key]
        for key, v in list(self.symbolcolors_dict.items()):#THIS IS NOT USED YET make all the keys only ascii and only lower case and also add 'strat_' as prefix
            newkey = 'strat_' + utils.return_lower_ascii_string(key)
            self.symbolcolors_dict[newkey] = self.symbolcolors_dict[key] 
            del self.symbolcolors_dict[key]
        self.iface = iface
        self.root = QgsProject.instance().layerTreeRoot()
        self.legend = self.iface.legendInterface()
        self.remove_views()
        self.drop_db_views()
        self.create_db_views()
        self.dbconnection.commit_and_closedb()
        self.add_layers()

    def add_layers(self):#not tested and not ready, must fix basic styles (preferrably colors based on some definition dicitonary
        MyGroup = self.root.insertGroup(0, "stratigraphy_layers_for_qgis2threejs")#verify this is inserted at top

        uri = self.dbconnection.uri

        canvas = self.iface.mapCanvas()
        layer_list = []
        map_canvas_layer_list=[]
        
        list_with_all_strat_layer = []
        for key in self.strat_layers_dict:
            list_with_all_strat_layer.append(key)
        #print list_with_all_strat_layer#debug

        list_with_all_strat_layer.append('strat_obs_p_for_qgsi2threejs')

        colors = []

        for strat_layer_view in list_with_all_strat_layer: 
            uri.setDataSource('',strat_layer_view, 'Geometry')
            dbtype = db_utils.get_dbtype(self.dbconnection.dbtype)
            layer = QgsVectorLayer(uri.uri(), strat_layer_view, dbtype) # Adding the layer as 'spatialite' instead of ogr vector layer is preferred
            layer_list.append(layer)

            try:
                supplied_color = self.symbolcolors_dict[strat_layer_view]
            except KeyError:
                color = None
            else:
                try:
                    # matplotlib 2
                    color = mpl.colors.to_rgbsupplied_color()
                except AttributeError:
                    try:
                        # matplotlib 1
                        converter = mpl.colors.ColorConverter()
                        color = converter.to_rgb(supplied_color)
                        color = [x * 255 for x in color]
                    except Exception as e:
                        utils.MessagebarAndLog.warning(
                            bar_msg=ru(QCoreApplication.translate(u'PrepareForQgis2Threejs', u'Setting color from dict failed')),
                            log_msg=ru(QCoreApplication.translate(u'PrepareForQgis2Threejs', u'Error msg %s'))%str(e))
                        color = None

            colors.append(color)

        # create a new single symbol renderer
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        renderer = QgsSingleSymbolRenderer(symbol)

        for idx, layer in enumerate(layer_list):#now loop over all the layers, add them to canvas and set colors
            if not layer.isValid():
                try:
                    print(layer.name() + ' is not valid layer')
                except:
                    pass
                pass
            else:
                # TODO: Made this a comment, but there might be some hidden feature thats still needed!
                #map_canvas_layer_list.append(QgsMapCanvasLayer(layer))

                #now try to load the style file
                stylefile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions",layer.name() + ".qml")
                try:
                    layer.loadNamedStyle(stylefile)
                except:
                    try:
                        print("Loading stylefile %s failed."%stylefile)
                    except:
                        pass

                color = colors[idx]
                if color:
                    current_symbols = layer.rendererV2().symbols()
                    current_symbol = current_symbols[0]
                    current_symbol.setColor(QColor.fromRgb(color[0], color[1], color[2]))

                QgsProject.instance().addMapLayers([layer],False)
                MyGroup.insertLayer(0,layer)
                                
            #finally refresh canvas
            canvas.refresh()

    def create_db_views(self):
        SQLFile = os.path.join(os.sep,os.path.dirname(__file__),"..","definitions","add_spatial_views_for_gis2threejs.sql")

        self.dbconnection.execute(r"""create view strat_obs_p_for_qgsi2threejs as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."geometry" as "geometry" from "obs_points" as "a" JOIN "stratigraphy" as "b" using ("obsid") where (typeof("a"."h_toc") in ('integer', 'real') or typeof("a"."h_gs") in ('integer', 'real'))""")
        self.dbconnection.execute(r"""insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('strat_obs_p_for_qgsi2threejs', 'geometry', 'rowid', 'obs_points', 'geometry',1);""")

        for key in self.strat_layers_dict:
            f = open(SQLFile, 'r')
            linecounter = 1
            for line in f:
                if linecounter > 1:    # first line is encoding info....
                    sqliteline = line.replace('CHANGETOVIEWNAME',key).replace('CHANGETOPLOTTYPESDICTVALUE',self.strat_layers_dict[key])
                    #print(sqliteline)#debug
                    self.dbconnection.execute(sqliteline)
                linecounter += 1

    def drop_db_views(self):
        sql1="delete from views_geometry_columns where view_name = 'strat_obs_p_for_qgsi2threejs'"
        sql2="drop view if exists strat_obs_p_for_qgsi2threejs"
        db_utils.sql_alter_db(sql1, dbconnection=self.dbconnection)
        db_utils.sql_alter_db(sql2, dbconnection=self.dbconnection)

        placeholder_sign = db_utils.placeholder_sign(self.dbconnection)
        sql1="delete from views_geometry_columns where view_name = %s"%placeholder_sign
        sql2="drop view if exists "
        for key in self.strat_layers_dict:
            db_utils.sql_alter_db(sql1, dbconnection=self.dbconnection, all_args=[(key,)])
            db_utils.sql_alter_db(sql2 + key, dbconnection=self.dbconnection)

    def remove_views(self):
        remove_group = self.root.findGroup("stratigraphy_layers_for_qgis2threejs")
        self.root.removeChildNode(remove_group)
        
