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
import db_utils
from PyQt4.QtCore import QUrl, QDir
from PyQt4.QtGui import QDesktopServices

import os
import locale
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
import codecs
from time import sleep

from PyQt4.QtCore import QCoreApplication

class Drillreport():        # general observation point info for the selected object

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

        obs_points_translations = {
            'obsid': ru(QCoreApplication.translate('Drillreport2', 'obsid')),
            'name': ru(QCoreApplication.translate('Drillreport2', 'name')),
            'place': ru(QCoreApplication.translate('Drillreport2', 'place')),
            'type': ru(QCoreApplication.translate('Drillreport2', 'type')),
            'length': ru(QCoreApplication.translate('Drillreport2', 'length')),
            'drillstop': ru(QCoreApplication.translate('Drillreport2', 'drillstop')),
            'diam': ru(QCoreApplication.translate('Drillreport2', 'diam')),
            'material': ru(QCoreApplication.translate('Drillreport2', 'material')),
            'screen': ru(QCoreApplication.translate('Drillreport2', 'screen')),
            'capacity': ru(QCoreApplication.translate('Drillreport2', 'capacity')),
            'drilldate': ru(QCoreApplication.translate('Drillreport2', 'drilldate')),
            'wmeas_yn': ru(QCoreApplication.translate('Drillreport2', 'wmeas_yn')),
            'wlogg_yn': ru(QCoreApplication.translate('Drillreport2', 'wlogg_yn')),
            'east': ru(QCoreApplication.translate('Drillreport2', 'east')),
            'north': ru(QCoreApplication.translate('Drillreport2', 'north')),
            'ne_accur': ru(QCoreApplication.translate('Drillreport2', 'ne_accur')),
            'ne_source': ru(QCoreApplication.translate('Drillreport2', 'ne_source')),
            'h_toc': ru(QCoreApplication.translate('Drillreport2', 'h_toc')),
            'h_tocags': ru(QCoreApplication.translate('Drillreport2', 'h_tocags')),
            'h_gs': ru(QCoreApplication.translate('Drillreport2', 'h_gs')),
            'h_accur': ru(QCoreApplication.translate('Drillreport2', 'h_accur')),
            'h_syst': ru(QCoreApplication.translate('Drillreport2', 'h_syst')),
            'h_source': ru(QCoreApplication.translate('Drillreport2', 'h_source')),
            'source': ru(QCoreApplication.translate('Drillreport2', 'source')),
            'com_onerow': ru(QCoreApplication.translate('Drillreport2', 'com_onerow')),
            'com_html': ru(QCoreApplication.translate('Drillreport2', 'com_html'))}

        """
        thelist = [ "obsid", "stratid", "depthtop", "depthbot", "geology", "geoshort", "capacity", "development", "comment"]
        >>> y = '\n'.join(["'%s'"%x + ': ' + "ru(QCoreApplication.translate('Drillreport2', '%s')),"%x for x in thelist])
        >>> print(y)
        """

        #Settings:
        #--------------
        #The order and content of the geographical and general tables will follow general_metadata and geo_metadata list.
        # All obs_points columns could appear here except geometry.
        # The XY-reference system is added a bit down in the script to the list geo_data. The append has to be commented away
        # if it's not wanted.
        general_metadata = [u'type',
                            u'h_tocags',
                            u'material',
                            u'diam',
                            u'drillstop',
                            u'screen',
                            u'drilldate']

        geo_metadata = [u'east',
                        u'north',
                        u'ne_accur',
                        u'ne_source',
                        u'h_source',
                        u'h_toc',
                        u'h_accur']

        #If False, the header will be written outside the table
        header_in_table = True
        #If True, headers/values in general_metadata and geo_metadata will be skipped if the value is empty, else they
        #will be printed anyway
        skip_empty = False
        ###############

        dbconnection = db_utils.DbConnectionManager()

        obs_points_cols =  ["obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html"]
        all_obs_points_data = ru(db_utils.get_sql_result_as_dict(u'SELECT %s FROM obs_points WHERE obsid IN (%s) ORDER BY obsid'%(u', '.join(obs_points_cols), u', '.join([u"'{}'".format(x) for x in obsids])),
                                                            dbconnection=dbconnection)[1], keep_containers=True)

        all_stratigrapy_data = ru(db_utils.get_sql_result_as_dict(u'SELECT obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development, comment FROM stratigraphy WHERE obsid IN (%s) ORDER BY obsid, stratid'%(u', '.join([u"'{}'".format(x) for x in obsids])),
                                                            dbconnection=dbconnection)[1], keep_containers=True)

        crs = ru(db_utils.sql_load_fr_db(u"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'""", dbconnection=dbconnection)[1][0][0])
        crsname = ru(db_utils.get_srid_name(crs, dbconnection=dbconnection))

        dbconnection.closedb()

        f, rpt = self.open_file(', '.join(obsids), reportpath)
        rpt += ur"""<html>"""
        for obsid in obsids:
            obs_points_data = all_obs_points_data[obsid][0]
            general_data = [(obs_points_translations.get(header, header), obs_points_data[obs_points_cols.index(header)-1]) for header in general_metadata]
            geo_data = [(obs_points_translations.get(header, header), obs_points_data[obs_points_cols.index(header)-1]) for header in geo_metadata]
            geo_data.append((ru(QCoreApplication.translate('Drillreport2', u'XY Reference system')), '%s'%('%s, '%crsname if crsname else '') + 'EPSG:' + crs))

            strat_data = all_stratigrapy_data.get(obsid, None)

            comment_data = [obs_points_data[obs_points_cols.index(header)-1] for header in (u'com_onerow', u'com_html') if
                            all([obs_points_data[obs_points_cols.index(header)-1].strip(),
                                 u'text-indent:0px;"><br /></p>' not in obs_points_data[obs_points_cols.index(header)-1],
                                 u'text-indent:0px;"></p>' not in obs_points_data[obs_points_cols.index(header)-1],
                                 u'text-indent:0px;">NULL</p>' not in obs_points_data[obs_points_cols.index(header)-1].strip()])]

            rpt += self.write_obsid(obsid, general_data, geo_data, strat_data, comment_data, header_in_table=header_in_table, skip_empty=skip_empty)
            rpt += ur"""<p>    </p>"""

        rpt += ur"""</html>"""
        f.write(rpt)
        self.close_file(f, reportpath)



    def open_file(self, header, reportpath):
        #open connection to report file
        f = codecs.open(reportpath, "wb", "utf-8")
        #write some initiating html, header and also
        rpt = ur"""<meta http-equiv="content-type" content="text/html; charset=utf-8" />"""
        rpt += ur"""<head><title>%s %s</title></head>"""%(header, ru(QCoreApplication.translate(u'Drillreport', u'General report from Midvatten plugin for QGIS')))

        return f, rpt

    def close_file(self, f, reportpath):
        f.write("\n</p></body></html>")
        f.close()
        #print reportpath#debug
        url_status = QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))
        return url_status

    def obsid_header(self, obsid):
        return ur"""<h3 style="font-family:'Ubuntu';font-size:12pt; font-weight:600">%s</h3>"""%ru(obsid)

    def write_obsid(self, obsid, general_data, geo_data, strat_data, comment_data, header_in_table=True, skip_empty=False):
        """This part only handles writing the information. It does not do any db data collection."""

        rpt = u''

        if not header_in_table:
            rpt += self.obsid_header(obsid)

        rpt += ur"""<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 CELLSPACING=3>"""

        if header_in_table:
        #Row 1, obsid header
            rpt += ur"""<TR VALIGN=TOP>"""
            rpt += ur"""<TD WIDTH=100% COLSPAN=2>"""
            rpt += ur"""<h3 style="font-family:'Ubuntu';font-size:12pt; font-weight:600">%s</h3>"""%ru(obsid)
            rpt += ur"""</TD>"""
            rpt += ur"""</TR>"""


        #Row 2, general and geographical information
        rpt += ur"""<TR VALIGN=TOP>"""
        rpt += ur"""<TD WIDTH=60%>"""
        rpt += self.write_two_col_table(general_data, ru(QCoreApplication.translate(u'Drillreport2', u'General information')), skip_empty)
        rpt += ur"""</TD>"""

        rpt += ur"""<TD WIDTH=40%>"""
        rpt += self.write_two_col_table(geo_data, ru(QCoreApplication.translate(u'Drillreport2', u'Geographical information')), skip_empty)
        rpt += ur"""</TD>"""
        rpt += ur"""</TR>"""

        #Row 3, stratigraphy and comments

        if strat_data or comment_data:
            rpt += ur"""<TR VALIGN=TOP>"""
            rpt += ur"""<TD WIDTH=100% COLSPAN=2>"""

            if strat_data:
                rpt += self.write_strat_data(strat_data, ru(QCoreApplication.translate(u'Drillreport2', u'Stratigraphy')))

            if comment_data:
                rpt += self.write_comment_data(comment_data, ru(QCoreApplication.translate(u'Drillreport2', u'Comment')))

            rpt += ur"""</TD>"""
            rpt += ur"""</TR>"""
        rpt += ur"""</TABLE>"""

        return rpt

    def write_two_col_table(self, data, table_header, skip_empty=False):

        rpt = ur"""<P><U><B>%s</B></U></P>"""%table_header
        rpt += ur"""<TABLE style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*>"""

        rpt += ur"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""
        for header, value in data:
            header = ru(header)
            value = ru(value) if ru(value) is not None and ru(value) != u'NULL' else u''
            if skip_empty:
                if value and value != 'NULL' and value != header:
                    try:
                        _test = float(value)
                    except ValueError:
                        pass
                    else:
                        if _test == 0.0:
                            continue
                else:
                    continue


            try:
                rpt += ur"""<TR VALIGN=TOP><TD WIDTH=33%>{}</TD><TD WIDTH=50%>{}</TD></TR>""".format(header, value)
            except UnicodeEncodeError:
                try:
                    utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'drillreport2', u'Writing drillreport failed, see log message panel')),
                                                    log_msg=ru(QCoreApplication.translate(u'drillreport2', u'Writing header %s and value %s failed'))%(header, value))
                    print("header %s"%header)
                    print("value %s"%value)
                except:
                    pass
                raise
        rpt += r"""</p>"""
        rpt += r"""</TABLE>"""
        return rpt

    def write_strat_data(self, strat_data, table_header):
        rpt = ur"""<P><U><B>%s</B></U></P>""" % table_header

        rpt += ur"""<TABLE style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*>"""

        rpt += ur"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""

        col_widths = [u'15', u'27', u'17', u'9', u'13', u'21']

        headers = [ru(QCoreApplication.translate(u'Drillreport2_strat', u'level (m b gs)')),
                   ru(QCoreApplication.translate(u'Drillreport2_strat', u'geology, full text')),
                   ru(QCoreApplication.translate(u'Drillreport2_strat', u'geology, short')),
                   ru(QCoreApplication.translate(u'Drillreport2_strat', u'capacity')),
                   ru(QCoreApplication.translate(u'Drillreport2_strat', u'development')),
                   ru(QCoreApplication.translate(u'Drillreport2_strat', u'comment'))]

        if len(strat_data) > 0:
            rpt += ur"""<TR VALIGN=TOP>"""
            for colnr, header in enumerate(headers):
                rpt += ur"""<TD WIDTH={}%><P><u>{}</P></u></TD>""".format(col_widths[colnr], header)
            rpt += ur"""</TR>"""

            for rownr, row in enumerate(strat_data):
                rpt += ur"""<TR VALIGN=TOP>"""
                col2 = u'' if row[1]=='NULL' else row[1]
                col3 = u'' if row[2]=='NULL' else row[2]
                col4 = u'' if row[3]=='NULL' else row[3]
                col5 = u'' if row[4]=='NULL' else row[4]
                col6 = u'' if row[5]=='NULL' else row[5]
                col7 = u'' if row[6]=='NULL' else row[6]
                col8 = u'' if row[7]=='NULL' else row[7]
                rpt += ur"""<TD WIDTH={}%><P>{}</P></TD>""".format(col_widths[0], col2 + ' - ' + col3)
                rpt += ur"""<TD WIDTH={}%><P>{}</P></TD>""".format(col_widths[1], col4)
                rpt += ur"""<TD WIDTH={}%><P>{}</P></TD>""".format(col_widths[2], col5)
                rpt += ur"""<TD WIDTH={}%><P>{}</P></TD>""".format(col_widths[3], col6)
                rpt += ur"""<TD WIDTH={}%><P>{}</P></TD>""".format(col_widths[4], col7)
                rpt += ur"""<TD WIDTH={}%><P>{}</P></TD>""".format(col_widths[5], col8)

                rpt += ur"""</TR>"""
        rpt += ur"""</p>"""
        rpt += ur"""</TABLE>"""

        return rpt

    def write_comment_data(self, comment_data, header):
        if comment_data:
            rpt = ur"""<P><U><B>{}</B></U></P>""".format(header)
            rpt += ur"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""
            rpt += ur"""""".join([ru(x) for x in comment_data if ru(x) not in ['','NULL']])
            rpt += ur"""</p>"""
        else:
            rpt = u''

        return rpt


def GetStatistics(obsid = ''):
    Statistics_list = [0]*4

    columns = ['meas', 'level_masl']
    meas_or_level_masl= 'meas'#default value

    #number of values, also decide wehter to use meas or level_masl in report
    for column in columns:
        sql = r"""select Count(""" + column + r""") from w_levels where obsid = '"""
        sql += obsid
        sql += r"""'"""
        ConnectionOK, number_of_values = db_utils.sql_load_fr_db(sql)
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
    ConnectionOK, min_value = db_utils.sql_load_fr_db(sql)
    if min_value:
        Statistics_list[0] = min_value[0][0]

    #median value
    median_value = db_utils.calculate_median_value(u'w_levels', meas_or_level_masl, obsid)
    if median_value:
        Statistics_list[1] = median_value

    #max value
    if meas_or_level_masl=='meas':
        sql = r"""select max(meas) from w_levels where obsid = '"""
    else:
        sql = r"""select min(level_masl) from w_levels where obsid = '"""
    sql += obsid
    sql += r"""'"""
    ConnectionOK, max_value = db_utils.sql_load_fr_db(sql)
    if max_value:
        Statistics_list[3] = max_value[0][0]

    return meas_or_level_masl, Statistics_list

