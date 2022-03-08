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
from __future__ import absolute_import
from __future__ import print_function

import copy
import csv
import os
from builtins import object
from builtins import range
from builtins import str
from operator import itemgetter

import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsCoordinateReferenceSystem

import midvatten.definitions.midvatten_defs as defs
from midvatten.tools import import_data_to_db
from midvatten.tools.utils import common_utils, midvatten_utils, db_utils, date_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools.utils.gui_utils import RowEntry, VRowEntry, get_line, RowEntryGrid, DistinctValuesBrowser

import_ui_dialog =  qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]


class GeneralCsvImportGui(qgis.PyQt.QtWidgets.QMainWindow, import_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate('GeneralCsvImportGui', "Csv import")))  # Set the title for the dialog
        self.table_chooser = None
        self.file_data = None
        self.srid = None

    def load_gui(self):
        self.tables_columns_info = {k: v for (k, v) in db_utils.db_tables_columns_info().items() if not k.endswith('_geom')}
        self.table_chooser = ImportTableChooser(self.tables_columns_info, file_header=None)
        self.main_vertical_layout.addWidget(self.table_chooser.widget)
        self.main_vertical_layout.addStretch()
        #General buttons
        self.select_file_button = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Load data from file')))
        self.gridLayout_buttons.addWidget(self.select_file_button, 0, 0)
        self.select_file_button.clicked.connect(lambda x: self.select_file())


        self.import_all_features_button = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Load data from all features\nfrom active layer')))
        self.gridLayout_buttons.addWidget(self.import_all_features_button, 1, 0)
        self.import_all_features_button.clicked.connect(lambda x: self.import_all_features())

        self.import_selected_features_button = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Load data from selected features\nfrom active layer')))
        self.gridLayout_buttons.addWidget(self.import_selected_features_button, 2, 0)
        self.import_selected_features_button.clicked.connect(lambda x: self.import_selected_features())

        self.gridLayout_buttons.addWidget(get_line(), 3, 0)

        tables_columns = db_utils.tables_columns()
        self.distinct_value_browser = DistinctValuesBrowser(tables_columns)
        self.gridLayout_buttons.addWidget(self.distinct_value_browser.widget, 4, 0)

        self.gridLayout_buttons.addWidget(get_line(), 5, 0)

        self.close_after_import = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Close dialog after import')))
        self.close_after_import.setChecked(True)
        self.gridLayout_buttons.addWidget(self.close_after_import, 6, 0)

        self.start_import_button = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Start import')))
        self.gridLayout_buttons.addWidget(self.start_import_button, 7, 0)
        self.start_import_button.clicked.connect(lambda x: self.start_import())

        self.gridLayout_buttons.setRowStretch(8, 1)
        self.setGeometry(100, 100, 1800, 800)
        self.show()

    @common_utils.general_exception_handler
    def select_file(self):
        self.load_files()
        self.table_chooser.reload()
        self.file_data_loaded_popup()

    @common_utils.general_exception_handler
    @common_utils.waiting_cursor
    def import_all_features(self):
        self.load_from_active_layer(only_selected=False)
        self.table_chooser.reload()
        self.file_data_loaded_popup()

    @common_utils.general_exception_handler
    @common_utils.waiting_cursor
    def import_selected_features(self):
        self.load_from_active_layer(only_selected=True)
        self.table_chooser.reload()
        self.file_data_loaded_popup()

    def load_files(self):
        charset = midvatten_utils.ask_for_charset()
        if not charset:
            raise common_utils.UserInterruptError()
        filename = midvatten_utils.select_files(only_one_file=True, extension=ru(QCoreApplication.translate('GeneralCsvImportGui', "Comma or semicolon separated csv file %s;;Comma or semicolon separated csv text file %s;;Comma or semicolon separated file %s")) % ('(*.csv)', '(*.txt)', '(*.*)'))
        if isinstance(filename, (list, tuple)):
            filename = filename[0]

        filename = ru(filename)

        delimiter = common_utils.get_delimiter(filename=filename, charset=charset, delimiters=[',', ';'])
        self.file_data = self.file_to_list(filename, charset, delimiter)

        header_question = common_utils.Askuser(question="YesNo", msg=ru(QCoreApplication.translate('GeneralCsvImportGui', """Does the file contain a header?""")))

        common_utils.start_waiting_cursor()
        if header_question.result:
            # Remove duplicate header entries
            header = self.file_data[0]
            seen = set()
            seen_add = seen.add
            remove_cols = [idx for idx, x in enumerate(header) if x and (x in seen or seen_add(x))]
            self.file_data = [[col for idx, col in enumerate(row) if idx not in remove_cols] for row in self.file_data]

            self.table_chooser.file_header = self.file_data[0]
        else:
            header = ['Column ' + str(colnr) for colnr in range(len(self.file_data[0]))]
            self.table_chooser.file_header = header
            self.file_data.reverse()
            self.file_data.append(header)
            self.file_data.reverse()
        common_utils.stop_waiting_cursor()

    def file_data_loaded_popup(self):
        if self.file_data is not None:
            for button in (self.select_file_button, self.import_all_features_button, self.import_selected_features_button):
                button.setEnabled(False)
            common_utils.pop_up_info(msg=ru(QCoreApplication.translate('GeneralCsvImportGui', 'File data loaded. Select table to import to.')))

    @staticmethod
    def file_to_list(filename, charset, delimiter, quotechar='"'):
        common_utils.start_waiting_cursor()
        try:
            with open(filename, 'rt', encoding=str(charset)) as f:
                rows_unsplit = [row.lstrip().rstrip('\n').rstrip('\r') for row in f]
                csvreader = csv.reader(rows_unsplit, delimiter=delimiter, quotechar=quotechar)
                file_data = [ru(row, keep_containers=True) for row in csvreader]
        except:
            common_utils.stop_waiting_cursor()
            raise
        else:
            common_utils.stop_waiting_cursor()
        return file_data

    def load_from_active_layer(self, only_selected=False):
        self.file_data = None
        self.table_chooser.file_header = None

        active_layer = common_utils.get_active_layer()
        if not active_layer:
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('GeneralCsvImportGui', 'Import error, no layer selected.')))
            return None

        if not only_selected:
            active_layer.selectAll()

        features = list(active_layer.getSelectedFeatures())
        file_data = [[ru(field.name()) for field in active_layer.fields()]]
        [file_data.append([ru(attr) if all([ru(attr).strip() != 'NULL' if attr is not None else '', attr is not None]) else '' for attr in feature]) for feature in features]
        geometries = [feature.geometry().asWkt() if feature.geometry().asWkt() else None for feature in features]
        if any(geometries):
            geom_name = 'geometry'
            while geom_name in file_data[0]:
                geom_name += '_'
            file_data[0].append(geom_name)
            [file_data[idx+1].append(wkt) for idx, wkt in enumerate(geometries)]

        self.file_data = file_data
        self.srid = active_layer.crs().authid()
        self.table_chooser.file_header = file_data[0]

    @common_utils.waiting_cursor
    @common_utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self):
        """
        TODO: I have NO IDEA where the dummy parameter is coming from. It gets the value False for some reason!
        :param dummy:
        :return:
        """
        if self.file_data is None:
            raise common_utils.UsageError(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Error, must select a file first!')))

        translation_dict = self.table_chooser.get_translation_dict()

        file_data = copy.deepcopy(self.file_data)

        dest_table = self.table_chooser.import_method

        foreign_keys = db_utils.get_foreign_keys(dest_table)

        foreign_key_obsid_tables = [tname for tname, colnames in foreign_keys.items() for colname in colnames if colname[0] == 'obsid']
        if len(foreign_key_obsid_tables) == 1:
            foreign_key_obsid_table = foreign_key_obsid_tables[0]
        else:
            foreign_key_obsid_table = dest_table
        for file_column in list(translation_dict.keys()):
            alter_colnames = []
            new_value = None
            # Check if obsid should be set from selection and add an obsid-column if so.
            if isinstance(file_column, Obsids_from_selection):
                selected = common_utils.get_selected_features_as_tuple()
                if len(selected) != 1:
                    common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('GeneralCsvImportGui', 'Import error, must select 1 obsid')), duration=60)
                    return 'cancel'
                alter_colnames = ['obsid']
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
        file_data = self.convert_comma_to_points_for_double_columns(file_data, self.tables_columns_info[dest_table])
        if columns_factors:
            file_data = self.multiply_by_factor(file_data, columns_factors)
        file_data = self.remove_preceding_trailing_spaces_tabs(file_data)
        if foreign_key_obsid_table and foreign_key_obsid_table != dest_table and 'obsid' in file_data[0]:
            file_data = common_utils.filter_nonexisting_values_and_ask(file_data, 'obsid', db_utils.get_all_obsids(foreign_key_obsid_table), try_capitalize=False)

        file_data = self.reformat_date_time(file_data)

        importer = import_data_to_db.midv_data_importer()
        answer = importer.general_import(dest_table=dest_table, file_data=file_data, source_srid=self.srid)
        common_utils.stop_waiting_cursor()

        if self.close_after_import.isChecked():
            self.close()

    @staticmethod
    def translate_and_reorder_file_data(file_data, translation_dict):
        new_file_header = [db_column for file_column, db_columns in sorted(translation_dict.items()) for db_column in sorted(db_columns)]
        file_column_index = dict([(file_column, idx) for idx, file_column in enumerate(file_data[0])])
        new_file_data = [new_file_header]
        #The loop "for db_column in sorted(db_columns)" is used for cases where one file column is sent to multiple database columns.

        # Due to the python3 non-leaking behaviour, this try-except no longer performs the way its intended, so I'm not
        # using it anymore.
        #try:
        res = [[row[file_column_index[file_column]] for file_column, db_columns in sorted(translation_dict.items()) for
                 db_column in sorted(db_columns)] for rownr, row in enumerate(file_data[1:])]
        #except IndexError as e:
        #    raise IndexError(ru(QCoreApplication.translate('GeneralCsvImportGui', 'Import error on row number %s:\n%s'))%(str(rownr + 1), '\n'.join([': '.join(x) for x in zip(file_data[0], row)])))
        new_file_data.extend(res)
        return new_file_data

    def add_line(self, layout=None):
        """ just adds a line"""
        # horizontalLineWidget = PyQt4.QtWidgets.QWidget()
        # horizontalLineWidget.setFixedHeight(2)
        # horizontalLineWidget.setSizePolicy(PyQt4.QtWidgets.QSizePolicy.Expanding, PyQt4.QtWidgets.QSizePolicy.Fixed)
        # horizontalLineWidget.setStyleSheet(PyQt4.QtCore.QString("background-color: #c0c0c0;"));
        line = qgis.PyQt.QtWidgets.QFrame()
        # line.setObjectName(QString::fromUtf8("line"));
        line.setGeometry(qgis.PyQt.QtCore.QRect(320, 150, 118, 3))
        line.setFrameShape(qgis.PyQt.QtWidgets.QFrame.HLine)
        line.setFrameShadow(qgis.PyQt.QtWidgets.QFrame.Sunken)
        if layout is None:
            self.add_row(line)
        else:
            layout.addWidget(line)

    @staticmethod
    def convert_comma_to_points_for_double_columns(file_data, table_column):
        """
        Converts comma to point for columns with column types real or double
        :param file_data: a list of lists like [['obsid', 'date_time', 'reading'], ['obs1', '2017-04-12 11:03', '123,456']]
        :param table_column: a tuple like ((6, 'comment', 'text', 0, None, 0), (4, 'cond_mscm', 'double', 0, None, 0), (1, 'date_time', 'text', 1, None, 2), (2, 'head_cm', 'double', 0, None, 0), (5, 'level_masl', 'double', 0, None, 0), (0, 'obsid', 'text', 1, None, 1), (3, 'temp_degc', 'double', 0, None, 0))
        :return: file_data where double and real column types have been converted from comma to point.
        """
        table_column_dict = dict([(column[1], column[2]) for column in table_column])
        colnrs_to_convert = [colnr for colnr, col in enumerate(file_data[0]) if table_column_dict.get(col, '').lower() in ('double', 'double precision', 'real')]
        file_data = [[col.replace(',', '.') if all([colnr in colnrs_to_convert, rownr > 0, col is not None]) else col for colnr, col in enumerate(row)] for rownr, row in enumerate(file_data)]
        return file_data

    @staticmethod
    def multiply_by_factor(file_data, columns_factors):
        """
        Multiplies all values in the file data with a given factor for each column
        :param file_data: a list of lists like [['obsid', 'date_time', 'reading'], ['obs1', '2017-04-12 11:03', '123,456']]
        :param table_columns_factors: a dict like {'reading': 10}
        :return: file_data where the columns have been multiplied by the factor.
        """
        file_data = [[str(float(col) * columns_factors[file_data[0][colnr]]) if
                      (file_data[0][colnr] in columns_factors and common_utils.to_float_or_none(col) is not None)
                      else col for colnr, col in enumerate(row)]
                     if rownr > 0 else row for rownr, row in enumerate(file_data)]
        return file_data

    @staticmethod
    def reformat_date_time(file_data):
        try:
            colnrs_to_convert = [file_data[0].index('date_time')]
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
                    common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('GeneralCsvImportGui', '%s rows without parsable date_time format skipped during import')) % str(num_removed_rows))
            return file_data

    @staticmethod
    def remove_preceding_trailing_spaces_tabs(file_data):
        file_data = [[col.lstrip().rstrip() if all([rownr > 0, col is not None]) else col for colnr, col in enumerate(row)] for rownr, row in enumerate(file_data)]
        return file_data


class ImportTableChooser(VRowEntry):
    def __init__(self, tables_columns, file_header=None):
        super(ImportTableChooser, self).__init__()
        self.tables_columns = tables_columns
        self.file_header = file_header
        self.columns = []
        self.numeric_datatypes = db_utils.numeric_datatypes()

        chooser = RowEntry()

        self.label = qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('ImportTableChooser', 'Import to table')))
        self.__import_method = qgis.PyQt.QtWidgets.QComboBox()
        self.__import_method.addItem('')
        self.__import_method.addItems(sorted(list(tables_columns.keys()), key=lambda s: s.lower()))

        self.__import_method.currentIndexChanged.connect( self.choose_method)

        for widget in [self.label, self.__import_method]:
            chooser.layout.addWidget(widget)
        chooser.layout.insertStretch(-1, 5)

        self.layout.addWidget(chooser.widget)

        self.specific_info_widget = VRowEntry()
        self.specific_info_widget.layout.addWidget(get_line())
        self.specific_table_info = qgis.PyQt.QtWidgets.QLabel()
        self.specific_info_widget.layout.addWidget(self.specific_table_info)
        self.specific_info_widget.layout.addWidget(get_line())

        self.layout.addWidget(self.specific_info_widget.widget)

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
        try:
            layer = common_utils.find_layer(import_method_name)
        except common_utils.UsageError:
            pass
        else:
            if layer is not None:
                if layer.isEditable():
                    common_utils.pop_up_info(ru(QCoreApplication.translate('ImportTableChooser', "Layer %s is currently in editing mode.\nPlease exit this mode before proceeding with this operation.")) % str(layer.name()), ru(QCoreApplication.translate('GeneralCsvImportGui', "Error")), )
                    self.import_method = ''
                    import_method_name = None

        self.specific_table_info.setText(defs.specific_table_info.get(import_method_name, ''))

        if file_header is None:
            return None


        try:
            self.layout.removeWidget(self.grid.widget)
            self.grid.widget.close()
        except:
            pass

        self.columns = []

        if not import_method_name:
            return None

        self.grid = RowEntryGrid()
        self.layout.addWidget(self.grid.widget)

        self.grid.layout.addWidget(qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('ImportTableChooser', 'Column name'))), 0, 0)
        self.grid.layout.addWidget(qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('ImportTableChooser', 'File column'))), 0, 1)
        self.grid.layout.addWidget(qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('ImportTableChooser', 'Static value'))), 0, 2)
        self.grid.layout.addWidget(qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('ImportTableChooser', 'Factor'))), 0, 3)
        self.grid.layout.addWidget(qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('ImportTableChooser', 'Ignore not null warning'))), 0, 4)

        for index, tables_columns_info in enumerate(sorted(tables_columns[import_method_name], key=itemgetter(0))):
            column = ColumnEntry(tables_columns_info, file_header, self.numeric_datatypes)
            rownr = self.grid.layout.rowCount()
            for colnr, wid in enumerate(column.column_widgets):
                self.grid.layout.addWidget(wid, rownr, colnr)
            self.columns.append(column)

        self.grid.layout.setColumnStretch(5, 5)

    def reload(self):
        import_method = self.import_method
        self.import_method = ''
        self.import_method = import_method


class ColumnEntry(object):
    def __init__(self, tables_columns_info, file_header, numeric_datatypes):
        self.tables_columns_info = tables_columns_info
        self.obsids_from_selection = None
        self.file_header = file_header

        self.db_column = tables_columns_info[1]
        self.column_type = tables_columns_info[2]
        self.notnull = int(tables_columns_info[3])
        pk = int(tables_columns_info[5])
        concatted_info = ', '.join([_x for _x in [self.column_type, 'not null' if self.notnull else False,
                                      'primary key' if pk else False] if _x])
        label = qgis.PyQt.QtWidgets.QLabel(' '.join(['Column ', self.db_column, '({})'.format(concatted_info)]))

        self.column_widgets = [label]
        self._all_widgets = [label]

        self.combobox = qgis.PyQt.QtWidgets.QComboBox()
        self.combobox.setEditable(True)
        self.combobox.addItem('')
        self.combobox.addItems(sorted(self.file_header, key=lambda s: s.lower()))

        if self.db_column == 'obsid':
            self.obsids_from_selection = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('ColumnEntry', 'Obsid from qgis selection')))
            self.obsids_from_selection.setToolTip(ru(QCoreApplication.translate('ColumnEntry', 'Select 1 obsid from obs_points or obs_lines attribute table or map.')))
            self.obsids_from_selection.clicked.connect(lambda x: self.obsids_from_selection_checked())

            self.obsid_widget = RowEntry()
            self.obsid_widget.layout.addWidget(self.obsids_from_selection)
            self.obsid_widget.layout.addWidget(self.combobox)

            self._all_widgets.extend([self.obsids_from_selection, self.combobox, self.obsid_widget.widget])

            self.column_widgets.append(self.obsid_widget.widget)
        else:
            self.column_widgets.append(self.combobox)
            self._all_widgets.extend(self.column_widgets)

        self.static_checkbox = qgis.PyQt.QtWidgets.QCheckBox()
        self.static_checkbox.setToolTip(ru(QCoreApplication.translate('ColumnEntry', 'The supplied string will be written to the current column name for all\nimported rows instead of being read from file column.')))
        self.column_widgets.append(self.static_checkbox)
        self._all_widgets.append(self.static_checkbox)

        self._factor = qgis.PyQt.QtWidgets.QLineEdit()
        self._factor.setText('1')
        self._factor.setToolTip(ru(QCoreApplication.translate('ColumnEntry', 'Multiply each imported value in the column with a factor.')))
        self._factor.setFixedWidth(40)
        self.column_widgets.append(self._factor)
        self._all_widgets.append(self._factor)

        if self.column_type not in numeric_datatypes:
            self._factor.setVisible(False)

        self._ignore_not_null_checkbox = qgis.PyQt.QtWidgets.QCheckBox()
        self._ignore_not_null_checkbox.setToolTip(ru(QCoreApplication.translate('ColumnEntry', 'Ignores not null warning and try to import anyway. Check when importing to Postgres SERIAL PRIMARY KEY columns.')))
        self._ignore_not_null_checkbox.setChecked(False)
        self.column_widgets.append(self._ignore_not_null_checkbox)
        self._all_widgets.append(self._ignore_not_null_checkbox)

        self.static_checkbox.clicked.connect(lambda x: self.static_checkbox_checked())

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

        if self.notnull and not selected and not self._ignore_not_null_checkbox.isChecked():
            raise common_utils.UsageError(ru(QCoreApplication.translate('ColumnEntry', 'Import error, the column %s must have a value')) % self.db_column)

        if selected and not self.static_checkbox.isChecked() and selected not in self.file_header:
            raise common_utils.UsageError(ru(QCoreApplication.translate('ColumnEntry', 'Import error, the chosen file column for the column %s did not exist in the file header.')) % self.db_column)
        else:
            return selected

    @file_column_name.setter
    def file_column_name(self, value):
        if value is None:
            self.combobox.setCurrentIndex(0)
        elif self.static_checkbox.isChecked():
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
            if isinstance(self.obsids_from_selection, qgis.PyQt.QtWidgets.QCheckBox):
                self.obsids_from_selection.setChecked(False)

    @property
    def factor(self):
        value = self._factor.text()
        as_float = common_utils.to_float_or_none(value)
        if isinstance(as_float, float):
            return as_float
        else:
            return None

    @factor.setter
    def factor(self, value):
        as_float = common_utils.to_float_or_none(value)
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


