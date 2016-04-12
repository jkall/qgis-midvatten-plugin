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


class TestStandardParametersForWQuality():
    def test_standard_parameters_for_wquality_is_dict(self):
        assert isinstance(midvatten_defs.standard_parameters_for_wquality(), tuple)

    def test_standard_parameters_for_wquality_k_v_is_unicode(self):
        for k, v in midvatten_defs.standard_parameters_for_wquality():
            assert isinstance(k, unicode)
            assert isinstance(v, tuple)
            for x in v:
                assert isinstance(x, unicode)
            
class TestStandardParametersForWFlow():
    def test_standard_parameters_for_wflow_is_dict(self):
        assert isinstance(midvatten_defs.standard_parameters_for_wflow(), tuple)

    def test_standard_parameters_for_wflow_k_v_is_unicode(self):
        for k, v in midvatten_defs.standard_parameters_for_wflow():
            assert isinstance(k, unicode)
            assert isinstance(v, tuple)
            for x in v:
                assert isinstance(x, unicode)

class TestStandardParametersForWSamle():
    def test_standard_parameters_for_wsample_is_dict(self):
        assert isinstance(midvatten_defs.standard_parameters_for_wsample(), tuple)

    def test_standard_parameters_for_wsample_k_v_is_unicode(self):
        for k, v in midvatten_defs.standard_parameters_for_wsample():
            assert isinstance(k, unicode)
            assert isinstance(v, tuple)
            for x in v:
                assert isinstance(x, unicode)
