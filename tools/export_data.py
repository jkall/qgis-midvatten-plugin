# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the part of the Midvatten plugin that enables quick export of data from the database
                              -------------------
        begin                : 2015-08-30
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

import sqlite3, csv, codecs, cStringIO, os, os.path
import midvatten_utils as utils

class ExportData():

    def __init__(self, OBSID_P, OBSID_L):
        self.ID_obs_points = OBSID_P
        self.ID_obs_lines = OBSID_L

    def export_2_csv(self,exportfolder):
        database = utils.dbconnection()
        database.connect2db() #establish connection to the current midv db
        curs = database.conn.cursor()#get a cursor
        #--------First export selected obs_points and corresponding data---------------------------
        if len(self.ID_obs_points)>0:#only if there are any obs_points selected at all
            ptabs = ['obs_points', 'w_levels', 'w_levels_logger', 'w_flow', 'w_qual_lab', 'w_qual_field', 'stratigraphy', 'meteo']
            for tname in ptabs:
                # problems with string replacement and tuples (no success with parameter substitution)
                # and therefore different sql_clause depending on number of obs
                if len(self.ID_obs_points)==1:
                    sql_clause = r"""select count(obsid) from %s where obsid in ('%s')""" %(tname, self.ID_obs_points[0])
                elif len(self.ID_obs_points)>1:
                    sql_clause = r"select count(obsid) from %s where obsid in %s" %(tname, self.ID_obs_points)
                no_of_obs_cursor = curs.execute(sql_clause)
                no_of_obs = no_of_obs_cursor.fetchall()

                if no_of_obs[0][0] > 0:#only go on if there are any observations for this obsid
                    some_data = 0
                    if len(self.ID_obs_points)==1:#problems to combine parameter substitution and string replacement in same sql clause, should be fixed
                        sql_clause = r"""select * from %s where obsid in ('%s')""" %(tname, self.ID_obs_points[0])
                        some_data = 1
                    elif len(self.ID_obs_points)>1:
                        sql_clause = r"select * from %s where obsid in %s" %(tname, self.ID_obs_points)
                        some_data = 1
                    if some_data !=0:
                        output = UnicodeWriter(file(os.path.join(exportfolder,tname + ".csv"), 'w'))
                        curs.execute(sql_clause)
                        output.writerow([col[0] for col in curs.description])
                        filter(None, (output.writerow(row) for row in curs))

        #--------Then export selected obs_lines with corresponding data---------------------------
        if len(self.ID_obs_lines)>0:#only if there are any obs_points selected at all
            ptabs = ['obs_lines', 'vlf_data', 'seismic_data']
            for tname in ptabs:
                # problems with string replacement and tuples (no success with parameter substitution)
                # and therefore different sql_clause depending on number of obs
                if len(self.ID_obs_lines)==1:
                    sql_clause = r"""select count(obsid) from %s where obsid in ('%s')""" %(tname, self.ID_obs_lines[0])
                elif len(self.ID_obs_lines)>1:
                    sql_clause = r"select count(obsid) from %s where obsid in %s" %(tname, self.ID_obs_lines)
                no_of_obs_cursor = curs.execute(sql_clause)
                no_of_obs = no_of_obs_cursor.fetchall()

                if no_of_obs[0][0] > 0:#only go on if there are any observations for this obsid
                    some_data = 0
                    if len(self.ID_obs_lines)==1:#problems to combine parameter substitution and string replacement in same sql clause, should be fixed
                        sql_clause = r"""select * from %s where obsid in ('%s')""" %(tname, self.ID_obs_lines[0])
                        some_data = 1
                    elif len(self.ID_obs_lines)>1:
                        sql_clause = r"select * from %s where obsid in %s" %(tname, self.ID_obs_lines)
                        some_data = 1
                    if some_data !=0:
                        output = UnicodeWriter(file(os.path.join(exportfolder,tname + ".csv"), 'w'))
                        curs.execute(sql_clause)
                        output.writerow([col[0] for col in curs.description])
                        filter(None, (output.writerow(row) for row in curs))
        
        database.closedb()

    def export_2_splite(self,exportdb):
        pass

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    Source: http://docs.python.org/library/csv.html#csv-examples
    Modified to cope with non-string columns.
    """

    def __init__(self, f, dialect=csv.excel, delimiter=';', encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, delimiter=delimiter,**kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def encodeone(self, item):
        if type(item) == unicode:
            return self.encoder.encode(item)
        else:
            return item

    def writerow(self, row):
        self.writer.writerow([self.encodeone(s) for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
