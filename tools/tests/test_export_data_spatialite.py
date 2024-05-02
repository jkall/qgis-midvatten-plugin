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

import mock

from midvatten.tools.utils import db_utils, common_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.tests.mocks_for_tests import MockUsingReturnValue, MockReturnUsingDictIn
from midvatten.definitions import db_defs

EXPORT_DB_PATH = '/tmp/tmp_midvatten_export_db.sqlite'
TEMP_DIR = '/tmp/'
from nose.plugins.attrib import attr


@attr(status='on')
class TestExport(utils_for_tests.MidvattenTestSpatialiteDbEn):
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

    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getExistingDirectory')
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_export_csv(self, mock_iface, mock_savepath):
        mock_savepath.return_value = '/tmp/'
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'labpar1', 's1', '2015-01-01 01:00:00', 'unit1')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot) VALUES ('P1', 1, 0, 10)''')
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
            ", [obsid;date_time;comment;staff;type",
            ", P1;2015-01-01 00:00:00;comment1;s1;",
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
            ", P1;1;0.0;10.0;;;;;",
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
        print(test_string)
        print(reference_string)
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_no_selection.get_v)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getExistingDirectory')
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_export_csv_no_selection(self, mock_iface, mock_savepath):
        mock_savepath.return_value = '/tmp/'
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(1 2)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'labpar1', 's1', '2015-01-01 01:00:00', 'unit1')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot) VALUES ('P1', 1, 0, 10)''')
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
            ", P2;;;;;;;;;;;;;1.0;2.0;;;;;;;;;;;",
            "], comments.csv",
            ", [obsid;date_time;comment;staff;type",
            ", P1;2015-01-01 00:00:00;comment1;s1;",
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
            ", P1;1;0.0;10.0;;;;;",
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
        print(test_string)
        print(reference_string)
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.utils.midvatten_utils.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten.tools.utils.midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.tools.utils.midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.export_data.common_utils.pop_up_info', autospec=True)
    def test_export_spatialite(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = 'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]
        dbconnection = db_utils.DbConnectionManager()
        mock_newdbpath.return_value = (EXPORT_DB_PATH, '')
        mock_verify.return_value = 0

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot) VALUES ('P1', 1, 0, 10)''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('L1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''', dbconnection=dbconnection)

        dbconnection.commit_and_closedb()

        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = ['''select obsid, ST_AsText(geometry) from obs_points''',
                    '''select staff from zz_staff''',
                    '''select obsid, date_time, staff, comment from comments''',
                    '''select obsid, parameter, report, staff from w_qual_lab''',
                    '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                    '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                    '''select obsid, date_time, meas from w_levels''',
                    '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                    '''select obsid from obs_lines''',
                    '''select obsid, length from seismic_data''',
                    '''select obsid, instrumentid, parameter, date_time from meteo''']


        conn = db_utils.connect_with_spatialite_connect(EXPORT_DB_PATH)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = ['''[''',
                            '''select obsid, ST_AsText(geometry) from obs_points''',
                            ''', [(P1, POINT(633466 711659))], ''',
                            '''select staff from zz_staff''',
                            ''', [(s1)], ''',
                            '''select obsid, date_time, staff, comment from comments''',
                            ''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            '''select obsid, parameter, report, staff from w_qual_lab''',
                            ''', [(P1, labpar1, report1, s1)], ''',
                            '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            ''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            ''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            '''select obsid, date_time, meas from w_levels''',
                            ''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                            ''', [(P1, 1, 0.0, 10.0)], ''',
                            '''select obsid from obs_lines''',
                            ''', [(L1)], ''',
                            '''select obsid, length from seismic_data''',
                            ''', [(L1, 5.0)], ''',
                            '''select obsid, instrumentid, parameter, date_time from meteo''',
                            ''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']
        reference_string = '\n'.join(reference_string)
        print("Ref:")
        print(str(reference_string))
        print("Test:")
        print(str(test_string))
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.utils.midvatten_utils.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_no_selection.get_v)
    @mock.patch('midvatten.tools.utils.midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.tools.utils.midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.export_data.common_utils.pop_up_info', autospec=True)
    def test_export_spatialite_no_selected(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = 'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]
        dbconnection = db_utils.DbConnectionManager()
        mock_newdbpath.return_value = (EXPORT_DB_PATH, '')
        mock_verify.return_value = 0

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P2', ST_GeomFromText('POINT(1 2)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot) VALUES ('P1', 1, 0, 10)''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('L1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''', dbconnection=dbconnection)

        dbconnection.commit_and_closedb()

        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = ['''select obsid, ST_AsText(geometry) from obs_points''',
                    '''select staff from zz_staff''',
                    '''select obsid, date_time, staff, comment from comments''',
                    '''select obsid, parameter, report, staff from w_qual_lab''',
                    '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                    '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                    '''select obsid, date_time, meas from w_levels''',
                    '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                    '''select obsid from obs_lines''',
                    '''select obsid, length from seismic_data''',
                    '''select obsid, instrumentid, parameter, date_time from meteo''']


        conn = db_utils.connect_with_spatialite_connect(EXPORT_DB_PATH)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = ['''[''',
                            '''select obsid, ST_AsText(geometry) from obs_points''',
                            ''', [(P1, POINT(633466 711659)), (P2, POINT(1 2))], ''',
                            '''select staff from zz_staff''',
                            ''', [(s1)], ''',
                            '''select obsid, date_time, staff, comment from comments''',
                            ''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            '''select obsid, parameter, report, staff from w_qual_lab''',
                            ''', [(P1, labpar1, report1, s1)], ''',
                            '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            ''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            ''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            '''select obsid, date_time, meas from w_levels''',
                            ''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                            ''', [(P1, 1, 0.0, 10.0)], ''',
                            '''select obsid from obs_lines''',
                            ''', [(L1)], ''',
                            '''select obsid, length from seismic_data''',
                            ''', [(L1, 5.0)], ''',
                            '''select obsid, instrumentid, parameter, date_time from meteo''',
                            ''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']
        reference_string = '\n'.join(reference_string)
        print(test_string)
        print(str(mock_messagebar.mock_calls))
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.utils.midvatten_utils.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple')
    @mock.patch('midvatten.tools.utils.midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.tools.utils.midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.export_data.common_utils.pop_up_info', autospec=True)
    def test_export_spatialite_with_umlauts(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_selection, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_selection.return_value = ('åäö', )
        mock_find_layer.return_value.crs.return_value.authid.return_value = 'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]

        mock_newdbpath.return_value = (EXPORT_DB_PATH, '')
        mock_verify.return_value = 0

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('åäö', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('åäö', '2015-01-01 00:00:00', 's1', 'comment1')''')

        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = ['''select obsid, ST_AsText(geometry) from obs_points''',
                    '''select staff from zz_staff''',
                    '''select obsid, date_time, staff, comment from comments''']

        conn = db_utils.connect_with_spatialite_connect(EXPORT_DB_PATH)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = ['''[''',
                            '''select obsid, ST_AsText(geometry) from obs_points''',
                            ''', [(åäö, POINT(633466 711659))], ''',
                            '''select staff from zz_staff''',
                            ''', [(s1)], ''',
                            '''select obsid, date_time, staff, comment from comments''',
                            ''', [(åäö, 2015-01-01 00:00:00, s1, comment1)]]''']
        reference_string = '\n'.join(reference_string)

        print("Ref")
        print(reference_string)
        print("Test")
        print(test_string)
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.utils.midvatten_utils.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten.tools.utils.midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.tools.utils.midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.export_data.common_utils.pop_up_info', autospec=True)
    def test_export_spatialite_transform_coordinates(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = 'EPSG:3006'
        mock_createdb_crs_question.return_value = ['3010', True]

        mock_newdbpath.return_value = (EXPORT_DB_PATH, '')
        mock_verify.return_value = 0

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(1 1)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''')
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot) VALUES ('P1', 1, 0, 10)''')
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('L1')''')
        db_utils.sql_alter_db('''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''')
        db_utils.sql_alter_db('''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = ['''select obsid, ST_AsText(geometry) from obs_points''',
                    '''select staff from zz_staff''',
                    '''select obsid, date_time, staff, comment from comments''',
                    '''select obsid, parameter, report, staff from w_qual_lab''',
                    '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                    '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                    '''select obsid, date_time, meas from w_levels''',
                    '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                    '''select obsid from obs_lines''',
                    '''select obsid, length from seismic_data''',
                    '''select obsid, instrumentid, parameter, date_time from meteo''']

        conn = db_utils.connect_with_spatialite_connect(EXPORT_DB_PATH)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        """
        # The coordinates aquired from st_transform differs from Linux Mint 18.2 to Linux Mint 19
        # In Mint 18, it's -517888.383773 for both postgis and spatialite
        # In Mint 19, it's -517888.383737 for both postgis and spatialite
        # In Ubuntu 20.04 it's -517888.384559 for both postgis and spatialite
        #// I've made changes to the transformation so the above values no longer exists, but the previous issue probably does.
        # !!! No idea why
        # In Ubuntu 22.10, (1, 1) in 3006 turns into 'POINT(10.511265 0.000009)' in WGS84 and into POINT(-517888.39291 1.000667) in 3010!
        # The problem must be rounding related. 
        
        reference_string = ['''[''',
                            '''select obsid, ST_AsText(geometry) from obs_points''',
                            ''', [(P1, POINT(-517888.392089 1.000667))], ''',
                            '''select staff from zz_staff''',
                            ''', [(s1)], ''',
                            '''select obsid, date_time, staff, comment from comments''',
                            ''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            '''select obsid, parameter, report, staff from w_qual_lab''',
                            ''', [(P1, labpar1, report1, s1)], ''',
                            '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            ''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            ''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            '''select obsid, date_time, meas from w_levels''',
                            ''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                            ''', [(P1, 1, 0.0, 10.0)], ''',
                            '''select obsid from obs_lines''',
                            ''', [(L1)], ''',
                            '''select obsid, length from seismic_data''',
                            ''', [(L1, 5.0)], ''',
                            '''select obsid, instrumentid, parameter, date_time from meteo''',
                            ''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']
        """
        reference_string = ['''[''',
                            '''select obsid, ST_AsText(geometry) from obs_points''',
                            ''', [(P1, POINT(-517888.384559 1.002821))], ''',
                            '''select staff from zz_staff''',
                            ''', [(s1)], ''',
                            '''select obsid, date_time, staff, comment from comments''',
                            ''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            '''select obsid, parameter, report, staff from w_qual_lab''',
                            ''', [(P1, labpar1, report1, s1)], ''',
                            '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            ''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            ''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            '''select obsid, date_time, meas from w_levels''',
                            ''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                            ''', [(P1, 1, 0.0, 10.0)], ''',
                            '''select obsid from obs_lines''',
                            ''', [(L1)], ''',
                            '''select obsid, length from seismic_data''',
                            ''', [(L1, 5.0)], ''',
                            '''select obsid, instrumentid, parameter, date_time from meteo''',
                            ''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']

        reference_string = '\n'.join(reference_string)
        print("Test\n" + test_string)
        print("Ref\n" + reference_string)
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.utils.midvatten_utils.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten.tools.utils.midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.tools.utils.midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.export_data.common_utils.pop_up_info', autospec=True)
    def test_export_spatialite_zz_tables(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = 'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]
        dbconnection = db_utils.DbConnectionManager()
        mock_newdbpath.return_value = (EXPORT_DB_PATH, '')
        mock_verify.return_value = 0

        """
        insert into zz_strat(geoshort,strata) values('land fill','fyll');
        insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('torv','DarkGray','+','darkGray','NoBrush');
        insert into zz_capacity (capacity,explanation) values('6 ','mycket god');
        insert into zz_capacity (capacity,explanation) values('6+','mycket god');
        insert into zz_capacity_plots (capacity,color_qt) values('', 'gray');
        """

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''', dbconnection=dbconnection)
        dbconnection.execute('''PRAGMA foreign_keys='off'  ''')
        dbconnection.execute('''UPDATE zz_strat SET strata = 'filling' WHERE geoshort = 'land fill' ''')
        dbconnection.execute('''INSERT INTO zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values ('filling','Yellow','+','darkGray','NoBrush') ''')
        dbconnection.execute('''UPDATE zz_stratigraphy_plots SET color_mplot = 'OrangeFIX' WHERE strata = 'made ground' ''')
        dbconnection.execute('''UPDATE zz_capacity SET explanation = 'anexpl' WHERE capacity = '0' ''')
        dbconnection.execute('''UPDATE zz_capacity_plots SET color_qt = 'whiteFIX' WHERE capacity = '0' ''')
        #print(str(dbconnection.execute_and_fetchall('select * from zz_strat')))
        #dbconnection.commit_and_closedb()
        dbconnection.commit()
        sql_list = ['''SELECT geoshort, strata FROM zz_strat WHERE geoshort IN ('land fill', 'rock') ''',
                    '''SELECT strata, color_mplot FROM zz_stratigraphy_plots WHERE strata IN ('made ground', 'rock', 'filling') ''',
                    '''SELECT capacity, explanation FROM zz_capacity WHERE capacity IN ('0', '1')''',
                    '''SELECT capacity, color_qt FROM zz_capacity_plots WHERE capacity IN ('0', '1') ''']


        print("Before export")
        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(dbconnection.cursor.execute(sql).fetchall())

        dbconnection.closedb()
        print("After")

        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'en_US'

        self.midvatten.export_spatialite()


        conn = db_utils.connect_with_spatialite_connect(EXPORT_DB_PATH)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)


        reference_string = ['''[''',
                            '''SELECT geoshort, strata FROM zz_strat WHERE geoshort IN ('land fill', 'rock') ''',
                            ''', [(land fill, filling), (rock, rock)], ''',
                            '''SELECT strata, color_mplot FROM zz_stratigraphy_plots WHERE strata IN ('made ground', 'rock', 'filling') ''',
                            ''', [(filling, Yellow), (made ground, OrangeFIX), (rock, red)], ''',
                            '''SELECT capacity, explanation FROM zz_capacity WHERE capacity IN ('0', '1')''',
                            ''', [(0, anexpl), (1, above gwl)], ''',
                            '''SELECT capacity, color_qt FROM zz_capacity_plots WHERE capacity IN ('0', '1') ''',
                            ''', [(0, whiteFIX), (1, red)]]''']

        reference_string = '\n'.join(reference_string)
        print(str(test_string))
        print(str(reference_string))
        assert test_string == reference_string

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.utils.midvatten_utils.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.create_db.common_utils.NotFoundQuestion')
    @mock.patch('midvatten.tools.utils.common_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten.tools.utils.common_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten.tools.utils.midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.tools.utils.midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten.tools.export_data.common_utils.pop_up_info', autospec=True)
    def test_export_spatialite_extra_tables(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = 'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]
        dbconnection = db_utils.DbConnectionManager()
        mock_newdbpath.return_value = (EXPORT_DB_PATH, '')
        mock_verify.return_value = 0

        db_utils.execute_sqlfile(db_defs.extra_datatables_sqlfile(), dbconnection, merge_newlines=True)

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO zz_staff (staff) VALUES ('s1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot) VALUES ('P1', 1, 0, 10)''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO obs_lines (obsid) VALUES ('L1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO s_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar2', 'report2', 's1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db('''INSERT INTO w_qual_logger (obsid, date_time, instrument, parameter, unit) VALUES ('P1', '2021-08-11 11:14', 'testinst', 'testpar', 'm')''',
            dbconnection=dbconnection)

        dbconnection.commit_and_closedb()

        print(str(db_utils.sql_load_fr_db('''select * From s_qual_lab''')))

        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = ['''select obsid, ST_AsText(geometry) from obs_points''',
                    '''select staff from zz_staff''',
                    '''select obsid, date_time, staff, comment from comments''',
                    '''select obsid, parameter, report, staff from w_qual_lab''',
                    '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                    '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                    '''select obsid, date_time, meas from w_levels''',
                    '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                    '''select obsid from obs_lines''',
                    '''select obsid, length from seismic_data''',
                    '''select obsid, instrumentid, parameter, date_time from meteo''',
                    '''select obsid, parameter, report, staff from s_qual_lab''',
                    '''select obsid, date_time, instrument, parameter, unit from w_qual_logger''']


        conn = db_utils.connect_with_spatialite_connect(EXPORT_DB_PATH)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = ['''[''',
                            '''select obsid, ST_AsText(geometry) from obs_points''',
                            ''', [(P1, POINT(633466 711659))], ''',
                            '''select staff from zz_staff''',
                            ''', [(s1)], ''',
                            '''select obsid, date_time, staff, comment from comments''',
                            ''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            '''select obsid, parameter, report, staff from w_qual_lab''',
                            ''', [(P1, labpar1, report1, s1)], ''',
                            '''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            ''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            '''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            ''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            '''select obsid, date_time, meas from w_levels''',
                            ''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            '''select obsid, stratid, depthtop, depthbot from stratigraphy''',
                            ''', [(P1, 1, 0.0, 10.0)], ''',
                            '''select obsid from obs_lines''',
                            ''', [(L1)], ''',
                            '''select obsid, length from seismic_data''',
                            ''', [(L1, 5.0)], ''',
                            '''select obsid, instrumentid, parameter, date_time from meteo''',
                            ''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)], ''',
                            '''select obsid, parameter, report, staff from s_qual_lab''',
                            ''', [(P1, labpar2, report2, s1)], ''',
                            '''select obsid, date_time, instrument, parameter, unit from w_qual_logger''',
                            ''', [(P1, 2021-08-11 11:14, testinst, testpar, m)]]'''
                            ]
        reference_string = '\n'.join(reference_string)
        print("Ref:")
        print(str(reference_string))
        print("Test:")
        print(str(test_string))
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


