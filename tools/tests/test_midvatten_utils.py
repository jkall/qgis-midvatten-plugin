# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles often used
 utilities.

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
import midvatten_utils as utils
import mock
from mocks_for_tests import MockNotFoundQuestion, MockUsingReturnValue
pass
#class TestUserinput(object):
#    def test_setup(self):
#        userinput = utils.Userinput(u'a dialog title', u'a text', [u'one', u'two'])
#        userinput.ignored_clicked()
#        assert
#        print("\nAnswer: ")
#        print(userinput.answer)
#        print(userinput.chosen)
#        print("\n")

class TestFilterNonexistingObsidsAndAsk(object):
        notfound = MockNotFoundQuestion('ok', 10)
        return_notfound = MockUsingReturnValue(notfound)

        @mock.patch('midvatten_utils.NotFoundQuestion', return_notfound.get_v)
        def test_filter_nonexisting_obsids_and_ask(self):
                file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
                existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']

                filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids, existing_obsids[0])
                print('\ntest_filter_nonexisting_obsids_and_ask result')
                print(filtered_file_data)
