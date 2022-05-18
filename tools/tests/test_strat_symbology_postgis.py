# -*- coding: utf-8 -*-

from builtins import str

import mock
from nose.plugins.attrib import attr
from qgis.core import QgsProject

from midvatten.tools.utils import common_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests


@attr(status='on')
class TestStratSymbology(utils_for_tests.MidvattenTestPostgisDbSv):

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_strat_symbology(self, mock_messagebar):
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(1 2)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')

        @mock.patch('qgis.utils.iface', autospec=True)
        def _test(self, mock_iface):
            mock_mapcanvas = mock_iface.mapCanvas.return_value
            mock_mapcanvas.layerCount.return_value = 0
            self.midvatten.load_strat_symbology()
            self.ss = self.midvatten.strat_symbology
            try:
                self.ss.create_symbology()
            except:
                print(str(mock_messagebar.mock_calls))
                raise

        _test(self)
        root = QgsProject.instance().layerTreeRoot()
        test = common_utils.anything_to_string_representation(utils_for_tests.recursive_children(root))
        ref = '["", "", [["Midvatten strat symbology", "", [["Bars", "", [["Obsid label", True, []], ["Layer texts", True, []], ["W levels", "", [["W levels label", True, []], ["W levels", True, []]]], ["Bedrock", "", [["Bedrock label", True, []], ["Bedrock", True, []]]], ["Frame", True, []], ["Layers", "", [["Geology", True, []], ["Hydro", True, []]]], ["Shadow", True, []]]], ["Static bars", "", [["Obsid label", True, []], ["Layer texts", True, []], ["W levels", "", [["W levels label", True, []], ["W levels", True, []]]], ["Bedrock", "", [["Bedrock label", True, []], ["Bedrock", True, []]]], ["Frame", True, []], ["Layers", "", [["Geology", True, []], ["Hydro", True, []]]], ["Shadow", True, []]]], ["Rings", "", [["Bedrock", "", [["Bedrock", True, []]]], ["Layers", "", [["Geology", True, []], ["Hydro", True, []]]]]]]]]]'
        print(str(test))
        print(str(ref))
        print(str(mock_messagebar.mock_calls))
        assert test == ref
        assert mock_messagebar.mock_calls == []
