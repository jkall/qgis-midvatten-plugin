# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This file contains dictionaries, lists and variable definitions for the Midvatten plugin. 
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
#from PyQt4 import QtCore, QtGui
#from qgis.core import *
#from qgis.gui import *
#import sys

def settingsdict():    #These are the default settings, they shall not be changed!!!
    dictionary = { 'database' : '',
            'tstable' : 'w_levels',
            'tscolumn' : 'level_masl',
            'tsdotmarkers' : 0,
            'tsstepplot' : 0,
            'xytable' : 'seismic_data',
            'xy_xcolumn' : 'length',
            'xy_y1column' : 'ground',
            'xy_y2column' : 'bedrock',
            'xy_y3column' : '',
            'xydotmarkers' : 0,
            'stratigraphytable' : 'stratigraphy',
            'wqualtable' : 'w_qual_lab',
            'wqual_paramcolumn' : 'parameter',
            'wqual_valuecolumn' : 'reading_txt',
            'wqual_unitcolumn' : 'unit',
            'wqual_sortingcolumn' : 'report',
            'tabwidget' : 0,
            'secplotwlvltab' : 'w_levels',
            'secplotdates' : [],
            'secplottext' : '',
            'secplotcolor':'geoshort',
            'secplotdrillstop':'',
            'secplotbw':2
            }
    return dictionary
    
def default_layers ():        #These may be changed
    list = ['obs_lines', 'obs_points', 'obs_p_w_qual_field', 'obs_p_w_qual_lab', 'obs_p_w_lvl', 'obs_p_w_strat', 'w_lvls_last_geom']    # This should be a list with all relevant tables and views that are to be loaded
    return list

def default_nonspatlayers():            # These may be changed
    list =  ['stratigraphy', 'w_levels', 'w_flow', 'w_qual_lab', 'w_qual_field']
    return list
    
def default_layers_w_ui():
    list = ['obs_lines', 'obs_points', 'w_lvls_last_geom']
    return list
    
def geocolorsymbols():    # THIS IS WHERE YOU SHALL CHANGE TO YOUR OWN GEOLOGIC CODES, SYMBOLS AND COLORS
    dictionary  = { '': ('NoBrush', 'white'),
                ' ': ('NoBrush', 'white'),
                'berg': ('DiagCrossPattern', 'red'),
                'Berg': ('DiagCrossPattern', 'red'),
                'BERG': ('DiagCrossPattern', 'red'),
                'BERG': ('DiagCrossPattern', 'red'),
                'B': ('DiagCrossPattern', 'red'),
                'Rock': ('DiagCrossPattern', 'red'),
                'rock': ('DiagCrossPattern', 'red'),
                'Ro': ('DiagCrossPattern', 'red'),
                'ro': ('DiagCrossPattern', 'red'),
                'grovgrus': ('Dense6Pattern', 'darkGreen'),
                'Grovgrus': ('Dense6Pattern', 'darkGreen'),
                'Grg': ('Dense6Pattern', 'darkGreen'),
                'grg': ('Dense6Pattern', 'darkGreen'),
                'Coarse Gravel': ('Dense6Pattern', 'darkGreen'),
                'coarse Gravel': ('Dense6Pattern', 'darkGreen'),
                'coarse gravel': ('Dense6Pattern', 'darkGreen'),
                'CGr': ('Dense6Pattern', 'darkGreen'),
                'Cgr': ('Dense6Pattern', 'darkGreen'),
                'cGr': ('Dense6Pattern', 'darkGreen'),
                'cgr': ('Dense6Pattern', 'darkGreen'),
                'grus': ('Dense6Pattern', 'darkGreen'),
                'Grus': ('Dense6Pattern', 'darkGreen'),
                'GRUS': ('Dense6Pattern', 'darkGreen'),
                'Gr': ('Dense6Pattern', 'darkGreen'),
                'gr': ('Dense6Pattern', 'darkGreen'),
                'Gravel': ('Dense6Pattern', 'darkGreen'),
                'gravel': ('Dense6Pattern', 'darkGreen'),
                'mellangrus': ('Dense5Pattern', 'darkGreen'),
                'Mellangrus': ('Dense5Pattern', 'darkGreen'),
                'MELLANGRUS': ('Dense5Pattern', 'darkGreen'),
                'Grm': ('Dense5Pattern', 'darkGreen'),
                'grm': ('Dense5Pattern', 'darkGreen'),
                'Medium Gravel': ('Dense5Pattern', 'darkGreen'),
                'medium Gravel': ('Dense5Pattern', 'darkGreen'),
                'medium gravel': ('Dense5Pattern', 'darkGreen'),
                'MGr': ('Dense5Pattern', 'darkGreen'),
                'mGr': ('Dense5Pattern', 'darkGreen'),
                'Mgr': ('Dense5Pattern', 'darkGreen'),
                'mgr': ('Dense5Pattern', 'darkGreen'),
                'fingrus': ('Dense5Pattern', 'darkGreen'),
                'Fingrus': ('Dense5Pattern', 'darkGreen'),
                'FINGRUS': ('Dense5Pattern', 'darkGreen'),
                'Grf': ('Dense5Pattern', 'darkGreen'),
                'grf': ('Dense5Pattern', 'darkGreen'),
                'Fine Gravel': ('Dense5Pattern', 'darkGreen'),
                'fine Gravel': ('Dense5Pattern', 'darkGreen'),
                'fine gravel': ('Dense5Pattern', 'darkGreen'),
                'FGr': ('Dense5Pattern', 'darkGreen'),
                'Fgr': ('Dense5Pattern', 'darkGreen'),
                'fGr': ('Dense5Pattern', 'darkGreen'),
                'fgr': ('Dense5Pattern', 'darkGreen'),
                'grovsand': ('Dense4Pattern', 'green'),
                'Grovsand': ('Dense4Pattern', 'green'),
                'GROVSAND': ('Dense4Pattern', 'green'),
                'Sag': ('Dense4Pattern', 'green'),
                'sag': ('Dense4Pattern', 'green'),
                'Coarse Sand': ('Dense4Pattern', 'green'),
                'coarse Sand': ('Dense4Pattern', 'green'),
                'coarse sand': ('Dense4Pattern', 'green'),
                'CSa': ('Dense4Pattern', 'green'),
                'Csa': ('Dense4Pattern', 'green'),
                'cSa': ('Dense4Pattern', 'green'),
                'csa': ('Dense4Pattern', 'green'),
                'sand': ('Dense4Pattern', 'green'),
                'Sand': ('Dense4Pattern', 'green'),
                'SAND': ('Dense4Pattern', 'green'),
                'Sa': ('Dense4Pattern', 'green'),
                'sa': ('Dense4Pattern', 'green'),
                'mellansand': ('FDiagPattern', 'green'),
                'Mellansand': ('FDiagPattern', 'green'),
                'MELLANSAND': ('FDiagPattern', 'green'),
                'Sam': ('FDiagPattern', 'green'),
                'sam': ('FDiagPattern', 'green'),
                'Medium Sand': ('FDiagPattern', 'green'),
                'medium Sand': ('FDiagPattern', 'green'),
                'medium sand': ('FDiagPattern', 'green'),
                'MSa': ('FDiagPattern', 'green'),
                'Msa': ('FDiagPattern', 'green'),
                'msa': ('FDiagPattern', 'green'),
                'mSa': ('FDiagPattern', 'green'),
                'finsand': ('BDiagPattern', 'yellow'),
                'Finsand': ('BDiagPattern', 'yellow'),
                'FINSAND': ('BDiagPattern', 'yellow'),
                'Saf': ('BDiagPattern', 'yellow'),
                'saf': ('BDiagPattern', 'yellow'),
                'Fine Sand': ('BDiagPattern', 'yellow'),
                'fine Sand': ('BDiagPattern', 'yellow'),
                'fine Sand': ('BDiagPattern', 'yellow'),
                'FSa': ('BDiagPattern', 'yellow'),
                'Fsa': ('BDiagPattern', 'yellow'),
                'fSa': ('BDiagPattern', 'yellow'),
                'fsa': ('BDiagPattern', 'yellow'),
                'silt': ('VerPattern', 'yellow'),
                'Silt': ('VerPattern', 'yellow'),
                'SILT': ('VerPattern', 'yellow'),
                'Si': ('VerPattern', 'yellow'),
                'si': ('VerPattern', 'yellow'),
                'lera': ('HorPattern', 'darkYellow'),
                'Lera': ('HorPattern', 'darkYellow'),
                'LERA': ('HorPattern', 'darkYellow'),
                'Le': ('HorPattern', 'darkYellow'),
                'le': ('HorPattern', 'darkYellow'),
                'Clay': ('HorPattern', 'darkYellow'),
                'clay': ('HorPattern', 'darkYellow'),
                'Cl': ('HorPattern', 'darkYellow'),
                'cl': ('HorPattern', 'darkYellow'),
                'moran': ('CrossPattern', 'cyan'),
                'Moran': ('CrossPattern', 'cyan'),
                'MORAN': ('CrossPattern', 'cyan'),
                'Mn': ('CrossPattern', 'cyan'),
                'mn': ('CrossPattern', 'cyan'),
                'Till': ('CrossPattern', 'cyan'),
                'till': ('CrossPattern', 'cyan'),
                'Ti': ('CrossPattern', 'cyan'),
                'ti': ('CrossPattern', 'cyan'),
                'torv': ('NoBrush', 'darkGray'),
                'Torv': ('NoBrush', 'darkGray'),
                'TORV': ('NoBrush', 'darkGray'),
                'T': ('NoBrush', 'darkGray'),
                'Peat': ('NoBrush', 'darkGray'),
                'peat': ('NoBrush', 'darkGray'),
                'Pt': ('NoBrush', 'darkGray'),
                'pt': ('NoBrush', 'darkGray'),
                't': ('NoBrush', 'darkGray'),
                'fyll': ('DiagCrossPattern', 'white'),
                'Fyll': ('DiagCrossPattern', 'white'),
                'FYLL': ('DiagCrossPattern', 'white'),
                'fyllning': ('DiagCrossPattern', 'white'),
                'Fyllning': ('DiagCrossPattern', 'white'),
                'FYLLNING': ('DiagCrossPattern', 'white'),
                'F': ('DiagCrossPattern', 'white'),
                'f': ('DiagCrossPattern', 'white'),
                'Made Ground': ('DiagCrossPattern', 'white'),
                'Made ground': ('DiagCrossPattern', 'white'),
                'mage ground': ('DiagCrossPattern', 'white'),
                'MG': ('DiagCrossPattern', 'white'),
                'Mg': ('DiagCrossPattern', 'white'),
                'mg': ('DiagCrossPattern', 'white')
                }
    return dictionary
    
def hydrocolors(): # THIS IS WHERE YOU SHALL CHANGE TO YOUR OWN capacity CODES AND COLORS
    dictionary = { '': ('okant', 'gray'),
                  ' ': ('okant', 'gray'),
                  '0': ('okant', 'gray'),
                  '0 ': ('okant', 'gray'),
                  '1': ('ovan gvy', 'red'),
                  '1 ': ('ovan gvy', 'red'),
                  '2': ('ingen', 'magenta'),
                  '2 ': ('ingen', 'magenta'),
                  '3-': ('obetydlig', 'yellow'),
                  '3': ('obetydlig', 'yellow'),
                  '3 ': ('obetydlig', 'yellow'),
                  '3+': ('obetydlig', 'darkYellow'),
                  '4-': ('mindre god', 'green'),
                  '4': ('mindre god', 'green'),
                  '4 ': ('mindre god', 'green'),
                  '4+': ('mindre god', 'darkGreen'),
                  '5-': ('god', 'cyan'),
                  '5': ('god', 'cyan'),
                  '5 ': ('god', 'cyan'),
                  '5+': ('god', 'darkCyan'),
                  '6-': ('mycket god', 'blue'),
                  '6': ('mycket god', 'blue'),
                  '6 ': ('mycket god', 'blue'),
                  '6+': ('mycket god', 'darkBlue'),
                }
    return dictionary

def stratitable(): # THIS IS THE NAME OF THE table WITH stratigraphy _ MUST NOT BE CHANGED
    return 'stratigraphy'
