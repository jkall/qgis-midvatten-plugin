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

import midvatten_utils as utils
from definitions.midvatten_defs import standard_parameters_for_w_qual_field, standard_parameters_for_w_flow

export_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'export_fieldlogger_ui_dialog.ui'))[0]


class ExportToFieldLogger(PyQt4.QtGui.QMainWindow, export_fieldlogger_ui_dialog):
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

        self.show()

    def create_parameters(self):
        """ Creaters self.parameters dict with parameters
        :return: a dict like "{'typename': {'parameter': Parameter()}}"
        """
        parameters = {}

        #level parameters:
        parameters['level'] = {'meas': Parameter('meas', '[m] from top of tube', 'level')}
        parameters['level']['comment'] = Parameter('comment', 'make comment...', 'level', 'text', True)

        #Flow parameters:
        flow_params_and_units = utils.get_flow_params_and_units()
        parameters['flow'] = dict([(param, Parameter(param, unit, 'flow')) for param, unit in standard_parameters_for_w_flow().iteritems()])
        parameters['flow'].update(dict([(param, Parameter(param, unit[0], 'flow')) for param, unit in flow_params_and_units.iteritems()]))
        parameters['flow']['comment'] = Parameter('comment', 'make comment...', 'flow', 'text', True)
        parameters['flow']['instrument'] = Parameter('instrument', 'the measurement instrument id', 'flow', 'text', True)

        #Quality parameters
        qual_params_and_units = utils.get_qual_params_and_units()
        parameters['quality'] = dict([(param, Parameter(param, unit, 'quality')) for param, unit in standard_parameters_for_w_qual_field().iteritems()])
        parameters['quality'].update(dict([(param, Parameter(param, unit[0], 'quality')) for param, unit in qual_params_and_units.iteritems()]))
        parameters['quality']['comment'] = Parameter('comment', 'make comment...', 'quality', 'text', True)
        parameters['quality']['instrument'] = Parameter('instrument', 'the measurement instrument id', 'quality', 'text', True)
        parameters['quality']['flow_lpm'] = Parameter('flow_lpm', 'the water flow during water quality measurement', 'quality', 'numberDecimal|numberSigned', True)

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
            splitted = type_parameter_name.split('.')
            typename = splitted[0]
            parametername = '.'.join(splitted[1:])
            checkbox = types_dict[typename][parametername]
            checkbox.setChecked(check_state)

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

                        chosen_parameter_headers.add(types_parameters_dict[typename][parameter].get_header_word())
                        chosen_parameter_headers.update([v.get_header_word() for k, v in types_parameters_dict[typename].iteritems() if v.hidden])

                if subname is not None:
                    lat, lon = latlons.get(obsid)
                    obsid_rows.append(';'.join((obsid, subname, str(lat), str(lon), '|'.join(chosen_parameters))))

        printlist = []
        printlist.append("FileVersion 1;" + str(len(chosen_parameter_headers)))
        printlist.append("NAME;INPUTTYPE;HINT")
        printlist.extend(sorted(chosen_parameter_headers))
        printlist.append('NAME;SUBNAME;LAT;LON;INPUTFIELD')

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



class Parameter(object):
    def __init__(self, name, hint, parameter_type, valuetype='numberDecimal|numberSigned', hidden=False):
        """ A class representing a parameter

        :param name: The name of the parameter
        :param hint: A hint to the user
        :param parameter_type: ex: flow, level, quality
        :param valuetype: a valuetype, ex: 'text', 'numberDecimal', 'numberSigned'
        :param hidden: True/False. If True, the parameter will not be printed as a checkbox.
        :return: None
        """
        self.name = name
        self.parameter_type = parameter_type
        self.valuetype = valuetype
        self.hidden = hidden
        self.header_word = None

        if not hint:
            self.hint = self.name
        else:
            self.hint = utils.returnunicode(hint)

        self.full_name = '.'.join((self.parameter_type, self.name))

    def __repr__(self):
        return self.name

    def get_header_word(self):
        if self.header_word is None:
            self.header_word = ';'.join((self.full_name, self.valuetype, self.hint))
        return self.header_word

