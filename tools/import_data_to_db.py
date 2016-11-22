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


import_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_fieldlogger.ui'))[0]


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
        self.fieldlogger_staff = None

    def default_import(self, importer):
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        importer()
        self.SanityCheckVacuumDB()
        
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

        self.send_file_data_to_importer(wquallab_data_table, self.wquallab_import_from_csvlayer, self.check_obsids)
        self.SanityCheckVacuumDB()

    def parse_interlab4(self, filenames=None):
        """ Reads the interlab
        :param filenames:
        :return: A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        """
        if filenames is None:
            filenames = utils.select_files(only_one_file=False, should_ask_for_charset=False, extension="lab (*.lab)")[0]
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

    def seismics_import(self):
        self.prepare_import('temporary_seismics')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1]) #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) # To select distinct data posts from the import table
            cleaningok = self.multiple_field_duplicates(6, 'seismic_data', sqlremove, 'obs_lines', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "seismic_data" (obsid, length, ground, bedrock, gw_table, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[5][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM seismic_data""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def strat_import(self):
        self.prepare_import('temporary_stratigraphy')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1]) #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(9, 'stratigraphy', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "stratigraphy" (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as integer), CAST("%s" as double), CAST("%s" as double), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1], self.columns[1][1], self.columns[2][1], self.columns[3][1], self.columns[4][1], self.columns[5][1], self.columns[6][1], self.columns[7][1], self.columns[8][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM stratigraphy""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
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

    def wflow_import_from_csvlayer(self): #please note the particular behaviour of adding additional flowtypes to table zz_flowtype
        """
        self.csvlayer must contain columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment"
        :return:
        """
        self.prepare_import('temporary_wflow')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(7, 'w_flow', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then fix zz_flowtype and then copy data from the temporary table to the original table in the db
                #check for flowtypes and add those that are not present in db table zz_flowtype the obsid actually exists in obs_points
                FlTypesInDb = utils.sql_load_fr_db('select distinct type, unit from zz_flowtype')[1]
                FlTypes2BImported = utils.sql_load_fr_db("""select distinct "%s", "%s" from %s"""%(self.columns[2][1], self.columns[5][1],self.temptableName))[1]

                try:
                    for tp in FlTypes2BImported:
                        if tp not in FlTypesInDb:
                            sql = """insert into "zz_flowtype" (type, unit, explanation) VALUES ("%s", "%s", '');"""%(str(tp[0]), tp[1])
                            utils.sql_alter_db(sql)
                except TypeError:
                    qgis.utils.iface.messageBar().pushMessage("Import warning","""Flow type could not be updated. Table zz_flowtype needs to be upgraded to latest version.""")

                sqlpart1 = """INSERT OR IGNORE INTO "w_flow" (obsid, instrumentid, flowtype, date_time, reading, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_flow""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def meteo_import(self): #please note the particular behaviour of adding additional flowtypes to table zz_meteoparam
        self.prepare_import('temporary_meteo')
        self.csvlayer = self.selectcsv() # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(8, 'meteo', sqlremove, 'obs_points', sqlNoOfdistinct)#
            if cleaningok == 1: # If cleaning was OK, then fix zz_meteoparam and then copy data from the temporary table to the original table in the db
                #check for parameters and add those that are not present in db table zz_meteoparam
                FlTypesInDb = utils.sql_load_fr_db('select distinct parameter from zz_meteoparam')[1] 
                FlTypes2BImported = utils.sql_load_fr_db("""select distinct "%s" from %s"""%(self.columns[2][1],self.temptableName))[1]
                for tp in FlTypes2BImported:
                        if not tp in FlTypesInDb:
                            sql = """insert into "zz_meteoparam" (parameter, explanation) VALUES ("%s", '');"""%str(tp[0])
                            utils.sql_alter_db(sql)
            
                sqlpart1 = """INSERT OR IGNORE INTO "meteo" (obsid, instrumentid, parameter, date_time, reading_num, reading_txt, unit, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1],self.columns[4][1],self.columns[4][1],self.columns[5][1],self.columns[6][1],self.columns[7][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM meteo""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def wlvl_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, date_time, meas, comment"
        :return: None
        """
        self.prepare_import('temporary_wlevels')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table
            if len(self.columns) < 4:
                qgis.utils.iface.messageBar().pushMessage("Import Failure","""The file had less than the required 4 columns""")
                cleaningok = 0
            else:
                sqlremove = """DELETE FROM "%s" where ("%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null) or (("%s"='' or "%s"=' ' or "%s" is null) and ("%s"='' or "%s"=' ' or "%s" is null))"""%(self.temptableName,self.columns[0][1],self.columns[0][1],self.columns[0][1],self.columns[1][1],self.columns[1][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.columns[3][1],self.columns[3][1])#Delete empty records from the import table!!!
                sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(self.columns[0][1],self.columns[1][1],self.temptableName) #Number of distinct data posts in the import table
                cleaningok = self.multiple_field_duplicates(4, 'w_levels', sqlremove, 'obs_points', sqlNoOfdistinct)

            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                sqlpart1 = """INSERT OR IGNORE INTO "w_levels" (obsid, date_time, meas, comment) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), (case when "%s"!='' then CAST("%s" as double) else null end), CAST("%s" as text) FROM %s"""%(self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[2][1],self.columns[3][1],self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
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

    def wlvllogg_import_from_csvlayer(self, column_header_translation_dict={}):
        """ Method for importing diveroffice csv files
            The csv-file is assumend to have colums: date_time, meas, temperature, obsid
            or
            date_time, meas, temperature, conductivity, obsid

            n\nDate/time,Water head[cm],Temperature[°C]\nor\nDate/time,Water head[cm],Temperature[°C],1:Conductivity[mS/c
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtGui.QCursor(PyQt4.QtCore.Qt.WaitCursor))  #show the user this may take a long time...

        self.prepare_import(u'temporary_logg_lvl')

        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table

            column_headers_types = {u'obsid': u'text',
                                   u'date_time': u'text',
                                   u'head_cm': u'double',
                                   u'temp_degc': u'double',
                                   u'cond_mscm': u'double',
                                   u'level_masl': u'double',
                                   u'comment': u'text'}

            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
            existing_columns = [x[1] for x in self.columns]
            column_headers = dict([(column_header, column_header_translation_dict.get(column_header, column_header)) for column_header in column_headers_types.keys() if column_header_translation_dict.get(column_header, column_header) in existing_columns])
            required_columns =  [u'obsid', u'date_time', u'head_cm']
            for _column in required_columns:
                if _column not in column_headers:
                    qgis.utils.iface.messageBar().pushMessage("ERROR Import failed: Column '" + _column + " did not exist in the csvfile.")
                    return

            #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
            nr_before = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1]
            utils.sql_alter_db(u'''delete from "%s" where obsid || date_time || ':00' in ( select obsid || date_time from w_levels_logger)'''%(self.temptableName))
            utils.sql_alter_db(u'''delete from "%s" where SUBSTR(obsid || date_time, 1, length(obsid || date_time) - 3) in ( select obsid || date_time from w_levels_logger)'''%(self.temptableName))
            nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1]
            if nr_after > nr_before:
                qgis.utils.iface.messageBar().pushMessage("""In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported."""%(str(nr_after - nr_before)))

            #Delete empty records from the import table!!! (Temperature and conductivity is allowed to be NULL.
            sqlremove_list = []
            sqlremove_list.append(ur"""DELETE FROM "%s" where """%(self.temptableName))
            sqlremove_list.append(u' or '.join([ur""""%s" in ('', ' ') or "%s" is null"""%(column, column) for column in required_columns]))
            sqlremove = u''.join(sqlremove_list).encode(u'utf-8')

            sqlNoOfdistinct = u"""SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(column_headers[u'date_time'], column_headers[u'obsid'], self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(len(column_headers), u'w_levels_logger', sqlremove, u'obs_points', sqlNoOfdistinct)

            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db
                # Add level_masl column and fill with data
                if u'level_masl' not in column_headers:
                    utils.sql_alter_db(u"""ALTER table "%s" ADD COLUMN level_masl double"""%self.temptableName)
                    utils.sql_alter_db(u"""UPDATE "%s" SET level_masl = -999-"%s" """%(self.temptableName, u'head_cm'))
                    column_headers[u'level_masl'] = u'level_masl'

                sql_list = []
                # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                sql_list.append(u"""INSERT OR IGNORE INTO "w_levels_logger" (""")
                sql_list.append(u', '.join([u'"{}"'.format(k) for k in sorted(column_headers.keys())]))
                sql_list.append(u""") SELECT """)
                sql_list.append(u', '.join([u"""(case when "%s"!='' then CAST("%s" as "%s") else null end)"""%(colname, colname, column_headers_types[k]) for k, colname in sorted(column_headers.iteritems())]))
                sql_list.append(u"""FROM %s"""%(self.temptableName))
                sql = u''.join(sql_list)
                utils.sql_alter_db(sql.encode(u'utf-8'))

                self.status = 'True'        # Cleaning was OK and import perfomed!!

                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1])[0][0] #for the statistics
                self.StatsAfter()

                qgis.utils.iface.messageBar().pushMessage("""In total %s measurements were imported."""%((self.recsafter - self.recsbefore)))
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed

            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def wquallab_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        :return: None
        """
        self.prepare_import('temporary_wquallab')

        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table

            obsid = self.columns[0][1]
            depth = self.columns[1][1]
            report = self.columns[2][1]
            project = self.columns[3][1]
            staff = self.columns[4][1]
            date_time = self.columns[5][1]
            anameth = self.columns[6][1]
            parameter = self.columns[7][1]
            reading_num = self.columns[8][1]
            reading_txt = self.columns[9][1]
            unit = self.columns[10][1]
            comment = self.columns[11][1]

            #Delete empty records from the import table!!!
            sqlremove_list = []
            sqlremove_list.append(r"""DELETE FROM "%s" """%(self.temptableName))
            sqlremove_list.append(r"""where "%s" in ('', ' ') or "%s" is null """%(obsid, obsid))
            sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(report, report))
            sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(date_time, date_time))
            sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(parameter, parameter))
            sqlremove_list.append(r"""or ("%s" in ('', ' ') or "%s" is null) """%(reading_num, reading_num))
            sqlremove_list.append(r"""and ("%s" in ('', ' ') or "%s" is null) """%(reading_txt, reading_txt))
            sqlremove_list.append(r"""and ("%s" in ('', ' ') or "%s" is null)"""%(comment, comment))
            sqlremove = ''.join(sqlremove_list)

            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s" FROM %s)"""%(report,parameter,self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(12, 'w_qual_lab', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db

                if utils.verify_table_exists('zz_staff'):
                    #Add staffs that does not exist in db
                    staffs = set([x[0] for x in utils.sql_load_fr_db("""select distinct staff from %s"""%self.temptableName)[1]])
                    self.staff_import(staffs)

                sql_list = []
                sql_list.append(r"""INSERT OR IGNORE INTO "w_qual_lab" (obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment) """)
                sql_list.append(r"""SELECT CAST("%s" as text), """%obsid)
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(depth, depth))
                sql_list.append(r"""CAST("%s" as text), """%(report))
                sql_list.append(r"""CAST("%s" as text), """%(project))
                sql_list.append(r"""CAST("%s" as text), """%(staff))
                sql_list.append(r"""CAST("%s" as text), """%(date_time))
                sql_list.append(r"""CAST("%s" as text), """%(anameth))
                sql_list.append(r"""CAST("%s" as text), """%(parameter))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(reading_num, reading_num))
                sql_list.append(r"""CAST("%s" as text), """%(reading_txt))
                sql_list.append(r"""CAST("%s" as text), """%(unit))
                sql_list.append(r"""CAST("%s" as text)           """%(comment))
                sql_list.append(r"""FROM %s"""%(self.temptableName))
                sql = ''.join(sql_list)

                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_lab""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def check_obsids(self, file_data):
        return utils.filter_nonexisting_values_and_ask(file_data, u'obsid', utils.get_all_obsids(), try_capitalize=False)

    def wqualfield_import_from_csvlayer(self):
        """
        self.csvlayer must contain columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, flow_lpm, comment"
        :return:
        """
        self.prepare_import('temporary_wqualfield')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table

            obsid = self.columns[0][1]
            staff = self.columns[1][1]
            date_time = self.columns[2][1]
            instrument = self.columns[3][1]
            parameter = self.columns[4][1]
            reading_num = self.columns[5][1]
            reading_txt = self.columns[6][1]
            unit = self.columns[7][1]
            depth = self.columns[8][1]
            comment = self.columns[9][1]

            sqlremove = """DELETE FROM "%s" where "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null or "%s" in ('', ' ') or "%s" is null"""%(self.temptableName, obsid, obsid, date_time, date_time, parameter, parameter)#Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(obsid, date_time, parameter, unit, self.temptableName) #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(9, 'w_qual_field', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1: # If cleaning was OK, then copy data from the temporary table to the original table in the db

                if utils.verify_table_exists('zz_staff'):
                    #Add staffs that does not exist in db
                    staffs = set([x[0] for x in utils.sql_load_fr_db("""select distinct staff from %s"""%self.temptableName)[1]])
                    self.staff_import(staffs)

                sql_list = []
                sql_list.append(r"""INSERT OR IGNORE INTO "w_qual_field" (obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment) """)
                sql_list.append(r"""SELECT CAST("%s" as text), """%(obsid))
                sql_list.append(r"""CAST("%s" as text), """%(staff))
                sql_list.append(r"""CAST("%s" as text), """%(date_time))
                sql_list.append(r"""CAST("%s" as text), """%(instrument))
                sql_list.append(r"""CAST("%s" as text), """%(parameter))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(reading_num, reading_num))
                sql_list.append(r"""CAST("%s" as text), """%(reading_txt))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as text) else null end), """%(unit, unit))
                sql_list.append(r"""(case when "%s"!='' then CAST("%s" as double) else null end), """%(depth, depth))
                sql_list.append(r"""CAST("%s" as text) """%(comment))
                sql_list.append(r"""FROM %s"""%(self.temptableName))
                sql = ''.join(sql_list)

                utils.sql_alter_db(sql) # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                self.status = 'True'        # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM w_qual_field""")[1])[0][0] #for the statistics

                self.StatsAfter()
            else:   
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def fieldlogger_import(self):
        self.fieldlogger_staff = None
        result_dict = self.fieldlogger_import_select_and_parse_rows()
        if result_dict == u'cancel':
            self.status = True
            return u'cancel'

        existing_obsids = utils.get_all_obsids()

        typename_preparer_importer = {u'level': (self.fieldlogger_prepare_level_data, self.wlvl_import_from_csvlayer),
                                      u'flow': (self.fieldlogger_prepare_flow_data, self.wflow_import_from_csvlayer),
                                      u'quality': (self.fieldlogger_prepare_quality_and_sample, self.wqualfield_import_from_csvlayer)}

        for typename, obsdict in result_dict.iteritems():
            preparer = typename_preparer_importer[typename][0]
            importer = typename_preparer_importer[typename][1]
            file_data = preparer(copy.deepcopy(obsdict))
            if file_data == u'cancel':
                self.status = True
                return u'cancel'
            elif len(file_data) < 2:
                continue
            filtered_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            if filtered_data == u'cancel':
                self.status = True
                return u'cancel'
            self.send_file_data_to_importer(filtered_data, importer)

        #Import comments
        file_data = self.fieldlogger_prepare_comments_data(copy.deepcopy(result_dict))
        if file_data == u'cancel':
            self.status = True
            return u'cancel'
        filtered_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
        if filtered_data == u'cancel':
            self.status = True
            return u'cancel'
        if len(filtered_data) > 1:
            self.send_file_data_to_importer(filtered_data, self.comments_import_from_csv)
        self.status = True
        self.SanityCheckVacuumDB()

    def fieldlogger_import_select_and_parse_rows(self):
        filename = self.select_files(only_one_file=True, should_ask_for_charset=True)
        if not filename:
            self.status = True
            return u'cancel'

        filename = utils.returnunicode(filename[0])

        #Ask user if the date should be shifted
        question = utils.askuser(u'DateShift', u'User input needed')
        if question.result == u'cancel':
            self.status = True
            return u'cancel'
        shift_date = question.result

        result_dict = {}
        with io.open(filename, 'r', encoding=str(self.charsetchoosen[0])) as f:
            #Skip header
            f.readline()
            result_dict = self.fieldlogger_import_parse_rows(f, shift_date)
        return result_dict

    @staticmethod
    def fieldlogger_import_parse_rows(f, shift_date=[u'0', u'hours']):
        """
        Parses rows from fieldlogger format into a dict
        :param f: File_data, often an open file or a list of rows
        :return: a dict like {typename: {obsid: {date_time: {parameter: value, }}}}

        f must not have a header.
        """

        #Here sample and quality are merged, because they are going to the same place
        typeshortnames_typelongnames = {u's': u'quality',
                                        u'q': u'quality',
                                        u'l': u'level',
                                        u'f': u'flow'}

        result_dict = {}
        for rownr, rawrow in enumerate(f):
            row = utils.returnunicode(rawrow).rstrip(u'\r').rstrip(u'\n')
            if not row:
                continue
            cols = row.split(u';')
            date = cols[1]
            time = cols[2]
            date_time = datestring_to_date(date + u' ' + time)
            date_time = dateshift(date_time, shift_date[0], shift_date[1])
            value = cols[3]
            paramtypename_parameter_unit = cols[4].split(u'.')
            parameter = paramtypename_parameter_unit[1]
            try:
                unit = paramtypename_parameter_unit[2]
            except IndexError:
                unit = u''
            typeshortname = paramtypename_parameter_unit[0]

            obsid_type = cols[0]
            typelongname = obsid_type.split(u'.')[-1]
            obsid = utils.rstrip(u'.' + typelongname, obsid_type)

            if typelongname not in typeshortnames_typelongnames.values():
                if typeshortname in typeshortnames_typelongnames:
                    typelongname = typeshortnames_typelongnames[typeshortname]
                else:
                    utils.pop_up_info("The typename on row: " + row + " could not be parsed. The row will be skipped.")
                    continue

            result_dict.setdefault(typelongname, {}).setdefault(obsid, {}).setdefault(date_time, {})[(parameter, unit)] = value
        return result_dict

    @staticmethod
    def fieldlogger_prepare_level_data(obsdict):
        """
        Produces a filestring with columns "obsid, date_time, meas, comment" and imports it
        :param obsdict: a dict like {obsid: {date_time: {parameter: value}}}
        :return: None
        """
        file_data_list = [[u'obsid', u'date_time', u'meas', u'comment']]
        for obsid, date_time_dict in sorted(obsdict.iteritems()):
            for date_time, param_dict in sorted(date_time_dict.iteritems()):
                printrow = [obsid]
                printrow.append(datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S'))

                try:
                    comment = param_dict.pop((u'comment', u''))
                except KeyError:
                    comment = u''

                meas = None

                for param_unit, value in sorted(param_dict.iteritems()):
                    param, unit = param_unit
                    if param == u'meas':
                        meas = value.replace(u',', u'.')

                if meas is not None:
                    printrow.append(meas)
                    printrow.append(comment)
                    file_data_list.append(printrow)

        return file_data_list

    @staticmethod
    def fieldlogger_prepare_flow_data(obsdict):
        """
        Produces a filestring with columns "obsid, instrumentid, flowtype, date_time, reading, unit, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :return:
        """

        file_data_list = [[u'obsid', u'instrumentid', u'flowtype', u'date_time', u'reading', u'unit', u'comment']]
        instrumentids = utils.get_last_used_flow_instruments()[1]

        for obsid, date_time_dict in sorted(obsdict.iteritems()):
            for date_time, param_dict in sorted(date_time_dict.iteritems()):
                datestring = datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')

                try:
                    comment = param_dict.pop((u'comment', u''))
                except KeyError:
                    comment = u''

                for param_unit, value in sorted(param_dict.iteritems()):
                    param, unit = param_unit

                    flowtype = param
                    reading = value.replace(u',', u'.')

                    instrumentids_for_obsid = instrumentids.get(obsid, None)
                    if instrumentids_for_obsid is None:
                        last_used_instrumentid = u''
                    else:
                        last_used_instrumentid = sorted([(_date_time, _instrumentid) for _flowtype, _instrumentid, _date_time in instrumentids[obsid] if (_flowtype == flowtype)])[-1][1]
                    question = utils.NotFoundQuestion(dialogtitle=u'Submit instrument id',
                                                    msg=u''.join([u'Submit the instrument id for the measurement:\n ', u','.join([obsid, datestring, flowtype])]),
                                                    existing_list=[last_used_instrumentid],
                                                    default_value=last_used_instrumentid,
                                                    combobox_label=u'Instrument id:s in database.\nThe last used instrument for the for the current obsid is prefilled:')
                    answer = question.answer
                    if answer == u'cancel':
                        return u'cancel'
                    instrumentid = utils.returnunicode(question.value)

                    printrow = [obsid, instrumentid, flowtype, datestring, reading, unit, comment]
                    file_data_list.append(printrow)

        return file_data_list

    def fieldlogger_prepare_quality_and_sample(self, obsdict):
        """
        Produces a filestring with columns "obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, depth, comment" and imports it
        :param obsdict:  a dict like {obsid: {date_time: {parameter: value}}}
        :param quality_or_water_sample: Word written at user question: u'quality' or u'water sample'.
        :return:
        """
        file_data_list = [[u'obsid', u'staff', u'date_time', u'instrument', u'parameter', u'reading_num', u'reading_txt', u'unit', u'depth', u'comment']]

        instrumentids = sorted(utils.get_quality_instruments()[1])
        last_used_quality_instruments = utils.get_last_used_quality_instruments()
        w_qual_field_parameters = defs.w_qual_field_parameters()
        existing_parameter_units = [u','.join([utils.returnunicode(v[1]), utils.returnunicode(v[2])]) for v in w_qual_field_parameters]

        asked_instruments = {}
        asked_parameters_units = {}

        for obsid, date_time_dict in sorted(obsdict.iteritems()):
            for date_time, param_dict in sorted(date_time_dict.iteritems()):
                datestring = datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')

                try:
                    comment = param_dict.pop((u'comment', u''))
                except KeyError:
                    comment = u''

                try:
                    depth = param_dict.pop((u'depth', u''))
                except KeyError:
                    depth = u''

                for param_unit, value in sorted(param_dict.iteritems()):
                    parameter_shortname, unit = param_unit
                    parameter = None

                    #Get the parameter name from the shortname and unit
                    if (parameter_shortname, unit) in asked_parameters_units:
                        parameter, unit = asked_parameters_units[(parameter_shortname, unit)]
                    else:
                        #Try to match the parameter short names
                        parameter_unit = [(_parameter, _unit) for _shortname, _parameter, _unit in w_qual_field_parameters if (parameter_shortname, unit) == (_shortname, _unit)]
                        #If that didn't work, try to match the shortname to parameter name instead.
                        if not len(parameter_unit) == 1:
                            parameter_unit = [(_parameter, _unit) for _shortname, _parameter, _unit in w_qual_field_parameters if (parameter_shortname, unit) == (_parameter, _unit)]

                        if len(parameter_unit) == 1:
                            parameter, unit = parameter_unit[0]
                        #If that didn't work either, ask the user for it.
                        else:
                            question = utils.NotFoundQuestion(dialogtitle=u'Submit parameter and unit',
                                                           msg=u'The parameter and unit was not found in db\n\nSubmit parameter and unit separated by comma for the row:\n' + u', '.join([obsid, datestring, parameter_shortname, unit]) + u'\n\nIt will be used for the rest of the water quality imports\nwith the same parameter, unit combination.',
                                                           existing_list=existing_parameter_units)
                            answer = question.answer
                            if answer == u'cancel':
                                return u'cancel'
                            parameter, unit = utils.returnunicode(question.value).split(u',')
                        asked_parameters_units[(parameter_shortname, unit)] = (parameter, unit)

                    staff = self.ask_for_staff()
                    if staff == u'cancel':
                        return u'cancel'

                    instrument = asked_instruments.get((parameter, unit), None)
                    if instrument is None:
                        current_last_used_instrument = u''
                        try:
                            current_last_used_instrument = utils.returnunicode([_instrument for _unit, _staff, _instrument, _date_time in last_used_quality_instruments[parameter] if _staff == staff and _unit == unit][0])
                        except KeyError:
                            pass
                        except IndexError:
                            pass
                        except Exception, e:
                            utils.MessagebarAndLog.warning(bar_msg=u'Import warning!, see Log Message Panel', log_msg=u'Getting instruments from db failed: ' + str(e))
                            pass

                        question = utils.NotFoundQuestion(dialogtitle=u'Submit instrument id',
                                                       msg=u'Submit the instrument id for the water quality measurement:\n' + u', '.join([obsid, datestring, parameter, unit]) + u'\n\nIt will be used for the rest of the water quality imports\nfor the current parameter and unit.',
                                                       existing_list=instrumentids,
                                                       combobox_label=u'Instrument id:s in database.\nThe last used instrument for the for the current staff, parameter and unit is prefilled:',
                                                       default_value=current_last_used_instrument)
                        answer = question.answer
                        if answer == u'cancel':
                            return u'cancel'
                        instrument = utils.returnunicode(question.value)
                        if instrument not in instrumentids:
                            instrumentids.append(instrument)
                    asked_instruments[(parameter, unit)] = instrument

                    reading_num = value.replace(u',', u'.')
                    reading_txt = reading_num

                    printrow = [obsid, staff, datestring, instrument, parameter, reading_num, reading_txt, unit, depth, comment]
                    file_data_list.append(printrow)

        return file_data_list

    def fieldlogger_prepare_comments_data(self, typesdict):
        file_data_list = [[u'obsid', u'date_time', u'comment', u'staff']]

        for typename, obsdict in sorted(typesdict.iteritems()):
            for obsid, date_time_dict in sorted(obsdict.iteritems()):
                for date_time, param_dict in sorted(date_time_dict.iteritems()):
                    try:
                        datestring = datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')
                    except TypeError:
                        utils.pop_up_info("datetime: " + str(date_time))
                        return

                    comment = ''

                    #If there is no comment, continue to next date_time
                    try:
                        comment = param_dict.pop((u'comment', u''))
                    except KeyError:
                        continue

                    #If there was more than the comment parameter, the comment should not go to notes.
                    if len(param_dict) > 0:
                        continue

                    staff = self.ask_for_staff()
                    if staff == u'cancel':
                        return u'cancel'

                    printrow = [obsid, datestring, comment, staff]
                    file_data_list.append(printrow)
        return file_data_list

    def ask_for_staff(self):
        existing_staff = defs.staff_list()[1]

        if self.fieldlogger_staff is None:
            question = utils.NotFoundQuestion(dialogtitle=u'Submit field staff',
                                           msg=u'Submit the field staff who made the FieldLogger measurements.\nIt will be used for the rest of the import',
                                           existing_list=existing_staff)
            answer = question.answer
            if answer == u'cancel':
                return u'cancel'

            self.fieldlogger_staff = utils.returnunicode(question.value)
        return self.fieldlogger_staff

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
                utils.pop_up_info("Creating csvlayer for " + str(importer) + " failed!")
                return
            self.csvlayer = csvlayer
            importer()

    def comments_import_from_csv(self):
        if not utils.verify_table_exists('comments'):
            qgis.utils.iface.messageBar().pushMessage("Table comments did not exist. Stand alone comments not imported")
            return

        self.prepare_import('temporary_comments')
        if self.csvlayer:
            self.qgiscsv2sqlitetable() #loads qgis csvlayer into sqlite table
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]#Load column names from sqlite table

            obsid = self.columns[0][1]
            date_time = self.columns[1][1]
            comment = self.columns[2][1]
            staff = self.columns[3][1]

            sqlremove = """DELETE FROM "%s" where "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null or "%s"='' or "%s"=' ' or "%s" is null"""%(self.temptableName, obsid, obsid, obsid, date_time, date_time, date_time, comment, comment, comment, staff, staff, staff)  #Delete empty records from the import table!!!
            sqlNoOfdistinct = """SELECT Count(*) FROM (SELECT DISTINCT "%s", "%s", "%s", "%s" FROM %s)"""%(obsid, date_time, comment, staff,self.temptableName)  #Number of distinct data posts in the import table
            cleaningok = self.multiple_field_duplicates(4, 'comments', sqlremove, 'obs_points', sqlNoOfdistinct)
            if cleaningok == 1:

                #Add staffs that does not exist in db
                if utils.verify_table_exists('zz_staff'):
                    staffs = set([x[0] for x in utils.sql_load_fr_db("""select distinct staff from %s"""%self.temptableName)[1]])
                    self.staff_import(staffs)

                # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                sqlpart1 = """INSERT OR IGNORE INTO "comments" (obsid, date_time, comment, staff) """
                sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as text), CAST("%s" as text) FROM %s"""%(obsid, date_time, comment, staff, self.temptableName)
                sql = sqlpart1 + sqlpart2
                utils.sql_alter_db(sql)

                self.status = 'True'  # Cleaning was OK and import perfomed!!
                self.recsafter = (utils.sql_load_fr_db("""SELECT Count(*) FROM comments""")[1])[0][0] #for the statistics
                self.StatsAfter()
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed
            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def staff_import(self, staff):
        """ Inserts initials if they don't exist in table staff
        :param initials: a string with initials, or a list of strings with initials
        :return:
        """
        name = u''

        if isinstance(staff, basestring):
            staff = [staff]

        for _staff in staff:
            _staff = utils.returnunicode(_staff)
            existing_staff = [utils.returnunicode(x) for x in defs.staff_list()[1]]
            if _staff in existing_staff:
                continue
            else:
                sql = u"""insert into "zz_staff" (staff, name) VALUES ("%s", "%s");"""%(_staff, name)
                utils.sql_alter_db(sql.encode('utf-8'))

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

    def multiple_field_duplicates(self, NoCols, GoalTable, sqlremove, MajorTable, sqlNoOfdistinct, ):  #For secondary tables linking to obs_points and obs_lines: Sanity checks and removes duplicates
        """perform some sanity checks of the imported data and removes duplicates and empty records"""
        if len(self.columns)<NoCols: 
            qgis.utils.iface.messageBar().pushMessage("Import failure","Import file must have at least " + str(NoCols) + " columns!\nCheck your data and try again.",2)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            self.status = 'False'
            return 0 #only to stop function
        else:    #If correct number of columns, remove empty records
            if len(self.columns) > NoCols:#Here is where the user may interrupt if there are more columns than needed for w_levels
                ManyColsQuestion = utils.askuser("YesNo", """Please note!\nThere are %s columns in your csv file which may be perfectly fine if the first %s corresponds to those needed.\n\nDo you want to proceed with the import?"""%(str(len(self.columns)),str(NoCols)),"Warning!")
                if ManyColsQuestion.result == 0:      # if the user wants to abort
                    self.status = 'False'
                    PyQt4.QtGui.QApplication.restoreOverrideCursor()
                    return 0   # return simply to stop this function
            utils.sql_alter_db(sqlremove)
            #Then verify that obsid exists in MajorTable and perform statistics
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

    def parse_wells_file(self):
        """ Opens a wells file and returns a parsed dict
        :return: A dict like {obsid: {typename: [parameter, unit]}}
        """
        try:
            path = self.select_files(only_one_file=True)[0]
        except IndexError:
            return u'cancel'
        charset = self.charsetchoosen

        if not path:
            return None
        with io.open(path, u'r', encoding=str(charset[0])) as f:
            obsid_dict = self.wells_parse_rows(f)
        return obsid_dict

    @staticmethod
    def wells_parse_rows(f):
        """
        Parses rows from a wells file
        :return: A dict like {obsid: {typename: [parameter, unit]}}
        """
        obsid_dict = {}
        start_import = False
        for rawrow in f:
            row = utils.returnunicode(rawrow).rstrip(u'\r').rstrip(u'\n')

            if row == u'NAME;SUBNAME;LAT;LON;INPUTFIELD':
                start_import = True
                continue

            if not start_import:
                continue

            cols = row.split(u';')
            obsid_type = cols[1]
            obsid_type_splitted = obsid_type.split(u'.')

            if len(obsid_type_splitted) < 2:
                utils.pop_up_info("The typename and obsid on row: " + row + " could not be read. It will be skipped.")
                continue
            typename = obsid_type.split(u'.')[-1]
            obsid = utils.rstrip(u'.' + typename, obsid_type)
            parameters = cols[4].split(u'|')

            for parameter in parameters:
                type_parameter_unit =  parameter.split(u'.')
                parameter = type_parameter_unit[1]
                try:
                    unit = type_parameter_unit[2]
                except IndexError:
                    unit = u''

                obsid_dict.setdefault(obsid, {}).setdefault(typename, []).append((parameter, unit))
        return obsid_dict

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
                
    def qgiscsv2sqlitetable(self): # general importer
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'."""
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
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names
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


class wlvlloggimportclass():
    """ Note, thes class is a quickfix and have been incorporated into the multi-import class as wlvllogg_import"""
    def __init__(self):
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.csvpath = ''
        self.temptableName = 'temporary_logg_lvl'
        self.status = 'False' #Changed to True if uploadQgisVectorLayer succeeds
        self.columns=[]
        self.charsetchoosen = ('','')

        # Find obsid for the selected object
        self.obsid = utils.getselectedobjectnames(qgis.utils.iface.activeLayer())     #A list of length 1! To get the acutal ID, call self.obsid[0]
        # Import the csv file as a ogr csvlayer
        self.csvlayer = self.selectcsv()
        if self.csvlayer:
            # upload the ogr csvlayer to splite db
            self.uploadLoggerdataToSplite()    # Calling similar function as uploadQgisVectorLayer
            # perform some cleaning of imported data
            cleaningok = self.cleanuploggerdata() # returns 1 if cleaning went well

            #HERE IS WHERE DATA IS TRANSFERRED TO w_levels_logger
            if cleaningok == 1: # If cleaning was OK, then perform the import
                self.goalcolumns = utils.sql_load_fr_db("""PRAGMA table_info(w_levels_logger)""")[1]
                if len(self.columns) == 5: #No conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[3][1],self.columns[0][1],self.columns[1][1],self.columns[2][1])     
                    sqlpart3 = """ FROM %s"""%(self.temptableName)    
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    utils.sql_alter_db(sql)     
                    #utils.pop_up_info(sql, "debug") #debug                
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                elif len(self.columns) ==6: #Including conductivity data
                    sqlpart1 = """INSERT OR IGNORE INTO "w_levels_logger" ("%s", "%s", "%s", "%s", "%s") """%(self.goalcolumns[0][1],self.goalcolumns[1][1],self.goalcolumns[2][1],self.goalcolumns[3][1],self.goalcolumns[4][1])     # 'OR IGNORE' SIMPLY SKIPS ALL THOSE THAT WOULD CAUSE DUPLICATES - INSTEAD OF THROWING BACK A SQLITE ERROR MESSAGE
                    sqlpart2 = """SELECT CAST("%s" as text), CAST("%s" as text), CAST("%s" as double), CAST("%s" as double), CAST("%s" as double)"""%(self.columns[4][1],self.columns[0][1],self.columns[1][1],self.columns[2][1],self.columns[3][1])     
                    sqlpart3 = """ FROM %s"""%(self.temptableName)    
                    sql = sqlpart1 + sqlpart2 + sqlpart3
                    utils.sql_alter_db(sql)     
                    #utils.pop_up_info(sql, "debug") #debug
                    self.status = 'True'        # Cleaning was OK and import perfomed!!

                #Statistics
                self.RecordsAfter = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
                NoExcluded = self.RecordsToImport[0][0] - (self.RecordsAfter[0][0] - self.RecordsBefore[0][0])
                if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were not imported from the file since they would cause duplicates in the database."""%NoExcluded)
                else:  # If some of the imported data already existed in the database, let the user know
                    utils.pop_up_info("""In total %s measurements were imported."""%(self.RecordsAfter[0][0] - self.RecordsBefore[0][0]))
            elif cleaningok == 0 and not(len(self.columns)==5 or len(self.columns)==6):
                utils.pop_up_info("Import file must have exactly three columns!\n(Or four if conductivity is also measured.)", "Import Error")
                self.status = 'False'
            else:
                self.status = 'False'       #Cleaning was not ok and status is false - no import performed

            utils.sql_alter_db("DROP table %s"%self.temptableName) # finally drop the temporary table
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            sanity = utils.askuser("YesNo","""It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""",'Vacuum the database?')
            if sanity.result == 1:
                PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
                utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
        
    def selectcsv(self):     
        """Select the csv file"""
        # USER MUST ALSO TELL WHAT CHARSET TO USE!! 
        try:#MacOSX fix2
            localencoding = locale.getdefaultlocale()[1]
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, normally\niso-8859-1, utf-8, cp1250 or cp1252.\n\nOn your computer " + localencoding + " is default.",PyQt4.QtGui.QLineEdit.Normal,locale.getdefaultlocale()[1])
        except:
            self.charsetchoosen = PyQt4.QtGui.QInputDialog.getText(None, "Set charset encoding", "Give charset used in the file, default charset on normally\nutf-8, iso-8859-1, cp1250 or cp1252.",PyQt4.QtGui.QLineEdit.Normal,'utf-8')
        if self.charsetchoosen and not (self.charsetchoosen[0]==0 or self.charsetchoosen[0]==''):
            self.csvpath = PyQt4.QtGui.QFileDialog.getOpenFileName(None, "Select File","","csv (*.csv)")
            if not self.csvpath or self.csvpath=='': 
                return
            else:
                csvlayer = QgsVectorLayer(self.csvpath, "temporary_csv_layer", "ogr")
                if not csvlayer.isValid():
                    utils.pop_up_info("Impossible to Load File in QGis:\n" + str(self.csvpath))
                    return False
                #Set Layer Encoding
                csvlayer.setProviderEncoding(str(self.charsetchoosen[0]))
                return csvlayer
        
    def uploadLoggerdataToSplite(self):
        self.status = 'False'
        #Verify if temptableName already exists in DB
        ExistingNames=utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]
        #Propose user to automatically rename DB
        for existingname in ExistingNames:  #this should only be needed if an earlier import failed
            if str(existingname[0]) == str(self.temptableName):
                #utils.pop_up_info("found it")       #DEBUGGING
                reponse=PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the\ncurrent DataBase. This could indicate a failure during last import.\nPlease verify that your w_levels table contains all expected data\nand then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a\ntemporary table '%s_2' in database?'''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
                if reponse==PyQt4.QtGui.QMessageBox.Yes:
                    self.temptableName='%s_2'%self.temptableName
                else:
                    return None
                  
        #Get fields in loaded csv-file with corresponding types
        provider=self.csvlayer.dataProvider()       # The loaded csv-file
        fields=[]
        fieldsNames=[]

        for name in provider.fields(): 
            fldName=unicode(name.name()).replace("'"," ").replace('"'," ")
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName='%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool,PyQt4.QtCore.QVariant.Int,QtCore.QVariant.LongLong,PyQt4.QtCore.QVariant.UInt,PyQt4.QtCore.QVariant.ULongLong): # field type is integer
                fldType='integer'
            elif fldType==PyQt4.QtCore.QVariant.Double: # field type is double
                fldType='real'
            else: # field type is not recognized by SQLITE
                fldType=fldTypeName
            fields.append(""" "%s" %s """%(fldName,fldType))
            fieldsNames.append(fldName.upper())
        
        #Create new table in DB
        fields=','.join(fields) 
        fields = ''.join([x for x in fields if ord(x) < 128])    # Just get rid of all non-ascii, the column names are not important anyway
        sql = """CREATE table "%s" (%s)"""%(self.temptableName, fields)
        #utils.pop_up_info(sql)      # debugging
        utils.sql_alter_db(sql) #NO PKUID, Number of fields exactly the same as imported csv file
        #create connection and cursor
        dbpath = QgsProject.instance().readEntry("Midvatten","database")
        conn = sqlite.connect(dbpath[0],detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        curs = conn.cursor()
        curs.execute("PRAGMA foreign_keys = ON")    #Foreign key constraints are disabled by default (for backwards compatibility), so must be enabled separately for each database connection separately.
        # Retreive every feature 
        for feature in self.csvlayer.getFeatures(): 
            # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
            # show all attributes and their values
            values_perso=[]
            for attr in feature.attributes():
                values_perso.append(attr) # attr is supposed to be unicode and should be kept like that, sometimes though it ends up being a byte string, do not know why....
            
            #Create line in DB table
            if len(fields)>0:   # NOTE CANNOT USET utils.sql_alter_db() SINCE THE OPTION OF SENDING 2 ARGUMENTS TO .execute IS USED BELOW
                curs.execute("""INSERT INTO "%s" VALUES (%s)"""%(self.temptableName,','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso])) # NO PKUID
                self.status = 'True'
            else: #no attribute Datas
                utils.pop_up_info("No data found in table!!")
                self.status = 'False'
        conn.commit()   # This one is absolutely needed when altering a db, python will not really write into db until given the commit command
        curs.execute("PRAGMA foreign_keys = OFF")
        curs.close()
        conn.close()

    def cleanuploggerdata(self):
        """performs some sanity checks of the imported data and removes duplicates and empty records"""
        #First load column names
        self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
        if len(self.columns)==3 or len(self.columns)==4:  #only if correct number of columns!!
            #And then simply remove all empty records
            for column in self.columns:      #This method is quite cruel since it removes every record where any of the fields are empty
                utils.sql_alter_db("""DELETE FROM "%s" where "%s" in('',' ') or "%s" is null"""%(self.temptableName,column[1],column[1]))
            #THE METHOD ABOVE NEEDS REVISON

            #Fix date_time format from "yyyy/mm/dd hh:mm:ss" to "yyyy-mm-dd hh:mm:ss"
            utils.sql_alter_db("""UPDATE "%s" SET "%s" = REPLACE("%s",'/','-')"""%(self.temptableName,str(self.columns[0][1]),str(self.columns[0][1])))
            # Add obsid column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN obsid text"""%self.temptableName)
            utils.sql_alter_db("""UPDATE "%s" SET obsid = "%s" """%(self.temptableName,self.obsid[0]))
            # Add level_masl column and fill with data
            utils.sql_alter_db("""ALTER table "%s" ADD COLUMN level_masl double"""%self.temptableName)
            utils.sql_alter_db("""UPDATE "%s" SET level_masl = -999-"%s" """%(self.temptableName,self.columns[1][1]))
            #Then reload self.columns since two new columns are added!
            self.columns = utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName )[1]
            
            #Some statistics
            self.RecordsBefore = utils.sql_load_fr_db("""SELECT Count(*) FROM w_levels_logger""")[1]
            self.RecordsToImport = utils.sql_load_fr_db("""SELECT Count(*) FROM (SELECT DISTINCT "%s" FROM %s)"""%(self.columns[0][1],self.temptableName))[1]
            self.RecordsInFile = utils.sql_load_fr_db("""SELECT Count(*) FROM %s"""%self.temptableName)[1]
            utils.pop_up_info("The import file has " + str(self.RecordsInFile[0][0]) + " non-empty records\n" + "and among these are found " + str(self.RecordsInFile[0][0] - self.RecordsToImport[0][0]) + " duplicates.")   # debug

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


class FieldloggerImport(PyQt4.QtGui.QMainWindow, import_fieldlogger_ui_dialog):
    def __init__(self, parent, settingsdict={}):
        self.status = False
        self.iface = parent
        self.settingsdict = settingsdict
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)  # Required by Qt4 to initialize the UI

        self.status = True
        self.stored_presets = OrderedDict()

        #self.observations = self.select_file_and_parse_rows()
        #if self.observations == u'cancel':
        #    self.status = True
        #    return u'cancel'

        self.observations = [{u'sublocation': u'a.1', u'date_time': datestring_to_date(u'2016-01-01'), u'parametername': u'Aveflow.m3s', u'value': 123},
                             {u'sublocation': u'b.c.2', u'date_time': datestring_to_date(u'2016-01-01'), u'parametername': u'Aveflow.m3s', u'value': 123},
                             {u'sublocation': u'b.c.2.3', u'date_time': datestring_to_date(u'2016-01-01'), u'parametername': u'Aveflow.m3s', u'value': 123},
                             {u'sublocation': u'b.d.2.3', u'date_time': datestring_to_date(u'2016-01-01'), u'parametername': u'Aveflow.m3s', u'value': 123},
                             {u'sublocation': u'b.d.2.3', u'date_time': datestring_to_date(u'2016-01-01'), u'parametername': u'Temp.grC', u'value': 123}]


        #Filters and general settings
        self.settings_with_own_loop = []
        self.settings = []
        self.settings.append(StaffQuestion())
        self.settings.append(DateShiftQuestion())
        self.settings.append(DateTimeFilter()) #This includes a checkbox for "include only latest
        self.settings_with_own_loop.append(ObsidFilter())

        sublocation_groups = self.sublocation_to_groups([observation[u'sublocation'] for observation in self.observations], delimiter=u'.')
        for _length, sublocation_group in sorted(sublocation_groups.iteritems()):
            self.settings.append(SublocationFilter(sublocation_group))

        for setting in self.settings:
            self.add_row(setting.widget)

        for setting in self.settings_with_own_loop:
            self.add_row(setting.widget)

        self.add_line()

        #self.main_vertical_layout.addStretch()
        #self.main_vertical_layout.insertStretch(-1)
        #self.add_line()

        self.parameter_names = list(set([observation[u'parametername'] for observation in self.observations]))
        self.parameter_imports = OrderedDict()
        for parametername in self.parameter_names:
            param_import_obj = ImportMethodChoser(parametername, self.parameter_names, self.connect)
            self.parameter_imports[parametername] = param_import_obj
            self.add_row(param_import_obj.widget)

        self.main_vertical_layout.addStretch(1)
        #self.add_row(self.parameters_layout())




        #The parameter


        #Parameters
        #The parameters should be stored so that they are easy to access when the import is started.
        #Should the settings be stored in qt-variables, i.e. the fields themselves, or should it be local variables in dicts for example.

        #Maybe it's best to create an object for each one and store the values in the fields inside the objects. The import method field would then be
        #connected to a method inside the object itself that would alter the layout of itself by adding the neccessary fields.
        #parameter_names = sorted(set([observation[u'parameter'] for observation in self.observations]))

        #Here a stored parameter setup connected to each parameter_name is prefilled.

        #for parameter_name in parameter_names:
        #    self.parameters_layout.append(self.parameter_setting(parameter_name))

        #This should be an
        #self.parameter_imports = OrderedDict()

        #Connect button to start import.
        #User should press start import which will filter the data, check obsids, split the import into all import types (w_levels, w_flow, comment, w_qual_field)
        # Instrument id should be checked for in the needed imports.

        self.start_import_button = PyQt4.QtGui.QPushButton(u'Start import')
        self.gridLayout_buttons.addWidget(self.start_import_button, 0, 0)
        self.connect(self.start_import_button, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.start_import(self.observations))

        self.show()

    def select_file_and_parse_rows(self):
        filename = self.select_files(only_one_file=True, should_ask_for_charset=True)
        if not filename:
            self.status = True
            return u'cancel'

        filename = utils.returnunicode(filename[0])

        observations = {}
        with io.open(filename, 'r', encoding=str(self.charsetchoosen[0])) as f:
            #Skip header
            f.readline()
            observations = self.parse_rows(f)
        return observations

    @staticmethod
    def parse_rows(f):
        """
        Parses rows from fieldlogger format into a dict
        :param f: File_data, often an open file or a list of rows
        :return: a list of dicts like [{date_time: x, sublocation: y, parametername: z, value: o}, ...]

        #If the observations instead were stored like a list of dicts:
        [{date_time: x, sublocation: y, parametername: z, value: o}, ]
        it would be very easy to change names, access data, resort data and so fourth.
        Filtering data would also be VERY easy. Obsid filter would be as simple as obs = [obs for obs in observations where x['date_time' < x]

        Extracting the data would be VERY easy for the importer functions as well. depth = observations.get(depth, None)
        or:
        instrumentid = observations.get(instrumentid, None)
        if instrumentid is None:
            instrumentid = observations.get(instrument, None)
        if instrumentid is None:
            ask_for_instrument_id()

        Negative: It will be a lot of looping through the structure.
        solution: This could be solved by making lookup dicts directly to the observations. But it's probably never needed.



        f must not have a header.
        """
        observations = []
        for rownr, rawrow in enumerate(f):
            observation = {}
            row = utils.returnunicode(rawrow).rstrip(u'\r').rstrip(u'\n')
            if not row:
                continue
            cols = row.split(u';')
            observation[u'sublocation'] = cols[0]
            date = cols[1]
            time = cols[2]
            observation[u'date_time'] = datestring_to_date(u' '.join([date, time]))
            observation[u'value'] = cols[3]
            observation[u'parametername'] = cols[4]
        return observations

    def add_row(self, a_widget):
        """
        :param: a_widget:
        """
        self.main_vertical_layout.addWidget(a_widget)

    def add_line(self):
        """ just adds a line"""
        #horizontalLineWidget = PyQt4.QtGui.QWidget()
        #horizontalLineWidget.setFixedHeight(2)
        #horizontalLineWidget.setSizePolicy(PyQt4.QtGui.QSizePolicy.Expanding, PyQt4.QtGui.QSizePolicy.Fixed)
        #horizontalLineWidget.setStyleSheet(PyQt4.QtCore.QString("background-color: #c0c0c0;"));
        line = PyQt4.QtGui.QFrame()
        #line.setObjectName(QString::fromUtf8("line"));
        line.setGeometry(PyQt4.QtCore.QRect(320, 150, 118, 3))
        line.setFrameShape(PyQt4.QtGui.QFrame.HLine);
        line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken);
        self.add_row(line)

    @staticmethod
    def sublocation_to_groups(sublocations, delimiter=u'.'):
        """
        This method splits sublocation using a splitter, default to u'.'. Each list position is grouped to lists
         containing all distinct values. It's finally stored in a dict with the lenght of the splitted group as key.
        :param: sublocations: A list of sublocations, ex: [u'c', u'a.1', u'a.2', u'b.1.1']
        :return: a dict like {1: [set(distinct values)], 2: [set(distinct values)}, set(), set()], ...)
        """
        sublocation_groups = {}
        for sublocation in sublocations:
            splitted = sublocation.split(delimiter)
            length = len(splitted)
            for index in xrange(length):
                #a dict like {1: [set()], 2: [set(), set()], ...}
                sublocation_groups.setdefault(length, [set()for i in xrange(length)])[index].add(splitted[index])
        return sublocation_groups

    def start_import(self, observations):
        """

        :param date_time_to_from:
        :param sublocation_filter_types:
        :return:
        """

        #Filter and alter data
        filtered_observations = []
        for observation in observations:
            for setting in self.settings:
                altered_observation =  setting.alter_data(observation)
                if altered_observation == u'cancel':
                    return u'cancel'
                elif altered_observation is not None:
                    filtered_observations.append(filtered_observations)
        observations = filtered_observations

        for setting in self.settings_with_own_loop:
            observations = setting.alter_data(observations)
            if observations == u'cancel':
                return u'cancel'

        print(observations)
        return None
        #All parameter could be stored as self.parameter_settings and be used just like the filters
        for parameter_setting in self.parameter_settings:
            observations = parameter_setting.alter_data(observations)

        ordered_under_import_methods = {}
        for observation in observations:
            import_method = observation.get(u'import_method', None)
            if import_method is not None:
                ordered_under_import_methods.setdefault(import_method, []).append(observation)

        # Next step is to send parts of the observations to it's specific importer.

    def get_stored_presets(self, settingsdict, stored_presets):
        #Populate using stored settings:
        #The stored settings should probably be stored like this:
        #stored = parameter_name:parametername|import_method:stored_method| ... the rest should depend on the import_method, like:
        #Aveflow.m3|import_method:w_flow|parameter:Aveflow|unit:m3/
        #
        # Presetting should then be done like:
        parameter_presets_string = utils.returnunicode(settingsdict[u'fieldlogger_import_parameter_presets'])
        parameter_presets = parameter_presets_string.split(u'/')

        for parameter_preset in parameter_presets:
            presets = parameter_preset.split(u'|')
            parametername = presets[0]
            stored_presets[parametername] = OrderedDict()

            for attrs in presets[1:]:
                attr, value = attrs.split(u':')
                stored_presets[parametername][attr] = value

    def set_parameters_using_stored_presets(self, stored_presets, parameter_imports):
        stored_presets = copy.deepcopy(stored_presets)
        for parameter_import in parameter_imports:
            preset = stored_presets.get(parameter_import.parameter_name, None)
            if preset is None:
                continue

            parameter_import.import_method = preset[u'import_method']
            del preset[u'import_method']
            parameter_widget = parameter_import.parameter_widget
            if parameter_widget is None:
                continue

            for attr, val in preset.iteritems():
                try:
                    setattr(parameter_widget, attr, val)
                except:
                    pass

    def update_stored_presets(self, stored_settings, parameter_imports):
        for parameter_import in parameter_imports:
            if parameter_import.import_method is None:
                continue

            attrdict = stored_settings.get(parameter_import.parameter_name, OrderedDict())
            attrdict[u'import_method'] = parameter_import.import_method

            parameter_widget = parameter_import.parameter_widget
            if parameter_widget is None:
                continue

            for attr, value in parameter_widget.get_settings().iteritems():
                attrdict[attr] = value

    def save_stored_presets(self, settingsdict, stored_settings):
        stored_settings = utils.returnunicode(stored_settings, keep_containers=True)
        presets_list = []
        for parameter_name, attrs in stored_settings.iteritems():
            paramlist = [parameter_name]
            paramlist.extend([u':'.join([attr, value]) for attr, value in attrs.iteritems()])
            presets_list.append(u'|'.join(paramlist))

        preset_string = u'/'.join(presets_list)
        settingsdict[u'fieldlogger_import_parameter_presets'] = preset_string










class RowEntry(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QHBoxLayout()
        self.widget.setLayout(self.layout)

class RowEntryGrid(object):
    def __init__(self):
        self.widget = PyQt4.QtGui.QWidget()
        self.layout = PyQt4.QtGui.QGridLayout()
        self.widget.setLayout(self.layout)



class ObsidFilter(RowEntry):
    def __init__(self):
        super(ObsidFilter, self).__init__()
        self.try_capitalize_checkbox = PyQt4.QtGui.QCheckBox(u"Obsid filter: Try capitalize obsids")
        self.layout.addWidget(self.try_capitalize_checkbox)
        self.layout.addStretch()

    def alter_data(self, observations):
        existing_obsids = utils.get_all_obsids()

        for observation in observations:
            observation[u'obsid'] = observation[u'sublocation'].split(u'.')[0]

        obsids = list(sorted(set([(observation[u'obsid'], observation[u'obsid']) for observation in observations])))

        answer = utils.filter_nonexisting_values_and_ask([[u'old_obsid', u'new_obsid'], obsids], u'new_obsid', existing_obsids, self.try_capitalize_checkbox.isChecked())
        if answer == u'cancel':
            return answer

        if answer is not None:
            if isinstance(answer, (list, tuple)):
                if len(answer) > 1:
                    obsid_rename_dict = dict([(old_obsid_new_obsid[0], old_obsid_new_obsid[1]) for old_obsid_new_obsid in answer[1:]])

                    #Filter and rename obsids
                    observations = [observation.update({u'obsid': obsid_rename_dict.get(observation[u'obsid'], None)})
                                    for observation in observations if obsid_rename_dict.get(observation[u'obsid'], None) is not None]

        if len(observations) == 0:
            utils.MessagebarAndLog.warning(bar_msg=u'No observations imported, see log message panel',
                                           log_msg=u'No observations returned from obsid verification.' +
                                                   u'Were all skipped?')
            return u'cancel'
        return observations


class StaffQuestion(RowEntry):
    def __init__(self):
        super(StaffQuestion, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Staff who did the measurement')
        self.existing_staff_combobox = PyQt4.QtGui.QComboBox(self.widget)
        self.existing_staff_combobox.setEditable(True)
        self.existing_staff_combobox.addItem(u'')
        existing_staff = sorted(defs.staff_list()[1])
        self.existing_staff_combobox.addItems(existing_staff)

        for widget in [self.label, self.existing_staff_combobox]:
            self.layout.addWidget(widget)
        self.layout.addStretch()

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        observation[u'staff'] = self.existing_staff_combobox.currentText()
        return observation


class DateShiftQuestion(RowEntry):
    def __init__(self):
        super(DateShiftQuestion, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Shift dates, supported format ex. "-1 hours":')
        self.dateshift_lineedit = PyQt4.QtGui.QLineEdit()
        self.dateshift_lineedit.setText(u'0 hours')

        for widget in [self.label, self.dateshift_lineedit]:
            self.layout.addWidget(widget)
        self.layout.addStretch()

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        shift_specification = self.dateshift_lineedit.text()

        step_steplength = shift_specification.split(u' ')
        failed = False

        bar_msg = u'Dateshift specification wrong format, se log message panel'
        log_msg = (u'Dateshift specification must be made using format ' +
                    '"step step_length", ex: "0 hours", "-1 hours", "-1 days" etc.\n' +
                    'Supported step lengths: microseconds, milliseconds, seconds, ' +
                    'minutes, hours, days, weeks.')

        if len(step_steplength) != 2:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            return u'cancel'
        try:
            step = float(step_steplength[0])
            steplength = step_steplength[1]
        except:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            return u'cancel'

        test_shift = dateshift('2015-02-01', step, steplength)
        if test_shift == None:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)
            return u'cancel'

        observation[u'date_time'] = dateshift(observation[u'date_time'], step, steplength)
        return observation


class DateTimeFilter(RowEntry):
    def __init__(self):
        super(DateTimeFilter, self).__init__()
        self.label = PyQt4.QtGui.QLabel(u'Import data from: ')
        self.from_datetimeedit = PyQt4.QtGui.QDateTimeEdit(datestring_to_date(u'1900-01-01 00:00:00'))
        self.label_to = PyQt4.QtGui.QLabel(u'to: ')
        self.to_datetimeedit = PyQt4.QtGui.QDateTimeEdit(datestring_to_date(u'2099-12-31 23:59:59'))

        for widget in [self.label, self.from_datetimeedit, self.label_to, self.to_datetimeedit]:
            self.layout.addWidget(widget)
        self.layout.addStretch()

    def alter_datas(self, observations):

        observations = [observation for observation in observations if self.alter_data(observation) is not None]

        if not observations:
            utils.MessagebarAndLog.warning(bar_msg=u'Datetime filter resulted in no remaining observations. No import done')
            return u'cancel'
        return observations

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        _from = self.from_datetimeedit.dateTime().toPyDateTime()
        _to = self.to_datetimeedit.dateTime().toPyDateTime()
        if not _from and not _to:
            return observation
        if _from and _to:
            if _from < observation[u'date_time'] < _to:
                return observation
        elif _from:
            if _from < observation[u'date_time']:
                return observation
        elif _to:
            if observation[u'date_time'] < _to:
                return observation
        return None


class SublocationFilter(RowEntry):
    def __init__(self, sublocation_list):
        """
        a list like [set(distinct values), set(distinct values), set(), ...]
        :param sublocation_group:
        """
        super(SublocationFilter, self).__init__()
        self.label = PyQt4.QtGui.QLabel()
        self.label.setText(u'Sublocation filter: ')
        self.layout.addWidget(self.label)
        self.filters = []
        for idx, inner_set in enumerate(sublocation_list):
            self.filters.append(PyQt4.QtGui.QListWidget())
            self.filters[-1].setSelectionMode(PyQt4.QtGui.QAbstractItemView.MultiSelection)
            self.filters[-1].addItems(sorted(inner_set))
            self.layout.addWidget(self.filters[-1])
            if idx != len(sublocation_list) - 1:
                dotlabel = PyQt4.QtGui.QLabel(u'.')
                self.layout.addWidget(dotlabel)
        self.layout.addStretch()

    def alter_datas(self, observations):
        remaining_observations = []
        for observation in observations:
            checked_observation = self.alter_data(observation)
            if checked_observation is not None:
                remaining_observations.append(checked_observation)
        return remaining_observations

    def alter_data(self, observation):
        observation = copy.deepcopy(observation)
        sublocation = observation[u'sublocation'].split(u'.')
        if len(sublocation) == len(self.filters):
            for idx, filter in self.filters:
                selected_items = filter.selectedItems()
                if selected_items:
                    if sublocation[idx] not in selected_items:
                        return None
        return observation


class ImportMethodChoser(RowEntry):
    def __init__(self, parameter_name, parameter_names, connect):
        super(ImportMethodChoser, self).__init__()
        self.connect = connect
        self.parameter_widget = None
        self.parameter_name = parameter_name
        self.parameter_names = parameter_names
        self.label = PyQt4.QtGui.QLabel()
        self.label.setText(self.parameter_name)
        self.__import_method = PyQt4.QtGui.QComboBox()

        self.__import_method_classes = OrderedDict(((u'', None),
                                                  (u'comments', CommentsImportFields),
                                                  (u'w_level', WLevelImportFields),
                                                  (u'w_flow', WFlowImportFields),
                                                  (u'w_qual_field', WQualFieldImportFields)))

        self.__import_method.addItems(self.__import_method_classes.keys())
        self.connect(self.__import_method, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.choose_method(self.__import_method_classes))

        for widget in [self.label, self.__import_method]:
            self.layout.addWidget(widget)

    @property
    def import_method(self):
        return self.__import_method.currentText()

    @import_method.setter
    def import_method(self, value):
        self.__import_method.setEditText(utils.returnunicode(value))

    def choose_method(self, import_methods_classes):
        import_method_name = self.import_method
        utils.MessagebarAndLog.info(bar_msg=u'Method chosen: ' + import_method_name)
        try:
            self.layout.removeWidget(self.parameter_widget)
            self.parameter_widget.close()
        except:
            pass
        parameter_import_fields_class = import_methods_classes.get(import_method_name, None)

        if parameter_import_fields_class is None:
            self.parameter_widget = None
        else:
            parameter_import_fields = parameter_import_fields_class(self, self.connect)
            self.parameter_widget = parameter_import_fields.widget
            self.layout.addWidget(self.parameter_widget)


class CommentsImportFields(object):
    """
    This class should create a layout and populate it with question boxes relevant to comment import, which is probably an empty layout.
    What I want it to do:
    I want it to be able to receive comments-data, format it and send it to the regular comments-importer.
    The method to format and send to formatter should also get a dict with obsids and their final names.

    This is the class that knows how the comments-table looks like.
    """
    def __init__(self, import_method_chooser, connect):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super(CommentsImportFields, self).__init__()
        self.import_method_chooser = import_method_chooser
        pass

    def send_data_to_formatter(self):
        """
        This method should call format_data and then send it to the formatter.
        :return:
        """
        pass

    def format_data(self):
        """
        This method should format self.data into the columns contained in the table.
        :return:
        """
        pass

    def get_settings(self):
        pass

    def update_comments(self, observations):
        observations = copy.deepcopy(observations)
        parameter_name = self.import_method_chooser.parameter_name
        obsdict = {}
        dateformat = '%Y%M%D %H:%m:%s'
        for observation in observations:
            if observation[u'parametername'] == parameter_name:
                datestring = datetime.strftime(observation[u'date_time'], dateformat)
                obsdict.setdefault(observation[u'sublocation'], {})[datestring] = observation

        for observation in observations:
            if observation[u'parametername'] != parameter_name:
                comment_obs = obsdict.get(observation[u'sublocation'], {}).get(observation[u'date_time'], None)
                if comment_obs != None:
                    observation[u'comment'] = comment_obs[u'value']
                    comment_obs[u'skip_import'] = True
        return observations


class WLevelImportFields(object):
    """
    This class should create a layout and populate it with question boxes relevant to w_levels import, which is probably an empty layout.
    What I want it to do:
    I want it to be able to recieve w_levels-data, format it and send it to the regular comments-importer.
    The method to format and send to formatter should also get a dict with obsids and their final names.

    This is the class that knows how the comments-table looks like.
    """

    def __init__(self, mport_method_chooser, connect):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super(WLevelImportFields, self).__init__()
        pass

    def send_data_to_formatter(self):
        """
        This method should call format_data and then send it to the formatter.
        :return:
        """
        pass

    def format_data(self):
        """
        This method should format self.data into the columns contained in the table.
        :return:
        """
        pass

    def get_settings(self):
        pass


    def alter_data(self, observation, observations=None):
        return copy.deepcopy(observation)

class WFlowImportFields(RowEntryGrid):
    """
    This class should create a layout and populate it with question boxes relevant to w_flow import which is probably "flowtype" and "unit" dropdown lists.
    """


    def __init__(self, import_method_chooser, connect):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super(WFlowImportFields, self).__init__()
        self.connect = connect
        self._import_method_chooser = import_method_chooser
        self.label_flowtype = PyQt4.QtGui.QLabel(u'Flowtype: ')
        self.__flowtype = PyQt4.QtGui.QComboBox(self.widget)
        self.__flowtype.setEditable(True)
        self.__flowtype.addItem(u'')
        self._flowtypes_units = defs.w_flow_flowtypes_units()
        self.__flowtype.addItems(sorted(self._flowtypes_units.keys()))
        self.label_unit = PyQt4.QtGui.QLabel(u'Unit: ')
        self.__unit = PyQt4.QtGui.QComboBox()
        self.__unit.setEditable(True)
        self.connect(self.__flowtype, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda : self.fill_list(self.__unit, self.flowtype, self._flowtypes_units))

        self.layout.addWidget(self.label_flowtype, 0, 0)
        self.layout.addWidget(self.__flowtype, 1, 0)
        self.layout.addWidget(self.label_unit, 0, 1)
        self.layout.addWidget(self.__unit, 1, 1)
        self.layout.setColumnStretch(2, 1)

        #self.layout.addStretch()

    def alter_data(self, observation, observations=None):
        observation = copy.deepcopy(observation)
        observation[u'unit'] = self.unit
        observation[u'flowtype'] = self.flowtype
        return observation

    @property
    def flowtype(self):
        return self.__flowtype.currentText()

    @flowtype.setter
    def flowtype(self, value):
        self.__flowtype.setEditText(value)

    @property
    def unit(self):
        return self.__unit.currentText()

    @unit.setter
    def unit(self, value):
        self.__unit.setEditText(utils.returnunicode(value))

    def fill_list(self, combobox_var, parameter_var, parameter_list_dict):
        """

        :param combobox_var: a QComboBox object
        :param parameter_var: a string parameter name
        :param parameter_list_dict: A dict like  {u'Accvol': [(u'm3',)], u'Momflow': [(u'l/s',)]}
        :return:
        """
        vals = parameter_list_dict.get(parameter_var, None)
        if vals is None:
            vals = list(sorted(set([val for vals_list in parameter_list_dict.values() for val in vals_list[0]])))
        else:
            vals = list(vals[0])
        combobox_var.clear()
        combobox_var.addItem(u'')
        combobox_var.addItems(utils.returnunicode(vals, keep_containers=True))

    def get_settings(self):
        return OrderedDict((u'flowtype', self.flowtype),
                           (u'unit', self.unit))


class WQualFieldImportFields(RowEntryGrid):
    """
    This class should create a layout and populate it with question boxes relevant to w_qual_fields import which is probably "parameter", "unit" dropdown lists.
    And a depth dropdown list which is populated by the parameternames. The purpose is that the user should select which parametername to use as the depth variable

    """

    def __init__(self, import_method_chooser, connect):
        """
        A HBoxlayout should be created as self.layout.
        It shuold also create an empty list for future data as self.data
        Connecting the dropdown lists as events is done here (or in submethods).
        """
        super(WQualFieldImportFields, self).__init__()
        self.connect = connect
        self._import_method_chooser = import_method_chooser
        self.label_parameter = PyQt4.QtGui.QLabel(u'Parameter: ')
        self.__parameter = PyQt4.QtGui.QComboBox()
        self.__parameter.setEditable(True)
        self.__parameter.addItem(u'')
        self._parameters_units = defs.w_qual_field_parameter_units()
        self.__parameter.addItems(self._parameters_units.keys())
        self.label_unit = PyQt4.QtGui.QLabel(u'Unit: ')
        self.__unit = PyQt4.QtGui.QComboBox()
        self.__unit.setEditable(True)
        self.label_depth = PyQt4.QtGui.QLabel(u'Depth parameter: ')
        self.__depth = PyQt4.QtGui.QComboBox()
        self.__depth.setEditable(True)
        self.__depth.addItem(u'')
        self.__depth.addItems(self._import_method_chooser.parameter_names)
        self.__instrument = PyQt4.QtGui.QComboBox()
        self.__instrument.setEditable(True)
        self.label_instrument = PyQt4.QtGui.QLabel(u'Instrument: ')
        self.parameter_instruments = {}
        for parameter, unit_instrument_staff_date_time_list_of_lists in utils.get_last_used_quality_instruments().iteritems():
            for unit, instrument, staff, date_time, in unit_instrument_staff_date_time_list_of_lists:
                self.parameter_instruments.setdefault(parameter, set()).add(instrument)

        for parameter, instrument_set in self.parameter_instruments.iteritems():
            self.parameter_instruments[parameter] = [list(instrument_set)]

        self.layout.addWidget(self.label_parameter, 0, 0)
        self.layout.addWidget(self.__parameter, 1, 0)
        self.layout.addWidget(self.label_unit, 0, 1)
        self.layout.addWidget(self.__unit, 1, 1)
        self.layout.addWidget(self.label_depth, 0, 2)
        self.layout.addWidget(self.__depth, 1, 2)
        self.layout.addWidget(self.label_instrument, 0, 3)
        self.layout.addWidget(self.__instrument, 1, 3)
        self.layout.setColumnStretch(4, 1)

        self.connect(self.__parameter, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda : self.fill_list(self.__unit, self.parameter, self._parameters_units))

        self.connect(self.__parameter, PyQt4.QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     lambda: self.fill_list(self.__instrument, self.parameter, self.parameter_instruments))

    def alter_data(self, observation, observations):
        observation = copy.deepcopy(observation)
        observation[u'unit'] = self.unit
        observation[u'parameter'] = self.parameter
        observation[u'instrument'] = self.instrument
        observation[u'depth'] = None
        if self.depth is not None:
            depth = [_observation[u'value'] for _observation in observations for _observation in observations
                     if all(_observation[u'date_time'] == observation[u'date_time'], _observation[u'sublocation'] == observation[u'sublocation' ])]
            if depth:
                observation[u'depth'] = depth
        return observation

    @property
    def parameter(self):
        return self.__parameter.currentText()

    @parameter.setter
    def parameter(self, value):
        self.__parameter.setEditText(value)

    @property
    def unit(self):
        return self.__unit.currentText()

    @unit.setter
    def unit(self, value):
        self.__unit.setEditText(utils.returnunicode(value))

    @property
    def depth(self):
        return self.__depth.currentText()

    @depth.setter
    def depth(self, value):
        self.__depth.setEditText(utils.returnunicode(value))

    @property
    def instrument(self):
        return self.__instrument.currentText()

    @instrument.setter
    def instrument(self, value):
        self.__instrument.setEditText(utils.returnunicode(value))

    def fill_list(self, combobox_var, parameter_var, parameter_list_dict):
        """

        :param combobox_var: a QComboBox object
        :param parameter_var: a string parameter name
        :param parameter_list_dict: A dict like  {u'Accvol': [(u'm3',)], u'Momflow': [(u'l/s',)]}
        :return:
        """
        vals = parameter_list_dict.get(parameter_var, None)
        if vals is None:
            vals = list(sorted(set([val for vals_list in parameter_list_dict.values() for val in vals_list[0]])))
        else:
            vals = list(vals[0])
        combobox_var.clear()
        combobox_var.addItem(u'')
        combobox_var.addItems(utils.returnunicode(vals, keep_containers=True))

    def get_settings(self):
        return OrderedDict((u'parameter', self.parameter),
                           (u'unit', self.unit),
                           (u'depth', self.depth),
                           (u'instrument', self.instrument))










