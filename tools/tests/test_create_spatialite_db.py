# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the creating of the database.

 This part is to a big extent based on QSpatialite plugin.
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
from definitions import midvatten_defs as defs
from import_data_to_db import midv_data_importer
import os


class TestCreateMemoryDb(utils_for_tests.MidvattenTestSpatialiteNotCreated):
    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_memory_db(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = u':memory:'
        self.midvatten.new_db()
        assert True


class _TestCreateDb(utils_for_tests.MidvattenTestSpatialiteNotCreated):
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_create_db_locale_sv(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface, mock_messagebar):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = self.TEMP_DBPATH
        self.midvatten.new_db()
        assert db_utils.check_connection_ok()
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select * from zz_strat'))
        reference_string = ur"""(True, [(berg, berg), (b, berg), (rock, berg), (ro, berg), (grovgrus, grovgrus), (grg, grovgrus), (coarse gravel, grovgrus), (cgr, grovgrus), (grus, grus), (gr, grus), (gravel, grus), (mellangrus, mellangrus), (grm, mellangrus), (medium gravel, mellangrus), (mgr, mellangrus), (fingrus, fingrus), (grf, fingrus), (fine gravel, fingrus), (fgr, fingrus), (grovsand, grovsand), (sag, grovsand), (coarse sand, grovsand), (csa, grovsand), (sand, sand), (sa, sand), (mellansand, mellansand), (sam, mellansand), (medium sand, mellansand), (msa, mellansand), (finsand, finsand), (saf, finsand), (fine sand, finsand), (fsa, finsand), (silt, silt), (si, silt), (lera, lera), (ler, lera), (le, lera), (clay, lera), (cl, lera), (morän, morän), (moran, morän), (mn, morän), (till, morän), (ti, morän), (torv, torv), (t, torv), (peat, torv), (pt, torv), (fyll, fyll), (fyllning, fyll), (f, fyll), (made ground, fyll), (mg, fyll), (land fill, fyll)])"""
        assert test_string == reference_string
        current_locale = utils.getcurrentlocale()[0]
        assert current_locale == u'sv_SE'

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_create_db_locale_en(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'en_US'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = self.TEMP_DBPATH
        self.midvatten.new_db()
        assert db_utils.check_connection_ok()
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select * from zz_strat'))
        reference_string = ur"""(True, [(berg, rock), (b, rock), (rock, rock), (ro, rock), (grovgrus, coarse gravel), (grg, coarse gravel), (coarse gravel, coarse gravel), (cgr, coarse gravel), (grus, gravel), (gr, gravel), (gravel, gravel), (mellangrus, medium gravel), (grm, medium gravel), (medium gravel, medium gravel), (mgr, medium gravel), (fingrus, fine gravel), (grf, fine gravel), (fine gravel, fine gravel), (fgr, fine gravel), (grovsand, coarse sand), (sag, coarse sand), (coarse sand, coarse sand), (csa, coarse sand), (sand, sand), (sa, sand), (mellansand, medium sand), (sam, medium sand), (medium sand, medium sand), (msa, medium sand), (finsand, fine sand), (saf, fine sand), (fine sand, fine sand), (fsa, fine sand), (silt, silt), (si, silt), (lera, clay), (ler, clay), (le, clay), (clay, clay), (cl, clay), (morän, till), (moran, till), (mn, till), (till, till), (ti, till), (torv, peat), (t, peat), (peat, peat), (pt, peat), (fyll, made ground), (fyllning, made ground), (f, made ground), (made ground, made ground), (mg, made ground), (land fill, made ground), (unknown, unknown)])"""
        assert test_string == reference_string
        current_locale = utils.getcurrentlocale()[0]
        assert current_locale == u'en_US'

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_create_db_setup_string(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        """
        This test fails every time anything other than comments are changed in create_db
        The purpose is to be sure that every change is meant to be.
        """
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = self.TEMP_DBPATH
        self.midvatten.new_db()
        test_string = defs.db_setup_as_string()
        reference_string = u'[(u"about_db", ), [(0, u"tablename", u"text", 0, None, 0, ), (1, u"columnname", u"text", 0, None, 0, ), (2, u"data_type", u"text", 0, None, 0, ), (3, u"not_null", u"text", 0, None, 0, ), (4, u"default_value", u"text", 0, None, 0, ), (5, u"primary_key", u"text", 0, None, 0, ), (6, u"foreign_key", u"text", 0, None, 0, ), (7, u"description", u"text", 0, None, 0, ), (8, u"upd_date", u"text", 0, None, 0, ), (9, u"upd_sign", u"text", 0, None, 0, )], (u"comments", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"date_time", u"text", 1, None, 2, ), (2, u"comment", u"text", 1, None, 0, ), (3, u"staff", u"text", 1, None, 0, )], (u"meteo", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"instrumentid", u"text", 1, None, 2, ), (2, u"parameter", u"text", 1, None, 3, ), (3, u"date_time", u"text", 1, None, 4, ), (4, u"reading_num", u"double", 0, None, 0, ), (5, u"reading_txt", u"text", 0, None, 0, ), (6, u"unit", u"text", 0, None, 0, ), (7, u"comment", u"text", 0, None, 0, )], (u"obs_lines", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"name", u"text", 0, None, 0, ), (2, u"place", u"text", 0, None, 0, ), (3, u"type", u"text", 0, None, 0, ), (4, u"source", u"text", 0, None, 0, ), (5, u"geometry", u"LINESTRING", 0, None, 0, )], (u"obs_p_w_lvl", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"geometry", u"POINT", 0, None, 0, )], (u"obs_p_w_qual_field", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"geometry", u"POINT", 0, None, 0, )], (u"obs_p_w_qual_lab", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"geometry", u"POINT", 0, None, 0, )], (u"obs_p_w_strat", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"h_toc", u"double", 0, None, 0, ), (3, u"h_gs", u"double", 0, None, 0, ), (4, u"geometry", u"POINT", 0, None, 0, )], (u"obs_points", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"name", u"text", 0, None, 0, ), (2, u"place", u"text", 0, None, 0, ), (3, u"type", u"text", 0, None, 0, ), (4, u"length", u"double", 0, None, 0, ), (5, u"drillstop", u"text", 0, None, 0, ), (6, u"diam", u"double", 0, None, 0, ), (7, u"material", u"text", 0, None, 0, ), (8, u"screen", u"text", 0, None, 0, ), (9, u"capacity", u"text", 0, None, 0, ), (10, u"drilldate", u"text", 0, None, 0, ), (11, u"wmeas_yn", u"integer", 0, None, 0, ), (12, u"wlogg_yn", u"integer", 0, None, 0, ), (13, u"east", u"double", 0, None, 0, ), (14, u"north", u"double", 0, None, 0, ), (15, u"ne_accur", u"double", 0, None, 0, ), (16, u"ne_source", u"text", 0, None, 0, ), (17, u"h_toc", u"double", 0, None, 0, ), (18, u"h_tocags", u"double", 0, None, 0, ), (19, u"h_gs", u"double", 0, None, 0, ), (20, u"h_accur", u"double", 0, None, 0, ), (21, u"h_syst", u"text", 0, None, 0, ), (22, u"h_source", u"text", 0, None, 0, ), (23, u"source", u"text", 0, None, 0, ), (24, u"com_onerow", u"text", 0, None, 0, ), (25, u"com_html", u"text", 0, None, 0, ), (26, u"geometry", u"POINT", 0, None, 0, )], (u"seismic_data", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"length", u"double", 1, None, 2, ), (2, u"ground", u"double", 0, None, 0, ), (3, u"bedrock", u"double", 0, None, 0, ), (4, u"gw_table", u"double", 0, None, 0, ), (5, u"comment", u"text", 0, None, 0, )], (u"stratigraphy", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"stratid", u"integer", 1, None, 2, ), (2, u"depthtop", u"double", 0, None, 0, ), (3, u"depthbot", u"double", 0, None, 0, ), (4, u"geology", u"text", 0, None, 0, ), (5, u"geoshort", u"text", 0, None, 0, ), (6, u"capacity", u"text", 0, None, 0, ), (7, u"development", u"text", 0, None, 0, ), (8, u"comment", u"text", 0, None, 0, )], (u"vlf_data", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"length", u"double", 1, None, 2, ), (2, u"real_comp", u"double", 0, None, 0, ), (3, u"imag_comp", u"double", 0, None, 0, ), (4, u"comment", u"text", 0, None, 0, )], (u"w_flow", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"instrumentid", u"text", 1, None, 2, ), (2, u"flowtype", u"text", 1, None, 3, ), (3, u"date_time", u"text", 1, None, 4, ), (4, u"reading", u"double", 0, None, 0, ), (5, u"unit", u"text", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"w_flow_accvol", ), [(0, u"obsid", u"text", 0, None, 0, ), (1, u"instrumentid", u"text", 0, None, 0, ), (2, u"date_time", u"text", 0, None, 0, ), (3, u"reading", u"double", 0, None, 0, ), (4, u"unit", u"text", 0, None, 0, ), (5, u"comment", u"text", 0, None, 0, )], (u"w_flow_aveflow", ), [(0, u"obsid", u"text", 0, None, 0, ), (1, u"instrumentid", u"text", 0, None, 0, ), (2, u"date_time", u"text", 0, None, 0, ), (3, u"reading", u"double", 0, None, 0, ), (4, u"unit", u"text", 0, None, 0, ), (5, u"comment", u"text", 0, None, 0, )], (u"w_flow_momflow", ), [(0, u"obsid", u"text", 0, None, 0, ), (1, u"instrumentid", u"text", 0, None, 0, ), (2, u"date_time", u"text", 0, None, 0, ), (3, u"reading", u"double", 0, None, 0, ), (4, u"unit", u"text", 0, None, 0, ), (5, u"comment", u"text", 0, None, 0, )], (u"w_levels", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"date_time", u"text", 1, None, 2, ), (2, u"meas", u"double", 0, None, 0, ), (3, u"h_toc", u"double", 0, None, 0, ), (4, u"level_masl", u"double", 0, None, 0, ), (5, u"comment", u"text", 0, None, 0, )], (u"w_levels_geom", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"date_time", u"text", 0, None, 0, ), (3, u"meas", u"double", 0, None, 0, ), (4, u"h_toc", u"double", 0, None, 0, ), (5, u"level_masl", u"double", 0, None, 0, ), (6, u"geometry", u"POINT", 0, None, 0, )], (u"w_levels_logger", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"date_time", u"text", 1, None, 2, ), (2, u"head_cm", u"double", 0, None, 0, ), (3, u"temp_degc", u"double", 0, None, 0, ), (4, u"cond_mscm", u"double", 0, None, 0, ), (5, u"level_masl", u"double", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"w_lvls_last_geom", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"date_time", u"", 0, None, 0, ), (3, u"meas", u"double", 0, None, 0, ), (4, u"level_masl", u"double", 0, None, 0, ), (5, u"geometry", u"POINT", 0, None, 0, )], (u"w_qual_field", ), [(0, u"obsid", u"text", 1, None, 1, ), (1, u"staff", u"text", 0, None, 0, ), (2, u"date_time", u"text", 1, None, 2, ), (3, u"instrument", u"text", 0, None, 0, ), (4, u"parameter", u"text", 1, None, 3, ), (5, u"reading_num", u"double", 0, None, 0, ), (6, u"reading_txt", u"text", 0, None, 0, ), (7, u"unit", u"text", 0, None, 4, ), (8, u"depth", u"double", 0, None, 0, ), (9, u"comment", u"text", 0, None, 0, )], (u"w_qual_field_geom", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"staff", u"text", 0, None, 0, ), (3, u"date_time", u"text", 0, None, 0, ), (4, u"instrument", u"text", 0, None, 0, ), (5, u"parameter", u"text", 0, None, 0, ), (6, u"reading_num", u"double", 0, None, 0, ), (7, u"reading_txt", u"text", 0, None, 0, ), (8, u"unit", u"text", 0, None, 0, ), (9, u"comment", u"text", 0, None, 0, ), (10, u"geometry", u"POINT", 0, None, 0, )], (u"w_qual_lab", ), [(0, u"obsid", u"text", 1, None, 0, ), (1, u"depth", u"double", 0, None, 0, ), (2, u"report", u"text", 1, None, 1, ), (3, u"project", u"text", 0, None, 0, ), (4, u"staff", u"text", 0, None, 0, ), (5, u"date_time", u"text", 0, None, 0, ), (6, u"anameth", u"text", 0, None, 0, ), (7, u"parameter", u"text", 1, None, 2, ), (8, u"reading_num", u"double", 0, None, 0, ), (9, u"reading_txt", u"text", 0, None, 0, ), (10, u"unit", u"text", 0, None, 0, ), (11, u"comment", u"text", 0, None, 0, )], (u"w_qual_lab_geom", ), [(0, u"rowid", u"INTEGER", 0, None, 0, ), (1, u"obsid", u"text", 0, None, 0, ), (2, u"depth", u"double", 0, None, 0, ), (3, u"report", u"text", 0, None, 0, ), (4, u"staff", u"text", 0, None, 0, ), (5, u"date_time", u"text", 0, None, 0, ), (6, u"anameth", u"text", 0, None, 0, ), (7, u"parameter", u"text", 0, None, 0, ), (8, u"reading_txt", u"text", 0, None, 0, ), (9, u"reading_num", u"double", 0, None, 0, ), (10, u"unit", u"text", 0, None, 0, ), (11, u"geometry", u"POINT", 0, None, 0, )], (u"zz_capacity", ), [(0, u"capacity", u"text", 1, None, 1, ), (1, u"explanation", u"text", 1, None, 0, )], (u"zz_capacity_plots", ), [(0, u"capacity", u"text", 1, None, 1, ), (1, u"color_qt", u"text", 1, None, 0, )], (u"zz_flowtype", ), [(0, u"type", u"text", 1, None, 1, ), (1, u"explanation", u"text", 0, None, 0, )], (u"zz_meteoparam", ), [(0, u"parameter", u"text", 1, None, 1, ), (1, u"explanation", u"text", 0, None, 0, )], (u"zz_staff", ), [(0, u"staff", u"text", 0, None, 1, ), (1, u"name", u"text", 0, None, 0, )], (u"zz_strat", ), [(0, u"geoshort", u"text", 1, None, 1, ), (1, u"strata", u"text", 1, None, 0, )], (u"zz_stratigraphy_plots", ), [(0, u"strata", u"text", 1, None, 1, ), (1, u"color_mplot", u"text", 1, None, 0, ), (2, u"hatch_mplot", u"text", 1, None, 0, ), (3, u"color_qt", u"text", 1, None, 0, ), (4, u"brush_qt", u"text", 1, None, 0, )]]'
        assert test_string == reference_string


class _TestObsPointsTriggers(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self):
        super(TestObsPointsTriggers, self).setUp()
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_insert_obs_points_geom_fr_coords""")
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_update_obs_points_geom_fr_coords""")
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_insert_obs_points_coords_fr_geom""")
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_update_obs_points_coords_fr_geom""")

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_triggers_not_change_existing(self):
        """ Adding triggers should not automatically change the db """
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None)])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_triggers_add_east_north(self):
        """ Updating coordinates from NULL should create geometry. """
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', NULL, NULL)''')

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        db_utils.sql_alter_db(u"""update obs_points set east='1.0', north='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 2.0, POINT(1 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_triggers_not_deleting_geom_when_east_north_null(self):
        """ Adding triggers should not automatically delete geometry when east AND north is NULL """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_triggers_not_deleting_geom_when_one_east_north_null(self):
        
        """ Adding triggers should not automatically delete geometry when east OR north is NULL """
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        db_utils.sql_alter_db(u"""update obs_points set east=X(geometry) where east is null and geometry is not null""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, None, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 2.0, None, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east=NULL""")
        db_utils.sql_alter_db(u"""update obs_points set north='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, 2.0, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='3.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 2.0, POINT(3 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='4.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 4.0, 2.0, POINT(4 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east=NULL, north=NULL""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, POINT(4 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='5.0', north='6.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 5.0, 6.0, POINT(5 6))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_geometry_from_east_north(self):
        """ Test that adding triggers and adding obsid with east, north also adds geometry
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_east_north_from_geometry(self):
        """ Test that adding triggers and adding obsid with geometry also adds east, north
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and adding obsid don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from geometry don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from east, north don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb2', 2, 2)""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_update_geometry_from_east_north(self):
        """ Test that adding triggers and updating obsid with east, north also updates geometry
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        db_utils.sql_alter_db(u'''UPDATE obs_points SET east = 2, north = 2 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_update_east_north_from_geometry(self):
        """ Test that adding triggers and updating obsid with geometry also updates east, north
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u'''UPDATE obs_points SET geometry = GeomFromText('POINT(2.0 2.0)', 3006) WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_trigger_update_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and updating obsid don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u'''UPDATE obs_points SET geometry = GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, None, None, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_update_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from geometry don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u'''UPDATE obs_points SET geometry = GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_update_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, GeomFromText('POINT(2.0 2.0)', 3006))""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        db_utils.sql_alter_db(u'''UPDATE obs_points SET east = 3, north = 3 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_obsid_without_anything(self):
        """
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb1')""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb2')""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, None), (rb2, None, None, None)])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_obsid_without_anything_not_changing_existing(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb2')""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb3')""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, None, None, None), (rb3, None, None, None)])'
        assert test_string == reference_string


