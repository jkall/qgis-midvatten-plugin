# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles exports to
  csv format.

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

import io
import os
import unittest

import db_utils
import midvatten_utils as utils
import mock
from midvatten import midvatten

import utils_for_tests
from mocks_for_tests import MockUsingReturnValue, MockQgsProjectInstance, MockReturnUsingDictIn, DummyInterface2

EXPORT_DB_PATH = '/tmp/tmp_midvatten_export_db.sqlite'
TEMP_DIR = '/tmp/'
from nose.plugins.attrib import attr


@attr(status='only')
class TestExport(utils_for_tests.MidvattenTestPostgisDbSv):
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    crs_question = MockUsingReturnValue([3006])
    mock_askuser = MockReturnUsingDictIn({'It is a strong': answer_no_obj, 'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_selection = MockReturnUsingDictIn({'obs_points': ('P1', ), 'obs_lines': ('L1', )}, 0)
    mock_no_selection = MockReturnUsingDictIn({'obs_points': tuple(), 'obs_lines': tuple()}, 0)
    exported_csv_files = [os.path.join(TEMP_DIR, filename) for filename in ['obs_points.csv', 'comments.csv', 'w_levels.csv', 'w_flow.csv', 'w_qual_lab.csv', 'w_qual_field.csv', 'stratigraphy.csv', 'meteo.csv', 'obs_lines.csv', 'seismic_data.csv', 'zz_flowtype.csv', 'zz_meteoparam.csv', 'zz_staff.csv', 'zz_strat.csv', 'zz_capacity.csv']]
    exported_csv_files_no_zz = [os.path.join(TEMP_DIR, filename) for filename in ['obs_points.csv', 'comments.csv', 'w_levels.csv', 'w_flow.csv', 'w_qual_lab.csv', 'w_qual_field.csv', 'stratigraphy.csv', 'meteo.csv', 'obs_lines.csv', 'seismic_data.csv']]

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getExistingDirectory')
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_export_csv(self, mock_iface, mock_savepath, mock_messagebar):
        mock_savepath.return_value = '/tmp/'
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'labpar1', 's1', '2015-01-01 01:00:00', 'unit1')''')

        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid) VALUES ('P1', 1)''')
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('L1')''')
        db_utils.sql_alter_db('''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''')
        db_utils.sql_alter_db('''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        self.midvatten.export_csv()

        file_contents = []
        for filename in TestExport.exported_csv_files_no_zz:
            with io.open(filename, 'r', encoding='utf-8') as f:
                file_contents.append(os.path.basename(filename) + '\n')
                if os.path.basename(filename) == 'obs_points.csv':
                    file_contents.append([';'.join(l.replace('\r', '').split(';')[:-1]) + '\n' for l in f])
                else:
                    file_contents.append([l.replace('\r', '') for l in f])
        test_string = utils_for_tests.create_test_string(file_contents)

        with io.open('/tmp/refstring.txt', 'w', encoding='utf-8') as of:
            of.write(test_string)

        reference_string = '\n'.join([
            "[obs_points.csv",
            ", [obsid;name;place;type;length;drillstop;diam;material;screen;capacity;drilldate;wmeas_yn;wlogg_yn;east;north;ne_accur;ne_source;h_toc;h_tocags;h_gs;h_accur;h_syst;h_source;source;com_onerow;com_html",
            ", P1;;;;;;;;;;;;;633466.0;711659.0;;;;;;;;;;;",
            "], comments.csv",
            ", [obsid;date_time;comment;staff",
            ", P1;2015-01-01 00:00:00;comment1;s1",
            "], w_levels.csv",
            ", [obsid;date_time;meas;h_toc;level_masl;comment",
            ", P1;2015-01-02 00:00:01;2.0;;;",
            "], w_flow.csv",
            ", [obsid;instrumentid;flowtype;date_time;reading;unit;comment",
            ", P1;inst1;Momflow;2015-04-13 00:00:00;;l/s;",
            "], w_qual_lab.csv",
            ", [obsid;depth;report;project;staff;date_time;anameth;parameter;reading_num;reading_txt;unit;comment",
            ", P1;;report1;;s1;;;labpar1;;;;",
            "], w_qual_field.csv",
            ", [obsid;staff;date_time;instrument;parameter;reading_num;reading_txt;unit;depth;comment",
            ", P1;s1;2015-01-01 01:00:00;;labpar1;;;unit1;;",
            "], stratigraphy.csv",
            ", [obsid;stratid;depthtop;depthbot;geology;geoshort;capacity;development;comment",
            ", P1;1;;;;;;;",
            "], meteo.csv",
            ", [obsid;instrumentid;parameter;date_time;reading_num;reading_txt;unit;comment",
            ", P1;meteoinst;precip;2017-01-01 00:19:00;;;;",
            "], obs_lines.csv",
            ", [obsid;name;place;type;source;geometry",
            ", L1;;;;;",
            "], seismic_data.csv",
            ", [obsid;length;ground;bedrock;gw_table;comment",
            ", L1;5.0;;;;",
            "]]"])

        assert test_string == reference_string

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.get_selected_features_as_tuple', mock_no_selection.get_v)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getExistingDirectory')
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('db_utils.get_postgis_connections', utils_for_tests.MidvattenTestPostgisNotCreated.mock_postgis_connections)
    def test_export_csv_no_selection(self, mock_iface, mock_savepath, mock_messagebar):
        mock_savepath.return_value = '/tmp/'
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'labpar1', 's1', '2015-01-01 01:00:00', 'unit1')''')

        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid) VALUES ('P1', 1)''')
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('L1')''')
        db_utils.sql_alter_db('''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''')
        db_utils.sql_alter_db('''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        self.midvatten.export_csv()

        file_contents = []
        for filename in TestExport.exported_csv_files_no_zz:
            with io.open(filename, 'r', encoding='utf-8') as f:
                file_contents.append(os.path.basename(filename) + '\n')
                if os.path.basename(filename) == 'obs_points.csv':
                    file_contents.append([';'.join(l.replace('\r', '').split(';')[:-1]) + '\n' for l in f])
                else:
                    file_contents.append([l.replace('\r', '') for l in f])
        test_string = utils_for_tests.create_test_string(file_contents)

        with io.open('/tmp/refstring.txt', 'w', encoding='utf-8') as of:
            of.write(test_string)

        reference_string = '\n'.join([
            "[obs_points.csv",
            ", [obsid;name;place;type;length;drillstop;diam;material;screen;capacity;drilldate;wmeas_yn;wlogg_yn;east;north;ne_accur;ne_source;h_toc;h_tocags;h_gs;h_accur;h_syst;h_source;source;com_onerow;com_html",
            ", P1;;;;;;;;;;;;;633466.0;711659.0;;;;;;;;;;;",
            "], comments.csv",
            ", [obsid;date_time;comment;staff",
            ", P1;2015-01-01 00:00:00;comment1;s1",
            "], w_levels.csv",
            ", [obsid;date_time;meas;h_toc;level_masl;comment",
            ", P1;2015-01-02 00:00:01;2.0;;;",
            "], w_flow.csv",
            ", [obsid;instrumentid;flowtype;date_time;reading;unit;comment",
            ", P1;inst1;Momflow;2015-04-13 00:00:00;;l/s;",
            "], w_qual_lab.csv",
            ", [obsid;depth;report;project;staff;date_time;anameth;parameter;reading_num;reading_txt;unit;comment",
            ", P1;;report1;;s1;;;labpar1;;;;",
            "], w_qual_field.csv",
            ", [obsid;staff;date_time;instrument;parameter;reading_num;reading_txt;unit;depth;comment",
            ", P1;s1;2015-01-01 01:00:00;;labpar1;;;unit1;;",
            "], stratigraphy.csv",
            ", [obsid;stratid;depthtop;depthbot;geology;geoshort;capacity;development;comment",
            ", P1;1;;;;;;;",
            "], meteo.csv",
            ", [obsid;instrumentid;parameter;date_time;reading_num;reading_txt;unit;comment",
            ", P1;meteoinst;precip;2017-01-01 00:19:00;;;;",
            "], obs_lines.csv",
            ", [obsid;name;place;type;source;geometry",
            ", L1;;;;;",
            "], seismic_data.csv",
            ", [obsid;length;ground;bedrock;gw_table;comment",
            ", L1;5.0;;;;",
            "]]"])

        assert test_string == reference_string

    def tearDown(self):
        #Delete database
        try:
            os.remove(EXPORT_DB_PATH)
        except OSError:
            pass

        for filename in TestExport.exported_csv_files:
            try:
                os.remove(filename)
            except OSError:
                pass

        super(self.__class__, self).tearDown()


