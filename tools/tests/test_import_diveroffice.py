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
#

import utils_for_tests
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from tools.midvatten_utils import get_foreign_keys
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch, call
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, \
    MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, \
    MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
from mock import MagicMock
import io
from midvatten.midvatten import midvatten
import os
import PyQt4
from collections import OrderedDict
from import_data_to_db import midv_data_importer
from import_diveroffice import DiverofficeImport

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)

class TestParseDiverofficeFile(object):
    utils_ask_user_about_stopping = MockReturnUsingDictIn({'Failure, delimiter did not match': 'cancel',
                                                           'Failure: The number of data columns in file': 'cancel',
                                                           'Failure, parsing failed for file': 'cancel'},
                                                          0)

    def setUp(self):
        pass

    def test_parse_diveroffice_file_utf8(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )

        charset_of_diverofficefile = u'utf-8'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)


        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = u'[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == u'rb1'

    def test_parse_diveroffice_file_cp1252(self):

        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26.9,5.18',
             u'2016/03/15 11:00:00,157.7,0.6'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = u'[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == u'rb1'

    def test_parse_diveroffice_file_semicolon_sep(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26.9;5.18',
             u'2016/03/15 11:00:00;157.7;0.6'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = u'[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == u'rb1'

    def test_parse_diveroffice_file_comma_dec(self):

        f = (u'Location=rb1',
             u'Date/time;Water head[cm];Temperature[°C]',
             u'2016/03/15 10:30:00;26,9;5,18',
             u'2016/03/15 11:00:00;157,7;0,6'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = ur'''[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, ], [2016-03-15 11:00:00, 157.7, 0.6, ]]'''
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == u'rb1'

    @mock.patch('import_data_to_db.utils.ask_user_about_stopping', utils_ask_user_about_stopping.get_v)
    def test_parse_diveroffice_file_comma_sep_comma_dec_failed(self):
        f = (u'Location=rb1',
             u'Date/time,Water head[cm],Temperature[°C]',
             u'2016/03/15 10:30:00,26,9,5,18',
             u'2016/03/15 11:00:00,157,7,0,6'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)

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

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data)
        reference_string = 'cancel'
        assert test_string == reference_string

    def test_parse_diveroffice_file_changed_order(self):
        f = (u'Location=rb1',
             u'Temperature[°C];2:Spec.cond.[mS/cm];Date/time;Water head[cm]',
             u'5.18;2;2016/03/15 10:30:00;26.9',
             u'0.6;3;2016/03/15 11:00:00;157.7'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
                file_data = DiverofficeImport.parse_diveroffice_file(path, charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = u'[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, 26.9, 5.18, 2.0], [2016-03-15 11:00:00, 157.7, 0.6, 3.0]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == u'rb1'

    @mock.patch("midvatten_utils.MessagebarAndLog")
    def test_parse_diveroffice_warning_missing_head_cm(self, mock_messagebarandlog):
        f = (u'Location=rb1',
             u'Temperature[°C];2:Spec.cond.[mS/cm];Date/time',
             u'5.18;2;2016/03/15 10:30:00',
             u'0.6;3;2016/03/15 11:00:00'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
            file_data = DiverofficeImport.parse_diveroffice_file(path,
                                                                   charset_of_diverofficefile)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = u'[[date_time, head_cm, temp_degc, cond_mscm], [2016-03-15 10:30:00, , 5.18, 2.0], [2016-03-15 11:00:00, , 0.6, 3.0]]'

        assert len(mock_messagebarandlog.mock_calls) == 1
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == u'rb1'

    @mock.patch("midvatten_utils.MessagebarAndLog")
    def test_parse_diveroffice_warning_missing_date_time(self, mock_messagebarandlog):
        f = (u'Location=rb1',
             u'Temperature[°C];2:Spec.cond.[mS/cm];dada',
             u'5.18;2;2016/03/15 10:30:00',
             u'0.6;3;2016/03/15 11:00:00'
             )

        charset_of_diverofficefile = u'cp1252'
        with utils.tempinput(u'\n'.join(f), charset_of_diverofficefile) as path:
            file_data = DiverofficeImport.parse_diveroffice_file(path,
                                                                   charset_of_diverofficefile)

        assert file_data == u'skip'
        assert len(mock_messagebarandlog.mock_calls) == 1


class TestWlvllogImportFromDiverofficeFiles(object):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(TEMP_DB_PATH)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TEMP_DB_PATH
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
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

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)


                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_skip_duplicate_datetimes(self):
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
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:30', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
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
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb1, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb1, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb1, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb1, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
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

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_try_capitalize(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = u'ok'
                mock_notfoundquestion.return_value.value = u'rb1'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = DiverofficeImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()
                importer.import_all_data.checked = False
                importer.confirm_names.checked = False
                importer.start_import(importer.files,
                                      importer.skip_rows.checked,
                                      importer.confirm_names.checked,
                                      importer.import_all_data.checked)

            _test_wlvllogg_import_from_diveroffice_files(self, filenames)

            test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
            reference_string = ur'''(True, [(Rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (Rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None)])'''
            assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_cancel(self):
        files = [(u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101')
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            filenames = [f1]
            utils_askuser_answer_no_obj = MockUsingReturnValue(None)
            utils_askuser_answer_no_obj.result = 0
            utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

            @mock.patch('import_data_to_db.utils.NotFoundQuestion')
            @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.utils.select_files')
            def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                mock_notfoundquestion.return_value.answer = u'cancel'
                mock_notfoundquestion.return_value.value = u'rb1'
                mock_notfoundquestion.return_value.reuse_column = u'location'
                mock_filenames.return_value = filenames
                mock_encoding.return_value = [u'utf-8']

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = DiverofficeImport(self.iface.mainWindow(), ms)
                importer.select_files_and_load_gui()
                importer.import_all_data.checked = True
                importer.confirm_names.checked = False
                answer = importer.start_import(importer.files,
                                      importer.skip_rows.checked,
                                      importer.confirm_names.checked,
                                      importer.import_all_data.checked)

                return answer

            answer = _test_wlvllogg_import_from_diveroffice_files(self, filenames)
            assert isinstance(answer, utils.Cancel)

            test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
            reference_string = ur'''(True, [])'''
            assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_skip_missing_water_level(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,,101'),
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

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(),
                                                     ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.skip_rows.checked = True
                        importer.start_import(importer.files,
                                              importer.skip_rows.checked,
                                              importer.confirm_names.checked,
                                              importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_not_skip_missing_water_level(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,,101'),
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

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                        mock_notfoundquestion.return_value.answer = u'ok'
                        mock_notfoundquestion.return_value.value = u'rb1'
                        mock_notfoundquestion.return_value.reuse_column = u'location'
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(),
                                                     ms)
                        importer.select_files_and_load_gui()
                        importer.import_all_data.checked = True
                        importer.confirm_names.checked = False
                        importer.skip_rows.checked = False
                        importer.start_import(importer.files,
                                              importer.skip_rows.checked,
                                              importer.confirm_names.checked,
                                              importer.import_all_data.checked)

                    _test_wlvllogg_import_from_diveroffice_files(self,
                                                                 filenames)

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))

                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, None, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_datetime_filter(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101',
                u'2016/06/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                 ]

        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb2")''')
        utils.sql_alter_db(u'''INSERT INTO w_levels_logger ("obsid", "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:

                filenames = [f1, f2]


                @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                @mock.patch('import_data_to_db.utils.askuser')
                @mock.patch('qgis.utils.iface', autospec=True)
                @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                @mock.patch('import_data_to_db.utils.select_files')
                def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion):
                    mock_notfoundquestion.return_value.answer = u'ok'
                    mock_notfoundquestion.return_value.value = u'rb1'
                    mock_notfoundquestion.return_value.reuse_column = u'location'
                    mock_filenames.return_value = filenames
                    mock_encoding.return_value = [u'utf-8']

                    ms = MagicMock()
                    ms.settingsdict = OrderedDict()
                    importer = DiverofficeImport(self.iface.mainWindow(), ms)
                    importer.select_files_and_load_gui()
                    importer.import_all_data.checked = True
                    importer.confirm_names.checked = False
                    importer.date_time_filter.from_date = u'2016-03-15 11:00:00'
                    importer.date_time_filter.to_date = u'2016-04-15 10:30:00'
                    importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked,  importer.date_time_filter.from_date, importer.date_time_filter.to_date)

                _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None)])'''
                assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wlvllogg_import_from_diveroffice_files_skip_obsid(self):
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

        DiverofficeImport.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), DiverofficeImport.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), DiverofficeImport.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), DiverofficeImport.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch("midvatten_utils.MessagebarAndLog")
                    @mock.patch('import_data_to_db.utils.NotFoundQuestion')
                    @mock.patch('midvatten_utils.QgsProject.instance', TestWlvllogImportFromDiverofficeFiles.mock_dbpath.get_v)
                    @mock.patch('import_data_to_db.utils.askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_notfoundquestion, mock_messagebarandlog):

                        mocks_notfoundquestion = []
                        for answer, value in [[u'ok', u'rb1'],
                                              [u'ok', u'rb2'],
                                              [u'skip', u'rb3']]:
                            a_mock = MagicMock()
                            a_mock.answer = answer
                            a_mock.value = value
                            a_mock.reuse_column = u'location'
                            mocks_notfoundquestion.append(a_mock)

                        mock_notfoundquestion.side_effect = mocks_notfoundquestion

                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        ms = MagicMock()
                        ms.settingsdict = OrderedDict()
                        importer = DiverofficeImport(self.iface.mainWindow(), ms)
                        importer.select_files_and_load_gui()

                        importer.start_import(importer.files, importer.skip_rows.checked, importer.confirm_names.checked, importer.import_all_data.checked)

                        print(u'\n'.join([str(x) for x in mock_messagebarandlog.mock_calls]))


                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None)])'''
                    print(test_string)
                    print(reference_string)
                    assert test_string == reference_string


class TestFilterDatesFromFiledata(object):

    def test_filter_dates_from_filedata(self):

        file_data = [[u'obsid', u'date_time'], [u'rb1', u'2015-05-01 00:00:00'], [u'rb1', u'2016-05-01 00:00'], [u'rb2', u'2015-05-01 00:00:00'], [u'rb2', u'2016-05-01 00:00'], [u'rb3', u'2015-05-01 00:00:00'], [u'rb3', u'2016-05-01 00:00']]
        obsid_last_imported_dates = {u'rb1': [(datestring_to_date(u'2016-01-01 00:00:00'),)], u'rb2': [(datestring_to_date(u'2017-01-01 00:00:00'),)]}
        test_file_data = utils_for_tests.create_test_string(DiverofficeImport.filter_dates_from_filedata(file_data, obsid_last_imported_dates))

        reference_file_data = u'''[[obsid, date_time], [rb1, 2016-05-01 00:00], [rb3, 2015-05-01 00:00:00], [rb3, 2016-05-01 00:00]]'''

        assert test_file_data == reference_file_data