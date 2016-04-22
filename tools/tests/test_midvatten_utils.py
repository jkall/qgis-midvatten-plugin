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
import io

class TestFilterNonexistingObsidsAndAsk(object):
    notfound_ok = MockUsingReturnValue(MockNotFoundQuestion('ok', 10))
    notfound_ignore = MockUsingReturnValue(MockNotFoundQuestion('ignore', 10))
    notfound_cancel = MockUsingReturnValue(MockNotFoundQuestion('cancel', 10))

    @mock.patch('midvatten_utils.NotFoundQuestion', notfound_ok.get_v)
    def test_filter_nonexisting_obsids_and_ask_ok(self):
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'10', u'b'], [u'10', u'h']]
            assert filtered_file_data == reference_list

    @mock.patch('midvatten_utils.NotFoundQuestion', notfound_ignore.get_v)
    def test_filter_nonexisting_obsids_and_ask_ignore(self):
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'10', u'b'], [u'10', u'h']]
            assert filtered_file_data == reference_list

    @mock.patch('midvatten_utils.NotFoundQuestion', notfound_cancel.get_v)
    def test_filter_nonexisting_obsids_and_ask_cancel(self):
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            assert filtered_file_data == u'cancel'

    def test_filter_nonexisting_obsids_and_ask_header_not_found(self):
            file_data = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            existing_obsids = [u'2', u'3', u'10', u'1_g', u'1 a']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'header_that_should_not_exist', existing_obsids)
            reference_list = [[u'obsid', u'ae'], [u'1', u'b'], [u'2', u'c'], [u'3', u'd'], [u'10', u'e'], [u'1_g', u'f'], [u'1 a', u'g'], [u'21', u'h']]
            assert filtered_file_data == reference_list

    def test_filter_nonexisting_obsids_and_ask_header_capitalize(self):
            file_data = [[u'obsid', u'ae'], [u'a', u'b'], [u'2', u'c']]
            existing_obsids = [u'A', u'2']
            filtered_file_data = utils.filter_nonexisting_values_and_ask(file_data, u'obsid', existing_obsids, True)
            reference_list = [[u'obsid', u'ae'], [u'2', u'c'], [u'A', u'b']]
            assert filtered_file_data == reference_list


class TestTempinput(object):
    def test_tempinput(self):
        rows = u'543\n21'
        with utils.tempinput(rows) as filename:
            with io.open(filename, 'r', encoding=u'utf-8') as f:
                res = f.readlines()
        reference_list = [u'543\n', u'21']
        assert res == reference_list


class TestAskUser(object):
    PyQt4_QtGui_QInputDialog_getText = MockUsingReturnValue([u'-1 hours'])
    cancel = MockUsingReturnValue([u''])

    @mock.patch('PyQt4.QtGui.QInputDialog.getText', PyQt4_QtGui_QInputDialog_getText.get_v)
    def test_askuser_dateshift(self):
        question = utils.askuser('DateShift')
        assert question.result == ['-1', 'hours']

    @mock.patch('PyQt4.QtGui.QInputDialog.getText', cancel.get_v)
    def test_askuser_dateshift_cancel(self):
        question = utils.askuser('DateShift')
        assert question.result == u'cancel'