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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
import codecs
import os
import time  # for debugging
from functools import partial

import qgis.PyQt
import ast
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QUrl, Qt, QDir
from qgis.PyQt.QtGui import QDesktopServices, QCursor
from qgis.PyQt.QtWidgets import QApplication

import db_utils
import gui_utils
import qgis
# midvatten modules
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from midvatten_utils import general_exception_handler

custom_drillreport_dialog = qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'compact_w_qual_report.ui'))[0]

class CompactWqualReportUi(qgis.PyQt.QtWidgets.QMainWindow, custom_drillreport_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate('CompactWqualReportUi',
                                                          "Compact water quality report")))  # Set the title for the dialog

        self.manual_label.setText("<a href=\"https://github.com/jkall/qgis-midvatten-plugin/wiki/5.-Plots-and-reports#create-compact-water-quality-report\">%s</a>"%QCoreApplication.translate('CompactWqualReportUi', '(manual)'))
        self.manual_label.setOpenExternalLinks(True)

        tables = list(db_utils.tables_columns().keys())
        self.sql_table.addItems(sorted(tables))
        #Use w_qual_lab as default.
        gui_utils.set_combobox(self.sql_table, 'w_qual_lab', add_if_not_exists=False)

        self.save_attrnames = ['num_data_cols',
                         'rowheader_colwidth_percent',
                         'empty_row_between_tables',
                         'page_break_between_tables',
                         'from_active_layer',
                         'from_sql_table',
                         'sql_table']

        self.stored_settings_key = 'compactwqualreport'

        self.stored_settings = utils.get_stored_settings(self.ms, self.stored_settings_key, {})
        self.update_from_stored_settings(self.stored_settings)

        self.pushButton_ok.clicked.connect(lambda x: self.wqualreport())

        #self.pushButton_cancel, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.close())

        self.pushButton_update_from_string.clicked.connect(lambda x: self.ask_and_update_stored_settings())

        self.sql_table.currentIndexChanged.connect(lambda: self.from_sql_table.setChecked(True))

        self.empty_row_between_tables.clicked.connect(
                     lambda: self.page_break_between_tables.setChecked(False) if self.empty_row_between_tables.isChecked() else True)
        self.page_break_between_tables.clicked.connect(
                     lambda: self.empty_row_between_tables.setChecked(False) if self.page_break_between_tables.isChecked() else True)

        self.show()

    @utils.general_exception_handler
    def wqualreport(self):

        num_data_cols = int(self.num_data_cols.text())
        rowheader_colwidth_percent = int(self.rowheader_colwidth_percent.text())
        empty_row_between_tables = self.empty_row_between_tables.isChecked()
        page_break_between_tables = self.page_break_between_tables.isChecked()
        from_active_layer = self.from_active_layer.isChecked()
        from_sql_table = self.from_sql_table.isChecked()
        sql_table = self.sql_table.currentText()

        self.save_stored_settings(self.save_attrnames)

        wqual = Wqualreport(self.ms.settingsdict, num_data_cols, rowheader_colwidth_percent, empty_row_between_tables,
                            page_break_between_tables, from_active_layer, sql_table)

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
                    elif isinstance(selfattr, (qgis.PyQt.QtWidgets.QCheckBox, qgis.PyQt.QtWidgets.QRadioButton)):
                        selfattr.setChecked(val)
                    elif isinstance(selfattr, qgis.PyQt.QtWidgets.QLineEdit):
                        selfattr.setText(val)
                    elif isinstance(selfattr, qgis.PyQt.QtWidgets.QComboBox):
                        gui_utils.set_combobox(selfattr, val, add_if_not_exists=False)

    @utils.general_exception_handler
    def ask_and_update_stored_settings(self):
        self.stored_settings = self.ask_for_stored_settings(self.stored_settings)
        self.update_from_stored_settings(self.stored_settings)
        self.save_stored_settings(self.save_attrnames)

    def save_stored_settings(self, save_attrnames):
        stored_settings = {}
        for attrname in save_attrnames:
            try:
                attr = getattr(self, attrname)
            except:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('DrillreportUi',
                                                                                  "Programming error. Attribute name %s didn't exist in self.")) % attrname)
            else:
                if isinstance(attr, qgis.PyQt.QtWidgets.QPlainTextEdit):
                    val = [x for x in attr.toPlainText().split('\n') if x]
                elif isinstance(attr, (qgis.PyQt.QtWidgets.QCheckBox, qgis.PyQt.QtWidgets.QRadioButton)):
                    val = attr.isChecked()
                elif isinstance(attr, qgis.PyQt.QtWidgets.QLineEdit):
                    val = attr.text()
                elif isinstance(attr, qgis.PyQt.QtWidgets.QComboBox):
                    val = attr.currentText()
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

        msg = ru(QCoreApplication.translate('CompactWqualReportUi', 'Replace the settings string with a new settings string.'))
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
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('CompactWqualReportUi', 'Translating string to dict failed, see log message panel')),
                                           log_msg=str(e))
            raise utils.UsageError()
        else:
            return as_dict


class Wqualreport(object):        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    @general_exception_handler
    def __init__(self, settingsdict, num_data_cols, rowheader_colwidth_percent, empty_row_between_tables,
                            page_break_between_tables, from_active_layer, sql_table):
        #show the user this may take a long time...
        utils.start_waiting_cursor()

        self.nr_header_rows = 3

        reportfolder = os.path.join(QDir.tempPath(), 'midvatten_reports')
        if not os.path.exists(reportfolder):
            os.makedirs(reportfolder)
        reportpath = os.path.join(reportfolder, "w_qual_report.html")
        f = codecs.open(reportpath, "wb", "utf-8")

        #write some initiating html
        rpt = r"""<head><title>%s</title></head>"""%ru(QCoreApplication.translate('Wqualreport', 'water quality report from Midvatten plugin for QGIS'))
        rpt += r""" <meta http-equiv="content-type" content="text/html; charset=utf-8" />""" #NOTE, all report data must be in 'utf-8'
        rpt += "<html><body>"
        f.write(rpt)

        if from_active_layer:
            utils.pop_up_info(ru(QCoreApplication.translate('CompactWqualReport', 'Check that exported number of rows are identical to expected number of rows!\nFeatures in layers from sql queries can be invalid and then excluded from the report!')), 'Warning!')
            w_qual_lab_layer = qgis.utils.iface.activeLayer()
            if w_qual_lab_layer is None:
                raise utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'Must select a layer!')))
            if not w_qual_lab_layer.selectedFeatureCount():
                w_qual_lab_layer.selectAll()
            data = self.get_data_from_qgislayer(w_qual_lab_layer)
        else:
            data = self.get_data_from_sql(sql_table, utils.getselectedobjectnames())

        report_data, num_data = self.data_to_printlist(data)
        utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('CompactWqualReport', 'Created report from %s number of rows.'))%str(num_data))

        for startcol in range(1, len(report_data[0]), num_data_cols):
            printlist = [[row[0]] for row in report_data]
            for rownr, row in enumerate(report_data):
                printlist[rownr].extend(row[startcol:min(startcol+num_data_cols, len(row))])

            filtered = [row for row in printlist if any(row[1:])]

            self.htmlcols = len(filtered[0])
            self.WriteHTMLReport(filtered, f, rowheader_colwidth_percent, empty_row_between_tables=empty_row_between_tables,
                        page_break_between_tables=page_break_between_tables)

        # write some finishing html and close the file
        f.write("\n</body></html>")
        f.close()

        utils.stop_waiting_cursor()  # now this long process is done and the cursor is back as normal

        if report_data:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def get_data_from_sql(self, table, obsids):
        """

        :param skip_or_keep_reports_with_parameters: a dict like {'IN': ['par1', 'par2'], 'NOT IN': ['par3', 'par4']}
        The parameter skip_or_keep_reports_with_parameters is used to filter reports.
        :param obsids:
        :param dbconnection:
        :return:
        """
        sql = '''SELECT obsid, date_time, report, parameter, unit, reading_txt FROM %s'''%table
        if obsids:
            sql += ''' WHERE obsid in (%s)'''%sql_list(obsids)

        rows = db_utils.sql_load_fr_db(sql)[1]

        data = {}
        for row in rows:
            data.setdefault(row[0], {}).setdefault(row[1], {}).setdefault(row[2], {})[', '.join([x for x in [row[3], row[4]] if x])] = row[5]

        return data

    def get_data_from_qgislayer(self, w_qual_lab_layer):
        """
        obsid, date_time, report, {parameter} || ', ' ||
                 CASE WHEN {unit} IS NULL THEN '' ELSE {unit} END,
                 reading_txt 
        """
        fields = w_qual_lab_layer.fields()
        fieldnames = [field.name() for field in fields]
        columns = ['obsid', 'date_time', 'report', 'parameter', 'unit', 'reading_txt']
        for column in columns:
            if not column in fieldnames:
                raise utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'The chosen layer must contain column %s'))%column)

        indexes = {column: fields.indexFromName(column) for column in columns}

        data = {}
        for feature in w_qual_lab_layer.getSelectedFeatures():
            attrs = feature.attributes()
            obsid = attrs[indexes['obsid']]
            date_time = attrs[indexes['date_time']]
            report = attrs[indexes['report']]
            parameter = attrs[indexes['parameter']]
            unit = attrs[indexes['unit']]
            reading_txt = attrs[indexes['reading_txt']]
            par_unit = ', '.join([x for x in [parameter, unit] if x])
            data.setdefault(obsid, {}).setdefault(date_time, {}).setdefault(report, {})[par_unit] = reading_txt
        return data

    def data_to_printlist(self, data):
        num_data = 0

        distinct_parameters = set([p for obsid, date_times in data.items()
                                   for date_time, reports in date_times.items()
                                        for reports, parameters in reports.items()
                                            for p in list(parameters.keys())])

        outlist = [['obsid'], ['date_time'], ['report']]
        outlist.extend([[p] for p in sorted(distinct_parameters, key=lambda s: s.lower())])

        for obsid, date_times in sorted(iter(data.items()), key=lambda s: s[0].lower()):
            for date_time, reports in sorted(date_times.items()):
                for report, parameters in sorted(reports.items()):
                    outlist[0].append(obsid)
                    outlist[1].append(date_time)
                    outlist[2].append(report)

                    for parameterlist in outlist[3:]:
                        if parameterlist[0] in parameters:
                            reading_txt = parameters[parameterlist[0]]
                            num_data += 1
                        else:
                            reading_txt = ''
                        parameterlist.append(reading_txt)

        return outlist, num_data

    def WriteHTMLReport(self, ReportData, f, rowheader_colwidth_percent, empty_row_between_tables=False,
                        page_break_between_tables=False):
        rpt = """<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 class="no-spacing" CELLSPACING=0 PADDING-BOTTOM=0 PADDING=0>"""
        f.write(rpt)

        for counter, sublist in enumerate(ReportData):
            sublist = ru(sublist, keep_containers=True)
            try:
                if counter < self.nr_header_rows:
                    rpt = "<tr><TH WIDTH={}%><font size=1>{}</font></th>".format(str(rowheader_colwidth_percent), sublist[0])

                    data_colwidth = (100.0 - float(rowheader_colwidth_percent)) / len(sublist[1:])

                    coltext = "<th width ={colwidth}%><font size=1>{data}</font></th>"
                    rpt += "".join([coltext.format(**{"colwidth": str(data_colwidth),
                                                      "data": x}) for x in sublist[1:]])

                    rpt += "</tr>\n"
                else:
                    rpt = "<tr>"
                    rpt += """<td align=\"left\"><font size=1>{}</font></td>""".format(sublist[0])
                    coltext = """<td align=\"right\"><font size=1>{}</font></td>"""
                    rpt += "".join([coltext.format(x) for x in sublist[1:]])

                    rpt += "</tr>\n"
            except:
                try:
                    print("here was an error: %s"%sublist)
                except:
                    pass
            f.write(rpt)

        f.write("\n</table><p></p><p></p>")

        #All in one table:
        if empty_row_between_tables:
            f.write("""<p>empty_row_between_tables</p>""")

        #Separate tables:
        if page_break_between_tables:
            f.write("""<p style="page-break-before: always"></p>""")


def sql_list(alist):
    return ', '.join(["'{}'".format(x) for x in alist])