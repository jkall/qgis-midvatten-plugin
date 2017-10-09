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
import db_utils
import midvatten_utils as utils
import mock
import utils_for_tests
from definitions import midvatten_defs

class TestDefsFunctions(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_tables_columns(self, mock_instance):
        mock_instance.return_value.readEntry.return_value = self.SETTINGS_DATABASE
        res = db_utils.tables_columns()
        assert res
        assert isinstance(res, dict)
        for k, v in res.iteritems():
            assert isinstance(k, unicode)
            assert isinstance(v, (tuple, list))
            for x in v:
                assert isinstance(x, (tuple, list))
                assert x


class TestGeocolorsymbols(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_only_moran(self, mock_instance):
        db_utils.sql_alter_db(u'DELETE FROM zz_strat')
        db_utils.sql_alter_db(u'DELETE FROM zz_stratigraphy_plots')
        db_utils.sql_alter_db(u"""INSERT INTO zz_strat(geoshort, strata) VALUES('morän', 'morän')""")
        db_utils.sql_alter_db(u"""INSERT INTO zz_strat(geoshort, strata) VALUES('moran', 'morän')""")
        db_utils.sql_alter_db(u"""INSERT INTO zz_stratigraphy_plots(strata, color_mplot, hatch_mplot, color_qt, brush_qt) VALUES('morän', 'theMPcolor', '/', 'theQTcolor', 'thePattern')""")

        test_string = utils.anything_to_string_representation(midvatten_defs.geocolorsymbols())
        reference_string = u'''{u"moran": (u"thePattern", u"theQTcolor", ), u"morän": (u"thePattern", u"theQTcolor", )}'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_missing_colors_patterns(self, mock_instance):
        utils.sql_alter_db(u'DELETE FROM zz_strat')
        utils.sql_alter_db(u'DELETE FROM zz_stratigraphy_plots')
        utils.sql_alter_db(u"""INSERT INTO zz_strat(geoshort, strata) VALUES('nostrata', 'noshort')""")
        utils.sql_alter_db(u"""INSERT INTO zz_stratigraphy_plots(strata, color_mplot, hatch_mplot, color_qt, brush_qt) VALUES('moran', 'theMPcolor', '/', 'theQTcolor', 'thePattern')""")

        test_string = utils.anything_to_string_representation(midvatten_defs.geocolorsymbols())
        reference_string = u'''{u"nostrata": (u"NoBrush", u"white", )}'''
        assert test_string == reference_string

