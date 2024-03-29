# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  diveroffice files.

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-03-08
        copyright            : (C) 2016 by joskal (HenrikSpa)
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

import os
from builtins import object

import mock
from midvatten.tools.utils.date_utils import datestring_to_date
from nose.plugins.attrib import attr

from midvatten.tools.utils import common_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.tests.mocks_for_tests import MockReturnUsingDictIn
from midvatten.tools.import_diveroffice import DiverofficeImport


#


@attr(status='on')
class TestParseDiverofficeFile(object):
    utils_ask_user_about_stopping = MockReturnUsingDictIn({'Failure, delimiter did not match': 'cancel',
                                                           'Failure: The number of data columns in file': 'cancel',
                                                           'Failure, parsing failed for file': 'cancel'},
                                                          0)

    def setUp(self):
        pass

    def test_parse_diveroffice_file_utf8(self):

        f = ('Location=rb1',
             'Date/time,Water head[cm],Temperature[°C]',
             '2016/03/15 10:30:00,26.9,5.18',
             '2016/03/15 11:00:00,157.7,0.6'
             )

        charset_of_diverofficefile = 'utf-8'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)


        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'

    def test_parse_diveroffice_file_cp1252(self):

        f = ('Location=rb1',
             'Date/time,Water head[cm],Temperature[°C]',
             '2016/03/15 10:30:00,26.9,5.18',
             '2016/03/15 11:00:00,157.7,0.6'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'

    def test_parse_diveroffice_file_semicolon_sep(self):

        f = ('Location=rb1',
             'Date/time;Water head[cm];Temperature[°C]',
             '2016/03/15 10:30:00;26.9;5.18',
             '2016/03/15 11:00:00;157.7;0.6'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'

    def test_parse_diveroffice_file_comma_dec(self):

        f = ('Location=rb1',
             'Date/time;Water head[cm];Temperature[°C]',
             '2016/03/15 10:30:00;26,9;5,18',
             '2016/03/15 11:00:00;157,7;0,6'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = r'''[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'''
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'

    @mock.patch('midvatten.tools.import_data_to_db.common_utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_parse_diveroffice_file_comma_sep_comma_dec_failed(self):
        f = ('Location=rb1',
             'Date/time,Water head[cm],Temperature[°C]',
             '2016/03/15 10:30:00,26,9,5,18',
             '2016/03/15 11:00:00,157,7,0,6'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = 'cancel'
        assert test_string == reference_string

    @mock.patch('midvatten.tools.import_data_to_db.common_utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_parse_diveroffice_file_different_separators_failed(self):

        f = ('Location=rb1',
             'Date/time,Water head[cm],Temperature[°C]',
             '2016/03/15 10:30:00;26,9;5,18',
             '2016/03/15 11:00:00;157,7;0,6'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = 'cancel'
        assert test_string == reference_string

    def test_parse_diveroffice_file_changed_order(self):
        f = ('Location=rb1',
             'Temperature[°C];2:Spec.cond.[mS/cm];Date/time;Water head[cm]',
             '5.18;2;2016/03/15 10:30:00;26.9',
             '0.6;3;2016/03/15 11:00:00;157.7'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, 2.0], [2016-03-15 11:00:00, 157.7, 0.6, 3.0]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'

    @mock.patch("midvatten.tools.import_diveroffice.common_utils.MessagebarAndLog")
    def test_parse_diveroffice_warning_missing_head_cm(self, mock_messagebarandlog):
        f = ('Location=rb1',
             'Temperature[°C];2:Spec.cond.[mS/cm];Date/time',
             '5.18;2;2016/03/15 10:30:00',
             '0.6;3;2016/03/15 11:00:00'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
            file_data = DiverofficeImport.parse_diveroffice_file_old(path,
                                                                   charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, , 5.18, 2.0], [2016-03-15 11:00:00, , 0.6, 3.0]]'

        assert len(mock_messagebarandlog.mock_calls) == 1
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'

    @mock.patch("midvatten.tools.import_diveroffice.common_utils.MessagebarAndLog")
    def test_parse_diveroffice_warning_missing_date_time(self, mock_messagebarandlog):
        f = ('Location=rb1',
             'Temperature[°C];2:Spec.cond.[mS/cm];dada',
             '5.18;2;2016/03/15 10:30:00',
             '0.6;3;2016/03/15 11:00:00'
             )

        charset_of_diverofficefile = 'cp1252'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
            file_data = DiverofficeImport.parse_diveroffice_file_old(path,
                                                                   charset_of_diverofficefile)

        assert file_data == 'skip'
        assert len(mock_messagebarandlog.mock_calls) == 1

    @mock.patch("midvatten.tools.import_diveroffice.common_utils.MessagebarAndLog")
    def test_parse_diveroffice_get_timezone(self, mock_messagebarandlog):

        f = ('Location=rb1',
             'Instrument number       =UTC+1',
             'Date/time,Water head[cm],Temperature[°C]',
             '2016/03/15 10:30:00,26.9,5.18',
             '2016/03/15 11:00:00,157.7,0.6'
             )

        charset_of_diverofficefile = 'utf-8'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file_old(path, charset_of_diverofficefile)


        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'
        assert file_data[3] == 'UTC+1'

    @mock.patch("midvatten.tools.import_diveroffice.common_utils.MessagebarAndLog")
    def test_parse_diveroffice_comma_missing_head_cm_value(self, mock_messagebarandlog):
        f = ('[Logger settings]',
                  'Location=rb1',
                  '[Channel 1]',
                  'Identification          =LEVEL',
                  '[Channel 2]',
                  'Identification          =TEMPERATURE',
                  '',
                  'Date/time;Water head[cm];Temperature[°C]',
                  '2016/03/15 10:30:00;1,2;10',
                  '2016/03/15 11:00:00;    ;101',
                  'END OF DATA FILE OF DATALOGGER FOR WINDOWS',
                  '    ')

        charset_of_diverofficefile = 'utf-8'
        with common_utils.tempinput('\n'.join(f), charset_of_diverofficefile, suffix='.csv') as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)


        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 1.2, 10, None], [2016-03-15 11:00:00, None, 101, None]]'

        print(f"Ref: {reference_string}\ntest: {test_string}")
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'rb1'



@attr(status='on')
class TestFilterDatesFromFiledata(object):

    def test_filter_dates_from_filedata(self):

        file_data = [['obsid', 'date_time'], ['rb1', '2015-05-01 00:00:00'], ['rb1', '2016-05-01 00:00'], ['rb2', '2015-05-01 00:00:00'], ['rb2', '2016-05-01 00:00'], ['rb3', '2015-05-01 00:00:00'], ['rb3', '2016-05-01 00:00']]
        obsid_last_imported_dates = {'rb1': [(datestring_to_date('2016-01-01 00:00:00'),)], 'rb2': [(datestring_to_date('2017-01-01 00:00:00'),)]}
        test_file_data = utils_for_tests.create_test_string(DiverofficeImport.filter_dates_from_filedata(file_data, obsid_last_imported_dates))

        reference_file_data = '''[[obsid, date_time], [rb1, 2016-05-01 00:00], [rb3, 2015-05-01 00:00:00], [rb3, 2016-05-01 00:00]]'''

        assert test_file_data == reference_file_data