# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that enables quick export of data from the database
                              -------------------
        begin                : 2015-08-30
        copyright            : (C) 2011 by joskal
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

import ast
import copy
import json
import os.path
from builtins import object
from builtins import range
from builtins import str
from collections import OrderedDict

import qgis.PyQt
import qgis.gui
from qgis.gui import QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt import QtWidgets
# from qgis._core import QgsProject
from qgis.core import QgsProject, QgsWkbTypes, QgsGeometry, QgsVectorLayer, QgsMapLayer, QgsCoordinateTransform, \
    QgsCoordinateReferenceSystem, QgsMapLayerProxyModel, Qgis

import midvatten.definitions.midvatten_defs as defs
from midvatten.tools.utils import common_utils, midvatten_utils, db_utils, gui_utils
from midvatten.tools.utils.common_utils import returnunicode as ru, start_waiting_cursor, stop_waiting_cursor
from midvatten.tools.utils.gui_utils import SplitterWithHandel, ExtendedQPlainTextEdit, get_line, set_combobox, VRowEntry

export_fieldlogger_ui_dialog =  qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]
parameter_browser_dialog = qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'fieldlogger_parameter_browser.ui'))[0]

class ExportToFieldLogger(QtWidgets.QMainWindow, export_fieldlogger_ui_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate('ExportToFieldLogger', "Export to Fieldlogger dialog"))) # Set the title for the dialog

        self.widget.setMinimumWidth(180)

        try:
            tables_columns = db_utils.tables_columns()
        except common_utils.UsageError as e:
            tables_columns = {}
            common_utils.MessagebarAndLog.info(bar_msg=str(e))

        self.parameter_groups = None

        self.stored_settingskey = 'fieldlogger_export_pgroups'
        self.stored_settingskey_parameterbrowser = 'fieldlogger_export_pbrowser'
        self.stored_settingskey_format = 'fieldlogger_export_format'

        for settingskey in [self.stored_settingskey, self.stored_settingskey_parameterbrowser, self.stored_settingskey_format]:
            if settingskey not in self.ms.settingsdict:
                common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('ExportToFieldLogger', '%s did not exist in settingsdict')) % settingskey)


        self.export_format_row = VRowEntry()
        self.export_format_row.layout.setContentsMargins(0, 0, 0, 0)
        self.export_as_fieldlogger = QtWidgets.QRadioButton(
            QCoreApplication.translate('ExportToFieldLogger', 'FieldLogger'))
        self.export_as_fieldform = QtWidgets.QRadioButton(
            QCoreApplication.translate('ExportToFieldLogger', 'FieldForm'))
        self.export_format_row.layout.addWidget(QtWidgets.QLabel(QCoreApplication.translate('ExportToFieldLogger', 'Export format')))
        self.export_format_row.layout.addWidget(self.export_as_fieldlogger)
        self.export_format_row.layout.addWidget(self.export_as_fieldform)
        self.gridLayout_buttons.addWidget(self.export_format_row.widget,
                                          self.gridLayout_buttons.rowCount(), 0)
        self.gridLayout_buttons.addWidget(get_line(),
                                          self.gridLayout_buttons.rowCount(), 0)
        self.export_as_fieldlogger.setChecked(True)
        self.export_as_fieldform.clicked.connect(lambda x: self.parameter_browser.use_fieldform())
        self.export_as_fieldlogger.clicked.connect(lambda x: self.parameter_browser.use_fieldlogger())
        if common_utils.get_stored_settings(self.ms, self.stored_settingskey_format, 'FieldLogger', skip_ast=True).lower() == 'fieldform':
            self.export_as_fieldform.setChecked(True)

        self.obs_from_obs_points = QtWidgets.QRadioButton(
            QCoreApplication.translate('ExportToFieldLogger', 'table obs_points (id obsid)'))
        self.obs_from_vlayer = QtWidgets.QRadioButton(
            QCoreApplication.translate('ExportToFieldLogger', 'point layer:'))
        self.obslayer = ObsLayer(self.iface, self.obs_from_vlayer)
        self.obs_from_row = VRowEntry()
        self.obs_from_row.layout.setContentsMargins(0, 0, 0, 0)
        self.obs_from_row.layout.addWidget(self.obs_from_obs_points)
        self.obs_from_row.layout.addWidget(self.obs_from_vlayer)


        self.parameter_groups = self.create_parameter_groups_using_stored_settings(
            common_utils.get_stored_settings(self.ms, self.stored_settingskey),
            self.obslayer)
        if self.parameter_groups is None or not self.parameter_groups:
            self.parameter_groups = [ParameterGroup(self.obslayer)]

        self.main_vertical_layout.addWidget(QtWidgets.QLabel(ru(QCoreApplication.translate('ExportToFieldLogger', 'Fieldlogger input fields and locations:'))))
        self.main_vertical_layout.addWidget(get_line())
        self.splitter = SplitterWithHandel(qgis.PyQt.QtCore.Qt.Vertical)
        self.main_vertical_layout.addWidget(self.splitter)

        #This is about adding a messagebar to the fieldlogger window. But for some reason qgis crashes or closes
        #when the timer ends for the regular messagebar
        #self.lbl = MessageBar(self.splitter)
        #qgis.utils.iface.optional_bar = self.lbl

        self.widgets_layouts = self.init_splitters_layouts(self.splitter)

        if self.parameter_groups:
            for export_object in self.parameter_groups:
                self.add_parameter_group_to_gui(self.widgets_layouts, export_object)

        #Buttons

        #ParameterUnitBrowser
        self.parameter_browser = ParameterBrowser(tables_columns, self.widget, use_fieldlogger=self.export_as_fieldlogger.isChecked())
        self.parameter_browser_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Create Input Fields')))
        self.gridLayout_buttons.addWidget(self.parameter_browser_button, self.gridLayout_buttons.rowCount(), 0)
        self.parameter_browser_button.clicked.connect(
                     lambda : self.parameter_browser.show())

        self.update_parameter_browser_using_stored_settings(
            common_utils.get_stored_settings(self.ms, self.stored_settingskey_parameterbrowser), self.parameter_browser)

        self.add_parameter_group = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'More Fields and Locations')))
        self.add_parameter_group.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'Creates an additional empty input field group.')))
        self.gridLayout_buttons.addWidget(self.add_parameter_group, self.gridLayout_buttons.rowCount(), 0)
        #Lambda and map is used to run several functions for every button click
        self.add_parameter_group.clicked.connect(self._add_parameter_group)

        self.gridLayout_buttons.addWidget(get_line(), self.gridLayout_buttons.rowCount(), 0)

        # obsid-layers:
        self.gridLayout_buttons.addWidget(QtWidgets.QLabel(
            QCoreApplication.translate('ExportToFieldLogger', 'Locations from:')))
        self.gridLayout_buttons.addWidget(self.obs_from_row.widget, self.gridLayout_buttons.rowCount(), 0)
        self.gridLayout_buttons.addWidget(self.obslayer.widget, self.gridLayout_buttons.rowCount(), 0)
        self.gridLayout_buttons.addWidget(get_line(), self.gridLayout_buttons.rowCount(), 0)

        if tables_columns:
            self.obs_from_obs_points.setChecked(True)
        else:
            self.obs_from_vlayer.setChecked(True)

        # Obsid settings

        #Buttons
        self.save_settings_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Save settings')))
        self.save_settings_button.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'Saves the current input fields settings.')))
        self.gridLayout_buttons.addWidget(self.save_settings_button, self.gridLayout_buttons.rowCount(), 0)
        self.save_settings_button.clicked.connect(self.save_stored_settings)

        self.clear_settings_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Clear settings')))
        self.clear_settings_button.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'Clear all input fields settings.')))
        self.gridLayout_buttons.addWidget(self.clear_settings_button, self.gridLayout_buttons.rowCount(), 0)
        self.clear_settings_button.clicked.connect(self.clear_settings)

        self.settings_strings_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Settings strings')))
        self.settings_strings_button.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'Access the settings strings ("Create input fields" and input fields) to copy and paste all settings between different qgis projects.\n Usage: Select string and copy to a text editor or directly into Settings strings dialog of another qgis project.')))
        self.gridLayout_buttons.addWidget(self.settings_strings_button, self.gridLayout_buttons.rowCount(), 0)
        self.settings_strings_button.clicked.connect(lambda x: self.settings_strings_dialogs())

        self.default_settings_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Default settings')))
        self.default_settings_button.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'Updates "Create input fields" and input fields to default settings.')))
        self.gridLayout_buttons.addWidget(self.default_settings_button, self.gridLayout_buttons.rowCount(), 0)
        self.default_settings_button.clicked.connect(lambda x: self.restore_default_settings())

        self.gridLayout_buttons.addWidget(get_line(), self.gridLayout_buttons.rowCount(), 0)

        self.preview_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Preview')))
        self.preview_button.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'View a preview of the Fieldlogger location file as pop-up info.')))
        self.gridLayout_buttons.addWidget(self.preview_button, self.gridLayout_buttons.rowCount(), 0)
        # Lambda and map is used to run several functions for every button click
        self.preview_button.clicked.connect(lambda x: self.preview())

        self.export_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ExportToFieldLogger', 'Export')))
        self.export_button.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger', 'Exports the current combination of locations and input fields to a Fieldlogger location file.')))
        self.gridLayout_buttons.addWidget(self.export_button, self.gridLayout_buttons.rowCount(), 0)
        # Lambda and map is used to run several functions for every button click
        self.export_button.clicked.connect(lambda x: self.export())

        self.gridLayout_buttons.setRowStretch(self.gridLayout_buttons.rowCount(), 1)

        self.show()

    @staticmethod
    def init_splitters_layouts(splitter):
        widgets_layouts = []
        for nr in range(2):
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout()
            widget.setLayout(layout)
            splitter.addWidget(widget)
            widgets_layouts.append((widget, layout))
        return widgets_layouts

    def add_parameter_group_to_gui(self, widgets_layouts, parameter_group):

            self.create_widget_and_connect_widgets(widgets_layouts[0][1],
                                                   [QtWidgets.QLabel(ru(QCoreApplication.translate('ExportToFieldLogger', 'Sub-location suffix'))),
                                                    parameter_group._sublocation_suffix,
                                                    QtWidgets.QLabel(ru(QCoreApplication.translate('ExportToFieldLogger', 'Input fields'))),
                                                    parameter_group._input_field_group_list])

            self.create_widget_and_connect_widgets(widgets_layouts[1][1],
                                                   [QtWidgets.QLabel(ru(QCoreApplication.translate('ExportToFieldLogger', 'Locations'))),
                                                    parameter_group.paste_from_selection_button,
                                                    parameter_group._obsid_list,
                                                   QtWidgets.QLabel(ru(QCoreApplication.translate('ExportToFieldLogger', 'Location suffix\n(ex. project number)'))),
                                                   parameter_group._location_suffix])

    @staticmethod
    def create_widget_and_connect_widgets(parent_layout=None, widgets=None, layout_class=QtWidgets.QVBoxLayout):
        new_widget = QtWidgets.QWidget()
        layout = layout_class()
        new_widget.setLayout(layout)
        if parent_layout is not None:
            parent_layout.addWidget(new_widget)
        for widget in widgets:
            layout.addWidget(widget)
        return new_widget

    @staticmethod
    def create_parameter_groups_using_stored_settings(stored_settings, obslayer):
        """
        """
        if not stored_settings or stored_settings is None:
            return []

        parameter_groups = []
        for index, attrs in stored_settings:
            parameter_group = ParameterGroup(obslayer)
            attrs_set = False
            for attr in attrs:
                if hasattr(parameter_group, attr[0]):
                    setattr(parameter_group, attr[0], attr[1])
                    attrs_set = True
                else:
                    common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('ExportToFieldLogger', 'Tried to load input field groups but the variable %s did not exist.')) % attr[0])

            if attrs_set:
                parameter_groups.append(parameter_group)

        return parameter_groups

    @staticmethod
    def update_parameter_browser_using_stored_settings(stored_settings, parameter_browser):
        if not stored_settings or stored_settings is None:
            return
        for index, attrs in stored_settings:
            for attr in attrs:
                try:
                    if hasattr(parameter_browser, ru(attr[0])):
                        setattr(parameter_browser, ru(attr[0]), ru(attr[1], keep_containers=True))
                    else:
                        common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('ExportToFieldLogger',
                                                                                         'Tried to load input field fields browser but the variable %s did not exist.')) %
                                                                              attr[0])
                except UnicodeEncodeError:
                    common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('ExportToFieldLogger',
                                                                                         'Tried to load input field fields browser but the string %s could not be handled.')) %
                                                                              ru(attr[1]))

    @staticmethod
    def update_stored_settings(objects_with_get_settings):
        return [[index, copy.deepcopy(an_object.get_settings())] for index, an_object in enumerate(objects_with_get_settings) if an_object.get_settings()]

    def restore_default_settings(self):
        input_field_browser, input_fields_groups = defs.export_fieldlogger_defaults('FieldLogger' if self.export_as_fieldlogger.isChecked() else 'FieldForm')
        self.update_settings(input_field_browser, self.stored_settingskey_parameterbrowser)
        self.update_settings(input_fields_groups, self.stored_settingskey)
        common_utils.save_stored_settings(self.ms,
                                          'FieldForm' if self.export_as_fieldform.isChecked() else 'FieldLogger',
                                          self.stored_settingskey_format, skip_ast=True)

        common_utils.pop_up_info(ru(QCoreApplication.translate('ExportToFieldLogger', 'Input fields and "Create Input Fields" updated to default.\nRestart Export to Fieldlogger dialog to complete,\nor press "Save settings" to save current input fields settings again.')))

    def settings_strings_dialogs(self):

        msg = ru(QCoreApplication.translate('ExportToFieldLogger', 'Edit the settings string for input fields browser and restart export fieldlogger dialog\nto load the change.'))
        browser_updated = self.ask_and_update_settings([self.parameter_browser], self.stored_settingskey_parameterbrowser, msg)
        msg = ru(QCoreApplication.translate('ExportToFieldLogger', 'Edit the settings string for input fields groups and restart export fieldlogger dialog\nto load the change.'))
        groups_updated = self.ask_and_update_settings(self.parameter_groups, self.stored_settingskey, msg)
        if browser_updated or groups_updated:
            common_utils.pop_up_info(ru(QCoreApplication.translate('ExportToFieldLogger', 'Settings updated. Restart Export to Fieldlogger dialog\nor press "Save settings" to undo.')))

    def ask_and_update_settings(self, objects_with_get_settings, settingskey, msg=''):

        old_string = common_utils.anything_to_string_representation(self.update_stored_settings(objects_with_get_settings))

        new_string = QtWidgets.QInputDialog.getText(None, ru(QCoreApplication.translate('ExportToFieldLogger', "Edit settings string")), msg,
                                                           QtWidgets.QLineEdit.Normal, old_string)
        if not new_string[1]:
            return False

        new_string_text = ru(new_string[0])

        self.update_settings(new_string_text, settingskey)

    def update_settings(self, new_string_text, settingskey):
        try:
            stored_settings = ast.literal_eval(new_string_text)
        except SyntaxError as e:
            stored_settings = []
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('ExportToFieldLogger', 'Parsing settings failed, see log message panel')), log_msg=ru(QCoreApplication.translate('ExportToFieldLogger', 'Parsing settings failed using string\n%s\n%s')) % (new_string_text, str(e)))
            return False

        common_utils.save_stored_settings(self.ms, stored_settings, settingskey)

        return True

    def get_latlons(self):
        if self.obs_from_obs_points.isChecked():
            try:
                latlons = db_utils.get_latlon_for_all_obsids()
            except common_utils.UsageError as e:
                common_utils.MessagebarAndLog.warning(bar_msg=str(e))
                latlons = {}
        else:
            latlons = self.obslayer.get_latlon_for_features()
        latlons = {str(k): v for k, v in latlons.items()}
        return latlons

    @common_utils.general_exception_handler
    def export(self):
        start_waiting_cursor()
        common_utils.save_stored_settings(self.ms, self.update_stored_settings(self.parameter_groups), self.stored_settingskey)
        if self.export_as_fieldform.isChecked():
            self.write_to_file(json.dumps(self.create_json_export(self.parameter_groups, self.get_latlons()), ensure_ascii=False, indent=4), filter='json (*.json)')
        else:
            self.write_to_file('\n'.join(self.create_export_printlist(self.parameter_groups, self.get_latlons())))
        stop_waiting_cursor()

    def preview(self):
        if self.export_as_fieldform.isChecked():
            output = json.dumps(self.create_json_export(self.parameter_groups, self.get_latlons()), ensure_ascii=False) #.encode('utf8')
        else:
            output = '\n'.join(self.create_export_printlist(self.parameter_groups, self.get_latlons()))
        QtWidgets.QMessageBox.information(None, 'Preview', output)

    @staticmethod
    def organize_for_export(parameter_groups, latlons):
        sublocations_locations = {}
        locations_sublocations = OrderedDict()
        locations_lat_lon = OrderedDict()
        sublocations_parameters = OrderedDict()

        parameters_inputtypes_hints = OrderedDict()

        for index, parameter_group in enumerate(parameter_groups):
            _parameters_inputtypes_hints = parameter_group.input_field_group_list
            if not _parameters_inputtypes_hints:
                common_utils.MessagebarAndLog.warning(
                    bar_msg=ru(QCoreApplication.translate('ExportToFieldLogger', "Warning: Empty input fields list for group nr %s"))%str(index + 1))
                continue

            for location, sublocation, obsid in parameter_group.locations_sublocations_obsids:
                lat, lon = [None, None]

                if location not in locations_lat_lon:
                    lat, lon = latlons.get(obsid, [None, None])
                    if not lat or not lon:
                        common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ExportToFieldLogger', 'Critical: Obsid %s did not have lat-lon coordinates. Check obs_points table')) % obsid)
                        continue

                #If a parameter appears again, delete it and add it again to make it appear last.
                for _parameter_inputtype_hint in _parameters_inputtypes_hints:
                    _parameter = _parameter_inputtype_hint.split(';')[0]

                    existed_p_i_h = parameters_inputtypes_hints.get(_parameter, None)
                    if existed_p_i_h is not None:
                        if existed_p_i_h != _parameter_inputtype_hint:
                            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('ExportToFieldLogger', 'Warning, parameter error, see log message panel')), log_msg=ru(QCoreApplication.translate('ExportToFieldLogger', 'The parameter %s exists more than once and the last one will overwrite the previous.')) % _parameter)
                        del parameters_inputtypes_hints[_parameter]
                    parameters_inputtypes_hints[_parameter] = _parameter_inputtype_hint

                    existed = sublocations_parameters.get(sublocation, [])
                    if _parameter not in existed:
                        sublocations_parameters.setdefault(sublocation, []).append(_parameter)

                if sublocations_parameters.get(sublocation, []):
                    if location not in locations_lat_lon:
                        locations_lat_lon[location] = (ru(lat), ru(lon))
                    locations_sublocations.setdefault(location, []).append(sublocation)
                    if sublocation not in sublocations_locations:
                        sublocations_locations[sublocation] = location
        return sublocations_locations, locations_sublocations, locations_lat_lon, sublocations_parameters, parameters_inputtypes_hints


    @staticmethod
    def create_export_printlist(parameter_groups, latlons):
        """
        Creates a result list with FieldLogger format from selected obsids and parameters
        :return: a list with result lines to export to file
        """
        sublocations_locations, locations_sublocations, locations_lat_lon, sublocations_parameters, parameters_inputtypes_hints = ExportToFieldLogger.organize_for_export(parameter_groups, latlons)

        printlist = []
        printlist.append("NAME;INPUTTYPE;HINT")
        #Add a space after the parameter rows just to be sure that there will always be a hint (it needs to be.
        printlist.extend([p_i_h + ' ' if not p_i_h.endswith(' ') else p_i_h for p_i_h in list(parameters_inputtypes_hints.values())])

        printlist.append('NAME;SUBNAME;LAT;LON;INPUTFIELD')
        for location, sublocations in sorted(locations_sublocations.items()):
            lat, lon = locations_lat_lon[location]

            for sublocation in sorted(sublocations):

                parameters = '|'.join(sublocations_parameters[sublocation])
                printrow = ';'.join([location, sublocation, lat, lon, parameters])
                #This test is really bad and is due to some logical error above.
                if printrow not in printlist:
                    printlist.append(printrow)

        return printlist

    @staticmethod
    def write_to_file(out_string, filter='csv (*.csv)'):
        stop_waiting_cursor()
        filename = common_utils.get_save_file_name_no_extension(parent=None, caption=ru(QCoreApplication.translate('ExportToFieldLogger', 'Choose a file name')), directory='', filter=filter)
        start_waiting_cursor()
        if os.path.splitext(filename)[1] != f".{filter.split()[0]}":
            filename += f".{filter.split()[0]}"
        try:
            with open(filename, 'w', encoding='utf8') as f:
                f.write(out_string)
        except IOError as e:
            common_utils.pop_up_info(ru(QCoreApplication.translate('ExportToFieldLogger', "Writing of file failed!: %s ")) % str(e))
        except UnicodeDecodeError as e:
            common_utils.pop_up_info(ru(QCoreApplication.translate('ExportToFieldLogger', "Error writing %s")) % str(out_string))

    @staticmethod
    def create_json_export(parameter_groups, latlons):
        sublocations_locations, locations_sublocations, locations_lat_lon, sublocations_parameters, parameters_inputtypes_hints = ExportToFieldLogger.organize_for_export(parameter_groups, latlons)
        json_output = {}
        for parameter, _parameters_inputtypes_hints in parameters_inputtypes_hints.items():
            print(f"_parameters_inputtypes_hints {_parameters_inputtypes_hints}")
            json_output.setdefault('inputfields', {}).update(json.loads(_parameters_inputtypes_hints))

        # TODO: Make sure this works.
        for location, sublocations in sorted(locations_sublocations.items()):
            loc_dict = {}
            lat, lon = locations_lat_lon[location]
            loc_dict['lat'] = float(lat)
            loc_dict['lon'] = float(lon)
            #loc_dict['lat'], loc_dict['lon'] = locations_lat_lon[location]
            for sublocation in sorted(sublocations):
                inputfields = [parameter_name for d in sublocations_parameters[sublocation]
                               for parameter_name in ast.literal_eval(d).keys()]
                loc_dict.setdefault('sublocations', {})[sublocation] = {'inputfields': inputfields}
            json_output.setdefault('locations', {})[location] = loc_dict
        print(f"Got output {json_output}")
        return json_output

    def save_stored_settings(self):
        common_utils.save_stored_settings(self.ms,
                                          self.update_stored_settings(
                                              self.parameter_groups),
                                          self.stored_settingskey)

        common_utils.save_stored_settings(self.ms,
                                          self.update_stored_settings(
                                              [self.parameter_browser]),
                                          self.stored_settingskey_parameterbrowser)

        common_utils.save_stored_settings(self.ms,
                                          'FieldForm' if self.export_as_fieldform.isChecked() else 'FieldLogger',
                                          self.stored_settingskey_format, skip_ast=True)


    def clear_settings(self):
        common_utils.save_stored_settings(self.ms, [], self.stored_settingskey),
        common_utils.save_stored_settings(self.ms, 'FieldLogger', self.stored_settingskey_format, skip_ast=True)
        common_utils.pop_up_info(ru(QCoreApplication.translate('ExportToFieldLogger',
            'Settings cleared. Restart Export to Fieldlogger dialog to complete,\nor press "Save settings" to save current input fields settings again.')))

    def _add_parameter_group(self):
        self.parameter_groups.append(ParameterGroup(self.obslayer))
        self.add_parameter_group_to_gui(self.widgets_layouts,   self.parameter_groups[-1])




class ParameterGroup(object):
    def __init__(self, obslayer):
        """
        """
        self.obslayer = obslayer
        #Widget list:

        self._location_suffix = QtWidgets.QLineEdit()
        self._sublocation_suffix = QtWidgets.QLineEdit()
        self._input_field_group_list = ExtendedQPlainTextEdit(keep_sorted=False)
        self._obsid_list = ExtendedQPlainTextEdit(keep_sorted=True)
        self.paste_from_selection_button = QtWidgets.QPushButton(ru(QCoreApplication.translate('ParameterGroup','Paste selected ids')))
        #------------------------------------------------------------------------
        self._location_suffix.setToolTip(ru(QCoreApplication.translate('ParameterGroup',
                                         """(optional)\n"""
                                         """The Fieldlogger location in the Fieldlogger map will be "obsid.LOCATION SUFFIX".\n\n"""
                                         """Location suffix is useful for separating locations with identical obsids.\n"""
                                         """ex: Location suffix 1234 --> obsid.1234""")))
        self._sublocation_suffix.setToolTip(ru(QCoreApplication.translate('ParameterGroup',
                                           """(optional)\n"""
                                            """Fieldlogger sub-location will be obsid.Location suffix.Sub-location suffix\n\n"""
                                            """Parameters sharing the same sub-location will be shown together.\n"""
                                            """Sub-location suffix is used to separate input fields into groups for the Fieldlogger user.\n"""
                                            """ex: level, quality, sample, comment, flow.""")))
        self._input_field_group_list.setToolTip(ru(QCoreApplication.translate('ParameterGroup',
                                       """Copy and paste input fields from "Create Input Fields" to this box\n"""
                                        """or from/to other input field boxes.\n"""
                                        """The input fields in Fieldlogger will appear in the same order as in\n"""
                                        """this list.\n"""
                                        """The topmost input field will be the first selected input field when\n"""
                                        """the user enters the input fields in Fieldlogger. (!!! If the input\n"""
                                        """field already exists in a previous group it will end up on top!!!)""")))
        locations_box_tooltip = ru(QCoreApplication.translate('ParameterGroup',
                               """Add locations to Locations box by selecting rows in the chosen layer (see "Locations from"\n"""
                                """in the left column) using it's attribute table or selection from map.\n"""
                                """Then click the button "Paste selected ids."\n"""
                                """Copy and paste obsids between Locations boxes."""))

        self._obsid_list.setToolTip(locations_box_tooltip)
        self.paste_from_selection_button.setToolTip(locations_box_tooltip)

        #-------------------------------------------------------------------------------------
        self.paste_from_selection_button.clicked.connect(
                         lambda : self.paste_from_selection())

    def paste_from_selection(self):
        if self.obslayer.obs_from_vlayer.isChecked():
            self._obsid_list.paste_data(
                common_utils.get_selected_features_as_tuple(layer_name=self.obslayer.current_layer(),
                                                                        column_name=self.obslayer.current_column()))
        else:
            try:
                self._obsid_list.paste_data(
                    common_utils.get_selected_features_as_tuple(layer_name='obs_points',
                                                                            column_name='obsid'))
            except common_utils.UsageError as e:
                common_utils.MessagebarAndLog.warning(bar_msg=str(e))

    def get_settings(self):
        settings = (('input_field_group_list', self.input_field_group_list),
                   ('location_suffix', self.location_suffix),
                   ('sublocation_suffix', self.sublocation_suffix))
        settings = tuple((k, v) for k, v in settings if v)
        return ru(settings, keep_containers=True)

    @property
    def location_suffix(self):
        return ru(self._location_suffix.text())

    @location_suffix.setter
    def location_suffix(self, value):
        self._location_suffix.setText(ru(value))

    @property
    def sublocation_suffix(self):
        return ru(self._sublocation_suffix.text())

    @sublocation_suffix.setter
    def sublocation_suffix(self, value):
        self._sublocation_suffix.setText(ru(value))

    @property
    def locations_sublocations_obsids(self):
        """

        :return: a list like [[obsid.locationsuffix as location, obsid.locationsuffix.sublocationsuffix as sublocation, obsid), ...]
        """
        locations_sublocations_obsids = [('.'.join([x for x in [ru(obsid), ru(self.location_suffix)] if x]),
                                      '.'.join([x for x in [ru(obsid), ru(self.location_suffix), ru(self.sublocation_suffix)] if x]), ru(obsid))
                                     for obsid in set(self._obsid_list.get_all_data())]
        return locations_sublocations_obsids

    @property
    def input_field_group_list(self):
        return ru(self._input_field_group_list.get_all_data(), keep_containers=True)

    @input_field_group_list.setter
    def input_field_group_list(self, value):
        value = ru(value, keep_containers=True)
        if isinstance(value, (list, tuple)):
            self._input_field_group_list.paste_data(paste_list=value)
        else:
            self._input_field_group_list.paste_data(paste_list=value.split('\n'))


class ParameterBrowser(QtWidgets.QDialog, parameter_browser_dialog):
    def __init__(self, tables_columns, parent=None, use_fieldlogger=True):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        #Widgets:
        # ------------------------------------------------------------------------------------
        #Other widgets in the ui-file
        self._input_field_list = ExtendedQPlainTextEdit(keep_sorted=True)
        self._input_field_list.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)

        # ------------------------------------------------------------------------------------
        self._parameter_table.addItem('')
        self._parameter_table.addItems(sorted(tables_columns.keys()))
        self._parameter_table.currentIndexChanged.connect(
                     lambda: self.replace_items(self._parameter_columns, tables_columns.get(self.parameter_table, [])))
        self._parameter_columns.currentIndexChanged.connect(
                     lambda: self.replace_items(self._distinct_parameter, self.get_distinct_values(self.parameter_table, self.parameter_columns)))
        self._unit_table.addItem('')
        self._unit_table.addItems(sorted(tables_columns.keys()))
        self._unit_table.currentIndexChanged.connect(
                     lambda: self.replace_items(self._unit_columns, tables_columns.get(self.unit_table, [])))
        self._unit_columns.currentIndexChanged.connect(
                     lambda: self.replace_items(self._distinct_unit, self.get_distinct_values(self.unit_table, self.unit_columns)))

        self._distinct_parameter.editTextChanged.connect(
                     lambda: self._combined_name.setText('.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        self._distinct_unit.editTextChanged.connect(
                     lambda: self._combined_name.setText('.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))

        self._add_button.clicked.connect(
                lambda : self.combine_name(self.combined_name, self.input_type, self.hint, self.options, self.default_value))

        # ------------------------------------------------------------------------------------
        par_unit_tooltip = ru(QCoreApplication.translate('ParameterBrowser' ,
                           ('(optional)\n'
                            'When both parameter and unit is given, they will be combined to create the input field name.')))
        self._distinct_parameter.setToolTip(par_unit_tooltip)
        self._distinct_unit.setToolTip(par_unit_tooltip)
        self._combined_name.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger',
                                      '(mandatory)\n'
                                       'Either supply a chosen name directly or use parameter\n'
                                       'and unit boxes to create a name.\n'
                                       'ex: parameter.unit')))

        self._hint.setToolTip(ru(QCoreApplication.translate('ParameterBrowser', '(optional)\nHint given to the Fieldlogger/FieldForm user for the parameter. Ex: "depth to water"')))
        #------------------------------------------------------------------------------------
        self._input_field_list.setToolTip(ru(QCoreApplication.translate('ParameterBrowser', 'Copy input fields to the "Input Fields" boxes using ctrl+c, ctrl+v.')))
        self._input_field_list.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self._input_field_list.setMinimumWidth(200)
        #------------------------------------------------------------------------------------
        self.horizontalLayout.addWidget(self._input_field_list)

        self._options.setToolTip(ru(QCoreApplication.translate('ParameterBrowser', '(optional)\nThe options between which the user can choose when type=choice or type=multichoice.\n'
                                                                                   "Specify as a comma separated list, ex: 'OptionB', 'OptionB', 'OptionC'")))
        self._default_value.setToolTip(ru(QCoreApplication.translate('ParameterBrowser', "(optional)\nThe default value for an inputfield, only supported for type=choice")))


        self._use_fieldlogger = use_fieldlogger
        if use_fieldlogger:
            self.use_fieldlogger()
        else:
            self.use_fieldform()

        #self.horizontalLayoutWidget.setTabOrder(self._add_button, self._input_field_list)
        #self.horizontalLayoutWidget.setTabOrder(self._input_field_list, self._parameter_table)

    @staticmethod
    def get_distinct_values(tablename, columnname):
        if not tablename or not columnname:
            return []
        sql = '''SELECT distinct %s FROM %s'''%(columnname, tablename)
        connection_ok, result = db_utils.sql_load_fr_db(sql)

        if not connection_ok:
            common_utils.MessagebarAndLog.critical(
                bar_msg=ru(QCoreApplication.translate('ParameterBrowser', "Error, sql failed, see log message panel")),
                log_msg=ru(QCoreApplication.translate('ParameterBrowser', """Cannot get data from sql %s"""))%ru(sql))
            return []

        values = [col[0] for col in result]
        return values

    @staticmethod
    def replace_items(combobox, items):
        combobox.clear()
        combobox.addItem('')
        try:
            combobox.addItems(ru(items, keep_containers=True))
        except TypeError:
            for item in items:
                combobox.addItem(ru(item))

    def get_settings(self):
        if not self.input_field_list:
            return None
        settings = (('input_field_list', self.input_field_list),)
        return ru(settings, keep_containers=True)

    def combine_name(self, combined_name, input_type, hint, options=None, default=None):
        if self._use_fieldlogger:
            unique_names = [input_field.split(';')[0] for input_field in self.input_field_list]
            if not combined_name:
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ParameterBrowser', 'Error, input name not set')))
                return
            elif not input_type:
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ParameterBrowser', 'Error, input type not set')))
                return
            elif combined_name in unique_names:
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('ParameterBrowser', 'Error, input name already existing. No duplicates allowed')))
                return

            if not hint:
                common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('ParameterBrowser', 'Warning, hint not given and will be set to a space (" ") as it must exist')))
                hint = hint + ' '

            self._input_field_list.paste_data([';'.join([combined_name, input_type, hint])])

        else:
            # FieldForm format:
            input_field = {combined_name: {'type': input_type}}
            if hint:
                input_field['hint'] = hint
            if options and input_type in ('choice', 'multichoice'):
                input_field['options'] = ast.literal_eval(f"({options})")
            if default and type == 'choice':
                input_field['default_value'] = default
            self._input_field_list.paste_data([json.dumps(input_field, ensure_ascii=False)])

    @property
    def parameter_table(self):
        return ru(self._parameter_table.currentText())

    @parameter_table.setter
    def parameter_table(self, value):
        set_combobox(self._parameter_table, value)

    @property
    def parameter_columns(self):
        return ru(self._parameter_columns.currentText())

    @parameter_columns.setter
    def parameter_columns(self, value):
        set_combobox(self._parameter_columns, value)

    @property
    def distinct_parameter(self):
        return ru(self._distinct_parameter.currentText())

    @distinct_parameter.setter
    def distinct_parameter(self, value):
        set_combobox(self._distinct_parameter, value)

    @property
    def unit_table(self):
        return ru(self._unit_table.currentText())

    @unit_table.setter
    def unit_table(self, value):
        set_combobox(self._unit_table, value)

    @property
    def unit_columns(self):
        return ru(self._unit_columns.currentText())

    @unit_columns.setter
    def unit_columns(self, value):
        set_combobox(self._unit_columns, value)

    @property
    def distinct_unit(self):
        return ru(self._distinct_unit.currentText())

    @distinct_unit.setter
    def distinct_unit(self, value):
        set_combobox(self._distinct_unit, value)

    @property
    def combined_name(self):
        return ru(self._combined_name.text())

    @combined_name.setter
    def combined_name(self, value):
        self._combined_name.setText(ru(value))

    @property
    def input_type(self):
        return ru(self._input_type.currentText())

    @input_type.setter
    def input_type(self, value):
        set_combobox(self._input_type, value)

    @property
    def hint(self):
        return ru(self._hint.text())

    @hint.setter
    def hint(self, value):
        self._hint.setText(ru(value))

    @property
    def input_field_list(self):
        return ru(self._input_field_list.get_all_data(), keep_containers=True)

    @property
    def options(self):
        return ru(self._options.text())

    @options.setter
    def options(self, value):
        self._options.setText(ru(value))

    @property
    def default_value(self):
        return ru(self._default_value.text())

    @default_value.setter
    def default_value(self, value):
        self._default_value.setText(ru(value))


    @input_field_list.setter
    def input_field_list(self, value):
        value = ru(value, keep_containers=True)
        if isinstance(value, (list, tuple)):
            self._input_field_list.paste_data(paste_list=value)
        else:
            self._input_field_list.paste_data(paste_list=value.split('\n'))

    def use_fieldlogger(self):
        self._input_type.clear()
        self._input_type.addItem('')
        self._input_type.addItems(['numberDecimal|numberSigned', 'text'])
        self._input_type.setToolTip(ru(QCoreApplication.translate('ExportToFieldLogger',
                                                                  '(mandatory)\n'
                                                                  'Decides the keyboard layout in the Fieldlogger app.\n'
                                                                  'numberDecimal|numberSigned: Decimals with allowed "-" sign for FieldLogger app\n'
                                                                  'text: Text\n')))
        self._options.setEnabled(False)
        self._default_value.setEnabled(False)
        self._use_fieldlogger = True

    def use_fieldform(self):
        self._input_type.clear()
        self._input_type.addItem('')
        self._input_type.addItems(['number', 'text', 'choice', 'multichoice', 'photo', 'check', 'date', 'time', 'datetime'])
        self._input_type.setToolTip('')
        self._options.setEnabled(True)
        self._default_value.setEnabled(True)
        self._use_fieldlogger = False


class MessageBar(qgis.gui.QgsMessageBar):
    """
    From http://gis.stackexchange.com/a/152733
    """
    def __init__(self, parent=None):
        super(MessageBar, self).__init__(parent)
        self.parent().installEventFilter(self)

    def showEvent(self, event):
        self.resize(qgis.PyQt.QtCore.QSize(self.parent().geometry().size().width(), self.height()))
        self.move(0, self.parent().geometry().size().height() - self.height())
        self.raise_()

    def eventFilter(self, object, event):
        if event.type() == qgis.PyQt.QtCore.QEvent.Resize:
            self.showEvent(None)
        return super(MessageBar, self).eventFilter(object, event)

    def popWidget(self, QgsMessageBarItem=None):
        self.setParent(0)
        self.hide()


class ObsLayer(gui_utils.VRowEntry):
    def __init__(self, iface, obs_from_vlayer):
        super().__init__()
        self.obs_from_vlayer = obs_from_vlayer
        self.iface = iface

        self.vectorlayer_list = QgsMapLayerComboBox()
        self.vectorlayer_list.setFilters(Qgis.LayerFilter.PointLayer) # QgsMapLayerProxyModel.VectorLayer |
        self.vectorlayer_list.setAdditionalItems([''])
        self.vectorlayer_list.setCurrentIndex(self.vectorlayer_list.count()-1)

        self._vectorlayers = None
        self.column_list = QtWidgets.QComboBox()
        self.vectorlayer_list.layerChanged.connect(lambda x: self.update_column_list())

        self.obs_from_vlayer.toggled.connect(lambda: self.vectorlayer_list.setEnabled(self.obs_from_vlayer.isChecked()))
        self.obs_from_vlayer.toggled.connect(lambda: self.column_list.setEnabled(self.obs_from_vlayer.isChecked()))

        for combobox in [self.vectorlayer_list, self.column_list]:
            combobox.setEnabled(False)

        self.layout.addWidget(self.vectorlayer_list)
        self.layout.addWidget(
            QtWidgets.QLabel(QCoreApplication.translate('ObsLayer', 'id column:')))
        self.layout.addWidget(self.column_list)

    def update_column_list(self, select_column='obsid'):
        if select_column is None:
            select_column = self.current_column()

        self.column_list.clear()

        if self.current_layer() is not None:
            fields = self.current_layer().fields()
            fieldnames = [field.name() for field in fields]
            self.column_list.addItems(fieldnames)
            gui_utils.set_combobox(self.column_list, select_column)

    def get_selected(self):
        return common_utils.getselectedobjectnames(thelayer=self.current_layer(), column_name=self.current_column())

    def current_layer(self):
        return self.vectorlayer_list.currentLayer()

    def current_column(self):
        return self.column_list.currentText()

    def get_latlon_for_features(self):
        current_layer = self.current_layer()
        _from = QgsCoordinateReferenceSystem(current_layer.crs())
        _to = QgsCoordinateReferenceSystem('EPSG:4326')
        coordinatetransform = QgsCoordinateTransform(_from, _to, QgsProject.instance())
        fields = current_layer.fields()
        id_index = fields.indexFromName(self.current_column())

        def transform(geometry):
            geometry = QgsGeometry(geometry)
            geometry.transform(coordinatetransform)
            return geometry

        features = {f.attributes()[id_index]: transform(f.geometry()) for f in current_layer.getFeatures('True')}
        latlons = {k: ((v.asPoint().y(), v.asPoint().x()) if not v.isNull() else (None, None))
                    for k, v in features.items()}
        return latlons


