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
from __future__ import absolute_import

import re
from builtins import str

import mock

from mock import call
from nose.plugins.attrib import attr
from qgis.core import QgsProject, QgsVectorLayer

from midvatten.tools.utils import db_utils, gui_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.utils.midvatten_utils import anything_to_string_representation


@attr(status='on')
class TestSectionPlot(utils_for_tests.MidvattenTestPostgisDbSv):
    """ The test doesn't go through the whole section plot unfortunately
    """

    def setUp(self):
        super(TestSectionPlot, self).setUp()
        self.midvatten.ms.settingsdict['secplot_loaded_template'] = ''
        self.midvatten.ms.settingsdict['secplot_templates'] = ''
        self.midvatten.ms.settingsdict['secplotlocation'] = 0

    def create_and_select_vlayer(self):
        self.midvatten.ms.settingsdict['secplotdrillstop'] = "%berg%"
        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')
        dbtype = db_utils.get_dbtype(dbconnection.dbtype)
        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', dbtype)
        QgsProject.instance().addMapLayer(self.vlayer)
        features = self.vlayer.getFeatures()
        feature_ids = [feature.id() for feature in features]
        print(str(feature_ids))
        self.vlayer.selectByIds(feature_ids)

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs, length, drillstop) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 10, 'berg')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs, length, drillstop) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), 3, 20, NULL)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs, length, drillstop) VALUES ('P3', ST_GeomFromText('POINT(6720728 016569)', 3006), 4, 30, NULL)''')

        self.create_and_select_vlayer()
        print(str(self.vlayer.selectedFeatureCount()))

        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.drillstoplineEdit.setText("%berg%")
            self.myplot.draw_plot()
        _test_plot_section(self)

        assert """call.info(log_msg='Settings {""" in str(mock_messagebar.mock_calls)
        assert self.myplot.drillstoplineEdit.text() == '%berg%'
        assert anything_to_string_representation(list(self.myplot.obsids_x_position.keys())) == '''["P1", "P2", "P3"]'''
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called
        #print(str(mock_messagebar.mock_calls))
        print("self.myplot.p {} self.myplot.get_legend_items_labels()[1] {}".format(str(self.myplot.p),
                                                              str(self.myplot.get_legend_items_labels()[1])))
        assert len(self.myplot.get_legend_items_labels()[0]) == len(self.myplot.get_legend_items_labels()[1])
        assert len(self.myplot.p) - 1 == len(self.myplot.get_legend_items_labels()[0])  # The bars should not be labeled, so there is one less label than plot.

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_no_linelayer_message(self, mock_messagebar):

        @mock.patch('midvatten.tools.sectionplot.SectionPlot.do_it')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_sectionplot):
            mock_layer = mock.Mock(spec=QgsVectorLayer)
            mock_iface.mapCanvas.return_value.currentLayer.return_value = mock_layer
            mock_layer.selectedFeatureCount.return_value = 2
            mock_geom = mock.Mock()
            mock_geom.wkbType.return_value = 'test'
            mock_feature = mock.Mock()
            mock_feature.geometry.return_value = mock_geom
            mock_layer.getFeatures.return_value = [mock_feature]
            self.midvatten.plot_section()

        _test(self)
        assert call.info(bar_msg='No line layer was selected. The stratigraphy bars will be lined up from south-north or west-east and no DEMS will be plotted.', duration=10) in mock_messagebar.mock_calls
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_with_string_obsid(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash with string obsid """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 1)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P3', ST_GeomFromText('POINT(6720728 016569)', 3006), 3)''')

        self.create_and_select_vlayer()
        print(str(self.vlayer.selectedFeatureCount()))
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.drillstoplineEdit.setText("%berg%")
            self.myplot.draw_plot()
        _test_plot_section(self)

        assert """call.info(log_msg='Settings {""" in str(mock_messagebar.mock_calls)
        assert self.myplot.drillstoplineEdit.text() == '%berg%'
        assert anything_to_string_representation(list(self.myplot.obsids_x_position.keys())) == '''["P1", "P2", "P3"]'''
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_with_depth(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1', 3)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL, 4)''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_messagebar, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            print(str(mock_messagebar.mock_calls))
            self.myplot = self.midvatten.myplot
        _test(self)

        print(str(mock_messagebar.mock_calls))
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_with_w_levels(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1', 3)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL, 4)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')

        self.create_and_select_vlayer()
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.draw_plot()

        _test(self)

        print(str(mock_messagebar.mock_calls))
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_with_w_levels_duplicate_label(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs, drillstop) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 2, 'berg')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs, drillstop) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1', 3, NULL)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs, drillstop) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL, 4, NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')

        self.create_and_select_vlayer()
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.secplot_templates.loaded_template['wlevels_Axes_plot'] = {'2015': {'label': '1', 'linestyle': '-', 'linewidth': 1, 'marker': 'v', 'markersize': 6, 'zorder': 8},
                                                                                  '2015_2': {'label': '2', 'linestyle': '-', 'linewidth': 1, 'marker': 'v', 'markersize': 6, 'zorder': 8},
                                                                                  'DEFAULT': {'label': 'DEFAULT', 'linestyle': '-', 'linewidth': 1, 'marker': 'v', 'markersize': 6, 'zorder': 8}}
            self.myplot.draw_plot()

        _test(self)

        print(str(mock_messagebar.mock_calls))
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called
        labels = [p.get_label() for p in self.myplot.p]
        print(str(labels))
        assert anything_to_string_representation(labels) == '''["1", "2", "drillstop like %berg%", "frame"]'''
        assert anything_to_string_representation(self.myplot.water_level_labels_duplicate_check) == '''["2015", "2015_2"]'''

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_length_along_slope(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """

        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(2 0, 10 10)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P1', ST_GeomFromText('POINT(1 0)', 3006), 1)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P2', ST_GeomFromText('POINT(3 0)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P3', ST_GeomFromText('POINT(5 0)', 3006), 3)''')

        self.create_and_select_vlayer()
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(midvatten, vlayer, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            self.myplot = midvatten.myplot
            self.myplot.drillstoplineEdit.setText("%berg%")
            self.myplot.draw_plot()
        _test(self.midvatten, self.vlayer)

        test_string = utils_for_tests.create_test_string({k: round(v, 6)
                                                          for k, v in self.myplot.obsids_x_position.items()})
        print(str(test_string))
        print(str(mock_messagebar.mock_calls))
        assert test_string == '{P1: 0.0, P2: 0.624695, P3: 1.874085}'
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_length_along(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(0 0, 1 0, 10 0)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P1', ST_GeomFromText('POINT(1 0)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P2', ST_GeomFromText('POINT(3 5)', 3006), 3)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs) VALUES ('P3', ST_GeomFromText('POINT(5 10)', 3006), 4)''')

        self.create_and_select_vlayer()
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(midvatten, vlayer, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            myplot = midvatten.myplot
            myplot.drillstoplineEdit.setText("%berg%")
            myplot.draw_plot()
            return myplot
        myplot = _test(self.midvatten, self.vlayer)

        test_string = utils_for_tests.create_test_string(myplot.obsids_x_position)
        assert test_string == "{P1: 1.0, P2: 3.0, P3: 5.0}"
        assert mock.call.info(log_msg='Hidden features, obsids and length along section:\nP1;P2;P3\\1.0;3.0;5.0') in mock_messagebar.mock_calls
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_p_label_lengths(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, drillstop) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 'berg')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')

        self.create_and_select_vlayer()
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.Stratigraphy_radioButton.setChecked(True)
            self.myplot.Legend_checkBox.setChecked(True)
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.draw_plot()
        _test(self)

        print(str(mock_messagebar.mock_calls))
        print(str(self.myplot.p))
        assert len(self.myplot.get_legend_items_labels()[0]) == 2
        #assert False

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_p_label_lengths_with_geology(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, drillstop) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 'berg')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 1, 0, 1, 'sand')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 2, 1, 2, 'gravel')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.Stratigraphy_radioButton.setChecked(True)
            self.myplot.Legend_checkBox.setChecked(True)
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.draw_plot()

        _test(self)

        print(str(mock_messagebar.mock_calls))
        print(str(self.myplot.p))
        assert len(self.myplot.get_legend_items_labels()[0]) == len(self.myplot.get_legend_items_labels()[1])
        print(str(self.myplot.get_legend_items_labels()[1]))
        assert len(self.myplot.get_legend_items_labels()[0]) == 4

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_p_label_lengths_with_geology_changed_label(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, drillstop) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 'berg')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 1, 0, 1, 'sand')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 2, 1, 2, 'gravel')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.secplot_templates.loaded_template['geology_Axes_bar'] = {'sand': {'label': 'sandtest', 'edgecolor': 'black', 'zorder': 5},
                                                                                  'grus': {'label': 'grustest', 'edgecolor': 'black', 'zorder': 5},
                                                                                  'DEFAULT': {'edgecolor': 'black', 'zorder': 5}}
            print("before: " + str(self.myplot.secplot_templates.loaded_template['geology_Axes_bar']))
            self.myplot.Stratigraphy_radioButton.setChecked(True)
            self.myplot.Legend_checkBox.setChecked(True)
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')

            self.myplot.draw_plot()

        _test(self)

        #print(str(mock_messagebar.mock_calls))
        #print(str(self.myplot.p))
        labels = [p.get_label() for p in self.myplot.p]
        assert len(self.myplot.get_legend_items_labels()[0]) == len(self.myplot.get_legend_items_labels()[1])
        assert len(self.myplot.get_legend_items_labels()[1]) == 4
        assert anything_to_string_representation(labels) == '''["sandtest", "grustest", "2015", "drillstop like %berg%", "frame"]'''
        assert anything_to_string_representation(self.myplot.water_level_labels_duplicate_check) == '''["2015"]'''

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_with_w_levels_animation(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2, 21)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1', 22)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length, h_gs) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL, 23)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-02 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-03 00:00:00', '15', '200', '185')''')
        self.create_and_select_vlayer()

        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.interactive_groupbox.setChecked(True)
            #self.myplot.datetimetextEdit.append('2015')

            self.myplot.draw_plot()
            return self.myplot

        myplot = _test(self)
        print(str(mock_messagebar.mock_calls))
        assert myplot.interactive_groupbox.isChecked()
        assert len(myplot.figure.axes) > 1
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_obsids(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(1 0, 4 0)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs, length) VALUES ('P1', ST_GeomFromText('POINT(1 1)', 3006), 50, 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_gs, length) VALUES ('P2', ST_GeomFromText('POINT(2 2)', 3006), 70, '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, h_toc,length) VALUES ('P3', ST_GeomFromText('POINT(4 4)', 3006), 90, NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 1, 0, 1, 'sand')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P3', 2, 1, 2, 'gravel')''')

        self.create_and_select_vlayer()
        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.draw_plot()

        _test(self)
        #print(str(self.myplot.obsid_annotation))
        print(str(self.myplot.obsid_annotation))
        #print(str(mock_messagebar.mock_calls))
        assert str(self.myplot.obsid_annotation) == '''{'P1': (0.0, 50.0), 'P3': (3.0, 90.0), 'P2': (1.0, 183.0)}'''
        assert mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten.tools.sectionplot.common_utils.MessagebarAndLog')
    def test_plot_section_h_gs_h_toc_failed(self, mock_messagebar):
        db_utils.sql_alter_db(
            '''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(
            '''INSERT INTO obs_points (obsid, h_gs, h_toc, geometry, length) VALUES ('P1', NULL, 123, ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db(
            '''INSERT INTO obs_points (obsid, h_gs, h_toc, geometry, length) VALUES ('P2', NULL, NULL, ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db(
            '''INSERT INTO obs_points (obsid, h_gs, h_toc, geometry, length) VALUES ('P3', 456, 789, ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db(
            '''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 1, 0, 1, 'sand')''')
        db_utils.sql_alter_db(
            '''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 2, 1, 2, 'gravel')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten.tools.sectionplot.common_utils.find_layer')
        @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames, mock_findlayer):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_findlayer.return_value.isEditable.return_value = False
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.Stratigraphy_radioButton.setChecked(True)
            self.myplot.Legend_checkBox.setChecked(True)
            self.myplot.draw_plot()

        _test(self)

        print(str(mock_messagebar.mock_calls))
        print(str(self.myplot.p))

        pattern_obsids = {'''Obsid {}: using h_gs '[0-9None]+' failed, using 'h_toc' instead.''': ['P1'],
                          '''Obsid {}: using h_gs None or h_toc None failed, using 0 instead.''': ['P2']}
        for p in ['P1', 'P2', 'P3']:
            for pattern, obsids in pattern_obsids.items():
                patt = pattern.format(p)
                m = re.findall(patt, str(mock_messagebar.mock_calls))
                print(str(m))
                print(patt)
                if p in obsids:
                    assert m
                else:
                    assert not m
