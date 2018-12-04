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
from builtins import str
from builtins import object
import db_utils
from qgis.PyQt.QtCore import QUrl, QDir
from qgis.PyQt.QtGui import QDesktopServices
import qgis.PyQt
import ast

import os
import locale
from collections import OrderedDict
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
import codecs
from time import sleep
import qgis

from qgis.PyQt.QtCore import QCoreApplication


custom_drillreport_dialog = qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'custom_drillreport.ui'))[0]

class DrillreportUi(qgis.PyQt.QtWidgets.QMainWindow, custom_drillreport_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        self.stored_settings_key = 'customdrillreportstoredsettings'
        self.stored_settings = utils.get_stored_settings(self.ms, self.stored_settings_key, {})
        self.update_from_stored_settings(self.stored_settings)

        self.pushButton_ok.clicked.connect(lambda x: self.drillreport())

        self.pushButton_cancel.clicked.connect(lambda x: self.close())

        self.pushButton_update_from_string.clicked.connect(lambda x: self.ask_and_update_stored_settings())

        self.show()

    @utils.general_exception_handler
    def drillreport(self):
        general_metadata = [x for x in self.general_metadata.toPlainText().split('\n') if x]
        geo_metadata = [x for x in self.geo_metadata.toPlainText().split('\n') if x]
        strat_columns = [x for x in self.strat_columns.toPlainText().split('\n') if x]
        header_in_table = self.header_in_table.isChecked()
        skip_empty = self.skip_empty.isChecked()
        include_comments = self.include_comments.isChecked()
        obsids = sorted(utils.getselectedobjectnames(qgis.utils.iface.activeLayer()))  # selected obs_point is now found in obsid[0]
        general_metadata_header = self.general_metadata_header.text()
        geo_metadata_header = self.geo_metadata_header.text()
        strat_columns_header = self.strat_columns_header.text()
        comment_header = self.comment_header.text()
        empty_row_between_obsids = self.empty_row_between_obsids.isChecked()
        topleft_topright_colwidths = self.topleft_topright_colwidths.text().split(';')
        general_colwidth = self.general_colwidth.text().split(';')
        geo_colwidth = self.geo_colwidth.text().split(';')
        decimal_separator = self.decimal_separator.text()
        if not obsids:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('DrillreportUi', 'Must select at least 1 obsid in selected layer')))
            raise utils.UsageError()
        self.save_stored_settings()
        drillrep = Drillreport(obsids, self.ms, general_metadata, geo_metadata, strat_columns, header_in_table,
                               skip_empty, include_comments, general_metadata_header, geo_metadata_header, strat_columns_header,
                               comment_header, empty_row_between_obsids, topleft_topright_colwidths, general_colwidth,
                               geo_colwidth, decimal_separator)

    @utils.general_exception_handler
    def ask_and_update_stored_settings(self):
        self.stored_settings = self.ask_for_stored_settings(self.stored_settings)
        self.update_from_stored_settings(self.stored_settings)
        self.save_stored_settings()

    def update_from_stored_settings(self, stored_settings):
        if isinstance(stored_settings, dict) and stored_settings:
            for attr, val in stored_settings.items():
                try:
                    selfattr = getattr(self, attr)
                except:
                    pass
                else:
                    if isinstance(selfattr, qgis.PyQt.QtWidgets.QPlainTextEdit):
                        if isinstance(val, (list, tuple)):
                            val = '\n'.join(val)
                        selfattr.setPlainText(val)
                    elif isinstance(selfattr, qgis.PyQt.QtWidgets.QCheckBox):
                        selfattr.setChecked(val)
                    elif isinstance(selfattr, qgis.PyQt.QtWidgets.QLineEdit):
                        selfattr.setText(val)
        else:
            # Settings:
            # --------------
            # The order and content of the geographical and general tables will follow general_metadata and geo_metadata list.
            # All obs_points columns could appear here except geometry.
            # The XY-reference system is added a bit down in the script to the list geo_data. The append has to be commented away
            # if it's not wanted.
            self.general_metadata.setPlainText('\n'.join(['type',
                                                           'h_tocags',
                                                           'material',
                                                           'diam',
                                                           'drillstop',
                                                           'screen',
                                                           'drilldate']))

            self.geo_metadata.setPlainText('\n'.join(['east',
                                                       'north',
                                                       'ne_accur',
                                                       'ne_source',
                                                       'h_source',
                                                       'h_toc',
                                                       'h_accur']))

            self.strat_columns.setPlainText('\n'.join(['depth',
                                                        'geology',
                                                        'geoshort',
                                                        'capacity',
                                                        'development',
                                                        'comment']))

            self.general_metadata_header.setText(
                ru(QCoreApplication.translate('Drillreport2', 'General information')))
            self.geo_metadata_header.setText(
                ru(QCoreApplication.translate('Drillreport2', 'Geographical information')))
            self.strat_columns_header.setText(ru(QCoreApplication.translate('Drillreport2', 'Stratigraphy')))
            self.comment_header.setText(ru(QCoreApplication.translate('Drillreport2', 'Comment')))
            ##If False, the header will be written outside the table
            # header_in_table = True
            ##If True, headers/values in general_metadata and geo_metadata will be skipped if the value is empty, else they
            ##will be printed anyway
            # skip_empty = False
            # include_comments = True
            ###############

    def save_stored_settings(self):
        stored_settings = {}
        for attrname in ['general_metadata',
                        'geo_metadata',
                        'strat_columns',
                        'header_in_table',
                        'skip_empty',
                        'include_comments',
                        'general_metadata_header',
                        'geo_metadata_header',
                        'strat_columns_header',
                        'comment_header',
                        'empty_row_between_obsids',
                        'topleft_topright_colwidths',
                        'general_colwidth',
                        'geo_colwidth',
                        'decimal_separator']:
            try:
                attr = getattr(self, attrname)
            except:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('DrillreportUi',
                                                                                  "Programming error. Attribute name %s didn't exist in self.")) % attrname)
            else:
                if isinstance(attr, qgis.PyQt.QtWidgets.QPlainTextEdit):
                    val = [x for x in attr.toPlainText().split('\n') if x]
                elif isinstance(attr, qgis.PyQt.QtWidgets.QCheckBox):
                    val = attr.isChecked()
                elif isinstance(attr, qgis.PyQt.QtWidgets.QLineEdit):
                    val = attr.text()
                else:
                    utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('DrillreportUi', 'Programming error. The Qt-type %s is unhandled.'))%str(type(attr)))
                    continue
                stored_settings[attrname] = val

        self.stored_settings = stored_settings

        utils.save_stored_settings(self.ms, self.stored_settings, self.stored_settings_key)

    def ask_for_stored_settings(self, stored_settings):
        old_string = utils.anything_to_string_representation(stored_settings, itemjoiner=',\n', pad='    ',
                                                             dictformatter='{\n%s}',
                                                             listformatter='[\n%s]', tupleformatter='(\n%s, )')

        msg = ru(QCoreApplication.translate('DrillreportUi', 'Replace the settings string with a new settings string.'))
        new_string = qgis.PyQt.QtWidgets.QInputDialog.getText(None, ru(QCoreApplication.translate('DrillreportUi', "Edit settings string")), msg,
                                                           qgis.PyQt.QtWidgets.QLineEdit.Normal, old_string)
        if not new_string[1]:
            raise utils.UserInterruptError()

        new_string_text = ru(new_string[0])
        if not new_string_text:
            return {}

        try:
            as_dict = ast.literal_eval(new_string_text)
        except Exception as e:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('DrillreportUi', 'Translating string to dict failed, see log message panel')),
                                           log_msg=str(e))
            raise utils.UsageError()
        else:
            return as_dict


class Drillreport(object):        # general observation point info for the selected object

    def __init__(self, obsids, settingsdict, general_metadata, geo_metadata, strat_columns, header_in_table,
         skip_empty, include_comments, general_metadata_header, geo_metadata_header, strat_columns_header,
         comment_header, empty_row_between_obsids, topleft_topright_colwidths, general_colwidth,
         geo_colwidth, decimal_separator):

        reportfolder = os.path.join(QDir.tempPath(), 'midvatten_reports')
        if not os.path.exists(reportfolder):
            os.makedirs(reportfolder)
        reportpath = os.path.join(reportfolder, "drill_report.html")
        logopath = os.path.join(os.sep,os.path.dirname(__file__),"..","templates","midvatten_logga.png")
        imgpath = os.path.join(os.sep,os.path.dirname(__file__),"..","templates")

        if len(obsids) == 0:
            utils.pop_up_info(ru(QCoreApplication.translate('Drillreport', "Must select one or more obsids!")))
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

        dbconnection = db_utils.DbConnectionManager()

        obs_points_cols =  ["obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html"]
        all_obs_points_data = ru(db_utils.get_sql_result_as_dict('SELECT %s FROM obs_points WHERE obsid IN (%s) ORDER BY obsid'%(', '.join(obs_points_cols), ', '.join(["'{}'".format(x) for x in obsids])),
                                                            dbconnection=dbconnection)[1], keep_containers=True)

        if strat_columns:
            strat_sql_columns_list = [x.split(';')[0] for x in strat_columns]
            if 'depth' in strat_sql_columns_list:
                strat_sql_columns_list.extend(['depthtop', 'depthbot'])
                strat_sql_columns_list.remove('depth')
                strat_sql_columns_list = [x for x in strat_sql_columns_list if x not in ('obsid')]

            all_stratigrapy_data = ru(db_utils.get_sql_result_as_dict('SELECT obsid, %s FROM stratigraphy WHERE obsid IN (%s) ORDER BY obsid, stratid'%(', '.join(strat_sql_columns_list), ', '.join(["'{}'".format(x) for x in obsids])),
                                                                dbconnection=dbconnection)[1], keep_containers=True)
        else:
            all_stratigrapy_data = {}
            strat_sql_columns_list = []

        crs = ru(db_utils.sql_load_fr_db("""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'""", dbconnection=dbconnection)[1][0][0])
        crsname = ru(db_utils.get_srid_name(crs, dbconnection=dbconnection))

        dbconnection.closedb()

        f, rpt = self.open_file(', '.join(obsids), reportpath)
        rpt += r"""<html>"""
        for obsid in obsids:
            obs_points_data = all_obs_points_data[obsid][0]
            general_data_no_rounding = [x.split(';')[0] for x in general_metadata]
            general_rounding = [x.split(';')[1] if len(x.split(';')) == 2 else None for x in general_metadata]
            general_data = [(obs_points_translations.get(header, header), obs_points_data[obs_points_cols.index(header)-1]) for header in general_data_no_rounding]
            if geo_metadata:
                geo_metadata_no_rounding = [x.split(';')[0] for x in geo_metadata]
                geo_rounding = [x.split(';')[1] if len(x.split(';')) == 2 else None for x in geo_metadata]
                geo_data = [(obs_points_translations.get(header, header), obs_points_data[obs_points_cols.index(header)-1]) for header in geo_metadata_no_rounding]
                if 'east' in geo_metadata_no_rounding or 'north' in geo_metadata_no_rounding:
                    geo_data.append((ru(QCoreApplication.translate('Drillreport2', 'XY Reference system')), '%s'%('%s, '%crsname if crsname else '') + 'EPSG:' + crs))
            else:
                geo_data = []
                geo_rounding = []

            strat_data = all_stratigrapy_data.get(obsid, None)

            if include_comments:
                comment_data = [obs_points_data[obs_points_cols.index(header)-1] for header in ('com_onerow', 'com_html') if
                                all([obs_points_data[obs_points_cols.index(header)-1].strip(),
                                     'text-indent:0px;"><br /></p>' not in obs_points_data[obs_points_cols.index(header)-1],
                                     'text-indent:0px;"></p>' not in obs_points_data[obs_points_cols.index(header)-1],
                                     'text-indent:0px;">NULL</p>' not in obs_points_data[obs_points_cols.index(header)-1].strip()])]
            else:
                comment_data = []

            rpt += self.write_obsid(obsid, general_data, geo_data, strat_data, comment_data, strat_columns,
                                    header_in_table=header_in_table, skip_empty=skip_empty,
                                    general_metadata_header=general_metadata_header,
                                    geo_metadata_header=geo_metadata_header,
                                    strat_columns_header=strat_columns_header,
                                    comment_header=comment_header,
                                    general_rounding=general_rounding,
                                    geo_rounding=geo_rounding,
                                    strat_sql_columns_list=strat_sql_columns_list,
                                    topleft_topright_colwidths=topleft_topright_colwidths,
                                    general_colwidth=general_colwidth,
                                    geo_colwidth=geo_colwidth,
                                    decimal_separator=decimal_separator)
            rpt += r"""<p>    </p>"""
            if empty_row_between_obsids:
                rpt += r"""<p>empty_row_between_obsids</p>"""

        rpt += r"""</html>"""
        f.write(rpt)
        self.close_file(f, reportpath)

    def open_file(self, header, reportpath):
        #open connection to report file
        f = codecs.open(reportpath, "wb", "utf-8")
        #write some initiating html, header and also
        rpt = r"""<meta http-equiv="content-type" content="text/html; charset=utf-8" />"""
        rpt += r"""<head><title>%s %s</title></head>"""%(header, ru(QCoreApplication.translate('Drillreport', 'General report from Midvatten plugin for QGIS')))

        return f, rpt

    def close_file(self, f, reportpath):
        f.write("\n</p></body></html>")
        f.close()
        #print reportpath#debug
        url_status = QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))
        return url_status

    def obsid_header(self, obsid):
        return r"""<h3 style="font-family:'Ubuntu';font-size:12pt; font-weight:600"><font size=4>%s</font></h3>"""%ru(obsid)

    def write_obsid(self, obsid, general_data, geo_data, strat_data, comment_data, strat_columns, header_in_table=True,
                    skip_empty=False, general_metadata_header='', geo_metadata_header='', strat_columns_header='',
                    comment_header='', general_rounding=[], geo_rounding=[], strat_sql_columns_list=[],
                    topleft_topright_colwidths=[], general_colwidth=[], geo_colwidth=[], decimal_separator='.'):
        """This part only handles writing the information. It does not do any db data collection."""

        rpt = ''

        if not header_in_table:
            rpt += self.obsid_header(obsid)

        rpt += r"""<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 class="no-spacing" CELLSPACING=0>"""

        if header_in_table:
        #Row 1, obsid header
            rpt += r"""<TR VALIGN=TOP>"""
            rpt += r"""<TD WIDTH=100% COLSPAN=2>"""
            rpt += self.obsid_header(obsid)
            rpt += r"""</TD>"""
            rpt += r"""</TR>"""


        #Row 2, general and geographical information
        rpt += r"""<TR VALIGN=TOP>"""
        if geo_data:
            if len(topleft_topright_colwidths) == 2:
                rpt += r"""<TD WIDTH=%s>""" % (topleft_topright_colwidths[0])
            else:
                rpt += r"""<TD WIDTH=60%>"""
        else:
            rpt += r"""<TD WIDTH=100% COLSPAN=2>"""


        rpt += self.write_two_col_table(general_data, general_metadata_header, skip_empty, general_rounding,
                                        general_colwidth, decimal_separator)
        rpt += r"""</TD>"""

        if geo_data:
            if len(topleft_topright_colwidths) == 2:
                rpt += r"""<TD WIDTH=%s>""" % (topleft_topright_colwidths[1])
            else:
                rpt += r"""<TD WIDTH=40%>"""

            rpt += self.write_two_col_table(geo_data, geo_metadata_header, skip_empty, geo_rounding, geo_colwidth,
                                            decimal_separator)
            rpt += r"""</TD>"""
        rpt += r"""</TR>"""

        #Row 3, stratigraphy and comments

        if strat_data or comment_data:
            rpt += r"""<TR VALIGN=TOP>"""
            rpt += r"""<TD WIDTH=100% COLSPAN=2>"""

            if strat_data:

                rpt += self.write_strat_data(strat_data, strat_columns, strat_columns_header, strat_sql_columns_list,
                                             decimal_separator)

            if comment_data:
                rpt += self.write_comment_data(comment_data, comment_header)

            rpt += r"""</TD>"""
            rpt += r"""</TR>"""
        rpt += r"""</TABLE>"""

        return rpt

    def write_two_col_table(self, data, table_header, skip_empty=False, column_rounding=None, col_widths=None, decimal_separator='.'):
        if column_rounding is None:
            column_rounding = []

        if table_header:
            rpt = r"""<P><U><B><font size=3>%s</font></B></U></P>"""%table_header
        else:
            rpt = r''

        if not col_widths or len(col_widths) != 2:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Drillreport2', 'Column width not entered correctly, must be like x;y. Was %s'%str(col_widths))))
            col_widths = ['2*', '3*']

        rpt += r"""<TABLE style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 class="no-spacing" CELLSPACING=0><COL WIDTH={}><COL WIDTH={}>""".format(col_widths[0], col_widths[1])

        rpt += r"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""
        for idx, header_value in enumerate(data):
            header, value = header_value
            header = ru(header)
            value = ru(value) if ru(value) is not None and ru(value) != 'NULL' else ''
            if skip_empty:
                if value and value != 'NULL' and value != header:
                    try:
                        _test = float(value)
                    except ValueError:
                        pass
                    else:
                        pass
                        #if _test == 0.0:
                        #    continue
                else:
                    continue
            try:
                round = column_rounding[idx]
            except IndexError:
                pass
            else:
                if round is not None:
                    try:
                        _test = float(value)
                    except ValueError:
                        pass
                    else:
                        #Round the numbers to the maximum given rounding.
                        int_and_dec = value.split('.')
                        if len(int_and_dec) == 2:
                            len_dec = len(int_and_dec[1])
                            prec = min(len_dec, int(round))
                        else:
                            prec = int(round)

                        value = '{:.{prec}f}'.format(float(value), prec=prec)

            if decimal_separator != '.':
                value = value.replace('.', decimal_separator)

            try:
                rpt += r"""<TR VALIGN=TOP><TD WIDTH=33%><P><font size=1>{}</font></P></TD><TD WIDTH=50%><P><font size=1>{}</font></P></TD></TR>""".format(header, value)
            except UnicodeEncodeError:
                try:
                    utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('custom_drillreport', 'Writing drillreport failed, see log message panel')),
                                                    log_msg=ru(QCoreApplication.translate('custom_drillreport', 'Writing header %s and value %s failed'))%(header, value))
                except:
                    pass
                raise
        rpt += r"""</p>"""
        rpt += r"""</TABLE>"""
        return rpt

    def write_strat_data(self, strat_data, _strat_columns, table_header, strat_sql_columns_list, decimal_separator):
        if table_header:
            rpt = r"""<P><U><B><font size=3>%s</font></B></U></P>""" % table_header
        else:
            rpt = r''
        strat_columns = [x.split(';')[0] for x in _strat_columns]

        col_widths = [x.split(';')[1] if len(x.split(';')) == 2 else '1*' for x in _strat_columns]


        rpt += r"""<TABLE style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 class="no-spacing" CELLSPACING=0>"""
        for col_width in col_widths:
            rpt += r"""<COL WIDTH={}>""".format(col_width)
        rpt += r"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""

        headers_txt = OrderedDict([('stratid', ru(QCoreApplication.translate('Drillreport2_strat', 'Layer number'))),
                                   ('depth', ru(QCoreApplication.translate('Drillreport2_strat', 'level (m b gs)'))),
                                   ('depthtop', ru(QCoreApplication.translate('Drillreport2_strat', 'top of layer (m b gs)'))),
                                   ('depthbot', ru(QCoreApplication.translate('Drillreport2_strat', 'bottom of layer (m b gs)'))),
                                    ('geology', ru(QCoreApplication.translate('Drillreport2_strat', 'geology, full text'))),
                                    ('geoshort', ru(QCoreApplication.translate('Drillreport2_strat', 'geology, short'))),
                                    ('capacity', ru(QCoreApplication.translate('Drillreport2_strat', 'capacity'))),
                                    ('development', ru(QCoreApplication.translate('Drillreport2_strat', 'development'))),
                                    ('comment', ru(QCoreApplication.translate('Drillreport2_strat', 'comment')))])

        if len(strat_data) > 0:
            rpt += r"""<TR VALIGN=TOP>"""
            for header in strat_columns:
                rpt += r"""<TD><P><font size=2><u>{}</font></P></u></TD>""".format(headers_txt[header])
            rpt += r"""</TR>"""

            for rownr, row in enumerate(strat_data):

                rpt += r"""<TR VALIGN=TOP>"""
                for col in strat_columns:
                    if col == 'depth':
                        try:
                            depthtop_idx = strat_sql_columns_list.index('depthtop')
                            depthbot_idx = strat_sql_columns_list.index('depthbot')
                        except ValueError:
                            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('Drillreport2',
                                                                                                  'Programming error, depthtop and depthbot columns was supposed to exist')))
                            rpt += r"""<TD><P><font size=1> </font></P></TD>""".format(value)
                        else:
                            depthtop = '' if row[depthtop_idx] == 'NULL' else row[depthtop_idx].replace('.', decimal_separator)
                            depthbot = '' if row[depthbot_idx] == 'NULL' else row[depthbot_idx].replace('.', decimal_separator)
                            rpt += r"""<TD><P><font size=1>{}</font></P></TD>""".format(' - '.join([depthtop, depthbot]))
                    else:
                        value_idx = strat_sql_columns_list.index(col)
                        value = '' if row[value_idx] == 'NULL' else row[value_idx]
                        if col in ('depthtop', 'depthbot') and decimal_separator != '.':
                            value = value.replace('.', decimal_separator)
                        rpt += r"""<TD><P><font size=1>{}</font></P></TD>""".format(value)

                rpt += r"""</TR>"""
        rpt += r"""</p>"""
        rpt += r"""</TABLE>"""

        return rpt

    def write_comment_data(self, comment_data, header):
        if comment_data:
            if header:
                rpt = r"""<P><U><B><font size=3>{}</font></B></U></P>""".format(header)
            else:
                rpt = r''

            rpt += r"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;"><font size=1>"""
            rpt += r'. '.join([ru(x) for x in comment_data if ru(x) not in ['','NULL']])
            rpt += r"""</font></p>"""
        else:
            rpt = ''

        return rpt


def GetStatistics(obsid = ''):
    Statistics_list = [0]*4

    columns = ['meas', 'level_masl']
    # default value
    meas_or_level_masl= 'meas'

    #number of values, also decide wehter to use meas or level_masl in report
    for column in columns:
        sql = r"""select Count(%s) from w_levels where obsid = '%s'"""%(column, obsid)
        ConnectionOK, number_of_values = db_utils.sql_load_fr_db(sql)
        if number_of_values and number_of_values[0][0] > Statistics_list[2]:#this will select meas if meas >= level_masl
            meas_or_level_masl = column
            Statistics_list[2] = number_of_values[0][0]

    #min value
    if meas_or_level_masl=='meas':
        sql = r"""select min(meas) from w_levels where obsid = '%s'""" % obsid
    else:
        sql = r"""select max(level_masl) from w_levels where obsid = '%s'""" % obsid

    ConnectionOK, min_value = db_utils.sql_load_fr_db(sql)
    if min_value:
        Statistics_list[0] = min_value[0][0]

    #median value
    median_value = db_utils.calculate_median_value('w_levels', meas_or_level_masl, obsid)
    if median_value:
        Statistics_list[1] = median_value

    #max value
    if meas_or_level_masl=='meas':
        sql = r"""select max(meas) from w_levels where obsid = '%s' """ % obsid
    else:
        sql = r"""select min(level_masl) from w_levels where obsid = '%s' """ % obsid
    ConnectionOK, max_value = db_utils.sql_load_fr_db(sql)
    if max_value:
        Statistics_list[3] = max_value[0][0]

    return meas_or_level_masl, Statistics_list

