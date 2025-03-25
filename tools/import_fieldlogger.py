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
from queue import Queue
from collections import OrderedDict
from datetime import datetime
from functools import partial
from time import sleep


import qgis.PyQt
from qgis.PyQt import QtCore, QtWidgets, uic
from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools.utils import common_utils, midvatten_utils, db_utils
import midvatten.tools.import_data_to_db as import_data_to_db
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools.utils.date_utils import datestring_to_date, dateshift
import midvatten.definitions.midvatten_defs as defs
from midvatten.tools.utils.gui_utils import SplitterWithHandel, RowEntry, RowEntryGrid, VRowEntry, DateTimeFilter, \
    set_combobox


import_fieldlogger_ui_dialog = uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]

class FieldloggerImport(QtWidgets.QMainWindow, import_fieldlogger_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.status = True
        self.main_vertical_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.main_vertical_layout.setContentsMargins(0, 0, 0, 0)

    @common_utils.general_exception_handler
    def parse_observations_and_populate_gui(self):
        splitter = SplitterWithHandel(QtCore.Qt.Vertical)
        self.add_row(splitter)
        self.main_vertical_layout.setAlignment(splitter, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.observations = self.select_file_and_parse_rows(self.parse_rows)
        if self.observations is None:
            return None

        #Filters and general settings
        settings_widget = QtWidgets.QWidget()
        settings_layout = QtWidgets.QVBoxLayout()
        settings_widget.setLayout(settings_layout)
        splitter.addWidget(settings_widget)
        self.settings = []
        self.settings.append(StaffQuestion())
        self.settings.append(DateShiftQuestion())
        self.date_time_filter = DateTimeFilter()
        self.date_time_filter.date_time_filter_update_button = QtWidgets.QPushButton(QCoreApplication.translate('FieldloggerImport',
                                                                                                 'Filter dates'))
        self.date_time_filter.date_time_filter_update_button.setToolTip(ru(QCoreApplication.translate('FieldloggerImport',
                                                                                     'Filter observations using from and to dates and update gui.')))
        self.date_time_filter.layout().addWidget(self.date_time_filter.date_time_filter_update_button)

        self.settings.append(self.date_time_filter)
        for setting in self.settings:
            if isinstance(setting, QtWidgets.QWidget):
                settings_layout.addWidget(setting)
        #self.add_line(settings_layout)

        #Settings with own loop gets self.observations to work on.
        self.settings_with_own_loop = [ObsidFilter()]

        #Sublocations
        sublocations = [observation['sublocation'] for observation in self.observations]
        self.sublocation_filter = SublocationFilter(sublocations)
        self.settings.append(self.sublocation_filter)
        splitter.addWidget(self.sublocation_filter)
        #sublocations_layout.addWidget(self.sublocation_filter.widget)
        #self.add_line(sublocations_layout)

        self.stored_settingskey = 'fieldlogger_import_parameter_settings'
        self.stored_settings = common_utils.get_stored_settings(self.ms, self.stored_settingskey)

        #Input fields
        self.input_fields = InputFields()
        self.input_fields.update_parameter_imports_queue(self.observations, self.stored_settings)

        splitter.addWidget(self.input_fields)

        #General buttons
        self.save_settings_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('FieldloggerImport', 'Save settings')))
        self.gridLayout_buttons.addWidget(self.save_settings_button, 0, 0)
        self.save_settings_button.clicked.connect(
                         lambda : [x() for x in [lambda : self.input_fields.update_stored_settings(self.stored_settings),
                                                 lambda : common_utils.save_stored_settings(self.ms, self.stored_settings, self.stored_settingskey)]])

        self.clear_settings_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('FieldloggerImport', 'Clear settings')))
        self.clear_settings_button.setToolTip(ru(QCoreApplication.translate('FieldloggerImport', 'Clear all parameter settings\nReopen Fieldlogger import gui to have it reset,\nor press "Save settings" to undo.')))
        self.gridLayout_buttons.addWidget(self.clear_settings_button, 1, 0)
        self.clear_settings_button.clicked.connect(
                     lambda: [x() for x in [lambda: common_utils.save_stored_settings(self.ms, [], self.stored_settingskey),
                                            lambda: common_utils.pop_up_info(ru(QCoreApplication.translate('FieldloggerImport', 'Settings cleared. Restart import Fieldlogger dialog')))]])

        self.close_after_import = QtWidgets.QCheckBox(ru(QCoreApplication.translate('FieldloggerImport', 'Close dialog after import')))
        self.close_after_import.setChecked(True)
        self.gridLayout_buttons.addWidget(self.close_after_import, 2, 0)

        self.start_import_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('FieldloggerImport', 'Start import')))
        self.gridLayout_buttons.addWidget(self.start_import_button, 3, 0)
        self.start_import_button.clicked.connect(lambda : self.start_import(self.observations))

        self.date_time_filter.date_time_filter_update_button.clicked.connect(
                     self.update_sublocations_and_inputfields_on_date_change)

        #Button click first filters data from the settings and then updates input fields.
        self.input_fields.update_parameters_button.clicked.connect(lambda: self.update_input_fields_from_button())

        self.gridLayout_buttons.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.setGeometry(500, 150, 1100, 700)

        self.show()

    @staticmethod
    @common_utils.general_exception_handler
    def select_file_and_parse_rows(row_parser):
        filenames = midvatten_utils.select_files(only_one_file=False, extension="csv (*.csv)")
        observations = []
        for filename in filenames:
            filename = ru(filename)
            supported_encodings = ['utf-8', 'cp1252']
            for encoding in supported_encodings:
                try:
                    delimiter = common_utils.get_delimiter(filename=filename, charset=encoding, delimiters=[';', ','], num_fields=5)
                    if delimiter is None:
                        return None

                    with io.open(filename, 'rt', encoding=encoding) as f:
                        rows = f.readlines()
                        observations.extend(row_parser(rows, delimiter))

                except UnicodeDecodeError:
                    continue
                else:
                    break

        #Remove duplicates
        observations_no_duplicates = []
        for possible_duplicate in observations:
            as_tuple = possible_duplicate.items()
            if as_tuple not in observations_no_duplicates:
                observations_no_duplicates.append(as_tuple)
        observations = [dict(x) for x in observations_no_duplicates]

        return observations

    @staticmethod
    def parse_rows(f, delimiter=';'):
        """
        Parses rows from fieldlogger format into a dict
        :param f: File_data, often an open file or a list of rows without header
        :return: a list of dicts like [{date_time: x, sublocation: y, parametername: z, value: o}, ...]

        """
        observations = []

        header_rownr = None
        for rownr, rawrow in enumerate(f):
            row = rawrow.rstrip('\n').strip().lower()
            cols = row.split(delimiter)
            if not row:
                continue
            else:
                if 'location' in row:
                    try:
                        location_idx = cols.index('location')
                        date_idx = cols.index('date')
                        time_idx = cols.index('time')
                        type_idx = cols.index('type')
                        value_idx = cols.index('value')
                    except ValueError:
                        pass
                    else:
                        header_rownr = rownr
                else:
                    # Header was not the first row with data.
                    # Use column
                    break

        for rownr, rawrow in enumerate(f):
            observation = {}
            row = rawrow.rstrip('\n').strip()
            cols = row.split(delimiter)
            if not row:
                continue
            if header_rownr is None and not rownr:
                # Assume that the first row is the header row.
                continue
            if header_rownr is not None and rownr <= header_rownr:
                continue

            if header_rownr is not None:
                observation['sublocation'] = cols[location_idx]
                date = cols[date_idx]
                time = cols[time_idx]
                observation['date_time'] = datestring_to_date(' '.join([date, time]))
                observation['value'] = cols[value_idx]
                observation['parametername'] = cols[type_idx]
            else:
                # Assume it's structured as fieldlogger measurement file.
                observation['sublocation'] = cols[0]
                date = cols[1]
                time = cols[2]
                observation['date_time'] = datestring_to_date(' '.join([date, time]))
                observation['value'] = cols[3]
                observation['parametername'] = cols[4]

            if observation['value']:
                observations.append(observation)
        return observations

    def add_row(self, a_widget):
        """
        :param: a_widget:
        """
        self.main_vertical_layout.addWidget(a_widget)

    def add_line(self, layout=None):
        """ just adds a line"""
        #horizontalLineWidget = PyQt4.QtWidgets.QWidget()
        #horizontalLineWidget.setFixedHeight(2)
        #horizontalLineWidget.setSizePolicy(PyQt4.QtWidgets.QSizePolicy.Expanding, PyQt4.QtWidgets.QSizePolicy.Fixed)
        #horizontalLineWidget.setStyleSheet(PyQt4.QtCore.QString("background-color: #c0c0c0;"));
        line = QtWidgets.QFrame()
        #line.setObjectName(QString::fromUtf8("line"));
        line.setGeometry(QtCore.QRect(320, 150, 118, 3))
        line.setFrameShape(QtWidgets.QFrame.HLine);
        line.setFrameShadow(QtWidgets.QFrame.Sunken);
        if layout is None:
            self.add_row(line)
        else:
            layout.addWidget(line)

    @staticmethod
    def sublocation_to_groups(sublocations, delimiter='.'):
        """
        This method splits sublocation using a splitter, default to u'.'. Each list position is grouped to lists
         containing all distinct values. It's finally stored in a dict with the lenght of the splitted group as key.
        :param: sublocations: A list of sublocations, ex: ['c', 'a.1', 'a.2', 'b.1.1']
        :return: a dict like {1: [set(distinct values)], 2: [set(distinct values)}, set(), set()], ...)
        """
        sublocation_groups = {}
        for sublocation in sublocations:
            splitted = sublocation.split(delimiter)
            length = len(splitted)
            for index in range(length):
                #a dict like {1: [set()], 2: [set(), set()], ...}
                sublocation_groups.setdefault(length, [set()for i in range(length)])[index].add(splitted[index])
        return sublocation_groups

    def update_sublocations_and_inputfields_on_date_change(self):
        sleep(0.2)
        observations = copy.deepcopy(self.observations)
        date_time_filter = self.date_time_filter
        sublocation_filter = self.sublocation_filter
        input_fields = self.input_fields
        stored_settings = self.stored_settings

        observations = copy.deepcopy(observations)
        observations = self.filter_by_settings_using_shared_loop(observations, [date_time_filter])
        sublocations = [observation['sublocation'] for observation in observations]
        sublocation_filter.update_sublocations(sublocations)
        observations = self.filter_by_settings_using_shared_loop(observations, [sublocation_filter])
        input_fields.update_parameter_imports_queue(observations, stored_settings, staff=self.get_staff())

    def get_staff(self):
        _staff = [x.staff for x in self.settings if isinstance(x, StaffQuestion)]
        if _staff:
            staff = _staff[0]
        else:
            staff = None
        return staff

    @common_utils.general_exception_handler
    def update_input_fields_from_button(self):
        self.input_fields.update_parameter_imports_queue(self.filter_by_settings_using_shared_loop(self.observations, self.settings), self.stored_settings, staff=self.get_staff())

    @staticmethod
    def prepare_w_levels_data(observations):
        """
        Produces a filestring with columns "obsid, date_time, meas, comment" and imports it
        :param obsdict: a dict like {obsid: {date_time: {parameter: value}}}
        :return: None
        """
        file_data_list = [['obsid', 'date_time', 'meas', 'h_toc', 'level_masl', 'comment']]
        for observation in observations:
            obsid = observation['obsid']
            date_time = datetime.strftime(observation['date_time'], '%Y-%m-%d %H:%M:%S')
            level_masl = observation.get('level_masl', '').replace(',', '.')
            h_toc = observation.get('h_toc', '').replace(',', '.')
            meas = observation.get('meas', '').replace(',', '.')
            comment = observation.get('comment', '')

            file_data_list.append([obsid, date_time, meas, h_toc, level_masl, comment])
        if len(file_data_list) < 2:
            return None
        return file_data_list

    @staticmethod
    def prepare_comments_data(observations):
        file_data_list = [['obsid', 'date_time', 'comment', 'staff']]
        for observation in observations:

            if observation.get('skip_comment_import', False):
                continue
            obsid = observation['obsid']
            date_time = datetime.strftime(observation['date_time'], '%Y-%m-%d %H:%M:%S')
            comment = observation['value']
            staff = observation['staff']
            file_data_list.append([obsid, date_time, comment, staff])
        if len(file_data_list) < 2:
            return None
        return file_data_list

    @staticmethod
    def prepare_w_flow_data(observations):
        """
        Produces a filestring with columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :return:
        """

        file_data_list = [['obsid', 'instrumentid', 'flowtype', 'date_time', 'reading', 'unit', 'comment']]
        instrumentids = midvatten_utils.get_last_used_flow_instruments()[1]
        already_asked_instruments = {}

        for observation in observations:
            obsid = observation['obsid']
            flowtype = observation['flowtype']
            date_time = datetime.strftime(observation['date_time'], '%Y-%m-%d %H:%M:%S')
            unit = observation['unit']
            sublocation = observation['sublocation']

            instrumentid = already_asked_instruments.get(sublocation, None)
            if instrumentid is None:
                instrumentids_for_obsid = instrumentids.get(obsid, None)
                if instrumentids_for_obsid is None:
                    last_used_instrumentid = ['']
                else:
                    last_used_instrumentid = sorted(
                        [(_date_time, _instrumentid) for _flowtype, _instrumentid, _date_time in instrumentids[obsid] if
                         (_flowtype == flowtype)], reverse=True)
                    if last_used_instrumentid:
                        last_used_instrumentid = [x[1] for x in last_used_instrumentid]
                    else:
                        last_used_instrumentid = ['']
                question = common_utils.NotFoundQuestion(dialogtitle=ru(QCoreApplication.translate('FieldloggerImport', 'Submit instrument id')),
                                                                     msg=''.join([ru(QCoreApplication.translate('FieldloggerImport', 'Submit the instrument id for the measurement:\n ')),
                                                                ', '.join([sublocation, obsid, date_time, flowtype, unit])]),
                                                                     existing_list=last_used_instrumentid,
                                                                     default_value=last_used_instrumentid[0],
                                                                     combobox_label=ru(QCoreApplication.translate('FieldloggerImport', 'Instrument id:s in database for obsid %s.\nThe last used instrument id for obsid %s is prefilled:'))%(obsid, obsid))
                answer = question.answer
                if answer == 'cancel':
                    raise common_utils.UserInterruptError()
                instrumentid = ru(question.value)
                already_asked_instruments[sublocation] = instrumentid

            reading = observation['value'].replace(',', '.')

            comment = observation.get('comment', '')
            file_data_list.append([obsid, instrumentid, flowtype, date_time, reading, unit, comment])
        if len(file_data_list) < 2:
            return None
        return file_data_list

    @staticmethod
    def prepare_w_qual_field_data(observations):
        """
        Produces a filestring with columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :param quality_or_water_sample: Word written at user question: 'quality' or 'water sample'.
        :return:
        """
        file_data_list = [['obsid', 'staff', 'date_time', 'instrument', 'parameter', 'reading_num', 'reading_txt', 'unit', 'depth', 'comment']]

        for observation in observations:
            obsid = observation['obsid']
            staff = observation['staff']
            date_time = datetime.strftime(observation['date_time'], '%Y-%m-%d %H:%M:%S')
            instrument = observation['instrument']
            parameter = observation['parameter']
            reading_num = observation['value'].replace(',', '.')
            reading_txt = observation['value']
            unit = observation['unit']
            depth = observation.get('depth', '').replace(',', '.')
            comment = observation.get('comment', '')
            file_data_list.append([obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment])
        if len(file_data_list) < 2:
            return None
        return file_data_list

    @staticmethod
    def filter_by_settings_using_shared_loop(observations, settings):

        observations = copy.deepcopy(observations)
        filtered_observations = []
        for observation in observations:
            for setting in settings:
                observation = setting.alter_data(observation)
                if observation is None:
                    break
            if observation is not None:
                filtered_observations.append(observation)
        observations = filtered_observations
        return observations

    @staticmethod
    def filter_by_settings_using_own_loop(observations, settings_with_own_loop):

        observations = copy.deepcopy(observations)
        for setting in settings_with_own_loop:
            observations = setting.alter_data(observations)
        return observations

    @common_utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self, observations):
        """

        :param observations:
        :return:
        """
        observations = copy.deepcopy(observations)

        #Start by saving the parameter settings
        self.input_fields.update_stored_settings(self.stored_settings)
        common_utils.save_stored_settings(self.ms, self.stored_settings, self.stored_settingskey)

        chosen_methods = [import_method_chooser.import_method for import_method_chooser in list(self.input_fields.parameter_imports.values())
                          if import_method_chooser.import_method]
        if not chosen_methods:
            common_utils.pop_up_info(ru(QCoreApplication.translate('FieldloggerImport', "Must choose at least one parameter import method")))
            common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('FieldloggerImport', "No parameter import method chosen")))
            return None

        #Update the observations using the general settings, filters and parameter settings
        observations = self.input_fields.filter_import_methods_not_set(observations)
        observations = self.filter_by_settings_using_shared_loop(observations, self.settings)
        observations = self.filter_by_settings_using_own_loop(observations, self.settings_with_own_loop)
        observations = self.input_fields.update_observations(observations)

        if not observations:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('FieldloggerImport', "No observations left to import after filtering")))
            return None

        observations_importmethods = self.input_fields.get_observations_importmethods(observations)

        importer = import_data_to_db.midv_data_importer()

        data_preparers = {'w_levels': self.prepare_w_levels_data,
                          'w_flow': self.prepare_w_flow_data,
                          'w_qual_field': self.prepare_w_qual_field_data,
                          'comments': self.prepare_comments_data,
                          'w_qual_field_depth': lambda x: None}

        for import_method, observations in sorted(observations_importmethods.items()):
            if import_method:
                file_data = data_preparers[import_method](observations)
                if file_data is None:
                    continue

                importer.general_import(file_data=file_data, dest_table=import_method)

        if self.close_after_import.isChecked():
            self.close()
        common_utils.stop_waiting_cursor()


class ObsidFilter(object):
    def __init__(self):
        self.obsid_rename_dict = {}
        pass

    def alter_data(self, observations):
        observations = copy.deepcopy(observations)
        existing_obsids = db_utils.get_all_obsids()

        for observation in observations:
            observation['obsid'] = observation['sublocation'].split('.')[0]

        obsids = [list(x) for x in sorted(set([(observation['obsid'], observation['obsid']) for observation in observations if observation['obsid'] not in self.obsid_rename_dict]))]
        if obsids:
            obsids.reverse()
            obsids.append(['old_obsid', 'new_obsid'])
            obsids.reverse()

            answer = common_utils.filter_nonexisting_values_and_ask(obsids, 'new_obsid', existing_values=existing_obsids, try_capitalize=False)

            if answer is not None:
                if isinstance(answer, (list, tuple)):
                    if len(answer) > 1:
                        self.obsid_rename_dict.update(dict([(old_obsid_new_obsid[0], old_obsid_new_obsid[1]) for old_obsid_new_obsid in answer[1:]]))

        #Filter and rename obsids
        if self.obsid_rename_dict:
            [observation.update({'obsid': self.obsid_rename_dict.get(observation['obsid'], None)})
                for observation in observations]
            observations = [observation for observation in observations if all([observation['obsid'] is not None, observation['obsid']])]

        if len(observations) == 0:
            raise common_utils.UsageError(ru(QCoreApplication.translate('ObsidFilter', 'No observations returned from obsid verification. Were all skipped?')))
        return observations


class StaffQuestion(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qgis.PyQt.QtWidgets.QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.label = QtWidgets.QLabel(ru(QCoreApplication.translate('StaffQuestion', 'Staff who did the measurement')))
        self.existing_staff_combobox = default_combobox()
        existing_staff = sorted(defs.staff_list()[1])
        self.existing_staff_combobox.addItems(existing_staff)

        for widget in [self.label, self.existing_staff_combobox]:
            self.layout().addWidget(widget)

    @property
    def staff(self):
        return ru(self.existing_staff_combobox.currentText())

    @staff.setter
    def staff(self, value):
        self.existing_staff_combobox.setEditText(value)

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        if self.staff is None or not self.staff:
            raise common_utils.UsageError(ru(QCoreApplication.translate('StaffQuestion', 'Import error, staff not given')))

        observation['staff'] = self.staff
        return observation


class DateShiftQuestion(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qgis.PyQt.QtWidgets.QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.label = QtWidgets.QLabel(ru(QCoreApplication.translate('DateShiftQuestion', 'Shift dates, supported format ex. "%s":'))%'-1 hours')
        self.dateshift_lineedit = QtWidgets.QLineEdit()
        self.dateshift_lineedit.setText('0 hours')

        for widget in [self.label, self.dateshift_lineedit]:
            self.layout().addWidget(widget)

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        shift_specification = ru(self.dateshift_lineedit.text())

        step_steplength = shift_specification.split(' ')
        failed = False

        bar_msg = ru(QCoreApplication.translate('DateShiftQuestion', 'Dateshift specification wrong format, se log message panel'))

        log_msg = (ru(QCoreApplication.translate('DateShiftQuestion', 'Dateshift specification must be made using format "step step_length", ex: "%s", "%s", "%s" etc.\nSupported step lengths: %s'))%('0 hours', '-1 hours', '-1 days', 'microseconds, milliseconds, seconds, minutes, hours, days, weeks.'))

        if len(step_steplength) != 2:
            common_utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            raise common_utils.UsageError()
        try:
            step = float(step_steplength[0])
            steplength = step_steplength[1]
        except:
            common_utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            raise common_utils.UsageError()

        test_shift = dateshift('2015-02-01', step, steplength)
        if test_shift == None:
            common_utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            raise common_utils.UsageError()

        observation['date_time'] = dateshift(observation['date_time'], step, steplength)

        return observation


class SublocationFilter(QtWidgets.QWidget):
    def __init__(self, sublocations, parent=None):
        """

        :param sublocations: a list like ['a.b', '1.2.3', ...]
        """
        super().__init__(parent)
        self.setLayout(qgis.PyQt.QtWidgets.QVBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.layout().addWidget(QtWidgets.QLabel(
            ru(QCoreApplication.translate('FieldloggerImport', 'Select sublocations to import:'))))

        self.table = QtWidgets.QTableWidget()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.MinimumExpanding)
        self.table.sizePolicy().setVerticalStretch(2)
        self.table.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.MinimumExpanding)

        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)

        self.update_sublocations(sublocations)
        self.layout().addWidget(self.table)
        self.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.MinimumExpanding)
        self.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.MinimumExpanding)

    def set_selection(self, sublocations, true_or_false):
        """

        :param sublocations: an iterable, ex: list, tuple etc. of sublocation strings
        :param true_or_false: True/False. Sets selection to this
        :return:
        """
        for sublocation in sublocations:
            self.table.setItemSelected(self.table_items[sublocation], true_or_false)

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        sublocation = observation['sublocation']

        if self.table_items[sublocation].isSelected():
            return observation
        else:
            return None

    def update_sublocations(self, sublocations):
        self.table.clear()

        sublocations = sorted(list(set(sublocations)))

        if not sublocations:
            num_rows = 1
            num_columns = 1
        else:
            num_rows = len(sublocations)
            #num_columns = reduce(lambda x, y: max(x , len(y.split('.'))), sublocations, 0)
            num_columns = max([len(sublocation.split('.')) for sublocation in sublocations])

        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_columns)

        self.table_items = {}
        for rownr, sublocation in enumerate(sublocations):
            for colnr, value in enumerate(sublocation.split('.')):
                tablewidgetitem = QtWidgets.QTableWidgetItem(value)
                if sublocation not in self.table_items:
                    self.table_items[sublocation] = tablewidgetitem
                self.table.setItem(rownr, colnr, tablewidgetitem)

        self.table.resizeColumnsToContents()

        self.table.selectAll()


class InputFields(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QtWidgets.QVBoxLayout())

        self.active_updater = False
        self.update_queue = Queue()
        self.update_queue_working = False

        self.layout().addWidget(QtWidgets.QLabel(ru(QCoreApplication.translate('InputFields', 'Specify import methods for input fields'))))

        self.parameter_imports = OrderedDict()

        #This button has to get filtered observations as input, so it has to be
        #connected elsewhere.
        self.update_parameters_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('InputFields', 'Update input fields')))
        self.update_parameters_button.setToolTip(ru(QCoreApplication.translate('InputFields', 'Update input fields using the observations remaining after filtering by date and sublocation selection.')))
        self.layout().addWidget(self.update_parameters_button)

    def update_parameter_imports_queue(self, *args, **kwargs):
        if self.update_queue_working:
            self.update_queue.put(partial(self.update_parameter_imports, *args, **kwargs))
            return
        else:
            self.update_queue_working = True
            self.update_queue.put(partial(self.update_parameter_imports, *args, **kwargs))
            while not self.update_queue.empty():
                upd_func = self.update_queue.get()
                upd_func()
                self.update_queue.task_done()
            else:
                self.update_queue_working = False


    def update_parameter_imports(self, observations, stored_settings=None, staff=None):

        if stored_settings is None:
            stored_settings = []

        #Remove and close all widgets
        while self.parameter_imports:
            try:
                k, imp_obj = self.parameter_imports.popitem()
            except KeyError:
                break
            imp_obj.deleteLater()
            imp_obj = None
            #self.layout.removeWidget(imp_obj.widget)
            #imp_obj.close()

        observations = copy.deepcopy(observations)
        parameter_names = list(sorted(set([observation['parametername'] for observation in observations])))

        maximumwidth = 0
        for parametername in parameter_names:
            testlabel = QtWidgets.QLabel()
            testlabel.setText(parametername)
            maximumwidth = max(maximumwidth, testlabel.sizeHint().width())
            testlabel.deleteLater()
        testlabel = None

        if self.parameter_imports:
            # When would this ever happen?
            return

        for parametername in parameter_names:
            param_import_obj = ImportMethodChooser(parametername, staff=staff)
            param_import_obj.label.setFixedWidth(maximumwidth)
            if parametername not in self.parameter_imports:
                self.parameter_imports[parametername] = param_import_obj
                self.layout().addWidget(param_import_obj)

        self.set_parameters_using_stored_settings(stored_settings)

        #utils.MessagebarAndLog.info(log_msg="Imports in self.parameter_imports:\n" + '\n'.join([': '.join([k, str(v), v.parameter_name, str(v.widget)]) for k, v in self.parameter_imports.iteritems()]))
        #utils.MessagebarAndLog.info(log_msg="Conected widgets:\n" + '\n'.join([' ,parent:'.join([str(self.layout.itemAt(wid).widget()), str(self.layout.itemAt(wid).widget().parentWidget())]) for wid in xrange(self.layout.count())]))
        #utils.MessagebarAndLog.info(log_msg="All children parents:\n" + '\n'.join([': '.join([str(w), str(w.parentWidget())]) for w in self.all_children]))

    def update_observations(self, observations):
        observations = copy.deepcopy(observations)
        for parameter_name, import_method_chooser in self.parameter_imports.items():
            parameter_import_fields = import_method_chooser.parameter_import_fields
            if parameter_import_fields is not None:
                observations = parameter_import_fields.alter_data(
                    observations)
        return observations

    def filter_import_methods_not_set(self, observations):
        observations = copy.deepcopy(observations)
        #Order the observations under the import methods, and filter out the parameters not set.
        _observations = []
        for observation in observations:
            #This test is needed when the input fields have been filtered so that not all
            #parameternames exists as parameter import.
            if observation['parametername'] in self.parameter_imports:
                if self.parameter_imports[observation['parametername']].import_method and self.parameter_imports[observation['parametername']].import_method is not None:
                    _observations.append(observation)
        observations = _observations
        return observations

    def get_observations_importmethods(self, observations):
        observations = copy.deepcopy(observations)
        observations_importmethods = {}
        for observation in observations:
            if self.parameter_imports[observation['parametername']].import_method:
                observations_importmethods.setdefault(self.parameter_imports[observation['parametername']].import_method, []).append(observation)
        return observations_importmethods

    def set_parameters_using_stored_settings(self, stored_settings):
        """
        Sets the parameter settings based on a stored settings dict.

        parametername|import_method:w_flow|flowtype:Aveflow|unit:m3/s/parametername2|import_method:comment ...
        :param stored_settings: alist like [['parametername', [['attr1', 'val1'], ...]], ...]
        :return:
        """
        common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('InputFields', 'Setting parameters using stored settings: %s')) % str(stored_settings))
        for import_method_chooser in list(self.parameter_imports.values()):

            if not stored_settings:
                continue
            settings = [attrs for param, attrs in stored_settings if param == import_method_chooser.parameter_name]

            if settings:
                settings = settings[0]
            else:
                continue

            if settings is None or not settings:
                continue

            try:
                import_method_chooser.import_method = [v if v else None for k, v in settings if k == 'import_method'][0]
            except ValueError:
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('InputFields', 'Could not parse setting "%s". The stored settings probably use an old format. This will be corrected automatically.')) % str(settings))
                import_method_chooser.import_method = None
                continue

            if import_method_chooser.parameter_import_fields is None:
                import_method_chooser.choose_method(import_method_chooser.import_method_classes)

            for attr, val in settings:
                if attr == 'import_method':
                    continue
                try:
                    setattr(import_method_chooser.parameter_import_fields, attr, val)
                except Exception as e:
                    common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('InputFields', 'Setting parameter %s for %s to value %s failed, msg:\n%s')) % (str(attr), import_method_chooser.parameter_name, str(val), str(e)))

    def update_stored_settings(self, stored_settings, force_update=False):
        setted_pars = []
        new_settings = []
        for parameter_name, import_method_chooser in self.parameter_imports.items():
            if not force_update:
                if import_method_chooser.import_method is None or not import_method_chooser.import_method:
                    continue

            attrs = [('import_method', import_method_chooser.import_method)]

            parameter_import_fields = import_method_chooser.parameter_import_fields
            if parameter_import_fields is None:
                continue

            try:
                settings = parameter_import_fields.get_settings()
            except AttributeError as e:
                common_utils.MessagebarAndLog.info(log_msg=ru(
                    QCoreApplication.translate('InputFields', 'Getting attribute failed: %s, msg: %s')) % (str(
                    type(parameter_import_fields)), str(e)))
                settings = tuple()

            if settings:
                attrs.extend(settings)
            new_settings.append([parameter_name, attrs])
            setted_pars.append(parameter_name)

        for parameter, attrs in stored_settings:
            if parameter not in setted_pars:
                new_settings.append([parameter, attrs])

        stored_settings[:] = new_settings

    def clear_widgets(self):
        for name, param_import_obj in self.parameter_imports.items():
            param_import_obj.deleteLater()
            #self.layout.removeWidget(param_import_obj.widget)
            #param_import_obj.widget.close()
        self.parameter_imports = OrderedDict()


class ImportMethodChooser(QtWidgets.QWidget):
    def __init__(self, parameter_name, staff=None, parent=None):
        #super(ImportMethodChooser, self).__init__()
        super().__init__(parent)
        self.setLayout(qgis.PyQt.QtWidgets.QHBoxLayout())

        self.staff = staff
        self.parameter_widget = None
        self.parameter_name = parameter_name
        self.parameter_import_fields = None
        self.label = QtWidgets.QLabel()
        self.label.setText(self.parameter_name)
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.__import_method = QtWidgets.QComboBox()

        self.import_method_classes = OrderedDict((('', None),
                                                  ('comments', CommentsImportFields),
                                                  ('w_levels', WLevelsImportFields),
                                                  ('w_flow', WFlowImportFields),
                                                  ('w_qual_field_depth', WQualFieldDepthImportFields),
                                                  ('w_qual_field', WQualFieldImportFields)))

        self.__import_method.addItems(list(self.import_method_classes.keys()))

        self.__import_method.currentIndexChanged.connect(
                     lambda: self.choose_method(self.import_method_classes))

        for widget in [self.label, self.__import_method]:
            self.layout().addWidget(widget)

        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout().setContentsMargins(0, 0, 0, 0)

    @property
    def import_method(self):
        return str(self.__import_method.currentText())

    @import_method.setter
    def import_method(self, value):
        index = self.__import_method.findText(ru(value))
        if index != -1:
            self.__import_method.setCurrentIndex(index)

    def choose_method(self, import_methods_classes):
        import_method_name = self.import_method
        if self.parameter_widget is not None:
            try:
                self.parameter_widget.deleteLater()
                #self.layout.removeWidget(self.parameter_widget)
            except Exception as e:
                self.parameter_widget = None
            else:
                self.parameter_widget = None
        """try:
            self.parameter_widget.close()
        except Exception as e:
            pass"""
        self.parameter_import_fields = None


        parameter_import_fields_class = import_methods_classes.get(import_method_name, None)

        if parameter_import_fields_class is None:
            self.parameter_widget = None
            self.parameter_import_fields = None
        else:
            self.parameter_import_fields = parameter_import_fields_class(self, staff=self.staff)
            self.parameter_widget = self.parameter_import_fields
            self.layout().addWidget(self.parameter_widget)

    """def close(self):
        for child in self.layout().children():
            #self.layout.removeWidget(child)
            child.deleteLater()
            #child.close()
        #self.widget.close()
        self.deleteLater()"""


class CommentsImportFields(QtWidgets.QWidget):
    """
    """
    def __init__(self, import_method_chooser, staff=None, parent=None):
        """
        """
        super().__init__(parent)
        self.setLayout(qgis.PyQt.QtWidgets.QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.import_method_chooser = import_method_chooser

    def alter_data(self, observations):
        observations = copy.deepcopy(observations)
        parameter_name = self.import_method_chooser.parameter_name
        comment_obsdict = {}
        dateformat = '%Y%m%d %H:%M:%S'
        for observation in observations:
            if observation['parametername'] == parameter_name:
                datestring = datetime.strftime(observation['date_time'], dateformat)
                comment_obsdict.setdefault(observation['sublocation'], {})[datestring] = observation

        for observation in observations:
            if observation['parametername'] != parameter_name:
                datestring = datetime.strftime(observation['date_time'], dateformat)
                comment_obs = comment_obsdict.get(observation['sublocation'], {}).get(datestring, None)
                if comment_obs != None:
                    observation['comment'] = comment_obs['value']
                    comment_obs['skip_comment_import'] = True

        return observations

    def get_settings(self):
        return tuple()


class WLevelsImportFields(QtWidgets.QWidget):
    """
    """

    def __init__(self, import_method_chooser, staff=None, parent=None):
        """
        """
        super().__init__(parent)
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.h_toc_dict = None
        self.import_method_chooser = import_method_chooser
        self.label_value_column = QtWidgets.QLabel('Value column: ')
        self._value_column = QtWidgets.QComboBox()
        self._calculate_level_masl_checkbox = QtWidgets.QCheckBox(ru(QCoreApplication.translate('WLevelsImportFields', 'Calculate level_masl from meas and h_toc')))
        self._calculate_level_masl_checkbox.setToolTip(ru(QCoreApplication.translate('WLevelsImportFields', 'If h_toc is not NULL in table obs_points, level_masl is calculated as h_toc - meas.')))
        self._value_column.addItems(['meas', 'level_masl'])
        self.value_column = 'meas'
        self.layout().addWidget(self.label_value_column, 0, 0)
        self.layout().addWidget(self._value_column, 1, 0)
        self.layout().addWidget(self._calculate_level_masl_checkbox, 1, 1)

        self._value_column.currentIndexChanged.connect(self.set_calculate_level_masl_visibility)

        self.set_calculate_level_masl_visibility()

    @property
    def value_column(self):
        return str(self._value_column.currentText())

    @value_column.setter
    def value_column(self, value):
        index = self._value_column.findText(ru(value))
        if index != -1:
            self._value_column.setCurrentIndex(index)
        if value == 'meas':
            self.calculate_level_masl = True
        else:
            self.calculate_level_masl = False
        self.set_calculate_level_masl_visibility()

    @property
    def calculate_level_masl(self):
        return self._calculate_level_masl_checkbox.isChecked()

    @calculate_level_masl.setter
    def calculate_level_masl(self, a_bool):
        if a_bool:
            self._calculate_level_masl_checkbox.setChecked(True)
        else:
            self._calculate_level_masl_checkbox.setChecked(False)

    def set_calculate_level_masl_visibility(self):
        if self.value_column == 'meas':
            self._calculate_level_masl_checkbox.setVisible(True)
        else:
            self._calculate_level_masl_checkbox.setVisible(False)

    def alter_data(self, observations):
        for observation in observations:
            if observation['parametername'] == self.import_method_chooser.parameter_name:
                if self.value_column == 'level_masl':
                    observation['level_masl'] = observation['value']
                else:
                    observation['meas'] = observation['value'].replace(',', '.')

                    if self.calculate_level_masl:
                        if self.h_toc_dict is None:
                            self.h_toc_dict = dict([(obsid_h_toc[0], obsid_h_toc[1]) for obsid_h_toc in db_utils.sql_load_fr_db('SELECT obsid, h_toc FROM obs_points WHERE h_toc IS NOT NULL')[1]])
                        h_toc = self.h_toc_dict.get(observation['obsid'], None)
                        if h_toc is not None:
                            try:
                                h_toc = float(h_toc)
                            except ValueError:
                                pass
                            else:
                                observation['level_masl'] = str(h_toc - float(observation['meas']))
                                observation['h_toc'] = str(h_toc)
        return observations

    def get_settings(self):
        return (('value_column', self.value_column), )


class WFlowImportFields(QtWidgets.QWidget):
    """
    This class should create a layout and populate it with question boxes relevant to w_flow import which is probably "flowtype" and "unit" dropdown lists.
    """


    def __init__(self, import_method_chooser, staff=None, parent=None):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super().__init__(parent)
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._import_method_chooser = import_method_chooser
        self.label_flowtype = QtWidgets.QLabel('Flowtype: ')
        self.__flowtype = default_combobox()
        self._flowtypes_units = defs.w_flow_flowtypes_units()
        self.__flowtype.addItems(sorted(self._flowtypes_units.keys()))
        self.label_unit = QtWidgets.QLabel('Unit: ')
        self.__unit = default_combobox()
        self.__flowtype.editTextChanged.connect(
                     lambda : self.fill_list(self.__unit, self.flowtype, self._flowtypes_units))

        self.layout().addWidget(self.label_flowtype, 0, 0)
        self.layout().addWidget(self.__flowtype, 1, 0)
        self.layout().addWidget(self.label_unit, 0, 1)
        self.layout().addWidget(self.__unit, 1, 1)

    @property
    def flowtype(self):
        return ru(self.__flowtype.currentText())

    @flowtype.setter
    def flowtype(self, value):
        self.__flowtype.setEditText(value)

    @property
    def unit(self):
        return ru(self.__unit.currentText())

    @unit.setter
    def unit(self, value):
        self.__unit.setEditText(ru(value))

    def fill_list(self, combobox_var, parameter_var, parameter_list_dict):
        """

        :param combobox_var: a QComboBox object
        :param parameter_var: a string parameter name
        :param parameter_list_dict: A dict like  {'Accvol': [('m3',)], 'Momflow': [('l/s',)]}
        :return:
        """
        vals = parameter_list_dict.get(parameter_var, None)
        if vals is None:
            vals = list(sorted(set([val for vals_list in list(parameter_list_dict.values()) for val in vals_list[0]])))
        else:
            vals = list(vals[0])
        combobox_var.clear()
        combobox_var.addItem('')
        combobox_var.addItems(ru(vals, keep_containers=True))

    def get_settings(self):
        return (('flowtype', self.flowtype), ('unit', self.unit))

    def alter_data(self, observations):
        if not self.flowtype:
            raise common_utils.UsageError(ru(QCoreApplication.translate('WFlowImportFields', 'Import error, flowtype not given')))
        if not self.unit:
            raise common_utils.UsageError(ru(QCoreApplication.translate('WFlowImportFields', 'Import error, unit not given')))

        observations = copy.deepcopy(observations)
        for observation in observations:
            if observation['parametername'] == self._import_method_chooser.parameter_name:
                observation['flowtype'] = self.flowtype
                observation['unit'] = self.unit

        return observations


class WQualFieldImportFields(QtWidgets.QWidget):
    """
    This class should create a layout and populate it with question boxes relevant to w_qual_fields import which is probably "parameter", "unit" dropdown lists.
    And a depth dropdown list which is populated by the parameternames. The purpose is that the user should select which parametername to use as the depth variable

    """

    def __init__(self, import_method_chooser, staff=None, parent=None):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super().__init__(parent)
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.staff = staff
        self._import_method_chooser = import_method_chooser
        self.label_parameter = QtWidgets.QLabel(ru(QCoreApplication.translate('WQualFieldImportFields', 'Parameter: ')))
        self.__parameter = default_combobox()

        self._parameters_units = self.get_sorted_parameter_date_time_list(self.staff, 1)
        self.__parameter.addItems(list(self._parameters_units.keys()))
        self.label_unit = QtWidgets.QLabel(ru(QCoreApplication.translate('WQualFieldImportFields', 'Unit: ')))
        self.__unit = default_combobox()
        unit_tooltip = ru(QCoreApplication.translate('WQualFieldImportFields', ('The unit list is sorted with the unit from the\n'
                                                                                      'currently chosen staff first in descending date order, then\n'
                                                                                      'the rest of the units in descending date order.')))
        self.__unit.setToolTip(unit_tooltip)
        self.label_unit.setToolTip(unit_tooltip)

        self.__instrument = default_combobox()
        self.label_instrument = QtWidgets.QLabel(ru(QCoreApplication.translate('WQualFieldImportFields', 'Instrument: ')))
        instrument_tooltip = ru(QCoreApplication.translate('WQualFieldImportFields', ('The instrument list is sorted with the instruments from the\n'
                                                                                      'currently chosen staff first in descending date order, then\n'
                                                                                      'the rest of the instruments in descending date order.')))
        self.__instrument.setToolTip(instrument_tooltip)
        self.label_instrument.setToolTip(instrument_tooltip)
        self.parameter_instruments = self.get_sorted_parameter_date_time_list(self.staff, 2)

        self.layout().addWidget(self.label_parameter, 0, 0)
        self.layout().addWidget(self.__parameter, 1, 0)
        self.layout().addWidget(self.label_unit, 0, 1)
        self.layout().addWidget(self.__unit, 1, 1)
        self.layout().addWidget(self.label_instrument, 0, 3)
        self.layout().addWidget(self.__instrument, 1, 3)

        self.__parameter.editTextChanged.connect(
                     lambda : self.fill_list(self.__unit, self.parameter, self._parameters_units, sort_list=False,
                                            select_first_nonempty_row=True))

        self.__parameter.editTextChanged.connect(
                     lambda: self.fill_list(self.__instrument, self.parameter, self.parameter_instruments, sort_list=False,
                                            select_first_nonempty_row=True))

    def get_sorted_parameter_date_time_list(self, staff, value_index):
        # The instrument list is sorted with the instruments from the currently chosen staff first, then the rest of the instruments in descending date order.
        all_res = {}
        for parameter, staff_dicts in defs.get_last_used_quality_instruments().items():
            res = []
            if staff is not None and staff in staff_dicts:
                for _parameter_unit_instrument_staff_date_time in staff_dicts[staff]:
                    if _parameter_unit_instrument_staff_date_time[value_index] not in res:
                        res.append(_parameter_unit_instrument_staff_date_time[value_index])
            for _staff, _parameter_unit_instrument_staff_date_times in staff_dicts.items():
                for _parameter_unit_instrument_staff_date_time in _parameter_unit_instrument_staff_date_times:
                    if _parameter_unit_instrument_staff_date_time[value_index] not in res:
                        res.append(_parameter_unit_instrument_staff_date_time[value_index])
            all_res[parameter] = res
        return all_res

    @property
    def parameter(self):
        return ru(self.__parameter.currentText())

    @parameter.setter
    def parameter(self, value):
        self.__parameter.setEditText(value)

    @property
    def unit(self):
        return ru(self.__unit.currentText())

    @unit.setter
    def unit(self, value):
        self.__unit.setEditText(ru(value))

    @property
    def instrument(self):
        return ru(self.__instrument.currentText())

    @instrument.setter
    def instrument(self, value):
        self.__instrument.setEditText(ru(value))

    def fill_list(self, combobox_var, parameter_var, parameter_list_dict, sort_list=True, select_first_nonempty_row=False):
        """

        :param combobox_var: a QComboBox object
        :param parameter_var: a string parameter name
        :param parameter_list_dict: A dict like  {'Accvol': [('m3',)], 'Momflow': [('l/s',)]}
        :return:
        """
        vals = parameter_list_dict.get(parameter_var, None)
        if vals is None:
            vals = list(set([val[0] if isinstance(val, (list, tuple)) else val for vals_list in list(parameter_list_dict.values()) for val in vals_list]))
        else:
            vals = [val[0] if isinstance(val, (list, tuple)) else val for val in vals]

        if sort_list:
            vals = sorted(vals)

        combobox_var.clear()
        combobox_var.addItem('')
        combobox_var.addItems(ru(vals, keep_containers=True))
        if select_first_nonempty_row:
            for value in vals:
                if value:
                    set_combobox(combobox_var, value, add_if_not_exists=False)
                    break

    def get_settings(self):
        """
        Skipped instrument and unit ('unit', self.unit) ('instrument', self.instrument). It's filled from last used instrument for the staff instead.
        :return:
        """
        return (('parameter', self.parameter), )

    def alter_data(self, observations):
        if not self.parameter:
            raise common_utils.UsageError(ru(QCoreApplication.translate('WQualFieldImportFields', 'Import error, parameter not given')))

        observations = copy.deepcopy(observations)

        """
        #Only for dev
        adepth_dict = {}
        try:
            for obs in observations:
                midvatten_utils.MessagebarAndLog.info(log_msg="Obs: " + str(obs))
                if obs['parametername'] == self.depth:
                    adepth_dict[obs['date_time']] = obs['value']
        except TypeError, e:
            raise Exception("Obs: " + str(obs) + " e " + str(e))
        """
        for observation in observations:
            try:
                if observation['parametername'] == self._import_method_chooser.parameter_name:
                    observation['parameter'] = self.parameter
                    observation['instrument'] = self.instrument
                    observation['unit'] = self.unit
            except TypeError:
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('WQualFieldImportFields', "Import error. See message log panel")),
                                                                   log_msg=ru(QCoreApplication.translate('WQualFieldImportFields', "error on observation : %s\nand parameter: %s"))%(str(observation), self.parameter))
                raise TypeError
        return observations


class WQualFieldDepthImportFields(QtWidgets.QWidget):
    """
    """
    def __init__(self, import_method_chooser, staff=None, parent=None):
        """
        """
        super().__init__(parent)
        self.setLayout(qgis.PyQt.QtWidgets.QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.import_method_chooser = import_method_chooser

    def alter_data(self, observations):
        #Depth should be added for all observations with the same obsid and date_time

        observations = copy.deepcopy(observations)

        parameter_name = self.import_method_chooser.parameter_name

        dateformat = '%Y%m%d %H:%M:%S'
        depths = dict([((obs['sublocation'], datetime.strftime(obs['date_time'], dateformat)), obs['value'])
                       for obs in observations if obs['parametername'] == parameter_name])
        if not depths:
            return observations

        for observation in observations:
            depth = depths.get((observation['sublocation'], datetime.strftime(observation['date_time'], dateformat)), None)
            if depth is not None:
                observation['depth'] = depth

        return observations

    def get_settings(self):
        return tuple()

    def set_settings(self):
        pass


def default_combobox(editable=True):
    combo_box = QtWidgets.QComboBox()
    combo_box.setEditable(editable)
    combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
    combo_box.setMinimumWidth(80)
    combo_box.addItem('')
    return combo_box

