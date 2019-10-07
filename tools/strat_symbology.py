# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that load stratigraphy symbology
                              -------------------
        begin                : 2019-09-18
        copyright            : (C) 2019 by HenrikSpa
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
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer, QgsGeometryGeneratorSymbolLayer, QgsMarkerSymbol
from qgis.PyQt.QtGui import QColor

import db_utils
import midvatten_utils as utils
from builtins import object
import traceback

from definitions import midvatten_defs as defs
from midvatten_utils import add_layers_to_list
from qgis.PyQt.QtCore import QCoreApplication


def strat_symbology(iface):
    """
    TODO: berg and rock are hardcoded both in code and in view
    :param iface:
    :return:
    """
    root = QgsProject.instance().layerTreeRoot()
    dbconnection = db_utils.DbConnectionManager()
    plot_types = defs.PlotTypesDict()
    bedrock_geoshort = defs.bedrock_geoshort()
    bedrock_types = plot_types[bedrock_geoshort]
    geo_colors = defs.geocolorsymbols()
    hydro_colors = defs.hydrocolors()
    groupname = 'Midvatten strat symbology'

    try:
        add_views_to_db(dbconnection, bedrock_types)
    except:
        utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('strat_symbology', '''Creating database views failed, see log message panel'''),
                                        log_msg=QCoreApplication.translate('strat_symbology', '''%s''')%str(traceback.format_exc()))
        dbconnection.closedb()
        return

    root.removeChildNode(root.findGroup(groupname))
    stratigraphy_group = qgis.core.QgsLayerTreeGroup(name=groupname, checked=True)
    root.insertChildNode(0, stratigraphy_group)
    stratigraphy_group.setIsMutuallyExclusive(True)
    for name, stylename, wlvls_stylename, bedrock_stylename in (('Bars', 'bars_strat', 'bars_w_lvls_last_geom', 'bars_bedrock'),
                                                                ('Static bars', 'bars_static_strat', 'bars_static_w_lvls_last_geom', 'bars_static_bedrock'),
                                                                ('Rings', 'rings_strat', None, 'rings_bedrock')):
        group = qgis.core.QgsLayerTreeGroup(name=name, checked=True)
        group.setExpanded(False)
        stratigraphy_group.insertChildNode(0, group)
        layers = []
        add_layers_to_list(layers, ['bars_strat', 'bars_strat', 'w_lvls_last_geom', 'bedrock'], geometrycolumn='geometry', dbconnection=dbconnection, layernames=['Geology', 'Hydro', 'W levels', 'Bedrock'])
        symbology_using_cloning(plot_types, geo_colors, layers[0], stylename, 'geoshort')
        symbology_using_cloning({k: "= '{}'".format(k) for k in sorted(hydro_colors.keys())}, hydro_colors, layers[1], stylename, 'capacity')
        QgsProject.instance().addMapLayers(layers[:2], False)

        if wlvls_stylename is not None and 'h_tocags' in layers[2].fields().names():
            apply_style(layers[2], wlvls_stylename)
            QgsProject.instance().addMapLayer(layers[2], False)
            group.addLayer(layers[2])
            group.children()[-1].setExpanded(False)

        if bedrock_stylename is not None:
            create_bedrock_symbology(layers[3], bedrock_stylename, bedrock_geoshort, group)

        color_group = qgis.core.QgsLayerTreeGroup(name='Layers', checked=True)
        color_group.setIsMutuallyExclusive(True)
        group.insertChildNode(-1, color_group)
        color_group.addLayer(layers[0])
        color_group.addLayer(layers[1])

    iface.mapCanvas().refresh()

def create_bedrock_symbology(bedrock_layer, bedrock_stylename, bedrock_geoshort, group):
    apply_style(bedrock_layer, bedrock_stylename)
    bedrock_root_rule = bedrock_layer.renderer().rootRule()
    bedrock_rules = bedrock_root_rule.children()

    if len(bedrock_rules) not in (2, 3):
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('strat_symbology',
                                                                          'Style and code discrepancy! The style %s has an unsupported number of rules!'))
        return
    if len(bedrock_rules) == 3:
        # Bars with triangle, open and closed ending
        bedrock_triangle, bedrock_closed_ending, bedrock_open_ending = bedrock_rules
        bedrock_triangle.setFilterExpression('''LOWER("drillstop") LIKE '%{}%' '''.format(bedrock_geoshort))
    elif len(bedrock_rules) == 2:
        # Rings with open and closed ending
        bedrock_closed_ending, bedrock_open_ending = bedrock_rules

    bedrock_closed_ending.setFilterExpression('''LOWER("drillstop") LIKE '%{}%' '''.format(bedrock_geoshort))
    bedrock_open_ending.setFilterExpression(
        '''LOWER("drillstop") NOT LIKE '%{}%' OR "drillstop" IS NULL '''.format(bedrock_geoshort))
    QgsProject.instance().addMapLayer(bedrock_layer, False)
    group.addLayer(bedrock_layer)
    group.children()[-1].setExpanded(False)

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
    try:
        root = renderer.rootRule()
    except:
        print(str(stylename))
        raise
    for_cloning = root.children()[-1]

    for key, types in plot_types.items():
        color = QColor(colors.get(key, [None, 'white'])[1])
        rule = for_cloning.clone()
        rule.setIsElse(False)
        rule.setFilterExpression('''"{}" {}'''.format(column, types))
        rule.setLabel(key)
        sl = rule.symbol().symbolLayer(0)
        sl.setColor(color)

        if sl.subSymbol() is not None:
            ssl = sl.subSymbol().symbolLayer(0)
            ssl.setStrokeColor(color)
        root.insertChild(1, rule)

def set_geometry_width_and_factor(layer, xfactor=None, yfactor=None):
    # TODO: Ongoing developement
    # QgsGeometryGeneratorSymbolLayer.setGeometryExpression(). This could be used to allow a factor in the expression.
    # It must be used for every layer (bedrock and w_levels) as well though.

    renderer = layer.renderer()
    root = renderer.rootRule()
    for child in root.children():
        if isinstance(child, QgsGeometryGeneratorSymbolLayer):
            geometry_expression = child.geometryExpression()
            if xfactor is not None:
                geometry_expression = geometry_expression.replace('{xfactor}', str(xfactor))
            else:
                geometry_expression = geometry_expression.replace('{xfactor}', '')
            if yfactor is not None:
                geometry_expression = geometry_expression.replace('{yfactor}', str(yfactor))
            else:
                geometry_expression = geometry_expression.replace('{yfactor}', '')

        #elif isinstance(child, QgsMarkerSymbol):
        #    if child.dataDefinedSize() is not None:
        #        child.setDataDefinedSize('''coalesce(scale_linear("soildepth", 1, 54.3, 1, 10), 0)''')

def add_views_to_db(dbconnection, bedrock_types):
    view_name = 'bars_strat'
    dbconnection.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' '''.format(view_name))
    dbconnection.execute('''
CREATE VIEW {} AS
    SELECT stratigraphy.{} AS rowid, "obsid", (SELECT MAX(depthbot) FROM stratigraphy AS a where a.obsid = stratigraphy.obsid) AS "maxdepthbot",
    "stratid", "depthtop", "depthbot", "geology", "geoshort", stratigraphy."capacity", stratigraphy."development", "comment", geometry FROM stratigraphy JOIN obs_points USING (obsid)'''.format(view_name, db_utils.rowid_string(dbconnection)))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1'''.format(view_name))

    view_name = 'w_lvls_last_geom'
    dbconnection.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' '''.format(view_name))
    dbconnection.execute('''CREATE VIEW {} AS SELECT b.{} AS rowid, a.obsid AS obsid, MAX(a.date_time) AS date_time,  a.meas AS meas,  a.level_masl AS level_masl, b.h_tocags AS h_tocags, b.geometry AS geometry FROM w_levels AS a JOIN obs_points AS b using (obsid) GROUP BY obsid;'''.format(view_name, db_utils.rowid_string(dbconnection)))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1;'''.format(view_name))

    view_name = 'bedrock'
    dbconnection.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' '''.format(view_name))
    bergy = (
        '''
CREATE VIEW {view_name} AS
 SELECT a.{rowid}, a.obsid,
    a.h_toc,
    a.h_gs,
    a.h_tocags,
    a.length,
    a.h_syst,
        CASE
            WHEN a.h_gs IS NOT NULL AND a.h_gs != 0 THEN a.h_gs
            WHEN a.h_toc IS NOT NULL AND a.h_toc != 0 AND a.h_tocags IS NOT NULL THEN a.h_toc - a.h_tocags
            WHEN a.h_toc IS NOT NULL AND a.h_toc != 0 THEN a.h_toc
            ELSE NULL
        END AS ground_surface,
        CASE
            WHEN COALESCE(u.soildepth, a.length) = 0.0 THEN NULL
            ELSE COALESCE(u.soildepth, a.length)
        END AS soildepth,
        CASE
            WHEN a.h_gs IS NOT NULL AND a.h_gs != 0 THEN a.h_gs
            WHEN a.h_toc IS NOT NULL AND a.h_toc != 0 AND a.h_tocags IS NOT NULL THEN a.h_toc - a.h_tocags
            WHEN a.h_toc IS NOT NULL AND a.h_toc != 0 THEN a.h_toc
            ELSE NULL
        END -
        CASE
            WHEN COALESCE(u.soildepth, a.length) = 0.0 THEN NULL
            ELSE COALESCE(u.soildepth, a.length)
        END AS bedrock,
        COALESCE(u.geo, a.drillstop) AS drillstop,
        CASE
            WHEN u.soildepth IS NULL THEN 'obs_points'
            ELSE 'stratigraphy'
        END AS bedrock_from_table,
    a.geometry
   FROM obs_points a
     LEFT JOIN (SELECT s.obsid, MIN(s.depthtop) AS soildepth,
                'Stratigraphy: '||MIN(s.geology)||' '||MIN(s.geoshort) AS geo
                FROM stratigraphy s
                WHERE LOWER(s.geoshort) {bedrock_types}
                GROUP BY s.obsid
                ) u ON a.obsid = u.obsid
    ORDER BY a.obsid'''.format(**{'view_name': view_name, 'bedrock_types': bedrock_types, 'rowid': db_utils.rowid_string(dbconnection)}))
    dbconnection.execute(bergy)
    if dbconnection.dbtype == 'spatialite':
        dbconnection.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1'''.format(view_name))

    dbconnection.commit()

