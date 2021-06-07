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
from __future__ import absolute_import
from builtins import str
import io
import os
from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools.utils import common_utils, date_utils, midvatten_utils
from midvatten.tools.utils.common_utils import returnunicode as ru
from midvatten.tools import import_diveroffice


class LeveloggerImport(import_diveroffice.DiverofficeImport):
    def __init__(self, parent, msettings=None):
        super(self.__class__, self).__init__(parent, msettings)
        self.default_charset = 'cp1252'
        self.use_skiprows = True

        self.setWindowTitle(QCoreApplication.translate('LeveloggerImport', "Levelogger import"))  # Set the title for the dialog

        self.parse_func = self.parse_levelogger_file

    @staticmethod
    def parse_levelogger_file(path, charset, skip_rows_without_water_level=False, begindate=None, enddate=None):
        """ Parses a levelogger csv file into a string

        :param path: The file name
        :param existing_obsids: A list or tuple with the obsids that exist in the db.
        :param ask_for_names: (True/False) True to ask for location name for every location. False to only ask if the location is not found in existing_obsids.
        :return: A string representing a table file. Including '\n' for newlines.

        Assumptions and limitations:
        * The Location attribute is used as location and added as a column.
        * Values containing ',' is replaced with '.'
        * Rows with missing "Water head[cm]"-data is skipped.

        """
        #These can be set to paritally import files.
        #begindate = datetime.strptime('2016-06-08 20:00:00','%Y-%m-%d %H:%M:%S')
        #enddate = datetime.strptime('2016-06-08 19:00:00','%Y-%m-%d %H:%M:%S')

        #It should be possible to import all cols that exists in the translation dict

        filedata = []
        location = None
        level_unit_factor_to_cm = 100
        spec_cond_factor_to_mScm = 0.001
        filename = os.path.basename(path)
        if begindate is not None:
            begindate = date_utils.datestring_to_date(begindate)
        if enddate is not None:
            enddate = date_utils.datestring_to_date(enddate)

        with io.open(path, 'rt', encoding=str(charset)) as f:
            rows_unsplit = [row.lstrip().rstrip('\n').rstrip('\r') for row in f]

        try:
            data_header_idx = [rownr for rownr, row in enumerate(rows_unsplit) if row.startswith('Date')][0]
        except IndexError:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('LeveloggerImport',
                                                                                 '''File %s could not be parsed.''')) % filename)
            return [], filename, location

        delimiter = common_utils.get_delimiter_from_file_rows(rows_unsplit[data_header_idx:], filename=filename, delimiters=[';', ','], num_fields=None)

        if delimiter is None:
            return [], filename, location

        rows = [row.split(';') for row in rows_unsplit]
        lens = set([len(row) for row in rows[data_header_idx:]])
        if len(lens) != 1 or list(lens)[0] == 1:
            # Assume that the delimiter was not ';'
            rows = [row.split(',') for row in rows_unsplit]

        col1 = [row[0] for row in rows]

        try:
            location_idx = col1.index('Location:')
        except ValueError:
            pass
        else:
            location = col1[location_idx + 1]

        try:
            level_unit_idx = col1.index('LEVEL')
        except ValueError:
            pass
        else:
            try:
                level_unit = col1[level_unit_idx + 1].split(':')[1].lstrip()
            except IndexError:
                pass
            else:
                if level_unit == 'cm':
                    level_unit_factor_to_cm = 1
                elif level_unit == 'm':
                    level_unit_factor_to_cm = 100
                else:
                    level_unit_factor_to_cm = 100
                    common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('LeveloggerImport', '''The unit for level wasn't m or cm, a factor of %s was used. Check the imported data.''')) % str(level_unit_factor_to_cm))

        file_header = rows[data_header_idx]

        new_header = ['date_time', 'head_cm', 'temp_degc', 'cond_mscm']
        filedata.append(new_header)

        date_colnr = file_header.index('Date')
        time_colnr = file_header.index('Time')
        try:
            level_colnr = file_header.index('LEVEL')
        except ValueError:
            level_colnr = None
        try:
            temp_colnr = file_header.index('TEMPERATURE')
        except ValueError:
            temp_colnr = None
        try:
            spec_cond_colnr = file_header.index('spec. conductivity (uS/cm)')
        except ValueError:
            try:
                spec_cond_colnr = file_header.index('spec. conductivity (mS/cm)')
            except ValueError:
                spec_cond_colnr = None
            else:
                spec_cond_factor_to_mScm = 1
        else:
            spec_cond_factor_to_mScm = 0.001

        try:
            first_data_row = rows[data_header_idx + 1]
        except IndexError:
            common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('LeveloggerImport',
                                                                                 '''No data in file %s.''')) % filename)
            return [], filename, location
        else:
            date_str = ' '.join([first_data_row[date_colnr], first_data_row[time_colnr]])
            date_format = date_utils.datestring_to_date(date_str)
            if date_format is None:
                common_utils.MessagebarAndLog.warning(bar_msg=ru(QCoreApplication.translate('LeveloggerImport',
                                                                                     '''Dateformat in file %s could not be parsed.''')) % filename)
                return [], filename, location

        filedata.extend([[date_utils.long_dateformat(' '.join([row[date_colnr], row[time_colnr]]), date_format),
                          str(float(row[level_colnr].replace(',', '.')) * level_unit_factor_to_cm) if (
                              common_utils.to_float_or_none(row[level_colnr]) is not None if level_colnr is not None else None) else None,
                          str(float(row[temp_colnr].replace(',', '.'))) if (tools.utils.common_utils.to_float_or_none(row[temp_colnr]) if temp_colnr is not None else None) else None,
                          str(float(row[spec_cond_colnr].replace(',', '.')) * spec_cond_factor_to_mScm) if (
                              common_utils.to_float_or_none(row[spec_cond_colnr]) if spec_cond_colnr is not None else None) else None]
                         for row in rows[data_header_idx + 1:]
                         if all([isinstance(tools.utils.common_utils.to_float_or_none(row[level_colnr]), float) if skip_rows_without_water_level else True,
                                 date_utils.datestring_to_date(' '.join([row[date_colnr], row[time_colnr]]), df=date_format) >= begindate if begindate is not None else True,
                                 date_utils.datestring_to_date(' '.join([row[date_colnr], row[time_colnr]]), df=date_format) <= enddate if enddate is not None else True])])


        filedata = [row for row in filedata if any(row[1:])]

        return filedata, filename, location
