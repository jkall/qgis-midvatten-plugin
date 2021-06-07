# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Util Translator
Description          : Add translation
Date                 : July, 2017
copyright            : (C) 2017 by Luiz Motta
email                : motta.luiz@gmail.com

 ***************************************************************************/
 
 /***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

For create file 'qm'
1) Define that files need for translation: PLUGIN_NAME.pro
2) Create 'ts': pylupdate4 -verbose PLUGIN_NAME.pro
3) Edit your translation: QtLinquist
4) Create 'qm': lrelease PLUGIN_NAME_LOCALE.ts (Ex.: _pt_BR)

"""
import glob
import os

from qgis.PyQt.QtCore import QFileInfo, QSettings, QLocale, QTranslator, QCoreApplication
from qgis.core import QgsApplication, Qgis


def getTranslate(namePlugin, nameDir=None):
    if nameDir is None:
      nameDir = namePlugin

    pluginPath = os.path.join('python', 'plugins', nameDir)

    userPath = QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path()
    userPluginPath = os.path.join(userPath, pluginPath)
    
    systemPath = QgsApplication.prefixPath()
    systemPluginPath = os.path.join(systemPath, pluginPath)

    pp = userPluginPath if QFileInfo(userPluginPath).exists() else systemPluginPath

    overrideLocale = QSettings().value('locale/overrideFlag', False, type=bool)
    if overrideLocale:
        qmPathFilepattern = os.path.join('i18n', '{0}_{1}_*.qm'.format(namePlugin, QSettings().value('locale/userLocale', '')))

        qmfiles = glob.glob(os.path.join(pp, qmPathFilepattern))
        if qmfiles:
            translationFile = sorted(qmfiles)[0]
            QgsApplication.messageLog().logMessage(
                ("QGIS location overried is activated. Using the first found translationfile for pattern {}.".format(qmPathFilepattern)),
                'Midvatten',
                level=Qgis.Info)
        else:
            QgsApplication.messageLog().logMessage(
                ("QGIS location overried is activated. No translation file found using pattern {}, no translation file installed!".format(qmPathFilepattern)),
                'Midvatten',
                level=Qgis.Info)
            return
    else:
        localeFullName = QLocale.system().name()
        qmPathFile = os.path.join('i18n', '{0}_{1}.qm'.format(namePlugin, localeFullName))
        translationFile = os.path.join(pp, qmPathFile)

    if QFileInfo(translationFile).exists():
        translator = QTranslator()
        translator.load(translationFile)
        QCoreApplication.installTranslator(translator)
        QgsApplication.messageLog().logMessage(('Installed translation file {}'.format(translationFile)), 'Midvatten',
                                               level=Qgis.Info)
        return translator
    else:
        QgsApplication.messageLog().logMessage(
            ("translationFile {} didn't exist, no translation file installed!".format(translationFile)), 'Midvatten',
                                               level=Qgis.Info)
