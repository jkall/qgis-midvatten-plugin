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
from tools.tests.mocks_for_tests import DummyInterface
from PyQt4 import QtCore, QtGui, QtTest
from export_fieldlogger import ExportToFieldLogger
from mocks_for_tests import MockUsingReturnValue
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
from utils_for_tests import dict_to_sorted_list

class TestExportFieldlogger():
    qual_params = MockUsingReturnValue(((u'redoxpotential', (u'mV',)), (u'syre', (u'mg/L', u'%')), (u'pH', (u'',))))
    flow_params = MockUsingReturnValue(((u'Momflow', (u'l/s',)), (u'Accvol', (u'm3',))))
    sample_params = MockUsingReturnValue(((u'turbiditet', (u'FNU',)),))
    the_obsids = MockUsingReturnValue((u'Rb1301', u'Rb1302'))
    the_latlons = MockUsingReturnValue({u'Rb1301': (60.0, 10.0), u'Rb1302': (50.0, 4.0)})
    selected_obsids_from_map = MockUsingReturnValue((u'Rb1302',))
    empty_dict = MockUsingReturnValue({})
    importinstance = MockUsingReturnValue(MockUsingReturnValue(int))
    importinstance.get_v().parse_wells_file = lambda : {u'Rb1301': {u'level': [(u'comment', u''), (u'meas', u'm')], u'quality': [(u'comment', u''), (u'syre', u'mg/L'), (u'konduktivitet', u'µS/cm'), (u'redoxpotential', u'mV'), (u'pH', u'')], u'sample': [(u'temperatur', u'grC'), (u'comment', u''), (u'turbiditet', u'FNU')]}, u'Rb1302': {u'quality': [(u'comment', u''), (u'syre', u'mg/L'), (u'konduktivitet', u'µS/cm'), (u'redoxpotential', u'mV'), (u'pH', u'')], u'sample': [(u'temperatur', u'grC'), (u'comment', u''), (u'turbiditet', u'FNU')]}}
    skip_popup = MockUsingReturnValue('')

    @mock.patch('export_fieldlogger.standard_parameters_for_wquality', qual_params.get_v)
    @mock.patch('export_fieldlogger.standard_parameters_for_wflow', flow_params.get_v)
    @mock.patch('export_fieldlogger.standard_parameters_for_wsample', sample_params.get_v)
    @mock.patch('export_fieldlogger.utils.get_all_obsids', the_obsids.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        widget = QtGui.QWidget()
        self.export_fieldlogger_obj = ExportToFieldLogger(widget)

    @mock.patch('export_fieldlogger.standard_parameters_for_wquality', qual_params.get_v)
    @mock.patch('export_fieldlogger.standard_parameters_for_wflow', flow_params.get_v)
    @mock.patch('export_fieldlogger.standard_parameters_for_wsample', sample_params.get_v)
    def test_create_parameters(self):
        parameters = [(types, parametername, parameter.hint) for types, parameterdict in sorted(self.export_fieldlogger_obj.create_parameters().iteritems()) for parametername, parameter in sorted(parameterdict.iteritems())]
        assert parameters == [(u'flow', u'Accvol', u'm3'), (u'flow', u'Momflow', u'l/s'), (u'flow', u'comment', u'make comment...'), (u'level', u'comment', u'make comment...'), (u'level', u'meas', u'm'), (u'quality', u'comment', u'make comment...'), (u'quality', u'pH', u'pH'), (u'quality', u'redoxpotential', u'mV'), (u'quality', u'syre.%', u'%'), (u'quality', u'syre.mg/L', u'mg/L'), (u'sample', u'comment', u'make comment...'), (u'sample', u'turbiditet', u'FNU')]

    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_all_momflow(self):
        self.export_fieldlogger_obj.select_all(u'flow.Momflow', True)
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == [u'FileVersion 1;2', u'NAME;INPUTTYPE;HINT', u'f.Momflow.l/s;numberDecimal|numberSigned;l/s', u'f.comment;text;make comment...', u'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1301;Rb1301.flow;60.0;10.0;f.Momflow.l/s|f.comment', u'Rb1302;Rb1302.flow;50.0;4.0;f.Momflow.l/s|f.comment']

    @mock.patch('export_fieldlogger.utils.get_selected_features_as_tuple', selected_obsids_from_map.get_v)
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_from_map_click(self):
        self.export_fieldlogger_obj.select_from_map(u'quality.syre.%')
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == [u'FileVersion 1;2', u'NAME;INPUTTYPE;HINT', u'q.syre.%;numberDecimal|numberSigned;%', u'q.comment;text;make comment...', u'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1302;Rb1302.quality;50.0;4.0;q.comment|q.syre.%']

    @mock.patch('export_fieldlogger.utils.get_selected_features_as_tuple', selected_obsids_from_map.get_v)
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_three_from_map_click(self):
        self.export_fieldlogger_obj.select_from_map(u'quality.syre.%')
        self.export_fieldlogger_obj.select_from_map(u'quality.syre.mg/L')
        self.export_fieldlogger_obj.select_from_map(u'sample.turbiditet')
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == [u'FileVersion 1;5', u'NAME;INPUTTYPE;HINT', u'q.syre.mg/L;numberDecimal|numberSigned;mg/L', u'q.syre.%;numberDecimal|numberSigned;%', u'q.comment;text;make comment...', u's.turbiditet.FNU;numberDecimal|numberSigned;FNU', u's.comment;text;make comment...', u'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1302;Rb1302.quality;50.0;4.0;q.comment|q.syre.mg/L|q.syre.%', u'Rb1302;Rb1302.sample;50.0;4.0;s.comment|s.turbiditet.FNU']

    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    @mock.patch('export_fieldlogger.midv_data_importer', importinstance.get_v)
    @mock.patch('import_data_to_db.utils.pop_up_info', skip_popup.get_v)
    def test_select_from_wells(self):
        self.export_fieldlogger_obj.select_from_wells()
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == [u'FileVersion 1;8', u'NAME;INPUTTYPE;HINT', u'l.meas.m;numberDecimal|numberSigned;m', u'l.comment;text;make comment...', u'q.redoxpotential.mV;numberDecimal|numberSigned;mV', u'q.syre.mg/L;numberDecimal|numberSigned;mg/L', u'q.pH;numberDecimal|numberSigned;pH', u'q.comment;text;make comment...', u's.turbiditet.FNU;numberDecimal|numberSigned;FNU', u's.comment;text;make comment...', u'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1301;Rb1301.level;60.0;10.0;l.comment|l.meas.m', u'Rb1301;Rb1301.quality;60.0;10.0;q.pH|q.syre.mg/L|q.redoxpotential.mV|q.comment', u'Rb1301;Rb1301.sample;60.0;10.0;s.comment|s.turbiditet.FNU', u'Rb1302;Rb1302.quality;50.0;4.0;q.pH|q.syre.mg/L|q.redoxpotential.mV|q.comment', u'Rb1302;Rb1302.sample;50.0;4.0;s.comment|s.turbiditet.FNU']

    def tearDown(self):
        self.iface = None
        self.export_fieldlogger_obj = None
        pass
