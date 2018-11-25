# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles exports to
  fieldlogger format.

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
import midvatten_utils as utils
import mock
from nose.plugins.attrib import attr

import db_utils
import utils_for_tests
from definitions import midvatten_defs

@attr(status='only')
class TestDefsFunctions(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_tables_columns(self):
        res = db_utils.db_tables_columns_info()
        assert res
        assert isinstance(res, dict)
        for k, v in res.items():
            assert isinstance(k, str)
            assert isinstance(v, (tuple, list))
            for x in v:
                assert isinstance(x, (tuple, list))
                assert x

@attr(status='only')
class TestGeocolorsymbols(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_only_moran(self):
        db_utils.sql_alter_db('DELETE FROM zz_strat')
        db_utils.sql_alter_db('DELETE FROM zz_stratigraphy_plots')
        db_utils.sql_alter_db("""INSERT INTO zz_strat(geoshort, strata) VALUES('morän', 'morän')""")
        db_utils.sql_alter_db("""INSERT INTO zz_strat(geoshort, strata) VALUES('moran', 'morän')""")
        db_utils.sql_alter_db("""INSERT INTO zz_stratigraphy_plots(strata, color_mplot, hatch_mplot, color_qt, brush_qt) VALUES('morän', 'theMPcolor', '/', 'theQTcolor', 'thePattern')""")

        test_string = utils.anything_to_string_representation(midvatten_defs.geocolorsymbols())
        reference_string = '''{"moran": ("thePattern", "theQTcolor", ), "morän": ("thePattern", "theQTcolor", )}'''
        assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_missing_colors_patterns(self):
        db_utils.sql_alter_db('DELETE FROM zz_strat')
        db_utils.sql_alter_db('DELETE FROM zz_stratigraphy_plots')
        db_utils.sql_alter_db("""INSERT INTO zz_strat(geoshort, strata) VALUES('nostrata', 'noshort')""")
        db_utils.sql_alter_db("""INSERT INTO zz_stratigraphy_plots(strata, color_mplot, hatch_mplot, color_qt, brush_qt) VALUES('moran', 'theMPcolor', '/', 'theQTcolor', 'thePattern')""")

        test_string = utils.anything_to_string_representation(midvatten_defs.geocolorsymbols())
        reference_string = '''{"nostrata": ("NoBrush", "white", )}'''
        assert test_string == reference_string
