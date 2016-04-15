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
        arg = args[self.args_idx]
        return_value = self.adict[arg]
        return return_value

class MockReturnUsingDictIn(object):
    def __init__(self, adict, args_idx):
        self.adict = adict
        self.args_idx = args_idx
        self.args_called_with = []

    def get_v(self, *args, **kwargs):
        self.args_called_with.extend(args)
        self.args_called_with.extend(kwargs)
        for k, v in self.adict.iteritems():
            if args[self.args_idx].startswith(k):
               return_value = v
        return return_value


class MockNotFoundQuestion(object):
    def __init__(self, answer, value):
        self.value = value
        self.answer = answer

class MockQgisUtilsIface(object):
    def __init__(self):
        pass
    def activeLayer(self, *args, **kwargs):
        return None
    def messageBar(self, *args, **kwargs):
        messagebar = MessageBar()
        return MessageBar()

class MessageBar(object):
    def pushMessage(self, *args, **kwargs):
        return None

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