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
from builtins import str

from qgis.core import QgsProject, QgsVectorLayer

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
        self.vlayer.selectByIds(feature_ids)

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.drillstoplineEdit.setText("%berg%")
            self.myplot.draw_plot()
            self.selected_obsids = self.myplot.selected_obsids
        _test_plot_section(self)

        assert """call.info(log_msg='Settings {""" in str(mock_messagebar.mock_calls)

        assert self.myplot.drillstoplineEdit.text() == '%berg%'
        assert utils_for_tests.create_test_string(self.myplot.selected_obsids) == "['P1' 'P2' 'P3']"
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called
        print("self.myplot.p {} self.myplot.labels {}".format(str(self.myplot.p), str(self.myplot.labels)))
        assert len(self.myplot.p) - 1 == len(self.myplot.labels) # The bars should not be labeled, so there is one less label than plot.

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_no_linelayer_message(self, mock_messagebar):

        @mock.patch('sectionplot.SectionPlot.do_it')
        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
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

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_with_string_obsid(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash with string obsid """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(6720728 016569)', 3006))''')

        self.create_and_select_vlayer()
        print(str(self.vlayer.selectedFeatureCount()))
        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            self.myplot.drillstoplineEdit.setText("%berg%")
            self.myplot.draw_plot()
            self.selected_obsids = self.myplot.selected_obsids
        _test_plot_section(self)

        assert """call.info(log_msg='Settings {""" in str(mock_messagebar.mock_calls)
        assert self.myplot.drillstoplineEdit.text() == '%berg%'
        assert utils_for_tests.create_test_string(self.myplot.selected_obsids) == "['P1' 'P2' 'P3']"
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_with_depth(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section_with_depth(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
        _test_plot_section_with_depth(self)

        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_with_w_levels(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.myplot = self.midvatten.myplot
            gui_utils.set_combobox(self.myplot.wlvltableComboBox, 'w_levels')
            self.myplot.datetimetextEdit.append('2015')
            self.myplot.draw_plot()

        _test(self)

        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_length_along_slope(self, mock_messagebar):

        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(2 0, 10 10)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(3 0)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(5 0)', 3006))''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(midvatten, vlayer, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            self.myplot = midvatten.myplot
            self.myplot.drillstoplineEdit.setText("%berg%")
            self.myplot.draw_plot()
        _test(self.midvatten, self.vlayer)

        test_string = utils_for_tests.create_test_string(self.myplot.length_along)
        assert any([test_string == "[ 0.          0.62469505  1.87408514]",
                    test_string == "[0.         0.62469505 1.87408514]"])

        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_length_along(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LineString(0 0, 1 0, 10 0)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(3 5)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(5 10)', 3006))''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(midvatten, vlayer, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            myplot = midvatten.myplot
            myplot.drillstoplineEdit.setText("%berg%")
            myplot.draw_plot()
            return myplot
        myplot = _test(self.midvatten, self.vlayer)

        test_string = utils_for_tests.create_test_string(myplot.length_along)
        assert any([test_string == "[ 1.  3.  5.]", test_string == "[1. 3. 5.]"])
        assert mock.call.info(log_msg='Hidden features, obsids and length along section:\nP1;P2;P3\\1.0;3.0;5.0') in mock_messagebar.mock_calls
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_p_label_lengths(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
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
        print(str(self.myplot.labels))
        assert len(self.myplot.skipped_bars) == len(self.myplot.labels)
        assert len(self.myplot.skipped_bars) == 2
        #assert False

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_p_label_lengths_with_geology(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 1, 0, 1, 'sand')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('P1', 2, 1, 2, 'gravel')''')

        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
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
        print(str(self.myplot.labels))
        assert len(self.myplot.skipped_bars) == len(self.myplot.labels)
        assert len(self.myplot.skipped_bars) == 4

    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_plot_section_with_w_levels_animation(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-01 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P2', '2015-01-01 00:00:00', '17', '200', '183')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-02 00:00:00', '15', '200', '185')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas, h_toc, level_masl) VALUES ('P1', '2015-01-03 00:00:00', '15', '200', '185')''')
        self.create_and_select_vlayer()

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
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