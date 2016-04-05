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
from mocks_for_tests import mock_using_return_value
from nose.tools import raises
from mock import MagicMock
import mock

class test_dummyiface():
    def setUp(self):
        init_test()
        self.iface = DummyInterface()

    def tearDown(self):
        QgsApplication.exitQgis

    def test_iface(self):
        iface = self.iface


class TestCreateParameters():
    def setUp(self):
        app = init_test()
        #print("App: " + QgsApplication.showSettings())
        print("Application: " + str(app.instance()))
        self.iface = DummyInterface()
        widget = QtGui.QWidget()
        #self.export_fieldlogger = ExportToFieldLogger(widget)

    @mock.patch('midvatten_utils.get_flow_params_and_units', mock_using_return_value({'redoxpotential': 'mV'}).get_v)
    @mock.patch('midvatten_utils.get_flow_params_and_units', mock_using_return_value({'Momflow': 'l/s'}).get_v)
    def test_create_parameters(self):
#        #self.create_parameters()
#        print("App2: " + QgsApplication.showSettings())
        pass

    def tearDown(self):
        QgsApplication.exitQgis







#from export_fieldlogger import ExportToFieldLogger
#import utils_for_tests
#from nose.tools import raises
#from mock import MagicMock, patch
#
#class TestCreateParameters():
#    def setUp(self):
#        #@patch('utils.get_flow_params_and_units', mock_using_return_value({'redoxpotential': 'mV'}).get_v)
#        #@patch('utils.get_flow_params_and_units', mock_using_return_value({'Momflow': 'l/s'}).get_v)
#        self.export_fieldlogger = ExportToFieldLogger(None)
#
#    def test_create_parameters(self):
#        self.create_parameters()
