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
    def __init__(self, parent, settingsdict1={}, obsids=None):
        self.iface = parent
        self.obsids = obsids

        self.settingsdict = settingsdict1
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle("Export to FieldLogger") # Set the title for the dialog

        self.splitter = PyQt4.QtGui.QSplitter(PyQt4.QtCore.Qt.Vertical)
        self.export_objects = None

        self.main_vertical_layout.addWidget(self.splitter)

        self.stored_settingskey = u'fieldlogger_export'

        #self.stored_settings = self.get_stored_settings(self.ms, self.stored_settingskey)
        #self.export_objects = self.create_export_objects_using_stored_settings(self.stored_settings, self.splitter)
        if self.export_objects is None or not self.export_objects:
            self.export_objects = [ExportObject(defs.tables_columns(), self.connect)]

        utils.pop_up_info(str(self.export_objects))
        self.add_export_objects_to_gui(self.splitter, self.export_objects)

        self.show()

    def add_export_objects_to_gui(self, splitter, export_objects):
        """
        This needs to create a QHBoxlayout for every "split".
        In every split, one QVBoxlayout is created for every export object
         
        Maybe the export objects could be stored using column as key. 
         
        :param splitter: 
        :param export_objects: 
        :return: 
        """

        # Create main layouts for the splitter
        self.widgets_layouts = []
        for nr in xrange(4):
            widget = PyQt4.QtGui.QWidget()
            layout = PyQt4.QtGui.QHBoxLayout()
            widget.setLayout(layout)
            self.splitter.addWidget(widget)
            self.widgets_layouts.append((widget, layout))

        self.columns = {}

        for index, export_object in enumerate(self.export_objects):

            widget0 = self.create_widget_and_connect_widgets(self.widgets_layouts[0][1],
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
                                                             export_object._distinct_unit])

            widget1 = self.create_widget_and_connect_widgets(self.widgets_layouts[1][1], [export_object.input_type])

            widget2 = self.create_widget_and_connect_widgets(self.widgets_layouts[2][1],
                                                             [export_object.location_suffix_label,
                                                              export_object._location_suffix,
                                                              export_object.subname_label,
                                                              export_object._subname_suffix,
                                                              export_object.final_parameter_name_label,
                                                              export_object._final_parameter_name])

            widget3 = self.create_widget_and_connect_widgets(self.widgets_layouts[3][1],
                                                             [export_object.paste_from_selection_button,
                                                              export_object.obsid_list])


            self.columns[index] = (export_object, widget0, widget1, widget2, widget3)

    def create_widget_and_connect_widgets(self, parent_layout, widgets):
        new_widget = PyQt4.QtGui.QWidget()
        layout = PyQt4.QtGui.QVBoxLayout()
        new_widget.setLayout(layout)
        parent_layout.addWidget(new_widget)
        for widget in widgets:
            layout.addWidget(widget)

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
    def create_export_objects_using_stored_settings(stored_settings, splitter):
        """
        """
        pass

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
        self.input_type = import_fieldlogger.default_combobox(editable=True)
        self.location_suffix_label = PyQt4.QtGui.QLabel(u'Location suffix')
        self._location_suffix = PyQt4.QtGui.QLineEdit()
        self.subname_label = PyQt4.QtGui.QLabel(u'Subname suffix')
        self._subname_suffix = PyQt4.QtGui.QLineEdit()
        self.final_parameter_name_label = PyQt4.QtGui.QLabel(u'Final parameter name')
        self._final_parameter_name = PyQt4.QtGui.QLineEdit()
        self.obsid_list = CopyPasteDeleteableQListWidget()
        self.paste_from_selection_button = PyQt4.QtGui.QPushButton(u'Paste obs_points selection')
        
        #------------------------------------------------------------------------
        self._parameter_table.addItems(sorted(tables_columns.keys()))
        connect(self._parameter_table, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self._parameter_columns.addItems(tables_columns.get(self.parameter_table, [])))     
        connect(self._parameter_columns, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self._distinct_parameter.addItems(self.get_distinct_values(self.parameter_table, self.parameter_columns)))

        self._unit_table.addItems(sorted(tables_columns.keys()))
        connect(self._unit_table, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self._unit_columns.addItems(tables_columns.get(self.unit_table, [])))
        connect(self._unit_columns, PyQt4.QtCore.SIGNAL("activated(int)"),
                     lambda: self._distinct_unit.addItems(self.get_distinct_values(self.unit_table, self.unit_columns)))

        connect(self._distinct_parameter, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._final_parameter_name.setEditText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        connect(self._distinct_unit, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._final_parameter_name.setEditText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        #------------------------------------------------------------------------------------

        self.input_type.addItems([u'numberDecimal|numberSigned', u'numberDecimal',u'numberSigned', u'text'])

        #-------------------------------------------------------------------------------------

        self._location_suffix.setToolTip(u'Name shown in fieldlogger map. location.SUFFIX. Ex: location.projectnumber')
        self._subname_suffix.setToolTip(u'Name shown if more than one subname exists for each location. Ex: location.projectnumber.parameter_group')
        
        #-------------------------------------------------------------------------------------

        self.obsid_list.setSelectionMode(PyQt4.QtGui.QAbstractItemView.MultiSelection)
        connect(self.paste_from_selection_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.obsid_list.paste_items(utils.get_selected_features_as_tuple('obs_points')))


    @staticmethod
    def get_distinct_values(tablename, columnname):
        if not tablename or not columnname:
            return []
        sql = '''SELECT distinct "%s" from "%s"'''%(tablename, columnname)
        connection_ok, result = utils.sql_load_fr_db(sql)
        
        if not connection_ok:
            textstring = u"""Cannot get data from sql """ + utils.returnunicode(sql)
            utils.MessagebarAndLog.critical(
                bar_msg=u"Error, sql failed, see log message panel",
                log_msg=textstring)
            return []
        
        values = [col[0] for col in result]
        return values

    @property
    def parameter_table(self):
        return utils.returnunicode(self._parameter_table.currentText())

    @property
    def parameter_columns(self):
        return utils.returnunicode(self._parameter_columns.currentText())

    @property
    def unit_table(self):
        return utils.returnunicode(self._unit_table.currentText())

    @property
    def unit_columns(self):
        return utils.returnunicode(self._unit_columns.currentText())

    @property
    def final_parameter_name(self):
        return utils.returnunicode(self._final_parameter_name.currentText())

    @property
    def distinct_parameter(self):
        return utils.returnunicode(self._distinct_parameter.currentText())

    @property
    def distinct_parameter(self):
        return utils.returnunicode(self._distinct_parameter.currentText())

    @property
    def location_suffix(self):
        return utils.returnunicode(self._location_suffix.text())

    @location_suffix.setter
    def location_suffix(self, value):
        self._location_suffix.setText(value)

    @property
    def subname_suffix(self):
        return utils.returnunicode(self._subname_suffix.text())

    @subname_suffix.setter
    def subname_suffix(self, value):
        self._subname_suffix.setText(value)
    

class CopyPasteDeleteableQListWidget(PyQt4.QtGui.QListWidget):
    def __init__(self, *args, **kwargs):
        super(CopyPasteDeleteableQListWidget, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if isinstance(event, PyQt4.QtGui.QKeySequence.Copy):
            self.selectedItems()
            stringlist = PyQt4.QtCore.QStringList(self.selectedItems())
            PyQt4.QtGui.QApplication.clipboard().setText(u'\n'.join(stringlist))
        elif isinstance(event, PyQt4.QtGui.QKeySequence.Paste):
            new_text = PyQt4.QtGui.QApplication.clipboard().text().split(u'\n')
            self.paste_items(new_text)

        elif isinstance(event, PyQt4.QtGui.QKeySequence.Delete):
            all_items = [self.item(i).text() for i in self.count()]
            items_to_delete = PyQt4.QtCore.QStringList(self.selectedItems())
            keep_items = [item for item in all_items if item not in items_to_delete]
            self.clear()
            self.addItems(sorted(keep_items))

    def paste_items(self, paste_list):
        old_text = [self.item(i).text() for i in xrange(self.count())]
        new_items = set()
        new_items.update(paste_list)
        new_items.update(old_text)
        self.clear()
        self.addItems(list(sorted(new_items)))

