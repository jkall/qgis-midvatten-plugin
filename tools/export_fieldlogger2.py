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
        self.stored_settingskey = u'fieldlogger_export'
        self.stored_settingskey_parameterbrowser = u'fieldlogger_export_parameter_browser'

        self.parameter_groups = self.create_parameter_groups_using_stored_settings(self.get_stored_settings(self.ms, self.stored_settingskey),
                                                                                   self.connect)
        if self.parameter_groups is None or not self.parameter_groups:
            self.parameter_groups = [ParameterGroup(self.connect)]

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

        #ParameterUnitBrowser
        self.parameter_browser = ParameterBrowser(tables_columns, self.connect, self.widget)
        self.parameter_browser_button = PyQt4.QtGui.QPushButton(u'Parameter browser')
        self.gridLayout_buttons.addWidget(self.parameter_browser_button, 0, 0)
        self.connect(self.parameter_browser_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda : self.parameter_browser.show())
        self.update_parameter_browser_using_stored_settings(self.get_stored_settings(self.ms, self.stored_settingskey_parameterbrowser), self.parameter_browser)

        #Buttons
        self.save_settings_button = PyQt4.QtGui.QPushButton(u'Save settings')
        self.save_settings_button.setToolTip(u'Saves the current parameter setup to midvatten settings.')
        self.gridLayout_buttons.addWidget(self.save_settings_button, 1, 0)
        self.connect(self.save_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                        lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms,
                                                            self.update_stored_settings(self.parameter_groups),
                                                            self.stored_settingskey),
                                  lambda: self.save_stored_settings(self.ms,
                                                                    self.update_stored_settings([self.parameter_browser]),
                                                                    self.stored_settingskey_parameterbrowser)]))

        self.add_parameter_group = PyQt4.QtGui.QPushButton(u'New parameter group')
        self.add_parameter_group.setToolTip(u'Creates an additional empty parameter group.')
        self.gridLayout_buttons.addWidget(self.add_parameter_group, 2, 0)
        #Lambda and map is used to run several functions for every button click
        self.connect(self.add_parameter_group, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.parameter_groups.append(ParameterGroup(self.connect)),
                                  lambda: self.add_parameter_group_to_gui(self.widgets_layouts, self.parameter_groups[-1])]))

        self.export_button = PyQt4.QtGui.QPushButton(u'Export')

        self.export_button.setToolTip(u'Exports to a Fieldlogger wells file.')
        self.gridLayout_buttons.addWidget(self.export_button, 3, 0)
        # Lambda and map is used to run several functions for every button click
        self.connect(self.export_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms,
                                                                    self.update_stored_settings(self.parameter_groups),
                                                                    self.stored_settingskey),
                                  lambda: self.write_printlist_to_file(self.create_export_printlist(self.parameter_groups))]))

        self.clear_settings_button = PyQt4.QtGui.QPushButton(u'Clear settings')
        self.gridLayout_buttons.addWidget(self.clear_settings_button, 4, 0)
        self.connect(self.clear_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms, None, self.stored_settingskey),
                                  lambda: self.save_stored_settings(self.ms, None, self.stored_settingskey_parameterbrowser),
                                  lambda: utils.pop_up_info(u'Settings cleard. Restart Export Fieldlogger dialog')]))

        self.gridLayout_buttons.setRowStretch(5, 1)

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
                                                   [PyQt4.QtGui.QLabel(u'Fieldlogger parameters and locations:'),
                                                    PyQt4.QtGui.QLabel(u'Parameters'),
                                                    parameter_group._parameter_list,
                                                    get_line(),
                                                    PyQt4.QtGui.QLabel(u'Location suffix'),
                                                    parameter_group._location_suffix,
                                                    PyQt4.QtGui.QLabel(u'Sub-location suffix'),
                                                    parameter_group._sublocation_suffix,
                                                    get_line()])


            self.create_widget_and_connect_widgets(widgets_layouts[1][1],
                                                   [parameter_group.paste_from_selection_button,
                                                    parameter_group._obsid_list])

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
        Reads the settings from settingskey and returns a tuple

        The settings string is assumed to look like this:
        objname;attr1:value1;attr2:value2/objname2;attr3:value3...

        :param ms: midvatten settings
        :param settingskey: the key to get from midvatten settings.
        :return: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
        """

        settings_string_raw = ms.settingsdict.get(settingskey, None)
        if settings_string_raw is None:
            return []

        try:
            stored_settings = ast.literal_eval(settings_string_raw)
        except SyntaxError:
            stored_settings = []

        return returnunicode(stored_settings, keep_containers=True)

    @staticmethod
    def create_parameter_groups_using_stored_settings(stored_settings, connect):
        """
        """
        export_objects = []
        for index, attrs in stored_settings:
            export_object = ParameterGroup(connect)
            attrs_set = False
            for attr in attrs:
                if hasattr(export_object, attr[0]):
                    setattr(export_object, attr[0], attr[1])
                    attrs_set = True

            if attrs_set:
                export_objects.append(export_object)

        return export_objects

    @staticmethod
    def update_parameter_browser_using_stored_settings(stored_settings, parameter_browser):
        for index, attrs in stored_settings:
            for attr in attrs:
                if hasattr(parameter_browser, attr[0]):
                    setattr(parameter_browser, attr[0], attr[1])

    @staticmethod
    def update_stored_settings(an_object_with_get_settings):
        return [(index, copy.deepcopy(export_object.get_settings())) for index, export_object in enumerate(an_object_with_get_settings)]

    @staticmethod
    def save_stored_settings(ms, stored_settings, settingskey):
        """
        Saves the current parameter settings into midvatten settings

        :param ms: midvattensettings
        :param stored_settings: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
        :return: stores a string like objname;attr1:value1;attr2:value2/objname2;attr3:value3... in midvatten settings
        """
        ms.settingsdict[settingskey] = utils.anything_to_string_representation(stored_settings)
        ms.save_settings()

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
            _parameters_inputtypes_hints = parameter_group.parameter_list
            if not _parameters_inputtypes_hints:
                utils.MessagebarAndLog.warning(
                    bar_msg=u"Warning: Empty parameter list for group nr " + str(index + 1))
                continue

            for location, sublocation, obsid in parameter_group.locations_sublocations_obsids:

                if sublocation in sublocations_locations:
                    if sublocations_locations[sublocation] != location:
                        utils.MessagebarAndLog.warning(bar_msg=u'Warning: Sublocation ' + sublocation + u' error, see log message panel', log_msg=u'Sublocation ' + sublocation + u' already existed for location ' + location_exists + u' and is duplicated by location ' + location + u'. It will be skipped.')
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
                    if existed_param is not None:
                        utils.MessagebarAndLog.critical(bar_msg=u'Critical: Parameter error, see log message panel', log_msg=u'The parameter ' + _parameter_inputtype_hint + u'already existed as ' + existed_param + u'. Skipping it!')
                    else:
                        parameters_inputtypes_hints[_parameter] = _parameter_inputtype_hint

                    existed = sublocations_parameters.get(sublocation, [])
                    if _parameter not in existed:
                        sublocations_parameters.setdefault(sublocation, []).append(_parameter)

                if sublocations_parameters.get(sublocation, []):
                    locations_lat_lon[location] = (returnunicode(lat), returnunicode(lon))
                    locations_sublocations.setdefault(location, []).append(sublocation)
                    if sublocation not in sublocations_locations:
                        sublocations_locations[sublocation] = location


        printlist = []
        printlist.append(u"FileVersion 1;" + str(len(parameters_inputtypes_hints)))
        printlist.append(u"NAME;INPUTTYPE;HINT")
        printlist.extend(parameters_inputtypes_hints.values())

        printlist.append(u'NAME;SUBNAME;LAT;LON;INPUTFIELD')

        for location, sublocations in sorted(locations_sublocations.iteritems()):
            lat, lon = locations_lat_lon[location]

            sublocation_with_only_one_comment = False

            for sublocation in sorted(sublocations):
                parameters = sublocations_parameters[sublocation]

                comments = [par for par in parameters if u'comment' in par or u'kommentar' in par]
                if len(parameters) == 1 and comments:
                    sublocation_with_only_one_comment = True

                if not comments:
                    utils.MessagebarAndLog.warning(bar_msg=u'Import warning, see log message panel',
                                                   log_msg=u'Sublocation ' + sublocation + u' may be missing a parameter group comment-parameter. Make sure you add one')

                parameters = u'|'.join(sublocations_parameters[sublocation])
                printrow = u';'.join([location, sublocation, lat, lon, parameters])
                #This test is really bad and is due to some logical error above.
                if printrow not in printlist:
                    printlist.append(printrow)

            if not sublocation_with_only_one_comment:
                utils.MessagebarAndLog.warning(bar_msg=u'Import warning, see log message panel',
                                               log_msg=u'Location ' + location + u' may be missing a general comment parameter. Make sure you add one')

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
        self._parameter_list = CopyPasteDeleteableQListWidget()
        self._obsid_list = CopyPasteDeleteableQListWidget()
        self.paste_from_selection_button = PyQt4.QtGui.QPushButton(u'Paste obs_points selection')
        #------------------------------------------------------------------------
        self._location_suffix.setToolTip(u'(optional)\nFieldlogger NAME = obsid.SUFFIX\nUseful for separating projects or databases\nex: suffix = 1234 --> obsid.1234')
        self._sublocation_suffix.setToolTip(u'(optional)\nFieldlogger sub-location = obsid.SUFFIX\nUseful for separating parameters into groups for the user.\nParameters sharing the same sub-location will be shown together\n ex: suffix 1234.quality --> obsid.1234.quality')
        #-------------------------------------------------------------------------------------
        connect(self.paste_from_selection_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self._obsid_list.paste_data(utils.get_selected_features_as_tuple('obs_points')))
        connect(self._location_suffix, PyQt4.QtCore.SIGNAL("textChanged(const QString&)"),
                         lambda : self.set_sublocation_suffix(self.location_suffix))

    def get_settings(self):
        settings = ((u'parameter_list', self.parameter_list),
                   (u'location_suffix', self.location_suffix),
                   (u'sublocation_suffix', self.sublocation_suffix))

        settings = tuple((k, v) for k, v in settings if v)
        return utils.returnunicode(settings, keep_containers=True)

    def set_sublocation_suffix(self, location_suffix):
        current_suffix = self.sublocation_suffix
        try:
            current_suffix = self.sublocation_suffix.split(u'.')[1]
        except IndexError:
            pass
        if not current_suffix:
            self.sublocation_suffix = location_suffix
        else:
            self.sublocation_suffix = u'.'.join([location_suffix, current_suffix])

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
        locations_sublocations_obsids = [(u'.'.join([x for x in [returnunicode(obsid), returnunicode(self.location_suffix)] if x]),
                                      u'.'.join([x for x in [returnunicode(obsid), returnunicode(self.sublocation_suffix)] if x]), returnunicode(obsid))
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
        self._parameter_list = CopyPasteDeleteableQListWidget()
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

        connect(self.add_parameter_button, PyQt4.QtCore.SIGNAL("clicked()"),
                lambda : self.combine_name(self.combined_name, self.input_type, self.hint))

        # ------------------------------------------------------------------------------------
        self._input_type.addItem(u'')
        self._input_type.addItems([u'numberDecimal|numberSigned', u'numberDecimal', u'numberSigned', u'text'])
        self._input_type.setToolTip(u'(mandatory)\nDecides the keyboard layout in the Fieldlogger app.')
        self._hint.setToolTip(u'(optional)\nHint given to the Fieldlogger user for the parameter. Ex: "depth to water"')
        #------------------------------------------------------------------------------------
        self._combined_name.setToolTip(u'Copy value using ctrl+v, ctrl+c to parameter name.')
        self._parameter_list.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Expanding)
        self._parameter_list.setMinimumWidth(200)
        #------------------------------------------------------------------------------------
        self.horizontalLayout.addWidget(self._parameter_list)

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
        settings = ((u'parameter_list', self.parameter_list),)
        return utils.returnunicode(settings, keep_containers=True)

    def combine_name(self, combined_name, input_type, hint):
        if not combined_name:
            utils.MessagebarAndLog.critical(bar_msg=u'Error, Fieldlogger parameter name not set')
            return
        elif not input_type:
            utils.MessagebarAndLog.critical(bar_msg=u'Error, Fieldlogger input type not set')
            return
        else:
            self._parameter_list.paste_data([u';'.join([self.combined_name, self.input_type, self.hint])])

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
    def parameter_list(self):
        return utils.returnunicode(self._parameter_list.get_all_data(), keep_containers=True)

    @parameter_list.setter
    def parameter_list(self, value):
        value = returnunicode(value, keep_containers=True)
        if isinstance(value, (list, tuple)):
            self._parameter_list.paste_data(paste_list=value)
        else:
            self._parameter_list.paste_data(paste_list=value.split(u'\n'))


class CopyPasteDeleteableQListWidget(PyQt4.QtGui.QListWidget):
    """

    """
    def __init__(self, *args, **kwargs):
        super(CopyPasteDeleteableQListWidget, self).__init__(*args, **kwargs)
        self.setSelectionMode(PyQt4.QtGui.QAbstractItemView.ExtendedSelection)

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
        old_text = [returnunicode(self.item(i).text()) for i in xrange(self.count())]
        new_items = set()
        new_items.update([returnunicode(x) for x in paste_list])
        new_items.update(old_text)
        self.clear()
        self.addItems(list(sorted(new_items)))

    def delete_data(self):
        all_items = [self.item(i).text() for i in xrange(self.count())]
        items_to_delete = [item.text() for item in self.selectedItems()]
        keep_items = [item for item in all_items if item not in items_to_delete]
        self.clear()
        self.addItems(sorted(keep_items))

    def get_all_data(self):
        return [self.item(i).text() for i in xrange(self.count())]


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



