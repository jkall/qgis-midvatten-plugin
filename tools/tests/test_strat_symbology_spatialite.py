# -*- coding: utf-8 -*-

from builtins import str

import db_utils
import midvatten_utils as utils
import mock
import qgis
import utils_for_tests
from nose.plugins.attrib import attr
from qgis.core import QgsProject


@attr(status='on')
class TestStratSymbology(utils_for_tests.MidvattenTestSpatialiteDbSv):

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self):
        super(TestStratSymbology, self).setUp()


    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_strat_symbology(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(1 2)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')

        @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface):
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            root = qgis.core.QgsLayerTreeGroup(name='root', checked=True)
            utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database.return_value.layerTreeRoot.return_value = root
            self.midvatten.load_strat_symbology()
            self.ss = self.midvatten.strat_symbology
            try:
                self.ss.create_symbology()
            except:
                print(str(mock_messagebar.mock_calls))
                raise
            return root

        root = _test(self)
        print(str(mock_messagebar.mock_calls))
        test = utils.anything_to_string_representation(utils_for_tests.recursive_children(root))
        ref = '["root", "", [["Midvatten strat symbology", "", [["Rings", "", [["Bedrock", True, []], ["Layers", "", [["Geology", True, []], ["Hydro", True, []]]]]], ["Static bars", "", [["W levels", True, []], ["Bedrock", True, []], ["Layers", "", [["Geology", True, []], ["Hydro", True, []]]]]], ["Bars", "", [["W levels", True, []], ["Bedrock", True, []], ["Layers", "", [["Geology", True, []], ["Hydro", True, []]]]]]]]]]'
        assert test == ref
        assert mock_messagebar.mock_calls == []


