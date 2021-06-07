# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the stratigraphy plot.

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2017-10-17
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
from __future__ import print_function

from builtins import str

import mock
from nose.plugins.attrib import attr
from qgis.core import QgsProject, QgsVectorLayer

from midvatten.tools.utils import common_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.stratigraphy import Stratigraphy


@attr(status='on')
class TestStratigraphy(utils_for_tests.MidvattenTestPostgisDbSv):

    def create_and_select_vlayer(self):
        self.midvatten.ms.settingsdict['secplotdrillstop'] = "%berg%"
        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource('', 'obs_points', 'geometry', '', 'obsid')
        dbtype = db_utils.get_dbtype(dbconnection.dbtype)
        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', dbtype)
        QgsProject.instance().addMapLayer(self.vlayer)

        features = self.vlayer.getFeatures()
        feature_ids = [feature.id() for feature in features]
        self.vlayer.selectByIds(feature_ids)
        print("1. Valid vlayer '{}'".format(self.vlayer.isValid()))
        print("2. feature_ids: " + str(feature_ids))
        print("3. QgsVectorLayer.selectedFeatureIds: " + str(self.vlayer.selectedFeatureIds()))
        print("4. QgsVectorLayer.getSelectedFeatures: " + str([x.id() for x in self.vlayer.getSelectedFeatures()]))
        print("5. QgsVectorLayer.getFeature(): " + str([self.vlayer.getFeature(x).id() for x in feature_ids]))
        print("6. QgsVectorLayer.getFeature() type: " + str([str(type(self.vlayer.getFeature(x))) for x in feature_ids]))
        print("7. QgsVectorLayer.getFeatures(): " + str([x.id() for x in self.vlayer.getFeatures(feature_ids)]))

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.stratigraphy.common_utils.pop_up_info', autospec=True)
    def test_stratigraphy(self, mock_skippopup, mock_messagebar):
        """
        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('2', 10, ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('3', 20, ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')

        self.create_and_select_vlayer()

        #print(str(self.vlayer.isValid()))
        #print(str(db_utils.sql_load_fr_db('select * from obs_points')))
        #print(str(db_utils.sql_load_fr_db('select * from stratigraphy')))
        dlg = Stratigraphy(self.iface, self.vlayer, self.midvatten.ms.settingsdict)
        #print(str(mock_messagebar.mock_calls))
        #print(str(mock_skippopup.mock_calls))
        dlg.showSurvey()
        test = common_utils.anything_to_string_representation(dlg.data)
        test_survey = common_utils.anything_to_string_representation(repr(dlg.data['1']))
        test_strata = common_utils.anything_to_string_representation(
            common_utils.returnunicode(dlg.data['1'].strata, keep_containers=True))

        assert len(mock_skippopup.mock_calls) == 0
        print(str(mock_messagebar.mock_calls))
        assert len(mock_messagebar.mock_calls) == 0
        assert test == """{"1": SURVEY('1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')}"""
        assert test_survey == '''"SURVEY('1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')"'''
        print("test_strata: " + test_strata)
        assert test_strata == '''["strata(1, '3', 'sand', 'sand', 0.000000-1.000000)", "strata(2, '3', 'morän', 'moran', 1.000000-4.500000)"]'''

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.stratigraphy.common_utils.pop_up_info', autospec=True)
    def test_stratigraphy_with_other_obsid_numbers(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('8', 5, ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('9', 10, ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('10', 20, ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('8', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('8', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')
        self.create_and_select_vlayer()

        dlg = Stratigraphy(self.iface, self.vlayer, self.midvatten.ms.settingsdict)

        dlg.showSurvey()
        print(str(mock_skippopup.mock_calls))
        test = common_utils.anything_to_string_representation(dlg.data)
        test_survey = common_utils.anything_to_string_representation(repr(dlg.data['8']))
        test_strata = common_utils.anything_to_string_representation(
            common_utils.returnunicode(dlg.data['8'].strata, keep_containers=True))

        assert len(mock_skippopup.mock_calls) == 0
        assert len(mock_messagebar.mock_calls) == 0
        assert test == """{"8": SURVEY('8', 5.000000, '<QgsPointXY: POINT(633466 711659)>')}"""
        assert test_survey == '''"SURVEY('8', 5.000000, '<QgsPointXY: POINT(633466 711659)>')"'''
        print("Test strata " + test_strata)
        assert test_strata == '''["strata(1, '3', 'sand', 'sand', 0.000000-1.000000)", "strata(2, '3', 'morän', 'moran', 1.000000-4.500000)"]'''

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.stratigraphy.common_utils.pop_up_info', autospec=True)
    def test_stratigraphy_with_string_obsid(self, mock_skippopup, mock_messagebar):
        """
        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('P1', 5, ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('P2', 10, ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('P3', 20, ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('P1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('P1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')

        self.create_and_select_vlayer()

        print(str(self.vlayer.isValid()))
        print(str(db_utils.sql_load_fr_db('select * from obs_points')))
        print(str(db_utils.sql_load_fr_db('select * from stratigraphy')))
        dlg = Stratigraphy(self.iface, self.vlayer, self.midvatten.ms.settingsdict)
        print(str(mock_messagebar.mock_calls))
        print(str(mock_skippopup.mock_calls))
        dlg.showSurvey()
        test = common_utils.anything_to_string_representation(dlg.data)
        test_survey = common_utils.anything_to_string_representation(repr(dlg.data['P1']))
        test_strata = common_utils.anything_to_string_representation(
            common_utils.returnunicode(dlg.data['P1'].strata, keep_containers=True))

        assert len(mock_skippopup.mock_calls) == 0
        print(str(mock_messagebar.mock_calls))
        assert len(mock_messagebar.mock_calls) == 0
        assert test == """{"P1": SURVEY('P1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')}"""
        assert test_survey == '''"SURVEY('P1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')"'''
        assert test_strata == '''["strata(1, '3', 'sand', 'sand', 0.000000-1.000000)", "strata(2, '3', 'morän', 'moran', 1.000000-4.500000)"]'''

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.stratigraphy.common_utils.pop_up_info', autospec=True)
    def test_stratigraphy_gap(self, mock_skippopup, mock_messagebar):
        """
        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('2', 10, ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('3', 20, ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 2, 4.5, 'morän', 'morän', '3', 'j')''')

        self.create_and_select_vlayer()

        print(str(self.vlayer.isValid()))
        print(str(db_utils.sql_load_fr_db('select * from obs_points')))
        print(str(db_utils.sql_load_fr_db('select * from stratigraphy')))
        dlg = Stratigraphy(self.iface, self.vlayer, self.midvatten.ms.settingsdict)
        print(str(mock_messagebar.mock_calls))
        print(str(mock_skippopup.mock_calls))
        dlg.showSurvey()
        test = common_utils.anything_to_string_representation(dlg.data)
        test_survey = common_utils.anything_to_string_representation(repr(dlg.data['1']))
        test_strata = common_utils.anything_to_string_representation(
            common_utils.returnunicode(dlg.data['1'].strata, keep_containers=True))

        assert len(mock_skippopup.mock_calls) == 0
        assert len(mock_messagebar.mock_calls) == 0
        assert test == """{"1": SURVEY('1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')}"""
        assert test_survey == '''"SURVEY('1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')"'''
        assert test_strata == '''["strata(1, '3', 'sand', 'sand', 0.000000-1.000000)", "strata(2, '', '', '', 1.000000-2.000000)", "strata(3, '3', 'morän', 'moran', 2.000000-4.500000)"]'''

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.stratigraphy.common_utils.pop_up_info', autospec=True)
    def test_stratigraphy_missing_h_gs(self, mock_skippopup, mock_messagebar):
        """
        
        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, h_toc, geometry) VALUES ('2', NULL, 10, ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('3', ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('2', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('2', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('3', 1, 0, 2, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('3', 2, 2, 6, 'morän', 'morän', '3', 'j')''')
        self.create_and_select_vlayer()

        dlg = Stratigraphy(self.iface, self.vlayer, self.midvatten.ms.settingsdict)

        dlg.showSurvey()
        test = common_utils.anything_to_string_representation(dlg.data)
        test_survey = common_utils.anything_to_string_representation(repr(dlg.data['1']))
        test_strata = common_utils.anything_to_string_representation(
            common_utils.returnunicode(dlg.data['1'].strata, keep_containers=True))

        assert len(mock_skippopup.mock_calls) == 1
        print(str(mock_skippopup.mock_calls))
        print(str(mock_messagebar.mock_calls))
        assert mock_skippopup.mock_calls == [mock.call('Warning, h_gs is missing. See messagebar.')]
        assert mock_messagebar.mock_calls == [mock.call.warning(bar_msg="Obsid 2: using h_gs '' failed, using 'h_toc' instead.", duration=90, log_msg='False'),
                                              mock.call.warning(bar_msg="Obsid 3: using h_gs '' failed, using '-1' instead.", duration=90, log_msg='False')]
        print("test: " + test)
        assert test == """{"1": SURVEY('1', 5.000000, '<QgsPointXY: POINT(633466 711659)>'), "2": SURVEY('2', 10.000000, '<QgsPointXY: POINT(6720727 16568)>'), "3": SURVEY('3', -1.000000, '<QgsPointXY: POINT(6720728 16569)>')}"""
        print("test_survey " + test_survey)
        assert test_survey == '''"SURVEY('1', 5.000000, '<QgsPointXY: POINT(633466 711659)>')"'''
        print("Test strata " + test_strata)
        assert test_strata == '''["strata(1, '3', 'sand', 'sand', 0.000000-1.000000)", "strata(2, '3', 'morän', 'moran', 1.000000-4.500000)"]'''