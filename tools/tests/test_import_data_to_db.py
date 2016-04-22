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
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance
import mock
import io
import midvatten
import os


class TestFieldLoggerImporter():
    #flow_instrument_id = MockReturnUsingDict({u'Instrument not found': [u'testid', u'']}, 1)
    instrument_staff_questions = MockReturnUsingDict({u'Submit instrument id': MockNotFoundQuestion(u'ok', u'testid'), u'Submit field staff': MockNotFoundQuestion(u'ok', u'teststaff')}, u'dialogtitle')
    prev_used_flow_instr_ids = MockUsingReturnValue((True, {u'Rb1615': [(u'Accvol', u'Flm01', u'2015-01-01 00:00:00'), (u'Momflow', u'Flm02', u'2016-01-01 00:00:00')]}))
    quality_instruments = MockUsingReturnValue((True, (u'instr1', u'instr2', u'instr3')))
    skip_popup = MockUsingReturnValue('')
    notfound_ok = MockUsingReturnValue(MockNotFoundQuestion(u'ok', u'testvalue'))
    existing_staff = MockUsingReturnValue((True, (u'a', u'b')))

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
    #@mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', flow_instrument_id.get_v)
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
    #@mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', flow_instrument_id.get_v)
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

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
    #@mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_staff_initials_list' , existing_staff.get_v)
    def test_fieldlogger_prepare_quality_data(self):
        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;q.syre.%\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            "Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            "Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            ]

        parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        result_list = self.importinstance.fieldlogger_prepare_quality_data(parsed_rows[u'quality'])
        test_string = utils_for_tests.create_test_string(result_list)
        reference_string = u'[[obsid, staff, date_time, instrument, parameter, reading_num, reading_txt, unit, comment], [Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863, 863, µS/cm, hej], [Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 58, 58, %, test], [Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67, 67, mg/L, test], [Rb1512, teststaff, 2016-03-30 15:30:39, , temperatur, 8, 8, grC, test]]'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
    #@mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_staff_initials_list' , existing_staff.get_v)
    def test_fieldlogger_prepare_quality_data_sample(self):

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
        reference_string = u'obsid;staff;date_time;instrument;parameter;reading_num;reading_txt;unit;comment\nRb1512;teststaff;2016-03-30 15:31:30;testid;turbiditet;899;899;FNU;'
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string

    @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
    #@mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
    @mock.patch('import_data_to_db.utils.get_staff_initials_list' , existing_staff.get_v)
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
        file_string = utils.lists_to_string(self.importinstance.fieldlogger_prepare_comments_data(parsed_rows))
        reference_string = u'obsid;date_time;comment;staff\nRb1202;2016-03-30 15:31:30;comment3;teststaff\nRb1505;2016-03-30 15:29:25;comment1;teststaff\nRb1608;2016-03-30 15:34:40;comment4;teststaff\nRb1615;2016-03-30 15:30:10;comment2;teststaff'
        sorted_file_string = u'\n'.join(sorted(file_string.split(u'\n')))
        sorted_reference_string = u'\n'.join(sorted(reference_string.split(u'\n')))
        assert sorted_file_string == sorted_reference_string


    def test_fieldlogger_import(self):
        """ Almost full integration test of fieldlogger import
        :return:
        """
        f = [
            "Location;date_time;value;parameter\n",
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

        self.importinstance.charsetchoosen = [u'utf-8']

        with utils.tempinput(''.join(f)) as filename:
            selected_file = MockUsingReturnValue([filename])
            return_int = MockUsingReturnValue(int)
            mocked_iface = MockQgisUtilsIface()

            instrument_staff_questions = MockReturnUsingDict({u'Submit instrument id': MockNotFoundQuestion(u'ok', u'testid'), u'Submit field staff': MockNotFoundQuestion(u'ok', u'teststaff')}, u'dialogtitle')
            prev_used_flow_instr_ids = MockUsingReturnValue((True, {u'Rb1615': [(u'Accvol', u'Flm01', u'2015-01-01 00:00:00'), (u'Momflow', u'Flm02', u'2016-01-01 00:00:00')]}))
            quality_instruments = MockUsingReturnValue((u'instr1', u'instr2', u'instr3'))
            notfound_ignore = MockUsingReturnValue(MockNotFoundQuestion('ignore', u'Rb1512'))
            mocked_send_file_data_to_importer = MockUsingReturnValue(int)
            skip_popup = MockUsingReturnValue('')
            notfound_ok = MockUsingReturnValue(MockNotFoundQuestion('ok', 'testvalue'))
            existing_staff = MockUsingReturnValue((True, (u'a', u'b')))

            @mock.patch('import_data_to_db.utils.pop_up_info', skip_popup.get_v)
            @mock.patch('midvatten_utils.NotFoundQuestion', notfound_ignore.get_v)
            @mock.patch('import_data_to_db.utils.get_last_used_flow_instruments', prev_used_flow_instr_ids.get_v)
            @mock.patch('import_data_to_db.midv_data_importer.wlvl_import_from_csvlayer', return_int.get_v)
            @mock.patch('import_data_to_db.midv_data_importer.select_files', selected_file.get_v)
            @mock.patch('qgis.utils.iface', mocked_iface)
            #@mock.patch('import_data_to_db.PyQt4.QtGui.QInputDialog.getText', instrument_staff_questions.get_v)
            @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
            @mock.patch('import_data_to_db.midv_data_importer.send_file_data_to_importer', mocked_send_file_data_to_importer.get_v)
            @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
            @mock.patch('import_data_to_db.utils.get_staff_initials_list' , existing_staff.get_v)
            def _test_fieldlogger_import():
                self.importinstance.fieldlogger_import()

            _test_fieldlogger_import()

            #print(','.join(test_utils.dict_to_sorted_list(mocked_send_file_data_to_importer.args_called_with)))

            #TODO: Fix and assert string that works with object instance names.
        #parsed_rows = self.importinstance.fieldlogger_import_parse_rows(f)
        #result_list = utils_for_tests.dict_to_sorted_list(parsed_rows)
        #result_string = ','.join(result_list)
        #reference_string = "flow,Rb1615,2016-03-30 15:30:09,Accvol,m3,357,comment,,gick bra,level,Rb1608,2016-03-30 15:34:13,comment,,ergv,meas,m,555,2016-03-30 15:34:40,comment,,testc,quality,Rb1505,2016-03-30 15:29:26,comment,,hej,konduktivitet,µS/cm,863,Rb1512,2016-03-30 15:30:39,comment,,test,syre,%,58,syre,mg/L,58,temperatur,grC,8,sample,Rb1202,2016-03-30 15:31:30,comment,,hej2,Rb1512,2016-03-30 15:31:30,turbiditet,FNU,899"
        #assert result_string == reference_string


class TestImportWellsFile(object):

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


class notimplementedyet():
    pass
        #class TestCommentsImportFromCsv(object):
    #    utils_verify_table_exists = MockUsingReturnValue(True)
    #    mocked_iface = MockQgisUtilsIface()
    #    alterdb = MockUsingReturnValue(int)
    #
    #    memorydb_obj = MockUsingReturnValue(int)
    #    memorydb_obj.readEntry = lambda x, n: ':memory:'
    #    memorydb = MockUsingReturnValue(memorydb_obj)
    #
    #    def setUp(self):
    #        self.importinstance = midv_data_importer()
    #
    #    @mock.patch('import_data_to_db.QgsProject.instance', memorydb.get_v)
    #    @mock.patch('import_data_to_db.utils.sql_alter_db', alterdb.get_v)
    #    @mock.patch('qgis.utils.iface', mocked_iface)
    #    @mock.patch('import_data_to_db.utils.verify_table_exists', utils_verify_table_exists.get_v)
    #    def test_comments_import_from_csv(self):
    #        """ TODO: NOT IMPLEMENTED TESTThis test is hard to get right due to all the different database calls.
    #        :return:
    #        """
    #        return
    #        file_data = [[u'obsid', u'date_time', u'comment', u'staff'],
    #                     [u'rb1', u'2016-01-01 00:00:00', u'testcomment', u'teststaff']]
    #
    #        self.importinstance.send_file_data_to_importer(file_data, self.importinstance.comments_import_from_csv)


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


class TestWlvlloggImport(object):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """

    def setUp(self):
        self.importinstance = midv_data_importer()

    def test_wlvllogg_import(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/05/15 10:30:00,3,30',
                u'2016/05/15 11:00:00,31,301')
                 ]

        self.importinstance.charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen[0]) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen[0]) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen[0]) as f3:

                    #files = MockReturnUsingDict({u'f1': f1, u'f2': f2, u'f3': f3}, 0)
                    filenames = MockUsingReturnValue([f1, f2, f3])
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)
                    utils_get_all_obsids = MockUsingReturnValue([u'rb1', u'rb2', u'rb3'])
                    utils_sql_load_fr_db = MockReturnUsingDictIn({u'PRAGMA table_info': (True, [(True, u'a'), (True, u'b'), (True, u'c'), (True, u'd'), (True, u'e')]),
                                                                  u'SELECT Count(*)': (True, ((3, ),))},
                                                                 0)
                    qgiscsv2sqlitetable = MockUsingReturnValue(int)
                    cleanuploggerdata = MockUsingReturnValue(1)
                    alterdb = MockUsingReturnValue(int)
                    mocked_iface = MockQgisUtilsIface()
                    skip_popup = MockUsingReturnValue('')

                    self.importinstance.columns = [(True, u'a'), (True, u'b'), (True, u'c'), (True, u'd'), (True, u'e')]
                    self.importinstance.RecordsToImport = ((5,), )
                    self.importinstance.RecordsBefore = ((5, ), )

                    #@mock.patch('import_data_to_db.midv_data_importer.load_diveroffice_file', files.get_v)
                    @mock.patch('qgis.utils.iface', mocked_iface)
                    @mock.patch('import_data_to_db.midv_data_importer.select_files', filenames.get_v)
                    @mock.patch('import_data_to_db.utils.sql_load_fr_db', utils_sql_load_fr_db.get_v)
                    @mock.patch('import_data_to_db.utils.askuser', utils_askuser_answer_no.get_v)
                    @mock.patch('import_data_to_db.utils.sql_alter_db', alterdb.get_v)
                    @mock.patch('import_data_to_db.utils.get_all_obsids', utils_get_all_obsids.get_v)
                    @mock.patch('import_data_to_db.midv_data_importer.qgiscsv2sqlitetable', qgiscsv2sqlitetable.get_v)
                    @mock.patch('import_data_to_db.midv_data_importer.cleanuploggerdata', cleanuploggerdata.get_v)
                    @mock.patch('import_data_to_db.utils.pop_up_info', skip_popup.get_v)
                    def test_wlvllogg_import(self):
                        self.test = 1
                        self.importinstance.wlvllogg_import()

                    test_wlvllogg_import(self)


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

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_verify_table_exists(self):
        exists = utils.verify_table_exists(u'obs_points')
        assert exists

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_import_staff(self):
        self.importinstance.staff_import(u'staff1')
        imported_staff = utils.sql_load_fr_db(u'select * from zz_staff')
        assert imported_staff == (True, [(u'staff1', u'')])

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_import_obsids(self):
        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid2")')
        result = utils.sql_load_fr_db(u'select * from obs_points')

        msgbar = TestDbCalls.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        assert result == (True, [(u'obsid1', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), (u'obsid2', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)])

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
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
        test_flow_type = utils.sql_load_fr_db(u'select * from zz_flowtype')

        msgbar = TestDbCalls.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        assert test_flow_type == reference_flow_type

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
    def test_send_file_data_to_importer_and_comments_import_from_csv(self):
        utils.sql_alter_db("""INSERT INTO obs_points ("obsid") VALUES ('obsid1')""")
        #obsid, date_time, comment, staff
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
            prev_used_flow_instr_ids = MockUsingReturnValue((True, {u'Rb1615': [(u'Accvol', u'Flm01', u'2015-01-01 00:00:00'), (u'Momflow', u'Flm02', u'2016-01-01 00:00:00')]}))
            quality_instruments = MockUsingReturnValue((u'instr1', u'instr2', u'instr3'))
            notfound_ignore = MockUsingReturnValue(MockNotFoundQuestion('ignore', u'Rb1512'))
            notfound_ok = MockUsingReturnValue(MockNotFoundQuestion('ok', 'testvalue'))
            existing_staff = MockUsingReturnValue((True, (u'a', u'b')))
            answer_no_obj = MockUsingReturnValue()
            answer_no_obj.result = 0
            answer_yes_obj = MockUsingReturnValue()
            answer_yes_obj.result = 1
            mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)

            @mock.patch('midvatten_utils.QgsProject.instance', TestDbCalls.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser', mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestDbCalls.skip_popup.get_v)
            #@mock.patch('midvatten_utils.NotFoundQuestion', notfound_ignore.get_v)
            #@mock.patch('import_data_to_db.utils.get_last_used_flow_instruments', prev_used_flow_instr_ids.get_v)
            @mock.patch('import_data_to_db.midv_data_importer.select_files', selected_file.get_v)
            @mock.patch('qgis.utils.iface', mocked_iface)
            @mock.patch('import_data_to_db.utils.get_quality_instruments', quality_instruments.get_v)
            @mock.patch('midvatten_utils.NotFoundQuestion', instrument_staff_questions.get_v)
            #@mock.patch('import_data_to_db.utils.get_staff_initials_list' , existing_staff.get_v)
            def _test_fieldlogger_import(mocked_iface):
                utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("Rb1505")')
                utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("Rb1615")')
                utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("Rb1512")')
                utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("Rb1202")')
                utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("Rb1608")')
                self.importinstance.fieldlogger_import()
                test_data = utils_for_tests.create_test_string(dict([(k, utils.sql_load_fr_db(u'select * from %s'%k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
                reference_data = u"{comments: (True, [(Rb1608, 2016-03-30 15:34:40, testc, teststaff), (Rb1202, 2016-03-30 15:31:30, hej2, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv)]), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, ), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, hej), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, test), (Rb1512, teststaff, 2016-03-30 15:30:39, , temperatur, 8.0, 8, grC, test), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, )]), zz_staff: (True, [(teststaff, )])}"

                #print("Messagebar: \n" + str(mock_askuser.args_called_with) + " \n")
                msgbar = mocked_iface.messagebar.messages
                if msgbar:
                    print str(msgbar)

                assert test_data == reference_data

            _test_fieldlogger_import(mocked_iface)

    def tearDown(self):
        #Delete database
        os.remove(TestDbCalls.temp_db_path)


class _TestObsPointsTriggers(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    #temp_db_path = '/home/henrik/temp/tmp_midvatten_temp_db.sqlite'
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_no_obj = MockUsingReturnValue()
    answer_no_obj.result = 0
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    crs_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no_obj, u'Please note!\nThere are ': answer_yes_obj}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten.midvatten(self.iface)
        try:
            os.remove(TestObsPointsTriggers.temp_db_path)
        except OSError:
            pass
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()
        utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_insert_obs_points_geom_fr_coords""")
        utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_update_obs_points_geom_fr_coords""")
        utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_insert_obs_points_coords_fr_geom""")
        utils.sql_alter_db(u"""DROP TRIGGER IF EXISTS after_update_obs_points_coords_fr_geom""")

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_triggers_not_change_existing(self):
        """ Adding triggers should not automatically change the db """
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        utils.add_triggers_to_obs_points()
        reference_string = u'(True, [(rb1, 1.0, 1.0, None)])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_geometry_from_east_north(self):
        """ Test that adding triggers and adding obsid with east, north also adds geometry
        :return:
        """
        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_east_north_from_geometry(self):
        """ Test that adding triggers and adding obsid with geometry also adds east, north
        :return:
        """
        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_trigger_add_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and adding obsid don't set null values for previous obsid.
        :return:
        """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from geometry don't set null values for previous obsid.
        :return:
        """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and adding obsid from east, north don't set null values for previous obsid.
        :return:
        """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb1', 1, 1)""")

        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north) VALUES ('rb2', 2, 2)""")

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_update_geometry_from_east_north(self):
        """ Test that adding triggers and updating obsid with east, north also updates geometry
        :return:
        """
        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', 1, 1)''')
        utils.sql_alter_db(u'''UPDATE obs_points SET east = 2, north = 2 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_update_east_north_from_geometry(self):
        """ Test that adding triggers and updating obsid with geometry also updates east, north
        :return:
        """
        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        utils.sql_alter_db(u'''UPDATE obs_points SET geometry = GeomFromText('POINT(2.0 2.0)', 3006) WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_trigger_update_geometry_not_nulling_geometry(self):
        """ Test that adding triggers and updating obsid don't set null values for previous obsid.
        :return:
        """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb2', GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u'''UPDATE obs_points SET geometry = GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, None, None, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_update_trigger_add_geometry_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from geometry don't set null values for previous obsid.
        :return:
        """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, GeomFromText('POINT(1.0 1.0)', 3006))""")
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, GeomFromText('POINT(2.0 2.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u'''UPDATE obs_points SET geometry = GeomFromText('POINT(3.0 3.0)', 3006) WHERE (obsid = 'rb1')''')
        #After the second: u'(True, [(rb1, 1.0, 1.0, POINT(1 1)), (rb2, 2.0, 2.0, POINT(2 2))])

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_update_trigger_add_east_north_not_nulling_east_north(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb1', 1, 1, GeomFromText('POINT(1.0 1.0)', 3006))""")
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, east, north, geometry) VALUES ('rb2', 2, 2, GeomFromText('POINT(2.0 2.0)', 3006))""")

        utils.add_triggers_to_obs_points()

        utils.sql_alter_db(u'''UPDATE obs_points SET east = 3, north = 3 WHERE (obsid = 'rb1')''')

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 3.0, POINT(3 3)), (rb2, 2.0, 2.0, POINT(2 2))])'
        assert test_string == reference_string

    def tearDown(self):
        #Delete database
        os.remove(TestObsPointsTriggers.temp_db_path)



