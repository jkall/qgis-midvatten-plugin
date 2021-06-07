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
from __future__ import absolute_import

from builtins import object

from nose.plugins.attrib import attr

from midvatten.tools.utils import common_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.import_general_csv_gui import GeneralCsvImportGui


@attr(status='on')
class TestStaticMethods(object):

    def test_translate_and_reorder_file_data(self):
        file_data = [['obsid', 'acol', 'acol2'],
                    ['rb1', '1', '2']]

        translation_dict = {'obsid': ['obsid'], 'acol': ['num', 'txt'], 'acol2': ['comment']}

        test_string = utils_for_tests.create_test_string(GeneralCsvImportGui.translate_and_reorder_file_data(file_data, translation_dict))
        reference_string = '[[num, txt, comment, obsid], [1, 1, 2, rb1]]'
        assert test_string == reference_string

    def test_convert_comma_to_points_for_double_columns(self):
        file_data = [['obsid', 'date_time', 'reading'], ['obs1,1', '2017-04-12 11:03', '123,456']]

        #(6, 'comment', 'text', 0, None, 0)
        tables_columns = ((0, 'obsid', 'text', 0, None, 0), (1, 'reading', 'double', 0, None, 0))
        test_string = common_utils.anything_to_string_representation(GeneralCsvImportGui.convert_comma_to_points_for_double_columns(file_data, tables_columns))
        reference = '[["obsid", "date_time", "reading"], ["obs1,1", "2017-04-12 11:03", "123.456"]]'
        assert test_string == reference


