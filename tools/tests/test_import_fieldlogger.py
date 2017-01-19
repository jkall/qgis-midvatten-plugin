# -*- coding: utf-8 -*-
import utils_for_tests
import midvatten_utils as utils
from date_utils import datestring_to_date
from tools.tests.mocks_for_tests import DummyInterface
from mock import MagicMock, call
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDictIn, MockQgisUtilsIface, MockQgsProjectInstance, mock_answer
import mock
from midvatten.midvatten import midvatten
import os
import import_fieldlogger
from import_fieldlogger import FieldloggerImport, InputFields
from collections import OrderedDict
from utils_for_tests import create_test_string

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)

class TestFieldLoggerImporterDb(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', DBPATH_QUESTION.get_v)
    def setUp(self, mock_locale):
        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_staff_not_given(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')

        f = [
            u"Location;date_time;value;comment\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _test_staff_not_given(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename ):
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                importer.start_import(importer.observations)
                mock_MessagebarAndLog.critical.assert_called_with(bar_msg=u'Import error, staff not given')

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_full_integration_test_to_db(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1202")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1608")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1615")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1505")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1512")''')
        utils.sql_alter_db(u'''INSERT INTO zz_staff ("staff") VALUES ("teststaff")''')

        utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype ("type") VALUES ("Accvol")''')

        f = [
            u"Location;date_time;value;comment\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_fieldlogger.utils.askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _full_integration_test_to_db(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
                mock_vacuum.return_value.result = 1
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]
                mock_ask_instrument.return_value.value = u'testid'

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_fieldlogger.StaffQuestion):
                        setting.staff = u'teststaff'

                stored_settings = [[u's.comment', [[u'import_method', u'comments']]],
                                   [u'l.comment', [[u'import_method', u'comments']]],
                                   [u'f.comment', [[u'import_method', u'comments']]],
                                   [u'q.comment', [[u'import_method', u'comments']]],
                                   [u'l.meas.m', [[u'import_method', u'w_levels']]],
                                   [u'f.Accvol.m3', [[u'import_method', u'w_flow'], [u'flowtype', u'Accvol'], [u'unit', u'm3']]],
                                   [u's.turbiditet.FNU', [[u'import_method', u'w_qual_field'], [u'parameter', u'turbiditet'], [u'unit', u'FNU'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.konduktivitet.µS/cm', [[u'import_method', u'w_qual_field'], [u'parameter', u'konduktivitet'], [u'unit', u'µS/cm'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.mg/L', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'mg/L'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.%', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'%'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.temperatur.grC', [[u'import_method', u'w_qual_field'], [u'parameter', u'temperatur'], [u'unit', u'grC'], [u'depth', u''], [u'instrument', u'testid']]]]
                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _full_integration_test_to_db(self, filename)

            test_string = create_test_string(dict([(k, utils.sql_load_fr_db(u'select * from %s'%k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1202, 2016-03-30 15:31:30, hej2, teststaff), (Rb1608, 2016-03-30 15:34:40, testc, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv)]), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, None), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, None), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_full_into_zz_flowtype(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("2")''')
        #utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("5")''')
        f = [u'LOCATION;DATE;TIME;VALUE;TYPE\n',
            u'5.2892.level;12-12-2016;10:02:49;comment;l.comment\n',
            u'5.2892.level;12-12-2016;10:02:49;123;meas.m\n',
            u'5.2892.level;12-12-2016;10:02:57;onlycomment;l.comment\n',
            u'2.2892.flow;12-12-2016;10:03:07;123;Aveflow.m3/s\n',
            u'2.2892.flow;12-12-2016;10:03:15;onlycomment;f.comment\n',
            u'2.2892.comment;12-12-2016;10:03:24;onlycomment;comment\n']

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_fieldlogger.utils.askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_askuser):
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]
                mock_ask_instrument.return_value.value = u'testid'

                def side_effect(*args, **kwargs):
                    mock_result = mock.MagicMock()
                    if len(args) > 1:
                        if args[1].startswith(u'Do you want to confirm'):
                            mock_result.result = 0
                            return mock_result
                        elif args[1].startswith(u'Do you want to import all'):
                            mock_result.result = 0
                            return mock_result
                        elif args[1].startswith(u'Please note!\nForeign keys'):
                            mock_result.result = 1
                            return mock_result
                        elif args[1].startswith(u'Please note!\nThere are'):
                            mock_result.result = 1
                            return mock_result
                        elif args[1].startswith(u'It is a strong recommendation'):
                            mock_result.result = 0
                            return mock_result

                mock_askuser.side_effect = side_effect


                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_fieldlogger.StaffQuestion):
                        setting.staff = u'teststaff'

                stored_settings = [[u'f.comment', [[u'import_method', u'comments']]],
                                   [u'Aveflow.m3/s', [[u'import_method', u'w_flow'], [u'flowtype', u'Momflow2'], [u'unit', u'aunit']]]]

                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, utils.sql_load_fr_db(u'select * from %s'%k)) for k in (u'w_flow', u'zz_staff', u'comments', u'zz_flowtype')]))
            reference_string = u'{comments: (True, [(2, 2016-12-12 10:03:15, onlycomment, teststaff)]), w_flow: (True, [(2, testid, Momflow2, 2016-12-12 10:03:07, 123.0, aunit, None)]), zz_flowtype: (True, [(Accvol, Accumulated volume), (Momflow, Momentary flow rate), (Aveflow, Average flow since last reading), (Momflow2, None)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string


class TestFieldLoggerImporterNoDb(object):

    @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
    @mock.patch('import_fieldlogger.utils.get_last_used_flow_instruments')
    def test_prepare_w_flow_data(self, mock_flow_instruments, mock_instrument_not_found):
        mock_flow_instruments = [True, {}]
        mock_instrument_not_found.return_value.answer = u'ok'
        mock_instrument_not_found.return_value.value = u'inst1'
        observations = [{u'obsid': u'obs1', u'flowtype': u'atype', u'date_time': datestring_to_date(u'2016-01-01 00:00'), u'unit': u'aunit', u'value': u'123,4'}]
        test_string = create_test_string(FieldloggerImport.prepare_w_flow_data(observations))
        reference_string = u'[[obsid, instrumentid, flowtype, date_time, reading, unit, comment], [obs1, inst1, atype, 2016-01-01 00:00:00, 123.4, aunit, ]]'
        assert test_string == reference_string

    @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
    @mock.patch('import_fieldlogger.utils.get_last_used_flow_instruments')
    def test_prepare_w_flow_data_assert_only_ask_instrument_once(self, mock_flow_instruments,
                                 mock_instrument_not_found):
        mock_flow_instruments = [True, {}]
        mock_instrument_not_found.return_value.answer = u'ok'
        mock_instrument_not_found.return_value.value = u'inst1'
        observations = [{u'obsid': u'obs1', u'flowtype': u'atype',
                         u'date_time': datestring_to_date(u'2016-01-01 00:00'),
                         u'unit': u'aunit', u'value': u'123,4'},
                        {u'obsid': u'obs1', u'flowtype': u'atype',
                         u'date_time': datestring_to_date(u'2016-01-02 00:00'),
                         u'unit': u'aunit', u'value': u'223,4'}]
        test_string = create_test_string(FieldloggerImport.prepare_w_flow_data(observations))
        mock_instrument_not_found.assert_called_once_with(combobox_label=u'Instrument id:s in database.\nThe last used instrument id for the current obsid is prefilled:', default_value=u'', dialogtitle=u'Submit instrument id', existing_list=[u''], msg=u'Submit the instrument id for the measurement:\n obs1, 2016-01-01 00:00:00, atype, aunit')
        reference_string = u'[[obsid, instrumentid, flowtype, date_time, reading, unit, comment], [obs1, inst1, atype, 2016-01-01 00:00:00, 123.4, aunit, ], [obs1, inst1, atype, 2016-01-02 00:00:00, 223.4, aunit, ]]'
        assert test_string == reference_string

    @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
    @mock.patch('import_fieldlogger.utils.get_last_used_flow_instruments')
    def test_prepare_w_flow_data_assert_only_ask_instrument_twice(self, mock_flow_instruments,
                                 mock_instrument_not_found):
        mock_flow_instruments = [True, {}]
        mock_instrument_not_found.return_value.answer = u'ok'
        mock_instrument_not_found.return_value.value = u'inst1'
        observations = [{u'obsid': u'obs1', u'flowtype': u'atype',
                         u'date_time': datestring_to_date(u'2016-01-01 00:00'),
                         u'unit': u'aunit', u'value': u'123,4'},
                        {u'obsid': u'obs2', u'flowtype': u'atype',
                         u'date_time': datestring_to_date(u'2016-01-02 00:00'),
                         u'unit': u'aunit', u'value': u'223,4'},
                        {u'obsid': u'obs2', u'flowtype': u'atype',
                         u'date_time': datestring_to_date(u'2016-01-03 00:00'),
                         u'unit': u'aunit', u'value': u'223,4'}]
        test_string = create_test_string(FieldloggerImport.prepare_w_flow_data(observations))
        expected_calls = [call(combobox_label=u'Instrument id:s in database.\nThe last used instrument id for the current obsid is prefilled:', default_value=u'', dialogtitle=u'Submit instrument id', existing_list=[u''], msg=u'Submit the instrument id for the measurement:\n obs1, 2016-01-01 00:00:00, atype, aunit'),
 call(combobox_label=u'Instrument id:s in database.\nThe last used instrument id for the current obsid is prefilled:', default_value=u'', dialogtitle=u'Submit instrument id', existing_list=[u''], msg=u'Submit the instrument id for the measurement:\n obs2, 2016-01-02 00:00:00, atype, aunit')]
        assert mock_instrument_not_found.mock_calls == expected_calls
        reference_string = u'[[obsid, instrumentid, flowtype, date_time, reading, unit, comment], [obs1, inst1, atype, 2016-01-01 00:00:00, 123.4, aunit, ], [obs2, inst1, atype, 2016-01-02 00:00:00, 223.4, aunit, ], [obs2, inst1, atype, 2016-01-03 00:00:00, 223.4, aunit, ]]'
        assert test_string == reference_string

    def test_load_file(self):

        f = [
            u"Location;date_time;value;comment\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename ):
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]

                test_string = create_test_string(FieldloggerImport.select_file_and_parse_rows(FieldloggerImport.parse_rows))
                return test_string

            test_string = _test(self, filename)
            reference = u'[{date_time: 2016-03-30 15:29:26, parametername: q.comment, sublocation: Rb1505.quality, value: hej}, {date_time: 2016-03-30 15:30:39, parametername: q.syre.mg/L, sublocation: Rb1512.quality, value: 67}, {date_time: 2016-03-30 15:31:30, parametername: s.turbiditet.FNU, sublocation: Rb1512.sample, value: 899}, {date_time: 2016-03-30 15:29:26, parametername: q.konduktivitet.µS/cm, sublocation: Rb1505.quality, value: 863}, {date_time: 2016-03-30 15:30:09, parametername: f.comment, sublocation: Rb1615.flow, value: gick bra}, {date_time: 2016-03-30 15:30:40, parametername: q.syre.%, sublocation: Rb1512.quality, value: 58}, {date_time: 2016-03-30 15:34:13, parametername: l.meas.m, sublocation: Rb1608.level, value: 555}, {date_time: 2016-03-30 15:30:39, parametername: q.comment, sublocation: Rb1512.quality, value: test}, {date_time: 2016-03-30 15:31:30, parametername: s.comment, sublocation: Rb1202.sample, value: hej2}, {date_time: 2016-03-30 15:34:40, parametername: l.comment, sublocation: Rb1608.level, value: testc}, {date_time: 2016-03-30 15:30:09, parametername: f.Accvol.m3, sublocation: Rb1615.flow, value: 357}, {date_time: 2016-03-30 15:34:13, parametername: l.comment, sublocation: Rb1608.level, value: ergv}, {date_time: 2016-03-30 15:30:39, parametername: q.temperatur.grC, sublocation: Rb1512.quality, value: 8}]'
            assert test_string == reference


class TestCommentsImportFields(object):
    def setUp(self):
        mock_import_method_chooser = MagicMock()
        mock_import_method_chooser.parameter_name = u'comment'
        self.comments_import = import_fieldlogger.CommentsImportFields(mock_import_method_chooser, None)

    def test_alter_data(self):
        observations = [{u'parametername': u'comment',
                         u'date_time': datestring_to_date(u'2016-01-01'),
                         u'sublocation': u'1',
                         u'value': u'shared_comment'},
                        {u'parametername': u'par_get_shared_comment',
                         u'date_time': datestring_to_date(u'2016-01-01'),
                         u'sublocation': u'1',
                         u'value': u'1'},
                        {u'parametername': u'par_not_get_shared_comment',
                         u'date_time': datestring_to_date(u'2016-01-02'),
                         u'sublocation': u'2',
                         u'value': u'1'},
                        {u'parametername': u'par_not_get_shared_comment',
                         u'date_time': datestring_to_date(u'2016-01-04'),
                         u'sublocation': u'1',
                         u'value': u'1'},
                        {u'parametername': u'comment',
                         u'date_time': datestring_to_date(u'2016-01-03'),
                         u'sublocation': u'1',
                         u'value': u'not_shared_comment'}
                        ]
        observations = self.comments_import.alter_data(observations)

        test_string = create_test_string(observations)
        reference_string = u'[{date_time: 2016-01-01 00:00:00, parametername: comment, skip_comment_import: True, sublocation: 1, value: shared_comment}, {comment: shared_comment, date_time: 2016-01-01 00:00:00, parametername: par_get_shared_comment, sublocation: 1, value: 1}, {date_time: 2016-01-02 00:00:00, parametername: par_not_get_shared_comment, sublocation: 2, value: 1}, {date_time: 2016-01-04 00:00:00, parametername: par_not_get_shared_comment, sublocation: 1, value: 1}, {date_time: 2016-01-03 00:00:00, parametername: comment, sublocation: 1, value: not_shared_comment}]'
        assert test_string == reference_string


class TestStaffQuestion(object):

    @mock.patch('import_fieldlogger.defs.staff_list')
    def setUp(self, mock_stafflist):
        mock_stafflist.return_value = (True, [u'staff1', u'staff2'])
        self.staff_question = import_fieldlogger.StaffQuestion()

    def test_alter_data(self):
        observation = {u'sublocation': u'1'}

        self.staff_question.staff = u'teststaff'
        test_string = create_test_string(self.staff_question.alter_data(observation))
        reference_string = u'{staff: teststaff, sublocation: 1}'
        assert test_string == reference_string


class TestObsidFilter(object):
    def setUp(self):
        self.obsid_filter = import_fieldlogger.ObsidFilter()

    @mock.patch('import_fieldlogger.utils.get_all_obsids')
    def test_alter_data(self, mock_get_all_obsids):
        mock_get_all_obsids.return_value = [u'rb1', u'rb2']

        observations = [{u'sublocation': u'rb1'}, {u'sublocation': u'rb2'}]

        test_string = create_test_string(self.obsid_filter.alter_data(observations))
        reference_string = u'[{obsid: rb1, sublocation: rb1}, {obsid: rb2, sublocation: rb2}]'
        assert test_string == reference_string

@mock.patch('import_fieldlogger.utils.MessagebarAndLog')
@mock.patch('import_fieldlogger.defs.w_qual_field_parameter_units')
def test_set_parameters_using_stored_settings(mock_w_qual_field_parameter_units, mock_mock_message_bar):
    mock_w_qual_field_parameter_units.retun_value = {}

    stored_settings = [[u's.comment', [[u'import_method', u'comments']]],
                   [u'l.meas.m', [[u'import_method', u'w_level']]],
                   [u'f.Accvol.m3', [[u'import_method', u'w_flow'], [u'flowtype', u'Accvol'], [u'unit', u'm3']]],
                   [u's.turbiditet.FNU', [[u'import_method', u'w_qual_field'], [u'parameter', u'turbiditet'], [u'unit', u'FNU'], [u'depth', u'1'], [u'instrument', u'testid']]]]

    mock_connect = MagicMock()
    input_fields = InputFields(mock_connect)
    input_fields.parameter_imports = OrderedDict([(k, import_fieldlogger.ImportMethodChooser(k, [x[0] for x in stored_settings], mock_connect)) for k in [x[0] for x in stored_settings]])

    input_fields.set_parameters_using_stored_settings(stored_settings)

    settings = []
    for k, v in input_fields.parameter_imports.iteritems():
        try:
            setting = v.parameter_import_fields.get_settings()
        except Exception, e:
            pass
        else:
            settings.append((k, setting))
    test_string = create_test_string(settings)
    reference_string = u'[(f.Accvol.m3, ((flowtype, Accvol), (unit, m3))), (s.turbiditet.FNU, ((parameter, turbiditet), (unit, FNU), (depth, 1), (instrument, testid)))]'
    assert test_string == reference_string

    new_stored = []
    input_fields.update_stored_settings(new_stored)
    test_string = create_test_string(new_stored)
    reference_string = u'[[s.comment, [(import_method, comments)]], [f.Accvol.m3, [(import_method, w_flow), (flowtype, Accvol), (unit, m3)]], [s.turbiditet.FNU, [(import_method, w_qual_field), (parameter, turbiditet), (unit, FNU), (depth, 1), (instrument, testid)]]]'
    assert test_string == reference_string


def test_SublocationFilter():
    sublocation_filter = import_fieldlogger.SublocationFilter([u'a.1', u'a.2'])

    assert u'{sublocation: a.1}' == create_test_string(sublocation_filter.alter_data({u'sublocation': u'a.1'}))

    sublocation_filter.set_selection([u'a.1'], False)
    assert sublocation_filter.alter_data({u'sublocation': u'a.1'}) is None
    assert u'{sublocation: a.2}' == create_test_string(sublocation_filter.alter_data({u'sublocation': u'a.2'}))

    sublocation_filter.set_selection([u'a.1'], True)
    assert u'{sublocation: a.1}' == create_test_string(sublocation_filter.alter_data({u'sublocation': u'a.1'}))
    assert u'{sublocation: a.2}' == create_test_string(sublocation_filter.alter_data({u'sublocation': u'a.2'}))






