# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the sectionplot.

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-03-08
        copyright            : (C) 2016 by joskal (HenrikSpa)
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

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsApplication

import db_utils
import gui_utils
import mock
from mock import call
from nose.plugins.attrib import attr

import utils_for_tests


@attr(status='on')
class TestSectionPlot(utils_for_tests.MidvattenTestPostgisDbSv):
    """ The test doesn't go through the whole section plot unfortunately
    """
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def setUp(self):
        super(TestSectionPlot, self).setUp()
        self.midvatten.ms.settingsdict['secplotcustomsettings'] = ''
    
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def create_and_select_vlayer(self):
        self.qgs = QgsApplication([], True)
        self.qgs.initQgis()

        self.midvatten.ms.settingsdict['secplotdrillstop'] = u"%berg%"

        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')
        dbtype = db_utils.get_dbtype(dbconnection.dbtype)
        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', dbtype)
        features = self.vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()
        self.vlayer.setSelectedFeatures([featureid])

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_plot_section(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        self.create_and_select_vlayer()

        @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
        @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.drillstoplineEdit.setText(u"%berg%")
            self.myplot.draw_plot()
            self.selected_obsids = self.myplot.selected_obsids
        _test_plot_section(self)

        assert call.info(log_msg=u'Settings key secplotcustomsettings was empty.') in mock_messagebar.mock_calls
        assert call.info(log_msg=u'Settings {"Axes_set_xlabel": {"fontsize": 10, "xlabel": u"Distance along section"}, "Axes_set_xlim": None, "Axes_set_ylabel": {"fontsize": 10, "ylabel": u"Level, masl"}, "Axes_set_ylim": None, "Figure_subplots_adjust": {}, "dems_Axes_plot": {"DEFAULT": {"linestyle": "-", "linewidth": 1, "marker": "None"}}, "drillstop_Axes_plot": {"color": "black", "linestyle": "", "marker": "^", "markersize": 8}, "geology_Axes_bar": {"edgecolor": "black"}, "grid_Axes_grid": {"b": True, "color": "0.65", "linestyle": "-", "which": "both"}, "layer_Axes_annotate": {"bbox": {"alpha": 0.6, "boxstyle": "square,pad=0.05", "edgecolor": "white", "fc": "white"}, "fontsize": 9, "ha": "left", "textcoords": "offset points", "va": "center", "xytext": (5, 0, )}, "legend_Axes_legend": {"fontsize": 10, "framealpha": 1, "loc": 0}, "legend_Frame_set_facecolor": "1", "legend_Frame_set_fill": False, "legend_Text_set_fontsize": 10, "obsid_Axes_annotate": {"bbox": {"alpha": 0.4, "boxstyle": "square,pad=0.05", "edgecolor": "white", "fc": "white"}, "fontsize": 9, "ha": "center", "rotation": 0, "textcoords": "offset points", "va": "top", "xytext": (0, 10, )}, "obsid_Axes_bar": {"edgecolor": "black", "fill": False}, "plot_height": None, "plot_width": None, "ticklabels_Text_set_fontsize": {"fontsize": 10}, "wlevels_Axes_plot": {"DEFAULT": {"linestyle": "-", "linewidth": 1, "marker": "v", "markersize": 6}}} stored for key secplotcustomsettings.') in mock_messagebar.mock_calls

        assert self.myplot.drillstoplineEdit.text() == u'%berg%'
        assert utils_for_tests.create_test_string(self.myplot.selected_obsids) == "[u'P1' u'P2' u'P3']"
        assert len(mock_messagebar.mock_calls) == 4

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_plot_section_with_depth(self, mock_messagebar):
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section_with_depth(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
        _test_plot_section_with_depth(self)

        assert len(mock_messagebar.mock_calls) == 3

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_plot_section_with_w_levels(self, mock_messagebar):
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, u'w_levels')
            self.myplot.datetimetextEdit.append(u'2015')
            self.myplot.draw_plot()

        _test(self)

        assert len(mock_messagebar.mock_calls) == 4

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_plot_section_length_along_slope(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """

        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(2 0, 10 10)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(3 0)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(5 0)', 3006))''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(midvatten, vlayer, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            self.myplot = midvatten.myplot
            self.myplot.drillstoplineEdit.setText(u"%berg%")
            self.myplot.draw_plot()
        _test(self.midvatten, self.vlayer)

        test_string = utils_for_tests.create_test_string(self.myplot.LengthAlong)
        print(str(test_string))
        print(str(mock_messagebar.mock_calls))
        assert test_string == u"[ 0.          0.62469505  1.87408514]"
        assert len(mock_messagebar.mock_calls) == 4

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_plot_section_length_along(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(0 0, 1 0, 10 0)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(3 5)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(5 10)', 3006))''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(midvatten, vlayer, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            myplot = midvatten.myplot
            myplot.drillstoplineEdit.setText(u"%berg%")
            myplot.draw_plot()
            return myplot
        myplot = _test(self.midvatten, self.vlayer)

        test_string = utils_for_tests.create_test_string(myplot.LengthAlong)
        assert test_string == u"[ 1.  3.  5.]"
        assert len(mock_messagebar.mock_calls) == 4
        assert mock.call.info(log_msg=u'Hidden features, obsids and length along section:\nP1;P2;P3\\1.0;3.0;5.0') in mock_messagebar.mock_calls

    def tearDown(self):
        QgsMapLayerRegistry.instance().addMapLayer(self.vlayer)
        QgsMapLayerRegistry.instance().removeMapLayer(self.vlayer.id())
        super(self.__class__, self).tearDown()



