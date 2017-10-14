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
from qgis.core import QgsApplication, QgsProviderRegistry
from utils_for_tests import init_test
from collections import OrderedDict
from tools.tests.mocks_for_tests import DummyInterface
from PyQt4 import QtCore, QtGui, QtTest
from export_fieldlogger import ExportToFieldLogger
from mocks_for_tests import MockUsingReturnValue
import export_fieldlogger
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
import utils_for_tests
from utils_for_tests import dict_to_sorted_list, create_test_string

class _TestExportFieldloggerNoDb():
    def setUp(self):
        self.ExportToFieldLogger = ExportToFieldLogger

    @staticmethod
    def test_get_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {u'test_settings_key': u'0;final_parameter_name:testname;test:gotten_test/1;key1:value1;key2:value2;key3:value3'}
        settingskey = u'test_settings_key'
        stored_settings = create_test_string(ExportToFieldLogger.get_stored_settings(mock_ms, settingskey))
        reference_string = u'((0, ((final_parameter_name, testname), (test, gotten_test))), (1, ((key1, value1), (key2, value2), (key3, value3))))'
        assert stored_settings == reference_string

    @staticmethod
    def test_update_stored_settings():

        export_objects = [MagicMock(), MagicMock()]
        export_objects[0].get_settings.return_value = ((u'key0_1', u'value0_1'), (u'key0_2', u'value0_2'))
        export_objects[1].get_settings.return_value = ((u'key1_1', u'value1_1'), (u'key1_2', u'value1_2'))

        stored_settings = ExportToFieldLogger.update_stored_settings(export_objects)
        test_string = create_test_string(stored_settings)
        reference_string = u'[(0, ((key0_1, value0_1), (key0_2, value0_2))), (1, ((key1_1, value1_1), (key1_2, value1_2)))]'
        assert test_string == reference_string

    @staticmethod
    def test_update_stored_settings_using_real_export_objects():

        mock_connect = MagicMock()
        export_objects = [export_fieldlogger.ExportObject(mock_connect),
                          export_fieldlogger.ExportObject(mock_connect)]

        setattr(export_objects[0], 'final_parameter_name', 'testname1')
        setattr(export_objects[1], 'final_parameter_name', 'testname2')
        setattr(export_objects[1], 'location_suffix', 'locationsuffix2')

        stored_settings = ExportToFieldLogger.update_stored_settings(export_objects)
        test_string = create_test_string(stored_settings)
        reference_string = u'[(0, ((final_parameter_name, testname1))), (1, ((final_parameter_name, testname2), (location_suffix, locationsuffix2)))]'
        assert test_string == reference_string

    @staticmethod
    def test_create_export_objects_using_stored_settings_no_settings():
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])
        stored_settings = [(0, ((u'key0_1', u'value0_1'), (u'key0_2', u'value0_2'))), (1, ((u'key1_1', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings, tables_columns, mock_connect)
        stored_settings = ExportToFieldLogger.update_stored_settings(export_objects)
        assert stored_settings == []

    @staticmethod
    def test_create_export_objects_using_stored_settings():
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])
        stored_settings = [(0, ((u'final_parameter_name', u'value0_1'), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings,
                                                                                           tables_columns,
                                                                                           mock_connect)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(export_objects))
        reference = u'[(0, ((final_parameter_name, value0_1))), (1, ((location_suffix, value1_1)))]'
        assert stored_settings == reference

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_no_comment(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type1'), (u'hint', u'hint1'))),
                           (1, ((u'final_parameter_name', u'par2'), (u'sublocation_suffix', u'proj2.group'), (u'location_suffix', u'proj2'), (u'input_type', u'type2'), (u'hint', u'hint2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings,
                                                                                           tables_columns,
                                                                                           mock_connect)
        export_objects[0].obsid_list.addItems([u'1', u'4'])
        export_objects[1].obsid_list.addItems([u'2', u'3', u'4'])

        printlist = ExportToFieldLogger.create_export_printlist(export_objects)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.warning.assert_called_with(bar_msg=u'Warning: No comment parameter found. Is it forgotten?')

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_no_latlon(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type1'), (u'hint', u'hint1'))),
                           (1, ((u'final_parameter_name', u'par2'), (u'sublocation_suffix', u'proj2.group'), (u'location_suffix', u'proj2'), (u'input_type', u'type2'), (u'hint', u'hint2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings,
                                                                                           tables_columns,
                                                                                           mock_connect)
        export_objects[0].obsid_list.addItems([u'1', u'4'])
        export_objects[1].obsid_list.addItems([u'2', u'3', u'4'])

        printlist = ExportToFieldLogger.create_export_printlist(export_objects)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_called_with(bar_msg=u'Critical: Obsid  did not have lat-lon coordinates. Check obs_points table')

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type1'), (u'hint', u'hint1'))),
                           (1, ((u'final_parameter_name', u'par2'), (u'sublocation_suffix', u'proj2.group'), (u'location_suffix', u'proj2'), (u'input_type', u'type2'), (u'hint', u'hint2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings,
                                                                                           tables_columns,
                                                                                           mock_connect)
        export_objects[0].obsid_list.addItems([u'1', u'4'])
        export_objects[1].obsid_list.addItems([u'2', u'3', u'4'])

        printlist = ExportToFieldLogger.create_export_printlist(export_objects)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1, par2;type2;hint2, NAME;sublocation;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_one_obsid_two_parameters(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type1'), (u'hint', u'hint1'))),
                           (1, ((u'final_parameter_name', u'par2'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type2'), (u'hint', u'hint2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings,
                                                                                           tables_columns,
                                                                                           mock_connect)
        export_objects[0].obsid_list.addItems([u'1'])
        export_objects[1].obsid_list.addItems([u'1'])

        printlist = ExportToFieldLogger.create_export_printlist(export_objects)
        test_string = create_test_string(printlist)

        reference_string = u'[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1, par2;type2;hint2, NAME;sublocation;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1|par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_duplicate_parameters(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type1'), (u'hint', u'hint1'))),
                           (1, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type2'), (u'hint', u'hint2'))),
                           (2, ((u'final_parameter_name', u'comment'), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'), (u'input_type', u'type2'), (u'hint', u'hint2')))]
        mock_connect = MagicMock()

        export_objects = ExportToFieldLogger.create_export_objects_using_stored_settings(stored_settings,
                                                                                           tables_columns,
                                                                                           mock_connect)
        export_objects[0].obsid_list.addItems([u'1'])
        export_objects[1].obsid_list.addItems([u'1'])

        test_string = create_test_string(ExportToFieldLogger.create_export_printlist(export_objects))
        parameter = u'par1'
        mock_MessagebarAndLog.warning.assert_called_with(bar_msg=u"Warning: Parameter " + parameter + u' error. See log message panel', log_msg=u'The parameter ' + parameter + u' already exists. Only the first occurence one will be written to file.')
        reference_string = u'[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1, comment;type2;hint2, NAME;sublocation;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1]'
        assert test_string == reference_string


