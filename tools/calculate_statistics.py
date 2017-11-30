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
import os
import PyQt4
from PyQt4.QtCore import QCoreApplication

import db_utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
import gui_utils


calculate_statistics_dialog = PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calculate_statistics_ui.ui'))[0]

class CalculateStatisticsGui(PyQt4.QtGui.QMainWindow, calculate_statistics_dialog):
    def __init__(self, parent, midv_settings):
        self.iface = parent

        self.ms = midv_settings
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        tables_columns = db_utils.tables_columns()
        self.db_browser = DbBrowser(tables_columns, self.connect)


        self.gridLayout.addWidget(self.db_browser.widget, 0, 0)

        self.connect(self.pushButton_ok, PyQt4.QtCore.SIGNAL("clicked()"), self.calculate)

        self.connect(self.pushButton_cancel, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.close())

        self.show()

    @utils.waiting_cursor
    def calculate(self):
        table = self.db_browser.table_list
        column = self.db_browser.column_list
        obsids = utils.get_selected_features_as_tuple()

        printlist = [obsid + ";" + ';'.join([str(x) for x in get_statistics(obsid=obsid, table=table, data_columns=[column])[1]]) for obsid in sorted(obsids)]
        printlist.reverse()
        printlist.append(ru(QCoreApplication.translate(u"Midvatten", 'Obsid;Min;Median;Nr of values;Max')))
        printlist.reverse()
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


def get_statistics(obsid ='', table=u'w_levels', data_columns=None):
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