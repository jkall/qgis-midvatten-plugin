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
import PyQt4
import ast
import copy
import os.path
import qgis.gui
from collections import OrderedDict

import db_utils
import definitions.midvatten_defs as defs
import midvatten_utils as utils
from gui_utils import SplitterWithHandel, ExtendedQPlainTextEdit, get_line, set_combobox
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
        self.setWindowTitle("Export to Fieldlogger dialog") # Set the title for the dialog

        self.widget.setMinimumWidth(180)

        tables_columns = db_utils.tables_columns()

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
        self.splitter = SplitterWithHandel(PyQt4.QtCore.Qt.Vertical)
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
        self.save_settings_button.setToolTip(u'Saves the current input fields settings.')
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
        self.clear_settings_button.setToolTip(u'Clear all input fields settings.')
        self.gridLayout_buttons.addWidget(self.clear_settings_button, 4, 0)
        self.connect(self.clear_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms, [], self.stored_settingskey),
                                  lambda: utils.pop_up_info(u'Settings cleared. Restart Export to Fieldlogger dialog to complete,\nor press "Save settings" to save current input fields settings again.')]))

        self.settings_strings_button = PyQt4.QtGui.QPushButton(u'Settings strings')
        self.settings_strings_button.setToolTip(u'Access the settings strings ("Create input fields" and input fields) to copy and paste all settings between different qgis projects.\n Usage: Select string and copy to a text editor or directly into Settings strings dialog of another qgis project.')
        self.gridLayout_buttons.addWidget(self.settings_strings_button, 5, 0)
        self.connect(self.settings_strings_button, PyQt4.QtCore.SIGNAL("clicked()"), self.settings_strings_dialogs)

        self.default_settings_button = PyQt4.QtGui.QPushButton(u'Default settings')
        self.default_settings_button.setToolTip(u'Updates "Create input fields" and input fields to default settings.')
        self.gridLayout_buttons.addWidget(self.default_settings_button, 6, 0)
        self.connect(self.default_settings_button, PyQt4.QtCore.SIGNAL("clicked()"), self.restore_default_settings)

        self.gridLayout_buttons.addWidget(get_line(), 7, 0)

        self.preview_button = PyQt4.QtGui.QPushButton(u'Preview')
        self.preview_button.setToolTip(u'View a preview of the Fieldlogger location file as pop-up info.')
        self.gridLayout_buttons.addWidget(self.preview_button, 8, 0)
        # Lambda and map is used to run several functions for every button click
        self.connect(self.preview_button, PyQt4.QtCore.SIGNAL("clicked()"), self.preview)

        self.export_button = PyQt4.QtGui.QPushButton(u'Export')
        self.export_button.setToolTip(u'Exports the current combination of locations and input fields to a Fieldlogger location file.')
        self.gridLayout_buttons.addWidget(self.export_button, 9, 0)
        # Lambda and map is used to run several functions for every button click
        self.connect(self.export_button, PyQt4.QtCore.SIGNAL("clicked()"), self.export)

        self.gridLayout_buttons.setRowStretch(10, 1)

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
                                                    parameter_group._input_field_group_list])

            self.create_widget_and_connect_widgets(widgets_layouts[1][1],
                                                   [PyQt4.QtGui.QLabel(u'Locations'),
                                                    parameter_group.paste_from_selection_button,
                                                    parameter_group._obsid_list,
                                                   PyQt4.QtGui.QLabel(u'Location suffix\n(ex. project number)'),
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
            utils.MessagebarAndLog.info(bar_msg=u'Settings key ' + settingskey + u' did not exist in midvatten settings.')
            return []
        if not settings_string_raw:
            utils.MessagebarAndLog.info(log_msg=u'Settings key ' + settingskey + u' was empty.')
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

    def restore_default_settings(self):
        input_field_browser, input_fields_groups = defs.export_fieldlogger_defaults()
        self.update_settings(input_field_browser, self.stored_settingskey_parameterbrowser)
        self.update_settings(input_fields_groups, self.stored_settingskey)
        utils.pop_up_info(u'Input fields and "Create Input Fields" updated to default.\nRestart Export to Fieldlogger dialog to complete,\nor press "Save settings" to save current input fields settings again.')

    def settings_strings_dialogs(self):

        msg = u'Edit the settings string for input fields browser and restart export fieldlogger dialog\nto load the change.'
        browser_updated = self.ask_and_update_settings([self.parameter_browser], self.stored_settingskey_parameterbrowser, msg)
        msg = u'Edit the settings string for input fields groups and restart export fieldlogger dialog\nto load the change.'
        groups_updated = self.ask_and_update_settings(self.parameter_groups, self.stored_settingskey, msg)
        if browser_updated or groups_updated:
            utils.pop_up_info(u'Settings updated. Restart Export to Fieldlogger dialog\nor press "Save settings" to undo.')

    def ask_and_update_settings(self, objects_with_get_settings, settingskey, msg=''):

        old_string = utils.anything_to_string_representation(self.update_stored_settings(objects_with_get_settings))

        new_string = PyQt4.QtGui.QInputDialog.getText(None, "Edit settings string", msg,
                                                           PyQt4.QtGui.QLineEdit.Normal, old_string)
        if not new_string[1]:
            return False

        new_string_text = returnunicode(new_string[0])

        self.update_settings(new_string_text, settingskey)

    def update_settings(self, new_string_text, settingskey):
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

    def preview(self):
        export_printlist = self.create_export_printlist(self.parameter_groups)
        PyQt4.QtGui.QMessageBox.information(None, u'Preview', u'\n'.join(export_printlist))

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

        for index, parameter_group in enumerate(parameter_groups):
            _parameters_inputtypes_hints = parameter_group.input_field_group_list
            if not _parameters_inputtypes_hints:
                utils.MessagebarAndLog.warning(
                    bar_msg=u"Warning: Empty input fields list for group nr " + str(index + 1))
                continue

            for location, sublocation, obsid in parameter_group.locations_sublocations_obsids:
                lat, lon = [None, None]

                if location not in locations_lat_lon:
                    lat, lon = latlons.get(obsid, [None, None])
                    if any([lat is None, not lat, lon is None, not lon]):
                        utils.MessagebarAndLog.critical(bar_msg=u'Critical: Obsid ' + obsid + u' did not have lat-lon coordinates. Check obs_points table')
                        continue

                #If a parameter appears again, delete it and add it again to make it appear last.
                for _parameter_inputtype_hint in _parameters_inputtypes_hints:
                    _parameter = _parameter_inputtype_hint.split(u';')[0]

                    existed_p_i_h = parameters_inputtypes_hints.get(_parameter, None)
                    if existed_p_i_h is not None:
                        if existed_p_i_h != _parameter_inputtype_hint:
                            utils.MessagebarAndLog.warning(bar_msg=u'Warning, parameter error, see log message panel', log_msg=u'The parameter %s exists more than once and the last one will overwrite the previous.'%_parameter)
                        del parameters_inputtypes_hints[_parameter]
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
        filename = PyQt4.QtGui.QFileDialog.getSaveFileName(parent=None, caption='Choose a file name', directory='', filter='csv (*.csv)')
        if not filename:
            return
        if os.path.splitext(filename)[1] != u'.csv':
            filename += u'.csv'
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
        """
        #Widget list:

        self._location_suffix = PyQt4.QtGui.QLineEdit()
        self._sublocation_suffix = PyQt4.QtGui.QLineEdit()
        self._input_field_group_list = ExtendedQPlainTextEdit(keep_sorted=False)
        self._obsid_list = ExtendedQPlainTextEdit(keep_sorted=True)
        self.paste_from_selection_button = PyQt4.QtGui.QPushButton(u'Paste obs_points selection')
        #------------------------------------------------------------------------
        self._location_suffix.setToolTip(u"""(optional)\n""" +
                                         u"""The Fieldlogger location in the Fieldlogger map will be "obsid.LOCATION SUFFIX".\n\n""" +
                                         u"""Location suffix is useful for separating locations with identical obsids.\n""" +
                                         u"""ex: Location suffix 1234 --> obsid.1234""")
        self._sublocation_suffix.setToolTip(u"""(optional)\n""" +
                                            u"""Fieldlogger sub-location will be obsid.Location suffix.Sub-location suffix\n\n""" +
                                            u"""Parameters sharing the same sub-location will be shown together.\n""" +
                                            u"""Sub-location suffix is used to separate input fields into groups for the Fieldlogger user.\n""" +
                                            u"""ex: level, quality, sample, comment, flow.""")
        self._input_field_group_list.setToolTip(u"""Copy and paste input fields from "Create Input Fields" to this box\n""" +
                                        u"""or from/to other input field boxes.\n""" +
                                        u"""The input fields in Fieldlogger will appear in the same order as in\n""" +
                                        u"""this list.\n""" +
                                        u"""The topmost input field will be the first selected input field when\n""" +
                                        u"""the user enters the input fields in Fieldlogger. (!!! If the input\n""" +
                                        u"""field already exists in a previous group it will end up on top!!!)""")
        locations_box_tooltip = (u"""Add obsids to Locations box by selecting obsids from the table "obs_points"\n""" +
                                u"""using it's attribute table or select from map.\n""" +
                                u"""Then click the button "Paste obs_points selection"\n""" +
                                u"""Copy and paste obsids between Locations boxes.""")


        self._obsid_list.setToolTip(locations_box_tooltip)
        self.paste_from_selection_button.setToolTip(locations_box_tooltip)

        #-------------------------------------------------------------------------------------
        connect(self.paste_from_selection_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self._obsid_list.paste_data(utils.get_selected_features_as_tuple('obs_points')))

    def get_settings(self):
        settings = ((u'input_field_group_list', self.input_field_group_list),
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
                                     for obsid in set(self._obsid_list.get_all_data())]
        return locations_sublocations_obsids

    @property
    def input_field_group_list(self):
        return utils.returnunicode(self._input_field_group_list.get_all_data(), keep_containers=True)

    @input_field_group_list.setter
    def input_field_group_list(self, value):
        value = returnunicode(value, keep_containers=True)
        if isinstance(value, (list, tuple)):
            self._input_field_group_list.paste_data(paste_list=value)
        else:
            self._input_field_group_list.paste_data(paste_list=value.split(u'\n'))


class ParameterBrowser(PyQt4.QtGui.QDialog, parameter_browser_dialog):
    def __init__(self, tables_columns_org, connect, parent=None):
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        #Widgets:
        # ------------------------------------------------------------------------------------
        #Other widgets in the ui-file
        self._input_field_list = ExtendedQPlainTextEdit(keep_sorted=True)
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
        par_unit_tooltip = (u'(optional)\n' +
                            u'When both parameter and unit is given, they will be combined to create the input field name.')
        self._distinct_parameter.setToolTip(par_unit_tooltip)
        self._distinct_unit.setToolTip(par_unit_tooltip)
        self._combined_name.setToolTip(u'(mandatory)\n' +
                                       u'Either supply a chosen name directly or use parameter\n' +
                                       u'and unit boxes to create a name.\n' +
                                       u'ex: parameter.unit')
        self._input_type.addItem(u'')
        self._input_type.addItems([u'numberDecimal|numberSigned', u'text'])
        self._input_type.setToolTip(u'(mandatory)\n' +
                                    u'Decides the keyboard layout in the Fieldlogger app.\n' +
                                    u'numberDecimal|numberSigned: Decimals with allowed "-" sign\n' +
                                    u'text: Text')
        self._hint.setToolTip(u'(optional)\nHint given to the Fieldlogger user for the parameter. Ex: "depth to water"')
        #------------------------------------------------------------------------------------
        self._input_field_list.setToolTip(u'Copy input fields to the "Input Fields" boxes using ctrl+c, ctrl+v.')
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
        connection_ok, result = db_utils.sql_load_fr_db(sql)

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
        try:
            combobox.addItems(items)
        except TypeError:
            for item in items:
                combobox.addItem(item)

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



