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
import mock
import utils_for_tests
from definitions import midvatten_defs

class _TestDefsFunctions(utils_for_tests.MidvattenTestSpatialiteDbSv):
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


class TestGeocolorsymbols(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    #temp_db_path = '/home/henrik/temp/tmp_midvatten_temp_db.sqlite'
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    crs_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def setUp(self):

        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TestGeocolorsymbols.temp_db_path)
        except OSError:
            pass

    def tearDown(self):
        #Delete database
        try:
            os.remove(TestGeocolorsymbols.temp_db_path)
        except OSError:
            pass

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_only_moran(self, mock_locale, mock_iface):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        utils.sql_alter_db(u'DELETE FROM zz_strat')
        utils.sql_alter_db(u'DELETE FROM zz_stratigraphy_plots')
        utils.sql_alter_db(u"""INSERT INTO zz_strat(geoshort, strata) VALUES('morän', 'morän')""")
        utils.sql_alter_db(u"""INSERT INTO zz_strat(geoshort, strata) VALUES('moran', 'morän')""")
        utils.sql_alter_db(u"""INSERT INTO zz_stratigraphy_plots(strata, color_mplot, hatch_mplot, color_qt, brush_qt) VALUES('morän', 'theMPcolor', '/', 'theQTcolor', 'thePattern')""")

        test_string = utils.anything_to_string_representation(midvatten_defs.geocolorsymbols())
        reference_string = u'''{u"moran": (u"thePattern", u"theQTcolor", ), u"morän": (u"thePattern", u"theQTcolor", )}'''
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_missing_colors_patterns(self, mock_locale, mock_iface):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        utils.sql_alter_db(u'DELETE FROM zz_strat')
        utils.sql_alter_db(u'DELETE FROM zz_stratigraphy_plots')
        utils.sql_alter_db(u"""INSERT INTO zz_strat(geoshort, strata) VALUES('nostrata', 'noshort')""")
        utils.sql_alter_db(u"""INSERT INTO zz_stratigraphy_plots(strata, color_mplot, hatch_mplot, color_qt, brush_qt) VALUES('moran', 'theMPcolor', '/', 'theQTcolor', 'thePattern')""")

        test_string = utils.anything_to_string_representation(midvatten_defs.geocolorsymbols())
        reference_string = u'''{u"nostrata": (u"NoBrush", u"white", )}'''
        assert test_string == reference_string

