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
import copy
import os
import traceback

import qgis.utils
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsDataSourceUri, QgsProject, QgsGeometryGeneratorSymbolLayer, QgsVectorLayerSimpleLabeling, \
    QgsProperty, QgsFeatureRequest, QgsExpression

from midvatten.definitions import midvatten_defs as defs
from midvatten.tools.utils import common_utils, db_utils, midvatten_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools.utils.midvatten_utils import add_layers_to_list

strat_symbology_dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'strat_symbology_dialog.ui'))[0]


class StratSymbology(qgis.PyQt.QtWidgets.QDialog, strat_symbology_dialog):
    def __init__(self, iface, parent):
        self.iface = iface
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.ok_button.clicked.connect(lambda : self.create_symbology())
        self.show()

    @common_utils.general_exception_handler
    def create_symbology(self):
        common_utils.start_waiting_cursor()
        strat_symbology(self.iface,
                        self.rings_groupbox.isChecked(),
                        self.bars_groupbox.isChecked(),
                        self.static_bars_groupbox.isChecked(),
                        self.bars_xfactor.value(),
                        self.bars_yfactor.value(),
                        self.static_bars_xfactor.value(),
                        self.static_bars_yfactor.value(),
                        self.apply_obsid_filter.isChecked())
        common_utils.stop_waiting_cursor()


def strat_symbology(iface, plot_rings, plot_bars, plot_static_bars, bars_xfactor, bars_yfactor, static_bars_xfactor,
                    static_bars_yfactor, apply_obsid_filter):
    """
    TODO: There is a logical bug where layers that should get caught as ELSE isn't because the shadow  ("maxdepthbot"  =  "depthbot")
          gets them... I might have to put the shadow in other layer...
    :param iface:
    :return:
    """
    root = QgsProject.instance().layerTreeRoot()

    plot_types = defs.PlotTypesDict()
    bedrock_geoshort = defs.bedrock_geoshort()
    bedrock_types = plot_types[bedrock_geoshort]
    geo_colors = defs.geocolorsymbols()
    hydro_colors = defs.hydrocolors()
    groupname = 'Midvatten strat symbology'

    dbconnection = db_utils.DbConnectionManager()
    try:
        add_views_to_db(dbconnection, bedrock_types)
    except:
        common_utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('strat_symbology', '''Creating database views failed, see log message panel'''),
                                                           log_msg=QCoreApplication.translate('strat_symbology', '''%s''')%str(traceback.format_exc()))
        dbconnection.closedb()
        return
    else:
        dbconnection.commit_and_closedb()

    old_group = root.findGroup(groupname)
    previously_visible = ''
    if old_group:
        for child in old_group.children():
            if child.isVisible():
                previously_visible = child.name()
    else:
        previously_visible = 'Bars'

    root.removeChildNode(root.findGroup(groupname))
    stratigraphy_group = qgis.core.QgsLayerTreeGroup(name=groupname, checked=True)
    root.insertChildNode(0, stratigraphy_group)
    stratigraphy_group.setIsMutuallyExclusive(True)

    symbology_tables = {'Geology': 'bars_strat',
                        'Hydro': 'bars_strat',
                        'Bedrock': 'bedrock',
                        'W levels': 'w_lvls_last_geom',
                        'W levels label': 'w_lvls_last_geom',
                        'Obsid label': 'bedrock',
                        'Frame': 'bedrock',
                        'Bedrock label': 'bedrock',
                        'Shadow': 'bars_strat',
                        'Layer texts': 'bars_strat'}

    all_layers = []

    group_spec = {'Bars': {'symbology_stylename': {'Geology': 'bars_strat',
                                               'Hydro': 'bars_strat',
                                               'Bedrock': 'bars_bedrock',
                                               'W levels': 'bars_w_levels',
                                               'W levels label': 'bars_w_levels_label',
                                               'Obsid label': 'bars_obsid_label',
                                               'Frame': 'bars_frame',
                                               'Bedrock label': 'bars_bedrock_label',
                                               'Shadow': 'bars_shadow',
                                               'Layer texts': 'bars_layer_texts'
                                                },
                           'xfactor': bars_xfactor, 'yfactor': bars_yfactor,
                           'use_map_scale': True},
                 'Rings': {'symbology_stylename': {'Geology': 'rings_strat',
                                               'Hydro': 'rings_strat',
                                               'Bedrock': 'rings_bedrock',
                                               }}}

    if plot_static_bars:
        _group_spec = {'Bars': group_spec['Bars']}
        _group_spec['Static bars'] = copy.deepcopy(group_spec['Bars'])
        _group_spec['Static bars']['use_map_scale'] = False
        _group_spec['Static bars']['xfactor'] = static_bars_xfactor
        _group_spec['Static bars']['yfactor'] = static_bars_yfactor
        _group_spec.update({k: v for k, v in group_spec.items() if k not in _group_spec})
        group_spec = _group_spec

    if not plot_bars:
        del group_spec['Bars']
    if not plot_rings:
        del group_spec['Rings']

    for groupname, spec in group_spec.items():
        symbology_stylename = spec['symbology_stylename']
        group = add_group(stratigraphy_group, groupname)
        layers = create_layers({k: symbology_tables[k] for k in symbology_stylename.keys()})

        symbology = 'Obsid label'
        if symbology in symbology_stylename:
            try:
                add_generic_symbology(group, layers[symbology], symbology_stylename[symbology])
            except StyleNotFoundError as e:
                common_utils.MessagebarAndLog.info(bar_msg=str(e))
            except:
                common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        symbology = 'Layer texts'
        if symbology in symbology_stylename:
            try:
                add_generic_symbology(group, layers[symbology], symbology_stylename[symbology], checked=False)
            except StyleNotFoundError as e:
                common_utils.MessagebarAndLog.info(bar_msg=str(e))
            except:
                common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        symbology = 'W levels'
        if symbology in symbology_stylename:
            wlvls_layer = layers.get(symbology)
            if 'h_tocags' in wlvls_layer.fields().names():
                wlvls_group = add_group(group, symbology, checked=True)
                wlvl_label = 'W levels label'
                if wlvl_label in symbology_stylename:
                    try:
                        add_generic_symbology(wlvls_group, layers[wlvl_label],
                                              symbology_stylename[wlvl_label],
                                              checked=False)
                    except StyleNotFoundError as e:
                        common_utils.MessagebarAndLog.info(bar_msg=str(e))
                    except:
                        common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())
                try:
                    add_wlvls_symbology(wlvls_group, wlvls_layer, symbology_stylename[symbology])
                except StyleNotFoundError as e:
                    common_utils.MessagebarAndLog.info(bar_msg=str(e))
                except:
                    common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        symbology = 'Bedrock'
        if symbology in symbology_stylename:
            bedrock_group = add_group(group, symbology, checked=True)
            bedrock_label = symbology_stylename.get('Bedrock label')
            if bedrock_label:
                try:
                    add_generic_symbology(bedrock_group, layers['Bedrock label'],
                                      symbology_stylename['Bedrock label'], checked=False)
                except StyleNotFoundError as e:
                    common_utils.MessagebarAndLog.info(bar_msg=str(e))
                except:
                    common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())
                else:
                    _bedrock_label = '''LOWER("drillstop") LIKE '%{}%' '''
                    for child in layers['Bedrock label'].labeling().rootRule().children():
                        if not child.isElse():
                            child.setFilterExpression(_bedrock_label.format(bedrock_geoshort))

            try:
                add_bedrock_symbology(bedrock_group, layers[symbology], symbology_stylename[symbology],
                                      bedrock_geoshort)
            except RuleDiscrepancyError:
                del layers[symbology]
            except StyleNotFoundError as e:
                common_utils.MessagebarAndLog.info(bar_msg=str(e))
            except:
                common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        symbology = 'Frame'
        if symbology in symbology_stylename:
            try:
                add_generic_symbology(group, layers[symbology], symbology_stylename[symbology])
            except StyleNotFoundError as e:
                common_utils.MessagebarAndLog.info(bar_msg=str(e))
            except:
                common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        layers_group = add_group(group, 'Layers', checked=True)
        try:
            add_layers_symbology(layers_group, plot_types, geo_colors, hydro_colors, layers['Geology'],
                                 layers['Hydro'], symbology_stylename['Geology'])
        except StyleNotFoundError as e:
            common_utils.MessagebarAndLog.info(bar_msg=str(e))
        except:
            common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        symbology = 'Shadow'
        if symbology in symbology_stylename:
            try:
                add_generic_symbology(group, layers[symbology], symbology_stylename[symbology])
            except StyleNotFoundError as e:
                common_utils.MessagebarAndLog.info(bar_msg=str(e))
            except:
                common_utils.MessagebarAndLog.info(bar_msg=traceback.format_exc())

        if any([spec.get('xfactor'), spec.get('yfactor'), spec.get('use_map_scale')]):
            for layer in layers.values():
                scale_geometry(layer, xfactor=spec.get('xfactor'), yfactor=spec.get('yfactor'),
                               use_map_scale=spec.get('use_map_scale'))

        all_layers.extend(layers.values())


    QgsProject.instance().addMapLayers(all_layers, False)
    if apply_obsid_filter:
        apply_obsid_filter_to_layers(all_layers)

    for child in stratigraphy_group.children():
        if child.name() == previously_visible:
            child.setItemVisibilityChecked(True)
    iface.mapCanvas().refresh()

def create_layers(layers_names_tables):
    layers = []
    add_layers_to_list(layers, list(layers_names_tables.values()),
                       geometrycolumn='geometry',
                       layernames=list(layers_names_tables.keys()))
    layers = {layer_name: layers[idx] for idx, layer_name in enumerate(layers_names_tables.keys())}
    return layers

def add_group(parent_group, name, checked=False):
    group = qgis.core.QgsLayerTreeGroup(name=name, checked=checked)
    group.setExpanded(False)
    parent_group.insertChildNode(-1, group)
    return group

def apply_obsid_filter_to_layers(layers):
    selected_obsids = common_utils.getselectedobjectnames(column_name='obsid')
    if selected_obsids:
        filter_string = '''obsid IN ({})'''.format(common_utils.sql_unicode_list(selected_obsids))
        for layer in layers:
            req = QgsFeatureRequest(QgsExpression(filter_string))
            layer.setSubsetString(req.filterExpression().expression())

def add_layers_symbology(layers_group, plot_types, geo_colors, hydro_colors, geo_layer, hydro_layer,
                         layers_stylename):
    symbology_using_cloning(plot_types, geo_colors, geo_layer, layers_stylename, 'geoshort')
    symbology_using_cloning({k: "= '{}'".format(k) for k in sorted(hydro_colors.keys())}, hydro_colors,
                            hydro_layer, layers_stylename, 'capacity')

    for layer in [geo_layer, hydro_layer]:
        layers_group.addLayer(layer)
        layers_group.children()[-1].setExpanded(False)

    layers_group.setIsMutuallyExclusive(True)

def add_wlvls_symbology(wlvls_group, wlvls_layer, wlvls_stylename):
    apply_style(wlvls_layer, wlvls_stylename)
    # QgsProject.instance().addMapLayer(layers[2], False)
    wlvls_group.addLayer(wlvls_layer)
    wlvls_group.children()[-1].setExpanded(False)

def add_generic_symbology(group, layer, stylename, checked=True):
    apply_style(layer, stylename)
    group.addLayer(layer)
    group.children()[-1].setExpanded(False)
    group.children()[-1].setItemVisibilityChecked(checked)

def add_bedrock_symbology(bedrock_group, bedrock_layer, bedrock_stylename, bedrock_geoshort):
    apply_style(bedrock_layer, bedrock_stylename)
    bedrock_root_rule = bedrock_layer.renderer().rootRule()
    bedrock_rules = bedrock_root_rule.children()

    if len(bedrock_rules) == 1:
        # Bars with triangle
        bedrock_triangle = bedrock_rules[0]
        bedrock_triangle.setFilterExpression('''LOWER("drillstop") LIKE '%{}%' '''.format(bedrock_geoshort))
    elif len(bedrock_rules) == 2:
        # Rings with open and closed ending
        bedrock_closed_ending, bedrock_open_ending = bedrock_rules
        bedrock_closed_ending.setFilterExpression('''LOWER("drillstop") LIKE '%{}%' '''.format(bedrock_geoshort))
        bedrock_open_ending.setFilterExpression(
            '''LOWER("drillstop") NOT LIKE '%{}%' OR "drillstop" IS NULL '''.format(bedrock_geoshort))
    elif len(bedrock_rules) == 3:
        # Bars with triangle, open and closed ending
        bedrock_triangle, bedrock_closed_ending, bedrock_open_ending = bedrock_rules
        bedrock_triangle.setFilterExpression('''LOWER("drillstop") LIKE '%{}%' '''.format(bedrock_geoshort))
        bedrock_closed_ending.setFilterExpression('''LOWER("drillstop") LIKE '%{}%' '''.format(bedrock_geoshort))
        bedrock_open_ending.setFilterExpression(
            '''LOWER("drillstop") NOT LIKE '%{}%' OR "drillstop" IS NULL '''.format(bedrock_geoshort))
    else:
        common_utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('strat_symbology',
                                                                          'Style and code discrepancy! The style %s has an unsupported number of rules!'))
        raise RuleDiscrepancyError()

    bedrock_group.addLayer(bedrock_layer)
    bedrock_group.children()[-1].setExpanded(False)
    return bedrock_group

def apply_style(layer, stylename):
    # now try to load the style file
    stylefile_sv = os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions", "strat_symbology",
                                "{}_sv.qml".format(stylename))
    stylefile = os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions", "strat_symbology",
                             "{}.qml".format(stylename))
    if midvatten_utils.getcurrentlocale()[0] == 'sv_SE' and os.path.isfile(stylefile_sv):  # swedish forms are loaded only if locale settings indicate sweden
        try:
            layer.loadNamedStyle(stylefile_sv)
        except:
            if not os.path.isfile(stylefile):
                raise StyleNotFoundError(ru(QCoreApplication.translate('strat_symbology',
                                         ''''Missing stylefile %s''')) % ru(stylefile))
            else:
                layer.loadNamedStyle(stylefile)

    else:
        if not os.path.isfile(stylefile):
            raise StyleNotFoundError(ru(QCoreApplication.translate('strat_symbology',
                                     ''''Missing stylefile %s'''))%ru(stylefile))
        else:
            layer.loadNamedStyle(stylefile)


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
        rule.setFilterExpression('''trim(lower("{}")) {}'''.format(column, types))
        rule.setLabel(key)
        sl = rule.symbol().symbolLayer(0)
        sl.setColor(color)

        if sl.subSymbol() is not None:
            ssl = sl.subSymbol().symbolLayer(0)
            ssl.setStrokeColor(color)
        root.insertChild(0, rule)

    if for_cloning.isElse():
        for_cloning.setActive(False)

def scale_geometry(layer, xfactor=None, yfactor=None, use_map_scale=None):
    if not any([xfactor, yfactor, use_map_scale]):
        return
    renderer = layer.renderer()
    if not isinstance(renderer, qgis.core.QgsNullSymbolRenderer):
        try:
            root = renderer.rootRule()
        except AttributeError:
            symbols = [renderer.symbol()]
        else:
            symbols = [rule.symbol() for rule in root.children()]

        for symbol in symbols:
            sl = symbol.symbolLayer(0)
            if isinstance(sl, QgsGeometryGeneratorSymbolLayer):
                geometry_expression = sl.geometryExpression()
                if xfactor is not None:
                    geometry_expression = geometry_expression.replace('/**{xfactor}*/', '* ' + str(xfactor))
                if yfactor is not None:
                    geometry_expression = geometry_expression.replace('/**{yfactor}*/', '* ' + str(yfactor))
                if use_map_scale:
                    geometry_expression = geometry_expression.replace('/**{map_scale}*/', '*0.001*@map_scale')
                sl.setGeometryExpression(geometry_expression)
                # elif isinstance(rule, QgsMarkerSymbol):
                #    if rule.dataDefinedSize() is not None:
                #        rule.setDataDefinedSize('''coalesce(scale_linear("soildepth", 1, 54.3, 1, 10), 0)''')

    labeling = layer.labeling()
    if labeling:
        if isinstance(labeling, QgsVectorLayerSimpleLabeling):
            labels = [labeling]
        elif isinstance(labeling, qgis.core.QgsRuleBasedLabeling):
            labels = labeling.rootRule().children()
        else:
            labels = []

        for label in labels:
            settings = label.settings()
            ddf = settings.dataDefinedProperties()

            #'PositionX' = index 9
            for propertyno, factor, factortext in [(9, xfactor, '/**{xfactor}*/'),
                                                   (10, yfactor, '/**{yfactor}*/')]:
                expr = ddf.property(propertyno).expressionString()
                if factor is not None:
                    expr = expr.replace(factortext, '* ' + str(factor))
                if use_map_scale:
                    expr = expr.replace('/**{map_scale}*/', '*0.001*@map_scale')
                p = QgsProperty.fromExpression(expr)
                ddf.setProperty(propertyno, p)

            settings.setDataDefinedProperties(ddf)
            labeling.setSettings(settings)

def add_views_to_db(dbconnection, bedrock_types):
    view_name = 'bars_strat'
    cur = dbconnection.cursor
    try:
        cur.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    except:
        midvatten_utils.MessagebarAndLog.warning(log_msg=traceback.format_exc())

    if dbconnection.dbtype == 'spatialite':
        cur.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' '''.format(view_name))
        sql = '''
    CREATE VIEW {} AS
        SELECT stratigraphy.{} AS rowid, "obsid", (SELECT MAX(depthbot) FROM stratigraphy AS a where a.obsid = stratigraphy.obsid) AS "maxdepthbot",
        "stratid", "depthtop", "depthbot", "geology", "geoshort", stratigraphy."capacity", stratigraphy."development", "comment", geometry FROM stratigraphy JOIN obs_points USING (obsid)'''.format(view_name, db_utils.rowid_string(dbconnection))
    else:
        # The first user that creates this view will own it in the PostgreSQL-database.
        #
        sql = '''
            CREATE OR REPLACE VIEW {} AS
            SELECT row_number() OVER (ORDER BY "obsid", "stratid") "rowid",
            "obsid", "maxdepthbot", "stratid", "depthtop", "depthbot", "geology", "geoshort", "capacity", "development", "comment", "geometry"
            FROM (
            SELECT "obsid", (SELECT MAX(depthbot) FROM stratigraphy AS a where a.obsid = stratigraphy.obsid) AS "maxdepthbot",
            "stratid", "depthtop", "depthbot", "geology", "geoshort", stratigraphy."capacity", stratigraphy."development", "comment", geometry FROM stratigraphy JOIN obs_points USING (obsid)
            ) b'''.format(
            view_name, db_utils.rowid_string(dbconnection))
    try:
        cur.execute(sql)
    except:
        midvatten_utils.MessagebarAndLog.warning(log_msg=traceback.format_exc())

    if view_name not in list(db_utils.tables_columns(dbconnection=dbconnection).keys()):
        raise NotFoundError(ru(QCoreApplication.translate('strat_symbology',
            'Stratsymbology failed. The view %s could not be found. See log for info.'))%view_name)

    if dbconnection.dbtype == 'spatialite':
        cur.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1'''.format(view_name))

    view_name = 'w_lvls_last_geom'
    try:
        if dbconnection.dbtype == 'spatialite':
            cur.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' '''.format(view_name))
            cur.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
            cur.execute('''CREATE VIEW {view_name} AS 
                                    SELECT b.{rowid} AS rowid, a.obsid AS obsid, MAX(a.date_time) AS date_time,  a.meas AS meas,  a.level_masl AS level_masl, b.h_tocags AS h_tocags, b.geometry AS geometry 
                                    FROM w_levels AS a JOIN obs_points AS b using (obsid) 
                                    GROUP BY obsid;'''.format(
                **{'view_name': view_name, 'rowid': db_utils.rowid_string(dbconnection)}))
            cur.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1;'''.format(view_name))
        else:
            cur.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
            cur.execute('''CREATE OR REPLACE VIEW {view_name} AS SELECT a.obsid AS obsid, a.date_time AS date_time, a.meas AS meas, a.level_masl AS level_masl, c.h_tocags AS h_tocags, c.geometry AS geometry FROM w_levels AS a JOIN (SELECT obsid, max(date_time) as date_time FROM w_levels GROUP BY obsid) as b ON a.obsid=b.obsid and a.date_time=b.date_time JOIN obs_points AS c ON a.obsid=c.obsid;'''
                                 .format(**{'view_name': view_name}))
    except:
        midvatten_utils.MessagebarAndLog.warning(log_msg=traceback.format_exc())

    view_found = False
    if view_name in list(db_utils.tables_columns(dbconnection=dbconnection).keys()):
        if 'h_tocags' in db_utils.tables_columns(table=view_name,
                                                 dbconnection=dbconnection)[view_name]:
            view_found = True
    if not view_found:
        raise NotFoundError(ru(QCoreApplication.translate('strat_symbology',
            'Stratsymbology failed. The view %s could not be found. See log for info.'))%view_name)

    view_name = 'bedrock'
    try:
        cur.execute('''DROP VIEW IF EXISTS {}'''.format(view_name))
    except:
        midvatten_utils.MessagebarAndLog.warning(log_msg=traceback.format_exc())

    if dbconnection.dbtype == 'spatialite':
        cur.execute('''DELETE FROM views_geometry_columns WHERE view_name = '{}' '''.format(view_name))
    bergy = (
        '''
CREATE VIEW {view_name} AS
 SELECT a.{rowid},
    a.obsid,
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

    try:
        cur.execute(bergy)
    except:
        midvatten_utils.MessagebarAndLog.warning(log_msg=traceback.format_exc())

    if dbconnection.dbtype == 'spatialite':
        cur.execute('''INSERT OR IGNORE INTO views_geometry_columns SELECT '{}', 'geometry', 'rowid', 'obs_points', 'geometry', 1'''.format(view_name))

    if view_name not in list(db_utils.tables_columns(dbconnection=dbconnection).keys()):
        midvatten_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('strat_symbology',
            'Stratsymbology failed. The view %s could not be found. See log for info.')) % view_name)
        raise NotFoundError()


class RuleDiscrepancyError(Exception):
    pass


class StyleNotFoundError(Exception):
    pass


class NotFoundError(Exception):
    pass
