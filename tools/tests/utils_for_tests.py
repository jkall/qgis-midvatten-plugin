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
import PyQt4
import io
import os
from PyQt4 import QtCore
from qgis.core import QgsApplication

import midvatten_utils as utils
import mock
from midvatten.midvatten import midvatten
from tools.tests.mocks_for_tests import DummyInterface


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
        for k, v in sorted(adict.iteritems()):
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

def create_test_string(anything):
    ur""" Turns anything into a string used for testing
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
        aunicode = u''.join([u'{', u', '.join([u': '.join([create_test_string(k), create_test_string(v)]) for k, v in sorted(anything.iteritems())]), u'}'])
    elif isinstance(anything, list):
        aunicode = u''.join([u'[', u', '.join([create_test_string(x) for x in anything]), u']'])
    elif isinstance(anything, tuple):
        aunicode = u''.join([u'(', u', '.join([create_test_string(x) for x in anything]), u')'])
    elif isinstance(anything, (basestring, float, int)):
        aunicode = utils.returnunicode(anything)
    elif isinstance(anything, PyQt4.QtCore.QVariant):
        print("Was varaint")
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
    def __init__(self):
        self.TEMP_DB_SETTINGS = {u'spatialite': {u'dbpath': u'/tmp/tmp_midvatten_temp_db.sqlite'}}
        self.TEMP_DBPATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
        self.SETTINGS_DATABASE = (u"{u'spatialite': {u'dbpath': u'/tmp/tmp_midvatten_temp_db.sqlite'}}", True)

    @mock.patch('midvatten_utils.QgsProject.instance')
    def setUp(self, mocked_instance):
        mocked_instance.return_value = utils.anything_to_string_representation(self.TEMP_DB_SETTINGS)

        self.iface = mock.MagicMock()
        self.midvatten = midvatten(self.iface)
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
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    @mock.patch('midvatten_utils.QgsProject.instance')
    def setUp(self, mocked_instance, mock_savefilename, mock_crs_question, mock_answer_yes, mock_locale, mock_iface):
        super(MidvattenTestSpatialiteDbSv, self).setUp()
        mocked_instance.return_value.readEntry.return_value = self.SETTINGS_DATABASE
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        mock_answer_yes.return_value.result = 1
        mock_crs_question.return_value.__getitem__.return_value = 3006
        mock_savefilename.return_value = self.TEMP_DBPATH
        self.midvatten.new_db()
