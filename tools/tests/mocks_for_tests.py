# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin with mocks used for testing.

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
import mock
from PyQt4 import QtGui
from qgis.core import QgsMapLayerRegistry
from PyQt4.QtCore import QString


class MockUsingReturnValue(object):
    def __init__(self, v=None):
        self.v =  v
        self.args_called_with = []
    def get_v(self, *args, **kwargs):
        self.args_called_with.extend(args)
        self.args_called_with.extend(kwargs)
        return self.v


class MockReturnUsingDict(object):
    def __init__(self, adict, args_idx):
        self.adict = adict
        self.args_idx = args_idx
        self.args_called_with = []

    def get_v(self, *args, **kwargs):
        self.args_called_with.extend(args)
        self.args_called_with.extend(kwargs)

        if isinstance(self.args_idx, int):
            arg = args[self.args_idx]
        elif isinstance(self.args_idx, basestring):
            arg = kwargs[self.args_idx]

        return_value = self.adict.get(arg, None)
        return return_value


class MockReturnUsingDictIn(object):
    def __init__(self, adict, args_idx):
        self.adict = adict
        self.args_idx = args_idx
        self.args_called_with = []

    def get_v(self, *args, **kwargs):
        self.args_called_with.extend(args)
        self.args_called_with.extend(kwargs)
        return_value = None
        if isinstance(self.args_idx, int):
            for k, v in self.adict.iteritems():
                a = args[self.args_idx]
                if isinstance(a, QString):
                    a = str(a)
                if a.startswith(k):
                   return_value = v
        elif isinstance(self.args_idx, basestring):
            for k, v in self.adict.iteritems():
                if str(kwargs[self.args_idx]).startswith(k):
                   return_value = v
        if return_value == None:
            raise Exception("MockReturnUsingDictIn: return_value could not be set for: " + str(args) + ' ' + str(kwargs))
        return return_value


class MockNotFoundQuestion(object):
    def __init__(self, answer, value):
        self.value = value
        self.answer = answer


class MockQgisUtilsIface(object):
    """
    Usage:
    Put variable directly under class:
    mocked_iface = MockQgisUtilsIface()

    Add as patch before method:
    @mock.patch('qgis.utils.iface', mocked_iface)
    def ...

    Messages can be printed if needed:
    print(str(<classname>.mocked_iface.messagebar.messages))
    Where <classname> is the name of the current Test class
    """
    def __init__(self):
        self.messagebar = MessageBar()
    def activeLayer(self, *args, **kwargs):
        return None
    def messageBar(self, *args, **kwargs):
        return self.messagebar


class MessageBar(object):
    def __init__(self):
        self.messages = []
    def pushMessage(self, *args, **kwargs):
        self.messages.append([arg for arg in args])
        self.messages.append([arg for arg in kwargs])
        return None


class MockQgsProjectInstance(object):
    def __init__(self, entry=u''):
        self.entry = entry
    def readEntry(self, *args, **kwargs):
        return self.entry


class DummyInterface(object):
    def __init__(self):
        self.widget = QtGui.QWidget()
        self.mainwindow = QtGui.QMainWindow(self.widget)
    def __getattr__(self, *args, **kwargs):
        def dummy(*args, **kwargs):
            return self
        return dummy
    def return_none_method(self):
        return None
    def mainWindow(self):
        return self.mainwindow
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration
    def layers(self):
        # simulate iface.legendInterface().layers()
        return QgsMapLayerRegistry.instance().mapLayers().values()


class DummyInterface2(object):
    """ This should probably be used instead of DummyInterface
        Based on mock instad of an own type of object.

        Usage:
        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
    """
    def __init__(self):
        self.mock = mock.MagicMock()
        self.widget = QtGui.QWidget()
        self.mainwindow = QtGui.QMainWindow(self.widget)
        self.mock.mainWindow.return_value = self.mainwindow
        self.mock.layers.return_value = QgsMapLayerRegistry.instance().mapLayers().values()

def mock_answer(yes_or_no='yes'):
    ans = {'yes': 1, 'no': 0}
    answer_obj = MockUsingReturnValue()
    answer_obj.result = ans.get(yes_or_no, yes_or_no)
    answer = MockUsingReturnValue(answer_obj)
    return answer
