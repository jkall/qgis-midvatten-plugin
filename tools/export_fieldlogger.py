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
import warnings
import qgis.gui

import midvatten_utils as utils
import definitions.midvatten_defs as defs
from import_data_to_db import midv_data_importer
import import_fieldlogger
from midvatten_utils import returnunicode

export_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]


class ExportToFieldLogger(PyQt4.QtGui.QMainWindow, export_fieldlogger_ui_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle("Export to FieldLogger") # Set the title for the dialog

        tables_columns = defs.tables_columns()

        self.export_objects = None
        self.stored_settingskey = u'fieldlogger_export'

        self.export_objects = self.create_export_objects_using_stored_settings(self.get_stored_settings(self.ms, self.stored_settingskey),
                                                                               tables_columns,
                                                                               self.connect)
        if self.export_objects is None or not self.export_objects:
            self.export_objects = [ExportObject(self.connect)]

        self.splitter = PyQt4.QtGui.QSplitter(PyQt4.QtCore.Qt.Vertical)
        self.main_vertical_layout.addWidget(self.splitter)

        #This is about adding a messagebar to the fieldlogger window. But for some reason qgis crashes or closes
        #when the timer ends for the regular messagebar
        #self.lbl = MessageBar(self.splitter)
        #qgis.utils.iface.optional_bar = self.lbl

        self.widgets_layouts = self.init_splitters_layouts(self.splitter)

        if self.export_objects:
            for export_object in self.export_objects:
                self.add_export_object_to_gui(self.widgets_layouts, export_object)

        #ParameterUnitBrowser
        browser = ParameterUnitBrowser(tables_columns, self.connect)
        self.gridLayout_buttons.addWidget(browser.widget, 0, 0)
        

        #Buttons
        self.save_settings_button = PyQt4.QtGui.QPushButton(u'Save settings')
        self.save_settings_button.setToolTip(u'Saves the current parameter setup to midvatten settings.')
        self.gridLayout_buttons.addWidget(self.save_settings_button, 1, 0)
        self.connect(self.save_settings_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.save_stored_settings(self.ms,
                                                            self.update_stored_settings(self.export_objects),
                                                            self.stored_settingskey))

        self.add_one_parameter_button = PyQt4.QtGui.QPushButton(u'New parameter')
        self.add_one_parameter_button.setToolTip(u'Creates an additional empty parameter setting.')
        self.gridLayout_buttons.addWidget(self.add_one_parameter_button, 2, 0)
        #Lambda and map is used to run several functions for every button click
        self.connect(self.add_one_parameter_button, PyQt4.QtCore.SIGNAL("clicked()"),
                     lambda: map(lambda x: x(),
                                 [lambda: self.export_objects.append(ExportObject(self.connect)),
                                  lambda: self.add_export_object_to_gui(self.widgets_layouts, self.export_objects[-1])]))

        self.export_button = PyQt4.QtGui.QPushButton(u'Export')

        self.export_button.setToolTip(u'Exports to a Fieldlogger wells file.')
        self.gridLayout_buttons.addWidget(self.export_button, 3, 0)
        # Lambda and map is used to run several functions for every button click
        self.connect(self.export_button, PyQt4.QtCore.SIGNAL("clicked()"),
                                  lambda: map(lambda x: x(),
                                 [lambda: self.save_stored_settings(self.ms,
                                                                    self.update_stored_settings(self.export_objects),
                                                                    self.stored_settingskey),
                                  lambda: self.write_printlist_to_file(self.create_export_printlist(self.export_objects))]))

        self.gridLayout_buttons.setRowStretch(4, 1)

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

    def add_export_object_to_gui(self, widgets_layouts, export_object):

            self.create_widget_and_connect_widgets(widgets_layouts[0][1],
                                                   [PyQt4.QtGui.QLabel(u'Fieldlogger parameters and locations:'),
                                                    PyQt4.QtGui.QLabel(u'Parameter name'),
                                                    export_object._final_parameter_name,
                                                    PyQt4.QtGui.QLabel(u'Input type'),
                                                    export_object._input_type,
                                                    PyQt4.QtGui.QLabel(u'Hint'),
                                                    export_object._hint,
                                                    get_line(),
                                                    PyQt4.QtGui.QLabel(u'Location suffix'),
                                                    export_object._location_suffix,
                                                    get_line()])


            self.create_widget_and_connect_widgets(widgets_layouts[1][1],
                                                   [export_object.paste_from_selection_button,
                                                    export_object.obsid_list,
                                                   PyQt4.QtGui.QLabel(u'Sub-location suffix'),
                                                   export_object._sublocation_suffix])

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
            export_object = ExportObject(connect)
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

        :param ms: midvattensettings
        :param stored_settings: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
        :return: stores a string like objname;attr1:value1;attr2:value2/objname2;attr3:value3... in midvatten settings
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

    @staticmethod
    def create_export_printlist(export_objects):
        """
        Creates a result list with FieldLogger format from selected obsids and parameters
        :return: a list with result lines to export to file
        """
        latlons = utils.get_latlon_for_all_obsids()

        parameters_inputtypes_hints = OrderedDict()

        subnames_locations = OrderedDict()
        subnames_lat_lon = OrderedDict()
        subnames_parameters = OrderedDict()

        for export_object in export_objects:
            parameter = export_object.final_parameter_name
            if not parameter:
                utils.MessagebarAndLog.critical(
                    bar_msg=u"Critical: Parameter " + parameter + u' error. See log message panel',
                    log_msg=u'Parameter name not given.')
                continue

            input_type = export_object.input_type
            if not input_type:
                utils.MessagebarAndLog.critical(
                    bar_msg=u"Critical: Parameter " + parameter + u' error. See log message panel',
                    log_msg=u'Input type not given.')
                continue

            if parameter in parameters_inputtypes_hints:
                utils.MessagebarAndLog.warning(bar_msg=u"Warning: Parameter " + parameter + u' error. See log message panel', log_msg=u'The parameter ' + parameter + u' already exists. Only the first occurence one will be written to file.')
                continue

            parameters_inputtypes_hints[parameter] = (input_type, export_object.hint)

            for location, subname, obsid in export_object.locations_sublocations_obsids:
                location_exists = subnames_locations.get(subname, None)
                if location != location_exists and location_exists is not None:
                    utils.MessagebarAndLog.warning(bar_msg=u'Warning: Subname ' + subname + u' error, see log message panel', log_msg=u'Subname ' + subname + u' already existed for location ' + location_exists + u' and is duplicated by location ' + location + u'. It will be skipped.')
                    continue

                if subname not in subnames_lat_lon:
                    lat, lon = latlons.get(obsid, [None, None])
                    if any([lat is None, not lat, lon is None, not lon]):
                        utils.MessagebarAndLog.critical(bar_msg=u'Critical: Obsid ' + u' did not have lat-lon coordinates. Check obs_points table')
                        continue
                    subnames_lat_lon[subname] = (returnunicode(lat), returnunicode(lon))
                subnames_locations[subname] = location
                subnames_parameters.setdefault(subname, []).append(parameter)

        comments = [par for par in parameters_inputtypes_hints.keys() if u'comment' in par]
        if not comments:
            utils.MessagebarAndLog.warning(bar_msg=u'Warning: No comment parameter found. Is it forgotten?')

        #Make a flat set of used parameters
        #used_parameters = [item for v in subnames_parameters.values() for item in v]
        #Remove unused parameters
        #parameters_inputtypes_hints = OrderedDict([(k, v) for k, v in parameters_inputtypes_hints.iteritems() if k in used_parameters])

        printlist = []
        printlist.append(u"FileVersion 1;" + str(len(parameters_inputtypes_hints)))
        printlist.append(u"NAME;INPUTTYPE;HINT")
        printlist.extend([u';'.join([returnunicode(par),
                                     returnunicode(i_h[0]) if i_h[0] else u'',
                                     returnunicode(i_h[1]) if i_h[1] else u''])
                          for par, i_h in parameters_inputtypes_hints.iteritems()])
        printlist.append(u'NAME;SUBNAME;LAT;LON;INPUTFIELD')

        printlist.extend([u';'.join([returnunicode(location),
                                     returnunicode(subname),
                                     returnunicode(subnames_lat_lon[subname][0]),
                                     returnunicode(subnames_lat_lon[subname][1]),
                                     u'|'.join(returnunicode(subnames_parameters[subname], keep_containers=True))])
                          for subname, location in sorted(subnames_locations.iteritems())])

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


class ExportObject(object):
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

        self._input_type = import_fieldlogger.default_combobox(editable=True)
        self._hint = PyQt4.QtGui.QLineEdit()
        self._location_suffix = PyQt4.QtGui.QLineEdit()
        self._sublocation_suffix = PyQt4.QtGui.QLineEdit()
        self._final_parameter_name = PyQt4.QtGui.QLineEdit()
        self.obsid_list = CopyPasteDeleteableQListWidget()
        self.paste_from_selection_button = PyQt4.QtGui.QPushButton(u'Paste obs_points selection')
        #------------------------------------------------------------------------
        self._input_type.addItems([u'numberDecimal|numberSigned', u'numberDecimal', u'numberSigned', u'text'])
        self._input_type.setToolTip(u'(mandatory)\nDecides the keyboard layout in the Fieldlogger app.')
        self._hint.setToolTip(u'(optional)\nHint given to the Fieldlogger user for the parameter. Ex: "depth to water"')
        #-------------------------------------------------------------------------------------

        self._location_suffix.setToolTip(u'(optional)\nFieldlogger NAME = obsid.SUFFIX\nUseful for separating projects or databases\nex: suffix = 1234 --> obsid.1234')
        self._sublocation_suffix.setToolTip(u'(optional)\nFieldlogger sub-location = obsid.SUFFIX\nUseful for separating parameters into groups for the user.\nParameters sharing the same sub-location will be shown together\n ex: suffix 1234.quality --> obsid.1234.quality')
        self._final_parameter_name.setToolTip(u'(mandatory)\nFieldlogger parameter name. Ex: parameter.unit')
        #-------------------------------------------------------------------------------------
        self.obsid_list.setSelectionMode(PyQt4.QtGui.QAbstractItemView.ExtendedSelection)
        connect(self.paste_from_selection_button, PyQt4.QtCore.SIGNAL("clicked()"),
                         lambda : self.obsid_list.paste_data(utils.get_selected_features_as_tuple('obs_points')))
        connect(self._location_suffix, PyQt4.QtCore.SIGNAL("textChanged(const QString&)"),
                         lambda : self.set_sublocation_suffix(self.location_suffix))



    def get_settings(self):
        settings = ((u'final_parameter_name', self.final_parameter_name),
                   (u'input_type', self.input_type),
                   (u'hint', self.hint),
                   (u'location_suffix', self.location_suffix),
                   (u'subname_suffix', self.subname_suffix))

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
        set_combobox(self._input_type, value)
        
    @property
    def hint(self):
        return utils.returnunicode(self._hint.text())

    @hint.setter
    def hint(self, value):
        self._hint.setText(utils.returnunicode(value))

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
        locations_sublocations_obsids = [(u'.'.join([returnunicode(obsid), returnunicode(self.location_suffix)]),
                                      u'.'.join([returnunicode(obsid), returnunicode(self.sublocation_suffix)]), returnunicode(obsid))
                                     for obsid in self.obsid_list.get_all_data()]
        return locations_sublocations_obsids
    

class CopyPasteDeleteableQListWidget(PyQt4.QtGui.QListWidget):
    """

    """
    def __init__(self, *args, **kwargs):
        super(CopyPasteDeleteableQListWidget, self).__init__(*args, **kwargs)

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
        
        
class ParameterUnitBrowser(object):
    def __init__(self, tables_columns_org, connect):

        tables_columns = {}
        for table, columns_tuple in tables_columns_org.iteritems():
            for column in columns_tuple:
                tables_columns.setdefault(table, []).append(column[1])

        self.layout = PyQt4.QtGui.QVBoxLayout()
        self.widget = PyQt4.QtGui.QWidget()
        self.widget.setLayout(self.layout)

        #Widget list
        self._parameter_table = import_fieldlogger.default_combobox(editable=False)
        self._parameter_columns = import_fieldlogger.default_combobox(editable=False)
        self._distinct_parameter = import_fieldlogger.default_combobox(editable=True)
        self._unit_table = import_fieldlogger.default_combobox(editable=False)
        self._unit_columns = import_fieldlogger.default_combobox(editable=False)
        self._distinct_unit = import_fieldlogger.default_combobox(editable=True)
        self._combined_name = PyQt4.QtGui.QLineEdit()

        # ------------------------------------------------------------------------------------
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
                     lambda: self._combined_name.setText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        connect(self._distinct_unit, PyQt4.QtCore.SIGNAL("editTextChanged(const QString&)"),
                     lambda: self._combined_name.setText(u'.'.join([self.distinct_parameter, self.distinct_unit]) if self.distinct_parameter and self.distinct_unit else None))
        #------------------------------------------------------------------------------------
        self._combined_name.setToolTip(u'Copy value using ctrl+v, ctrl+c to parameter name.')
        #------------------------------------------------------------------------------------
        #Add widgets to layout
        for widget in [PyQt4.QtGui.QLabel(u'Parameter and\nunit browser:'),
                       PyQt4.QtGui.QLabel(u'Parameter table'),
                       self._parameter_table,
                       PyQt4.QtGui.QLabel(u'Column'),
                       self._parameter_columns,
                       PyQt4.QtGui.QLabel(u'Name'),
                       self._distinct_parameter,
                       PyQt4.QtGui.QLabel(u'Unit table'),
                       self._unit_table,
                       PyQt4.QtGui.QLabel(u'Column'),
                       self._unit_columns,
                       PyQt4.QtGui.QLabel(u'Name'),
                       self._distinct_unit,
                       PyQt4.QtGui.QLabel(u'Combined name'),
                       self._combined_name]:
            self.layout.addWidget(widget)

        add_line(self.layout)

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
