# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the creating of the database.

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
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance
import mock
import io
from midvatten.midvatten import midvatten
import os


class TestCreateMemoryDb():
    answer_yes_obj = MockUsingReturnValue()
    answer_yes_obj.result = 1
    answer_yes = MockUsingReturnValue(answer_yes_obj)
    CRS_question = MockUsingReturnValue([3006])
    dbpath_question = MockUsingReturnValue(':memory:')

    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)

    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def test_new_db(self):
        self.midvatten.new_db()

    def tearDown(self):
        self.iface = None
        self.midvatten = None


class TestCreateDb(object):
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
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)
        try:
            os.remove(TestCreateDb.temp_db_path)
        except OSError:
            pass

    def tearDown(self):
        #Delete database
        try:
            os.remove(TestCreateDb.temp_db_path)
        except OSError:
            pass

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_create_db_se(self):
        self.midvatten.new_db(u'sv_SE')
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select * from zz_strat'))
        reference_string = ur"""(True, [(berg, berg), (b, berg), (rock, berg), (ro, berg), (grovgrus, grovgrus), (grg, grovgrus), (coarse gravel, grovgrus), (cgr, grovgrus), (grus, grus), (gr, grus), (gravel, grus), (mellangrus, mellangrus), (grm, mellangrus), (medium gravel, mellangrus), (mgr, mellangrus), (fingrus, fingrus), (grf, fingrus), (fine gravel, fingrus), (fgr, fingrus), (grovsand, grovsand), (sag, grovsand), (coarse sand, grovsand), (csa, grovsand), (sand, sand), (sa, sand), (mellansand, mellansand), (sam, mellansand), (medium sand, mellansand), (msa, mellansand), (finsand, finsand), (saf, finsand), (fine sand, finsand), (fsa, finsand), (silt, silt), (si, silt), (lera, lera), (ler, lera), (le, lera), (clay, lera), (cl, lera), (morän, morän), (moran, morän), (mn, morän), (till, morän), (ti, morän), (torv, torv), (t, torv), (peat, torv), (pt, torv), (fyll, fyll), (fyllning, fyll), (f, fyll), (made ground, fyll), (mg, fyll), (land fill, fyll)])"""
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('create_db.locale.getdefaultlocale', autospec=True)
    def test_create_db_locale_se(self, mock_locale):
        mock_locale.return_value = [u'se_SV']
        self.midvatten.new_db(u'sv_SE')
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select * from zz_strat'))
        reference_string = ur"""(True, [(berg, berg), (b, berg), (rock, berg), (ro, berg), (grovgrus, grovgrus), (grg, grovgrus), (coarse gravel, grovgrus), (cgr, grovgrus), (grus, grus), (gr, grus), (gravel, grus), (mellangrus, mellangrus), (grm, mellangrus), (medium gravel, mellangrus), (mgr, mellangrus), (fingrus, fingrus), (grf, fingrus), (fine gravel, fingrus), (fgr, fingrus), (grovsand, grovsand), (sag, grovsand), (coarse sand, grovsand), (csa, grovsand), (sand, sand), (sa, sand), (mellansand, mellansand), (sam, mellansand), (medium sand, mellansand), (msa, mellansand), (finsand, finsand), (saf, finsand), (fine sand, finsand), (fsa, finsand), (silt, silt), (si, silt), (lera, lera), (ler, lera), (le, lera), (clay, lera), (cl, lera), (morän, morän), (moran, morän), (mn, morän), (till, morän), (ti, morän), (torv, torv), (t, torv), (peat, torv), (pt, torv), (fyll, fyll), (fyllning, fyll), (f, fyll), (made ground, fyll), (mg, fyll), (land fill, fyll)])"""
        assert test_string == reference_string

    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    @mock.patch('create_db.locale.getdefaultlocale', autospec=True)
    def test_create_db_locale_en(self, mock_locale):
        mock_locale.return_value = [u'en_US']
        self.midvatten.new_db()
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select * from zz_strat'))
        reference_string = ur"""(True, [(berg, rock), (b, rock), (rock, rock), (ro, rock), (grovgrus, coarse gravel), (grg, coarse gravel), (coarse gravel, coarse gravel), (cgr, coarse gravel), (grus, gravel), (gr, gravel), (gravel, gravel), (mellangrus, medium gravel), (grm, medium gravel), (medium gravel, medium gravel), (mgr, medium gravel), (fingrus, fine gravel), (grf, fine gravel), (fine gravel, fine gravel), (fgr, fine gravel), (grovsand, coarse sand), (sag, coarse sand), (coarse sand, coarse sand), (csa, coarse sand), (sand, sand), (sa, sand), (mellansand, medium sand), (sam, medium sand), (medium sand, medium sand), (msa, medium sand), (finsand, fine sand), (saf, fine sand), (fine sand, fine sand), (fsa, fine sand), (silt, silt), (si, silt), (lera, clay), (ler, clay), (le, clay), (clay, clay), (cl, clay), (morän, till), (moran, till), (mn, till), (till, till), (ti, till), (torv, peat), (t, peat), (peat, peat), (pt, peat), (fyll, made ground), (fyllning, made ground), (f, made ground), (made ground, made ground), (mg, made ground), (land fill, made ground), (unknown, unknown)])"""
        assert test_string == reference_string


class TestObsPointsTriggers(object):
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
    @mock.patch('midvatten_utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', crs_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', dbpath_question.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten(self.iface)
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
        utils.add_triggers_to_obs_points()
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 1.0, None)])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_triggers_add_east_north(self):
        """ Updating coordinates from NULL should create geometry. """
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid", "east", "north") VALUES ('rb1', NULL, NULL)''')

        utils.add_triggers_to_obs_points()

        utils.sql_alter_db(u"""update obs_points set east='1.0', north='2.0'""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, 2.0, POINT(1 2))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_triggers_not_deleting_geom_when_east_north_null(self):
        """ Adding triggers should not automatically delete geometry when east AND north is NULL """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")
        #After the first: u'(True, [(rb1, None, None, POINT(1 1))])

        utils.add_triggers_to_obs_points()

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, POINT(1 1))])'
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_triggers_not_deleting_geom_when_one_east_north_null(self):
        """ Adding triggers should not automatically delete geometry when east OR north is NULL """
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid, geometry) VALUES ('rb1', GeomFromText('POINT(1.0 1.0)', 3006))""")

        utils.add_triggers_to_obs_points()

        utils.sql_alter_db(u"""update obs_points set east=X(geometry) where east is null and geometry is not null""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 1.0, None, POINT(1 1))])'
        assert test_string == reference_string

        utils.sql_alter_db(u"""update obs_points set east='2.0'""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 2.0, None, POINT(1 1))])'
        assert test_string == reference_string

        utils.sql_alter_db(u"""update obs_points set east=NULL""")
        utils.sql_alter_db(u"""update obs_points set north='2.0'""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, 2.0, POINT(1 1))])'
        assert test_string == reference_string

        utils.sql_alter_db(u"""update obs_points set east='3.0'""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 3.0, 2.0, POINT(3 2))])'
        assert test_string == reference_string

        utils.sql_alter_db(u"""update obs_points set east='4.0'""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 4.0, 2.0, POINT(4 2))])'
        assert test_string == reference_string

        utils.sql_alter_db(u"""update obs_points set east=NULL, north=NULL""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, POINT(4 2))])'
        assert test_string == reference_string

        utils.sql_alter_db(u"""update obs_points set east='5.0', north='6.0'""")
        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, 5.0, 6.0, POINT(5 6))])'
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

    @mock.patch('midvatten_utils.QgsProject.instance', mock_dbpath.get_v)
    def test_add_trigger_add_obsid_without_anything(self):
        """ Test that adding triggers and updating obsid from east, north don't set null values for previous obsid.
        :return:
        """
        utils.add_triggers_to_obs_points()
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb1')""")
        utils.sql_alter_db(u"""INSERT INTO obs_points (obsid) VALUES ('rb2')""")

        test_string = utils_for_tests.create_test_string(utils.sql_load_fr_db(u'select obsid, east, north, AsText(geometry) from obs_points'))
        reference_string = u'(True, [(rb1, None, None, None), (rb2, None, None, None)])'
        assert test_string == reference_string

    def tearDown(self):
        #Delete database
        os.remove(TestObsPointsTriggers.temp_db_path)

