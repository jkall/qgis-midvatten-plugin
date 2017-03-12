# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  measurements.

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
#
import db_utils
import utils_for_tests
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from db_utils import get_foreign_keys
from tests import utils_for_tests
from tests.mocks_for_tests import MockReturnUsingDictIn
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch, call
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
from midvatten.midvatten import midvatten
import os
import PyQt4
from collections import OrderedDict
from import_data_to_db import midv_data_importer


class TestParseDiverofficeFile(object):
    utils_ask_user_about_stopping = MockReturnUsingDictIn({'Failure, delimiter did not match': 'cancel',
                                                           'Failure: The number of data columns in file': 'cancel',
                                                           'Failure, parsing failed for file': 'cancel'},
                                                          0)

    def setUp(self):
        self.importinstance = midv_data_importer()

    def test_parse_diveroffice_file_utf8(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'utf-8'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = u'[[obsid, date_time, head_cm, temp_degc, cond_mscm], [rb1, 2016-03-15 10:30:00, 26.9, 5.18, ], [rb1, 2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string

    def test_parse_diveroffice_file_cp1252(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = u'[[obsid, date_time, head_cm, temp_degc, cond_mscm], [rb1, 2016-03-15 10:30:00, 26.9, 5.18, ], [rb1, 2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string

    def test_parse_diveroffice_file_semicolon_sep(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26.9;5.18',
             u'2016/03/15 11:00:00;157.7;0.6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = u'[[obsid, date_time, head_cm, temp_degc, cond_mscm], [rb1, 2016-03-15 10:30:00, 26.9, 5.18, ], [rb1, 2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string

    def test_parse_diveroffice_file_comma_dec(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = ur'''[[obsid, date_time, head_cm, temp_degc, cond_mscm], [rb1, 2016-03-15 10:30:00, 26.9, 5.18, ], [rb1, 2016-03-15 11:00:00, 157.7, 0.6, ]]'''
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_parse_diveroffice_file_comma_sep_comma_dec_failed(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26,9,5,18',
             u'2016/03/15 11:00:00,157,7,0,6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = 'cancel'
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_parse_diveroffice_file_different_separators_failed(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = 'cancel'
        assert test_string == reference_string

    def test_parse_diveroffice_file_try_capitalize(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )
        existing_obsids = [u'Rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = u'[[obsid, date_time, head_cm, temp_degc, cond_mscm], [Rb1, 2016-03-15 10:30:00, 26.9, 5.18, ], [Rb1, 2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.NotFoundQuestion', autospec=True)
    def test_parse_diveroffice_file_cancel(self, mock_notfoundquestion):
        mock_notfoundquestion.return_value.answer = u'cancel'
        mock_notfoundquestion.return_value.value = u''
        mock_notfoundquestion.return_value.reuse_column = u'obsid'

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )
        existing_obsids = [u'rb2']

        charset_of_diverofficefile = u'utf-8'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.parse_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = u'cancel'
        assert test_string == reference_string


class TestFilterDatesFromFiledata(object):
    def test_filter_dates_from_filedata(self):
        self.importinstance = midv_data_importer()
        file_data = [[u'obsid', u'date_time'], [u'rb1', u'2015-05-01 00:00:00'], [u'rb1', u'2016-05-01 00:00'], [u'rb2', u'2015-05-01 00:00:00'], [u'rb2', u'2016-05-01 00:00'], [u'rb3', u'2015-05-01 00:00:00'], [u'rb3', u'2016-05-01 00:00']]
        obsid_last_imported_dates = {u'rb1': [(datestring_to_date(u'2016-01-01 00:00:00'),)], u'rb2': [(datestring_to_date(u'2017-01-01 00:00:00'),)]}
        test_file_data = utils_for_tests.create_test_string(self.importinstance.filter_dates_from_filedata(file_data, obsid_last_imported_dates))

        reference_file_data = u'''[[obsid, date_time], [rb1, 2016-05-01 00:00], [rb3, 2015-05-01 00:00:00], [rb3, 2016-05-01 00:00]]'''

        assert test_file_data == reference_file_data