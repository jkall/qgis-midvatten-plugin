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
from qgis.PyQt import QtCore
from collections import OrderedDict
from qgis.core import QgsApplication

import db_utils
import midvatten_utils as utils
import mock
from import_data_to_db import midv_data_importer
from midvatten.midvatten import midvatten

from .mocks_for_tests import DummyInterface2
from tools.tests.mocks_for_tests import DummyInterface


class test_qapplication_is_running(object):
    """ Tests that the QApplication is running
    """
    def setUp(self):
        self.iface = DummyInterface()

    def tearDown(self):
        pass

    def test_iface(self):
        iface = self.iface
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
        result_list.append(utils.returnunicode(adict).encode('utf-8'))
    return result_list

def init_test():
    QgsApplication.setPrefixPath(r'/usr', True)
    app = QgsApplication.initQgis()
    QtCore.QCoreApplication.setOrganizationName('QGIS')
    QtCore.QCoreApplication.setApplicationName('QGIS2')
    return app

def create_test_string(anything=None):
    r""" Turns anything into a string used for testing
    :param anything: just about anything
    :return: A unicode string
     >>> create_test_string(u'123')
     u'123'
     >>> create_test_string([1, 2, 3])
     u'[1, 2, 3]'
     >>> create_test_string({3: 'a', 2: 'b', 1: ('c', 'd')})
     u'{1: (c, d), 2: b, 3: a}'
    """
    if isinstance(anything, dict):
        aunicode = u''.join([u'{', u', '.join([u': '.join([create_test_string(k), create_test_string(v)]) for k, v in sorted(anything.items())]), u'}'])
    elif isinstance(anything, list):
        aunicode = u''.join([u'[', u', '.join([create_test_string(x) for x in anything]), u']'])
    elif isinstance(anything, tuple):
        aunicode = u''.join([u'(', u', '.join([create_test_string(x) for x in anything]), u')'])
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


class MidvattenTestSpatialiteNotCreated(object):
    mock_instance_settings_database = mock.MagicMock()
    mock_instance_settings_database.return_value.readEntry.return_value = (u"{u'spatialite': {u'dbpath': u'/tmp/tmp_midvatten_temp_db.sqlite'}}", True)

    def __init__(self):
        self.TEMP_DB_SETTINGS = {u'spatialite': {u'dbpath': u'/tmp/tmp_midvatten_temp_db.sqlite'}}
        self.TEMP_DBPATH = u'/tmp/tmp_midvatten_temp_db.sqlite'

    @mock.patch('midvatten_utils.QgsProject.instance', mock_instance_settings_database)
    def setUp(self):

        #self.iface = mock.MagicMock()
        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        self.ms = mock.MagicMock()
        self.ms.settingsdict = OrderedDict()
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


class MidvattenTestSpatialiteDbSv(MidvattenTestSpatialiteNotCreated):
    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance', MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        super(MidvattenTestSpatialiteDbSv, self).setUp()
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = self.TEMP_DBPATH
        self.midvatten.new_db()

class MidvattenTestSpatialiteDbEn(MidvattenTestSpatialiteNotCreated):
    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtWidgets.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance', MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        super(MidvattenTestSpatialiteDbEn, self).setUp()
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'en_US'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = self.TEMP_DBPATH
        self.midvatten.new_db()

class MidvattenTestSpatialiteDbSvImportInstance(MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance', MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def setUp(self):
        super(MidvattenTestSpatialiteDbSvImportInstance, self).setUp()
        self.importinstance = midv_data_importer()


class MidvattenTestPostgisNotCreated(object):
    ALL_POSTGIS_SETTINGS = {u'nosetests': {u'estimatedMetadata': u'false', u'username': u'henrik3', u'publicOnly': u'false', u'service': u'', u'database': u'nosetests', u'dontResolveType': u'false', u'saveUsername': u'true', u'sslmode': u'1', u'host': u'127.0.0.1', u'authcfg': u'', u'geometryColumnsOnly': u'false', u'allowGeometrylessTables': u'false', u'password': u'0000', u'savePassword': u'false', u'port': u'5432'}}
    TEMP_DB_SETTINGS = {u'postgis': {u'connection': u'nosetests/127.0.0.1:5432/nosetests'}}
    SETTINGS_DATABASE = (utils.anything_to_string_representation(TEMP_DB_SETTINGS), True)

    mock_postgis_connections = mock.MagicMock()
    mock_postgis_connections.return_value = ALL_POSTGIS_SETTINGS

    mock_instance_settings_database = mock.MagicMock()
    mock_instance_settings_database.return_value.readEntry.return_value = SETTINGS_DATABASE

    def __init__(self):
        self.TEMP_DB_SETTINGS = MidvattenTestPostgisNotCreated.TEMP_DB_SETTINGS
        self.SETTINGS_DATABASE = MidvattenTestPostgisNotCreated.SETTINGS_DATABASE
        pass

    @mock.patch('db_utils.get_postgis_connections', mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_instance_settings_database)
    def setUp(self):
        #self.iface = mock.MagicMock()
        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)
        self.ms = mock.MagicMock()
        self.ms.settingsdict = OrderedDict()

        #Clear the database
        try:
            db_utils.sql_alter_db(u'DROP SCHEMA public CASCADE;')
            db_utils.sql_alter_db(u'CREATE SCHEMA public;')
        except Exception as e:
            print("Failure resetting db: " + str(e))

    @mock.patch('db_utils.get_postgis_connections', mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_instance_settings_database)
    @mock.patch('midvatten_utils.MessagebarAndLog')
    def tearDown(self, mock_messagebar):
        #mocked_instance.return_value.readEntry.return_value = self.SETTINGS_DATABASE
        #Clear the database
        try:
            db_utils.sql_alter_db(u'DROP SCHEMA public CASCADE;')
            db_utils.sql_alter_db(u'CREATE SCHEMA public;')
        except Exception as e:
            print("Failure resetting db: " + str(e))
            print("MidvattenTestPostgisNotCreated tearDownproblem: " + str(mock_messagebar.mock_calls))


class MidvattenTestPostgisDbSv(MidvattenTestPostgisNotCreated):
    @mock.patch('db_utils.get_postgis_connections', MidvattenTestPostgisNotCreated.mock_postgis_connections)
    @mock.patch('midvatten_utils.QgsProject.instance', MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('qgis.utils.iface')
    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    def setUp(self, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        super(MidvattenTestPostgisDbSv, self).setUp()
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        self.midvatten.new_postgis_db()


class MidvattenTestPostgisDbSvImportInstance(MidvattenTestPostgisDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance', MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def setUp(self):
        super(MidvattenTestPostgisDbSvImportInstance, self).setUp()
        self.importinstance = midv_data_importer()



def foreign_key_test_from_exception(e, dbtype):
    if dbtype == u'spatialite':
        return str(e) == u'FOREIGN KEY constraint failed'
    elif dbtype == u'postgis':
        return u'is not present in table' in str(e)
