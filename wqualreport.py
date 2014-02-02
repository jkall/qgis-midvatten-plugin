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
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QDesktopServices

from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import os
import locale
import midvatten_utils as utils  
import codecs

class wqualreport():        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    def __init__(self,layer, settingsdict = {}):
        self.settingsdict = settingsdict
        provider = layer.dataProvider()  # OGR provider
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        observations = layer.selectedFeatures()
        i = 0
        reportpath = os.path.join(os.sep,os.path.dirname(__file__),"reports","w_qual_report.html")
        #f = open(reportpath, "wb" )
        f = codecs.open(reportpath, "wb", "utf-8")

        #write some initiating html
        rpt = r"""<head><title>water quality report from Midvatten plugin for QGIS</title></head>"""
        rpt += r""" <meta http-equiv="content-type" content="text/html; charset=utf-8" />""" #NOTE, all report data must be in 'utf-8'
        rpt += "<html><body>"
        #rpt += "<table width=\"100%\" border=\"1\">\n"
        #rpt2 = rpt.encode("utf-8")
        f.write(rpt)

        for object in observations:
            attributes = observations[i]
            obsid = attributes[kolumnindex]
            ReportData = self.GetData(self.settingsdict['database'], obsid)   # one observation at a time
            if ReportData:
                self.WriteHTMLReport(ReportData, f)
            i = i+1

        #write some finishing html and close the file
        f.write("\n</body></html>")        
        f.close()

        if ReportData:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def GetData(self, dbPath='', obsid = ''):            # GetData method that returns a table with water quality data
        conn = sqlite.connect(dbPath,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        # skapa en cursor
        curs = conn.cursor()

        # Load all water quality parameters stored in two result columns: parameter, unit
        if not(unicode(self.settingsdict['wqual_unitcolumn']) ==''):          #If there is a a given column for unit 
            sql =r"""select distinct parameter, """
            sql += self.settingsdict['wqual_unitcolumn']
            sql +=r""" from """
        else:                              # IF no specific column exist for unit
            sql =r"""select distinct parameter, parameter from """  # The twice selection of parameter is a dummy to keep same structure (2 cols) of sql-answer as if a unit column exists
        sql += self.settingsdict['wqualtable']
        sql += r""" where obsid = '"""
        sql += obsid  
        sql += r"""' ORDER BY parameter"""
        parameters_cursor = curs.execute(sql) #Send SQL-syntax to cursor
        parameters = parameters_cursor.fetchall()
        if not parameters:
            qgis.utils.iface.messageBar().pushMessage("Debug","Something is wrong, no parameters are found in table w_qual_lab for "+ obsid, 0 ,duration=10)#DEBUG
            return False

        # Load all date_times, stored in two result columns: reportnr, date_time
        if not (self.settingsdict['wqual_sortingcolumn'] == ''):          #If there is a a specific reportnr 
            sql =r"""select distinct """
            sql += self.settingsdict['wqual_sortingcolumn']
            sql += r""", date_time from """      #including parameters
        else:                     # IF no specific column exist for report
            sql =r"""select distinct date_time, date_time from """      # The twice selection of date_time is a dummy to keep same structure (2 cols) of sql-answer as if reportnr exists
        sql += self.settingsdict['wqualtable']
        sql += """ where obsid = '"""
        sql += obsid 
        sql += """' ORDER BY date_time"""
        #sql2 = unicode(sql) #To get back to unicode-string
        date_times_cursor = curs.execute(sql) #Send SQL-syntax to cursor,
        date_times = date_times_cursor.fetchall()

        if not date_times:
            qgis.utils.iface.messageBar().pushMessage("Debug","Something is wrong, no parameters are found in table w_qual_lab for "+ obsid, 0 ,duration=10)#DEBUG
            return

        ReportTable = ['']*(len(parameters)+2)    # Define size of ReportTable
        for i in range(len(parameters)+2): # Fill the table with ''
            ReportTable[i] = [''] * (len(date_times)+1)

        #Populate First 'column' w parameters
        parametercounter = 2    #First two rows are for obsid and date_time    
        for p, u in parameters:
            if not(self.settingsdict['wqual_unitcolumn']==''):
                if u:
                    #ReportTable[parametercounter][0] = p.encode(locale.getdefaultlocale()[1]) + ", " +  u.encode(locale.getdefaultlocale()[1])
                    ReportTable[parametercounter][0] = p + ", " +  u
                else: 
                    #ReportTable[parametercounter][0] = p.encode(locale.getdefaultlocale()[1])
                    ReportTable[parametercounter][0] = p
            else:
                #ReportTable[parametercounter][0] = p.encode(locale.getdefaultlocale()[1])
                ReportTable[parametercounter][0] = p
            parametercounter = parametercounter + 1

        #Populate First 'row' w obsid
        datecounter = 1    #First col is 'parametercolumn'
        for r, d in date_times: #date_times includes both report and date_time (or possibly date_time and date_time if there is no reportnr)
            ReportTable[0][datecounter]=obsid 
            datecounter += 1
        
        datecounter=1    # first 'column' is for parameter names
        for k, v in date_times:    # Loop through all report    
            #if datecounter < 3: #debug
            parametercounter = 1    # first row is for obsid    
            ReportTable[parametercounter][datecounter] = v # v is date_time
            for p, u in parameters:
                parametercounter = parametercounter + 1 # one 'row' down after date was stored
                sql =r"""SELECT """
                sql += self.settingsdict['wqual_valuecolumn']
                sql += r""" from """
                sql += self.settingsdict['wqualtable']
                sql += """ where obsid = '"""
                sql += obsid
                sql += """' and date_time = '"""
                sql += v 
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
                rs = curs.execute(sql) #Send SQL-syntax to cursor, NOTE: here we send sql which was utf-8 already from interpreting it
                recs = rs.fetchall()  # All data are stored in recs
                if recs:
                    try:
                        the_value = recs[0][0] #unicode should be return from pysqlite
                    except UnicodeError:
                        try:
                            the_value = unicode(recs[0][0])# if not, try converting to unicode
                            qgis.utils.iface.messageBar().pushMessage("Note!","""Your db may contain characters with non-utf encoding, check the value %s which had to be converted to unicode!"""%the_value,0,duration=3)#debug
                        except UnicodeError:
                            the_value = recs[0][0].encode('utf-8') #if still encoding problems, try convert to byte string 
                            qgis.utils.iface.messageBar().pushMessage("Note!","""Your db may contain characters with non-utf encoding, check the value %s which had to be converted to utf-8 byte string!"""%the_value,0,duration=3)#debug
                        else: 
                            the_value = 'Value could not be loaded, check database!'    # if it fails, load this string to let user know
                    ReportTable[parametercounter][datecounter] =the_value
                else: 
                    ReportTable[parametercounter][datecounter] =' '
            datecounter = datecounter + 1
        self.htmlcols = datecounter + 1    # to be able to set a relevant width to the table
        parameters_cursor.close()
        date_times_cursor.close()
        rs.close()
        conn.close()
        return ReportTable
        
    def WriteHTMLReport(self, ReportData, f):            
        tabellbredd = 180 + 75*self.htmlcols
        rpt = "<table width=\""
        rpt += str(tabellbredd) # set table total width from no of water quality analyses
        rpt += "\" border=\"1\">\n"
        f.write(rpt)
        counter = 0
        for sublist in ReportData:
            if counter <2:
                rpt = "  <tr><th>"
                rpt += "    </th><th width =\"75\">".join(sublist)
                rpt += "  </th></tr>\n"
            else:
                rpt = "  <tr><td>"
                rpt += "    </td><td align=\"right\">".join(sublist)
                rpt += "  </td></tr>\n"
            f.write(rpt)
            counter = counter + 1
        f.write("\n</table><p></p><p></p>")
