# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the db_utils for postgis.

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

from midvatten.tools.utils import db_utils
from midvatten.tools.tests import utils_for_tests


@attr(status='only')
class TestDbTablesColumnsInfo(utils_for_tests.MidvattenTestPostgisDbSv):

    def test_tables_columns_info_all_tables(self):
        """  """
        #Assert that obsid is primary key and not null in obs_points
        #{'tablename': (ordernumber, name, type, notnull, defaultvalue, primarykey)}
        tables_columns_info = db_utils.db_tables_columns_info()
        col_obsid = [col for col in tables_columns_info['obs_points'] if col[1] == 'obsid'][0]
        assert len(tables_columns_info) > 1
        assert int(col_obsid[0]) == 1
        assert col_obsid[1] == 'obsid'
        assert col_obsid[2].lower() == 'text'
        assert int(col_obsid[3]) == 1
        assert col_obsid[4] is None
        assert int(col_obsid[5]) == 1


    def test_tables_columns_info_only_obs_points(self):
        """  """
        # Assert that obsid is primary key and not null in obs_points
        # {'tablename': (ordernumber, name, type, notnull, defaultvalue, primarykey)}
        tables_columns_info = db_utils.db_tables_columns_info('obs_points')
        col_obsid = [col for col in tables_columns_info['obs_points'] if col[1] == 'obsid'][0]
        assert len(tables_columns_info) == 1
        assert int(col_obsid[0]) == 1
        assert col_obsid[1] == 'obsid'
        assert col_obsid[2].lower() == 'text'
        assert int(col_obsid[3]) == 1
        assert col_obsid[4] is None
        assert int(col_obsid[5]) == 1


@attr(status='only')
class TestTablesColumns(utils_for_tests.MidvattenTestPostgisDbSv):

    def test_tables_columns_no_dbconnection_supplied(self):
        """  """
        tables_columns = db_utils.tables_columns()
        for tablename in ['obs_points', 'w_levels', 'w_qual_lab', 'w_lvls_last_geom']:
            assert tablename in tables_columns
            assert 'obsid' in tables_columns[tablename]

        for tablename in ['geometry_columns', 'spatial_ref_sys']:
            assert tablename not in tables_columns


    def test_tables_columns_dbconnection_supplied(self):
        """  """
        dbconnection = db_utils.DbConnectionManager()
        tables_columns = db_utils.tables_columns(dbconnection=dbconnection)
        for tablename in ['obs_points', 'w_levels', 'w_qual_lab', 'w_lvls_last_geom']:
            assert tablename in tables_columns
            assert 'obsid' in tables_columns[tablename]

        for tablename in ['geometry_columns', 'spatial_ref_sys']:
            assert tablename not in tables_columns


@attr(status='only')
class TestGetForeignKeys(utils_for_tests.MidvattenTestPostgisDbSv):

    def test_get_foreign_keys(self):
        """  """
        foreign_keys = db_utils.get_foreign_keys('w_levels')
        test_string = utils_for_tests.create_test_string(foreign_keys)
        reference = '{obs_points: [(obsid, obsid)]}'
        assert test_string == reference


    def test_get_foreign_keys_no_keys(self):
        """  """
        foreign_keys = db_utils.get_foreign_keys('obs_points')
        test_string = utils_for_tests.create_test_string(foreign_keys)
        reference = '{}'
        assert test_string == reference


@attr(status='only')
class TestVerifyTableExist(utils_for_tests.MidvattenTestPostgisDbSv):

    def test_verify_table_exists(self):
        exists = db_utils.verify_table_exists('obs_points')
        assert exists


@attr(status='only')
class TestNonplotTables(object):
    def test_as_tuple(self):
        tables = db_utils.nonplot_tables(as_tuple=True)

        assert tables == ('about_db',
                        'comments',
                        'zz_flowtype',
                        'zz_meteoparam',
                        'zz_strat',
                        'zz_hydro')
    def test_as_string(self):
        tables = db_utils.nonplot_tables(as_tuple=False)

        assert tables == r"""('about_db', 'comments', 'zz_flowtype', 'zz_meteoparam', 'zz_strat', 'zz_hydro')"""

    def test_as_string_default(self):
        tables = db_utils.nonplot_tables()

        assert tables == r"""('about_db', 'comments', 'zz_flowtype', 'zz_meteoparam', 'zz_strat', 'zz_hydro')"""


@attr(status='only')
class TestGetTimezoneFromDb(utils_for_tests.MidvattenTestPostgisDbSv):
    def test_get_timezone_from_db(self):
        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (UTC+1)'
            WHERE tablename = 'w_levels_logger' and columnname = 'date_time';""")
        tz = db_utils.get_timezone_from_db('w_levels_logger')
        #print(str(tz))
        assert tz == 'UTC+1'

    def test_other_than_utc(self):
        db_utils.sql_alter_db("""UPDATE about_db SET description = description || ' (Europe/Stockholm)'
                    WHERE tablename = 'w_levels' and columnname = 'date_time';""")
        tz = db_utils.get_timezone_from_db('w_levels')
        assert tz == 'Europe/Stockholm'

@attr(status='only')
class TestAddSchema(utils_for_tests.MidvattenTestPostgisDbSv):

    def test_add_schema_to_query(self):
        c = db_utils.DbConnectionManager()
        c.schema = 'public'

        test = c.add_schema_to_query("CREATE TABLE obs_points()")
        print(test)
        assert test == '''CREATE TABLE "public"."obs_points"()'''

        """>>>add_schema_to_query("INSERT INTO about_db (", 'public')
        INSERT INTO "public".about_db (

        >>>add_schema_to_query("ALTER TABLE obs_points ", 'public')
        ALTER TABLE "public".obs_points

        >>>add_schema_to_query("ALTER TABLE obs_points ", 'public')
        ALTER TABLE "public".obs_points

        >>>add_schema_to_query("CREATE UNIQUE INDEX w_qual_field_unit_unique_index_null ON w_qual_field", 'public')
        CREATE UNIQUE INDEX w_qual_field_unit_unique_index_null ON "public".w_qual_field

        >>>add_schema_to_query("REFERENCES obs_points(obsid)", 'public')
        REFERENCES "public".obs_points(obsid)

        >>>add_schema_to_query("CREATE VIEW obs_p_w_qual_field", 'public')
        CREATE VIEW "public".obs_p_w_qual_field

        >>>add_schema_to_query("FROM obs_points", 'public')
        FROM "public".obs_points

        >>>add_schema_to_query("REFERENCES obs_points(obsid)", 'public')
        REFERENCES "public".obs_points(obsid)

        >>>add_schema_to_query("JOIN w_qual_field", 'public')
        JOIN "public".w_qual_field

        >>>add_schema_to_query("CREATE INDEX idx_wquallab_odtp ON w_qual_lab", 'public')
        CREATE INDEX idx_wquallab_odtp ON "public".w_qual_lab

        >>>add_schema_to_query("UPDATE "public".w_levels_logger", 'public')
        UPDATE "public".w_levels_logger

        >>>add_schema_to_query("SELECT * FROM obs_points", 'public')
        UPDATE "public".w_levels_logger"""


