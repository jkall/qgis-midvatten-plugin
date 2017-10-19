# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the sectionplot.

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

 Notes:
     * The uri = QgsDataSourceURI() doesn't reset unless given a new database
     name (for some reason). This is the reason that the tests
     has to be split up into several classes.
"""
from qgis.core import QgsVectorLayer

import db_utils
import mock
from nose.plugins.attrib import attr
from stratigraphy import Stratigraphy

import utils_for_tests


@attr(status='unstable')
class TestStratigraphy(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('stratigraphy.SurveyDialog.show', autospec=True)
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_stratigraphy(self, mock_show):
        dbconnection = db_utils.DbConnectionManager()
        uri = dbconnection.uri
        uri.setDataSource(schema, tablename, geometrycolumn, sql, keycolumn)
        layer = QgsVectorLayer(uri.uri(), tablename, dbtype.encode('utf-8'))
        uri.setDataSource('', 'obs_points', 'geometry', '', 'obsid')
        print(str(uri.ur()))
        self.vlayer = QgsVectorLayer(uri.uri(), u'TestLayer', u'spatialite'.encode('utf-8'))
        raise Exception()
        features = self.vlayer.getFeatures()
        featureids = [feature.id() for feature in features]
        self.vlayer.setSelectedFeatures(featureids)

        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ('P1', GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ('P2', GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ('P3', GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES (P1, 1, 0, 1, 'sand', 'sand', 3, 'j')''')
        db_utils.sql_alter_db(u'''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES (P1, 2, 1, 4.5, 'morän', 'morän', 3, 'j')''')

        mock_active_layer = mock.MagicMock()
        #mock_active_layer.selectedFeaturesIds().return_value =
        dlg = Stratigraphy(self.iface, mock_active_layer, self.ms.settingsdict)
        print("Init")
        #dlg.showSurvey()
        print(str(mock_active_layer.mock_calls))
        assert False
