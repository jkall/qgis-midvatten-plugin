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
import sqlite3 as sqlite, csv, codecs, cStringIO, os, os.path
import midvatten_utils as utils
import qgis.utils

class ExportData():

    def __init__(self, OBSID_P, OBSID_L):
        self.ID_obs_points = OBSID_P
        self.ID_obs_lines = OBSID_L

    def export_2_csv(self,exportfolder):
        database = utils.dbconnection()
        database.connect2db() #establish connection to the current midv db
        self.curs = database.conn.cursor()#get a cursor

        self.exportfolder = exportfolder
        self.write_data(self.to_csv, self.ID_obs_points, ['obs_points', 'comments', 'w_levels', 'w_levels_logger', 'w_flow', 'w_qual_lab', 'w_qual_field', 'stratigraphy', 'meteo'], utils.verify_table_exists)
        self.write_data(self.to_csv, self.ID_obs_lines, ['obs_lines', 'vlf_data', 'seismic_data'], utils.verify_table_exists)
        self.write_data(self.zz_to_csv, u'no_obsids', ['zz_flowtype', 'zz_meteoparam', 'zz_staff', 'zz_strat', 'zz_capacity', 'zz_w_qual_field_parameters'], utils.verify_table_exists)
        database.closedb()

    def export_2_splite(self,target_db,source_db, EPSG_code):
        conn = sqlite.connect(target_db,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.curs = conn.cursor()
        self.curs.execute("PRAGMA foreign_keys = ON")
        self.curs.execute(r"""delete from spatial_ref_sys where NOT (srid='%s')"""%EPSG_code)
        self.curs.execute(r"""ATTACH DATABASE '%s' AS a"""%source_db)
        conn.commit()#commit sql statements so far

        self.write_data(self.to_sql, self.ID_obs_points, ['obs_points', 'comments', 'w_levels', 'w_levels_logger', 'w_flow', 'w_qual_lab', 'w_qual_field', 'stratigraphy', 'meteo'], self.verify_table_in_attached_db, 'a.')
        conn.commit()
        self.write_data(self.to_sql, self.ID_obs_lines, ['obs_lines', 'vlf_data', 'seismic_data'], self.verify_table_in_attached_db, 'a.')
        conn.commit()
        self.write_data(self.zz_to_sql, u'no_obsids', ['zz_flowtype', 'zz_meteoparam', 'zz_staff', 'zz_strat', 'zz_capacity', 'zz_w_qual_field_parameters'], self.verify_table_in_attached_db, 'a.')

        self.curs.execute(r"""DETACH DATABASE a""")
        self.curs.execute('vacuum')
        conn.commit()
        conn.close()

    def get_create_statement(self, tname):

        sql_list = []
        sql_list.append("""SELECT sql FROM (""")
        sql_list.append("""SELECT sql sql, type type, tbl_name tbl_name, name name """)
        sql_list.append("""FROM sqlite_master""")
        sql_list.append("""UNION ALL """)
        sql_list.append("""SELECT sql, type, tbl_name, name """)
        sql_list.append("""FROM sqlite_temp_master) """)
        sql_list.append("""WHERE type != 'meta' """)
        sql_list.append("""AND sql NOTNULL """)
        sql_list.append("""AND name NOT LIKE 'sqlite_%' """)
        sql_list.append("""AND tbl_name = '%s' """%(tname))
        sql_list.append("""ORDER BY substr(type, 2, 1), name""")
        sql = ''.join(sql_list)
        result = self.curs.execute(sql).fetchall()
        return result

    def format_obsids(self, obsids):
        formatted_obsids = u''.join([u'(', u', '.join([u"'{}'".format(k) for k in utils.returnunicode(obsids, True)]), u')']).encode('utf-8')
        return formatted_obsids

    def get_number_of_obsids(self, obsids, tname):
        no_of_obs_cursor = self.curs.execute(r"select count(obsid) from %s where obsid in %s" %(tname, self.format_obsids(obsids)))
        no_of_obs = no_of_obs_cursor.fetchall()
        return no_of_obs

    def write_data(self, to_writer, obsids, ptabs, verify_table_exists, tname_prefix=''):
        if len(obsids) > 0 or obsids == u'no_obsids':#only if there are any obs_points selected at all
            for tname in ptabs:
                tname_with_prefix = tname_prefix + tname
                if not verify_table_exists(tname):
                    continue

                if obsids != u'no_obsids':
                    no_of_obs = self.get_number_of_obsids(obsids, tname_with_prefix)

                    if no_of_obs[0][0] > 0:#only go on if there are any observations for this obsid
                        to_writer(tname, tname_with_prefix, obsids)
                else:
                    to_writer(tname, tname_with_prefix)

    def to_csv(self, tname, tname_with_prefix, obsids):
        output = UnicodeWriter(file(os.path.join(self.exportfolder, tname + ".csv"), 'w'))
        self.curs.execute(r"select * from %s where obsid in %s"%(tname, self.format_obsids(obsids)))
        output.writerow([col[0] for col in self.curs.description])
        filter(None, (output.writerow(row) for row in self.curs))

    def to_sql(self, tname, tname_with_prefix, obsids):
        foreign_keys = self.get_foreign_keys(tname)

        for reference_table, from_to_fields in foreign_keys.iteritems():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]

            sql = r"""insert or ignore into %s (%s) select distinct %s from  %s"""%(reference_table, ', '.join(to_list), ', '.join(from_list), tname_with_prefix)
            self.curs.execute(sql)

        sql = r"insert into %s select * from %s where obsid in %s" %(tname, tname_with_prefix, self.format_obsids(obsids))
        try:
            self.curs.execute(sql)
        except Exception, e:
            qgis.utils.iface.messageBar().pushMessage("Export warning, sql failed: " + sql + "\nmsg: " + str(e))

    def zz_to_csv(self, tname, tname_with_prefix):
        output = UnicodeWriter(file(os.path.join(self.exportfolder, tname + ".csv"), 'w'))
        self.curs.execute(r"select * from %s"%(tname))
        output.writerow([col[0] for col in self.curs.description])
        filter(None, (output.writerow(row) for row in self.curs))

    def zz_to_sql(self, tname, tname_with_prefix):

        #Null-values as primary keys don't equal each other and can therefore cause duplicates.
        #This part concatenates the primary keys to make a string comparison for equality instead.
        primary_keys = self.get_primary_keys(tname)
        ifnull_primary_keys = [''.join(["ifnull(", pk, ",'')"]) for pk in primary_keys]
        concatenated_primary_keys = ' || '.join(ifnull_primary_keys)

        sql = r"insert or ignore into %s select * from %s where %s not in (select %s from %s)"%(tname, tname_with_prefix, concatenated_primary_keys, concatenated_primary_keys, tname)
        try:
            self.curs.execute(sql)
        except Exception, e:
            qgis.utils.iface.messageBar().pushMessage("Export warning, sql failed: " + sql + "\nmsg: " + str(e))

    def get_foreign_keys(self, tname):
        result_list = self.curs.execute("""PRAGMA foreign_key_list(%s)"""%(tname)).fetchall()
        foreign_keys = {}
        for row in result_list:
            foreign_keys.setdefault(row[2], []).append((row[3], row[4]))
        return foreign_keys

    def get_primary_keys(self, tname):
        result_list = self.curs.execute("""PRAGMA table_info(%s)"""%(tname)).fetchall()
        primary_keys = [column_tuple[1] for column_tuple in result_list if column_tuple[5] != 0]
        return primary_keys

    def verify_table_in_attached_db(self, tname):
        result = self.curs.execute(u"""SELECT name FROM a.sqlite_master WHERE type='table' AND name='%s'"""%(tname)).fetchall()
        if result:
            return True
        else:
            return False


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
