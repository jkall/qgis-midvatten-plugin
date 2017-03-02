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

 Notes:
     * The uri = QgsDataSourceURI() doesn't reset unless given a new database
     name (for some reason). This is the reason that the section plot tests
     has to be split up into several classes.



"""
import db_utils
import utils_for_tests
import midvatten_utils as utils
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from functools import partial
from mock import mock_open, patch
from multiprocessing import Pool, Process
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
from midvatten.midvatten import midvatten
import os
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsVectorLayer, QgsGeometry, QgsFeature, QgsApplication
import qgis
import sectionplot
from PyQt4 import QtCore

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
TEMP_DB_PATH2 = u'/tmp/tmp_midvatten_temp_db2.sqlite'
TEMP_DB_PATH3 = u'/tmp/tmp_midvatten_temp_db3.sqlite'
TEMP_DB_PATH4 = u'/tmp/tmp_midvatten_temp_db4.sqlite'

MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]


class TestSectionPlot(object):
    """ The test doesn't go through the whole section plot unfortunately
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    crs_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.midvatten.ms.settingsareloaded = True

    def tearDown(self):
        #Delete database
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        try:
            self.midvatten.myplot = None
        except:
            pass
        try:
            self.midvatten.myplot.close()
        except:
            pass

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_plot_section(self, mock_qgsproject_instance):
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db(u'''insert into obs_lines (obsid, geometry) values ("L1", GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P1", GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P2", GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P3", GeomFromText('POINT(6720728 016569)', 3006))''')

        uri = QgsDataSourceURI()
        uri.setDatabase(TEMP_DB_PATH)
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')

        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', 'spatialite')
        features = self.vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()

        self.vlayer.setSelectedFeatures([featureid])

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

        assert self.myplot.drillstoplineEdit.text() == u'%berg%'
        assert utils_for_tests.create_test_string(self.myplot.selected_obsids) == "['P1' 'P2' 'P3']"

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_plot_section_with_depth(self, mock_qgsproject_instance):
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT
        db_utils.sql_alter_db(u'''insert into obs_lines (obsid, geometry) values ("L1", GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry, length) values ("P1", GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry, length) values ("P2", GeomFromText('POINT(6720727 016568)', 3006), "1")''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry, length) values ("P3", GeomFromText('POINT(6720727 016568)', 3006), NULL)''')

        uri = QgsDataSourceURI()
        uri.setDatabase(TEMP_DB_PATH)
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')

        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', 'spatialite')
        features = self.vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()

        self.vlayer.setSelectedFeatures([featureid])

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section_with_depth(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
        _test_plot_section_with_depth(self)

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_plot_section_with_w_levels(self, mock_qgsproject_instance):
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT
        db_utils.sql_alter_db(u'''insert into obs_lines (obsid, geometry) values ("L1", GeomFromText('LINESTRING(633466.711659 6720684.24498, 633599.530455 6720727.016568)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry, length) values ("P1", GeomFromText('POINT(633466 711659)', 3006), 2)''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry, length) values ("P2", GeomFromText('POINT(6720727 016568)', 3006), "1")''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry, length) values ("P3", GeomFromText('POINT(6720727 016568)', 3006), NULL)''')
        db_utils.sql_alter_db(u'''insert into w_levels (obsid, date_time, meas, h_toc, level_masl) values ("P1", "2015-01-01 00:00:00", "15", "200", "185")''')
        db_utils.sql_alter_db(u'''insert into w_levels (obsid, date_time, meas, h_toc, level_masl) values ("P2", "2015-01-01 00:00:00", "17", "200", "183")''')

        uri = QgsDataSourceURI()
        uri.setDatabase(TEMP_DB_PATH)
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')

        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', 'spatialite')
        features = self.vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()

        self.vlayer.setSelectedFeatures([featureid])

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test_plot_section_with_depth(self, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = self.vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.plot_section()
        _test_plot_section_with_depth(self)

        
class TestSectionPlot2(object):
    """ The test doesn't go through the whole section plot unfortunately
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    crs_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH2
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH2)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.midvatten.ms.settingsareloaded = True

    def tearDown(self):
        #Delete database
        try:
            os.remove(TEMP_DB_PATH2)
        except OSError:
            pass
        try:
            self.midvatten.myplot = None
        except:
            pass
        try:
            self.midvatten.myplot.close()
        except:
            pass

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_plot_section_length_along_slope(self, mock_qgsproject_instance):
        mock_qgsproject_instance.return_value.readEntry = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH2]}[(x, y)]

        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db(u'''insert into obs_lines (obsid, geometry) values ("L1", GeomFromText('LINESTRING(2 0, 10 10)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P1", GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P2", GeomFromText('POINT(3 0)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P3", GeomFromText('POINT(5 0)', 3006))''')

        uri = QgsDataSourceURI()
        uri.setDatabase(TEMP_DB_PATH2)
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')

        vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', 'spatialite')
        features = vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()

        vlayer.setSelectedFeatures([featureid])

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
        myplot = _test(self.midvatten, vlayer)

        test_string = utils_for_tests.create_test_string(myplot.LengthAlong)
        assert test_string == u"[ 0.          0.62469505  1.87408514]"


class TestSectionPlot3(object):
    """ The test doesn't go through the whole section plot unfortunately
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    crs_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH3
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH3)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.midvatten.ms.settingsareloaded = True

    def tearDown(self):
        #Delete database
        try:
            os.remove(TEMP_DB_PATH3)
        except OSError:
            pass
        try:
            self.midvatten.myplot = None
        except:
            pass
        try:
            self.midvatten.myplot.close()
        except:
            pass

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_plot_section_length_along(self, mock_qgsproject_instance):
        mock_qgsproject_instance.return_value.readEntry = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH3]}[(x, y)]

        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db(u'''insert into obs_lines (obsid, geometry) values ("L1", GeomFromText('LINESTRING(0 0, 1 0, 10 0)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P1", GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P2", GeomFromText('POINT(3 5)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P3", GeomFromText('POINT(5 10)', 3006))''')

        uri = QgsDataSourceURI()
        uri.setDatabase(TEMP_DB_PATH3)
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')

        vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', 'spatialite')
        features = vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()

        vlayer.setSelectedFeatures([featureid])

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
        myplot = _test(self.midvatten, vlayer)

        test_string = utils_for_tests.create_test_string(myplot.LengthAlong)
        assert test_string == u"[ 1.  3.  5.]"
        
        
class __TestSectionPlot4(object):
    """ The test doesn't go through the whole section plot unfortunately
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    crs_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH4
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        self.midvatten2 = midvatten(self.iface)
        self.midvatten3 = midvatten(self.iface)
        self.midvatten4 = midvatten(self.iface)

        try:
            os.remove(TEMP_DB_PATH4)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.midvatten.ms.settingsareloaded = True
        self.midvatten2.ms.settingsareloaded = True
        self.midvatten3.ms.settingsareloaded = True
        self.midvatten4.ms.settingsareloaded = True
        self.midvattens = [self.midvatten, self.midvatten2, self.midvatten3, self.midvatten4]

    def tearDown(self):
        #Delete database
        try:
            os.remove(TEMP_DB_PATH4)
        except OSError:
            pass
        try:
            self.midvatten.myplot = None
        except:
            pass
        try:
            self.midvatten.myplot.close()
        except:
            pass

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_multiple_plots(self, mock_qgsproject_instance):
        mock_qgsproject_instance.return_value.readEntry = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH4]}[(x, y)]

        """For now, the test only initiates the plot. Check that it does not crash """
        db_utils.sql_alter_db(u'''insert into obs_lines (obsid, geometry) values ("L1", GeomFromText('LINESTRING(0 0, 1 0, 10 0)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P1", GeomFromText('POINT(1 0)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P2", GeomFromText('POINT(3 5)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P3", GeomFromText('POINT(5 10)', 3006))''')

        uri = QgsDataSourceURI()
        uri.setDatabase(TEMP_DB_PATH4)
        uri.setDataSource('', 'obs_lines', 'geometry', '', 'obsid')

        vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', 'spatialite')
        features = vlayer.getFeatures()
        for feature in features:
            featureid = feature.id()

        vlayer.setSelectedFeatures([featureid])

        @mock.patch('midvatten_utils.getselectedobjectnames', autospec=True)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, midvatten, vlayer, mock_iface, mock_getselectedobjectnames):
            mock_iface.mapCanvas.return_value.currentLayer.return_value = vlayer
            mock_getselectedobjectnames.return_value = (u'P1', u'P2', u'P3')
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            midvatten.plot_section()
            myplot = midvatten.myplot
            myplot.drillstoplineEdit.setText(u"%berg%")
            myplot.draw_plot()
            return myplot

        def worker(i):
            _test(self, self.midvattens[i], vlayer)

        jobs = []
        for i in xrange(4):
            p = Process(target=lambda: worker(i))
            jobs.append(p)
            p.start()
        p.join()

        print("Test worked")


