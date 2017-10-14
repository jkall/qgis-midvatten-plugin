# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  measurements.

 This part is to a big extent based on QSpatialite plugin.
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
#

import utils_for_tests
import midvatten_utils as utils
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from functools import partial
from mock import mock_open, patch
from multiprocessing import Pool, Process
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
from midvatten.midvatten import midvatten
import os
from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI, QgsVectorLayer, QgsGeometry, QgsFeature, QgsApplication
import qgis
import piper
from PyQt4 import QtCore
TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)


class _TestPiperPlotDb(object):
    """ The test doesn't go through the whole section plot unfortunately
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    crs_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.midvatten.ms.settingsareloaded = True

    def tearDown(self):
        #Delete database
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass

    @mock.patch('piper.plt.show')
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_piper_plot_default_settings(self, mock_qgsproject_instance, mock_showplot):
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT
        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {r"""piper_cl""": '',
                                r"""piper_hco3""": '',
                                r"""piper_so4""": '',
                                r"""piper_na""": '',
                                r"""piper_k""": '',
                                r"""piper_ca""": '',
                                r"""piper_mg""": ''}
        mock_active_layer = mock.MagicMock()
        piperplot = piper.PiperPlot(mock_ms, mock_active_layer)
        piperplot.create_parameter_selection()

        test = utils.anything_to_string_representation(piperplot.ParameterList)
        ref = '''["(lower(parameter) like '%klorid%' or lower(parameter) like '%chloride%')", "(lower(parameter) like '%alkalinitet%' or lower(parameter) like '%alcalinity%')", "(lower(parameter) like '%sulfat%' or lower(parameter) like '%sulphat%')", "(lower(parameter) like '%natrium%')", "(lower(parameter) like '%kalium%' or lower(parameter) like '%potassium%')", "(lower(parameter) like '%kalcium%' or lower(parameter) like '%calcium%')", "(lower(parameter) like '%magnesium%')"]'''
        assert test == ref

    @mock.patch('piper.plt.show')
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_piper_plot_user_chosen_settings(self, mock_qgsproject_instance, mock_showplot):
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT
        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {r"""piper_cl""": 'cl',
                                r"""piper_hco3""": 'hco3',
                                r"""piper_so4""": 'so4',
                                r"""piper_na""": 'na',
                                r"""piper_k""": 'k',
                                r"""piper_ca""": 'ca',
                                r"""piper_mg""": 'mg'}
        mock_active_layer = mock.MagicMock()
        piperplot = piper.PiperPlot(mock_ms, mock_active_layer)
        piperplot.create_parameter_selection()

        test = utils.anything_to_string_representation(piperplot.ParameterList)
        ref = '''["parameter = 'cl'", "parameter = 'hco3'", "parameter = 'so4'", "parameter = 'na'", "parameter = 'k'", "parameter = 'ca'", "parameter = 'mg'"]'''
        assert test == ref

