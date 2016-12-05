# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of data to the database. 
 
 This part is to a big extent based on QSpatialite plugin.
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
import io
import os
import locale
import qgis.utils
import copy
from collections import OrderedDict
from datetime import datetime
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
from qgis.core import *

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4

import midvatten_utils as utils
from definitions import midvatten_defs as defs

from date_utils import find_date_format, datestring_to_date, dateshift

class midv_data_importer():  # this class is intended to be a multipurpose import class  BUT loggerdata probably needs specific importer or its own subfunction

    def __init__(self):
        self.columns = 0
        self.status= 'False'
        self.recsbefore = 0
        self.recsafter = 0
        self.recstoimport = 0
        self.recsinfile = 0
        self.temptablename = ''
        self.charsetchoosen = ('','')
        self.csvlayer = None

    def default_import(self, importer):
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        importer()
        self.SanityCheckVacuumDB()

    def general_csv_import(self, goal_table=None, column_header_translation_dict=None):

        if goal_table is None:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error: No goal table given!')
            self.status = 'False'
            return

        if not self.csvlayer:
            self.csvlayer = self.selectcsv()  # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        self.general_sqlite_table_import(column_header_translation_dict=column_header_translation_dict, goal_table=goal_table)
        
    def obslines_import(self):
        self.prepare_import('temporary_obs_lines')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            ConnectionOK, self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]) #first two cols are expected to be WKT geometry and obsid
            cleaningok = self.SingleFieldDuplicates(6,'obs_lines',sqlremove,1) # This is where duplicates are removed  LAST ARGUMENT IS COLUMN FOR ID
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_lines'"""
                SRID = str((utils.sql_load_fr_db(sql)[1])[0][0])# THIS IS DUE TO WKT-import of geometries below
                sqlpart1 = """INSERT OR IGNORE INTO "obs_lines" (obsid, name, place, type, source, geometry) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), ST_GeomFromText("%s",%s) from %s"""%(self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[0][1],SRID,self.temptableName)#PLEASE NOTE THE SRID!
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM obs_lines""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def obsp_import(self): 
        self.prepare_import('temporary_obs_points')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = (utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName)[1])#Load column names from sqlite table

            obsid = self.columns[0][1]
            name = self.columns[1][1]
            place = self.columns[2][1]
            atype = self.columns[3][1]
            length = self.columns[4][1]
            drillstop = self.columns[5][1]
            diam = self.columns[6][1]
            material = self.columns[7][1]
            screen = self.columns[8][1]
            capacity = self.columns[9][1]
            drilldate = self.columns[10][1]
            wmeas_yn = self.columns[11][1]
            wlogg_yn = self.columns[12][1]
            east = self.columns[13][1]
            north = self.columns[14][1]
            ne_accur = self.columns[15][1]
            ne_source = self.columns[16][1]
            h_toc = self.columns[17][1]
            h_tocags = self.columns[18][1]
            h_gs = self.columns[19][1]
            h_accur = self.columns[20][1]
            h_syst = self.columns[21][1]
            h_source = self.columns[22][1]
            source = self.columns[23][1]
            com_onerow = self.columns[24][1]
            com_html = self.columns[25][1]

            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null"""%(self.temptableName, obsid, obsid) #CHANGE HERE!!!
            cleaningok = self.SingleFieldDuplicates(26,'obs_points',sqlremove,0) # This is where duplicates are removed  LAST ARGUMENT IS COLUMN FOR ID 
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sql_list = []
                sql_list.append(r"""INSERT OR IGNORE INTO "obs_points" (obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html) """)
                sql_list.append(r"""SELECT CAST("%s" as text)"""%obsid)
                sql_list.append(r""", CAST("%s" as text)"""%name)
                sql_list.append(r""", CAST("%s" as text)"""%place)
                sql_list.append(r""", CAST("%s" as text)"""%atype)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(length, length))
                sql_list.append(r""", CAST("%s" as text)"""%drillstop)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(diam, diam))
                sql_list.append(r""", CAST("%s" as text)"""%material)
                sql_list.append(r""", CAST("%s" as text)"""%screen)
                sql_list.append(r""", CAST("%s" as text)"""%capacity)
                sql_list.append(r""", CAST("%s" as text)"""%drilldate)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as integer) else null end)"""%(wmeas_yn, wmeas_yn))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as integer) else null end)"""%(wlogg_yn, wlogg_yn))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(east, east))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(north, north))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(ne_accur, ne_accur))
                sql_list.append(r""", CAST("%s" as text)"""%ne_source)
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_toc, h_toc))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_tocags, h_tocags))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_gs, h_gs))
                sql_list.append(r""", (case when "%s"!='' then CAST("%s" as double) else null end)"""%(h_accur, h_accur))
                sql_list.append(r""", CAST("%s" as text)"""%h_syst)
                sql_list.append(r""", CAST("%s" as text)"""%h_source)
                sql_list.append(r""", CAST("%s" as text)"""%source)
                sql_list.append(r""", CAST("%s" as text)"""%com_onerow)
                sql_list.append(r""", CAST("%s" as text)"""%com_html)
                sql_list.append(r"""FROM %s"""%self.temptableName)
                sql = ''.join(sql_list)
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM obs_points""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def import_interlab4(self, filenames=None):
        all_lab_results = self.parse_interlab4(filenames)
        if all_lab_results == u'cancel':
            self.status = False
            return u'cancel'

        wquallab_data_table = self.interlab4_to_table(all_lab_results, utils.get_all_obsids())
        if wquallab_data_table in [u'cancel', u'error']:
            self.status = False
            return wquallab_data_table

        self.send_file_data_to_importer(wquallab_data_table, lambda : self.general_csv_import(goal_table=u'w_qual_lab'), self.check_obsids)
        self.SanityCheckVacuumDB()

    def parse_interlab4(self, filenames=None):
        """ Reads the interlab
        :param filenames:
        :return: A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        """
        if filenames is None:
            filenames = utils.select_files(only_one_file=False, extension="lab (*.lab)")
        if not filenames:
            return u'cancel'

        all_lab_results = {}

        for filename in filenames:
            file_error, version, encoding, decimalsign, quotechar = (True, None, None, None, None)
            file_error, version, encoding, decimalsign, quotechar = self.interlab4_parse_filesettings(filename)
            if file_error:
                utils.pop_up_info("Warning: The file information" + filename + " could not be read. Skipping file")
                continue

            with open(filename, 'rb') as f:
                if quotechar:
                    unicode_reader = utils.UnicodeReader(f, encoding=encoding, quotechar=str(quotechar), delimiter=';')
                else:
                    unicode_reader = utils.UnicodeReader(f, encoding=encoding, delimiter=';')

                lab_results = {}
                file_error = False
                read_metadata_header = False
                parse_metadata_values = False
                read_data_header = False
                parse_data_values = False

                metadata_header = None
                data_header = None

                for cols in unicode_reader:
                    if not cols:
                        continue

                    if cols[0].lower().startswith(u'#slut'):
                        break

                    if cols[0].lower().startswith(u'#provadm'):
                        parse_data_values = False
                        parse_metadata_values = False
                        read_data_header = False
                        read_metadata_header = True
                        data_header = None
                        metadata_header = None
                        continue

                    if cols[0].lower().startswith(u'#provdat'):
                        parse_data_values = False
                        parse_metadata_values = False
                        read_metadata_header = False
                        read_data_header = True
                        continue

                    if read_metadata_header:
                        metadata_header = [x.lower() for x in cols]
                        read_metadata_header = False
                        parse_metadata_values = True
                        continue

                    if parse_metadata_values:
                        metadata = dict([(metadata_header[idx], value.lstrip(' ').rstrip(' ')) for idx, value in enumerate(cols) if value.lstrip(' ').rstrip(' ')])
                        lab_results.setdefault(metadata[u'lablittera'], {})[u'metadata'] = metadata
                        continue

                    if read_data_header:
                        data_header = [x.lower() for x in cols]
                        read_data_header = False
                        parse_data_values = True
                        continue

                    if parse_data_values:

                        data = dict([(data_header[idx], value.lstrip(' ').rstrip(' ')) for idx, value in enumerate(cols) if value.lstrip(' ').rstrip(' ')])
                        if u'mätvärdetal' in data:
                            data[u'mätvärdetal'] = data[u'mätvärdetal'].replace(decimalsign, '.')

                        if not u'parameter' in data:
                            utils.pop_up_info("WARNING: Parsing error. The parameter is missing on row " + str(cols))
                            continue

                        if data[u'lablittera'] not in lab_results:
                            utils.pop_up_info("WARNING: Parsing error. Data for " + data['lablittera'] + " read before it's metadata.")
                            file_error = True
                            break

                        """
                        Kalium (This part is VERY specific to Midvatten data analyses and probably doesn't affect anyone else)

                        Kalium is (in our very specific case) measured using two different methods. A high and a low resolution method.
                        The lowest value for low resolution method is '<2,5' (in the parameter 'mätvärdetext') and '<1' for the high resolution method.
                        If two kalium is present, we try to extract the high resolution method and store that one in the database.
                        If kalium is between 1 and 2,5, the high resolution method will show 1,5 (for example) while the low resolution will show '<2,5'.
                        If kalium is below 1, they will have values '<2,5' and '<1' in 'mätvärdetext'
                        If both are above 2,5, there is no good way to separate them. In that case, use the last one.
                        """
                        if data[u'parameter'] == u'kalium':
                            if u'kalium' not in lab_results[data[u'lablittera']]:
                                #kalium has not been parsed yet. Keep the current one.
                                pass
                            else:
                                if data.get(u'mätvärdetext', u'').strip(u' ') == u'<1' or lab_results[data[u'lablittera']][u'kalium'].get(u'mätvärdetext', u'').strip(u' ').replace(u',', u'.') == u'<2.5':
                                    #The current one is the high resolution one. Keep it to overwrite the other one.
                                    pass
                                elif data.get(u'mätvärdetext', u'').strip(u' ').replace(u',', u'.') == u'<2.5' or lab_results[data[u'lablittera']][u'kalium'].get(u'mätvärdetext', u'').strip(u' ') == u'<1':
                                    #The current one is the low resolution one, skip it.
                                    continue
                                else:
                                    #Hope that the current one (the last one) is the high resolution one and let it overwrite the existing one
                                    pass

                        lab_results[data[u'lablittera']][data[u'parameter']] = data

                        continue
                if not file_error:
                    all_lab_results.update(lab_results)

        return all_lab_results

    def interlab4_parse_filesettings(self, filename):
        """
        :param filename: Parses the file settings of an interlab4 file
        :return: a tuple like (file_error, version, encoding, decimalsign, quotechar)
        """
        version = None
        quotechar = False
        decimalsign = None
        file_error = False
        encoding=None
        #First find encoding
        for test_encoding in ['utf-16', 'utf-8', 'iso-8859-1']:
            try:
                with io.open(filename, 'r', encoding=test_encoding) as f:
                    for rawrow in f:
                        if '#tecken=' in rawrow.lower():
                            row = rawrow.lstrip('#').rstrip('\n').lower()
                            cols = row.split('=')
                            encoding = cols[1]
                            break
                        if not rawrow.startswith('#'):
                            break
            except UnicodeError:
                continue

        if encoding is None:
            encoding = utils.ask_for_charset('utf-16')

        #Parse the filedescriptor
        with io.open(filename, 'r', encoding=encoding) as f:
            for rawrow in f:
                if not rawrow.startswith('#'):
                    if any(x is  None for x in (version, decimalsign, quotechar)):
                        file_error = True
                    break

                row = rawrow.lstrip('#').rstrip('\n').lower()
                cols = row.split(u'=')
                if cols[0].lower() == u'version':
                    version = cols[1]
                elif cols[0].lower() == u'decimaltecken':
                    decimalsign = cols[1]
                elif cols[0].lower() == u'textavgränsare':
                    if cols[1].lower() == 'ja':
                        quotechar = '"'

        return (file_error, version, encoding, decimalsign, quotechar)

    def interlab4_to_table(self, _data_dict, existing_obsids=[]):
        """
        Converts a parsed interlab4 dict into a table for w_qual_lab import

        :param _data_dict:A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        :return: a list like [[u'obsid, depth, report, project, staff, date_time, anameth, reading_num, reading_txt, unit, comment'], rows with values]

        The translation from svensktvatten interlab4-keywords to w_qual_lab is from
        http://www.svensktvatten.se/globalassets/dricksvatten/riskanalys-och-provtagning/interlab-4-0.pdf

        """
        data_dict = copy.deepcopy(_data_dict)

        file_data = [[u'obsid', u'depth', u'report', u'project', u'staff', u'date_time', u'anameth', u'parameter', u'reading_num', u'reading_txt', u'unit', u'comment']]
        for lablittera, lab_results in data_dict.iteritems():
            metadata = lab_results.pop(u'metadata')

            try:
                obsid = metadata[u'provplatsid']
            except KeyError, e:
                obsid = None

            if obsid not in existing_obsids:
                metadata_as_text = [u': '.join([u'lablittera', lablittera])]
                metadata_as_text.extend([u': '.join([k, v]) for k, v in sorted(metadata.iteritems())])
                metadata_as_text = u'\n'.join(metadata_as_text)

                question = utils.NotFoundQuestion(dialogtitle=u'Submit obsid',
                                                  msg=u''.join([u'Submit the obsid for the metadata:\n ', metadata_as_text]),
                                                  existing_list=existing_obsids,
                                                  default_value=u'',
                                                  button_names=[u'Skip', u'Ok', u'Cancel'])
                answer = question.answer
                if answer == u'cancel':
                    return u'cancel'
                elif answer == u'skip':
                    continue

                obsid = utils.returnunicode(question.value)

            depth = None
            report = lablittera
            project = metadata.get(u'projekt', None)
            staff = metadata.get(u'provtagare', None)

            sampledate = metadata.get(u'provtagningsdatum', None)
            if sampledate is None:
                qgis.utils.iface.messageBar().pushMessage('Interlab4 import warning: There was no sample date found (column "provtagningsdatum"). Importing without it.')
                date_time = None
            else:
                sampletime = metadata.get(u'provtagningstid', None)
                if sampletime is not None:
                    date_time = datetime.strftime(datestring_to_date(u' '.join([sampledate, sampletime])), u'%Y-%m-%d %H:%M:%S')
                else:
                    date_time = datetime.strftime(datestring_to_date(sampledate), u'%Y-%m-%d %H:%M:%S')
                    qgis.utils.iface.messageBar().pushMessage('Interlab4 import warning: There was no sample time found (column "provtagningstid"). Importing without it.')

            meta_comment = metadata.get(u'kommentar', None)
            additional_meta_comments = [u'provtagningsorsak',
                                        u'provtyp',
                                        u'provtypspecifikation',
                                        u'bedömning',
                                        u'kemisk bedömning',
                                        u'mikrobiologisk bedömning',
                                        u'mätvärdetalanm',
                                        u'rapporteringsgräns',
                                        u'detektionsgräns',
                                        u'mätosäkerhet',
                                        u'mätvärdespår',
                                        u'parameterbedömning']
            #Only keep the comments that really has a value.
            more_meta_comments = u'. '.join([u': '.join([_x, metadata[_x]]) for _x in [_y for _y in additional_meta_comments if _y in metadata]  if all([metadata[_x], metadata[_x] is not None, metadata[_x].lower() != u'ej bedömt'])])
            if not more_meta_comments:
                more_meta_comments = None

            for parameter, parameter_dict in lab_results.iteritems():
                anameth = parameter_dict.get(u'metodbeteckning', None)
                reading_num = parameter_dict.get(u'mätvärdetal', None)

                try:
                    reading_txt = parameter_dict[u'mätvärdetext']
                except KeyError:
                    reading_txt = reading_num

                unit = parameter_dict.get(u'enhet', None)
                parameter_comment = parameter_dict.get(u'kommentar', None)

                file_data.append([obsid,
                                  depth,
                                  report,
                                  project,
                                  staff,
                                  date_time,
                                  anameth,
                                  parameter,
                                  reading_num,
                                  reading_txt,
                                  unit,
                                  u'. '.join([comment for comment in [parameter_comment, meta_comment, more_meta_comments] if comment is not None])]
                                 )
        return file_data
        
    def vlf_import(self):
        self.prepare_import('temporary_vlf_data')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = (utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1])#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(5, 'vlf_data', sqlremove, 'obs_lines', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "vlf_data" (obsid, length, real_comp, imag_comp, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM vlf_data""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def wlvllogg_import_from_diveroffice_files(self):
        """ Method for importing diveroffice csv files
        :return: None
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...

        existing_obsids = utils.get_all_obsids()

        confirm_names = utils.askuser("YesNo", "Do you want to confirm each logger import name before import?")

        import_all_data = utils.askuser("YesNo", "Do you want to import all data?\n\n" +
                                        "'No' = only new data after the latest date in the database,\n" +
                                        "for each observation point, will be imported.\n\n" +
                                        "'Yes' = any data not matching an exact datetime in the database\n" +
                                        " for the corresponding obs_point will be imported.")

        files = self.select_files()
        parsed_files = []
        for selected_file in files:
            file_data = self.parse_diveroffice_file(selected_file, self.charsetchoosen[0], existing_obsids, confirm_names.result)
            if file_data == u'cancel':
                self.status = True
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return u'cancel'
            elif file_data == u'skip':
                continue
            elif not isinstance(file_data, list):
                utils.MessagebarAndLog.critical(bar_msg="Import Failure: Something went wrong with file " + str(selected_file))
                continue

            parsed_files.append(file_data)

        if len(parsed_files) == 0:
            utils.MessagebarAndLog.critical(bar_msg="Import Failure: No files imported""")
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return

        #Header
        file_to_import_to_db =  [parsed_files[0][0]]
        file_to_import_to_db.extend([row for parsed_file in parsed_files for row in parsed_file[1:]])

        if not import_all_data.result:
            file_to_import_to_db = self.filter_dates_from_filedata(file_to_import_to_db, utils.get_last_logger_dates())

        file_string = utils.lists_to_string(file_to_import_to_db)

        with utils.tempinput(file_string, self.charsetchoosen[0]) as csvpath:
            self.csvlayer = self.csv2qgsvectorlayer(csvpath)
            #Continue to next file if the file failed to import
            if not self.csvlayer:
                qgis.utils.iface.messageBar().pushMessage("Import Failure","""No files imported""")
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return
            else:
                self.wlvllogg_import_from_csvlayer()

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def general_sqlite_table_import(self, column_header_translation_dict=None, goal_table=None):
        """ General method for importing an sqlite table into a goal_table

            self.temptableName must be the name of the table containing the new data to import.

        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...

        self.prepare_import(goal_table + u'_temp')

        if self.csvlayer:
            self.qgiscsv2sqlitetable(column_header_translation_dict) #loads qgis csvlayer into sqlite table

            #Create a dict with column names as keys and their types as units.
            table_info = utils.sql_load_fr_db(u'''PRAGMA table_info("%s")'''%goal_table)[1]
            column_headers_types = dict([(row[1], row[2]) for row in table_info])
            primary_keys = [row[1] for row in table_info if row[5] not in (u'0', 0)]
            columns_not_null = [row[1] for row in table_info if row[3] not in (u'0', 0)]
            columns_not_primary_key = [column for column in column_headers_types.keys() if column not in primary_keys]

            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
            existing_columns = [x[1] for x in self.columns]

            #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
            nr_before = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1]
            if u'date_time' in primary_keys:
                pks = [pk for pk in primary_keys if pk != u'date_time']
                pks.append(u'date_time')
                #Delete records that have the same date_time but with :00 at the end. (2016-01-01 00:00 will not be imported if 2016-01-01 00:00:00 exists
                utils.sql_alter_db(u'''delete from "%s" where "%s" in (select "%s" from "%s")'''%(self.temptableName,
                                                                                                  u' || '.join([pk for pk in pks]) + u':00',
                                                                                                  u' || '.join([pk for pk in pks]),
                                                                                                  goal_table))
                # Delete records that have the same date_time but with :00 at the end. (2016-01-01 00:00:00 will not be imported if 2016-01-01 00:00 exists
                utils.sql_alter_db(u'''delete from "%s" where "%s" in (select "%s" from "%s")'''%(self.temptableName,
                                                                                                  u' || '.join([pk for pk in pks])[:-3],
                                                                                                  u' || '.join([pk for pk in pks]),
                                                                                                  goal_table))

            nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1]
            if nr_after == 0:
                utils.MessagebarAndLog.critical(bar_msg=u'Import error, nothing imported.')
                self.status = False
                return
            elif nr_after > nr_before:
                utils.MessagebarAndLog.warning(bar_msg=u"Import warning, see log message panel", log_msg='In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported.'%(str(nr_after - nr_before)))

            #Delete empty records from the import table. All not-null must exist and at least one non-pk field.
            nr_before = utils.sql_load_fr_db(u'''select count(*) from "%s"''' % (self.temptableName))[1]
            sqlremove_list = []
            sqlremove_list.append(ur"""DELETE FROM "%s" where """%(self.temptableName))
            sqlremove_list.append(u' or '.join([ur""""%s" in ('', ' ') or "%s" is null """%(column, column) for column in columns_not_null]))
            sqlremove_list.append(u' or (')
            sqlremove_list.append(u' and '.join([ur"""("%s" in ('', ' ') or "%s" is null) """%(column, column) for column in columns_not_primary_key]))
            sqlremove_list.append(u')')
            sqlremove = u''.join(sqlremove_list).encode(u'utf-8')
            utils.sql_alter_db(sqlremove)
            nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1]

            nr_before = utils.sql_load_fr_db(u'SELECT Count(*) FROM "%s"'%self.temptableName)[1][0]
            if nr_before == 0:
                utils.MessagebarAndLog.critical(bar_msg=u'Import error, nothing imported.')
                self.status = False
                return
            if nr_before > nr_before:
                utils.MessagebarAndLog.info(bar_msg=u"Import info, see log message panel", log_msg=u'In total "%s" rows remain after empty rows have been deleted'%(str(nr_after - nr_before)))

            sqlNoOfdistinct = u"""SELECT Count(*) FROM (SELECT DISTINCT %s FROM %s)"""%(u', '.join([u'"{}"'.format(pk_col) for pk_col in primary_keys]), self.temptableName) #Number of distinct data posts in the import table

            #Check for foreign keys:
            foreign_keys = self.get_foreign_keys(goal_table)
            # Import foreign keys in some special cases
            force_import_of_foreign_keys_tables = [u'zz_flowtype', u'zz_staff', u'zz_meteoparam']
            for fk_table, from_to_fields in foreign_keys.iteritems:
                if fk_table in force_import_of_foreign_keys_tables:
                    from_list = [x[0] for x in from_to_fields]
                    to_list = [x[1] for x in from_to_fields]

                    sql = ur"""insert or ignore into %s (%s) select distinct %s from %s""" % (fk_table,
                                                                                             u', '.join(to_list),
                                                                                             u', '.join(from_list),
                                                                                             self.temptableName)
                    utils.sql_alter_db(sql)
                else:


            verifyok = self.VerifyIDInMajorTable(MajorTable)



            geometry_columns = self.get_geometry_columns()
            geocol = [_geocol for _geocol in geometry_columns if _geocol in foreign_keys]
            if len(geocol) > 1:
                log_msg = u'The table "%s" had more than two geometry columns as foreign key tables.'%goal_table
                print(log_msg)
                utils.MessagebarAndLog.warning(bar_msg=u"Import error, see log message panel", log_msg=log_msg)
                self.status = 'False'
                return
            elif len(geocol) == 1:
                MajorTable = geocol[0]
            else:
                MajorTable = None
            cleaningok = self.multiple_field_duplicates(GoalTable=goal_table,
                                                        sqlremove=sqlremove,
                                                        MajorTable=MajorTable,
                                                        sqlNoOfdistinct=sqlNoOfdistinct)

            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                # Add level_masl column and fill with data

                if goal_table == u'w_levels_logger':
                    column_headers = self.add_level_masl(self.temptableName, column_headers, column_header_translation_dict)

                #Import foreign keys in some special cases
                for zz_table in [u'zz_flowtype', u'zz_staff', u'zz_meteoparam']:
                    from_to_fields = foreign_keys.get(zz_table, None)
                    if from_to_fields is not None:
                        from_list = [column_header_translation_dict.get(x[0], x[0]) for x in from_to_fields]
                        to_list = [x[1] for x in from_to_fields]

                        sql = r"""insert or ignore into %s (%s) select distinct %s from %s"""%(zz_table,
                                                                                               ', '.join(to_list),
                                                                                               ', '.join(from_list),
                                                                                               self.temptableName)
                        utils.sql_alter_db(sql)

                # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                sql_list = [u"""INSERT OR IGNORE INTO "%s" ("""%goal_table]
                sql_list.append(u', '.join([u'"{}"'.format(k) for k in sorted(column_headers.keys())]))
                sql_list.append(u""") SELECT """)
                sql_list.append(u', '.join([u"""(case when "%s"!='' then CAST("%s" as "%s") else null end)"""%(orig_colname, orig_colname, column_headers_types[k]) for k, orig_colname in sorted(column_headers.iteritems())]))
                sql_list.append(u"""FROM %s"""%(self.temptableName))
                sql = u''.join(sql_list)
                utils.sql_alter_db(sql.encode(u'utf-8'))

                self.status = 'True'        # Cleaning was OK and import perfomed!!

                self.recsafter = (utils.sql_load_fr_db(u'''SELECT Count(*) FROM "%s"'''%goal_table)[1])[0][0] #for the statistics
                self.StatsAfter()

                utils.MessagebarAndLog.info(bar_msg="""In total %s measurements were imported."""%((self.recsafter - self.recsbefore)))
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed

            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def check_obsids(self, file_data):
        return utils.filter_nonexisting_values_and_ask(file_data, u'obsid', utils.get_all_obsids(), try_capitalize=False)

    def ask_for_staff(self):
        existing_staff = defs.staff_list()[1]

        question = utils.NotFoundQuestion(dialogtitle=u'Submit field staff',
                                       msg=u'Submit the field staff who made the FieldLogger measurements.\nIt will be used for the rest of the import',
                                       existing_list=existing_staff)
        answer = question.answer
        if answer == u'cancel':
            return u'cancel'

        return utils.returnunicode(question.value)

    def send_file_data_to_importer(self, file_data, importer, cleaning_function=None):
        self.csvlayer = None
        if len(file_data) < 2:
            return

        if cleaning_function is not None:
            file_data = cleaning_function(file_data)

        file_string = utils.lists_to_string(file_data)

        with utils.tempinput(file_string) as csvpath:
            csvlayer = self.csv2qgsvectorlayer(csvpath)
            if not csvlayer:
                utils.MessagebarAndLog.critical("Import error: Creating csvlayer failed!")
                return
            self.csvlayer = csvlayer
            importer()

    def prepare_import(self, temptableName):
        """ Shared stuff as preparation for the import """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.status = 'False' #True if upload to sqlite and cleaning of data succeeds 
        self.temptableName = temptableName        

    def VerifyIDInMajorTable(self,MajorTable): #for all tables with foreign key = obsid
        notinmajor = 'False'
        possibleobsids = utils.sql_load_fr_db("""select distinct obsid from %s"""%MajorTable)[1]
        #obsidstobeimported = []
        obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))[1]
        #obsidstobeimported.append(tuple([x.toPyObject() if isinstance(x, PyQt4.QtCore.QVariant) else x for y in utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[0][1],self.temptableName))[1] for x in y]))
        for id in obsidstobeimported:
                if not id in possibleobsids:
                    qgis.utils.iface.messageBar().pushMessage("Import Failure","""The obsid=%s do not exist in %s!"""%(str(id[0]),MajorTable),2)
                    self.status = 'False'
                    notinmajor = 'True'
        if notinmajor == 'True':
            return 0
        else:
            return 1
            
    def CheckIfOBSIDExists(self,GoalTable,idcol):#for obs_points and obs_lines where primary key = obsid
        possibleobsids = utils.sql_load_fr_db("""select distinct obsid from '%s'"""%GoalTable)[1]
        obsidstobeimported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[idcol][1],self.temptableName))[1]
        for id in obsidstobeimported:
            if id in possibleobsids:
                qgis.utils.iface.messageBar().pushMessage("Warning","""obsid=%s do already exist in the database and will not be imported again!"""%str(id[0]),1,duration=10)

    def multiple_field_duplicates(self, NoCols=None, GoalTable=None, sqlremove=None, MajorTable=None, sqlNoOfdistinct=None):  #For secondary tables linking to obs_points and obs_lines: Sanity checks and removes duplicates
        """perform some sanity checks of the imported data and removes duplicates and empty records"""
        if NoCols is not None:
            if len(self.columns)<NoCols:
                qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                self.status = 'False'
                return 0 #only to stop function
            elif len(self.columns) > NoCols:#Here is where the user may interrupt if there are more columns than needed
                ManyColsQuestion = utils.askuser("YesNo", """Please note!\nThere are %s columns in your csv file which may be perfectly fine if the first %s corresponds to those needed.\n\nDo you want to proceed with the import?"""%(str(len(self.columns)),str(NoCols)),"Warning!")
                if ManyColsQuestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
        #remove empty records
        utils.sql_alter_db(sqlremove)
        #Then verify that obsid exists in MajorTable and perform statistics
        verifyok = 1
        if MajorTable is not None:
            verifyok = self.VerifyIDInMajorTable(MajorTable) #Verify that all ID's exist in major table (obs_points or obs_lines)
        if verifyok == 1: #Go on with some statistics
            self.recsbefore = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%GoalTable)[1])[0][0]
            self.recstoimport = (utils.sql_load_fr_db(sqlNoOfdistinct)[1])[0][0]
            self.recsinfile = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1])[0][0]
            #qgis.utils.iface.messageBar().pushMessage("Info","The csv file had " + str(self.recsinfile) + " non-empty posts \n" + "and among these were found " + str(self.recsinfile - self.recstoimport) + " duplicates.", 0)
            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.recsinfile > self.recstoimport: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?"""%(self.recsinfile - self.recstoimport),"Warning!")
                if duplicatequestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
            return 1
        else:
            return 0

    def SingleFieldDuplicates(self,NoCols,GoalTable,sqlremove,idcol): #For major tables obs_points and obs_lines: Sanity checks and removes duplicates
        """perform some sanity checks of the imported data and removes duplicates and empty records"""
        if not len(self.columns)==NoCols:
            qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have exactly " + str(NoCols) + " columns!\nCheck your data and try again.",2)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.status = 'False'
            return 0 #only to stop function
        else:    #If correct number of columns, remove empty records
            utils.sql_alter_db(sqlremove)
            #Then check if any obsid already exist in GoalTable and perform statistics
            self.CheckIfOBSIDExists(GoalTable,idcol)
            #Some statistics
            self.recsbefore = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%GoalTable)[1])[0][0] 
            self.recstoimport = (utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))[1])[0][0]
            self.recsinfile = (utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1])[0][0]
            #qgis.utils.iface.messageBar().pushMessage("Info","The csv file had " + str(self.recsinfile) + " non-empty posts \n" + "and among these were found " + str(self.recsinfile - self.recstoimport) + " duplicates.", 0)
            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.recsinfile > self.recstoimport: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?"""%(self.recsinfile - self.recstoimport),"Warning!")
                if duplicatequestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
            return 1

    def StatsAfter(self):
        NoExcluded = self.recstoimport - (self.recsafter - self.recsbefore)
        if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
            qgis.utils.iface.messageBar().pushMessage("Warning","""In total %s posts were not imported since they would have caused duplicates in the database."""%NoExcluded, 1)

    def selectcsv(self, only_one_file=True): # general importer
        """Select the csv file, user must also tell what charset to use"""
        try:#MacOSX fix2
            localencoding = locale.getdefaultlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        except:
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal,'utf-8')
        if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
            if only_one_file:
                csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
                csvlayer = self.csv2qgsvectorlayer(csvpath)
            else:
                csvpath = PyQt4.QtGui.QFileDialog.getOpenFileNames(None, "Select Files","","csv (*.csv)")
                csvlayer = [self.csv2qgsvectorlayer(path) for path in csvpath if path]
            return csvlayer

    def select_files(self, only_one_file=False, should_ask_for_charset=True):

        def get_path(only_one_file):
            if only_one_file:
                path = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            else:
                path = PyQt4.QtGui.QFileDialog.getOpenFileNames(None, "Select Files","","csv (*.csv)")
            if not isinstance(path, (list, tuple)):
                path = [path]
            return path

        path = []

        if not should_ask_for_charset:
            path = get_path(only_one_file)
        else:
            try:#MacOSX fix2
                localencoding = locale.getdefaultlocale()[1]
                self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
            except:
                self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal, 'utf-8')
            if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
                path = get_path(only_one_file)
        #Filter all empty strings
        path = [p for p in path if p]
        return path

    @staticmethod
    def parse_diveroffice_file(path, charset, existing_obsids=None, ask_for_names=True, begindate=None, enddate=None):
        """ Parses a diveroffice csv file into a string

        :param path: The file name
        :param existing_obsids: A list or tuple with the obsids that exist in the db.
        :param ask_for_names: (True/False) True to ask for obsid name for every obsid. False to only ask if the obsid is not found in existing_obsids.
        :return: A string representing a table file. Including '\n' for newlines.

        Assumptions and limitations:
        * The Location attribute is used as obsid and added as a column.
        * Values containing ',' is replaced with '.'
        * Rows with missing "Water head[cm]"-data is skipped.

        """
        #These can be set to paritally import files.
        #begindate = datetime.strptime(u'2016-06-08 20:00:00',u'%Y-%m-%d %H:%M:%S')
        #enddate = datetime.strptime(u'2016-06-08 19:00:00',u'%Y-%m-%d %H:%M:%S')

        filedata = []
        begin_extraction = False
        delimiter = u';'
        num_cols = None
        with io.open(path, u'r', encoding=str(charset)) as f:
            obsid = None
            for rawrow in f:
                row = rawrow.rstrip(u'\n').rstrip(u'\r').lstrip()

                #Try to get obsid
                if row.startswith(u'Location'):
                    obsid = row.split(u'=')[1].strip()
                    continue

                cols = row.split(delimiter)

                #Parse header
                if row.startswith(u'Date/time'):
                    #Check that the delimitor is ; or try , or stop.
                    if not 3 <= len(cols) <= 4:
                        if 3 <= len(row.split(u',')) <= 4:
                            delimiter = u','
                        else:
                            return utils.ask_user_about_stopping("Failure, delimiter did not match ';' or ',' or there was less than 3 or more than 4 columns in the file " + path + "\nDo you want to stop the import? (else it will continue with the next file)")

                    cols = row.split(delimiter)
                    num_cols = len(cols)

                    header = cols
                    begin_extraction = True
                    continue

                #Parse data
                if begin_extraction:
                    dateformat = find_date_format(cols[0])
                    if dateformat is not None:
                        if len(cols) != num_cols:
                            return utils.ask_user_about_stopping("Failure: The number of data columns in file " + path + " was not equal to the header.\nIs the decimal separator the same as the delimiter?\nDo you want to stop the import? (else it will continue with the next file)")

                        #Skip rows without flow value
                        try:
                            float(cols[1].replace(u',', u'.'))
                        except ValueError:
                            continue

                        date = datetime.strptime(cols[0], dateformat)

                        #TODO: These checks are not implemented as a dialog yet.
                        if begindate is not None:
                            if date < begindate:
                                continue
                        if enddate is not None:
                            if date > enddate:
                                continue

                        printrow = [datetime.strftime(date,u'%Y-%m-%d %H:%M:%S')]
                        printrow.extend([col.replace(u',', u'.') for col in cols[1:]])
                        filedata.append(printrow)

        if len(filedata) == 0:
            return utils.ask_user_about_stopping("Failure, parsing failed for file " + path + "\nNo valid data found!\nDo you want to stop the import? (else it will continue with the next file)")

        answer = None
        if ask_for_names:
            answer = utils.filter_nonexisting_values_and_ask([[u'obsid'], [obsid]], u'obsid', existing_obsids, try_capitalize=False)
        else:
            if obsid not in existing_obsids:
                answer = utils.filter_nonexisting_values_and_ask([[u'obsid'], [obsid]], u'obsid', existing_obsids, try_capitalize=True)

        if answer == u'cancel':
            return answer

        if answer is not None:
            if isinstance(answer, (list, tuple)):
                if len(answer) > 1:
                    obsid = answer[1][0]
                else:
                    return u'skip'

        header.append(u'obsid')
        for row in filedata:
            row.append(obsid)

        if u'Conductivity[mS/cm]' not in header:
            header.append(u'Conductivity[mS/cm]')
            for row in filedata:
                row.append(u'')

        translation_dict_in_order = OrderedDict([(u'obsid', u'obsid'),
                                                 (u'Date/time', u'date_time'),
                                                 (u'Water head[cm]', u'head_cm'),
                                                 (u'Temperature[°C]', u'temp_degc'),
                                                 (u'Conductivity[mS/cm]', u'cond_mscm')])

        try:
            translated_header = [translation_dict_in_order[headername] for headername in header]
        except KeyError:
            utils.MessagebarAndLog.critical(bar_msg=u"Failure during import. See log for more information", log_msg=u"Failure, the file " + utils.returnunicode(path) + u"\ndid not have the correct headers and will not be imported.\nMake sure its barocompensated!\nSupported headers are obsid, Date/time, Water head[cm], Temperature[°C] and optionally Conductivity[mS/cm].")
            return u'skip'

        filedata.reverse()
        filedata.append(translated_header)
        filedata.reverse()

        sorted_filedata = [[row[translated_header.index(v)] for v in translation_dict_in_order.values()] for row in filedata]

        return sorted_filedata

    @staticmethod
    def filter_dates_from_filedata(file_data, obsid_last_imported_dates, obsid_header_name=u'obsid', date_time_header_name=u'date_time'):
        """
        :param file_data: a list of lists like [[u'obsid', u'date_time', ...], [obsid1, date_time1, ...]]
        :param obsid_last_imported_dates: a dict like {u'obsid1': last_date_in_db, ...}
        :param obsid_header_name: the name of the obsid header
        :param date_time_header_name: the name of the date_time header
        :return: A filtered list with only dates after last date is included for each obsid.

        >>> midv_data_importer.filter_dates_from_filedata([['obsid', 'date_time'], ['obs1', '2016-09-28'], ['obs1', '2016-09-29']], {'obs1': [('2016-09-28', )]})
        [['obsid', 'date_time'], ['obs1', '2016-09-29']]
        """
        if len(file_data) == 1:
            return file_data

        obsid_idx = file_data[0].index(obsid_header_name)
        date_time_idx = file_data[0].index(date_time_header_name)
        filtered_file_data = [row for row in file_data[1:] if datestring_to_date(row[date_time_idx]) > datestring_to_date(obsid_last_imported_dates.get(row[obsid_idx], [(u'0001-01-01 00:00:00',)])[0][0])]
        filtered_file_data.reverse()
        filtered_file_data.append(file_data[0])
        filtered_file_data.reverse()
        return filtered_file_data

    def csv2qgsvectorlayer(self, path):
        """ Creates QgsVectorLayer from a csv file """
        if not path:
            qgis.utils.iface.messageBar().pushMessage("Failure, no csv file was selected.")
            return False        
        csvlayer = QgsVectorLayer(path, "temporary_csv_layer", "ogr")
        if not csvlayer.isValid():
            qgis.utils.iface.messageBar().pushMessage("Failure","Impossible to Load File in QGis:\n" + str(path), 2)
            return False
        csvlayer.setProviderEncoding(str(self.charsetchoosen[0]))                 #Set the Layer Encoding                                        
        return csvlayer                
                
    def qgiscsv2sqlitetable(self, column_header_translation_dict=None): # general importer
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'."""

        if column_header_translation_dict is None:
            column_names_translation_dict = column_header_translation_dict

        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.temptableName): #if so, propose to rename the temporary import-table
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.temptableName='%s_2'%self.temptableName
                else:
                    return None
                  
        #Get all fields with corresponding types for the csv-csvlayer in qgis
        fields=[]
        fieldsNames=[]
        provider=self.csvlayer.dataProvider()
        for name in provider.fields(): #fix field names and types in temporary table
            fldName = unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names
            fldName = column_header_translation_dict.get(fldName, fldName)
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not a .csvt file is defined beside the imported file.
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool, PyQt4.QtCore.QVariant.Int,QtCore.QVariant.LongLong, PyQt4.QtCore.QVariant.UInt, PyQt4.QtCore.QVariant.ULongLong):  # field type is integer
                fldType='integer'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is double
                fldType='real'
            else: # if field type is not recognized by qgis
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())
        
        #Create the import-table in DB
        fields=','.join(fields) 
        utils.sql_alter_db("""CREATE table "%s" (%s)"""%(self.temptableName, fields)) # Create a temporary table with only text columns (unless a .csvt file was defined by user parallell to the .csv file)
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.

        # Retreive every feature from temporary .csv qgis csvlayer and write it to the temporary table in sqlite (still only text fields unless user specified a .csvt file)
        for feature in self.csvlayer.getFeatures(): 
            values_perso=[]
            for attr in feature.attributes():
                #If automatic convertion from PyQt4.QtCore.QVariant did not work, it must be done manually
                if isinstance(attr, PyQt4.QtCore.QVariant):
                    attr = attr.toPyObject()
                values_perso.append(attr) # attr is supposed to be unicode and should be kept like that, sometimes though it ends up being a byte string, do not know why....
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USE utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                #please note the usage of ? for parameter substitution - highly recommended
                #curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso]))
                try:
                    curs.execute("""INSERT INTO %s VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([value for value in values_perso])) # Assuming value is unicode, send it as such to sqlite
                except:
                    curs.execute("""INSERT INTO %s VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) #in case of errors, the value must be a byte string, then try to convert to unicode
                self.status = 'True'
            else: #no attribute Datas
                qgis.utils.iface.messageBar().pushMessage("No data found!!","No data will be imported!!", 2)
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.close()
        conn.close()

    def cleanuploggerdata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
        if len(self.columns)==4 or len(self.columns)==5:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null"""%(self.temptableName,column[1],column[1]))
            #THE METHOD ABOVE NEEDS REVISON
            # Add level_masl column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double"""%self.temptableName)
            utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """%(self.temptableName,self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
            
            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))[1]
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1]

            #Then check wether there are duplicates in the imported file and if so, ask user what to do
            if self.RecordsInFile[0][0] > self.RecordsToImport[0][0]: # If there are duplicates in the import file, let user choose whether to abort or import only last of duplicates
                duplicatequestion = utils.askuser("YesNo", """Please note!\nThere are %s duplicates in your data!\n(More than one measurement at the same date_time.)\nDo you really want to import these data?\nAnswering yes will start, from top of the imported file and only import the first of the duplicate measurements.\n\nProceed?"""%(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]),"Warning!")
                #utils.pop_up_info(duplicatequestion.result)    #debug
                if duplicatequestion.result == 0:      # if the user wants to abort
                    return 0    # return 0 and then nothing will be imported

            # Return 1 to perform import if either no duplicates existed in importfile or user wants to import only the last record of the duplicates 
            return 1
        else:
            return 0                    
        
    def SanityCheckVacuumDB(self):
        sanity = utils.askuser("YesNo","""It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""",'Vacuum the database?')
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def add_level_masl(self, tablename, column_headers, column_header_translation_dict):
        if u'level_masl' not in column_headers:
            column_headers = copy.deepcopy(column_headers)
            utils.sql_alter_db(u"""ALTER table "%s" ADD COLUMN level_masl double""" % tablename)
            utils.sql_alter_db(u"""UPDATE "%s" SET level_masl = -999-"%s" """ %(tablename,
                                                                                column_header_translation_dict.get(u'head_cm', u'head_cm')))
            column_headers[u'level_masl'] = u'level_masl'
        return column_headers

    def verify_and_import_to_zz_flowtype(self, temptablename, type_column):
        existing_types = [col[0] for col in utils.sql_load_fr_db('select distinct type from zz_flowtype')[1]]
        types_in_temptable = [col[0] for col in utils.sql_load_fr_db("""select distinct "%s" from %s"""%(type_column, temptablename))[1]]
        for _type in types_in_temptable:
            if _type not in existing_types:
                sql = u"""insert into "zz_flowtype" ("type", "explanation") VALUES ('%s', NULL)""" %(_type)
                utils.sql_alter_db(sql)

    def get_foreign_keys(self, tname):
        result_list = utils.sql_load_fr_db(u"""PRAGMA foreign_key_list(%s)"""%(tname))[1]
        foreign_keys = {}
        for row in result_list:
            foreign_keys.setdefault(row[2], []).append((row[3], row[4]))
        return foreign_keys

    def get_geometry_columns(self):
        return [row[0] for row in utils.sql_load_fr_db(u'SELECT "f_table_name" FROM "geometry_columns"')[1]]










