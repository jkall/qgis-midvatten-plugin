# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin with utilities used for testing.
 
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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
import qgis.core
import qgis.PyQt
import io
import os
from operator import itemgetter
from qgis.PyQt import QtCore
from collections import OrderedDict
from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QWidget, QDialog
import matplotlib.pyplot as plt
from qgis.core import QgsProject
import unittest
import qgis

import db_utils
import midvatten_utils as utils
import mock
from import_data_to_db import midv_data_importer
from midvatten import Midvatten
from qgis.PyQt.QtCore import QSettings

from mocks_for_tests import DummyInterface2



class test_qapplication_is_running(object):
    """ Tests that the QApplication is running
    """
    def test_iface(self):
        assert QgsApplication.instance() is not None


def dict_to_sorted_list(adict):
    """
    Creates a list of a dict of dicts
    :param adict: a dict that may contain more dicts
    :return:

    >>> dict_to_sorted_list({'a': {'o':{'d': 1, 'c': 2}, 'e': ['u']}, 't': (5, 6)})
    ['a', 'e', 'u', 'o', 'c', '2', 'd', '1', 't', '5', '6']
    >>> dict_to_sorted_list({'a': {'o':{'d': 1, 'c': 2}, 'e': ['u']}, 't': (5, {'k': 8, 'i': 9})})
    ['a', 'e', 'u', 'o', 'c', '2', 'd', '1', 't', '5', 'i', '9', 'k', '8']
    >>> dict_to_sorted_list({'a': {'o':{'d': 1, 'c': 2}, 'e': ['u']}, 't': (5, {'k': 8, 'i': (9, 29)})})
    ['a', 'e', 'u', 'o', 'c', '2', 'd', '1', 't', '5', 'i', '9', 29, 'k', '8']

    """
    result_list = []
    if isinstance(adict, dict):
        for k, v in sorted(adict.items()):
            result_list.extend(dict_to_sorted_list(k))
            result_list.extend(dict_to_sorted_list(v))
    elif isinstance(adict, list) or isinstance(adict, tuple):
        for k in adict:
            result_list.extend(dict_to_sorted_list(k))
    else:
        result_list.append(utils.returnunicode(adict)) #.encode('utf-8'))
    return result_list

def create_test_string(anything=None):
    r""" Turns anything into a string used for testing
    :param anything: just about anything
    :return: A unicode string
     >>> create_test_string('123')
     '123'
     >>> create_test_string([1, 2, 3])
     '[1, 2, 3]'
     >>> create_test_string({3: 'a', 2: 'b', 1: ('c', 'd')})
     '{1: (c, d), 2: b, 3: a}'
    """
    if isinstance(anything, dict):
        aunicode = ''.join(['{', ', '.join([': '.join([create_test_string(k), create_test_string(v)]) for k, v in sorted(anything.items())]), '}'])
    elif isinstance(anything, list):
        aunicode = ''.join(['[', ', '.join([create_test_string(x) for x in anything]), ']'])
    elif isinstance(anything, tuple):
        aunicode = ''.join(['(', ', '.join([create_test_string(x) for x in anything]), ')'])
    elif isinstance(anything, (str, float, int)):
        aunicode = utils.returnunicode(anything)
    elif isinstance(anything, qgis.PyQt.QtCore.QVariant):
        print("Was variant")
        aunicode = utils.returnunicode(anything.toString().data())
    else:
        aunicode = utils.returnunicode(str(anything))
    return aunicode


class ContextualStringIO(io.StringIO):
    """ Copied function from stackoverflow
    """
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close() # icecrime does it, so I guess I should, too
        return False # Indicate that we haven't handled the exception, if received


class MidvattenTestBase(object):
    def __init__(self):
        self.stop_show()

    def setUp(self):
        #QgsProject.instance().layerTreeRoot().removeAllChildren()
        #QgsProject.instance().removeAllMapLayers()
        QgsProject.instance().clear()
        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = Midvatten(self.iface)
        self.midvatten.initGui()
        self.midvatten.setup()

    def stop_show(self):
        """ Replace QWidget.show to stop the tests from producing a lot of dialogs.

        :return:
        """
        def show(self):
            #Do nothing
            pass
        QWidget.show = show
        QDialog.exec_ = show

    def tearDown(self):
        plt.close('all')
        #QgsProject.instance().layerTreeRoot().removeAllChildren()
        #QgsProject.instance().removeAllMapLayers()
        QgsProject.instance().clear()


class MidvattenTestSpatialiteNotCreated(MidvattenTestBase):
    def __init__(self):
        super().__init__()
        self.TEMP_DBPATH = '/tmp/tmp_midvatten_temp_db.sqlite'

    def setUp(self):
        super().setUp()
        try:
            os.remove(self.TEMP_DBPATH)
        except OSError:
            pass

    def tearDown(self):
        #Delete database
        try:
            os.remove(self.TEMP_DBPATH)
        except OSError:
            pass
        super().tearDown()


class MidvattenTestSpatialiteDbSv(MidvattenTestSpatialiteNotCreated):
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale):
        super().setUp()
        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')
        self.midvatten.new_db()


class MidvattenTestSpatialiteDbEn(MidvattenTestSpatialiteNotCreated):
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    @mock.patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale):
        super().setUp()
        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'en_US'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = (self.TEMP_DBPATH, 'Spatialite (*.sqlite)')
        self.midvatten.new_db()

class MidvattenTestSpatialiteDbSvImportInstance(MidvattenTestSpatialiteDbSv):
    def setUp(self):
        super().setUp()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        self.importinstance = None
        super().tearDown()


class MidvattenTestPostgisNotCreated(MidvattenTestBase):
    ALL_POSTGIS_SETTINGS = {'nosetests': {'estimatedMetadata': 'false', 'username': 'henrik3', 'publicOnly': 'false', 'service': '', 'database': 'nosetests', 'dontResolveType': 'false', 'saveUsername': 'true', 'sslmode': '1', 'host': '127.0.0.1', 'authcfg': '', 'geometryColumnsOnly': 'false', 'allowGeometrylessTables': 'false', 'password': '0000', 'savePassword': 'false', 'port': '5432'}}
    TEMP_DB_SETTINGS = {'postgis': {'connection': 'nosetests/127.0.0.1:5432/nosetests'}}

    def __init__(self):
        super().__init__()

    def setUp(self):
        super().setUp()
        QgsProject.instance().writeEntry("Midvatten", 'database', utils.anything_to_string_representation(MidvattenTestPostgisNotCreated.TEMP_DB_SETTINGS))
        qs = QSettings()
        for k, v in MidvattenTestPostgisNotCreated.ALL_POSTGIS_SETTINGS['nosetests'].items():
            qs.setValue('PostgreSQL/connections/{}/{}'.format('nosetests', k), v)
        #Clear the database
        try:
            db_utils.sql_alter_db('DROP SCHEMA public CASCADE;')
            db_utils.sql_alter_db('CREATE SCHEMA public;')
        except Exception as e:
            print("Failure resetting db: " + str(e))
    @mock.patch('midvatten_utils.MessagebarAndLog')
    def tearDown(self, mock_messagebar):
        #Clear the database
        try:
            db_utils.sql_alter_db('DROP SCHEMA public CASCADE;')
            db_utils.sql_alter_db('CREATE SCHEMA public;')
        except Exception as e:
            print("Failure resetting db: " + str(e))
            print("MidvattenTestPostgisNotCreated tearDownproblem: " + str(mock_messagebar.mock_calls))
        super().tearDown()


class MidvattenTestPostgisDbSv(MidvattenTestPostgisNotCreated):
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    def setUp(self, mock_crs_question, mock_answer_yes, mock_locale):
        super().setUp()
        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()


class MidvattenTestPostgisDbEn(MidvattenTestPostgisNotCreated):
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.qgis.PyQt.QtWidgets.QInputDialog.getInt')
    def setUp(self, mock_crs_question, mock_answer_yes, mock_locale):
        super().setUp()
        mock_locale.return_value.answer = 'ok'
        mock_locale.return_value.value = 'en_US'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()


class MidvattenTestPostgisDbSvImportInstance(MidvattenTestPostgisDbSv):
    def setUp(self):
        super().setUp()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        self.importinstance = None
        super().tearDown()


def foreign_key_test_from_exception(e, dbtype):
    if dbtype == 'spatialite':
        return str(e) == 'FOREIGN KEY constraint failed'
    elif dbtype == 'postgis':
        return 'is not present in table' in str(e)


def compare_strings(str1, str2):
    if str1 and not str2:
        return "Str2 was empty and str1 not."
    elif str2 and not str1:
        return "Str1 was empty and str2 not."

    def return20chars(astr, idx, numidx):
        min_idx = max(0, idx - numidx)
        max_idx = min(len(astr), idx + numidx)
        return astr[min_idx:max_idx]

    diff = False
    for idx in range(len(str1)):

        str1_t = return20chars(str1, idx, 40)
        str2_t = return20chars(str2, idx, 40)

        if str1[idx] != str2[idx]:
            #print(str(str1_t))
            #print(str(str2_t))
            diff = True
            break
    if diff:
        return "diff at idx {}, \nstr1:{}\nstr2:{}".format(str(idx), str1_t, str2_t)
    else:
        return 'The same'


def recursive_children(parent):
    try:
        children = parent.children()
    except AttributeError:
        children = []

    try:
        valid = parent.layer().isValid()
    except AttributeError:
        valid = ''

    return [parent.name(), valid, [recursive_children(child) for child in children]]