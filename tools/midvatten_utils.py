# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the place to store some global (for the Midvatten plugin) utility functions.
 NOTE - if using this file, it has to be imported by midvatten.py
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
from __future__ import print_function
from __future__ import absolute_import

from future import standard_library

from qgis._core import QgsVectorLayer

standard_library.install_aliases()
from builtins import filter
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
import qgis.PyQt
import ast
import shutil
import glob
import io
import codecs
import copy
import csv
import datetime
import difflib
import io
import re
import locale
import math
import os
import qgis.utils
import tempfile
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWebKitWidgets import QWebView
from qgis.PyQt import QtCore, QtGui, uic, QtWidgets
from collections import OrderedDict
from contextlib import contextmanager
from functools import wraps
from operator import itemgetter
from qgis.core import QgsLogger, QgsMapLayer, QgsProject, QgsProject, Qgis, QgsApplication, QgsMapLayer
from qgis.gui import QgsMessageBar, QtCore
from definitions.db_defs import latest_database_version

import numpy as np
from qgis.PyQt.QtCore import QCoreApplication

try:
    import pandas as pd
except:
    pandas_on = False
else:
    pandas_on = True

from matplotlib.dates import num2date

import db_utils

not_found_dialog = uic.loadUiType(os.path.join(os.path.dirname(__file__), '..', 'ui', 'not_found_gui.ui'))[0]


class MessagebarAndLog(object):
    """ Class that sends logmessages to messageBar and or to QgsMessageLog

    Usage: MessagebarAndLog.info(bar_msg='a', log_msg='b', duration=10,
    messagebar_level=Qgis.Info, log_level=Qgis.Info,
    button=True)

    :param bar_msg: A short msg displayed in messagebar and log.
    :param log_msg: A long msg displayed only in log.
    :param messagebar_level: The message level of the messageBar.
    :param log_level: The message level of the QgsMessageLog  { Info = 0, Warning = 1, Critical = 2 }.
    :param duration: The duration of the messageBar.
    :param button: (True/False, default True) If False, the button to the
                   QgsMessageLog does not appear at the messageBar.

    :return:

    The message bar_msg is written to both messageBar and QgsMessageLog
    The log_msg is only written to QgsMessageLog

    * If the user only supplies bar_msg, a messageBar popup appears without button to message log.
    * If the user supplies only log_msg, the message is only written to message log.
    * If the user supplies both, a messageBar with bar_msg appears with a button to open message log.
      In the message log, the bar_msg and log_msg is written.

      Activate writing of log messages to file by settings :
      qgis Settings > Options > System > Environment > mark Use custom variables > Click Add >
      enter "QGIS_LOG_FILE" in the field Variable and a filename as Value.
    """
    def __init__(self):
        pass

    @staticmethod
    def log(bar_msg=None, log_msg=None, duration=10, messagebar_level=Qgis.Info, log_level=Qgis.Info, button=True):
        if qgis.utils.iface is None:
            return None
        if bar_msg is not None:
            widget = qgis.utils.iface.messageBar().createMessage(returnunicode(bar_msg))
            log_button = QtWidgets.QPushButton(QCoreApplication.translate('MessagebarAndLog', "View message log"), pressed=show_message_log)
            if log_msg is not None and button:
                widget.layout().addWidget(log_button)
            qgis.utils.iface.messageBar().pushWidget(widget, level=messagebar_level, duration=duration)
            #This part can be used to push message to an additional messagebar, but dialogs closes after the timer
            if hasattr(qgis.utils.iface, 'optional_bar'):
                try:
                    qgis.utils.iface.optional_bar.pushWidget(widget, level=messagebar_level, duration=duration)
                except:
                    pass
        QgsApplication.messageLog().logMessage(returnunicode(bar_msg), 'Midvatten', level=log_level)
        if log_msg is not None:
            QgsApplication.messageLog().logMessage(returnunicode(log_msg), 'Midvatten', level=log_level)

    @staticmethod
    def info(bar_msg=None, log_msg=None, duration=10, button=True, optional_bar=False):
        MessagebarAndLog.log(bar_msg, log_msg, duration, Qgis.Info, Qgis.Info, button)

    @staticmethod
    def warning(bar_msg=None, log_msg=None, duration=10, button=True, optional_bar=False):
        MessagebarAndLog.log(bar_msg, log_msg, duration, Qgis.Warning, Qgis.Warning, button)

    @staticmethod
    def critical(bar_msg=None, log_msg=None, duration=10, button=True, optional_bar=False):
        MessagebarAndLog.log(bar_msg, log_msg, duration, Qgis.Critical, Qgis.Critical, button)


def write_qgs_log_to_file(message, tag, level):
    logfile = QgsLogger.logFile()
    if logfile is not None:
        QgsLogger.logMessageToFile('{}: {}({}): {} '.format('%s'%(returnunicode(get_date_time())), returnunicode(tag), returnunicode(level), '%s'%(returnunicode(message))))


class Askuser(QtWidgets.QDialog):
    def __init__(self, question="YesNo", msg = '', dialogtitle=QCoreApplication.translate('askuser', 'User input needed'), parent=None):
        self.result = ''
        if question == 'YesNo':         #  Yes/No dialog
            reply = QtWidgets.QMessageBox.information(parent, dialogtitle, msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
            if reply==QtWidgets.QMessageBox.Yes:
                self.result = 1 #1 = "yes"
            else:
                self.result = 0  #0="no"
        elif question == 'AllSelected': # All or Selected Dialog
            btnAll = QtWidgets.QPushButton(QCoreApplication.translate('askuser', "All"))   # = "0"
            btnSelected = QtWidgets.QPushButton(QCoreApplication.translate('askuser', "Selected"))     # = "1"
            #btnAll.clicked.connect(lambda x: self.DoForAll())
            #btnSelected.clicked.connect(lambda x: self.DoForSelected())
            msgBox = QtWidgets.QMessageBox(parent)
            msgBox.setText(msg)
            msgBox.setWindowTitle(dialogtitle)
            #msgBox.setWindowModality(Qt.ApplicationModal)
            msgBox.addButton(btnAll, QtWidgets.QMessageBox.ActionRole)
            msgBox.addButton(btnSelected, QtWidgets.QMessageBox.ActionRole)
            msgBox.addButton(QtWidgets.QMessageBox.Cancel)
            reply = msgBox.exec_()
            self.result = reply  # ALL=0, SELECTED=1
        elif question == 'DateShift':
            supported_units = ['microseconds', 'milliseconds', 'seconds', 'minutes', 'hours', 'days', 'weeks']
            while True:
                answer = str(qgis.PyQt.QtWidgets.QInputDialog.getText(None, QCoreApplication.translate('askuser', "User input needed"), returnunicode(QCoreApplication.translate('askuser', "Give needed adjustment of date/time for the data.\nSupported format: +- X <resolution>\nEx: 1 hours, -1 hours, -1 days\nSupported units:\n%s"))%', '.join(supported_units), qgis.PyQt.QtWidgets.QLineEdit.Normal, '0 hours')[0])
                if not answer:
                    self.result = 'cancel'
                    break
                else:
                    adjustment_unit = answer.split()
                    if len(adjustment_unit) == 2:
                        if adjustment_unit[1] in supported_units:
                            self.result = adjustment_unit
                            break
                        else:
                            pop_up_info(returnunicode(QCoreApplication.translate('askuser', "Failure:\nOnly support resolutions\n%s"))%', '.join(supported_units))
                    else:
                        pop_up_info(QCoreApplication.translate('askuser', "Failure:\nMust write time resolution also.\n"))


class NotFoundQuestion(QtWidgets.QDialog, not_found_dialog):
    window_position = qgis.PyQt.QtCore.QPoint(500, 150)
    def __init__(self, dialogtitle='Warning', msg='', existing_list=None, default_value='', parent=None, button_names=['Ignore', 'Cancel', 'Ok'], combobox_label='Similar values found in db (choose or edit):', reuse_header_list=None, reuse_column='', ignore_checkbox=False):
        QtWidgets.QDialog.__init__(self, parent)
        self.answer = None
        self.setupUi(self)
        self.setWindowTitle(dialogtitle)
        self.label.setText(msg)
        self.label.setTextInteractionFlags(qgis.PyQt.QtCore.Qt.TextSelectableByMouse)
        self.comboBox.addItem(default_value)
        self.label_2.setText(combobox_label)
        if existing_list is not None:
            for existing in existing_list:
                self.comboBox.addItem(existing)

        if ignore_checkbox:
            self.ignore_checkbox = qgis.PyQt.QtWidgets.QCheckBox(QCoreApplication.translate('NotFoundQuestion', 'Ignore database missmatch'), self)
            self.ignore_checkbox.setToolTip(QCoreApplication.translate('NotFoundQuestion', 'Ignore database missmatch and try to import anyway'))
            self.ignore_layout.addWidget(self.ignore_checkbox)
        for idx, button_name in enumerate(button_names):
            button = QtWidgets.QPushButton(button_name)
            button.setObjectName(button_name.lower())
            self.buttonBox.addButton(button, QtWidgets.QDialogButtonBox.ActionRole)
            button.clicked.connect(lambda x: self.button_clicked())

        self.reuse_label = qgis.PyQt.QtWidgets.QLabel(QCoreApplication.translate('NotFoundQuestion', 'Reuse answer for all identical'))
        self._reuse_column = qgis.PyQt.QtWidgets.QComboBox()
        self._reuse_column.addItem('')
        if isinstance(reuse_header_list, (list, tuple)):
            self.reuse_layout.addWidget(self.reuse_label)
            self.reuse_layout.addWidget(self._reuse_column)
            self.reuse_layout.addStretch()
            self._reuse_column.addItems(reuse_header_list)
            self.reuse_column_temp = reuse_column

        _label = QtWidgets.QLabel(msg)
        if 140 < _label.height() <= 300:
            self.setGeometry(NotFoundQuestion.window_position.x(), NotFoundQuestion.window_position.y(), self.width(), 415)
        elif _label.height() > 300:
            self.setGeometry(NotFoundQuestion.window_position.x(), NotFoundQuestion.window_position.y(), self.width(), 600)

        self.exec_()

    @property
    def reuse_column_temp(self, value):
        index = self._reuse_column.findText(returnunicode(value))
        if index != -1:
            self._reuse_column.setCurrentIndex(index)

    @reuse_column_temp.setter
    def reuse_column_temp(self, value):
        index = self._reuse_column.findText(returnunicode(value))
        if index != -1:
            self._reuse_column.setCurrentIndex(index)

    def button_clicked(self):
        button = self.sender()
        button_object_name = button.objectName()
        self.set_answer_and_value(button_object_name)
        self.close()

    def set_answer_and_value(self, answer):
        self.answer = answer
        self.value = returnunicode(self.comboBox.currentText())
        self.reuse_column = self._reuse_column.currentText()

    def closeEvent(self, event):
        if self.answer is None:
            self.set_answer_and_value('cancel')
        NotFoundQuestion.window_position = self.geometry().topLeft()
        super(NotFoundQuestion, self).closeEvent(event)

        #self.close()


class HtmlDialog(QtWidgets.QDialog):

    def __init__(self, title='', filepath=''):
        QtWidgets.QDialog.__init__(self)
        self.setModal(True)
        self.setupUi(title, filepath)

    def setupUi(self, title, filepath):
        self.resize(600, 500)
        self.webView = QWebView()
        self.setWindowTitle(title)
        self.verticalLayout= QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.addWidget(self.webView)
        self.closeButton = QtWidgets.QPushButton()
        self.closeButton.setText(QCoreApplication.translate('HtmlDialog', "Close"))
        self.closeButton.setMaximumWidth(150)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.addStretch(1000)
        self.horizontalLayout.addWidget(self.closeButton)
        self.closeButton.clicked.connect(lambda x: self.closeWindow())
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setLayout(self.verticalLayout)
        url = QtCore.QUrl(filepath)
        self.webView.load(url)

    def closeWindow(self):
        self.close()


def show_message_log(pop_error=False):
    """
    Source: qgis code
     """
    if pop_error:
        qgis.utils.iface.messageBar().popWidget()

    qgis.utils.iface.openMessageLog()


def ask_user_about_stopping(question):
    """
    Asks the user a question and returns 'failed' or 'continue' as yes or no
    :param question: A string to write at the dialog box.
    :return: The string 'failed' or 'continue' as yes/no
    """
    answer = Askuser("YesNo", question)
    if answer.result:
        return 'cancel'
    else:
        return 'ignore'


def create_dict_from_db_2_cols(params):#params are (col1=keys,col2=values,db-table)
    sqlstring = r"""select %s, %s from %s"""%(params)
    connection_ok, list_of_tuples= db_utils.sql_load_fr_db(sqlstring)

    if not connection_ok:
        textstring = returnunicode(QCoreApplication.translate('create_dict_from_db_2_cols', """Cannot create dictionary from columns %s and %s in table %s!"""))%(params)#col1,col2,table)
        #qgis.utils.iface.messageBar().pushMessage("Error",textstring, 2,duration=10)
        MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('create_dict_from_db_2_cols', 'Some sql failure, see log for additional info.'), log_msg=textstring, duration=4,button=True)
        return False, {'':''}

    adict = dict([(k, v) for k, v in list_of_tuples])
    return True, adict


def find_layer(layer_name):
    found_layers = [layer for name, layer in QgsProject.instance().mapLayers().items()
                    if layer.name() == layer_name]

    if len(found_layers) == 0:
        raise UsageError(returnunicode(QCoreApplication.translate('find_layer', 'The layer %s was not found!'))%layer_name)
    elif len(found_layers) > 1:
        raise UsageError(returnunicode(QCoreApplication.translate('find_layer', 'Found %s layers with the name "%s". There can be only one!'))%(str(len(found_layers)), layer_name))
    else:
        return found_layers[0]


def get_all_obsids(table='obs_points'):
    """ Returns all obsids from obs_points
    :return: All obsids from obs_points
    """
    obsids = []
    connection_ok, result = db_utils.sql_load_fr_db('''SELECT DISTINCT obsid FROM %s ORDER BY OBSID''' % table)
    if connection_ok:
        obsids = [row[0] for row in result]
    return obsids


def get_date_time():
    """returns date and time as a string in a pre-formatted format"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_selected_features_as_tuple(layer_name=None, column_name=None):
    """ Returns all selected features from layername

        Returns a tuple of obsids stored as unicode
    """
    if layer_name is not None:
        if isinstance(layer_name, str):
            obs_points_layer = find_layer(layer_name)
        elif isinstance(layer_name, QgsMapLayer):
            obs_points_layer = layer_name
        else:
            MessagebarAndLog.info(log_msg=QCoreApplication.translate('get_selected_features_as_tuple', 'Programming error: The layername "%s" was not str or QgsMapLayer!')%str(layer_name))
            obs_points_layer = None

        if obs_points_layer is None:
            return tuple()
        if column_name is not None:
            selected_obs_points = getselectedobjectnames(layer_name=obs_points_layer, column_name=column_name)
        else:
            selected_obs_points = getselectedobjectnames(layer_name=obs_points_layer)
    else:
        if column_name is not None:
            selected_obs_points = getselectedobjectnames(column_name=column_name)
        else:
            selected_obs_points = getselectedobjectnames()
    #module midv_exporting depends on obsid being a tuple
    #we cannot send unicode as string to sql because it would include the u' so str() is used
    obsidtuple = tuple([returnunicode(id) for id in selected_obs_points])
    return obsidtuple


def getselectedobjectnames(layer_name='default', column_name='obsid'):
    """ Returns a list of obsid as unicode

        thelayer is an optional argument, if not given then activelayer is used
    """
    if layer_name == 'default':
        layer_name = get_active_layer()
    if not layer_name:
        return []
    selectedobs = layer_name.selectedFeatures()
    kolumnindex = layer_name.dataProvider().fieldNameIndex(column_name)  #OGR data provier is used to find index for column named 'obsid'
    if kolumnindex == -1:
        kolumnindex = layer_name.dataProvider().fieldNameIndex(column_name.upper())  #backwards compatibility
    observations = [obs[kolumnindex] for obs in selectedobs] # value in column obsid is stored as unicode
    return observations


def getQgisVectorLayers():
    """Return list of all valid QgsVectorLayer in QgsProject"""
    layermap = QgsProject.instance().mapLayers()
    layerlist = []
    for name, layer in layermap.items():
        if layer.isValid() and layer.type() == QgsMapLayer.VectorLayer:
                layerlist.append( layer )
    return layerlist


def isfloat(str):
    try: float(str)
    except ValueError: return False
    return True


def isinteger(str):
    try: int(str)
    except ValueError: return False
    return True


def isdate(str):
    result = False
    formats = ['%Y-%m-%d', '%Y-%m-%d %H', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']
    for fmt in formats:
        try:
            time.strptime(str, fmt)
            result = True
        except ValueError:
            pass
    return result


def null_2_empty_string(input_string):
    return(input_string.replace('NULL', '').replace('null', ''))


def pop_up_info(msg='',title=QCoreApplication.translate('pop_up_info', 'Information'),parent=None):
    """Display an info message via Qt box"""
    QtWidgets.QMessageBox.information(parent, title, '%s' % (msg))


def return_lower_ascii_string(textstring):
    def onlyascii(char):
        if ord(char) < 48 or ord(char) > 127:
            return ''
        else:
            return char
    filtered_string= ''.join(list(filter(onlyascii, textstring)))
    filtered_string = filtered_string.lower()
    return filtered_string


def returnunicode(anything, keep_containers=False): #takes an input and tries to return it as unicode
    r"""

    >>> returnunicode('b')
    'b'
    >>> returnunicode(int(1))
    '1'
    >>> returnunicode(None)
    ''
    >>> returnunicode([])
    '[]'
    >>> returnunicode(['a', 'b'])
    "['a', 'b']"
    >>> returnunicode(['a', 'b'])
    "['a', 'b']"
    >>> returnunicode(['ä', 'ö'])
    "['\\xe4', '\\xf6']"
    >>> returnunicode(float(1))
    '1.0'
    >>> returnunicode(None)
    ''
    >>> returnunicode([(1, ), {2: 'a'}], True)
    [('1',), {'2': 'a'}]

    :param anything: just about anything
    :return: hopefully a unicode converted anything
    """
    if isinstance(anything, str):
        return anything
    elif anything is None:
        decoded = ''
    elif isinstance(anything, (list, tuple, dict, OrderedDict)):
        if isinstance(anything, list):
            decoded = [returnunicode(x, keep_containers) for x in anything]
        elif isinstance(anything, tuple):
            decoded = tuple([returnunicode(x, keep_containers) for x in anything])
        elif isinstance(anything, dict):
            decoded = dict([(returnunicode(k, keep_containers), returnunicode(v, keep_containers)) for k, v in anything.items()])
        elif isinstance(anything, OrderedDict):
            decoded = OrderedDict([(returnunicode(k, keep_containers), returnunicode(v, keep_containers)) for k, v in anything.items()])
        if not keep_containers:
            decoded = str(decoded)
    # This is not optimal, but needed for tests where nosetests stand alone PyQt4 instead of QGis PyQt4.
    elif str(type(anything)) in ("<class 'PyQt4.QtCore.QVariant'>", "<class 'PyQt5.QtCore.QVariant'>"):
        if anything.isNull():
            decoded = ''
        else:
            decoded = returnunicode(anything.toString())
    # This is not optimal, but needed for tests where nosetests stand alone PyQt4 instead of QGis PyQt4.
    elif str(type(anything)) in ("<class 'PyQt4.QtCore.QString'>", "<class 'PyQt5.QtCore.QString'>"):
        decoded = returnunicode(str(anything.toUtf8(), 'utf-8'))
    # This is not optimal, but needed for tests where nosetests stand alone PyQt4 instead of QGis PyQt4.
    elif str(type(anything)) in ("<class 'PyQt4.QtCore.QPyNullVariant'>", "<class 'PyQt5.QtCore.QPyNullVariant'>"):
        decoded = ''
    else:
        decoded = str(anything)

    if isinstance(decoded, bytes):
        for charset in ['ascii', 'utf-8', 'utf-16', 'cp1252', 'iso-8859-1', 'ascii']:
            try:
                decoded = anything.decode(charset)
            except UnicodeEncodeError:
                continue
            except UnicodeDecodeError:
                continue
            else:
                break
        else:
            decoded = str(QCoreApplication.translate('returnunicode', 'data type unknown, check database'))

    return decoded


def selection_check(layer='', selectedfeatures=0):  #defaultvalue selectedfeatures=0 is for a check if any features are selected at all, the number is unimportant
    if layer.dataProvider().fieldNameIndex('obsid')  > -1 or layer.dataProvider().fieldNameIndex('OBSID')  > -1: # 'OBSID' to get backwards compatibility
        if selectedfeatures == 0 and layer.selectedFeatureCount() > 0:
            return 'ok'
        elif not(selectedfeatures==0) and layer.selectedFeatureCount()==selectedfeatures:
            return 'ok'
        elif selectedfeatures == 0 and not(layer.selectedFeatureCount() > 0):
            MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('selection_check', 'Error, select at least one object in the qgis layer!'))
        else:
            MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('selection_check', '"""Error, select exactly %s object in the qgis layer!'))%str(selectedfeatures))
    else:
        pop_up_info(QCoreApplication.translate('selection_check', "Select a qgis layer that has a field obsid!"))


def strat_selection_check(layer=''):
    if layer.dataProvider().fieldNameIndex('h_gs')  > -1 or layer.dataProvider().fieldNameIndex('h_toc')  > -1  or layer.dataProvider().fieldNameIndex('SURF_LVL')  > -1: # SURF_LVL to enable backwards compatibility
            return 'ok'
    else:
        MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('strat_selection_check', 'Error, select a qgis layer with field h_gs!')))


def unicode_2_utf8(anything): #takes an unicode and tries to return it as utf8
    r"""

    :param anything: just about anything
    :return: hopefully a utf8 converted anything
    """
    #anything = returnunicode(anything)
    text = None
    try:
        if type(anything) == type(None):
            text = ('').encode('utf-8')
        elif isinstance(anything, str):
            text = anything.encode('utf-8')
        elif isinstance(anything, list):
            text = ([unicode_2_utf8(x) for x in anything])
        elif isinstance(anything, tuple):
            text = (tuple([unicode_2_utf8(x) for x in anything]))
        elif isinstance(anything, float):
            text = anything.encode('utf-8')
        elif isinstance(anything, int):
            text = anything.encode('utf-8')
        elif isinstance(anything, dict):
            text = (dict([(unicode_2_utf8(k), unicode_2_utf8(v)) for k, v in anything.items()]))
        elif isinstance(anything, str):
            text = anything
        elif isinstance(anything, bool):
            text = anything.encode('utf-8')
    except:
        pass

    if text is None:
        text = returnunicode(QCoreApplication.translate('unicode_2_utf8', 'data type unknown, check database')).encode('utf-8')
    return text


def verify_msettings_loaded_and_layer_edit_mode(iface, mset, allcritical_layers=(''), only_error_if_editing_enabled=True):
    if isinstance(allcritical_layers, str):
        allcritical_layers = (allcritical_layers, )

    errorsignal = 0
    if not mset.settingsareloaded:
        mset.loadSettings()
    for layername in allcritical_layers:
        if not layername:
            continue
        try:
            layerexists = find_layer(str(layername))
        except UsageError:
            if not only_error_if_editing_enabled:
                errorsignal += 1
                MessagebarAndLog.warning(bar_msg=returnunicode(
                    QCoreApplication.translate('verify_msettings_loaded_and_layer_edit_mode',
                                               "Error layer %s is required but missing!")) % str(
                    layername))
                errorsignal += 1
        else:
            if layerexists:
                if layerexists.isEditable():
                    MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('verify_msettings_loaded_and_layer_edit_mode', "Error %s is currently in editing mode.\nPlease exit this mode before proceeding with this operation."))%str(layerexists.name()))
                    #pop_up_info("Layer " + str(layerexists.name()) + " is currently in editing mode.\nPlease exit this mode before proceeding with this operation.", "Warning")
                    errorsignal += 1

    if not mset.settingsdict['database']:
        MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('verify_msettings_loaded_and_layer_edit_mode', "Error, No database found. Please check your Midvatten Settings. Reset if needed."))
        errorsignal += 1
    else:
        try:
            connection_ok = db_utils.check_connection_ok()
        except db_utils.DatabaseLockedError:
            MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('verify_msettings_loaded_and_layer_edit_mode', 'Databas is already in use'))
            errorsignal += 1
        else:
            if not connection_ok:
                MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('verify_msettings_loaded_and_layer_edit_mode', "Error, The selected database doesn't exist. Please check your Midvatten Settings and database location. Reset if needed."))
                errorsignal += 1

    return errorsignal


def verify_layer_selection(errorsignal,selectedfeatures=0):
    layer = get_active_layer()
    if layer:
        if not(selection_check(layer) == 'ok'):
            errorsignal += 1
            if selectedfeatures==0:
                MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('verify_layer_selection', 'Error, you have to select some features!'))
            else:
                MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('verify_layer_selection', 'Error, you have to select exactly %s features!'))%str(selectedfeatures))
    else:
        MessagebarAndLog.critical(bar_msg=QCoreApplication.translate('verify_layer_selection', 'Error, you have to select a relevant layer!'))
        errorsignal += 1
    return errorsignal


def get_active_layer():
    iface = qgis.utils.iface
    if iface is not None:
        return iface.activeLayer()
    else:
        return False


def verify_this_layer_selected_and_not_in_edit_mode(errorsignal,layername):
    layer = get_active_layer()
    if not layer:#check there is actually a layer selected
        errorsignal += 1
        MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('verify_this_layer_selected_and_not_in_edit_mode', 'Error, you have to select/activate %s layer!'))%layername)
    elif layer.isEditable():
        errorsignal += 1
        MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('verify_this_layer_selected_and_not_in_edit_mode', 'Error, the selected layer is currently in editing mode. Please exit this mode before updating coordinates.')))
    elif not(layer.name() == layername):
        errorsignal += 1
        MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('verify_this_layer_selected_and_not_in_edit_mode', 'Error, you have to select/activate %s layer!'))%layername)
    return errorsignal


@contextmanager
def tempinput(data, charset='UTF-8'):
    """ Creates and yields a temporary file from data

        The file can't be deleted in windows for some strange reason.
        There shouldn't be so many temporary files using this function
        for it to be a major problem though. Relying on windows temp file
        cleanup instead.
    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    unicode_data = returnunicode(data)
    encoded_data = unicode_data.encode(charset)
    temp.write(encoded_data)
    temp.close()
    yield temp.name
    #os.unlink(temp.name) #TODO: This results in an error: WindowsError: [Error 32] Det går inte att komma åt filen eftersom den används av en annan process: 'c:\\users\\dator\\appdata\\local\\temp\\tmpxvcfna.csv'


def find_nearest_date_from_event(event):
    """ Returns the nearest date from a picked list event artist from mouse click

        The x-axis of the artist is assumed to be a date as float or int.
        The found date float is then converted into datetime and returned.
        
        // This way of getting the date is now replaced with the MUCH simpler event.artist.get_xdata()[event.ind[0]]
    """
    line_nodes = np.array(list(zip(event.artist.get_xdata(), event.artist.get_ydata())))
    xy_click = np.array((event.mouseevent.xdata, event.mouseevent.ydata))
    nearest_xy = find_nearest_using_pythagoras(xy_click, line_nodes)
    nearest_date = num2date(nearest_xy[0])
    return nearest_date


def find_nearest_using_pythagoras(xy_point, xy_array):
    """ Finds the point in xy_array that is nearest xy_point

        xy_point: tuple with two floats representing x and y
        xy_array: list of tuples with floats representing x and y points

        The search is using pythagoras theorem.
        If the search becomes very slow when the xy_array gets long,
        it could probably we rewritten using numpy methods.

        >>> find_nearest_using_pythagoras((1, 2), ((4, 5), (3, 5), (-1, 1)))
        (-1, 1)
        >>> find_nearest_using_pythagoras((1, None), (1, 2), ((4, 5), (3, 5), (-1, 1)))
        (-1, 1)
    """
    xy_array = xy_array[~np.isnan(xy_array).any(axis=1)]
    distances = [math.sqrt((float(xy_point[0]) - float(xy_array[x][0]))**2 + (float(xy_point[1]) - float(xy_array[x][1]))**2) for x in range(len(xy_array))]
    min_index = distances.index(min(distances))
    return xy_array[min_index]


def ts_gen(ts):
    """ A generator that supplies one tuple from a list of tuples at a time

        ts: a list of tuples where the tuple contains two positions.

        Usage:
        a = ts_gen(ts)
        b = next(a)

        >>> for x in ts_gen(((1, 2), ('a', 'b'))): print x
        (1, 2)
        ('a', 'b')
    """
    for idx in range(len(ts)):
        yield (ts[idx][0], ts[idx][1])


def calc_mean_diff(coupled_vals):
    """ Calculates the mean difference for all value couples in a list of tuples

        Nan-values are excluded from the mean.

    >>> calc_mean_diff(([5, 2] , [8, 1]))
    5.0
    """
    return np.mean([float(m) - float(l) for m, l in coupled_vals if not math.isnan(m) or math.isnan(l)])


def get_latlon_for_all_obsids():
    """
    Returns lat, lon for all obsids
    :return: A dict of tuples with like {'obsid': (lat, lon)} for all obsids in obs_points
    """
    latlon_dict = db_utils.get_sql_result_as_dict('SELECT obsid, Y(Transform(geometry, 4326)) as lat, X(Transform(geometry, 4326)) as lon from obs_points')[1]
    latlon_dict = dict([(obsid, lat_lon[0]) for obsid, lat_lon in latlon_dict.items()])
    return latlon_dict


def get_last_used_flow_instruments():
    """ Returns flow instrumentids
    :return: A dict like {obsid: (flowtype, instrumentid, last date used for obsid)
    """
    return db_utils.get_sql_result_as_dict('SELECT obsid, flowtype, instrumentid, max(date_time) FROM w_flow GROUP BY obsid, flowtype, instrumentid')


def get_last_logger_dates():
    ok_or_not, obsid_last_imported_dates = db_utils.get_sql_result_as_dict('select obsid, max(date_time) from w_levels_logger group by obsid')
    return returnunicode(obsid_last_imported_dates, True)


def get_quality_instruments():
    """
    Returns quality instrumentids
    :return: A tuple with instrument ids from w_qual_field
    """
    sql = 'SELECT distinct instrument from w_qual_field'
    sql_result = db_utils.sql_load_fr_db(sql)
    connection_ok, result_list = sql_result

    if not connection_ok:
        MessagebarAndLog.critical(bar_msg=sql_failed_msg(), log_msg=returnunicode(QCoreApplication.translate('get_quality_instruments', 'Failed to get quality instruments from sql\n%s'))%sql)
        return False, tuple()

    return True, returnunicode([x[0] for x in result_list], True)


def lstrip(word, from_string):
    """
    Strips word from the start of from_string
    :param word: a string to strip
    :param from_string: the string to strip from
    :return: the new string or the old string if word was not at the beginning of from_string.

    >>> lstrip('123', '123abc')
    'abc'
    >>> lstrip('1234', '123abc')
    '123abc'
    """
    new_word = from_string
    if from_string.startswith(word):
        new_word = from_string[len(word):]
    return new_word


def rstrip(word, from_string):
    """
    Strips word from the end of from_string
    :param word: a string to strip
    :param from_string: the string to strip from
    :return: the new string or the old string if word was not at the end of from_string.

    >>> rstrip('abc', '123abc')
    '123'
    >>> rstrip('abcd', '123abc')
    '123abc'
    """
    new_word = from_string
    if from_string.endswith(word):
        new_word = from_string[0:-len(word)]
    return new_word

def select_files(only_one_file=True, extension="csv (*.csv)"):
    """Asks users to select file(s)"""
    try:
        dir = os.path.dirname(db_utils.get_spatialite_db_path_from_dbsettings_string(QgsProject.instance().readEntry("Midvatten","database")[0]))
    except Exception as e:
        MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('select_files', 'Getting directory for select_files failed with msg %s'))%str(e))
        dir = ''

    if only_one_file:
        csvpath = [QtWidgets.QFileDialog.getOpenFileName(parent=None, caption=QCoreApplication.translate('select_files', "Select file"), directory=dir, filter=extension)[0]]
    else:
        csvpath = QtWidgets.QFileDialog.getOpenFileNames(parent=None, caption=QCoreApplication.translate('select_files', "Select files"), directory=dir, filter=extension)[0]
    csvpath = [returnunicode(p) for p in csvpath if p]
    if not csvpath:
        MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('select_files', 'No file selected!')))
        raise UserInterruptError()
    return csvpath


def ask_for_charset(default_charset=None, msg=None):
    try:#MacOSX fix2
        localencoding = getcurrentlocale()[1]
        if default_charset is None:
            if msg is None:
                msg = returnunicode(QCoreApplication.translate('ask_for_charset',"Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer %s is default."))%localencoding
            charsetchoosen = QtWidgets.QInputDialog.getText(None, QCoreApplication.translate('ask_for_charset',"Set charset encoding"), msg,QtWidgets.QLineEdit.Normal,getcurrentlocale()[1])[0]
        else:
            if msg is None:
                msg = QCoreApplication.translate('ask_for_charset', "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.")
            charsetchoosen = QtWidgets.QInputDialog.getText(None, QCoreApplication.translate('ask_for_charset',"Set charset encoding"), msg, QtWidgets.QLineEdit.Normal, default_charset)[0]
    except Exception as e:
        if default_charset is None:
            default_charset = 'utf-8'
        if msg is None:
            msg = QCoreApplication.translate('ask_for_charset', "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.")
        charsetchoosen = QtWidgets.QInputDialog.getText(None, QCoreApplication.translate('ask_for_charset',"Set charset encoding"), msg, QtWidgets.QLineEdit.Normal, default_charset)[0]

    return str(charsetchoosen)


def ask_for_export_crs(default_crs=''):
    return str(QtWidgets.QInputDialog.getText(None, QCoreApplication.translate('ask_for_export_crs',"Set export crs"), QCoreApplication.translate('ask_for_export_crs', "Give the crs for the exported database.\n"),QtWidgets.QLineEdit.Normal,str(default_crs))[0])


def lists_to_string(alist_of_lists, quote=False):
    r'''

        The long Version:
        reslist = []
        for row in alist_of_lists:
            if isinstance(row, (list, tuple)):
                innerlist = []
                for col in row:
                    if quote:
                        if all(['"' in returnunicode(col), '""' not in returnunicode(col)]):
                            innerword = returnunicode(col).replace('"', '""')
                        else:
                            innerword = returnunicode(col)
                        try:
                            innerlist.append('"{}"'.format(innerword))
                        except UnicodeDecodeError:
                            print(str(innerword))
                            raise Exception
                    else:
                        innerlist.append(returnunicode(col))
                reslist.append(';'.join(innerlist))
            else:
                reslist.append(returnunicode(row))

        return_string = '\n'.join(reslist)


    :param alist_of_lists:
    :return: A string with '\n' separating rows and ; separating columns.

    >>> lists_to_string([1])
    '1'
    >>> lists_to_string([('a', 'b'), (1, 2)])
    'a;b\n1;2'
    >>> lists_to_string([('a', 'b'), (1, 2)], quote=True)
    '"a";"b"\n"1";"2"'
    >>> lists_to_string([('"a"', 'b'), (1, 2)], quote=False)
    '"a";b\n1;2'
    >>> lists_to_string([('"a"', 'b'), (1, 2)], quote=True)
    '"""a""";"b"\n"1";"2"'
    '''
    if isinstance(alist_of_lists, (list, tuple)):

        return_string = '\n'.join(
            [';'.join(['"{}"'.format(returnunicode(col).replace('"', '""')
                                       if all(['"' in returnunicode(col),
                                               '""' not in returnunicode(col)])
                                       else returnunicode(col))
                        if quote
                        else
                        returnunicode(col) for col in row])
             if isinstance(row, (list, tuple))
             else
             returnunicode(row) for row in alist_of_lists])

    else:
        return_string = returnunicode(alist_of_lists)
    return return_string


def find_similar(word, wordlist, hits=5):
    r"""

    :param word: the word to find similar words for
    :param wordlist: the word list to find similar in
    :param hits: the number of hits in first match (more hits will be added than this)
    :return:  a set with the matches

    some code from http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-whilst-preserving-order

    >>> find_similar('rb1203', ['Rb1203', 'rb 1203', 'gert', 'rb', 'rb1203', 'b1203', 'rb120', 'rb11', 'rb123', 'rb1203_bgfgf'], 5)
    ['rb1203', 'rb 1203', 'rb123', 'rb120', 'b1203', 'Rb1203', 'rb1203_bgfgf']
    >>> find_similar('1', ['2', '3'], 5)
    ['']
    >>> find_similar(None, ['2', '3'], 5)
    ['']
    >>> find_similar(None, None, 5)
    ['']
    >>> find_similar('1', [], 5)
    ['']
    >>> find_similar('1', False, 5)
    ['']
    >>> find_similar(False, ['2', '3'], 5)
    ['']

    """
    if None in [word, wordlist] or not wordlist or not word:
        return ['']

    matches = difflib.get_close_matches(word, wordlist, hits)

    matches.extend([x for x in wordlist if any((x.startswith(word.lower()), x.startswith(word.upper()), x.startswith(word.capitalize())))])
    nr_of_hits = len(matches)
    if nr_of_hits == 0:
        return ['']

    #Remove duplicates
    seen = set()
    seen_add = seen.add
    matches = [x for x in matches if x and not (x in seen or seen_add(x))]

    return matches


def filter_nonexisting_values_and_ask(file_data=None, header_value=None, existing_values=None, try_capitalize=False, always_ask_user=False):
    """

    The class NotFoundQuestion is used with 4 buttons; 'Ignore', 'Cancel', 'Ok', 'Skip'.
    Ignore = use the chosen value and move to the next obsid.
    Cancel = raises UserInterruptError
    Ok = Tries the currently submitted obsid against the existing once. If it doesn't exist, it asks again.
    Skip = None is used as obsid and the row is removed from the file_data

    :param file_data:
    :param header_value:
    :param existing_values:
    :param try_capitalize: If True, the header_value will be matched against existing_values both original value and as capitalized value. This parameter only has an effect if always_ask_user is False.
    :param always_ask_user: The used will be requested for every distinct header_value
    :return:

    """
    if file_data is None or header_value is None:
        return []
    if existing_values is None:
        existing_values = []
    header_value = returnunicode(header_value)
    filtered_data = []
    data_to_ask_for = []
    add_column = False
    try:
        index = file_data[0].index(header_value)
    except ValueError:
        # The header and all answers will be added as a new column.
        file_data[0].append(header_value)
        index = -1
        add_column = True
        filtered_data.append(file_data[0])
        pass
    else:
        filtered_data.append(file_data[0])

    for row in file_data[1:]:
        if add_column:
            row.append(None)
        if always_ask_user:
            data_to_ask_for.append(row)
        else:
            values = [row[index]]
            if try_capitalize:
                try:
                    values.append(row[index].capitalize())
                except AttributeError:
                    pass

            for _value in values:
                if _value in existing_values:
                    row[index] = _value
                    filtered_data.append(row)
                    break
            else:
                data_to_ask_for.append(row)

    headers_colnr = dict([(header, colnr) for colnr, header in enumerate(file_data[0])])

    already_asked_values = {} # {'obsid': {'asked_for': 'answer'}, 'report': {'asked_for_report': 'answer'}}
    reuse_column = ''
    for rownr, row in enumerate(data_to_ask_for):
        current_value = row[index]
        found = False
        #First check if the current value already has been asked for and if so
        # use the same answer again.
        for asked_header, asked_answers in already_asked_values.items():
            colnr = headers_colnr[asked_header]
            try:
                row[index] = asked_answers[row[colnr]]
            except KeyError:
                current_value = row[index]
            else:
                if row[index] is not None:
                    filtered_data.append(row)
                    found = True
                    break
                else:
                    found = True
                    break
        if found:

            continue

        submitted_value = None
        similar_values = find_similar(current_value, existing_values, hits=5)
        similar_values.extend([x for x in sorted(existing_values) if x not in similar_values])
        while submitted_value not in existing_values:
            #Put the found similar values on top, but include all values in the database as well
            msg = returnunicode(QCoreApplication.translate('filter_nonexisting_values_and_ask', '(Message %s of %s)\n\nGive the %s for:\n%s'))%(str(rownr + 1), str(len(data_to_ask_for)), header_value, '\n'.join([': '.join((file_data[0][_colnr], word if word is not None else '')) for _colnr, word in enumerate(row)]))
            question = NotFoundQuestion(dialogtitle=QCoreApplication.translate('filter_nonexisting_values_and_ask', 'User input needed'),
                                        msg=msg,
                                        existing_list=similar_values,
                                        default_value=similar_values[0],
                                        button_names=['Cancel', 'Ok', 'Skip'],
                                        reuse_header_list=sorted(headers_colnr.keys()),
                                        reuse_column=reuse_column,
                                        ignore_checkbox=True)
            answer = question.answer

            submitted_value = returnunicode(question.value)
            reuse_column = returnunicode(question.reuse_column)

            if answer == 'cancel':
                raise UserInterruptError()

            if answer == 'skip':
                submitted_value = None

            if reuse_column:
                already_asked_values.setdefault(reuse_column, {})[row[headers_colnr[reuse_column]]] = submitted_value

            if submitted_value is not None:
                row[index] = submitted_value
                filtered_data.append(row)

            if answer == 'skip' or question.ignore_checkbox.isChecked():
                break

    return filtered_data


def add_triggers_to_obs_points(filename):
    """
    /*
    * These are quick-fixes for updating coords from geometry and the other way around
    * Please notice that these are AFTER insert/update although BEFORE should be preferrable?
    * Also, srid is not yet read from the
    */

    -- geometry updated after coordinates are inserted
    CREATE TRIGGER "after_insert_obs_points_geom_fr_coords" AFTER INSERT ON "obs_points"
    WHEN (0 < (select count() from obs_points where ((NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL))))
    BEGIN
        UPDATE obs_points
        SET  geometry = MakePoint(east, north, (select srid from geometry_columns where f_table_name = 'obs_points'))
        WHERE (NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL);
    END;

    -- coordinates updated after geometries are inserted
    CREATE TRIGGER "after_insert_obs_points_coords_fr_geom" AFTER INSERT ON "obs_points"
    WHEN (0 < (select count() from obs_points where ((NEW.east is null) AND (NEW.north is null) AND (NEW.geometry is not NULL))))
    BEGIN
        UPDATE obs_points
        SET  east = X(geometry), north = Y(geometry)
        WHERE (NEW.east is null) AND (NEW.north is null) AND (NEW.geometry is not NULL);
    END;

    -- coordinates updated after geometries are updated
    CREATE TRIGGER "after_update_obs_points_coords_fr_geom" AFTER UPDATE ON "obs_points"
    WHEN (0 < (select count() from obs_points where NEW.geometry != OLD.geometry) )
    BEGIN
        UPDATE obs_points
        SET  east = X(geometry), north = Y(geometry)
        WHERE (NEW.geometry != OLD.geometry);
    END;

    -- geometry updated after coordinates are updated
    CREATE TRIGGER "after_update_obs_points_geom_fr_coords" AFTER UPDATE ON "obs_points"
    WHEN (0 < (select count() from obs_points where ((NEW.east != OLD.east) OR (NEW.north != OLD.north))) )
    BEGIN
        UPDATE obs_points
        SET  geometry = MakePoint(east, north, (select srid from geometry_columns where f_table_name = 'obs_points'))
        WHERE ((NEW.east != OLD.east) OR (NEW.north != OLD.north));
    END;
    :return:
    """
    db_utils.execute_sqlfile(os.path.join(os.sep, os.path.dirname(__file__), "..", "definitions", filename),
                     db_utils.sql_alter_db)


def sql_to_parameters_units_tuple(sql):
    parameters_from_table = returnunicode(db_utils.sql_load_fr_db(sql)[1], True)
    parameters_dict = {}
    for parameter, unit in parameters_from_table:
        parameters_dict.setdefault(parameter, []).append(unit)
    parameters = tuple([(k, tuple(v)) for k, v in sorted(parameters_dict.items())])
    return parameters


def scale_nparray(x, a=1, b=0):
    """
    Scales a 1d numpy array using linear equation
    :param x: A numpy 1darray, x in y=kx+m
    :param a: k in y=ax+b
    :param b: m in y=ax+b
    :return: A numpy 1darray, y in y=ax+b

    >>> scale_nparray(np.array([2,3,1,0]), b=10)
    array([12, 13, 11, 10])
    >>> scale_nparray(np.array([2,3,1,0]), b=10, a=4)
    array([18, 22, 14, 10])
    >>> scale_nparray(np.array([2,3,1,0]), 2)
    array([4, 6, 2, 0])
    >>> scale_nparray(np.array([2,3,1,0]), 2, -5)
    array([-1,  1, -3, -5])
    >>> scale_nparray(np.array([2,3,1,0]), -2, -5)
    array([ -9, -11,  -7,  -5])
    """
    return a * copy.deepcopy(x) + b


def remove_mean_from_nparray(x):
    """

    """
    x = copy.deepcopy(x)
    mean = x[np.logical_not(np.isnan(x))]
    mean = mean.mean(axis=0)
    x = x - mean

    # for colnr, col in enumerate(x):
    #     x[colnr] = x[colnr] - np.mean(x[colnr])
    return x


def getcurrentlocale(print_error_message_in_bar=True):
    db_locale = get_locale_from_db(print_error_message_in_bar=print_error_message_in_bar)

    if db_locale is not None and db_locale:
        return [db_locale, locale.getdefaultlocale()[1]]
    else:
        return locale.getdefaultlocale()[:2]


def get_locale_from_db(print_error_message_in_bar=True):
    connection_ok, locale_row = db_utils.sql_load_fr_db("SELECT description FROM about_db WHERE description LIKE 'locale:%'",
                                                        print_error_message_in_bar=print_error_message_in_bar)
    if connection_ok:
        try:
            locale_setting = returnunicode(locale_row, keep_containers=True)[0][0].split(':')
        except IndexError:
            return None

        try:
            locale_setting = locale_setting[1]
        except IndexError:
            return None
        else:
            return locale_setting
    else:
        MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('get_locale_from_db', 'Connection to db failed when getting locale from db.')))
        return None


def calculate_db_table_rows():
    results = {}

    tablenames = list(db_utils.tables_columns().keys())

    sql_failed = []
    for tablename in sorted(tablenames):
        sql = """SELECT count(*) FROM %s""" % (tablename)

        sql_result = db_utils.sql_load_fr_db(sql)
        connection_ok, nr_of_rows = sql_result

        if not connection_ok:
            sql_failed.append(sql)
            continue

        results[tablename] = str(nr_of_rows[0][0])

    if sql_failed:
        MessagebarAndLog.warning(
            bar_msg=sql_failed_msg(),
            log_msg=returnunicode(QCoreApplication.translate('calculate_db_table_rows', 'Sql failed:\n%s\n'))%'\n'.join(sql_failed))

    if results:
        printable_msg = '{0:40}{1:15}'.format('Tablename', 'Nr of rows\n')
        printable_msg += '\n'.join(
            ['{0:40}{1:15}'.format(table_name, _nr_of_rows) for
             table_name, _nr_of_rows in sorted(results.items())])
        MessagebarAndLog.info(
            bar_msg=QCoreApplication.translate('calculate_db_table_rows', 'Calculation done, see log for results.'),
            log_msg=printable_msg)


def anything_to_string_representation(anything, itemjoiner=', ', pad='', dictformatter='{%s}',
                                      listformatter='[%s]', tupleformatter='(%s, )'):
    r""" Turns anything into a string used for testing
    :param anything: just about anything
    :param itemjoiner: The string to join list/tuple/dict items with.
    :return: A unicode string
     >>> anything_to_string_representation({('123'): 4.5, "a": '7'})
     '{"123": 4.5, "a": "7"}'
     >>> anything_to_string_representation({('123', ): 4.5, "a": '7'})
     '{"a": "7", ("123", ): 4.5}'
     >>> anything_to_string_representation(['1', '2', 3])
     '["1", "2", 3]'
     >>> anything_to_string_representation({'123': 4.5, "a": '7'}, ',\n', '    ')
     '{    "123": 4.5,\n    "a": "7"}'
    """
    if isinstance(anything, dict):
        aunicode = dictformatter%itemjoiner.join([pad + ': '.join([anything_to_string_representation(k, itemjoiner,
                                                                                                      pad + pad,
                                                                                                      dictformatter,
                                                                                                      listformatter,
                                                                                                      tupleformatter),
                                                                    anything_to_string_representation(v, itemjoiner,  pad + pad,
                                                                                                      dictformatter,
                                                                                                      listformatter,
                                                                                                      tupleformatter)]) for k, v in sorted(anything.items())])
    elif isinstance(anything, list):
        aunicode = listformatter%itemjoiner.join([pad + anything_to_string_representation(x, itemjoiner, pad + pad,
                                                                                          dictformatter,
                                                                                          listformatter,
                                                                                          tupleformatter) for x in anything])
    elif isinstance(anything, tuple):
        aunicode = tupleformatter%itemjoiner.join([pad + anything_to_string_representation(x, itemjoiner, pad + pad,
                                                                                           dictformatter,
                                                                                           listformatter,
                                                                                           tupleformatter) for x in anything])
    elif isinstance(anything, (float, int)):
        aunicode = '{}'.format(returnunicode(anything))
    elif isinstance(anything, str):
        aunicode = '"{}"'.format(anything)
    elif isinstance(anything, str):
        aunicode = '"{}"'.format(anything)
    elif isinstance(anything, qgis.PyQt.QtCore.QVariant):
        aunicode = returnunicode(anything.toString().data())
    else:
        aunicode = returnunicode(str(anything))
    return aunicode


def waiting_cursor(func):
    def func_wrapper(*args, **kwargs):
        start_waiting_cursor()
        result = func(*args, **kwargs)
        stop_waiting_cursor()
        return result
    return func_wrapper

def start_waiting_cursor():
    qgis.PyQt.QtWidgets.QApplication.setOverrideCursor(qgis.PyQt.QtCore.Qt.WaitCursor)

def stop_waiting_cursor():
    qgis.PyQt.QtWidgets.QApplication.restoreOverrideCursor()

class Cancel(object):
    """Object for transmitting cancel messages instead of using string 'cancel'.
        use isinstance(variable, Cancel) to check for it.

        Usage:
        return Cancel()

        Return the same Cancel object.
        if isinstance(answer, Cancel):
            return answer

        Potential improvements could be to include messages inside the objects.
    """
    def __init__(self):
        pass


def get_delimiter(filename, charset='utf-8', delimiters=None, num_fields=None):
    if filename is None:
        raise TypeError(QCoreApplication.translate('get_delimiter', 'Must give filename'))
    with io.open(filename, 'r', encoding=charset) as f:
        rows = f.readlines()

    delimiter = get_delimiter_from_file_rows(rows, filename=filename, delimiters=None, num_fields=None)
    return delimiter


def get_delimiter_from_file_rows(rows, filename=None, delimiters=None, num_fields=None):
    if filename is None:
        filename = 'the rows'
    delimiter = None
    if delimiters is None:
        delimiters = [',', ';']
    tested_delim = []
    for _delimiter in delimiters:
        cols_on_all_rows = set()
        cols_on_all_rows.update([len(row.split(_delimiter)) for row in rows])
        if len(cols_on_all_rows) == 1:
            nr_of_cols = cols_on_all_rows.pop()
            if num_fields is not None and nr_of_cols == num_fields:
                delimiter = _delimiter
                break
            tested_delim.append((_delimiter, nr_of_cols))

    if not delimiter:
        # No delimiter worked
        if not tested_delim:
            _delimiter = ask_for_delimiter(question=returnunicode(QCoreApplication.translate('get_delimiter_from_file_rows', "Delimiter couldn't be found automatically for %s. Give the correct one (ex ';'):"))% filename)
            delimiter = _delimiter[0]
        else:
            if delimiter is None:
                if num_fields is not None:
                    MessagebarAndLog.critical(returnunicode(QCoreApplication.translate('get_delimiter_from_file_rows', 'Delimiter not found for %s. The file must contain %s fields, but none of %s worked as delimiter.'))%(filename, str(num_fields), ' or '.join(delimiters)))
                    return None

                lenght = max(tested_delim, key=itemgetter(1))[1]

                more_than_one_delimiter = [x[0] for x in tested_delim if x[1] == lenght]

                delimiter = max(tested_delim, key=itemgetter(1))[0]

                if lenght == 1 or len(more_than_one_delimiter) > 1:
                    _delimiter = ask_for_delimiter(question=returnunicode(QCoreApplication.translate('get_delimiter_from_file_rows', "Delimiter couldn't be found automatically for %s. Give the correct one (ex ';'):")) % filename)
                    delimiter = _delimiter[0]
    return delimiter


def ask_for_delimiter(header=QCoreApplication.translate('ask_for_delimiter', 'Give delimiter'), question='', default=';'):
    _delimiter = qgis.PyQt.QtWidgets.QInputDialog.getText(None,
                                                  QCoreApplication.translate('ask_for_delimiter', "Give delimiter"),
                                                  question,
                                                  qgis.PyQt.QtWidgets.QLineEdit.Normal,
                                                  default)
    if not _delimiter[1]:
        MessagebarAndLog.info(bar_msg=returnunicode(QCoreApplication.translate('ask_for_delimiter', 'Delimiter not given. Stopping.')))
        raise UserInterruptError()
    else:
        delimiter = _delimiter[0]
    return delimiter


def create_markdown_table_from_table(tablename, transposed=False, only_description=False):
    table = list_of_lists_from_table(tablename)
    if only_description:
        descr_idx = table[0].index('description')
        tablename_idx = table[0].index('tablename')
        columnname_idx = table[0].index('columnname')

        table = [[row[tablename_idx], row[columnname_idx], row[descr_idx]] for row in table]

    if transposed:
        table = transpose_lists_of_lists(table)
        for row in table:
            row[0] = '**{}**'.format(row[0])

    column_names = table[0]
    table_contents = table[1:]

    printlist = ['|{}|'.format(' | '.join(column_names))]
    printlist.append('|{}|'.format(' | '.join([':---' for idx, x in enumerate(column_names)])))
    printlist.extend(['|{}|'.format(' | '.join([item if item is not None else '' for item in row])) for row in table_contents])
    return '\n'.join(printlist)


def list_of_lists_from_table(tablename):
    list_of_lists = []
    table_info = db_utils.get_table_info(tablename)
    table_info = returnunicode(table_info, keep_containers=True)
    column_names = [x[1] for x in table_info]
    list_of_lists.append(column_names)
    table_contents = db_utils.sql_load_fr_db('SELECT * FROM %s'%tablename)[1]
    table_contents = returnunicode(table_contents, keep_containers=True)
    list_of_lists.extend(table_contents)
    return list_of_lists


def transpose_lists_of_lists(list_of_lists):
    outlist_of_lists = [[row[colnr] for row in list_of_lists] for colnr in range(len(list_of_lists[0]))]
    return outlist_of_lists


def sql_failed_msg():
    return QCoreApplication.translate('sql_failed_msg', 'Sql failed, see log message panel.')


def fn_timer(function):
    """from http://www.marinamele.com/7-tips-to-time-python-scripts-and-control-memory-and-cpu-usage"""
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        #logging.debug("Total time running %s: %s seconds" %
        #       (function.func_name, str(t1-t0))
        #
        try:
            print ("Total time running %s: %s seconds" %
                  (function.__name__, str(t1-t0))
                   )
        except IOError:
            pass

        return result
    return function_timer


class UserInterruptError(Exception):
    pass


class UsageError(Exception):
    pass


def general_exception_handler(func):
    """
    If UsageError is raised without message, it is assumed that the programmer has used MessagebarAndLog for the messages
    and no additional message will be printed.

    UserInterruptError is assumed to never have an error text.

    :param func:
    :return:
    """
    def new_func(*args, **kwargs):
        #print("general_exception_handler args: '{}' kwargs: '{}' ".format(str(args), str(kwargs)))
        try:
            result = func(*args, **kwargs)
        except UserInterruptError:
            # The user interrupted the process.
            stop_waiting_cursor()
            pass
        except UsageError as e:
            stop_waiting_cursor()
            msg = str(e)
            if msg:
                MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('general_exception_handler', 'Usage error: %s'))%str(e),
                                          duration=30)
        except:
            stop_waiting_cursor()
            raise
        else:
            return result
    return new_func


def save_stored_settings(ms, stored_settings, settingskey):
    """
    Saves the current parameter settings into midvatten settings

    :param ms: midvattensettings
    :param stored_settings: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
    :return: stores a string like objname;attr1:value1;attr2:value2/objname2;attr3:value3... in midvatten settings
    """
    settings_string = anything_to_string_representation(stored_settings)
    ms.settingsdict[settingskey] = settings_string
    ms.save_settings(settingskey)
    MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('save_stored_settings', 'Settings %s stored for key %s.'))%(settings_string, settingskey))


def get_stored_settings(ms, settingskey, default=None):
    """
    Reads the settings from settingskey and returns a created dict/list/tuple using ast.literal_eval

    :param ms: midvatten settings
    :param settingskey: the key to get from midvatten settings.
    :return: a tuple like ((objname', ((attr1, value1), (attr2, value2))), (objname2, ((attr3, value3), ...)
    """
    if default is None:
        default = []
    settings_string_raw = ms.settingsdict.get(settingskey, None)
    if settings_string_raw is None:
        MessagebarAndLog.info(bar_msg=returnunicode(QCoreApplication.translate('get_stored_settings', 'Settings key %s did not exist in midvatten settings.'))%settingskey)
        return default
    if not settings_string_raw:
        MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('get_stored_settings', 'Settings key %s was empty.'))%settingskey)
        return default

    settings_string_raw = returnunicode(settings_string_raw)

    try:
        MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('get_stored_settings', 'Reading stored settings "%s":\n%s'))%(settingskey,
                                                                                                                                               settings_string_raw))
    except:
        pass

    try:
        stored_settings = ast.literal_eval(settings_string_raw)
    except SyntaxError as e:
        stored_settings = default
        MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('get_stored_settings', 'Getting stored settings failed for key %s see log message panel.'))%settingskey, log_msg=returnunicode(QCoreApplication.translate('ExportToFieldLogger', 'Parsing the settingsstring %s failed. Msg "%s"'))%(settings_string_raw, str(e)))
    except ValueError as e:
        stored_settings = default
        MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('get_stored_settings', 'Getting stored settings failed for key %s see log message panel.'))%settingskey, log_msg=returnunicode(QCoreApplication.translate('ExportToFieldLogger', 'Parsing the settingsstring %s failed. Msg "%s"'))%(settings_string_raw, str(e)))
    return stored_settings


def to_float_or_none(anything):
    if isinstance(anything, float):
        return anything
    elif isinstance(anything, int):
        return float(anything)
    elif isinstance(anything, str):
        try:
            a_float = float(anything.replace(',', '.'))
        except TypeError:
            return None
        except ValueError:
            return None
        except:
            return None
        else:
            return a_float
    elif anything is None:
        return anything
    else:
        try:
            a_float = float(str(anything).replace(',', '.'))
        except:
            return None
        else:
            return a_float


class PlotTemplates(object):
    def __init__(self, plot_object,
                 template_list,
                 edit_button,
                 load_button,
                 save_as_button,
                 import_button,
                 remove_button,
                 template_folder,
                 templates_settingskey,
                 loaded_template_settingskey,
                 fallback_template,
                 msettings=None):

        # Gui objects
        self.template_list = template_list
        self.edit_button = edit_button
        self.load_button = load_button
        self.save_as_button = save_as_button
        self.import_button = import_button
        self.remove_button = remove_button

        self.ms = msettings
        self.templates = {}
        self.loaded_template = {}

        self.template_folder = template_folder
        self.fallback_template = fallback_template
        self.templates_settingskey = templates_settingskey
        self.loaded_template_settingskey = loaded_template_settingskey

        self.templates = {}

        self.import_saved_templates()
        self.import_from_template_folder()

        try:
            self.loaded_template = self.string_to_dict(self.ms.settingsdict[self.loaded_template_settingskey])
        except:
            MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('PlotTemplates', 'Failed to load saved template, loading default template instead.')))
        if self.loaded_template:
            MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('PlotTemplates', 'Loaded template from midvatten settings %s.'))%self.loaded_template_settingskey)

        default_filename = os.path.join(self.template_folder, 'default.txt')

        if not self.loaded_template:
            if not os.path.isfile(default_filename):
                MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('PlotTemplates',
                                                                                     'Default template not found, loading hard coded default template.')))
            else:
                try:
                    self.load(self.templates[default_filename]['template'])
                except Exception as e:
                    MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('PlotTemplates',
                                                                                         'Failed to load default template, loading hard coded default template.')),
                                                   log_msg=returnunicode(QCoreApplication.translate('PlotTemplates', 'Error msg %s'))%str(e))
            if self.loaded_template:
                MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('PlotTemplates', 'Loaded template from default template file.')))

        if not self.loaded_template:
            self.loaded_template = self.fallback_template
            if self.loaded_template:
                MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('PlotTemplates', 'Loaded template from default hard coded template.')))

        self.edit_button.clicked.connect(lambda x: self.edit())
        self.load_button.clicked.connect(lambda x: self.load())
        self.save_as_button.clicked.connect(lambda x: self.save_as())
        self.import_button.clicked.connect(lambda x: self.import_templates())
        self.remove_button.clicked.connect(lambda x: self.remove())

    @general_exception_handler
    def edit(self):
        old_string = self.readable_output(self.loaded_template)

        msg = returnunicode(QCoreApplication.translate('StoredSettings', 'Replace the settings string with a new settings string.'))
        new_string = qgis.PyQt.QtWidgets.QInputDialog.getText(None, returnunicode(QCoreApplication.translate('StoredSettings', "Edit settings")), msg,
                                                           qgis.PyQt.QtWidgets.QLineEdit.Normal, old_string)
        if not new_string[1]:
            raise UserInterruptError()

        as_dict = self.string_to_dict(returnunicode(new_string[0]))

        self.loaded_template = as_dict

    @general_exception_handler
    def load(self, template=None):
        if isinstance(template, dict):
            self.loaded_template = template
        else:
            selected = self.template_list.selectedItems()
            if selected:
                filename = selected[0].filename
                template = self.parse_template(filename)
                if template:
                    self.templates[filename] = template
                self.loaded_template = self.templates[filename]['template']

    @general_exception_handler
    def save_as(self):
        filename = get_save_file_name_no_extension(parent=None, caption=returnunicode(QCoreApplication.translate('PlotTemplates', 'Choose a file name')), directory='', filter='txt (*.txt)')
        as_str = self.readable_output(self.loaded_template)
        with io.open(filename, 'w', encoding='utf8') as of:
            of.write(as_str)

        name = os.path.splitext(os.path.basename(filename))[0]
        template = copy.deepcopy(self.loaded_template)
        self.templates[filename] = {'filename': filename, 'template': template, 'name': name}

        self.update_settingsdict()
        self.update_template_list()

    @general_exception_handler
    def import_templates(self, filenames=None):
        if filenames is None:
            filenames = select_files(only_one_file=False, extension='')
        templates = {}
        if filenames:
            for filename in filenames:
                if not filename:
                    continue

                processed_before = filename in list(self.templates.keys())
                processed_now = filename in list(templates.keys())

                if not processed_before and not processed_now:
                    template = self.parse_template(filename)
                    if template:
                        templates[filename] = template

        self.templates.update(templates)
        self.update_settingsdict()
        self.update_template_list()

    @general_exception_handler
    def remove(self):
        selected = self.template_list.selectedItems()
        if selected:
            filename = selected[0].filename
            del self.templates[filename]
            self.update_settingsdict()
            self.update_template_list()

    @general_exception_handler
    def import_from_template_folder(self):
        for root, dirs, files in os.walk(self.template_folder):
            if files:
                filenames = [os.path.join(root, filename) for filename in files]
                self.import_templates(filenames)

    @general_exception_handler
    def import_saved_templates(self):
        filenames = [x for x in self.ms.settingsdict[self.templates_settingskey].split(';') if x]
        if filenames:
            MessagebarAndLog.info(
                log_msg=returnunicode(QCoreApplication.translate('', 'Loading saved templates %s')) % '\n'.join(filenames))
            self.import_templates(filenames)

    def parse_template(self, filename):
        name = os.path.splitext(os.path.basename(filename))[0]
        if not os.path.isfile(filename):
            raise UsageError(returnunicode(QCoreApplication.translate('PlotTemplates', '"%s" was not a file.')) % filename)
        try:
            with io.open(filename, 'rt', encoding='utf-8') as f:
                lines = ''.join([line for line in f if line])
        except Exception as e:
            MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('PlotTemplates',
                                                                                  'Loading template %s failed, see log message panel')) % filename,
                                            log_msg=returnunicode(QCoreApplication.translate('PlotTemplates', 'Reading file failed, msg:\n%s'))%returnunicode(str(e)))
            raise

        if lines:
            try:
                template = self.string_to_dict(''.join(lines))
            except Exception as e:
                MessagebarAndLog.critical(bar_msg=returnunicode(QCoreApplication.translate('PlotTemplates',
                                                                                      'Loading template %s failed, see log message panel')) % filename,
                                                log_msg=returnunicode(QCoreApplication.translate('PlotTemplates',
                                                                                      'Parsing file rows failed, msg:\n%s')) % returnunicode(str(e)))
                raise
            else:
                return {'filename': filename, 'template': template, 'name': name}
        else:
            return {}

    def update_settingsdict(self):
        self.ms.settingsdict[self.templates_settingskey] = ';'.join(list(self.templates.keys()))
        self.ms.save_settings(self.templates_settingskey)

    def update_template_list(self):
        self.template_list.clear()
        for filename, template in sorted(iter(self.templates.items()), key=lambda x: os.path.basename(x[0])):
            qlistwidgetitem = qgis.PyQt.QtWidgets.QListWidgetItem()
            qlistwidgetitem.setText(template['name'])
            qlistwidgetitem.filename = template['filename']
            self.template_list.addItem(qlistwidgetitem)

    def readable_output(self, a_dict=None):
        if a_dict is None:
            a_dict = self.loaded_template
        return anything_to_string_representation(a_dict, itemjoiner=',\n', pad='    ',
                                                dictformatter='{\n%s}',
                                                listformatter='[\n%s]', tupleformatter='(\n%s, )')

    def string_to_dict(self, the_string):
        the_string = returnunicode(the_string)
        if not the_string:
            return ''
        try:
            as_dict = ast.literal_eval(the_string)
        except Exception as e:
            MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('StoredSettings', 'Translating string to dict failed, see log message panel')),
                                           log_msg=returnunicode(QCoreApplication.translate('StoredSettings', 'Error %s\nfor string\n%s'))%(str(e), the_string))
        else:
            return as_dict


class MatplotlibStyles(object):
    def __init__(self, plot_object,
                 style_list,
                 import_button,
                 open_folder_button,
                 available_settings_button,
                 save_as_button,
                 last_used_style_settingskey,
                 defaultstyle_stylename,
                 msettings=None):

        # Gui objects
        self.style_list = style_list
        self.import_button = import_button
        self.open_folder_button = open_folder_button
        self.available_settings_button = available_settings_button
        self.save_as_button = save_as_button

        self.style_extension = '.mplstyle'
        self.style_folder = os.path.join(mpl.get_configdir(), 'stylelib')
        if os.path.isdir(mpl.get_configdir()):
            if os.path.exists(self.style_folder):
                if not os.path.isdir(self.style_folder):
                    MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles',
                                                                                              '''Matplotlib style folder %s was not a directory!'''))%self.style_folder)
            else:
                try:
                    os.makedirs(self.style_folder)
                except Exception as e:
                    MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles',
                                                                                              '''Could not create style folder %s, see log message panel!''')) % self.style_folder,
                                             log_msg=str(e))
                else:
                    MessagebarAndLog.info(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles',
                                                                                              '''Matplotlib style folder created %s.''')) % self.style_folder)
        else:
            MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles', '''Matplotlib config directory not found. User styles not used.''')))



        if not os.path.isdir(self.style_folder):
            os.mkdir(self.style_folder)

        self.ms = msettings

        self.defaultstyle_stylename = defaultstyle_stylename

        self.last_used_style_settingskey = last_used_style_settingskey

        self.update_style_list()

        if not os.path.isfile(self.filename_from_style(self.defaultstyle_stylename[1])):
            self.save_style_to_stylelib(self.defaultstyle_stylename)
        try:
            last_used_style = self.ms.settingsdict[self.last_used_style_settingskey]
        except:
            MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles', 'Failed to load saved style, loading default style instead.')))
        else:
            self.select_style_in_list(last_used_style)

        self.import_button.clicked.connect(lambda x: self.import_style())
        self.open_folder_button.clicked.connect(lambda x: self.open_folder())
        self.available_settings_button.clicked.connect(lambda x: self.available_settings_to_log())
        self.save_as_button.clicked.connect(lambda x: self.save_as())

    def save_style_to_stylelib(self, stylestring_stylename):
        filename = self.filename_from_style(stylestring_stylename[1])
        with io.open(filename, 'w', encoding='utf-8') as of:
            of.write(stylestring_stylename[0])
        mpl.style.reload_library()

    def get_selected_style(self):
        selected = self.style_list.selectedItems()
        if selected:
            return selected[0].text()

    def style_from_filename(self, filename):
        return os.path.splitext(os.path.basename(filename))

    def filename_from_style(self, style):
        filename = os.path.join(self.style_folder, style + self.style_extension)
        return filename

    @general_exception_handler
    def load(self, drawfunc, plot_widget_navigationtoolbar_name=None):
        #mpl.rcdefaults()
        mpl.style.reload_library()
        fallback_style = 'fallback_' + self.defaultstyle_stylename[1]
        self.save_style_to_stylelib([self.defaultstyle_stylename[0], fallback_style])
        styles = [self.get_selected_style(), self.defaultstyle_stylename[1], fallback_style, 'default']

        use_style = None
        for _style in styles:
            if not _style:
                continue
            try:
                with plt.style.context(_style):
                    pass
            except Exception as e:
                MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles', 'Failed to load style, check style settings in %s.')) % self.filename_from_style(_style),
                                         log_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles', 'Error msg %s')) % str(e))
            else:
                use_style = _style
                break
        if use_style is not None:
            with plt.style.context(use_style):
                drawfunc()
            if plot_widget_navigationtoolbar_name is not None:
                navigationtoolbar = getattr(plot_widget_navigationtoolbar_name[0], plot_widget_navigationtoolbar_name[1])
                navigationtoolbar.midv_use_style = use_style
        else:
            drawfunc()

    @general_exception_handler
    def import_style(self, filenames=None):
        if filenames is None:
            filenames = select_files(only_one_file=False, extension='')
        if filenames:
            for filename in filenames:
                if not filename:
                    continue

                folder, _filename = os.path.split(filename)
                basename, ext = os.path.splitext(_filename)
                newname = basename + self.style_extension
                new_fullname = os.path.join(self.style_folder, newname)
                if os.path.isfile(new_fullname):
                    answer = Askuser(question="YesNo", msg=returnunicode(QCoreApplication.translate('MatplotlibStyles', 'The style file existed. Overwrite?')))
                    if not answer:
                        return
                shutil.copy2(filename, new_fullname)
            self.update_style_list()

    @general_exception_handler
    def save_as(self):
        filename = get_save_file_name_no_extension(parent=None, caption=returnunicode(QCoreApplication.translate('MatplotlibStyles', 'Choose a file name')), directory=self.style_folder, filter='mplstyle (*.mplstyle)')
        if not filename.endswith('.mplstyle'):
            basename, ext = os.path.splitext(filename)
            filename = basename + '.mplstyle'
        with plt.style.context(self.get_selected_style()):
            rcparams = self.rcparams()
        with io.open(filename, 'w', encoding='utf8') as of:
            of.write(rcparams)
        self.update_style_list()

    @general_exception_handler
    def open_folder(self):
        url = QtCore.QUrl(self.style_folder, QtCore.QUrl.TolerantMode)
        QDesktopServices.openUrl(url)

    def update_settingsdict(self):
        self.ms.settingsdict[self.last_used_style_settingskey] = self.get_selected_style()
        self.ms.save_settings(self.last_used_style_settingskey)

    def update_style_list(self):
        mpl.style.reload_library()
        selected_style = self.get_selected_style()
        self.style_list.clear()
        for style in sorted(plt.style.available):
            qlistwidgetitem = qgis.PyQt.QtWidgets.QListWidgetItem()
            qlistwidgetitem.setText(style)
            self.style_list.addItem(qlistwidgetitem)
            if style == selected_style:
                qlistwidgetitem.setSelected(True)

    def available_settings_to_log(self):
        rows = self.rcparams()
        MessagebarAndLog.info(bar_msg=returnunicode(QCoreApplication.translate('MatplotlibStyles', 'rcParams written to log, see log messages')),
                              log_msg=rows)

    def rcparams(self):
        def format_v(v):
            if isinstance(v, (list, tuple)):
                if v:
                    return ','.join([str(_v) for _v in v])
                else:
                    return ''
            else:
                return str(v)

        return '\n'.join(['{}: {}'.format(str(k), format_v(v)) for k, v in sorted(mpl.rcParams.items())])

    def select_style_in_list(self, style):
        for idx in range(self.style_list.count()):
            item = self.style_list.item(idx)
            if item.text() == style:
                item.setSelected(True)
            else:
                item.setSelected(False)


def create_layer(tablename, geometrycolumn=None, sql=None, keycolumn=None, dbconnection=None, layername=None):
    if not isinstance(dbconnection, db_utils.DbConnectionManager):
        dbconnection = db_utils.DbConnectionManager()

    uri = dbconnection.uri
    dbtype = dbconnection.dbtype
    schema = dbconnection.schemas()
    # For QgsVectorLayer, dbtype has to be postgres instead of postgis
    dbtype = db_utils.get_dbtype(dbtype)

    uri.setDataSource(schema, tablename, geometrycolumn, sql, keycolumn)
    _name = tablename if layername is None else layername
    layer = QgsVectorLayer(uri.uri(), _name, dbtype)
    return layer


def add_layers_to_list(resultlist, tablenames, geometrycolumn=None, dbconnection=None, layernames=None):
    if not isinstance(dbconnection, db_utils.DbConnectionManager):
        dbconnection = db_utils.DbConnectionManager()
    existing_tables = db_utils.get_tables(dbconnection, skip_views=False)

    for idx, tablename in enumerate(tablenames):  # first load all non-spatial layers
        orig_tablename = tablename

        if not tablename in existing_tables:
            continue

        layername = layernames[idx] if layernames is not None else None

        if tablename in ['obs_points', 'obs_lines'] and 'view_{}'.format(tablename) in existing_tables:
            tablename = 'view_{}'.format(tablename)

        for keycolumn in [None, 'obsid', 'rowid']:
            layer = create_layer(tablename, geometrycolumn=geometrycolumn, dbconnection=dbconnection, layername=layername,
                                 keycolumn=keycolumn)
            if layer.isValid():
                break
        else:
            MessagebarAndLog.critical(bar_msg=layer.name() + ' is not valid layer')
            return

        if tablename in ['view_obs_points', 'view_obs_lines']:
            layer.setName(orig_tablename)
        resultlist.append(layer)


def write_printlist_to_file(filename, printlist, dialect=csv.excel, delimiter=';', encoding="utf-8", **kwds):
    with io.open(filename, 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=delimiter, dialect=dialect, **kwds)
        #csvwriter.writerows([[bytes(returnunicode(col), encoding) for col in row] for row in printlist])
        csvwriter.writerows(returnunicode(printlist, keep_containers=True))
    MessagebarAndLog.info(bar_msg=returnunicode(QCoreApplication.translate('write_printlist_to_file', 'Data written to file %s.'))%filename)


def sql_unicode_list(an_iterator):
    return ', '.join(["'{}'".format(returnunicode(x)) for x in an_iterator])


def get_save_file_name_no_extension(**kwargs):
    filename = qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName(**kwargs)
    if not filename[0]:
        raise UserInterruptError()
    else:
        return filename[0]

def dict_to_tuple(adict):
    return tuple([(k, v) for k, v in sorted(adict.items())])


class ContinuousColorCycle(object):
    def __init__(self, color_cycle, color_cycle_len, style_cycler, used_style_color_combo):
        self.color_cycle = color_cycle
        self.color_cycle_len = color_cycle_len
        self.style_cycler_len = len(style_cycler)
        self.style_cycle = style_cycler()
        # Initiate the first to match the logic in __next__
        next(self.style_cycle)
        self.used_style_color_combo = used_style_color_combo

    def __next__(self):
        # Go one lap around the cycle
        [next(self.style_cycle) for _ in range(self.style_cycler_len - 1)]

        for _ in range(self.style_cycler_len):
            s = next(self.style_cycle)
            for _ in range(self.color_cycle_len):
                c = next(self.color_cycle)
                next_combo = dict(c)
                next_combo.update(s)
                next_combo_str = dict_to_tuple(next_combo)
                if next_combo_str not in self.used_style_color_combo:
                    self.used_style_color_combo.add(next_combo_str)
                    return next_combo
        else:
            MessagebarAndLog.info(
                bar_msg=returnunicode(QCoreApplication.translate('Customplot', 'Style cycler ran out of unique combinations. Using random color!')))
            #Use next again to not get the same as last time.
            next(self.style_cycle)
            next_combo = dict(next(self.style_cycle))
            r = np.random.rand(3, 1).ravel()
            next_combo.update({'color': r})
            return next_combo


def warn_about_old_database():
    try:
        dbconnection = db_utils.DbConnectionManager()
    except UsageError:
        #Probably empty project
        return

    try:
        dbconnection.cursor.execute('''SELECT description FROM about_db LIMIT 1''')
        rows = dbconnection.cursor.fetchall()
    except Exception as e:
        MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('warn_about_old_database',
                                                                               "Database might not be a valid Midvatten database!")),
                              log_msg=returnunicode(QCoreApplication.translate('warn_about_old_database', 'msg: %s'))%str(e))
        return

    try:
        row = rows[0][0]
    except:
        MessagebarAndLog.info(log_msg=returnunicode(QCoreApplication.translate('warn_about_old_database', "No row returned from about_db when searching for version.")))
        return
    if row:
        patterns = ['''Midvatten plugin Version ([0-9\.a-b]+)''',
                    '''Midvatten plugin ([0-9\.a-b]+)''',
                    ]
        version = None
        for pattern in patterns:
            m = re.search(pattern, row)
            if m:
                version = m.groups()[0]
                break
        if version:
            wikipage = 'https://github.com/jkall/qgis-midvatten-plugin/wiki/6.-Database-management#upgrade-database'
            if version < latest_database_version():
                MessagebarAndLog.info(bar_msg=returnunicode(QCoreApplication.translate('warn_about_old_database', '''The database version appears to be older than %s. An upgrade is suggested! See %s'''))%(latest_database_version(), wikipage), duration=5)

    #wikipage_view_obs_points = 'https://github.com/jkall/qgis-midvatten-plugin/wiki/6.-Database-management#add-view_obs_points-as-workaround-for-qgis-bug-20633'
    if dbconnection.dbtype == 'spatialite' and not all([db_utils.verify_table_exists('view_obs_points', dbconnection=dbconnection),
                                                        db_utils.verify_table_exists('view_obs_lines', dbconnection=dbconnection)]):
        #answer = Askuser(question="YesNo", msg = "Database is missing view_obs_points or view_obs_lines. It's recommended to add them. Do you want to add them?, dialogtitle=QCoreApplication.translate('askuser', 'User input needed"), parent=None)
        #if answer:
        #    add_view_obs_points_obs_lines()

        MessagebarAndLog.warning(bar_msg=returnunicode(QCoreApplication.translate('warn_about_old_database', '''Database is missing view_obs_points or view_obs_lines! Add these using Midvatten>Database Management>Add view_obs_points as workaround for qgis bug #20633.''')), duration=60)


def execute_sqlfile(sqlfilename, dbconnection, merge_newlines=False):
    with open(sqlfilename, 'r') as f:
        lines = [returnunicode(line).rstrip('\r').rstrip('\n') for rownr, line in enumerate(f) if rownr > 0]
    lines = [line for line in lines if all([line.strip(), not line.strip().startswith("#")])]

    if merge_newlines:
        lines = ['{};'.format(line) for line in ''.join(lines).split(';') if line.strip()]

    for line in lines:
        if line:
            try:
                dbconnection.execute(line)
            except Exception as e:
                MessagebarAndLog.critical(bar_msg=sql_failed_msg(), log_msg=returnunicode(QCoreApplication.translate('NewDb', 'sql failed:\n%s\nerror msg:\n%s\n'))%(returnunicode(line), str(e)))


def add_view_obs_points_obs_lines():
    dbconnection = db_utils.DbConnectionManager()
    if dbconnection.dbtype != 'spatialite':
        MessagebarAndLog.info(bar_msg=QCoreApplication.translate("Midvatten", 'Views not added for PostGIS databases (not needed)!'))
        return

    connection_ok = dbconnection.connect2db()
    if connection_ok:
        dbconnection.execute('''DROP VIEW IF EXISTS view_obs_points;''')
        dbconnection.execute('''DROP VIEW IF EXISTS view_obs_lines;''')
        dbconnection.execute('''DELETE FROM views_geometry_columns WHERE view_name IN ('view_obs_points', 'view_obs_lines');''')
        execute_sqlfile(get_full_filename('qgis3_obsp_fix.sql'), dbconnection)
        dbconnection.commit_and_closedb()
        MessagebarAndLog.info(bar_msg=QCoreApplication.translate("Midvatten",
                                                                           'Views added. Please reload layers (Midvatten>Load default db-layers to qgis or "F7").'))

def get_full_filename(filename):
    return os.path.join(os.sep,os.path.dirname(__file__), "..", "definitions", filename)


class PickAnnotator(object):
    def __init__(self, fig, canvas=None, mpltoolbar=None, mousebutton='left'):
        self.fig = fig
        self.annotation = None

        self.mousebutton = mousebutton
        if canvas is None:
            canvas = fig.canvas
        if mpltoolbar is None:
            mpltoolbar = fig.canvas.manager.toolbar
        canvas.mpl_connect('pick_event', lambda event: self.identify_plot(mpltoolbar, event))
        canvas.mpl_connect('figure_enter_event', self.remove_annotation)
        MessagebarAndLog.info( log_msg=QCoreApplication.translate("PickAnnotator", 'PickAnnotator initialized.'))

    def identify_plot(self, mpltoolbar, event):
        try:
            if mpltoolbar._active:
                return
            mouseevent = event.mouseevent
            if mouseevent.button.name.lower() != self.mousebutton:
                return
            artist = event.artist
            ax = artist.axes

            try:
                xtext = datetime.datetime.strftime(num2date(mouseevent.xdata), '%Y-%m-%d %H:%M:%S')
            except:
                xtext = mouseevent.xdata

            try:
                ytext = round(mouseevent.ydata, 3)
            except:
                ytext = mouseevent.ydata
            new_text = ', '.join(['"{}"'.format(artist.get_label()), str(xtext), str(ytext)])

            pos = (mouseevent.xdata, mouseevent.ydata)
            if not isinstance(self.annotation, mpl.text.Annotation):
                try:
                    self.annotation = ax.annotate(text=new_text, xy=pos, fontsize=8, xycoords='data',
                                                  bbox=dict(boxstyle='round',
                                                            fc="w", ec="k", alpha=0.5))
                except:
                    self.annotation = ax.annotate(new_text, xy=pos, fontsize=8, xycoords='data',
                                                  bbox=dict(boxstyle='round', fc="w", ec="k", alpha=0.5))
            else:
                self.annotation.set_text(new_text)
                self.annotation.set_x(pos[0])
                self.annotation.set_y(pos[1])

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        except Exception as e:
            MessagebarAndLog.info(
                log_msg=QCoreApplication.translate("PickAnnotator", 'Adding annotation failed, msg: %s.') % str(e))
            raise

    def remove_annotation(self, event):
        if isinstance(self.annotation, mpl.text.Annotation):
            try:
                self.annotation.remove()
                self.annotation = None
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
            except Exception as e:
                MessagebarAndLog.info(
                    log_msg=QCoreApplication.translate("PickAnnotator", 'Removing annotation failed, msg: %s.') % str(
                        e))

class Timer(object):
    def __init__(self, name):
        self.t0 = time.time()
        self.name = name

    def stop(self):
        t1 = time.time()
        MessagebarAndLog.info(log_msg=QCoreApplication.translate("Timer", 'Total time running %s: %s seconds') % (
            self.name, str(t1 - self.t0)))

@contextmanager
def timer(name):
    t0 = time.time()
    yield
    t1 = time.time()
    MessagebarAndLog.info(
        log_msg=QCoreApplication.translate("timer", 'Total time running %s: %s seconds') % (name, str(t1 - t0)))