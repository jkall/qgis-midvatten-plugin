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
from operator import itemgetter
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
import date_utils
from midvatten_utils import returnunicode as ru
from midvatten_utils import general_exception_handler

custom_drillreport_dialog = qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'compact_w_qual_report.ui'))[0]

class CompactWqualReportUi(qgis.PyQt.QtWidgets.QMainWindow, custom_drillreport_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.tables_columns = db_utils.tables_columns()

        self.ms = midv_settings
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.setWindowTitle(ru(QCoreApplication.translate('CompactWqualReportUi',
                                                          "Compact water quality report")))  # Set the title for the dialog

        self.manual_label.setText("<a href=\"https://github.com/jkall/qgis-midvatten-plugin/wiki/5.-Plots-and-reports#create-compact-water-quality-report\">%s</a>"%QCoreApplication.translate('CompactWqualReportUi', '(manual)'))
        self.manual_label.setOpenExternalLinks(True)

        def num_decimals(alist):
            try:
                [float(x.replace(',', '.')) for x in alist]
            except (TypeError, ValueError):
                return None

            min_decimals = min([len(str(x).replace(',', '.').split('.')[-1])
                                if len(str(x).replace(',', '.').split('.')) == 2 else None
                                for x in alist])
            return min_decimals


        self.date_time_formats = {'YYYY-MM': '%Y-%m',
                                  'YYYY-MM-DD': '%Y-%m-%d',
                                  'YYYY-MM-DD hh': '%Y-%m-%d %H',
                                  'YYYY-MM-DD hh:mm': '%Y-%m-%d %H:%M',
                                  'YYYY-MM-DD hh:mm:ss': '%Y-%m-%d %H:%M:%S'}
        self.methods = {'concat': lambda x: ', '.join([ru(y) for y in x]),
                        'avg': lambda x: x[0] if len(x) < 2 else round(sum([float(y) for y in x])/float(len(x)), num_decimals(x)),
                        'sum': lambda x: x[0] if len(x) < 2 else round(sum([float(y) for y in x]), num_decimals(x)),
                        'min': lambda x: min([float(y) for y in x]),
                        'max': lambda x: max([float(y) for y in x])}

        self.date_time_format.addItems(self.date_time_formats.keys())
        self.method.addItems(self.methods.keys())

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
                         'sql_table',
                         'sort_alphabetically',
                         'sort_by_obsid',
                         'date_time_as_columns',
                         'date_time_format',
                         'method',
                         'data_column']

        self.stored_settings_key = 'compactwqualreport'

        self.pushButton_ok.clicked.connect(lambda x: self.wqualreport())

        #self.from_active_layer.setToolTip(ru(QCoreApplication.translate('CompactWqualReport', 'Do not use an sqlite database view or a qgis sql query as the active layer! This can result in invalid features and mismatching data!\nIf the active layer is a layer like that, export the layer to a different format or convert into a proper sqlite table instead.')))
        #self.label_4.setToolTip(self.from_active_layer.toolTip())
        self.from_active_layer.clicked.connect(lambda x: self.set_columns_from_activelayer())
        self.from_sql_table.clicked.connect(lambda x: self.set_columns_from_sql_layer())
        self.sql_table.currentIndexChanged.connect(lambda x: self.set_columns_from_sql_layer())

        self.pushButton_update_from_string.clicked.connect(lambda x: self.ask_and_update_stored_settings())

        self.sql_table.currentIndexChanged.connect(lambda: self.from_sql_table.setChecked(True))

        self.empty_row_between_tables.clicked.connect(
                     lambda: self.page_break_between_tables.setChecked(False) if self.empty_row_between_tables.isChecked() else True)
        self.page_break_between_tables.clicked.connect(
                     lambda: self.empty_row_between_tables.setChecked(False) if self.page_break_between_tables.isChecked() else True)

        self.stored_settings = utils.get_stored_settings(self.ms, self.stored_settings_key, {})
        self.update_from_stored_settings(self.stored_settings)

        self.show()

    def set_columns_from_sql_layer(self):
        fields = self.tables_columns[self.sql_table.currentText()]
        self.set_columns(fields)

    def set_columns_from_activelayer(self):
        fields = [field.name() for field in qgis.utils.iface.activeLayer().fields()]
        self.set_columns(fields)

    def set_columns(self, fields):
        self.data_column.clear()
        self.data_column.addItems(sorted(fields))

    @utils.general_exception_handler
    def wqualreport(self):

        num_data_cols = int(self.num_data_cols.text())
        rowheader_colwidth_percent = int(self.rowheader_colwidth_percent.text())
        empty_row_between_tables = self.empty_row_between_tables.isChecked()
        page_break_between_tables = self.page_break_between_tables.isChecked()
        from_active_layer = self.from_active_layer.isChecked()
        from_sql_table = self.from_sql_table.isChecked()
        sql_table = self.sql_table.currentText()
        sort_alphabetically = self.sort_alphabetically.isChecked()
        sort_by_obsid = self.sort_by_obsid.isChecked()
        date_time_as_columns = self.date_time_as_columns.isChecked()
        date_time_format = self.date_time_formats[self.date_time_format.currentText()]
        method = self.methods[self.method.currentText()]
        data_column = self.data_column.currentText()

        self.save_stored_settings(self.save_attrnames)

        wqual = Wqualreport(self.ms.settingsdict, num_data_cols, rowheader_colwidth_percent, empty_row_between_tables,
                            page_break_between_tables, from_active_layer, sql_table, sort_alphabetically, sort_by_obsid,
                            date_time_as_columns, date_time_format, method, data_column)

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
                        if bool(val):
                            selfattr.click()
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
                 page_break_between_tables, from_active_layer, sql_table, sort_parameters_alphabetically,
                 sort_by_obsid, date_time_as_columns, date_time_format, method, data_column):
        #show the user this may take a long time...
        utils.start_waiting_cursor()

        if date_time_as_columns:
            nr_header_rows = 3
        else:
            nr_header_rows = 1

        dateformatter = lambda x: date_utils.datestring_to_date(x).strftime(date_time_format)

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
            w_qual_lab_layer = qgis.utils.iface.activeLayer()
            if w_qual_lab_layer is None:
                raise utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'Must select a layer!')))
            if not w_qual_lab_layer.selectedFeatureCount():
                w_qual_lab_layer.selectAll()
            data, par_unit_order = self.get_data_from_qgislayer(w_qual_lab_layer, dateformatter, data_column)
        else:
            data, par_unit_order = self.get_data_from_sql(sql_table, utils.getselectedobjectnames(), dateformatter, data_column)

        if date_time_as_columns:
            report_data, num_data = self.data_to_printlist(data, par_unit_order, sort_parameters_alphabetically, sort_by_obsid)
        else:
            report_data, num_data = self.data_to_printlist_dates(data, par_unit_order, sort_parameters_alphabetically, method)

        utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('CompactWqualReport', 'Created report from %s number of rows.'))%str(num_data))

        for startcol in range(1, len(report_data[0]), num_data_cols):
            printlist = [[row[0]] for row in report_data]
            for rownr, row in enumerate(report_data):
                printlist[rownr].extend(row[startcol:min(startcol+num_data_cols, len(row))])

            filtered = [row for row in printlist if any(row[1:])]

            self.htmlcols = len(filtered[0])
            self.WriteHTMLReport(filtered, f, rowheader_colwidth_percent, empty_row_between_tables=empty_row_between_tables,
                        page_break_between_tables=page_break_between_tables, nr_header_rows=nr_header_rows)

        # write some finishing html and close the file
        f.write("\n</body></html>")
        f.close()

        utils.stop_waiting_cursor()  # now this long process is done and the cursor is back as normal

        if report_data:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def get_data_from_sql(self, table, obsids, dateformatter, data_column):
        """

        :param skip_or_keep_reports_with_parameters: a dict like {'IN': ['par1', 'par2'], 'NOT IN': ['par3', 'par4']}
        The parameter skip_or_keep_reports_with_parameters is used to filter reports.
        :param obsids:
        :param dbconnection:
        :return:
        """
        sql = '''SELECT obsid, date_time, report, parameter, unit, %s FROM %s'''%(data_column, table)
        if obsids:
            sql += ''' WHERE obsid in (%s)'''%sql_list(obsids)

        rows = db_utils.sql_load_fr_db(sql)[1]

        data = {}
        par_unit_order = []
        for row in rows:
            par_unit = ', '.join([x for x in [row[3], row[4]] if x])
            data.setdefault(row[0], {}).setdefault(dateformatter(row[1]), {}).setdefault(row[2], {})[par_unit] = row[5]
            if par_unit not in par_unit_order:
                par_unit_order.append(par_unit)

        return data, par_unit_order

    def get_data_from_qgislayer(self, w_qual_lab_layer, dateformatter, data_column):
        """
        obsid, date_time, report, {parameter} || ', ' ||
                 CASE WHEN {unit} IS NULL THEN '' ELSE {unit} END,
                 value
        """
        fields = w_qual_lab_layer.fields()
        nr_of_selected = w_qual_lab_layer.selectedFeatureCount()

        fieldnames = [field.name() for field in fields]
        columns = ['obsid', 'date_time', 'report', 'parameter', 'unit', data_column]
        for column in columns:
            if not column in fieldnames:
                raise utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'The chosen layer must contain column %s'))%column)

        indexes = {column: fields.indexFromName(column) for column in columns}

        selected_ids = w_qual_lab_layer.selectedFeatureIds()
        ids = [f for f in w_qual_lab_layer.getFeatures('True') if f.id() in selected_ids]

        data = {}
        par_unit_order = []
        invalid_features = 0
        num_features = 0
        for feature in ids: # selectedFeatures():
            if not feature.isValid():
                invalid_features += 1
                print("Invalid")
                continue

            attrs = feature.attributes()
            obsid = attrs[indexes['obsid']]
            date_time = dateformatter(attrs[indexes['date_time']])
            report = attrs[indexes['report']]
            parameter = attrs[indexes['parameter']]
            unit = attrs[indexes['unit']]
            value = attrs[indexes[data_column]]
            par_unit = ', '.join([x for x in [parameter, unit] if x])
            if par_unit not in par_unit_order:
                par_unit_order.append(par_unit)
            data.setdefault(obsid, {}).setdefault(date_time, {}).setdefault(report, {})[par_unit] = value
            num_features += 1

        if invalid_features:
            msgfunc = utils.MessagebarAndLog.warning
        else:
            msgfunc = utils.MessagebarAndLog.info

        msgfunc(bar_msg=ru(QCoreApplication.translate('CompactWqualReport', 'Layer processed with %s selected features, %s read features and %s invalid features.'))%(str(nr_of_selected), str(num_features), str(invalid_features)))

        return data, par_unit_order

    def data_to_printlist(self, data, par_unit_order, sort_parameters_alphabetically=True, sort_by_obsid=True):
        num_data = 0

        if sort_parameters_alphabetically:
            distinct_parameters = sorted(par_unit_order, key=lambda s: s[0].lower())
        else:
            distinct_parameters = par_unit_order

        outlist = [['obsid'], ['date_time'], ['report']]
        outlist.extend([[p] for p in distinct_parameters])

        data_as_list = [(obsid, date_time, report, parameters)
                        for obsid, date_times in data.items()
                        for date_time, reports in date_times.items()
                        for report, parameters in sorted(reports.items())]

        if sort_by_obsid:
            sort_key = lambda s: (s[0].lower(), s[1], s[2])
        else:
            sort_key = lambda s: (s[1], s[0], s[2])

        for obsid, date_time, report, parameters in sorted(data_as_list, key=sort_key):
            outlist[0].append(obsid)
            outlist[1].append(date_time)
            outlist[2].append(report)

            for parameterlist in outlist[3:]:
                if parameterlist[0] in parameters:
                    value = parameters[parameterlist[0]]
                    num_data += 1
                else:
                    value = ''
                parameterlist.append(value)

        return outlist, num_data

    def data_to_printlist_dates(self, data, par_unit_order, sort_parameters_alphabetically=True, method=None):
        num_data = 0

        if sort_parameters_alphabetically:
            distinct_parameters = sorted(par_unit_order, key=lambda s: s[0].lower())
        else:
            distinct_parameters = par_unit_order

        params_dates = {}
        for obsid, date_times in data.items():
            for date_time, reports in date_times.items():
                for report, parameters in sorted(reports.items()):
                    for parameter, reading_txt in parameters.items():
                        if date_time not in params_dates.get(parameter, []):
                            params_dates.setdefault(parameter, []).append(date_time)

        if sort_parameters_alphabetically:
            params_dates = {parameter: sorted(date_time) for parameter, date_time in sorted(params_dates.items())}
        else:
            params_dates = {parameter: sorted(params_dates[parameter]) for parameter in distinct_parameters}

        outlist = [['parameter', 'date_time']]
        outlist[0].extend(sorted(data.keys()))

        for parameter, date_times in params_dates.items():
            for date_time in date_times:
                outlist.append([parameter, date_time])
                for obsid in outlist[0][2:]:
                    if date_time in data[obsid]:
                        reports_parameters = data[obsid][date_time]
                        values = []
                        for report, parameters in reports_parameters.items():
                            if parameter in parameters:
                                values.append(parameters[parameter])
                        if values:
                            if method is not None:
                                try:
                                    word = method(values)
                                except:
                                    word = ', '.join([ru(y) for y in values])
                            else:
                                word = ''
                            outlist[-1].append(word)
                            num_data += 1
                        else:
                            outlist[-1].append('')
                    else:
                        outlist[-1].append('')

        return outlist, num_data

    def WriteHTMLReport(self, ReportData, f, rowheader_colwidth_percent, empty_row_between_tables=False,
                        page_break_between_tables=False, nr_header_rows=3):
        rpt = """<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 class="no-spacing" CELLSPACING=0 PADDING-BOTTOM=0 PADDING=0>"""
        f.write(rpt)

        for counter, sublist in enumerate(ReportData):
            sublist = ru(sublist, keep_containers=True)
            try:
                if counter < nr_header_rows:
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