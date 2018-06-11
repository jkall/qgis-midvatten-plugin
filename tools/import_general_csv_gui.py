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
import copy
import io
import os
from operator import itemgetter

import PyQt4
from PyQt4.QtCore import QCoreApplication

import date_utils
import db_utils
import import_data_to_db
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from gui_utils import RowEntry, VRowEntry, get_line, RowEntryGrid
from midvatten_utils import returnunicode as ru
from gui_utils import DistinctValuesBrowser

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
        self.setWindowTitle(ru(QCoreApplication.translate(u'GeneralCsvImportGui', "Csv import")))  # Set the title for the dialog
        self.table_chooser = None
        self.file_data = None
        self.status = True

    def load_gui(self):
        self.tables_columns_info = {k: v for (k, v) in db_utils.db_tables_columns_info().iteritems() if not k.endswith(u'_geom')}
        self.table_chooser = ImportTableChooser(self.tables_columns_info, self.connect, file_header=None)
        self.main_vertical_layout.addWidget(self.table_chooser.widget)
        self.main_vertical_layout.addStretch()
        #General buttons
        self.select_file_button = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Load data from file')))
        self.gridLayout_buttons.addWidget(self.select_file_button, 0, 0)
        self.connect(self.select_file_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(), [lambda: self.load_files(),
                                                 lambda: self.table_chooser.reload(),
                                                 lambda: self.file_data_loaded_popup()]))


        self.import_all_features_button = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Load data from all features\nfrom active layer')))
        self.gridLayout_buttons.addWidget(self.import_all_features_button, 1, 0)
        self.connect(self.import_all_features_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(), [lambda: self.load_from_active_layer(only_selected=False),
                                                 lambda: self.table_chooser.reload(),
                                                 lambda: self.file_data_loaded_popup()]))

        self.import_selected_features_button = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Load data from selected features\nfrom active layer')))
        self.gridLayout_buttons.addWidget(self.import_selected_features_button, 2, 0)
        self.connect(self.import_selected_features_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(), [lambda: self.load_from_active_layer(only_selected=True),
                                                 lambda: self.table_chooser.reload(),
                                                 lambda: self.file_data_loaded_popup()]))

        self.gridLayout_buttons.addWidget(get_line(), 3, 0)

        tables_columns = db_utils.tables_columns()
        self.distinct_value_browser = DistinctValuesBrowser(tables_columns, self.connect)
        self.gridLayout_buttons.addWidget(self.distinct_value_browser.widget, 4, 0)

        self.gridLayout_buttons.addWidget(get_line(), 5, 0)

        self.close_after_import = PyQt4.QtGui.QCheckBox(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Close dialog after import')))
        self.close_after_import.setChecked(True)
        self.gridLayout_buttons.addWidget(self.close_after_import, 6, 0)

        self.start_import_button = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Start import')))
        self.gridLayout_buttons.addWidget(self.start_import_button, 7, 0)
        self.connect(self.start_import_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     self.start_import)

        self.gridLayout_buttons.setRowStretch(8, 1)

        self.show()

    @utils.waiting_cursor
    def load_files(self):
        charset = utils.ask_for_charset()
        if not charset:
            return None
        filename = utils.select_files(only_one_file=True, extension=ru(QCoreApplication.translate(u'GeneralCsvImportGui', "Comma or semicolon separated csv file %s;;Comma or semicolon separated csv text file %s;;Comma or semicolon separated file %s"))%('(*.csv)', '(*.txt)', '(*.*)'))
        if not filename:
            return None
        if isinstance(filename, (list, tuple)):
            filename = filename[0]
        else:
            filename = filename
        filename = ru(filename)

        delimiter = utils.get_delimiter(filename=filename, charset=charset, delimiters=[u',', u';'])
        self.file_data = self.file_to_list(filename, charset, delimiter)

        header_question = utils.Askuser(question=u"YesNo", msg=ru(QCoreApplication.translate(u'GeneralCsvImportGui', u"""Does the file contain a header?""")))
        if header_question.result:
            # Remove duplicate header entries
            header = self.file_data[0]
            seen = set()
            seen_add = seen.add
            remove_cols = [idx for idx, x in enumerate(header) if x and (x in seen or seen_add(x))]
            self.file_data = [[col for idx, col in enumerate(row) if idx not in remove_cols] for row in self.file_data]

            self.table_chooser.file_header = self.file_data[0]
        else:
            header = [u'Column ' + str(colnr) for colnr in xrange(len(self.file_data[0]))]
            self.table_chooser.file_header = header
            self.file_data.reverse()
            self.file_data.append(header)
            self.file_data.reverse()

    def file_data_loaded_popup(self):
        if self.file_data is not None:
            for button in (self.select_file_button, self.import_all_features_button, self.import_selected_features_button):
                button.setEnabled(False)
            utils.pop_up_info(msg=ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'File data loaded. Select table to import to.')))

    def file_to_list(self, filename, charset, delimiter):
        with io.open(filename, 'r', encoding=charset) as f:
            file_data = [rawrow.rstrip(u'\n').rstrip(u'\r').split(delimiter) for rawrow in f if rawrow.strip()]
        return file_data

    @utils.waiting_cursor
    def load_from_active_layer(self, only_selected=False):
        self.file_data = None
        self.table_chooser.file_header = None

        active_layer = utils.get_active_layer()
        if not active_layer:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Import error, no layer selected.')))
            return None

        if not only_selected:
            active_layer.selectAll()

        features = active_layer.selectedFeaturesIterator()
        file_data = [[ru(field.name()) for field in active_layer.fields()]]

        for feature in features:
            file_data.append([ru(attr) if all([ru(attr).strip() != u'NULL' if attr is not None else u'', attr is not None]) else u'' for attr in feature])

        self.file_data = file_data
        self.table_chooser.file_header = file_data[0]

    @utils.waiting_cursor
    @utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self):
        if self.file_data is None:
            raise utils.UsageError(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Error, must select a file first!')))

        translation_dict = self.table_chooser.get_translation_dict()

        file_data = copy.deepcopy(self.file_data)

        goal_table = self.table_chooser.import_method

        foreign_keys = db_utils.get_foreign_keys(goal_table)

        foreign_key_obsid_tables = [tname for tname, colnames in foreign_keys.iteritems() for colname in colnames if colname[0] == u'obsid']
        if len(foreign_key_obsid_tables) == 1:
            foreign_key_obsid_table = foreign_key_obsid_tables[0]
        else:
            foreign_key_obsid_table = goal_table
        for file_column in translation_dict.keys():
            alter_colnames = []
            new_value = None
            # Check if obsid should be set from selection and add an obsid-column if so.
            if isinstance(file_column, Obsids_from_selection):
                selected = utils.get_selected_features_as_tuple()
                if len(selected) != 1:
                    utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Import error, must select 1 obsid')), duration=60)
                    return u'cancel'
                alter_colnames = [u'obsid']
                new_value = selected[0]
            elif isinstance(file_column, StaticValue):
                if translation_dict[file_column]:
                    alter_colnames = translation_dict[file_column]
                    new_value = file_column.value
            for alter_colname in alter_colnames:
                if alter_colnames is not None and new_value is not None:
                    try:
                        colindex = file_data[0].index(alter_colname)
                    except ValueError:
                        colindex = len(file_data[0])
                        file_data[0].append(alter_colname)

                    for row in file_data[1:]:
                        if colindex + 1 < len(file_data[0]):
                            row[colindex] = new_value
                        else:
                            row.append(new_value)

                    #[row.insert(obsidindex, selected[0]) if obsidindex + 1 < len(file_data[0]) else row.append(selected[0]) for row in file_data[1:]]
                    del translation_dict[file_column]

                    translation_dict[alter_colname] = [alter_colname]

        columns_factors = self.table_chooser.get_columns_factors_dict()

        #Translate column names and add columns that appear more than once
        file_data = self.translate_and_reorder_file_data(file_data, translation_dict)
        file_data = self.convert_comma_to_points_for_double_columns(file_data, self.tables_columns_info[goal_table])
        if columns_factors:
            file_data = self.multiply_by_factor(file_data, columns_factors)
        file_data = self.remove_preceding_trailing_spaces_tabs(file_data)
        if foreign_key_obsid_table and foreign_key_obsid_table != goal_table and u'obsid' in file_data[0]:
            file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', utils.get_all_obsids(foreign_key_obsid_table), try_capitalize=False)

        file_data = self.reformat_date_time(file_data)

        importer = import_data_to_db.midv_data_importer()
        answer = importer.general_import(goal_table=goal_table, file_data=file_data)
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        importer.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

        if self.close_after_import.isChecked():
            self.close()

    @staticmethod
    def translate_and_reorder_file_data(file_data, translation_dict):
        new_file_header = [db_column for file_column, db_columns in sorted(translation_dict.iteritems()) for db_column in sorted(db_columns)]
        file_column_index = dict([(file_column, idx) for idx, file_column in enumerate(file_data[0])])
        new_file_data = [new_file_header]
        #The loop "for db_column in sorted(db_columns)" is used for cases where one file column is sent to multiple database columns.
        try:
            new_file_data.extend([[row[file_column_index[file_column]] for file_column, db_columns in sorted(translation_dict.iteritems()) for db_column in sorted(db_columns)] for rownr, row in enumerate(file_data[1:])])
        except IndexError as e:
            raise IndexError(ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'Import error on row number %s:\n%s'))%(str(rownr + 1), u'\n'.join([u': '.join(x) for x in zip(file_data[0], row)])))

        return new_file_data

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

    @staticmethod
    def convert_comma_to_points_for_double_columns(file_data, table_column):
        """
        Converts comma to point for columns with column types real or double
        :param file_data: a list of lists like [[u'obsid', u'date_time', u'reading'], [u'obs1', u'2017-04-12 11:03', '123,456']]
        :param table_column: a tuple like ((6, u'comment', u'text', 0, None, 0), (4, u'cond_mscm', u'double', 0, None, 0), (1, u'date_time', u'text', 1, None, 2), (2, u'head_cm', u'double', 0, None, 0), (5, u'level_masl', u'double', 0, None, 0), (0, u'obsid', u'text', 1, None, 1), (3, u'temp_degc', u'double', 0, None, 0))
        :return: file_data where double and real column types have been converted from comma to point.
        """
        table_column_dict = dict([(column[1], column[2]) for column in table_column])
        colnrs_to_convert = [colnr for colnr, col in enumerate(file_data[0]) if table_column_dict.get(col, u'').lower() in (u'double', u'double precision', u'real')]
        file_data = [[col.replace(u',', u'.') if all([colnr in colnrs_to_convert, rownr > 0, col is not None]) else col for colnr, col in enumerate(row)] for rownr, row in enumerate(file_data)]
        return file_data

    @staticmethod
    def multiply_by_factor(file_data, columns_factors):
        """
        Multiplies all values in the file data with a given factor for each column
        :param file_data: a list of lists like [[u'obsid', u'date_time', u'reading'], [u'obs1', u'2017-04-12 11:03', '123,456']]
        :param table_columns_factors: a dict like {u'reading': 10}
        :return: file_data where the columns have been multiplied by the factor.
        """
        print(str(columns_factors))
        file_data = [[str(float(col) * columns_factors[file_data[0][colnr]]) if
                      (file_data[0][colnr] in columns_factors and utils.to_float_or_none(col) is not None)
                      else col for colnr, col in enumerate(row)]
                     if rownr > 0 else row for rownr, row in enumerate(file_data)]
        return file_data

    @staticmethod
    def reformat_date_time(file_data):
        try:
            colnrs_to_convert = [file_data[0].index(u'date_time')]
        except ValueError:
            return file_data
        else:
            if colnrs_to_convert:
                num_rows_before = len(file_data)
                file_data = [[date_utils.reformat_date_time(col) if all([rownr > 0, colnr in colnrs_to_convert]) else col
                              for colnr, col in enumerate(row)]
                             for rownr, row in enumerate(file_data)
                             if rownr == 0 or all([date_utils.reformat_date_time(row[_colnr]) for _colnr in colnrs_to_convert])]

                num_rows_after = len(file_data)
                num_removed_rows = num_rows_before - num_rows_after
                if num_removed_rows > 0:
                    utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'GeneralCsvImportGui', u'%s rows without parsable date_time format skipped during import'))%str(num_removed_rows))
            return file_data

    @staticmethod
    def remove_preceding_trailing_spaces_tabs(file_data):
        file_data = [[col.lstrip().rstrip() if all([rownr > 0, col is not None]) else col for colnr, col in enumerate(row)] for rownr, row in enumerate(file_data)]
        return file_data


class ImportTableChooser(VRowEntry):
    def __init__(self, tables_columns, connect, file_header=None):
        super(ImportTableChooser, self).__init__()
        self.connect = connect
        self.tables_columns = tables_columns
        self.file_header = file_header
        self.columns = []
        self.numeric_datatypes = db_utils.numeric_datatypes()

        chooser = RowEntry()

        self.label = PyQt4.QtGui.QLabel(ru(QCoreApplication.translate(u'ImportTableChooser', 'Import to table')))
        self.__import_method = PyQt4.QtGui.QComboBox()
        self.__import_method.addItem(u'')
        self.__import_method.addItems(sorted(tables_columns.keys(), key=lambda s: s.lower()))

        self.connect(self.__import_method, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.choose_method)

        for widget in [self.label, self.__import_method]:
            chooser.layout.addWidget(widget)

        self.layout.addWidget(chooser.widget)

        self.specific_info_widget = VRowEntry()
        self.specific_info_widget.layout.addWidget(get_line())
        self.specific_table_info = PyQt4.QtGui.QLabel()
        self.specific_info_widget.layout.addWidget(self.specific_table_info)
        self.specific_info_widget.layout.addWidget(get_line())

        self.layout.addWidget(self.specific_info_widget.widget)

        self.layout.insertStretch(-1, 4)

    def get_translation_dict(self):
        translation_dict = {}
        for column_entry in self.columns:
            file_column_name = column_entry.file_column_name
            if file_column_name:
                column_list = translation_dict.get(file_column_name, [])
                column_list = copy.deepcopy(column_list)
                column_list.append(column_entry.db_column)
                translation_dict[file_column_name] = column_list
        return translation_dict

    def get_columns_factors_dict(self):
        columns_factors = dict([(column_entry.db_column, column_entry.factor)
                                for column_entry in self.columns
                                if column_entry.column_type in self.numeric_datatypes
                                and column_entry.factor != 1])

        return columns_factors

    @property
    def import_method(self):
        return str(self.__import_method.currentText())

    @import_method.setter
    def import_method(self, value):
        index = self.__import_method.findText(ru(value))
        if index != -1:
            self.__import_method.setCurrentIndex(index)

    def choose_method(self):
        tables_columns = self.tables_columns
        file_header = self.file_header
        import_method_name = self.import_method
        layer = utils.find_layer(import_method_name)
        if layer is not None:
            if layer.isEditable():
                utils.pop_up_info(ru(QCoreApplication.translate(u'ImportTableChooser', u"Layer %s is currently in editing mode.\nPlease exit this mode before proceeding with this operation."))%str(layer.name()), ru(QCoreApplication.translate(u'GeneralCsvImportGui', "Error")),)
                self.import_method = u''
                import_method_name = None

        self.specific_table_info.setText(defs.specific_table_info.get(import_method_name, u''))

        if file_header is None:
            return None

        #Remove stretch
        self.layout.takeAt(-1)

        try:
            self.layout.removeWidget(self.grid.widget)
            self.grid.widget.close()
        except:
            pass

        self.columns = []

        if not import_method_name:
            self.layout.insertStretch(-1, 4)
            return None

        self.grid = RowEntryGrid()
        self.layout.addWidget(self.grid.widget)

        self.grid.layout.addWidget(PyQt4.QtGui.QLabel(ru(QCoreApplication.translate(u'ImportTableChooser', u'Column name'))), 0, 0)
        self.grid.layout.addWidget(PyQt4.QtGui.QLabel(ru(QCoreApplication.translate(u'ImportTableChooser', u'File column'))), 0, 1)
        self.grid.layout.addWidget(PyQt4.QtGui.QLabel(ru(QCoreApplication.translate(u'ImportTableChooser', u'Static value'))), 0, 2)
        self.grid.layout.addWidget(PyQt4.QtGui.QLabel(ru(QCoreApplication.translate(u'ImportTableChooser', u'Factor'))), 0, 3)

        for index, tables_columns_info in enumerate(sorted(tables_columns[import_method_name], key=itemgetter(0))):
            column = ColumnEntry(tables_columns_info, file_header, self.connect, self.numeric_datatypes)
            rownr = self.grid.layout.rowCount()
            for colnr, wid in enumerate(column.column_widgets):
                self.grid.layout.addWidget(wid, rownr, colnr)
            self.columns.append(column)

        self.layout.insertStretch(-1, 4)

    def reload(self):
        import_method = self.import_method
        self.import_method = u''
        self.import_method = import_method


class ColumnEntry(object):
    def __init__(self, tables_columns_info, file_header, connect, numeric_datatypes):
        self.tables_columns_info = tables_columns_info
        self.connect = connect
        self.obsids_from_selection = None
        self.file_header = file_header

        self.db_column = tables_columns_info[1]
        self.column_type = tables_columns_info[2]
        self.notnull = int(tables_columns_info[3])
        pk = int(tables_columns_info[5])
        concatted_info = u', '.join([_x for _x in [self.column_type, u'not null' if self.notnull else False,
                                      u'primary key' if pk else False] if _x])
        label = PyQt4.QtGui.QLabel(u' '.join([u'Column ', self.db_column, u'({})'.format(concatted_info)]))

        self.column_widgets = [label]
        self._all_widgets = [label]

        self.combobox = PyQt4.QtGui.QComboBox()
        self.combobox.setEditable(True)
        self.combobox.addItem(u'')
        self.combobox.addItems(sorted(self.file_header, key=lambda s: s.lower()))

        if self.db_column == u'obsid':
            self.obsids_from_selection = PyQt4.QtGui.QCheckBox(ru(QCoreApplication.translate(u'ColumnEntry', u'Obsid from qgis selection')))
            self.obsids_from_selection.setToolTip(ru(QCoreApplication.translate(u'ColumnEntry', u'Select 1 obsid from obs_points or obs_lines attribute table or map.')))
            self.connect(self.obsids_from_selection, PyQt4.QtCore.SIGNAL("clicked()"), self.obsids_from_selection_checked)

            self.obsid_widget = RowEntry()
            self.obsid_widget.layout.addWidget(self.obsids_from_selection)
            self.obsid_widget.layout.addWidget(self.combobox)

            self._all_widgets.extend([self.obsids_from_selection, self.combobox, self.obsid_widget.widget])

            self.column_widgets.append(self.obsid_widget.widget)
        else:
            self.column_widgets.append(self.combobox)
            self._all_widgets.extend(self.column_widgets)

        self.static_checkbox = PyQt4.QtGui.QCheckBox()
        self.static_checkbox.setToolTip(ru(QCoreApplication.translate(u'ColumnEntry', u'The supplied string will be written to the current column name for all\nimported rows instead of being read from file column.')))
        self.column_widgets.append(self.static_checkbox)
        self._all_widgets.append(self.static_checkbox)

        self._factor = PyQt4.QtGui.QLineEdit()
        self._factor.setText(u'1')
        self._factor.setToolTip(ru(QCoreApplication.translate(u'ColumnEntry', u'Multiply each imported value in the column with a factor.')))
        self._factor.setFixedWidth(40)
        self.column_widgets.append(self._factor)
        self._all_widgets.append(self._factor)

        if self.column_type not in numeric_datatypes:
            self._factor.setVisible(False)

        self.connect(self.static_checkbox, PyQt4.QtCore.SIGNAL("clicked()"), self.static_checkbox_checked)

        #This line prefills the columns if the header names matches the database column names
        self.file_column_name = self.db_column

    @property
    def file_column_name(self):
        if self.obsids_from_selection is not None:
            if self.obsids_from_selection.isChecked():
                return Obsids_from_selection()

        selected = ru(self.combobox.currentText())
        if self.static_checkbox.isChecked():
            selected = StaticValue(ru(self.combobox.currentText()))

        if self.notnull and not selected:
            raise utils.UsageError(ru(QCoreApplication.translate(u'ColumnEntry', u'Import error, the column %s must have a value'))%self.db_column)

        if selected and not self.static_checkbox.isChecked() and selected not in self.file_header:
            raise utils.UsageError(ru(QCoreApplication.translate(u'ColumnEntry', u'Import error, the chosen file column for the column %s did not exist in the file header.'))%self.db_column)
        else:
            return selected

    @file_column_name.setter
    def file_column_name(self, value):
        if self.static_checkbox.isChecked():
            self.combobox.setEditText(value)
        else:
            index = self.combobox.findText(ru(value))
            if index != -1:
                self.combobox.setCurrentIndex(index)

    def obsids_from_selection_checked(self):
        if self.obsids_from_selection.isChecked():
            self.combobox.setEnabled(False)
            self.static_checkbox.setChecked(False)
        else:
            self.combobox.setEnabled(True)

    def static_checkbox_checked(self):
        if self.static_checkbox.isChecked():
            self.combobox.setEnabled(True)
            if isinstance(self.obsids_from_selection, PyQt4.QtGui.QCheckBox):
                self.obsids_from_selection.setChecked(False)

    @property
    def factor(self):
        value = self._factor.text()
        as_float = utils.to_float_or_none(value)
        if isinstance(as_float, float):
            return as_float
        else:
            return None

    @factor.setter
    def factor(self, value):
        as_float = utils.to_float_or_none(value)
        if isinstance(as_float, float):
            self._factor.setText(str(as_float))


class Obsids_from_selection(object):
    def __init__(self):
        pass


class StaticValue(object):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(self.value)


