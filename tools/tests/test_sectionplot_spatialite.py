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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str

from qgis.core import QgsProject, QgsVectorLayer, QgsApplication

import db_utils
import gui_utils
import mock
from mock import call
from nose.plugins.attrib import attr
from midvatten_utils import returnunicode as ru

import utils_for_tests


@attr(status='only')
class TestSectionPlot(utils_for_tests.MidvattenTestSpatialiteDbSv):
    """ The test doesn't go through the whole section plot unfortunately
    """
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self):
        super(TestSectionPlot, self).setUp()
        self.midvatten.ms.settingsdict['secplot_loaded_template'] = ''
        self.midvatten.ms.settingsdict['secplot_templates'] = ''
        self.midvatten.ms.settingsdict['secplotlocation'] = 0

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def create_and_select_vlayer(self):
        self.qgs = QgsApplication([], True)
        self.qgs.initQgis()

        self.midvatten.ms.settingsdict['secplotdrillstop'] = "%berg%"

        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')
        dbtype = db_utils.get_dbtype(dbconnection.dbtype)
        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', dbtype)
        features = self.vlayer.getFeatures()
        feature_ids = [feature.id() for feature in features]
        self.vlayer.selectByIds([feature_ids[0]])

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_plot_section(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P3', ST_GeomFromText('POINT(6720728 016569)', 3006))''')

        self.create_and_select_vlayer()

        @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = ('P1', 'P2', 'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
            self.midvatten.ms = self.ms
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
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_plot_section_with_depth(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P2', ST_GeomFromText('POINT(6720727 016568)', 3006), '1')''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry, length) VALUES ('P3', ST_GeomFromText('POINT(6720727 016568)', 3006), NULL)''')

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
        _test(self)

        print(str(mock_messagebar.mock_calls))
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
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

        print(str(mock_messagebar.mock_calls))
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_plot_section_length_along_slope(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """

        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(2 0, 10 10)', 3006))''')
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

        test_string = utils_for_tests.create_test_string(self.myplot.LengthAlong)
        print(str(test_string))
        print(str(mock_messagebar.mock_calls))
        assert any([test_string == "[ 0.          0.62469505  1.87408514]",
                    test_string == "[0.         0.62469505 1.87408514]"])
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_plot_section_length_along(self, mock_messagebar):
        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid, geometry) VALUES ('L1', ST_GeomFromText('LINESTRING(0 0, 1 0, 10 0)', 3006))''')
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

        test_string = utils_for_tests.create_test_string(myplot.LengthAlong)
        assert any([test_string == "[ 1.  3.  5.]", test_string == "[1. 3. 5.]"])
        assert mock.call.info(log_msg='Hidden features, obsids and length along section:\nP1;P2;P3\\1.0;3.0;5.0') in mock_messagebar.mock_calls
        assert not mock_messagebar.warning.called
        assert not mock_messagebar.critical.called

    def tearDown(self):
        QgsProject.instance().addMapLayer(self.vlayer)
        QgsProject.instance().removeMapLayer(self.vlayer.id())
        super(self.__class__, self).tearDown()



