# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that returns a report with general observation point info, 
 "drill report"for the selected obs_point. 
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
# Import the PyQt libraries
from PyQt4.QtCore import *  #Not necessary?
from PyQt4.QtGui import *  #Not necessary?
from qgis.core import *   # Necessary for the QgsFeature()
from qgis.gui import *
from sqlite3 import dbapi2 as sqlite    #sqlite3 is good enough since we not handle spatial data in this class (otherwise pyspatialite)
import os
import locale
import midvatten_utils as utils  
#import codecs

class drillreport():        # general observation point info for the selected object
    
    def __init__(self, obsid='', settingsdict = {}):
         #open connection to report file
        reportpath = os.path.join(os.sep,os.path.dirname(__file__),"reports","drill_report.html")
        logopath = os.path.join(os.sep,os.path.dirname(__file__),"about","midvatten_logga.png")
        f = open(reportpath, "wb" )
        #f = codecs.open(reportpath, "wb", "utf-8")
        
        #write some initiating html, header and also 
        rpt = r"""<meta http-equiv="content-type" content="text/html; charset=utf-8" />"""  # NOTE, perhaps 'latin-1' due to use on win machines??
        rpt += r"""<head><title>Midvatten plugin for QGIS - general report</title></head>"""
        rpt += r"""<html><TABLE WIDTH=100% BORDER=0 CELLPADDING=1 CELLSPACING=1 STYLE="page-break-before: always"><TR VALIGN=TOP><TD WIDTH=15%><h3 style="font-family:'arial';font-size:18pt; font-weight:600">"""
        rpt += obsid
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            rpt += r"""</h3><img src="for_general_report_sv.png" /><br><img src='"""
        else:
            rpt += r"""</h3><img src="for_general_report.png" /><br><img src='"""
        rpt += logopath
        rpt +="""' /></TD><TD WIDTH=85%><TABLE WIDTH=100% BORDER=1 CELLPADDING=4 CELLSPACING=3 STYLE="page-break-before: always"><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>""" 
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            rpt += u'Allmän information' 
        else:
            rpt += u'General information' 
        rpt += r"""</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*>"""
        rpt2 = rpt.encode("utf-8")
        f.write(rpt2)
        
        # GENERAL DATA UPPER LEFT QUADRANT
        GeneralData = self.GetData(str(settingsdict['database']).encode(locale.getdefaultlocale()[1]), obsid, 'obs_points', 'n')
        CRS = self.returnunicode(utils.sql_load_fr_db(r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'""")[0][0]) #1st we need crs
        CRSname = self.returnunicode(utils.sql_load_fr_db(r"""SELECT ref_sys_name FROM spatial_ref_sys where srid =""" + CRS)[0][0]) # and crs name
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            reportdata_1 = self.rpt_upper_left_sv(GeneralData, CRS, CRSname)
        else:
            reportdata_1 = self.rpt_upper_left(GeneralData, CRS, CRSname)
        rpt2 = reportdata_1.encode("utf-8")
        f.write(rpt2)

        rpt = r"""</TABLE></TD><TD WIDTH=50%><P><U><B>""" 
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            rpt += u'Lagerföljd' 
        else:
            rpt += u'Stratigraphy' 
        rpt += r"""</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*>"""
        rpt2 = rpt.encode("utf-8")
        f.write(rpt2)        

        # STRATIGRAPHY DATA UPPER RIGHT QUADRANT
        StratData = self.GetData(str(settingsdict['database']).encode(locale.getdefaultlocale()[1]), obsid, 'stratigraphy', 'n')
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            reportdata_2 = self.rpt_upper_right_sv(StratData)
        else:
            reportdata_2 = self.rpt_upper_right(StratData)
        rpt2 = reportdata_2.encode("utf-8")
        f.write(rpt2)

        rpt = r"""</TABLE></TD></TR><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>""" 
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            rpt += u'Kommentarer' 
        else:
            rpt += u'Comments' 
        rpt += r"""</B></U></P>"""
        rpt2 = rpt.encode("utf-8")
        f.write(rpt2)        

        # COMMENTS LOWER LEFT QUADRANT
        reportdata_3 = self.rpt_lower_left(GeneralData)
        rpt2 = reportdata_3.encode("utf-8")
        f.write(rpt2)

        rpt = r"""</TD><TD WIDTH=50%><P><U><B>""" 
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            rpt += u'Vattennivåer' 
        else:
            rpt += u'Water levels' 
        rpt += r"""</B></U></P>"""
        rpt2 = rpt.encode("utf-8")
        f.write(rpt2)

        # WATER LEVEL STATISTICS LOWER RIGHT QUADRANT
        statistics = self.GetStatistics(str(settingsdict['database']).encode(locale.getdefaultlocale()[1]), obsid)
        if  locale.getdefaultlocale()[0] == 'sv_SE':
            reportdata_4 = self.rpt_lower_right_sv(statistics)
        else:
            reportdata_4 = self.rpt_lower_right(statistics)
        rpt2 = reportdata_4.encode("utf-8")
        f.write(rpt2)
        
        f.write(r"""</TD></TR></TABLE></TD></TR></TABLE>""")    
        f.write("\n</p></body></html>")        
        f.close()
        
        QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def rpt_upper_left_sv(self, GeneralData, CRS='', CRSname=''):
        rpt = r"""<p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;">"""
        if self.returnunicode(GeneralData[0][1]) != '' and self.returnunicode(GeneralData[0][1]) != self.returnunicode(GeneralData[0][0]):
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'originalbenämning' + r"""</TD><TD WIDTH=67%>""" + self.returnunicode(GeneralData[0][1]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][3]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'obstyp' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][3]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][4]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'djup (m fr my t botten)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][4]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][17]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'röröverkant (möh)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][17])
            if self.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  self.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if self.returnunicode(GeneralData[0][18]) != '' and self.returnunicode(GeneralData[0][18]) != '0' and self.returnunicode(GeneralData[0][18]) != '0.0':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'rörövermått (m ö my)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][18]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][19]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'markytans nivå, my (möh)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][19])
            if self.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  self.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if self.returnunicode(GeneralData[0][20]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'onoggrannhet i höjd, avser rök (m)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][20]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][13]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'östlig koordinat' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][13]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if self.returnunicode(GeneralData[0][14]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'nordlig koordinat' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][14]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if self.returnunicode(GeneralData[0][13]) != '' and self.returnunicode(GeneralData[0][14]) != '' and self.returnunicode(GeneralData[0][15]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'lägesnoggrannhet' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][15]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][7]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'material' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][7]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][6]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'innerdiameter (mm)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][6]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][5]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'borrningens avslut' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][5]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][8]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'filter/spets' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][8]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][10]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'borrningen avslutades' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][10]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][9]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'kapacitet/vg på spetsnivå' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][9]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][2]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'fastighet/plats' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][2]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][23]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'referens' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][23]) + '</TD></TR>'
        rpt += r"""</p>"""
        if self.returnunicode(GeneralData[0][16]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'lägesangivelsens ursprung' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][16]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][22]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'höjdangivelsens ursprung' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][22]) + '</TD></TR>'
        return rpt

    def rpt_upper_left(self, GeneralData, CRS='', CRSname=''):
        rpt = r"""<p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;">"""
        if self.returnunicode(GeneralData[0][1]) != '' and self.returnunicode(GeneralData[0][1]) != self.returnunicode(GeneralData[0][0]):
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'original name' + r"""</TD><TD WIDTH=67%>""" + self.returnunicode(GeneralData[0][1]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][3]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'obs type' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][3]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][4]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'depth (m fr gs to bottom)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][4]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][17]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'top of casing, toc (masl)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][17])
            if self.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  self.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if self.returnunicode(GeneralData[0][18]) != '' and self.returnunicode(GeneralData[0][18]) != '0' and self.returnunicode(GeneralData[0][18]) != '0.0':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'distance toc-gs, tocags (mags)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][18]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][19]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'ground surface level, gs (masl)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][19])
            if self.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  self.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if self.returnunicode(GeneralData[0][20]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'elevation accuracy (m)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][20]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][13]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'eastern coordinate' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][13]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if self.returnunicode(GeneralData[0][14]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'northern coordinate' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][14]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if self.returnunicode(GeneralData[0][13]) != '' and self.returnunicode(GeneralData[0][14]) != '' and self.returnunicode(GeneralData[0][15]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'position accuracy' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][15]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][7]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'material' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][7]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][6]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'inner diameter (mm)' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][6]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][5]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'drill stop' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][5]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][8]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'screen type' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][8]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][10]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'drill date' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][10]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][9]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'capacity' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][9]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][2]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'place' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][2]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][23]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'reference' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][23]) + '</TD></TR>'
        rpt += r"""</p>"""
        if self.returnunicode(GeneralData[0][16]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'source for position' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][16]) + '</TD></TR>'
        if self.returnunicode(GeneralData[0][22]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'source for elevation' + r"""</TD><TD WIDTH=50%>""" + self.returnunicode(GeneralData[0][22]) + '</TD></TR>'
        return rpt
        
    def rpt_upper_right_sv(self, StratData):
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if len(StratData) > 0:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=17%><P><u>""" + u'nivå (mumy)</P></u></TD>'
            rpt += r"""<TD WIDTH=27%><P><u>""" + u'jordart, fullst beskrivn' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=17%><P><u>""" + u'huvudfraktion' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=5%><P><u>""" + u'vg' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=9%><P><u>""" + u'stänger?' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=27%><P><u>""" + u'kommentar' + '</P></u></TD></TR>'
        for row in StratData:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=17%><P>"""
            rpt += self.returnunicode(row[2]) + ' - ' + self.returnunicode(row[3]) + '</P></TD>'
            rpt += r"""<TD WIDTH=27%><P>""" + self.returnunicode(row[4]) + '</P></TD>'
            rpt += r"""<TD WIDTH=17%><P>""" + self.returnunicode(row[5]) + '</P></TD>'
            rpt += r"""<TD WIDTH=5%><P>""" + self.returnunicode(row[6]) + '</P></TD>'
            rpt += r"""<TD WIDTH=9%><P>""" + self.returnunicode(row[7]) + '</P></TD>'
            rpt += r"""<TD WIDTH=27%><P>""" + self.returnunicode(row[8]) + '</P></TD></TR>'
        rpt += r"""</p>"""
        return rpt

    def rpt_upper_right(self, StratData):
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if len(StratData) > 0:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=15%><P><u>""" + u'level (m b gs)</P></u></TD>'
            rpt += r"""<TD WIDTH=27%><P><u>""" + u'geology, full text' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=17%><P><u>""" + u'geology, short' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=9%><P><u>""" + u'capacity' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=13%><P><u>""" + u'development' + '</P></u></TD>'
            rpt += r"""<TD WIDTH=21%><P><u>""" + u'comment' + '</P></u></TD></TR>'
        for row in StratData:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=15%><P>"""
            rpt += self.returnunicode(row[2]) + ' - ' + self.returnunicode(row[3]) + '</P></TD>'
            rpt += r"""<TD WIDTH=27%><P>""" + self.returnunicode(row[4]) + '</P></TD>'
            rpt += r"""<TD WIDTH=17%><P>""" + self.returnunicode(row[5]) + '</P></TD>'
            rpt += r"""<TD WIDTH=9%><P>""" + self.returnunicode(row[6]) + '</P></TD>'
            rpt += r"""<TD WIDTH=13%><P>""" + self.returnunicode(row[7]) + '</P></TD>'
            rpt += r"""<TD WIDTH=21%><P>""" + self.returnunicode(row[8]) + '</P></TD></TR>'
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_left(self, GeneralData):
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if self.returnunicode(GeneralData[0][24]) != '' and self.returnunicode(GeneralData[0][25]) != '':
            rpt += self.returnunicode(GeneralData[0][24])
            rpt += self.returnunicode(GeneralData[0][25])
        elif self.returnunicode(GeneralData[0][24]) != '':
            rpt += self.returnunicode(GeneralData[0][24])
        elif self.returnunicode(GeneralData[0][25]) != '':
            rpt += self.returnunicode(GeneralData[0][25])
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_right_sv(self, statistics):
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if self.returnunicode(statistics[2]) != '' and self.returnunicode(statistics[2]) != '0':
            rpt += u'Antal nivåmätningar: ' +  self.returnunicode(statistics[2]) + u' st<br>'
            if self.returnunicode(statistics[0]) != '':
                rpt += u'Högsta uppmätta nivå: ' +  self.returnunicode(statistics[0]) + u' m u rök<br>'
            if self.returnunicode(statistics[1]) != '':
                rpt += u'Medianvärde för nivå: ' +  self.returnunicode(statistics[1]) + u' m u rök<br>'
            if self.returnunicode(statistics[3]) != '':
                rpt += u'Lägsta uppmätta nivå: ' +  self.returnunicode(statistics[3]) + u' m u rök'
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_right(self, statistics):
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if self.returnunicode(statistics[2]) != '' and self.returnunicode(statistics[2]) != '0':
            rpt += u'Number of water level measurements: ' +  self.returnunicode(statistics[2]) + u'<br>'
            if self.returnunicode(statistics[0]) != '':
                rpt += u'Highest measured water level: ' +  self.returnunicode(statistics[0]) + u' m below toc<br>'
            if self.returnunicode(statistics[1]) != '':
                rpt += u'Median water level: ' +  self.returnunicode(statistics[1]) + u' m below toc<br>'
            if self.returnunicode(statistics[3]) != '':
                rpt += u'Lowest measured water level: ' +  self.returnunicode(statistics[3]) + u' m below toc'
        rpt += r"""</p>"""
        return rpt

    def GetData(self, dbPath='', obsid = '', tablename='', debug = 'n'):            # GetData method that returns a table with water quality data
        # Load all data in obs_points table
        sql = r"""select * from """
        sql += tablename
        sql += r""" where obsid = '"""
        sql += obsid   
        sql += r"""'"""
        if tablename == 'stratigraphy':
            sql += r""" order by stratid"""
        if debug == 'y':
            utils.pop_up_info(sql)
        data = utils.sql_load_fr_db(sql)
        return data

    def GetStatistics(self, dbPath='', obsid = ''):            # GetData method that returns a table with water quality data
        Statistics_list = [0]*4
        
        sql = r"""select min(meas) from w_levels where obsid = '"""
        sql += obsid
        sql += r"""'"""
        min_value = utils.sql_load_fr_db(sql)
        if min_value:
            Statistics_list[0] = min_value[0][0]
        
        sql = r"""SELECT x.obsid, x.meas as median from (select obsid, meas FROM w_levels WHERE obsid = '"""
        sql += obsid
        sql += r"""') as x, (select obsid, meas FROM w_levels WHERE obsid = '"""
        sql += obsid
        sql += r"""') as y GROUP BY x.meas HAVING SUM(CASE WHEN y.meas <= x.meas THEN 1 ELSE 0 END)>=(COUNT(*)+1)/2 AND SUM(CASE WHEN y.meas >= x.meas THEN 1 ELSE 0 END)>=(COUNT(*)/2)+1"""
        median_value = utils.sql_load_fr_db(sql)
        if median_value:
            Statistics_list[1] = median_value[0][1]
        
        sql = r"""select Count(meas) from w_levels where obsid = '"""
        sql += obsid
        sql += r"""'"""
        number_of_values = utils.sql_load_fr_db(sql)
        if number_of_values:
            Statistics_list[2] = number_of_values[0][0]
        
        sql = r"""select max(meas) from w_levels where obsid = '"""
        sql += obsid
        sql += r"""'"""
        max_value = utils.sql_load_fr_db(sql)
        if max_value:
            Statistics_list[3] = max_value[0][0]
        
        return Statistics_list    
        
    def returnunicode(self, anything): #takes an input and tries to return it as unicode
        if type(anything) == type(None):
            text = unicode('')
        elif type(anything) == type(unicode('unicodetextstring')):
            text = anything 
        #elif (type(anything) == type (1)) or (type(anything) == type (1.1)):
        #    text = unicode(str(anything))
        #elif type(anything) == type('ordinary_textstring'):
        #    text = unicode(anything)
        else:
            try:
                text = unicode(str(anything))
            except:
                text = unicode('data type unknown, check database')
        return text 
