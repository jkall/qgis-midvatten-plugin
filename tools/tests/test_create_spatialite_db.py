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
from __future__ import absolute_import
from __future__ import print_function

import ast
from builtins import range
from builtins import str

import mock
from nose.plugins.attrib import attr

from midvatten.tools.utils import common_utils, midvatten_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.definitions import midvatten_defs as defs


@attr(status='on')
class TestCreateMemoryDb(utils_for_tests.MidvattenTestSpatialiteNotCreated):
    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def test_memory_db(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_not_found, mock_iface):
        def side_effect(*args, **kwargs):
            mock_result = mock.MagicMock()
            if kwargs.get('combobox_label', None) == 'Locales':
                mock_result.answer = 'ok'
                mock_result.value = 'sv_SE'
            elif kwargs.get('combobox_label', None) == 'Timezone':
                mock_result.answer = 'ok'
                mock_result.value = ''
            return mock_result
        mock_not_found.side_effect = side_effect

        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = ':memory:'
        self.midvatten.new_db()


@attr(status='on')
class TestCreateDb(utils_for_tests.MidvattenTestSpatialiteNotCreated):
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def test_create_db_locale_sv(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_not_found, mock_iface, mock_messagebar):
        def side_effect(*args, **kwargs):
            mock_result = mock.MagicMock()
            if kwargs.get('combobox_label', None) == 'Locales':
                mock_result.answer = 'ok'
                mock_result.value = 'sv_SE'
            elif kwargs.get('combobox_label', None) == 'Timezone':
                mock_result.answer = 'ok'
                mock_result.value = ''
            return mock_result
        mock_not_found.side_effect = side_effect

        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')

        self.midvatten.new_db()
        assert db_utils.check_connection_ok()
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select * from zz_strat'))
        reference_string = r"""(True, [(berg, berg), (b, berg), (rock, berg), (ro, berg), (grovgrus, grovgrus), (grg, grovgrus), (coarse gravel, grovgrus), (cgr, grovgrus), (grus, grus), (gr, grus), (gravel, grus), (mellangrus, mellangrus), (grm, mellangrus), (medium gravel, mellangrus), (mgr, mellangrus), (fingrus, fingrus), (grf, fingrus), (fine gravel, fingrus), (fgr, fingrus), (grovsand, grovsand), (sag, grovsand), (coarse sand, grovsand), (csa, grovsand), (sand, sand), (sa, sand), (mellansand, mellansand), (sam, mellansand), (medium sand, mellansand), (msa, mellansand), (finsand, finsand), (saf, finsand), (fine sand, finsand), (fsa, finsand), (silt, silt), (si, silt), (lera, lera), (ler, lera), (le, lera), (clay, lera), (cl, lera), (morän, morän), (moran, morän), (mn, morän), (till, morän), (ti, morän), (torv, torv), (t, torv), (peat, torv), (pt, torv), (fyll, fyll), (fyllning, fyll), (f, fyll), (made ground, fyll), (mg, fyll), (land fill, fyll)])"""
        assert test_string == reference_string
        current_locale = midvatten_utils.getcurrentlocale()[0]
        assert current_locale == 'sv_SE'

    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def test_create_db_locale_en(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_not_found, mock_iface):
        def side_effect(*args, **kwargs):
            mock_result = mock.MagicMock()
            if kwargs.get('combobox_label', None) == 'Locales':
                mock_result.answer = 'ok'
                mock_result.value = 'en_US'
            elif kwargs.get('combobox_label', None) == 'Timezone':
                mock_result.answer = 'ok'
                mock_result.value = ''
            return mock_result
        mock_not_found.side_effect = side_effect

        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')
        self.midvatten.new_db()
        assert db_utils.check_connection_ok()
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select * from zz_strat'))
        reference_string = r"""(True, [(berg, rock), (b, rock), (rock, rock), (ro, rock), (grovgrus, coarse gravel), (grg, coarse gravel), (coarse gravel, coarse gravel), (cgr, coarse gravel), (grus, gravel), (gr, gravel), (gravel, gravel), (mellangrus, medium gravel), (grm, medium gravel), (medium gravel, medium gravel), (mgr, medium gravel), (fingrus, fine gravel), (grf, fine gravel), (fine gravel, fine gravel), (fgr, fine gravel), (grovsand, coarse sand), (sag, coarse sand), (coarse sand, coarse sand), (csa, coarse sand), (sand, sand), (sa, sand), (mellansand, medium sand), (sam, medium sand), (medium sand, medium sand), (msa, medium sand), (finsand, fine sand), (saf, fine sand), (fine sand, fine sand), (fsa, fine sand), (silt, silt), (si, silt), (lera, clay), (ler, clay), (le, clay), (clay, clay), (cl, clay), (morän, till), (moran, till), (mn, till), (till, till), (ti, till), (torv, peat), (t, peat), (peat, peat), (pt, peat), (fyll, made ground), (fyllning, made ground), (f, made ground), (made ground, made ground), (mg, made ground), (land fill, made ground), (unknown, unknown)])"""
        assert test_string == reference_string
        current_locale = midvatten_utils.getcurrentlocale()[0]
        print(str(current_locale))
        assert current_locale == 'en_US'

    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def test_create_db_setup_string(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_not_found, mock_iface):

        """
        This test fails every time anything other than comments are changed in create_db
        The purpose is to be sure that every change is meant to be.
        """
        def side_effect(*args, **kwargs):
            mock_result = mock.MagicMock()
            if kwargs.get('combobox_label', None) == 'Locales':
                mock_result.answer = 'ok'
                mock_result.value = 'sv_SE'
            elif kwargs.get('combobox_label', None) == 'Timezone':
                mock_result.answer = 'ok'
                mock_result.value = ''
            return mock_result
        mock_not_found.side_effect = side_effect

        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')
        self.midvatten.new_db()
        #reference_string_no_view_obs_points = '[("about_db", ), [(0, "tablename", "text", 0, None, 0, ), (1, "columnname", "text", 0, None, 0, ), (2, "data_type", "text", 0, None, 0, ), (3, "not_null", "text", 0, None, 0, ), (4, "default_value", "text", 0, None, 0, ), (5, "primary_key", "text", 0, None, 0, ), (6, "foreign_key", "text", 0, None, 0, ), (7, "description", "text", 0, None, 0, ), (8, "upd_date", "text", 0, None, 0, ), (9, "upd_sign", "text", 0, None, 0, )], ("comments", ), [(0, "obsid", "text", 1, None, 1, ), (1, "date_time", "text", 1, None, 2, ), (2, "comment", "text", 1, None, 0, ), (3, "staff", "text", 1, None, 0, )], ("zz_interlab4_obsid_assignment", ), [(0, "specifik_provplats", "text", 1, None, 1, ), (1, "provplatsnamn", "text", 1, None, 2, ), (2, "obsid", "text", 1, None, 0, )], ("meteo", ), [(0, "obsid", "text", 1, None, 1, ), (1, "instrumentid", "text", 1, None, 2, ), (2, "parameter", "text", 1, None, 3, ), (3, "date_time", "text", 1, None, 4, ), (4, "reading_num", "double", 0, None, 0, ), (5, "reading_txt", "text", 0, None, 0, ), (6, "unit", "text", 0, None, 0, ), (7, "comment", "text", 0, None, 0, )], ("obs_lines", ), [(0, "obsid", "text", 1, None, 1, ), (1, "name", "text", 0, None, 0, ), (2, "place", "text", 0, None, 0, ), (3, "type", "text", 0, None, 0, ), (4, "source", "text", 0, None, 0, ), (5, "geometry", "LINESTRING", 0, None, 0, )], ("obs_p_w_lvl", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_qual_field", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_qual_lab", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_strat", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "h_toc", "double", 0, None, 0, ), (3, "h_gs", "double", 0, None, 0, ), (4, "geometry", "POINT", 0, None, 0, )], ("obs_points", ), [(0, "obsid", "text", 1, None, 1, ), (1, "name", "text", 0, None, 0, ), (2, "place", "text", 0, None, 0, ), (3, "type", "text", 0, None, 0, ), (4, "length", "double", 0, None, 0, ), (5, "drillstop", "text", 0, None, 0, ), (6, "diam", "double", 0, None, 0, ), (7, "material", "text", 0, None, 0, ), (8, "screen", "text", 0, None, 0, ), (9, "capacity", "text", 0, None, 0, ), (10, "drilldate", "text", 0, None, 0, ), (11, "wmeas_yn", "INTEGER", 0, None, 0, ), (12, "wlogg_yn", "INTEGER", 0, None, 0, ), (13, "east", "double", 0, None, 0, ), (14, "north", "double", 0, None, 0, ), (15, "ne_accur", "double", 0, None, 0, ), (16, "ne_source", "text", 0, None, 0, ), (17, "h_toc", "double", 0, None, 0, ), (18, "h_tocags", "double", 0, None, 0, ), (19, "h_gs", "double", 0, None, 0, ), (20, "h_accur", "double", 0, None, 0, ), (21, "h_syst", "text", 0, None, 0, ), (22, "h_source", "text", 0, None, 0, ), (23, "source", "text", 0, None, 0, ), (24, "com_onerow", "text", 0, None, 0, ), (25, "com_html", "text", 0, None, 0, ), (26, "geometry", "POINT", 0, None, 0, )], ("seismic_data", ), [(0, "obsid", "text", 1, None, 1, ), (1, "length", "double", 1, None, 2, ), (2, "ground", "double", 0, None, 0, ), (3, "bedrock", "double", 0, None, 0, ), (4, "gw_table", "double", 0, None, 0, ), (5, "comment", "text", 0, None, 0, )], ("stratigraphy", ), [(0, "obsid", "text", 1, None, 1, ), (1, "stratid", "INTEGER", 1, None, 2, ), (2, "depthtop", "double", 0, None, 0, ), (3, "depthbot", "double", 0, None, 0, ), (4, "geology", "text", 0, None, 0, ), (5, "geoshort", "text", 0, None, 0, ), (6, "capacity", "text", 0, None, 0, ), (7, "development", "text", 0, None, 0, ), (8, "comment", "text", 0, None, 0, )], ("vlf_data", ), [(0, "obsid", "text", 1, None, 1, ), (1, "length", "double", 1, None, 2, ), (2, "real_comp", "double", 0, None, 0, ), (3, "imag_comp", "double", 0, None, 0, ), (4, "comment", "text", 0, None, 0, )], ("w_flow", ), [(0, "obsid", "text", 1, None, 1, ), (1, "instrumentid", "text", 1, None, 2, ), (2, "flowtype", "text", 1, None, 3, ), (3, "date_time", "text", 1, None, 4, ), (4, "reading", "double", 0, None, 0, ), (5, "unit", "text", 0, None, 0, ), (6, "comment", "text", 0, None, 0, )], ("w_flow_accvol", ), [(0, "obsid", "text", 0, None, 0, ), (1, "instrumentid", "text", 0, None, 0, ), (2, "date_time", "text", 0, None, 0, ), (3, "reading", "double", 0, None, 0, ), (4, "unit", "text", 0, None, 0, ), (5, "comment", "text", 0, None, 0, )], ("w_flow_aveflow", ), [(0, "obsid", "text", 0, None, 0, ), (1, "instrumentid", "text", 0, None, 0, ), (2, "date_time", "text", 0, None, 0, ), (3, "reading", "double", 0, None, 0, ), (4, "unit", "text", 0, None, 0, ), (5, "comment", "text", 0, None, 0, )], ("w_flow_momflow", ), [(0, "obsid", "text", 0, None, 0, ), (1, "instrumentid", "text", 0, None, 0, ), (2, "date_time", "text", 0, None, 0, ), (3, "reading", "double", 0, None, 0, ), (4, "unit", "text", 0, None, 0, ), (5, "comment", "text", 0, None, 0, )], ("w_levels", ), [(0, "obsid", "text", 1, None, 1, ), (1, "date_time", "text", 1, None, 2, ), (2, "meas", "double", 0, None, 0, ), (3, "h_toc", "double", 0, None, 0, ), (4, "level_masl", "double", 0, None, 0, ), (5, "comment", "text", 0, None, 0, )], ("w_levels_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "date_time", "text", 0, None, 0, ), (3, "meas", "double", 0, None, 0, ), (4, "h_toc", "double", 0, None, 0, ), (5, "level_masl", "double", 0, None, 0, ), (6, "geometry", "POINT", 0, None, 0, )], ("w_levels_logger", ), [(0, "obsid", "text", 1, None, 1, ), (1, "date_time", "text", 1, None, 2, ), (2, "head_cm", "double", 0, None, 0, ), (3, "temp_degc", "double", 0, None, 0, ), (4, "cond_mscm", "double", 0, None, 0, ), (5, "level_masl", "double", 0, None, 0, ), (6, "comment", "text", 0, None, 0, )], ("w_lvls_last_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "date_time", "", 0, None, 0, ), (3, "meas", "double", 0, None, 0, ), (4, "level_masl", "double", 0, None, 0, ), (5, "geometry", "POINT", 0, None, 0, )], ("w_qual_field", ), [(0, "obsid", "text", 1, None, 1, ), (1, "staff", "text", 0, None, 0, ), (2, "date_time", "text", 1, None, 2, ), (3, "instrument", "text", 0, None, 0, ), (4, "parameter", "text", 1, None, 3, ), (5, "reading_num", "double", 0, None, 0, ), (6, "reading_txt", "text", 0, None, 0, ), (7, "unit", "text", 0, None, 4, ), (8, "depth", "double", 0, None, 0, ), (9, "comment", "text", 0, None, 0, )], ("w_qual_field_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "staff", "text", 0, None, 0, ), (3, "date_time", "text", 0, None, 0, ), (4, "instrument", "text", 0, None, 0, ), (5, "parameter", "text", 0, None, 0, ), (6, "reading_num", "double", 0, None, 0, ), (7, "reading_txt", "text", 0, None, 0, ), (8, "unit", "text", 0, None, 0, ), (9, "comment", "text", 0, None, 0, ), (10, "geometry", "POINT", 0, None, 0, )], ("w_qual_lab", ), [(0, "obsid", "text", 1, None, 0, ), (1, "depth", "double", 0, None, 0, ), (2, "report", "text", 1, None, 1, ), (3, "project", "text", 0, None, 0, ), (4, "staff", "text", 0, None, 0, ), (5, "date_time", "text", 0, None, 0, ), (6, "anameth", "text", 0, None, 0, ), (7, "parameter", "text", 1, None, 2, ), (8, "reading_num", "double", 0, None, 0, ), (9, "reading_txt", "text", 0, None, 0, ), (10, "unit", "text", 0, None, 0, ), (11, "comment", "text", 0, None, 0, )], ("w_qual_lab_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "depth", "double", 0, None, 0, ), (3, "report", "text", 0, None, 0, ), (4, "staff", "text", 0, None, 0, ), (5, "date_time", "text", 0, None, 0, ), (6, "anameth", "text", 0, None, 0, ), (7, "parameter", "text", 0, None, 0, ), (8, "reading_txt", "text", 0, None, 0, ), (9, "reading_num", "double", 0, None, 0, ), (10, "unit", "text", 0, None, 0, ), (11, "geometry", "POINT", 0, None, 0, )], ("zz_capacity", ), [(0, "capacity", "text", 1, None, 1, ), (1, "explanation", "text", 1, None, 0, )], ("zz_capacity_plots", ), [(0, "capacity", "text", 1, None, 1, ), (1, "color_qt", "text", 1, None, 0, )], ("zz_flowtype", ), [(0, "type", "text", 1, None, 1, ), (1, "explanation", "text", 0, None, 0, )], ("zz_meteoparam", ), [(0, "parameter", "text", 1, None, 1, ), (1, "explanation", "text", 0, None, 0, )], ("zz_staff", ), [(0, "staff", "text", 1, None, 1, ), (1, "name", "text", 0, None, 0, )], ("zz_strat", ), [(0, "geoshort", "text", 1, None, 1, ), (1, "strata", "text", 1, None, 0, )], ("zz_stratigraphy_plots", ), [(0, "strata", "text", 1, None, 1, ), (1, "color_mplot", "text", 1, None, 0, ), (2, "hatch_mplot", "text", 1, None, 0, ), (3, "color_qt", "text", 1, None, 0, ), (4, "brush_qt", "text", 1, None, 0, )]]'
        reference_string_with_view_obs_points_obs_lines = '[("about_db", ), [(0, "id", "INTEGER", 0, None, 1, ), (1, "tablename", "TEXT", 0, None, 0, ), (2, "columnname", "TEXT", 0, None, 0, ), (3, "data_type", "TEXT", 0, None, 0, ), (4, "not_null", "TEXT", 0, None, 0, ), (5, "default_value", "TEXT", 0, None, 0, ), (6, "primary_key", "TEXT", 0, None, 0, ), (7, "foreign_key", "TEXT", 0, None, 0, ), (8, "description", "TEXT", 0, None, 0, ), (9, "upd_date", "TEXT", 0, None, 0, ), (10, "upd_sign", "TEXT", 0, None, 0, )], ("comments", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "date_time", "TEXT", 1, None, 2, ), (2, "comment", "TEXT", 1, None, 0, ), (3, "staff", "TEXT", 1, None, 0, ), (4, "type", "TEXT", 0, None, 0, )], ("meteo", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "instrumentid", "TEXT", 1, None, 2, ), (2, "parameter", "TEXT", 1, None, 3, ), (3, "date_time", "TEXT", 1, None, 4, ), (4, "reading_num", "double", 0, None, 0, ), (5, "reading_txt", "TEXT", 0, None, 0, ), (6, "unit", "TEXT", 0, None, 0, ), (7, "comment", "TEXT", 0, None, 0, )], ("obs_lines", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "name", "TEXT", 0, None, 0, ), (2, "place", "TEXT", 0, None, 0, ), (3, "type", "TEXT", 0, None, 0, ), (4, "source", "TEXT", 0, None, 0, ), (5, "geometry", "LINESTRING", 0, None, 0, )], ("obs_p_w_lvl", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_lvl_logger", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_qual_field", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_qual_lab", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "geometry", "POINT", 0, None, 0, )], ("obs_p_w_strat", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "h_toc", "double", 0, None, 0, ), (3, "h_gs", "double", 0, None, 0, ), (4, "geometry", "POINT", 0, None, 0, )], ("obs_points", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "name", "TEXT", 0, None, 0, ), (2, "place", "TEXT", 0, None, 0, ), (3, "type", "TEXT", 0, None, 0, ), (4, "length", "double", 0, None, 0, ), (5, "drillstop", "TEXT", 0, None, 0, ), (6, "diam", "double", 0, None, 0, ), (7, "material", "TEXT", 0, None, 0, ), (8, "screen", "TEXT", 0, None, 0, ), (9, "capacity", "TEXT", 0, None, 0, ), (10, "drilldate", "TEXT", 0, None, 0, ), (11, "wmeas_yn", "INTEGER", 0, None, 0, ), (12, "wlogg_yn", "INTEGER", 0, None, 0, ), (13, "east", "double", 0, None, 0, ), (14, "north", "double", 0, None, 0, ), (15, "ne_accur", "double", 0, None, 0, ), (16, "ne_source", "TEXT", 0, None, 0, ), (17, "h_toc", "double", 0, None, 0, ), (18, "h_tocags", "double", 0, None, 0, ), (19, "h_gs", "double", 0, None, 0, ), (20, "h_accur", "double", 0, None, 0, ), (21, "h_syst", "TEXT", 0, None, 0, ), (22, "h_source", "TEXT", 0, None, 0, ), (23, "source", "TEXT", 0, None, 0, ), (24, "com_onerow", "TEXT", 0, None, 0, ), (25, "com_html", "TEXT", 0, None, 0, ), (26, "geometry", "POINT", 0, None, 0, )], ("seismic_data", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "length", "double", 1, None, 2, ), (2, "ground", "double", 0, None, 0, ), (3, "bedrock", "double", 0, None, 0, ), (4, "gw_table", "double", 0, None, 0, ), (5, "comment", "TEXT", 0, None, 0, )], ("stratigraphy", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "stratid", "INTEGER", 1, None, 2, ), (2, "depthtop", "double", 0, None, 0, ), (3, "depthbot", "double", 0, None, 0, ), (4, "geology", "TEXT", 0, None, 0, ), (5, "geoshort", "TEXT", 0, None, 0, ), (6, "capacity", "TEXT", 0, None, 0, ), (7, "development", "TEXT", 0, None, 0, ), (8, "comment", "TEXT", 0, None, 0, )], ("view_obs_lines", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "name", "TEXT", 0, None, 0, ), (3, "place", "TEXT", 0, None, 0, ), (4, "type", "TEXT", 0, None, 0, ), (5, "source", "TEXT", 0, None, 0, ), (6, "geometry", "LINESTRING", 0, None, 0, )], ("view_obs_points", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "name", "TEXT", 0, None, 0, ), (3, "place", "TEXT", 0, None, 0, ), (4, "type", "TEXT", 0, None, 0, ), (5, "length", "double", 0, None, 0, ), (6, "drillstop", "TEXT", 0, None, 0, ), (7, "diam", "double", 0, None, 0, ), (8, "material", "TEXT", 0, None, 0, ), (9, "screen", "TEXT", 0, None, 0, ), (10, "capacity", "TEXT", 0, None, 0, ), (11, "drilldate", "TEXT", 0, None, 0, ), (12, "wmeas_yn", "INTEGER", 0, None, 0, ), (13, "wlogg_yn", "INTEGER", 0, None, 0, ), (14, "east", "double", 0, None, 0, ), (15, "north", "double", 0, None, 0, ), (16, "ne_accur", "double", 0, None, 0, ), (17, "ne_source", "TEXT", 0, None, 0, ), (18, "h_toc", "double", 0, None, 0, ), (19, "h_tocags", "double", 0, None, 0, ), (20, "h_gs", "double", 0, None, 0, ), (21, "h_accur", "double", 0, None, 0, ), (22, "h_syst", "TEXT", 0, None, 0, ), (23, "h_source", "TEXT", 0, None, 0, ), (24, "source", "TEXT", 0, None, 0, ), (25, "com_onerow", "TEXT", 0, None, 0, ), (26, "com_html", "TEXT", 0, None, 0, ), (27, "geometry", "POINT", 0, None, 0, )], ("vlf_data", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "length", "double", 1, None, 2, ), (2, "real_comp", "double", 0, None, 0, ), (3, "imag_comp", "double", 0, None, 0, ), (4, "comment", "TEXT", 0, None, 0, )], ("w_flow", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "instrumentid", "TEXT", 1, None, 2, ), (2, "flowtype", "TEXT", 1, None, 3, ), (3, "date_time", "TEXT", 1, None, 4, ), (4, "reading", "double", 0, None, 0, ), (5, "unit", "TEXT", 0, None, 0, ), (6, "comment", "TEXT", 0, None, 0, )], ("w_flow_accvol", ), [(0, "obsid", "TEXT", 0, None, 0, ), (1, "instrumentid", "TEXT", 0, None, 0, ), (2, "date_time", "TEXT", 0, None, 0, ), (3, "reading", "double", 0, None, 0, ), (4, "unit", "TEXT", 0, None, 0, ), (5, "comment", "TEXT", 0, None, 0, )], ("w_flow_aveflow", ), [(0, "obsid", "TEXT", 0, None, 0, ), (1, "instrumentid", "TEXT", 0, None, 0, ), (2, "date_time", "TEXT", 0, None, 0, ), (3, "reading", "double", 0, None, 0, ), (4, "unit", "TEXT", 0, None, 0, ), (5, "comment", "TEXT", 0, None, 0, )], ("w_flow_momflow", ), [(0, "obsid", "TEXT", 0, None, 0, ), (1, "instrumentid", "TEXT", 0, None, 0, ), (2, "date_time", "TEXT", 0, None, 0, ), (3, "reading", "double", 0, None, 0, ), (4, "unit", "TEXT", 0, None, 0, ), (5, "comment", "TEXT", 0, None, 0, )], ("w_levels", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "date_time", "TEXT", 1, None, 2, ), (2, "meas", "double", 0, None, 0, ), (3, "h_toc", "double", 0, None, 0, ), (4, "level_masl", "double", 0, None, 0, ), (5, "comment", "TEXT", 0, None, 0, )], ("w_levels_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "date_time", "TEXT", 0, None, 0, ), (3, "meas", "double", 0, None, 0, ), (4, "h_toc", "double", 0, None, 0, ), (5, "level_masl", "double", 0, None, 0, ), (6, "geometry", "POINT", 0, None, 0, )], ("w_levels_logger", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "date_time", "TEXT", 1, None, 2, ), (2, "head_cm", "double", 0, None, 0, ), (3, "temp_degc", "double", 0, None, 0, ), (4, "cond_mscm", "double", 0, None, 0, ), (5, "level_masl", "double", 0, None, 0, ), (6, "comment", "TEXT", 0, None, 0, ), (7, "source", "TEXT", 0, None, 0, )], ("w_lvls_last_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "date_time", "", 0, None, 0, ), (3, "meas", "double", 0, None, 0, ), (4, "level_masl", "double", 0, None, 0, ), (5, "h_tocags", "double", 0, None, 0, ), (6, "geometry", "POINT", 0, None, 0, )], ("w_qual_field", ), [(0, "obsid", "TEXT", 1, None, 1, ), (1, "staff", "TEXT", 0, None, 0, ), (2, "date_time", "TEXT", 1, None, 2, ), (3, "instrument", "TEXT", 0, None, 0, ), (4, "parameter", "TEXT", 1, None, 3, ), (5, "reading_num", "double", 0, None, 0, ), (6, "reading_txt", "TEXT", 0, None, 0, ), (7, "unit", "TEXT", 0, None, 4, ), (8, "depth", "double", 0, None, 0, ), (9, "comment", "TEXT", 0, None, 0, )], ("w_qual_field_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "staff", "TEXT", 0, None, 0, ), (3, "date_time", "TEXT", 0, None, 0, ), (4, "instrument", "TEXT", 0, None, 0, ), (5, "parameter", "TEXT", 0, None, 0, ), (6, "reading_num", "double", 0, None, 0, ), (7, "reading_txt", "TEXT", 0, None, 0, ), (8, "unit", "TEXT", 0, None, 0, ), (9, "comment", "TEXT", 0, None, 0, ), (10, "geometry", "POINT", 0, None, 0, )], ("w_qual_lab", ), [(0, "obsid", "TEXT", 1, None, 0, ), (1, "depth", "double", 0, None, 0, ), (2, "report", "TEXT", 1, None, 1, ), (3, "project", "TEXT", 0, None, 0, ), (4, "staff", "TEXT", 0, None, 0, ), (5, "date_time", "TEXT", 0, None, 0, ), (6, "anameth", "TEXT", 0, None, 0, ), (7, "parameter", "TEXT", 1, None, 2, ), (8, "reading_num", "double", 0, None, 0, ), (9, "reading_txt", "TEXT", 0, None, 0, ), (10, "unit", "TEXT", 0, None, 0, ), (11, "comment", "TEXT", 0, None, 0, )], ("w_qual_lab_geom", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "TEXT", 0, None, 0, ), (2, "depth", "double", 0, None, 0, ), (3, "report", "TEXT", 0, None, 0, ), (4, "staff", "TEXT", 0, None, 0, ), (5, "date_time", "TEXT", 0, None, 0, ), (6, "anameth", "TEXT", 0, None, 0, ), (7, "parameter", "TEXT", 0, None, 0, ), (8, "reading_txt", "TEXT", 0, None, 0, ), (9, "reading_num", "double", 0, None, 0, ), (10, "unit", "TEXT", 0, None, 0, ), (11, "geometry", "POINT", 0, None, 0, )], ("zz_capacity", ), [(0, "capacity", "TEXT", 1, None, 1, ), (1, "explanation", "TEXT", 1, None, 0, )], ("zz_capacity_plots", ), [(0, "capacity", "TEXT", 1, None, 1, ), (1, "color_qt", "TEXT", 1, None, 0, )], ("zz_flowtype", ), [(0, "type", "TEXT", 1, None, 1, ), (1, "explanation", "TEXT", 0, None, 0, )], ("zz_interlab4_obsid_assignment", ), [(0, "specifik_provplats", "TEXT", 1, None, 1, ), (1, "provplatsnamn", "TEXT", 1, None, 2, ), (2, "obsid", "TEXT", 1, None, 0, )], ("zz_meteoparam", ), [(0, "parameter", "TEXT", 1, None, 1, ), (1, "explanation", "TEXT", 0, None, 0, )], ("zz_staff", ), [(0, "staff", "TEXT", 1, None, 1, ), (1, "name", "TEXT", 0, None, 0, )], ("zz_strat", ), [(0, "geoshort", "TEXT", 1, None, 1, ), (1, "strata", "TEXT", 1, None, 0, )], ("zz_stratigraphy_plots", ), [(0, "strata", "TEXT", 1, None, 1, ), (1, "color_mplot", "TEXT", 1, None, 0, ), (2, "hatch_mplot", "TEXT", 1, None, 0, ), (3, "color_qt", "TEXT", 1, None, 0, ), (4, "brush_qt", "TEXT", 1, None, 0, )]]'
        #'("view_obs_points", ), [(0, "rowid", "INTEGER", 0, None, 0, ), (1, "obsid", "text", 0, None, 0, ), (2, "name", "text", 0, None, 0, ), (3, "place", "text", 0, None, 0, ), (4, "type", "text", 0, None, 0, ), (5, "length", "double", 0, None, 0, ), (6, "drillstop", "text", 0, None, 0, ), (7, "diam", "double", 0, None, 0, ), (8, "material", "text", 0, None, 0, ), (9, "screen", "text", 0, None, 0, ), (10, "capacity", "text", 0, None, 0, ), (11, "drilldate", "text", 0, None, 0, ), (12, "wmeas_yn", "INTEGER", 0, None, 0, ), (13, "wlogg_yn", "INTEGER", 0, None, 0, ), (14, "east", "double", 0, None, 0, ), (15, "north", "double", 0, None, 0, ), (16, "ne_accur", "double", 0, None, 0, ), (17, "ne_source", "text", 0, None, 0, ), (18, "h_toc", "double", 0, None, 0, ), (19, "h_tocags", "double", 0, None, 0, ), (20, "h_gs", "double", 0, None, 0, ), (21, "h_accur", "double", 0, None, 0, ), (22, "h_syst", "text", 0, None, 0, ), (23, "h_source", "text", 0, None, 0, ), (24, "source", "text", 0, None, 0, ), (25, "com_onerow", "text", 0, None, 0, ), (26, "com_html", "text", 0, None, 0, ), (27, "geometry", "POINT", 0, None, 0, )]'

        test_string = defs.db_setup_as_string()

        """aslist = ast.literal_eval(test_string)
        for idx, row in enumerate(aslist[1]):
            row = list(row)
            row[2] = row[2].lower()
            aslist[1][idx] = tuple(row)
        test_string = common_utils.anything_to_string_representation(aslist)"""

        #print("Test")
        #print(str(test_string))
        #print("\nref\n")
        #print(str(reference_string))
        #print(str())
        #print(str(test_string))
        #print(str(utils_for_tests.compare_strings(test_string, reference_string)))
        print(utils_for_tests.compare_strings(reference_string_with_view_obs_points_obs_lines, test_string))
        print(test_string)
        assert test_string == reference_string_with_view_obs_points_obs_lines

    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def test_about_db_creation(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_not_found, mock_iface):
        """
        Check that about_db is written correctly
        """
        def side_effect(*args, **kwargs):
            mock_result = mock.MagicMock()
            if kwargs.get('combobox_label', None) == 'Locales':
                mock_result.answer = 'ok'
                mock_result.value = 'sv_SE'
            elif kwargs.get('combobox_label', None) == 'Timezone':
                mock_result.answer = 'ok'
                mock_result.value = ''
            return mock_result
        mock_not_found.side_effect = side_effect

        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')
        self.midvatten.new_db()

        #print(str(midvatten_utils.sql_load_fr_db('select * from about_db')))

        reference = '''(True, [("*", "*", "", "", "", "", "", "locale:sv_SE", "", "", ), ("about_db", "*", "", "", "", "", "", "A status log for the tables in the db", None, None, ), ("about_db", "id", "INTEGER", "", "", "1", "", "None", None, None, ), ("about_db", "tablename", "TEXT", "", "", "", "", "Name of a table in the db", None, None, ), ("about_db", "columnname", "TEXT", "", "", "", "", "Name of column", None, None, ), ("about_db", "data_type", "TEXT", "", "", "", "", "Data type of the column", None, None, ), ("about_db", "not_null", "TEXT", "", "", "", "", "1 if NULL-values isn't allowed", None, None, ), ("about_db", "default_value", "TEXT", "", "", "", "", "The default value of the column", None, None, ), ("about_db", "primary_key", "TEXT", "", "", "", "", "The primary key order number if column is a primary key", None, None, ), ("about_db", "foreign_key", "TEXT", "", "", "", "", "Foreign key table(foreign key column)", None, None, ), ("about_db", "description", "TEXT", "", "", "", "", "Description for column or table", None, None, ), ("about_db", "upd_date", "TEXT", "", "", "", "", "Date for last update", None, None, ), ("about_db", "upd_sign", "TEXT", "", "", "", "", "Person responsible for update", None, None, ), ("comments", "*", "", "", "", "", "", "Comments connected to obsids", None, None, ), ("comments", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("comments", "date_time", "TEXT", "1", "", "2", "", "Date and Time for the comment", None, None, ), ("comments", "comment", "TEXT", "1", "", "", "", "Comment", None, None, ), ("comments", "staff", "TEXT", "1", "", "", "", "Staff who made the comment", None, None, ), ("comments", "type", "TEXT", "", "", "", "", "Can be used to distinguish different types of comments", None, None, ), ("meteo", "*", "", "", "", "", "", "meteorological observations", None, None, ), ("meteo", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("meteo", "instrumentid", "TEXT", "1", "", "2", "", "Instrument ID", None, None, ), ("meteo", "parameter", "TEXT", "1", "", "3", "zz_meteoparam(parameter)", "The meteorological parameter", None, None, ), ("meteo", "date_time", "TEXT", "1", "", "4", "", "Date and Time for the observation", None, None, ), ("meteo", "reading_num", "double", "", "", "", "", "Value (real number) reading for the parameter", None, None, ), ("meteo", "reading_txt", "TEXT", "", "", "", "", "Value as text (ex. can contain '>' and '<')", None, None, ), ("meteo", "unit", "TEXT", "", "", "", "", "Unit corresponding to the value reading", None, None, ), ("meteo", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("obs_lines", "*", "", "", "", "", "", "One of the two main tables. This table holds all line observation objects.", None, None, ), ("obs_lines", "obsid", "TEXT", "1", "", "1", "", "ID for observation line", None, None, ), ("obs_lines", "name", "TEXT", "", "", "", "", "Ordinary name for the observation", None, None, ), ("obs_lines", "place", "TEXT", "", "", "", "", "Place for the observation", None, None, ), ("obs_lines", "type", "TEXT", "", "", "", "", "Type of observation", None, None, ), ("obs_lines", "source", "TEXT", "", "", "", "", "The origin for the observation", None, None, ), ("obs_lines", "geometry", "LINESTRING", "", "", "", "", "None", None, None, ), ("obs_points", "*", "", "", "", "", "", "One of the two main tables. This table holds all point observation objects.", None, None, ), ("obs_points", "obsid", "TEXT", "1", "", "1", "", "ID for the observation point", None, None, ), ("obs_points", "name", "TEXT", "", "", "", "", "Ordinary name for the observation", None, None, ), ("obs_points", "place", "TEXT", "", "", "", "", "Place for the observation. E.g. estate", None, None, ), ("obs_points", "type", "TEXT", "", "", "", "", "Type of observation", None, None, ), ("obs_points", "length", "double", "", "", "", "", "Borehole length from ground surface to bottom (equals to depth if vertical)", None, None, ), ("obs_points", "drillstop", "TEXT", "", "", "", "", "Drill stop (ex 'Driven to bedrock')", None, None, ), ("obs_points", "diam", "double", "", "", "", "", "Inner diameter for casing or upper part of borehole", None, None, ), ("obs_points", "material", "TEXT", "", "", "", "", "Well material", None, None, ), ("obs_points", "screen", "TEXT", "", "", "", "", "Type of well screen", None, None, ), ("obs_points", "capacity", "TEXT", "", "", "", "", "Well capacity", None, None, ), ("obs_points", "drilldate", "TEXT", "", "", "", "", "Date when drilling was completed", None, None, ), ("obs_points", "wmeas_yn", "INTEGER", "", "", "", "", "1/0 if water level is to be measured for this point or not", None, None, ), ("obs_points", "wlogg_yn", "INTEGER", "", "", "", "", "1/0 if water level if borehole is equipped with a logger or not", None, None, ), ("obs_points", "east", "double", "", "", "", "", "Eastern coordinate (in the corresponding CRS)", None, None, ), ("obs_points", "north", "double", "", "", "", "", "Northern coordinate (in the corresponding CRS)", None, None, ), ("obs_points", "ne_accur", "double", "", "", "", "", "Approximate inaccuracy for coordinates", None, None, ), ("obs_points", "ne_source", "TEXT", "", "", "", "", "Source for the given position", None, None, ), ("obs_points", "h_toc", "double", "", "", "", "", "Elevation (masl) for the measuring point", None, None, ), ("obs_points", "h_tocags", "double", "", "", "", "", "Distance from Measuring point to Ground Surface (m)", None, None, ), ("obs_points", "h_gs", "double", "", "", "", "", "Ground Surface level (m).", None, None, ), ("obs_points", "h_accur", "double", "", "", "", "", "Inaccuracy (m) for Measuring Point level", None, None, ), ("obs_points", "h_syst", "TEXT", "", "", "", "", "Reference system for elevation", None, None, ), ("obs_points", "h_source", "TEXT", "", "", "", "", "Source for the measuring point elevation (consultancy report or similar)", None, None, ), ("obs_points", "source", "TEXT", "", "", "", "", "The source for the observation point", None, None, ), ("obs_points", "com_onerow", "TEXT", "", "", "", "", "Onerow comment", None, None, ), ("obs_points", "com_html", "TEXT", "", "", "", "", "Multiline formatted comment in html format", None, None, ), ("obs_points", "geometry", "POINT", "", "", "", "", "None", None, None, ), ("seismic_data", "*", "", "", "", "", "", "Interpreted data from seismic measurements", None, None, ), ("seismic_data", "obsid", "TEXT", "1", "", "1", "obs_lines(obsid)", "Obsid linked to obs_lines.obsid", None, None, ), ("seismic_data", "length", "double", "1", "", "2", "", "Length along line", None, None, ), ("seismic_data", "ground", "double", "", "", "", "", "Ground surface level", None, None, ), ("seismic_data", "bedrock", "double", "", "", "", "", "Interpreted level for bedrock surface", None, None, ), ("seismic_data", "gw_table", "double", "", "", "", "", "Interpreted level for limit between unsaturated/saturated conditions", None, None, ), ("seismic_data", "comment", "TEXT", "", "", "", "", "Additional info", None, None, ), ("stratigraphy", "*", "", "", "", "", "", "Stratigraphy information from drillings", None, None, ), ("stratigraphy", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("stratigraphy", "stratid", "INTEGER", "1", "", "2", "", "Stratigraphy layer ID for the OBSID", None, None, ), ("stratigraphy", "depthtop", "double", "", "", "", "", "Top of the layer in m from ground surface", None, None, ), ("stratigraphy", "depthbot", "double", "", "", "", "", "Bottom of the layer in m from ground surface", None, None, ), ("stratigraphy", "geology", "TEXT", "", "", "", "", "Full description of geology", None, None, ), ("stratigraphy", "geoshort", "TEXT", "", "", "", "", "Short description of geology", None, None, ), ("stratigraphy", "capacity", "TEXT", "", "", "", "", "Well development at the layer", None, None, ), ("stratigraphy", "development", "TEXT", "", "", "", "", "Well development - Is the flushed water clear and free of suspended solids?", None, None, ), ("stratigraphy", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("vlf_data", "*", "", "", "", "", "", "Raw data from VLF measurements", None, None, ), ("vlf_data", "obsid", "TEXT", "1", "", "1", "obs_lines(obsid)", "Obsid linked to obs_lines.obsid", None, None, ), ("vlf_data", "length", "double", "1", "", "2", "", "Length along line", None, None, ), ("vlf_data", "real_comp", "double", "", "", "", "", "Raw data real component (in-phase(%))", None, None, ), ("vlf_data", "imag_comp", "double", "", "", "", "", "Raw data imaginary component", None, None, ), ("vlf_data", "comment", "TEXT", "", "", "", "", "Additional info", None, None, ), ("w_flow", "*", "", "", "", "", "", "Water flow", None, None, ), ("w_flow", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("w_flow", "instrumentid", "TEXT", "1", "", "2", "", "Instrument Id", None, None, ), ("w_flow", "flowtype", "TEXT", "1", "", "3", "zz_flowtype(type)", "Flowtype must correspond to type in flowtypes", None, None, ), ("w_flow", "date_time", "TEXT", "1", "", "4", "", "Date and Time for the observation", None, None, ), ("w_flow", "reading", "double", "", "", "", "", "Value (real number) reading for the flow rate", None, None, ), ("w_flow", "unit", "TEXT", "", "", "", "", "Unit corresponding to the value reading", None, None, ), ("w_flow", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("w_levels", "*", "", "", "", "", "", "Manual water level measurements", None, None, ), ("w_levels", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("w_levels", "date_time", "TEXT", "1", "", "2", "", "Date and Time for the observation", None, None, ), ("w_levels", "meas", "double", "", "", "", "", "Distance from measuring point to water level", None, None, ), ("w_levels", "h_toc", "double", "", "", "", "", "Elevation (masl) for the measuring point at the particular date_time (measuring point elevation may vary by time)", None, None, ), ("w_levels", "level_masl", "double", "", "", "", "", "Water level elevation (masl) calculated from measuring point and distance from measuring point to water level", None, None, ), ("w_levels", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("w_levels_logger", "*", "", "", "", "", "", "Automatic water level readings", None, None, ), ("w_levels_logger", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("w_levels_logger", "date_time", "TEXT", "1", "", "2", "", "Date and Time for the observation", None, None, ), ("w_levels_logger", "head_cm", "double", "", "", "", "", "Pressure (cm water column) on pressure transducer", None, None, ), ("w_levels_logger", "temp_degc", "double", "", "", "", "", "Temperature degrees C", None, None, ), ("w_levels_logger", "cond_mscm", "double", "", "", "", "", "Electrical conductivity mS/cm", None, None, ), ("w_levels_logger", "level_masl", "double", "", "", "", "", "Corresponding Water level elevation (masl)", None, None, ), ("w_levels_logger", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("w_levels_logger", "source", "TEXT", "", "", "", "", "The source of the measurement (used to keep series apart)", None, None, ), ("w_qual_field", "*", "", "", "", "", "", "Water quality from field measurements", None, None, ), ("w_qual_field", "obsid", "TEXT", "1", "", "1", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("w_qual_field", "staff", "TEXT", "", "", "", "", "Field staff", None, None, ), ("w_qual_field", "date_time", "TEXT", "1", "", "2", "", "Date and Time for the observation", None, None, ), ("w_qual_field", "instrument", "TEXT", "", "", "", "", "Instrument ID", None, None, ), ("w_qual_field", "parameter", "TEXT", "1", "", "3", "", "Measured parameter", None, None, ), ("w_qual_field", "reading_num", "double", "", "", "", "", "Value as real number", None, None, ), ("w_qual_field", "reading_txt", "TEXT", "", "", "", "", "Value as text (ex. can contain '>' and '<')", None, None, ), ("w_qual_field", "unit", "TEXT", "", "", "4", "", "Unit", None, None, ), ("w_qual_field", "depth", "double", "", "", "", "", "The depth at which the measurement was done", None, None, ), ("w_qual_field", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("w_qual_lab", "*", "", "", "", "", "", "Water quality from laboratory analysis", None, None, ), ("w_qual_lab", "obsid", "TEXT", "1", "", "", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("w_qual_lab", "depth", "double", "", "", "", "", "Depth (m below h_gs) from where sample is taken", None, None, ), ("w_qual_lab", "report", "TEXT", "1", "", "1", "", "Report no from laboratory", None, None, ), ("w_qual_lab", "project", "TEXT", "", "", "", "", "Project number", None, None, ), ("w_qual_lab", "staff", "TEXT", "", "", "", "", "Field staff", None, None, ), ("w_qual_lab", "date_time", "TEXT", "", "", "", "", "Date and Time for the observation", None, None, ), ("w_qual_lab", "anameth", "TEXT", "", "", "", "", "Analysis method", None, None, ), ("w_qual_lab", "parameter", "TEXT", "1", "", "2", "", "Measured parameter", None, None, ), ("w_qual_lab", "reading_num", "double", "", "", "", "", "Value as real number", None, None, ), ("w_qual_lab", "reading_txt", "TEXT", "", "", "", "", "Value as text (ex. can contain '>' and '<')", None, None, ), ("w_qual_lab", "unit", "TEXT", "", "", "", "", "Unit", None, None, ), ("w_qual_lab", "comment", "TEXT", "", "", "", "", "Comment", None, None, ), ("zz_capacity", "*", "", "", "", "", "", "Data domain for capacity classes used by the plugin", None, None, ), ("zz_capacity", "capacity", "TEXT", "1", "", "1", "", "Water capacity (ex. in the range 1-6)", None, None, ), ("zz_capacity", "explanation", "TEXT", "1", "", "", "", "Description of water capacity classes", None, None, ), ("zz_capacity_plots", "*", "", "", "", "", "", "Data domain for capacity plot colors used by the plugin", None, None, ), ("zz_capacity_plots", "capacity", "TEXT", "1", "", "1", "zz_capacity(capacity)", "Water capacity (ex. in the range 1-6)", None, None, ), ("zz_capacity_plots", "color_qt", "TEXT", "1", "", "", "", "Hatchcolor codes for Qt plots", None, None, ), ("zz_flowtype", "*", "", "", "", "", "", "Data domain for flowtypes in table w_flow", None, None, ), ("zz_flowtype", "type", "TEXT", "1", "", "1", "", "Allowed flowtypes", None, None, ), ("zz_flowtype", "explanation", "TEXT", "", "", "", "", "Explanation of the flowtypes", None, None, ), ("zz_interlab4_obsid_assignment", "*", "", "", "", "", "", "Assign obsids automatically during interlab4 import", None, None, ), ("zz_interlab4_obsid_assignment", "specifik_provplats", "TEXT", "1", "", "1", "", "The attribute Specifik Provplats from interlab4 file format.", None, None, ), ("zz_interlab4_obsid_assignment", "provplatsnamn", "TEXT", "1", "", "2", "", "The attribute Provplatsnamn from interlab4 file format.", None, None, ), ("zz_interlab4_obsid_assignment", "obsid", "TEXT", "1", "", "", "obs_points(obsid)", "Obsid linked to obs_points.obsid", None, None, ), ("zz_meteoparam", "*", "", "", "", "", "", "Data domain for meteorological parameters in meteo", None, None, ), ("zz_meteoparam", "parameter", "TEXT", "1", "", "1", "", "Allowed meteorological parameters", None, None, ), ("zz_meteoparam", "explanation", "TEXT", "", "", "", "", "Explanation of the parameters", None, None, ), ("zz_staff", "*", "", "", "", "", "", "Data domain for field staff used when importing data", None, None, ), ("zz_staff", "staff", "TEXT", "1", "", "1", "", "Initials of the field staff", None, None, ), ("zz_staff", "name", "TEXT", "", "", "", "", "Name of the field staff", None, None, ), ("zz_strat", "*", "", "", "", "", "", "Data domain for stratigraphy classes", None, None, ), ("zz_strat", "geoshort", "TEXT", "1", "", "1", "", "Abbreviation for the strata (stratigraphy class)", None, None, ), ("zz_strat", "strata", "TEXT", "1", "", "", "", "clay etc", None, None, ), ("zz_stratigraphy_plots", "*", "", "", "", "", "", "Data domain for stratigraphy plot colors and symbols used by the plugin", None, None, ), ("zz_stratigraphy_plots", "strata", "TEXT", "1", "", "1", "", "clay etc", None, None, ), ("zz_stratigraphy_plots", "color_mplot", "TEXT", "1", "", "", "", "Color codes for matplotlib plots", None, None, ), ("zz_stratigraphy_plots", "hatch_mplot", "TEXT", "1", "", "", "", "Hatch codes for matplotlib plots", None, None, ), ("zz_stratigraphy_plots", "color_qt", "TEXT", "1", "", "", "", "Color codes for Qt plots", None, None, ), ("zz_stratigraphy_plots", "brush_qt", "TEXT", "1", "", "", "", "Brush types for Qt plots", None, None, )], )'''

        result = db_utils.sql_load_fr_db("select tablename, columnname, data_type, not_null, default_value, primary_key, foreign_key, description, upd_date, upd_sign from about_db WHERE rowid != 1 and tablename not in %s"%db_utils.sqlite_internal_tables())
        test_string = common_utils.anything_to_string_representation(result)
        print(str(result))
        print(str(test_string))
        printnum = 40
        for charnr in range(len(test_string)):
            if test_string[charnr] != reference[charnr]:
                print('%s\n%s'%(test_string[charnr-printnum:charnr+printnum], reference[charnr-printnum:charnr+printnum]))
                break

        #print(test_string)
        assert test_string == reference

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('midvatten.tools.create_db.qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def test_about_db_creation_version_string(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_not_found, mock_iface, mock_messagebar):
        """
        Check that version string in about_db is written correctly
        """
        def side_effect(*args, **kwargs):
            mock_result = mock.MagicMock()
            if kwargs.get('combobox_label', None) == 'Locales':
                mock_result.answer = 'ok'
                mock_result.value = 'sv_SE'
            elif kwargs.get('combobox_label', None) == 'Timezone':
                mock_result.answer = 'ok'
                mock_result.value = ''
            return mock_result
        mock_not_found.side_effect = side_effect

        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')
        self.midvatten.new_db()

        result = db_utils.sql_load_fr_db("SELECT tablename, columnname, data_type, not_null, default_value, primary_key, foreign_key, description, upd_date, upd_sign FROM about_db LIMIT 1")

        print(str(mock_messagebar.mock_calls))
        #print(str(db_utils.sql_load_fr_db("SELECT * FROM geometry_columns")))
        test_string = common_utils.anything_to_string_representation(result)
        print(test_string)

        ref_strings = ['running QGIS version',
                        'on top of SpatiaLite version']
        for ref_string in ref_strings:
            assert ref_string in test_string


@attr(status='on')
class TestObsPointsTriggers(utils_for_tests.MidvattenTestSpatialiteDbSv):

    def setUp(self):
        super(TestObsPointsTriggers, self).setUp()
        db_utils.sql_alter_db("""DROP TRIGGER IF EXISTS after_insert_obs_points_geom_fr_coords""")
        db_utils.sql_alter_db("""DROP TRIGGER IF EXISTS after_update_obs_points_geom_fr_coords""")
        db_utils.sql_alter_db("""DROP TRIGGER IF EXISTS after_insert_obs_points_coords_fr_geom""")
        db_utils.sql_alter_db("""DROP TRIGGER IF EXISTS after_update_obs_points_coords_fr_geom""")


    def test_add_triggers_not_change_existing(self):
        """ Adding triggers should not automatically change the db """
        db_utils.sql_alter_db('''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 1.0, None)])'
        assert test_string == reference_string


    def test_add_triggers_add_east_north(self):
        """ Updating coordinates from NULL should create geometry. """
        db_utils.sql_alter_db('''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', NULL, NULL)''')

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        db_utils.sql_alter_db("""update obs_points set east='1.0', north='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 2.0, POINT(1 2))])'
        assert test_string == reference_string


    def test_add_triggers_not_deleting_geom_when_east_north_null(self):
        """ Adding triggers should not automatically delete geometry when east AND north is NULL """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: '(True, [(rb1, None, None, POINT(1 1))])

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, None, None, POINT(1 1))])'
        assert test_string == reference_string


    def test_add_triggers_not_deleting_geom_when_one_east_north_null(self):

        """ Adding triggers should not automatically delete geometry when east OR north is NULL """
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        db_utils.sql_alter_db("""update obs_points set east=X(geometry) where east is null and geometry is not null""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, None, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db("""update obs_points set east='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 2.0, None, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db("""update obs_points set east=NULL""")
        db_utils.sql_alter_db("""update obs_points set north='2.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, None, 2.0, POINT(1 1))])'
        assert test_string == reference_string

        db_utils.sql_alter_db("""update obs_points set east='3.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 3.0, 2.0, POINT(3 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db("""update obs_points set east='4.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 4.0, 2.0, POINT(4 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db("""update obs_points set east=NULL, north=NULL""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, None, None, POINT(4 2))])'
        assert test_string == reference_string

        db_utils.sql_alter_db("""update obs_points set east='5.0', north='6.0'""")
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 5.0, 6.0, POINT(5 6))])'
        assert test_string == reference_string


    def test_add_geometry_from_east_north(self):
        """ Test that adding triggers and adding obsid with east, north also adds geometry
        :return:
        """

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db('''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string


    def test_add_east_north_from_geometry(self):
        """ Test that adding triggers and adding obsid with geometry also adds east, north
        :return:
        """

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string


    def test_add_trigger_add_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and adding obsid don't set null values for previous obsid.
        :return:
        """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: '(True, [(rb1, None, None, POINT(1 1))])

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: '(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, None, None, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_add_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from geometry don't set null values for previous obsid.
        :return:
        """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")
        #After the first: '(True, [(rb1, None, None, POINT(1 1))])

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: '(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_add_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from east, north don't set null values for previous obsid.
        :return:
        """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north) VALUES ('rb2', 2, 2)""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_update_geometry_from_east_north(self):
        """ Test that adding triggers and updating obsid with east, north also updates geometry
        :return:
        """

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db('''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        db_utils.sql_alter_db('''UPDATE obs_points SET east = 2, north = 2 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_update_east_north_from_geometry(self):
        """ Test that adding triggers and updating obsid with geometry also updates east, north
        :return:
        """

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db('''UPDATE obs_points SET geometry = GeomFromText('POINT(2.0 2.0)', 3006) WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_add_trigger_update_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and updating obsid don't set null values for previous obsid.
        :return:
        """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: '(True, [(rb1, None, None, POINT(1 1))])

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db('''UPDATE obs_points SET geometry = GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: '(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, None, None, POINT(2 2))])'
        assert test_string == reference_string


    def test_update_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from geometry don't set null values for previous obsid.
        :return:
        """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: '(True, [(rb1, None, None, POINT(1 1))])

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db('''UPDATE obs_points SET geometry = GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: '(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_update_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """

        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, GeomFromText('POINT(2.0 2.0)', 3006))""")

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')

        db_utils.sql_alter_db('''UPDATE obs_points SET east = 3, north = 3 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string


    def test_add_trigger_add_obsid_without_anything(self):
        """
        :return:
        """

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid) VALUES ('rb1')""")
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid) VALUES ('rb2')""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, None, None, None), (rb2, None, None, None)])'
        assert test_string == reference_string


    def test_add_trigger_add_obsid_without_anything_not_changing_existing(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """

        midvatten_utils.add_triggers_to_obs_points('insert_obs_points_triggers.sql')
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid) VALUES ('rb2')""")
        db_utils.sql_alter_db("""INSERT INTO obs_points (obsid) VALUES ('rb3')""")

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = '(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, None, None, None), (rb3, None, None, None)])'
        assert test_string == reference_string


@attr(status='on')
class TestSqls(utils_for_tests.MidvattenTestSpatialiteDbSv):

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_import_null_as_double(self, mock_messagebar):
        """ Adding triggers should not automatically change the db """
        sql = '''INSERT INTO obs_points (obsid, length) VALUES ('rb1', CASE WHEN NULL IS NULL THEN %s END)'''%db_utils.cast_null('double precision')
        db_utils.sql_alter_db(sql)
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db('select obsid, length FROM obs_points'))
        reference_string = '(True, [(rb1, None)])'
        print(str(mock_messagebar.mock_calls))
        print(test_string)
        assert test_string == reference_string
