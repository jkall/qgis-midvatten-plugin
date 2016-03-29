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

        self.parameters = self.get_parameters()
        self.set_headers(self.horizontalLayout_headers, self.parameters)
        self.obsids = utils.get_all_obsids()

        self.selection_dict = self.build_selection_dict(self.obsids, self.parameters, self.gridWidget_selections)
        self.set_obsids_and_parameters_checkboxes(self.gridLayout_selections, self.selection_dict)
        self.set_and_connect_selectall(self.horizontalLayout_selectall, self.parameters)
        self.connect(self.pushButtonExport, PyQt4.QtCore.SIGNAL("clicked()"), self.export_selected)

        self.check_checkboxes_from_initial_selection(obsids, self.selection_dict)

        #utils.pop_up_info(str(obsids))

        self.show()

    def get_parameters(self):
        return ['head_cm', 'comment']

    def set_headers(self, header_field, parameters):
        """
        :param header_field: The QHBoxLayout to put the headers in.
        :param parameters: The parameter names to print as headers.
        :return: None
        """

        header_field.addWidget(PyQt4.QtGui.QLabel('Obsid'))

        for parameter in sorted(parameters):
            label = PyQt4.QtGui.QLabel(parameter)
            header_field.addWidget(label)

    def set_and_connect_selectall(self, select_all_field, parameters):
        select_all_field.addWidget(PyQt4.QtGui.QLabel('Select all'))
        for colnr, parameter in enumerate(sorted(parameters)):
            checkbox = PyQt4.QtGui.QCheckBox()
            checkbox.setObjectName('selectall_' + parameter)
            self.connect(checkbox, PyQt4.QtCore.SIGNAL("clicked()"), self.select_all_click)
            select_all_field.addWidget(checkbox)

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

    def set_obsids_and_parameters_checkboxes(self, grid_layout, selection_dict):
        """
        Creates a matrix of checkboxes for choosing parameters
        :param grid_layout: A QGridLayout.
        :param selection_dict: a dict like {'obsid': {'parametername': QCheckBox, ...}, ...}
        :return: None
        """
        for rownr, obs_parameter_dict_tuple in enumerate(sorted(selection_dict.iteritems())):
            #Write obsidname as a qlabel

            obsid, parameter_dict = obs_parameter_dict_tuple
            grid_layout.addWidget(PyQt4.QtGui.QLabel(obsid), rownr, 0)
            for parno, parameter_checkbox_tuple in enumerate(sorted(parameter_dict.iteritems())):
                parameter, checkbox = parameter_checkbox_tuple
                checkbox.setMinimumSize(20, 20)
                colnr = parno + 1
                grid_layout.addWidget(checkbox, rownr, colnr)

    def select_all_click(self):
        checkbox = self.sender()
        parameter = checkbox.objectName().lstrip('selectall_')
        check_state = checkbox.isChecked()
        self.select_all(parameter, check_state)

    def select_all(self, parameter, check_state):
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

#
#        utils.pop_up_info('\n'.join(checkboxes))
        printlist = []
        printlist.append("FileVersion 1;2\n")
        printlist.append("NAME;INPUTTYPE;HINT\n")
        printlist.extend([self.parameter_export_word(parameter) for parameter in sorted(chosen_parameters)])


        printlist.append('NAME;SUBNAME;LAT;LON;INPUTFIELD\n')

        printlist.extend([self.obsid_export_word(obsid, parameter_dict) for obsid, parameter_dict in sorted(selection_dict.iteritems()) if self.obsid_export_word(obsid, parameter_dict)])

        utils.pop_up_info(str(printlist))


        #utils.pop_up_info(str(chosen_parameters))


#        try:
#            with open(filename, 'w') as f:
#                f.write("test")
#        except IOError:
#            pass

    def parameter_export_word(self, parameter):

        parameter_hint = {'head_cm': "[m] from top of tube. -999 for dry wells or other problems",
                          'comment': 'make comment, ex: "dry"'}
        parameter_type = {'head_cm': 'numberSigned',
                          'comment': 'text'}

        return ';'.join([parameter, parameter_type, parameter_hint]) + '\n'

    def obsid_export_word(self, obsid, parameter_dict):
        out_parameters = '|'.join([parameter for parameter, checkbox in sorted(parameter_dict.iteritems()) if checkbox.isChecked()])
        if out_parameters:
            return ';'.join([obsid, obsid, 'lat', 'lon', out_parameters, '\n'])
        else:
            return False

