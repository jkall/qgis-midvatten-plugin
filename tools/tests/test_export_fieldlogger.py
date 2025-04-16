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

from collections import OrderedDict


import mock
from PyQt5.QtCore import QVariant

from mock import MagicMock
from nose.plugins.attrib import attr
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsField, QgsGeometry
from qgis.core import QgsProject

from midvatten.tools.utils import common_utils
from midvatten.tools.tests.utils_for_tests import create_test_string, create_vectorlayer, MidvattenTestBase
from midvatten.tools.export_fieldlogger import ExportToFieldLogger
from midvatten.tools import export_fieldlogger

@attr(status='on')
class TestExportFieldloggerNoDb(MidvattenTestBase):
    def setUp(self):
        super().__init__()
        #self.ExportToFieldLogger = ExportToFieldLogger
        pass
    def tearDown(self):
        super().tearDown()

    @staticmethod
    def test_get_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {"test_settings_key": '((0, ("final_parameter_name", "testname"), ("test", "gotten_test")), (1, ("key1", "value1"), ("key2", "value2"), ("key3", "value3")))'}
        settingskey = 'test_settings_key'
        stored_settings = create_test_string(common_utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '((0, (final_parameter_name, testname), (test, gotten_test)), (1, (key1, value1), (key2, value2), (key3, value3)))'
        assert stored_settings == reference_string

    @staticmethod
    def test_save_stored_settings():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {}
        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1', 'p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]
        testkey = 'thekey'
        common_utils.save_stored_settings(mock_ms, stored_settings, testkey)

        teststring = mock_ms.settingsdict[testkey]
        reference_string = '[(0, (("input_field_group_list", ["p1.u1;it1:h1", "p2.u2;it2:h2"], ), ("key0_2", "value0_2", ), ), ), (1, (("location_suffix", "value1_1", ), ("key1_2", "value1_2", ), ), )]'
        assert teststring == reference_string

    @staticmethod
    def test_get_stored_settings_parameter_browser():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {'fieldlogger_export_parameter_browser': '((0, ("input_field_group_list", ("p1.u1;input;hint", "np2.u2;input2;hint2"), ), ), )'}
        settingskey = 'fieldlogger_export_parameter_browser'
        stored_settings = create_test_string(common_utils.get_stored_settings(mock_ms, settingskey))
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

        parameter_groups = [export_fieldlogger.ParameterGroup(None),
                          export_fieldlogger.ParameterGroup(None)]

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


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        stored_settings = ExportToFieldLogger.update_stored_settings(parameter_groups)
        assert stored_settings == []

    @staticmethod
    def test_create_parameter_groups_using_stored_settings():
        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1, p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = '[[0, ((input_field_group_list, [p1.u1;it1:h1, p2.u2;it2:h2]))], [1, ((location_suffix, value1_1))]]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_nonexisting_variable_name():
        stored_settings = [(0, (('parameter_input_field_lNONEXISTING', ['p1.u1;it1:h1, p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        stored_settings = create_test_string(ExportToFieldLogger.update_stored_settings(parameter_groups))
        reference = '[[0, ((location_suffix, value1_1))]]'
        assert stored_settings == reference

    @staticmethod
    def test_create_parameter_groups_using_stored_settings_nonexisting_variable_name_empty_result():
        stored_settings = [(0, (('parameter_liöst', ['p1.u1;it1:h1, p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
                           (1, (('location_s%uffix', 'value1_1'), ('key1_2', 'value1_2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
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
    def test_create_parameter_browser_using_stored_settings_nonexisting_variable_name():
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])
        stored_settings = [(0, (('input_field_lNONEXISTING', ['p1.u1;it1:h1', 'p2.u2;it2:h2']), ('key0_2', 'value0_2'))),
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
        test_string = create_test_string(common_utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '(0, (input_field_group_list, [Aveflow.m3/s;numberDecimal|numberSigned;measure flow, Accflow.m3;numberDecimal|numberSigned;measure flow]))'
        assert test_string == reference_string

    @staticmethod
    def test_save_stored_settings_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {}
        stored_settings = [(0, (('input_field_group_list', ['Aveflow.m3/s;numberDecimal|numberSigned;measure flow', 'Accflow.m3;numberDecimal|numberSigned;measure flow']), ('key0_2', 'value0_2'))),
                           (1, (('location_suffix', 'value1_1'), ('key1_2', 'value1_2')))]
        testkey = 'fieldlogger_pgroups'
        common_utils.save_stored_settings(mock_ms, stored_settings, testkey)

        teststring = create_test_string(mock_ms.settingsdict[testkey])
        reference_string = '[(0, (("input_field_group_list", ["Aveflow.m3/s;numberDecimal|numberSigned;measure flow", "Accflow.m3;numberDecimal|numberSigned;measure flow"], ), ("key0_2", "value0_2", ), ), ), (1, (("location_suffix", "value1_1", ), ("key1_2", "value1_2", ), ), )]'
        assert teststring == reference_string

    @staticmethod
    def test_get_stored_settings_parameter_browser_real_parameter_name():
        mock_ms = MagicMock()
        mock_ms.settingsdict = {"fieldlogger_pbrowser": '[(0, ("input_field_group_list", ["Aveflow.m3/s;numberDecimal|numberSigned;measure flow", "Accflow.m3;numberDecimal|numberSigned;measure flow"]))]'}
        settingskey = 'fieldlogger_pbrowser'
        test_string = create_test_string(common_utils.get_stored_settings(mock_ms, settingskey))
        reference_string = '[(0, (input_field_group_list, [Aveflow.m3/s;numberDecimal|numberSigned;measure flow, Accflow.m3;numberDecimal|numberSigned;measure flow]))]'
        assert test_string == reference_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_assert_empty_input_field_group_list(mock_MessagebarAndLog):
        latlons = {'1': (None, None)}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('final_parameter_name', 'par1'), ('sublocation_suffix', 'group'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.warning.assert_called_with(bar_msg='Warning: Empty input fields list for group nr 1')

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_assert_no_latlon(mock_MessagebarAndLog):
        latlons = {'1': (None, None)}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1 ']), ('sublocation_suffix', 'proj.group'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_called_with(bar_msg='Critical: Obsid 1 did not have lat-lon coordinates. Check obs_points table')

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])
        
        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference_string = '[NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_duplicate_parameters(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par1;type2;hint2']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1'])
        parameter_groups[1]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference_string = '[NAME;INPUTTYPE;HINT, par1;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1, 1.proj;1.proj.group2;lat1;lon1;par1]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_duplicate_sub_location_suffixes(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1'])
        parameter_groups[1]._obsid_list.paste_data(['1'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference = '[NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par1|par2]'
        assert test_string == reference

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_assert_no_critical_msg(mock_MessagebarAndLog):
        latlons = {'1': (123, 465), '2': (123, 465), '3': (123, 465)}

        stored_settings = [(0, (('input_field_group_list', ['p1.u1;it1:h1', 'l.comment;test;make a comment']), ('location_suffix', 'ls'), ('sublocation_suffix', 'with_p1_u1_and_l_comment'))),
                           (1, (('input_field_group_list', ['comment;test;make a general comment']), ('location_suffix', 'ls'), ('sublocation_suffix', 'with_comment')))]

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1', '2', '3'])
        parameter_groups[1]._obsid_list.paste_data(['1', '2', '3'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        mock_MessagebarAndLog.critical.assert_not_called()
        reference_string = '[NAME;INPUTTYPE;HINT, p1.u1;it1:h1 , l.comment;test;make a comment , comment;test;make a general comment , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.ls;1.ls.with_comment;123;465;comment, 1.ls;1.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment, 2.ls;2.ls.with_comment;123;465;comment, 2.ls;2.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment, 3.ls;3.ls.with_comment;123;465;comment, 3.ls;3.ls.with_p1_u1_and_l_comment;123;465;p1.u1|l.comment]'
        assert test_string == reference_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_not_same_latlon(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group1'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference_string = '[NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1, 2.proj;2.proj.group2;lat2;lon2;par2, 4.proj;4.proj.group1;lat4;lon4;par1, 4.proj;4.proj.group2;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_not_same_latlon2(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group1'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj'))),
                           (2, (('input_field_group_list', ['par3;type3;hint3']), ('sublocation_suffix', 'group3'), ('location_suffix', 'proj')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])
        parameter_groups[2]._obsid_list.paste_data(['2', '4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference_string = '[NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , par3;type3;hint3 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1, 2.proj;2.proj.group2;lat2;lon2;par2, 2.proj;2.proj.group3;lat2;lon2;par3, 4.proj;4.proj.group1;lat4;lon4;par1, 4.proj;4.proj.group2;lat4;lon4;par2, 4.proj;4.proj.group3;lat4;lon4;par3]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_not_same_latlon3(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1', 'par2;type2;hint2']), ('sublocation_suffix', 'group1'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par3;type3;hint3']), ('sublocation_suffix', 'group2'), ('location_suffix', 'proj')))]



        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1', '2', '4'])
        parameter_groups[1]._obsid_list.paste_data(['1', '2', '4'])


        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference_string = '[NAME;INPUTTYPE;HINT, par1;type1;hint1 , par2;type2;hint2 , par3;type3;hint3 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group1;lat1;lon1;par1|par2, 1.proj;1.proj.group2;lat1;lon1;par3, 2.proj;2.proj.group1;lat2;lon2;par1|par2, 2.proj;2.proj.group2;lat2;lon2;par3, 4.proj;4.proj.group1;lat4;lon4;par1|par2, 4.proj;4.proj.group2;lat4;lon4;par3]'
        assert reference_string == test_string

    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.pop_up_info')
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.export_fieldlogger.qgis.PyQt.QtWidgets.QInputDialog.getText')
    @mock.patch('midvatten.tools.export_fieldlogger.db_utils.tables_columns')
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_create_parameter_groups_using_stored_settings_string(self, mock_iface, mock_tables_columns, mock_settingsstrings, mock_settingsbarandlog, mock_popup):
        mock_tables_columns.return_value = {}
        mock_ms = MagicMock()
        mock_ms.settingsdict = {'fieldlogger_export_pbrowser': '',
                                'fieldlogger_export_pgroups': ''}
        mock_settingsstrings.side_effect = [('[[0, (("input_field_list", ["DO.mg/l;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), )]]', True),
                                            ('[[0, (("input_field_group_list", ["DO.mg/l;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), ("location_suffix", "2766", ), ("sublocation_suffix", "level", ), )], [1, (("input_field_group_list", ["comment;text;Obsid related comment"], ), ("location_suffix", "1234", ), ("sublocation_suffix", "comment", ), )]]', True)]

        mock_iface = QWidget()
        mock_iface.legendInterface = mock.Mock()
        mock_iface.legendInterface.return_value.layers.return_value = []
        exportfieldlogger = ExportToFieldLogger(mock_iface, mock_ms)
        exportfieldlogger.obs_from_vlayer.setChecked(True)

        exportfieldlogger.settings_strings_dialogs()

        assert mock_ms.settingsdict['fieldlogger_export_pbrowser'] == '[[0, (("input_field_list", ["DO.mg/l;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), )]]'
        assert mock_ms.settingsdict['fieldlogger_export_pgroups'] == '[[0, (("input_field_group_list", ["DO.mg/l;numberDecimal|numberSigned; ", "comment;text;Obsid related comment"], ), ("location_suffix", "2766", ), ("sublocation_suffix", "level", ), )], [1, (("input_field_group_list", ["comment;text;Obsid related comment"], ), ("location_suffix", "1234", ), ("sublocation_suffix", "comment", ), )]]'

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_create_export_printlist_correct_order(mock_MessagebarAndLog):
        latlons = {'1': ('lat1', 'lon1'), '2': ('lat2', 'lon2'), '4': ('lat4', 'lon4')}
        tables_columns = OrderedDict([('testtable', ('col1', 'col2'))])

        stored_settings = [(0, (('input_field_group_list', ['par4;type1;hint1', 'par1;type1;hint1']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'), ('location_suffix', 'proj2')))]


        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['1', '4'])
        parameter_groups[1]._obsid_list.paste_data(['2', '3', '4'])

        printlist = ExportToFieldLogger.create_export_printlist(parameter_groups, latlons)
        test_string = create_test_string(printlist)
        reference_string = '[NAME;INPUTTYPE;HINT, par4;type1;hint1 , par1;type1;hint1 , par2;type2;hint2 , NAME;SUBNAME;LAT;LON;INPUTFIELD, 1.proj;1.proj.group;lat1;lon1;par4|par1, 2.proj2;2.proj2.group;lat2;lon2;par2, 4.proj;4.proj.group;lat4;lon4;par4|par1, 4.proj2;4.proj2.group;lat4;lon4;par2]'
        assert reference_string == test_string

    @staticmethod
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.get_save_file_name_no_extension')
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_write_to_file(mock_MessagebarAndLog, mock_get_save_file_name_no_extension):
        lines = (
                    "NAME;INPUTTYPE;HINT",
                    "Value;numberDecimal|numberSigned;in m to top of tube",
                    "Comment;text;make comment...",
                    "NAME;SUBNAME;LAT;LON;INPUTFIELD",
                    "Location1;Location1_1;60.56309363068154;15.494655445218088;Value|Comment",
                    "Location2;Location2_1;60.532112200075446;15.509033761918545;Value|Comment")



        with common_utils.tempinput('', 'utf-8') as testfile:
            mock_get_save_file_name_no_extension.return_value = testfile

            export_fieldlogger.ExportToFieldLogger.write_to_file('\n'.join(lines))

        with open(testfile, 'r') as f:
            result_lines = [row.rstrip('\n') for row in f]

        assert tuple(lines) == tuple(result_lines)

    @mock.patch('midvatten.tools.export_fieldlogger.db_utils.tables_columns')
    @mock.patch('midvatten.tools.export_fieldlogger.ExportToFieldLogger.write_to_file')
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_laton_from_vectorlayer(self, mock_tables_columns, mock_write_to_file, mock_MessagebarAndLog):
        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {}

        mock_tables_columns.return_value = {}
        _fields = [QgsField('id', QVariant.Int, QVariant.typeToName(QVariant.Int)),
                   QgsField('obsid', QVariant.String, QVariant.typeToName(QVariant.String))]
        data = [[1, 'obsid1'], [2, 'obsid2'], [3, 'obsid3']]
        geometries = [QgsGeometry.fromWkt('POINT(1000000.0 100000.0)'),
                      QgsGeometry.fromWkt('POINT(2000000.0 200000.0)'),
                      QgsGeometry.fromWkt('POINT(3000000.0 300000.0)')]

        self.vlayer = create_vectorlayer(_fields, data, geometries=geometries, geomtype='Point', crs=3006)
        #print(f"vlayer is {self.vlayer}")
        #QgsProject.instance().addMapLayer(self.vlayer)
        #mock_iface = QWidget()
        #mock_iface.legendInterface = mock.Mock()
        #mock_iface.legendInterface.return_value.layers.return_value = [vlayer]
        exporttofieldlogger = ExportToFieldLogger(None, mock_ms)

        stored_settings = [(0, (('input_field_group_list', ['par1;type1;hint1']), ('sublocation_suffix', 'group'),
                                ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['par2;type2;hint2']), ('sublocation_suffix', 'group'),
                                ('location_suffix', 'proj2')))]

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['obsid1', 'obsid2'])
        parameter_groups[1]._obsid_list.paste_data(['obsid3'])
        exporttofieldlogger.parameter_groups = parameter_groups
        exporttofieldlogger.obs_from_vlayer.setChecked(True)
        exporttofieldlogger.obslayer.vectorlayer_list.setCurrentIndex(0)

        exporttofieldlogger.export()

        #print("printlist" + str(mock_write_printlist_to_file.mock_calls))
        print("Prints")
        #maximum_test_precision = 8
        testlist = []
        for _call in mock_write_to_file.call_args_list:
            args = _call[0][0].split('\n')
            #print(str(args))
            for location_idx in range(len(args)):
                loc = args[location_idx]
                if location_idx in [4, 5, 6]:
                    #String 'obsid1.proj;obsid1.proj.group;0.9019366063889331;19.489297537299507;par1'
                    alist = loc.split(';')
                    for colnr in [2, 3]:
                        alist[colnr] = '{:.8f}'.format(float(alist[colnr]))
                    testlist.append(';'.join(alist))
                else:
                    testlist.append(loc)
        print("Test")
        print(str(testlist))

        # Full number of decimals
        """ref = ('NAME;INPUTTYPE;HINT', 
              'par1;type1;hint1 ', 
              'par2;type2;hint2 ', 
              'NAME;SUBNAME;LAT;LON;INPUTFIELD', 
              'obsid1.proj;obsid1.proj.group;0.9019366063889334;19.489297537299507;par1', 
              'obsid2.proj;obsid2.proj.group;1.7601631374427096;28.363010767336505;par1', 
              'obsid3.proj2;obsid3.proj2.group;2.5166567545976224;36.93072164080035;par2')"""

        # 6 decimals
        """ref = ('NAME;INPUTTYPE;HINT',
                                   'par1;type1;hint1 ',
                                   'par2;type2;hint2 ',
                                   'NAME;SUBNAME;LAT;LON;INPUTFIELD',
                                   'obsid1.proj;obsid1.proj.group;0.901936;19.489297;par1',
                                   'obsid2.proj;obsid2.proj.group;1.760163;28.363010;par1',
                                   'obsid3.proj2;obsid3.proj2.group;2.516656;36.930721;par2')"""

        # 8 decimals
        ref = ('NAME;INPUTTYPE;HINT',
               'par1;type1;hint1 ',
               'par2;type2;hint2 ',
               'NAME;SUBNAME;LAT;LON;INPUTFIELD',
               'obsid1.proj;obsid1.proj.group;0.90193661;19.48929754;par1',
               'obsid2.proj;obsid2.proj.group;1.76016314;28.36301077;par1',
               'obsid3.proj2;obsid3.proj2.group;2.51665675;36.93072164;par2')

        print("Ref")
        print(ref)
        assert tuple(testlist) == ref
        #assert False

    @mock.patch('midvatten.tools.export_fieldlogger.db_utils.tables_columns')
    @mock.patch('midvatten.tools.export_fieldlogger.ExportToFieldLogger.write_to_file')
    @mock.patch('midvatten.tools.export_fieldlogger.common_utils.MessagebarAndLog')
    def test_laton_from_vectorlayer_fieldform(self, mock_tables_columns, mock_write_printlist_to_file, mock_MessagebarAndLog):
        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {}

        mock_tables_columns.return_value = {}
        _fields = [QgsField('id', QVariant.Int, QVariant.typeToName(QVariant.Int)),
                   QgsField('obsid', QVariant.String, QVariant.typeToName(QVariant.String))]
        data = [[1, 'obsid1'], [2, 'obsid2'], [3, 'obsid3']]
        geometries = [QgsGeometry.fromWkt('POINT(1000000.0 100000.0)'),
                      QgsGeometry.fromWkt('POINT(2000000.0 200000.0)'),
                      QgsGeometry.fromWkt('POINT(3000000.0 300000.0)')]

        self.vlayer = create_vectorlayer(_fields, data, geometries=geometries, geomtype='Point', crs=3006)
        QgsProject.instance().addMapLayer(self.vlayer)
        #mock_iface = QWidget()
        #mock_iface.legendInterface = mock.Mock()
        #mock_iface.legendInterface.return_value.layers.return_value = [vlayer]
        exporttofieldlogger = ExportToFieldLogger(None, mock_ms)

        stored_settings = [(0, (('input_field_group_list', ['{"par1": {"type": "type1", "hint": "hint1"}}']), ('sublocation_suffix', 'group'),
                                ('location_suffix', 'proj'))),
                           (1, (('input_field_group_list', ['{"par2": {"type": "type2", "hint": "hint2"}}']), ('sublocation_suffix', 'group'),
                                ('location_suffix', 'proj2')))]

        parameter_groups = ExportToFieldLogger.create_parameter_groups_using_stored_settings(stored_settings, None)
        parameter_groups[0]._obsid_list.paste_data(['obsid1', 'obsid2'])
        parameter_groups[1]._obsid_list.paste_data(['obsid3'])
        exporttofieldlogger.parameter_groups = parameter_groups
        exporttofieldlogger.obs_from_vlayer.setChecked(True)
        exporttofieldlogger.obslayer.vectorlayer_list.setCurrentIndex(0)

        exporttofieldlogger.export_as_fieldform.setChecked(True)

        exporttofieldlogger.export()

        test = mock_write_printlist_to_file.call_args_list[0][0][0]

        ref__ = (
            {
                "settings": {
                    "use_standard_time": "YES"
                },
                "inputfields": {
                    "value": {
                        "type": "number"
                    },
                    "comment": {
                        "type": "text",
                        "hint": "place a comment"
                    },
                    "reliable": {
                        "type": "choice",
                        "hint": "is this measurement reliable?",
                        "options": [
                            "yes",
                            "no"
                        ]
                    },
                    "photo": {
                        "type": "photo",
                        "hint": "take a picture"
                    }
                },
                "groups": {
                    "group_1": {
                        "name": "Group 1",
                        "color": "orange"
                    },
                    "group_2": {
                        "name": "Group 2",
                        "color": "blue"
                    }
                },
                "locations": {
                    "location_1": {
                        "lat": 51.9,
                        "lon": 6.5,
                        "group": "group_1",
                        "sublocations": {
                            "loc_1_1": {
                                "inputfields": [
                                    "value",
                                    "reliable",
                                    "comment"
                                ],
                                "photo": "loc_1.png",
                                "properties": {
                                    "surface level": "20.74",
                                    "filter level": 18.64
                                }
                            },
                            "loc_1_2": {
                                "inputfields": [
                                    "value",
                                    "reliable",
                                    "comment"
                                ],
                                "photo": "loc_1.png",
                                "properties": {
                                    "surface level": "20.74",
                                    "filter level": 10.0
                                }
                            }
                        }
                    },
                    "location_2": {
                        "lat": 52.1,
                        "lon": 6.3,
                        "group": "group_2",
                        "sublocations": {
                            "loc_2_1": {
                                "inputfields": [
                                    "value",
                                    "photo"
                                ],
                                "photo": "loc_2.pdf",
                                "properties": {
                                    "surface level": "10.41",
                                    "filter level": 8.26
                                }
                            }
                        }
                    }
                }
            }




        )



        # 8 decimals
        #ref = """{"inputfields": {"par1": {"type": "type1", "hint": "hint1"}, "par2": {"type": "type2", "hint": "hint2"}}, "locations": {"obsid1.proj": {"lat": 0.9019366063889331, "lon": 19.489297537299507, "sublocations": {"obsid1.proj.group": {"inputfields": ["par1"]}}}, "obsid2.proj": {"lat": 1.7601631374427096, "lon": 28.3630107673365, "sublocations": {"obsid2.proj.group": {"inputfields": ["par1"]}}}, "obsid3.proj2": {"lat": 2.516656754597623, "lon": 36.93072164080036, "sublocations": {"obsid3.proj2.group": {"inputfields": ["par2"]}}}}}"""
        ref = """{
    "inputfields": {
        "par1": {
            "type": "type1",
            "hint": "hint1"
        },
        "par2": {
            "type": "type2",
            "hint": "hint2"
        }
    },
    "locations": {
        "obsid1.proj": {
            "lat": 0.9019366063889331,
            "lon": 19.489297537299507,
            "sublocations": {
                "obsid1.proj.group": {
                    "inputfields": [
                        "par1"
                    ]
                }
            }
        },
        "obsid2.proj": {
            "lat": 1.7601631374427096,
            "lon": 28.3630107673365,
            "sublocations": {
                "obsid2.proj.group": {
                    "inputfields": [
                        "par1"
                    ]
                }
            }
        },
        "obsid3.proj2": {
            "lat": 2.516656754597623,
            "lon": 36.93072164080036,
            "sublocations": {
                "obsid3.proj2.group": {
                    "inputfields": [
                        "par2"
                    ]
                }
            }
        }
    }
}"""
        print("Ref")
        print(ref)
        print(f"Test")
        print(test)
        assert test == ref
        #assert False