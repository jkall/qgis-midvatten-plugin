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
        self.setWindowTitle("Csv import")  # Set the title for the dialog
        self.table_chooser = None
        self.status = True

    def load_gui(self):
        tables_columns = {k: v for (k, v) in defs.tables_columns().iteritems() if not k.endswith(u'_geom')}
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
        delimiter = self.get_delimiter(self.filename, self.charset)
        self.file_data = self.file_to_list(self.filename, self.charset, delimiter)

        self.table_chooser.file_header = self.file_data[0]

    def file_to_list(self, filename, charset, delimiter):
        with io.open(filename, 'r', encoding=charset) as f:
            file_data = [rawrow.rstrip(u'\n').rstrip(u'\r').split(delimiter) for rawrow in f]
        return file_data

    @staticmethod
    def get_delimiter(filename, charset):
        with io.open(filename, 'r', encoding=charset) as f:
            header = f.readline().rstrip(u'\n').rstrip(u'\r')
        delimiters = [u',', u';']
        tested_header = [len(header.split(delimiter)) for delimiter in delimiters]
        delimiter = delimiters[tested_header.index(max(tested_header))]
        return delimiter

    def start_import(self):
        translation_dict = self.table_chooser.get_translation_dict()
        if isinstance(translation_dict, Cancel):
            return u'cancel'

        goal_table = self.table_chooser.import_method

        foreign_keys = utils.get_foreign_keys(goal_table)

        foreign_key_obsid_tables = [tname for tname, colnames in foreign_keys.iteritems() if colnames[0] == u'obsid']
        if len(foreign_key_obsid_tables) == 1:
            foreign_key_obsid_table = foreign_key_obsid_tables[0]
        else:
            foreign_key_obsid_table = False

        file_data = copy.deepcopy(self.file_data)

        for k, v in translation_dict.iteritems():
            if isinstance(v, Obsids_from_selection):
                if foreign_key_obsid_table:
                    selected = utils.get_selected_features_as_tuple(foreign_key_obsid_table)
                else:
                    #TODO: Must create a useful error here.
                    pass
                if not selected:
                    utils.MessagebarAndLog.critical(bar_msg=u'Import error, no obsid selected')
                try:
                    obsidindex = file_data[0].index(k)
                except ValueError:
                    file_data[0].append(k)
                    obsidindex = len(file_data[0]) - 1

                file_data = [row.insert(obsidindex, selected[0]) for row in self.file_data]
                translation_dict[k] = k

        importer = import_data_to_db.midv_data_importer()

        if foreign_key_obsid_table:
            file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', utils.get_all_obsids(foreign_key_obsid_table), try_capitalize=False)

        importer.send_file_data_to_importer(file_data, partial(importer.general_csv_import,
                                                               goal_table=goal_table,
                                                               column_header_translation_dict=translation_dict))

        PyQt4.QtGui.QApplication.restoreOverrideCursor()

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
            column = ColumnEntry(tables_columns_info, file_header, self.connect)
            self.layout.addWidget(column.widget)
            self.columns_widgets.append(column.widget)
            self.columns.append(column)

        self.layout.addStretch()


class ColumnEntry(RowEntry):
    def __init__(self, tables_columns_info, observation_columns, connect):
        super(ColumnEntry, self).__init__()
        self.tables_columns_info = tables_columns_info
        self.connect = connect

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

        if self.db_column == u'obsid':
            utils.pop_up_info(self.db_column)
            self.obsids_from_selection = PyQt4.QtGui.QCheckBox(u'Obsid from qgis selection')
            self.connect(self.obsids_from_selection, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.combobox.setEnabled(True if not self.obsids_from_selection.isChecked() else False))
            self.widgets = [label, self.obsids_from_selection, self.combobox]
            self.layout.addWidget(self.obsids_from_selection)
        else:
            self.widgets = [label, self.combobox]

        self.layout.addWidget(self.combobox)

    @property
    def file_column_name(self):
        if not self.combobox.isEnabled():
            return Obsids_from_selection()

        selected = returnunicode(self.combobox.currentText())
        if self.notnull and not selected:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, the column ' + self.db_column + u' must have a value')
            return Cancel()
        else:
            return selected

    @file_column_name.setter
    def file_column_name(self, value):
        index = self.combobox.findText(utils.returnunicode(value))
        if index != -1:
            self.combobox.setCurrentIndex(index)

    def clear_widgets(self):
        for widget in self.widgets:
            self.layout.removeWidget(widget)
            widget.close()


class Cancel(object):
    def __init__(self):
        pass

class Obsids_from_selection(object):
    def __init__(self):
        pass




