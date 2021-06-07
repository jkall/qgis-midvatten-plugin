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
from __future__ import absolute_import
from __future__ import print_function

import ast
import codecs
import os
from builtins import object
from builtins import range
from builtins import str

import numpy as np
import pandas as pd
import qgis
import qgis.PyQt

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QUrl, QDir
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QApplication

from midvatten.tools.utils import common_utils, db_utils, gui_utils
from midvatten.tools.utils.common_utils import returnunicode as ru, general_exception_handler


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

        self.date_time_formats = {'YYYY-MM': '%Y-%m',
                                  'YYYY-MM-DD': '%Y-%m-%d',
                                  'YYYY-MM-DD hh': '%Y-%m-%d %H',
                                  'YYYY-MM-DD hh:mm': '%Y-%m-%d %H:%M',
                                  'YYYY-MM-DD hh:mm:ss': '%Y-%m-%d %H:%M:%S'}

        self.methods = {'concat': lambda x: ', '.join([ru(y) for y in x.values]),
                    'avg': lambda x: round(sum([float(y) for y in x.values]) / float(len(x.values)), num_decimals(x.values)) if all([floatable(y) for y in x.values]) else ', '.join([ru(y) for y in x.values]),
                    'sum': lambda x: round(sum([float(y) for y in x]), num_decimals(x)) if all([floatable(y) for y in x.values]) else ', '.join(x.values),
                    'min': lambda x: min(x.values),
                    'max': lambda x: max(x.values)}

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

        self.from_active_layer.clicked.connect(lambda x: self.set_columns_from_activelayer())
        self.from_sql_table.clicked.connect(lambda x: self.set_columns_from_sql_layer())
        self.sql_table.currentIndexChanged.connect(lambda x: self.set_columns_from_sql_layer())

        self.pushButton_update_from_string.clicked.connect(lambda x: self.ask_and_update_stored_settings())

        self.sql_table.currentIndexChanged.connect(lambda: self.from_sql_table.setChecked(True))

        self.empty_row_between_tables.clicked.connect(
                     lambda: self.page_break_between_tables.setChecked(False) if self.empty_row_between_tables.isChecked() else True)
        self.page_break_between_tables.clicked.connect(
                     lambda: self.empty_row_between_tables.setChecked(False) if self.page_break_between_tables.isChecked() else True)

        self.stored_settings = common_utils.get_stored_settings(self.ms, self.stored_settings_key, {})
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

    @common_utils.general_exception_handler
    def wqualreport(self):
        common_utils.start_waiting_cursor()
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
        common_utils.stop_waiting_cursor()

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

    @common_utils.general_exception_handler
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
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('DrillreportUi',
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
                    common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('DrillreportUi', 'Programming error. The Qt-type %s is unhandled.')) % str(type(attr)))
                    continue
                stored_settings[attrname] = val

        self.stored_settings = stored_settings

        common_utils.save_stored_settings(self.ms, self.stored_settings, self.stored_settings_key)

    def ask_for_stored_settings(self, stored_settings):
        old_string = common_utils.anything_to_string_representation(stored_settings, itemjoiner=',\n', pad='    ',
                                                                                dictformatter='{\n%s}',
                                                                                listformatter='[\n%s]', tupleformatter='(\n%s, )')

        msg = ru(QCoreApplication.translate('CompactWqualReportUi', 'Replace the settings string with a new settings string.'))
        new_string = qgis.PyQt.QtWidgets.QInputDialog.getText(None, ru(QCoreApplication.translate('DrillreportUi', "Edit settings string")), msg,
                                                           qgis.PyQt.QtWidgets.QLineEdit.Normal, old_string)
        if not new_string[1]:
            raise common_utils.UserInterruptError()

        new_string_text = ru(new_string[0])
        if not new_string_text:
            return {}

        try:
            as_dict = ast.literal_eval(new_string_text)
        except Exception as e:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('CompactWqualReportUi', 'Translating string to dict failed, see log message panel')),
                                                              log_msg=str(e))
            raise common_utils.UsageError()
        else:
            return as_dict


class Wqualreport(object):        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    @general_exception_handler
    def __init__(self, settingsdict, num_data_cols, rowheader_colwidth_percent, empty_row_between_tables,
                 page_break_between_tables, from_active_layer, sql_table, sort_parameters_alphabetically,
                 sort_by_obsid, date_time_as_columns, date_time_format, method, data_column):
        #show the user this may take a long time...

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

        if date_time_as_columns:
            data_columns = ['obsid', 'date_time', 'report', 'parameter', 'unit', data_column]
        else:
            data_columns = ['obsid', 'date_time', 'parameter', 'unit', data_column]

        if from_active_layer:
            w_qual_lab_layer = qgis.utils.iface.activeLayer()
            if w_qual_lab_layer is None:
                raise common_utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'Must select a layer!')))
            if not w_qual_lab_layer.selectedFeatureCount():
                w_qual_lab_layer.selectAll()
            df = self.get_data_from_qgislayer(w_qual_lab_layer, data_columns)
        else:
            df = self.get_data_from_sql(sql_table, common_utils.getselectedobjectnames(), data_columns)

        if date_time_as_columns:
            columns = ['obsid', 'date_time']
            if 'report' in df.columns.values.tolist():
                columns.append('report')
            rows = ['parunit']
            values = [data_column]
            report_data = self.data_to_printlist(df, list(columns), list(rows), values, sort_parameters_alphabetically, sort_by_obsid, method, date_time_format)
        else:
            columns = ['obsid']
            rows = ['parunit', 'date_time']
            values = [data_column]
            report_data = self.data_to_printlist(df, list(columns), list(rows), values, sort_parameters_alphabetically, sort_by_obsid, method, date_time_format)

        # Split the data into separate tables with the specified number of columns
        for startcol in range(len(rows), len(report_data[0]), num_data_cols):
            printlist = [row[:len(rows)] for row in report_data]
            for rownr, row in enumerate(report_data):
                printlist[rownr].extend(row[startcol:min(startcol+num_data_cols, len(row))])

            filtered = [row for row in printlist if any(row[len(rows):])]

            self.htmlcols = len(filtered[0])
            self.write_html_table(filtered, f, rowheader_colwidth_percent, empty_row_between_tables=empty_row_between_tables,
                                  page_break_between_tables=page_break_between_tables, nr_header_rows=len(columns),
                                  nr_row_header_columns=len(rows))

        # write some finishing html and close the file
        f.write("\n</body></html>")
        f.close()

        if report_data:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def get_data_from_sql(self, table, obsids, columns):
        """

        :param skip_or_keep_reports_with_parameters: a dict like {'IN': ['par1', 'par2'], 'NOT IN': ['par3', 'par4']}
        The parameter skip_or_keep_reports_with_parameters is used to filter reports.
        :param obsids:
        :param dbconnection:
        :return:
        """
        dbconnection = db_utils.DbConnectionManager()
        fieldnames = db_utils.tables_columns(table, dbconnection)[table]
        missing = [column not in fieldnames for column in columns if column != 'report']
        columns = [column for column in columns if column in fieldnames]
        if any(missing):
                raise common_utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'The chosen table must contain columns %s')) % str(columns))


        sql = '''SELECT %s FROM %s'''%(', '.join(columns), table)
        if obsids:
            sql += ''' WHERE obsid in (%s)'''%sql_list(obsids)

        df = pd.read_sql(con=dbconnection.conn, sql=sql,
                         parse_dates=['date_time'])
        dbconnection.closedb()

        return df

    def get_data_from_qgislayer(self, w_qual_lab_layer, columns):
        """
        """
        fields = w_qual_lab_layer.fields()
        fieldnames = [field.name() for field in fields]
        missing = [column not in fieldnames for column in columns if column != 'report']
        columns = [column for column in columns if column in fieldnames]

        if any(missing):
                raise common_utils.UsageError(ru(QCoreApplication.translate('CompactWqualReport', 'The chosen layer must contain columns %s')) % str(columns))

        columns = [column for column in columns if column in fieldnames]

        indexes = {column: fields.indexFromName(column) for column in columns}
        features = [f for f in w_qual_lab_layer.getFeatures('True') if f.id() in w_qual_lab_layer.selectedFeatureIds()]
        file_data = [columns]
        file_data.extend([[ru(feature.attributes()[indexes[col]]) for col in columns]
                           for feature in features if feature.isValid()])

        df = pd.DataFrame(file_data[1:], columns=file_data[0])
        df['date_time'] = pd.to_datetime(df['date_time'])

        num_features = len(file_data) - 1
        invalid_features = len(features) - num_features
        if invalid_features:
            msgfunc = common_utils.MessagebarAndLog.warning
        else:
            msgfunc = common_utils.MessagebarAndLog.info

        msgfunc(bar_msg=ru(QCoreApplication.translate('CompactWqualReport', 'Layer processed with %s selected features, %s read features and %s invalid features.'))%(str(w_qual_lab_layer.selectedFeatureCount()), str(num_features), str(invalid_features)))
        return df

    def data_to_printlist(self, df, columns, rows, values, sort_parameters_alphabetically, sort_by_obsid, method, date_time_format):
        df['parunit'] = df['parameter'] + ', ' + df['unit'].fillna('')
        par_unit_order = {val: idx for idx, val in enumerate(df['parunit'].drop_duplicates(keep='first').tolist())}
        df['par_unit_order'] = df['parunit']
        df = df.replace({'par_unit_order': par_unit_order})
        df['date_time'] = df['date_time'].dt.strftime(date_time_format)
        rows.insert(0, 'par_unit_order')

        df = pd.pivot_table(df, values=values, index=rows, columns=columns,
                            aggfunc=method)

        if len(columns) >= 2:
            if sort_by_obsid:
                    order = ['obsid', 'date_time']
            else:
                    order = ['date_time', 'obsid']
            if 'report' in columns:
                order.append('report')
        else:
            order = ['obsid']
        df = df.sort_index(axis=1, level=order)

        if sort_parameters_alphabetically:
            df = df.sort_index(axis=0, level=[x for x in rows if x != 'par_unit_order'])
        else:
            df = df.sort_index(axis=0, level=[x for x in rows if x != 'parunit'])

        # Drop par_unit_order order
        df.index = df.index.droplevel(0)

        df = df.replace(np.nan, '', regex=True)

        index = [list(row) if isinstance(row, tuple) else [row] for row in df.index.values.tolist()]
        columns = [x[1:] for x in df.columns.values.tolist()]
        values = df.values.tolist()
        printlist = [['']*df.index.nlevels for _ in range(df.columns.nlevels-1)]
        [row.extend([c[idx] for c in columns]) for idx, row in enumerate(printlist)]
        [row.extend(values[idx]) for idx, row in enumerate(index)]
        printlist.extend(index)

        return printlist

    def write_html_table(self, ReportData, f, rowheader_colwidth_percent, empty_row_between_tables=False,
                         page_break_between_tables=False, nr_header_rows=3, nr_row_header_columns=1):
        rpt = """<TABLE WIDTH=100% BORDER=1 CELLPADDING=1 class="no-spacing" CELLSPACING=0 PADDING-BOTTOM=0 PADDING=0>"""
        f.write(rpt)

        for counter, row in enumerate(ReportData):
            row = ru(row, keep_containers=True)
            try:
                if counter < nr_header_rows:
                    rpt = "<tr>"
                    for idx in range(nr_row_header_columns):
                        rpt += "<TH WIDTH={}%><font size=1>{}</font></th>".format(str(rowheader_colwidth_percent), row[idx])

                    data_colwidth = (100.0 - (float(rowheader_colwidth_percent)*nr_row_header_columns)) / len(row[nr_row_header_columns:])

                    coltext = "<th width ={colwidth}%><font size=1>{data}</font></th>"
                    rpt += "".join([coltext.format(**{"colwidth": str(data_colwidth),
                                                      "data": x}) for x in row[nr_row_header_columns:]])

                    rpt += "</tr>\n"
                else:
                    rpt = "<tr>"
                    for idx in range(nr_row_header_columns):
                        rpt += """<td align=\"left\"><font size=1>{}</font></td>""".format(row[idx])
                    coltext = """<td align=\"right\"><font size=1>{}</font></td>"""
                    rpt += "".join([coltext.format(x) for x in row[nr_row_header_columns:]])
                    rpt += "</tr>\n"
            except:
                try:
                    print("here was an error: %s"%row)
                except:
                    pass
            f.write(rpt)

        f.write("\n</table><p></p><p></p>")

        #All in one table:Wqualreport
        if empty_row_between_tables:
            f.write("""<p>empty_row_between_tables</p>""")

        #Separate tables:
        if page_break_between_tables:
            f.write("""<p style="page-break-before: always"></p>""")

def isnan(x):
    if x is None:
        return True
    try:
        answer = np.isnan(x)
    except TypeError:
        return False
    else:
        return answer


def sql_list(alist):
    return ', '.join(["'{}'".format(x) for x in alist])

def floatable(anything):
    if isinstance(anything, (pd.DataFrame, pd.Series)):
        try:
            anything.astype('float64')
        except ValueError as e:
            return False
        else:
            return True
    else:
        try:
            float(anything)
        except (ValueError, TypeError):
            return False
        else:
            return True

def num_decimals(alist):
    try:
        [float(x.replace(',', '.')) if isinstance(x, str) else float(x) for x in alist]
    except (TypeError, ValueError):
        return 0

    min_decimals = min([len(str(x).replace(',', '.').split('.')[-1])
                        if len(str(x).replace(',', '.').split('.')) == 2 else None
                        for x in alist])
    return min_decimals if min_decimals is not None else 0
