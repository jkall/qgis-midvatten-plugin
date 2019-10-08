# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests creating vectorlayer from spatialite.
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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from qgis.core import QgsProject, QgsVectorLayer

import db_utils
import midvatten_utils as utils
import mock
from nose.plugins.attrib import attr
from stratigraphy import Stratigraphy
import string

import utils_for_tests


@attr(status='on')
class TestVectorlayer(utils_for_tests.MidvattenTestSpatialiteDbSv):

    def create_vlayer(self, no_print=False):
        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource('', 'obs_points', 'geometry', '', 'obsid')
        dbtype = db_utils.get_dbtype(dbconnection.dbtype)
        self.vlayer = QgsVectorLayer(uri.uri(), 'TestLayer', dbtype)
        QgsProject.instance().addMapLayer(self.vlayer)

        features = self.vlayer.getFeatures()
        feature_ids = [feature.id() for feature in features]

        if not no_print:
            print("1. Valid vlayer '{}'".format(self.vlayer.isValid()))
            print("2. feature_ids: " + str(feature_ids))
            print("5. QgsVectorLayer.getFeature(): " + str([self.vlayer.getFeature(x).id() for x in feature_ids]))
            print("6. QgsVectorLayer.getFeature() type: " + str([str(type(self.vlayer.getFeature(x))) for x in feature_ids]))
            print("7. QgsVectorLayer.getFeatures(): " + str([x.id() for x in self.vlayer.getFeatures(feature_ids)]))
            print("8. QgsVectorLayer.featureCount(): " + str(self.vlayer.featureCount()))

    def select_features(self, feature_ids=None, no_print=True):
        if feature_ids is None:
            features = self.vlayer.getFeatures()
            feature_ids = [feature.id() for feature in features]
        self.vlayer.selectByIds(feature_ids)

        if not no_print:
            print("3. QgsVectorLayer.selectedFeatureIds: " + str(self.vlayer.selectedFeatureIds()))
            print("4. QgsVectorLayer.getSelectedFeatures: " + str([x.id() for x in self.vlayer.getSelectedFeatures()]))

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('stratigraphy.utils.pop_up_info', autospec=True)
    def test_vlayer(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        for obsid in [1, 2, 3]:
            db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ({})'''.format(str(obsid)))

        self.create_vlayer()
        self.select_features()
        feature_ids = [feature.id() for feature in self.vlayer.getFeatures()]

        reference_ids = (1, 2, 3)
        assert self.vlayer.isValid()
        assert len(feature_ids) == len(reference_ids)
        assert tuple(feature_ids) == reference_ids
        assert tuple(sorted([x for x in self.vlayer.selectedFeatureIds()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getSelectedFeatures()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getFeatures(feature_ids)])) == reference_ids


    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('stratigraphy.utils.pop_up_info', autospec=True)
    def test_vlayer_other_ints_ids(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        for obsid in [4, 5, 6]:
            db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ({})'''.format(str(obsid)))

        self.create_vlayer()
        self.select_features()
        feature_ids = [feature.id() for feature in self.vlayer.getFeatures()]

        reference_ids = (1, 2, 3)
        assert self.vlayer.isValid()
        assert len(feature_ids) == len(reference_ids)
        assert tuple(feature_ids) == reference_ids
        assert tuple(sorted([x for x in self.vlayer.selectedFeatureIds()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getSelectedFeatures()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getFeatures(feature_ids)])) == reference_ids


    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('stratigraphy.utils.pop_up_info', autospec=True)
    def test_vlayer_strings(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        for obsid in ['A', 'b', 'c1']:
            db_utils.sql_alter_db('''INSERT INTO obs_points (obsid) VALUES ('{}')'''.format(str(obsid)))

        self.create_vlayer()
        self.select_features()
        feature_ids = [feature.id() for feature in self.vlayer.getFeatures()]

        reference_ids = (1, 2, 3)
        assert self.vlayer.isValid()
        assert len(feature_ids) == len(reference_ids)
        assert tuple(feature_ids) == reference_ids
        assert tuple(sorted([x for x in self.vlayer.selectedFeatureIds()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getSelectedFeatures()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getFeatures(feature_ids)])) == reference_ids


    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('stratigraphy.utils.pop_up_info', autospec=True)
    def test_vlayer_1000_features(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        dbconnection = db_utils.DbConnectionManager()
        cur = dbconnection.cursor

        cur.execute('''BEGIN TRANSACTION;''')
        for obsid in range(1000):
            cur.execute('''INSERT INTO obs_points (obsid) VALUES ('{}');'''.format(str(obsid)))
        cur.execute('''END TRANSACTION;''')


        self.create_vlayer(no_print=True)
        self.select_features(no_print=True)
        feature_ids = [feature.id() for feature in self.vlayer.getFeatures()]

        reference_ids = tuple(range(1, 1001))

        print("First 10 ids: " + str(feature_ids[:10]))
        print("Last 10 ids: " + str(feature_ids[-10:]))
        print("First 10 reference_ids: " + str(reference_ids[:10]))
        print("Last 10 reference_ids: " + str(reference_ids[-10:]))

        assert self.vlayer.isValid()
        assert len(feature_ids) == len(reference_ids)
        assert tuple(feature_ids) == reference_ids
        assert tuple(sorted([x for x in self.vlayer.selectedFeatureIds()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getSelectedFeatures()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getFeatures(feature_ids)])) == reference_ids

        
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('stratigraphy.utils.pop_up_info', autospec=True)
    def test_vlayer_2000_ints(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        dbconnection = db_utils.DbConnectionManager()
        cur = dbconnection.cursor

        cur.execute('''BEGIN TRANSACTION;''')
        for obsid in range(2000):
            cur.execute('''INSERT INTO obs_points (obsid) VALUES ('{}');'''.format(str(obsid)))
        cur.execute('''END TRANSACTION;''')


        self.create_vlayer(no_print=True)
        self.select_features(no_print=True)
        feature_ids = [feature.id() for feature in self.vlayer.getFeatures()]

        reference_ids = tuple(range(1, 2001))

        print("First 10 ids: " + str(feature_ids[:10]))
        print("Last 10 ids: " + str(feature_ids[-10:]))
        print("First 10 reference_ids: " + str(reference_ids[:10]))
        print("Last 10 reference_ids: " + str(reference_ids[-10:]))

        assert self.vlayer.isValid()
        assert len(feature_ids) == len(reference_ids)
        assert tuple(feature_ids) == reference_ids
        assert tuple(sorted([x for x in self.vlayer.selectedFeatureIds()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getSelectedFeatures()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getFeatures(feature_ids)])) == reference_ids

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('stratigraphy.utils.pop_up_info', autospec=True)
    def test_vlayer_2000_strings(self, mock_skippopup, mock_messagebar):
        """

        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        dbconnection = db_utils.DbConnectionManager()
        cur = dbconnection.cursor

        obsids = [letter + str(_int) for letter in string.ascii_letters for _int in range(80)]

        cur.execute('''BEGIN TRANSACTION;''')
        for obsid in obsids:
            cur.execute('''INSERT INTO obs_points (obsid) VALUES ('{}');'''.format(str(obsid)))
        cur.execute('''END TRANSACTION;''')
        dbconnection.commit()

        self.create_vlayer(no_print=True)
        self.select_features(no_print=True)
        feature_ids = [feature.id() for feature in self.vlayer.getFeatures()]

        reference_ids = tuple(range(1, len(obsids)+1))

        print("First 10 ids: " + str(feature_ids[:10]))
        print("Last 10 ids: " + str(feature_ids[-10:]))
        print("First 10 reference_ids: " + str(reference_ids[:10]))
        print("Last 10 reference_ids: " + str(reference_ids[-10:]))
        print(str(self.vlayer.featureCount()))

        assert self.vlayer.isValid()
        assert len(feature_ids) == len(reference_ids)
        assert tuple(feature_ids) == reference_ids
        assert tuple(sorted([x for x in self.vlayer.selectedFeatureIds()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getSelectedFeatures()])) == reference_ids
        assert tuple(sorted([x.id() for x in self.vlayer.getFeatures(feature_ids)])) == reference_ids
