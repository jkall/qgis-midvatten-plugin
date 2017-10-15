# -*- coding: utf-8 -*-
import copy
from collections import OrderedDict

import db_utils
import import_fieldlogger
import midvatten_utils as utils
import mock
from import_fieldlogger import FieldloggerImport, DateTimeFilter
from mock import MagicMock
from nose.plugins.attrib import attr

import utils_for_tests
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDictIn, MockQgisUtilsIface, mock_answer
from utils_for_tests import create_test_string


@attr(status='on')
class TestFieldLoggerImporterDb(utils_for_tests.MidvattenTestSpatialiteDbSv):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_staff_not_given(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test_staff_not_given(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename ):
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                importer.start_import(importer.observations)
                mock_MessagebarAndLog.critical.assert_called_with(bar_msg=u'Import error, staff not given')

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
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
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

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

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1202, 2016-03-30 15:31:30, hej2, teststaff), (Rb1608, 2016-03-30 15:34:40, testc, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv)]), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, None), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, None), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_w_levels_value_to_level_masl(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
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
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

                stored_settings = [[u's.comment', [[u'import_method', u'comments']]],
                                   [u'l.comment', [[u'import_method', u'comments']]],
                                   [u'f.comment', [[u'import_method', u'comments']]],
                                   [u'q.comment', [[u'import_method', u'comments']]],
                                   [u'l.meas.m', [[u'import_method', u'w_levels'], [u'value_column', u'level_masl']]],
                                   [u'f.Accvol.m3', [[u'import_method', u'w_flow'], [u'flowtype', u'Accvol'], [u'unit', u'm3']]],
                                   [u's.turbiditet.FNU', [[u'import_method', u'w_qual_field'], [u'parameter', u'turbiditet'], [u'unit', u'FNU'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.konduktivitet.µS/cm', [[u'import_method', u'w_qual_field'], [u'parameter', u'konduktivitet'], [u'unit', u'µS/cm'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.mg/L', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'mg/L'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.%', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'%'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.temperatur.grC', [[u'import_method', u'w_qual_field'], [u'parameter', u'temperatur'], [u'unit', u'grC'], [u'depth', u''], [u'instrument', u'testid']]]]
                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1202, 2016-03-30 15:31:30, hej2, teststaff), (Rb1608, 2016-03-30 15:34:40, testc, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, None, None, 555.0, ergv)]), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, None), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, None), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_w_levels_value_to_meas(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
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
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

                stored_settings = [[u's.comment', [[u'import_method', u'comments']]],
                                   [u'l.comment', [[u'import_method', u'comments']]],
                                   [u'f.comment', [[u'import_method', u'comments']]],
                                   [u'q.comment', [[u'import_method', u'comments']]],
                                   [u'l.meas.m', [[u'import_method', u'w_levels'], [u'value_column', u'meas']]],
                                   [u'f.Accvol.m3', [[u'import_method', u'w_flow'], [u'flowtype', u'Accvol'], [u'unit', u'm3']]],
                                   [u's.turbiditet.FNU', [[u'import_method', u'w_qual_field'], [u'parameter', u'turbiditet'], [u'unit', u'FNU'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.konduktivitet.µS/cm', [[u'import_method', u'w_qual_field'], [u'parameter', u'konduktivitet'], [u'unit', u'µS/cm'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.mg/L', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'mg/L'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.%', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'%'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.temperatur.grC', [[u'import_method', u'w_qual_field'], [u'parameter', u'temperatur'], [u'unit', u'grC'], [u'depth', u''], [u'instrument', u'testid']]]]
                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1202, 2016-03-30 15:31:30, hej2, teststaff), (Rb1608, 2016-03-30 15:34:40, testc, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv)]), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, None), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, None), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_w_levels_value_to_both(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1608.level;30-03-2016;15:34:14;777;l.masl.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
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
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

                stored_settings = [[u's.comment', [[u'import_method', u'comments']]],
                                   [u'l.comment', [[u'import_method', u'comments']]],
                                   [u'f.comment', [[u'import_method', u'comments']]],
                                   [u'q.comment', [[u'import_method', u'comments']]],
                                   [u'l.meas.m', [[u'import_method', u'w_levels'], [u'value_column', u'meas']]],
                                    [u'l.masl.m', [[u'import_method', u'w_levels'], [u'value_column', u'level_masl']]],
                                   [u'f.Accvol.m3', [[u'import_method', u'w_flow'], [u'flowtype', u'Accvol'], [u'unit', u'm3']]],
                                   [u's.turbiditet.FNU', [[u'import_method', u'w_qual_field'], [u'parameter', u'turbiditet'], [u'unit', u'FNU'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.konduktivitet.µS/cm', [[u'import_method', u'w_qual_field'], [u'parameter', u'konduktivitet'], [u'unit', u'µS/cm'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.mg/L', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'mg/L'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.%', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'%'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.temperatur.grC', [[u'import_method', u'w_qual_field'], [u'parameter', u'temperatur'], [u'unit', u'grC'], [u'depth', u''], [u'instrument', u'testid']]]]
                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1202, 2016-03-30 15:31:30, hej2, teststaff), (Rb1608, 2016-03-30 15:34:40, testc, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv), (Rb1608, 2016-03-30 15:34:14, None, None, 777.0, None)]), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, None), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, None), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_datetimefilter(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
                mock_vacuum.return_value.result = 1
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]
                mock_ask_instrument.return_value.value = u'testid'

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                for setting in importer.settings:
                    if isinstance(setting, DateTimeFilter):
                        setting.to_date = u'2016-03-30 15:30:40'
                        break

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_fieldlogger.StaffQuestion):
                        setting.staff = u'teststaff'
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

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

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, []), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, []), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_datetimefilter_still_work_after_update_button(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
                mock_vacuum.return_value.result = 1
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]
                mock_ask_instrument.return_value.value = u'testid'

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()



                for setting in importer.settings:
                    if isinstance(setting, DateTimeFilter):
                        setting.to_date = u'2016-03-30 15:30:40'
                        break

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_fieldlogger.StaffQuestion):
                        setting.staff = u'teststaff'
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

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

                importer.input_fields.update_parameter_imports_queue(
                    importer.filter_by_settings_using_shared_loop(
                        importer.observations,
                        importer.settings), importer.stored_settings)

                importer.input_fields.set_parameters_using_stored_settings(
                    stored_settings)

                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, []), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, []), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_change_datetimefilter_after_update_button(self):
        #Changing datetime filter should reset sublocation filter and input fields and
        #input fields should yet again be set from stored settings. Thus, the only
        #filter left would be datetime filter.
        #
        #I haven't found a way to activate the connected signals to make this work though.
        #So the test more more or less tests that changing filters many times doesn't
        #break the final result.

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
                mock_vacuum.return_value.result = 1
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]
                mock_ask_instrument.return_value.value = u'testid'

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()
                for setting in importer.settings:
                    if isinstance(setting, DateTimeFilter):
                        setting.to_date = u'2016-03-30 15:30:40'
                        break

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_fieldlogger.StaffQuestion):
                        setting.staff = u'teststaff'
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

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

                importer.input_fields.update_parameter_imports(
                    importer.filter_by_settings_using_shared_loop(
                        importer.observations,
                        importer.settings), importer.stored_settings)

                importer.input_fields.set_parameters_using_stored_settings(
                    stored_settings)

                for setting in importer.settings:
                    if isinstance(setting, DateTimeFilter):
                        setting.to_date = u'2016-03-30 15:31:59'
                        break

                importer.update_sublocations_and_inputfields_on_date_change()
                importer.update_input_fields_from_button()
                importer.input_fields.set_parameters_using_stored_settings(stored_settings)

                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1202, 2016-03-30 15:31:30, hej2, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, []), w_qual_field: (True, [(Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, None), (Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, None), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_changeing_filter_must_not_change_observations_before_import(self):
        #Changing datetime filter should reset sublocation filter and input fields and
        #input fields should yet again be set from stored settings. Thus, the only
        #filter left would be datetime filter.

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1202')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1608')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1615')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1505')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('Rb1512')''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
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
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
                mock_vacuum.return_value.result = 1
                mock_charset.return_value = ('utf-8', True)
                mock_savefilename.return_value = [filename]
                mock_ask_instrument.return_value.value = u'testid'

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()
                obs_before = copy.deepcopy(importer.observations)

                for setting in importer.settings:
                    if isinstance(setting, DateTimeFilter):
                        setting.to_date = u'2016-03-30 15:30:40'
                        break

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_fieldlogger.StaffQuestion):
                        setting.staff = u'teststaff'
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

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

                importer.input_fields.update_parameter_imports(
                    importer.filter_by_settings_using_shared_loop(
                        importer.observations,
                        importer.settings), importer.stored_settings)

                importer.input_fields.set_parameters_using_stored_settings(
                    stored_settings)

                for setting in importer.settings:
                    if isinstance(setting, DateTimeFilter):
                        setting.to_date = u'2016-03-30 15:31:59'
                        break

                obs_after = copy.deepcopy(importer.observations)
                return obs_before, obs_after

            obs_before, obs_after = _test(self, filename)

            assert create_test_string(obs_before) == create_test_string(obs_after)

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_into_zz_flowtype(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('2')''')
        #db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('5')''')
        f = [u'LOCATION;DATE;TIME;VALUE;TYPE\n',
            u'5.2892.level;12-12-2016;10:02:49;comment;l.comment\n',
            u'5.2892.level;12-12-2016;10:02:49;123;meas.m\n',
            u'5.2892.level;12-12-2016;10:02:57;onlycomment;l.comment\n',
            u'2.2892.flow;12-12-2016;10:03:07;123;Aveflow.m3/s\n',
            u'2.2892.flow;12-12-2016;10:03:15;onlycomment;f.comment\n',
            u'2.2892.comment;12-12-2016;10:03:24;onlycomment;comment\n']

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
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
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = False

                stored_settings = [[u'f.comment', [[u'import_method', u'comments']]],
                                   [u'Aveflow.m3/s', [[u'import_method', u'w_flow'], [u'flowtype', u'Momflow2'], [u'unit', u'aunit']]]]

                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'SELECT * FROM %s' % k)) for k in (u'w_flow', u'zz_staff', u'comments', u'zz_flowtype')]))
            reference_string = u'{comments: (True, [(2, 2016-12-12 10:03:15, onlycomment, teststaff)]), w_flow: (True, [(2, testid, Momflow2, 2016-12-12 10:03:07, 123.0, aunit, None)]), zz_flowtype: (True, [(Accvol, Accumulated volume), (Momflow, Momentary flow rate), (Aveflow, Average flow since last reading), (Momflow2, None)]), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string

    @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
    def test_full_integration_test_to_db_w_levels_value_calculate_level_masl(self):
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('Rb1202', 0)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('Rb1608', 0)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('Rb1615', NULL)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('Rb1505', 0)''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid, h_toc) VALUES ('Rb1512', 10)''')
        db_utils.sql_alter_db(u'''INSERT INTO zz_staff (staff) VALUES ('teststaff')''')

        db_utils.sql_alter_db(u'''INSERT or ignore INTO zz_flowtype (type) VALUES ('Accvol')''')

        f = [
            u"LOCATION;DATE;TIME;VALUE;TYPE\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1615.level;29-03-2016;15:34:13;ergv2;l.comment\n",
            u"Rb1615.level;31-03-2016;15:34:13;ergv1;l.comment\n",
            u"Rb1615.level;31-03-2016;15:34:13;111;l.meas.m\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('import_fieldlogger.utils.Askuser')
            @mock.patch('import_fieldlogger.utils.NotFoundQuestion')
            @mock.patch('import_fieldlogger.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_fieldlogger.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_fieldlogger.utils.MessagebarAndLog')
            @mock.patch('db_utils.QgsProject.instance', utils_for_tests.MidvattenTestSpatialiteNotCreated.mock_instance_settings_database)
            def _test(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename, mock_ask_instrument, mock_vacuum):
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
                    if isinstance(setting, import_fieldlogger.WLevelsImportFields):
                        setting.calculate_level_masl = True

                stored_settings = [[u's.comment', [[u'import_method', u'comments']]],
                                   [u'l.comment', [[u'import_method', u'comments']]],
                                   [u'f.comment', [[u'import_method', u'comments']]],
                                   [u'q.comment', [[u'import_method', u'comments']]],
                                   [u'l.meas.m', [[u'import_method', u'w_levels'], [u'value_column', u'meas']]],
                                   [u'f.Accvol.m3', [[u'import_method', u'w_flow'], [u'flowtype', u'Accvol'], [u'unit', u'm3']]],
                                   [u's.turbiditet.FNU', [[u'import_method', u'w_qual_field'], [u'parameter', u'turbiditet'], [u'unit', u'FNU'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.konduktivitet.µS/cm', [[u'import_method', u'w_qual_field'], [u'parameter', u'konduktivitet'], [u'unit', u'µS/cm'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.mg/L', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'mg/L'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.syre.%', [[u'import_method', u'w_qual_field'], [u'parameter', u'syre'], [u'unit', u'%'], [u'depth', u''], [u'instrument', u'testid']]],
                                   [u'q.temperatur.grC', [[u'import_method', u'w_qual_field'], [u'parameter', u'temperatur'], [u'unit', u'grC'], [u'depth', u''], [u'instrument', u'testid']]]]
                importer.input_fields.set_parameters_using_stored_settings(stored_settings)
                importer.start_import(importer.observations)

            _test(self, filename)

            test_string = create_test_string(dict([(k, db_utils.sql_load_fr_db(u'select * from %s'%k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            print(test_string)
            reference_string = u'{comments: (True, [(Rb1608, 2016-03-30 15:34:40, testc, teststaff), (Rb1615, 2016-03-29 15:34:13, ergv2, teststaff)]), w_flow: (True, []), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, 0.0, -555.0, ergv), (Rb1615, 2016-03-31 15:34:13, 111.0, None, None, ergv1)]), w_qual_field: (True, []), zz_staff: (True, [(teststaff, None)])}'
            assert test_string == reference_string


