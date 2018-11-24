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
from __future__ import absolute_import
from builtins import object

from collections import OrderedDict

import export_fieldlogger
import mock
from export_fieldlogger import ExportToFieldLogger
from mock import MagicMock
from nose.plugins.attrib import attr
import midvatten_utils as utils

from .utils_for_tests import create_test_string


@attr(status='on')
class TestExportFieldloggerNoDb(object):
    def setUp(self):
        #self.ExportToFieldLogger = ExportToFieldLogger
        pass

    @staticmethod
    def test_get_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {"test_settings_key": '((0, ("final_parameter_name", "testname"), ("test", "gotten_test")), (1, ("key1", "value1"), ("key2", "value2"), ("key3", "value3")))'}
        settingskey = 'test_settings_key'
        stored_settings = create_test_string(utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '((0, (final_parameter_name, testname), (test, gotten_test)), (1, (key1, value1), (key2, value2), (key3, value3)))'
        assert stored_settings == reference_string

    @staticmethod
    def test_save_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {}
        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1', 'p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]
        testkey = 'thekey'
        utils.save_stored_settings(mock_ms, stored_settings, testkey)

        teststring = mock_ms.settingsdict[testkey]
        reference_string = '[(0, (("input_field_group_list", ["p1.u1;it1:h1", "p2.u2;it2:h2"], ), ("key0_2", "value0_2", ), ), ), (1, (("location_suffix", "value1_1", ), ("key1_2", "value1_2", ), ), )]'
        assert teststring == reference_string

    @staticmethod
    def test_get_stored_settings_parameter_browser():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {'fieldlogger_export_parameter_browser': '((0, ("input_field_group_list", ("p1.u1;input;hint", "np2.u2;input2;hint2"), ), ), )'}
        settingskey = 'fieldlogger_export_parameter_browser'
        stored_settings = create_test_string(utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '((0, (input_field_group_list, (p1.u1;input;hint, np2.u2;input2;hint2))))'
        assert stored_settings == reference_string

    @staticmethod
    def test_update_stored_settings():

        parameter_groups = [MagicMock(), MagicMock()]
        parameter_groups[0].get_settings.return_value = (('key0_1', 'value0_1'), ('key0_2', 'value0_2'))
        parameter_groups[1].get_settings.return_value = (('key1_1', 'value1_1'), ('key1_2', 'value1_2'))

        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        test_string = create_test_string(stored_settings)
        reference_string = '[[0, ((key0_1, value0_1), (key0_2, value0_2))], [1, ((key1_1, value1_1), (key1_2, value1_2))]]'
        assert test_string == reference_string

    @staticmethod
    def test_update_stored_settings_using_real_parameter_groups():

        parameter_groups = [export_fieldlogger.ParameterGroup(),
                          export_fieldlogger.ParameterGroup()]

        setattr(parameter_groups[0], 'input_field_group_list', ['p1.u1;it1:h1', 'p2.u2;it2:h2'])
        setattr(parameter_groups[1], 'location_suffix', 'loc1')
        setattr(parameter_groups[1], 'sublocation_suffix', 'subloc1')

        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        test_string = create_test_string(stored_settings)
        reference_string = '[[0, ((input_field_group_list, [p1.u1;it1:h1, p2.u2;it2:h2]))], [1, ((location_suffix, loc1), (sublocation_suffix, subloc1))]]'
        assert test_string == reference_string

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_no_settings():
        stored_settings = [(0, (('key0_1', 'value0_1'), ('key0_2', 'value0_2'))), (1, (('key1_1', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        assert stored_settings == []

    @staticmethod
    def test_create_parameter_groups_using_stored_settings():
        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1, p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = '[[0, ((input_field_group_list, [p1.u1;it1:h1, p2.u2;it2:h2]))], [1, ((location_suffix, value1_1))]]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_nonexisting_variable_name():
        stored_settings = [(0, (('parameter_läistä', ['p1.u1;it1:h1, p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = '[[0, ((location_suffix, value1_1))]]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_nonexisting_variable_name_empty_result():
        stored_settings = [(0, (('parameter_liöst', ['p1.u1;it1:h1, p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_s%uffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = '[]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_browser_using_stored_settings():
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])
        stored_settings = [(0, (('input_field_list', ['p1.u1;it1:h1', 'p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_browser = export_fieldlogger.ParameterBrowser(tables_columns)
        ExportToFieldLogger.update_parameter_browser_using_stored_settings(stored_settings, parameter_browser)

        test_string = create_test_string(ExportToFieldLogger.update_stored_settings([parameter_browser]))
        reference = '[[0, ((input_field_list, [p1.u1;it1:h1, p2.u2;it2:h2]))]]'
        assert test_string == reference

    @staticmethod
    @attr(status='only')
    def test_create_parameter_browser_using_stored_settings_nonexisting_variable_name():
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])
        stored_settings = [(0, (('input_field_läistä', ['p1.u1;it1:h1', 'p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_browser = export_fieldlogger.ParameterBrowser(tables_columns)
        ExportToFieldLogger.update_parameter_browser_using_stored_settings(stored_settings, parameter_browser)

        test_string = create_test_string(ExportToFieldLogger.update_stored_settings([parameter_browser]))
        reference = '[]'
        assert test_string == reference

    @staticmethod
    def test_get_stored_settings_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {"fieldlogger_pgroups": '((0, ("input_field_group_list", ["Aveflow.m3/s;numberDecimal|numberSigned;measure flow", "Accflow.m3;numberDecimal|numberSigned;measure flow"])))'}
        settingskey = 'fieldlogger_pgroups'
        test_string = create_test_string(utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '(0, (input_field_group_list, [Aveflow.m3/s;numberDecimal|numberSigned;measure flow, Accflow.m3;numberDecimal|numberSigned;measure flow]))'
        assert test_string == reference_string

    @staticmethod
    def test_save_stored_settings_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {}
        stored_settings = [(0, (('input_field_group_list', ['Aveflow.m3/s;numberDecimal|numberSigned;measure flow', 'Accflow.m3;numberDecimal|numberSigned;measure flow']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]
        testkey = 'fieldlogger_pgroups'
        utils.save_stored_settings(mock_ms, stored_settings, testkey)

        teststring = create_test_string(mock_ms.settingsdict[testkey])
        reference_string = '[(0, (("input_field_group_list", ["Aveflow.m3/s;numberDecimal|numberSigned;measure flow", "Accflow.m3;numberDecimal|numberSigned;measure flow"], ), ("key0_2", "value0_2", ), ), ), (1, (("location_suffix", "value1_1", ), ("key1_2", "value1_2", ), ), )]'
        assert teststring == reference_string

    @staticmethod
    def test_get_stored_settings_parameter_browser_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {"fieldlogger_pbrowser": '[(0, ("input_field_group_list", ["Aveflow.m3/s;numberDecimal|numberSigned;measure flow", "Accflow.m3;numberDecimal|numberSigned;measure flow"]))]'}
        settingskey = 'fieldlogger_pbrowser'
        test_string = create_test_string(utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '[(0, (input_field_group_list, [Aveflow.m3/s;numberDecimal|numberSigned;measure flow, Accflow.m3;numberDecimal|numberSigned;measure flow]))]'
        assert test_string == reference_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_empty_input_field_group_list(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': (None, None)}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('final_parameter_name', 'par1'), ('sublocation_suffix', 'group'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.warning.assert_called_with(bar_msg='Warning: Empty input fields list for group nr 1')

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_no_latlon(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': (None, None)}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1 ']), ('sublocation_suffix', 'proj.group'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_called_with(bar_msg='Critical: Obsid 1 did not have lat-lon coordinates. Check obs_points table')

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])
        
        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = '[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_duplicate_parameters(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par1;type2;hint2']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1'])
        parameter_groups[1]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = '[FileVersion 1;1, NAME;INPUTTYPE;HINT, par1;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 1.proj;1.proj.group2;lat1;lon1;par1]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_duplicate_sub_location_suffixes(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1'])
        parameter_groups[1]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference = '[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1|par2]'
        assert test_string == reference

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_assert_no_critical_msg(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': (123, 465), '2': (123, 465), '3': (123, 465)}

        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1', 'l.comment;test;make a comment']), ('location_suffix', 'ls'), ('sublocation_suffix', 'with_p1_u1_and_l_comment'))),
                           (1, (('input_field_group_list', ['comment;test;make a general comment']), ('location_suffix', 'ls'), ('sublocation_suffix', 'with_comment')))]



        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1', '2', '3'])
        parameter_groups[1]._obsid_list.paste_data(['1', '2', '3'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_not_called()
        reference_string = '[FileVersion 1;3, NAME;INPUTTYPE;HINT, p1.u1;it1:h1 , l.comment;test;make a comment , comment;test;make a general comment , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.ls;1.ls.with_comment;123;465;comment, 1.ls;1.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment, 2.ls;2.ls.with_comment;123;465;comment, 2.ls;2.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment, 3.ls;3.ls.with_comment;123;465;comment, 3.ls;3.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment]'
        assert test_string == reference_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_not_same_latlon(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group1'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = '[FileVersion 1;2, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1, 2.proj;2.proj.group2;lat2;lon2;par2, 4.proj;4.proj.group1;lat4;lon4;par1, 4.proj;4.proj.group2;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_not_same_latlon2(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group1'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj'))),
                           (2, (('input_field_group_list', ['par3;type3;hint3']), ('sublocation_suffix', 'group3'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])
        parameter_groups[2]._obsid_list.paste_data(['2', '4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = '[FileVersion 1;3, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , par3;type3;hint3 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1, 2.proj;2.proj.group2;lat2;lon2;par2, 2.proj;2.proj.group3;lat2;lon2;par3, 4.proj;4.proj.group1;lat4;lon4;par1, 4.proj;4.proj.group2;lat4;lon4;par2, 4.proj;4.proj.group3;lat4;lon4;par3]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_not_same_latlon3(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1', 'par2;type2;hint2']), ('sublocation_suffix', 'group1'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par3;type3;hint3']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj')))]



        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1', '2', '4'])
        parameter_groups[1]._obsid_list.paste_data(['1', '2', '4'])


        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = '[FileVersion 1;3, NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , par3;type3;hint3 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1|par2, 1.proj;1.proj.group2;lat1;lon1;par3, 2.proj;2.proj.group1;lat2;lon2;par1|par2, 2.proj;2.proj.group2;lat2;lon2;par3, 4.proj;4.proj.group1;lat4;lon4;par1|par2, 4.proj;4.proj.group2;lat4;lon4;par3]'
        assert reference_string == test_string

    @mock.patch('export_fieldlogger.utils.pop_up_info')
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.qgis.PyQt.QtWidgets.QInputDialog.getText')
    @mock.patch('export_fieldlogger.db_utils.tables_columns')
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_create_parameter_groups_using_stored_settings_string(self, mock_iface, mock_tables_columns, mock_settingsstrings, mock_settingsbarandlog, mock_popup):
        mock_tables_columns.return_value = {}
        mock_ms = MagicMock()
        mock_ms.settingsdict = {'fieldlogger_export_pbrowser': '',
                                'fieldlogger_export_pgroups': ''}
        mock_settingsstrings.side_effect = [('[[0, (("input_field_list", ["DO.mg/L;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), )]]', True),
                                            ('[[0, (("input_field_group_list", ["DO.mg/L;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), ("location_suffix", "2766", ), ("sublocation_suffix", "level", ), )], [1, (("input_field_group_list", ["comment;text;Obsid related comment"], ), ("location_suffix", "1234", ), ("sublocation_suffix", "comment", ), )]]', True)]

        exportfieldlogger = ExportToFieldLogger(None, mock_ms)

        exportfieldlogger.settings_strings_dialogs()

        assert mock_ms.settingsdict['fieldlogger_export_pbrowser'] == '[[0, (("input_field_list", ["DO.mg/L;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), )]]'
        assert mock_ms.settingsdict['fieldlogger_export_pgroups'] == '[[0, (("input_field_group_list", ["DO.mg/L;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), ("location_suffix", "2766", ), ("sublocation_suffix", "level", ), )], [1, (("input_field_group_list", ["comment;text;Obsid related comment"], ), ("location_suffix", "1234", ), ("sublocation_suffix", "comment", ), )]]'

    @staticmethod
    @mock.patch('export_fieldlogger.utils.MessagebarAndLog')
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids')
    def test_create_export_printlist_correct_order(mock_latlons, mock_MessagebarAndLog):
        mock_latlons.return_value = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par4;type1;hint1', 'par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups)
        test_string = create_test_string(printlist)
        reference_string = '[FileVersion 1;3, NAME;INPUTTYPE;HINT, par4;type1;hint1 , par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par4|par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par4|par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

