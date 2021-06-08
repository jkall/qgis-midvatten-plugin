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

import mock
from nose.plugins.attrib import attr

from midvatten.tools.utils import common_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools import piper


#


@attr(status='on')
class TestPiperPlotDb(utils_for_tests.MidvattenTestPostgisDbSv):
    """ The test doesn't go through the whole section plot unfortunately
    """

    @mock.patch('matplotlib.pyplot.Figure.show')
    def test_piper_plot_default_settings(self, mock_showplot):
        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {r"""piper_cl""": '',
                                r"""piper_hco3""": '',
                                r"""piper_so4""": '',
                                r"""piper_na""": '',
                                r"""piper_k""": '',
                                r"""piper_ca""": '',
                                r"""piper_mg""": ''}
        mock_active_layer = mock.MagicMock()
        piperplot = piper.PiperPlot(mock_ms, mock_active_layer)
        piperplot.create_parameter_selection()

        test = common_utils.anything_to_string_representation(piperplot.ParameterList)
        ref = '''["(lower(parameter) like '%klorid%' or lower(parameter) like '%chloride%')", "(lower(parameter) like '%alkalinitet%' or lower(parameter) like '%alcalinity%')", "(lower(parameter) like '%sulfat%' or lower(parameter) like '%sulphat%')", "(lower(parameter) like '%natrium%')", "(lower(parameter) like '%kalium%' or lower(parameter) like '%potassium%')", "(lower(parameter) like '%kalcium%' or lower(parameter) like '%calcium%')", "(lower(parameter) like '%magnesium%')"]'''
        assert test == ref

    @mock.patch('matplotlib.pyplot.Figure.show')
    def test_piper_plot_user_chosen_settings(self, mock_showplot):
        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {r"""piper_cl""": 'cl',
                                r"""piper_hco3""": 'hco3',
                                r"""piper_so4""": 'so4',
                                r"""piper_na""": 'na',
                                r"""piper_k""": 'k',
                                r"""piper_ca""": 'ca',
                                r"""piper_mg""": 'mg'}
        mock_active_layer = mock.MagicMock()
        piperplot = piper.PiperPlot(mock_ms, mock_active_layer)
        piperplot.create_parameter_selection()

        test = common_utils.anything_to_string_representation(piperplot.ParameterList)
        ref = '''["parameter = 'cl'", "parameter = 'hco3'", "parameter = 'so4'", "parameter = 'na'", "parameter = 'k'", "parameter = 'ca'", "parameter = 'mg'"]'''
        assert test == ref

    @mock.patch('midvatten.tools.piper.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.sectionplot.common_utils.getselectedobjectnames')
    @mock.patch('matplotlib.pyplot.Figure.show')
    def test_piper_plot_get_data(self, mock_showplot, mock_selected, mock_messagebar):

        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, type, geometry) VALUES ('P1', 'well', ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, type, geometry) VALUES ('P2', 'notwell', ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'chloride', '1', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'alcalinity', '2', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'sulphat', '3', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'natrium', '4', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'kalium', '5', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'kalcium', '6', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P1', '1', 'magnesium', '7', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'chloride', '10', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'alcalinity', '20', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'sulphat', '30', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'natrium', '40', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'kalium', '50', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'kalcium', '60', 'mg/l', '2017-01-01')''')
        db_utils.sql_alter_db('''INSERT INTO w_qual_lab (obsid, report, parameter, reading_num, unit, date_time) VALUES ('P2', '2', 'magnesium', '70', 'mg/l', '2017-01-01')''')

        """
        Manual calculation:
        (factor1 * reading_num) / factor2 = meq 
        1		1	/	35,453	=	0,028206357713029
        1		2	/	61,0168	=	0,032777857901431
        2	*	3	/	96,063	=	0,062459011273852

        1		4	/	22,9898	=	0,173990204351495
        1		5	/	39,0983	=	0,127882797973313
        sum                         0,301873002

        2	*	6	/	40,078	=	0,299416138529867
        2	*	7	/	24,305	=	0,576013166015223
                    /			
        1		10	/	35,453	=	0,282063577130285
        1		20	/	61,0168	=	0,327778579014304
        2	*	30	/	96,063	=	0,624590112738515

        1		40	/	22,9898	=	1,73990204351495
        1		50	/	39,0983	=	1,27882797973313
        sum                         3,018730023

        2	*	60	/	40,078	=	2,99416138529867
        2	*	70	/	24,305	=	5,76013166015223

        """

        mock_ms = mock.MagicMock()
        mock_ms.settingsdict = {r"""piper_cl""": '',
                                r"""piper_hco3""": '',
                                r"""piper_so4""": '',
                                r"""piper_na""": '',
                                r"""piper_k""": '',
                                r"""piper_ca""": '',
                                r"""piper_mg""": ''}
        mock_active_layer = mock.MagicMock()
        mock_selected.return_value = ['P1', 'P2']
        piperplot = piper.PiperPlot(mock_ms, mock_active_layer)
        piperplot.create_parameter_selection()
        piperplot.ms.settingsdict['piper_markers'] = 'obsid'
        piperplot.get_data_and_make_plot()
        data = piperplot.obsnp_nospecformat
        print("data: " + str(data))
        for l in data:
            for idx in range(3, 9):
                l[idx] = '{0:.10f}'.format(float(l[idx]))
        print("data: " + str(data))

        test_paramlist = common_utils.anything_to_string_representation(piperplot.ParameterList)
        ref_paramlist = '''["(lower(parameter) like '%klorid%' or lower(parameter) like '%chloride%')", "(lower(parameter) like '%alkalinitet%' or lower(parameter) like '%alcalinity%')", "(lower(parameter) like '%sulfat%' or lower(parameter) like '%sulphat%')", "(lower(parameter) like '%natrium%')", "(lower(parameter) like '%kalium%' or lower(parameter) like '%potassium%')", "(lower(parameter) like '%kalcium%' or lower(parameter) like '%calcium%')", "(lower(parameter) like '%magnesium%')"]'''
        assert test_paramlist == ref_paramlist

        test_data = tuple([tuple(_) for _ in data])

        ref_data = (('P1', '2017-01-01', 'well', '0.0282063577', '0.0327778579', '0.0624590113', '0.3018730023',
                     '0.2994161385', '0.5760131660'), ('P2', '2017-01-01', 'notwell', '0.2820635771', '0.3277785790',
                                                       '0.6245901127', '3.0187300232', '2.9941613853', '5.7601316602'))

        print("test")
        print(test_data)
        print("REF")
        print(ref_data)
        assert test_data == ref_data

        assert len(mock_messagebar.mock_calls) == 0

