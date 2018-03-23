# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the creating of the postgis database.

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
from nose.plugins.attrib import attr

import utils_for_tests
from definitions import midvatten_defs as defs


@attr(status='on')
class TestFillDb(utils_for_tests.MidvattenTestPostgisNotCreated):
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_create_db_locale_sv(self, mock_crs_question, mock_answer_yes, mock_locale, mock_iface, mocked_messagebar):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()
        assert db_utils.check_connection_ok()
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select * from zz_strat'))
        reference_string = ur"""(True, [(berg, berg), (b, berg), (rock, berg), (ro, berg), (grovgrus, grovgrus), (grg, grovgrus), (coarse gravel, grovgrus), (cgr, grovgrus), (grus, grus), (gr, grus), (gravel, grus), (mellangrus, mellangrus), (grm, mellangrus), (medium gravel, mellangrus), (mgr, mellangrus), (fingrus, fingrus), (grf, fingrus), (fine gravel, fingrus), (fgr, fingrus), (grovsand, grovsand), (sag, grovsand), (coarse sand, grovsand), (csa, grovsand), (sand, sand), (sa, sand), (mellansand, mellansand), (sam, mellansand), (medium sand, mellansand), (msa, mellansand), (finsand, finsand), (saf, finsand), (fine sand, finsand), (fsa, finsand), (silt, silt), (si, silt), (lera, lera), (ler, lera), (le, lera), (clay, lera), (cl, lera), (morän, morän), (moran, morän), (mn, morän), (till, morän), (ti, morän), (torv, torv), (t, torv), (peat, torv), (pt, torv), (fyll, fyll), (fyllning, fyll), (f, fyll), (made ground, fyll), (mg, fyll), (land fill, fyll)])"""
        assert test_string == reference_string
        current_locale = utils.getcurrentlocale()[0]
        assert current_locale == u'sv_SE'
        print(str(mocked_messagebar.mock_calls))
        assert len(mocked_messagebar.mock_calls) == 0

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_create_db_locale_en(self, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'en_US'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()
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
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_create_db_setup_string(self, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        """
        This test fails every time anything other than comments are changed in create_db
        The purpose is to be sure that every change is meant to be.
        """
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()
        assert db_utils.check_connection_ok()
        reference_string = u'[(u"about_db", ), [(1, u"tablename", u"text", 0, None, 0, ), (2, u"columnname", u"text", 0, None, 0, ), (3, u"data_type", u"text", 0, None, 0, ), (4, u"not_null", u"text", 0, None, 0, ), (5, u"default_value", u"text", 0, None, 0, ), (6, u"primary_key", u"text", 0, None, 0, ), (7, u"foreign_key", u"text", 0, None, 0, ), (8, u"description", u"text", 0, None, 0, ), (9, u"upd_date", u"text", 0, None, 0, ), (10, u"upd_sign", u"text", 0, None, 0, )], (u"comments", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"date_time", u"text", 1, None, 1, ), (3, u"comment", u"text", 1, None, 0, ), (4, u"staff", u"text", 1, None, 0, )], (u"meteo", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"instrumentid", u"text", 1, None, 1, ), (3, u"parameter", u"text", 1, None, 1, ), (4, u"date_time", u"text", 1, None, 1, ), (5, u"reading_num", u"double precision", 0, None, 0, ), (6, u"reading_txt", u"text", 0, None, 0, ), (7, u"unit", u"text", 0, None, 0, ), (8, u"comment", u"text", 0, None, 0, )], (u"obs_lines", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"name", u"text", 0, None, 0, ), (3, u"place", u"text", 0, None, 0, ), (4, u"type", u"text", 0, None, 0, ), (5, u"source", u"text", 0, None, 0, ), (6, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"obs_p_w_lvl", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"obs_p_w_qual_field", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"obs_p_w_qual_lab", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"obs_p_w_strat", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"h_toc", u"double precision", 0, None, 0, ), (3, u"h_gs", u"double precision", 0, None, 0, ), (4, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"obs_points", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"name", u"text", 0, None, 0, ), (3, u"place", u"text", 0, None, 0, ), (4, u"type", u"text", 0, None, 0, ), (5, u"length", u"double precision", 0, None, 0, ), (6, u"drillstop", u"text", 0, None, 0, ), (7, u"diam", u"double precision", 0, None, 0, ), (8, u"material", u"text", 0, None, 0, ), (9, u"screen", u"text", 0, None, 0, ), (10, u"capacity", u"text", 0, None, 0, ), (11, u"drilldate", u"text", 0, None, 0, ), (12, u"wmeas_yn", u"integer", 0, None, 0, ), (13, u"wlogg_yn", u"integer", 0, None, 0, ), (14, u"east", u"double precision", 0, None, 0, ), (15, u"north", u"double precision", 0, None, 0, ), (16, u"ne_accur", u"double precision", 0, None, 0, ), (17, u"ne_source", u"text", 0, None, 0, ), (18, u"h_toc", u"double precision", 0, None, 0, ), (19, u"h_tocags", u"double precision", 0, None, 0, ), (20, u"h_gs", u"double precision", 0, None, 0, ), (21, u"h_accur", u"double precision", 0, None, 0, ), (22, u"h_syst", u"text", 0, None, 0, ), (23, u"h_source", u"text", 0, None, 0, ), (24, u"source", u"text", 0, None, 0, ), (25, u"com_onerow", u"text", 0, None, 0, ), (26, u"com_html", u"text", 0, None, 0, ), (27, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"seismic_data", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"length", u"double precision", 1, None, 1, ), (3, u"ground", u"double precision", 0, None, 0, ), (4, u"bedrock", u"double precision", 0, None, 0, ), (5, u"gw_table", u"double precision", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"stratigraphy", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"stratid", u"integer", 1, None, 1, ), (3, u"depthtop", u"double precision", 0, None, 0, ), (4, u"depthbot", u"double precision", 0, None, 0, ), (5, u"geology", u"text", 0, None, 0, ), (6, u"geoshort", u"text", 0, None, 0, ), (7, u"capacity", u"text", 0, None, 0, ), (8, u"development", u"text", 0, None, 0, ), (9, u"comment", u"text", 0, None, 0, )], (u"vlf_data", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"length", u"double precision", 1, None, 1, ), (3, u"real_comp", u"double precision", 0, None, 0, ), (4, u"imag_comp", u"double precision", 0, None, 0, ), (5, u"comment", u"text", 0, None, 0, )], (u"w_flow", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"instrumentid", u"text", 1, None, 1, ), (3, u"flowtype", u"text", 1, None, 1, ), (4, u"date_time", u"text", 1, None, 1, ), (5, u"reading", u"double precision", 0, None, 0, ), (6, u"unit", u"text", 0, None, 0, ), (7, u"comment", u"text", 0, None, 0, )], (u"w_flow_accvol", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"instrumentid", u"text", 0, None, 0, ), (3, u"date_time", u"text", 0, None, 0, ), (4, u"reading", u"double precision", 0, None, 0, ), (5, u"unit", u"text", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"w_flow_aveflow", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"instrumentid", u"text", 0, None, 0, ), (3, u"date_time", u"text", 0, None, 0, ), (4, u"reading", u"double precision", 0, None, 0, ), (5, u"unit", u"text", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"w_flow_momflow", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"instrumentid", u"text", 0, None, 0, ), (3, u"date_time", u"text", 0, None, 0, ), (4, u"reading", u"double precision", 0, None, 0, ), (5, u"unit", u"text", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"w_levels", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"date_time", u"text", 1, None, 1, ), (3, u"meas", u"double precision", 0, None, 0, ), (4, u"h_toc", u"double precision", 0, None, 0, ), (5, u"level_masl", u"double precision", 0, None, 0, ), (6, u"comment", u"text", 0, None, 0, )], (u"w_levels_geom", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"date_time", u"text", 0, None, 0, ), (3, u"meas", u"double precision", 0, None, 0, ), (4, u"h_toc", u"double precision", 0, None, 0, ), (5, u"level_masl", u"double precision", 0, None, 0, ), (6, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"w_levels_logger", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"date_time", u"text", 1, None, 1, ), (3, u"head_cm", u"double precision", 0, None, 0, ), (4, u"temp_degc", u"double precision", 0, None, 0, ), (5, u"cond_mscm", u"double precision", 0, None, 0, ), (6, u"level_masl", u"double precision", 0, None, 0, ), (7, u"comment", u"text", 0, None, 0, )], (u"w_lvls_last_geom", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"date_time", u"text", 0, None, 0, ), (3, u"meas", u"double precision", 0, None, 0, ), (4, u"level_masl", u"double precision", 0, None, 0, ), (5, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"w_qual_field", ), [(1, u"obsid", u"text", 1, None, 1, ), (2, u"staff", u"text", 0, None, 0, ), (3, u"date_time", u"text", 1, None, 1, ), (4, u"instrument", u"text", 0, None, 0, ), (5, u"parameter", u"text", 1, None, 1, ), (6, u"reading_num", u"double precision", 0, None, 0, ), (7, u"reading_txt", u"text", 0, None, 0, ), (8, u"unit", u"text", 1, None, 1, ), (9, u"depth", u"double precision", 0, None, 0, ), (10, u"comment", u"text", 0, None, 0, )], (u"w_qual_field_geom", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"staff", u"text", 0, None, 0, ), (3, u"date_time", u"text", 0, None, 0, ), (4, u"instrument", u"text", 0, None, 0, ), (5, u"parameter", u"text", 0, None, 0, ), (6, u"reading_num", u"double precision", 0, None, 0, ), (7, u"reading_txt", u"text", 0, None, 0, ), (8, u"unit", u"text", 0, None, 0, ), (9, u"comment", u"text", 0, None, 0, ), (10, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"w_qual_lab", ), [(1, u"obsid", u"text", 1, None, 0, ), (2, u"depth", u"double precision", 0, None, 0, ), (3, u"report", u"text", 1, None, 1, ), (4, u"project", u"text", 0, None, 0, ), (5, u"staff", u"text", 0, None, 0, ), (6, u"date_time", u"text", 0, None, 0, ), (7, u"anameth", u"text", 0, None, 0, ), (8, u"parameter", u"text", 1, None, 1, ), (9, u"reading_num", u"double precision", 0, None, 0, ), (10, u"reading_txt", u"text", 0, None, 0, ), (11, u"unit", u"text", 0, None, 0, ), (12, u"comment", u"text", 0, None, 0, )], (u"w_qual_lab_geom", ), [(1, u"obsid", u"text", 0, None, 0, ), (2, u"depth", u"double precision", 0, None, 0, ), (3, u"report", u"text", 0, None, 0, ), (4, u"staff", u"text", 0, None, 0, ), (5, u"date_time", u"text", 0, None, 0, ), (6, u"anameth", u"text", 0, None, 0, ), (7, u"parameter", u"text", 0, None, 0, ), (8, u"reading_txt", u"text", 0, None, 0, ), (9, u"reading_num", u"double precision", 0, None, 0, ), (10, u"unit", u"text", 0, None, 0, ), (11, u"geometry", u"USER-DEFINED", 0, None, 0, )], (u"zz_capacity", ), [(1, u"capacity", u"text", 1, None, 1, ), (2, u"explanation", u"text", 1, None, 0, )], (u"zz_capacity_plots", ), [(1, u"capacity", u"text", 1, None, 1, ), (2, u"color_qt", u"text", 1, None, 0, )], (u"zz_flowtype", ), [(1, u"type", u"text", 1, None, 1, ), (2, u"explanation", u"text", 0, None, 0, )], (u"zz_meteoparam", ), [(1, u"parameter", u"text", 1, None, 1, ), (2, u"explanation", u"text", 0, None, 0, )], (u"zz_staff", ), [(1, u"staff", u"text", 1, None, 1, ), (2, u"name", u"text", 0, None, 0, )], (u"zz_strat", ), [(1, u"geoshort", u"text", 1, None, 1, ), (2, u"strata", u"text", 1, None, 0, )], (u"zz_stratigraphy_plots", ), [(1, u"strata", u"text", 1, None, 1, ), (2, u"color_mplot", u"text", 1, None, 0, ), (3, u"hatch_mplot", u"text", 1, None, 0, ), (4, u"color_qt", u"text", 1, None, 0, ), (5, u"brush_qt", u"text", 1, None, 0, )]]'

        test_string = defs.db_setup_as_string()
        print(test_string)
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_about_db_creation(self, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        """
        Check that about_db is written correctly
        """
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()
        assert db_utils.check_connection_ok()

        #print(str(utils.sql_load_fr_db(u'select * from about_db')))

        reference = u'''(True, [(u"*", u"*", u"", u"", u"", u"", u"", u"locale:sv_SE", u"", u"", ), (u"about_db", u"*", u"", u"", u"", u"", u"", u"A status log for the tables in the db", None, None, ), (u"about_db", u"tablename", u"text", u"", u"", u"", u"", u"Name of a table in the db", None, None, ), (u"about_db", u"columnname", u"text", u"", u"", u"", u"", u"Name of column", None, None, ), (u"about_db", u"data_type", u"text", u"", u"", u"", u"", u"Data type of the column", None, None, ), (u"about_db", u"not_null", u"text", u"", u"", u"", u"", u"1 if NULL-values isn't allowed", None, None, ), (u"about_db", u"default_value", u"text", u"", u"", u"", u"", u"The default value of the column", None, None, ), (u"about_db", u"primary_key", u"text", u"", u"", u"", u"", u"The primary key order number if column is a primary key", None, None, ), (u"about_db", u"foreign_key", u"text", u"", u"", u"", u"", u"foreign key table(foreign key column)", None, None, ), (u"about_db", u"description", u"text", u"", u"", u"", u"", u"Description for column or table", None, None, ), (u"about_db", u"upd_date", u"text", u"", u"", u"", u"", u"Date for last update", None, None, ), (u"about_db", u"upd_sign", u"text", u"", u"", u"", u"", u"Person responsible for update", None, None, ), (u"comments", u"*", u"", u"", u"", u"", u"", u"Comments connected to obsids", None, None, ), (u"comments", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"comments", u"date_time", u"text", u"1", u"", u"1", u"", u"Date and Time for the comment", None, None, ), (u"comments", u"comment", u"text", u"1", u"", u"", u"", u"Comment", None, None, ), (u"comments", u"staff", u"text", u"1", u"", u"", u"zz_staff(staff)", u"Staff who made the comment", None, None, ), (u"meteo", u"*", u"", u"", u"", u"", u"", u"meteorological observations", None, None, ), (u"meteo", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"meteo", u"instrumentid", u"text", u"1", u"", u"1", u"", u"Instrument ID", None, None, ), (u"meteo", u"parameter", u"text", u"1", u"", u"1", u"zz_meteoparam(parameter)", u"The meteorological parameter", None, None, ), (u"meteo", u"date_time", u"text", u"1", u"", u"1", u"", u"Date and Time for the observation", None, None, ), (u"meteo", u"reading_num", u"double precision", u"", u"", u"", u"", u"Value (real number) reading for the parameter", None, None, ), (u"meteo", u"reading_txt", u"text", u"", u"", u"", u"", u"Value as text (ex. can contain '>' and '<')", None, None, ), (u"meteo", u"unit", u"text", u"", u"", u"", u"", u"Unit corresponding to the value reading", None, None, ), (u"meteo", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"obs_lines", u"*", u"", u"", u"", u"", u"", u"One of the two main tables. This table holds all line observation objects.", None, None, ), (u"obs_lines", u"obsid", u"text", u"1", u"", u"1", u"", u"ID for observation line", None, None, ), (u"obs_lines", u"name", u"text", u"", u"", u"", u"", u"Ordinary name for the observation", None, None, ), (u"obs_lines", u"place", u"text", u"", u"", u"", u"", u"Place for the observation", None, None, ), (u"obs_lines", u"type", u"text", u"", u"", u"", u"", u"Type of observation", None, None, ), (u"obs_lines", u"source", u"text", u"", u"", u"", u"", u"The origin for the observation", None, None, ), (u"obs_lines", u"geometry", u"USER-DEFINED", u"", u"", u"", u"", u"None", None, None, ), (u"obs_points", u"*", u"", u"", u"", u"", u"", u"One of the two main tables. This table holds all point observation objects.", None, None, ), (u"obs_points", u"obsid", u"text", u"1", u"", u"1", u"", u"ID for the observation point", None, None, ), (u"obs_points", u"name", u"text", u"", u"", u"", u"", u"Ordinary name for the observation", None, None, ), (u"obs_points", u"place", u"text", u"", u"", u"", u"", u"Place for the observation. E.g. estate", None, None, ), (u"obs_points", u"type", u"text", u"", u"", u"", u"", u"Type of observation", None, None, ), (u"obs_points", u"length", u"double precision", u"", u"", u"", u"", u"Borehole length from ground surface to bottom (equals to depth if vertical)", None, None, ), (u"obs_points", u"drillstop", u"text", u"", u"", u"", u"", u"Drill stop (ex Driven to bedrock)", None, None, ), (u"obs_points", u"diam", u"double precision", u"", u"", u"", u"", u"Inner diameter for casing or upper part of borehole", None, None, ), (u"obs_points", u"material", u"text", u"", u"", u"", u"", u"Well material", None, None, ), (u"obs_points", u"screen", u"text", u"", u"", u"", u"", u"Type of well screen", None, None, ), (u"obs_points", u"capacity", u"text", u"", u"", u"", u"", u"Well capacity", None, None, ), (u"obs_points", u"drilldate", u"text", u"", u"", u"", u"", u"Date when drilling was completed", None, None, ), (u"obs_points", u"wmeas_yn", u"integer", u"", u"", u"", u"", u"1/0 if water level is to be measured for this point or not", None, None, ), (u"obs_points", u"wlogg_yn", u"integer", u"", u"", u"", u"", u"1/0 if water level if borehole is equipped with a logger or not", None, None, ), (u"obs_points", u"east", u"double precision", u"", u"", u"", u"", u"Eastern coordinate (in the corresponding CRS)", None, None, ), (u"obs_points", u"north", u"double precision", u"", u"", u"", u"", u"Northern coordinate (in the corresponding CRS)", None, None, ), (u"obs_points", u"ne_accur", u"double precision", u"", u"", u"", u"", u"Approximate inaccuracy for coordinates", None, None, ), (u"obs_points", u"ne_source", u"text", u"", u"", u"", u"", u"Source for the given position", None, None, ), (u"obs_points", u"h_toc", u"double precision", u"", u"", u"", u"", u"Elevation (masl) for the measuring point", None, None, ), (u"obs_points", u"h_tocags", u"double precision", u"", u"", u"", u"", u"Distance from Measuring point to Ground Surface (m)", None, None, ), (u"obs_points", u"h_gs", u"double precision", u"", u"", u"", u"", u"Ground Surface level (m).", None, None, ), (u"obs_points", u"h_accur", u"double precision", u"", u"", u"", u"", u"Inaccuracy (m) for Measuring Point level", None, None, ), (u"obs_points", u"h_syst", u"text", u"", u"", u"", u"", u"Reference system for elevation", None, None, ), (u"obs_points", u"h_source", u"text", u"", u"", u"", u"", u"Source for the measuring point elevation (consultancy report or similar)", None, None, ), (u"obs_points", u"source", u"text", u"", u"", u"", u"", u"The source for the observation point", None, None, ), (u"obs_points", u"com_onerow", u"text", u"", u"", u"", u"", u"Onerow comment", None, None, ), (u"obs_points", u"com_html", u"text", u"", u"", u"", u"", u"Multiline formatted comment in html format", None, None, ), (u"obs_points", u"geometry", u"USER-DEFINED", u"", u"", u"", u"", u"None", None, None, ), (u"seismic_data", u"*", u"", u"", u"", u"", u"", u"Interpreted data from seismic measurements", None, None, ), (u"seismic_data", u"obsid", u"text", u"1", u"", u"1", u"obs_lines(obsid)", u"Obsid linked to obs_lines.obsid", None, None, ), (u"seismic_data", u"length", u"double precision", u"1", u"", u"1", u"", u"Length along line", None, None, ), (u"seismic_data", u"ground", u"double precision", u"", u"", u"", u"", u"Ground surface level", None, None, ), (u"seismic_data", u"bedrock", u"double precision", u"", u"", u"", u"", u"Interpreted level for bedrock surface", None, None, ), (u"seismic_data", u"gw_table", u"double precision", u"", u"", u"", u"", u"Interpreted level for limit between unsaturated/saturated conditions", None, None, ), (u"seismic_data", u"comment", u"text", u"", u"", u"", u"", u"Additional info", None, None, ), (u"stratigraphy", u"*", u"", u"", u"", u"", u"", u"Stratigraphy information from drillings", None, None, ), (u"stratigraphy", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"stratigraphy", u"stratid", u"integer", u"1", u"", u"1", u"", u"Stratigraphy layer ID for the OBSID", None, None, ), (u"stratigraphy", u"depthtop", u"double precision", u"", u"", u"", u"", u"Top of the layer in m from ground surface", None, None, ), (u"stratigraphy", u"depthbot", u"double precision", u"", u"", u"", u"", u"Bottom of the layer in m from ground surface", None, None, ), (u"stratigraphy", u"geology", u"text", u"", u"", u"", u"", u"Full description of geology", None, None, ), (u"stratigraphy", u"geoshort", u"text", u"", u"", u"", u"", u"Short description of geology", None, None, ), (u"stratigraphy", u"capacity", u"text", u"", u"", u"", u"", u"Well development at the layer", None, None, ), (u"stratigraphy", u"development", u"text", u"", u"", u"", u"", u"Well development - Is the flushed water clear and free of suspended solids?", None, None, ), (u"stratigraphy", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"vlf_data", u"*", u"", u"", u"", u"", u"", u"Raw data from VLF measurements", None, None, ), (u"vlf_data", u"obsid", u"text", u"1", u"", u"1", u"obs_lines(obsid)", u"Obsid linked to obs_lines.obsid", None, None, ), (u"vlf_data", u"length", u"double precision", u"1", u"", u"1", u"", u"Length along line", None, None, ), (u"vlf_data", u"real_comp", u"double precision", u"", u"", u"", u"", u"Raw data real component (in-phase(%))", None, None, ), (u"vlf_data", u"imag_comp", u"double precision", u"", u"", u"", u"", u"Raw data imaginary component", None, None, ), (u"vlf_data", u"comment", u"text", u"", u"", u"", u"", u"Additional info", None, None, ), (u"w_flow", u"*", u"", u"", u"", u"", u"", u"Water flow", None, None, ), (u"w_flow", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"w_flow", u"instrumentid", u"text", u"1", u"", u"1", u"", u"Instrument Id", None, None, ), (u"w_flow", u"flowtype", u"text", u"1", u"", u"1", u"zz_flowtype(type)", u"Flowtype must correspond to type in flowtypes", None, None, ), (u"w_flow", u"date_time", u"text", u"1", u"", u"1", u"", u"Date and Time for the observation", None, None, ), (u"w_flow", u"reading", u"double precision", u"", u"", u"", u"", u"Value (real number) reading for the flow rate", None, None, ), (u"w_flow", u"unit", u"text", u"", u"", u"", u"", u"Unit corresponding to the value reading", None, None, ), (u"w_flow", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"w_levels", u"*", u"", u"", u"", u"", u"", u"Manual water level measurements", None, None, ), (u"w_levels", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"w_levels", u"date_time", u"text", u"1", u"", u"1", u"", u"Date and Time for the observation", None, None, ), (u"w_levels", u"meas", u"double precision", u"", u"", u"", u"", u"Distance from measuring point to water level", None, None, ), (u"w_levels", u"h_toc", u"double precision", u"", u"", u"", u"", u"Elevation (masl) for the measuring point at the particular date_time (measuring point elevation may vary by time)", None, None, ), (u"w_levels", u"level_masl", u"double precision", u"", u"", u"", u"", u"Water level elevation (masl) calculated from measuring point and distance from measuring point to water level", None, None, ), (u"w_levels", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"w_levels_logger", u"*", u"", u"", u"", u"", u"", u"Automatic water level readings", None, None, ), (u"w_levels_logger", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"w_levels_logger", u"date_time", u"text", u"1", u"", u"1", u"", u"Date and Time for the observation", None, None, ), (u"w_levels_logger", u"head_cm", u"double precision", u"", u"", u"", u"", u"Pressure (cm water column) on pressure transducer", None, None, ), (u"w_levels_logger", u"temp_degc", u"double precision", u"", u"", u"", u"", u"Temperature degrees C", None, None, ), (u"w_levels_logger", u"cond_mscm", u"double precision", u"", u"", u"", u"", u"Electrical conductivity mS/cm", None, None, ), (u"w_levels_logger", u"level_masl", u"double precision", u"", u"", u"", u"", u"Corresponding Water level elevation (masl)", None, None, ), (u"w_levels_logger", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"w_qual_field", u"*", u"", u"", u"", u"", u"", u"Water quality from field measurements", None, None, ), (u"w_qual_field", u"obsid", u"text", u"1", u"", u"1", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"w_qual_field", u"staff", u"text", u"", u"", u"", u"zz_staff(staff)", u"Field staff", None, None, ), (u"w_qual_field", u"date_time", u"text", u"1", u"", u"1", u"", u"Date and Time for the observation", None, None, ), (u"w_qual_field", u"instrument", u"text", u"", u"", u"", u"", u"Instrument ID", None, None, ), (u"w_qual_field", u"parameter", u"text", u"1", u"", u"1", u"", u"Measured parameter", None, None, ), (u"w_qual_field", u"reading_num", u"double precision", u"", u"", u"", u"", u"Value as real number", None, None, ), (u"w_qual_field", u"reading_txt", u"text", u"", u"", u"", u"", u"Value as text (ex. can contain '>' and '<')", None, None, ), (u"w_qual_field", u"unit", u"text", u"1", u"", u"1", u"", u"Unit", None, None, ), (u"w_qual_field", u"depth", u"double precision", u"", u"", u"", u"", u"The depth at which the measurement was done", None, None, ), (u"w_qual_field", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"w_qual_lab", u"*", u"", u"", u"", u"", u"", u"Water quality from laboratory analysis", None, None, ), (u"w_qual_lab", u"obsid", u"text", u"1", u"", u"", u"obs_points(obsid)", u"Obsid linked to obs_points.obsid", None, None, ), (u"w_qual_lab", u"depth", u"double precision", u"", u"", u"", u"", u"Depth (m below h_gs) from where sample is taken", None, None, ), (u"w_qual_lab", u"report", u"text", u"1", u"", u"1", u"", u"Report no from laboratory", None, None, ), (u"w_qual_lab", u"project", u"text", u"", u"", u"", u"", u"Project number", None, None, ), (u"w_qual_lab", u"staff", u"text", u"", u"", u"", u"zz_staff(staff)", u"Field staff", None, None, ), (u"w_qual_lab", u"date_time", u"text", u"", u"", u"", u"", u"Date and Time for the observation", None, None, ), (u"w_qual_lab", u"anameth", u"text", u"", u"", u"", u"", u"Analysis method", None, None, ), (u"w_qual_lab", u"parameter", u"text", u"1", u"", u"1", u"", u"Measured parameter", None, None, ), (u"w_qual_lab", u"reading_num", u"double precision", u"", u"", u"", u"", u"Value as real number", None, None, ), (u"w_qual_lab", u"reading_txt", u"text", u"", u"", u"", u"", u"Value as text (ex. can contain '>' and '<')", None, None, ), (u"w_qual_lab", u"unit", u"text", u"", u"", u"", u"", u"Unit", None, None, ), (u"w_qual_lab", u"comment", u"text", u"", u"", u"", u"", u"Comment", None, None, ), (u"zz_capacity", u"*", u"", u"", u"", u"", u"", u"Data domain for capacity classes used by the plugin", None, None, ), (u"zz_capacity", u"capacity", u"text", u"1", u"", u"1", u"", u"Water capacity (ex. in the range 1-6)", None, None, ), (u"zz_capacity", u"explanation", u"text", u"1", u"", u"", u"", u"Description of water capacity classes", None, None, ), (u"zz_capacity_plots", u"*", u"", u"", u"", u"", u"", u"Data domain for capacity plot colors used by the plugin", None, None, ), (u"zz_capacity_plots", u"capacity", u"text", u"1", u"", u"1", u"zz_capacity(capacity)", u"Water capacity (ex. in the range 1-6)", None, None, ), (u"zz_capacity_plots", u"color_qt", u"text", u"1", u"", u"", u"", u"Hatchcolor codes for Qt plots", None, None, ), (u"zz_flowtype", u"*", u"", u"", u"", u"", u"", u"Data domain for flowtypes in table w_flow", None, None, ), (u"zz_flowtype", u"type", u"text", u"1", u"", u"1", u"", u"Allowed flowtypes", None, None, ), (u"zz_flowtype", u"explanation", u"text", u"", u"", u"", u"", u"Explanation of the flowtypes", None, None, ), (u"zz_meteoparam", u"*", u"", u"", u"", u"", u"", u"Data domain for meteorological parameters in meteo", None, None, ), (u"zz_meteoparam", u"parameter", u"text", u"1", u"", u"1", u"", u"Allowed meteorological parameters", None, None, ), (u"zz_meteoparam", u"explanation", u"text", u"", u"", u"", u"", u"Explanation of the parameters", None, None, ), (u"zz_staff", u"*", u"", u"", u"", u"", u"", u"Data domain for field staff used when importing data", None, None, ), (u"zz_staff", u"staff", u"text", u"1", u"", u"1", u"", u"Initials of the field staff", None, None, ), (u"zz_staff", u"name", u"text", u"", u"", u"", u"", u"Name of the field staff", None, None, ), (u"zz_strat", u"*", u"", u"", u"", u"", u"", u"Data domain for stratigraphy classes", None, None, ), (u"zz_strat", u"geoshort", u"text", u"1", u"", u"1", u"", u"Abbreviation for the strata (stratigraphy class)", None, None, ), (u"zz_strat", u"strata", u"text", u"1", u"", u"", u"", u"clay etc", None, None, ), (u"zz_stratigraphy_plots", u"*", u"", u"", u"", u"", u"", u"Data domain for stratigraphy plot colors and symbols used by the plugin", None, None, ), (u"zz_stratigraphy_plots", u"strata", u"text", u"1", u"", u"1", u"", u"clay etc", None, None, ), (u"zz_stratigraphy_plots", u"color_mplot", u"text", u"1", u"", u"", u"", u"Color codes for matplotlib plots", None, None, ), (u"zz_stratigraphy_plots", u"hatch_mplot", u"text", u"1", u"", u"", u"", u"Hatch codes for matplotlib plots", None, None, ), (u"zz_stratigraphy_plots", u"color_qt", u"text", u"1", u"", u"", u"", u"Color codes for Qt plots", None, None, ), (u"zz_stratigraphy_plots", u"brush_qt", u"text", u"1", u"", u"", u"", u"Brush types for Qt plots", None, None, )], )'''


        result = db_utils.sql_load_fr_db(u"SELECT * FROM about_db WHERE tablename NOT IN %s OFFSET 1"%db_utils.postgis_internal_tables())
        test_string = utils.anything_to_string_representation(result)
        print(test_string)

        printnum = 40
        for charnr in xrange(len(test_string)):
            if test_string[charnr] != reference[charnr]:
                #print(u'%s\n%s'%(test_string[charnr-printnum:charnr+printnum], reference[charnr-printnum:charnr+printnum]))
                break
        assert test_string == reference

    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_about_db_creation_version_string(self, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        """
        Check that version string in about_db is written correctly
        """
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()
        assert db_utils.check_connection_ok()

        result = db_utils.sql_load_fr_db(u"SELECT * FROM about_db LIMIT 1")
        test_string = utils.anything_to_string_representation(result)
        print(test_string)

        ref_strings = [u'running QGIS version',
                        u'on top of PostGIS version PostgreSQL',
                        u'POSTGIS=']
        for ref_string in ref_strings:
            assert ref_string in test_string


@attr(status='on')
class TestObsPointsTriggers(utils_for_tests.MidvattenTestPostgisDbSv):
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def setUp(self, mock_messagebar):
        super(TestObsPointsTriggers, self).setUp()
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS trigger_after_insert_obs_points_geom_fr_coords ON obs_points;""")
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS trigger_after_update_obs_points_geom_fr_coords ON obs_points;""")
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS trigger_after_insert_obs_points_coords_fr_geom ON obs_points;""")
        db_utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS trigger_after_update_obs_points_coords_fr_geom ON obs_points;""")
        db_utils.sql_alter_db(u"""DROP FUNCTION IF EXISTS after_insert_obs_points_geom_fr_coords();""")
        db_utils.sql_alter_db(u"""DROP FUNCTION IF EXISTS after_update_obs_points_geom_fr_coords();""")
        db_utils.sql_alter_db(u"""DROP FUNCTION IF EXISTS after_insert_obs_points_coords_fr_geom();""")
        db_utils.sql_alter_db(u"""DROP FUNCTION IF EXISTS after_update_obs_points_coords_fr_geom();""")
        mock_calls = str(mock_messagebar.mock_calls)
        if mock_calls != u'[]':
            print(mock_calls)

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_triggers_not_change_existing(self, mock_messagebar):
        """ Adding triggers should not automatically change the db """
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None)])'

        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_triggers_add_east_north(self):
        """ Updating coordinates from NULL should create geometry. """
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', NULL, NULL)''')

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')

        db_utils.sql_alter_db(u"""update obs_points set east='1.0', north='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 2.0, POINT(1 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_triggers_not_deleting_geom_when_east_north_null(self):
        """ Adding triggers should not automatically delete geometry when east AND north is NULL """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, None, None, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_triggers_not_deleting_geom_when_one_east_north_null(self):
        
        """ Adding triggers should not automatically delete geometry when east OR north is NULL """
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')

        db_utils.sql_alter_db(u"""update obs_points set east=ST_X(geometry) where east is null and geometry is not null""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, None, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 2.0, None, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east=NULL""")
        db_utils.sql_alter_db(u"""update obs_points set north='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, None, 2.0, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='3.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 3.0, 2.0, POINT(3 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='4.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 4.0, 2.0, POINT(4 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east=NULL, north=NULL""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, None, None, POINT(4 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db(u"""update obs_points set east='5.0', north='6.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 5.0, 6.0, POINT(5 6))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_geometry_from_east_north(self):
        """ Test that adding triggers and adding obsid with east, north also adds geometry
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_east_north_from_geometry(self):
        """ Test that adding triggers and adding obsid with geometry also adds east, north
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and adding obsid don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', ST_GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, None, None, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from geometry don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', ST_GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from east, north don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb2', 2, 2)""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_update_geometry_from_east_north(self):
        """ Test that adding triggers and updating obsid with east, north also updates geometry
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        db_utils.sql_alter_db(u'''UPDATE obs_points SET east = 2, north = 2 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_update_east_north_from_geometry(self):
        """ Test that adding triggers and updating obsid with geometry also updates east, north
        :return:
        """
        
        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u'''UPDATE obs_points SET geometry = ST_GeomFromText('POINT(2.0 2.0)', 3006) WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_trigger_update_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and updating obsid don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', ST_GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u'''UPDATE obs_points SET geometry = ST_GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, None, None, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_update_trigger_add_geometry_not_nulling_east_north(self,):
        """ Test that adding triggers and updating obsid from geometry don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, ST_GeomFromText('POINT(1.0 1.0)', 3006));""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, ST_GeomFromText('POINT(2.0 2.0)', 3006));""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""UPDATE obs_points SET geometry = ST_GeomFromText('POINT(3.0 3.0)', 3006) WHERE obsid='rb1';""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid;'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'


        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_update_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """
        
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, ST_GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, ST_GeomFromText('POINT(2.0 2.0)', 3006))""")

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')

        db_utils.sql_alter_db(u'''UPDATE obs_points SET east = 3, north = 3 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_obsid_without_anything(self):
        """
        :return:
        """

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb1')""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb2')""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, None, None, None), (rb2, None, None, None)])'
        assert test_string == reference_string

    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_add_trigger_add_obsid_without_anything_not_changing_existing(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """

        utils.add_triggers_to_obs_points('insert_obs_points_triggers_postgis.sql')
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', ST_GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb2')""")
        db_utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb3')""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, east, north, ST_AsText(geometry) from obs_points order by obsid'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, None, None, None), (rb3, None, None, None)])'
        assert test_string == reference_string


@attr(status='on')
class TestSqls(utils_for_tests.MidvattenTestPostgisDbSvImportInstance):

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_import_null_as_double(self, mock_messagebar):
        """ Adding triggers should not automatically change the db """
        sql = u'''INSERT INTO obs_points (obsid, length) VALUES ('rb1', CASE WHEN NULL IS NULL THEN %s END)'''%db_utils.cast_null(u'double precision')
        db_utils.sql_alter_db(sql)
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'select obsid, length FROM obs_points'))
        reference_string = u'(True, [(rb1, None)])'
        print(str(mock_messagebar.mock_calls))
        print(test_string)
        assert test_string == reference_string