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
import db_utils
from PyQt4.QtCore import QUrl, Qt, QDir
from PyQt4.QtGui import QDesktopServices, QApplication, QCursor

from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import os
import locale
import codecs
import time #for debugging
#midvatten modules
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru

from PyQt4.QtCore import QCoreApplication

class Wqualreport():        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    def __init__(self,layer, settingsdict = {}):
        #show the user this may take a long time...
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.settingsdict = settingsdict
        provider = layer.dataProvider()  # OGR provider
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        observations = layer.selectedFeatures()

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

        for i, object in enumerate(observations):
            attributes = observations[i]
            obsid = attributes[kolumnindex]
            try:
                print('about to get data for ' + obsid + ', at time: ' + str(time.time()))#debug
            except:
                pass
            ReportData = self.GetData(self.settingsdict['database'], obsid, dbconnection)   # one observation at a time
            try:
                print('done with getting data for ' + obsid + ', at time: ' + str(time.time()))#debug
            except:
                pass
            if ReportData:
                self.WriteHTMLReport(ReportData, f)
            try:
                print('wrote html report for ' + obsid + ', at time: ' + str(time.time()))#debug
            except:
                pass

        dbconnection.closedb()
        #write some finishing html and close the file
        f.write("\n</body></html>")        
        f.close()

        QApplication.restoreOverrideCursor()#now this long process is done and the cursor is back as normal

        if ReportData:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))
        
    def GetData(self, dbPath='', obsid = '', dbconnection=None):            # GetData method that returns a table with water quality data
        # Load all water quality parameters stored in two result columns: parameter, unit
        if not(unicode(self.settingsdict['wqual_unitcolumn']) ==''):          #If there is a a given column for unit 
            sql =r"""select distinct """ + self.settingsdict['wqual_paramcolumn'] + """, """
            sql += self.settingsdict['wqual_unitcolumn']
            sql +=r""" from """
        else:                              # IF no specific column exist for unit
            sql =r"""select distinct """ + self.settingsdict['wqual_paramcolumn'] + """, """ + self.settingsdict['wqual_paramcolumn'] + """ from """  # The twice selection of parameter is a dummy to keep same structure (2 cols) of sql-answer as if a unit column exists
        sql += self.settingsdict['wqualtable']
        sql += r""" where obsid = '"""
        sql += obsid  
        sql += r"""' ORDER BY """ + self.settingsdict['wqual_paramcolumn']
        connection_ok, parameters = db_utils.sql_load_fr_db(sql, dbconnection)
        if not parameters:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'Wqualreport', u'Debug, something is wrong, no parameters are found in table w_qual_lab for %s'))%obsid)
            return False
        try:
            print('parameters for ' + obsid + ' is loaded at time: ' + str(time.time()))#debug
        except:
            pass
        # Load all date_times, stored in two result columns: reportnr, date_time
        if self.settingsdict['wqual_sortingcolumn']:          #If there is a a specific sorting column
            if len(self.settingsdict['wqual_date_time_format']) > 16:
                sql =r"""select distinct """
                sql += self.settingsdict['wqual_sortingcolumn']
                sql += r""", date_time from """      #including parameters
            else:
                sql = r"""select distinct %s, date_time from (select %s, substr(date_time,1,%s) as date_time from """%(self.settingsdict['wqual_sortingcolumn'], self.settingsdict['wqual_sortingcolumn'], len(self.settingsdict['wqual_date_time_format']))
        else:                     # IF no specific column exist for sorting
            if len(self.settingsdict['wqual_date_time_format'])>16:
                sql =r"""select distinct date_time, date_time from """ # The twice selection of date_time is a dummy to keep same structure (2 cols) of sql-answer as if reportnr exists
            else:
                sql =r"""select distinct dummy, date_time from (select substr(date_time,1,%s) as dummy, substr(date_time,1,%s) as date_time from """%(len(self.settingsdict['wqual_date_time_format']),len(self.settingsdict['wqual_date_time_format']))      # The twice selection of date_time is a dummy to keep same structure (2 cols) of sql-answer as if reportnr exists
        sql += self.settingsdict['wqualtable']
        sql += """ where obsid = '"""
        sql += obsid
        if len(self.settingsdict['wqual_date_time_format'])>16:
            sql += """' ORDER BY date_time"""
        else:
            sql += """') ORDER BY date_time"""
        #sql2 = unicode(sql) #To get back to unicode-string
        connection_ok, date_times = db_utils.sql_load_fr_db(sql, dbconnection) #Send SQL-syntax to cursor,

        try:
            print('loaded distinct date_time for the parameters for ' + obsid + ' at time: ' + str(time.time()))#debug
        except:
            pass
        if not date_times:
            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'Wqualreport', u"Debug, Something is wrong, no parameters are found in table w_qual_lab for %s"))%obsid)
            return

        if self.settingsdict['wqual_sortingcolumn']:
            self.nr_header_rows = 3
        else:
            self.nr_header_rows = 2

        ReportTable = [''] * (len(parameters) + self.nr_header_rows)    # Define size of ReportTable

        for i in range(len(parameters)+self.nr_header_rows): # Fill the table with ''
            ReportTable[i] = [''] * (len(date_times)+1)

        #Populate First 'column' w parameters

        for parametercounter, p_u in enumerate(parameters, start=self.nr_header_rows):
            p, u = p_u
            if not(self.settingsdict['wqual_unitcolumn']==''):
                if u:
                    #ReportTable[parametercounter][0] = p.encode(utils.getcurrentlocale()[1]) + ", " +  u.encode(utils.getcurrentlocale()[1])
                    ReportTable[parametercounter][0] = p + ", " +  u
                else: 
                    #ReportTable[parametercounter][0] = p.encode(utils.getcurrentlocale()[1])
                    ReportTable[parametercounter][0] = p
            else:
                #ReportTable[parametercounter][0] = p.encode(utils.getcurrentlocale()[1])
                ReportTable[parametercounter][0] = p

        try:
            print('now go for each parameter value for ' + obsid + ', at time: ' + str(time.time()))#debug
        except:
            pass
        ReportTable[0][0] = u'obsid'
        ReportTable[1][0] = u'date_time'
        for datecounter, r_d in enumerate(date_times, start=1): #date_times includes both report and date_time (or possibly date_time and date_time if there is no reportnr)
            r, d = r_d
            ReportTable[0][datecounter]=obsid
            ReportTable[1][datecounter] = d  # d is date_time
            if self.settingsdict['wqual_sortingcolumn']:
                ReportTable[2][0] = self.settingsdict['wqual_sortingcolumn']
                ReportTable[2][datecounter] = r


        for datecounter, sorting_date_time in enumerate(date_times, start=1):    # Loop through all report
            sorting, date_time = sorting_date_time

            # Parameter rows starts after date or sorting row
            for parametercounter, p_u in enumerate(parameters, start=self.nr_header_rows):
                p, u = p_u
                sql =r"""SELECT """
                sql += self.settingsdict['wqual_valuecolumn']
                sql += r""" from """
                sql += self.settingsdict['wqualtable']
                sql += """ where obsid = '"""
                sql += obsid
                if len(self.settingsdict['wqual_date_time_format'])>16:
                    sql += "' and date_time  = '"
                else:
                    sql += "' and substr(date_time,1,%s)  = '"%str(len(self.settingsdict['wqual_date_time_format']))
                sql += date_time
                if not(self.settingsdict['wqual_unitcolumn'] == '') and u:
                    sql += """' and parameter = '"""
                    sql += p
                    sql += """' and """
                    sql += self.settingsdict['wqual_unitcolumn']
                    sql += """ = '"""
                    sql += u
                    sql += """'"""
                else:
                    sql += """' and parameter = '"""
                    sql += p
                    sql += """'"""
                if self.settingsdict['wqual_sortingcolumn']:
                    sql += """ and "%s" = '%s'"""%(self.settingsdict['wqual_sortingcolumn'], sorting)

                connection_ok, recs = db_utils.sql_load_fr_db(sql, dbconnection)
                #each value must be in unicode or string to be written as html report
                if recs:
                    try:
                        ReportTable[parametercounter][datecounter] = ru(recs[0][0])
                    except:
                        ReportTable[parametercounter][datecounter]=''
                        utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'Wqualreport', u"Note!, the value for %s [%s] at %s, %s was not readable. Check your data!"))%(p,u,sorting,date_time))
                else: 
                    ReportTable[parametercounter][datecounter] =' '

        self.htmlcols = datecounter + 1    # to be able to set a relevant width to the table
        return ReportTable
        
    def WriteHTMLReport(self, ReportData, f):
        tabellbredd = 180 + 75*self.htmlcols
        rpt = "<table width=\""
        rpt += str(tabellbredd) # set table total width from no of water quality analyses
        rpt += "\" border=\"1\">\n"
        f.write(rpt)

        for counter, sublist in enumerate(ReportData):
            try:
                if counter < self.nr_header_rows:
                    rpt = "  <tr><th>"
                    rpt += "    </th><th width =\"75\">".join(sublist)
                    rpt += "  </th></tr>\n"
                else:
                    rpt = "  <tr><td>"
                    rpt += "    </td><td align=\"right\">".join(sublist)
                    rpt += "  </td></tr>\n"
            except:
                try:
                    print("here was an error: %s"%sublist)
                except:
                    pass
            f.write(rpt)
        f.write("\n</table><p></p><p></p>")

