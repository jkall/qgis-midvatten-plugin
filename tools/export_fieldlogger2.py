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
import ast
import PyQt4
import os
import os.path
import qgis.utils
import copy
from collections import OrderedDict
import warnings
import qgis.gui

import midvatten_utils as utils
import definitions.midvatten_defs as defs
from import_data_to_db import midv_data_importer
import import_fieldlogger
from midvatten_utils import returnunicode

export_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]
parameter_browser_dialog = PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'fieldlogger_parameter_browser.ui'))[0]

class ExportToFieldLogger(PyQt4.QtGui.QMainWindow, export_fieldlogger_ui_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle("Export to FieldLogger file") # Set the title for the dialog

        self.widget.setMinimumWidth(180)

        tables_columns = defs.tables_columns()

        self.parameter_groups = None

        self.stored_settingskey = 'fieldlogger_export_pgroups'
        self.stored_settingskey_parameterbrowser = 'fieldlogger_export_pbrowser'

        for settingskey in [self.stored_settingskey, self.stored_settingskey_parameterbrowser]:
            if settingskey not in self.ms.settingsdict:
                utils.MessagebarAndLog.warning(bar_msg=settingskey + " did not exist in settingsdict")

        self.parameter_groups = self.create_parameter_groups_using_stored_settings(self.get_stored_settings(self.ms, self.stored_settingskey),
                                                                                   self.connect)
        if self.parameter_groups is None or not self.parameter_groups:
            self.parameter_groups = [ParameterGroup(self.connect)]


        self.main_vertical_layout.addWidget(PyQt4.QtGui.QLabel(u'Fieldlogger input fields and locations:'))
        self.main_vertical_layout.addWidget(get_line())
        self.splitter = PyQt4.QtGui.QSplitter(PyQt4.QtCore.Qt.Vertical)
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
        self.parameter_browser = ParameterBrowser(tables_columns, self.connect, self.widget)
        self.parameter_browser_button = PyQt4.QtGui.QPushButton(u'Create Input Fields')
        self.gridLayout_buttons.addWidget(self.parameter_browser_button, 0, 0)
        self.connect(self.parameter_browser_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda : self.parameter_browser.show())

        self.update_parameter_browser_using_stored_settings(self.get_stored_settings(self.ms, self.stored_settingskey_parameterbrowser), self.parameter_browser)

        self.add_parameter_group = PyQt4.QtGui.QPushButton(u'More Fields and Locations')
        self.add_parameter_group.setToolTip(u'Creates an additional empty input field group.')
        self.gridLayout_buttons.addWidget(self.add_parameter_group, 1, 0)
        #Lambda and map is used to run several functions for every button click
        self.connect(self.add_parameter_group, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.parameter_groups.append(ParameterGroup(self.connect)),
                                  lambda: self.add_parameter_group_to_gui(self.widgets_layouts, self.parameter_groups[-1])]))

        self.gridLayout_buttons.addWidget(get_line(), 2, 0)

        #Buttons
        self.save_settings_button = PyQt4.QtGui.QPushButton(u'Save settings')
        self.save_settings_button.setToolTip(u'Saves the current input fields settings to midvatten settings.')
        self.gridLayout_buttons.addWidget(self.save_settings_button, 3, 0)
        self.connect(self.save_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                        lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms,
                                                            self.update_stored_settings(self.parameter_groups),
                                                            self.stored_settingskey),
                                  lambda: self.save_stored_settings(self.ms,
                                                                    self.update_stored_settings([self.parameter_browser]),
                                                                    self.stored_settingskey_parameterbrowser)]))

        self.clear_settings_button = PyQt4.QtGui.QPushButton(u'Clear settings')
        self.clear_settings_button.setToolTip(u'Clear input fields and settings.\nReopen Fieldlogger export gui to it reset,\nor press "Save settings" to undo.')
        self.gridLayout_buttons.addWidget(self.clear_settings_button, 4, 0)
        self.connect(self.clear_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms, [], self.stored_settingskey),
                                  lambda: self.save_stored_settings(self.ms, [], self.stored_settingskey_parameterbrowser),
                                  lambda: utils.pop_up_info(u'Settings cleared. Restart Export Fieldlogger dialog\nor press "Save settings" to undo.')]))

        self.settings_strings_button = PyQt4.QtGui.QPushButton(u'Settings strings')
        self.settings_strings_button.setToolTip(u'Access the settings strings to copy and paste all settings between different qgis projects.\n Usage: Select string and copy to a text editor or directly\ninto Settings strings dialog of another qgis project.')
        self.gridLayout_buttons.addWidget(self.settings_strings_button, 5, 0)
        self.connect(self.settings_strings_button, PyQt4.QtCore.SIGNAL("clicked()"), self.settings_strings_dialogs)

        self.gridLayout_buttons.addWidget(get_line(), 6, 0)

        self.export_button = PyQt4.QtGui.QPushButton(u'Export')
        self.export_button.setToolTip(u'Exports the current combination of locations, sublocations and input fields to a Fieldlogger wells file.')
        self.gridLayout_buttons.addWidget(self.export_button, 7, 0)
        # Lambda and map is used to run several functions for every button click
        self.connect(self.export_button, PyQt4.QtCore.SIGNAL("clicked()"), self.export)

        self.gridLayout_buttons.setRowStretch(8, 1)

        self.show()

    @staticmethod
    def init_splitters_layouts(splitter):
        widgets_layouts = []
        for nr in xrange(2):
            widget = PyQt4.QtGui.QWidget()
            layout = PyQt4.QtGui.QHBoxLayout()
            widget.setLayout(layout)
            splitter.addWidget(widget)
            widgets_layouts.append((widget, layout))
        return widgets_layouts

    def add_parameter_group_to_gui(self, widgets_layouts, parameter_group):

            self.create_widget_and_connect_widgets(widgets_layouts[0][1],
                                                   [PyQt4.QtGui.QLabel(u'Sub-location suffix'),
                                                    parameter_group._sublocation_suffix,
                                                    PyQt4.QtGui.QLabel(u'Input fields'),
                                                    parameter_group._parameter_list])

            self.create_widget_and_connect_widgets(widgets_layouts[1][1],
                                                   [PyQt4.QtGui.QLabel(u'Locations'),
                                                    parameter_group.paste_from_selection_button,
                                                    parameter_group._obsid_list,
                                                   PyQt4.QtGui.QLabel(u'Location suffix\n(location name in map)'),
                                                   parameter_group._location_suffix])

    @staticmethod
    def create_widget_and_connect_widgets(parent_layout=None, widgets=None, layout_class=PyQt4.QtGui.QVBoxLayout):
        new_widget = PyQt4.QtGui.QWidget()
        layout = layout_class()
        new_widget.setLayout(layout)
        if parent_layout is not None:
            parent_layout.addWidget(new_widget)
        for widget in widgets:
            layout.addWidget(widget)
        return new_widget

    @staticmethod
    def get_stored_settings(ms, settingskey):
        """
        Reads the settings from settingskey and returns a created dict/list/tuple using ast.literal_eval

        :param ms: midvatten settings
        :param settingskey: the key to get from midvatten settings.
        :return: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
        """
        settings_string_raw = ms.settingsdict.get(settingskey, None)
        if settings_string_raw is None:
            utils.MessagebarAndLog.warning(bar_msg=u'Settings key ' + settingskey + u' did not exist in midvatten settings.')
            return []
        if not settings_string_raw:
            utils.MessagebarAndLog.warning(log_msg=u'Settings key ' + settingskey + u' was empty.')
            return []

        settings_string_raw = utils.returnunicode(settings_string_raw)

        try:
            stored_settings = ast.literal_eval(settings_string_raw)
        except SyntaxError:
            stored_settings = []
            utils.MessagebarAndLog.warning(bar_msg=u'Getting stored settings failed for key ' + settingskey + u' see log message panel.', log_msg=u'Parsing the settingsstring ' + str(settings_string_raw) + u'failed.')
        except ValueError:
            stored_settings = []
            utils.MessagebarAndLog.warning(bar_msg=u'Getting stored settings failed for key ' + settingskey + u' see log message panel.', log_msg=u'Parsing the settingsstring ' + str(settings_string_raw) + u'failed.')
        return stored_settings

    @staticmethod
    def create_parameter_groups_using_stored_settings(stored_settings, connect):
        """
        """
        if not stored_settings or stored_settings is None:
            return []

        parameter_groups = []
        for index, attrs in stored_settings:
            parameter_group = ParameterGroup(connect)
            attrs_set = False
            for attr in attrs:
                if hasattr(parameter_group, attr[0].encode(u'utf-8')):
                    setattr(parameter_group, attr[0].encode(u'utf-8'), attr[1])
                    attrs_set = True
                else:
                    utils.MessagebarAndLog.warning(log_msg=u'Tried to load input field groups but the variable ' + attr[0] + u' did not exist')

            if attrs_set:
                parameter_groups.append(parameter_group)

        return parameter_groups

    @staticmethod
    def update_parameter_browser_using_stored_settings(stored_settings, parameter_browser):
        if not stored_settings or stored_settings is None:
            return
        for index, attrs in stored_settings:
            for attr in attrs:
                if hasattr(parameter_browser, attr[0].encode(u'utf-8')):
                    setattr(parameter_browser, attr[0].encode(u'utf-8'), attr[1])
                else:
                    utils.MessagebarAndLog.warning(log_msg=u'Tried to load input field fields browser but the variable ' + attr[0] + u' did not exist')

    @staticmethod
    def update_stored_settings(objects_with_get_settings):
        return [[index, copy.deepcopy(an_object.get_settings())] for index, an_object in enumerate(objects_with_get_settings) if an_object.get_settings()]

    @staticmethod
    def save_stored_settings(ms, stored_settings, settingskey):
        """
        Saves the current parameter settings into midvatten settings

        :param ms: midvattensettings
        :param stored_settings: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
        :return: stores a string like objname;attr1:value1;attr2:value2/objname2;attr3:value3... in midvatten settings
        """
        settings_string = utils.anything_to_string_representation(stored_settings)
        ms.settingsdict[settingskey] = settings_string
        ms.save_settings()
        utils.MessagebarAndLog.info(log_msg=u'Settings ' + settings_string + u' stored for key ' + settingskey)

    def settings_strings_dialogs(self):

        msg = u'Edit the settings string for input fields browser and restart export fieldlogger dialog\nto load the change.'
        browser_updated = self.ask_and_update_settings([self.parameter_browser], self.stored_settingskey_parameterbrowser, msg)
        msg = u'Edit the settings string for input fields groups and restart export fieldlogger dialog\nto load the change.'
        groups_updated = self.ask_and_update_settings(self.parameter_groups, self.stored_settingskey, msg)
        if browser_updated or groups_updated:
            utils.pop_up_info(u'Settings updated. Restart Export Fieldlogger dialog\nor press "Save settings" to undo.')

    def ask_and_update_settings(self, objects_with_get_settings, settingskey, msg=''):

        old_string = utils.anything_to_string_representation(self.update_stored_settings(objects_with_get_settings))

        new_string = PyQt4.QtGui.QInputDialog.getText(None, "Edit settings string", msg,
                                                           PyQt4.QtGui.QLineEdit.Normal, old_string)
        if not new_string[1]:
            return False

        new_string_text = returnunicode(new_string[0])

        try:
            stored_settings = ast.literal_eval(new_string_text)
        except SyntaxError, e:
            stored_settings = []
            utils.MessagebarAndLog.warning(bar_msg=u'Parsing settings failed, see log message panel', log_msg=u'Parsing settings failed using string\n' + new_string_text + u'\n' + str(e))
            return False

        self.save_stored_settings(self.ms, stored_settings, settingskey)

        return True

    @utils.waiting_cursor
    def export(self):
        self.save_stored_settings(self.ms, self.update_stored_settings(self.parameter_groups), self.stored_settingskey)
        self.write_printlist_to_file(self.create_export_printlist(self.parameter_groups))

    @staticmethod
    def create_export_printlist(parameter_groups):
        """
        Creates a result list with FieldLogger format from selected obsids and parameters
        :return: a list with result lines to export to file
        """
        latlons = utils.get_latlon_for_all_obsids()

        sublocations_locations = {}
        locations_sublocations = OrderedDict()
        locations_lat_lon = OrderedDict()
        sublocations_parameters = OrderedDict()

        parameters_inputtypes_hints = OrderedDict()

        #Check for duplicates in sublocation suffixes
        all_sublocations = [l_s_o[1] for parameter_group in parameter_groups for l_s_o in parameter_group.locations_sublocations_obsids if parameter_group.parameter_list]
        if len(all_sublocations) != len(set(all_sublocations)):
            utils.MessagebarAndLog.critical(bar_msg=u'Critical: Combination of obsid, locationsuffix and sublocation suffix must be unique')
            return

        for index, parameter_group in enumerate(parameter_groups):
            _parameters_inputtypes_hints = parameter_group.parameter_list
            if not _parameters_inputtypes_hints:
                utils.MessagebarAndLog.warning(
                    bar_msg=u"Warning: Empty parameter list for group nr " + str(index + 1))
                continue

            for location, sublocation, obsid in parameter_group.locations_sublocations_obsids:
                lat, lon = [None, None]

                if sublocation in sublocations_locations:
                    if sublocations_locations[sublocation] != location:
                        utils.MessagebarAndLog.warning(bar_msg=u'Warning: Sublocation ' + sublocation + u' error, see log message panel', log_msg=u'Sublocation ' + sublocation + u' already existed for location ' + location + u'.\n Duplications not allowd. It will be skipped.')
                        continue

                if location not in locations_lat_lon:
                    lat, lon = latlons.get(obsid, [None, None])
                    if any([lat is None, not lat, lon is None, not lon]):
                        utils.MessagebarAndLog.critical(bar_msg=u'Critical: Obsid ' + obsid + u' did not have lat-lon coordinates. Check obs_points table')
                        continue

                #sublocations_parameters.setdefault(sublocation, []).extend([par.split(u';')[0] for par in _parameters_inputtypes_hints])

                for _parameter_inputtype_hint in _parameters_inputtypes_hints:
                    _parameter = _parameter_inputtype_hint.split(u';')[0]
                    existed_param = parameters_inputtypes_hints.get(_parameter, None)
                    if existed_param is not None and existed_param != _parameter_inputtype_hint:
                        utils.MessagebarAndLog.critical(bar_msg=u'Critical: Parameter error, see log message panel', log_msg=u'The parameter ' + _parameter_inputtype_hint + u'already existed as ' + existed_param + u'. Skipping it!')
                    else:
                        parameters_inputtypes_hints[_parameter] = _parameter_inputtype_hint

                    existed = sublocations_parameters.get(sublocation, [])
                    if _parameter not in existed:
                        sublocations_parameters.setdefault(sublocation, []).append(_parameter)

                if sublocations_parameters.get(sublocation, []):
                    if location not in locations_lat_lon:
                        locations_lat_lon[location] = (returnunicode(lat), returnunicode(lon))
                    locations_sublocations.setdefault(location, []).append(sublocation)
                    if sublocation not in sublocations_locations:
                        sublocations_locations[sublocation] = location

        printlist = []
        printlist.append(u"FileVersion 1;" + str(len(parameters_inputtypes_hints)))
        printlist.append(u"NAME;INPUTTYPE;HINT")
        #Add a space after the parameter rows just to be sure that there will always be a hint (it needs to be.
        printlist.extend([p_i_h + u' ' if not p_i_h.endswith(u' ') else p_i_h for p_i_h in parameters_inputtypes_hints.values()])

        printlist.append(u'NAME;SUBNAME;LAT;LON;INPUTFIELD')

        for location, sublocations in sorted(locations_sublocations.iteritems()):
            lat, lon = locations_lat_lon[location]

            for sublocation in sorted(sublocations):

                parameters = u'|'.join(sublocations_parameters[sublocation])
                printrow = u';'.join([location, sublocation, lat, lon, parameters])
                #This test is really bad and is due to some logical error above.
                if printrow not in printlist:
                    printlist.append(printrow)

        return printlist

    @staticmethod
    def write_printlist_to_file(printlist):
        filename = PyQt4.QtGui.QFileDialog.getSaveFileName(None, 'Choose a file name', '', 'csv (*.csv)')

        if not filename:
            return
        try:
            with open(filename, 'w') as f:
                f.write(u'\n'.join(printlist).encode('utf-8'))
        except IOError, e:
            utils.pop_up_info("Writing of file failed!: " + str(e))
        except UnicodeDecodeError, e:
            utils.pop_up_info("Error writing " + str(printlist))


class ParameterGroup(object):
    def __init__(self, connect):
        """
        This one should contain:

        Two widgets and two layouts (separate classes.

        Widget 1 contains the comboboxes and fields for producing the parameter names.

            part 1: parameter names
                option 1:
                less flexible. Choosing a table and a pre-created list of parameters/units will appear using select distinct parameter, unit from ...
                option 2:
                choosing table, then column, then distinct parameter, then table, column and distinct unit.
                This could create bad combinations of parameters and units. and takes up more space.
                Maybe these could be set using a separate pop-up dialog.

                qlineedit: final_parameter_name. This is the one that really matters. The other fields are only for help
                qcombobox: inputtype?
                qcombobox: color?

            part 2: obsids.
                obsidnames (obsid.suffix)
                sublocation-names (obsid.suffix.groupname)
                This, two qlineedits, obsid-suffix, and sublocation-suffix. (Which can be unequal or equal.

        Widget 2 contains all the obsids which will be under the first widget.

        Maybe a vertical splitter can be used to hide parts.

        QCombobox

        """
        #Widget list:

        self._location_suffix = PyQt4.QtGui.QLineEdit()
        self._sublocation_suffix = PyQt4.QtGui.QLineEdit()
        self._parameter_list = CopyPasteDeleteableQListWidget(keep_sorted=False)
        self._obsid_list = CopyPasteDeleteableQListWidget(keep_sorted=True)
        self.paste_from_selection_button = PyQt4.QtGui.QPushButton(u'Paste obs_points selection')
        #------------------------------------------------------------------------
        self._location_suffix.setToolTip(u"""(optional)\n""" +
                                         u"""Fieldlogger NAME = obsid.SUFFIX\n""" +
                                         u"""Useful for separating projects or databases\n""" +
                                         u"""ex: suffix = 1234 --> obsid.1234""")
        self._sublocation_suffix.setToolTip(u"""(optional)\n""" +
                                            u"""Fieldlogger sub-location = obsid.SUFFIX\n""" +
                                            u"""Useful for separating parameters into groups for the user.\n""" +
                                            u"""Parameters sharing the same sub-location will be shown together\n""" +
                                            u"""ex: suffix 1234.quality --> obsid.1234.quality""")
        self._parameter_list.setToolTip(u"""Copy and paste input fields from "Create Input Fields" to this box\n""" +
                                        u"""or from/to other input field boxes.\n""" +
                                        u"""The input fields in Fieldlogger will appear in the same order as in\n""" +
                                        u"""this list.\n""" +
                                        u"""The topmost input field will be the first selected input field when\n""" +
                                        u"""the user enters the input fields in Fieldlogger.""")
        self._obsid_list.setToolTip(u"""Add obsids to this box by selecting obsids from the table "obs_points"\n""" +
                                    u"""using it's attribute table or select from map.\n""" +
                                    u"""Then click the button "Paste obs_points selection"\n""" +
                                    u"""Copy and paste obsids between Locations boxes""")
        #-------------------------------------------------------------------------------------
        connect(self.paste_from_selection_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self._obsid_list.paste_data(utils.get_selected_features_as_tuple('obs_points')))

    def get_settings(self):
        settings = ((u'parameter_list', self.parameter_list),
                   (u'location_suffix', self.location_suffix),
                   (u'sublocation_suffix', self.sublocation_suffix))

        settings = tuple((k, v) for k, v in settings if v)
        return utils.returnunicode(settings, keep_containers=True)

    @property
    def location_suffix(self):
        return utils.returnunicode(self._location_suffix.text())

    @location_suffix.setter
    def location_suffix(self, value):
        self._location_suffix.setText(utils.returnunicode(value))

    @property
    def sublocation_suffix(self):
        return utils.returnunicode(self._sublocation_suffix.text())

    @sublocation_suffix.setter
    def sublocation_suffix(self, value):
        self._sublocation_suffix.setText(utils.returnunicode(value))

    @property
    def locations_sublocations_obsids(self):
        """

        :return: a list like [[obsid.locationsuffix as location, obsid.locationsuffix.sublocationsuffix as sublocation, obsid), ...]
        """
        locations_sublocations_obsids = [(u'.'.join([x for x in [returnunicode(obsid), returnunicode(self.location_suffix)] if x]),
                                      u'.'.join([x for x in [returnunicode(obsid), returnunicode(self.location_suffix), returnunicode(self.sublocation_suffix)] if x]), returnunicode(obsid))
                                     for obsid in self._obsid_list.get_all_data()]
        return locations_sublocations_obsids

    @property
    def parameter_list(self):
        return utils.returnunicode(self._parameter_list.get_all_data(), keep_containers=True)

    @parameter_list.setter
    def parameter_list(self, value):
        value = returnunicode(value, keep_containers=True)
        if isinstance(value, (list, tuple)):
            self._parameter_list.paste_data(paste_list=value)
        else:
            self._parameter_list.paste_data(paste_list=value.split(u'\n'))


class ParameterBrowser(PyQt4.QtGui.QDialog, parameter_browser_dialog):
    def __init__(self, tables_columns_org, connect, parent=None):
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        #Widgets:
        # ------------------------------------------------------------------------------------
        #Other widgets in the ui-file
        self._input_field_list = CopyPasteDeleteableQListWidget(keep_sorted=True)
        # ------------------------------------------------------------------------------------

        tables_columns = {}
        for table, columns_tuple in tables_columns_org.iteritems():
            for column in columns_tuple:
                tables_columns.setdefault(table, []).append(column[1])

        # ------------------------------------------------------------------------------------
        self._parameter_table.addItem(u'')
        self._parameter_table.addItems(sorted(tables_columns.keys()))
        connect(self._parameter_table, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._parameter_columns, tables_columns.get(self.parameter_table, [])))
        connect(self._parameter_columns, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._distinct_parameter, self.get_distinct_values(self.parameter_table, self.parameter_columns)))
        self._unit_table.addItem(u'')
        self._unit_table.addItems(sorted(tables_columns.keys()))
        connect(self._unit_table, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._unit_columns, tables_columns.get(self.unit_table, [])))
        connect(self._unit_columns, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._distinct_unit, self.get_distinct_values(self.unit_table, self.unit_columns)))

        connect(self._distinct_parameter, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._combined_name.setText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        connect(self._distinct_unit, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._combined_name.setText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))

        connect(self._add_button, PyQt4.QtCore.SIGNAL("clicked()"),
                lambda : self.combine_name(self.combined_name, self.input_type, self.hint))

        # ------------------------------------------------------------------------------------
        self._input_type.addItem(u'')
        self._input_type.addItems([u'numberDecimal|numberSigned', u'numberDecimal', u'numberSigned', u'text'])
        self._input_type.setToolTip(u'(mandatory)\n' +
                                    u'Decides the keyboard layout in the Fieldlogger app.\n' +
                                    u'numberDecimal: Decimal number\n' +
                                    u'numberSigned: Integers\n' +
                                    u'numberDecimal|numberSigned: Both integers and decimal numbers\n' +
                                    u'text: Text')
        self._hint.setToolTip(u'(optional)\nHint given to the Fieldlogger user for the parameter. Ex: "depth to water"')
        #------------------------------------------------------------------------------------
        self._input_field_list.setToolTip(u'Copy input fields to the "Input Fields" boxes using ctrl+v, ctrl+c.')
        self._input_field_list.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Expanding)
        self._input_field_list.setMinimumWidth(200)
        #------------------------------------------------------------------------------------
        self.horizontalLayout.addWidget(self._input_field_list)

        #self.horizontalLayoutWidget.setTabOrder(self._add_button, self._input_field_list)
        #self.horizontalLayoutWidget.setTabOrder(self._input_field_list, self._parameter_table)

    @staticmethod
    def get_distinct_values(tablename, columnname):
        if not tablename or not columnname:
            return []
        sql = '''SELECT distinct "%s" from "%s"'''%(columnname, tablename)
        connection_ok, result = utils.sql_load_fr_db(sql)

        if not connection_ok:
            textstring = u"""Cannot get data from sql """ + utils.returnunicode(sql)
            utils.MessagebarAndLog.critical(
                bar_msg=u"Error, sql failed, see log message panel",
                log_msg=textstring)
            return []

        values = [col[0] for col in result]
        return values

    @staticmethod
    def replace_items(combobox, items):
        combobox.clear()
        combobox.addItem(u'')
        combobox.addItems(items)

    def get_settings(self):
        if not self.input_field_list:
            return None
        settings = ((u'input_field_list', self.input_field_list),)
        return utils.returnunicode(settings, keep_containers=True)

    def combine_name(self, combined_name, input_type, hint):

        unique_names = [input_field.split(u';')[0] for input_field in self.input_field_list]

        if not combined_name:
            utils.MessagebarAndLog.critical(bar_msg=u'Error, input name not set')
            return
        elif not input_type:
            utils.MessagebarAndLog.critical(bar_msg=u'Error, input type not set')
            return
        elif combined_name in unique_names:
            utils.MessagebarAndLog.critical(bar_msg=u'Error, input name already existing. No duplicates allowed')
            return

        if not hint:
            utils.MessagebarAndLog.warning(bar_msg=u'Warning, hint not given and will be set to a space (" ") as it must exist')
            hint = hint + u' '

        self._input_field_list.paste_data([u';'.join([combined_name, input_type, hint])])

    @property
    def parameter_table(self):
        return utils.returnunicode(self._parameter_table.currentText())

    @parameter_table.setter
    def parameter_table(self, value):
        set_combobox(self._parameter_table, value)

    @property
    def parameter_columns(self):
        return utils.returnunicode(self._parameter_columns.currentText())

    @parameter_columns.setter
    def parameter_columns(self, value):
        set_combobox(self._parameter_columns, value)

    @property
    def distinct_parameter(self):
        return utils.returnunicode(self._distinct_parameter.currentText())

    @distinct_parameter.setter
    def distinct_parameter(self, value):
        set_combobox(self._distinct_parameter, value)

    @property
    def unit_table(self):
        return utils.returnunicode(self._unit_table.currentText())

    @unit_table.setter
    def unit_table(self, value):
        set_combobox(self._unit_table, value)

    @property
    def unit_columns(self):
        return utils.returnunicode(self._unit_columns.currentText())

    @unit_columns.setter
    def unit_columns(self, value):
        set_combobox(self._unit_columns, value)

    @property
    def distinct_unit(self):
        return utils.returnunicode(self._distinct_unit.currentText())

    @distinct_unit.setter
    def distinct_unit(self, value):
        set_combobox(self._distinct_unit, value)

    @property
    def combined_name(self):
        return utils.returnunicode(self._combined_name.text())

    @combined_name.setter
    def combined_name(self, value):
        self._combined_name.setText(utils.returnunicode(value))

    @property
    def input_type(self):
        return utils.returnunicode(self._input_type.currentText())

    @input_type.setter
    def input_type(self, value):
        set_combobox(self._input_type, value)

    @property
    def hint(self):
        return utils.returnunicode(self._hint.text())

    @hint.setter
    def hint(self, value):
        self._hint.setText(utils.returnunicode(value))

    @property
    def input_field_list(self):
        return utils.returnunicode(self._input_field_list.get_all_data(), keep_containers=True)

    @input_field_list.setter
    def input_field_list(self, value):
        value = returnunicode(value, keep_containers=True)
        if isinstance(value, (list, tuple)):
            self._input_field_list.paste_data(paste_list=value)
        else:
            self._input_field_list.paste_data(paste_list=value.split(u'\n'))


class CopyPasteDeleteableQListWidget(PyQt4.QtGui.QListWidget):
    """

    """
    def __init__(self, keep_sorted=False, *args, **kwargs):
        super(CopyPasteDeleteableQListWidget, self).__init__(*args, **kwargs)
        self.setSelectionMode(PyQt4.QtGui.QAbstractItemView.ExtendedSelection)
        self.keep_sorted = keep_sorted

    def keyPressEvent(self, e):
        """
        Method using many parts from http://stackoverflow.com/a/23919177
        :param e:
        :return:
        """

        if e.type() == PyQt4.QtCore.QEvent.KeyPress:
            key = e.key()
            modifiers = e.modifiers()

            if modifiers & PyQt4.QtCore.Qt.ShiftModifier:
                key += PyQt4.QtCore.Qt.SHIFT
            if modifiers & PyQt4.QtCore.Qt.ControlModifier:
                key += PyQt4.QtCore.Qt.CTRL
            if modifiers & PyQt4.QtCore.Qt.AltModifier:
                key += PyQt4.QtCore.Qt.ALT
            if modifiers & PyQt4.QtCore.Qt.MetaModifier:
                key += PyQt4.QtCore.Qt.META

            new_sequence = PyQt4.QtGui.QKeySequence(key)

            if new_sequence.matches(PyQt4.QtGui.QKeySequence.Copy):
                self.copy_data()
            elif new_sequence.matches(PyQt4.QtGui.QKeySequence.Paste):
                self.paste_data()
            elif new_sequence.matches(PyQt4.QtGui.QKeySequence.Delete):
                self.delete_data()
            elif new_sequence.matches(PyQt4.QtGui.QKeySequence.Cut):
                self.cut_data()

    def copy_data(self):
        self.selectedItems()
        stringlist = [item.text() for item in self.selectedItems()]
        PyQt4.QtGui.QApplication.clipboard().setText(u'\n'.join(stringlist))

    def cut_data(self):
        all_items = [self.item(i).text() for i in xrange(self.count())]
        items_to_delete = [item.text() for item in self.selectedItems()]
        PyQt4.QtGui.QApplication.clipboard().setText(u'\n'.join(items_to_delete))
        keep_items = [item for item in all_items if item not in items_to_delete]
        self.clear()
        self.addItems(sorted(keep_items))

    def paste_data(self, paste_list=None):
        if paste_list is None:
            paste_list = PyQt4.QtGui.QApplication.clipboard().text().split(u'\n')

        #Use lists to keep the data ordering (the reason set() is not used
        old_text = self.get_all_data()
        new_items = []
        for alist in [old_text, paste_list]:
            for x in alist:
                if x not in new_items:
                    new_items.append(returnunicode(x))

        self.clear()
        if self.keep_sorted:
            self.addItems(list(sorted(new_items)))
        else:
            self.addItems(list(new_items))

    def delete_data(self):
        all_items = [self.item(i).text() for i in xrange(self.count())]
        items_to_delete = [item.text() for item in self.selectedItems()]
        keep_items = [item for item in all_items if item not in items_to_delete]
        self.clear()
        self.addItems(sorted(keep_items))

    def get_all_data(self):
        return returnunicode([self.item(i).text() for i in xrange(self.count())], keep_containers=True)


class MessageBar(qgis.gui.QgsMessageBar):
    """
    From http://gis.stackexchange.com/a/152733
    """
    def __init__(self, parent=None):
        super(MessageBar, self).__init__(parent)
        self.parent().installEventFilter(self)

    def showEvent(self, event):
        self.resize(PyQt4.QtCore.QSize(self.parent().geometry().size().width(), self.height()))
        self.move(0, self.parent().geometry().size().height() - self.height())
        self.raise_()

    def eventFilter(self, object, event):
        if event.type() == PyQt4.QtCore.QEvent.Resize:
            self.showEvent(None)
        return super(MessageBar, self).eventFilter(object, event)

    def popWidget(self, QgsMessageBarItem=None):
        self.setParent(0)
        self.hide()


def set_combobox(combobox, value):
    index = combobox.findText(returnunicode(value))
    if index != -1:
        combobox.setCurrentIndex(index)
    else:
        combobox.addItem(returnunicode(value))
        index = combobox.findText(returnunicode(value))
        combobox.setCurrentIndex(index)

def add_line(layout):
    """ just adds a line"""
    layout.addWidget(get_line())

def get_line():
    line = PyQt4.QtGui.QFrame()
    line.setGeometry(PyQt4.QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(PyQt4.QtGui.QFrame.HLine)
    line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken)
    return line



