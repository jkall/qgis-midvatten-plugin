# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the stratigraphy plot.

 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2017-10-17
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
from __future__ import print_function

from builtins import str

import mock
import PyQt5
from nose.plugins.attrib import attr
from qgis.core import QgsProject, QgsVectorLayer

from midvatten.tools.utils import common_utils
from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests
from midvatten.tools.drillreport import Drillreport


@attr(status='on')
class TestDrillreport(utils_for_tests.MidvattenTestSpatialiteDbSv):
    @mock.patch('midvatten.tools.drillreport.QDesktopServices.openUrl')
    @mock.patch('midvatten.tools.utils.common_utils.MessagebarAndLog')
    @mock.patch('midvatten.tools.stratigraphy.common_utils.pop_up_info', autospec=True)
    def test_drillreport(self, mock_skippopup, mock_messagebar, openurl):
        """
        :param mock_skippopup:
        :param mock_messagebar:
        :return:
        """
        #QDesktopServices.openUrl(
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('1', 5, ST_GeomFromText('POINT(633466 711659)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('2', 10, ST_GeomFromText('POINT(6720727 016568)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO obs_points (obsid, h_gs, geometry) VALUES ('3', 20, ST_GeomFromText('POINT(6720728 016569)', 3006))''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, h_toc, level_masl) VALUES ('1', '2021-01-01 00:00', 20, 123)''')
        db_utils.sql_alter_db('''INSERT INTO w_levels (obsid, date_time, h_toc, level_masl) VALUES ('2', '2021-01-01 00:00', 20, NULL)''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 1, 0, 1, 'sand', 'sand', '3', 'j')''')
        db_utils.sql_alter_db('''INSERT INTO stratigraphy (obsid, stratid, depthtop, depthbot, geology, geoshort, capacity, development) VALUES ('1', 2, 1, 4.5, 'morän', 'morän', '3', 'j')''')


        #print(str(self.vlayer.isValid()))
        #print(str(db_utils.sql_load_fr_db('select * from obs_points')))
        #print(str(db_utils.sql_load_fr_db('select * from stratigraphy')))
        dlg = Drillreport(['1', '2', '3'], self.midvatten.ms.settingsdict)

        print(str(mock_messagebar.mock_calls))

        assert mock.call(PyQt5.QtCore.QUrl('file:///tmp/midvatten_reports/drill_report.html')) in openurl.mock_calls

        with open('/tmp/midvatten_reports/drill_report.html', 'r') as f:
            report = ''.join(f.readlines())
        print(str(report))

        assert report == '''<meta http-equiv="content-type" content="text/html; charset=utf-8" /><head><title>1, 2, 3 General report from Midvatten plugin for QGIS</title></head><html><TABLE WIDTH=100% BORDER=0 CELLPADDING=1 CELLSPACING=1><TR VALIGN=TOP><TD WIDTH=15%><h3 style="font-family:'arial';font-size:18pt; font-weight:600">1</h3><img src="/home/henrik/dev/midvatten/tools/../templates/for_general_report_sv.png" /><br><img src='/home/henrik/dev/midvatten/tools/../templates/midvatten_logga.png' /></TD><TD WIDTH=85%><TABLE WIDTH=100% BORDER=1 CELLPADDING=4 CELLSPACING=3><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>Allmän information</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;"><TR VALIGN=TOP><TD WIDTH=33%>markytans nivå, my (möh)</TD><TD WIDTH=50%>5.0</TD></TR><TR VALIGN=TOP><TD WIDTH=33%>östlig koordinat</TD><TD WIDTH=50%>633466.0 (SWEREF99 TM, EPSG:3006)</TD></TR><TR VALIGN=TOP><TD WIDTH=33%>nordlig koordinat</TD><TD WIDTH=50%>711659.0 (SWEREF99 TM, EPSG:3006)</TD></TR></p></TABLE></TD><TD WIDTH=50%><P><U><B>Lagerföljd</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"><TR VALIGN=TOP><TD WIDTH=17%><P><u>nivå (mumy)</P></u></TD><TD WIDTH=27%><P><u>jordart, fullst beskrivn</P></u></TD><TD WIDTH=17%><P><u>huvudfraktion</P></u></TD><TD WIDTH=5%><P><u>vg</P></u></TD><TD WIDTH=9%><P><u>stänger?</P></u></TD><TD WIDTH=27%><P><u>kommentar</P></u></TD></TR><TR VALIGN=TOP><TD WIDTH=17%><P>0.0 - 1.0</P></TD><TD WIDTH=27%><P>sand</P></TD><TD WIDTH=17%><P>sand</P></TD><TD WIDTH=5%><P>3</P></TD><TD WIDTH=9%><P>j</P></TD><TD WIDTH=27%><P></P></TD></TR><TR VALIGN=TOP><TD WIDTH=17%><P>1.0 - 4.5</P></TD><TD WIDTH=27%><P>morän</P></TD><TD WIDTH=17%><P>morän</P></TD><TD WIDTH=5%><P>3</P></TD><TD WIDTH=9%><P>j</P></TD><TD WIDTH=27%><P></P></TD></TR></p></TABLE></TD></TR><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>Kommentarer</B></U></P><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TD><TD WIDTH=50%><P><U><B>Vattennivåer</B></U></P><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;">Antal nivåmätningar: 1<br>Högsta uppmätta nivå: 123.0 m ö h<br>Medianvärde för nivå: 123.0 m ö h<br>Lägsta uppmätta nivå: 123.0 m ö h<br></p></TD></TR></TABLE></TD></TR></TABLE><meta http-equiv="content-type" content="text/html; charset=utf-8" /><head><title>1, 2, 3 General report from Midvatten plugin for QGIS</title></head><html><TABLE WIDTH=100% BORDER=0 CELLPADDING=1 CELLSPACING=1><TR VALIGN=TOP><TD WIDTH=15%><h3 style="font-family:'arial';font-size:18pt; font-weight:600">2</h3><img src="/home/henrik/dev/midvatten/tools/../templates/for_general_report_sv.png" /><br><img src='/home/henrik/dev/midvatten/tools/../templates/midvatten_logga.png' /></TD><TD WIDTH=85%><TABLE WIDTH=100% BORDER=1 CELLPADDING=4 CELLSPACING=3><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>Allmän information</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;"><TR VALIGN=TOP><TD WIDTH=33%>markytans nivå, my (möh)</TD><TD WIDTH=50%>10.0</TD></TR><TR VALIGN=TOP><TD WIDTH=33%>östlig koordinat</TD><TD WIDTH=50%>6720727.0 (SWEREF99 TM, EPSG:3006)</TD></TR><TR VALIGN=TOP><TD WIDTH=33%>nordlig koordinat</TD><TD WIDTH=50%>16568.0 (SWEREF99 TM, EPSG:3006)</TD></TR></p></TABLE></TD><TD WIDTH=50%><P><U><B>Lagerföljd</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TABLE></TD></TR><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>Kommentarer</B></U></P><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TD><TD WIDTH=50%><P><U><B>Vattennivåer</B></U></P><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TD></TR></TABLE></TD></TR></TABLE><meta http-equiv="content-type" content="text/html; charset=utf-8" /><head><title>1, 2, 3 General report from Midvatten plugin for QGIS</title></head><html><TABLE WIDTH=100% BORDER=0 CELLPADDING=1 CELLSPACING=1><TR VALIGN=TOP><TD WIDTH=15%><h3 style="font-family:'arial';font-size:18pt; font-weight:600">3</h3><img src="/home/henrik/dev/midvatten/tools/../templates/for_general_report_sv.png" /><br><img src='/home/henrik/dev/midvatten/tools/../templates/midvatten_logga.png' /></TD><TD WIDTH=85%><TABLE WIDTH=100% BORDER=1 CELLPADDING=4 CELLSPACING=3><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>Allmän information</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><p style="font-family:'arial'; font-size:8pt; font-weight:400; font-style:normal;"><TR VALIGN=TOP><TD WIDTH=33%>markytans nivå, my (möh)</TD><TD WIDTH=50%>20.0</TD></TR><TR VALIGN=TOP><TD WIDTH=33%>östlig koordinat</TD><TD WIDTH=50%>6720728.0 (SWEREF99 TM, EPSG:3006)</TD></TR><TR VALIGN=TOP><TD WIDTH=33%>nordlig koordinat</TD><TD WIDTH=50%>16569.0 (SWEREF99 TM, EPSG:3006)</TD></TR></p></TABLE></TD><TD WIDTH=50%><P><U><B>Lagerföljd</B></U></P><TABLE style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;" WIDTH=100% BORDER=0 CELLPADDING=0 CELLSPACING=1><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><COL WIDTH=43*><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TABLE></TD></TR><TR VALIGN=TOP><TD WIDTH=50%><P><U><B>Kommentarer</B></U></P><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TD><TD WIDTH=50%><P><U><B>Vattennivåer</B></U></P><p style="font-family:'arial'; font-size:10pt; font-weight:400; font-style:normal;"></p></TD></TR></TABLE></TD></TR></TABLE>
</p></body></html>'''