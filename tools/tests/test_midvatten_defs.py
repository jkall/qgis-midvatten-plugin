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
from definitions import midvatten_defs


class TestStandardParametersForWQualField():
    def test_standard_parameters_for_w_qual_field_is_dict(self):
        assert isinstance(midvatten_defs.standard_parameters_for_w_qual_field(), dict)

    def test_standard_parameters_for_w_qual_field_k_v_is_unicode(self):
        for k, v in midvatten_defs.standard_parameters_for_w_qual_field().iteritems():
            assert isinstance(k, unicode)
            assert isinstance(v, unicode)
            
class TestStandardParametersForWFlow():
    def test_standard_parameters_for_w_flow_is_dict(self):
        assert isinstance(midvatten_defs.standard_parameters_for_w_qual_field(), dict)

    def test_standard_parameters_for_w_flow_k_v_is_unicode(self):
        for k, v in midvatten_defs.standard_parameters_for_w_qual_field().iteritems():
            assert isinstance(k, unicode)
            assert isinstance(v, unicode)
