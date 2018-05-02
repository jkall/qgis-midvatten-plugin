# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that returns a report with water quality data for the selected obs_point. 
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
import codecs
import os
import time  # for debugging

import PyQt4
import ast
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtCore import QUrl, Qt, QDir
from PyQt4.QtGui import QDesktopServices, QApplication, QCursor

import db_utils
import qgis
# midvatten modules
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from midvatten_utils import general_exception_handler

custom_drillreport_dialog = PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'compact_w_qual_report.ui'))[0]

class CompactWqualReportUi(PyQt4.QtGui.QMainWindow, custom_drillreport_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate(u'CompactWqualReportUi',
                                                          u"Compact Drillreport")))  # Set the title for the dialog

        self.stored_settings_key = u'compactwqualreport'
        self.stored_settings = utils.get_stored_settings(self.ms, self.stored_settings_key, {})
        self.update_from_stored_settings(self.stored_settings)

        self.connect(self.pushButton_ok, PyQt4.QtCore.SIGNAL("clicked()"), self.wqualreport)

        #self.connect(self.pushButton_cancel, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.close())

        self.connect(self.pushButton_update_from_string, PyQt4.QtCore.SIGNAL("clicked()"), self.ask_and_update_stored_settings)

        self.show()


    @utils.general_exception_handler
    def wqualreport(self):

        num_data_cols = int(self.num_data_cols.text())
        rowheader_colwidth_percent = int(self.rowheader_colwidth_percent.text())
        empty_row_between_tables = self.empty_row_between_tables.isChecked()
        page_break_between_tables = self.page_break_between_tables.isChecked()
        skip = ru(self.skip_reports.text()).split(u';')
        keep = ru(self.keep_reports.text()).split(u';')
        skip_reports_with_parameters = {'NOT IN': skip if any(skip) else [],
                                        'IN': keep if any(keep) else []}


        obsids = sorted(utils.getselectedobjectnames(qgis.utils.iface.activeLayer()))  # selected obs_point is now found in obsid[0]

        if not obsids:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'CompactWqualReportUi', u'Must select at least 1 obsid in selected layer')))
            raise utils.UsageError()
        self.save_stored_settings()

        wqual = Wqualreport(self.ms.settingsdict, obsids, num_data_cols, rowheader_colwidth_percent, empty_row_between_tables,
                            page_break_between_tables, skip_reports_with_parameters)

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
            self.num_data_cols.setText('10')
            self.rowheader_colwidth_percent.setText('15')
            self.empty_row_between_tables.setChecked(False)
            self.page_break_between_tables.setChecked(True)
            self.skip_reports.setText('')
            self.keep_reports.setText('')

    @utils.general_exception_handler
    def ask_and_update_stored_settings(self):
        self.stored_settings = self.ask_for_stored_settings(self.stored_settings)
        self.update_from_stored_settings(self.stored_settings)
        self.save_stored_settings()

    def save_stored_settings(self):
        stored_settings = {}
        for attrname in [u'num_data_cols',
                        u'rowheader_colwidth_percent',
                        u'empty_row_between_tables',
                        u'page_break_between_tables',
                        u'skip_reports',
                        u'keep_reports']:
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

        msg = ru(QCoreApplication.translate(u'CompactWqualReportUi', u'Replace the settings string with a new settings string.'))
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
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'CompactWqualReportUi', u'Translating string to dict failed, see log message panel')),
                                           log_msg=str(e))
            raise utils.UsageError()
        else:
            return as_dict


class Wqualreport():        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    @general_exception_handler
    def __init__(self, settingsdict, obsids, num_data_cols, rowheader_colwidth_percent, empty_row_between_tables,
                            page_break_between_tables, skip_reports_with_parameters):
        #show the user this may take a long time...
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.settingsdict = settingsdict

        self.nr_header_rows = 3

        reportfolder = os.path.join(QDir.tempPath(), 'midvatten_reports')
        if not os.path.exists(reportfolder):
            os.makedirs(reportfolder)
        reportpath = os.path.join(reportfolder, "w_qual_report.html")
        #f = open(reportpath, "wb" )
        f = codecs.open(reportpath, "wb", "utf-8")

        #write some initiating html
        rpt = r"""<head><title>%s</title></head>"""%ru(QCoreApplication.translate(u'Wqualreport', u'water quality report from Midvatten plugin for QGIS'))
        rpt += r""" <meta http-equiv="content-type" content="text/html; charset=utf-8" />""" #NOTE, all report data must be in 'utf-8'
        rpt += "<html><body>"
        #rpt += "<table width=\"100%\" border=\"1\">\n"
        #rpt2 = rpt.encode("utf-8")
        f.write(rpt)

        dbconnection = db_utils.DbConnectionManager()

        #skip_reports_with_parameters = {'IN': [u'Bly', u'Benso(ghi)perylen']}
        #obsids = utils.getselectedobjectnames()
        report_data = self.get_data(skip_reports_with_parameters, obsids, dbconnection)
        #num_data_cols = 17
        #rowheader_colwidth_percent = 11
        #empty_row_between_tables = False
        #page_break_between_tables = True

        for startcol in xrange(1, len(report_data[0]), num_data_cols):
            printlist = [[row[0]] for row in report_data]
            #print(printlist)
            for rownr, row in enumerate(report_data):
                printlist[rownr].extend(row[startcol:min(startcol+num_data_cols, len(row))])

            filtered = [row for row in printlist if any(row[1:])]

            self.htmlcols = len(filtered[0])
            self.WriteHTMLReport(filtered, f, rowheader_colwidth_percent, empty_row_between_tables=empty_row_between_tables,
                        page_break_between_tables=page_break_between_tables)

        dbconnection.closedb()
        # write some finishing html and close the file
        f.write("\n</body></html>")
        f.close()

        QApplication.restoreOverrideCursor()  # now this long process is done and the cursor is back as normal

        if report_data:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def get_data(self, skip_or_keep_reports_with_parameters, obsids, dbconnection):
        """

        :param skip_or_keep_reports_with_parameters: a dict like {'IN': ['par1', 'par2'], 'NOT IN': ['par3', 'par4']}
        The parameter skip_or_keep_reports_with_parameters is used to filter reports.
        :param obsids:
        :param dbconnection:
        :return:
        """
        skip_reports = ''

        for in_or_not_in, thelist in skip_or_keep_reports_with_parameters.iteritems():
            if not thelist:
                continue
            skip_reports += r""" AND report {IN or NOT IN} (SELECT DISTINCT report FROM {table}
                                WHERE {parameter} IN ({skip_parameters}))
                            """.format(**{'table': self.settingsdict['wqualtable'],
                                          'parameter': self.settingsdict['wqual_paramcolumn'],
                                          'skip_parameters': sql_list(thelist),
                                          'IN or NOT IN': in_or_not_in})

        sql = '''SELECT obsid, date_time, report, {parameter} || ', ' ||
                 CASE WHEN {unit} IS NULL THEN '' ELSE {unit} END,
                 reading_txt 
                 FROM {table} WHERE obsid in ({obsids}) {skip_reports}
              '''.format(**{'parameter': self.settingsdict['wqual_paramcolumn'],
                            'unit': self.settingsdict['wqual_unitcolumn'],
                            'table': self.settingsdict['wqualtable'],
                            'obsids': sql_list(obsids),
                            'skip_reports': skip_reports})

        rows = db_utils.sql_load_fr_db(sql, dbconnection=dbconnection)[1]

        data = {}
        for row in rows:
            data.setdefault(row[0], {}).setdefault(row[1], {}).setdefault(row[2], {})[row[3]] = row[4]

        distinct_parameters = sorted(set([p for obsid, date_times in data.iteritems()
                                    for date_time, reports in date_times.iteritems()
                                        for reports, parameters in reports.iteritems()
                                            for p in parameters.keys()]))

        outlist = [['obsid'], ['date_time'], ['report']]
        outlist.extend([[p] for p in distinct_parameters])

        for obsid, date_times in sorted(data.iteritems()):
            for date_time, reports in sorted(date_times.iteritems()):
                for report, parameters in sorted(reports.iteritems()):
                    outlist[0].append(obsid)
                    outlist[1].append(date_time)
                    outlist[2].append(report)

                    for parameterlist in outlist[3:]:
                        reading_txt = parameters.get(parameterlist[0], '')
                        parameterlist.append(reading_txt)

        return outlist

    def WriteHTMLReport(self, ReportData, f, rowheader_colwidth_percent, empty_row_between_tables=False,
                        page_break_between_tables=False):
        #tabellbredd = 180 + 75*self.htmlcols
        rpt = u"""<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 class="no-spacing" CELLSPACING=0 PADDING-BOTTOM=0 PADDING=0>"""
        #rpt = "<table width=\""
        #rpt += str(tabellbredd) # set table total width from no of water quality analyses
        #rpt += "\" border=\"1\">\n"
        f.write(rpt)

        for counter, sublist in enumerate(ReportData):
            sublist = ru(sublist, keep_containers=True)
            try:
                if counter < self.nr_header_rows:
                    rpt = u"<tr><TH WIDTH={}%><font size=1>{}</font></th>".format(str(rowheader_colwidth_percent), sublist[0])

                    data_colwidth = (100.0 - float(rowheader_colwidth_percent)) / len(sublist[1:])

                    coltext = u"<th width ={colwidth}%><font size=1>{data}</font></th>"
                    rpt += "".join([coltext.format(**{u"colwidth": str(data_colwidth),
                                                      u"data": x}) for x in sublist[1:]])

                    #Same columns on last table:
                    #if len(sublist[1:]) < len(ReportData[0][1:]):
                    #    rpt += u"".join([coltext.format(" ") for x in xrange(len(ReportData[0][1:]) - len(sublist[1:]))])

                    rpt += u"</tr>\n"
                else:
                    rpt = u"<tr>"
                    rpt += u"""<td align=\"left\"><font size=1>{}</font></td>""".format(sublist[0])
                    coltext = u"""<td align=\"right\"><font size=1>{}</font></td>"""
                    rpt += u"".join([coltext.format(x) for x in sublist[1:]])

                    #Same columns on last table:
                    #if len(sublist[1:]) < len(ReportData[0][1:]):
                    #    rpt += u"".join([coltext.format(" ") for x in xrange(len(ReportData[0][1:]) - len(sublist[1:]))])

                    rpt += u"</tr>\n"
            except:
                try:
                    print("here was an error: %s"%sublist)
                except:
                    pass
            f.write(rpt)

        #All in one table:
        if empty_row_between_tables:
            f.write("""<tr><td>empty_row_between_tables</td></tr>""")

        f.write("\n</table><p></p><p></p>")

        #Separate tables:
        if page_break_between_tables:
            f.write("""<p style="page-break-before: always">""")


def sql_list(alist):
    return u', '.join(["'{}'".format(x) for x in alist])