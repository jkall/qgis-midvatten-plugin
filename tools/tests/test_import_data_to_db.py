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
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2
import mock
import io
import midvatten
import os
import PyQt4

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)


class _TestFieldLoggerImporterNoDb():
    #flow_instrument_id = MockReturnUsingDict({u'Instrument not found': [u'testid', u'']}, 1)
    instrument_staff_questions = MockReturnUsingDict({u'Submit instrument id': MockNotFoundQuestion(u'ok', u'testid'), u'Submit field staff': MockNotFoundQuestion(u'ok', u'teststaff')}, u'dialogtitle')
    prev_used_flow_instr_ids = MockUsingReturnValue((True, {u'Rb1615': [(u'Accvol', u'Flm01', u'2015-01-01 00:00:00'), (u'Momflow', u'Flm02', u'2016-01-01 00:00:00')]}))
    quality_instruments = MockUsingReturnValue((True, (u'instr1', u'instr2', u'instr3')))
    skip_popup = MockUsingReturnValue('')
    notfound_ok = MockUsingReturnValue(MockNotFoundQuestion(u'ok', u'testvalue'))
    existing_staff = MockUsingReturnValue((True, (u'a', u'b')))
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    mock_askuser = MockReturnUsingDictIn({u'Do you want to confirm': answer_no_obj}, 1)

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
        result_string = utils_for_tests.create_test_string(parsed_rows)
        reference_string = u'{flow: {Rb1615: {2016-03-30 15:30:09: {(Accvol, m3): 357, (comment, ): gick bra}}}, level: {Rb1608: {2016-03-30 15:34:13: {(comment, ): ergv, (meas, m): 555}, 2016-03-30 15:34:40: {(comment, ): testc}}}, quality: {Rb1202: {2016-03-30 15:31:30: {(comment, ): hej2}}, Rb1505: {2016-03-30 15:29:26: {(comment, ): hej, (konduktivitet, µS/cm): 863}}, Rb1512: {2016-03-30 15:30:39: {(comment, ): test, (syre, %): 58, (syre, mg/L): 58, (temperatur, grC): 8}, 2016-03-30 15:31:30: {(turbiditet, FNU): 899}}}}'
        assert result_string == reference_string

    def test_fieldlogger_import_parse_rows_shift_date(self):

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

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f, [u'-1', u'hours'])
        test_string = utils_for_tests.create_test_string(parsed_rows)
        reference_string = u'{flow: {Rb1615: {2016-03-30 14:30:09: {(Accvol, m3): 357, (comment, ): gick bra}}}, level: {Rb1608: {2016-03-30 14:34:13: {(comment, ): ergv, (meas, m): 555}, 2016-03-30 14:34:40: {(comment, ): testc}}}, quality: {Rb1202: {2016-03-30 14:31:30: {(comment, ): hej2}}, Rb1505: {2016-03-30 14:29:26: {(comment, ): hej, (konduktivitet, µS/cm): 863}}, Rb1512: {2016-03-30 14:30:39: {(comment, ): test, (syre, %): 58, (syre, mg/L): 58, (temperatur, grC): 8}, 2016-03-30 14:31:30: {(turbiditet, FNU): 899}}}}'
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.pop_up_info', skip_popup.get_v)
    def _test_fieldlogger_import_parse_rows_skip_putcode(self):
        """ Test that the bug that enters PUTCODE instead of obsname and subname is handled
            This is not needed anymore since the import user will be asked for
            a correct obsid.
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

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
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

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
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

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_last_used_flow_instruments', prev_used_flow_instr_ids.get_v)
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

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_last_used_flow_instruments', prev_used_flow_instr_ids.get_v)
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

    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
    @mock.patch('import_data_to_db.utils.get_staff_list' , existing_staff.get_v)
    @mock.patch('import_data_to_db.utils.get_w_qual_field_parameters', autospec=True)
    @mock.patch('midvatten_utils.qgis.utils.iface', autospec=True)
    @mock.patch('import_data_to_db.utils.get_last_used_quality_instruments', autospec=True)
    def test_fieldlogger_prepare_quality_data(self, mock_last_used_instruments, mock_iface, mock_parameters):
        mock_last_used_instruments.return_value = {u'konduktivitet': [(u'µS/cm', u'teststaff', u'testid', u'')], u'syre': [(u'mg/L', u'teststaff', u'testid' , u''), (u'%', u'teststaff', u'testid' , u'')], u'temperatur': [(u'grC', u'teststaff', None, u'')]}
        mock_parameters.return_value = [(u'konduktivitet', u'konduktivitet', u'µS/cm'), (u'syre', u'syre', u'mg/L'), (u'syre', u'syre', u'%'), (u'temperatur', u'temperatur', u'grC')]
        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        result_list = self.importinstance.fieldlogger_prepare_quality_and_sample(parsed_rows[u'quality'])
        test_string = utils_for_tests.create_test_string(result_list)
        reference_string = u'[[obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, comment], [Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863, 863, µS/cm, hej], [Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 58, 58, %, test], [Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67, 67, mg/L, test], [Rb1512, teststaff, 2016-03-30 15:30:39, , temperatur, 8, 8, grC, test]]'
        assert test_string == reference_string

    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
    @mock.patch('import_data_to_db.utils.get_staff_list' , existing_staff.get_v)
    @mock.patch('import_data_to_db.utils.get_w_qual_field_parameters', autospec=True)
    @mock.patch('midvatten_utils.qgis.utils.iface', autospec=True)
    @mock.patch('import_data_to_db.utils.get_last_used_quality_instruments', autospec=True)
    def test_fieldlogger_prepare_quality_data_sample(self, mock_last_used_instruments, mock_iface, mock_parameters):
        mock_last_used_instruments.return_value = {u'turbiditet': [(u'FNU', u'teststaff', u'testid', u'')]}
        mock_parameters.return_value = [(u'turbiditet', u'turbiditet', u'FNU')]
        f = [
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        file_string = utils_for_tests.create_test_string(self.importinstance.fieldlogger_prepare_quality_and_sample(parsed_rows[u'quality']))
        reference_string = u'[[obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, comment], [Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899, 899, FNU, ]]'
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string


class _TestFieldLoggerImporterDb(object):
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', DBPATH_QUESTION.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten.midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()
        #utils.verify_table_exists(u'comments')

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    def test_fieldlogger_import_to_db(self):
        """ Full integration test of fieldlogger all the way to db
        :return:
        """

        f = [
            "Location;date_time;value;comment\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            "Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            "Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            "Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n"
            ]

        self.importinstance.charsetchoosen = [u'utf-8']

        with utils.tempinput(''.join(f)) as filename:
            selected_file = MockUsingReturnValue([filename])
            return_int = MockUsingReturnValue(int)
            mocked_iface = MockQgisUtilsIface()

            instrument_staff_questions = MockReturnUsingDict({u'Submit instrument id': MockNotFoundQuestion(u'ok', u'testid'), u'Submit field staff': MockNotFoundQuestion(u'ok', u'teststaff')}, u'dialogtitle')
            quality_instruments = MockUsingReturnValue((u'instr1', u'instr2', u'instr3'))
            answer_no_obj = MockUsingReturnValue()
            answer_no_obj.result = 0
            answer_yes_obj = MockUsingReturnValue()
            answer_yes_obj.result = 1
            answer_shift_date_obj = MockUsingReturnValue()
            answer_shift_date_obj.result = [u'0', u'hours']
            mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj, u'User input needed': answer_shift_date_obj, u'Do you want to confirm instrument': answer_no_obj}, 1)

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestFieldLoggerImporterDb.skip_popup.get_v)
            @mock.patch('import_data_to_db.midv_data_importer.select_files', selected_file.get_v)
            @mock.patch('qgis.utils.iface', mocked_iface)
            @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
            @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
            @mock.patch('import_data_to_db.utils.get_w_qual_field_parameters', autospec=True)
            @mock.patch('import_data_to_db.utils.get_last_used_quality_instruments', autospec=True)
            def _test_fieldlogger_import(self, mocked_iface, mock_last_used_instruments, mock_parameters):
                mock_last_used_instruments.return_value = {u'konduktivitet': [(u'µS/cm', u'teststaff', u'testid', u'')], u'syre': [(u'mg/L', u'teststaff', u'testid' , u''), (u'%', u'teststaff', u'testid' , u'')], u'temperatur': [(u'grC', u'teststaff', None, u'')], u'turbiditet': [(u'FNU', u'teststaff', u'testid', u'')]}
                mock_parameters.return_value = [(u'konduktivitet', u'konduktivitet', u'µS/cm'), (u'syre', u'syre', u'mg/L'), (u'syre', u'syre', u'%'), (u'temperatur', u'temperatur', u'grC'), (u'turbiditet', u'turbiditet', u'FNU')]

                utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1505")''')
                utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1615")''')
                utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1512")''')
                utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1202")''')
                utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1608")''')
                utils.sql_alter_db(u'''INSERT OR IGNORE INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("syre", "syre","mg/L")''')
                utils.sql_alter_db(u'''INSERT OR IGNORE INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("syre", "syre","%")''')
                utils.sql_alter_db(u'''INSERT OR IGNORE INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("konduktivitet", "konduktivitet","µS/cm")''')
                utils.sql_alter_db(u'''INSERT OR IGNORE INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("turbiditet", "turbiditet", "FNU")''')
                utils.sql_alter_db(u'''INSERT OR IGNORE INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("temperatur", "temperatur", "grC")''')

                self.importinstance.fieldlogger_import()
                test_data = utils_for_tests.create_test_string(dict([(k, utils.sql_load_fr_db(u'select * from %s'%k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
                reference_data = u'{comments: (True, [(Rb1608, 2016-03-30 15:34:40, testc, teststaff), (Rb1202, 2016-03-30 15:31:30, hej2, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv)]), w_qual_field: (True, [(Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, hej), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, test), (Rb1512, teststaff, 2016-03-30 15:30:39, , temperatur, 8.0, 8, grC, test), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, ), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, )]), zz_staff: (True, [(teststaff, )])}'

                #print("Messagebar: \n" + str(mock_askuser.args_called_with) + " \n")
                msgbar = mocked_iface.messagebar.messages
                if msgbar:
                    print str(msgbar)

                assert test_data == reference_data

            _test_fieldlogger_import(self, mocked_iface)

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_send_file_data_to_importer_and_wflow_import_from_csvlayer(self):
        """ A test that incorporates a lot of database functionality.
        :return: None
        """
        utils.sql_alter_db("""INSERT INTO obs_points ("obsid") VALUES ('obsid1')""")
        utils.sql_alter_db("""INSERT INTO obs_points ("obsid") VALUES ('obsid2')""")
        file_data = ([u'obsid', u'instrumentid', u'flowtype', u'date_time', u'reading', u'unit', u'comment'],
                     [u'obsid1', u'instrumentid1', u'flowtype1', u'2015-01-01 00:00:00', u'11', u'unit1', u'comment1'],
                     [u'obsid1', u'instrumentid1', u'flowtype1', u'2015-01-02 00:00:00', u'111', u'unit1', u'comment11'],
                     [u'obsid2', u'instrumentid2', u'flowtype2', u'2016-01-01 00:00:00', u'222', u'unit2', u'comment2'])
        self.importinstance.send_file_data_to_importer(file_data, self.importinstance.wflow_import_from_csvlayer)

        reference_flow_data = (True, [(u'obsid1', u'instrumentid1', u'flowtype1', u'2015-01-01 00:00:00', 11.0, u'unit1', u'comment1'), (u'obsid1', u'instrumentid1', u'flowtype1', u'2015-01-02 00:00:00', 111.0, u'unit1', u'comment11'), (u'obsid2', u'instrumentid2', u'flowtype2', u'2016-01-01 00:00:00', 222.0, u'unit2', u'comment2')])
        test_flow_data = utils.sql_load_fr_db(u'select * from w_flow')

        assert test_flow_data == reference_flow_data

        reference_flow_type = (True, [(u'Accvol', u'Accumulated volume'), (u'Momflow', u'Momentary flow rate'), (u'Aveflow', u'Average flow since last reading'), (u'flowtype1', u''), (u'flowtype2', u'')])
        test_flow_type = utils.sql_load_fr_db(u'select type, explanation from zz_flowtype')

        msgbar = TestDbCalls.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        assert test_flow_type == reference_flow_type

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_send_file_data_to_importer_and_comments_import_from_csv(self):
        utils.sql_alter_db("""INSERT INTO obs_points ("obsid") VALUES ('obsid1')""")
        file_data = ([u'obsid', u'date_time', u'comment', u'staff'],
                     [u'obsid1', u'2015-01-01 00:00.00', u'testcomment1', u'staff1'],
                     [u'obsid1', u'2016-01-01 00:00.00', u'testcomment2', u'staff2'])
        self.importinstance.send_file_data_to_importer(file_data, self.importinstance.comments_import_from_csv)

        reference_comments = (True, [(u'obsid1', u'2015-01-01 00:00.00', u'testcomment1', u'staff1'), (u'obsid1', u'2016-01-01 00:00.00', u'testcomment2', u'staff2')])
        test_comments = utils.sql_load_fr_db(u'select * from comments')
        assert test_comments == reference_comments

        reference_staff = u'(True, [(staff1, ), (staff2, )])'
        test_staff = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select * from zz_staff'))

        msgbar = TestDbCalls.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        assert test_staff == reference_staff


class _TestImportWellsFile(object):

    def setUp(self):
        self.importinstance = midv_data_importer()

    def test_wells_parse_rows(self):
        f = (
            u'FileVersion 1;X',
            u'NAME;INPUTTYPE;HINT',
            u'parameters...',
            u'NAME;SUBNAME;LAT;LON;INPUTFIELD',
            u'Rb1301;Rb1301.quality;60.5549041639;14.1875295081;q.comment|q.syre.mg/L|q.syre.%|q.konduktivitet.µS/cm|q.redoxpotential.mV|q.pH',
            u'Rb1301;Rb1301.sample;60.5549041639;14.1875295081;s.temperatur.grC|s.comment|s.turbiditet.FNU',
            u'Rb1301;Rb1301.level;60.5640220837;14.1901808137;l.comment|l.meas.m',
            u'Rb1302;Rb1302.quality;60.5640220837;14.1901808137;q.comment|q.syre.mg/L|q.konduktivitet.µS/cm|q.redoxpotential.mV|q.pH',
            u'Rb1302;Rb1302.sample;60.5640220837;14.1901808137;s.temperatur.grC|s.comment|s.turbiditet.FNU'
            )
        test_string = utils_for_tests.create_test_string(self.importinstance.wells_parse_rows(f))

        reference_string = u'{Rb1301: {level: [(comment, ), (meas, m)], quality: [(comment, ), (syre, mg/L), (syre, %), (konduktivitet, µS/cm), (redoxpotential, mV), (pH, )], sample: [(temperatur, grC), (comment, ), (turbiditet, FNU)]}, Rb1302: {quality: [(comment, ), (syre, mg/L), (konduktivitet, µS/cm), (redoxpotential, mV), (pH, )], sample: [(temperatur, grC), (comment, ), (turbiditet, FNU)]}}'
        assert test_string == reference_string

    def test_parse_wells_file(self):
        f = (
            u'FileVersion 1;X',
            u'NAME;INPUTTYPE;HINT',
            u'parameters...',
            u'NAME;SUBNAME;LAT;LON;INPUTFIELD',
            u'Rb1301;Rb1301.quality;60.5549041639;14.1875295081;q.comment|q.syre.mg/L|q.syre.%|q.konduktivitet.µS/cm|q.redoxpotential.mV|q.pH',
            u'Rb1301;Rb1301.sample;60.5549041639;14.1875295081;s.temperatur.grC|s.comment|s.turbiditet.FNU',
            u'Rb1301;Rb1301.level;60.5640220837;14.1901808137;l.comment|l.meas.m',
            u'Rb1302;Rb1302.quality;60.5640220837;14.1901808137;q.comment|q.syre.mg/L|q.konduktivitet.µS/cm|q.redoxpotential.mV|q.pH',
            u'Rb1302;Rb1302.sample;60.5640220837;14.1901808137;s.temperatur.grC|s.comment|s.turbiditet.FNU'
            )

        self.importinstance.charsetchoosen = (u'utf-8', True)
        with utils.tempinput(u'\n'.join(f), self.importinstance.charsetchoosen[0]) as filename:
            selected_file = MockUsingReturnValue([filename])

            @mock.patch('import_data_to_db.midv_data_importer.select_files', selected_file.get_v)
            def _test_parse_wells_file(self):

                test_string = utils_for_tests.create_test_string(self.importinstance.parse_wells_file())
                reference_string = u'{Rb1301: {level: [(comment, ), (meas, m)], quality: [(comment, ), (syre, mg/L), (syre, %), (konduktivitet, µS/cm), (redoxpotential, mV), (pH, )], sample: [(temperatur, grC), (comment, ), (turbiditet, FNU)]}, Rb1302: {quality: [(comment, ), (syre, mg/L), (konduktivitet, µS/cm), (redoxpotential, mV), (pH, )], sample: [(temperatur, grC), (comment, ), (turbiditet, FNU)]}}'
                assert test_string == reference_string

            _test_parse_wells_file(self)


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


class TestWlvllogImportFromDiverofficeFiles(object):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(TEMP_DB_PATH)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten.midvatten(self.iface)

        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen[0]) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen[0]) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen[0]) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.midv_data_importer.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, -1000.0, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, -1010.0, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, -1001.0, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, -1020.0, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, -1002.0, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, -1030.0, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_skip_duplicates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:30', '5.0')''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen[0]) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen[0]) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen[0]) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.midv_data_importer.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, -1010.0, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, -1001.0, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, -1020.0, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, -1002.0, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, -1030.0, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_filter_dates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen[0]) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen[0]) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen[0]) as f3:

                    filenames = [f1, f2, f3]
                    answer_no_obj = MockUsingReturnValue(None)
                    answer_no_obj.result = 0
                    answer_yes_obj = MockUsingReturnValue(None)
                    answer_yes_obj.result = 1
                    mock_askuser = MockReturnUsingDictIn({u'Do you want to confirm': answer_no_obj, u'Do you want to import': answer_yes_obj, u'It is a strong recommendation': answer_no_obj}, 1)

                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.midv_data_importer.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, -1010.0, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, -1001.0, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, -1020.0, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, -1002.0, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, -1030.0, None)])'''
                    print("Filter dates:\n")
                    print(test_string)
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_all_dates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb3")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen[0]) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen[0]) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen[0]) as f3:

                    filenames = [f1, f2, f3]
                    answer_no_obj = MockUsingReturnValue(None)
                    answer_no_obj.result = 0
                    answer_yes_obj = MockUsingReturnValue(None)
                    answer_yes_obj.result = 1
                    mock_askuser = MockReturnUsingDictIn({u'Do you want to confirm': answer_no_obj, u'Do you want to import': answer_no_obj, u'It is a strong recommendation': answer_no_obj}, 1)

                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.midv_data_importer.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, -1000.0, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, -1010.0, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, -1001.0, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, -1020.0, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, -1002.0, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, -1030.0, None)])'''
                    print("All dates:\n")
                    print(test_string)
                    assert test_string == reference_string


class _TestDefaultImport(object):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten.midvatten(self.iface)

        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_default_import_wlvllogg(self):
        file = [u'obsid,date_time,head_cm',
                 u'rb1,2016-03-15 10:30:00,1']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(file), self.importinstance.charsetchoosen[0]) as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test_default_import_wlvllogg(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                        mock_filename.return_value = filename
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.default_import(self.importinstance.wlvllogg_import_from_csvlayer)

                    _test_default_import_wlvllogg(self, filename)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, None, None, -1000.0, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_default_import_wlvllogg_with_comment(self):
        file = [u'obsid,date_time,head_cm,comment',
                 u'rb1,2016-03-15 10:30:00,1,testcomment']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(file), self.importinstance.charsetchoosen[0]) as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test_default_import_wlvllogg(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                        mock_filename.return_value = filename
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.default_import(self.importinstance.wlvllogg_import_from_csvlayer)

                    _test_default_import_wlvllogg(self, filename)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, None, None, -1000.0, testcomment)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_default_import_wlvllogg_with_temp(self):
        file = [u'obsid,date_time,head_cm,temp_degc',
                 u'rb1,2016-03-15 10:30:00,1, 5']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(file), self.importinstance.charsetchoosen[0]) as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test_default_import_wlvllogg(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                        mock_filename.return_value = filename
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.default_import(self.importinstance.wlvllogg_import_from_csvlayer)

                    _test_default_import_wlvllogg(self, filename)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 5.0, None, -1000.0, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_default_import_wlvllogg_with_temp_comment(self):
        file = [u'obsid,date_time,head_cm,temp_degc,cond_mscm',
                 u'rb1,2016-03-15 10:30:00,1,5,10']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(file), self.importinstance.charsetchoosen[0]) as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test_default_import_wlvllogg(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                        mock_filename.return_value = filename
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.default_import(self.importinstance.wlvllogg_import_from_csvlayer)

                    _test_default_import_wlvllogg(self, filename)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 5.0, 10.0, -1000.0, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_default_import_wlvllogg_different_order(self):
        file = [u'obsid,cond_mscm,date_time,head_cm,temp_degc',
                 u'rb1,10,2016-03-15 10:30:00,1,5']

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(file), self.importinstance.charsetchoosen[0]) as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test_default_import_wlvllogg(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                        mock_filename.return_value = filename
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance.default_import(self.importinstance.wlvllogg_import_from_csvlayer)

                    _test_default_import_wlvllogg(self, filename)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 5.0, 10.0, -1000.0, None)])'''
                    assert test_string == reference_string


class _TestInterlab4Importer():
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

        result_string = utils_for_tests.create_test_string(self.importinstance.interlab4_to_table(parsed_result))

        # "obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment"
        reference_string = u'[[obsid, depth, report, project, staff, date_time, anameth, parameter, reading_num, reading_txt, unit, comment], [Demo1 vattenverk, None, DM-990908-2773, Demoproj, DV, 2010-09-07 10:15:00, SS-EN ISO 7887-1/4, Färgtal, 5, 5, mg/l Pt, ]]'
        assert result_string == reference_string

    def tearDown(self):
        self.importinstance = None
        pass


class _TestDbCalls(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    #temp_db_path = '/home/henrik/temp/tmp_midvatten_temp_db.sqlite'
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    #mocked_qgsproject = MockQgsProject(mocked_qgsinstance)

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten.midvatten(self.iface)
        try:
            os.remove(TestDbCalls.temp_db_path)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()
        #utils.verify_table_exists(u'comments')

    def tearDown(self):
        #Delete database
        os.remove(TestDbCalls.temp_db_path)

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_verify_table_exists(self):
        exists = utils.verify_table_exists(u'obs_points')
        assert exists

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_import_staff(self):
        self.importinstance.staff_import(u'staff1')
        imported_staff = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select * from zz_staff'))
        assert imported_staff == u'(True, [(staff1, )])'

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_import_staff_two_staffs(self):
        self.importinstance.staff_import([u'staff1', u'staff2'])
        imported_staff = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select * from zz_staff'))
        assert imported_staff == u'(True, [(staff1, ), (staff2, )])'


class _TestImportObsPoints(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    #temp_db_path = '/home/henrik/temp/tmp_midvatten_temp_db.sqlite'
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])
    #mocked_qgsproject = MockQgsProject(mocked_qgsinstance)

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten.midvatten(self.iface)
        try:
            os.remove(TestImportObsPoints.temp_db_path)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TestImportObsPoints.temp_db_path)

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_import_obsids_directly(self):
        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid2")')
        result = utils.sql_load_fr_db(u'select * from obs_points')

        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        assert result == (True, [(u'obsid1', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), (u'obsid2', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)])


    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_import_obs_points_using_obsp_import(self):

        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            selected_file = MockUsingReturnValue(filename)

            @mock.patch('PyQt4.QtGui.QInputDialog.getText', TestImportObsPoints.mock_encoding.get_v)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName', selected_file.get_v)
            @mock.patch('midvatten_utils.QgsProject.instance', TestImportObsPoints.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser', TestImportObsPoints.mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestImportObsPoints.skip_popup.get_v)
            @mock.patch('qgis.utils.iface', TestImportObsPoints.mocked_iface)
            def _test_import_obs_points_using_obsp_import(self):
                self.importinstance.obsp_import()
            _test_import_obs_points_using_obsp_import(self)

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html", AsText(geometry) from obs_points'''))
        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, 421484.0, 6542696.0, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, POINT(421484 6542696))])'''
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_import_obs_points_using_obsp_import_no_east_north(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'', u'', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            selected_file = MockUsingReturnValue(filename)

            @mock.patch('PyQt4.QtGui.QInputDialog.getText', TestImportObsPoints.mock_encoding.get_v)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName', selected_file.get_v)
            @mock.patch('midvatten_utils.QgsProject.instance', TestImportObsPoints.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser', TestImportObsPoints.mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestImportObsPoints.skip_popup.get_v)
            @mock.patch('qgis.utils.iface', TestImportObsPoints.mocked_iface)
            def _test_import_obs_points_using_obsp_import(self):
                self.importinstance.obsp_import()
            _test_import_obs_points_using_obsp_import(self)

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html", AsText(geometry) from obs_points'''))
        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, None, None, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, None)])'''
        assert test_string == reference_string


class _TestWquallabImport(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TestWquallabImport.temp_db_path

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten.midvatten(self.iface)

        try:
            os.remove(TestWquallabImport.temp_db_path)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TestWquallabImport.temp_db_path)

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wquallab_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        utils.sql_alter_db('''insert into zz_staff (staff) values ('teststaff')''')

        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'depth', u'report', u'project', u'staff', u'date_time', u'anameth', u'parameter', u'reading_num', u'reading_txt', u'unit', u'comment'],
             [u'obsid1', u'2', u'testreport', u'testproject', u'teststaff', u'2011-10-19 12:30:00', u'testmethod', u'1,2-Dikloretan', u'1.5', u'<1.5', u'µg/l', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', TestWquallabImport.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser', TestWquallabImport.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _wquallab_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wquallab_import_from_csvlayer)
            _wquallab_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select * from w_qual_lab'''))

        reference_string = ur'''(True, [(obsid1, 2.0, testreport, testproject, teststaff, 2011-10-19 12:30:00, testmethod, 1,2-Dikloretan, 1.5, <1.5, µg/l, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wquallab_import_from_csvlayer_depth_empty_string(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        utils.sql_alter_db('''insert into zz_staff (staff) values ('teststaff')''')

        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'depth', u'report', u'project', u'staff', u'date_time', u'anameth', u'parameter', u'reading_num', u'reading_txt', u'unit', u'comment'],
             [u'obsid1', u'', u'testreport', u'testproject', u'teststaff', u'2011-10-19 12:30:00', u'testmethod', u'1,2-Dikloretan', u'1.5', u'<1.5', u'µg/l', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', TestWquallabImport.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser', TestWquallabImport.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def test_wquallab_import_from_csvlayer_depth_empty_string(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wquallab_import_from_csvlayer)
            test_wquallab_import_from_csvlayer_depth_empty_string(self, filename)

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select * from w_qual_lab'''))

        reference_string = ur'''(True, [(obsid1, None, testreport, testproject, teststaff, 2011-10-19 12:30:00, testmethod, 1,2-Dikloretan, 1.5, <1.5, µg/l, testcomment)])'''
        assert test_string == reference_string


class _TestWflowImport(object):
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', autospec=True)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten.midvatten(self.iface)

        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_wflow_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'instrumentid', u'flowtype', u'date_time', u'reading', u'unit', u'comment'],
             [u'obsid1', u'testid', u'Momflow', u'2011-10-19 12:30:00', u'2', u'l/s', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.askuser', TestWflowImport.mock_askuser.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_wflow_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wflow_import_from_csvlayer)
            _test_wflow_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select * from w_flow'''))
        reference_string = ur'''(True, [(obsid1, testid, Momflow, 2011-10-19 12:30:00, 2.0, l/s, testcomment)])'''
        assert test_string == reference_string


class _TestFilterDatesFromFiledata(object):

    def setUp(self):
        self.importinstance = midv_data_importer()

    def test_filter_dates_from_filedata(self):

        file_data = [[u'obsid', u'date_time'], [u'rb1', u'2015-05-01 00:00:00'], [u'rb1', u'2016-05-01 00:00'], [u'rb2', u'2015-05-01 00:00:00'], [u'rb2', u'2016-05-01 00:00'], [u'rb3', u'2015-05-01 00:00:00'], [u'rb3', u'2016-05-01 00:00']]
        obsid_last_imported_dates = {u'rb1': [(datestring_to_date(u'2016-01-01 00:00:00'),)], u'rb2': [(datestring_to_date(u'2017-01-01 00:00:00'),)]}
        test_file_data = utils_for_tests.create_test_string(self.importinstance.filter_dates_from_filedata(file_data, obsid_last_imported_dates))

        reference_file_data = u'''[[obsid, date_time], [rb1, 2016-05-01 00:00], [rb3, 2015-05-01 00:00:00], [rb3, 2016-05-01 00:00]]'''

        assert test_file_data == reference_file_data



