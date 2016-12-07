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
from mocks_for_tests import MockUsingReturnValue, MockQgsProjectInstance, DummyInterface2, mock_answer, MockQgisUtilsIface, MockReturnUsingDictIn
import midvatten_utils as utils
from nose.tools import raises
from mock import MagicMock
import mock
from utils_for_tests import dict_to_sorted_list
from definitions import midvatten_defs
from nose.plugins.skip import SkipTest
import os
import midvatten

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH], ('Midvatten', 'locale'): [u'sv_SE']}[(x, y)]


class TestDefsFunctions():
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)


    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH
        mock_qgsproject_instance.return_value.instance.readEntry.return_value = [u'en_US']

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten.midvatten(self.iface)

        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        self.midvatten.new_db()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_tables_columns(self, mock_iface):
        res = midvatten_defs.tables_columns()
        assert res
        assert isinstance(res, dict)
        for k, v in res.iteritems():
            assert isinstance(k, unicode)
            assert isinstance(v, (tuple, list))
            for x in v:
                assert isinstance(x, (tuple, list))
                assert x



