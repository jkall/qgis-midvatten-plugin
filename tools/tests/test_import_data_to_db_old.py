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
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
from midvatten.midvatten import midvatten
import os
import PyQt4
from collections import OrderedDict
from import_data_to_db_old import midv_data_importer, wlvlloggimportclass

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH]}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)

class _TestImportObsPoints(object):
    temp_db_path = TEMP_DB_PATH
    #temp_db_path = '/home/henrik/temp/tmp_midvatten_temp_db.sqlite'
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])
    #mocked_qgsproject = MockQgsProject(mocked_qgsinstance)

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def setUp(self, mock_locale):
        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TestImportObsPoints.temp_db_path)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TestImportObsPoints.temp_db_path)

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.Askuser', mock_askuser.get_v)
    def test_import_obsids_directly(self):
        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid2")')
        result = db_utils.sql_load_fr_db(u'select * from obs_points')

        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        assert result == (True, [(u'obsid1', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), (u'obsid2', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)])

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.Askuser', mock_askuser.get_v)
    def test_import_obs_points(self):

        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            selected_file = MockUsingReturnValue(filename)

            @mock.patch('PyQt4.QtGui.QInputDialog.getText', TestImportObsPoints.mock_encoding.get_v)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName', selected_file.get_v)
            @mock.patch('midvatten_utils.QgsProject.instance', TestImportObsPoints.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser', TestImportObsPoints.mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestImportObsPoints.skip_popup.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test_import_obs_points_using_obsp_import(self, mock_iface):
                self.importinstance.obsp_import()
            _test_import_obs_points_using_obsp_import(self)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html", AsText(geometry) from obs_points'''))
        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, 421484.0, 6542696.0, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, POINT(421484 6542696))])'''
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.Askuser', mock_askuser.get_v)
    def _test_import_obs_points_already_exist(self):

        db_utils.sql_alter_db(u'''insert into obs_points ("obsid") values ('rb1')''')
        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            selected_file = MockUsingReturnValue(filename)

            @mock.patch('PyQt4.QtGui.QInputDialog.getText', TestImportObsPoints.mock_encoding.get_v)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName', selected_file.get_v)
            @mock.patch('midvatten_utils.QgsProject.instance', TestImportObsPoints.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser', TestImportObsPoints.mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestImportObsPoints.skip_popup.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test_import_obs_points_using_obsp_import(self, mock_iface):
                self.importinstance.obsp_import()
                mock_iface.messageBar.return_value.createMessage.assert_called_with(u'Warning, In total 1 posts were not imported.')
                mock_iface.messageBar.return_value.createMessage.assert_called_with(u'In total 0 measurements were imported.')

            _test_import_obs_points_using_obsp_import(self)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html", AsText(geometry) from obs_points'''))
        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages

        #if msgbar:
        #    print str(msgbar)

        reference_string = ur'''(True, [(rb1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)])'''
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.Askuser', mock_askuser.get_v)
    def _test_import_obs_points_duplicates(self):

        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1'],
             [u'rb1', u'rb2', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421485', u'6542697', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1'],
             [u'rb1', u'rb3', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            selected_file = MockUsingReturnValue(filename)

            @mock.patch('PyQt4.QtGui.QInputDialog.getText', TestImportObsPoints.mock_encoding.get_v)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName', selected_file.get_v)
            @mock.patch('midvatten_utils.QgsProject.instance', TestImportObsPoints.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser', TestImportObsPoints.mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestImportObsPoints.skip_popup.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test_import_obs_points_using_obsp_import(self, mock_iface):
                self.importinstance.obsp_import()
                mock_iface.messageBar.return_value.createMessage.assert_called_with(u'Warning, In total 2 posts were not imported.')
                mock_iface.messageBar.return_value.createMessage.assert_called_with(u'In total 1 measurements were imported.')
            _test_import_obs_points_using_obsp_import(self)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html", AsText(geometry) from obs_points'''))
        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        #if msgbar:
        #    print str(msgbar)

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, 421484.0, 6542696.0, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, POINT(421484 6542696))])'''
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface', mocked_iface)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('import_data_to_db.utils.Askuser', mock_askuser.get_v)
    def _test_import_obs_points_no_east_north(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'', u'', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            selected_file = MockUsingReturnValue(filename)

            @mock.patch('PyQt4.QtGui.QInputDialog.getText', TestImportObsPoints.mock_encoding.get_v)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName', selected_file.get_v)
            @mock.patch('midvatten_utils.QgsProject.instance', TestImportObsPoints.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser', TestImportObsPoints.mock_askuser.get_v)
            @mock.patch('import_data_to_db.utils.pop_up_info', TestImportObsPoints.skip_popup.get_v)
            @mock.patch('qgis.utils.iface', autospec=True)
            def _test_import_obs_points_using_obsp_import(self, mock_iface):
                self.importinstance.obsp_import()
            _test_import_obs_points_using_obsp_import(self)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "length", "drillstop", "diam", "material", "screen", "capacity", "drilldate", "wmeas_yn", "wlogg_yn", "east", "north", "ne_accur", "ne_source", "h_toc", "h_tocags", "h_gs", "h_accur", "h_syst", "h_source", "source", "com_onerow", "com_html", AsText(geometry) from obs_points'''))
        msgbar = TestImportObsPoints.mocked_iface.messagebar.messages
        if msgbar:
            print str(msgbar)

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, None, None, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, None)])'''
        assert test_string == reference_string


class _TestWquallabImport(object):
    temp_db_path = u'/tmp/tmp_midvatten_temp_db.sqlite'
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(temp_db_path)
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_dbpath = MockUsingReturnValue(MockQgsProjectInstance([temp_db_path]))
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance')
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger')
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName')
    def setUp(self, mock_savefilename, mock_crsquestion, mock_qgsproject_instance, mock_locale):
        mock_crsquestion.return_value = [3006]
        mock_savefilename.return_value = TestWquallabImport.temp_db_path
        mock_qgsproject_instance.return_value.readEntry = MIDV_DICT

        self.dummy_iface = DummyInterface2()
        self.iface = self.dummy_iface.mock
        self.midvatten = midvatten(self.iface)

        try:
            os.remove(TestWquallabImport.temp_db_path)
        except OSError:
            pass
        mock_locale.return_value.answer = u'ok'
        mock_locale.return_value.value = u'sv_SE'
        self.midvatten.new_db()
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TestWquallabImport.temp_db_path)

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wquallab_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db('''insert into zz_staff (staff) values ('teststaff')''')

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'depth', u'report', u'project', u'staff', u'date_time', u'anameth', u'parameter', u'reading_num', u'reading_txt', u'unit', u'comment'],
             [u'obsid1', u'2', u'testreport', u'testproject', u'teststaff', u'2011-10-19 12:30:00', u'testmethod', u'1,2-Dikloretan', u'1.5', u'<1.5', u'µg/l', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', TestWquallabImport.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _wquallab_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wquallab_import_from_csvlayer)
            _wquallab_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_qual_lab'''))

        reference_string = ur'''(True, [(obsid1, 2.0, testreport, testproject, teststaff, 2011-10-19 12:30:00, testmethod, 1,2-Dikloretan, 1.5, <1.5, µg/l, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_wquallab_import_from_csvlayer_depth_empty_string(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db('''insert into zz_staff (staff) values ('teststaff')''')

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'depth', u'report', u'project', u'staff', u'date_time', u'anameth', u'parameter', u'reading_num', u'reading_txt', u'unit', u'comment'],
             [u'obsid1', u'', u'testreport', u'testproject', u'teststaff', u'2011-10-19 12:30:00', u'testmethod', u'1,2-Dikloretan', u'1.5', u'<1.5', u'µg/l', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', TestWquallabImport.mock_dbpath.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def test_wquallab_import_from_csvlayer_depth_empty_string(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wquallab_import_from_csvlayer)
            test_wquallab_import_from_csvlayer_depth_empty_string(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_qual_lab'''))

        reference_string = ur'''(True, [(obsid1, None, testreport, testproject, teststaff, 2011-10-19 12:30:00, testmethod, 1,2-Dikloretan, 1.5, <1.5, µg/l, testcomment)])'''
        assert test_string == reference_string


class _TestWlvlloggImport(object):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_import_wlvllogg(self):
        file = [u'date_time,head_cm,temp',
                 u'2016-03-15 10:30:00,1,100']

        db_utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("rb1")''')

        charsetchoosen = [u'utf-8']
        with utils.tempinput(u'\n'.join(file), charsetchoosen[0]) as filename:
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('import_data_to_db.utils.getselectedobjectnames')
                    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch.object(PyQt4.QtGui.QFileDialog, 'getOpenFileName')
                    def _test_import_wlvllogg(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_selected_obsid):
                        mock_selected_obsid.return_value = [u'rb1']
                        mock_filename.return_value = filename
                        mock_encoding.return_value = [True, u'utf-8']
                        self.importinstance = wlvlloggimportclass()

                    _test_import_wlvllogg(self, filename)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))

                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 100.0, None, None, None)])'''
                    assert test_string == reference_string


class _TestWflowImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_wflow_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'instrumentid', u'flowtype', u'date_time', u'reading', u'unit', u'comment'],
             [u'obsid1', u'testid', u'Momflow', u'2011-10-19 12:30:00', u'2', u'l/s', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_wflow_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wflow_import_from_csvlayer)
            _test_wflow_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_flow'''))
        reference_string = ur'''(True, [(obsid1, testid, Momflow, 2011-10-19 12:30:00, 2.0, l/s, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_wflow_import_from_csvlayer_type_missing(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'instrumentid', u'flowtype', u'date_time', u'reading', u'unit', u'comment'],
             [u'obsid1', u'testid', u'Testtype', u'2011-10-19 12:30:00', u'2', u'l/s', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_wflow_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wflow_import_from_csvlayer)
            _test_wflow_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_flow'''))
        reference_string = ur'''(True, [(obsid1, testid, Testtype, 2011-10-19 12:30:00, 2.0, l/s, testcomment)])'''
        assert test_string == reference_string


class _TestWqualfieldImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_w_qual_field_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'staff', u'date_time', u'instrument', u'parameter', u'reading_num', u'reading_txt', u'unit', u'depth', u'comment'],
             [u'obsid1', u'teststaff', u'2011-10-19 12:30:00', u'testinstrument', u'DO', u'12', u'<12', u'%', u'22', u'testcomment']]

        #utils.sql_alter_db(u'''insert into w_qual_field (obsid, date_time, parameter, reading_num, unit) values ('1', '2011-10-19 12:30:01', 'testp', '123', 'testunit')''')

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_w_qual_field_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wqualfield_import_from_csvlayer)
            _test_w_qual_field_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_qual_field'''))
        reference_string = ur'''(True, [(obsid1, teststaff, 2011-10-19 12:30:00, testinstrument, DO, 12.0, <12, %, 22.0, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_w_qual_field_import_from_csvlayer_no_depth(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'staff', u'date_time', u'instrument', u'parameter', u'reading_num', u'reading_txt', u'unit', u'depth', u'comment'],
             [u'obsid1', u'teststaff', u'2011-10-19 12:30:00', u'testinstrument', u'DO', u'12', u'<12', u'%', u'', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_w_qual_field_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wqualfield_import_from_csvlayer)
            _test_w_qual_field_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_qual_field'''))
        reference_string = ur'''(True, [(obsid1, teststaff, 2011-10-19 12:30:00, testinstrument, DO, 12.0, <12, %, None, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_w_qual_field_no_parameter(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'staff', u'date_time', u'instrument',
              u'reading_num', u'reading_txt', u'unit', u'depth', u'comment'],
             [u'obsid1', u'teststaff', u'2011-10-19 12:30:00', u'testinstrument',
              u'12', u'<12', u'%', u'22', u'testcomment']]

        # utils.sql_alter_db(u'''insert into w_qual_field (obsid, date_time, parameter, reading_num, unit) values ('1', '2011-10-19 12:30:01', 'testp', '123', 'testunit')''')

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch(
                'import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_w_qual_field_import_from_csvlayer(self, filename,
                                                        mock_filename,
                                                        mock_skippopup,
                                                        mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wqualfield_import_from_csvlayer)

            _test_w_qual_field_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_qual_field'''))
        reference_string = ur'''(True, [])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_w_qual_field_parameter_empty_string(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'staff', u'date_time', u'instrument', u'parameter', u'reading_num', u'reading_txt', u'unit', u'depth', u'comment'],
             [u'obsid1', u'teststaff', u'2011-10-19 12:30:00', u'testinstrument', u'DO', u'12', u'<12', u'%', u'22', u'testcomment'],
             [u'obsid2', u'teststaff', u'2011-10-19 12:30:00', u'testinstrument', u'', u'12', u'<12', u'%', u'22', u'testcomment']]

        # utils.sql_alter_db(u'''insert into w_qual_field (obsid, date_time, parameter, reading_num, unit) values ('1', '2011-10-19 12:30:01', 'testp', '123', 'testunit')''')

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch(
                'import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_w_qual_field_import_from_csvlayer(self, filename,
                                                        mock_filename,
                                                        mock_skippopup,
                                                        mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wqualfield_import_from_csvlayer)

            _test_w_qual_field_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_qual_field'''))
        reference_string = ur'''(True, [(obsid1, teststaff, 2011-10-19 12:30:00, testinstrument, DO, 12.0, <12, %, 22.0, testcomment)])'''
        assert test_string == reference_string


class _TestWlevelsImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_w_level_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'date_time', u'meas', u'comment'],
             [u'obsid1', u'2011-10-19 12:30:00', u'2', u'testcomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_wlvl_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wlvl_import_from_csvlayer)
            _test_wlvl_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_levels'''))
        reference_string = ur'''(True, [(obsid1, 2011-10-19 12:30:00, 2.0, None, None, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def _test_w_level_import_from_csvlayer_missing_columns(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        #f = [[u'obsid', u'date_time', u'meas', u'comment'],
        #     [u'obsid1', u'2011-10-19 12:30:00', u'2', u'testcomment']]
        f = [[u'obsid', u'date_time', u'meas'],
             [u'obsid1', u'2011-10-19 12:30:00', u'2']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_wlvl_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.default_import(self.importinstance.wlvl_import_from_csvlayer)
            _test_wlvl_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from w_levels'''))
        reference_string = ur'''(True, [])'''
        assert test_string == reference_string


class _TestSeismicImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_seismic_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_lines ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'length', u'ground', u'bedrock', u'gw_table', u'comment'],
             [u'obsid1', u'500', u'2', u'4', u'3', u'acomment']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_import_seismic_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.seismics_import()
            _test_import_seismic_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from seismic_data'''))
        reference_string = ur'''(True, [(obsid1, 500.0, 2.0, 4.0, 3.0, acomment)])'''
        assert test_string == reference_string


class _TestStratImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_strat_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'stratid', u'depthtop', u'depthbot', u'geology', u'geoshort', u'capacity', u'development', u'comment'],
             [u'obsid1', u'1', u'0', u'1', u'grusig sand', u'sand', u'5', u'(j)', u'acomment'],
             [u'obsid1', u'2', u'1', u'4', u'siltigt sandigt grus', u'grus', u'4+', u'(j)', u'acomment2']]

        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.strat_import() #goal_table=u'stratigraphy')
            _test(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from stratigraphy'''))
        reference_string = u'''(True, [(obsid1, 1, 0.0, 1.0, grusig sand, sand, 5, (j), acomment), (obsid1, 2, 1.0, 4.0, siltigt sandigt grus, grus, 4+, (j), acomment2)])'''
        assert test_string == reference_string


class _TestMeteoImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_meteo_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_points ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'instrumentid', u'parameter', u'date_time', u'reading_num', u'reading_txt', u'unit', u'comment'],
             [u'obsid1', u'ints1', u'pressure', u'2016-01-01 00:00:00', u'1100', u'1100', u'aunit', u'acomment']]
        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_import_meteo_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.meteo_import()
            _test_import_meteo_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from meteo'''))
        reference_string = u'''(True, [(obsid1, ints1, pressure, 2016-01-01 00:00:00, 1100.0, 1100, aunit, acomment)])'''
        assert test_string == reference_string


class _TestVlfImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_vlf_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        db_utils.sql_alter_db(u'INSERT INTO obs_lines ("obsid") VALUES ("obsid1")')
        f = [[u'obsid', u'length', u'real_comp', u'imag_comp', u'comment'],
             [u'obsid1', u'500', u'2', u'10', u'acomment']]
        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_import_vlf_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.vlf_import()
            _test_import_vlf_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from vlf_data'''))
        reference_string = u'''(True, [(obsid1, 500.0, 2.0, 10.0, acomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_vlf_import_from_csvlayer_no_obs_line(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'length', u'real_comp', u'imag_comp', u'comment'],
             [u'obsid1', u'500', u'2', u'10', u'acomment']]
        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_import_vlf_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.vlf_import()
            _test_import_vlf_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select * from vlf_data'''))
        reference_string = u'''(True, [])'''
        assert test_string == reference_string


class _TestObsLinesImport(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v(), u'Please note!\nForeign keys will': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')
    mock_encoding = MockUsingReturnValue([True, u'utf-8'])

    @mock.patch('create_db.utils.NotFoundQuestion')
    @mock.patch('midvatten_utils.Askuser', answer_yes.get_v)
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
        self.importinstance = midv_data_importer()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test_obs_lines_import_from_csvlayer(self):
        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'WKT', u'obsid', u'name', u'place', u'type', u'source'],
             [u'LINESTRING (30 10, 10 30, 40 40)', u'obsid1', u'aname', u'aplace', u'atype', u'asource']]
        with utils.tempinput(u'\n'.join([u';'.join(_x) for _x in f])) as filename:


            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.Askuser')
            @mock.patch('qgis.utils.iface', autospec=True)
            @mock.patch('PyQt4.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
            @mock.patch('import_data_to_db.PyQt4.QtGui.QFileDialog.getOpenFileName')
            def _test_obs_lines_import_from_csvlayer(self, filename, mock_filename, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                mock_filename.return_value = filename
                mock_encoding.return_value = [True, u'utf-8']
                self.mock_iface = mock_iface
                self.importinstance.obslines_import()
            _test_obs_lines_import_from_csvlayer(self, filename)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select "obsid", "name", "place", "type", "source", AsText("geometry") from obs_lines'''))
        reference_string = u'''(True, [(obsid1, aname, aplace, atype, asource, LINESTRING(30 10, 10 30, 40 40))])'''
        assert test_string == reference_string




