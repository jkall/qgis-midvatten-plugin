# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles shared gui tools

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-11-27
        copyright            : (C) 2016 by HenrikSpa (and joskal)
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
import copy

from midvatten_utils import returnunicode
from tools.date_utils import datestring_to_date


class SplitterWithHandel(PyQt4.QtGui.QSplitter):
    """
    Creates a splitter with a handle

    Using code from http://stackoverflow.com/questions/2545577/qsplitter-becoming-undistinguishable-between-qwidget-and-qtabwidget
    """
    def __init__(self, *args, **kwargs):
        super(SplitterWithHandel, self).__init__(*args, **kwargs)
        handle = self.handle(1)
        self.setHandleWidth(10)
        layout = PyQt4.QtGui.QVBoxLayout(handle)
        layout.setSpacing(0)
        layout.setMargin(0)
        line = PyQt4.QtGui.QFrame(handle)
        line.setFrameShape(PyQt4.QtGui.QFrame.HLine)
        line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken)
        layout.addWidget(line)


class RowEntry(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QHBoxLayout()
        self.widget.setLayout(self.layout)


class VRowEntry(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QVBoxLayout()
        self.widget.setLayout(self.layout)


class RowEntryGrid(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QGridLayout()
        self.widget.setLayout(self.layout)


class ExtendedQPlainTextEdit(PyQt4.QtGui.QPlainTextEdit):
    """

    """
    def __init__(self, keep_sorted=False, *args, **kwargs):
        super(ExtendedQPlainTextEdit, self).__init__(*args, **kwargs)
        self.keep_sorted = keep_sorted

    def paste_data(self, paste_list):
        #Use lists to keep the data ordering (the reason set() is not used
        old_text = self.get_all_data()
        new_items = []
        for alist in [old_text, paste_list]:
            for x in alist:
                if x:
                    if x not in new_items:
                        new_items.append(returnunicode(x))

        self.clear()
        if self.keep_sorted:
            self.setPlainText(u'\n'.join(sorted(new_items)))
        else:
            self.setPlainText(u'\n'.join(new_items))

    def get_all_data(self):
        if self.toPlainText():
            return returnunicode(self.toPlainText()).replace(u'\r', u'').split(u'\n')
        else:
            return []


def get_line():
    line = PyQt4.QtGui.QFrame()
    line.setGeometry(PyQt4.QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(PyQt4.QtGui.QFrame.HLine)
    line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken)
    return line


class DateTimeFilter(RowEntry):
    def __init__(self):
        super(DateTimeFilter, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Import data from: ')
        self.from_datetimeedit = PyQt4.QtGui.QDateTimeEdit(datestring_to_date(u'1900-01-01 00:00:00'))
        self.from_datetimeedit.setDisplayFormat(u'yyyy-MM-dd hh-mm-ss')
        self.label_to = PyQt4.QtGui.QLabel(u'to: ')
        self.to_datetimeedit = PyQt4.QtGui.QDateTimeEdit(datestring_to_date(u'2099-12-31 23:59:59'))
        self.to_datetimeedit.setDisplayFormat(u'yyyy-MM-dd hh-mm-ss')
        #self.import_after_last_date = PyQt4.QtGui.QCheckBox(u"Import after latest date in database for each obsid")
        for widget in [self.label, self.from_datetimeedit, self.label_to, self.to_datetimeedit]:
            self.layout.addWidget(widget)
        self.layout.addStretch()

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        _from = self.from_datetimeedit.dateTime().toPyDateTime()
        _to = self.to_datetimeedit.dateTime().toPyDateTime()
        if not _from and not _to:
            return observation
        if _from and _to:
            if _from < observation[u'date_time'] < _to:
                return observation
        elif _from:
            if _from < observation[u'date_time']:
                return observation
        elif _to:
            if observation[u'date_time'] < _to:
                return observation
        return None


    @property
    def from_date(self):
        return self.from_datetimeedit.dateTime().toPyDateTime()

    @from_date.setter
    def from_date(self, value):
        self.from_datetimeedit.setDateTime(datestring_to_date(value))

    @property
    def to_date(self):
        return self.to_datetimeedit.dateTime().toPyDateTime()

    @to_date.setter
    def to_date(self, value):
        self.to_datetimeedit.setDateTime(datestring_to_date(value))