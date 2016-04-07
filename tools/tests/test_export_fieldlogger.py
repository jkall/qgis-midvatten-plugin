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
from utils_for_tests import init_test, DummyInterface
from PyQt4 import QtCore, QtGui, QtTest
from export_fieldlogger import ExportToFieldLogger
from mocks_for_tests import MockUsingReturnValue
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
from utils_for_tests import dict_to_sorted_list

app = QtGui.QApplication([])

class test_qapplication_is_running():
    """ Tests that the QApplication is running
    """
    def setUp(self):
        self.iface = DummyInterface()

    def tearDown(self):
        pass

    def test_iface(self):
        iface = self.iface
        assert QgsApplication.instance() is not None


class TestExportFieldlogger():
    qual_params = MockUsingReturnValue({u'redoxpotential': (u'mV',), u'syre': (u'mg/L',), u'pH': (u'',)})
    flow_params = MockUsingReturnValue({u'Momflow': (u'l/s',), u'Accvol': (u'm3'),})
    the_obsids = MockUsingReturnValue((u'Rb1301', u'Rb1302'))
    the_latlons = MockUsingReturnValue({u'Rb1301': (60.0, 10.0), u'Rb1302': (50.0, 4.0)})
    selected_obsids_from_map = MockUsingReturnValue((u'Rb1302',))
    empty_dict = MockUsingReturnValue({})

    @mock.patch('export_fieldlogger.utils.get_qual_params_and_units', qual_params.get_v)
    @mock.patch('export_fieldlogger.utils.get_flow_params_and_units', flow_params.get_v)
    @mock.patch('export_fieldlogger.utils.get_all_obsids', the_obsids.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        widget = QtGui.QWidget()
        self.export_fieldlogger_obj = ExportToFieldLogger(widget)

    @mock.patch('export_fieldlogger.utils.get_qual_params_and_units', qual_params.get_v)
    @mock.patch('export_fieldlogger.utils.get_flow_params_and_units', flow_params.get_v)
    @mock.patch('export_fieldlogger.standard_parameters_for_w_flow', empty_dict.get_v)
    @mock.patch('export_fieldlogger.standard_parameters_for_w_qual_field', empty_dict.get_v)
    def test_create_parameters(self):
        parameters = [(parametername, parameter.hint) for types, parameterdict in sorted(self.export_fieldlogger_obj.create_parameters().iteritems()) for parametername, parameter in sorted(parameterdict.iteritems())]
        assert parameters == [(u'Accvol', u'm'), (u'Momflow', u'l/s'), ('comment', u'make comment...'), ('instrument', u'the measurement instrument id'), ('comment', u'make comment...'), ('meas', u'[m] from top of tube'), ('comment', u'make comment...'), ('flow_lpm', u'the water flow during water quality measurement'), ('instrument', u'the measurement instrument id'), (u'pH', u'pH'), (u'redoxpotential', u'mV'), (u'syre', u'mg/L')]

    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_all_momflow(self):
        self.export_fieldlogger_obj.select_all(u'flow.Momflow', True)
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == ['FileVersion 1;3', 'NAME;INPUTTYPE;HINT', u'flow.Momflow;numberDecimal|numberSigned;l/s', u'flow.comment;text;make comment...', u'flow.instrument;text;the measurement instrument id', 'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1301;Rb1301.flow;60.0;10.0;flow.comment|flow.instrument|flow.Momflow', u'Rb1302;Rb1302.flow;50.0;4.0;flow.comment|flow.instrument|flow.Momflow']

    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_all(self):
        self.export_fieldlogger_obj.select_all(u'flow.Momflow', True)
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == ['FileVersion 1;3', 'NAME;INPUTTYPE;HINT', u'flow.Momflow;numberDecimal|numberSigned;l/s', u'flow.comment;text;make comment...', u'flow.instrument;text;the measurement instrument id', 'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1301;Rb1301.flow;60.0;10.0;flow.comment|flow.instrument|flow.Momflow', u'Rb1302;Rb1302.flow;50.0;4.0;flow.comment|flow.instrument|flow.Momflow']

    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_all(self):
        self.export_fieldlogger_obj.select_all(u'flow.Momflow', True)
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == ['FileVersion 1;3', 'NAME;INPUTTYPE;HINT', u'flow.Momflow;numberDecimal|numberSigned;l/s', u'flow.comment;text;make comment...', u'flow.instrument;text;the measurement instrument id', 'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1301;Rb1301.flow;60.0;10.0;flow.comment|flow.instrument|flow.Momflow', u'Rb1302;Rb1302.flow;50.0;4.0;flow.comment|flow.instrument|flow.Momflow']

    @mock.patch('export_fieldlogger.utils.get_selected_features_as_tuple', selected_obsids_from_map.get_v)
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_from_map_click(self):
        self.export_fieldlogger_obj.select_from_map(u'quality.syre')
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == ['FileVersion 1;4', 'NAME;INPUTTYPE;HINT', u'quality.comment;text;make comment...', u'quality.flow_lpm;numberDecimal|numberSigned;the water flow during water quality measurement', u'quality.instrument;text;the measurement instrument id', u'quality.syre;numberDecimal|numberSigned;mg/L', 'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1302;Rb1302.quality;50.0;4.0;quality.syre|quality.instrument|quality.comment|quality.flow_lpm']

    def tearDown(self):
        pass
