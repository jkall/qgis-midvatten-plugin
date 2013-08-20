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
from PyQt4.QtCore import *  #Not necessary?
from PyQt4.QtGui import *  #Not necessary?
from qgis.core import *   # Necessary for the QgsFeature()
from qgis.gui import *
from pyspatialite import dbapi2 as sqlite #could have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
import os
import locale
import midvatten_utils as utils  

class wqualreport():        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    def __init__(self,layer, settingsdict = {}):
        self.settingsdict = settingsdict
        provider = layer.dataProvider()  # OGR provider
        kolumnindex = provider.fieldNameIndex('obsid') # To find the column named 'obsid'
        observations = layer.selectedFeatures()
        i = 0
        reportpath = os.path.join(os.sep,os.path.dirname(__file__),"reports","w_qual_report.html")
        f = open(reportpath, "wb" )
        #f = codecs.open(reportpath, "wb", "utf-8")     # Check later...

        #write some initiating html
        rpt = r""" <meta http-equiv="content-type" content="text/html; charset=latin-1" />"""  # NOTE, 'latin-1' is due to use on win machines    
        rpt += "<html><body>"
        #rpt += "<table width=\"100%\" border=\"1\">\n"
        rpt2 = rpt.encode("utf-8")
        f.write(rpt2)

        for object in observations:
            attributes = observations[i]
            obsid = str(attributes[kolumnindex])    # NOTE! obsid WAS a QString!! 
            ReportData = self.GetData(str(self.settingsdict['database']).encode(locale.getdefaultlocale()[1]), obsid)   # one observation at a time
            #ReportData.append(self.GetData(str(self.settingsdict['database']).encode('latin-1'), obsid))  # does not work as expected
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
        if not(str(self.settingsdict['wqual_unitcolumn']).encode(locale.getdefaultlocale()[1]) ==''):          #If there is a a given column for unit 
            sql =r"""select distinct parameter, """
            sql += str(self.settingsdict['wqual_unitcolumn']).encode(locale.getdefaultlocale()[1])
            sql +=r""" from """
        else:                              # IF no specific column exist for unit
            sql =r"""select distinct parameter, parameter from """  # The twice selection of parameter is a dummy to keep same structure (2 cols) of sql-answer as if a unit column exists
        sql += str(self.settingsdict['wqualtable']).encode(locale.getdefaultlocale()[1])
        sql += r""" where obsid = '"""
        sql += obsid   # obsid is a QString - no good...
        sql += r"""' ORDER BY parameter"""
        sql2 = str(sql).encode('utf-8')  #To get back to unicode-string
        parameters_cursor = curs.execute(sql2) #Send SQL-syntax to cursor
        parameters = parameters_cursor.fetchall()
        if not parameters:
            QMessageBox.information(None,"Info", "Something is wrong, no parameters are found in table w_qual_lab for "+ str(obsid).encode('utf-8')) #debugging
            return False

        # Load all date_times, stored in two result columns: reportnr, date_time
        if not (str(self.settingsdict['wqual_sortingcolumn']).encode(locale.getdefaultlocale()[1]) == ''):          #If there is a a specific reportnr 
            sql =r"""select distinct """
            sql += str(self.settingsdict['wqual_sortingcolumn']).encode(locale.getdefaultlocale()[1])
            sql += r""", date_time from """      #including parameters
        else:                     # IF no specific column exist for report
            sql =r"""select distinct date_time, date_time from """      # The twice selection of date_time is a dummy to keep same structure (2 cols) of sql-answer as if reportnr exists
        sql += str(self.settingsdict['wqualtable']).encode(locale.getdefaultlocale()[1])
        sql += """ where obsid = '"""
        sql += obsid      # obsid is a QString - no good...
        sql += """' ORDER BY date_time"""
        sql2 = str(sql).encode('utf-8')   #To get back to unicode-string
        date_times_cursor = curs.execute(sql2) #Send SQL-syntax to cursor,
        date_times = date_times_cursor.fetchall()

        if not date_times:
            QMessageBox.information(None,"Info", "Something is wrong, no analyses are found in table w_qual_lab for " + str(obsid).encode('utf-8')) #debugging
            return

        ReportTable = ['']*(len(parameters)+2)    # Define size of ReportTable
        for i in range(len(parameters)+2): # Fill the table with ''
            ReportTable[i] = [''] * (len(date_times)+1)
            #ReportTable[i] = [''] * (len(date_times)/2+1)   #Division w 2 due to both parameters and date_time
        
        #ReportTable[0][0]=str(obsid).encode('utf-8') # Upper left corner of report table is filled with obsid - not applicable if selected more than one observation
        
        #Populate First 'column' w parameters
        parametercounter = 2    #First two rows are for obsid and date_time    
        for p, u in parameters:
            if not(str(self.settingsdict['wqual_unitcolumn']).encode(locale.getdefaultlocale()[1])==''):
                #utils.pop_up_info(p + " " + u)  #DEBUG
                if u:
                    #ReportTable[parametercounter][0] = p.encode('latin-1') + ", " +  u.encode('latin-1')
                    ReportTable[parametercounter][0] = p.encode(locale.getdefaultlocale()[1]) + ", " +  u.encode(locale.getdefaultlocale()[1])
                    #ReportTable[parametercounter][0] = unicode(p,locale.getdefaultlocale()[1]) + ", " +  unicode(u,'latin-1')
                    #ReportTable[parametercounter][0] = unicode(str(p).encode('utf-8'),'utf-8') + ", " +  unicode(u,'latin-1')
                else: 
                    #ReportTable[parametercounter][0] = p.encode('latin-1')
                    ReportTable[parametercounter][0] = p.encode(locale.getdefaultlocale()[1])
                    #ReportTable[parametercounter][0] = unicode(p,'latin-1')
            else:
                #ReportTable[parametercounter][0] = p.encode('latin-1')
                ReportTable[parametercounter][0] = p.encode(locale.getdefaultlocale()[1])
                #ReportTable[parametercounter][0] = unicode(p,'latin-1')
            parametercounter = parametercounter + 1
        #QMessageBox.information(None,"Info", str(parametercounter)) # DEBUG

        #Populate First 'row' w obsid
        datecounter = 1    #First col is 'parametercolumn'
        #for d in date_times: 
        for r, d in date_times: #date_times includes both report and date_time (or possibly date_time and date_time if there is no reportnr)
            ReportTable[0][datecounter]=str(obsid).encode('utf-8') 
            datecounter += 1
        #QMessageBox.information(None,"Info", str(parametercounter)) # DEBUG
        
        datecounter=1    # first 'column' is for parameter names
        #for k in date_times:    # Loop through all dates    
        for k, v in date_times:    # Loop through all report    
            #if datecounter < 3: #debug
            #    utils.pop_up_info(str(k) + " and " + str(v))   #debug
            parametercounter = 1    # first row is for obsid    
            #ReportTable[parametercounter][datecounter] = k[0].encode('latin-1')
            ReportTable[parametercounter][datecounter] = str(v).encode(locale.getdefaultlocale()[1]) # v is date_time
            for p, u in parameters:
                parametercounter = parametercounter + 1 # one 'row' down after date was stored
                sql =r"""SELECT """
                sql += str(self.settingsdict['wqual_valuecolumn']).encode(locale.getdefaultlocale()[1])
                sql += r""" from """
                sql += str(self.settingsdict['wqualtable']).encode(locale.getdefaultlocale()[1])
                sql += """ where obsid = '"""
                sql += str(obsid).encode('utf-8')    # The string encoding  since obsid is QString 
                sql += """' and date_time = '"""
                #sql += k[0].encode('utf-8')        # NOTE!! This sql syntax is built up on a return from sqlite driver, thus we have to interpret it as utf-8 
                sql += str(v).encode('utf-8')        # v - date_time         This sql syntax is built up on a return from sqlite driver, thus we have to interpret it as utf-8 
                if not(str(self.settingsdict['wqual_unitcolumn']).encode(locale.getdefaultlocale()[1]) == '') and u:
                    sql += """' and parameter = '"""
                    sql += p.encode('utf-8') # NOTE!! This sql syntax is built up on a return from sqlite driver, thus we have to interpret it as utf-8 
                    #sql += p.encode(locale.getdefaultlocale()[1]) # If there are, by mistake, other encodings in sqlite db, then probably they are in local charset
                    #sql += unicode(p,'latin-1')
                    sql += """' and """
                    sql += str(self.settingsdict['wqual_unitcolumn']).encode(locale.getdefaultlocale()[1])
                    sql += """ = '"""
                    sql += u.encode('utf-8') # NOTE!! This sql syntax is built up on a return from sqlite driver, thus we have to interpret it as utf-8 
                    #sql += u.encode(locale.getdefaultlocale()[1]) # If there are, by mistake, other encodings in sqlite db, then probably they are in local charset
                    #sql += unicode(u,'latin-1')
                    sql += """'"""
                else:
                    sql += """' and parameter = '"""
                    sql += p.encode('utf-8') # NOTE!! This sql syntax is built up on a return from sqlite driver, thus we have to interpret it as utf-8 
                    #sql += p.encode(locale.getdefaultlocale()[1]) # If there are, by mistake, other encodings in sqlite db, then probably they are in local charset
                    #sql += unicode(p,'latin-1')
                    sql += """'"""
                rs = curs.execute(sql) #Send SQL-syntax to cursor, NOTE: here we send sql which was utf-8 already from interpreting it
                recs = rs.fetchall()  # All data are stored in recs
                #if parametercounter < 3:    # debug 
                #    utils.pop_up_info("debug: " + sql)       #debug
                if recs:
                    try:
                        #the_value = unicode(recs[0][0],locale.getdefaultlocale()[1]) # unicode enabled by conn.text_factory = str above
                        #the_value = str(recs[0][0]).encode(locale.getdefaultlocale()[1])   #.encode('latin-1') .encode('utf-8') .encode('cp1252')
                        the_value = str(recs[0][0]).encode('utf-8') # it should be utf-8 since that is default for sqlite db
                    except UnicodeError:
                        #utils.pop_up_info("Encoding error for " + recs[0][0], "Error") #debug
                        try:
                            the_value = recs[0][0].encode(locale.getdefaultlocale()[1]) #if data was inserted into database, overriding normal procedures, then local charset may exist in db 
                        except UnicodeError:
                            the_value = recs[0][0]  # last desperate attempt to read from db
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
        rpt += str(tabellbredd).encode("utf-8") # set table total width from no of water quality analyses
        rpt += "\" border=\"1\">\n"
        rpt2 = str(rpt).encode("utf-8")
        f.write(rpt2)
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
            #if counter < 2:        #Only for debugging
            #    QMessageBox.information(None, "info",rpt)    # only for debugging
            #rpt2 = rpt.encode("utf-8")
            f.write(rpt)
            counter = counter + 1
        f.write("\n</table><p></p><p></p>")
