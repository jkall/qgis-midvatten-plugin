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
from __future__ import print_function
from builtins import str

from collections import OrderedDict
import os
import io
from cycler import cycler

import db_utils
import midvatten_utils as utils
from qgis.PyQt.QtCore import QCoreApplication
from midvatten_utils import returnunicode as ru


def settingsdict():    #These are the default settings, they shall not be changed!!!
    dictionary = { 'database' : '',
            'temp_postgis_passwords': '',
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
            'stratigraphytable' : 'stratigraphy', #TODO: Remove this and fix the references
            'wqualtable' : 'w_qual_lab',
            'wqual_paramcolumn' : 'parameter',
            'wqual_valuecolumn' : 'reading_txt',
            'wqual_date_time_format' : 'YYYY-MM-DD',
            'wqual_unitcolumn' : 'unit',
            'wqual_sortingcolumn' : '',
            'tabwidget' : 0,
            'secplotwlvltab' : 'w_levels',
            'secplotdates' : [],
            'secplottext' : '',
            'secplotdrillstop':'',
            'secplotbw':2,
            'secplotlocation':8,
            'secplotselectedDEMs':[],
            'stratigraphyplotted':True,
            'secplothydrologyplotted':False,
            'secplotlabelsplotted':True,
            'secplotlegendplotted':True,
            'secplot_loaded_template': '',
            'secplot_templates': '',
            'secplotwidthofplot': 1,
            'secplotincludeviews': False,
            'settingslocation':1,
            'compactwqualreport':'',
            'custplot_tabwidget':0,
            'custplot_table1':'w_levels',
            'custplot_table2':'',
            'custplot_table3':'',
            'custplot_xcol1':'date_time',
            'custplot_xcol2':'',
            'custplot_xcol3':'',
            'custplot_ycol1':'level_masl',
            'custplot_ycol2':'',
            'custplot_ycol3':'',
            'custplot_maxtstep':0.0,
            'custplot_title':'',
            'custplot_xtitle':'',
            'custplot_ytitle':'',
            'custplot_legend':1,
            'custplot_grid':1,
            'custplot_filter1_1':'',
            'custplot_filter2_1':'',            
            'custplot_filter1_2':'',
            'custplot_filter2_2':'',            
            'custplot_filter1_3':'',
            'custplot_filter2_3':'',
            'custplot_filter1_1_selection':[],            
            'custplot_filter2_1_selection':[],            
            'custplot_filter1_2_selection':[],            
            'custplot_filter2_2_selection':[],            
            'custplot_filter1_3_selection':[],            
            'custplot_filter2_3_selection':[],
            'custplot_plottype1':'line',
            'custplot_plottype2':'line',
            'custplot_plottype3':'line',
            'custplot_last_used_template': '',
            'custplot_regular_xaxis_interval':1,
            'customdrillreportstoredsettings': '',
            'piper_cl':'Klorid, Cl',
            'piper_hco3':'Alkalinitet, HCO3',
            'piper_so4':'Sulfat, SO4',
            'piper_na':'Natrium, Na',
            'piper_k':'Kalium, K',
            'piper_ca':'Kalcium, Ca',
            'piper_mg':'Magnesium, Mg',
            'piper_markers':'type',
            'locale': '',
            'fieldlogger_import_parameter_settings': '',
            'fieldlogger_export_pgroups': '',
            'fieldlogger_export_pbrowser': '',
            'fieldlogger_export': '',
            }
    return dictionary

def geocolorsymbols():
    """
    This dictionary is used for stratigraph plots (Qt) to set color and brush style
    Default method is to read the database table zz_strat, the user may change zz_strat table to change the stratigraphy plots
    Predefined Qt colors are allowed (http://doc.qt.io/qt-4.8/qcolor.html#predefined-colors) and so is also svg 1.0 names (https://www.w3.org/TR/SVG/types.html#ColorKeywords)
    Fallback methods use color codes and brush styles found in code below
    """
    res1, dict_qt = db_utils.get_sql_result_as_dict('select strata, brush_qt, color_qt from zz_stratigraphy_plots')
    res2, dict_geo1 = db_utils.get_sql_result_as_dict('select strata, geoshort from zz_strat')
    # fallback method to maintain backwards compatibility
    if not (res1 and res2):
        # Fallback method - if using old databases where zz_strat is missing, then you may change the code below to reflect your own GEOLOGIC CODES, SYMBOLS AND COLORS
        utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate('geocolorsymbols', 'Reading zz_strat* tables failed. Using default dictionary instead'))
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
                    'grovgrus': ('Dense7Pattern', 'darkGreen'),
                    'Grovgrus': ('Dense7Pattern', 'darkGreen'),
                    'Grg': ('Dense7Pattern', 'darkGreen'),
                    'grg': ('Dense7Pattern', 'darkGreen'),
                    'Coarse Gravel': ('Dense7Pattern', 'darkGreen'),
                    'coarse Gravel': ('Dense7Pattern', 'darkGreen'),
                    'coarse gravel': ('Dense7Pattern', 'darkGreen'),
                    'CGr': ('Dense7Pattern', 'darkGreen'),
                    'Cgr': ('Dense7Pattern', 'darkGreen'),
                    'cGr': ('Dense7Pattern', 'darkGreen'),
                    'cgr': ('Dense7Pattern', 'darkGreen'),
                    'grus': ('Dense7Pattern', 'darkGreen'),
                    'Grus': ('Dense7Pattern', 'darkGreen'),
                    'GRUS': ('Dense7Pattern', 'darkGreen'),
                    'Gr': ('Dense7Pattern', 'darkGreen'),
                    'gr': ('Dense7Pattern', 'darkGreen'),
                    'Gravel': ('Dense7Pattern', 'darkGreen'),
                    'gravel': ('Dense7Pattern', 'darkGreen'),
                    'mellangrus': ('Dense6Pattern', 'darkGreen'),
                    'Mellangrus': ('Dense6Pattern', 'darkGreen'),
                    'MELLANGRUS': ('Dense6Pattern', 'darkGreen'),
                    'Grm': ('Dense6Pattern', 'darkGreen'),
                    'grm': ('Dense6Pattern', 'darkGreen'),
                    'Medium Gravel': ('Dense6Pattern', 'darkGreen'),
                    'medium Gravel': ('Dense6Pattern', 'darkGreen'),
                    'medium gravel': ('Dense6Pattern', 'darkGreen'),
                    'MGr': ('Dense6Pattern', 'darkGreen'),
                    'mGr': ('Dense6Pattern', 'darkGreen'),
                    'Mgr': ('Dense6Pattern', 'darkGreen'),
                    'mgr': ('Dense6Pattern', 'darkGreen'),
                    'fingrus': ('Dense6Pattern', 'darkGreen'),
                    'Fingrus': ('Dense6Pattern', 'darkGreen'),
                    'FINGRUS': ('Dense6Pattern', 'darkGreen'),
                    'Grf': ('Dense6Pattern', 'darkGreen'),
                    'grf': ('Dense6Pattern', 'darkGreen'),
                    'Fine Gravel': ('Dense6Pattern', 'darkGreen'),
                    'fine Gravel': ('Dense6Pattern', 'darkGreen'),
                    'fine gravel': ('Dense6Pattern', 'darkGreen'),
                    'FGr': ('Dense6Pattern', 'darkGreen'),
                    'Fgr': ('Dense6Pattern', 'darkGreen'),
                    'fGr': ('Dense6Pattern', 'darkGreen'),
                    'fgr': ('Dense6Pattern', 'darkGreen'),
                    'grovsand': ('Dense5Pattern', 'green'),
                    'Grovsand': ('Dense5Pattern', 'green'),
                    'GROVSAND': ('Dense5Pattern', 'green'),
                    'Sag': ('Dense5Pattern', 'green'),
                    'sag': ('Dense5Pattern', 'green'),
                    'Coarse Sand': ('Dense5Pattern', 'green'),
                    'coarse Sand': ('Dense5Pattern', 'green'),
                    'coarse sand': ('Dense5Pattern', 'green'),
                    'CSa': ('Dense5Pattern', 'green'),
                    'Csa': ('Dense5Pattern', 'green'),
                    'cSa': ('Dense5Pattern', 'green'),
                    'csa': ('Dense5Pattern', 'green'),
                    'sand': ('Dense5Pattern', 'green'),
                    'Sand': ('Dense5Pattern', 'green'),
                    'SAND': ('Dense5Pattern', 'green'),
                    'Sa': ('Dense5Pattern', 'green'),
                    'sa': ('Dense5Pattern', 'green'),
                    'mellansand': ('Dense4Pattern', 'green'),
                    'Mellansand': ('Dense4Pattern', 'green'),
                    'MELLANSAND': ('Dense4Pattern', 'green'),
                    'Sam': ('Dense4Pattern', 'green'),
                    'sam': ('Dense4Pattern', 'green'),
                    'Medium Sand': ('Dense4Pattern', 'green'),
                    'medium Sand': ('Dense4Pattern', 'green'),
                    'medium sand': ('Dense4Pattern', 'green'),
                    'MSa': ('Dense4Pattern', 'green'),
                    'Msa': ('Dense4Pattern', 'green'),
                    'msa': ('Dense4Pattern', 'green'),
                    'mSa': ('Dense4Pattern', 'green'),
                    'finsand': ('Dense4Pattern', 'darkYellow'),
                    'Finsand': ('Dense4Pattern', 'darkYellow'),
                    'FINSAND': ('Dense4Pattern', 'darkYellow'),
                    'Saf': ('Dense4Pattern', 'darkYellow'),
                    'saf': ('Dense4Pattern', 'darkYellow'),
                    'Fine Sand': ('Dense4Pattern', 'darkYellow'),
                    'fine Sand': ('Dense4Pattern', 'darkYellow'),
                    'fine Sand': ('Dense4Pattern', 'darkYellow'),
                    'FSa': ('Dense4Pattern', 'darkYellow'),
                    'Fsa': ('Dense4Pattern', 'darkYellow'),
                    'fSa': ('Dense4Pattern', 'darkYellow'),
                    'fsa': ('Dense4Pattern', 'darkYellow'),
                    'silt': ('BDiagPattern', 'yellow'),
                    'Silt': ('BDiagPattern', 'yellow'),
                    'SILT': ('BDiagPattern', 'yellow'),
                    'Si': ('BDiagPattern', 'yellow'),
                    'si': ('BDiagPattern', 'yellow'),
                    'lera': ('HorPattern', 'yellow'),
                    'Lera': ('HorPattern', 'yellow'),
                    'LERA': ('HorPattern', 'yellow'),
                    'Le': ('HorPattern', 'yellow'),
                    'le': ('HorPattern', 'yellow'),
                    'Clay': ('HorPattern', 'yellow'),
                    'clay': ('HorPattern', 'yellow'),
                    'Cl': ('HorPattern', 'yellow'),
                    'cl': ('HorPattern', 'yellow'),
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
    # new method create dict from db table
    #dict_geo1 is just a start, not yet populated with tuples of geoshorts for each strata, time to do so

    dictionary={}
    for strata, strata_synonyms in sorted(dict_geo1.items()):
        #In general there is only one geoshort in geoshort_as_strata_synonym
        for geoshort in strata_synonyms:
            geoshort = geoshort[0]
            try:
                dictionary[geoshort]=dict_qt[str(strata)][0]
            except Exception as a:
                try:
                    dictionary[geoshort] = dict_qt[strata][0]
                except Exception as b:
                    try:
                        dictionary[geoshort] = dict_qt[ru(strata)][0]
                    except Exception as c:
                        utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate('geocolorsymbols', 'Error in geocolorsymbols, setting brush and color for strata "%s" using geoshort %s failed. Msg1:\n%s\nMsg2:\n%s\Msg3:\n%s'))%(strata, geoshort, str(a), str(b), str(c)))
                        dictionary[geoshort]=('NoBrush', 'white')

    """
    # this was temporary method to deal with zz_stratigraphy table existing in plugin version 1.3.x
    # skip "unknown"
    dict_geo = {k: v for k, v in dict_geo1.iteritems() if 'not in' not in v}
    for key, value in sorted(dict_geo.iteritems()):
        #if 'not in' in value:
        #    print('Warning')#debug
        geoshort_string = value.replace('not in (','').replace('in (','').replace(')','').replace('\'','')
        #print(geoshort_string)#debug
        for v in geoshort_string.split(','):
            #print (key,utils.unicode_2_utf8(v), utils.unicode_2_utf8(dict_qt.get(key)[0]))#debug
            dictionary[utils.unicode_2_utf8(v)] = (utils.unicode_2_utf8(dict_qt.get(key)[0]))
    """
    return dictionary

def bedrock_geoshort():
    return 'berg' if utils.getcurrentlocale()[0] == 'sv_SE' else 'rock'

def get_subset_of_tables_fr_db(category='obs_points'):
    """returns various subsets of tables from the db, argument category is one of:
        'obs_points' - returns all tables containing observational data related to obs_points
        'obs_lines' - returns all tables containing observational data related to obs_lines
        'data_domains' - returns all tables containing various data domains, i.e. zz_tables
        'default_layers' - returns all tables that are loaded as default spatial layers in qgis
        'default_nonspatlayers'  - returns all tables that are loaded as default non-spatial layers in qgis
        'default_layers_w_ui'  - returns all tables that are loaded as default spatial layers in qgis, having a custom ui form
    """
    if category=='obs_points':
        return ['obs_points', 'comments', 'w_levels', 'w_levels_logger', 'w_flow', 'w_qual_lab', 'w_qual_field', 'stratigraphy', 'meteo']
    elif category == 'obs_lines':
        return ['obs_lines', 'vlf_data', 'seismic_data']
    elif category == 'data_domains':
        return ['zz_flowtype', 'zz_meteoparam', 'zz_staff', 'zz_strat', 'zz_stratigraphy_plots', 'zz_capacity', 'zz_capacity_plots']
    elif category == 'default_layers':
        return ['obs_lines', 'obs_points', 'obs_p_w_qual_field', 'obs_p_w_qual_lab', 'obs_p_w_lvl', 'obs_p_w_strat', 'w_lvls_last_geom']
    elif category == 'default_nonspatlayers':
        return ['stratigraphy', 'w_levels', 'w_flow', 'w_qual_lab', 'w_qual_field','comments']
    elif category == 'default_layers_w_ui':
        return ['obs_lines', 'obs_points', 'w_lvls_last_geom']
    elif category == 'stratitable':#not yet in use
        return ['stratigraphy']
    else:
        return []

def hydrocolors():
    """
    This dictionary is used for stratigraph plots (Qt) to set color depending on capacity
    Default method is to read the database table zz_capacity, the user may change zz_capacity table to change the stratigraphy plots
    Fallback methods use color codes found in code below
    """
    res, dict_qt1 = db_utils.get_sql_result_as_dict('select a.capacity, a.explanation, b.color_qt from zz_capacity a, zz_capacity_plots b where a.capacity = b.capacity')
    # fallback method to maintain backwards compatibility
    if not res:
        try:
            print('using fallback method for backwards compat.')
        except:
            pass
        utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('hydrocolors', 'Getting hydrocolors from database failed, using fallback method!')))
        dict_qt = { '': ('okant', 'gray'),
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
    else:
        dict_qt = ru({k: v[0] for k, v in dict_qt1.items()}, keep_containers=True)
    return dict_qt

def PlotTypesDict(international='no'): 
    """
    This dictionary is used by sectionplot (matplotlib) to compare with all possible geoshorts in stratigraphy table
    (Also used to generate dictionaries for stratigraphy plot (Qt))
    Default method is to read the database table zz_strat and generate the dictionary from columns 'strat' and 'geoshorts'
    The user may update these fields in the zz_strat table to use other stratigraphy units and other abbreviations (in geoshorts)
    Fallback method use dictionary defined in the code below
    """
    #success, Dict = utils.create_dict_from_db_2_cols(('strata','geoshort','zz_strat'))
    success, Dict = db_utils.get_sql_result_as_dict('select strata, geoshort from zz_strat')
    succss_strata, strata_order = db_utils.sql_load_fr_db('select strata from zz_stratigraphy_plots order by %s'%db_utils.rowid_string())
    if not success:
        utils.MessagebarAndLog.info(log_msg=QCoreApplication.translate('PlotTypesDict', 'Getting strata and geoshort from zz_strat failed, fallback method using PlotTypesDict from code'))
        if international=='no' and  utils.getcurrentlocale() == 'sv_SE':
            """
            Dict = {"Okänt" : "not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')",
            "Berg"  : "in ('berg','b','rock','ro')",
            "Grovgrus" : "in ('grovgrus','grg','coarse gravel','cgr')",
            "Grus" : "in ('grus','gr','gravel')",
            "Mellangrus" : "in ('mellangrus','grm','medium gravel','mgr')",
            "Fingrus" : "in ('fingrus','grf','fine gravel','fgr')",
            "Grovsand" : "in ('grovsand','sag','coarse sand','csa')",
            "Sand" : "in ('sand','sa')",
            "Mellansand" : "in ('mellansand','sam','medium sand','msa')",
            "Finsand" : "in ('finsand','saf','fine sand','fsa')",
            "Silt" : "in ('silt','si')",
            "Lera" : "in ('lera','ler','le','clay','cl')",
            "Morän" : "in ('morän','moran','mn','till','ti')",
            "Torv" : "in ('torv','t','peat','pt')",
            "Fyll":"in ('fyll','fyllning','f','made ground','mg','land fill')"}
            """
            dictionary = OrderedDict([("Okänt" , "not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')"),
            ("Berg"  , "in ('berg','b','rock','ro')"),
            ("Grovgrus" , "in ('grovgrus','grg','coarse gravel','cgr')"),
            ("Grus" , "in ('grus','gr','gravel')"),
            ("Mellangrus" , "in ('mellangrus','grm','medium gravel','mgr')"),
            ("Fingrus" , "in ('fingrus','grf','fine gravel','fgr')"),
            ("Grovsand" , "in ('grovsand','sag','coarse sand','csa')"),
            ("Sand" , "in ('sand','sa')"),
            ("Mellansand" , "in ('mellansand','sam','medium sand','msa')"),
            ("Finsand" , "in ('finsand','saf','fine sand','fsa')"),
            ("Silt" , "in ('silt','si')"),
            ("Lera" , "in ('lera','ler','le','clay','cl')"),
            ("Morän" , "in ('morän','moran','mn','till','ti')"),
            ("Torv" , "in ('torv','t','peat','pt')"),
            ("Fyll","in ('fyll','fyllning','f','made ground','mg','land fill')")])
        else:
            """
            Dict = {"Unknown" : "not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')",
            "Rock"  : "in ('berg','b','rock','ro')",
            "Coarse gravel" : "in ('grovgrus','grg','coarse gravel','cgr')",
            "Gravel" : "in ('grus','gr','gravel')",
            "Medium gravel" : "in ('mellangrus','grm','medium gravel','mgr')",
            "Fine gravel" : "in ('fingrus','grf','fine gravel','fgr')",
            "Coarse sand" : "in ('grovsand','sag','coarse sand','csa')",
            "Sand" : "in ('sand','sa')",
            "Medium sand" : "in ('mellansand','sam','medium sand','msa')",
            "Fine sand" : "in ('finsand','saf','fine sand','fsa')",
            "Silt" : "in ('silt','si')",
            "Clay" : "in ('lera','ler','le','clay','cl')",
            "Till" : "in ('morän','moran','mn','till','ti')",
            "Peat" : "in ('torv','t','peat','pt')",
            "Fill":"in ('fyll','fyllning','f','made ground','mg','land fill')"}
            """
            dictionary = OrderedDict([("Unknown" , "not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')"),
            ("Rock"  , "in ('berg','b','rock','ro')"),
            ("Coarse gravel" , "in ('grovgrus','grg','coarse gravel','cgr')"),
            ("Gravel" , "in ('grus','gr','gravel')"),
            ("Medium gravel" , "in ('mellangrus','grm','medium gravel','mgr')"),
            ("Fine gravel" , "in ('fingrus','grf','fine gravel','fgr')"),
            ("Coarse sand" , "in ('grovsand','sag','coarse sand','csa')"),
            ("Sand" , "in ('sand','sa')"),
            ("Medium sand" , "in ('mellansand','sam','medium sand','msa')"),
            ("Fine sand" , "in ('finsand','saf','fine sand','fsa')"),
            ("Silt" , "in ('silt','si')"),
            ("Clay" , "in ('lera','ler','le','clay','cl')"),
            ("Till" , "in ('morän','moran','mn','till','ti')"),
            ("Peat" , "in ('torv','t','peat','pt')"),
            ("Fill","in ('fyll','fyllning','f','made ground','mg','land fill')")])
    else:
        """manually create dictionary to reuse old code"""
        dictionary = OrderedDict({})
        #all_geoshorts = r"""not in ('"""
        #for key, value in sorted(Dict.iteritems()):

        for strata in strata_order:
            tl = r"""in ('"""
            if strata[0] in Dict:
                for geoshort in Dict[strata[0]]:
                    tl+=geoshort[0] + r"""', '"""
                    #all_geoshorts+=geoshort[0] + r"""', '"""
                tl = utils.rstrip(r""", '""",tl) + r""")"""
                #all_geoshorts = utils.rstrip(r""", '""",all_geoshorts) + r""")"""
                dictionary[strata[0]]=tl
        #all_geoshorts+=r"""')"""
    return dictionary

def PlotColorDict():
    """
    This dictionary is used by sectionplot (matplotlib) for relating the geoshort names with color codes
    The user may update these fields in the zz_strat table to use other colors
    Fallback method use dictionary defined in the code below
    """
    success, Dict = utils.create_dict_from_db_2_cols(('strata','color_mplot','zz_stratigraphy_plots'))
    if not success:
        utils.MessagebarAndLog.info(log_msg=QCoreApplication.translate('PlotColorDict', 'Getting strata and color_mplot form zz_stratigraphy_plots failed, fallback method with PlotColorDict from code'))
        if  utils.getcurrentlocale() == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {"Okänt" : "white",
            "Berg"  : "red",
            "Grovgrus" : "DarkGreen",
            "Grus" : "DarkGreen",
            "Mellangrus" : "DarkGreen",
            "Fingrus" : "DarkGreen",
            "Grovsand" : "green",
            "Sand" : "green",
            "Mellansand" : "green",
            "Finsand" : "DarkOrange",
            "Silt" : "yellow",
            "Lera" : "yellow",
            "Morän" : "cyan",
            "Torv" : "DarkGray",
            "Fyll":"white"}
        else:
            Dict = {"Unknown" : "white",
            "Rock"  : "red",
            "Coarse gravel" : "DarkGreen",
            "Gravel" : "DarkGreen",
            "Medium gravel" : "DarkGreen",
            "Fine gravel" : "DarkGreen",
            "Coarse sand" : "green",
            "Sand" : "green",
            "Medium sand" : "green",
            "Fine sand" : "DarkOrange",
            "Silt" : "yellow",
            "Clay" : "yellow",
            "Till" : "cyan",
            "Peat" : "DarkGray",
            "Fill":"white"}
    #print Dict#debug!
    Dict = {k.lower(): v for k, v in Dict.items()}
    return Dict

def PlotHatchDict():
    """
    This dictionary is used by sectionplot (matplotlib) for relating the geoshort names with hatches in plots
    The user may update these fields in the zz_strat table to use other hatches
    Fallback method use dictionary defined in the code below
    """
    success, Dict = utils.create_dict_from_db_2_cols(('strata','hatch_mplot','zz_stratigraphy_plots'))
    if not success:
        utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate('PlotHatchDict', 'Getting strata and hatch_mplot from zz_stratigraphy_plots failed, fallback method with PlotHatchDict from code'))
        # hatch patterns : ('-', '+', 'x', '\\', '*', 'o', 'O', '.','/')
        if  utils.getcurrentlocale() == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {"Okänt" : "",
            "Berg"  : "x",
            "Grovgrus" : "O",
            "Grus" : "O",
            "Mellangrus" : "o",
            "Fingrus" : "o",
            "Grovsand" : "*",
            "Sand" : "*",
            "Mellansand" : ".",
            "Finsand" : ".",
            "Silt" : "\\",
            "Lera" : "-",
            "Morän" : "/",
            "Torv" : "+",
            "Fyll":"+"}
        else:
            Dict = {"Unknown" : "",
            "Rock"  : "x",
            "Coarse gravel" : "O",
            "Gravel" : "O",
            "Medium gravel" : "o",
            "Fine gravel" : "o",
            "Coarse sand" : "*",
            "Sand" : "*",
            "Medium sand" : ".",
            "Fine sand" : ".",
            "Silt" : "\\",
            "Clay" : "-",
            "Till" : "/",
            "Peat" : "+",
            "Fill":"+"}
    Dict = {k.lower(): v for k, v in Dict.items()}
    return Dict

def staff_list():
    """
    :return: A list of staff members from the staff table
    """
    sql = 'SELECT distinct staff from zz_staff'
    sql_result = db_utils.sql_load_fr_db(sql)
    connection_ok, result_list = sql_result

    if not connection_ok:
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('staff_list', 'Sql failed, see log message panel'), log_msg=ru(QCoreApplication.translate('staff_list', 'Failed to get existing staff from staff table from sql %s'))%sql)
        return False, tuple()

    return True, ru(tuple([x[0] for x in result_list]), True)

def stratigraphy_table():
    return 'stratigraphy'

def w_flow_flowtypes_units():
    sql = 'select distinct flowtype, unit from w_flow'
    connection_ok, result_dict = db_utils.get_sql_result_as_dict(sql)

    if not connection_ok:
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('w_flow_flowtypes_units', "Error, sql failed, see log message panel"), log_msg=ru(QCoreApplication.translate('w_flow_flowtypes_units', 'Cannot get data from sql %s'))%ru(sql))
        return {}

    return ru(result_dict, keep_containers=True)

def w_qual_field_parameter_units():
    sql = 'select distinct parameter, unit from w_qual_field'
    connection_ok, result_dict = db_utils.get_sql_result_as_dict(sql)

    if not connection_ok:
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate('w_qual_field_parameter_units', 'Error, sql failed, see log message panel'), log_msg=ru(QCoreApplication.translate('w_qual_field_parameter_units', 'Cannot get data from sql %s'))%ru(sql))
        return {}

    return ru(result_dict, keep_containers=True)


def get_last_used_quality_instruments():
    """
    Returns quality instrumentids
    :return: A tuple with instrument ids from w_qual_field
    """
    sql = '''select parameter, unit, instrument, staff, max(date_time) from w_qual_field group by parameter, unit,
             instrument, staff order by parameter, date_time desc, unit asc, staff'''
    connection_ok, result = db_utils.sql_load_fr_db(sql)

    result_dict = {}
    # create dict like {parameter: {staff: [row]}, staff list ordered by parameter, staff, data_time (unit).
    [result_dict.setdefault(row[0], {}).setdefault(row[3], []).append(row) for row in result]

    return ru(result_dict, True)

specific_table_info = {'obs_lines': 'The geometry column supports WKT ("well known text") of type LINESTRING and\nthe geometries must correspond to SRID in the database.',
                       'obs_points': 'The geometry column supports WKT ("well known text") of type POINT and\nthe geometries must correspond to SRID in the database.'}

def export_fieldlogger_defaults():
    current_locale = utils.getcurrentlocale()[0]

    if current_locale != 'sv_SE':
        input_field_browser =  [
            [0, (("input_field_list",[
            "Accvol.m3;numberDecimal|numberSigned; ",
            "DO.mg/L;numberDecimal|numberSigned; ",
            "Momflow.l/s;numberDecimal|numberSigned; ",
            "Momflow.m3/h;numberDecimal|numberSigned; ",
            "comment;text;Obsid related comment",
            "cond.µS/cm;numberDecimal|numberSigned; ",
            "f.comment;text;Measurement related comment",
            "l.comment;text;Measurement related comment",
            "meas.m;numberDecimal|numberSigned;depth to water",
            "pH;numberDecimal|numberSigned; ",
            "q.comment;text;Measurement related comment",
            "redox.mV;numberDecimal|numberSigned; ",
            "s.comment;text;Measurement related comment",
            "temp.°C;numberDecimal|numberSigned; ",
            "turb.FNU;numberDecimal|numberSigned; "
            ]),)]]
        input_fields_groups = [
            [0, (("input_field_group_list",
                  ["meas.m;numberDecimal|numberSigned;depth to water",
                   "l.comment;text;Measurement related comment"]),
                ("sublocation_suffix", "level"))],
            [1, (("input_field_group_list",
                  ["comment;text;Obsid related comment"]),
                 ("sublocation_suffix", "comment"))],
            [2, (("input_field_group_list",
                  ["cond.µS/cm;numberDecimal|numberSigned; ",
                   "DO.mg/L;numberDecimal|numberSigned; ",
                   "pH;numberDecimal|numberSigned; ",
                   "redox.mV;numberDecimal|numberSigned; ",
                   "temp.°C;numberDecimal|numberSigned; ",
                   "turb.FNU;numberDecimal|numberSigned; ",
                   "q.comment;text;Measurement related comment"]),
                 ("sublocation_suffix", "quality"))],
            [3, (("input_field_group_list",
                  ["temp.°C;numberDecimal|numberSigned; ",
                   "turb.FNU;numberDecimal|numberSigned; ",
                   "s.comment;text;Measurement related comment"]),
                 ("sublocation_suffix", "sample"))],
            [4, (("input_field_group_list",
                  ["Accvol.m3;numberDecimal|numberSigned; ",
                   "Momflow.l/s;numberDecimal|numberSigned; ",
                   "Momflow.m3/h;numberDecimal|numberSigned; ",
                   "f.comment;text;Measurement related comment"]),
                 ("sublocation_suffix", "flow"))]]
    else:
        input_field_browser = [[0, (("input_field_list", [
            "Accvol.m3;numberDecimal|numberSigned; ",
            "DO.mg/L;numberDecimal|numberSigned; ",
            "Momflow.l/s;numberDecimal|numberSigned; ",
            "Momflow.m3/h;numberDecimal|numberSigned; ",
            "f.kommentar;text;mätrelaterad kommentar",
            "k.kommentar;text;mätrelaterad kommentar",
            "kommentar;text;obsidrelaterad kommentar",
            "kond.µS/cm;numberDecimal|numberSigned; ",
            "meas.m;numberDecimal|numberSigned;djup till vatten",
            "n.kommentar;text;mätrelaterad kommentar",
            "nedmätning.m;numberDecimal|numberSigned;djup till vatten",
            "p.kommentar;text;mätrelaterad kommentar", "pH;numberDecimal|numberSigned; ",
            "redox.mV;numberDecimal|numberSigned; ", "temp.°C;numberDecimal|numberSigned; ",
            "turb.FNU;numberDecimal|numberSigned; "
            ], ), )]]

        input_fields_groups = [
            [0, (("input_field_group_list",
               ["nedmätning.m;numberDecimal|numberSigned;djup till vatten",
                "n.kommentar;text;mätrelaterad kommentar"]),
              ("sublocation_suffix", "nivå"))],
            [1, (("input_field_group_list",
                  ["kommentar;text;obsidrelaterad kommentar"]),
                 ("sublocation_suffix", "kommentar"))],
            [2, (("input_field_group_list",
                  ["kond.µS/cm;numberDecimal|numberSigned; ",
                   "DO.mg/L;numberDecimal|numberSigned; ",
                   "pH;numberDecimal|numberSigned; ",
                   "redox.mV;numberDecimal|numberSigned; ",
                   "temp.°C;numberDecimal|numberSigned; ",
                   "turb.FNU;numberDecimal|numberSigned; ",
                   "k.kommentar;text;mätrelaterad kommentar"]),
                 ("sublocation_suffix", "kvalitet"))],
            [3, (("input_field_group_list",
                  ["temp.°C;numberDecimal|numberSigned; ",
                   "turb.FNU;numberDecimal|numberSigned; ",
                   "p.kommentar;text;mätrelaterad kommentar"]),
                 ("sublocation_suffix", "prov"))],
            [4, (("input_field_group_list",
                  ["Accvol.m3;numberDecimal|numberSigned; ",
                   "Momflow.l/s;numberDecimal|numberSigned; ",
                   "Momflow.m3/h;numberDecimal|numberSigned; ",
                   "f.kommentar;text;mätrelaterad kommentar"],),
                 ("sublocation_suffix", "flöde"))]]

    input_field_browser = utils.anything_to_string_representation(input_field_browser)
    input_fields_groups = utils.anything_to_string_representation(input_fields_groups)
    return input_field_browser, input_fields_groups

def db_setup_as_string():
    tables = db_utils.get_tables()
    #tables = db_utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name in""" + db_utils.sqlite_internal_tables() + r""") ORDER BY tbl_name""")[1]
    res = []
    for table in sorted(tables):
        res.append((table,))
        table_info = db_utils.get_table_info(table)
        res.append(table_info)
    return utils.anything_to_string_representation(res)

def secplot_default_template():
        loaded_template = {}
        loaded_template['ticklabels_Text_set_fontsize'] = {'fontsize': 10}
        loaded_template['Axes_set_xlabel'] = {
            'xlabel': ru(QCoreApplication.translate('SectionPlot', "Distance along section")),
            'fontsize': 10}
        loaded_template['Axes_set_xlabel_stratplot'] = {
            'xlabel': ru(QCoreApplication.translate('SectionPlot', "Observation Location Code")),
            'fontsize': 10}
        loaded_template['Axes_set_xlim'] = None  # Tuple like (min, max)
        loaded_template['Axes_set_ylim'] = None  # Tuple like (min, max)
        loaded_template['Axes_set_ylabel'] = {
            'ylabel': ru(QCoreApplication.translate('SectionPlot', "Level, masl")),
            'fontsize': 10}
        loaded_template['dems_Axes_plot'] = {'DEFAULT': {'marker': 'None',
                                                              'linestyle': '-',
                                                              'linewidth': 1}}
        loaded_template['drillstop_Axes_plot'] = {'marker': '^',
                                                       'markersize': 8,
                                                       'linestyle': '',
                                                       'color': 'black'}
        loaded_template['geology_Axes_bar'] = {'edgecolor': 'black'}
        loaded_template['grid_Axes_grid'] = {'b': True,
                                                  'which': 'both',
                                                  'color': '0.65',
                                                  'linestyle': '-'}
        loaded_template['layer_Axes_annotate'] = {'xytext': (5, 0),
                                                       'textcoords': 'offset points',
                                                       'ha': 'left',
                                                       'va': 'center',
                                                       'fontsize': 9,
                                                       'bbox': {'boxstyle': 'square,pad=0.05',
                                                                'fc': 'white',
                                                                'edgecolor': 'white',
                                                                'alpha': 0.6}}
        loaded_template['legend_Axes_legend'] = {'loc': 0,
                                                      'framealpha': 1,
                                                      'fontsize': 10}
        loaded_template['legend_Text_set_fontsize'] = 10
        loaded_template['legend_Frame_set_facecolor'] = '1'
        loaded_template['legend_Frame_set_fill'] = False
        loaded_template['obsid_Axes_annotate'] = {'xytext': (0, 10),
                                                       'textcoords': 'offset points',
                                                       'ha': 'center',
                                                       'va': 'top',
                                                       'fontsize': 9,
                                                       'rotation': 0,
                                                       'bbox': {'boxstyle': 'square,pad=0.05', 'fc': 'white',
                                                                'edgecolor': 'white', 'alpha': 0.4}}

        loaded_template['obsid_Axes_bar'] = {'edgecolor': 'black',
                                                  'fill': False,
                                                  'linewidth': 0.5}
        loaded_template["rcParams"] = {"savefig.dpi": 450,
                                       "figure.figsize": [6.4, 4.8]}
        loaded_template[
            'Figure_subplots_adjust'] = {}  # {"top": 0.95, "bottom": 0.15, "left": 0.09, "right": 0.97}
        loaded_template['wlevels_Axes_plot'] = {'DEFAULT': {'markersize': 6,
                                                                 'marker': 'v',
                                                                 'linestyle': '-',
                                                                 'linewidth': 1}}
        return loaded_template

def custplot_default_template():
    default = {
            "Axes_axhline": {
            },
            "Axes_axvline": {
            },
            "Axes_plot": {
                "linewidth": 1,
                "markersize": 6,
                "zorder": 8},
            "Axes_plot_date": {
                "linewidth": 1,
                "markersize": 6,
                "zorder": 8},
            "Axes_set_title": {
                "label": ""},
            "Axes_set_xlabel": {
                "fontsize": 10,
                "xlabel": ""},
            "Axes_set_ylabel": {
                "fontsize": 10,
                "ylabel": ""},
            "Axes_tick_param": {
                "axis": "both",
                "labelsize": 10},
            "Figure_add_subplot": {},
            "Figure_subplots_adjust": {
            },
            "grid_Axes_grid": {
                "b": True,
                "color": "0.65",
                "linestyle": "-",
                "which": "both",
                "zorder": 0},
            "legend_Axes_legend": {
                "fontsize": 10,
                "framealpha": 1,
                "loc": 10,
                "numpoints": 1},
            "legend_Frame_set_facecolor": "1",
            "legend_Frame_set_fill": False,
            "legend_Text_set_fontsize": 10,
            "legend_Line2D_methods": {'set_linewidth': 1.5},
            "plot_height": "",
            "plot_width": "",
            "rcParams": {"savefig.dpi": 450},
            "styles_colors": [
                "b",
                "r",
                "lime",
                "salmon",
                "darkcyan",
                "magenta",
                "turquoise",
                "pink",
                "cyan",
                "gray"],
            "styles_frequenzy": [
                "-",
                "--",
                "-.",
                ":"],
            "styles_line": [
                "-",
                "--",
                "-.",
                ":"],
            "styles_line_and_cross": [
                "+-"],
            "styles_line_and_marker": [
                "o-"],
            "styles_marker": [
                "o",
                "+",
                "s",
                "x"],
            "styles_step-post": [
                "-",
                "--",
                "-.",
                ":"],
            "styles_step-pre": [
                "-",
                "--",
                "-.",
                ":"],
            "tight_layout": False,
            "x_Axes_tick_param": {
                "axis": "x",
                "labelrotation": 45},
            "y_Axes_tick_param": {
                "axis": "y",
                "labelrotation": 0}}

    return default

def custplot_default_style():
    stylename = 'midv_custplot_default'
    filename = os.path.join(os.path.dirname(__file__), 'mpl_styles', '{}.mplstyle'.format(stylename))
    with io.open(filename, 'r', encoding='utf-8') as f:
        style = f.read()
    return (style, stylename)

def piperplot_style():
    return os.path.join(os.path.dirname(__file__), 'mpl_styles', 'midv_piperplot.mplstyle')


def pandas_rule_tooltip():
    return ru(QCoreApplication.translate('pandas_rule_tooltip',
                           'Steplength for resampling, ex:\n'
                           '"10S" = 10 seconds\n'
                           '"20T" = 20 minutes\n'
                           '"1h" = 1 hour\n'
                           '"24h" = 24 hours\n'
                           '(D = calendar day, M = month end, MS = month start, W = weekly, AS = year start, A = year end, ...)\n'
                           'No resampling if field is empty\n'
                           'See pandas pandas.DataFrame.resample documentation for more info.'))

def pandas_base_tooltip():
    return ru(QCoreApplication.translate('pandas_base_tooltip',
                           'The hour to start each timestep when rule "evenly subdivide 1 day" (for example Rule = 24h)\n'
                           'Ex: 7 (= 07:00). Default is 0 (00:00)\n'
                           'See pandas pandas.DataFrame.resample documentation for more info:\n'
                           'For frequencies that evenly subdivide 1 day, the "origin" of the aggregated intervals.\n'
                           'For example, for "5min" frequency, base could range from 0 through 4. Defaults to 0.'))

def pandas_how_tooltip():
    return ru(QCoreApplication.translate('pandas_how_tooltip',
                           'How to make the resample, ex. "mean" (default), "first", "last", "sum".\n'
                           'See pandas pandas.DataFrame.resample documentation for more info\n'
                           '(though "how" is not explained a lot)'))

def midv_line_cycle():
    return cycler('linestyle', ['-', '--', '-.', ':', (0, (3, 2, 1, 1, 1, 1))])

def midv_marker_cycle():
    return cycler('marker', ['o', '+', 's', 'x', "1", "2", "3", "4"])

def data_tables():
    return ['meteo', 'seismic_data', 'vlf_data', 'w_levels_logger']