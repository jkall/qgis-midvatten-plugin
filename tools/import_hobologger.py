# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles importing of data to the database
  from the levelogger format.

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
import csv
import datetime
import os
import re
from functools import partial

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools import import_diveroffice
from midvatten.tools.utils import common_utils, date_utils, gui_utils
from midvatten.tools.utils.common_utils import returnunicode as ru


class HobologgerImport(import_diveroffice.DiverofficeImport):
    def __init__(self, parent, msettings=None):
        super(self.__class__, self).__init__(parent, msettings)
        self.default_charset = 'utf8'
        self.use_skiprows = False

        self.setWindowTitle(QCoreApplication.translate('HobologgerImport', "Hobologger import"))  # Set the title for the dialog

        self.tz_converter = TzConverter()

        self.add_row(self.tz_converter.widget)

        self.parse_func = partial(self.parse_hobologger_file, tz_converter=self.tz_converter)


    @staticmethod
    def parse_hobologger_file(path, charset, skip_rows_without_water_level=False, begindate=None, enddate=None, tz_converter=None):
        """ Parses a HOBO temperature logger csv file into a string

        :param path: The file name
        :param charset:
        :param skip_rows_without_water_level:
        :param begindate:
        :param enddate:
        :param tz_converter: A TzConverter object.
        :return:

        """

        filedata = []
        location = None
        filename = os.path.basename(path)
        if begindate is not None:
            begindate = date_utils.datestring_to_date(begindate)
        if enddate is not None:
            enddate = date_utils.datestring_to_date(enddate)

        with open(path, 'rt', encoding=str(charset)) as f:
            rows_unsplit = [row.lstrip().rstrip('\n').rstrip('\r') for row in f]
            csvreader = csv.reader(rows_unsplit, delimiter=',', quotechar='"')

        rows = [ru(row, keep_containers=True) for row in csvreader]

        try:
            data_header_idx = [rownr for rownr, row in enumerate(rows) if 'Date Time' in '_'.join(row)][0]
        except IndexError:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('Hobologger import',
                                                                                 '''File %s could not be parsed.''')) % filename)
            return [], filename, location

        date_colnr = [idx for idx, col in enumerate(rows[1]) if 'Date Time' in col]
        if not date_colnr:
            raise Exception(ru(QCoreApplication.translate('Hobologger import', 'Date Time column not found!')))
        else:
            date_colnr = date_colnr[0]

        if tz_converter:
            tz_string = get_tz_string(rows[1][date_colnr])
            if tz_string is None:
                common_utils.MessagebarAndLog.warning(
                    bar_msg=ru(QCoreApplication.translate('Hobologger import', 'Timezone not found in %s')) % filename)
            tz_converter.source_tz = tz_string

        temp_colnr = [idx for idx, col in enumerate(rows[1]) if 'Temp, °C' in col]
        if not temp_colnr:
            raise Exception(ru(QCoreApplication.translate('Hobologger import', 'Temperature column not found!')))
        else:
            temp_colnr = temp_colnr[0]

        match = re.search('LBL: ([A-Za-z0-9_\-]+)', rows[1][temp_colnr])
        if not match:
            location = filename
        else:
            location = match.group(1)

        new_header = ['date_time', 'head_cm', 'temp_degc', 'cond_mscm']
        filedata.append(new_header)

        try:
            first_data_row = rows[data_header_idx + 1]
        except IndexError:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('HobologgerImport',
                                                                                 '''No data in file %s.''')) % filename)
            return [], filename, location
        else:
            dt = first_data_row[date_colnr]
            date_format = date_utils.find_date_format(dt, suppress_error_msg=True)
            if date_format is None:
                dt = first_data_row[date_colnr][:-2].rstrip()
                date_format = date_utils.find_date_format(dt)
                if date_format is None:
                    common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('HobologgerImport',
                                                                                         '''Dateformat in file %s could not be parsed.''')) % filename)
                    return [], filename, location

        filedata.extend([[date_utils.long_dateformat(fix_date(row[date_colnr], filename, tz_converter)),
                              '',
                          str(float(row[temp_colnr].replace(',', '.'))) if (
                              common_utils.to_float_or_none(row[temp_colnr]) if temp_colnr is not None else None) else '',
                              '']
                        for row in rows[data_header_idx + 1:]
                        if all([fix_date(row[date_colnr], filename, tz_converter) >= begindate if begindate is not None else True,
                                fix_date(row[date_colnr], filename, tz_converter) <= enddate if enddate is not None else True])])

        filedata = [row for row in filedata if any(row[1:])]

        return filedata, filename, location


def fix_date(date_time, filename, tz_converter=None):
    try:
        dt = datetime.datetime.strptime(date_time[:-2].rstrip(), '%m/%d/%y %I:%M:%S')
    except ValueError:
        dt = date_utils.datestring_to_date(date_time)
        if dt is None:
            raise FileError(ru(QCoreApplication.translate('HobologgerImport',
                                                          '''Dateformat in file %s could not be parsed.''')) % filename)
    else:
        dt_end = date_time[-2:]
        if dt_end.lower() in ('em', 'pm'):
            dt = date_utils.dateshift(dt, 12, 'hours')

    if tz_converter is not None:
        dt = tz_converter.convert_datetime(dt)

    return dt


def get_tz_string(date_time_tz):
    """

    :param date_time_tz:
    :return:

    >>> get_tz_string('Date Time, GMT+02:00')
    'GMT+02:00'
    >>> get_tz_string('Date Time, GMT+2')
    'GMT+2'
    >>> get_tz_string('Date Time, GMT')
    'GMT'
    >>> get_tz_string('Date Time, GMT-2:00')
    'GMT-2:00'

    """
    match = re.match('Date Time, ([A-Za-z0-9\+\-\:]+)', date_time_tz, re.IGNORECASE)
    if not match:
        return None
    else:
        return match.group(1)

class TzConverter(gui_utils.RowEntry):
    def __init__(self):
        super(TzConverter, self).__init__()
        self.source_tz = None
        self.label = QtWidgets.QLabel(ru(QCoreApplication.translate('TzSelector', 'Select target timezone: ')))
        timezones = ['GMT{:+d}'.format(x) for x in range(-11, 15)]

        self._tz_list = QtWidgets.QComboBox()
        self._tz_list.addItems(timezones)

        for widget in [self.label, self._tz_list]:
            self.layout.addWidget(widget)

        self.target_tz = 'GMT+1'

        self.layout.addStretch()

    def convert_datetime(self, date_time):
        if self.source_tz is None:
            return date_time

        source_td = date_utils.parse_timezone_to_timedelta(self.source_tz)
        target_td = date_utils.parse_timezone_to_timedelta(self.target_tz)

        diff = target_td - source_td

        if diff == 0:
            return date_time
        else:
            new_date = date_utils.datestring_to_date(date_time) + diff
            return new_date

    @property
    def target_tz(self):
        return (self._tz_list.currentText())

    @target_tz.setter
    def target_tz(self, value):
        gui_utils.set_combobox(self._tz_list, value)

class FileError(Exception):
    pass