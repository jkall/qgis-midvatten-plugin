# -*- coding: utf-8 -*-
import utils_for_tests
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch, MagicMock
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
import midvatten
import os
import PyQt4
from import_data_to_db import midv_data_importer, FieldloggerImport
import import_data_to_db
from collections import OrderedDict
import midvsettings

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH], ('Midvatten', 'locale'): [u'sv_SE']}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)

class TestFieldLoggerImporterDb(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
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
        #utils.verify_table_exists(u'comments')

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    @mock.patch('import_data_to_db.utils.MessagebarAndLog')
    def test_staff_not_given(self, mock_MessagebarAndLog):
        ms = MagicMock()
        ms.settingsdict = OrderedDict()
        importer = FieldloggerImport(self.iface.mainWindow(), ms)
        importer.start_import(importer.observations)
        mock_MessagebarAndLog.critical.assert_called_with(bar_msg=u'Import error, staff not given')

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test2(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')
        utils.sql_alter_db(u'''INSERT INTO zz_staff ("staff") VALUES ("HS")''')
        utils.sql_alter_db(u'''INSERT INTO zz_flowtype ("type", "unit") VALUES ("Aveflow", "m3/s")''')
        utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("Temperature", "Temp", "m3/s")''')
        ms = MagicMock()
        ms.settingsdict = OrderedDict()
        importer = FieldloggerImport(self.iface.mainWindow(), ms)

        #Set settings:
        for setting in importer.settings:
            if isinstance(setting, import_data_to_db.StaffQuestion):
                setting.staff(u'teststaff')

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
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n"
            ]

        with utils.tempinput(''.join(f)) as filename:
            selected_file = MockUsingReturnValue([filename])

            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _test(self, importer):
                importer.start_import(importer.observations)

            _test(self, importer)


