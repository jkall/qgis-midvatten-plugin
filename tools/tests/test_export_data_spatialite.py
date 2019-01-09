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

import io
import os
from pyspatialite import dbapi2 as sqlite

import db_utils
import mock

import utils_for_tests
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDictIn


EXPORT_DB_PATH = u'/tmp/tmp_midvatten_export_db.sqlite'
TEMP_DIR = u'/tmp/'
from nose.plugins.attrib import attr


@attr(status='on')
class TestExport(utils_for_tests.MidvattenTestSpatialiteDbEn):
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    crs_question = MockUsingReturnValue([3006])
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_selection = MockReturnUsingDictIn({u'obs_points': (u'P1', ), u'obs_lines': (u'L1', )}, 0)
    exported_csv_files = [os.path.join(TEMP_DIR, filename) for filename in ['obs_points.csv', 'comments.csv', 'w_levels.csv', 'w_flow.csv', 'w_qual_lab.csv', 'w_qual_field.csv', 'stratigraphy.csv', 'meteo.csv', 'obs_lines.csv', 'seismic_data.csv', 'zz_flowtype.csv', 'zz_meteoparam.csv', 'zz_staff.csv', 'zz_strat.csv', 'zz_capacity.csv']]
    exported_csv_files_no_zz = [os.path.join(TEMP_DIR, filename) for filename in ['obs_points.csv', 'comments.csv', 'w_levels.csv', 'w_flow.csv', 'w_qual_lab.csv', 'w_qual_field.csv', 'stratigraphy.csv', 'meteo.csv', 'obs_lines.csv', 'seismic_data.csv']]

    @mock.patch('midvatten_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('PyQt4.QtGui.QFileDialog.getExistingDirectory')
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_export_csv(self, mock_iface, mock_savepath):
        mock_savepath.return_value = u'/tmp/'
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db(u'''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'labpar1', 's1', '2015-01-01 01:00:00', 'unit1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db(u'''INSERT INTO stratigraphy (obsid, stratid) VALUES ('P1', 1)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid) VALUES ('L1')''')
        db_utils.sql_alter_db(u'''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''')
        db_utils.sql_alter_db(u'''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        self.midvatten.export_csv()
        file_contents = []
        for filename in TestExport.exported_csv_files_no_zz:
            with io.open(filename, 'r', encoding='utf-8') as f:
                file_contents.append(os.path.basename(filename) + '\n')
                if os.path.basename(filename) == u'obs_points.csv':
                    file_contents.append([u';'.join(l.replace('\r', '').split(u';')[:-1]) + u'\n' for l in f])
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

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QtGui.QInputDialog.getText')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('export_data.utils.pop_up_info', autospec=True)
    def test_export_spatialite(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = u'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]
        dbconnection = db_utils.DbConnectionManager()
        mock_newdbpath.return_value = EXPORT_DB_PATH
        mock_verify.return_value = 0

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('s1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO stratigraphy (obsid, stratid) VALUES ('P1', 1)''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid) VALUES ('L1')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''', dbconnection=dbconnection)
        db_utils.sql_alter_db(u'''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''', dbconnection=dbconnection)

        dbconnection.commit_and_closedb()

        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = [u'''select obsid, ST_AsText(geometry) from obs_points''',
                    u'''select staff from zz_staff''',
                    u'''select obsid, date_time, staff, comment from comments''',
                    u'''select obsid, parameter, report, staff from w_qual_lab''',
                    u'''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                    u'''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                    u'''select obsid, date_time, meas from w_levels''',
                    u'''select obsid, stratid from stratigraphy''',
                    u'''select obsid from obs_lines''',
                    u'''select obsid, length from seismic_data''',
                    u'''select obsid, instrumentid, parameter, date_time from meteo''']


        conn = sqlite.connect(EXPORT_DB_PATH, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = [u'''[''',
                            u'''select obsid, ST_AsText(geometry) from obs_points''',
                            u''', [(P1, POINT(633466 711659))], ''',
                            u'''select staff from zz_staff''',
                            u''', [(s1)], ''',
                            u'''select obsid, date_time, staff, comment from comments''',
                            u''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            u'''select obsid, parameter, report, staff from w_qual_lab''',
                            u''', [(P1, labpar1, report1, s1)], ''',
                            u'''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            u''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            u'''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            u''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            u'''select obsid, date_time, meas from w_levels''',
                            u''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            u'''select obsid, stratid from stratigraphy''',
                            u''', [(P1, 1)], ''',
                            u'''select obsid from obs_lines''',
                            u''', [(L1)], ''',
                            u'''select obsid, length from seismic_data''',
                            u''', [(L1, 5.0)], ''',
                            u'''select obsid, instrumentid, parameter, date_time from meteo''',
                            u''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']
        reference_string = u'\n'.join(reference_string)
        assert test_string == reference_string

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QtGui.QInputDialog.getText')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.get_selected_features_as_tuple')
    @mock.patch('midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('export_data.utils.pop_up_info', autospec=True)
    def test_export_spatialite_with_umlauts(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_selection, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_selection.return_value = (u'åäö', )
        mock_find_layer.return_value.crs.return_value.authid.return_value = u'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]

        mock_newdbpath.return_value = EXPORT_DB_PATH
        mock_verify.return_value = 0

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ("åäö", ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db(u'''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('åäö', '2015-01-01 00:00:00', 's1', 'comment1')''')

        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = [u'''select obsid, ST_AsText(geometry) from obs_points''',
                    u'''select staff from zz_staff''',
                    u'''select obsid, date_time, staff, comment from comments''']

        conn = sqlite.connect(EXPORT_DB_PATH, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = [u'''[''',
                            u'''select obsid, ST_AsText(geometry) from obs_points''',
                            u''', [(åäö, POINT(633466 711659))], ''',
                            u'''select staff from zz_staff''',
                            u''', [(s1)], ''',
                            u'''select obsid, date_time, staff, comment from comments''',
                            u''', [(åäö, 2015-01-01 00:00:00, s1, comment1)]]''']
        reference_string = u'\n'.join(reference_string)
        assert test_string == reference_string

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QtGui.QInputDialog.getText')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('export_data.utils.pop_up_info', autospec=True)
    def test_export_spatialite_transform_coordinates(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = u'EPSG:3006'
        mock_createdb_crs_question.return_value = [3010, True]

        mock_newdbpath.return_value = EXPORT_DB_PATH
        mock_verify.return_value = 0

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(1 1)', 3006))''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('s1')''')
        db_utils.sql_alter_db(u'''INSERT INTO comments (obsid, date_time, staff, comment) VALUES ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_qual_lab (obsid, parameter, report, staff) VALUES ('P1', 'labpar1', 'report1', 's1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_qual_field (obsid, parameter, staff, date_time, unit) VALUES ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_flow (obsid, instrumentid, flowtype, date_time, unit) VALUES ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels (obsid, date_time, meas) VALUES ('P1', '2015-01-02 00:00:01', '2')''')
        db_utils.sql_alter_db(u'''INSERT INTO stratigraphy (obsid, stratid) VALUES ('P1', 1)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_lines (obsid) VALUES ('L1')''')
        db_utils.sql_alter_db(u'''INSERT INTO seismic_data (obsid, length) VALUES ('L1', '5')''')
        db_utils.sql_alter_db(u'''INSERT INTO meteo (obsid, instrumentid, parameter, date_time) VALUES ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.export_spatialite()

        sql_list = [u'''select obsid, ST_AsText(geometry) from obs_points''',
                    u'''select staff from zz_staff''',
                    u'''select obsid, date_time, staff, comment from comments''',
                    u'''select obsid, parameter, report, staff from w_qual_lab''',
                    u'''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                    u'''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                    u'''select obsid, date_time, meas from w_levels''',
                    u'''select obsid, stratid from stratigraphy''',
                    u'''select obsid from obs_lines''',
                    u'''select obsid, length from seismic_data''',
                    u'''select obsid, instrumentid, parameter, date_time from meteo''']

        conn = sqlite.connect(EXPORT_DB_PATH, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)
        reference_string = [u'''[''',
                            u'''select obsid, ST_AsText(geometry) from obs_points''',
                            u''', [(P1, POINT(-517888.383737 1.002821))], ''',
                            u'''select staff from zz_staff''',
                            u''', [(s1)], ''',
                            u'''select obsid, date_time, staff, comment from comments''',
                            u''', [(P1, 2015-01-01 00:00:00, s1, comment1)], ''',
                            u'''select obsid, parameter, report, staff from w_qual_lab''',
                            u''', [(P1, labpar1, report1, s1)], ''',
                            u'''select obsid, parameter, staff, date_time, comment from w_qual_field''',
                            u''', [(P1, par1, s1, 2015-01-01 01:00:00, None)], ''',
                            u'''select obsid, instrumentid, flowtype, date_time, unit from w_flow''',
                            u''', [(P1, inst1, Momflow, 2015-04-13 00:00:00, l/s)], ''',
                            u'''select obsid, date_time, meas from w_levels''',
                            u''', [(P1, 2015-01-02 00:00:01, 2.0)], ''',
                            u'''select obsid, stratid from stratigraphy''',
                            u''', [(P1, 1)], ''',
                            u'''select obsid from obs_lines''',
                            u''', [(L1)], ''',
                            u'''select obsid, length from seismic_data''',
                            u''', [(L1, 5.0)], ''',
                            u'''select obsid, instrumentid, parameter, date_time from meteo''',
                            u''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']
        reference_string = u'\n'.join(reference_string)
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QtGui.QInputDialog.getText')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten_utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.find_layer', autospec=True)
    @mock.patch('qgis.utils.iface', autospec=True)
    @mock.patch('export_data.utils.pop_up_info', autospec=True)
    def test_export_spatialite_zz_tables(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify, mock_locale, mock_createdb_crs_question, mock_messagebar):
        mock_find_layer.return_value.crs.return_value.authid.return_value = u'EPSG:3006'
        mock_createdb_crs_question.return_value = [3006, True]
        dbconnection = db_utils.DbConnectionManager()
        mock_newdbpath.return_value = EXPORT_DB_PATH
        mock_verify.return_value = 0

        """
        insert into zz_strat(geoshort,strata) values('land fill','fyll');
        insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('torv','DarkGray','+','darkGray','NoBrush');
        insert into zz_capacity (capacity,explanation) values('6 ','mycket god');
        insert into zz_capacity (capacity,explanation) values('6+','mycket god');
        insert into zz_capacity_plots (capacity,color_qt) values('', 'gray');
        """

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, geometry) VALUES ('P1', ST_GeomFromText('POINT(633466 711659)', 3006))''', dbconnection=dbconnection)
        dbconnection.execute(u'''PRAGMA foreign_keys='off' ''')
        dbconnection.execute(u'''UPDATE zz_strat SET strata = 'filling' WHERE geoshort = 'land fill' ''')
        dbconnection.execute(u'''INSERT INTO zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values ('filling','Yellow','+','darkGray','NoBrush') ''')
        dbconnection.execute(u'''UPDATE zz_stratigraphy_plots SET color_mplot = 'OrangeFIX' WHERE strata = 'made ground' ''')
        dbconnection.execute(u'''UPDATE zz_capacity SET explanation = 'anexpl' WHERE capacity = 0 ''')
        dbconnection.execute(u'''UPDATE zz_capacity_plots SET color_qt = 'whiteFIX' WHERE capacity = 0 ''')

        dbconnection.commit_and_closedb()

        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'en_US'
        self.midvatten.export_spatialite()

        sql_list = [u'''SELECT geoshort, strata FROM zz_strat WHERE geoshort IN ('land fill', 'rock') ''',
                    u'''SELECT strata, color_mplot FROM zz_stratigraphy_plots WHERE strata IN ('made ground', 'rock', 'filling') ''',
                    u'''SELECT capacity, explanation FROM zz_capacity WHERE capacity IN (0, 1)''',
                    u'''SELECT capacity, color_qt FROM zz_capacity_plots WHERE capacity IN (0, 1) ''']

        conn = sqlite.connect(EXPORT_DB_PATH, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()

        test_list = []
        for sql in sql_list:
            test_list.append('\n' + sql + '\n')
            test_list.append(curs.execute(sql).fetchall())

        conn.commit()
        conn.close()

        test_string = utils_for_tests.create_test_string(test_list)


        reference_string = [u'''[''',
                            u'''SELECT geoshort, strata FROM zz_strat WHERE geoshort IN ('land fill', 'rock') ''',
                            u''', [(land fill, filling), (rock, rock)], ''',
                            u'''SELECT strata, color_mplot FROM zz_stratigraphy_plots WHERE strata IN ('made ground', 'rock', 'filling') ''',
                            u''', [(filling, Yellow), (made ground, OrangeFIX), (rock, red)], ''',
                            u'''SELECT capacity, explanation FROM zz_capacity WHERE capacity IN (0, 1)''',
                            u''', [(0, anexpl), (1, above gwl)], ''',
                            u'''SELECT capacity, color_qt FROM zz_capacity_plots WHERE capacity IN (0, 1) ''',
                            u''', [(0, whiteFIX), (1, red)]]''']

        reference_string = u'\n'.join(reference_string)
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


