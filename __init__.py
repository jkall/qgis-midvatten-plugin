# -*- coding: utf-8 -*-
"""
/***************************************************************************
  Midvatten
                                 A QGIS plugin
 This is mainly a toolset collecting existing funcions and plugins:
 - ARPAT (by Martin Dobias) in an adjusted version reading SQLite data
 - TimeSeries Plot (an earlier plugin that will be replaced by this toolset)
 - and a new function ScatterPlot (appropriate for ploting geophysical profiles, e.g. seismic data along a line)
 - ChartMaker in an adjusted version reading SQLite data
 
 The toolset is developed at the company Midvatten AB and aims to to be used within projects at Midvatten AB.
 The main purpose is to let the user quickly access and view different types of hydrogeological data that is stored in a sqlite Database
  
                             -------------------
        begin                : 2012-03-05
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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    from midvatten import midvatten
    return midvatten(iface)
