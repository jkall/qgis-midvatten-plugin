from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
from operator import itemgetter
# -*- coding: utf-8 -*-
from collections import OrderedDict
import ast


from qgis.core import QgsProject, QgsVectorLayer, QgsApplication
import import_fieldlogger
import midvatten_utils as utils
import mock
from date_utils import datestring_to_date
from import_fieldlogger import FieldloggerImport, InputFields, DateTimeFilter
from mock import MagicMock, call
from nose.plugins.attrib import attr

import utils_for_tests
from .utils_for_tests import create_test_string
import qgis
import db_utils


@attr(status='on')
class TestStratSymbology(utils_for_tests.MidvattenTestSpatialiteDbSv):

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self):
        super(TestStratSymbology, self).setUp()
        self.qgs = QgsApplication([], True)
        self.qgs.initQgis()

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_strat_symbology(self, mock_messagebar):

        #TODO: This test is not done yet

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(1 2)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')

        @mock.patch('qgis.core.QgsProject')
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface, mock_qgsproject):
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0

            root = qgis.core.QgsLayerTreeGroup(name='root', checked=True)

            mock_qgsproject.instance.layerTreeRoot.return_value = root

            self.midvatten.load_strat_symbology()
            self.ss = self.midvatten.strat_symbology
            self.ss.create_symbology()
            print(str(mock_qgsproject.mock_calls))
            print(str(mock_messagebar.mock_calls))
            return root

        root = _test(self)
        print(str(root.children()))
        print(str(mock_messagebar.mock_calls))

        assert False