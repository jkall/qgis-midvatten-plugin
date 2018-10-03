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

from collections import OrderedDict

import db_utils
import midvatten_utils as utils
from PyQt4.QtCore import QCoreApplication
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
            'secplotlabelsplotted':0,
            'secplotlegendplotted':2,
            'secplot_loaded_template': '',
            'secplot_templates': '',
            'secplotwidthofplot': 1,
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
            'custplot_legend':2,
            'custplot_grid':2,
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
            'custplot_templates': '',
            'custplot_loaded_template': '',
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
        utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate(u'geocolorsymbols', u'Reading zz_strat* tables failed. Using default dictionary instead'))
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
    for strata, strata_synonyms in sorted(dict_geo1.iteritems()):
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
                        utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate(u'geocolorsymbols', u'Error in geocolorsymbols, setting brush and color for strata "%s" using geoshort %s failed. Msg1:\n%s\nMsg2:\n%s\Msg3:\n%s'))%(strata, geoshort, str(a), str(b), str(c)))
                        dictionary[geoshort]=(u'NoBrush', u'white')

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
        utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'hydrocolors', u'Getting hydrocolors from database failed, using fallback method!')))
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
        dict_qt = utils.unicode_2_utf8(dict_qt1)
        for k, v in dict_qt.iteritems():
            dict_qt[k] = v[0]
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
        utils.MessagebarAndLog.info(log_msg=QCoreApplication.translate(u'PlotTypesDict', u'Getting strata and geoshort from zz_strat failed, fallback method using PlotTypesDict from code'))
        if international=='no' and  utils.getcurrentlocale() == 'sv_SE':
            """
            Dict = {u"Okänt" : u"not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')",
            "Berg"  : u"in ('berg','b','rock','ro')",
            "Grovgrus" : u"in ('grovgrus','grg','coarse gravel','cgr')",
            "Grus" : u"in ('grus','gr','gravel')",
            "Mellangrus" : u"in ('mellangrus','grm','medium gravel','mgr')",
            "Fingrus" : u"in ('fingrus','grf','fine gravel','fgr')",
            "Grovsand" : u"in ('grovsand','sag','coarse sand','csa')",
            "Sand" : u"in ('sand','sa')",
            "Mellansand" : u"in ('mellansand','sam','medium sand','msa')",
            "Finsand" : u"in ('finsand','saf','fine sand','fsa')",
            "Silt" : u"in ('silt','si')",
            "Lera" : u"in ('lera','ler','le','clay','cl')",
            u"Morän" : u"in ('morän','moran','mn','till','ti')",
            "Torv" : u"in ('torv','t','peat','pt')",
            "Fyll":u"in ('fyll','fyllning','f','made ground','mg','land fill')"}
            """
            dictionary = OrderedDict([(u"Okänt" , u"not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')"),
            ("Berg"  , u"in ('berg','b','rock','ro')"),
            ("Grovgrus" , u"in ('grovgrus','grg','coarse gravel','cgr')"),
            ("Grus" , u"in ('grus','gr','gravel')"),
            ("Mellangrus" , u"in ('mellangrus','grm','medium gravel','mgr')"),
            ("Fingrus" , u"in ('fingrus','grf','fine gravel','fgr')"),
            ("Grovsand" , u"in ('grovsand','sag','coarse sand','csa')"),
            ("Sand" , u"in ('sand','sa')"),
            ("Mellansand" , u"in ('mellansand','sam','medium sand','msa')"),
            ("Finsand" , u"in ('finsand','saf','fine sand','fsa')"),
            ("Silt" , u"in ('silt','si')"),
            ("Lera" , u"in ('lera','ler','le','clay','cl')"),
            (u"Morän" , u"in ('morän','moran','mn','till','ti')"),
            ("Torv" , u"in ('torv','t','peat','pt')"),
            ("Fyll",u"in ('fyll','fyllning','f','made ground','mg','land fill')")])
        else:
            """
            Dict = {u"Unknown" : u"not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')",
            "Rock"  : u"in ('berg','b','rock','ro')",
            "Coarse gravel" : u"in ('grovgrus','grg','coarse gravel','cgr')",
            "Gravel" : u"in ('grus','gr','gravel')",
            "Medium gravel" : u"in ('mellangrus','grm','medium gravel','mgr')",
            "Fine gravel" : u"in ('fingrus','grf','fine gravel','fgr')",
            "Coarse sand" : u"in ('grovsand','sag','coarse sand','csa')",
            "Sand" : u"in ('sand','sa')",
            "Medium sand" : u"in ('mellansand','sam','medium sand','msa')",
            "Fine sand" : u"in ('finsand','saf','fine sand','fsa')",
            "Silt" : u"in ('silt','si')",
            "Clay" : u"in ('lera','ler','le','clay','cl')",
            "Till" : u"in ('morän','moran','mn','till','ti')",
            "Peat" : u"in ('torv','t','peat','pt')",
            "Fill":u"in ('fyll','fyllning','f','made ground','mg','land fill')"}
            """
            dictionary = OrderedDict([("Unknown" , u"not in ('berg','b','rock','ro','grovgrus','grg','coarse gravel','cgr','grus','gr','gravel','mellangrus','grm','medium gravel','mgr','fingrus','grf','fine gravel','fgr','grovsand','sag','coarse sand','csa','sand','sa','mellansand','sam','medium sand','msa','finsand','saf','fine sand','fsa','silt','si','lera','ler','le','clay','cl','morän','moran','mn','till','ti','torv','t','peat','pt','fyll','fyllning','f','made ground','mg','land fill')"),
            ("Rock"  , u"in ('berg','b','rock','ro')"),
            ("Coarse gravel" , u"in ('grovgrus','grg','coarse gravel','cgr')"),
            ("Gravel" , u"in ('grus','gr','gravel')"),
            ("Medium gravel" , u"in ('mellangrus','grm','medium gravel','mgr')"),
            ("Fine gravel" , u"in ('fingrus','grf','fine gravel','fgr')"),
            ("Coarse sand" , u"in ('grovsand','sag','coarse sand','csa')"),
            ("Sand" , u"in ('sand','sa')"),
            ("Medium sand" , u"in ('mellansand','sam','medium sand','msa')"),
            ("Fine sand" , u"in ('finsand','saf','fine sand','fsa')"),
            ("Silt" , u"in ('silt','si')"),
            ("Clay" , u"in ('lera','ler','le','clay','cl')"),
            ("Till" , u"in ('morän','moran','mn','till','ti')"),
            ("Peat" , u"in ('torv','t','peat','pt')"),
            ("Fill",u"in ('fyll','fyllning','f','made ground','mg','land fill')")])
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
        utils.MessagebarAndLog.info(log_msg=QCoreApplication.translate(u'PlotColorDict', u'Getting strata and color_mplot form zz_stratigraphy_plots failed, fallback method with PlotColorDict from code'))
        if  utils.getcurrentlocale() == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {u"Okänt" : u"white",
            "Berg"  : u"red",
            "Grovgrus" : u"DarkGreen",
            "Grus" : u"DarkGreen",
            "Mellangrus" : u"DarkGreen",
            "Fingrus" : u"DarkGreen",
            "Grovsand" : u"green",
            "Sand" : u"green",
            "Mellansand" : u"green",
            "Finsand" : u"DarkOrange",
            "Silt" : u"yellow",
            "Lera" : u"yellow",
            u"Morän" : u"cyan",
            "Torv" : u"DarkGray",
            "Fyll":u"white"}
        else:
            Dict = {u"Unknown" : u"white",
            "Rock"  : u"red",
            "Coarse gravel" : u"DarkGreen",
            "Gravel" : u"DarkGreen",
            "Medium gravel" : u"DarkGreen",
            "Fine gravel" : u"DarkGreen",
            "Coarse sand" : u"green",
            "Sand" : u"green",
            "Medium sand" : u"green",
            "Fine sand" : u"DarkOrange",
            "Silt" : u"yellow",
            "Clay" : u"yellow",
            "Till" : u"cyan",
            "Peat" : u"DarkGray",
            "Fill":u"white"}
    #print Dict#debug!
    return Dict

def PlotHatchDict():
    """
    This dictionary is used by sectionplot (matplotlib) for relating the geoshort names with hatches in plots
    The user may update these fields in the zz_strat table to use other hatches
    Fallback method use dictionary defined in the code below
    """
    success, Dict = utils.create_dict_from_db_2_cols(('strata','hatch_mplot','zz_stratigraphy_plots'))
    if not success:
        utils.MessagebarAndLog.info(bar_msg=QCoreApplication.translate(u'PlotHatchDict', u'Getting strata and hatch_mplot from zz_stratigraphy_plots failed, fallback method with PlotHatchDict from code'))
        # hatch patterns : ('-', '+', 'x', '\\', '*', 'o', 'O', '.','/')
        if  utils.getcurrentlocale() == 'sv_SE': #swedish forms are loaded only if locale settings indicate sweden
            Dict = {u"Okänt" : u"",
            "Berg"  : u"x",
            "Grovgrus" : u"O",
            "Grus" : u"O",
            "Mellangrus" : u"o",
            "Fingrus" : u"o",
            "Grovsand" : u"*",
            "Sand" : u"*",
            "Mellansand" : u".",
            "Finsand" : u".",
            "Silt" : u"\\",
            "Lera" : u"-",
            u"Morän" : u"/",
            "Torv" : u"+",
            "Fyll":u"+"}
        else:
            Dict = {u"Unknown" : u"",
            "Rock"  : u"x",
            "Coarse gravel" : u"O",
            "Gravel" : u"O",
            "Medium gravel" : u"o",
            "Fine gravel" : u"o",
            "Coarse sand" : u"*",
            "Sand" : u"*",
            "Medium sand" : u".",
            "Fine sand" : u".",
            "Silt" : u"\\",
            "Clay" : u"-",
            "Till" : u"/",
            "Peat" : u"+",
            "Fill":u"+"}
    return Dict

def staff_list():
    """
    :return: A list of staff members from the staff table
    """
    sql = 'SELECT distinct staff from zz_staff'
    sql_result = db_utils.sql_load_fr_db(sql)
    connection_ok, result_list = sql_result

    if not connection_ok:
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate(u'staff_list', u'Sql failed, see log message panel'), log_msg=ru(QCoreApplication.translate(u'staff_list', u'Failed to get existing staff from staff table from sql %s'))%sql)
        return False, tuple()

    return True, ru(tuple([x[0] for x in result_list]), True)

def stratigraphy_table():
    return 'stratigraphy'

def w_flow_flowtypes_units():
    sql = 'select distinct flowtype, unit from w_flow'
    connection_ok, result_dict = db_utils.get_sql_result_as_dict(sql)

    if not connection_ok:
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate(u'w_flow_flowtypes_units', u"Error, sql failed, see log message panel"), log_msg=ru(QCoreApplication.translate(u'w_flow_flowtypes_units', u'Cannot get data from sql %s'))%ru(sql))
        return {}

    return ru(result_dict, keep_containers=True)

def w_qual_field_parameter_units():
    sql = 'select distinct parameter, unit from w_qual_field'
    connection_ok, result_dict = db_utils.get_sql_result_as_dict(sql)

    if not connection_ok:
        utils.MessagebarAndLog.warning(bar_msg=QCoreApplication.translate(u'w_qual_field_parameter_units', u'Error, sql failed, see log message panel'), log_msg=ru(QCoreApplication.translate(u'w_qual_field_parameter_units', u'Cannot get data from sql %s'))%ru(sql))
        return {}

    return ru(result_dict, keep_containers=True)


def get_last_used_quality_instruments():
    """
    Returns quality instrumentids
    :return: A tuple with instrument ids from w_qual_field
    """
    sql = 'select parameter, unit, instrument, staff, max(date_time) from w_qual_field group by parameter, unit, instrument, staff'
    connection_ok, result_dict = db_utils.get_sql_result_as_dict(sql)
    return ru(result_dict, True)

specific_table_info = {u'obs_lines': u'The geometry column supports WKT ("well known text") of type LINESTRING and\nthe geometries must correspond to SRID in the database.',
                       u'obs_points': u'The geometry column supports WKT ("well known text") of type POINT and\nthe geometries must correspond to SRID in the database.'}

def export_fieldlogger_defaults():
    current_locale = utils.getcurrentlocale()[0]

    if current_locale != u'sv_SE':
        input_field_browser =  [
            [0, ((u"input_field_list",[
            u"Accvol.m3;numberDecimal|numberSigned; ",
            u"DO.mg/L;numberDecimal|numberSigned; ",
            u"Momflow.l/s;numberDecimal|numberSigned; ",
            u"Momflow.m3/h;numberDecimal|numberSigned; ",
            u"comment;text;Obsid related comment",
            u"cond.µS/cm;numberDecimal|numberSigned; ",
            u"f.comment;text;Measurement related comment",
            u"l.comment;text;Measurement related comment",
            u"meas.m;numberDecimal|numberSigned;depth to water",
            u"pH;numberDecimal|numberSigned; ",
            u"q.comment;text;Measurement related comment",
            u"redox.mV;numberDecimal|numberSigned; ",
            u"s.comment;text;Measurement related comment",
            u"temp.°C;numberDecimal|numberSigned; ",
            u"turb.FNU;numberDecimal|numberSigned; "
            ]),)]]
        input_fields_groups = [
            [0, ((u"input_field_group_list",
                  [u"meas.m;numberDecimal|numberSigned;depth to water",
                   u"l.comment;text;Measurement related comment"]),
                (u"sublocation_suffix", u"level"))],
            [1, ((u"input_field_group_list",
                  [u"comment;text;Obsid related comment"]),
                 (u"sublocation_suffix", u"comment"))],
            [2, ((u"input_field_group_list",
                  [u"cond.µS/cm;numberDecimal|numberSigned; ",
                   u"DO.mg/L;numberDecimal|numberSigned; ",
                   u"pH;numberDecimal|numberSigned; ",
                   u"redox.mV;numberDecimal|numberSigned; ",
                   u"temp.°C;numberDecimal|numberSigned; ",
                   u"turb.FNU;numberDecimal|numberSigned; ",
                   u"q.comment;text;Measurement related comment"]),
                 (u"sublocation_suffix", u"quality"))],
            [3, ((u"input_field_group_list",
                  [u"temp.°C;numberDecimal|numberSigned; ",
                   u"turb.FNU;numberDecimal|numberSigned; ",
                   u"s.comment;text;Measurement related comment"]),
                 (u"sublocation_suffix", u"sample"))],
            [4, ((u"input_field_group_list",
                  [u"Accvol.m3;numberDecimal|numberSigned; ",
                   u"Momflow.l/s;numberDecimal|numberSigned; ",
                   u"Momflow.m3/h;numberDecimal|numberSigned; ",
                   u"f.comment;text;Measurement related comment"]),
                 (u"sublocation_suffix", u"flow"))]]
    else:
        input_field_browser = [[0, ((u"input_field_list", [
            u"Accvol.m3;numberDecimal|numberSigned; ",
            u"DO.mg/L;numberDecimal|numberSigned; ",
            u"Momflow.l/s;numberDecimal|numberSigned; ",
            u"Momflow.m3/h;numberDecimal|numberSigned; ",
            u"f.kommentar;text;mätrelaterad kommentar",
            u"k.kommentar;text;mätrelaterad kommentar",
            u"kommentar;text;obsidrelaterad kommentar",
            u"kond.µS/cm;numberDecimal|numberSigned; ",
            u"meas.m;numberDecimal|numberSigned;djup till vatten",
            u"n.kommentar;text;mätrelaterad kommentar",
            u"nedmätning.m;numberDecimal|numberSigned;djup till vatten",
            u"p.kommentar;text;mätrelaterad kommentar", u"pH;numberDecimal|numberSigned; ",
            u"redox.mV;numberDecimal|numberSigned; ", u"temp.°C;numberDecimal|numberSigned; ",
            u"turb.FNU;numberDecimal|numberSigned; "
            ], ), )]]

        input_fields_groups = [
            [0, ((u"input_field_group_list",
               [u"nedmätning.m;numberDecimal|numberSigned;djup till vatten",
                u"n.kommentar;text;mätrelaterad kommentar"]),
              (u"sublocation_suffix", u"nivå"))],
            [1, ((u"input_field_group_list",
                  [u"kommentar;text;obsidrelaterad kommentar"]),
                 (u"sublocation_suffix", u"kommentar"))],
            [2, ((u"input_field_group_list",
                  [u"kond.µS/cm;numberDecimal|numberSigned; ",
                   u"DO.mg/L;numberDecimal|numberSigned; ",
                   u"pH;numberDecimal|numberSigned; ",
                   u"redox.mV;numberDecimal|numberSigned; ",
                   u"temp.°C;numberDecimal|numberSigned; ",
                   u"turb.FNU;numberDecimal|numberSigned; ",
                   u"k.kommentar;text;mätrelaterad kommentar"]),
                 (u"sublocation_suffix", u"kvalitet"))],
            [3, ((u"input_field_group_list",
                  [u"temp.°C;numberDecimal|numberSigned; ",
                   u"turb.FNU;numberDecimal|numberSigned; ",
                   u"p.kommentar;text;mätrelaterad kommentar"]),
                 (u"sublocation_suffix", u"prov"))],
            [4, ((u"input_field_group_list",
                  [u"Accvol.m3;numberDecimal|numberSigned; ",
                   u"Momflow.l/s;numberDecimal|numberSigned; ",
                   u"Momflow.m3/h;numberDecimal|numberSigned; ",
                   u"f.kommentar;text;mätrelaterad kommentar"],),
                 (u"sublocation_suffix", u"flöde"))]]

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
            'xlabel': ru(QCoreApplication.translate(u'SectionPlot', u"Distance along section")),
            'fontsize': 10}
        loaded_template['Axes_set_xlabel_stratplot'] = {
            'xlabel': ru(QCoreApplication.translate(u'SectionPlot', u"Observation Location Code")),
            'fontsize': 10}
        loaded_template['Axes_set_xlim'] = None  # Tuple like (min, max)
        loaded_template['Axes_set_ylim'] = None  # Tuple like (min, max)
        loaded_template['Axes_set_ylabel'] = {
            'ylabel': ru(QCoreApplication.translate(u'SectionPlot', u"Level, masl")),
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
        loaded_template['plot_height'] = None
        loaded_template['plot_width'] = None
        loaded_template[
            'Figure_subplots_adjust'] = {}  # {"top": 0.95, "bottom": 0.15, "left": 0.09, "right": 0.97}
        loaded_template['wlevels_Axes_plot'] = {'DEFAULT': {'markersize': 6,
                                                                 'marker': 'v',
                                                                 'linestyle': '-',
                                                                 'linewidth': 1}}
        return loaded_template

def custplot_default_template():
    return u'{}'


