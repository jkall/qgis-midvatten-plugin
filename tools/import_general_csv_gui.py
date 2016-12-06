# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of data to the database
  from the fieldlogger format.

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
import io
import os
import locale
import qgis.utils
import copy
from operator import itemgetter
from functools import partial

import definitions.midvatten_defs
import import_data_to_db
import copy
from collections import OrderedDict
import midvatten_utils as utils
from midvatten_utils import returnunicode
from definitions import midvatten_defs as defs
from date_utils import find_date_format, datestring_to_date, dateshift
from datetime import datetime

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4

import_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]

class GeneralCsvImportGui(PyQt4.QtGui.QMainWindow, import_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.table_chooser = None
        self.status = True

    def load_gui(self):
        tables_columns = defs.tables_columns()

        self.table_chooser = ImportTableChooser(tables_columns, self.connect, file_header=None)
        self.main_vertical_layout.addWidget(self.table_chooser.widget)
        self.add_line(self.main_vertical_layout)
        #General buttons
        self.select_file_button = PyQt4.QtGui.QPushButton(u'Select file')
        self.gridLayout_buttons.addWidget(self.select_file_button, 0, 0)
        self.connect(self.select_file_button, PyQt4.QtCore.SIGNAL("clicked()"), self.load_files)

        self.start_import_button = PyQt4.QtGui.QPushButton(u'Start import')
        self.gridLayout_buttons.addWidget(self.start_import_button, 1, 0)
        self.connect(self.start_import_button, PyQt4.QtCore.SIGNAL("clicked()"), self.start_import)

        self.gridLayout_buttons.setRowStretch(2, 1)

        self.show()

    def load_files(self):
        self.charset = utils.ask_for_charset()
        if not self.charset:
            return None
        filename = utils.select_files(only_one_file=True, extension="Comma or semicolon separated csv file (*.csv);;Comma or semicolon separated csv text file (*.txt);;Comma or semicolon separated file (*.*)")
        if not filename:
            return None
        if isinstance(filename, (list, tuple)):
            filename = filename[0]
        else:
            filename = filename
        self.filename = returnunicode(filename)
        self.table_chooser.file_header = self.get_header(self.filename, self.charset)

    @staticmethod
    def get_header(filename, charset):
        with io.open(filename, 'r', encoding=charset) as f:
            header = f.readline().rstrip(u'\r').rstrip(u'\n').rstrip(u'\r').rstrip(u'\n')
        delimiters = [u',', u';']
        tested_header = [len(header.split(delimiter)) for delimiter in delimiters]
        delimiter = delimiters[tested_header.index(max(tested_header))]
        header = header.split(delimiter)
        return header

    def start_import(self):
        translation_dict = self.get_translation_dict(self.table_chooser)
        importer = import_data_to_db.midv_data_importer()
        importer.csv_layer = importer.csv2qgsvectorlayer(self.filename)
        importer.general_csv_import(goal_table=self.table_chooser.import_method,
                                    column_header_translation_dict=translation_dict)
        PyQt4.QtGui.QApplication.restoreOverrideCursor()


    @staticmethod
    def get_translation_dict(table_chooser):
        translation_dict = table_chooser.get_translation_dict()

        if not isinstance(translation_dict, Cancel):
            utils.pop_up_info(str(translation_dict))


    def add_line(self, layout=None):
        """ just adds a line"""
        # horizontalLineWidget = PyQt4.QtGui.QWidget()
        # horizontalLineWidget.setFixedHeight(2)
        # horizontalLineWidget.setSizePolicy(PyQt4.QtGui.QSizePolicy.Expanding, PyQt4.QtGui.QSizePolicy.Fixed)
        # horizontalLineWidget.setStyleSheet(PyQt4.QtCore.QString("background-color: #c0c0c0;"));
        line = PyQt4.QtGui.QFrame()
        # line.setObjectName(QString::fromUtf8("line"));
        line.setGeometry(PyQt4.QtCore.QRect(320, 150, 118, 3))
        line.setFrameShape(PyQt4.QtGui.QFrame.HLine)
        line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken)
        if layout is None:
            self.add_row(line)
        else:
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


class ImportTableChooser(VRowEntry):
    def __init__(self, tables_columns, connect, file_header=None):
        super(ImportTableChooser, self).__init__()
        self.connect = connect
        self.tables_columns = tables_columns
        self.file_header = file_header
        self.columns_widgets = []
        self.columns = []

        chooser = RowEntry()

        self.label = PyQt4.QtGui.QLabel('Import to table')

        self.__import_method = PyQt4.QtGui.QComboBox()
        self.__import_method.addItem(u'')
        self.__import_method.addItems(tables_columns.keys())

        self.connect(self.__import_method, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.choose_method)

        for widget in [self.label, self.__import_method]:
            chooser.layout.addWidget(widget)

        self.layout.addWidget(chooser.widget)

        self.layout.addStretch() #insertStretch(-1, 0)

    def get_translation_dict(self):
        translation_dict = {}
        for column_entry in self.columns:
            file_column_name = column_entry.file_column_name
            if isinstance(file_column_name, Cancel):
                return file_column_name
            if file_column_name:
                translation_dict[file_column_name] = column_entry.db_column
        return translation_dict

    @property
    def import_method(self):
        return str(self.__import_method.currentText())

    @import_method.setter
    def import_method(self, value):
        index = self.__import_method.findText(utils.returnunicode(value))
        if index != -1:
            self.__import_method.setCurrentIndex(index)

    def choose_method(self):
        tables_columns = self.tables_columns
        file_header = self.file_header
        import_method_name = self.import_method

        if file_header is None:
            return None

        #Remove stretch
        self.layout.takeAt(-1)
        for widget in self.columns_widgets:
            try:
                widget.clear_widgets()
            except:
                pass
            try:
                self.layout.removeWidget(widget)
            except:
                pass
            try:
                widget.close()
            except:
                pass
        self.columns_widgets = []
        self.columns = []

        if not import_method_name:
            self.layout.addStretch()
            return None

        for index, tables_columns_info in enumerate(sorted(tables_columns[import_method_name], key=itemgetter(0))):
            column = ColumnEntry(tables_columns_info, file_header)
            self.layout.addWidget(column.widget)
            self.columns_widgets.append(column.widget)
            self.columns.append(column)

        self.layout.addStretch()


class ColumnEntry(RowEntry):
    def __init__(self, tables_columns_info, observation_columns):
        super(ColumnEntry, self).__init__()
        self.tables_columns_info = tables_columns_info

        self.db_column = tables_columns_info[1]
        column_type = tables_columns_info[2]
        self.notnull = int(tables_columns_info[3])
        pk = int(tables_columns_info[5])
        concatted_info = u', '.join([_x for _x in [column_type, u'not null' if self.notnull else False,
                                      u'primary key' if pk else False] if _x])
        label = PyQt4.QtGui.QLabel(u' '.join([u'Column ', self.db_column, u'({})'.format(concatted_info)]))

        self.combobox = PyQt4.QtGui.QComboBox()
        self.combobox.addItem(u'')
        self.combobox.addItems(sorted(observation_columns))

        self.layout.addWidget(label)
        self.layout.addWidget(self.combobox)

        self.widgets = [label, self.combobox]

    @property
    def file_column_name(self):
        selected = returnunicode(self.combobox.currentText())
        if self.notnull and not selected:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, the column ' + self.db_column + u' must have a value')
            return Cancel()
        else:
            return selected

    def clear_widgets(self):
        for widget in self.widgets:
            self.layout.removeWidget(widget)
            widget.close()


class Cancel(object):
    def __init__(self):
        pass




