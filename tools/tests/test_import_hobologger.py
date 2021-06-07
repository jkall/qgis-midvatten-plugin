# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  hobologger files.

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

import os

import mock

from nose.plugins.attrib import attr

from midvatten.tools.utils import common_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.import_hobologger import HobologgerImport, TzConverter


@attr(status='on')
class TestParseHobologgerFile(object):

    def setUp(self):
        pass

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_parse_hobologger_file_utf8(self, mock_messagelog):

        f = ('﻿"Plot Title: temp"',
             '"#","Date Time, GMT+01:00","Temp, °C (LGR S/N: 1234, SEN S/N: 1234, LBL: Rb1)","Coupler Detached (LGR S/N: 1234)","Coupler Attached (LGR S/N: 1234)","Stopped (LGR S/N: 1234)","End Of File (LGR S/N: 1234)"',
             '1,07/19/18 10:00:00 fm,4.558,Logged,,,',
             '2,07/19/18 11:00:00 fm,4.402,,,,',
             '3,07/19/18 12:00:00 em,4.402,,,,',
             '4,07/19/18 01:00:00 em,4.402,,,,')

        charset_of_hobologgerfile = 'utf-8'
        #tz_string = get_tz_string('Date Time, GMT+02:00')
        tzconverter = TzConverter()
        #tzconverter.source_tz = tz_string
        with common_utils.tempinput('\n'.join(f), charset_of_hobologgerfile) as path:
            file_data = HobologgerImport.parse_hobologger_file(path, charset_of_hobologgerfile, tz_converter=tzconverter)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2018-07-19 10:00:00, , 4.558, ], [2018-07-19 11:00:00, , 4.402, ], [2018-07-19 12:00:00, , 4.402, ], [2018-07-19 13:00:00, , 4.402, ]]'
        #print(str(test_string))
        #print(str(reference_string))
        #print(str(mock_messagelog.mock_calls))
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'Rb1'

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_parse_hobologger_file_convert_tz(self, mock_messagelog):

        f = ('﻿"Plot Title: temp"',
             '"#","Date Time, GMT+03:00","Temp, °C (LGR S/N: 1234, SEN S/N: 1234, LBL: Rb1)","Coupler Detached (LGR S/N: 1234)","Coupler Attached (LGR S/N: 1234)","Stopped (LGR S/N: 1234)","End Of File (LGR S/N: 1234)"',
             '1,07/19/18 10:00:00 fm,4.558,Logged,,,',
             '2,07/19/18 11:00:00 fm,4.402,,,,',
             '3,07/19/18 12:00:00 em,4.402,,,,',
             '4,07/19/18 01:00:00 em,4.402,,,,')

        charset_of_hobologgerfile = 'utf-8'
        #tz_string = get_tz_string('Date Time, GMT+02:00')
        tzconverter = TzConverter()
        tzconverter.target_tz = 'GMT+01:00'
        #tzconverter.source_tz = tz_string
        with common_utils.tempinput('\n'.join(f), charset_of_hobologgerfile) as path:
            file_data = HobologgerImport.parse_hobologger_file(path, charset_of_hobologgerfile, tz_converter=tzconverter)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2018-07-19 08:00:00, , 4.558, ], [2018-07-19 09:00:00, , 4.402, ], [2018-07-19 10:00:00, , 4.402, ], [2018-07-19 11:00:00, , 4.402, ]]'
        #print(str(test_string))
        #print(str(reference_string))
        #print(str(mock_messagelog.mock_calls))
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'Rb1'

    def test_parse_hobologger_file_changed_order(self):
        f = ('﻿"Plot Title: temp"',
             '"#","Temp, °C (LGR S/N: 1234, SEN S/N: 1234, LBL: Rb1)","Date Time, GMT+01:00","Coupler Detached (LGR S/N: 1234)","Coupler Attached (LGR S/N: 1234)","Stopped (LGR S/N: 1234)","End Of File (LGR S/N: 1234)"',
             '1,4.558,07/19/18 10:00:00 fm,Logged,,,',
             '2,4.402,07/19/18 11:00:00 fm,,,,',
             '3,4.402,07/19/18 12:00:00 em,,,,',
             '4,4.402,07/19/18 01:00:00 em,,,,')

        charset_of_hobologgerfile = 'utf-8'
        #tz_string = get_tz_string('Date Time, GMT+02:00')
        tzconverter = TzConverter()
        #tzconverter.source_tz = tz_string
        with common_utils.tempinput('\n'.join(f), charset_of_hobologgerfile) as path:
            file_data = HobologgerImport.parse_hobologger_file(path, charset_of_hobologgerfile, tz_converter=tzconverter)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2018-07-19 10:00:00, , 4.558, ], [2018-07-19 11:00:00, , 4.402, ], [2018-07-19 12:00:00, , 4.402, ], [2018-07-19 13:00:00, , 4.402, ]]'
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'Rb1'

    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    def test_parse_hobologger_file_other_dateformat(self, mock_messagelog):

        f = ('﻿"Plot Title: temp"',
             '"#","Date Time, GMT+01:00","Temp, °C (LGR S/N: 1234, SEN S/N: 1234, LBL: Rb1)","Coupler Detached (LGR S/N: 1234)","Coupler Attached (LGR S/N: 1234)","Stopped (LGR S/N: 1234)","End Of File (LGR S/N: 1234)"',
             '1,2018-07-19 10:00:00,4.558,Logged,,,',
             '2,2018-07-19 11:00:00,4.402,,,,',
             '3,2018-07-19 12:00:00,4.402,,,,',
             '4,2018-07-19 13:00:00,4.402,,,,')

        charset_of_hobologgerfile = 'utf-8'
        #tz_string = get_tz_string('Date Time, GMT+02:00')
        tzconverter = TzConverter()
        #tzconverter.source_tz = tz_string
        with common_utils.tempinput('\n'.join(f), charset_of_hobologgerfile) as path:
            file_data = HobologgerImport.parse_hobologger_file(path, charset_of_hobologgerfile, tz_converter=tzconverter)

        test_string = utils_for_tests.create_test_string(file_data[0])
        reference_string = '[[date_time, head_cm, temp_degc, cond_mscm], [2018-07-19 10:00:00, , 4.558, ], [2018-07-19 11:00:00, , 4.402, ], [2018-07-19 12:00:00, , 4.402, ], [2018-07-19 13:00:00, , 4.402, ]]'
        #print(str(test_string))
        #print(str(reference_string))
        #print(str(mock_messagelog.mock_calls))
        assert test_string == reference_string
        assert os.path.basename(path) == file_data[1]
        assert file_data[2] == 'Rb1'