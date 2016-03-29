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
import sqlite3 as sqlite, csv, codecs, cStringIO, os, os.path
import midvatten_utils as utils

export_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'export_fieldlogger_ui_dialog.ui'))[0]


class ExportToFieldLogger(PyQt4.QtGui.QMainWindow, export_fieldlogger_ui_dialog):
    """ Class handling export of data for fieldlogger """
    
    def __init__(self, parent, settingsdict1={}, obsids=None):
        self.obsids = obsids

        self.settingsdict = settingsdict1
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        self.setWindowTitle("Export to FieldLogger") # Set the title for the dialog

        self.parameters = self.create_parameters()
        self.set_headers(self.gridLayout_selections, self.parameters.keys(), self.gridWidget_selections)
        self.set_and_connect_selectall(self.gridLayout_selections, self.parameters.keys(), self.gridWidget_selections)
        self.add_line(self.gridLayout_selections, len(self.parameters.keys()), self.gridWidget_selections)
        self.obsids = utils.get_all_obsids()

        self.selection_dict = self.build_selection_dict(self.obsids, self.parameters.keys(), self.gridWidget_selections)
        self.set_obsids_and_parameters_checkboxes(self.gridLayout_selections, self.selection_dict)

        self.connect(self.pushButtonExport, PyQt4.QtCore.SIGNAL("clicked()"), self.export_selected)

        self.check_checkboxes_from_initial_selection(obsids, self.selection_dict)

        self.show()

    def create_parameters(self):
        """ Creaters self.parameters dict with parameters
        :return: a dict like "{'parameter': Parameter()}"
        """
        parameters = {}
        parameters['head_cm'] = Parameter('head_cm', '[m] from top of tube')
        parameters['comment'] = Parameter('comment', 'make comment...', 'text')
        parameters['instrument'] = Parameter('instrument', 'the measurement instrument id', 'text')
        parameters['flow_lpm'] = Parameter('flow_lpm', 'the water flow during water quality measurement')

        qual_params_and_units = utils.get_qual_params_and_units()
        parameters.update(dict([(param, Parameter(param, unit[0])) for param, unit in qual_params_and_units.iteritems()]))

        flow_params_and_units = utils.get_flow_params_and_units()
        parameters.update(dict([(param, Parameter(param, unit[0])) for param, unit in flow_params_and_units.iteritems()]))
        return parameters

    def set_headers(self, grid, parameters, widget_parent):
        """
        Creates Qlabel headers for all parameters
        :param grid: A QGridLayout.
        :param parameters: The parameter names to print as headers.
        :return: None
        """
        rownr = grid.rowCount()
        grid.addWidget(PyQt4.QtGui.QLabel('Obsid', widget_parent), rownr, 0)

        for colnr, parameter in enumerate(sorted(parameters)):
            label = PyQt4.QtGui.QLabel(parameter)
            grid.addWidget(label, rownr, colnr + 1)

    def set_and_connect_selectall(self, grid, parameters, widget_parent):
        """
        Creates checkboxes for select all for all parameters
        :param grid: A QGridLayout.
        :param parameters: Parameter names
        :return: None
        """
        rownr = grid.rowCount()
        grid.addWidget(PyQt4.QtGui.QLabel('Select all'), rownr, 0)
        for colnr, parameter in enumerate(sorted(parameters)):
            checkbox = PyQt4.QtGui.QCheckBox(widget_parent)
            checkbox.setToolTip(parameter)
            checkbox.setObjectName(parameter)
            self.connect(checkbox, PyQt4.QtCore.SIGNAL("clicked()"), self.select_all_click)
            grid.addWidget(checkbox, rownr, colnr + 1)

    def add_line(self, grid, num_cols, widget_parent):
        rownr = grid.rowCount()
        frame = PyQt4.QtGui.QFrame(widget_parent)
        frame.setFrameShape(PyQt4.QtGui.QFrame.HLine)
        grid.addWidget(frame, rownr, 0, 1, num_cols + 1)

    def build_selection_dict(self, obsids, parameters, parent_widget):
        """ Creates a dict of obsids and their parameter checkbox objects
        :param obsids: A list of obsids
        :param parameters: A list of parameters
        :param parent_widget: The parent widget. It might be needed for this to work, but not sure.
        :return: a dict like {'obsid': {'parametername': QCheckBox, ...}, ...}
        """
        selection_dict = {}
        for obsid in obsids:
            parameter_dict = dict([(parameter, PyQt4.QtGui.QCheckBox(parent_widget)) for parameter in parameters]) #'checkbox_' + obsid + "_" + parameter

            selection_dict[obsid] = parameter_dict
        return selection_dict

    def set_obsids_and_parameters_checkboxes(self, grid, selection_dict):
        """
        Creates a matrix of checkboxes for choosing parameters
        :param grid: A QGridLayout.
        :param selection_dict: a dict like {'obsid': {'parametername': QCheckBox, ...}, ...}
        :return: None
        """
        start_rownr = grid.rowCount()
        for rownr, obs_parameter_dict_tuple in enumerate(sorted(selection_dict.iteritems())):
            rownr = start_rownr + rownr
            obsid, parameter_dict = obs_parameter_dict_tuple
            grid.addWidget(PyQt4.QtGui.QLabel(obsid), rownr, 0)
            for parno, parameter_checkbox_tuple in enumerate(sorted(parameter_dict.iteritems())):
                parameter, checkbox = parameter_checkbox_tuple
                checkbox.setMinimumSize(20, 20)
                checkbox.setToolTip(parameter)
                colnr = parno + 1
                grid.addWidget(checkbox, rownr, colnr)

    def select_all_click(self):
        """
        Method representing a select_all click.

        self.sender() is used to find the currently clicked checkbox.
        :return: None
        """
        checkbox = self.sender()
        parameter = checkbox.objectName()
        check_state = checkbox.isChecked()
        self.select_all(parameter, check_state)

    def select_all(self, parameter, check_state):
        """
        Selects or deselects a parameter for all obsids
        :param parameter: A parametername
        :param check_state: The state of the currently selected select_all checkbox.
        :return:
        """
        for obsid, parameter_dict in self.selection_dict.iteritems():
            checkbox = parameter_dict[parameter]
            checkbox.setChecked(check_state)

    def check_checkboxes_from_initial_selection(self, obsids, selection_dict):
        """
        Checks the checkboxes for all obsids
        :param obsids: Obsids to set checkboxes checked.
        :return: None
        """
        for obsid in obsids:
            parameter_dict = selection_dict[obsid]
            for parameter, checkbox in parameter_dict.iteritems():
                checkbox.setChecked(True)

    def export_selected(self):
        """ Export the selected obsids and parameters to a file
        """
        selection_dict = self.selection_dict
        filename = PyQt4.QtGui.QFileDialog.getSaveFileName(None, "Choose a file name","","csv (*.csv)")

        chosen_parameters = set([parameter for obsid, parameter_dict in selection_dict.iteritems() for parameter, checkbox in parameter_dict.iteritems() if checkbox.isChecked()])

        printlist = []
        printlist.append("FileVersion 1;" + str(len(chosen_parameters)))
        printlist.append("NAME;INPUTTYPE;HINT")
        printlist.extend([self.parameter_export_word(parameter) for parameter in sorted(chosen_parameters)])
        printlist.append('NAME;SUBNAME;LAT;LON;INPUTFIELD')

        latlons = utils.get_latlon_for_all_obsids()
        printlist.extend([self.obsid_export_word(obsid, parameter_dict, latlons.get(obsid)) for obsid, parameter_dict in sorted(selection_dict.iteritems()) if self.obsid_export_word(obsid, parameter_dict, latlons.get(obsid))])

        try:
            with open(filename, 'w') as f:
                f.write('\n'.join(printlist))
        except IOError, e:
            utils.pop_up_info("Writing of file failed!: " + str(e))

    def parameter_export_word(self, parameter):
        """ Creates a print line for a parameter for the FieldLogger format
        :param parameter: The name of the parameter
        :return: A word like "parametername;type;hint\n"
        """
        parameters = self.parameters
        valuetype = parameters[parameter].valuetype
        hint = parameters[parameter].hint
        try:
            return ';'.join([parameter, valuetype, hint])
        except:
            utils.pop_up_info("Parameter: " + parameter)
            utils.pop_up_info("valuetype: " + valuetype)
            utils.pop_up_info("hint:" + hint)

    def obsid_export_word(self, obsid, parameter_dict, latlon):
        """ Creates a print line for an obsid
        :param obsid: The obsid to print
        :param parameter_dict: A parameter_dict with parameter name as key and a QCheckbox as value.
        :param latlon: a tuple with (lat, lon)
        :return: Returns a word like "obsid;obsid;lat;lon;param1|param2|param3"
        """
        out_parameters = '|'.join([parameter for parameter, checkbox in sorted(parameter_dict.iteritems()) if checkbox.isChecked()])
        if out_parameters:
            return ';'.join([obsid, obsid, str(latlon[0]), str(latlon[1]), out_parameters])
        else:
            return False


class Parameter(object):
    def __init__(self, name, hint, valuetype='numberDecimal|numberSigned'):
        """ A class representing a parameter

        :param name: The name of the parameter
        :param hint: A hint to the user
        :param valuetype: a valuetype, ex: 'text', 'numberDecimal', 'numberSigned'
        :return: None
        """
        self.name = name
        if not hint:
            self.hint = 'no hint'
        else:
            self.hint = self.decode_word(hint, 'no hint')
        self.valuetype = valuetype

    def decode_word(self, word, default=''):
        decoded_word = default
        for charset in ('cp1252', 'cp1250', 'iso8859-1', 'utf-8'):
            try:
                decoded_word = word.decode(charset)
            except UnicodeEncodeError:
                continue
            else:
                break
        return decoded_word
