# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of data to the database
  from the interlab4 format.

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-11-27
        copyright            : (C) 2016 by HenrikSpa (and joskal)
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
from __future__ import absolute_import

import copy
import csv
import io
import os
import re
from builtins import range
from builtins import str
from datetime import datetime

import qgis.PyQt
from qgis.PyQt.QtCore import QCoreApplication, QItemSelectionModel

from midvatten.tools import import_data_to_db
from midvatten.tools.utils import common_utils, midvatten_utils
from midvatten.tools.utils.common_utils import returnunicode as ru, Cancel
from midvatten.tools.utils.date_utils import datestring_to_date
from midvatten.tools.utils.db_utils import tables_columns, sql_load_fr_db, sql_alter_db
from midvatten.tools.utils.gui_utils import SplitterWithHandel, RowEntry, VRowEntry, ExtendedQPlainTextEdit, get_line

import_fieldlogger_ui_dialog =  qgis.PyQt.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_interlab4.ui'))[0]

class Interlab4Import(qgis.PyQt.QtWidgets.QMainWindow, import_fieldlogger_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        qgis.PyQt.QtWidgets.QDialog.__init__(self, parent)
        self.setAttribute(qgis.PyQt.QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(ru(QCoreApplication.translate('Interlab4Import', "Import interlab4 data to w_qual_lab table"))) # Set the title for the dialog
        #self.MainWindow.setWindowTitle("Import interlab4 data to w_qual_lab table")
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.status = True
        self.obsid_assignment_table = 'zz_interlab4_obsid_assignment'

    def init_gui(self):
        splitter = SplitterWithHandel(qgis.PyQt.QtCore.Qt.Vertical)
        self.main_vertical_layout.addWidget(splitter)

        self.specific_meta_filter = MetaFilterSelection(None)

        splitter.addWidget(self.specific_meta_filter.widget)

        self.metadata_filter = MetadataFilter(None)
        splitter.addWidget(self.metadata_filter.widget)

        self.metadata_filter.update_selection_button.clicked.connect(lambda : self.metadata_filter.set_selection(self.specific_meta_filter.get_items_dict()))
        self.metadata_filter.buttonSave.clicked.connect(lambda: self.handle_save())

        self.skip_imported_reports = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('Interlab4Import', 'Skip imported reports')))
        self.skip_imported_reports.setChecked(True)

        self.select_files_button = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('Interlab4Import', 'Select files...')))
        self.select_files_button.clicked.connect(lambda: self.load_files())

        self.start_import_button = qgis.PyQt.QtWidgets.QPushButton(ru(QCoreApplication.translate('Interlab4Import', 'Start import')))
        self.start_import_button.setDisabled(True)

        self.help_label = qgis.PyQt.QtWidgets.QLabel(ru(QCoreApplication.translate('Interlab4Import', 'Instructions')))
        self.help_label.setToolTip(ru(QCoreApplication.translate('Interlab4Import',
                                   'Selected rows (lablitteras in the bottom table will be imported when pushing "Start import" button.\n'
                                   'The table can be sorted by clicking the column headers.\n\n'
                                   'Rows at the bottom table can also be selected using the top list.\n'
                                   'Howto:\n'
                                   '1. Choose column header to make a selection by in the Column header drop down list.\n'
                                   '2. Make a list of entries (one row per entry).\n'
                                   '3. Click "Update selection".\n'
                                   'All rows where values in the chosen column match entries in the pasted list will be selected.\n\n'
                                   'Hover over a column header to see which database column it will go to.\n\n'
                                   '("Save data table to csv" is a feature to save the data table into a csv file for examination in another application.)\n'
                                   '("Save metadata table to file" is a feature to save the metadata table into a csv file, at system temporary path, for examination in another application.)')))

        self.close_after_import = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('Interlab4Import', 'Close dialog after import')))
        self.close_after_import.setChecked(True)


        self.dump_2_temptable = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('Interlab4Import', 'Save datatable to csv')))
        self.dump_2_temptable.setToolTip(ru(QCoreApplication.translate('Interlab4Import','save the data table into a csv file, at system temporary path, for examination in another application')))
        self.dump_2_temptable.setChecked(False)


        self.use_obsid_assignment_table = qgis.PyQt.QtWidgets.QGroupBox(ru(QCoreApplication.translate('Interlab4Import', 'Assign obsid using table')))
        self.use_obsid_assignment_table.setCheckable(True)
        self.use_obsid_assignment_table.setLayout(qgis.PyQt.QtWidgets.QVBoxLayout())
        self.ignore_provtagningsorsak = qgis.PyQt.QtWidgets.QCheckBox(ru(QCoreApplication.translate('Interlab4Import', 'Ignore provtagningsorsak')))
        self.ignore_provtagningsorsak.setToolTip(ru(QCoreApplication.translate('Interlab4Import', 'If not set, the user is requested for obsid if the metadata "provtagningsorsak" is not empty')))
        self.use_obsid_assignment_table.layout().addWidget(self.ignore_provtagningsorsak)
        self.ignore_provtagningsorsak.setChecked(False)

        tables = tables_columns()
        if self.obsid_assignment_table not in tables:
            self.use_obsid_assignment_table.setToolTip(ru(QCoreApplication.translate('Interlab4Import', "(Table %s doesn't exist!) Assign obsid for each lablittera using table '%s'. Only possible if the table exists!")) % (self.obsid_assignment_table, self.obsid_assignment_table))
            self.use_obsid_assignment_table.setCheckable(False)
        else:
            self.use_obsid_assignment_table.setToolTip(ru(QCoreApplication.translate('Interlab4Import', "Assign obsid for each lablittera using table '%s'."))%self.obsid_assignment_table)
            self.use_obsid_assignment_table.setChecked(True)

        self.gridLayout_buttons.addWidget(self.skip_imported_reports, 0, 0)
        self.gridLayout_buttons.addWidget(self.select_files_button, 1, 0)
        self.gridLayout_buttons.addWidget(get_line(), 2, 0)
        self.gridLayout_buttons.addWidget(self.close_after_import, 3, 0)
        self.gridLayout_buttons.addWidget(self.dump_2_temptable, 4, 0)
        self.gridLayout_buttons.addWidget(self.use_obsid_assignment_table, 5, 0)
        self.gridLayout_buttons.addWidget(self.start_import_button, 6, 0)
        self.gridLayout_buttons.addWidget(self.help_label, 7, 0)
        self.gridLayout_buttons.setRowStretch(8, 1)

        self.start_import_button.clicked.connect(lambda : self.start_import(self.all_lab_results, self.metadata_filter.get_selected_lablitteras(), self.ignore_provtagningsorsak.isChecked()))

        self.show()

    @common_utils.general_exception_handler
    def load_files(self):
        filenames = tools.utils.midvatten_utils.select_files(only_one_file=False,
                                                             extension="lab (*.lab)")

        if self.skip_imported_reports.isChecked():
            skip_reports = [str(x[0]) for x in sql_load_fr_db('''SELECT DISTINCT report FROM w_qual_lab;''')[1]]
        else:
            skip_reports = []

        self.all_lab_results = self.parse(filenames, skip_reports)
        self.specific_meta_filter.update_combobox(self.all_lab_results)
        self.metadata_filter.update_table(self.all_lab_results)

        self.start_import_button.setDisabled(False)

    @common_utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self, all_lab_results, lablitteras_to_import, ignore_provtagningsorsak):
        all_lab_results = copy.deepcopy(all_lab_results)
        all_lab_results = dict([(lablittera, v) for lablittera, v in all_lab_results.items() if lablittera in lablitteras_to_import])

        #Allow the user to connect the metadata rows to obsids.
        meta_headers = get_metadata_headers(all_lab_results)
        ask_obsid_table = [meta_headers]
        for lablittera, v in sorted(all_lab_results.items()):
            metarow = [v['metadata'].get(meta_header, '') for meta_header in meta_headers]
            ask_obsid_table.append(metarow)
        existing_obsids = tools.utils.db_utils.get_all_obsids()

        connection_columns = ('specifik provplats', 'provplatsnamn')
        if self.use_obsid_assignment_table.isChecked():
            remaining_lablitteras_obsids, ask_obsid_table, add_to_table = self.obsid_assignment_using_table(ask_obsid_table, existing_obsids, connection_columns,
                                                                                                            ignore_provtagningsorsak)
        else:
            remaining_lablitteras_obsids = {}

        if ask_obsid_table:
            answer = common_utils.filter_nonexisting_values_and_ask(ask_obsid_table, 'obsid', existing_values=existing_obsids, try_capitalize=False, always_ask_user=True)
            if answer == 'cancel':
                self.status = True
                return Cancel()
            elif not answer:
                self.status = False
                common_utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate('Interlab4Import', 'Error, no observations remain. No import done.')))
                return Cancel()
            else:
                remaining_lablitteras_obsids.update(dict([(x[0], x[-1]) for x in answer[1:]]))

                if self.use_obsid_assignment_table.isChecked() and add_to_table:
                    header = answer[0]
                    handled = set()
                    for row in answer[1:]:
                        if not ignore_provtagningsorsak:
                            try:
                                idx = header.index('provtagningsorsak')
                            except ValueError:
                                pass
                            else:
                                provtagningsorsak = row[idx].replace('-', '').replace('0', '').strip()
                                # If the field staff has made a comment on the bottles, do not set obsid automatically.
                                if provtagningsorsak:
                                    continue

                        current = (row[header.index(connection_columns[0])], row[header.index(connection_columns[1])])
                        if current in add_to_table and current not in handled:
                            obsid = row[-1]
                            add_values = (current[0], current[1], obsid)
                            sql = '''INSERT INTO {} ({}, {}, obsid) VALUES ('{}', '{}', '{}')'''.format(self.obsid_assignment_table,
                                                                                                               connection_columns[0].replace(' ', '_'),
                                                                                                               connection_columns[1],
                                                                                                               *add_values)
                            sql_alter_db(sql)
                            handled.add(current)
                    if handled:
                        common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('Interlab4Import',
                                                                                              'Obsid assignments added to table %s.')) % self.obsid_assignment_table)

        #Filter the remaining lablitteras and add an obsid field
        _all_lab_results = {}
        for lablittera, v in all_lab_results.items():
            if lablittera in remaining_lablitteras_obsids:
                v['metadata']['obsid'] = remaining_lablitteras_obsids[lablittera]
                _all_lab_results[lablittera] = v
        all_lab_results = _all_lab_results

        self.wquallab_data_table = self.to_table(all_lab_results)

        importer = import_data_to_db.midv_data_importer()

        answer = importer.general_import(dest_table=u'w_qual_lab', file_data=self.wquallab_data_table, dump_temptable=self.dump_2_temptable.isChecked())

        if self.close_after_import.isChecked():
            self.close()

        common_utils.stop_waiting_cursor()

    def obsid_assignment_using_table(self, ask_obsid_table, existing_obsids, connection_columns, ignore_provtagningsorsak):
        remaining_lablitteras_obsids = {}
        header = [x.lower() for x in ask_obsid_table[0]]
        try:
            [header.index(col) for col in connection_columns]
        except ValueError:
            #One of the connection columns didn't have a value
            return remaining_lablitteras_obsids, ask_obsid_table, []

        _ask_obsid_table = [ask_obsid_table[0]]
        add_to_table = []
        try:
            connection_table = sql_load_fr_db('''SELECT {}, {}, "obsid" FROM {}'''.format(connection_columns[0].replace(' ', '_'), connection_columns[1], self.obsid_assignment_table))[1]
        except Exception as e:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Interlab4Import', 'Error, could not get data from %s.')) % self.obsid_assignment_table,
                                                              log_msg=ru(str(e)))
            return remaining_lablitteras_obsids, ask_obsid_table, []

        connection_dict = {(row[0], row[1]): row[2] for row in connection_table}
        for row in ask_obsid_table[1:]:
            current = (row[header.index(connection_columns[0])], row[header.index(connection_columns[1])])
            if not ignore_provtagningsorsak:
                try:
                    idx = header.index('provtagningsorsak')
                except ValueError:
                    pass
                else:
                    provtagningsorsak = row[idx].replace('-', '').replace('0', '').strip()
                    # If the field staff has made a comment on the bottles, do not set obsid automatically.
                    if provtagningsorsak:
                        _ask_obsid_table.append(row)
                        continue
            obsid = connection_dict.get(current, None)
            if obsid is None:
                _ask_obsid_table.append(row)
                add_to_table.append(current)
                continue
            else:
                if obsid not in existing_obsids:
                    common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Interlab4Import',
                                                                                         "Error! Obsid '%s' is used in %s but doesn't exist in obs_points")) % (obsid, self.obsid_assignment_table))
                    _ask_obsid_table.append(row)
                else:
                    remaining_lablitteras_obsids[row[0]] = obsid
        return remaining_lablitteras_obsids, _ask_obsid_table, add_to_table


    def parse(self, filenames, skip_reports=None):
        """ Reads the interlab
        :param filenames:
        :return: A dict like {<lablittera>: {'metadata': {'metadataheader': value, ...}, <par1_name>: {'dataheader': value, ...}}}
        """
        if skip_reports is None:
            skip_reports = []

        all_lab_results = {}

        for filename in filenames:
            file_settings = self.parse_filesettings(filename)
            file_error, version, encoding, decimalsign, quotechar = file_settings
            if file_error:
                common_utils.pop_up_info(ru(QCoreApplication.translate('Interlab4Import', "Warning: The file information %s could not be read. Skipping file")) % filename)
                continue

            with io.open(filename, 'r', encoding=encoding) as f:
                if quotechar:
                    unicode_reader = csv.reader(f, dialect=csv.excel, quotechar=str(quotechar), delimiter=';')
                else:
                    unicode_reader = csv.reader(f, dialect=csv.excel, delimiter=';')

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

                    if cols[0].lower().startswith('#slut'):
                        break

                    #cols = ru(cols, keep_containers=True)

                    if cols[0].lower().startswith('#provadm'):
                        parse_data_values = False
                        parse_metadata_values = False
                        read_data_header = False
                        read_metadata_header = True
                        data_header = None
                        metadata_header = None
                        continue

                    if cols[0].lower().startswith('#provdat'):
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
                        if str(cols[0]) not in skip_reports:
                            metadata = dict([(metadata_header[idx], value.lstrip(' ').rstrip(' ')) for idx, value in enumerate(cols) if value.lstrip(' ').rstrip(' ')])
                            lab_results.setdefault(metadata['lablittera'], {})['metadata'] = metadata
                        continue

                    if read_data_header:
                        data_header = [x.lower() for x in cols]
                        read_data_header = False
                        parse_data_values = True
                        continue

                    if parse_data_values:
                        if str(cols[0]) not in skip_reports:
                            data = dict([(data_header[idx], value.lstrip(' ').rstrip(' ')) for idx, value in enumerate(cols) if value.lstrip(' ').rstrip(' ')])
                            if 'mätvärdetal' in data:
                                data['mätvärdetal'] = data['mätvärdetal'].replace(decimalsign, '.')

                            if not 'parameter' in data:
                                common_utils.pop_up_info(ru(QCoreApplication.translate('Interlab4Import', "WARNING: Parsing error. The parameter is missing on row %s")) % str(cols))
                                continue

                            if data['lablittera'] not in lab_results:
                                common_utils.pop_up_info(ru(QCoreApplication.translate('Interlab4Import', "WARNING: Parsing error. Data for %s read before it's metadata.")) % data['lablittera'])
                                file_error = True
                                break

                            # If two parameter with the same name exists in the report, use the highest resolution one, that is, the one with the lowest value.
                            existing_data = lab_results[data['lablittera']].get(data['parameter'], None)
                            if existing_data is not None:
                                primary_data, _duplicate_data = self.compare_duplicate_parameters(data, existing_data)

                                lab_results[data['lablittera']][data['parameter']] = primary_data

                                dupl_index = 1
                                duplicate_parname = _duplicate_data['parameter']
                                while duplicate_parname in lab_results[data['lablittera']]:
                                    duplicate_translation = 'dubblett' if midvatten_utils.getcurrentlocale()[0] == 'sv_SE' else 'duplicate'
                                    duplicate_parname = '%s (%s %s)'%(_duplicate_data['parameter'], duplicate_translation, str(dupl_index))
                                    dupl_index += 1
                                else:
                                    _duplicate_data['parameter'] = duplicate_parname
                                    lab_results[data['lablittera']][_duplicate_data['parameter']] = _duplicate_data

                                continue


                            lab_results[data['lablittera']][data['parameter']] = data

                if not file_error:
                    all_lab_results.update(lab_results)
        return all_lab_results

    def parse_filesettings(self, filename):
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
            encoding = midvatten_utils.ask_for_charset(default_charset='utf-16', msg=ru(QCoreApplication.translate('Interlab4Import', 'Give charset used in the file %s'))%filename)
        if encoding is None or not encoding:
            common_utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate('Interlab4Import', 'Charset not given, stopping.')))
            raise common_utils.UserInterruptError()

        #Parse the filedescriptor
        with io.open(filename, 'r', encoding=encoding) as f:
            for rawrow in f:
                if not rawrow.startswith('#'):
                    if any(x is  None for x in (version, decimalsign, quotechar)):
                        file_error = True
                    break

                row = rawrow.lstrip('#').rstrip('\n').lower()
                cols = row.split('=')
                if cols[0].lower() == 'version':
                    version = cols[1]
                elif cols[0].lower() == 'decimaltecken':
                    decimalsign = cols[1]
                elif cols[0].lower() == 'textavgränsare':
                    if cols[1].lower() == 'ja':
                        quotechar = '"'

        return (file_error, version, encoding, decimalsign, quotechar)

    def to_table(self, _data_dict):
        """
        Converts a parsed interlab4 dict into a table for w_qual_lab import

        :param _data_dict:A dict like {<lablittera>: {'metadata': {'metadataheader': value, ...}, <par1_name>: {'dataheader': value, ...}}}
        :return: a list like [['obsid, depth, report, project, staff, date_time, anameth, reading_num, reading_txt, unit, comment'], rows with values]

        The translation from svensktvatten interlab4-keywords to w_qual_lab is from
        http://www.svensktvatten.se/globalassets/dricksvatten/riskanalys-och-provtagning/interlab-4-0.pdf

        """
        data_dict = copy.deepcopy(_data_dict)

        parameter_report_warning_messages = {}

        #### !!!! If a metadata-dbcolumn connection is changed, MetadataFilter.update_table.metaheader_dbcolumn_tooltips MUST be updated as well.

        file_data = [['obsid', 'depth', 'report', 'project', 'staff', 'date_time', 'anameth', 'parameter', 'reading_num', 'reading_txt', 'unit', 'comment']]
        for lablittera, lab_results in data_dict.items():
            metadata = lab_results.pop('metadata')

            obsid = metadata['obsid']
            depth = None
            report = lablittera
            project = metadata.get('projekt', None)
            staff = metadata.get('provtagare', None)

            sampledate = metadata.get('provtagningsdatum', None)
            if sampledate is None:
                common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Interlab4Import', 'Interlab4 import: There was no sample date found (column "provtagningsdatum") for lablittera %s. Importing without it.')) % lablittera)
                date_time = None
            else:
                sampletime = metadata.get('provtagningstid', None)
                if sampletime is not None:
                    date_time = datetime.strftime(datestring_to_date(' '.join([sampledate, sampletime])), '%Y-%m-%d %H:%M:%S')
                else:
                    date_time = datetime.strftime(datestring_to_date(sampledate), '%Y-%m-%d %H:%M:%S')
                    common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Interlab4Import', 'Interlab4 import: There was no sample time found (column "provtagningstid") for lablittera %s. Importing without it.')) % lablittera)

            meta_comment = metadata.get('kommentar', None)
            additional_meta_comments = ['provtagningsorsak',
                                        'provtyp',
                                        'provtypspecifikation',
                                        'bedömning',
                                        'kemisk bedömning',
                                        'mikrobiologisk bedömning',
                                        'provplatsid',
                                        'provplatsnamn',
                                        'specifik provplats']

            #Only keep the comments that really has a value.
            more_meta_comments = '. '.join([': '.join([_x, metadata[_x]]) for _x in [_y for _y in additional_meta_comments if _y in metadata]  if all([metadata[_x], metadata[_x] is not None, metadata[_x].lower() != 'ej bedömt', metadata[_x] != '-'])])
            if not more_meta_comments:
                more_meta_comments = None

            for parameter, parameter_dict in lab_results.items():
                anameth = parameter_dict.get('metodbeteckning', None)

                reading_num = parameter_dict.get('mätvärdetal', None)
                anm = parameter_dict.get('mätvärdetalanm', None)
                reading_txt = parameter_dict.get('mätvärdetext', None)

                if reading_num is None and reading_txt is not None:
                    _reading_txt_replaced = reading_txt.replace('<', '').replace('>', '').replace(',', '.')
                    try:
                        float(_reading_txt_replaced)
                    except ValueError:
                        reading_num = None
                        if parameter not in parameter_report_warning_messages:
                            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Interlab4Import', 'Import interlab4 warning, see log message panel')),
                                                                              log_msg=ru(QCoreApplication.translate('Interlab4Import', 'Could not set reading_num for parameter %s for one or more reports/lablitteras (%s etc.)'))%(
                                                               parameter,
                                                               lablittera))
                        parameter_report_warning_messages.setdefault(parameter, []).append(report)
                    else:
                        reading_num = _reading_txt_replaced

                if reading_txt is None and reading_num is not None:
                    reading_txt = reading_num

                if anm is not None and reading_txt is not None:
                    if not reading_txt.startswith(anm):
                        reading_txt = anm + reading_txt

                unit = parameter_dict.get('enhet', None)
                parameter_comment = parameter_dict.get('kommentar', None)
                additional_parameter_comments = ['rapporteringsgräns',
                                                'detektionsgräns',
                                                'mätosäkerhet',
                                                'mätvärdespår',
                                                'parameterbedömning'
                                                #u'mätvärdetalanm' This is used for creating reading_txt
                                                ]
                more_parameter_comments = '. '.join([': '.join([_x, parameter_dict[_x]]) for _x in [_y for _y in additional_parameter_comments if _y in parameter_dict]  if all([parameter_dict[_x], parameter_dict[_x] is not None, parameter_dict[_x].lower() != 'ej bedömt', parameter_dict[_x] != '-'])])

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
                                  '. '.join([comment for comment in [parameter_comment, meta_comment, more_meta_comments, more_parameter_comments] if comment is not None and comment])]
                                 )

        for parameter, reports in sorted(parameter_report_warning_messages.items()):
            common_utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate('Interlab4Import', 'reading_num could not be set for parameter %s for reports %s')) % (parameter, ', '.join(reports)))

        return file_data
    
    def add_row(self, a_widget):
        """
        :param: a_widget:
        """
        self.main_vertical_layout.addWidget(a_widget)

    def add_line(self, layout=None):
        """ just adds a line"""
        #horizontalLineWidget = PyQt4.QtWidgets.QWidget()
        #horizontalLineWidget.setFixedHeight(2)
        #horizontalLineWidget.setSizePolicy(PyQt4.QtWidgets.QSizePolicy.Expanding, PyQt4.QtWidgets.QSizePolicy.Fixed)
        #horizontalLineWidget.setStyleSheet(PyQt4.QtCore.QString("background-color: #c0c0c0;"));
        line = qgis.PyQt.QtWidgets.QFrame()
        #line.setObjectName(QString::fromUtf8("line"));
        line.setGeometry(qgis.PyQt.QtCore.QRect(320, 150, 118, 3))
        line.setFrameShape(qgis.PyQt.QtWidgets.QFrame.HLine);
        line.setFrameShadow(qgis.PyQt.QtWidgets.QFrame.Sunken);
        if layout is None:
            self.add_row(line)
        else:
            layout.addWidget(line)

    @common_utils.general_exception_handler
    def handle_save(self):
        """
        An extra, non-critical, feature to save metadata (as shown in the gui) as a csv file for examination in other application
        """
        path = ru(qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save File', '', 'CSV(*.csv)')[0])

        if path:
            printlist = [self.metadata_filter.sorted_table_header]

            printlist.extend([[ru(self.metadata_filter.table.item(row, column).text())
                          if self.metadata_filter.table.item(row, column) is not None
                          else ''
                          for column in range(self.metadata_filter.table.columnCount())]
                         for row in range(self.metadata_filter.table.rowCount())])

            common_utils.write_printlist_to_file(path, printlist)
        else:
            common_utils.MessagebarAndLog.info(
                log_msg=ru(QCoreApplication.translate('handle_save', 'No file selected!')))
            raise common_utils.UserInterruptError()

    def unitconversion_factor(self, unit):
        unit_conversion = {'g/l': ('mg/l', 1000.0),
                           'mg/l': ('mg/l', 1.0),
                           'µg/l': ('mg/l', 0.001),
                           'ng/l': ('mg/l', 0.000001),
                           'cfu/ml': ('cfu/ml', 1.0),
                           'cfu/100ml': ('cfu/ml', 0.01),
                           'cfu/10ml': ('cfu/ml', 0.01),
                           'mS/m': ('mS/m', 1.0),
                           'µS/m': ('mS/m', 0.001),
                           'mS/cm': ('mS/m', 100.0),
                           'µS/cm': ('mS/m', 0.001 * 100.0),
                           'g/l Pt': ('mg/l Pt', 1000.0),
                           'mg/l Pt': ('mg/l Pt', 1.0),
                           'µg/l Pt': ('mg/l Pt', 0.001),
                           'ng/l Pt': ('mg/l Pt', 0.000001),
                           'g': ('mg', 1000.0),
                           'mg': ('mg', 1.0),
                           'µg': ('mg', 0.001),
                           'ng': ('mg', 0.000001)
                           }
        return unit_conversion.get(unit, None)


    def get_reading_num(self, reading_num, reading_txt):
        if reading_num is None and reading_txt is not None:
            reading_num = reading_txt.replace('<', '').replace('>', '').replace(',', '.').lstrip().rstrip()
        return reading_num

    def as_float(self, _value):
        if _value is None:
            return None
        try:
            value = float(_value)
        except ValueError:
            value = None
        return value

    def number_of_decimals(self, str_value):
        if self.as_float(str_value) is None:
            return None

        try:
            splitted = str_value.split('.')
        except:
            return None
        if len(splitted) == 0:
            return None
        if len(splitted) == 1:
            return 0
        elif len(splitted) == 2:
            return len(splitted[1])

    def compare_duplicate_parameters(self, new_data, existing_data):
        """
        Compares data when a report has a duplicate parameter and returns the row with the smallest value.

        The smallest value is assumed to be of higher resolution.

        :param new_data:
        :param existing_data:
        :return:
        """
        existing_value = self.get_reading_num(existing_data.get('mätvärdetal', None), existing_data.get('mätvärdetext', None))
        existing_value_float = self.as_float(existing_value)
        existing_unit = existing_data.get('enhet', None)
        new_value = self.get_reading_num(new_data.get('mätvärdetal', None), new_data.get('mätvärdetext', None))
        new_value_float = self.as_float(new_value)
        new_unit = new_data.get('enhet', None)

        # Return new_data as primary data if the existing_data value isn't less.
        primary_data = new_data
        primary_value = new_value
        primary_unit = new_unit
        duplicate_data = existing_data

        done = False

        if new_value_float is None and existing_value_float is not None:
            primary_data = existing_data
            primary_value = existing_value
            primary_unit = existing_unit
            duplicate_data = new_data
        elif new_value_float is not None and existing_value_float is None:
            # Use new data.
            pass

        elif new_value_float is None and existing_value_float is None:
            # No comparison of float values can be made
            pass
        else:
            # Compare number of decimals. Use the one with most decimals. That one is assumed to be of highest resolution
            if existing_unit == new_unit:
                new_nr_of_decimals = self.number_of_decimals(new_value)
                existing_nr_of_decimals = self.number_of_decimals(existing_value)
                if new_nr_of_decimals > existing_nr_of_decimals:
                    pass
                elif new_nr_of_decimals < existing_nr_of_decimals:
                    primary_data = existing_data
                    primary_value = existing_value
                    primary_unit = existing_unit
                    duplicate_data = new_data
                else:
                    # Both have equal length. Use the smallest value. This is assumed to be the best value.
                    if existing_value_float < new_value_float:
                        primary_data = existing_data
                        primary_value = existing_value
                        primary_unit = existing_unit
                        duplicate_data = new_data
            else:
                # Compare the unit factors and use the smallest factor which is assumed to be of highest resolution
                new_unit_factor = self.unitconversion_factor(new_unit)
                existing_unit_factor = self.unitconversion_factor(existing_unit)

                if new_unit_factor and existing_unit_factor:
                    converted_new_unit, new_factor = new_unit_factor
                    converted_existing_unit, existing_factor = existing_unit_factor

                    if converted_new_unit == converted_existing_unit:
                        if existing_factor < new_factor:
                            # Current value is less than previous value, so replace data with new data.
                            primary_data = existing_data
                            primary_value = existing_value
                            primary_unit = existing_unit
                            duplicate_data = new_data

            common_utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate(
                'Interlab4Import', """Duplicate parameter '%s' found! Value and unit ('%s', '%s') was saved as primary parameter out of ('%s', '%s') and ('%s', '%s').""")) % (
                                                       new_data['parameter'],
                                                       primary_value,
                                                       primary_unit,
                                                       existing_value,
                                                       existing_unit,
                                                       new_value,
                                                       new_unit))

        return primary_data, duplicate_data




class MetaFilterSelection(VRowEntry):
    def __init__(self, all_lab_results):
        """

        """
        super(MetaFilterSelection, self).__init__()
        self.layout.addWidget(qgis.PyQt.QtWidgets.QLabel('Column header'))
        self.combobox = qgis.PyQt.QtWidgets.QComboBox()
        if all_lab_results:
            self.update_combobox(all_lab_results)
        self.layout.addWidget(self.combobox)
        self.items = ExtendedQPlainTextEdit()
        self.layout.addWidget(self.items)

    def update_combobox(self, all_lab_results):
        self.combobox.clear()
        self.combobox.addItem('')
        self.combobox.addItems(get_metadata_headers(all_lab_results))

    def get_items_dict(self):
        selected_items = self.items.get_all_data()
        return {ru(self.combobox.currentText()): selected_items}


class MetadataFilter(VRowEntry):
    def __init__(self, all_lab_results):
        """

        """
        self.all_lab_results = all_lab_results
        super(MetadataFilter, self).__init__()


        self.update_selection_button  = qgis.PyQt.QtWidgets.QPushButton('Update selection')
        self.button_layout = RowEntry()
        self.button_layout.layout.addWidget(self.update_selection_button)

        self.show_only_selected_checkbox = qgis.PyQt.QtWidgets.QCheckBox('Show only selected rows')
        self.button_layout.layout.addWidget(self.show_only_selected_checkbox)

        self.layout.addWidget(self.button_layout.widget)

        self.label = qgis.PyQt.QtWidgets.QLabel()
        self.label_layout = RowEntry()
        self.label_layout.layout.addWidget(self.label)

        self.buttonSave = qgis.PyQt.QtWidgets.QPushButton('Save metadata table to file')
        self.buttonSave.setToolTip(ru(QCoreApplication.translate('Interlab4Import','save the metadata table into a csv file for examination in another application')))
        self.label_layout.layout.addWidget(self.buttonSave)

        self.layout.addWidget(self.label_layout.widget)

        self.table = qgis.PyQt.QtWidgets.QTableWidget()
        self.table.setSelectionBehavior(qgis.PyQt.QtWidgets.QAbstractItemView.SelectRows)
        self.table.sizePolicy().setVerticalPolicy(qgis.PyQt.QtWidgets.QSizePolicy.MinimumExpanding)
        self.table.sizePolicy().setVerticalStretch(2)
        self.table.setSelectionMode(qgis.PyQt.QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setSelectionBehavior(qgis.PyQt.QtWidgets.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)

        self.table.itemSelectionChanged.connect(self.update_nr_of_selected)

        self.table_items = {}

        if all_lab_results:
            self.update_table(all_lab_results)
            self.update_nr_of_selected()
        self.layout.addWidget(self.table)


    @common_utils.waiting_cursor
    def set_selection(self, table_header):
        """
        :param table_header: {'table_header': [list of values]}
        :return:
        """
        self.table.clearSelection()
        table_header = {k: [row for row in v if row] for k, v in table_header.items() if k}
        if not table_header:
            return None

        #patterns = {k: [re.compile(x) for x in v] for k, v in table_header.items()}
        patterns = {k: re.compile('|'.join(sorted(v))) for k, v in table_header.items()}

        nr_of_cols = self.table.columnCount()
        nr_of_rows = self.table.rowCount()
        table_header_colnr = dict([(self.table.horizontalHeaderItem(colnr).text(), colnr) for colnr in range(nr_of_cols)])

        """[[self.table.item(rownr, colnr).setSelected(True) for colnr in range(nr_of_cols)]
         for rownr in range(nr_of_rows)
         for header, pattern in patterns.items()
         if re.search(pattern, self.table.item(rownr, table_header_colnr[header]).text())]"""

        mode = QItemSelectionModel.Select | QItemSelectionModel.Rows
        selectedItems = self.table.selectionModel().selection()

        def select(selected_items, table, rownr, mode):
            table.selectRow(rownr)
            selected_items.merge(table.selectionModel().selection(), mode)

        [select(selectedItems, self.table, rownr, mode)
         for rownr in range(nr_of_rows)
         for header, pattern in patterns.items()
         if re.search(pattern, self.table.item(rownr, table_header_colnr[header]).text())]

        self.table.selectionModel().clearSelection()
        self.table.selectionModel().select(selectedItems, mode)

        #Hide all rows that aren't selected
        [(self.table.hideRow(rownr), self.table.item(rownr, 0).setFlags(qgis.PyQt.QtCore.Qt.NoItemFlags))
         if all([not self.table.item(rownr, 0).isSelected(), self.show_only_selected_checkbox.isChecked()])
         else (self.table.showRow(rownr), self.table.item(rownr, 0).setFlags(qgis.PyQt.QtCore.Qt.ItemIsSelectable))
         for rownr in range(nr_of_rows)]



    @common_utils.waiting_cursor
    def update_table(self, all_lab_results):
        """
        all_lab_results: A dict like {<lablittera>: {'metadata': {'metadataheader': value, ...}, <par1_name>: {'dataheader': value, ...}}}
        """
        #Contains only the metadata headers that are hard coded to be put into something else than comment column.
        metaheader_dbcolumn_tooltips = {'lablittera': 'report',
                                        'projekt': 'project',
                                        'provtagare': 'staff',
                                        'provtagningsdatum': 'date_time',
                                        'provtagningstid': 'date_time'}

        self.table.clear()

        self.sorted_table_header = get_metadata_headers(all_lab_results)

        self.table.setColumnCount(len(self.sorted_table_header))
        self.table.setHorizontalHeaderLabels(self.sorted_table_header)
        for head_index, head_text in enumerate(self.sorted_table_header):
            self.table.horizontalHeaderItem(head_index).setToolTip(ru(QCoreApplication.translate('MetadataFilter', '%s will be put into database column "%s"'))%(head_text, metaheader_dbcolumn_tooltips.get(head_text, 'comment')))

        self.table.setRowCount(len(all_lab_results))

        self.table_items = {}
        for rownr, lablittera in enumerate(all_lab_results.keys()):
            metadata = all_lab_results[lablittera]['metadata']
            tablewidgetitem = qgis.PyQt.QtWidgets.QTableWidgetItem(lablittera)
            tablewidgetitem.setFlags(qgis.PyQt.QtCore.Qt.ItemIsSelectable)
            self.table.setItem(rownr, 0, tablewidgetitem)

            for colnr, metaheader in enumerate(self.sorted_table_header[1:], 1):
                tablewidgetitem = qgis.PyQt.QtWidgets.QTableWidgetItem(metadata.get(metaheader, ''))
                tablewidgetitem.setFlags(qgis.PyQt.QtCore.Qt.ItemIsSelectable)
                self.table.setItem(rownr, colnr, tablewidgetitem)

        self.table.resizeColumnsToContents()

        self.table.selectAll()

    def get_selected_lablitteras(self):
        selected_lablitteras = [ru(self.table.item(rownr, 0).text()) for rownr in range(self.table.rowCount()) if self.table.item(rownr, 0).isSelected()]
        return selected_lablitteras

    def get_all_data(self):
        """
        all_lab_results: A dict like {<lablittera>: {'metadata': {'metadataheader': value, ...}, <par1_name>: {'dataheader': value, ...}}}
        :return:
        """
        all_lab_results = {}

        headers = [self.table.horizontalHeaderItem(colnr) for colnr in range(self.table.columnCount())]
        lablittera_colnr = headers.index('lablittera')

        for rownr in range(self.table.rowCount()):
            lablittera = self.table.item(rownr, lablittera_colnr)
            all_lab_results.setdefault(lablittera, {})['metadata'] = dict([(headers[colnr], self.table.item(rownr, colnr)) for colnr in range(self.table.columnCount())])
        return all_lab_results

    def update_nr_of_selected(self):
        labeltext = ru(QCoreApplication.translate('MetadataFilter','Select lablitteras to import'))
        nr_of_selected = str(len(self.get_selected_lablitteras()))
        self.label.setText(' '.join([labeltext, ru(QCoreApplication.translate('MetadataFilter','(%s rows selected)'))%nr_of_selected]))


def get_metadata_headers(all_lab_results):
    table_header = set()

    for k, v in sorted(all_lab_results.items()):
        metadata = v['metadata']
        table_header.update(list(metadata.keys()))

    sorted_table_header = ['lablittera']
    sorted_table_header.extend([head for head in sorted(table_header) if
                                     head not in sorted_table_header])
    return sorted_table_header
