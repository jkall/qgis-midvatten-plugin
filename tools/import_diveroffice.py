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

import io
import os
from collections import OrderedDict
from datetime import datetime

import PyQt4
from PyQt4.QtCore import QCoreApplication

import import_data_to_db
import midvatten_utils as utils
from date_utils import find_date_format, datestring_to_date
from gui_utils import VRowEntry, get_line, DateTimeFilter
from midvatten_utils import returnunicode as ru

import_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]

class DiverofficeImport(PyQt4.QtGui.QMainWindow, import_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(QCoreApplication.translate('DiverofficeImport', "Diveroffice import"))  # Set the title for the dialog
        self.table_chooser = None
        self.file_data = None
        self.status = True
        self.parse_func = self.parse_diveroffice_file

    def select_files_and_load_gui(self):
        self.files = self.select_files()
        if not self.files:
            raise utils.UserInterruptError()

        self.date_time_filter = DateTimeFilter(calendar=True)
        self.add_row(self.date_time_filter.widget)

        self.add_row(get_line())

        self.skip_rows = CheckboxAndExplanation(QCoreApplication.translate('DiverofficeImport', u'Skip rows without water level'),
                                                QCoreApplication.translate('DiverofficeImport', u'Checked = Rows without a value for columns Water head[cm] or Level[cm] will be skipped.'))
        self.skip_rows.checked = True
        self.add_row(self.skip_rows.widget)
        self.add_row(get_line())
        self.confirm_names = CheckboxAndExplanation(QCoreApplication.translate('DiverofficeImport', u'Confirm each logger obsid before import'),
                                                    QCoreApplication.translate('DiverofficeImport', u'Checked = The obsid will be requested of the user for every file.\n\n') +
                                                    QCoreApplication.translate('DiverofficeImport', u'Unchecked = the location attribute, both as is and capitalized, in the\n') +
                                                    QCoreApplication.translate('DiverofficeImport', u'file will be matched against obsids in the database.\n\n') +
                                                    QCoreApplication.translate('DiverofficeImport', u'In both case, obsid will be requested of the user if no match in the database is found.'))
        self.confirm_names.checked = True
        self.add_row(self.confirm_names.widget)
        self.add_row(get_line())
        self.import_all_data = CheckboxAndExplanation(QCoreApplication.translate('DiverofficeImport', u'Import all data'),
                                                      QCoreApplication.translate('DiverofficeImport', u'Checked = any data not matching an exact datetime in the database\n') +
                                                      QCoreApplication.translate('DiverofficeImport', u'for the corresponding obsid will be imported.\n\n') +
                                                      QCoreApplication.translate('DiverofficeImport', u'Unchecked = only new data after the latest date in the database,\n') +
                                                      QCoreApplication.translate('DiverofficeImport', u'for each observation point, will be imported.'))
        self.import_all_data.checked = False
        self.add_row(self.import_all_data.widget)

        self.close_after_import = PyQt4.QtGui.QCheckBox(ru(QCoreApplication.translate(u'DiverofficeImport', u'Close dialog after import')))
        self.close_after_import.setChecked(True)
        self.gridLayout_buttons.addWidget(self.close_after_import, 0, 0)

        self.start_import_button = PyQt4.QtGui.QPushButton(QCoreApplication.translate('DiverofficeImport', u'Start import'))
        self.gridLayout_buttons.addWidget(self.start_import_button, 1, 0)
        self.connect(self.start_import_button, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.start_import(files=self.files, skip_rows_without_water_level=self.skip_rows.checked, confirm_names=self.confirm_names.checked, import_all_data=self.import_all_data.checked, from_date=self.date_time_filter.from_date, to_date=self.date_time_filter.to_date))

        self.gridLayout_buttons.setRowStretch(2, 1)

        self.show()


    def select_files(self):
        self.charsetchoosen = utils.ask_for_charset(default_charset='cp1252')
        if not self.charsetchoosen:
            self.status = 'True'
            return u'cancel'

        files = utils.select_files(only_one_file=False, extension="csv (*.csv)")
        return files

    @utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self, files, skip_rows_without_water_level, confirm_names, import_all_data, from_date=None, to_date=None):
        """
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...
        parsed_files = []
        for selected_file in files:
            res = self.parse_func(path=selected_file, charset=self.charsetchoosen, skip_rows_without_water_level=skip_rows_without_water_level, begindate=from_date, enddate=to_date)
            if res == u'cancel':
                self.status = True
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return res
            elif res in (u'skip', u'ignore'):
                continue

            try:
                file_data, filename, location = res
            except Exception as e:
                utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('DiverofficeImport', u'Import error, see log message panel'),
                                               log_msg=ru(QCoreApplication.translate('DiverofficeImport', u'File %s could not be parsed. Msg:\n%s'))%(selected_file, str(e)))
                continue
            parsed_files.append((file_data, filename, location))

        if len(parsed_files) == 0:
            utils.MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('DiverofficeImport', u"Import Failure: No files imported"""))
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return

        #Add obsid to all parsed filedatas by asking the user for it.
        filename_location_obsid = [[u'filename', u'location', u'obsid']]
        filename_location_obsid.extend([[parsed_file[1], parsed_file[2], parsed_file[2]] for parsed_file in parsed_files])

        if confirm_names:
            try_capitalize = False
        else:
            try_capitalize = True

        existing_obsids = utils.get_all_obsids()
        filename_location_obsid = utils.filter_nonexisting_values_and_ask(file_data=filename_location_obsid, header_value=u'obsid', existing_values=existing_obsids, try_capitalize=try_capitalize, always_ask_user=confirm_names)

        if len(filename_location_obsid) < 2:
            utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('DiverofficeImport', u'Warning. All files were skipped, nothing imported!'))
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return False

        filenames_obsid = dict([(x[0], x[2]) for x in filename_location_obsid[1:]])

        parsed_files_with_obsid = []
        for file_data, filename, location in parsed_files:
            if filename in filenames_obsid:
                file_data = list(file_data)
                obsid = filenames_obsid[filename]
                file_data[0].append(u'obsid')
                [row.append(obsid) for row in file_data[1:]]
                parsed_files_with_obsid.append([file_data, filename, location])
        #Header
        file_to_import_to_db =  [parsed_files_with_obsid[0][0][0]]
        file_to_import_to_db.extend([row for parsed_file in parsed_files_with_obsid for row in parsed_file[0][1:]])

        if not import_all_data:
            file_to_import_to_db = self.filter_dates_from_filedata(file_to_import_to_db, utils.get_last_logger_dates())
        if len(file_to_import_to_db) < 2:
            utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate('DiverofficeImport', u'No new data existed in the files. Nothing imported.'))
            self.status = 'True'
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return True

        importer = import_data_to_db.midv_data_importer()
        answer = importer.general_import(u'w_levels_logger', file_to_import_to_db)

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        importer.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

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
        #begindate = datetime.strptime(u'2016-06-08 20:00:00',u'%Y-%m-%d %H:%M:%S')
        #enddate = datetime.strptime(u'2016-06-08 19:00:00',u'%Y-%m-%d %H:%M:%S')

        #It should be possible to import all cols that exists in the translation dict

        translation_dict_in_order = OrderedDict([(u'Date/time', u'date_time'),
                                                 (u'Water head[cm]', u'head_cm'),
                                                 (u'Level[cm]', u'head_cm'),
                                                 (u'Temperature[°C]', u'temp_degc'),
                                                 (u'Conductivity[mS/cm]', u'cond_mscm'),
                                                 (u'1:Conductivity[mS/cm]', u'cond_mscm'),
                                                 (u'2:Spec.cond.[mS/cm]', u'cond_mscm')])

        filedata = []
        begin_extraction = False

        data_rows = []
        with io.open(path, u'rt', encoding=str(charset)) as f:
            location = None
            for rawrow in f:
                rawrow = ru(rawrow)
                row = rawrow.rstrip(u'\n').rstrip(u'\r').lstrip()

                #Try to get location
                if row.startswith(u'Location'):
                    location = row.split(u'=')[1].strip()
                    continue

                #Parse eader
                if u'Date/time' in row:
                    begin_extraction = True

                if begin_extraction:
                    if row and not u'end of data' in row.lower():
                        data_rows.append(row)

        if not begin_extraction:
            utils.MessagebarAndLog.critical(
                bar_msg=QCoreApplication.translate('DiverofficeImport', u"Diveroffice import warning. See log message panel"),
                log_msg=ru(QCoreApplication.translate('DiverofficeImport', u"Warning, the file %s \ndid not have Date/time as a header and will be skipped.\nSupported headers are %s"))%(ru(path), u', '.join(translation_dict_in_order.keys())))
            return u'skip'

        if len(data_rows[0].split(u',')) > len(data_rows[0].split(u';')):
            delimiter = u','
        else:
            delimiter = u';'

        file_header = data_rows[0].split(delimiter)
        nr_of_cols = len(file_header)

        if nr_of_cols < 2:
            utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('DiverofficeImport', u'Diveroffice import warning. See log message panel'),
                                           log_msg=ru(QCoreApplication.translate('DiverofficeImport', u'Delimiter could not be found for file %s or it contained only one column, skipping it.'))%path)
            return u'skip'

        translated_header = [translation_dict_in_order.get(col, None) for col in file_header]
        if u'head_cm' not in translated_header:
            utils.MessagebarAndLog.warning(
                bar_msg=QCoreApplication.translate('DiverofficeImport', u"Diveroffice import warning. See log message panel"),
                log_msg=ru(QCoreApplication.translate('DiverofficeImport', u"Warning, the file %s \ndid not have Water head[cm] as a header.\nMake sure its barocompensated!\nSupported headers are %s"))%(ru(path), u', '.join(translation_dict_in_order.keys())))
            if skip_rows_without_water_level:
                return u'skip'

        new_header = [u'date_time', u'head_cm', u'temp_degc', u'cond_mscm']
        colnrs_to_import = [translated_header.index(x) if x in translated_header else None for x in new_header]

        date_col = colnrs_to_import[0]
        filedata.append(new_header)

        errors = set()
        skipped_rows = 0
        for row in data_rows[1:]:
            cols = row.split(delimiter)
            if len(cols) != nr_of_cols:
                return utils.ask_user_about_stopping(
                    ru(QCoreApplication.translate('DiverofficeImport', u"Failure: The number of data columns in file %s was not equal to the header.\nIs the decimal separator the same as the delimiter?\nDo you want to stop the import? (else it will continue with the next file)"))%path)

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
                        float(cols[translated_header.index(u'head_cm')].replace(u',', u'.'))
                    except:
                        skipped_rows += 1
                        continue

                printrow = [datetime.strftime(date,u'%Y-%m-%d %H:%M:%S')]

                try:
                    printrow.extend([(str(float(cols[colnr].replace(u',', u'.'))) if cols[colnr] else u'')
                                     if colnr is not None else u''
                                     for colnr in colnrs_to_import if colnr != date_col])
                except ValueError as e:
                    errors.add(ru(QCoreApplication.translate('DiverofficeImport', "parse_diveroffice_file error: %s"))%str(e))
                    continue

                if any(printrow[1:]):
                    filedata.append(printrow)
        if errors:
           utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('DiverofficeImport', u'Error messages while parsing file "%s":\n%s'))%(path, u'\n'.join(errors)))

        if len(filedata) < 2:
            return utils.ask_user_about_stopping(ru(QCoreApplication.translate('DiverofficeImport', u"Failure, parsing failed for file %s\nNo valid data found!\nDo you want to stop the import? (else it will continue with the next file)"))%path)

        filename = os.path.basename(path)

        return filedata, filename, location

    @staticmethod
    def filter_dates_from_filedata(file_data, obsid_last_imported_dates, obsid_header_name=u'obsid', date_time_header_name=u'date_time'):
        """
        :param file_data: a list of lists like [[u'obsid', u'date_time', ...], [obsid1, date_time1, ...]]
        :param obsid_last_imported_dates: a dict like {u'obsid1': last_date_in_db, ...}
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
        filtered_file_data = [row for row in file_data[1:] if datestring_to_date(row[date_time_idx]) > datestring_to_date(obsid_last_imported_dates.get(row[obsid_idx], [(u'0001-01-01 00:00:00',)])[0][0])]

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
        self.checkbox = PyQt4.QtGui.QCheckBox(checkbox_label)
        self.layout.addWidget(self.checkbox)
        self.label = PyQt4.QtGui.QLabel()

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

