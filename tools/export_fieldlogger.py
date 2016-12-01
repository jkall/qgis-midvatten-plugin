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
import os
import os.path
import qgis.utils
import copy
from collections import OrderedDict

import midvatten_utils as utils
from definitions.midvatten_defs import standard_parameters_for_wquality, standard_parameters_for_wflow, standard_parameters_for_wsample
import definitions.midvatten_defs as defs
from import_data_to_db import midv_data_importer
import import_fieldlogger

export_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]


class _ExportToFieldLogger(PyQt4.QtGui.QMainWindow, export_fieldlogger_ui_dialog):
    """ Class handling export of data for fieldlogger """
    
    def __init__(self, parent, settingsdict1={}, obsids=None):
        self.iface = parent
        self.obsids = obsids

        self.settingsdict = settingsdict1
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle("Export to FieldLogger") # Set the title for the dialog

        self.parameters = self.create_parameters()
        self.unhidden_types_parameters = self.get_unhidden_types_parameters_names(self.parameters)
        self.set_headers(self.gridLayout_selections, self.unhidden_types_parameters, self.gridWidget_selections)
        self.set_and_connect_select_from_map(self.gridLayout_selections, self.unhidden_types_parameters, self.gridWidget_selections)
        self.set_and_connect_selectall(self.gridLayout_selections, self.unhidden_types_parameters, self.gridWidget_selections)
        self.add_line(self.gridLayout_selections, len(self.unhidden_types_parameters), self.gridWidget_selections)
        self.obsids = utils.get_all_obsids()

        self.selection_dict = self.build_selection_dict(self.obsids, self.unhidden_types_parameters, self.gridWidget_selections)
        self.set_obsids_and_parameters_checkboxes(self.gridLayout_selections, self.selection_dict, self.unhidden_types_parameters)

        self.connect(self.pushButtonExport, PyQt4.QtCore.SIGNAL("clicked()"), self.export_selected)
        self.connect(self.pushButtonImportWellsfile, PyQt4.QtCore.SIGNAL("clicked()"), self.select_from_wells)

        self.show()

    def create_parameters(self):
        """ Creaters self.parameters dict with parameters
        :return: a dict like "{'typename': {'parameter': Parameter()}}"
        """
        types = {}

        types_tuples = [(u'level', ((u'meas', (u'm',)),)),
                        (u'flow', standard_parameters_for_wflow()),
                        (u'quality', standard_parameters_for_wquality()),
                        (u'sample', standard_parameters_for_wsample())]

        for parameter_type, parameters_units_tuple in types_tuples:
            types[parameter_type] = OrderedDict()
            types[parameter_type].update(self.create_parameters_from_tuple(parameter_type, parameters_units_tuple))
            types[parameter_type][u'comment'] = Parameter(u'comment', u'make comment...', parameter_type, unit=u'', valuetype=u'text', hidden=True)

            if parameter_type in [u'quality', u'sample']:
                types[parameter_type][u'depth'] = Parameter(u'depth', u'depth of measurement', parameter_type, unit=u'm', hidden=True)

        return types

    def create_parameters_from_tuple(self, parameter_type, parameters_units_tuple):
        parameters = OrderedDict()
        for param, units in parameters_units_tuple:
            for unit in units:
                if len(units) > 1:
                    paramname = u'.'.join((param, unit))
                else:
                    paramname = param
                hint = unit
                parameters[paramname] = Parameter(paramname, hint, parameter_type, unit)
        return parameters

    def get_unhidden_types_parameters_names(self, parameters):
        unhidden_parameternames = tuple([(typename, parametername) for typename, parameter_dict in sorted(parameters.iteritems())
                                   for parametername, parameter in sorted(parameter_dict.iteritems()) if not parameter.hidden])
        return unhidden_parameternames

    def set_headers(self, grid, unhidden_types_parameters, widget_parent):
        """
        Creates Qlabel headers for all parameters
        :param grid: A QGridLayout.
        :param unhidden_types_parameters: A dict with type as key an innerdict with parameters as value
        :return: None
        """
        rownr = grid.rowCount()

        for colnr, type_parameter in enumerate(unhidden_types_parameters):
            label = PyQt4.QtGui.QLabel('.'.join(type_parameter))
            grid.addWidget(label, rownr, colnr + 1)

    def set_and_connect_select_from_map(self, grid, unhidden_types_parameters, widget_parent):
        """
        Creates buttons that selects all parameters for selected obsids in obs_points
        :param grid: A QGridLayout.
        :param unhidden_types_parameters: A dict with type as key an innerdict with parameters as value
        :param widget_parent:
        :return:
        """
        rownr = grid.rowCount()
        grid.addWidget(PyQt4.QtGui.QLabel('Select from map selection'), rownr, 0)
        for colnr, type_parameter in enumerate(unhidden_types_parameters):
            pushbutton = PyQt4.QtGui.QPushButton('Select from map', widget_parent)
            pushbutton.setToolTip('Select ' + '.'.join(type_parameter) + ' for all obsids selected in map')
            pushbutton.setObjectName('.'.join(type_parameter))
            grid.addWidget(pushbutton, rownr, colnr + 1)
            self.connect(pushbutton, PyQt4.QtCore.SIGNAL("clicked()"), self.select_from_map_click)

    def select_from_map_click(self):
        """
        Method representing a select_from_map click.

        self.sender() is used to find the currently clicked checkbox.
        :return: None
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...
        pushbutton = self.sender()
        type_parameter_name = pushbutton.objectName()
        self.select_from_map(type_parameter_name)
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def select_from_map(self, type_parameter_name):
        """
        Selects parameter for all obsids selected in map
        :param type_parameter_name: A parametername like type.parameter
        :return: None
        """
        selected_obsids = utils.get_selected_features_as_tuple('obs_points')
        for obsid in selected_obsids:
            types_dict = self.selection_dict[obsid]
            splitted = type_parameter_name.split('.')
            typename = splitted[0]
            parametername = '.'.join(splitted[1:])
            checkbox = types_dict[typename][parametername]
            checkbox.setChecked(True)

    def set_and_connect_selectall(self, grid, unhidden_types_parameters, widget_parent):
        """
        Creates checkboxes for select all for all parameters
        :param grid: A QGridLayout.
        :param unhidden_types_parameters: A dict with type as key an innerdict with parameters as value
        :return: None
        """
        rownr = grid.rowCount()
        grid.addWidget(PyQt4.QtGui.QLabel('Select all'), rownr, 0)

        for colnr, type_parameter in enumerate(unhidden_types_parameters):
            checkbox = PyQt4.QtGui.QCheckBox(widget_parent)
            checkbox.setToolTip('.'.join(type_parameter))
            checkbox.setObjectName('.'.join(type_parameter))
            grid.addWidget(checkbox, rownr, colnr + 1)
            self.connect(checkbox, PyQt4.QtCore.SIGNAL("clicked()"), self.select_all_click)

    def add_line(self, grid, num_cols, widget_parent):
        rownr = grid.rowCount()
        frame = PyQt4.QtGui.QFrame(widget_parent)
        frame.setFrameShape(PyQt4.QtGui.QFrame.HLine)
        grid.addWidget(frame, rownr, 0, 1, num_cols + 1)

    def build_selection_dict(self, obsids, unhidden_types_parameters, parent_widget):
        """ Creates a dict of obsids and their parameter checkbox objects
        :param obsids: A list of obsids
        :param unhidden_types_parameters: A dict with type as key an innerdict with parameters as value
        :param parent_widget: The parent widget. It might be needed for this to work, but not sure.
        :return: a dict like {'obsid': {'parametername': QCheckBox, ...}, ...}
        """
        selection_dict = {}
        for obsid in obsids:
            type_dict = {}
            for typename, parametername in unhidden_types_parameters:
                checkbox = PyQt4.QtGui.QCheckBox(parent_widget)
                type_dict.setdefault(typename, {})[parametername] = checkbox
            selection_dict[obsid] = type_dict
        return selection_dict

    def set_obsids_and_parameters_checkboxes(self, grid, selection_dict, unhidden_types_parameters):
        """
        Creates a matrix of checkboxes for choosing parameters
        :param grid: A QGridLayout.
        :param selection_dict: a dict like {'obsid': {'parametername': QCheckBox, ...}, ...}
        :return: None
        """
        start_rownr = grid.rowCount()
        for rownr, obs_types_dict_tuple in enumerate(sorted(selection_dict.iteritems())):
            obsid, types_dict = obs_types_dict_tuple
            grid.addWidget(PyQt4.QtGui.QLabel(obsid), rownr + start_rownr, 0)

            for colnr, type_parameter in enumerate(unhidden_types_parameters):
                typename, parametername = type_parameter
                checkbox = types_dict[typename][parametername]
                checkbox.setMinimumSize(20, 20)
                checkbox.setToolTip('.'.join((obsid, typename, parametername)))
                grid.addWidget(checkbox, rownr + start_rownr, colnr + 1)

    def select_all_click(self):
        """
        Method representing a select_all click.

        self.sender() is used to find the currently clicked checkbox.
        :return: None
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...
        checkbox = self.sender()
        type_parameter_name = checkbox.objectName()
        check_state = checkbox.isChecked()
        self.select_all(type_parameter_name, check_state)
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def select_all(self, type_parameter_name, check_state):
        """
        Selects or deselects a parameter for all obsids
        :param type_parameter_name: A parametername like type.parameter
        :param check_state: The state of the currently selected select_all checkbox.
        :return:
        """
        for obsid, types_dict in self.selection_dict.iteritems():
            splitted = type_parameter_name.split(u'.')
            typename = splitted[0]
            parametername = '.'.join(splitted[1:])
            checkbox = types_dict[typename][parametername]
            checkbox.setChecked(check_state)

    def select_from_wells(self):
        """ Select all from imported wells-file
        :return:
        """
        selection_dict = self.selection_dict

        importinstance = midv_data_importer()
        obsid_dict = importinstance.parse_wells_file()
        if obsid_dict == u'cancel':
            qgis.utils.iface.messageBar().pushMessage("Select from wells file: No file was chosen or no rows could be parsed.")
            return u'cancel'

        failed_imports = []
        for obsid, types_dict in obsid_dict.iteritems():
            for typename, parameters in types_dict.iteritems():
                for parameter, unit in parameters:
                    try:
                        types_dict = selection_dict[obsid]
                    except KeyError:
                        failed_imports.append([obsid, typename, parameter, unit])
                        continue
                    try:
                        parameters =  types_dict[typename]
                    except KeyError:
                        failed_imports.append([obsid, typename, parameter, unit])
                        continue
                    try:
                        checkbox = parameters[u'.'.join([parameter, unit])]
                    except KeyError:
                        try:
                            checkbox = parameters[parameter]
                        except KeyError:
                            failed_imports.append([obsid, typename, parameter, unit])
                            continue
                    checkbox.setChecked(True)
        if obsid_dict:
            utils.pop_up_info('Failed to import parameters:\n' + '\n'.join([', '.join(x) for x in failed_imports if x[2] != u'comment']))

    def export_selected(self):
        """ Export the selected obsids and parameters to a file
        """
        self.write_printlist_to_file(self.create_export_printlist())

    def create_export_printlist(self):
        """
        Creates a result list with FieldLogger format from selected obsids and parameters
        :return: a list with result lines to export to file
        """
        selection_dict = self.selection_dict
        types_parameters_dict = self.parameters

        latlons = utils.get_latlon_for_all_obsids()

        chosen_parameter_headers = set()

        obsid_rows = []
        for obsid, types_dict in selection_dict.iteritems():
            for typename, parameter_dict in types_dict.iteritems():
                subname = None
                chosen_parameters = set()
                for parameter, checkbox in parameter_dict.iteritems():
                    if checkbox.isChecked():
                        subname = '.'.join((obsid, typename))

                        chosen_parameters.add(types_parameters_dict[typename][parameter].full_name)
                        chosen_parameters.update([v.full_name for k, v in types_parameters_dict[typename].iteritems() if v.hidden])

                        chosen_parameter_headers.add((typename, parameter))
                        chosen_parameter_headers.update([(typename, k) for k, v in types_parameters_dict[typename].iteritems() if v.hidden])

                if subname is not None:
                    lat, lon = latlons.get(obsid)
                    obsid_rows.append(';'.join((obsid, subname, str(lat), str(lon), '|'.join(chosen_parameters))))


        #Sort the parameters to the same order as they were entered into the ordered types dict.
        sorted_chosen_parameter_headers = [parameter.get_header_word() for typename, parameters in sorted(types_parameters_dict.iteritems()) for parametername, parameter in parameters.iteritems() if (typename, parametername) in chosen_parameter_headers]

        printlist = []
        printlist.append(u"FileVersion 1;" + str(len(sorted_chosen_parameter_headers)))
        printlist.append(u"NAME;INPUTTYPE;HINT")
        printlist.extend(sorted_chosen_parameter_headers)
        printlist.append(u'NAME;SUBNAME;LAT;LON;INPUTFIELD')

        printlist.extend(sorted(obsid_rows))
        return printlist

    def write_printlist_to_file(self, printlist):
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


class Parameter2(object):
    def __init__(self, name, hint, parameter_type, unit='', valuetype='numberDecimal|numberSigned', hidden=False):
        """ A class representing a parameter

        :param name: The name of the parameter
        :param hint: A hint to the user
        :param parameter_type: ex: flow, level, quality
        :param valuetype: a valuetype, ex: 'text', 'numberDecimal', 'numberSigned'
        :param hidden: True/False. If True, the parameter will not be printed as a checkbox.
        :return: None
        """
        self.name = name
        self.unit = unit
        self.parameter_type = parameter_type
        self.valuetype = valuetype
        self.hidden = hidden
        self.header_word = None

        if not hint:
            self.hint = self.name
        else:
            self.hint = utils.returnunicode(hint)

        if self.name.endswith(self.unit):
            self.full_name = '.'.join((self.parameter_type[0], self.name))
        else:
            self.full_name = '.'.join((self.parameter_type[0], self.name, self.unit))

    def __repr__(self):
        return self.name

    def get_header_word(self):
        if self.header_word is None:
            self.header_word = ';'.join((self.full_name, self.valuetype, self.hint))
        return self.header_word


class ExportToFieldLogger(PyQt4.QtGui.QMainWindow, export_fieldlogger_ui_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle("Export to FieldLogger") # Set the title for the dialog


        self.export_objects = None
        self.stored_settingskey = u'fieldlogger_export'
        self.stored_settings = self.get_stored_settings(self.ms, self.stored_settingskey)
        self.export_objects = self.create_export_objects_using_stored_settings(self.stored_settings, defs.tables_columns(), self.connect)

        if self.export_objects is None or not self.export_objects:
            self.export_objects = [ExportObject(defs.tables_columns(), self.connect),
                                   ExportObject(defs.tables_columns(), self.connect)]

        self.splitter = PyQt4.QtGui.QSplitter(PyQt4.QtCore.Qt.Vertical)
        self.main_vertical_layout.addWidget(self.splitter)
        self.widgets_layouts = self.init_splitters_layouts(self.splitter)
        if self.export_objects:
            map(lambda x: self.add_export_object_to_gui(self.widgets_layouts, x), self.export_objects)

        #Buttons
        self.save_settings_button = PyQt4.QtGui.QPushButton(u'Save settings')
        self.gridLayout_buttons.addWidget(self.save_settings_button, 1, 0)
        self.connect(self.save_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : map(lambda x: x(),
                                      [lambda : setattr(self, 'stored_settings', self.update_stored_settings(self.export_objects)),
                                       lambda : self.save_stored_settings(self.ms, self.stored_settings, self.stored_settingskey)]))
        self.add_one_parameter_button = PyQt4.QtGui.QPushButton(u'Add parameter')
        self.gridLayout_buttons.addWidget(self.add_one_parameter_button, 2, 0)
        self.connect(self.add_one_parameter_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.export_objects.append(ExportObject(defs.tables_columns(), self.connect)),
                                  lambda: self.add_export_object_to_gui(self.widgets_layouts, self.export_objects[-1])]))


        self.show()

    @staticmethod
    def init_splitters_layouts(splitter):
        widgets_layouts = []
        for nr in xrange(3):
            widget = PyQt4.QtGui.QWidget()
            layout = PyQt4.QtGui.QHBoxLayout()
            widget.setLayout(layout)
            splitter.addWidget(widget)
            widgets_layouts.append((widget, layout))
        return widgets_layouts

    def add_export_object_to_gui(self, widgets_layouts, export_object):

            self.create_widget_and_connect_widgets(widgets_layouts[0][1],
                                                   [export_object.parameter_table_label,
                                                    export_object._parameter_table,
                                                    export_object.parameter_column_label,
                                                    export_object._parameter_columns,
                                                    export_object.parameter_name_label,
                                                    export_object._distinct_parameter,
                                                    export_object.unit_table_label,
                                                    export_object._unit_table,
                                                    export_object.unit_column_label,
                                                    export_object._unit_columns,
                                                    export_object.unit_name_label,
                                                    export_object._distinct_unit,
                                                    export_object.input_type_label,
                                                    export_object._input_type])

            self.create_widget_and_connect_widgets(widgets_layouts[1][1],
                                                 [export_object.location_suffix_label,
                                                  export_object._location_suffix,
                                                  export_object.subname_label,
                                                  export_object._subname_suffix,
                                                  export_object.final_parameter_name_label,
                                                  export_object._final_parameter_name])

            button_widgets = self.create_widget_and_connect_widgets(parent_layout=None,
                                                    widgets=[export_object.copy_button,
                                                             export_object.cut_button,
                                                             export_object.paste_button],
                                                    layout_class=PyQt4.QtGui.QHBoxLayout)
            self.create_widget_and_connect_widgets(widgets_layouts[2][1],
                                                     [export_object.paste_from_selection_button,
                                                      button_widgets,
                                                      export_object.obsid_list])

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
        Creates a parameter setting dict from midvattensettings

        Reads a string entry from midvattensettings that looks like this:
        importmethod:
        :param ms: midvattensettings
        :return:
        """
        settings_string_raw = ms.settingsdict.get(settingskey, None)
        if settings_string_raw is None:
            return []
        settings_string = utils.returnunicode(settings_string_raw)
        objects_settings = settings_string.split(u'/')
        stored_settings = []

        for object_settings in objects_settings:
            settings = object_settings.split(u';')
            object_name = settings[0]

            try:
                attributes = tuple([tuple(setting.split(u':')) for setting in settings[1:]])
            except ValueError, e:
                utils.MessagebarAndLog.warning(log_msg=u"ExportFieldlogger: Getting stored settings didn't work: " + str(e))
                continue

            stored_settings.append((object_name, attributes))

        return tuple(stored_settings)

    @staticmethod
    def create_export_objects_using_stored_settings(stored_settings, tables_columns, connect):
        """
        """
        export_objects = []
        for index, attrs in stored_settings:
            export_object = ExportObject(tables_columns, connect)
            attrs_set = False
            for attr in attrs:
                if hasattr(export_object, attr[0]):
                    setattr(export_object, attr[0], attr[1])
                    attrs_set = True

            if attrs_set:
                export_objects.append(export_object)

        return export_objects

    @staticmethod
    def update_stored_settings(export_objects):
        return [(index, copy.deepcopy(export_object.get_settings())) for index, export_object in enumerate(export_objects)]

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

        for object_index, attrs in stored_settings:
            object_settings = [object_index]
            object_settings.extend([u':'.join((k, v)) for k, v in attrs if k and v])
            if len(object_settings) > 1:
                settings_list.append(u';'.join(object_settings))

        setting_string = u'/'.join(settings_list)
        ms.settingsdict[settingskey] = utils.returnunicode(setting_string)
        ms.save_settings()

    def create_export_printlist(self):
        """
        Creates a result list with FieldLogger format from selected obsids and parameters
        :return: a list with result lines to export to file
        """
        selection_dict = self.selection_dict
        types_parameters_dict = self.parameters

        latlons = utils.get_latlon_for_all_obsids()

        chosen_parameter_headers = set()

        obsid_rows = []
        for obsid, types_dict in selection_dict.iteritems():
            for typename, parameter_dict in types_dict.iteritems():
                subname = None
                chosen_parameters = set()
                for parameter, checkbox in parameter_dict.iteritems():
                    if checkbox.isChecked():
                        subname = '.'.join((obsid, typename))

                        chosen_parameters.add(types_parameters_dict[typename][parameter].full_name)
                        chosen_parameters.update([v.full_name for k, v in types_parameters_dict[typename].iteritems() if v.hidden])

                        chosen_parameter_headers.add((typename, parameter))
                        chosen_parameter_headers.update([(typename, k) for k, v in types_parameters_dict[typename].iteritems() if v.hidden])

                if subname is not None:
                    lat, lon = latlons.get(obsid)
                    obsid_rows.append(';'.join((obsid, subname, str(lat), str(lon), '|'.join(chosen_parameters))))


        #Sort the parameters to the same order as they were entered into the ordered types dict.
        sorted_chosen_parameter_headers = [parameter.get_header_word() for typename, parameters in sorted(types_parameters_dict.iteritems()) for parametername, parameter in parameters.iteritems() if (typename, parametername) in chosen_parameter_headers]

        printlist = []
        printlist.append(u"FileVersion 1;" + str(len(sorted_chosen_parameter_headers)))
        printlist.append(u"NAME;INPUTTYPE;HINT")
        printlist.extend(sorted_chosen_parameter_headers)
        printlist.append(u'NAME;SUBNAME;LAT;LON;INPUTFIELD')

        printlist.extend(sorted(obsid_rows))
        return printlist

    def write_printlist_to_file(self, printlist):
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


class ExportObject(object):
    def __init__(self, tables_columns, connect):
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
        self.parameter_table_label = PyQt4.QtGui.QLabel(u'Parameter Table')
        self._parameter_table = import_fieldlogger.default_combobox(editable=False)
        self.parameter_column_label = PyQt4.QtGui.QLabel(u'Column')
        self._parameter_columns = import_fieldlogger.default_combobox(editable=False)
        self.parameter_name_label = PyQt4.QtGui.QLabel(u'Parameter name')
        self._distinct_parameter = import_fieldlogger.default_combobox(editable=True)
        self.unit_table_label = PyQt4.QtGui.QLabel(u'Unit Table')
        self._unit_table = import_fieldlogger.default_combobox(editable=False)
        self.unit_column_label = PyQt4.QtGui.QLabel(u'Column')
        self._unit_columns = import_fieldlogger.default_combobox(editable=False)
        self.unit_name_label = PyQt4.QtGui.QLabel(u'Unit name')
        self._distinct_unit = import_fieldlogger.default_combobox(editable=True)
        self.input_type_label = PyQt4.QtGui.QLabel(u'Fieldlogger input type')
        self._input_type = import_fieldlogger.default_combobox(editable=True)
        self.location_suffix_label = PyQt4.QtGui.QLabel(u'Location suffix')
        self._location_suffix = PyQt4.QtGui.QLineEdit()
        self.subname_label = PyQt4.QtGui.QLabel(u'Subname suffix')
        self._subname_suffix = PyQt4.QtGui.QLineEdit()
        self.final_parameter_name_label = PyQt4.QtGui.QLabel(u'Final parameter name')
        self._final_parameter_name = PyQt4.QtGui.QLineEdit()
        self.obsid_list = CopyPasteDeleteableQListWidget()
        self.paste_from_selection_button = PyQt4.QtGui.QPushButton(u'Paste obs_points selection')
        self.copy_button = PyQt4.QtGui.QPushButton(u'Copy')
        self.cut_button = PyQt4.QtGui.QPushButton(u'Cut')
        self.paste_button = PyQt4.QtGui.QPushButton(u'Paste')
        
        #------------------------------------------------------------------------
        self._parameter_table.addItems(sorted(tables_columns.keys()))
        connect(self._parameter_table, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._parameter_columns, tables_columns.get(self.parameter_table, [])))
        connect(self._parameter_columns, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._distinct_parameter, self.get_distinct_values(self.parameter_table, self.parameter_columns)))

        self._unit_table.addItems(sorted(tables_columns.keys()))
        connect(self._unit_table, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._unit_columns, tables_columns.get(self.unit_table, [])))
        connect(self._unit_columns, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self.replace_items(self._distinct_unit, self.get_distinct_values(self.unit_table, self.unit_columns)))

        connect(self._distinct_parameter, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._final_parameter_name.setText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        connect(self._distinct_unit, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._final_parameter_name.setText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        #------------------------------------------------------------------------------------

        self._input_type.addItems([u'numberDecimal|numberSigned', u'numberDecimal', u'numberSigned', u'text'])

        #-------------------------------------------------------------------------------------

        self._location_suffix.setToolTip(u'Name shown in fieldlogger map. location.SUFFIX. Ex: location.projectnumber')
        self._subname_suffix.setToolTip(u'Name shown if more than one subname exists for each location. Ex: location.projectnumber.parameter_group')
        
        #-------------------------------------------------------------------------------------

        self.obsid_list.setSelectionMode(PyQt4.QtGui.QAbstractItemView.MultiSelection)
        connect(self.paste_from_selection_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.obsid_list.paste_data(utils.get_selected_features_as_tuple('obs_points')))
        connect(self.copy_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.obsid_list.copy_data())
        connect(self.cut_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.obsid_list.cut_data())
        connect(self.paste_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.obsid_list.paste_data())

    @staticmethod
    def replace_items(combobox, items):
        combobox.clear()
        combobox.addItem(u'')
        combobox.addItems(items)

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
    def set_combobox(combobox, value):
        index = combobox.findText(utils.returnunicode(value))
        if index != -1:
            combobox.setCurrentIndex(index)

    @property
    def parameter_table(self):
        return utils.returnunicode(self._parameter_table.currentText())
    
    @parameter_table.setter
    def parameter_table(self, value):
        self.set_combobox(self._parameter_table, value)
        
    @property
    def parameter_columns(self):
        return utils.returnunicode(self._parameter_columns.currentText())

    @parameter_columns.setter
    def parameter_columns(self, value):
        self.set_combobox(self._parameter_columns, value)
        
    @property
    def distinct_parameter(self):
        return utils.returnunicode(self._distinct_parameter.currentText())
    
    @distinct_parameter.setter
    def distinct_parameter(self, value):
        self.set_combobox(self._distinct_parameter, value)

    @property
    def unit_table(self):
        return utils.returnunicode(self._unit_table.currentText())

    @unit_table.setter
    def unit_table(self, value):
        self.set_combobox(self._unit_table, value)

    @property
    def unit_columns(self):
        return utils.returnunicode(self._unit_columns.currentText())
    
    @unit_columns.setter
    def unit_columns(self, value):
        self.set_combobox(self._unit_columns, value)

    @property
    def distinct_unit(self):
        return utils.returnunicode(self._distinct_unit.currentText())

    @distinct_unit.setter
    def distinct_unit(self, value):
        self.set_combobox(self._distinct_unit, value)

    @property
    def final_parameter_name(self):
        return utils.returnunicode(self._final_parameter_name.text())
    
    @final_parameter_name.setter
    def final_parameter_name(self, value):
        self._final_parameter_name.setText(utils.returnunicode(value))

    @property
    def input_type(self):
        return utils.returnunicode(self._input_type.currentText())

    @input_type.setter
    def input_type(self, value):
        self.set_combobox(self._input_type, value)

    @property
    def location_suffix(self):
        return utils.returnunicode(self._location_suffix.text())

    @location_suffix.setter
    def location_suffix(self, value):
        self._location_suffix.setText(utils.returnunicode(value))

    @property
    def subname_suffix(self):
        return utils.returnunicode(self._subname_suffix.text())

    @subname_suffix.setter
    def subname_suffix(self, value):
        self._subname_suffix.setText(utils.returnunicode(value))
        
    def get_settings(self):
        settings = ((u'parameter_table', self.parameter_table),
                   (u'parameter_columns', self.parameter_columns),
                   (u'distinct_parameter', self.distinct_parameter),
                   (u'unit_table', self.unit_table),
                   (u'unit_columns', self.unit_columns),
                   (u'distinct_unit', self.distinct_unit),
                   (u'final_parameter_name', self.final_parameter_name),
                   (u'input_type', self.input_type),
                   (u'location_suffix', self.location_suffix),
                   (u'subname_suffix', self.subname_suffix))

        settings = tuple((k, v) for k, v in settings if v)
        return utils.returnunicode(settings, keep_containers=True)
    

class CopyPasteDeleteableQListWidget(PyQt4.QtGui.QListWidget):
    def __init__(self, *args, **kwargs):
        super(CopyPasteDeleteableQListWidget, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        utils.pop_up_info("Event: " + str(event) + " type: " + str(type(event)))
        if not isinstance(event, PyQt4.QtGui.QKeySequence):
            return None
        if event.matches(event, PyQt4.QtGui.QKeySequence.Copy):
            self.copy_data()
        elif event.matches(PyQt4.QtGui.QKeySequence.Paste):
            self.paste_data()
        elif event.matches(PyQt4.QtGui.QKeySequence.Delete):
            self.delete_data()
        elif event.matches(PyQt4.QtGui.QKeySequence.Cut):
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
        old_text = [self.item(i).text() for i in xrange(self.count())]
        new_items = set()
        new_items.update(paste_list)
        new_items.update(old_text)
        self.clear()
        self.addItems(list(sorted(new_items)))

    def delete_data(self):
        all_items = [self.item(i).text() for i in xrange(self.count())]
        items_to_delete = [item.text() for item in self.selectedItems()]
        keep_items = [item for item in all_items if item not in items_to_delete]
        self.clear()
        self.addItems(sorted(keep_items))

