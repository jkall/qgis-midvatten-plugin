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

import PyQt4

import qgis.utils

import datetime
import os

import db_utils
from matplotlib.dates import datestr2num
import numpy as np
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
#from ui.calc_aveflow_dialog import Ui_Dialog as Calc_Ui_Dialog
from PyQt4 import uic

from PyQt4.QtCore import QCoreApplication

Calc_Ui_Dialog =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'calc_aveflow_dialog.ui'))[0]


class Calcave(PyQt4.QtGui.QDialog, Calc_Ui_Dialog): # An instance of the class Calc_Ui_Dialog is created same time as instance of calclvl is created

    def __init__(self, parent):
        PyQt4.QtGui.QDialog.__init__(self)
        self.setupUi(self) # Required by Qt4 to initialize the UI
        #self.obsid = utils.getselectedobjectnames()
        self.setWindowTitle(ru(QCoreApplication.translate(u'Calcave', u"Calculate average flow"))) # Set the title for the dialog
        self.connect(self.pushButton_All, PyQt4.QtCore.SIGNAL("clicked()"), self.calcall)
        self.connect(self.pushButton_Selected, PyQt4.QtCore.SIGNAL("clicked()"), self.calcselected)
        self.connect(self.pushButton_Cancel, PyQt4.QtCore.SIGNAL("clicked()"), self.close)

    def calcall(self):
        obsar = db_utils.sql_load_fr_db('select distinct obsid from w_flow where flowtype="Accvol"')[1]
        self.observations = [str(obs[0]) for obs in obsar] #we cannot send unicode as string to sql because it would include the u'
        self.calculateaveflow()

    def calcselected(self):
        obsar = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())
        self.observations = [obs.encode('utf-8') for obs in obsar] #turn into a list of python byte strings
        self.calculateaveflow()

    def calculateaveflow(self):
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        date_from = self.FromDateTime.dateTime().toPyDateTime()
        date_to = self.ToDateTime.dateTime().toPyDateTime()
        #Identify distinct set of obsid and instrumentid with Accvol-data and within the user-defined date_time-interval:
        sql= """select distinct obsid, instrumentid from(select * from w_flow where flowtype = "Accvol" and date_time >="%s" and date_time <="%s" and obsid IN %s)"""%(date_from,date_to,(str(self.observations)).encode('utf-8').replace('[','(').replace(']',')'))
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
            utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'Calcave', u"Please notice that negative flow was encountered.")))
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.close()
