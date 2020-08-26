# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles calculation of average water flow
 based on readings of accumulated volume. Data is read from, and written to, table w_flow. 
                              -------------------
        begin                : 2014-01-23
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

import qgis.PyQt

import qgis.utils

import datetime
import os
import datetime as dt

import db_utils
from matplotlib.dates import datestr2num
import import_data_to_db
import numpy as np
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
#from ui.calc_aveflow_dialog import Ui_Dialog as Calc_Ui_Dialog
from qgis.PyQt import uic

from qgis.PyQt.QtCore import QCoreApplication

try:
    import pandas as pd
except:
    pandas_on = False
else:
    pandas_on = True

Calc_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calc_aveflow_dialog.ui'))[0]


class Calcave(qgis.PyQt.QtWidgets.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    def __init__(self, parent):
        qgis.PyQt.QtWidgets.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = utils.getselectedobjectnames()
        self.setWindowTitle(ru(QCoreApplication.translate('Calcave', "Calculate average flow"))) # Set the title for the dialog
        self.pushButton_All.clicked.connect(lambda x: self.calcall())
        self.pushButton_Selected.clicked.connect(lambda x: self.calcselected())
        self.pushButton_Cancel.clicked.connect(lambda x: self.close())

    def calcall(self, use_pandas=True):
        ok, obsar = db_utils.sql_load_fr_db('''SELECT DISTINCT obsid FROM w_flow WHERE flowtype = 'Accvol' ''')
        #if not ok:
        #    utils.MessagebarAndLog.critical(bar_msg=)
        if not obsar:
            utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('Calcave', "No observations with Accvol found, nothing calculated!")))
            return
        self.observations = [obs[0] for obs in obsar]
        if pandas_on and use_pandas:
            self.calculateaveflow_pandas()
        else:
            self.calculateaveflow()

    def calcselected(self, use_pandas=True):
        obsar = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())
        self.observations = [obs for obs in obsar] #turn into a list of python byte strings
        if pandas_on and use_pandas:
            self.calculateaveflow_pandas()
        else:
            self.calculateaveflow()

    def calculateaveflow(self):
        utils.start_waiting_cursor()
        date_from = self.FromDateTime.dateTime().toPyDateTime()
        date_to = self.ToDateTime.dateTime().toPyDateTime()
        #Identify distinct set of obsid and instrumentid with Accvol-data and within the user-defined date_time-interval:
        sql= """SELECT DISTINCT obsid, instrumentid FROM (SELECT * FROM w_flow WHERE flowtype = 'Accvol' AND date_time >= '%s' AND date_time <= '%s' AND obsid IN (%s))"""%(date_from,date_to, utils.sql_unicode_list(self.observations))
        #utils.pop_up_info(sql)#debug
        uniqueset = db_utils.sql_load_fr_db(sql)[1]  # The unique set of obsid and instrumentid is kept in uniqueset
        negativeflow = False
        for pyobsid, pyinstrumentid in uniqueset:
            sql= """select date_time, reading from w_flow where flowtype = 'Accvol' and obsid='%s' and instrumentid='%s' and date_time >='%s' and date_time <='%s' order by date_time"""%(pyobsid,pyinstrumentid,date_from,date_to)
            recs = db_utils.sql_load_fr_db(sql)[1]
            """Transform data to a numpy.recarray"""
            My_format = [('date_time', datetime.datetime), ('values', float)] #Define format with help from function datetime
            table = np.array(recs, dtype=My_format)  #NDARRAY
            table2=table.view(np.recarray)   # RECARRAY   Makes the two columns into callable objects, i.e. write table2.values
            for j, row in enumerate(table2):#This is where Aveflow is calculated for each obs and also written to db
                if j>0:#first row is "start-value" for Accvol and there is no Aveflow to be calculated
                    Volume = (table2.values[j] - table2.values[j-1])*1000#convert to L since Accvol is supposed to be in m3
                    """ Get help from function datestr2num to get date and time into float"""
                    DeltaTime = 24*3600*(datestr2num(table2.date_time[j]) - datestr2num(table2.date_time[j-1]))#convert to seconds since numtime is days
                    Aveflow = Volume/DeltaTime#L/s
                    if Aveflow<0:
                        negativeflow = True
                    sql = """insert or ignore into w_flow(obsid,instrumentid,flowtype,date_time,reading,unit) values('%s','%s','Aveflow','%s','%s','l/s')"""%(pyobsid,pyinstrumentid,table2.date_time[j],Aveflow)
                    db_utils.sql_alter_db(sql)
        if negativeflow:
            utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('Calcave', "Please notice that negative flow was encountered.")))
        utils.stop_waiting_cursor()
        self.close()

    def calculateaveflow_pandas(self):
        if not pandas_on:
            utils.MessagebarAndLog.warning(bar_msg=ru(
                QCoreApplication.translate('Calcave', "Python3 pandas not installed. No calculation done!")))
            return

        utils.start_waiting_cursor()
        date_from = self.FromDateTime.dateTime().toPyDateTime()
        date_to = self.ToDateTime.dateTime().toPyDateTime()

        sql = '''SELECT date_time, reading, obsid, instrumentid, comment FROM w_flow WHERE flowtype = 'Accvol' AND date_time >= '%s' AND date_time <= '%s' AND obsid IN (%s)
                 ORDER by obsid, instrumentid, date_time'''%(date_from,date_to, utils.sql_unicode_list(self.observations))
        dbconnection = db_utils.DbConnectionManager()
        df = pd.read_sql(sql, dbconnection.conn, index_col=['date_time'], coerce_float=True, params=None, parse_dates=['date_time'],
                             columns=None,
                             chunksize=None)
        dbconnection.closedb()

        df['dt'] = df.index.astype('int64')//1e9
        df = df.sort_values(by=['obsid', 'instrumentid', 'date_time']).reset_index()
        grouped = df.groupby(by=['obsid', 'instrumentid'])
        df['aveflow'] = (grouped['reading'].diff() / grouped['dt'].diff()) * 1000

        if (df['aveflow'] < 0).any():
            utils.MessagebarAndLog.info(
                bar_msg=ru(QCoreApplication.translate('Calcave', "Please notice that negative flow was encountered.")))

        columns = ['obsid', 'instrumentid', 'date_time', 'aveflow', 'comment']
        df['date_time'] = df['date_time'].astype(str)
        df = df.loc[df['aveflow'].notna(), columns] #'[[columns].copy()
        df.columns = ['obsid', 'instrumentid', 'date_time', 'reading', 'comment']
        df['flowtype'] = 'Aveflow'
        df['unit'] = 'l/s'

        file_data = df.values.tolist()
        file_data.reverse()
        file_data.append(list(df.columns))
        file_data.reverse()

        #print('\n'.join([', '.join([str(x) for x in row]) for row in file_data]))

        importer = import_data_to_db.midv_data_importer()
        importer.general_import(dest_table='w_flow', file_data=file_data)

        utils.stop_waiting_cursor()
        self.close()






