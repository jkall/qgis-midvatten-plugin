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
from __future__ import absolute_import
from builtins import object
import codecs
import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QUrl, QDir
from qgis.PyQt.QtGui import QDesktopServices

import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from .calculate_statistics import get_statistics_for_single_obsid


class Drillreport(object):        # general observation point info for the selected object
    
    def __init__(self, obsids=[''], settingsdict = {}):

        reportfolder = os.path.join(QDir.tempPath(), 'midvatten_reports')
        if not os.path.exists(reportfolder):
            os.makedirs(reportfolder)
        reportpath = os.path.join(reportfolder, "drill_report.html")
        logopath = os.path.join(os.sep,os.path.dirname(__file__),"..","templates","midvatten_logga.png")
        imgpath = os.path.join(os.sep,os.path.dirname(__file__),"..","templates")

        if len(obsids) == 0:
            utils.pop_up_info(ru(QCoreApplication.translate(u'Drillreport', u"Must select one or more obsids!")))
            return None
        elif len(obsids) == 1:
            merged_question = False
        else:
            #Due to problems regarding speed when opening many tabs, only the merge mode is used.
            #merged_question = utils.Askuser(question='YesNo', msg="Do you want to open all drill reports merged on the same tab?\n"
            #                                    "Else they will be opened separately.\n\n(If answering no, creating drill reports for many obsids take 0.2 seconds per obsid.\nIt might fail if the computer is to slow.\nIf it fails, try to select only one obsid at the time)").result
            merged_question = True

        if merged_question:
            f, rpt = self.open_file(', '.join(obsids), reportpath)
            for obsid in obsids:
                self.write_obsid(obsid, rpt, imgpath, logopath, f)
            self.close_file(f, reportpath)
        else:
            #opened = False
            for obsid in obsids:
                f, rpt = self.open_file(obsid, reportpath)
                self.write_obsid(obsid, rpt, imgpath, logopath, f)
                url_status = self.close_file(f, reportpath)
                #This must be used if many obsids are allowed to used this method.
                #if not opened:
                #    sleep(2)
                #    opened = True
                #else:
                #    sleep(0.2)


    def open_file(self, header, reportpath):
        #open connection to report file
        f = codecs.open(reportpath, "wb", "utf-8")
        #write some initiating html, header and also
        rpt = r"""<meta http-equiv="content-type" content="text/html; charset=utf-8" />"""
        rpt += r"""<head><title>%s %s</title></head>"""%(header, ru(QCoreApplication.translate(u'Drillreport', u'General report from Midvatten plugin for QGIS')))

        return f, rpt

    def close_file(self, f, reportpath):
        f.write("\n</p></body></html>")
        f.close()
        #print reportpath#debug
        url_status = QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))
        return url_status

    def write_obsid(self, obsid, rpt, imgpath, logopath, f):
        rpt += r"""<html><TABLE WIDTH=100% BORDER=0 CELLPADDING=1 CELLSPACING=1><TR VALIGN=TOP><TD WIDTH=15%><h3 style="font-family:'arial';font-size:18pt; font-weight:600">"""
        rpt += obsid
        if  utils.getcurrentlocale()[0] == 'sv_SE':
            rpt += ''.join([r'''</h3><img src="''', os.path.join(imgpath, 'for_general_report_sv.png'), r'''" /><br><img src=''', r"""'"""])
            #rpt += r"""</h3><img src="for_general_report_sv.png" /><br><img src='"""
        else:
            rpt += ''.join([r'''</h3><img src="''', os.path.join(imgpath, 'for_general_report.png'), r'''" /><br><img src=''', r"""'"""])
            #rpt += r"""</h3><img src="for_general_report.png" /><br><img src='"""
        rpt += logopath
        rpt +="""' /></TD><TD WIDTH=85%><TABLE WIDTH=100% BORDER=1 CELLPADDING=4 CELLSPACING=3><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>"""
        if  utils.getcurrentlocale()[0] == 'sv_SE':
            rpt += u'Allmän information'
        else:
            rpt += ru(QCoreApplication.translate(u'Drillreport', u'General information'))
        rpt += r"""</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*>"""
        f.write(rpt)

        # GENERAL DATA UPPER LEFT QUADRANT
        ConnectionOK, GeneralData = self.GetData(obsid, 'obs_points', 'n')#MacOSX fix1
        #utils.pop_up_info(str(ConnectionOK))#debug
        if ConnectionOK==True:
            result2 = db_utils.sql_load_fr_db(r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'""")[1][0][0]
            CRS = ru(result2) #1st we need crs
            result3 = db_utils.get_srid_name(result2)
            CRSname = ru(result3) # and crs name
            if  utils.getcurrentlocale()[0] == 'sv_SE':
                reportdata_1 = self.rpt_upper_left_sv(GeneralData, CRS, CRSname)
            else:
                reportdata_1 = self.rpt_upper_left(GeneralData, CRS, CRSname)
            f.write(reportdata_1)

            rpt = r"""</TABLE></TD><TD WIDTH=50%><P><U><B>"""
            if  utils.getcurrentlocale()[0] == 'sv_SE':
                rpt += u'Lagerföljd'
            else:
                rpt += ru(QCoreApplication.translate(u'Drillreport', u'Stratigraphy'))
            rpt += r"""</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*>"""
            f.write(rpt)

            # STRATIGRAPHY DATA UPPER RIGHT QUADRANT
            StratData = self.GetData(obsid, 'stratigraphy', 'n')[1] #MacOSX fix1
            if  utils.getcurrentlocale()[0] == 'sv_SE':
                reportdata_2 = self.rpt_upper_right_sv(StratData)
            else:
                reportdata_2 = self.rpt_upper_right(StratData)
            f.write(reportdata_2)

            rpt = r"""</TABLE></TD></TR><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>"""
            if  utils.getcurrentlocale()[0] == 'sv_SE':
                rpt += u'Kommentarer'
            else:
                rpt += ru(QCoreApplication.translate(u'Drillreport', u'Comments'))
            rpt += r"""</B></U></P>"""
            f.write(rpt)

            # COMMENTS LOWER LEFT QUADRANT
            reportdata_3 = self.rpt_lower_left(GeneralData)
            f.write(reportdata_3)

            rpt = r"""</TD><TD WIDTH=50%><P><U><B>"""
            if  utils.getcurrentlocale()[0] == 'sv_SE':
                rpt += u'Vattennivåer'
            else:
                rpt += ru(QCoreApplication.translate(u'Drillreport', u'Water levels'))
            rpt += r"""</B></U></P>"""
            f.write(rpt)

            # WATER LEVEL STATISTICS LOWER RIGHT QUADRANT
            meas_or_level_masl, statistics = get_statistics_for_single_obsid(obsid)#MacOSX fix1
            if  utils.getcurrentlocale()[0] == 'sv_SE':
                reportdata_4 = self.rpt_lower_right_sv(statistics,meas_or_level_masl)
            else:
                reportdata_4 = self.rpt_lower_right(statistics,meas_or_level_masl)
            f.write(reportdata_4)

            f.write(r"""</TD></TR></TABLE></TD></TR></TABLE>""")


    def rpt_upper_left_sv(self, GeneralData, CRS='', CRSname=''):
        rpt = r"""<p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;">"""
        if ru(GeneralData[0][1]) != '' and ru(GeneralData[0][1]) != 'NULL' and ru(GeneralData[0][1]) != ru(GeneralData[0][0]):
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'originalbenämning' + r"""</TD><TD WIDTH=67%>""" + ru(GeneralData[0][1]) + '</TD></TR>'
        if ru(GeneralData[0][3]) != '' and ru(GeneralData[0][3]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'obstyp' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][3]) + '</TD></TR>'
        if ru(GeneralData[0][4]) != '' and ru(GeneralData[0][4]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'djup (m fr my t botten)' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][4]) + '</TD></TR>'
        if ru(GeneralData[0][17]) != '' and ru(GeneralData[0][17]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'röröverkant (möh)' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][17])
            if ru(GeneralData[0][21]) != '':
                rpt += u' (' +  ru(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if ru(GeneralData[0][18]) != ''  and ru(GeneralData[0][18]) != 'NULL' and ru(GeneralData[0][18]) != '0' and ru(GeneralData[0][18]) != '0.0':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'rörövermått (m ö my)' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][18]) + '</TD></TR>'
        if ru(GeneralData[0][19]) != '' and ru(GeneralData[0][19]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'markytans nivå, my (möh)' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][19])
            if ru(GeneralData[0][21]) != '':
                rpt += u' (' +  ru(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if ru(GeneralData[0][20]) != '' and ru(GeneralData[0][20]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'onoggrannhet i höjd, avser rök (m)' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][20]) + '</TD></TR>'
        if ru(GeneralData[0][13]) != '' and ru(GeneralData[0][13]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'östlig koordinat' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][13]) + ' (' + '%s'%('%s, '%CRSname if CRSname else '') + 'EPSG:' + CRS + ')</TD></TR>'
        if ru(GeneralData[0][14]) != '' and ru(GeneralData[0][14]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'nordlig koordinat' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][14]) + ' (' + '%s'%('%s, '%CRSname if CRSname else '') + 'EPSG:' + CRS + ')</TD></TR>'
        if ru(GeneralData[0][13]) != ''  and ru(GeneralData[0][13]) != 'NULL' and ru(GeneralData[0][14]) != '' and ru(GeneralData[0][15]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'lägesonoggrannhet' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][15]) + '</TD></TR>'
        if ru(GeneralData[0][7]) != '' and ru(GeneralData[0][7]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'material' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][7]) + '</TD></TR>'
        if ru(GeneralData[0][6]) != '' and ru(GeneralData[0][6]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'innerdiameter (mm)' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][6]) + '</TD></TR>'
        if ru(GeneralData[0][5]) != '' and ru(GeneralData[0][5]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'borrningens avslut' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][5]) + '</TD></TR>'
        if ru(GeneralData[0][8]) != '' and ru(GeneralData[0][8]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'filter/spets' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][8]) + '</TD></TR>'
        if ru(GeneralData[0][10]) != '' and ru(GeneralData[0][10]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'borrningen avslutades' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][10]) + '</TD></TR>'
        if ru(GeneralData[0][9]) != '' and ru(GeneralData[0][9]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'kapacitet/vg på spetsnivå' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][9]) + '</TD></TR>'
        if ru(GeneralData[0][2]) != '' and ru(GeneralData[0][2]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'fastighet/plats' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][2]) + '</TD></TR>'
        if ru(GeneralData[0][23]) != '' and ru(GeneralData[0][23]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'referens' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][23]) + '</TD></TR>'
        rpt += r"""</p>"""
        if ru(GeneralData[0][16]) != '' and ru(GeneralData[0][16]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'lägesangivelsens ursprung' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][16]) + '</TD></TR>'
        if ru(GeneralData[0][22]) != '' and ru(GeneralData[0][22]) != 'NULL':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + u'höjdangivelsens ursprung' + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][22]) + '</TD></TR>'
        return rpt

    def rpt_upper_left(self, GeneralData, CRS='', CRSname=''):
        rpt = r"""<p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;">"""
        if ru(GeneralData[0][1]) != '' and ru(GeneralData[0][1]) != 'NULL' and ru(GeneralData[0][1]) != ru(GeneralData[0][0]):
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'original name')) + r"""</TD><TD WIDTH=67%>""" + ru(GeneralData[0][1]) + '</TD></TR>'
        if ru(GeneralData[0][3]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'obs type')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][3]) + '</TD></TR>'
        if ru(GeneralData[0][4]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'depth (m fr gs to bottom)')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][4]) + '</TD></TR>'
        if ru(GeneralData[0][17]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'top of casing, toc (masl)')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][17])
            if ru(GeneralData[0][21]) != '':
                rpt += u' (' +  ru(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if ru(GeneralData[0][18]) not in ['','NULL'] and ru(GeneralData[0][18]) != '0' and ru(GeneralData[0][18]) != '0.0':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'distance toc-gs, tocags (mags)')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][18]) + '</TD></TR>'
        if ru(GeneralData[0][19]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'ground surface level, gs (masl)')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][19])
            if ru(GeneralData[0][21]) != '':
                rpt += u' (' +  ru(GeneralData[0][21]) + ')'
            rpt += '</TD></TR>'
        if ru(GeneralData[0][20]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'elevation accuracy (m)')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][20]) + '</TD></TR>'
        if ru(GeneralData[0][13]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'eastern coordinate')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][13]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if ru(GeneralData[0][14]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'northern coordinate')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][14]) + ' (' + CRSname  + ', EPSG:' + CRS + ')</TD></TR>'
        if ru(GeneralData[0][13]) not in ['','NULL'] and ru(GeneralData[0][14]) != '' and ru(GeneralData[0][15]) != '':
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'position accuracy')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][15]) + '</TD></TR>'
        if ru(GeneralData[0][7]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'material')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][7]) + '</TD></TR>'
        if ru(GeneralData[0][6]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'inner diameter (mm)')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][6]) + '</TD></TR>'
        if ru(GeneralData[0][5]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'drill stop')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][5]) + '</TD></TR>'
        if ru(GeneralData[0][8]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'screen type')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][8]) + '</TD></TR>'
        if ru(GeneralData[0][10]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'drill date')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][10]) + '</TD></TR>'
        if ru(GeneralData[0][9]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'capacity')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][9]) + '</TD></TR>'
        if ru(GeneralData[0][2]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'place')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][2]) + '</TD></TR>'
        if ru(GeneralData[0][23]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'reference')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][23]) + '</TD></TR>'
        rpt += r"""</p>"""
        if ru(GeneralData[0][16]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'source for position')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][16]) + '</TD></TR>'
        if ru(GeneralData[0][22]) not in ['','NULL']:
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%>""" + ru(QCoreApplication.translate(u'Drillreport', u'source for elevation')) + r"""</TD><TD WIDTH=50%>""" + ru(GeneralData[0][22]) + '</TD></TR>'
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
            col2 = '' if ru(row[2])=='NULL' else ru(row[2])
            col3 = '' if ru(row[3])=='NULL' else ru(row[3])
            col4 = '' if ru(row[4])=='NULL' else ru(row[4])
            col5 = '' if ru(row[5])=='NULL' else ru(row[5])
            col6 = '' if ru(row[6])=='NULL' else ru(row[6])
            col7 = '' if ru(row[7])=='NULL' else ru(row[7])
            col8 = '' if ru(row[8])=='NULL' else ru(row[8])
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
            rpt += r"""<TR VALIGN=TOP><TD WIDTH=15%><P><u>""" + ru(QCoreApplication.translate(u'Drillreport', u'level (m b gs)')) + '</P></u></TD>'
            rpt += r"""<TD WIDTH=27%><P><u>""" + ru(QCoreApplication.translate(u'Drillreport', u'geology, full text')) + '</P></u></TD>'
            rpt += r"""<TD WIDTH=17%><P><u>""" + ru(QCoreApplication.translate(u'Drillreport', u'geology, short')) + '</P></u></TD>'
            rpt += r"""<TD WIDTH=9%><P><u>""" + ru(QCoreApplication.translate(u'Drillreport', u'capacity')) + '</P></u></TD>'
            rpt += r"""<TD WIDTH=13%><P><u>""" + ru(QCoreApplication.translate(u'Drillreport', u'development')) + '</P></u></TD>'
            rpt += r"""<TD WIDTH=21%><P><u>""" + ru(QCoreApplication.translate(u'Drillreport', u'comment')) + '</P></u></TD></TR>'
        for row in StratData:
            col2 = '' if ru(row[2])=='NULL' else ru(row[2])
            col3 = '' if ru(row[3])=='NULL' else ru(row[3])
            col4 = '' if ru(row[4])=='NULL' else ru(row[4])
            col5 = '' if ru(row[5])=='NULL' else ru(row[5])
            col6 = '' if ru(row[6])=='NULL' else ru(row[6])
            col7 = '' if ru(row[7])=='NULL' else ru(row[7])
            col8 = '' if ru(row[8])=='NULL' else ru(row[8])
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
        if ru(GeneralData[0][24]) not in ['','NULL'] and ru(GeneralData[0][25]) not in ['','NULL']:
            rpt += ru(GeneralData[0][24])
            rpt += ru(GeneralData[0][25])
        elif ru(GeneralData[0][24]) not in ['','NULL']:
            rpt += ru(GeneralData[0][24])
        elif ru(GeneralData[0][25]) not in ['','NULL']:
            rpt += ru(GeneralData[0][25])
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_right_sv(self, statistics,meas_or_level_masl):
        if meas_or_level_masl == 'meas':
            unit = u' m u rök<br>'
        else:
            unit = u' m ö h<br>'
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if ru(statistics[2]) != '' and ru(statistics[2]) != '0':
            rpt += u'Antal nivåmätningar: ' +  ru(statistics[2]) +  u'<br>'
            if ru(statistics[0]) != '':
                rpt += u'Högsta uppmätta nivå: ' +  ru(statistics[0]) + unit
            if ru(statistics[1]) != '':
                rpt += u'Medianvärde för nivå: ' +  ru(statistics[1]) + unit
            if ru(statistics[3]) != '':
                rpt += u'Lägsta uppmätta nivå: ' +  ru(statistics[3]) + unit
        rpt += r"""</p>"""
        return rpt

    def rpt_lower_right(self, statistics,meas_or_level_masl):
        if meas_or_level_masl == 'meas':
            unit = ru(QCoreApplication.translate(u'Drillreport', u' m below toc')) + u'<br>'
        else:
            unit = ru(QCoreApplication.translate(u'Drillreport', u' m above sea level')) + u'<br>'
        rpt = r"""<p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">"""
        if ru(statistics[2]) != '' and ru(statistics[2]) != '0':
            rpt += ru(QCoreApplication.translate(u'Drillreport', u'Number of water level measurements: ')) +  ru(statistics[2]) + u'<br>'
            if ru(statistics[0]) != '':
                rpt += ru(QCoreApplication.translate(u'Drillreport', u'Highest measured water level: ')) +  ru(statistics[0]) + unit
            if ru(statistics[1]) != '':
                rpt += ru(QCoreApplication.translate(u'Drillreport', u'Median water level: ')) +  ru(statistics[1]) + unit
            if ru(statistics[3]) != '':
                rpt += ru(QCoreApplication.translate(u'Drillreport', u'Lowest measured water level: ')) +  ru(statistics[3]) + unit
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
        ConnectionOK, data = db_utils.sql_load_fr_db(sql)
        return ConnectionOK, data

