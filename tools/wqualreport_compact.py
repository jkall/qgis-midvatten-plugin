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
import codecs
import os
import time  # for debugging

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtCore import QUrl, Qt, QDir
from PyQt4.QtGui import QDesktopServices, QApplication, QCursor

import db_utils
# midvatten modules
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from midvatten_utils import general_exception_handler


class Wqualreport():        # extracts water quality data for selected objects, selected db and given table, results shown in html report
    @general_exception_handler
    def __init__(self, settingsdict = {}):
        #show the user this may take a long time...
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        self.settingsdict = settingsdict

        self.nr_header_rows = 3

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

        skip_reports_with_parameters = [u'Bly', u'Benso(ghi)perylen']
        obsids = utils.getselectedobjectnames()
        report_data = self.get_data(skip_reports_with_parameters, obsids, dbconnection)

        col_step = 10

        for startcol in xrange(1, len(report_data[0]), col_step):
            printlist = [[row[0]] for row in report_data]
            print(printlist)
            for rownr, row in enumerate(report_data):
                printlist[rownr].extend(row[startcol:min(startcol+col_step, len(row))])

            filtered = [row for row in printlist if any(row[1:])]

            self.htmlcols = len(filtered[0])
            self.WriteHTMLReport(filtered, f)








        dbconnection.closedb()
        # write some finishing html and close the file
        f.write("\n</body></html>")
        f.close()

        QApplication.restoreOverrideCursor()  # now this long process is done and the cursor is back as normal

        if report_data:
            QDesktopServices.openUrl(QUrl.fromLocalFile(reportpath))

    def get_data(self, skip_reports_with_parameters, obsids, dbconnection):
        if skip_reports_with_parameters is not None:
            skip_reports = r""" AND report NOT IN (SELECT DISTINCT report FROM {table}
                                WHERE {parameter} IN ({skip_parameters}))
                            """.format(**{'table': self.settingsdict['wqualtable'],
                                          'parameter': self.settingsdict['wqual_paramcolumn'],
                                          'skip_parameters': sql_list(skip_reports_with_parameters)})
        else:
            skip_reports = ''

        sql = '''SELECT obsid, date_time, report, {parameter} || ', ' ||
                 CASE WHEN {unit} IS NULL THEN '' ELSE {unit} END,
                 reading_txt 
                 FROM {table} WHERE obsid in ({obsids}) {skip_reports}
              '''.format(**{'parameter': self.settingsdict['wqual_paramcolumn'],
                            'unit': self.settingsdict['wqual_unitcolumn'],
                            'table': self.settingsdict['wqualtable'],
                            'obsids': sql_list(obsids),
                            'skip_reports': skip_reports})

        rows = db_utils.sql_load_fr_db(sql, dbconnection=dbconnection)[1]

        data = {}
        for row in rows:
            data.setdefault(row[0], {}).setdefault(row[1], {}).setdefault(row[2], {})[row[3]] = row[4]

        distinct_parameters = sorted(set([p for obsid, date_times in data.iteritems()
                                    for date_time, reports in date_times.iteritems()
                                        for reports, parameters in reports.iteritems()
                                            for p in parameters.keys()]))

        outlist = [['obsid'], ['date_time'], ['report']]
        outlist.extend([[p] for p in distinct_parameters])

        for obsid, date_times in sorted(data.iteritems()):
            for date_time, reports in sorted(date_times.iteritems()):
                for report, parameters in sorted(reports.iteritems()):
                    outlist[0].append(obsid)
                    outlist[1].append(date_time)
                    outlist[2].append(report)

                    for parameterlist in outlist[3:]:
                        reading_txt = parameters.get(parameterlist[0], '')
                        parameterlist.append(reading_txt)

        return outlist

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
        f.write("""<p>empty_row_between_tables</p>""")


def sql_list(alist):
    return u', '.join(["'{}'".format(x) for x in alist])