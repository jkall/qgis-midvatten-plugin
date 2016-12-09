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
from qgis.core import QgsApplication, QgsProviderRegistry, QgsProject
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from PyQt4 import QtCore, QtGui, QtTest
from mocks_for_tests import MockUsingReturnValue, MockQgsProjectInstance, MockReturnUsingDictIn, DummyInterface2
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
import midvatten
import os
import utils_for_tests
import unittest
import sqlite3 as sqlite
import io
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsVectorLayer
from export_data import ExportData

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
EXPORT_DB_PATH = u'/tmp/tmp_midvatten_export_db.sqlite'
MOCK_EXPORT_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([EXPORT_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)
TEMP_DIR = u'/tmp/'

class _TestExport(unittest.TestCase):
    """
    """
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


    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH
        mock_qgsproject_instance.return_value.instance.readEntry.return_value = [u'en_US']

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten.midvatten(self.iface)
        for dbs in [TEMP_DB_PATH, EXPORT_DB_PATH]:
            try:
                os.remove(dbs)
            except OSError:
                pass
        self.midvatten.new_db()
        self.midvatten.ms.settingsareloaded = True

        for filename in TestExport.exported_csv_files:
            try:
                os.remove(filename)
            except OSError:
                pass

    def tearDown(self):
        #Delete database
        for dbs in [TEMP_DB_PATH, EXPORT_DB_PATH]:
            try:
                os.remove(dbs)
            except OSError:
                pass
        for filename in TestExport.exported_csv_files:
            try:
                os.remove(filename)
            except OSError:
                pass

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('midvatten.utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten.QFileDialog.getExistingDirectory')
    @mock.patch('midvatten.qgis.utils.iface', autospec=True)
    def test_export_csv(self, mock_iface, mock_savepath):
        mock_savepath.return_value = u'/tmp/'
        utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P1", GeomFromText('POINT(633466, 711659)', 3006))''')
        utils.sql_alter_db(u'''insert into zz_staff (staff) values ('s1')''')
        utils.sql_alter_db(u'''insert into comments (obsid, date_time, staff, comment) values ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        utils.sql_alter_db(u'''insert into w_qual_lab (obsid, parameter, report, staff) values ('P1', 'labpar1', 'report1', 's1')''')
        utils.sql_alter_db(u'''insert into w_qual_field (obsid, parameter, staff, date_time) values ('P1', 'labpar1', 's1', '2015-01-01 01:00:00')''')
        utils.sql_alter_db(u'''insert into w_flow (obsid, instrumentid, flowtype, date_time, unit) values ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        utils.sql_alter_db(u'''insert into w_levels (obsid, date_time, meas) values ('P1', '2015-01-02 00:00:01', '2')''')
        utils.sql_alter_db(u'''insert into stratigraphy (obsid, stratid) values ('P1', 'strat1')''')
        utils.sql_alter_db(u'''insert into obs_lines (obsid) values ('L1')''')
        utils.sql_alter_db(u'''insert into seismic_data (obsid, length) values ('L1', '5')''')
        utils.sql_alter_db(u'''insert into meteo (obsid, instrumentid, parameter, date_time) values ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        self.midvatten.export_csv()

        file_contents = []
        for filename in TestExport.exported_csv_files_no_zz:
            with io.open(filename, 'r', encoding='utf-8') as f:
                file_contents.append(os.path.basename(filename) + '\n')
                file_contents.append([l.replace('\r', '') for l in f])
        test_string = utils_for_tests.create_test_string(file_contents)

        with io.open('/tmp/refstring.txt', 'w', encoding='utf-8') as of:
            of.write(test_string)

        reference_string = '\n'.join([
            "[obs_points.csv",
            ", [obsid;name;place;type;length;drillstop;diam;material;screen;capacity;drilldate;wmeas_yn;wlogg_yn;east;north;ne_accur;ne_source;h_toc;h_tocags;h_gs;h_accur;h_syst;h_source;source;com_onerow;com_html;geometry",
            ", P1;;;;;;;;;;;;;;;;;;;;;;;;;;",
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
            ", P1;s1;2015-01-01 01:00:00;;labpar1;;;;;",
            "], stratigraphy.csv",
            ", [obsid;stratid;depthtop;depthbot;geology;geoshort;capacity;development;comment",
            ", P1;strat1;;;;;;;",
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

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten.utils.get_selected_features_as_tuple', mock_selection.get_v)
    @mock.patch('midvatten.utils.verify_msettings_loaded_and_layer_edit_mode', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten.utils.find_layer', autospec=True)
    @mock.patch('midvatten.qgis.utils.iface', autospec=True)
    @mock.patch('export_data.utils.pop_up_info', autospec=True)
    def test_export_spatialite(self, mock_skip_popup, mock_iface, mock_find_layer, mock_newdbpath, mock_verify):

        mock_find_layer.return_value.crs.return_value.authid.return_value = u'EPSG:3006'

        mock_newdbpath.return_value = EXPORT_DB_PATH
        mock_verify.return_value = 0

        utils.sql_alter_db(u'''insert into obs_points (obsid, geometry) values ("P1", GeomFromText('POINT(633466, 711659)', 3006))''')
        utils.sql_alter_db(u'''insert into zz_staff (staff) values ('s1')''')
        utils.sql_alter_db(u'''insert into comments (obsid, date_time, staff, comment) values ('P1', '2015-01-01 00:00:00', 's1', 'comment1')''')
        utils.sql_alter_db(u'''insert into w_qual_lab (obsid, parameter, report, staff) values ('P1', 'labpar1', 'report1', 's1')''')
        utils.sql_alter_db(u'''insert into w_qual_field (obsid, parameter, staff, date_time, unit) values ('P1', 'par1', 's1', '2015-01-01 01:00:00', 'unit1')''')
        utils.sql_alter_db(u'''insert into w_flow (obsid, instrumentid, flowtype, date_time, unit) values ('P1', 'inst1', 'Momflow', '2015-04-13 00:00:00', 'l/s')''')
        utils.sql_alter_db(u'''insert into w_levels (obsid, date_time, meas) values ('P1', '2015-01-02 00:00:01', '2')''')
        utils.sql_alter_db(u'''insert into stratigraphy (obsid, stratid) values ('P1', 'strat1')''')
        utils.sql_alter_db(u'''insert into obs_lines (obsid) values ('L1')''')
        utils.sql_alter_db(u'''insert into seismic_data (obsid, length) values ('L1', '5')''')
        utils.sql_alter_db(u'''insert into meteo (obsid, instrumentid, parameter, date_time) values ('P1', 'meteoinst', 'precip', '2017-01-01 00:19:00')''')

        self.midvatten.export_spatialite()

        sql_list = [u'''select obsid from obs_points''',
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
                            u'''select obsid from obs_points''',
                            u''', [(P1)], ''',
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
                            u''', [(P1, strat1)], ''',
                            u'''select obsid from obs_lines''',
                            u''', [(L1)], ''',
                            u'''select obsid, length from seismic_data''',
                            u''', [(L1, 5.0)], ''',
                            u'''select obsid, instrumentid, parameter, date_time from meteo''',
                            u''', [(P1, meteoinst, precip, 2017-01-01 00:19:00)]]''']
        reference_string = u'\n'.join(reference_string)
        assert test_string == reference_string




