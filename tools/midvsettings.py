# -*- coding: utf-8 -*-
"""
/***************************************************************************
 midvsettings
                                 A part of the QGIS plugin Midvatten
                                This part of the plugin handles plugin specific settings
                             -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/"""
from __future__ import absolute_import
from __future__ import print_function

import traceback
from builtins import object
from builtins import str

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProject

from midvatten.definitions import midvatten_defs
from midvatten.tools.utils.common_utils import MessagebarAndLog
from midvatten.tools.utils.common_utils import returnunicode as ru


class midvsettings(object):
    def __init__(self):
        # settings...
        self.settingsareloaded = False
        self.readingSettings = False # To enable resetsettings
        self.settingsdict = self.createsettingsdict()# calling for the method that defines an empty dictionary of settings NOTE!! byte strings in dict
        try:
            self.loadSettings()    # stored settings are loaded (if there are any)
            #The settings are loaded each time a new qgis project is loaded (and several methods below do check that settings really are loaded)
        except:
            pass

    def createsettingsdict(self):# Here is where an empty settings dictionary is defined, NOTE! byte strings in dictionary
        dictionary = midvatten_defs.settingsdict()
        return dictionary

    def loadSettings(self):# settingsdict is a dictionary belonging to instance midvsettings. Must be stored and loaded here.
        """read plugin settings from QgsProject instance"""
        self.settingsdict = self.createsettingsdict()
        self.readingSettings = True  
        # map data types to function names
        prj = QgsProject.instance()
        functions = {'str' : prj.readEntry,
                     'str' : prj.readEntry, # SIP API UPDATE 2.0
                     'int' : prj.readNumEntry,
                     'float' : prj.readDoubleEntry,
                     'bool' : prj.readBoolEntry,
                     'datetime' : prj.readDoubleEntry, # we converted datetimes to float in writeSetting()
                     'list' : prj.readListEntry, # SIP API UPDATE 2.0
                     'pyqtWrapperType' : prj.readListEntry # strange name for QStringList
                     }
        output = {}
        for (key, value) in list(self.settingsdict.items()):
            dataType = type(value).__name__
            try:
                func = functions[dataType]
                output[key] = func("Midvatten", key)
                self.settingsdict[key] = output[key][0]
            except KeyError:
                MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('midvsettings', "Settings key %s does not exist in project file. Maybe this file was last used with old Midvatten plugin?")) % (str(key)))
        self.readingSettings = False
        self.settingsareloaded = True

    def reset_settings(self):    
        self.settingsdict = self.createsettingsdict()    # calling for the method that defines an empty dictionary of settings

    def save_settings(self, key=None):# settingsdict is a dictionary belonging to instance midvatten. Must be stored and loaded here.
        if not self.readingSettings:
            if key is None:
                # if no argument, then save all settings according to dictionary
                for _key in list(self.settingsdict.keys()):
                    self.save_settings(_key)
            else:
                # otherwise only save specific setting as per given key
                value = self.settingsdict[key]
                if isinstance(value, float):
                    save_func = QgsProject.instance().writeEntryDouble
                else:
                    save_func = QgsProject.instance().writeEntry

                try:
                    save_func("Midvatten", key, value)
                except:
                    try:
                        print("debug info; midvsettings.save_settings failed, key: '{}', value '{}', value type: '{}', msg:\n{}".format(
                            key, str(value), str(type(value)), traceback.format_exc()))
                    except:
                        pass