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
from export_fieldlogger2 import ExportToFieldLogger
from mocks_for_tests import MockUsingReturnValue
import export_fieldlogger2 as export_fieldlogger
import midvatten_utils as utils
from midvatten_utils import anything_to_string_representation
from nose.tools import raises
from mock import MagicMock, call, patch
import mock
import utils_for_tests
from utils_for_tests import dict_to_sorted_list, create_test_string
import ast

class _TestExportFieldloggerNoDb():
    def setUp(self):
        #self.ExportToFieldLogger = ExportToFieldLogger
        pass

    @staticmethod
    def test_get_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {u"test_settings_key": u'((0, (u"final_parameter_name", u"testname"), (u"test", u"gotten_test")), (1, (u"key1", u"value1"), (u"key2", u"value2"), (u"key3", u"value3")))'}
        settingskey = u'test_settings_key'
        stored_settings = create_test_string(ExportToFieldLogger.get_stored_settings(mock_ms, settingskey))
        reference_string = u'((0, (final_parameter_name, testname), (test, gotten_test)), (1, (key1, value1), (key2, value2), (key3, value3)))'
        assert stored_settings == reference_string

    @staticmethod
    def test_save_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {}
        stored_settings = [(0, ((u'input_field_group_list', [u'p1.u1;it1:h1', u'p2.u2;it2:h2']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        testkey = u'thekey'
        ExportToFieldLogger.save_stored_settings(mock_ms, stored_settings, testkey)

        teststring = mock_ms.settingsdict[testkey]
        reference_string = u'[(0, ((u"input_field_group_list", [u"p1.u1;it1:h1", u"p2.u2;it2:h2"], ), (u"key0_2", u"value0_2", ), ), ), (1, ((u"location_suffix", u"value1_1", ), (u"key1_2", u"value1_2", ), ), )]'
        assert teststring == reference_string

    @staticmethod
    def test_get_stored_settings_parameter_browser():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {u'fieldlogger_export_parameter_browser': u'((0, (u"input_field_group_list", (u"p1.u1;input;hint", u"np2.u2;input2;hint2"), ), ), )'}
        settingskey = u'fieldlogger_export_parameter_browser'
        stored_settings = create_test_string(ExportToFieldLogger.get_stored_settings(mock_ms, settingskey))
        reference_string = u'((0, (input_field_group_list, (p1.u1;input;hint, np2.u2;input2;hint2))))'
        assert stored_settings == reference_string

    @staticmethod
    def test_update_stored_settings():

        parameter_groups = [MagicMock(), MagicMock()]
        parameter_groups[0].get_settings.return_value = ((u'key0_1', u'value0_1'), (u'key0_2', u'value0_2'))
        parameter_groups[1].get_settings.return_value = ((u'key1_1', u'value1_1'), (u'key1_2', u'value1_2'))

        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        test_string = create_test_string(stored_settings)
        reference_string = u'[[0, ((key0_1, value0_1), (key0_2, value0_2))], [1, ((key1_1, value1_1), (key1_2, value1_2))]]'
        assert test_string == reference_string

    @staticmethod
    def test_update_stored_settings_using_real_parameter_groups():

        mock_connect = MagicMock()
        parameter_groups = [export_fieldlogger.ParameterGroup(mock_connect),
                          export_fieldlogger.ParameterGroup(mock_connect)]

        setattr(parameter_groups[0], 'input_field_group_list', [u'p1.u1;it1:h1', u'p2.u2;it2:h2'])
        setattr(parameter_groups[1], 'location_suffix', 'loc1')
        setattr(parameter_groups[1], 'sublocation_suffix', 'subloc1')

        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        test_string = create_test_string(stored_settings)
        reference_string = u'[[0, ((input_field_group_list, [p1.u1;it1:h1, p2.u2;it2:h2]))], [1, ((location_suffix, loc1), (sublocation_suffix, subloc1))]]'
        assert test_string == reference_string

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_no_settings():
        stored_settings = [(0, ((u'key0_1', u'value0_1'), (u'key0_2', u'value0_2'))), (1, ((u'key1_1', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        assert stored_settings == []

    @staticmethod
    def test_create_parameter_groups_using_stored_settings():
        stored_settings = [(0, ((u'input_field_group_list', [u'p1.u1;it1:h1, p2.u2;it2:h2']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = u'[[0, ((input_field_group_list, [p1.u1;it1:h1, p2.u2;it2:h2]))], [1, ((location_suffix, value1_1))]]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_nonexisting_variable_name():
        stored_settings = [(0, ((u'parameter_liöst', [u'p1.u1;it1:h1, p2.u2;it2:h2']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = u'[[0, ((location_suffix, value1_1))]]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_nonexisting_variable_name_empty_result():
        stored_settings = [(0, ((u'parameter_liöst', [u'p1.u1;it1:h1, p2.u2;it2:h2']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_s%uffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = u'[]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_browser_using_stored_settings():
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])
        stored_settings = [(0, ((u'input_field_list', [u'p1.u1;it1:h1', u'p2.u2;it2:h2']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        parameter_browser = export_fieldlogger.ParameterBrowser(tables_columns, mock_connect)
        ExportToFieldLogger.update_parameter_browser_using_stored_settings(stored_settings, parameter_browser)

        test_string = create_test_string(ExportToFieldLogger.update_stored_settings([parameter_browser]))
        reference = u'[[0, ((input_field_list, [p1.u1;it1:h1, p2.u2;it2:h2]))]]'
        assert test_string == reference

    @staticmethod
    def test_create_parameter_browser_using_stored_settings_nonexisting_variable_name():
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])
        stored_settings = [(0, ((u'input_field_läist', [u'p1.u1;it1:h1', u'p2.u2;it2:h2']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        mock_connect = MagicMock()

        parameter_browser = export_fieldlogger.ParameterBrowser(tables_columns, mock_connect)
        ExportToFieldLogger.update_parameter_browser_using_stored_settings(stored_settings, parameter_browser)

        test_string = create_test_string(ExportToFieldLogger.update_stored_settings([parameter_browser]))
        reference = u'[]'
        assert test_string == reference

    @staticmethod
    def test_get_stored_settings_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {u"fieldlogger_pgroups": u'((0, (u"input_field_group_list", [u"Aveflow.m3/s;numberDecimal|numberSigned;measure flow", u"Accflow.m3;numberDecimal|numberSigned;measure flow"])))'}
        settingskey = u'fieldlogger_pgroups'
        test_string = create_test_string(ExportToFieldLogger.get_stored_settings(mock_ms, settingskey))
        reference_string = u'(0, (input_field_group_list, [Aveflow.m3/s;numberDecimal|numberSigned;measure flow, Accflow.m3;numberDecimal|numberSigned;measure flow]))'
        assert test_string == reference_string

    @staticmethod
    def test_save_stored_settings_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {}
        stored_settings = [(0, ((u'input_field_group_list', [u'Aveflow.m3/s;numberDecimal|numberSigned;measure flow', u'Accflow.m3;numberDecimal|numberSigned;measure flow']), (u'key0_2', u'value0_2'))),
                           (1, ((u'location_suffix', u'value1_1'), (u'key1_2', u'value1_2')))]
        testkey = u'fieldlogger_pgroups'
        ExportToFieldLogger.save_stored_settings(mock_ms, stored_settings, testkey)

        teststring = create_test_string(mock_ms.settingsdict[testkey])
        reference_string = u'[(0, ((u"input_field_group_list", [u"Aveflow.m3/s;numberDecimal|numberSigned;measure flow", u"Accflow.m3;numberDecimal|numberSigned;measure flow"], ), (u"key0_2", u"value0_2", ), ), ), (1, ((u"location_suffix", u"value1_1", ), (u"key1_2", u"value1_2", ), ), )]'
        assert teststring == reference_string

    @staticmethod
    def test_get_stored_settings_parameter_browser_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {u"fieldlogger_pbrowser": u'[(0, (u"input_field_group_list", [u"Aveflow.m3/s;numberDecimal|numberSigned;measure flow", u"Accflow.m3;numberDecimal|numberSigned;measure flow"]))]'}
        settingskey = u'fieldlogger_pbrowser'
        test_string = create_test_string(ExportToFieldLogger.get_stored_settings(mock_ms, settingskey))
        reference_string = u'[(0, (input_field_group_list, [Aveflow.m3/s;numberDecimal|numberSigned;measure flow, Accflow.m3;numberDecimal|numberSigned;measure flow]))]'
        assert test_string == reference_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_empty_input_field_group_list(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (None, None)}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'final_parameter_name', u'par1'), (u'sublocation_suffix', u'group'), (u'location_suffix', u'proj')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.warning.assert_called_with(bar_msg=u'Warning: Empty parameter list for group nr 1')

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_no_latlon(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (None, None)}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'p1.u1;it1:h1 ']), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_called_with(bar_msg=u'Critical: Obsid 1 did not have lat-lon coordinates. Check obs_points table')

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par1;type1;hint1']), (u'sublocation_suffix', u'group'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par2;type2;hint2']), (u'sublocation_suffix', u'group'), (u'location_suffix', u'proj2')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1', u'4'])
        parameter_groups[1]._obsid_list.paste_data([u'2', u'3', u'4'])
        
        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_duplicate_parameters(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par1;type1;hint1']), (u'sublocation_suffix', u'group'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par1;type2;hint2']), (u'sublocation_suffix', u'group2'), (u'location_suffix', u'proj')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1'])
        parameter_groups[1]._obsid_list.paste_data([u'1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;1, NAME;INPUTTYPE;HINT, par1;type1;hint1 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 1.proj;1.proj.group2;lat1;lon1;par1]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_duplicate_sub_location_suffixes(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par1;type1;hint1']), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par2;type2;hint2']), (u'sublocation_suffix', u'proj.group'), (u'location_suffix', u'proj')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1'])
        parameter_groups[1]._obsid_list.paste_data([u'1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = printlist
        assert test_string is None
        assert call.critical(bar_msg=u'Critical: Combination of obsid, locationsuffix and sublocation suffix must be unique') in mock_MessagebarAndLog.mock_calls

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_no_critical_msg(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (123, 465), u'2': (123, 465), u'3': (123, 465)}

        stored_settings = [(0, ((u'input_field_group_list', [u'p1.u1;it1:h1', u'l.comment;test;make a comment']), (u'location_suffix', u'ls'), (u'sublocation_suffix', u'with_p1_u1_and_l_comment'))),
                           (1, ((u'input_field_group_list', [u'comment;test;make a general comment']), (u'location_suffix', u'ls'), (u'sublocation_suffix', u'with_comment')))]

        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1', u'2', u'3'])
        parameter_groups[1]._obsid_list.paste_data([u'1', u'2', u'3'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_not_called()
        reference_string = u'[FileVersion 1;3, NAME;INPUTTYPE;HINT, p1.u1;it1:h1 , l.comment;test;make a comment , comment;test;make a general comment , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.ls;1.ls.with_comment;123;465;comment, 1.ls;1.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment, 2.ls;2.ls.with_comment;123;465;comment, 2.ls;2.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment, 3.ls;3.ls.with_comment;123;465;comment, 3.ls;3.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment]'
        assert test_string == reference_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_not_same_latlon(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par1;type1;hint1']), (u'sublocation_suffix', u'group1'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par2;type2;hint2']), (u'sublocation_suffix', u'group2'), (u'location_suffix', u'proj')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1', u'4'])
        parameter_groups[1]._obsid_list.paste_data([u'2', u'3', u'4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1, 2.proj;2.proj.group2;lat2;lon2;par2, 4.proj;4.proj.group1;lat4;lon4;par1, 4.proj;4.proj.group2;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_not_same_latlon2(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par1;type1;hint1']), (u'sublocation_suffix', u'group1'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par2;type2;hint2']), (u'sublocation_suffix', u'group2'), (u'location_suffix', u'proj'))),
                           (2, ((u'input_field_group_list', [u'par3;type3;hint3']), (u'sublocation_suffix', u'group3'), (u'location_suffix', u'proj')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1', u'4'])
        parameter_groups[1]._obsid_list.paste_data([u'2', u'3', u'4'])
        parameter_groups[2]._obsid_list.paste_data([u'2', u'4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;3, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , par3;type3;hint3 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1, 2.proj;2.proj.group2;lat2;lon2;par2, 2.proj;2.proj.group3;lat2;lon2;par3, 4.proj;4.proj.group1;lat4;lon4;par1, 4.proj;4.proj.group2;lat4;lon4;par2, 4.proj;4.proj.group3;lat4;lon4;par3]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_not_same_latlon3(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par1;type1;hint1', u'par2;type2;hint2']), (u'sublocation_suffix', u'group1'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par3;type3;hint3']), (u'sublocation_suffix', u'group2'), (u'location_suffix', u'proj')))]

        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1', u'2', u'4'])
        parameter_groups[1]._obsid_list.paste_data([u'1', u'2', u'4'])


        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;3, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , par3;type3;hint3 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1|par2, 1.proj;1.proj.group2;lat1;lon1;par3, 2.proj;2.proj.group1;lat2;lon2;par1|par2, 2.proj;2.proj.group2;lat2;lon2;par3, 4.proj;4.proj.group1;lat4;lon4;par1|par2, 4.proj;4.proj.group2;lat4;lon4;par3]'
        assert reference_string == test_string

    @mock.patch('export_fieldlogger2.utils.pop_up_info')
    @mock.patch('export_fieldlogger2.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger2.PyQt4.QtGui.QInputDialog.getText')
    @mock.patch('export_fieldlogger2.defs.tables_columns')
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_create_parameter_groups_using_stored_settings_string(self, mock_iface, mock_tables_columns, mock_settingsstrings, mock_settingsbarandlog, mock_popup):
        mock_tables_columns.return_value = {}
        mock_ms = MagicMock()
        mock_ms.settingsdict = {'fieldlogger_export_pbrowser': '',
                                'fieldlogger_export_pgroups': ''}
        mock_settingsstrings.side_effect = [(u'[[0, ((u"input_field_list", [u"DO.mg/L;numberDecimal|numberSigned; ", u"comment;text;Obsid related comment"], ), )]]', True),
                                            (u'[[0, ((u"input_field_group_list", [u"DO.mg/L;numberDecimal|numberSigned; ", u"comment;text;Obsid related comment"], ), (u"location_suffix", u"2766", ), (u"sublocation_suffix", u"level", ), )], [1, ((u"input_field_group_list", [u"comment;text;Obsid related comment"], ), (u"location_suffix", u"1234", ), (u"sublocation_suffix", u"comment", ), )]]', True)]

        exportfieldlogger = ExportToFieldLogger(None, mock_ms)

        exportfieldlogger.settings_strings_dialogs()

        assert mock_ms.settingsdict['fieldlogger_export_pbrowser'] == u'[[0, ((u"input_field_list", [u"DO.mg/L;numberDecimal|numberSigned; ", u"comment;text;Obsid related comment"], ), )]]'
        assert mock_ms.settingsdict['fieldlogger_export_pgroups'] == u'[[0, ((u"input_field_group_list", [u"DO.mg/L;numberDecimal|numberSigned; ", u"comment;text;Obsid related comment"], ), (u"location_suffix", u"2766", ), (u"sublocation_suffix", u"level", ), )], [1, ((u"input_field_group_list", [u"comment;text;Obsid related comment"], ), (u"location_suffix", u"1234", ), (u"sublocation_suffix", u"comment", ), )]]'

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_correct_order(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {u'1': (u'lat1', u'lon1'), u'2': (u'lat2', u'lon2'), u'4': (u'lat4', u'lon4')}
        tables_columns = OrderedDict([(u'testtable', (u'col1', u'col2'))])

        stored_settings = [(0, ((u'input_field_group_list', [u'par4;type1;hint1', u'par1;type1;hint1']), (u'sublocation_suffix', u'group'), (u'location_suffix', u'proj'))),
                           (1, ((u'input_field_group_list', [u'par2;type2;hint2']), (u'sublocation_suffix', u'group'), (u'location_suffix', u'proj2')))]
        mock_connect = MagicMock()

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, mock_connect)
        parameter_groups[0]._obsid_list.paste_data([u'1', u'4'])
        parameter_groups[1]._obsid_list.paste_data([u'2', u'3', u'4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = u'[FileVersion 1;3, NAME;INPUTTYPE;HINT, par4;type1;hint1 , par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par4|par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par4|par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

