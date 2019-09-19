# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that load stratigraphy symbology
                              -------------------
        begin                : 2019-09-18
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
import os
import qgis.utils
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer
from qgis.PyQt.QtGui import QColor

import db_utils
import midvatten_utils as utils
from builtins import object

from definitions import midvatten_defs as defs
from midvatten_utils import add_layers_to_list

def strat_symbology(iface):
    """
    TODO: Drillstop shold be a separatae layer like bergy.
    :param iface:
    :return:
    """
    root = QgsProject.instance().layerTreeRoot()
    midv = root.findGroup('Midvatten_OBS_DB')

    dbconnection = db_utils.DbConnectionManager()
    add_views_to_db(dbconnection)

    plot_types = defs.PlotTypesDict()
    geo_colors = defs.geocolorsymbols()
    hydro_colors = defs.hydrocolors()
    midv.removeChildNode(midv.findGroup('Stratigraphy symbology'))
    stratigraphy_group = qgis.core.QgsLayerTreeGroup(name='Stratigraphy symbology', checked=True)
    midv.insertChildNode(0, stratigraphy_group)
    stratigraphy_group.setIsMutuallyExclusive(True)
    for name, stylename in (('Bars', 'strat_bars'), ('Static bars', 'strat_static_bars')):
        group = qgis.core.QgsLayerTreeGroup(name=name, checked=True)
        stratigraphy_group.insertChildNodes(0, group)
        layers = []
        add_layers_to_list(layers, ['strat_bars', 'strat_bars', 'w_lvls_last_geom'], geometrycolumn='geometry', dbconnection=dbconnection, layernames=['Geology', 'Hydro', 'W levels'])
        #layers[0].setItemVisibilityCheckedRecursive(False)

        symbology_using_cloning(plot_types, geo_colors, layers[0], stylename)
        symbology_using_cloning(plot_types, hydro_colors, layers[1], stylename)

        if 'h_tocags' in layers[1].fields().names():
            apply_style(layers[1], 'w_lvls_last_geom_static_bars')
            QgsProject.instance().addMapLayers(layers, False)
            group.addLayer(layers[2])
        else:
            QgsProject.instance().addMapLayers(layers[:2], False)

        color_group = qgis.core.QgsLayerTreeGroup(name='Layers', checked=True)
        group.insertChildNode(-1, color_group)
        color_group.addLayer(layers[0])
        color_group.addLayer(layers[1])

        #layers[0].setRenderer(renderer)
    iface.mapCanvas().refresh()


def apply_style(layer, stylename):
    # now try to load the style file
    stylefile_sv = os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions","{}_sv.qml".format(stylename))
    stylefile = os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions", "{}.qml".format(stylename))
    if utils.getcurrentlocale()[0] == 'sv_SE' and os.path.isfile(stylefile_sv):  # swedish forms are loaded only if locale settings indicate sweden
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

def symbology_using_cloning(plot_types, colors, layer, stylename, column):
    apply_style(layer, stylename)

    renderer = layer.renderer()
    root = renderer.rootRule()
    for_cloning = root.children()[1]

    rock_key = 'berg' if utils.getcurrentlocale()[0] == 'sv_SE': else 'rock'
    root.children()[2].setFilterExpression('''"{}" {}'''.format('geoshort', plot_types[rock_key][1]))

    for key, types in plot_types.items():
        color = QColor(colors.get(key, 'white'))
        rule = for_cloning.clone()
        rule.setIsElse(False)
        rule.setFilterExpression('''"{}" {}'''.format(column, types))
        rule.setLabel(key)
        sl = rule.symbol().symbolLayer(0)
        sl.setColor(color)
        ssl = sl.subSymbol().symbolLayer(0)
        ssl.setStrokeColor(color)
        root.insertChild(1, rule)

def symbology_from_scratch(plot_types, colors, geometry_expression):
    renderer = qgis.core.QgsRuleBasedRenderer(create_symbol(geometry_expression, 'white'))
    for strata, types in plot_types.items():
        color = colors.get(strata, colors.get('Okänd', colors.get('Unknown', 'white')))
        rule = qgis.core.QgsRuleBasedRenderer.Rule(create_symbol(geometry_expression, color))
        rule.setFilterExpression('''"geoshort" {}'''.format(types))
        rule.setLabel(strata)
        renderer.rootRule().appendChild(rule)
    else:
        rule = qgis.core.QgsRuleBasedRenderer.Rule(create_symbol(geometry_expression, 'black'))
        rule.setIsElse(True)
        renderer.rootRule().appendChild(rule)
    return renderer

def create_symbol(geometry_expression, color):
    raise NotImplementedError()
    # https://qgis.org/api/classQgsSimpleFillSymbolLayer.html
    #simple_fill_symbol = qgis.core.QgsFillSymbol([qgis.core.QgsSimpleFillSymbolLayer(QColor(color),
    #                                                                                 strokeColor=QColor(color),
    #                                                                                 strokeWidth=0.1)])
    #qgis._core.QgsGeometryGeneratorSymbolLayer cannot be instantiated or sub-classed !!?!
    # https://qgis.org/api/qgsmarkersymbollayer_8cpp_source.html rows around 720
    """
    symbol_layer = qgis.core.QgsGeometryGeneratorSymbolLayer.create({'geometryModifier': geometry_expression,
                                                                     'SymbolType': 'Marker',
                                                                     'color': color,
                                                                     'line_color': color,
                                                                     'line_width': '0.1'})
    """
    #symbol_layer = qgis.core.QgsGeometryGeneratorSymbolLayer.create({'geometryModifier': geometry_expression})

    #symbol_layer.setGeometryExpression(geometry_expression)
    symbol_layer.setSubSymbol(simple_fill_symbol)
    symbol = qgis.core.QgsMarkerSymbol([symbol_layer])
    return symbol


def add_views_to_db(dbconnection):
    strat_view_name = 'strat_bars'
    dbconnection.execute('''DROP VIEW IF EXISTS {};'''.format(strat_view_name))
    dbconnection.execute('''
CREATE VIEW {} AS
    SELECT stratigraphy.rowid, "obsid", "stratid", "depthtop", "depthbot", "geology", "geoshort", stratigraphy."capacity", stratigraphy."development", "comment", geometry FROM stratigraphy JOIN obs_points USING (obsid);'''.format(strat_view_name))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' ;'''.format(strat_view_name))
        dbconnection.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1;'''.format(strat_view_name))

    view_name = 'w_lvls_last_geom'
    dbconnection.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    dbconnection.execute('''CREATE VIEW {} AS SELECT b.rowid AS rowid, a.obsid AS obsid, MAX(a.date_time) AS date_time,  a.meas AS meas,  a.level_masl AS level_masl, b.h_tocags AS h_tocags, b.geometry AS geometry FROM w_levels AS a JOIN obs_points AS b using (obsid) GROUP BY obsid;'''.format(view_name))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' ;'''.format(view_name))
        dbconnection.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1;'''.format(view_name))

    view_name = 'obs_p_bedrock'
    dbconnection.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    bergy = (
        '''
CREATE VIEW {} AS
    SELECT DISTINCT a.rowid AS rowid,
    		a.obsid AS obsid,
    		a.h_toc AS h_toc,
    		a.h_gs AS h_gs,
    		(CASE WHEN u.length IS NULL then a.length ELSE u.length END) as length,
    		a.h_gs - (CASE WHEN u.length IS NULL then a.length ELSE u.length END) as bergy,
    		a.drillstop as drillstop,
    		(CASE WHEN u.length IS NULL then 'obs_points' ELSE 'stratigraphy' END) AS from_table,
    		a.source AS source,
    		a.type AS obstype,
    		a.geometry AS geometry FROM obs_points AS a

    LEFT JOIN (SELECT s.obsid AS obsid, s.depthtop AS length 
               FROM stratigraphy AS s 
               WHERE (LOWER(s.geoshort) LIKE '%berg%' OR LOWER(s.geology) LIKE '%berg%')
               OR (LOWER(s.geoshort) LIKE '%rock%' OR LOWER(s.geology) LIKE '%rock%')
               ) AS u on a.obsid == u.obsid'''.format(view_name))
    dbconnection.execute(bergy)

    dbconnection.commit()

