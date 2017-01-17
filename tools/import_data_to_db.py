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
import PyQt4
import copy
import io
import qgis.utils
from collections import OrderedDict
from datetime import datetime
from functools import partial
from operator import itemgetter
from pyspatialite import dbapi2 as sqlite #could perhaps have used sqlite3 (or pysqlite2) but since pyspatialite needed in plugin overall it is imported here as well for consistency
from qgis.core import *

import PyQt4.QtCore
import PyQt4.QtGui

import midvatten_utils as utils
from date_utils import find_date_format, datestring_to_date


class midv_data_importer():  # this class is intended to be a multipurpose import class  BUT loggerdata probably needs specific importer or its own subfunction

    def __init__(self):
        self.columns = 0
        self.status= 'False'
        self.recsbefore = 0
        self.recsafter = 0
        self.recstoimport = 0
        self.recsinfile = 0
        self.temptablename = ''
        self.charsetchoosen = ''
        self.csvlayer = None
        self.foreign_keys_import_question = None

    def general_csv_import(self, goal_table=None, column_header_translation_dict=None):
        """General method for importing an sqlite table into a goal_table

            self.temptableName must be the name of the table containing the new data to import.

        :param column_header_translation_dict: a dict like {u'column_name_in_csv: column_name_in_db}
        :param goal_table:
        :return:
        """
        PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
        self.status = 'False' #True if upload to sqlite and cleaning of data succeeds
        self.temptableName = goal_table + u'_temp'

        if goal_table is None:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error: No goal table given!')
            self.status = 'False'
            return

        if not self.csvlayer:
            self.csvlayer = self.get_csvlayer()  # loads csv file as qgis csvlayer (qgsmaplayer, ordinary vector layer provider)
        if self.csvlayer == u'cancel' or not self.csvlayer:
            self.status = 'True'
            return

        self.qgiscsv2sqlitetable(column_header_translation_dict) #loads qgis csvlayer into sqlite table

        recsinfile = utils.sql_load_fr_db(u'select count(*) from "%s"'%self.temptableName)[1][0][0]

        table_info = utils.sql_load_fr_db(u'''PRAGMA table_info("%s")'''%goal_table)[1]
        column_headers_types = dict([(row[1], row[2]) for row in table_info])
        primary_keys = [row[1] for row in table_info if int(row[5])]        #Not null columns are allowed if they have a default value.
        not_null_columns = [row[1] for row in table_info if int(row[3]) and row[4] is None]
        #Only use the columns that exists in the goal table.
        existing_columns = [x[1] for x in utils.sql_load_fr_db("""PRAGMA table_info(%s)"""%self.temptableName)[1] if x[1] in column_headers_types]
        missing_columns = [column for column in not_null_columns if column not in existing_columns]

        if missing_columns:
            utils.MessagebarAndLog.critical(bar_msg=u'Error: Import failed, see log message panel', log_msg=u'Required columns ' + u', '.join(missing_columns) + u' are missing for table ' + goal_table, duration=999)
            self.status = False
            return

        #Delete records from self.temptable where yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already exist for the same date.
        nr_before = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1][0][0]
        if u'date_time' in primary_keys:
            self.delete_existing_date_times_from_temptable(primary_keys, goal_table)
        nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%(self.temptableName))[1][0][0]

        nr_same_date = nr_after - nr_before
        self.check_remaining(nr_before, nr_after, u"Import warning, see log message panel", u'In total "%s" rows with the same date \non format yyyy-mm-dd hh:mm or yyyy-mm-dd hh:mm:ss already existed and will not be imported.'%(str(nr_same_date)))
        if not self.status:
            return

        # Import foreign keys in some special cases
        nr_before = nr_after
        foreign_keys = utils.get_foreign_keys(goal_table)
        force_import_of_foreign_keys_tables = [u'zz_flowtype', u'zz_staff', u'zz_meteoparam']

        if self.foreign_keys_import_question is None:
            stop_question = utils.askuser(u"YesNo", u"""Please note!\nForeign keys will be imported silently into "%s" if needed. \n\nProceed?"""%(u', '.join(force_import_of_foreign_keys_tables)), u"Info!")
            if stop_question.result == 0:      # if the user wants to abort
                self.status = 'False'
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return 0   # return simply to stop this function
            else:
                self.foreign_keys_import_question = 1

        for fk_table, from_to_fields in foreign_keys.iteritems():
            from_list = [x[0] for x in from_to_fields]
            to_list = [x[1] for x in from_to_fields]
            if fk_table in force_import_of_foreign_keys_tables:
                if not all([_from in existing_columns for _from in from_list]):
                    continue
                nr_fk_before = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%fk_table)[1][0][0]
                _table_info = utils.sql_load_fr_db(u'''PRAGMA table_info("%s")'''% fk_table)[1]
                _column_headers_types = dict([(row[1], row[2]) for row in _table_info])
                sql = ur"""insert or ignore into %s (%s) select distinct %s from %s as b where %s"""%(fk_table,
                                                                                             u', '.join([u'"{}"'.format(k) for k in to_list]),
                                                                                             u', '.join([u'''CAST("b"."%s" as "%s")'''%(k, _column_headers_types[to_list[idx]]) for idx, k in enumerate(from_list)]),
                                                                                             self.temptableName,
                                                                                             u' and '.join([u''' "b"."{}" IS NOT NULL and "b"."{}" != '' and "b"."{}" != ' ' '''.format(k, k, k) for k in from_list]))
                utils.sql_alter_db(sql)
                nr_fk_after = utils.sql_load_fr_db(u'''select count(*) from "%s"'''%fk_table)[1][0][0]
                utils.MessagebarAndLog.info(u'In total ' + str(nr_fk_after - nr_fk_before) + u' rows were imported to foreign key table ' + fk_table)
            else:
                #Else check if there are foreign keys blocking the import and skip those rows
                existing_keys = utils.sql_load_fr_db(u'select distinct "%s" from "%s"'%(u', '.join(to_list),
                                                                                        fk_table))[1]
                new_keys = utils.sql_load_fr_db(u'select distinct "%s" from "%s"'%(u', '.join(from_list),
                                                                                   self.temptableName))[1]
                missing_keys = [keys for keys in new_keys if keys not in existing_keys]

                if missing_keys:
                    utils.MessagebarAndLog.warning(bar_msg=u'Import error, see log message panel',
                                                   log_msg=u'There was ' + str(len(missing_keys)) +
                                                   u'entries where foreign keys were missing from ' + fk_table +
                                                   u' which will not be imported:\n' + u'\n'.join([u', '.join(f) for f in missing_keys]),
                                                   duration=999)

                    utils.sql_alter_db(u'delete from "%s" where %s in (%s)'%(self.temptableName,
                                                                             u' || '.join(from_list),
                                                                             u', '.join([u"'{}'".format(u''.join([u'NULL' if k is None else k for k in mk])) for mk in missing_keys])))

        nr_after = utils.sql_load_fr_db(u'''select count(*) from "%s"''' % (self.temptableName))[1][0][0]
        nr_after_foreign_keys = nr_before - nr_after
        self.check_remaining(nr_before, nr_after, u"Import warning, see log message panel", u'In total "%s" rows were deleted due to foreign keys restrictions and "%s" rows remain.'%(str(nr_after_foreign_keys), str(nr_after)))
        if not self.status:
            return

        #Special cases for some tables
        if goal_table == u'stratigraphy':
            self.check_and_delete_stratigraphy(existing_columns)
        if goal_table == u'obs_lines':
            self.calculate_geometry(existing_columns)

        #Finally import data:
        nr_failed_import = recsinfile - nr_after
        if nr_failed_import > 0:
            stop_question = utils.askuser(u"YesNo", u"""Please note!\nThere are %s rows in your data that can not be imported!\nDo you really want to import the rest?\nAnswering yes will start, from top of the imported file and only import the first of the duplicates.\n\nProceed?"""%(str(nr_failed_import)),"Warning!")
            if stop_question.result == 0:      # if the user wants to abort
                self.status = 'False'
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return 0   # return simply to stop this function

        sql_list = [u"""INSERT OR IGNORE INTO "%s" ("""%goal_table]
        sql_list.append(u', '.join([u'"{}"'.format(k) for k in sorted(existing_columns)]))
        sql_list.append(u""") SELECT """)
        sql_list.append(u', '.join([u"""(case when ("%s"!='' and "%s"!=' ' and "%s" IS NOT NULL) then CAST("%s" as "%s") else null end)"""%(colname, colname, colname, colname, column_headers_types[colname]) for colname in sorted(existing_columns)]))
        sql_list.append(u"""FROM %s"""%(self.temptableName))
        sql = u''.join(sql_list)

        recsbefore = utils.sql_load_fr_db(u'select count(*) from "%s"' % (goal_table))[1][0][0]
        try:
            utils.sql_alter_db(sql.encode(u'utf-8'))
        except Exception, e:
            utils.MessagebarAndLog.critical(bar_msg=u'Error, import failed, see log message panel', log_msg=u'Sql\n' + sql + u' failed.\nMsg:\n' + str(e), duration=999)
            self.status = 'False'
            return
        recsafter = utils.sql_load_fr_db(u'select count(*) from "%s"' % (goal_table))[1][0][0]
        self.stats_after(recsinfile=recsinfile, recsbefore=recsbefore, recsafter=recsafter)

        self.status = 'True'

        utils.MessagebarAndLog.info(bar_msg=u'In total %s measurements were imported to "%s".'''%(recsafter - recsbefore, goal_table))

        utils.sql_alter_db(u"DROP table %s"%self.temptableName) # finally drop the temporary table
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def send_file_data_to_importer(self, file_data, importer, cleaning_function=None):
        self.csvlayer = None
        if len(file_data) < 2:
            utils.MessagebarAndLog.info(bar_msg=u'Import error, see log message panel', log_msg=u'Import failed only a header was sent to importer')
            return

        if cleaning_function is not None:
            file_data = cleaning_function(file_data)

        #QgsVectorLayer(path, "temporary_csv_layer", "ogr") doesn't work if the file only has one column, so an empty column has to be added
        if len(file_data[0]) == 1:
            [row.append(u'') for row in file_data]

        file_string = utils.lists_to_string(file_data)

        with utils.tempinput(file_string, charset=u'utf_8') as csvpath:
            self.charsetchoosen = u'UTF-8'
            csvlayer = self.csv2qgsvectorlayer(csvpath)
            if not csvlayer:
                utils.MessagebarAndLog.critical("Import error: Creating csvlayer failed!")
                return
            self.csvlayer = csvlayer
            importer()

    def get_csvlayer(self): # general importer
        """Select the csv file, user must also tell what charset to use"""
        self.charsetchoosen = utils.ask_for_charset()
        if not self.charsetchoosen:
            return u'cancel'

        csvpath = utils.select_files(only_one_file=True, extension="csv (*.csv)")
        if not csvpath:
            return u'cancel'

        return self.csv2qgsvectorlayer(csvpath[0])

    def csv2qgsvectorlayer(self, path):
        """ Creates QgsVectorLayer from a csv file """
        if not path:
            qgis.utils.iface.messageBar().pushMessage("Failure, no csv file was selected.")
            return False

        csvlayer = QgsVectorLayer(path, "temporary_csv_layer", "ogr")

        if not csvlayer.isValid():
            qgis.utils.iface.messageBar().pushMessage("Failure","Impossible to Load File in QGis:\n" + str(path), 2)
            PyQt4.QtGui.QApplication.restoreOverrideCursor()
            return False
        csvlayer.setProviderEncoding(str(self.charsetchoosen))
        return csvlayer

    def qgiscsv2sqlitetable(self, column_header_translation_dict=None): # general importer
        """Upload qgis csv-csvlayer (QgsMapLayer) as temporary table (temptableName) in current DB. status='True' if succesfull, else 'false'.

        :param column_header_translation_dict: a dict like {u'column_name_in_csv: column_name_in_db}

        """

        if column_header_translation_dict is None:
            column_header_translation_dict = {}

        self.status = 'False'
        #check if the temporary import-table already exists in DB (which only shoule be the case if an earlier import failed)
        existing_names= [str(existing_name[0]) for existing_name in utils.sql_load_fr_db(r"""SELECT tbl_name FROM sqlite_master WHERE (type='table' or type='view') and not (name = 'geom_cols_ref_sys' or name = 'geometry_columns' or name = 'geometry_columns_auth' or name = 'spatial_ref_sys' or name = 'spatialite_history' or name = 'sqlite_sequence' or name = 'sqlite_stat1' or name = 'views_geometry_columns' or name = 'virts_geometry_columns') ORDER BY tbl_name""")[1]]
        while self.temptableName in existing_names: #this should only be needed if an earlier import failed. if so, propose to rename the temporary import-table
            reponse = PyQt4.QtGui.QMessageBox.question(None, "Warning - Table name confusion!",'''The temporary import table '%s' already exists in the current DataBase. This could indicate a failure during last import. Please verify that your table contains all expected data and then remove '%s'.\n\nMeanwhile, do you want to go on with this import, creating a temporary table '%s_2' in database?'''%(self.temptableName,self.temptableName,self.temptableName), PyQt4.QtGui.QMessageBox.Yes | PyQt4.QtGui.QMessageBox.No)
            if reponse == PyQt4.QtGui.QMessageBox.Yes:
                self.temptableName = '%s_2'%self.temptableName
            else:
                return None

        #Get all fields with corresponding types for the csv-csvlayer in qgis
        fields=[]
        fieldsNames=[]
        provider=self.csvlayer.dataProvider()
        for name in provider.fields(): #fix field names and types in temporary table
            fldName = unicode(name.name()).replace("'"," ").replace('"'," ")  #Fixing field names
            if column_header_translation_dict:
                fldName = column_header_translation_dict.get(fldName, fldName)
            #Avoid two cols with same name:
            while fldName.upper() in fieldsNames:
                fldName = '%s_2'%fldName
            fldType=name.type()
            fldTypeName=unicode(name.typeName()).upper()
            if fldType in (PyQt4.QtCore.QVariant.Char,PyQt4.QtCore.QVariant.String): # field type is text  - this will be the case for all columns if not a .csvt file is defined beside the imported file.
                fldLength=name.length()
                fldType='text(%s)'%fldLength  #Add field Length Information
            elif fldType in (PyQt4.QtCore.QVariant.Bool, PyQt4.QtCore.QVariant.Int, PyQt4.QtCore.QVariant.LongLong, PyQt4.QtCore.QVariant.UInt, PyQt4.QtCore.QVariant.ULongLong):  # field type is integer
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

    def delete_existing_date_times_from_temptable(self, primary_keys, goal_table):
        pks = [pk for pk in primary_keys if pk != u'date_time']
        pks.append(u'date_time')

        #Delete records that have the same date_time but with :00 at the end. (2016-01-01 00:00 will not be imported if 2016-01-01 00:00:00 exists
        pks_and_00 = [u'"{}"'.format(pk) for pk in pks]
        pks_and_00.append(u"':00'")
        sql = u'''delete from "%s" where %s in (select %s from "%s")'''%(self.temptableName,
                                                                                          u' || '.join(pks_and_00),
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          goal_table)
        utils.sql_alter_db(sql)

        # Delete records that have the same date_time but with :00 at the end. (2016-01-01 00:00:00 will not be imported if 2016-01-01 00:00 exists
        sql = u'''delete from "%s" where SUBSTR(%s, 1, length(%s) - 3) in (select %s from "%s")'''%(self.temptableName,
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          u' || '.join([u'"{}"'.format(pk) for pk in pks]),
                                                                                          goal_table)
        utils.sql_alter_db(sql)

    def check_remaining(self, nr_before, nr_after, bar_msg, log_msg):
        if nr_after == 0:
            utils.MessagebarAndLog.critical(bar_msg=u'Import error, nothing imported.')
            self.status = False
        elif nr_before > nr_after:
            utils.MessagebarAndLog.warning(bar_msg=bar_msg, log_msg=log_msg)

    def calculate_geometry(self, existing_columns):
        # Calculate the geometry
        sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_lines'"""
        SRID = str((utils.sql_load_fr_db(sql)[1])[0][0])  # THIS IS DUE TO WKT-import of geometries below
        if u'WKT' in existing_columns:
            geocol = u'WKT'
        elif u'geometry' in existing_columns:
            geocol = u'geometry'
        else:
            utils.MessagebarAndLog.warning(bar_msg=u'Obslines without geometry imported')
            return None

        utils.sql_alter_db(u'''update "%s" set geometry=ST_GeomFromText("%s",'%s')'''%(self.temptableName,
                                                                                       geocol,
                                                                                       SRID))

    def check_and_delete_stratigraphy(self, existing_columns):
        if all([u'stratid' in existing_columns, u'depthtop' in existing_columns, u'depthbot' in existing_columns]):
            skip_obsids = []
            obsid_strat = utils.get_sql_result_as_dict(u'select obsid, stratid, depthtop, depthbot from "%s"'%self.temptableName)[1]
            for obsid, stratid_depthbot_depthtop  in obsid_strat.iteritems():
                #Turn everything to float
                strats = [[float(x) for x in y] for y in stratid_depthbot_depthtop]
                sorted_strats = sorted(strats, key=itemgetter(0))
                stratid_idx = 0
                depthtop_idx = 1
                depthbot_idx = 2
                for index in xrange(len(sorted_strats)):
                    if index == 0:
                        continue
                    #Check that there is no gap in the stratid:
                    if float(sorted_strats[index][stratid_idx]) - float(sorted_strats[index - 1][stratid_idx]) != 1:
                        utils.MessagebarAndLog.warning(bar_msg=u'Import error, see log message panel', log_msg=u'The obsid ' + obsid + u' will not be imported due to gaps in stratid')
                        skip_obsids.append(obsid)
                        break
                    #Check that the current depthtop is equal to the previous depthbot
                    elif sorted_strats[index][depthtop_idx] != sorted_strats[index - 1][depthbot_idx]:
                        utils.MessagebarAndLog.warning(bar_msg=u'Import error, see log message panel', log_msg=u'The obsid ' + obsid + u' will not be imported due to gaps in depthtop/depthbot')
                        skip_obsids.append(obsid)
                        break
            if skip_obsids:
                utils.sql_alter_db(u'delete from "%s" where obsid in (%s)'%(self.temptableName, u', '.join([u'"{}"'.format(obsid) for obsid in skip_obsids]) ))

    def import_interlab4(self, filenames=None):
        all_lab_results = self.parse_interlab4(filenames)
        if all_lab_results == u'cancel':
            self.status = False
            return u'cancel'

        wquallab_data_table = self.interlab4_to_table(all_lab_results, utils.get_all_obsids())
        if wquallab_data_table in [u'cancel', u'error']:
            self.status = False
            return wquallab_data_table

        utils.filter_nonexisting_values_and_ask(wquallab_data_table, u'obsid', utils.get_all_obsids(table=u'obs_points'), try_capitalize=False)
        self.send_file_data_to_importer(wquallab_data_table, partial(self.general_csv_import, goal_table=u'w_qual_lab'))
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
        self.charsetchoosen = utils.ask_for_charset(default_charset='cp1252')
        if not self.charsetchoosen:
            self.status = 'True'
            return u'cancel'

        files = utils.select_files(only_one_file=False, extension="csv (*.csv)")
        if not files:
            self.status = 'True'
            return u'cancel'

        parsed_files = []
        for selected_file in files:
            file_data = self.parse_diveroffice_file(selected_file, self.charsetchoosen, existing_obsids, confirm_names.result)
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

        with utils.tempinput(file_string, self.charsetchoosen) as csvpath:
            self.csvlayer = self.csv2qgsvectorlayer(csvpath)
            #Continue to next file if the file failed to import
            if not self.csvlayer:
                qgis.utils.iface.messageBar().pushMessage("Import Failure","""No files imported""")
                PyQt4.QtGui.QApplication.restoreOverrideCursor()
                return
            else:
                self.general_csv_import(goal_table=u'w_levels_logger')

        PyQt4.QtGui.QApplication.restoreOverrideCursor()
        self.SanityCheckVacuumDB()
        PyQt4.QtGui.QApplication.restoreOverrideCursor()

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

    def stats_after(self, recsinfile=None, recsbefore=None, recsafter=None):
        if recsinfile is None:
            recsinfile = self.recstoimport
        if recsafter is None:
            recsafter = self.recsafter
        if recsbefore is None:
            recsbefore = self.recsbefore

        NoExcluded = recsinfile - (recsafter - recsbefore)

        if NoExcluded > 0:  # If some of the imported data already existed in the database, let the user know
            utils.MessagebarAndLog.warning(bar_msg=u'Warning, In total %s posts were not imported.'%str(NoExcluded))

    def SanityCheckVacuumDB(self):
        sanity = utils.askuser("YesNo","""It is a strong recommendation that you do vacuum the database now, do you want to do so?\n(If unsure - then answer "yes".)""",'Vacuum the database?')
        if sanity.result == 1:
            PyQt4.QtGui.QApplication.setOverrideCursor(PyQt4.QtCore.Qt.WaitCursor)
            utils.sql_alter_db('vacuum')    # since a temporary table was loaded and then deleted - the db may need vacuuming
            PyQt4.QtGui.QApplication.restoreOverrideCursor()








