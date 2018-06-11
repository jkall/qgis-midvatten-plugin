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
from __future__ import absolute_import
from builtins import object
import qgis.PyQt
import copy
from qgis.PyQt.QtCore import QCoreApplication

from .date_utils import datestring_to_date
import midvatten_utils as utils
import db_utils
from .midvatten_utils import returnunicode as ru


class SplitterWithHandel(qgis.PyQt.QtGui.QSplitter):
    """
    Creates a splitter with a handle

    Using code from http://stackoverflow.com/questions/2545577/qsplitter-becoming-undistinguishable-between-qwidget-and-qtabwidget
    """
    def __init__(self, *args, **kwargs):
        super(SplitterWithHandel, self).__init__(*args, **kwargs)
        handle = self.handle(1)
        self.setHandleWidth(10)
        layout = qgis.PyQt.QtGui.QVBoxLayout(handle)
        layout.setSpacing(0)
        layout.setMargin(0)
        line = qgis.PyQt.QtGui.QFrame(handle)
        line.setFrameShape(qgis.PyQt.QtGui.QFrame.HLine)
        line.setFrameShadow(qgis.PyQt.QtGui.QFrame.Sunken)
        layout.addWidget(line)


class RowEntry(object):
    def __init__(self):
        self.widget = qgis.PyQt.QtGui.QWidget()
        self.layout = qgis.PyQt.QtGui.QHBoxLayout()
        self.widget.setLayout(self.layout)


class VRowEntry(object):
    def __init__(self):
        self.widget = qgis.PyQt.QtGui.QWidget()
        self.layout = qgis.PyQt.QtGui.QVBoxLayout()
        self.widget.setLayout(self.layout)


class RowEntryGrid(object):
    def __init__(self):
        self.widget = qgis.PyQt.QtGui.QWidget()
        self.layout = qgis.PyQt.QtGui.QGridLayout()
        self.widget.setLayout(self.layout)


class ExtendedQPlainTextEdit(qgis.PyQt.QtGui.QPlainTextEdit):
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
                        new_items.append(ru(x))

        self.clear()
        if self.keep_sorted:
            self.setPlainText(u'\n'.join(sorted(new_items)))
        else:
            self.setPlainText(u'\n'.join(new_items))

    def get_all_data(self):
        if self.toPlainText():
            return ru(self.toPlainText()).replace(u'\r', u'').split(u'\n')
        else:
            return []


def get_line():
    line = qgis.PyQt.QtGui.QFrame()
    line.setGeometry(qgis.PyQt.QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(qgis.PyQt.QtGui.QFrame.HLine)
    line.setFrameShadow(qgis.PyQt.QtGui.QFrame.Sunken)
    return line


class DateTimeFilter(RowEntry):
    def __init__(self, calendar=False, stretch=True):
        super(DateTimeFilter, self).__init__()
        self.label = qgis.PyQt.QtGui.QLabel(ru(QCoreApplication.translate(u'DateTimeFilter', u'Import data from: ')))
        self.from_datetimeedit = qgis.PyQt.QtGui.QDateTimeEdit(datestring_to_date(u'1901-01-01 00:00:00'))
        self.from_datetimeedit.setDisplayFormat(u'yyyy-MM-dd hh:mm:ss')
        self.from_datetimeedit.setMinimumWidth(180)

        self.label_to = qgis.PyQt.QtGui.QLabel(ru(QCoreApplication.translate(u'DateTimeFilter', u'to: ')))
        self.to_datetimeedit = qgis.PyQt.QtGui.QDateTimeEdit(datestring_to_date(u'2099-12-31 23:59:59'))
        self.to_datetimeedit.setDisplayFormat(u'yyyy-MM-dd hh:mm:ss')
        self.to_datetimeedit.setMinimumWidth(180)

        if calendar:
            self.from_datetimeedit.setCalendarPopup(True)
            self.to_datetimeedit.setCalendarPopup(True)
        #self.import_after_last_date = PyQt4.QtGui.QCheckBox(u"Import after latest date in database for each obsid")
        for widget in [self.label, self.from_datetimeedit, self.label_to, self.to_datetimeedit]:
            self.layout.addWidget(widget)
        if stretch:
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


def set_combobox(combobox, value, add_if_not_exists=True):
    index = combobox.findText(ru(value))
    if index != -1:
        combobox.setCurrentIndex(index)
    else:
        if add_if_not_exists:
            combobox.addItem(ru(value))
            index = combobox.findText(ru(value))
            combobox.setCurrentIndex(index)


class DistinctValuesBrowser(VRowEntry):
    def __init__(self, tables_columns, connect):
        super(DistinctValuesBrowser, self).__init__()

        self.browser_label = qgis.PyQt.QtGui.QLabel(ru(QCoreApplication.translate(u'DistinctValuesBrowser', u'DB browser:')))
        self.table_label = qgis.PyQt.QtGui.QLabel(ru(QCoreApplication.translate(u'DistinctValuesBrowser', u'Table')))
        self._table_list = qgis.PyQt.QtGui.QComboBox()
        self.column_label = qgis.PyQt.QtGui.QLabel(ru(QCoreApplication.translate(u'DistinctValuesBrowser', u'Column')))
        self._column_list = qgis.PyQt.QtGui.QComboBox()
        self.distinct_value_label = qgis.PyQt.QtGui.QLabel(ru(QCoreApplication.translate(u'DistinctValuesBrowser', u'Distinct values')))
        self._distinct_value = qgis.PyQt.QtGui.QComboBox()
        self._distinct_value.setEditable(True)


        self._table_list.addItem(u'')
        self._table_list.addItems(sorted(tables_columns.keys()))

        connect(self._table_list, qgis.PyQt.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._column_list, tables_columns.get(self.table_list, [])))
        connect(self._column_list, qgis.PyQt.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._distinct_value, self.get_distinct_values(self.table_list, self.column_list)))

        for widget in [self.browser_label, self.table_label, self._table_list,
                       self.column_label, self._column_list, self.distinct_value_label,
                       self._distinct_value]:
            self.layout.addWidget(widget)

    @staticmethod
    def get_distinct_values(tablename, columnname):
        if not tablename or not columnname:
            return []
        sql = '''SELECT DISTINCT %s FROM %s''' % (columnname, tablename)
        connection_ok, result = db_utils.sql_load_fr_db(sql)

        if not connection_ok:
            utils.MessagebarAndLog.critical(
                bar_msg=utils.sql_failed_msg(),
                log_msg=ru(QCoreApplication.translate(u'DistinctValuesBrowser', u"""Cannot get data from sql %s"""))%ru(sql))
            return []

        values = [ru(col[0]) for col in result]
        return values

    @staticmethod
    def replace_items(combobox, items):
        items = sorted(items)
        combobox.clear()
        combobox.addItem(u'')
        try:
            combobox.addItems(items)
        except TypeError:
            for item in items:
                combobox.addItem(item)

    @property
    def table_list(self):
        return ru(self._table_list.currentText())

    @table_list.setter
    def table_list(self, value):
        set_combobox(self._table_list, value)

    @property
    def column_list(self):
        return ru(self._column_list.currentText())

    @column_list.setter
    def column_list(self, value):
        set_combobox(self._column_list, value)

    @property
    def distinct_value(self):
        return ru(self._distinct_value.currentText())

    @distinct_value.setter
    def distinct_value(self, value):
        set_combobox(self._distinct_value, value)