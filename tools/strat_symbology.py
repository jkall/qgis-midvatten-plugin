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
    root = QgsProject.instance().layerTreeRoot()
    midv = root.findGroup('Midvatten_OBS_DB')

    #groups = {'Stratigraphy symbology': ('Bars', 'Static bars')}
    remove_group = midv.removeChildNode(midv.findGroup('Stratigraphy symbology'))
    stratigraphy_group = qgis.core.QgsLayerTreeGroup(name='Stratigraphy symbology', checked=False)
    stratigraphy_group.setIsMutuallyExclusive(True)
    bars_group = qgis.core.QgsLayerTreeGroup(name='Bars', checked=True)
    static_bars_group = qgis.core.QgsLayerTreeGroup(name='Bars', checked=True)
    midv.insertChildNode(0, stratigraphy_group)
    stratigraphy_group.insertChildNodes(0, [bars_group, static_bars_group])

    dbconnection = db_utils.DbConnectionManager()
    add_views_to_db(dbconnection)
    bars_layers = []
    add_layers_to_list(bars_layers, ['strat_symbology_view', 'w_lvls_last_geom'], geometrycolumn='geometry', dbconnection=dbconnection)
    #bars_layers[0].setItemVisibilityCheckedRecursive(False)
    QgsProject.instance().addMapLayers(bars_layers, False)
    bars_group.insertLayer(0, bars_layers[0])
    bars_group.insertLayer(0, bars_layers[1])
    plot_types = defs.PlotTypesDict()
    colors = defs.PlotColorDict()
    #renderer = symbology_from_scratch(plot_types, colors)

    geometry_expression = '''geom_from_wkt( format('POLYGON((%1 %2, %3 %4, %5 %6, %7 %8))', 
                                X($geometry)-2, Y($geometry) - "depthtop", 
                                X($geometry)+2, Y($geometry) - "depthtop", 
                                X($geometry)+2, Y($geometry) - "depthbot",
                                X($geometry)-2, Y($geometry) - "depthbot"))'''

    symbology_using_cloning(plot_types, colors, bars_layers[0], geometry_expression)
    #bars_layers[0].setRenderer(renderer)
    iface.mapCanvas().refresh()

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

def symbology_using_cloning(plot_types, colors, layer, geometry_expression):

    # now try to load the style file
    stylefile_sv = os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions",
                                layer.name() + "_bars_sv.qml")
    stylefile = os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions",
                             layer.name() + "_bars.qml")
    if utils.getcurrentlocale()[0] == 'sv_SE' and os.path.isfile(
            stylefile_sv):  # swedish forms are loaded only if locale settings indicate sweden
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

    renderer = layer.renderer()
    root = renderer.rootRule()
    for_cloning = root.children()[1]
    for strata, types in plot_types.items():
        color = QColor(colors.get(strata, colors.get('Okänd', colors.get('Unknown', 'white'))))
        rule = for_cloning.clone()
        rule.setIsElse(False)
        rule.setFilterExpression('''"geoshort" {}'''.format(types))
        rule.setLabel(strata)
        print(str(rule.symbol().symbolLayerCount()))
        sl = rule.symbol().symbolLayer(0)
        sl.setColor(color)
        print(str(sl.strokeColor()))

        print(str(sl.strokeColor()))
        ssl = sl.subSymbol().symbolLayer(0)
        ssl.setStrokeColor(color)

        #strokeColor
        #setStrokeColor
        #rule.setSymbol(create_symbol(geometry_expression, color))
        #root.appendChild(rule)
        root.insertChild(1, rule)

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
    dbconnection.execute('''DROP VIEW IF EXISTS strat_symbology_view;''')
    dbconnection.execute('''
CREATE VIEW strat_symbology_view AS
    SELECT stratigraphy.rowid, "obsid",
    (SELECT MAX(depthbot) FROM stratigraphy AS a where a.obsid = stratigraphy.obsid) AS "maxdepthbot",
    (CASE WHEN (SELECT MAX(depthbot) FROM stratigraphy AS a where a.obsid = stratigraphy.obsid) = "depthbot" THEN "drillstop" ELSE NULL END) AS "drillstop",
    "stratid", "depthtop", "depthbot", "geology", "geoshort", stratigraphy."capacity", stratigraphy."development", "comment", geometry FROM stratigraphy JOIN obs_points USING (obsid);''')

    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name = 'strat_symbology_view' ;''')
        dbconnection.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT 'strat_symbology_view', 'geometry', 'rowid', 'obs_points', 'geometry', 1;''')

    bergy = (
    '''CREATE VIEW obs_p_bergy AS
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

LEFT JOIN (SELECT s.obsid AS obsid, s.depthtop AS length FROM stratigraphy AS s WHERE s.geoshort LIKE '%berg%' OR s.geology LIKE '%berg%') AS u on a.obsid == u.obsid''')

    dbconnection.commit()

