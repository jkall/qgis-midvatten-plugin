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
from import_data_to_db import midv_data_importer
import utils_for_tests
import midvatten_utils as utils
import utils_for_tests as test_utils
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn
import mock
import io
import midvatten

class TestFieldLoggerImporter():
    flow_instrument_id = MockReturnUsingDict({u'Instrument not found': [u'testid', u'']}, 1)
    instrument_staff_questions = MockReturnUsingDict({u'Instrument not found': [u'testid', u''], u'Staff not found': [u'teststaff', u'']}, 1)
    prev_used_flow_instr_ids = MockUsingReturnValue({u'Rb1615': [(u'Accvol', u'Flm01', u'2015-01-01 00:00:00'), (u'Momflow', u'Flm02', u'2016-01-01 00:00:00')]})
    quality_instruments = MockUsingReturnValue((u'instr1', u'instr2', u'instr3'))
    skip_popup = MockUsingReturnValue('')

    def setUp(self):
        self.importinstance = midv_data_importer()

    @raises(IndexError)
    @mock.patch('import_data_to_db.utils.pop_up_info', skip_popup.get_v)
    def test_fieldlogger_import_parse_rows_fail_with_header(self):

        f = ("LOCATION;DATE;TIME;VALUE;TYPE\n"
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n")

        result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.fieldlogger_import_parse_rows(f)))

    def test_fieldlogger_import_parse_rows(self):

        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            "Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            "Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n"
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        result_list = utils_for_tests.dict_to_sorted_list(parsed_rows)
        result_string = ','.join(result_list)
        reference_string = "flow,Rb1615,2016-03-30 15:30:09,Accvol,m3,357,comment,,gick bra,level,Rb1608,2016-03-30 15:34:13,comment,,ergv,meas,m,555,2016-03-30 15:34:40,comment,,testc,quality,Rb1505,2016-03-30 15:29:26,comment,,hej,konduktivitet,µS/cm,863,Rb1512,2016-03-30 15:30:39,comment,,test,syre,%,58,syre,mg/L,58,temperatur,grC,8,sample,Rb1202,2016-03-30 15:31:30,comment,,hej2,Rb1512,2016-03-30 15:31:30,turbiditet,FNU,899"
        assert result_string == reference_string

    @mock.patch('import_data_to_db.utils.pop_up_info', skip_popup.get_v)
    def test_fieldlogger_import_parse_rows_skip_putcode(self):
        """ Test that the bug that enters instead of obsname and subname PUTCODE is handled
        :return:
        """
        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            "Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "PUTCODE;13-04-2016;10:54:54;3.775;l.meas.m\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            "Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n"
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        result_list = utils_for_tests.dict_to_sorted_list(parsed_rows)
        result_string = ','.join(result_list)
        reference_string = "flow,Rb1615,2016-03-30 15:30:09,Accvol,m3,357,comment,,gick bra,level,Rb1608,2016-03-30 15:34:13,comment,,ergv,meas,m,555,2016-03-30 15:34:40,comment,,testc,quality,Rb1505,2016-03-30 15:29:26,comment,,hej,konduktivitet,µS/cm,863,Rb1512,2016-03-30 15:30:39,comment,,test,syre,%,58,syre,mg/L,58,temperatur,grC,8,sample,Rb1202,2016-03-30 15:31:30,comment,,hej2,Rb1512,2016-03-30 15:31:30,turbiditet,FNU,899"
        assert result_string == reference_string

    def test_fieldlogger_prepare_level_data(self):

        f = [
            "Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            "Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n"
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_level_data(parsed_rows[u'level']))
        reference_string = 'obsid;date_time;meas;comment\nRb1608;2016-03-30 15:34:13;555;ergv'
        assert file_string == reference_string

    def test_fieldlogger_prepare_level_data_first_format(self):
        """ Test that fhe first format where parameter was named level.meas works to import.
        :return:
        """

        f = [
            "Rb1608.level;30-03-2016;15:34:13;ergv;level.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;level.meas\n",
            "Rb1608.level;30-03-2016;15:34:40;testc;level.comment\n"
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_level_data(parsed_rows[u'level']))
        reference_string = 'obsid;date_time;meas;comment\nRb1608;2016-03-30 15:34:13;555;ergv'
        assert file_string == reference_string

    @mock.patch('import_data_to_db.utils.get_last_used_flow_instruments', prev_used_flow_instr_ids.get_v)
    @mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', flow_instrument_id.get_v)
    def test_fieldlogger_prepare_flow_data(self):
        f = [
            "Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            "Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            ]
        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_flow_data(parsed_rows[u'flow']))
        reference_string = "obsid;instrumentid;flowtype;date_time;reading;unit;comment\nRb1615;testid;Accvol;2016-03-30 15:30:09;357;m3;gick bra"

        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string

    @mock.patch('import_data_to_db.utils.get_last_used_flow_instruments', prev_used_flow_instr_ids.get_v)
    @mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', flow_instrument_id.get_v)
    def test_fieldlogger_prepare_flow_data_no_comment(self):
        f = [
            "Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            "Rb1615.flow;30-03-2016;15:30:10;gick bra;f.comment\n",
            ]
        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_flow_data(parsed_rows[u'flow']))
        reference_string = "obsid;instrumentid;flowtype;date_time;reading;unit;comment\nRb1615;testid;Accvol;2016-03-30 15:30:09;357;m3;"
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string

    @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
    @mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
    def test_fieldlogger_prepare_quality_data(self):

        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_quality_data(parsed_rows[u'quality']))
        reference_string = u'obsid;staff;date_time;instrument;parameter;reading_num;reading_txt;unit;flow_lpm;comment\nRb1505;teststaff;2016-03-30 15:29:26;testid;konduktivitet;863;863;µS/cm;;hej\nRb1512;teststaff;2016-03-30 15:30:39;testid;temperatur;8;8;grC;;test'
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string

    @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
    @mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
    def test_fieldlogger_prepare_sample_data(self):

        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_quality_data(parsed_rows[u'sample']))
        reference_string = u'obsid;staff;date_time;instrument;parameter;reading_num;reading_txt;unit;flow_lpm;comment\nRb1512;teststaff;2016-03-30 15:31:30;testid;turbiditet;899;899;FNU;;'
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string

    @mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
    def test_fieldlogger_prepare_notes_data(self):
        f = [
            "Rb1505.quality;30-03-2016;15:29:25;comment1;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            "Rb1615.flow;30-03-2016;15:30:10;comment2;f.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;NOTcomment1;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;comment3;s.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;NOTcomment3;l.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            "Rb1608.level;30-03-2016;15:34:40;comment4;l.comment\n"
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_notes_data(parsed_rows))
        reference_string = u'obsid;date_time;staff;comment\nRb1202;2016-03-30 15:31:30;teststaff;comment3\nRb1505;2016-03-30 15:29:25;teststaff;comment1\nRb1608;2016-03-30 15:34:40;teststaff;comment4\nRb1615;2016-03-30 15:30:10;teststaff;comment2'
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string





class TestNewMemoryDb():
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(':memory:')

    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten.midvatten(self.iface)

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def test_new_db(self):
        self.midvatten.new_db()

    def tearDown(self):
        self.iface = None
        self.midvatten = None


class TestLoadDiverofficeFile(object):
    utils_ask_user_about_stopping = MockReturnUsingDictIn({'Failure, delimiter did not match': 'cancel',
                                                           'Failure: The number of data columns in file': 'cancel',
                                                           'Failure, parsing failed for file': 'cancel'},
                                                          0)

    def setUp(self):
        self.importinstance = midv_data_importer()

    def test_load_diveroffice_file_utf8(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'utf-8'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'Date/time;Water head[cm];Temperature[°C];obsid;2016-03-15 10:30:00;26.9;5.18;rb1;2016-03-15 11:00:00;157.7;0.6;rb1'
        assert test_string == reference_string

    def test_load_diveroffice_file_cp1252(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'Date/time;Water head[cm];Temperature[°C];obsid;2016-03-15 10:30:00;26.9;5.18;rb1;2016-03-15 11:00:00;157.7;0.6;rb1'
        assert test_string == reference_string

    def test_load_diveroffice_file_semicolon_sep(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26.9;5.18',
             u'2016/03/15 11:00:00;157.7;0.6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'Date/time;Water head[cm];Temperature[°C];obsid;2016-03-15 10:30:00;26.9;5.18;rb1;2016-03-15 11:00:00;157.7;0.6;rb1'
        assert test_string == reference_string

    def test_load_diveroffice_file_comma_dec(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'Date/time;Water head[cm];Temperature[°C];obsid;2016-03-15 10:30:00;26.9;5.18;rb1;2016-03-15 11:00:00;157.7;0.6;rb1'
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_load_diveroffice_file_comma_sep_comma_dec_failed(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26,9,5,18',
             u'2016/03/15 11:00:00,157,7,0,6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'cancel'
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_load_diveroffice_file_different_separators_failed(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )
        existing_obsids = [u'rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'cancel'
        assert test_string == reference_string

    #@mock.patch('import_data_to_db.utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_load_diveroffice_file_try_capitalize(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )
        existing_obsids = [u'Rb1']

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                ask_for_names = False
                file_data = self.importinstance.load_diveroffice_file(path, charset_of_diverofficefile, existing_obsids, ask_for_names)

        test_string = ';'.join(utils_for_tests.dict_to_sorted_list(utils_for_tests.dict_to_sorted_list(file_data)))
        reference_string = 'Date/time;Water head[cm];Temperature[°C];obsid;2016-03-15 10:30:00;26.9;5.18;Rb1;2016-03-15 11:00:00;157.7;0.6;Rb1'
        assert test_string == reference_string






class TestInterlab4Importer():
    def setUp(self):
        self.importinstance = midv_data_importer()

    def test_interlab4_parse_filesettings_utf16(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-16",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsn",
                        )
        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-16') as testfile:
            result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.interlab4_parse_filesettings(testfile)))

        reference_string = "['False', '4.0', 'utf-16', ',', 'False']"

        assert result_string == reference_string

    def test_interlab4_parse_filesettings_utf8(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-8",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsn",
                        )
        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.interlab4_parse_filesettings(testfile)))

        reference_string = "['False', '4.0', 'utf-8', ',', 'False']"

        assert result_string == reference_string

    def test_parse_interlab4_utf16(self):

        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-16",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-16') as testfile:
            result = self.importinstance.parse_interlab4([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_interlab4([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_iso_8859_1(self):

        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=ISO-8859-1",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'iso-8859-1') as testfile:
            result = self.importinstance.parse_interlab4([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_interlab4([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_utf8(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-8",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse_interlab4([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_interlab4([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string

    def test_parse_interlab4_ignore_bland_line(self):
        interlab4_lines = (
                    u"#Interlab",
                    u"#Version=4.0",
                    u"#Tecken=UTF-8",
                    u"#Textavgränsare=Nej",
                    u"#Decimaltecken=,",
                    u"#Provadm",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;",
                    u"#Provdat",
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2773;ISO 17294-2;Järn;;0,06;;mg/l;;;;;;;",
                    u"DM-990908-2773;Saknas;Temperatur vid provtagning;;14,5;;grader C;;;;;;;",
                    u"DM-990908-2773;SLV METOD1990-01-01 TA;Temperatur vid ankomst;;16,8;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2773;ISO 17294-2;Mangan;;0,001;<;mg/l;;;;;;;",
                    u"#Provadm ",
                    u"Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;",
                    u"DM-990908-2774;MFR;;;;;;Demo-Laboratoriet;NSG;DV;VV1784;Demo2 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;11:30;2010-09-07;14:15;",
                    u"#Provdat",
                    u'',
                    u"Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;",
                    u"DM-990908-2774;SS-EN ISO 7887-1/4;Färgtal;;6,5;;mg/l Pt;;;;;;;",
                    u"DM-990908-2774;ISO 17294-2;Järn;;0,05;<;mg/l;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid provtagning;;14,8;;grader C;;;;;;;",
                    u"DM-990908-2774;Saknas;Temperatur vid ankomst;;17,3;;grader C;;;;;;Ej kylt;",
                    u"DM-990908-2774;ISO 17294-2;Mangan;;0,004;;mg/l;;;;;;; ",
                    u"#Slut"
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse_interlab4([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_interlab4([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.06;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2773;metodbeteckning;ISO 17294-2;mätvärdetal;0.001;mätvärdetalanm;<;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2773;metodbeteckning;SLV METOD1990-01-01 TA;mätvärdetal;16.8;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2773;metodbeteckning;Saknas;mätvärdetal;14.5;parameter;Temperatur vid provtagning;metadata;adress;PG Vejdes väg 15;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;kommunkod;0780;lablittera;DM-990908-2773;laboratorium;Demo-Laboratoriet;namn;MFR;ort;Växjö;postnr;351 96;projekt;Demoproj;provplatsid;Demo1 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;10:15;provtyp;Utgående;provtypspecifikation;Nej;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010;DM-990908-2774;Färgtal;enhet;mg/l Pt;lablittera;DM-990908-2774;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;6.5;parameter;Färgtal;Järn;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.05;mätvärdetalanm;<;parameter;Järn;Mangan;enhet;mg/l;lablittera;DM-990908-2774;metodbeteckning;ISO 17294-2;mätvärdetal;0.004;parameter;Mangan;Temperatur vid ankomst;enhet;grader C;kommentar;Ej kylt;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;17.3;parameter;Temperatur vid ankomst;Temperatur vid provtagning;enhet;grader C;lablittera;DM-990908-2774;metodbeteckning;Saknas;mätvärdetal;14.8;parameter;Temperatur vid provtagning;metadata;bedömning;Tjänligt;inlämningsdatum;2010-09-07;inlämningstid;14:15;lablittera;DM-990908-2774;laboratorium;Demo-Laboratoriet;namn;MFR;provplatsid;Demo2 vattenverk;provtagare;DV;provtagningsdatum;2010-09-07;provtagningsorsak;Dricksvatten enligt SLVFS 2001:30;provtagningstid;11:30;provtyp;Utgående;provtypspecifikation;Nej;registertyp;VV1784;specifik provplats;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;år;2010'

        assert result_string == reference_string
        
    def test_parse_interlab4_quotechar(self):
        interlab4_lines = (
                    u'#Interlab',
                    u'#Version=4.0',
                    u'#Tecken=UTF-8',
                    u'#Textavgränsare=Ja',
                    u'#Decimaltecken=,',
                    u'#Provadm',
                    u'"Lablittera";"Namn";"Adress";"Postnr";"Ort";',
                    u'"DM-990908-2773";"MFR";"PG Vejdes väg 15";"351 96";"Växjö";',
                    u'#Provdat',
                    u'"Lablittera";"Metodbeteckning";"Parameter";"Mätvärdetext";"Mätvärdetal";',
                    u'"DM-990908-2773";"SS-EN ISO 7887-1/4";"Färgtal";;"5";',
                    u'#Slut'
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse_interlab4([testfile])
        result_string = ';'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_interlab4([testfile])))
        reference_string = 'DM-990908-2773;Färgtal;lablittera;DM-990908-2773;metodbeteckning;SS-EN ISO 7887-1/4;mätvärdetal;5;parameter;Färgtal;metadata;adress;PG Vejdes väg 15;lablittera;DM-990908-2773;namn;MFR;ort;Växjö;postnr;351 96'
        assert result_string == reference_string

    def test_parse_interlab4_quotechar_semicolon(self):
        interlab4_lines = (
                    u'#Interlab',
                    u'#Version=4.0',
                    u'#Tecken=UTF-8',
                    u'#Textavgränsare=Ja',
                    u'#Decimaltecken=,',
                    u'#Provadm',
                    u'"Lablittera";"Namn";"Adress";"Postnr";"Ort";',
                    u'"DM-990908-2773";"MFR";"PG ;Vejdes väg 15";"351 96";"Växjö";',
                    u'#Provdat',
                    u'"Lablittera";"Metodbeteckning";"Parameter";"Mätvärdetext";"Mätvärdetal";',
                    u'"DM-990908-2773";"SS-EN ISO 7887-1/4";"Färgtal";;"5";',
                    u'#Slut'
                        )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            result = self.importinstance.parse_interlab4([testfile])
        result_string = '|'.join(utils_for_tests.dict_to_sorted_list(self.importinstance.parse_interlab4([testfile])))
        reference_string = 'DM-990908-2773|Färgtal|lablittera|DM-990908-2773|metodbeteckning|SS-EN ISO 7887-1/4|mätvärdetal|5|parameter|Färgtal|metadata|adress|PG ;Vejdes väg 15|lablittera|DM-990908-2773|namn|MFR|ort|Växjö|postnr|351 96'

        assert result_string == reference_string

    def test_interlab4_to_table(self):
        #TODO: Not completed yet
        return
        interlab4_lines = (
            u'#Interlab',
            u'#Version=4.0',
            u'#Tecken=UTF-8',
            u'#Textavgränsare=Nej',
            u'#Decimaltecken=,',
            u'#Provadm',
            u'Lablittera;Namn;Adress;Postnr;Ort;Kommunkod;Projekt;Laboratorium;Provtyp;Provtagare;Registertyp;ProvplatsID;Provplatsnamn;Specifik provplats;Provtagningsorsak;Provtyp;Provtypspecifikation;Bedömning;Kemisk bedömning;Mikrobiologisk bedömning;Kommentar;År;Provtagningsdatum;Provtagningstid;Inlämningsdatum;Inlämningstid;',
            u'DM-990908-2773;MFR;PG Vejdes väg 15;351 96;Växjö;0780;Demoproj;Demo-Laboratoriet;NSG;DV;;Demo1 vattenverk;;Föreskriven regelbunden undersökning enligt SLVFS 2001:30;Dricksvatten enligt SLVFS 2001:30;Utgående;Nej;Tjänligt;;;;2010;2010-09-07;10:15;2010-09-07;14:15;',
            u'#Provdat',
            u'Lablittera;Metodbeteckning;Parameter;Mätvärdetext;Mätvärdetal;Mätvärdetalanm;Enhet;Rapporteringsgräns;Detektionsgräns;Mätosäkerhet;Mätvärdespår;Parameterbedömning;Kommentar;',
            u'DM-990908-2773;SS-EN ISO 7887-1/4;Färgtal;;5;;mg/l Pt;;;;;;;',
            u'#Slut'
                )

        with utils.tempinput(u'\n'.join(interlab4_lines), 'utf-8') as testfile:
            parsed_result = self.importinstance.parse_interlab4([testfile])

        result_string = self.importinstance.interlab4_to_table(parsed_result)

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'\n'.join((u'obsid;depth;report;project;staff;date_time;anameth;parameter;reading_num;reading_txt;unit;comment',
                                       u'Demo1 vattenverk;0;Demoproj;DV,2010-09-07 10:15:00;SS-EN ISO 7887-1/4;Färgtal;5;5;mg/l Pt;;'))

        assert result_string == reference_string

    def tearDown(self):
        self.importinstance = None
        pass


