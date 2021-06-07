# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of data to the database
  from the diveroffice format.

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

import io
import os
from builtins import str
from collections import OrderedDict
from datetime import datetime

import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools import import_data_to_db
from midvatten.tools.utils import common_utils, midvatten_utils, db_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools.utils.date_utils import find_date_format, datestring_to_date
from midvatten.tools.utils.gui_utils import VRowEntry, get_line, DateTimeFilter

import_ui_dialog =  qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]

class DiverofficeImport(qgis.PyQt.QtWidgets.QMainWindow, import_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.default_charset = 'cp1252'
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(QCoreApplication.translate('DiverofficeImport', "Diveroffice import"))  # Set the title for the dialog
        self.table_chooser = None
        self.file_data = None
        self.status = True
        self.parse_func = self.parse_diveroffice_file
        self.use_skiprows = True

    def select_files_and_load_gui(self):
        self.files = self.select_files()
        if not self.files:
            raise common_utils.UserInterruptError()

        self.date_time_filter = DateTimeFilter(calendar=True)
        self.add_row(self.date_time_filter.widget)

        self.add_row(get_line())

        self.skip_rows = CheckboxAndExplanation(QCoreApplication.translate('DiverofficeImport', 'Skip rows without water level'),
                                                QCoreApplication.translate('DiverofficeImport', 'Checked = Rows without a value for columns Water head[cm] or Level[cm] will be skipped.'))
        if self.use_skiprows:
            self.skip_rows.checked = True
            self.add_row(self.skip_rows.widget)
            self.add_row(get_line())
        else:
            self.skip_rows.checked = False

        self.confirm_names = CheckboxAndExplanation(QCoreApplication.translate('DiverofficeImport', 'Confirm each logger obsid before import'),
                                                    QCoreApplication.translate('DiverofficeImport', 'Checked = The obsid will be requested of the user for every file.\n\n') +
                                                    QCoreApplication.translate('DiverofficeImport', 'Unchecked = the location attribute, both as is and capitalized, in the\n') +
                                                    QCoreApplication.translate('DiverofficeImport', 'file will be matched against obsids in the database.\n\n') +
                                                    QCoreApplication.translate('DiverofficeImport', 'In both case, obsid will be requested of the user if no match in the database is found.'))
        self.confirm_names.checked = True
        self.add_row(self.confirm_names.widget)
        self.add_row(get_line())
        self.import_all_data = CheckboxAndExplanation(QCoreApplication.translate('DiverofficeImport', 'Import all data'),
                                                      QCoreApplication.translate('DiverofficeImport', 'Checked = any data not matching an exact datetime in the database\n') +
                                                      QCoreApplication.translate('DiverofficeImport', 'for the corresponding obsid will be imported.\n\n') +
                                                      QCoreApplication.translate('DiverofficeImport', 'Unchecked = only new data after the latest date in the database,\n') +
                                                      QCoreApplication.translate('DiverofficeImport', 'for each observation point, will be imported.'))
        self.import_all_data.checked = False
        self.add_row(self.import_all_data.widget)

        self.close_after_import = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('DiverofficeImport', 'Close dialog after import')))
        self.close_after_import.setChecked(True)
        self.gridLayout_buttons.addWidget(self.close_after_import, 0, 0)

        self.start_import_button = qgis.PyQt.QtWidgets.QPushButton(QCoreApplication.translate('DiverofficeImport', 'Start import'))
        self.gridLayout_buttons.addWidget(self.start_import_button, 1, 0)
        self.start_import_button.clicked.connect(
            lambda: self.start_import(files=self.files, skip_rows_without_water_level=self.skip_rows.checked,
                                      confirm_names=self.confirm_names.checked,
                                      import_all_data=self.import_all_data.checked,
                                      from_date=self.date_time_filter.from_date, to_date=self.date_time_filter.to_date,
                                      export_csv=False, import_to_db=True))

        self.export_csv_button = qgis.PyQt.QtWidgets.QPushButton(QCoreApplication.translate('DiverofficeImport', 'Export csv'))
        self.gridLayout_buttons.addWidget(self.export_csv_button, 2, 0)
        self.export_csv_button.clicked.connect(
            lambda: self.start_import(files=self.files, skip_rows_without_water_level=self.skip_rows.checked,
                                      confirm_names=self.confirm_names.checked,
                                      import_all_data=self.import_all_data.checked,
                                      from_date=self.date_time_filter.from_date, to_date=self.date_time_filter.to_date,
                                      export_csv=True, import_to_db=False))

        self.gridLayout_buttons.setRowStretch(3, 1)

        self.show()


    def select_files(self):
        self.charsetchoosen = midvatten_utils.ask_for_charset(default_charset=self.default_charset)
        if not self.charsetchoosen:
            raise common_utils.UserInterruptError()

        files = midvatten_utils.select_files(only_one_file=False, extension="csv (*.csv)")
        return files

    @common_utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self, files, skip_rows_without_water_level, confirm_names, import_all_data, from_date=None,
                     to_date=None, export_csv=False, import_to_db=True):
        """
        """
        common_utils.start_waiting_cursor()  #show the user this may take a long time...
        parsed_files = []
        for selected_file in files:
            try:
                res = self.parse_func(path=selected_file, charset=self.charsetchoosen, skip_rows_without_water_level=skip_rows_without_water_level, begindate=from_date, enddate=to_date)
            except:
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('LeveloggerImport',
                                                                                      '''Error on file %s.''')) % selected_file)
                raise

            if res == 'cancel':
                self.status = True
                common_utils.stop_waiting_cursor()
                return res
            elif res in ('skip', 'ignore'):
                continue

            try:
                file_data, filename, location = res
            except Exception as e:
                common_utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('DiverofficeImport', 'Import error, see log message panel'),
                                                                  log_msg=ru(QCoreApplication.translate('DiverofficeImport', 'File %s could not be parsed. Msg:\n%s'))%(selected_file, str(e)))
                continue
            parsed_files.append((file_data, filename, location))

        if len(parsed_files) == 0:
            common_utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('DiverofficeImport', "Import Failure: No files imported"""))
            common_utils.stop_waiting_cursor()
            return

        #Add obsid to all parsed filedatas by asking the user for it.
        filename_location_obsid = [['filename', 'location', 'obsid']]
        filename_location_obsid.extend([[parsed_file[1], parsed_file[2], parsed_file[2]] for parsed_file in parsed_files])

        if confirm_names:
            try_capitalize = False
        else:
            try_capitalize = True

        existing_obsids = db_utils.get_all_obsids()
        common_utils.stop_waiting_cursor()
        filename_location_obsid = common_utils.filter_nonexisting_values_and_ask(file_data=filename_location_obsid, header_value='obsid', existing_values=existing_obsids, try_capitalize=try_capitalize, always_ask_user=confirm_names)
        common_utils.start_waiting_cursor()

        if len(filename_location_obsid) < 2:
            common_utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('DiverofficeImport', 'Warning. All files were skipped, nothing imported!'))
            common_utils.stop_waiting_cursor()
            return False

        filenames_obsid = dict([(x[0], x[2]) for x in filename_location_obsid[1:]])

        parsed_files_with_obsid = []
        for file_data, filename, location in parsed_files:
            if filename in filenames_obsid:
                file_data = list(file_data)
                obsid = filenames_obsid[filename]
                file_data[0].append('obsid')
                [row.append(obsid) for row in file_data[1:]]
                parsed_files_with_obsid.append([file_data, filename, location])
        #Header
        file_to_import_to_db =  [parsed_files_with_obsid[0][0][0]]
        file_to_import_to_db.extend([row for parsed_file in parsed_files_with_obsid for row in parsed_file[0][1:]])

        # Add comment to import:
        #file_to_import_to_db[0].append('comment')
        #comment = ''
        #[row.append(comment) for row in file_to_import_to_db[1:]]

        if not import_all_data:
            file_to_import_to_db = self.filter_dates_from_filedata(file_to_import_to_db, midvatten_utils.get_last_logger_dates())
        if len(file_to_import_to_db) < 2:
            common_utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate('DiverofficeImport', 'No new data existed in the files. Nothing imported.'))
            self.status = 'True'
            common_utils.stop_waiting_cursor()
            return True

        if import_to_db:
            importer = import_data_to_db.midv_data_importer()
            answer = importer.general_import('w_levels_logger', file_to_import_to_db)

        if export_csv:
            path = qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save File', '', 'CSV(*.csv)')
            if path:
                path = ru(path[0])
                common_utils.write_printlist_to_file(path, file_to_import_to_db)

        common_utils.stop_waiting_cursor()

        if self.close_after_import.isChecked():
            self.close()



    @staticmethod
    def parse_diveroffice_file(path, charset, skip_rows_without_water_level=False, begindate=None, enddate=None):
        """ Parses a diveroffice csv file into a string

        :param path: The file name
        :param existing_obsids: A list or tuple with the obsids that exist in the db.
        :param ask_for_names: (True/False) True to ask for location name for every location. False to only ask if the location is not found in existing_obsids.
        :return: A string representing a table file. Including '\n' for newlines.

        Assumptions and limitations:
        * The Location attribute is used as location and added as a column.
        * Values containing ',' is replaced with '.'
        * Rows with missing "Water head[cm]"-data is skipped.

        """
        #These can be set to paritally import files.
        #begindate = datetime.strptime('2016-06-08 20:00:00','%Y-%m-%d %H:%M:%S')
        #enddate = datetime.strptime('2016-06-08 19:00:00','%Y-%m-%d %H:%M:%S')

        #It should be possible to import all cols that exists in the translation dict

        translation_dict_in_order = OrderedDict([('Date/time', 'date_time'),
                                                 ('Water head[cm]', 'head_cm'),
                                                 ('Level[cm]', 'head_cm'),
                                                 ('Temperature[°C]', 'temp_degc'),
                                                 ('Conductivity[mS/cm]', 'cond_mscm'),
                                                 ('1:Conductivity[mS/cm]', 'cond_mscm'),
                                                 ('2:Spec.cond.[mS/cm]', 'cond_mscm'),
                                                 ('Conductivity[ms/cm]', 'cond_mscm'),
                                                 ('1:Conductivity[ms/cm]', 'cond_mscm'),
                                                 ('2:Spec.cond.[ms/cm]', 'cond_mscm')
                                                 ])

        filedata = []
        begin_extraction = False

        data_rows = []
        with io.open(path, 'rt', encoding=str(charset)) as f:
            location = None
            for rawrow in f:
                rawrow = ru(rawrow)
                row = common_utils.lstrip()

                #Try to get location
                if row.startswith('Location'):
                    location = row.split('=')[1].strip()
                    continue

                #Parse eader
                if 'Date/time' in row:
                    begin_extraction = True

                if begin_extraction:
                    if row and not 'end of data' in row.lower():
                        data_rows.append(row)

        if not begin_extraction:
            common_utils.MessagebarAndLog.critical(
                bar_msg=QCoreApplication.translate('DiverofficeImport', "Diveroffice import warning. See log message panel"),
                log_msg=ru(QCoreApplication.translate('DiverofficeImport', "Warning, the file %s \ndid not have Date/time as a header and will be skipped.\nSupported headers are %s"))%(ru(path), ', '.join(list(translation_dict_in_order.keys()))))
            return 'skip'

        if len(data_rows[0].split(',')) > len(data_rows[0].split(';')):
            delimiter = ','
        else:
            delimiter = ';'

        file_header = data_rows[0].split(delimiter)
        nr_of_cols = len(file_header)

        if nr_of_cols < 2:
            common_utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('DiverofficeImport', 'Diveroffice import warning. See log message panel'),
                                                              log_msg=ru(QCoreApplication.translate('DiverofficeImport', 'Delimiter could not be found for file %s or it contained only one column, skipping it.'))%path)
            return 'skip'

        translated_header = [translation_dict_in_order.get(col, None) for col in file_header]
        if 'head_cm' not in translated_header:
            common_utils.MessagebarAndLog.warning(
                bar_msg=QCoreApplication.translate('DiverofficeImport', "Diveroffice import warning. See log message panel"),
                log_msg=ru(QCoreApplication.translate('DiverofficeImport', "Warning, the file %s \ndid not have Water head[cm] as a header.\nMake sure its barocompensated!\nSupported headers are %s"))%(ru(path), ', '.join(list(translation_dict_in_order.keys()))))
            if skip_rows_without_water_level:
                return 'skip'

        new_header = ['date_time', 'head_cm', 'temp_degc', 'cond_mscm']
        colnrs_to_import = [translated_header.index(x) if x in translated_header else None for x in new_header]
        date_col = colnrs_to_import[0]
        filedata.append(new_header)

        errors = set()
        skipped_rows = 0
        for row in data_rows[1:]:
            cols = row.split(delimiter)
            if len(cols) != nr_of_cols:
                return common_utils.ask_user_about_stopping(
                    ru(QCoreApplication.translate('DiverofficeImport', "Failure: The number of data columns in file %s was not equal to the header.\nIs the decimal separator the same as the delimiter?\nDo you want to stop the import? (else it will continue with the next file)"))%path)

            dateformat = find_date_format(cols[date_col])

            if dateformat is not None:
                date = datetime.strptime(cols[date_col], dateformat)

                if begindate is not None:
                    if date < begindate:
                        continue
                if enddate is not None:
                    if date > enddate:
                        continue

                if skip_rows_without_water_level:
                    try:
                        float(cols[translated_header.index('head_cm')].replace(',', '.'))
                    except:
                        skipped_rows += 1
                        continue

                printrow = [datetime.strftime(date,'%Y-%m-%d %H:%M:%S')]

                try:
                    printrow.extend([(str(float(cols[colnr].replace(',', '.'))) if cols[colnr] else '')
                                     if colnr is not None else ''
                                     for colnr in colnrs_to_import if colnr != date_col])
                except ValueError as e:
                    errors.add(ru(QCoreApplication.translate('DiverofficeImport', "parse_diveroffice_file error: %s"))%str(e))
                    continue

                if any(printrow[1:]):
                    filedata.append(printrow)
        if errors:
           common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('DiverofficeImport', 'Error messages while parsing file "%s":\n%s')) % (path, '\n'.join(errors)))

        if len(filedata) < 2:
            return common_utils.ask_user_about_stopping(ru(QCoreApplication.translate('DiverofficeImport', "Failure, parsing failed for file %s\nNo valid data found!\nDo you want to stop the import? (else it will continue with the next file)")) % path)

        filename = os.path.basename(path)

        return filedata, filename, location

    @staticmethod
    def filter_dates_from_filedata(file_data, obsid_last_imported_dates, obsid_header_name='obsid', date_time_header_name='date_time'):
        """
        :param file_data: a list of lists like [['obsid', 'date_time', ...], [obsid1, date_time1, ...]]
        :param obsid_last_imported_dates: a dict like {'obsid1': last_date_in_db, ...}
        :param obsid_header_name: the name of the obsid header
        :param date_time_header_name: the name of the date_time header
        :return: A filtered list with only dates after last date is included for each obsid.

        >>> DiverofficeImport.filter_dates_from_filedata([['obsid', 'date_time'], ['obs1', '2016-09-28'], ['obs1', '2016-09-29']], {'obs1': [('2016-09-28', )]})
        [['obsid', 'date_time'], ['obs1', '2016-09-29']]
        """
        if len(file_data) == 1:
            return file_data

        obsid_idx = file_data[0].index(obsid_header_name)
        date_time_idx = file_data[0].index(date_time_header_name)
        filtered_file_data = [row for row in file_data[1:] if datestring_to_date(row[date_time_idx]) > datestring_to_date(obsid_last_imported_dates.get(row[obsid_idx], [('0001-01-01 00:00:00',)])[0][0])]

        filtered_file_data.reverse()
        filtered_file_data.append(file_data[0])
        filtered_file_data.reverse()
        return filtered_file_data

    def add_row(self, a_widget):
        """
        :param: a_widget:
        """
        self.main_vertical_layout.addWidget(a_widget)


class CheckboxAndExplanation(VRowEntry):
    def __init__(self, checkbox_label, explanation=None):
        super(CheckboxAndExplanation, self).__init__()
        self.checkbox = qgis.PyQt.QtWidgets.QCheckBox(checkbox_label)
        self.layout.addWidget(self.checkbox)
        self.label = qgis.PyQt.QtWidgets.QLabel()

        if explanation:
            self.label.setText(explanation)
            self.layout.addWidget(self.label)

        #self.layout.addStretch()

    @property
    def checked(self):
        return self.checkbox.isChecked()

    @checked.setter
    def checked(self, check=True):
        self.checkbox.setChecked(check)

