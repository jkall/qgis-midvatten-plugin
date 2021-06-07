# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that prints column values from selected features.
                              -------------------
        begin                : 2011-10-18
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
import os
import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsVectorLayer


from midvatten.tools.utils import common_utils, gui_utils, midvatten_utils
from midvatten.tools.utils.common_utils import returnunicode as ru


selected_features_dialog = qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'selected_features.ui'))[0]

class ValuesFromSelectedFeaturesGui(qgis.PyQt.QtWidgets.QDialog, selected_features_dialog):
    def __init__(self, parent):
        self.iface = parent

        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        self.pushbutton_ok.clicked.connect(lambda : self.print_selected_features())

        self.pushbutton_cancel.clicked.connect(lambda : self.close())

        self.pushbutton_reload.clicked.connect(lambda: self.reload_combobox())

        self.activelayer = None
        self.selected_column = None

        self.reload_combobox()

        self.show()

    def reload_combobox(self):
        self.activelayer = common_utils.get_active_layer()
        if not isinstance(self.activelayer, QgsVectorLayer):
            common_utils.MessagebarAndLog.warning(bar_msg=ru(
                QCoreApplication.translate('ValuesFromSelectedFeaturesGui', 'Must select a vector layer!')))
            return None
        self.columns.clear()
        fields = [field.name() for field in self.activelayer.fields()]
        self.columns.addItems(sorted(fields))
        if self.selected_column is None or self.selected_column not in fields:
            self.selected_column = 'obsid'
        gui_utils.set_combobox(self.columns, self.selected_column, add_if_not_exists=False)

    def print_selected_features(self):
        """ Returns a list of obsid as unicode

            thelayer is an optional argument, if not given then activelayer is used
        """

        activelayer = common_utils.get_active_layer()
        if activelayer is not self.activelayer:
            self.reload_combobox()
            common_utils.MessagebarAndLog.warning(
                bar_msg=ru(QCoreApplication.translate('ValuesFromSelectedFeaturesGui', 'Column list reloaded. Select column and press Ok.')))
            return None

        self.selected_column = self.columns.currentText()

        selected = activelayer.selectedFeatures()
        idx = activelayer.dataProvider().fieldNameIndex(self.selected_column)
        if idx == -1:
            idx = activelayer.dataProvider().fieldNameIndex(self.selected_column.upper())  # backwards compatibility
        selected_values = [obs[idx] for obs in selected]  # value in column obsid is stored as unicode

        selected_feature_ids = [f.id() for f in selected]

        if not selected_values:
            common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('ValuesFromSelectedFeaturesGui',
                                                                              'No features selected!')))
        else:
            if self.unique_sorted_list_checkbox.isChecked():
                selected_values = sorted(set(selected_values))
            nr = len(selected_values)

            filter_string = '"{}" IN ({})'.format(self.selected_column,
                                                ', '.join(["'{}'".format(value.replace("'", "''")) if isinstance(value, str) else str(value)
                                                           for value in selected_values if value is not None]))

            nulls = [value for value in selected_values if value is None]
            if nulls:
                filter_string += ' or "{}" IS NULL'.format(self.selected_column)

            #filter_layer_checkbox
            bar_prefix = ''
            msg = ''
            if self.filter_layer_checkbox.isChecked():

                try:
                    activelayer.setSubsetString(filter_string)
                except Exception as e:
                    bar_prefix = 'Filtering failed! '
                    msg = 'Filtering failed, msg: ' + str(e)

            if self.copy_to_clipboard_checkbox.isChecked():
                self.copy_to_clipboard(filter_string)

            activelayer.selectByIds(selected_feature_ids)

            common_utils.MessagebarAndLog.info(bar_msg=ru(
                QCoreApplication.translate('ValuesFromSelectedFeaturesGui', bar_prefix +
                                           'List of %s selected %s written to log')) % (str(nr), self.selected_column),
                                                           log_msg=filter_string + '\n' + msg)

            self.close()

    def copy_to_clipboard(self, astring):
        clipboard = QApplication.clipboard()
        clipboard.setText(astring)


