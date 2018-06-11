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
import copy
import io
import os
from datetime import datetime

import PyQt4
from PyQt4.QtCore import QCoreApplication

import import_data_to_db
import midvatten_utils as utils
from date_utils import datestring_to_date
from gui_utils import SplitterWithHandel, RowEntry, VRowEntry, ExtendedQPlainTextEdit
from midvatten_utils import Cancel, returnunicode as ru

import_fieldlogger_ui_dialog =  PyQt4.uic.loadUiType(os.path.join(os.path.dirname(__file__),'..','ui', 'import_interlab4.ui'))[0]

class Interlab4Import(PyQt4.QtGui.QMainWindow, import_fieldlogger_ui_dialog):
    def __init__(self, parent, msettings=None):
        self.status = False
        self.iface = parent
        self.ms = msettings
        self.ms.loadSettings()
        PyQt4.QtGui.QDialog.__init__(self, parent)
        self.setAttribute(PyQt4.QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(ru(QCoreApplication.translate(u'Interlab4Import', "Import interlab4 data to w_qual_lab table"))) # Set the title for the dialog
        #self.MainWindow.setWindowTitle("Import interlab4 data to w_qual_lab table")
        self.setupUi(self)  # Required by Qt4 to initialize the UI
        self.status = True

    def parse_observations_and_populate_gui(self):
        filenames = utils.select_files(only_one_file=False,
                                       extension="lab (*.lab)")
        if filenames is None or not filenames:
            return Cancel()
        
        self.all_lab_results = self.parse(filenames)

        splitter = SplitterWithHandel(PyQt4.QtCore.Qt.Vertical)
        self.main_vertical_layout.addWidget(splitter)

        self.specific_meta_filter = MetaFilterSelection(self.all_lab_results)

        splitter.addWidget(self.specific_meta_filter.widget)

        self.metadata_filter = MetadataFilter(self.all_lab_results, self.connect)
        splitter.addWidget(self.metadata_filter.widget)

        self.connect(self.metadata_filter.update_selection_button, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.metadata_filter.set_selection(self.specific_meta_filter.get_items_dict()))

        self.start_import_button = PyQt4.QtGui.QPushButton(ru(QCoreApplication.translate(u'Interlab4Import', u'Start import')))
        self.gridLayout_buttons.addWidget(self.start_import_button, 0, 0)
        self.connect(self.start_import_button, PyQt4.QtCore.SIGNAL("clicked()"), lambda : self.start_import(self.all_lab_results, self.metadata_filter.get_selected_lablitteras()))

        self.help_label = PyQt4.QtGui.QLabel(ru(QCoreApplication.translate(u'Interlab4Import', u'Instructions')))
        self.help_label.setToolTip(ru(QCoreApplication.translate(u'Interlab4Import',
                                   u'Selected rows (lablitteras in the bottom table will be imported when pushing "Start import" button.\n'
                                   u'The table can be sorted by clicking the column headers.\n\n'
                                   u'Rows at the bottom table can also be selected using the top list.\n'
                                   u'Howto:\n'
                                   u'1. Choose column header to make a selection by in the Column header drop down list.\n'
                                   u'2. Make a list of entries (one row per entry).\n'
                                   u'3. Click "Update selection".\n'
                                   u'All rows where values in the chosen column match entries in the pasted list will be selected.\n\n'
                                   u'Hover over a column header to see which database column it will go to.')))

        self.close_after_import = PyQt4.QtGui.QCheckBox(ru(QCoreApplication.translate(u'Interlab4Import', u'Close dialog after import')))
        self.close_after_import.setChecked(True)
        self.gridLayout_buttons.addWidget(self.close_after_import, 0, 0)

        self.gridLayout_buttons.addWidget(self.start_import_button, 1, 0)
        self.gridLayout_buttons.addWidget(self.help_label, 2, 0)
        self.gridLayout_buttons.setRowStretch(3, 1)

        self.show()

    @utils.general_exception_handler
    @import_data_to_db.import_exception_handler
    def start_import(self, all_lab_results, lablitteras_to_import):
        all_lab_results = copy.deepcopy(all_lab_results)
        all_lab_results = dict([(lablittera, v) for lablittera, v in all_lab_results.iteritems() if lablittera in lablitteras_to_import])

        #Allow the user to connect the metadata rows to obsids.
        meta_headers = get_metadata_headers(all_lab_results)
        ask_obsid_table = [meta_headers]
        for lablittera, v in sorted(all_lab_results.iteritems()):
            metarow = [v[u'metadata'].get(meta_header, u'') for meta_header in meta_headers]
            ask_obsid_table.append(metarow)
        existing_obsids = utils.get_all_obsids()
        answer = utils.filter_nonexisting_values_and_ask(ask_obsid_table, u'obsid', existing_values=existing_obsids, try_capitalize=False, always_ask_user=True)
        if answer == u'cancel':
            self.status = True
            return Cancel()
        elif not answer:
            self.status = False
            utils.MessagebarAndLog.critical(bar_msg=u'Error, no observations remain. No import done.')
            return Cancel()
        else:
            remaining_lablitteras_obsids = dict([(x[0], x[-1]) for x in answer[1:]])
        #Filter the remaining lablitteras and add an obsid field
        _all_lab_results = {}
        for lablittera, v in all_lab_results.iteritems():
            if lablittera in remaining_lablitteras_obsids:
                v[u'metadata'][u'obsid'] = remaining_lablitteras_obsids[lablittera]
                _all_lab_results[lablittera] = v
        all_lab_results = _all_lab_results

        self.wquallab_data_table = self.to_table(all_lab_results)

        importer = import_data_to_db.midv_data_importer()
        answer = importer.general_import(goal_table=u'w_qual_lab', file_data=self.wquallab_data_table)

        importer.SanityCheckVacuumDB()

        if self.close_after_import.isChecked():
            self.close()

        PyQt4.QtGui.QApplication.restoreOverrideCursor()

    def parse(self, filenames):
        """ Reads the interlab
        :param filenames:
        :return: A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        """
        all_lab_results = {}

        for filename in filenames:
            file_settings = self.parse_filesettings(filename)
            file_error, version, encoding, decimalsign, quotechar = file_settings
            if file_error:
                utils.pop_up_info(ru(QCoreApplication.translate(u'Interlab4Import', u"Warning: The file information %s could not be read. Skipping file"))%filename)
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

                    #cols = ru(cols, keep_containers=True)

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
                            utils.pop_up_info(ru(QCoreApplication.translate(u'Interlab4Import', "WARNING: Parsing error. The parameter is missing on row %s"))%str(cols))
                            continue

                        if data[u'lablittera'] not in lab_results:
                            utils.pop_up_info(ru(QCoreApplication.translate(u'Interlab4Import', "WARNING: Parsing error. Data for %s read before it's metadata."))%data['lablittera'])
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
                        if u'kalium' in data[u'parameter'].lower():
                            current_kalium_name = data[u'parameter'].lower()
                            existing_same_names = [x for x in lab_results[data[u'lablittera']] if x == current_kalium_name]
                            if not existing_same_names:
                                #kalium has not been parsed yet. Keep the current one.
                                pass
                            else:
                                parameter_chosen = False
                                #Method 1: Use mätosäkerhet to find the high resolution kalium.
                                _previous_resolution = lab_results[data[u'lablittera']][current_kalium_name].get(u'mätosäkerhet', u'')
                                previous_resolution = _previous_resolution.replace(u'±', u'').replace(u'<', u'')
                                _current_resolution = data.get(u'mätosäkerhet', u'')
                                current_resolution = _current_resolution.replace(u'±', u'').replace(u'<', u'')
                                if previous_resolution and current_resolution:
                                    try:
                                        previous_resolution = float(previous_resolution)
                                        current_resolution = float(current_resolution)
                                    except ValueError:
                                        #mätosäkerhet could not be used. Try the other method
                                        parameter_chosen = False
                                        pass
                                    else:
                                        if previous_resolution > current_resolution:
                                            # The current one is the high resolution one. Keep it to overwrite the other one.
                                            parameter_chosen = True
                                            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Kalium was found more than once. The one with mätosäkerhet %s was used."'))%_current_resolution)
                                        elif current_resolution > previous_resolution:
                                            # The current one is the low resolution one, skip it.
                                            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Kalium was found more than once. The one with mätosäkerhet %s was used."'))%_previous_resolution)
                                            parameter_chosen = True
                                            continue
                                        elif current_resolution == previous_resolution:
                                            # This method could not be used to find the high resolution one. Try the other method.
                                            parameter_chosen = False

                                if not parameter_chosen:
                                    current_txt = data.get(u'mätvärdetext', u'').strip(u' ')
                                    previous_txt = lab_results[data[u'lablittera']][current_kalium_name].get(u'mätvärdetext', u'')
                                    #Method 2: Use < and <2.5 limits to try to find the high resolution one.
                                    if current_txt == u'<1' or previous_txt.strip(u' ').replace(u',', u'.') == u'<2.5':
                                        #The current one is the high resolution one. Keep it to overwrite the other one.
                                        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Kalium was found more than once. The one with mätvärdetext %s was used."'))%current_txt)
                                        pass
                                    elif current_txt == u'<2.5' or previous_txt.strip(u' ') == u'<1':
                                        #The current one is the low resolution one, skip it.
                                        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Kalium was found more than once. The one with mätvärdetext %s was used."'))%previous_txt)
                                        continue
                                    else:
                                        utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Kalium was found more than once. The high resolution one could not be found. The one with mätvärdetext %s was used."'))%current_txt)
                                        #Hope that the current one (the last one) is the high resolution one and let it overwrite the existing one
                                        pass

                        lab_results[data[u'lablittera']][data[u'parameter']] = data

                        continue
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
            encoding = utils.ask_for_charset(default_charset='utf-16', msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Give charset used in the file %s'))%filename)
        if encoding is None or not encoding:
            utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Charset not given, stopping.')))
            raise utils.UserInterruptError()

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

    def to_table(self, _data_dict):
        """
        Converts a parsed interlab4 dict into a table for w_qual_lab import

        :param _data_dict:A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        :return: a list like [[u'obsid, depth, report, project, staff, date_time, anameth, reading_num, reading_txt, unit, comment'], rows with values]

        The translation from svensktvatten interlab4-keywords to w_qual_lab is from
        http://www.svensktvatten.se/globalassets/dricksvatten/riskanalys-och-provtagning/interlab-4-0.pdf

        """
        data_dict = copy.deepcopy(_data_dict)

        parameter_report_warning_messages = {}

        #### !!!! If a metadata-dbcolumn connection is changed, MetadataFilter.update_table.metaheader_dbcolumn_tooltips MUST be updated as well.

        file_data = [[u'obsid', u'depth', u'report', u'project', u'staff', u'date_time', u'anameth', u'parameter', u'reading_num', u'reading_txt', u'unit', u'comment']]
        for lablittera, lab_results in data_dict.iteritems():
            metadata = lab_results.pop(u'metadata')

            obsid = metadata[u'obsid']
            depth = None
            report = lablittera
            project = metadata.get(u'projekt', None)
            staff = metadata.get(u'provtagare', None)

            sampledate = metadata.get(u'provtagningsdatum', None)
            if sampledate is None:
                utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Interlab4 import: There was no sample date found (column "provtagningsdatum") for lablittera %s. Importing without it.'))%lablittera)
                date_time = None
            else:
                sampletime = metadata.get(u'provtagningstid', None)
                if sampletime is not None:
                    date_time = datetime.strftime(datestring_to_date(u' '.join([sampledate, sampletime])), u'%Y-%m-%d %H:%M:%S')
                else:
                    date_time = datetime.strftime(datestring_to_date(sampledate), u'%Y-%m-%d %H:%M:%S')
                    utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Interlab4 import: There was no sample time found (column "provtagningstid") for lablittera %s. Importing without it.'))%lablittera)

            meta_comment = metadata.get(u'kommentar', None)
            additional_meta_comments = [u'provtagningsorsak',
                                        u'provtyp',
                                        u'provtypspecifikation',
                                        u'bedömning',
                                        u'kemisk bedömning',
                                        u'mikrobiologisk bedömning',
                                        u'provplatsid',
                                        u'provplatsnamn',
                                        u'specifik provplats']

            #Only keep the comments that really has a value.
            more_meta_comments = u'. '.join([u': '.join([_x, metadata[_x]]) for _x in [_y for _y in additional_meta_comments if _y in metadata]  if all([metadata[_x], metadata[_x] is not None, metadata[_x].lower() != u'ej bedömt', metadata[_x] != u'-'])])
            if not more_meta_comments:
                more_meta_comments = None

            for parameter, parameter_dict in lab_results.iteritems():
                anameth = parameter_dict.get(u'metodbeteckning', None)

                reading_num = parameter_dict.get(u'mätvärdetal', None)
                anm = parameter_dict.get(u'mätvärdetalanm', None)
                reading_txt = parameter_dict.get(u'mätvärdetext', None)

                if reading_num is None and reading_txt is not None:
                    _reading_txt_replaced = reading_txt.replace(u'<', u'').replace(u'>', u'').replace(u',', u'.')
                    try:
                        float(_reading_txt_replaced)
                    except ValueError:
                        reading_num = None
                        if parameter not in parameter_report_warning_messages:
                            utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Import interlab4 warning, see log message panel')),
                                                           log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'Could not set reading_num for parameter %s for one or more reports/lablitteras (%s etc.)'))%(
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

                unit = parameter_dict.get(u'enhet', None)
                parameter_comment = parameter_dict.get(u'kommentar', None)
                additional_parameter_comments = [u'rapporteringsgräns',
                                                u'detektionsgräns',
                                                u'mätosäkerhet',
                                                u'mätvärdespår',
                                                u'parameterbedömning'
                                                #u'mätvärdetalanm' This is used for creating reading_txt
                                                ]
                more_parameter_comments = u'. '.join([u': '.join([_x, parameter_dict[_x]]) for _x in [_y for _y in additional_parameter_comments if _y in parameter_dict]  if all([parameter_dict[_x], parameter_dict[_x] is not None, parameter_dict[_x].lower() != u'ej bedömt', parameter_dict[_x] != u'-'])])

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
                                  u'. '.join([comment for comment in [parameter_comment, meta_comment, more_meta_comments, more_parameter_comments] if comment is not None and comment])]
                                 )

        for parameter, reports in sorted(parameter_report_warning_messages.iteritems()):
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'Interlab4Import', u'reading_num could not be set for parameter %s for reports %s'))%(parameter, u', '.join(reports)))

        return file_data
    
    def add_row(self, a_widget):
        """
        :param: a_widget:
        """
        self.main_vertical_layout.addWidget(a_widget)

    def add_line(self, layout=None):
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
        if layout is None:
            self.add_row(line)
        else:
            layout.addWidget(line)


class MetaFilterSelection(VRowEntry):
    def __init__(self, all_lab_results):
        """

        """
        super(MetaFilterSelection, self).__init__()
        self.layout.addWidget(PyQt4.QtGui.QLabel(u'Column header'))
        self.combobox = PyQt4.QtGui.QComboBox()
        self.combobox.addItem(u'')
        self.combobox.addItems(get_metadata_headers(all_lab_results))
        self.layout.addWidget(self.combobox)
        self.items = ExtendedQPlainTextEdit()
        self.layout.addWidget(self.items)

    def get_items_dict(self):
        selected_items = self.items.get_all_data()
        return {ru(self.combobox.currentText()): selected_items}


class MetadataFilter(VRowEntry):
    def __init__(self, all_lab_results, connect):
        """

        """
        self.all_lab_results = all_lab_results
        super(MetadataFilter, self).__init__()
        self.connect = connect

        self.update_selection_button  = PyQt4.QtGui.QPushButton(u'Update selection')
        self.button_layout = RowEntry()
        self.button_layout.layout.addWidget(self.update_selection_button)

        self.show_only_selected_checkbox = PyQt4.QtGui.QCheckBox(u'Show only selected rows')
        self.button_layout.layout.addWidget(self.show_only_selected_checkbox)

        self.layout.addWidget(self.button_layout.widget)

        self.label = PyQt4.QtGui.QLabel()
        self.layout.addWidget(self.label)

        self.table = PyQt4.QtGui.QTableWidget()
        self.table.setSelectionBehavior(PyQt4.QtGui.QAbstractItemView.SelectRows)
        self.table.sizePolicy().setVerticalPolicy(PyQt4.QtGui.QSizePolicy.MinimumExpanding)
        self.table.sizePolicy().setVerticalStretch(2)
        self.table.setSelectionMode(PyQt4.QtGui.QAbstractItemView.ExtendedSelection)
        self.table.setSelectionBehavior(PyQt4.QtGui.QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)

        self.connect(self.table, PyQt4.QtCore.SIGNAL("itemSelectionChanged()"), self.update_nr_of_selected)

        self.table_items = {}

        self.update_table(all_lab_results)
        self.update_nr_of_selected()
        self.layout.addWidget(self.table)


    @utils.waiting_cursor
    def set_selection(self, table_header):
        """
        :param table_header: {u'table_header': [list of values]}
        :return:
        """
        self.table.clearSelection()
        table_header = {k: v for k, v in table_header.iteritems() if k}
        if not table_header:
            return None
        nr_of_cols = self.table.columnCount()
        nr_of_rows = self.table.rowCount()
        table_header_colnr = dict([(self.table.horizontalHeaderItem(colnr).text(), colnr) for colnr in xrange(nr_of_cols)])

        """
        [[self.table.setItemSelected(self.table.item(rownr, colnr), True) for colnr in xrange(nr_of_cols)]
         for header, selectionlist in table_header.iteritems()
         for rownr in xrange(nr_of_rows)
         for rexp in selectionlist
         if re.search(rexp, self.table.item(rownr, table_header_colnr[header]).text())]
        """

        #Select all items for chosen rows.

        [[self.table.setItemSelected(self.table.item(rownr, colnr), True) for colnr in xrange(nr_of_cols)]
         for header, selectionlist in table_header.iteritems()
         for rownr in xrange(nr_of_rows)
         if self.table.item(rownr, table_header_colnr[header]).text() in selectionlist]

        #Hide all rows that aren't selected
        [(self.table.hideRow(rownr), self.table.item(rownr, 0).setFlags(PyQt4.QtCore.Qt.NoItemFlags))
         if all([not self.table.item(rownr, 0).isSelected(), self.show_only_selected_checkbox.isChecked()])
         else (self.table.showRow(rownr), self.table.item(rownr, 0).setFlags(PyQt4.QtCore.Qt.ItemIsSelectable))
         for rownr in xrange(nr_of_rows)]

    @utils.waiting_cursor
    def update_table(self, all_lab_results):
        """
        all_lab_results: A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        """
        #Contains only the metadata headers that are hard coded to be put into something else than comment column.
        metaheader_dbcolumn_tooltips = {u'lablittera': u'report',
                                        u'projekt': u'project',
                                        u'provtagare': u'staff',
                                        u'provtagningsdatum': u'date_time',
                                        u'provtagningstid': u'date_time'}

        self.table.clear()

        self.sorted_table_header = get_metadata_headers(all_lab_results)

        self.table.setColumnCount(len(self.sorted_table_header))
        self.table.setHorizontalHeaderLabels(self.sorted_table_header)
        for head_index, head_text in enumerate(self.sorted_table_header):
            self.table.horizontalHeaderItem(head_index).setToolTip(ru(QCoreApplication.translate(u'MetadataFilter', u'%s will be put into database column "%s"'))%(head_text, metaheader_dbcolumn_tooltips.get(head_text, u'comment')))

        self.table.setRowCount(len(all_lab_results))

        self.table_items = {}
        for rownr, lablittera in enumerate(all_lab_results.keys()):
            metadata = all_lab_results[lablittera][u'metadata']
            tablewidgetitem = PyQt4.QtGui.QTableWidgetItem(lablittera)
            tablewidgetitem.setFlags(PyQt4.QtCore.Qt.ItemIsSelectable)
            self.table.setItem(rownr, 0, tablewidgetitem)

            for colnr, metaheader in enumerate(self.sorted_table_header[1:], 1):
                tablewidgetitem = PyQt4.QtGui.QTableWidgetItem(metadata.get(metaheader, u''))
                tablewidgetitem.setFlags(PyQt4.QtCore.Qt.ItemIsSelectable)
                self.table.setItem(rownr, colnr, tablewidgetitem)

        self.table.resizeColumnsToContents()

        self.table.selectAll()

    def get_selected_lablitteras(self):
        selected_lablitteras = [ru(self.table.item(rownr, 0).text()) for rownr in xrange(self.table.rowCount()) if self.table.item(rownr, 0).isSelected()]
        return selected_lablitteras

    def get_all_data(self):
        """
        all_lab_results: A dict like {<lablittera>: {u'metadata': {u'metadataheader': value, ...}, <par1_name>: {u'dataheader': value, ...}}}
        :return:
        """
        all_lab_results = {}

        headers = [self.table.horizontalHeaderItem(colnr) for colnr in xrange(self.table.columnCount())]
        lablittera_colnr = headers.index(u'lablittera')

        for rownr in xrange(self.table.rowCount()):
            lablittera = self.table.item(rownr, lablittera_colnr)
            all_lab_results.setdefault(lablittera, {})[u'metadata'] = dict([(headers[colnr], self.table.item(rownr, colnr)) for colnr in xrange(self.table.columnCount())])
        return all_lab_results

    def update_nr_of_selected(self):
        labeltext = ru(QCoreApplication.translate(u'MetadataFilter',u'Select lablitteras to import'))
        nr_of_selected = str(len(self.get_selected_lablitteras()))
        self.label.setText(u' '.join([labeltext, ru(QCoreApplication.translate(u'MetadataFilter',u'(%s rows selected)'))%nr_of_selected]))


def get_metadata_headers(all_lab_results):
    table_header = set()

    for k, v in sorted(all_lab_results.iteritems()):
        metadata = v[u'metadata']
        table_header.update(metadata.keys())

    sorted_table_header = [u'lablittera']
    sorted_table_header.extend([head for head in table_header if
                                     head not in sorted_table_header])
    return sorted_table_header