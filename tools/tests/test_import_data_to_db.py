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
from nose.tools import raises

class test_midv_data_importer():
    def setUp(self):
        self.importinstance = midv_data_importer()

    @raises(IndexError)
    def test_fieldlogger_import_parse_rows_fail_with_header(self):

        f = ("LOCATION;DATE;TIME;VALUE;TYPE\n"
            "Rb1505.quality;30-03-2016;15:29:26;hej;quality.comment\n")

        result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.fieldlogger_import_parse_rows(f)))

    def test_fieldlogger_import_parse_rows(self):

        f = [
            "Rb1505.quality;30-03-2016;15:29:26;hej;quality.comment\n",
            "Rb1505.quality;30-03-2016;15:29:26;555;quality.flow_lpm\n",
            "Rb1505.quality;30-03-2016;15:29:26;TEST;quality.instrument\n",
            "Rb1505.quality;30-03-2016;15:29:26;863;quality.konduktivitet\n",
            "Rb1615.flow;30-03-2016;15:30:09;357;flow.Accvol\n",
            "Rb1615.flow;30-03-2016;15:30:09;gick bra;flow.comment\n",
            "Rb1615.flow;30-03-2016;15:30:09;4888;flow.instrument\n",
            "Rb1512.quality;30-03-2016;15:30:39;test;quality.comment\n",
            "Rb1512.quality;30-03-2016;15:30:39;666;quality.flow_lpm\n",
            "Rb1512.quality;30-03-2016;15:30:39;flgkg;quality.instrument\n",
            "Rb1512.quality;30-03-2016;15:30:39;58;quality.syre\n",
            "Rb1512.quality;30-03-2016;15:30:39;8;quality.temperatur\n",
            "Rb1512.quality;30-03-2016;15:30:39;899;quality.turbiditet\n",
            "Rb1202.quality;30-03-2016;15:31:30;hej;quality.comment\n",
            "Rb1202.quality;30-03-2016;15:31:30;56;quality.flow_lpm\n",
            "Rb1202.quality;30-03-2016;15:31:30;ffggg;quality.instrument\n",
            "Rb1202.quality;30-03-2016;15:31:30;555;quality.konduktivitet\n",
            "Rb1608.quality;30-03-2016;15:33:48;ffg;quality.comment\n",
            "Rb1608.quality;30-03-2016;15:33:48;841;quality.flow_lpm\n",
            "Rb1608.quality;30-03-2016;15:33:48;xfg;quality.instrument\n",
            "Rb1608.quality;30-03-2016;15:33:48;805;quality.konduktivitet\n",
            "Rb1608.quality;30-03-2016;15:34:02;ffg;quality.comment\n",
            "Rb1608.quality;30-03-2016;15:34:02;555;quality.flow_lpm\n",
            "Rb1608.quality;30-03-2016;15:34:02;wer;quality.instrument\n",
            "Rb1608.quality;30-03-2016;15:34:02;852;quality.konduktivitet\n",
            "Rb1608.quality;30-03-2016;15:34:13;3fg;quality.comment\n",
            "Rb1608.quality;30-03-2016;15:34:13;885;quality.flow_lpm\n",
            "Rb1608.quality;30-03-2016;15:34:13;ergv;quality.instrument\n",
            "Rb1608.quality;30-03-2016;15:34:13;555;quality.konduktivitet\n",
            "Rb1608.level;30-03-2016;15:34:13;ergv;level.comment\n",
            "Rb1608.level;30-03-2016;15:34:13;555;level.meas\n"
            ]

        result_string = str(utils_for_tests.dict_to_sorted_list(self.importinstance.fieldlogger_import_parse_rows(f)))

        reference_string = "['flow', 'Rb1615', datetime.datetime(2016, 3, 30, 15, 30, 9), 'Accvol', '357', 'comment', 'gick bra', 'instrument', '4888', 'level', 'Rb1608', datetime.datetime(2016, 3, 30, 15, 34, 13), 'comment', 'ergv', 'meas', '555', 'quality', 'Rb1202', datetime.datetime(2016, 3, 30, 15, 31, 30), 'comment', 'hej', 'flow_lpm', '56', 'instrument', 'ffggg', 'konduktivitet', '555', 'Rb1505', datetime.datetime(2016, 3, 30, 15, 29, 26), 'comment', 'hej', 'flow_lpm', '555', 'instrument', 'TEST', 'konduktivitet', '863', 'Rb1512', datetime.datetime(2016, 3, 30, 15, 30, 39), 'comment', 'test', 'flow_lpm', '666', 'instrument', 'flgkg', 'syre', '58', 'temperatur', '8', 'turbiditet', '899', 'Rb1608', datetime.datetime(2016, 3, 30, 15, 33, 48), 'comment', 'ffg', 'flow_lpm', '841', 'instrument', 'xfg', 'konduktivitet', '805', datetime.datetime(2016, 3, 30, 15, 34, 2), 'comment', 'ffg', 'flow_lpm', '555', 'instrument', 'wer', 'konduktivitet', '852', datetime.datetime(2016, 3, 30, 15, 34, 13), 'comment', '3fg', 'flow_lpm', '885', 'instrument', 'ergv', 'konduktivitet', '555']"

        assert result_string == reference_string

