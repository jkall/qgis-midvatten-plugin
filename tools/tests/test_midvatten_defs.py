# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles exports to
  fieldlogger format.

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
import mock
import utils_for_tests
from definitions import midvatten_defs

class _TestDefsFunctions(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten_utils.QgsProject.instance')
    def test_tables_columns(self, mock_instance):
        mock_instance.return_value.readEntry.return_value = self.SETTINGS_DATABASE
        res = midvatten_defs.tables_columns()
        assert res
        assert isinstance(res, dict)
        for k, v in res.iteritems():
            assert isinstance(k, unicode)
            assert isinstance(v, (tuple, list))
            for x in v:
                assert isinstance(x, (tuple, list))
                assert x



