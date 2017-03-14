﻿# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line
select InitSpatialMetadata(1);
create table about_db /*A status log for the tables in the db*/(
table text --Name of a table in the db
, column text --Name of column
, data_type text --Name of column
, not_null text --1 if the column can not contain NULL
, default_value text --The default value of the column
, primary_key text --1 if column is a primary key
, foreign_key text --table(column) of foreign keys
, description text --Comment for column or table
, upd_date text --Date for last update
, upd_sign text --Person responsible for update
);
create table obs_points /*One of the two main tables. This table holds all point observation objects.*/(
obsid text not null --ID for the observation point
, name text --Ordinary name for the observation
, place text --Place for the observation. E.g. estate
, type text --Type of observation
, length double --Borehole length from ground surface to bottom (equals to depth if vertical)
, drillstop text --Drill stop
, diam double --Inner diameter for casing or upper part of borehol
, material text --Well material
, screen text --Type of well screen
, capacity text --Well capacity
, drilldate text --Date when drilling was completed
, wmeas_yn integer --1/0 if water level is to be measured for this point or not
, wlogg_yn integer --1/0 if water level if borehole is equipped with a logger or not
, east double --Eastern coordinate (in the corresponding CRS)
, north double --Northern coordinate (in the corresponding CRS)
, ne_accur double --Approximate inaccuracy for coordinates
, ne_source text --Source for the given position
, h_toc double --Elevation (masl) for the measuring point
, h_tocags double --Distance from Measuring point to Ground Surface (m)
, h_gs double --Ground Surface level (m). 
, h_accur double --Inaccuracy (m) for Measuring Point level
, h_syst text --Reference system for elevation
, h_source text --Source for the measuring point elevation (consultancy report or similar)
, source text --The source for the observation point
, com_onerow text --onerow comment
, com_html text --multiline formatted comment in html format
, primary key (obsid)
);
SELECT AddGeometryColumn(obs_points, geometry, CHANGETORELEVANTEPSGID, "POINT", "XY", 0);
create table obs_lines /*One of the two main tables. This table holds all line observation objects.*/(
obsid text  not null --ID for observation line
, name text --Ordinary name for the observation
, place text --Place for the observation
, type text --Type of observation
, source text --The origin for the observation
, primary key (obsid)
);
SELECT AddGeometryColumn(obs_lines, geometry, CHANGETORELEVANTEPSGID, "LINESTRING", "XY", 0);
create table w_levels /*Manual water level measurements*/(
obsid text not null --obsid linked to obs_points.obsid
, date_time text not null --Date and Time for the observation
, meas double --distance from measuring point to water level
, h_toc double --Elevation (masl) for the measuring point at the particular date_time (measuring point elevation may vary by time)
, level_masl double --Water level elevation (masl) calculated from measuring point and distance from measuring point to water level
, comment text --Comment
, primary key (obsid, date_time)
, foreign key(obsid) references obs_points(obsid)
);
create table w_levels_logger /*Automatic Water Level Readings*/(
obsid text not null --obsid linked to obs_points.obsid
, date_time text not null --Date and Time for the observation
, head_cm double --pressure (cm water column) on pressure transducer
, temp_degc double --temperature degrees C
, cond_mscm double --electrical conductivity mS/cm
, level_masl double --Corresponding Water level elevation (masl)
, comment text --Comment
, primary key (obsid, date_time)
, foreign key(obsid) references obs_points(obsid)
);
create table stratigraphy /*stratigraphy information from drillings*/(
obsid text not null --obsid linked to obs_points.obsid
, stratid integer not null --Stratigraphy layer ID for the OBSID
, depthtop double --Depth
, depthbot double --Depth
, geology text --Full description of geology
, geology text --Full description of geology
, geoshort text --Short description of geology
, capacity text --Well development at the layer
, development text --Well development - Is the flushed water clear and free of suspended solids? 
, comment text --Comment
, primary key (obsid, stratid)
, foreign key(obsid) references obs_points(obsid)
);
create table w_qual_field /*Water quality from field measurements*/(
obsid text not null --obsid linked to obs_points.obsid
, staff text --Field staff
, date_time text not null --Date and Time for the observation
, instrument text --Instrument ID
, parameter text not null --Measured parameter
, reading_num double --Value as real number
, reading_txt text --Value as text
, unit text --Unit
, depth double --The depth at which the measurement was done
, comment text --Comment
, primary key(obsid, date_time, parameter, unit)
, foreign key(obsid) references obs_points(obsid), foreign key(staff) references zz_staff(staff)
);
create table w_qual_lab /*Water quality from laboratory analysis*/(
obsid text not null --obsid linked to obs_points.obsid
, depth double --Depth (m below h_gs) from where sample is taken
, report text not null --Report no from laboratory
, project text --Project number
, staff text --Field staff
, date_time text --Date and Time for the observation
, anameth text --Analysis method
, parameter text not null --Measured parameter
, reading_num double --Value as real number
, reading_txt text --Value as text
, unit text --Unit
, comment text --Comments
, primary key(report, parameter)
, foreign key(obsid) references obs_points(obsid), foreign key(staff) references zz_staff(staff)
);
create table w_flow /*Water flow*/(
obsid text not null --obsid linked to obs_points.obsid
, instrumentid text not null --Instrument Id
, flowtype text not null --Flowtype must correspond to type in flowtypes - Accumulated volume
, date_time text not null --Date and Time for the observation
, reading double --Value (real number) reading for the flow rate
, unit text --Unit corresponding to the value reading
, comment text --Comment
, primary key (obsid, instrumentid, flowtype, date_time)
, foreign key(obsid) references obs_points(obsid), foreign key (flowtype) references zz_flowtype(type)
);
CREATE TABLE meteo /*meteorological observations*/(
obsid text not null --obsid linked to obs_points.obsid
, instrumentid text not null --Instrument Id
, parameter text not null --The meteorological parameter
, date_time text not null --Date and Time for the observation
, reading_num double --Value (real number) reading for the parameter
, reading_txt text --Value (text string) reading for the parameter
, unit text --Unit corresponding to the value reading
, comment text --Comment
, primary key (obsid, instrumentid, parameter, date_time)
, foreign key(obsid) references obs_points(obsid), foreign key (parameter) references zz_meteoparam(parameter)
);
create table seismic_data /*Interpreted data from seismic measurements*/(
obsid text not null --obsid linked to obs_lines.obsid
, length double not null --Length along line
, ground double --Ground surface level
, bedrock double --Interpreted level for bedrock surface
, gw_table double --Interpreted level for limit between unsaturated/saturated conditions
, comment text --Additional info
, primary key (obsid, Length)
, foreign key (obsid) references obs_lines(obsid)
);
create table vlf_data /*Raw data from VLF measurements*/(
obsid text not null --obsid linked to obs_lines.obsid
, length double not null --Length along line
, real_comp double --Raw data real component (in-phase(%))
, imag_comp double --Raw data imaginary component
, comment text --Additional info
, primary key (obsid, length)
, foreign key (obsid) references obs_lines(obsid)
);
CREATE TABLE comments /*comments connected to obsids*/(
obsid text not null --ID for the observation point
, date_time text not null --Date and Time for the comment
, comment text not null --comment connected to obsid
, staff text not null --initials of the staff who made the comment
, primary key("obsid", "date_time")
, foreign key(obsid) references obs_points(obsid), foreign key(staff) references zz_staff(staff)
);
CREATE TABLE zz_staff /*data domain for field staff used when importing data*/(
staff text --initials of the field staff
, name text --name of the field staff
, primary key("staff")
);
create table zz_flowtype /*data domain for flowtypes in table w_flow*/(
type text not null --
, explanation text --Explanation of the flowtypes
, primary key(type)
);
CREATE TABLE zz_meteoparam /*data domain for meteorological parameters in meteo*/(
parameter text not null --
, explanation text --Explanation of the parameters
, primary key(parameter)
);
CREATE TABLE zz_strat /*data domain for stratigraphy classes*/(
geoshort text not null --abbreviation for the strata (stratigraphy class)
, strata text not null --clay etc
, primary key(geoshort)
);
CREATE TABLE zz_stratigraphy_plots /*data domain for stratigraphy plot colors and symbols used by the plugin*/(
strata text not null --clay etc
, color_mplot text not null --color codes for matplotlib plots
, hatch_mplot text not null --hatch codes for matplotlib plots
, color_qt text not null --color codes for Qt plots
, brush_qt text not null --brush types for Qt plots
, primary key(strata)
);
CREATE TABLE zz_capacity /*data domain for stratigraphy classes and geological short names used by the plugin*/(
capacity text not null --water capacity classes
, explanation text not null --description of water capacity classes
, primary key(capacity)
);
CREATE TABLE zz_capacity_plots /*data domain for capacity plot colors used by the plugin*/(
capacity text not null --water capacity classes
, color_qt text not null --hatchcolor codes for Qt plots
, primary key(capacity)
, foreign key(capacity) references zz_capacity(capacity)
);
create view obs_p_w_qual_field as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."geometry" as "geometry" from "obs_points" as "a" JOIN "w_qual_field" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('obs_p_w_qual_field', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view obs_p_w_qual_lab as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."geometry" as "geometry" from "obs_points" as "a" JOIN "w_qual_lab" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('obs_p_w_qual_lab', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view obs_p_w_strat as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."h_toc" as "h_toc", "a"."h_gs" as "h_gs", "a"."geometry" as "geometry" from "obs_points" as "a" JOIN "stratigraphy" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('obs_p_w_strat', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view obs_p_w_lvl as select distinct "a"."rowid" AS "rowid", "a"."obsid" AS "obsid", "a"."geometry" AS "geometry" FROM "obs_points" AS "a" JOIN "w_levels" AS "b" USING ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('obs_p_w_lvl', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_lvls_last_geom" as select "b"."rowid" as "rowid", "a"."obsid" as "obsid", MAX("a"."date_time") as "date_time",  "a"."meas" as "meas",  "a"."level_masl" as "level_masl", "b"."geometry" as "geometry" from "w_levels" as "a" JOIN "obs_points" as "b" using ("obsid") GROUP BY obsid;
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_lvls_last_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_qual_field_geom" as select "w_qual_field"."rowid" as "rowid", "w_qual_field"."obsid" as "obsid", "w_qual_field"."staff" as "staff", "w_qual_field"."date_time" as "date_time", "w_qual_field"."instrument" as "instrument", "w_qual_field"."parameter" as "parameter", "w_qual_field"."reading_num" as "reading_num", "w_qual_field"."reading_txt" as "reading_txt", "w_qual_field"."unit" as "unit", "w_qual_field"."comment" as "comment", "obs_points"."geometry" as "geometry" from "w_qual_field" as "w_qual_field" left join "obs_points" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_qual_field_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_qual_lab_geom" as select "w_qual_lab".'rowid' as rowid, "w_qual_lab".'obsid', "w_qual_lab".'depth', "w_qual_lab".'report', "w_qual_lab".'staff', "w_qual_lab".'date_time', "w_qual_lab".'anameth', "w_qual_lab".'parameter', "w_qual_lab".'reading_txt', "w_qual_lab".'reading_num', "w_qual_lab".'unit', "obs_points".'geometry' as geometry  from "w_qual_lab", "obs_points" where "w_qual_lab".'obsid'="obs_points".'obsid';
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_qual_lab_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view "w_levels_geom" as select "b"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."date_time" as "date_time",  "a"."meas" as "meas",  "a"."h_toc" as "h_toc",  "a"."level_masl" as "level_masl", "b"."geometry" as "geometry" from "w_levels" as "a" join "obs_points" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) values ('w_levels_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
create view w_flow_momflow as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unit" as "unit", "comment" as "comment" from w_flow where flowtype="Momflow";
create view w_flow_aveflow as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unit" as "unit", "comment" as "comment" from w_flow where flowtype="Aveflow";
create view w_flow_accvol as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unit" as "unit", "comment" as "comment" from w_flow where flowtype="Accvol";
CREATE INDEX idx_wquallab_odtp ON w_qual_lab(obsid, date_time, parameter);
CREATE INDEX idx_wquallab_odtpu ON w_qual_lab(obsid, date_time, parameter, unit);
CREATE INDEX idx_wqualfield_odtpu ON w_qual_field(obsid, date_time, parameter, unit);