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
from PyQt4.QtCore import QUrl, QDir
from PyQt4.QtGui import QDesktopServices

from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import os
import locale
import midvatten_utils as utils
import codecs

class drillreport():        # general observation point info for the selected object
    
    def __init__(self, obsid='', settingsdict = {}):
         #open connection to report file
        reportfolder = os.path.join(QDir.tempPath(), 'midvatten_reports')
        if not os.path.exists(reportfolder):
            os.makedirs(reportfolder)
        reportpath = os.path.join(reportfolder, "drill_report.html")
        logopath = os.path.join(os.sep,os.path.dirname(__file__),"..","about","midvatten_logga.png")
        imgpath = os.path.join(os.sep,os.path.dirname(__file__),"..","reports")
        f = codecs.open(reportpath, "wb", "utf-8")
        
        #write some initiating html, header and also 
        rpt = r"""<meta http-equiv="content-type" content="text/html; charset=utf-8" />""" 
        rpt += r"""<head><title>%s General report from Midvatten plugin for QGIS</title></head>"""%obsid
        rpt += r"""<html><TABLE WIDTH=100% BORDER=0 CELLPADDING=1 CELLSPACING=1><TR VALIGN=TOP><TD WIDTH=15%><h3 style="font-family:'arial';font-size:18pt; font-weight:600">"""
        rpt += obsid
        if  utils.getcurrentlocale() == 'sv_SE':
            rpt += ''.join([r'''</h3><img src="''', os.path.join(imgpath, 'for_general_report_sv.png'), r'''" /><br><img src=''', r"""'"""])
            #rpt += r"""</h3><img src="for_general_report_sv.png" /><br><img src='"""
        else:
            rpt += ''.join([r'''</h3><img src="''', os.path.join(imgpath, 'for_general_report.png'), r'''" /><br><img src=''', r"""'"""])
            #rpt += r"""</h3><img src="for_general_report.png" /><br><img src='"""
        rpt += logopath
        rpt +="""' /></TD><TD WIDTH=85%><TABLE WIDTH=100% BORDER=1 CELLPADDING=4 CELLSPACING=3><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>"""
        if  utils.getcurrentlocale() == 'sv_SE':
            rpt += u'Allmän information' 
        else:
            rpt += u'General information' 
        rpt += r"""</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*>"""
        f.write(rpt)
        
        # GENERAL DATA UPPER LEFT QUADRANT
        ConnectionOK, GeneralData = self.GetData(obsid, 'obs_points', 'n')#MacOSX fix1
        #utils.pop_up_info(str(ConnectionOK))#debug
        if ConnectionOK==True:
            result2 = (utils.sql_load_fr_db(r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'""")[1])[0][0]
            CRS = utils.returnunicode(result2) #1st we need crs
            result3 = (utils.sql_load_fr_db(r"""SELECT ref_sys_name FROM spatial_ref_sys where srid =""" + CRS)[1])[0][0]
            CRSname = utils.returnunicode(result3) # and crs name
            if  utils.getcurrentlocale() == 'sv_SE':
                reportdata_1 = self.rpt_upper_left_sv(GeneralData, CRS, CRSname)
            else:
                reportdata_1 = self.rpt_upper_left(GeneralData, CRS, CRSname)
            f.write(reportdata_1)

            rpt = r"""</TABLE></TD><TD WIDTH=50%><P><U><B>"""
            if  utils.getcurrentlocale() == 'sv_SE':
                rpt += u'Lagerföljd' 
            else:
                rpt += u'Stratigraphy' 
            rpt += r"""</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*>"""
            f.write(rpt)        

            # STRATIGRAPHY DATA UPPER RIGHT QUADRANT
            StratData = self.GetData(obsid, 'stratigraphy', 'n')[1] #MacOSX fix1
            if  utils.getcurrentlocale() == 'sv_SE':
                reportdata_2 = self.rpt_upper_right_sv(StratData)
            else:
                reportdata_2 = self.rpt_upper_right(StratData)
            f.write(reportdata_2)

            rpt = r"""</TABLE></TD></TR><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>""" 
            if  utils.getcurrentlocale() == 'sv_SE':
                rpt += u'Kommentarer' 
            else:
                rpt += u'Comments' 
            rpt += r"""</B></U></P>"""
            f.write(rpt)        

            # COMMENTS LOWER LEFT QUADRANT
            reportdata_3 = self.rpt_lower_left(GeneralData)
            f.write(reportdata_3)

            rpt = r"""</TD><TD WIDTH=50%><P><U><B>""" 
            if  utils.getcurrentlocale() == 'sv_SE':
                rpt += u'Vattennivåer' 
            else:
                rpt += u'Water levels' 
            rpt += r"""</B></U></P>"""
            f.write(rpt)

            # WATER LEVEL STATISTICS LOWER RIGHT QUADRANT
            meas_or_level_masl, statistics = GetStatistics(obsid)#MacOSX fix1
            if  utils.getcurrentlocale() == 'sv_SE':
                reportdata_4 = self.rpt_lower_right_sv(statistics,meas_or_level_masl)
            else:
                reportdata_4 = self.rpt_lower_right(statistics,meas_or_level_masl)
            f.write(reportdata_4)
            
            f.write(r"""</TD></TR></TABLE></TD></TR></TABLE>""")    
            f.write("\n</p></body></html>")        
            f.close()
            #print reportpath#debug
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def rpt_upper_left_sv(self, GeneralData, CRS='', CRSname=''):
        rpt = r"""<p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;">"""
        if utils.returnunicode(GeneralData[0][1]) != '' and utils.returnunicode(GeneralData[0][1]) != 'NULL' and utils.returnunicode(GeneralData[0][1]) != utils.returnunicode(GeneralData[0][0]):
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'originalbenämning' + r"""</TD><TD WIDTH=67%>""" + utils.returnunicode(GeneralData[0][1]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][3]) != '' and utils.returnunicode(GeneralData[0][3]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'obstyp' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][3]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][4]) != '' and utils.returnunicode(GeneralData[0][4]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'djup (m fr my t botten)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][4]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][17]) != '' and utils.returnunicode(GeneralData[0][17]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'röröverkant (möh)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][17])
            if utils.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  utils.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if utils.returnunicode(GeneralData[0][18]) != ''  and utils.returnunicode(GeneralData[0][18]) != 'NULL' and utils.returnunicode(GeneralData[0][18]) != '0' and utils.returnunicode(GeneralData[0][18]) != '0.0':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'rörövermått (m ö my)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][18]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][19]) != '' and utils.returnunicode(GeneralData[0][19]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'markytans nivå, my (möh)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][19])
            if utils.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  utils.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if utils.returnunicode(GeneralData[0][20]) != '' and utils.returnunicode(GeneralData[0][20]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'onoggrannhet i höjd, avser rök (m)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][20]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][13]) != '' and utils.returnunicode(GeneralData[0][13]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'östlig koordinat' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][13]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if utils.returnunicode(GeneralData[0][14]) != '' and utils.returnunicode(GeneralData[0][14]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'nordlig koordinat' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][14]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if utils.returnunicode(GeneralData[0][13]) != ''  and utils.returnunicode(GeneralData[0][13]) != 'NULL' and utils.returnunicode(GeneralData[0][14]) != '' and utils.returnunicode(GeneralData[0][15]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'lägesonoggrannhet' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][15]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][7]) != '' and utils.returnunicode(GeneralData[0][7]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'material' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][7]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][6]) != '' and utils.returnunicode(GeneralData[0][6]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'innerdiameter (mm)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][6]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][5]) != '' and utils.returnunicode(GeneralData[0][5]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'borrningens avslut' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][5]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][8]) != '' and utils.returnunicode(GeneralData[0][8]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'filter/spets' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][8]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][10]) != '' and utils.returnunicode(GeneralData[0][10]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'borrningen avslutades' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][10]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][9]) != '' and utils.returnunicode(GeneralData[0][9]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'kapacitet/vg på spetsnivå' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][9]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][2]) != '' and utils.returnunicode(GeneralData[0][2]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'fastighet/plats' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][2]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][23]) != '' and utils.returnunicode(GeneralData[0][23]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'referens' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][23]) + '</TD></TR>'
        rpt += r"""</p>"""
        if utils.returnunicode(GeneralData[0][16]) != '' and utils.returnunicode(GeneralData[0][16]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'lägesangivelsens ursprung' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][16]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][22]) != '' and utils.returnunicode(GeneralData[0][22]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'höjdangivelsens ursprung' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][22]) + '</TD></TR>'
        return rpt

    def rpt_upper_left(self, GeneralData, CRS='', CRSname=''):
        rpt = r"""<p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;">"""
        if utils.returnunicode(GeneralData[0][1]) != '' and utils.returnunicode(GeneralData[0][1]) != 'NULL' and utils.returnunicode(GeneralData[0][1]) != utils.returnunicode(GeneralData[0][0]):
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'original name' + r"""</TD><TD WIDTH=67%>""" + utils.returnunicode(GeneralData[0][1]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][3]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'obs type' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][3]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][4]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'depth (m fr gs to bottom)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][4]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][17]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'top of casing, toc (masl)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][17])
            if utils.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  utils.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if utils.returnunicode(GeneralData[0][18]) not in ['','NULL'] and utils.returnunicode(GeneralData[0][18]) != '0' and utils.returnunicode(GeneralData[0][18]) != '0.0':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'distance toc-gs, tocags (mags)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][18]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][19]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'ground surface level, gs (masl)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][19])
            if utils.returnunicode(GeneralData[0][21]) != '':
                rpt += u' (' +  utils.returnunicode(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if utils.returnunicode(GeneralData[0][20]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'elevation accuracy (m)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][20]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][13]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'eastern coordinate' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][13]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if utils.returnunicode(GeneralData[0][14]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'northern coordinate' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][14]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if utils.returnunicode(GeneralData[0][13]) not in ['','NULL'] and utils.returnunicode(GeneralData[0][14]) != '' and utils.returnunicode(GeneralData[0][15]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'position accuracy' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][15]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][7]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'material' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][7]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][6]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'inner diameter (mm)' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][6]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][5]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'drill stop' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][5]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][8]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'screen type' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][8]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][10]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'drill date' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][10]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][9]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'capacity' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][9]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][2]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'place' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][2]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][23]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'reference' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][23]) + '</TD></TR>'
        rpt += r"""</p>"""
        if utils.returnunicode(GeneralData[0][16]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'source for position' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][16]) + '</TD></TR>'
        if utils.returnunicode(GeneralData[0][22]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'source for elevation' + r"""</TD><TD WIDTH=50%>""" + utils.returnunicode(GeneralData[0][22]) + '</TD></TR>'
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
            col2 = '' if utils.returnunicode(row[2])=='NULL' else utils.returnunicode(row[2])
            col3 = '' if utils.returnunicode(row[3])=='NULL' else utils.returnunicode(row[3])
            col4 = '' if utils.returnunicode(row[4])=='NULL' else utils.returnunicode(row[4])
            col5 = '' if utils.returnunicode(row[5])=='NULL' else utils.returnunicode(row[5])
            col6 = '' if utils.returnunicode(row[6])=='NULL' else utils.returnunicode(row[6])
            col7 = '' if utils.returnunicode(row[7])=='NULL' else utils.returnunicode(row[7])
            col8 = '' if utils.returnunicode(row[8])=='NULL' else utils.returnunicode(row[8])
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=17%><P>"""
            rpt += col2 + ' - ' + col3 + '</P></TD>'
            rpt += r"""<TD WIDTH=27%><P>""" + col4 + '</P></TD>'
            rpt += r"""<TD WIDTH=17%><P>""" + col5 + '</P></TD>'
            rpt += r"""<TD WIDTH=5%><P>""" + col6 + '</P></TD>'
            rpt += r"""<TD WIDTH=9%><P>""" + col7 + '</P></TD>'
            rpt += r"""<TD WIDTH=27%><P>""" + col8 + '</P></TD></TR>'
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
            col2 = '' if utils.returnunicode(row[2])=='NULL' else utils.returnunicode(row[2])
            col3 = '' if utils.returnunicode(row[3])=='NULL' else utils.returnunicode(row[3])
            col4 = '' if utils.returnunicode(row[4])=='NULL' else utils.returnunicode(row[4])
            col5 = '' if utils.returnunicode(row[5])=='NULL' else utils.returnunicode(row[5])
            col6 = '' if utils.returnunicode(row[6])=='NULL' else utils.returnunicode(row[6])
            col7 = '' if utils.returnunicode(row[7])=='NULL' else utils.returnunicode(row[7])
            col8 = '' if utils.returnunicode(row[8])=='NULL' else utils.returnunicode(row[8])
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=15%><P>"""
            rpt += col2 + ' - ' + col3 + '</P></TD>'
            rpt += r"""<TD WIDTH=27%><P>""" + col4 + '</P></TD>'
            rpt += r"""<TD WIDTH=17%><P>""" + col5 + '</P></TD>'
            rpt += r"""<TD WIDTH=9%><P>""" + col6 + '</P></TD>'
            rpt += r"""<TD WIDTH=13%><P>""" + col7 + '</P></TD>'
            rpt += r"""<TD WIDTH=21%><P>""" + col8 + '</P></TD></TR>'
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_left(self, GeneralData):
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if utils.returnunicode(GeneralData[0][24]) not in ['','NULL'] and utils.returnunicode(GeneralData[0][25]) not in ['','NULL']:
            rpt += utils.returnunicode(GeneralData[0][24])
            rpt += utils.returnunicode(GeneralData[0][25])
        elif utils.returnunicode(GeneralData[0][24]) not in ['','NULL']:
            rpt += utils.returnunicode(GeneralData[0][24])
        elif utils.returnunicode(GeneralData[0][25]) not in ['','NULL']:
            rpt += utils.returnunicode(GeneralData[0][25])
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_right_sv(self, statistics,meas_or_level_masl):
        if meas_or_level_masl == 'meas':
            unit = u' m u rök<br>'
        else:
            unit = u' m ö h<br>'
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if utils.returnunicode(statistics[2]) != '' and utils.returnunicode(statistics[2]) != '0':
            rpt += u'Antal nivåmätningar: ' +  utils.returnunicode(statistics[2]) +  u'<br>'
            if utils.returnunicode(statistics[0]) != '':
                rpt += u'Högsta uppmätta nivå: ' +  utils.returnunicode(statistics[0]) + unit
            if utils.returnunicode(statistics[1]) != '':
                rpt += u'Medianvärde för nivå: ' +  utils.returnunicode(statistics[1]) + unit
            if utils.returnunicode(statistics[3]) != '':
                rpt += u'Lägsta uppmätta nivå: ' +  utils.returnunicode(statistics[3]) + unit
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_right(self, statistics,meas_or_level_masl):
        if meas_or_level_masl == 'meas':
            unit = u' m below toc<br>'
        else:
            unit = u' m above sea level<br>'
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if utils.returnunicode(statistics[2]) != '' and utils.returnunicode(statistics[2]) != '0':
            rpt += u'Number of water level measurements: ' +  utils.returnunicode(statistics[2]) + u'<br>'
            if utils.returnunicode(statistics[0]) != '':
                rpt += u'Highest measured water level: ' +  utils.returnunicode(statistics[0]) + unit
            if utils.returnunicode(statistics[1]) != '':
                rpt += u'Median water level: ' +  utils.returnunicode(statistics[1]) + unit
            if utils.returnunicode(statistics[3]) != '':
                rpt += u'Lowest measured water level: ' +  utils.returnunicode(statistics[3]) + unit
        rpt += r"""</p>"""
        return rpt

    def GetData(self, obsid = '', tablename='', debug = 'n'):            # GetData method that returns a table with water quality data
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
        ConnectionOK, data = utils.sql_load_fr_db(sql)
        return ConnectionOK, data


def GetStatistics(obsid = ''):
    Statistics_list = [0]*4

    columns = ['meas', 'level_masl']
    meas_or_level_masl= 'meas'#default value

    #number of values, also decide wehter to use meas or level_masl in report
    for column in columns:
        sql = r"""select Count(""" + column + r""") from w_levels where obsid = '"""
        sql += obsid
        sql += r"""'"""
        ConnectionOK, number_of_values = utils.sql_load_fr_db(sql)
        if number_of_values and number_of_values[0][0] > Statistics_list[2]:#this will select meas if meas >= level_masl
            meas_or_level_masl = column
            Statistics_list[2] = number_of_values[0][0]

    #min value
    if meas_or_level_masl=='meas':
        sql = r"""select min(meas) from w_levels where obsid = '"""
    else:
        sql = r"""select max(level_masl) from w_levels where obsid = '"""
    sql += obsid
    sql += r"""'"""
    ConnectionOK, min_value = utils.sql_load_fr_db(sql)
    if min_value:
        Statistics_list[0] = min_value[0][0]

    #median value
    sql = r"""SELECT x.obsid, x.""" + meas_or_level_masl + r""" as median from (select obsid, """ + meas_or_level_masl + r""" FROM w_levels WHERE obsid = '"""
    sql += obsid
    sql += r"""' and (typeof(""" + meas_or_level_masl + r""")=typeof(0.01) or typeof(""" + meas_or_level_masl + r""")=typeof(1))) as x, (select obsid, """ + meas_or_level_masl + r""" FROM w_levels WHERE obsid = '"""
    sql += obsid
    sql += r"""' and (typeof(""" + meas_or_level_masl + r""")=typeof(0.01) or typeof(""" + meas_or_level_masl + r""")=typeof(1))) as y GROUP BY x.""" + meas_or_level_masl + r""" HAVING SUM(CASE WHEN y.""" + meas_or_level_masl + r""" <= x.""" + meas_or_level_masl + r""" THEN 1 ELSE 0 END)>=(COUNT(*)+1)/2 AND SUM(CASE WHEN y.""" + meas_or_level_masl + r""" >= x.""" + meas_or_level_masl + r""" THEN 1 ELSE 0 END)>=(COUNT(*)/2)+1"""
    ConnectionOK, median_value = utils.sql_load_fr_db(sql)
    if median_value:
        Statistics_list[1] = median_value[0][1]

    #max value
    if meas_or_level_masl=='meas':
        sql = r"""select max(meas) from w_levels where obsid = '"""
    else:
        sql = r"""select min(level_masl) from w_levels where obsid = '"""
    sql += obsid
    sql += r"""'"""
    ConnectionOK, max_value = utils.sql_load_fr_db(sql)
    if max_value:
        Statistics_list[3] = max_value[0][0]

    return meas_or_level_masl, Statistics_list

