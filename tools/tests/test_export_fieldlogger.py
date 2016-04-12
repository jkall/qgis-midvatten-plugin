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
    qual_params = MockUsingReturnValue(((u'redoxpotential', (u'mV',)), (u'syre', (u'mg/L',)), (u'pH', (u'',))))
    flow_params = MockUsingReturnValue(((u'Momflow', (u'l/s',)), (u'Accvol', (u'm3',))))
    sample_params = MockUsingReturnValue(((u'turbiditet', (u'FNU',)),))
    the_obsids = MockUsingReturnValue((u'Rb1301', u'Rb1302'))
    the_latlons = MockUsingReturnValue({u'Rb1301': (60.0, 10.0), u'Rb1302': (50.0, 4.0)})
    selected_obsids_from_map = MockUsingReturnValue((u'Rb1302',))
    empty_dict = MockUsingReturnValue({})

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
        assert parameters == [(u'flow', u'Accvol', u'm3'), (u'flow', u'Momflow', u'l/s'), (u'flow', u'comment', u'make comment...'), (u'level', u'comment', u'make comment...'), (u'level', u'meas', u'm'), (u'quality', u'comment', u'make comment...'), (u'quality', u'pH', u'pH'), (u'quality', u'redoxpotential', u'mV'), (u'quality', u'syre', u'mg/L'), (u'sample', u'comment', u'make comment...'), (u'sample', u'turbiditet', u'FNU')]

    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_all_momflow(self):
        self.export_fieldlogger_obj.select_all(u'flow.Momflow', True)
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == [u'FileVersion 1;2', u'NAME;INPUTTYPE;HINT', u'flow.Momflow;numberDecimal|numberSigned;l/s', u'flow.comment;text;make comment...', u'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1301;Rb1301.flow;60.0;10.0;flow.comment|flow.Momflow', u'Rb1302;Rb1302.flow;50.0;4.0;flow.comment|flow.Momflow']

    @mock.patch('export_fieldlogger.utils.get_selected_features_as_tuple', selected_obsids_from_map.get_v)
    @mock.patch('export_fieldlogger.utils.get_latlon_for_all_obsids', the_latlons.get_v)
    def test_select_from_map_click(self):
        self.export_fieldlogger_obj.select_from_map(u'quality.syre')
        printlist = self.export_fieldlogger_obj.create_export_printlist()
        assert printlist == [u'FileVersion 1;2', u'NAME;INPUTTYPE;HINT', u'quality.syre;numberDecimal|numberSigned;mg/L', u'quality.comment;text;make comment...', u'NAME;SUBNAME;LAT;LON;INPUTFIELD', u'Rb1302;Rb1302.quality;50.0;4.0;quality.syre|quality.comment']

    def tearDown(self):
        self.iface = None
        self.export_fieldlogger_obj = None
        pass
