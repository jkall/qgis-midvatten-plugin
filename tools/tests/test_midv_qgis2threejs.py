# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that prepares midvatten
 tables for Qgis2Threejs.

                             -------------------
        begin                : 2019-03-11
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
#

from collections import OrderedDict
from qgis.core import QgsProject, QgsVectorLayer, QgsApplication

import db_utils
import midvatten_utils as utils
import mock
from import_levelogger import LeveloggerImport
from mock import MagicMock
from nose.plugins.attrib import attr

import utils_for_tests
from mocks_for_tests import MockUsingReturnValue



@attr(status='on')
class TestPrepareQgis2Threejs(utils_for_tests.MidvattenTestSpatialiteDbSv):
    """ Test to make sure levelogger goes all the way to the end without errors
    """

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def init_qgis(self):
        self.qgs = QgsApplication([], True)
        self.qgs.initQgis()

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_prepare_qgis2threejs(self, mock_iface, mock_messagebar):
        self.init_qgis()

        dbconnection = db_utils.DbConnectionManager()
        dbconnection.execute('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 1, ST_GeomFromText('POINT(1 1)', 3006)); ''')
        dbconnection.execute('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('1', 1, 0, 1, 'torv'); ''')
        dbconnection.execute('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geoshort) VALUES ('1', 2, 1, 2, 'fyll'); ''')
        dbconnection.commit_and_closedb()
        #print(str(db_utils.sql_load_fr_db('''SELECT * FROM stratigraphy;''')))


        canvas = MagicMock()
        mock_iface.mapCanvas.return_value = canvas

        self.midvatten.prepare_layers_for_qgis2threejs()

        layers = ['strat_torv',
                    'strat_fyll',
                    'strat_lera',
                    'strat_silt',
                    'strat_finsand',
                    'strat_mellansand',
                    'strat_sand',
                    'strat_grovsand',
                    'strat_fingrus',
                    'strat_mellangrus',
                    'strat_grus',
                    'strat_grovgrus',
                    'strat_morn',
                    'strat_berg',
                    'strat_obs_p_for_qgsi2threejs']

        view_contents = []
        for l in layers:
            view_contents.append(db_utils.sql_load_fr_db('''SELECT rowid, obsid, z_coord, height, ST_AsText(geometry) FROM {};'''.format(l))[1])
        test = utils.anything_to_string_representation(view_contents)
        ref = '''[[(1, "1", 1.0, -1.0, "POINT(1 1)", )], [(2, "1", 0.0, -1.0, "POINT(1 1)", )], [], [], [], [], [], [], [], [], [], [], [], [], []]'''
        assert test == ref

    def tearDown(self):
        QgsProject.instance().addMapLayer(self.vlayer)
        QgsProject.instance().removeMapLayer(self.vlayer.id())
        super(self.__class__, self).tearDown()


