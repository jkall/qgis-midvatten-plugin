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
from functools import partial

import definitions.midvatten_defs
import import_data_to_db
import copy
from collections import OrderedDict
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import find_date_format, datestring_to_date, dateshift
from datetime import datetime

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4

import_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]

class FieldloggerImport(PyQt4.QtGui.QMainWindow, import_fieldlogger_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.status = True

    def parse_observations_and_populate_gui(self):

        splitter = PyQt4.QtGui.QSplitter(PyQt4.QtCore.Qt.Vertical)
        self.add_row(splitter)

        self.observations = self.select_file_and_parse_rows()
        if self.observations == u'cancel':
            self.status = True
            return u'cancel'

        #Filters and general settings
        settings_widget = PyQt4.QtGui.QWidget()
        settings_layout = PyQt4.QtGui.QVBoxLayout()
        settings_widget.setLayout(settings_layout)
        splitter.addWidget(settings_widget)
        self.settings = []
        self.settings.append(StaffQuestion())
        self.settings.append(DateShiftQuestion())
        self.settings.append(DateTimeFilter()) #This includes a checkbox for "include only latest
        for setting in self.settings:
            if hasattr(setting, u'widget'):
                settings_layout.addWidget(setting.widget)
        self.add_line(settings_layout)

        #Settings with own loop gets self.observations to work on.
        self.settings_with_own_loop = [ObsidFilter()]

        #Sublocations
        sublocations = [observation[u'sublocation'] for observation in self.observations]
        sublocations_widget = PyQt4.QtGui.QWidget()
        sublocations_layout = PyQt4.QtGui.QVBoxLayout()
        sublocations_widget.setLayout(sublocations_layout)
        splitter.addWidget(sublocations_widget)
        self.settings.append(SublocationFilter(sublocations))
        sublocations_layout.addWidget(self.settings[-1].widget)
        self.add_line(sublocations_layout)

        #Parameters
        parameter_widget = PyQt4.QtGui.QWidget()
        parameter_layout = PyQt4.QtGui.QVBoxLayout()
        parameter_widget.setLayout(parameter_layout)
        splitter.addWidget(parameter_widget)

        self.parameter_names = list(set([observation[u'parametername'] for observation in self.observations]))
        self.parameter_imports = OrderedDict()
        for parametername in self.parameter_names:
            param_import_obj = ImportMethodChooser(parametername, self.parameter_names, self.connect)
            self.parameter_imports[parametername] = param_import_obj
            parameter_layout.addWidget(param_import_obj.widget)

        self.main_vertical_layout.addStretch(1)

        self.stored_settingskey = u'fieldlogger_import_parameter_settings'

        #General buttons
        self.start_import_button = PyQt4.QtGui.QPushButton(u'Start import')
        self.gridLayout_buttons.addWidget(self.start_import_button, 0, 0)
        self.connect(self.start_import_button, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.start_import(self.observations))
        self.save_settings_button = PyQt4.QtGui.QPushButton(u'Save settings')
        self.gridLayout_buttons.addWidget(self.save_settings_button, 1, 0)
        self.connect(self.save_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : map(lambda x: x(),
                                      [lambda : self.update_stored_settings(self.stored_settings, self.parameter_imports),
                                       lambda : self.save_stored_settings(self.ms, self.stored_settings, self.stored_settingskey)]))



        #Load stored parameter settings
        self.stored_settings = self.get_stored_settings(self.ms, self.stored_settingskey)
        self.set_parameters_using_stored_settings(self.stored_settings, self.parameter_imports)

        self.show()

    def select_file_and_parse_rows(self):
        charset = utils.ask_for_charset('utf-8')
        filenames = utils.select_files(only_one_file=False, extension="csv (*.csv)")
        if filenames is None or charset is None:
            self.status = False
            return u'cancel'

        observations = []
        for filename in filenames:
            filename = utils.returnunicode(filename)
            with io.open(filename, 'r', encoding=charset) as f:
                #Skip header
                f.readline()
                observations.extend(self.parse_rows(f))

        #Remove duplicates
        observations = [dict(no_duplicate) for no_duplicate in set([tuple(possible_duplicate.items()) for possible_duplicate in observations])]

        return observations

    @staticmethod
    def parse_rows(f):
        """
        Parses rows from fieldlogger format into a dict
        :param f: File_data, often an open file or a list of rows without header
        :return: a list of dicts like [{date_time: x, sublocation: y, parametername: z, value: o}, ...]

        """
        observations = []
        for rownr, rawrow in enumerate(f):
            observation = {}
            row = utils.returnunicode(rawrow).rstrip(u'\r').rstrip(u'\n')
            if not row:
                continue
            cols = row.split(u';')
            observation[u'sublocation'] = cols[0]
            date = cols[1]
            time = cols[2]
            observation[u'date_time'] = datestring_to_date(u' '.join([date, time]))
            observation[u'value'] = cols[3]
            observation[u'parametername'] = cols[4]
            observations.append(observation)
        return observations

    def add_row(self, a_widget):
        """
        :param: a_widget:
        """
        self.main_vertical_layout.addWidget(a_widget)

    def add_line(self, layout=None):
        """ just adds a line"""
        #horizontalLineWidget = PyQt4.QtGui.QWidget()
        #horizontalLineWidget.setFixedHeight(2)
        #horizontalLineWidget.setSizePolicy(PyQt4.QtGui.QSizePolicy.Expanding, PyQt4.QtGui.QSizePolicy.Fixed)
        #horizontalLineWidget.setStyleSheet(PyQt4.QtCore.QString("background-color: #c0c0c0;"));
        line = PyQt4.QtGui.QFrame()
        #line.setObjectName(QString::fromUtf8("line"));
        line.setGeometry(PyQt4.QtCore.QRect(320, 150, 118, 3))
        line.setFrameShape(PyQt4.QtGui.QFrame.HLine);
        line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken);
        if layout is None:
            self.add_row(line)
        else:
            layout.addWidget(line)

    @staticmethod
    def sublocation_to_groups(sublocations, delimiter=u'.'):
        """
        This method splits sublocation using a splitter, default to u'.'. Each list position is grouped to lists
         containing all distinct values. It's finally stored in a dict with the lenght of the splitted group as key.
        :param: sublocations: A list of sublocations, ex: [u'c', u'a.1', u'a.2', u'b.1.1']
        :return: a dict like {1: [set(distinct values)], 2: [set(distinct values)}, set(), set()], ...)
        """
        sublocation_groups = {}
        for sublocation in sublocations:
            splitted = sublocation.split(delimiter)
            length = len(splitted)
            for index in xrange(length):
                #a dict like {1: [set()], 2: [set(), set()], ...}
                sublocation_groups.setdefault(length, [set()for i in xrange(length)])[index].add(splitted[index])
        return sublocation_groups

    @staticmethod
    def prepare_w_level_data(observations):
        """
        Produces a filestring with columns "obsid, date_time, meas, comment" and imports it
        :param obsdict: a dict like {obsid: {date_time: {parameter: value}}}
        :return: None
        """
        file_data_list = [[u'obsid', u'date_time', u'meas', u'comment']]
        for observation in observations:
            obsid = observation[u'obsid']
            date_time = datetime.strftime(observation[u'date_time'], '%Y-%m-%d %H:%M:%S')
            meas = observation[u'value'].replace(u',', u'.')
            comment = observation.get(u'comment', u'')
            file_data_list.append([obsid, date_time, meas, comment])

        return file_data_list

    @staticmethod
    def prepare_comments_data(observations):
        file_data_list = [[u'obsid', u'date_time', u'comment', u'staff']]
        for observation in observations:

            if observation.get(u'skip_comment_import', False):
                continue
            obsid = observation[u'obsid']
            date_time = datetime.strftime(observation[u'date_time'], '%Y-%m-%d %H:%M:%S')
            comment = observation[u'value']
            staff = observation[u'staff']
            file_data_list.append([obsid, date_time, comment, staff])
        return file_data_list

    @staticmethod
    def prepare_w_flow_data(observations):
        """
        Produces a filestring with columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :return:
        """

        file_data_list = [[u'obsid', u'instrumentid', u'flowtype', u'date_time', u'reading', u'unit', u'comment']]
        instrumentids = utils.get_last_used_flow_instruments()[1]

        for observation in observations:
            obsid = observation[u'obsid']
            flowtype = observation[u'flowtype']
            date_time = datetime.strftime(observation[u'date_time'], '%Y-%m-%d %H:%M:%S')
            unit = observation[u'unit']

            instrumentids_for_obsid = instrumentids.get(obsid, None)
            if instrumentids_for_obsid is None:
                last_used_instrumentid = u''
            else:
                last_used_instrumentid = sorted(
                    [(_date_time, _instrumentid) for _flowtype, _instrumentid, _date_time in instrumentids[obsid] if
                     (_flowtype == flowtype)])[-1][1]
            question = utils.NotFoundQuestion(dialogtitle=u'Submit instrument id',
                                              msg=u''.join([u'Submit the instrument id for the measurement:\n ',
                                                            u', '.join([obsid, date_time, flowtype, unit])]),
                                              existing_list=[last_used_instrumentid],
                                              default_value=last_used_instrumentid,
                                              combobox_label=u'Instrument id:s in database.\nThe last used instrument id for the current obsid is prefilled:')
            answer = question.answer
            if answer == u'cancel':
                return u'cancel'
            instrumentid = utils.returnunicode(question.value)

            reading = observation[u'value'].replace(u',', u'.')

            comment = observation.get(u'comment', u'')
            file_data_list.append([obsid, instrumentid, flowtype, date_time, reading, unit, comment])

        return file_data_list

    @staticmethod
    def prepare_w_qual_field_data(observations):
        """
        Produces a filestring with columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :param quality_or_water_sample: Word written at user question: u'quality' or u'water sample'.
        :return:
        """
        file_data_list = [[u'obsid', u'staff', u'date_time', u'instrument', u'parameter', u'reading_num', u'reading_txt', u'unit', u'depth', u'comment']]

        for observation in observations:
            obsid = observation[u'obsid']
            staff = observation[u'staff']
            date_time = datetime.strftime(observation[u'date_time'], '%Y-%m-%d %H:%M:%S')
            instrument = observation[u'instrument']
            parameter = observation[u'parameter']
            reading_num = observation[u'value'].replace(u',', u'.')
            reading_txt = observation[u'value']
            unit = observation[u'unit']
            depth = observation.get(u'depth', u'')
            comment = observation.get(u'comment', u'')
            file_data_list.append([obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment])

        return file_data_list

    @staticmethod
    def filter_and_alter_data(observations, settings, settings_with_own_loop, parameter_imports):
        observations = copy.deepcopy(observations)

        #Filter and alter data
        filtered_observations = []
        for observation in observations:
            for setting in settings:
                observation =  setting.alter_data(observation)
                if observation == u'cancel':
                    return u'cancel'
                elif observation is None:
                    break
            if observation is not None:
                filtered_observations.append(observation)
        observations = filtered_observations

        for setting in settings_with_own_loop:
            observations = setting.alter_data(observations)
            if observations == u'cancel':
                return u'cancel'

        #Update observations from parameter fields
        for parameter_name, import_method_chooser in parameter_imports.iteritems():
            parameter_import_fields = import_method_chooser.parameter_import_fields
            if parameter_import_fields is not None:
                observations = parameter_import_fields.alter_data(observations)

        return observations

    @staticmethod
    def get_stored_settings(ms, settingskey):
        """
        Creates a parameter setting dict from midvattensettings

        Reads a string entry from midvattensettings that looks like this:
        importmethod:
        :param ms: midvattensettings
        :return:
        """

        settings = ms.settingsdict.get(settingskey, None)
        if settings is None:
            return OrderedDict()
        parameter_settings_string = utils.returnunicode(settings)
        parameter_settings = parameter_settings_string.split(u'/')
        stored_settings = OrderedDict()

        for parameter_setting in parameter_settings:
            settings = parameter_setting.split(u'|')
            parametername = settings[0]
            stored_settings[parametername] = OrderedDict()

            for attrs in settings[1:]:
                attr, value = attrs.split(u':')
                stored_settings[parametername][attr] = value
        return stored_settings

    @staticmethod
    def set_parameters_using_stored_settings(stored_settings, import_method_choosers):
        """
        Sets the parameter settings based on a stored setitngs dict.

        parametername|import_method:w_flow|flowtype:Aveflow|unit:m3/s/parametername2|import_method:comment ...
        :param stored_settings: a dict like {parametername: {attribute1: value1, attribute2: value2 ...}}
        :param import_method_choosers: a dict like {parametername: ImportMethodChooser, ...}
        :return:
        """
        for import_method_chooser in import_method_choosers.values():

            setting = stored_settings.get(import_method_chooser.parameter_name, None)
            if setting is None:
                continue

            import_method_chooser.import_method = setting[u'import_method']

            if import_method_chooser.parameter_import_fields is None:
                import_method_chooser.choose_method(import_method_chooser.import_method_classes)


            for attr, val in setting.iteritems():
                if attr == u'import_method':
                    continue
                try:
                    setattr(import_method_chooser.parameter_import_fields, attr, val)
                except Exception, e:
                    print(str(e))

    @staticmethod
    def update_stored_settings(stored_settings, parameter_imports, force_update=False):
        for parameter_name, import_method_chooser in parameter_imports.iteritems():
            if not force_update:
                if import_method_chooser.import_method is None or not import_method_chooser.import_method:
                    continue

            attrdict = stored_settings.get(import_method_chooser.parameter_name, OrderedDict())

            attrdict[u'import_method'] = import_method_chooser.import_method

            parameter_import_fields = import_method_chooser.parameter_import_fields
            if parameter_import_fields is None:
                continue

            try:
                settings = parameter_import_fields.get_settings()
            except AttributeError:
                settings = OrderedDict()
            for attr, value in settings.iteritems():
                attrdict[attr] = value

            stored_settings[import_method_chooser.parameter_name] = attrdict

    @staticmethod
    def save_stored_settings(ms, stored_settings, settingskey):
        """
        Saves the current parameter settings into midvatten settings

        Stores the settings as a string:
        parametername|import_method:w_flow|flowtype:Aveflow|unit:m3/s/parametername2|import_method:comment ...

        :param ms: midvattensettings
        :param stored_settings: a dict like {parametername: {attribute1: value1, attribute2: value2 ...}}
        :return:
        """
        if stored_settings is None:
            return
        stored_settings = utils.returnunicode(stored_settings, keep_containers=True)
        settings_list = []
        for parameter_name, attrs in stored_settings.iteritems():
            paramlist = [parameter_name]
            paramlist.extend([u':'.join([attr, value]) for attr, value in attrs.iteritems()])
            settings_list.append(u'|'.join(paramlist))

        setting_string = u'/'.join(settings_list)
        ms.settingsdict[settingskey] = utils.returnunicode(setting_string)
        ms.save_settings()

    def start_import(self, observations):
        """

        :param observations:
        :return:
        """

        #Start by saving the parameter settings
        self.update_stored_settings(self.stored_settings, self.parameter_imports)
        self.save_stored_settings(self.ms, self.stored_settings, self.stored_settingskey)

        chosen_methods = [import_method_chooser.import_method for import_method_chooser in self.parameter_imports.values()
                          if import_method_chooser.import_method]
        if not chosen_methods:
            utils.pop_up_info("Must choose at least one parameter import method")
            utils.MessagebarAndLog.critical(bar_msg="No parameter import method chosen")
            return u'cancel'

        #Update the observations using the general settings, filters and parameter settings
        observations = self.filter_and_alter_data(observations, self.settings, self.settings_with_own_loop, self.parameter_imports)
        if observations == u'cancel':
            utils.MessagebarAndLog.warning(bar_msg=u"No observations left to import after filtering")
            return None

        observations_importmethods = {}
        for observation in observations:
            observations_importmethods.setdefault(self.parameter_imports[observation[u'parametername']].import_method, []).append(observation)

        importer = import_data_to_db.midv_data_importer()

        data_preparers = {u'w_levels': self.prepare_w_level_data,
                          u'w_flow': self.prepare_w_flow_data,
                          u'w_qual_field': self.prepare_w_qual_field_data,
                          u'comments': self.prepare_comments_data}

        for import_method, observations in observations_importmethods.iteritems():
            if import_method:
                file_data = data_preparers[import_method](observations)

                importer.send_file_data_to_importer(file_data, partial(importer.general_csv_import, goal_table=import_method))

        importer.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()


class RowEntry(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QHBoxLayout()
        self.widget.setLayout(self.layout)


class RowEntryGrid(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QGridLayout()
        self.widget.setLayout(self.layout)


class ObsidFilter(object):
    def __init__(self):
        pass

    def alter_data(self, observations):
        observations = copy.deepcopy(observations)
        existing_obsids = utils.get_all_obsids()

        for observation in observations:
            observation[u'obsid'] = observation[u'sublocation'].split(u'.')[0]

        obsids = [list(x) for x in sorted(set([(observation[u'obsid'], observation[u'obsid']) for observation in observations]))]
        obsids.reverse()
        obsids.append([u'old_obsid', u'new_obsid'])
        obsids.reverse()

        answer = utils.filter_nonexisting_values_and_ask(obsids, u'new_obsid', existing_values=existing_obsids, try_capitalize=False)
        if answer == u'cancel':
            return answer

        if answer is not None:
            if isinstance(answer, (list, tuple)):
                if len(answer) > 1:
                    obsid_rename_dict = dict([(old_obsid_new_obsid[0], old_obsid_new_obsid[1]) for old_obsid_new_obsid in answer[1:]])
                    #Filter and rename obsids
                    [observation.update({u'obsid': obsid_rename_dict.get(observation[u'obsid'], None)})
                        for observation in observations]
                    observations = [observation for observation in observations if all([observation[u'obsid'] is not None, observation[u'obsid']])]

        if len(observations) == 0:
            utils.MessagebarAndLog.warning(bar_msg=u'No observations imported, see log message panel',
                                           log_msg=u'No observations returned from obsid verification.' +
                                                   u'Were all skipped?')
            return u'cancel'
        return observations


class StaffQuestion(RowEntry):
    def __init__(self):
        super(StaffQuestion, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Staff who did the measurement')
        self.existing_staff_combobox = default_combobox()
        existing_staff = sorted(defs.staff_list()[1])
        self.existing_staff_combobox.addItems(existing_staff)

        for widget in [self.label, self.existing_staff_combobox]:
            self.layout.addWidget(widget)
        self.layout.addStretch()

    @property
    def staff(self):
        return utils.returnunicode(self.existing_staff_combobox.currentText())

    @staff.setter
    def staff(self, value):
        self.existing_staff_combobox.setEditText(value)

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        if self.staff is None or not self.staff:
            utils.MessagebarAndLog.critical(log_msg=u'Import error, staff not given')
            utils.pop_up_info(u'Import error, staff not given')
            return u'cancel'

        observation[u'staff'] = self.staff
        return observation


class DateShiftQuestion(RowEntry):
    def __init__(self):
        super(DateShiftQuestion, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Shift dates, supported format ex. "-1 hours":')
        self.dateshift_lineedit = PyQt4.QtGui.QLineEdit()
        self.dateshift_lineedit.setText(u'0 hours')

        for widget in [self.label, self.dateshift_lineedit]:
            self.layout.addWidget(widget)
        self.layout.insertStretch(-1, 1)

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        shift_specification = utils.returnunicode(self.dateshift_lineedit.text())

        step_steplength = shift_specification.split(u' ')
        failed = False

        bar_msg = u'Dateshift specification wrong format, se log message panel'
        log_msg = (u'Dateshift specification must be made using format ' +
                    '"step step_length", ex: "0 hours", "-1 hours", "-1 days" etc.\n' +
                    'Supported step lengths: microseconds, milliseconds, seconds, ' +
                    'minutes, hours, days, weeks.')

        if len(step_steplength) != 2:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            return u'cancel'
        try:
            step = float(step_steplength[0])
            steplength = step_steplength[1]
        except:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            return u'cancel'

        test_shift = dateshift('2015-02-01', step, steplength)
        if test_shift == None:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            return u'cancel'

        observation[u'date_time'] = dateshift(observation[u'date_time'], step, steplength)

        return observation


class DateTimeFilter(RowEntry):
    def __init__(self):
        super(DateTimeFilter, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Import data from: ')
        self.from_datetimeedit = PyQt4.QtGui.QDateTimeEdit(datestring_to_date(u'1900-01-01 00:00:00'))
        self.label_to = PyQt4.QtGui.QLabel(u'to: ')
        self.to_datetimeedit = PyQt4.QtGui.QDateTimeEdit(datestring_to_date(u'2099-12-31 23:59:59'))
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


class SublocationFilter(RowEntry):
    def __init__(self, sublocations):
        """

        :param sublocations: a list like [u'a.b', u'1.2.3', ...]
        """
        super(SublocationFilter, self).__init__()

        self.label = PyQt4.QtGui.QLabel(u'Select sublocations to import:')
        self.layout.addWidget(self.label)

        sublocations = sorted(list(set(sublocations)))
        num_rows = len(sublocations)
        #num_columns = reduce(lambda x, y: max(x , len(y.split(u'.'))), sublocations, 0)
        num_columns = max([len(sublocation.split(u'.')) for sublocation in sublocations])

        self.table = PyQt4.QtGui.QTableWidget(num_rows, num_columns)
        self.table.setSelectionBehavior(PyQt4.QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(PyQt4.QtGui.QAbstractItemView.ExtendedSelection)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table_items = {}
        for rownr, sublocation in enumerate(sublocations):
            for colnr, value in enumerate(sublocation.split(u'.')):
                tablewidgetitem = PyQt4.QtGui.QTableWidgetItem(value)
                if sublocation not in self.table_items:
                    self.table_items[sublocation] = tablewidgetitem
                self.table.setItem(rownr, colnr, tablewidgetitem)

        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

        self.table.selectAll()

        self.layout.addWidget(self.table)
        self.layout.addStretch()

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
        sublocation = observation[u'sublocation']

        if self.table_items[sublocation].isSelected():
            return observation
        else:
            return None


class ImportMethodChooser(RowEntry):
    def __init__(self, parameter_name, parameter_names, connect):
        super(ImportMethodChooser, self).__init__()
        self.connect = connect
        self.parameter_widget = None
        self.parameter_name = parameter_name
        self.parameter_names = parameter_names
        self.parameter_import_fields = None
        self.label = PyQt4.QtGui.QLabel()
        self.label.setText(self.parameter_name)
        self.label.setTextInteractionFlags(PyQt4.QtCore.Qt.TextSelectableByMouse)
        self.__import_method = PyQt4.QtGui.QComboBox()

        self.import_method_classes = OrderedDict(((u'', None),
                                                  (u'comments', CommentsImportFields),
                                                  (u'w_levels', WLevelsImportFields),
                                                  (u'w_flow', WFlowImportFields),
                                                  (u'w_qual_field', WQualFieldImportFields)))

        self.__import_method.addItems(self.import_method_classes.keys())

        self.connect(self.__import_method, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.choose_method(self.import_method_classes))

        for widget in [self.label, self.__import_method]:
            self.layout.addWidget(widget)

        self.layout.insertStretch(-1, 0)

    @property
    def import_method(self):
        return str(self.__import_method.currentText())

    @import_method.setter
    def import_method(self, value):
        index = self.__import_method.findText(utils.returnunicode(value))
        if index != -1:
            self.__import_method.setCurrentIndex(index)

    def choose_method(self, import_methods_classes):
        import_method_name = self.import_method
        #Remove stretch
        self.layout.takeAt(-1)
        try:
            self.layout.removeWidget(self.parameter_widget)
        except Exception, e:
            pass
        try:
            self.parameter_widget.close()
        except Exception, e:
            pass
        try:
            self.parameter_import_fields = None
        except Exception, e:
            pass

        parameter_import_fields_class = import_methods_classes.get(import_method_name, None)

        if parameter_import_fields_class is None:
            self.parameter_widget = None
            self.parameter_import_fields = None
            self.layout.insertStretch(-1, 0)

        else:
            self.parameter_import_fields = parameter_import_fields_class(self, self.connect)
            self.parameter_widget = self.parameter_import_fields.widget
            self.layout.addWidget(self.parameter_widget)


class CommentsImportFields(RowEntry):
    """
    """
    def __init__(self, import_method_chooser, connect):
        """
        """
        super(CommentsImportFields, self).__init__()
        self.import_method_chooser = import_method_chooser
        self.layout.insertStretch(-1, 0)

    def alter_data(self, observations):
        observations = copy.deepcopy(observations)
        parameter_name = self.import_method_chooser.parameter_name
        comment_obsdict = {}
        dateformat = '%Y%M%D %H:%m:%s'
        for observation in observations:
            if observation[u'parametername'] == parameter_name:
                datestring = datetime.strftime(observation[u'date_time'], dateformat)
                comment_obsdict.setdefault(observation[u'sublocation'], {})[datestring] = observation

        for observation in observations:
            if observation[u'parametername'] != parameter_name:
                datestring = datetime.strftime(observation[u'date_time'], dateformat)
                comment_obs = comment_obsdict.get(observation[u'sublocation'], {}).get(datestring, None)
                if comment_obs != None:
                    observation[u'comment'] = comment_obs[u'value']
                    comment_obs[u'skip_comment_import'] = True

        return observations


class WLevelsImportFields(RowEntry):
    """
    """

    def __init__(self, import_method_chooser, connect):
        """
        """
        super(WLevelsImportFields, self).__init__()
        self.import_method_chooser = import_method_chooser
        self.layout.insertStretch(-1, 0)

    def alter_data(self, observations):
        return observations


class WFlowImportFields(RowEntryGrid):
    """
    This class should create a layout and populate it with question boxes relevant to w_flow import which is probably "flowtype" and "unit" dropdown lists.
    """


    def __init__(self, import_method_chooser, connect):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super(WFlowImportFields, self).__init__()
        self.connect = connect
        self._import_method_chooser = import_method_chooser
        self.label_flowtype = PyQt4.QtGui.QLabel(u'Flowtype: ')
        self.__flowtype = default_combobox()
        self._flowtypes_units = defs.w_flow_flowtypes_units()
        self.__flowtype.addItems(sorted(self._flowtypes_units.keys()))
        self.label_unit = PyQt4.QtGui.QLabel(u'Unit: ')
        self.__unit = default_combobox()
        self.connect(self.__flowtype, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda : self.fill_list(self.__unit, self.flowtype, self._flowtypes_units))

        self.layout.addWidget(self.label_flowtype, 0, 0)
        self.layout.addWidget(self.__flowtype, 1, 0)
        self.layout.addWidget(self.label_unit, 0, 1)
        self.layout.addWidget(self.__unit, 1, 1)
        self.layout.setColumnStretch(2, 1)

        #self.layout.addStretch()

    @property
    def flowtype(self):
        return utils.returnunicode(self.__flowtype.currentText())

    @flowtype.setter
    def flowtype(self, value):
        self.__flowtype.setEditText(value)

    @property
    def unit(self):
        return utils.returnunicode(self.__unit.currentText())

    @unit.setter
    def unit(self, value):
        self.__unit.setEditText(utils.returnunicode(value))

    def fill_list(self, combobox_var, parameter_var, parameter_list_dict):
        """

        :param combobox_var: a QComboBox object
        :param parameter_var: a string parameter name
        :param parameter_list_dict: A dict like  {u'Accvol': [(u'm3',)], u'Momflow': [(u'l/s',)]}
        :return:
        """
        vals = parameter_list_dict.get(parameter_var, None)
        if vals is None:
            vals = list(sorted(set([val for vals_list in parameter_list_dict.values() for val in vals_list[0]])))
        else:
            vals = list(vals[0])
        combobox_var.clear()
        combobox_var.addItem(u'')
        combobox_var.addItems(utils.returnunicode(vals, keep_containers=True))

    def get_settings(self):
        return OrderedDict([(u'flowtype', self.flowtype), (u'unit', self.unit)])

    def alter_data(self, observations):
        if not self.flowtype:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, flowtype not given')
            return u'cancel'
        if not self.unit:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, unit not given')
            return u'cancel'

        observations = copy.deepcopy(observations)
        for observation in observations:
            if observation[u'parametername'] == self._import_method_chooser.parameter_name:
                observation[u'flowtype'] = self.flowtype
                observation[u'unit'] = self.unit

        return observations


class WQualFieldImportFields(RowEntryGrid):
    """
    This class should create a layout and populate it with question boxes relevant to w_qual_fields import which is probably "parameter", "unit" dropdown lists.
    And a depth dropdown list which is populated by the parameternames. The purpose is that the user should select which parametername to use as the depth variable

    """

    def __init__(self, import_method_chooser, connect):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super(WQualFieldImportFields, self).__init__()
        self.connect = connect
        self._import_method_chooser = import_method_chooser
        self.label_parameter = PyQt4.QtGui.QLabel(u'Parameter: ')
        self.__parameter = default_combobox()
        self._parameters_units = defs.w_qual_field_parameter_units()
        self.__parameter.addItems(self._parameters_units.keys())
        self.label_unit = PyQt4.QtGui.QLabel(u'Unit: ')
        self.__unit = default_combobox()
        self.label_depth = PyQt4.QtGui.QLabel(u'Depth parameter: ')
        self.__depth = default_combobox()
        self.__depth.addItems(self._import_method_chooser.parameter_names)
        self.__instrument = default_combobox()
        self.label_instrument = PyQt4.QtGui.QLabel(u'Instrument: ')
        self.parameter_instruments = {}
        for parameter, unit_instrument_staff_date_time_list_of_lists in definitions.midvatten_defs.get_last_used_quality_instruments().iteritems():
            for unit, instrument, staff, date_time, in unit_instrument_staff_date_time_list_of_lists:
                self.parameter_instruments.setdefault(parameter, set()).add(instrument)

        for parameter, instrument_set in self.parameter_instruments.iteritems():
            self.parameter_instruments[parameter] = list(instrument_set)

        self.layout.addWidget(self.label_parameter, 0, 0)
        self.layout.addWidget(self.__parameter, 1, 0)
        self.layout.addWidget(self.label_unit, 0, 1)
        self.layout.addWidget(self.__unit, 1, 1)
        self.layout.addWidget(self.label_depth, 0, 2)
        self.layout.addWidget(self.__depth, 1, 2)
        self.layout.addWidget(self.label_instrument, 0, 3)
        self.layout.addWidget(self.__instrument, 1, 3)
        self.layout.setColumnStretch(4, 1)

        self.connect(self.__parameter, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda : self.fill_list(self.__unit, self.parameter, self._parameters_units))

        self.connect(self.__parameter, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self.fill_list(self.__instrument, self.parameter, self.parameter_instruments))

    def alter_data(self, observation, observations):
        observation = copy.deepcopy(observation)
        observation[u'unit'] = self.unit
        observation[u'parameter'] = self.parameter
        observation[u'instrument'] = self.instrument
        observation[u'depth'] = None
        if self.depth is not None:
            depth = [_observation[u'value'] for _observation in observations for _observation in observations
                     if all(_observation[u'date_time'] == observation[u'date_time'], _observation[u'sublocation'] == observation[u'sublocation' ])]
            if depth:
                observation[u'depth'] = depth
        return observation

    @property
    def parameter(self):
        return utils.returnunicode(self.__parameter.currentText())

    @parameter.setter
    def parameter(self, value):
        self.__parameter.setEditText(value)

    @property
    def unit(self):
        return utils.returnunicode(self.__unit.currentText())

    @unit.setter
    def unit(self, value):
        self.__unit.setEditText(utils.returnunicode(value))

    @property
    def depth(self):
        return utils.returnunicode(self.__depth.currentText())

    @depth.setter
    def depth(self, value):
        self.__depth.setEditText(utils.returnunicode(value))

    @property
    def instrument(self):
        return utils.returnunicode(self.__instrument.currentText())

    @instrument.setter
    def instrument(self, value):
        self.__instrument.setEditText(utils.returnunicode(value))

    def fill_list(self, combobox_var, parameter_var, parameter_list_dict):
        """

        :param combobox_var: a QComboBox object
        :param parameter_var: a string parameter name
        :param parameter_list_dict: A dict like  {u'Accvol': [(u'm3',)], u'Momflow': [(u'l/s',)]}
        :return:
        """
        vals = parameter_list_dict.get(parameter_var, None)
        if vals is None:
            vals = list(sorted(set([val[0] if isinstance(val, (list, tuple)) else val for vals_list in parameter_list_dict.values() for val in vals_list])))
        else:
            vals = sorted([val[0] if isinstance(val, (list, tuple)) else val for val in vals])

        combobox_var.clear()
        combobox_var.addItem(u'')
        combobox_var.addItems(utils.returnunicode(vals, keep_containers=True))

    def get_settings(self):
        return OrderedDict([(u'parameter', self.parameter),
                           (u'unit', self.unit),
                           (u'depth', self.depth),
                           (u'instrument', self.instrument)])

    def alter_data(self, observations):
        if not self.parameter:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, parameter not given')
            return u'cancel'
        if not self.unit:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, unit not given')
            return u'cancel'
        if not self.instrument:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, instrument not given')
            return u'cancel'

        observations = copy.deepcopy(observations)
        depth_dict = dict([(obs[u'date_time'], obs[u'value']) for obs in observations if obs[u'parametername'] == self.depth])
        for observation in observations:
            try:
                if observation[u'parametername'] == self._import_method_chooser.parameter_name:
                    observation[u'depth'] = depth_dict.get(observation[u'date_time'], u'')
                    observation[u'parameter'] = self.parameter
                    observation[u'instrument'] = self.instrument
                    observation[u'unit'] = self.unit
            except TypeError:
                utils.MessagebarAndLog.critical(bar_msg="Import error. See message log panel",
                                                log_msg="error on observation : " + str(observation) +
                                                        "\nand parameter: " + self.parameter)
                raise TypeError
        return observations


def default_combobox(editable=True):
    combo_box = PyQt4.QtGui.QComboBox()
    combo_box.setEditable(editable)
    combo_box.setSizeAdjustPolicy(PyQt4.QtGui.QComboBox.AdjustToContents)
    combo_box.addItem(u'')
    return combo_box
