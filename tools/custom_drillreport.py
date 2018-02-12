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
import PyQt4
import ast

import os
import locale
from collections import OrderedDict
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
import codecs
from time import sleep
import qgis

from PyQt4.QtCore import QCoreApplication


custom_drillreport_dialog = PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'custom_drillreport.ui'))[0]

class DrillreportUi(PyQt4.QtGui.QMainWindow, custom_drillreport_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        self.stored_settings_key = u'customdrillreportstoredsettings'
        self.stored_settings = utils.get_stored_settings(self.ms, self.stored_settings_key, {})
        self.update_from_stored_settings(self.stored_settings)

        self.connect(self.pushButton_ok, PyQt4.QtCore.SIGNAL("clicked()"), self.drillreport)

        self.connect(self.pushButton_cancel, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.close())

        self.connect(self.pushButton_update_from_string, PyQt4.QtCore.SIGNAL("clicked()"), self.ask_and_update_stored_settings)

        self.show()

    @utils.general_exception_handler
    def drillreport(self):
        general_metadata = [x for x in self.general_metadata.toPlainText().split(u'\n') if x]
        geo_metadata = [x for x in self.geo_metadata.toPlainText().split(u'\n') if x]
        strat_columns = [x for x in self.strat_columns.toPlainText().split(u'\n') if x]
        header_in_table = self.header_in_table.isChecked()
        skip_empty = self.skip_empty.isChecked()
        include_comments = self.include_comments.isChecked()
        obsids = sorted(utils.getselectedobjectnames(qgis.utils.iface.activeLayer()))  # selected obs_point is now found in obsid[0]
        general_metadata_header = self.general_metadata_header.text()
        geo_metadata_header = self.geo_metadata_header.text()
        strat_columns_header = self.strat_columns_header.text()
        comment_header = self.comment_header.text()
        empty_row_between_obsids = self.empty_row_between_obsids.isChecked()
        topleft_topright_colwidths = self.topleft_topright_colwidths.text().split(u';')
        general_colwidth = self.general_colwidth.text().split(u';')
        geo_colwidth = self.geo_colwidth.text().split(u';')
        if not obsids:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'DrillreportUi', u'Must select at least 1 obsid in selected layer')))
            raise utils.UsageError()
        self.save_stored_settings()
        drillrep = Drillreport(obsids, self.ms, general_metadata, geo_metadata, strat_columns, header_in_table,
                               skip_empty, include_comments, general_metadata_header, geo_metadata_header, strat_columns_header,
                               comment_header, empty_row_between_obsids, topleft_topright_colwidths, general_colwidth,
                               geo_colwidth)

    @utils.general_exception_handler
    def ask_and_update_stored_settings(self):
        self.stored_settings = self.ask_for_stored_settings(self.stored_settings)
        self.update_from_stored_settings(self.stored_settings)
        self.save_stored_settings()

    def update_from_stored_settings(self, stored_settings):
        if isinstance(stored_settings, dict) and stored_settings:
            for attr, val in stored_settings.iteritems():
                try:
                    selfattr = getattr(self, attr)
                except:
                    pass
                else:
                    if isinstance(selfattr, PyQt4.QtGui.QPlainTextEdit):
                        if isinstance(val, (list, tuple)):
                            val = u'\n'.join(val)
                        selfattr.setPlainText(val)
                    elif isinstance(selfattr, PyQt4.QtGui.QCheckBox):
                        selfattr.setChecked(val)
                    elif isinstance(selfattr, PyQt4.QtGui.QLineEdit):
                        selfattr.setText(val)
        else:
            # Settings:
            # --------------
            # The order and content of the geographical and general tables will follow general_metadata and geo_metadata list.
            # All obs_points columns could appear here except geometry.
            # The XY-reference system is added a bit down in the script to the list geo_data. The append has to be commented away
            # if it's not wanted.
            self.general_metadata.setPlainText(u'\n'.join([u'type',
                                                           u'h_tocags',
                                                           u'material',
                                                           u'diam',
                                                           u'drillstop',
                                                           u'screen',
                                                           u'drilldate']))

            self.geo_metadata.setPlainText(u'\n'.join([u'east',
                                                       u'north',
                                                       u'ne_accur',
                                                       u'ne_source',
                                                       u'h_source',
                                                       u'h_toc',
                                                       u'h_accur']))

            self.strat_columns.setPlainText(u'\n'.join([u'depth',
                                                        u'geology',
                                                        u'geoshort',
                                                        u'capacity',
                                                        u'development',
                                                        u'comment']))

            self.general_metadata_header.setText(
                ru(QCoreApplication.translate(u'Drillreport2', u'General information')))
            self.geo_metadata_header.setText(
                ru(QCoreApplication.translate(u'Drillreport2', u'Geographical information')))
            self.strat_columns_header.setText(ru(QCoreApplication.translate(u'Drillreport2', u'Stratigraphy')))
            self.comment_header.setText(ru(QCoreApplication.translate(u'Drillreport2', u'Comment')))
            ##If False, the header will be written outside the table
            # header_in_table = True
            ##If True, headers/values in general_metadata and geo_metadata will be skipped if the value is empty, else they
            ##will be printed anyway
            # skip_empty = False
            # include_comments = True
            ###############

    def save_stored_settings(self):
        stored_settings = {}
        for attrname in [u'general_metadata',
                        u'geo_metadata',
                        u'strat_columns',
                        u'header_in_table',
                        u'skip_empty',
                        u'include_comments',
                        u'general_metadata_header',
                        u'geo_metadata_header',
                        u'strat_columns_header',
                        u'comment_header',
                        u'empty_row_between_obsids',
                        u'topleft_topright_colwidths',
                        u'general_colwidth',
                        u'geo_colwidth']:
            try:
                attr = getattr(self, attrname)
            except:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'DrillreportUi',
                                                                                  u"Programming error. Attribute name %s didn't exist in self.")) % attrname)
            else:
                if isinstance(attr, PyQt4.QtGui.QPlainTextEdit):
                    val = [x for x in attr.toPlainText().split(u'\n') if x]
                elif isinstance(attr, PyQt4.QtGui.QCheckBox):
                    val = attr.isChecked()
                elif isinstance(attr, PyQt4.QtGui.QLineEdit):
                    val = attr.text()
                else:
                    utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'DrillreportUi', u'Programming error. The Qt-type %s is unhandled.'))%str(type(attr)))
                    continue
                stored_settings[attrname] = val

        self.stored_settings = stored_settings

        utils.save_stored_settings(self.ms, self.stored_settings, self.stored_settings_key)

    def ask_for_stored_settings(self, stored_settings):
        old_string = utils.anything_to_string_representation(stored_settings, itemjoiner=u',\n', pad=u'    ',
                                                             dictformatter=u'{\n%s}',
                                                             listformatter=u'[\n%s]', tupleformatter=u'(\n%s, )')

        msg = ru(QCoreApplication.translate(u'DrillreportUi', u'Replace the settings string with a new settings string.'))
        new_string = PyQt4.QtGui.QInputDialog.getText(None, ru(QCoreApplication.translate(u'DrillreportUi', "Edit settings string")), msg,
                                                           PyQt4.QtGui.QLineEdit.Normal, old_string)
        if not new_string[1]:
            raise utils.UserInterruptError()

        new_string_text = ru(new_string[0])
        if not new_string_text:
            return {}

        try:
            as_dict = ast.literal_eval(new_string_text)
        except Exception as e:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'DrillreportUi', u'Translating string to dict failed, see log message panel')),
                                           log_msg=str(e))
            raise utils.UsageError()
        else:
            return as_dict


class Drillreport():        # general observation point info for the selected object

    def __init__(self, obsids, settingsdict, general_metadata, geo_metadata, strat_columns, header_in_table,
         skip_empty, include_comments, general_metadata_header, geo_metadata_header, strat_columns_header,
         comment_header, empty_row_between_obsids, topleft_topright_colwidths, general_colwidth,
         geo_colwidth):

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

        dbconnection = db_utils.DbConnectionManager()

        obs_points_cols =  ["obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html"]
        all_obs_points_data = ru(db_utils.get_sql_result_as_dict(u'SELECT %s FROM obs_points WHERE obsid IN (%s) ORDER BY obsid'%(u', '.join(obs_points_cols), u', '.join([u"'{}'".format(x) for x in obsids])),
                                                            dbconnection=dbconnection)[1], keep_containers=True)

        if strat_columns:
            strat_sql_columns_list = [x.split(u';')[0] for x in strat_columns]
            if u'depth' in strat_sql_columns_list:
                strat_sql_columns_list.extend([u'depthtop', u'depthbot'])
                strat_sql_columns_list.remove(u'depth')
                strat_sql_columns_list = [x for x in strat_sql_columns_list if x not in (u'obsid')]

            all_stratigrapy_data = ru(db_utils.get_sql_result_as_dict(u'SELECT obsid, %s FROM stratigraphy WHERE obsid IN (%s) ORDER BY obsid, stratid'%(u', '.join(strat_sql_columns_list), u', '.join([u"'{}'".format(x) for x in obsids])),
                                                                dbconnection=dbconnection)[1], keep_containers=True)
        else:
            all_stratigrapy_data = {}
            strat_sql_columns_list = []

        crs = ru(db_utils.sql_load_fr_db(u"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'""", dbconnection=dbconnection)[1][0][0])
        crsname = ru(db_utils.get_srid_name(crs, dbconnection=dbconnection))

        dbconnection.closedb()

        f, rpt = self.open_file(', '.join(obsids), reportpath)
        rpt += ur"""<html>"""
        for obsid in obsids:
            obs_points_data = all_obs_points_data[obsid][0]
            general_data_no_rounding = [x.split(u';')[0] for x in general_metadata]
            general_rounding = [x.split(u';')[1] if len(x.split(u';')) == 2 else None for x in general_metadata]
            general_data = [(obs_points_translations.get(header, header), obs_points_data[obs_points_cols.index(header)-1]) for header in general_data_no_rounding]
            if geo_metadata:
                geo_metadata_no_rounding = [x.split(u';')[0] for x in geo_metadata]
                geo_rounding = [x.split(u';')[1] if len(x.split(u';')) == 2 else None for x in geo_metadata]
                geo_data = [(obs_points_translations.get(header, header), obs_points_data[obs_points_cols.index(header)-1]) for header in geo_metadata_no_rounding]
                if u'east' in geo_metadata_no_rounding or u'north' in geo_metadata_no_rounding:
                    geo_data.append((ru(QCoreApplication.translate('Drillreport2', u'XY Reference system')), '%s'%('%s, '%crsname if crsname else '') + 'EPSG:' + crs))
            else:
                geo_data = []
                geo_rounding = []

            strat_data = all_stratigrapy_data.get(obsid, None)

            if include_comments:
                comment_data = [obs_points_data[obs_points_cols.index(header)-1] for header in (u'com_onerow', u'com_html') if
                                all([obs_points_data[obs_points_cols.index(header)-1].strip(),
                                     u'text-indent:0px;"><br /></p>' not in obs_points_data[obs_points_cols.index(header)-1],
                                     u'text-indent:0px;"></p>' not in obs_points_data[obs_points_cols.index(header)-1],
                                     u'text-indent:0px;">NULL</p>' not in obs_points_data[obs_points_cols.index(header)-1].strip()])]
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
                                    geo_colwidth=geo_colwidth)
            rpt += ur"""<p>    </p>"""
            if empty_row_between_obsids:
                rpt += ur"""<p>empty_row_between_obsids</p>"""

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
        return ur"""<h3 style="font-family:'Ubuntu';font-size:12pt; font-weight:600"><font size=4>%s</font></h3>"""%ru(obsid)

    def write_obsid(self, obsid, general_data, geo_data, strat_data, comment_data, strat_columns, header_in_table=True,
                    skip_empty=False, general_metadata_header=u'', geo_metadata_header=u'', strat_columns_header=u'',
                    comment_header=u'', general_rounding=[], geo_rounding=[], strat_sql_columns_list=[],
                    topleft_topright_colwidths=[], general_colwidth=[], geo_colwidth=[]):
        """This part only handles writing the information. It does not do any db data collection."""

        rpt = u''

        if not header_in_table:
            rpt += self.obsid_header(obsid)

        rpt += ur"""<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 class="no-spacing" CELLSPACING=0>"""

        if header_in_table:
        #Row 1, obsid header
            rpt += ur"""<TR VALIGN=TOP>"""
            rpt += ur"""<TD WIDTH=100% COLSPAN=2>"""
            rpt += self.obsid_header(obsid)
            rpt += ur"""</TD>"""
            rpt += ur"""</TR>"""


        #Row 2, general and geographical information
        rpt += ur"""<TR VALIGN=TOP>"""
        if geo_data:
            if len(topleft_topright_colwidths) == 2:
                rpt += ur"""<TD WIDTH=%s>""" % (topleft_topright_colwidths[0])
            else:
                rpt += ur"""<TD WIDTH=60%>"""
        else:
            rpt += ur"""<TD WIDTH=100%>"""


        rpt += self.write_two_col_table(general_data, general_metadata_header, skip_empty, general_rounding, general_colwidth)
        rpt += ur"""</TD>"""

        if geo_data:
            if len(topleft_topright_colwidths) == 2:
                rpt += ur"""<TD WIDTH=%s>""" % (topleft_topright_colwidths[1])
            else:
                rpt += ur"""<TD WIDTH=40%>"""

            rpt += self.write_two_col_table(geo_data, geo_metadata_header, skip_empty, geo_rounding, geo_colwidth)
            rpt += ur"""</TD>"""
        rpt += ur"""</TR>"""

        #Row 3, stratigraphy and comments

        if strat_data or comment_data:
            rpt += ur"""<TR VALIGN=TOP>"""
            rpt += ur"""<TD WIDTH=100% COLSPAN=2>"""

            if strat_data:

                rpt += self.write_strat_data(strat_data, strat_columns, strat_columns_header, strat_sql_columns_list)

            if comment_data:
                rpt += self.write_comment_data(comment_data, comment_header)

            rpt += ur"""</TD>"""
            rpt += ur"""</TR>"""
        rpt += ur"""</TABLE>"""

        return rpt

    def write_two_col_table(self, data, table_header, skip_empty=False, column_rounding=None, col_widths=None):
        if column_rounding is None:
            column_rounding = []

        if table_header:
            rpt = ur"""<P><U><B><font size=3>%s</font></B></U></P>"""%table_header
        else:
            rpt = ur''

        if not col_widths or len(col_widths) != 2:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'Drillreport2', u'Column width not entered correctly, must be like x;y. Was %s'%str(col_widths))))
            col_widths = [u'2*', u'3*']

        rpt += ur"""<TABLE style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 class="no-spacing" CELLSPACING=0><COL WIDTH={}><COL WIDTH={}>""".format(col_widths[0], col_widths[1])

        rpt += ur"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""
        for idx, header_value in enumerate(data):
            header, value = header_value
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
                        int_and_dec = value.split(u'.')
                        if len(int_and_dec) == 2:
                            len_dec = len(int_and_dec[1])
                            prec = min(len_dec, int(round))
                        else:
                            prec = int(round)

                        value = u'{:.{prec}f}'.format(float(value), prec=prec)

            try:
                rpt += ur"""<TR VALIGN=TOP><TD WIDTH=33%><P><font size=1>{}</font></P></TD><TD WIDTH=50%><P><font size=1>{}</font></P></TD></TR>""".format(header, value)
            except UnicodeEncodeError:
                try:
                    utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'custom_drillreport', u'Writing drillreport failed, see log message panel')),
                                                    log_msg=ru(QCoreApplication.translate(u'custom_drillreport', u'Writing header %s and value %s failed'))%(header, value))
                except:
                    pass
                raise
        rpt += r"""</p>"""
        rpt += r"""</TABLE>"""
        return rpt

    def write_strat_data(self, strat_data, _strat_columns, table_header, strat_sql_columns_list):
        if table_header:
            rpt = ur"""<P><U><B><font size=3>%s</font></B></U></P>""" % table_header
        else:
            rpt = ur''
        strat_columns = [x.split(u';')[0] for x in _strat_columns]

        col_widths = [x.split(u';')[1] if len(x.split(u';')) == 2 else u'1*' for x in _strat_columns]


        rpt += ur"""<TABLE style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 class="no-spacing" CELLSPACING=0>"""
        for col_width in col_widths:
            rpt += ur"""<COL WIDTH={}>""".format(col_width)
        rpt += ur"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;">"""

        headers_txt = OrderedDict([(u'stratid', ru(QCoreApplication.translate(u'Drillreport2_strat', u'Layer number'))),
                                   (u'depth', ru(QCoreApplication.translate(u'Drillreport2_strat', u'level (m b gs)'))),
                                   (u'depthtop', ru(QCoreApplication.translate(u'Drillreport2_strat', u'top of layer (m b gs)'))),
                                   (u'depthbot', ru(QCoreApplication.translate(u'Drillreport2_strat', u'bottom of layer (m b gs)'))),
                                    (u'geology', ru(QCoreApplication.translate(u'Drillreport2_strat', u'geology, full text'))),
                                    (u'geoshort', ru(QCoreApplication.translate(u'Drillreport2_strat', u'geology, short'))),
                                    (u'capacity', ru(QCoreApplication.translate(u'Drillreport2_strat', u'capacity'))),
                                    (u'development', ru(QCoreApplication.translate(u'Drillreport2_strat', u'development'))),
                                    (u'comment', ru(QCoreApplication.translate(u'Drillreport2_strat', u'comment')))])

        if len(strat_data) > 0:
            rpt += ur"""<TR VALIGN=TOP>"""
            for header in strat_columns:
                rpt += ur"""<TD><P><font size=2><u>{}</font></P></u></TD>""".format(headers_txt[header])
            rpt += ur"""</TR>"""

            for rownr, row in enumerate(strat_data):

                rpt += ur"""<TR VALIGN=TOP>"""
                for col in strat_columns:
                    if col == u'depth':
                        try:
                            depthtop_idx = strat_sql_columns_list.index(u'depthtop')
                            depthbot_idx = strat_sql_columns_list.index(u'depthbot')
                        except ValueError:
                            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'Drillreport2',
                                                                                                  u'Programming error, depthtop and depthbot columns was supposed to exist')))
                            rpt += ur"""<TD><P><font size=1> </font></P></TD>""".format(value)
                        else:
                            depthtop = u'' if row[depthtop_idx] == 'NULL' else row[depthtop_idx]
                            depthbot = u'' if row[depthbot_idx] == 'NULL' else row[depthbot_idx]
                            rpt += ur"""<TD><P><font size=1>{}</font></P></TD>""".format(u' - '.join([depthtop, depthbot]))
                    else:
                        value_idx = strat_sql_columns_list.index(col)
                        value = u'' if row[value_idx] == 'NULL' else row[value_idx]
                        rpt += ur"""<TD><P><font size=1>{}</font></P></TD>""".format(value)

                rpt += ur"""</TR>"""
        rpt += ur"""</p>"""
        rpt += ur"""</TABLE>"""

        return rpt

    def write_comment_data(self, comment_data, header):
        if comment_data:
            if header:
                rpt = ur"""<P><U><B><font size=3>{}</font></B></U></P>""".format(header)
            else:
                rpt = ur''

            rpt += ur"""<p style="font-family:'Ubuntu'; font-size:8pt; font-weight:400; font-style:normal;"><font size=1>"""
            rpt += ur'. '.join([ru(x) for x in comment_data if ru(x) not in ['','NULL']])
            rpt += ur"""</font></p>"""
        else:
            rpt = u''

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
    median_value = db_utils.calculate_median_value(u'w_levels', meas_or_level_masl, obsid)
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

