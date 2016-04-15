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
import io

from PyQt4 import QtCore
from qgis.core import QgsApplication

import midvatten_utils as utils
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


class ContextualStringIO(io.StringIO):
    """ Copied function from stackoverflow
    """
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close() # icecrime does it, so I guess I should, too
        return False # Indicate that we haven't handled the exception, if received

