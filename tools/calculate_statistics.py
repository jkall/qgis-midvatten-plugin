# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that calculates some general statistics
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
import os
import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication

import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
import gui_utils


calculate_statistics_dialog = qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calculate_statistics_ui.ui'))[0]

class CalculateStatisticsGui(qgis.PyQt.QtWidgets.QMainWindow, calculate_statistics_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        tables_columns = db_utils.tables_columns()
        self.db_browser = DbBrowser(tables_columns, self.connect)


        self.gridLayout.addWidget(self.db_browser.widget, 0, 0)

        self.connect(self.pushButton_ok, qgis.PyQt.QtCore.SIGNAL("clicked()"), self.calculate)

        self.connect(self.pushButton_cancel, qgis.PyQt.QtCore.SIGNAL("clicked()"), lambda : self.close())

        self.show()

    @utils.waiting_cursor
    @utils.general_exception_handler
    def calculate(self):
        table = self.db_browser.table_list
        column = self.db_browser.column_list
        obsids = utils.get_selected_features_as_tuple()

        if not all([table, column, obsids]):
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'CalculateStatisticsGui', u'''Calculation failed, make sure you've selected a table, a column and features with a column obsid.''')))
            return None

        sql_function_order = [u'min', u'max', u'avg', u'count']
        stats = get_statistics(obsids, table, column, sql_function_order=sql_function_order, median=True)
        printlist = []
        printlist.append(ru(QCoreApplication.translate(u"Midvatten", 'Obsid;Min;Median;Average;Max;Nr of values')))
        printlist.extend([u';'.join([ru(x) for x in (obsid, v[0], v[4], v[2], v[1], v[3])]) for obsid, v in sorted(stats.items())])
        utils.MessagebarAndLog.info(
            bar_msg=ru(QCoreApplication.translate("Midvatten", 'Statistics for table %s column %s done, see log for results.'))%(table, column),
            log_msg='\n'.join(printlist), duration=15, button=True)

class DbBrowser(gui_utils.DistinctValuesBrowser):

    def __init__(self, tables_columns, connect):
        super(DbBrowser, self).__init__(tables_columns, connect)

        self.distinct_value_label.setVisible(False)
        self._distinct_value.setVisible(False)
        self.browser_label.setVisible(False)

    @staticmethod
    def get_distinct_values(tablename, columnname):
        return []

def get_statistics(obsids, table, column, sql_function_order=None, median=True, dbconnection=None):
    if not isinstance(dbconnection, db_utils.DbConnectionManager):
        dbconnection = db_utils.DbConnectionManager()

    if sql_function_order is None:
        sql_function_order = [u'min', u'max', u'avg', u'count']
    if not isinstance(obsids, (list, tuple)):
        obsids = [obsids]

    sql = u'select obsid, %s from %s where obsid in (%s) group by obsid'%(u', '.join([u'%s(%s)'%(func, column) for func in sql_function_order]), table, u', '.join([u"'{}'".format(x) for x in obsids]))
    _res = db_utils.get_sql_result_as_dict(sql, dbconnection=dbconnection)[1]
    res = dict([(obsid, list(v[0])) for obsid, v in _res.items()])
    if median:
        [v.append(db_utils.calculate_median_value(table, column, obsid, dbconnection)) for obsid, v in res.items()]
    return res

def get_statistics_for_single_obsid(obsid ='', table=u'w_levels', data_columns=None):
    Statistics_list = [0]*4

    if data_columns is None:
        data_columns = ['meas', 'level_masl']
    data_column = data_columns[0] #default value


    #number of values, also decide wehter to use meas or level_masl in report
    for column in data_columns:
        sql = r"""select Count(%s) from %s where obsid = '%s'"""%(column, table, obsid)
        ConnectionOK, number_of_values = db_utils.sql_load_fr_db(sql)
        if number_of_values and number_of_values[0][0] > Statistics_list[2]:#this will select meas if meas >= level_masl
            data_column = column
            Statistics_list[2] = number_of_values[0][0]

    #min value
    sql = r"""select min(%s) from %s where obsid = '%s'"""%(data_column, table, obsid)
    ConnectionOK, min_value = db_utils.sql_load_fr_db(sql)
    if min_value:
        Statistics_list[0] = min_value[0][0]

    #median value
    median_value = db_utils.calculate_median_value(table, data_column, obsid)
    if median_value:
        Statistics_list[1] = median_value

    #max value
    sql = r"""select max(%s) from %s where obsid = '%s'"""%(data_column, table, obsid)
    ConnectionOK, max_value = db_utils.sql_load_fr_db(sql)
    if max_value:
        Statistics_list[3] = max_value[0][0]

    return data_column, Statistics_list