# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line
select 'drop table ' || name || ';' from sqlite_master where type = 'table';
select InitSpatialMetadata();
create table about_db ("table" text, "column" text, "upd_date" text, "upd_sign" text, "description" text);
insert into about_db values('*', '*', '', '', 'This db was created by Midvatten plugin CHANGETOPLUGINVERSION, running QGIS version CHANGETOQGISVERSION on top of SpatiaLite version CHANGETOSPLITEVERSION')
insert into about_db values('about_db', '*', '', '', 'A status log for the tables in the db')
insert into about_db values('about_db', 'table', '', '', 'Name of a table in the db')
insert into about_db values('about_db', 'column', '', '', 'Name of column')
insert into about_db values('about_db', 'upd_date', '', '', 'Date for last update')
insert into about_db values('about_db', 'upd_sign', '', '', 'Person responsible for update')
insert into about_db values('about_db', 'contents', '', '', 'Contents')
insert into about_db values('obs_points', '*', '', '', 'One of the two main tables. This table holds all point observation objects.')
insert into about_db values('obs_points', 'obsid', '', '', 'ID for the observation point, eg Well01, Br1201, Rb1201')
insert into about_db values('obs_points', 'name', '', '', 'Ordinary name for the observation, e.g. Pumping well no 1, Brunn 123, Flow gauge A, pegel 3 etc ')
insert into about_db values('obs_points', 'place', '', '', 'Place for the observation. E.g. estate, property, site')
insert into about_db values('obs_points', 'type', '', '', 'Type of observation')
insert into about_db values('obs_points', 'length', '', '', 'Borehole length from ground surface to bottom (equals to depth if vertical)')
insert into about_db values('obs_points', 'drillstop', '', '', 'Drill stop, e.g. probing/direct push drilling stopped against rock')
insert into about_db values('obs_points', 'diam', '', '', 'Inner diameter for casing or upper part of borehol')
insert into about_db values('obs_points', 'material', '', '', 'Well material')
insert into about_db values('obs_points', 'screen', '', '', 'Type of well screen, including description, e.g. 1 m Johnson Well Screen 2,5mm ')
insert into about_db values('obs_points', 'capacity', '', '', 'Well capacity')
insert into about_db values('obs_points', 'drilldate', '', '', 'Date when drilling was completed')
insert into about_db values('obs_points', 'wmeas_yn', '', '', '1/0 if water level is to be measured for this point or not')
insert into about_db values('obs_points', 'wlogg_yn', '', '', '1/0 if water level if borehole is equipped with a logger or not')
insert into about_db values('obs_points', 'east', '', '', 'Eastern coordinate (in the corresponding CRS)')
insert into about_db values('obs_points', 'north', '', '', 'Northern coordinate (in the corresponding CRS)')
insert into about_db values('obs_points', 'ne_accur', '', '', 'Approximate inaccuracy for coordinates')
insert into about_db values('obs_points', 'ne_source', '', '', 'Source for the given position, e.g. from an old map or measured in field campaign')
insert into about_db values('obs_points', 'h_toc', '', '', 'Elevation (masl) for the measuring point, the point from which water level is measured, normally Top Of Casing')
insert into about_db values('obs_points', 'h_tocags', '', '', 'Distance from Measuring point to Ground Surface (m), Top Of Casing Above Ground Surface')
insert into about_db values('obs_points', 'h_gs', '', '', 'Ground Surface level (m). ')
insert into about_db values('obs_points', 'h_accur', '', '', 'Inaccuracy (m) for Measuring Point level, h_toc')
insert into about_db values('obs_points', 'h_syst', '', '', 'Reference system for elevation')
insert into about_db values('obs_points', 'h_source', '', '', 'Source for the measuring point elevation (consultancy report or similar)')
insert into about_db values('obs_points', 'source', '', '', 'The source for the observation point, eg full reference to consultancy report or authority and year')
insert into about_db values('obs_points', 'com_onerow', '', '', 'onerow comment, appropriate for map labels')
insert into about_db values('obs_points', 'com_html', '', '', 'multiline formatted comment in html format')
insert into about_db values('obs_points', 'Geometry', '', '', 'The geometry of OGR/FDO type point')
insert into about_db values('obs_lines', '*', '', '', 'One of the two main tables. This table holds all line observation objects.')
insert into about_db values('obs_lines', 'obsid', '', '', 'ID for observation line, e.g. S1.')
insert into about_db values('obs_lines', 'name', '', '', 'Ordinary name for the observation, e.g. Seismic profile no 1')
insert into about_db values('obs_lines', 'place', '', '', 'Place for the observation')
insert into about_db values('obs_lines', 'type', '', '', 'Type of observation, e.g. vlf, seismics or gpr')
insert into about_db values('obs_lines', 'source', '', '', 'The origin for the observation, eg full reference to consultancy report')
insert into about_db values('obs_lines', 'Geometry', '', '', 'The geometry of OGR/FDO type linestring')
insert into about_db values('seismic_data', '*', '', '', 'Interpreted data from seismic measurements')
insert into about_db values('seismic_data', 'obsid', '', '', 'obsid linked to obs_lines.obsid')
insert into about_db values('seismic_data', 'length', '', '', 'Length along line')
insert into about_db values('seismic_data', 'east', '', '', 'Eastern coordinate (in the corresponding CRS)')
insert into about_db values('seismic_data', 'north', '', '', 'Northern coordinate (in the corresponding CRS)')
insert into about_db values('seismic_data', 'ground', '', '', 'Ground surface level')
insert into about_db values('seismic_data', 'bedrock', '', '', 'Interpreted level for bedrock surface')
insert into about_db values('seismic_data', 'gw_table', '', '', 'Interpreted level for limit between unsaturated/saturated conditions')
insert into about_db values('stratigraphy', '*', '', '', 'stratigraphy information from drillings, probings etc')
insert into about_db values('stratigraphy', 'obsid', '', '', 'obsid linked to obs_points.obsid')
insert into about_db values('stratigraphy', 'stratid', '', '', 'Stratigraphy layer ID for the OBSID, starts with layer 1 from ground surface and increases below')
insert into about_db values('stratigraphy', 'depthtop', '', '', 'Depth, from surface level, to top of the stratigraphy layer')
insert into about_db values('stratigraphy', 'depthbot', '', '', 'Depth, from surface level, to bottom of the stratigraphy layer')
insert into about_db values('stratigraphy', 'geology', '', '', 'Full description of geology')
insert into about_db values('stratigraphy', 'geoshort', '', '', 'Short description of geology, should correspond to the dictionaries used. Stratigraphy plot looks in this field and relates to coded dictionaries with fill patterns and colors.')
insert into about_db values('stratigraphy', 'capacity', '', '', 'Well development at the layer, may also be waterloss or similar. If using notations 1, 2, 3, 4-, 4, and so on until 6+ it will match color codes in Midvatten plugin. ')
insert into about_db values('stratigraphy', 'development', '', '', 'Well development - Is the flushed water clear and free of suspended solids? ')
insert into about_db values('stratigraphy', 'comment', '', '', 'Comment')
insert into about_db values('vlf_data', '*', '', '', 'Raw data from VLF measurements')
insert into about_db values('vlf_data', 'obsid', '', '', 'obsid linked to obs_lines.obsid')
insert into about_db values('vlf_data', 'length', '', '', 'Length along line')
insert into about_db values('vlf_data', 'east', '', '', 'Eastern coordinate (in the corresponding CRS)')
insert into about_db values('vlf_data', 'north', '', '', 'Northern coordinate (in the corresponding CRS)')
insert into about_db values('vlf_data', 'real_comp', '', '', 'Raw data real component (in-phase(%))')
insert into about_db values('vlf_data', 'imag_comp', '', '', 'Raw data imaginary component')
insert into about_db values('w_flow', '*', '', '', 'Water flow')
insert into about_db values('w_flow', 'obsid', '', '', 'obsid linked to obs_points.obsid')
insert into about_db values('w_flow', 'instrumentid', '', '', 'Instrument Id, may use several flowmeters at same borehole')
insert into about_db values('w_flow', 'flowtype', '', '', 'Flowtype must correspond to type in flowtypes - Accumulated volume, momentary flow etc')
insert into about_db values('w_flow', 'date_time', '', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss')
insert into about_db values('w_flow', 'reading', '', '', 'Value (real number) reading for the flow rate, accumulated volume etc')
insert into about_db values('w_flow', 'unit', '', '', 'Unit corresponding to the value reading')
insert into about_db values('w_flow', 'comment', '', '', 'Comment')
insert into about_db values('w_levels', '*', '', '', 'Manual water level measurements')
insert into about_db values('w_levels', 'obsid', '', '', 'obsid linked to obs_points.obsid')
insert into about_db values('w_levels', 'date_time', '', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss')
insert into about_db values('w_levels', 'meas', '', '', 'distance from measuring point to water level')
insert into about_db values('w_levels', 'h_toc', '', '', 'Elevation (masl) for the measuring point at the particular date_time (measuring point elevation may vary by time)')
insert into about_db values('w_levels', 'level_masl', '', '', 'Water level elevation (masl) calculated from measuring point and distance from measuring point to water level')
insert into about_db values('w_levels', 'comment', '', '', 'Comment')
insert into about_db values('w_levels_logger', '*', '', '', 'Automatic Water Level Readings')
insert into about_db values('w_levels_logger', 'obsid', '', '', 'obsid linked to obs_points.obsid')
insert into about_db values('w_levels_logger', 'date_time', '', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss')
insert into about_db values('w_levels_logger', 'head_cm', '', '', 'pressure (cm water column) on pressure transducer')
insert into about_db values('w_levels_logger', 'temp_degc', '', '', 'temperature degrees C')
insert into about_db values('w_levels_logger', 'cond_mscm', '', '', 'electrical conductivity mS/cm')
insert into about_db values('w_levels_logger', 'level_masl', '', '', 'Corresponding Water level elevation (masl)')
insert into about_db values('w_levels_logger', 'comment', '', '', 'Comment')
insert into about_db values('w_qual_field', '*', '', '', 'Water quality from field measurements')
insert into about_db values('w_qual_field', 'obsid', '', '', 'obsid linked to obs_points.obsid')
insert into about_db values('w_qual_field', 'staff', '', '', 'Field staff')
insert into about_db values('w_qual_field', 'date_time', '', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss')
insert into about_db values('w_qual_field', 'instrument', '', '', 'Instrument ID')
insert into about_db values('w_qual_field', 'parameter', '', '', 'Measured parameter')
insert into about_db values('w_qual_field', 'reading_num', '', '', 'Value as real number')
insert into about_db values('w_qual_field', 'reading_txt', '', '', 'Value as text, incl more than and less than symbols')
insert into about_db values('w_qual_field', 'unit', '', '', 'Unit')
insert into about_db values('w_qual_field', 'flow_lpm', '', '', 'Sampling flow (l/min)')
insert into about_db values('w_qual_field', 'comment', '', '', 'Comment')
insert into about_db values('w_qual_lab', '*', '', '', 'Water quality from laboratory analysis')
insert into about_db values('w_qual_lab', 'obsid', '', '', 'obsid linked to obs_points.obsid')
insert into about_db values('w_qual_lab', 'depth', '', '', 'Depth (m below h_gs) from where sample is taken')
insert into about_db values('w_qual_lab', 'report', '', '', 'Report no from laboratory')
insert into about_db values('w_qual_lab', 'project', '', '', 'Project number')
insert into about_db values('w_qual_lab', 'staff', '', '', 'Field staff')
insert into about_db values('w_qual_lab', 'date_time', '', '', 'Date and Time for the observation, on format yyyy-mm-dd hh:mm:ss')
insert into about_db values('w_qual_lab', 'anameth', '', '', 'Analysis method, preferrably code relating to analysis standard')
insert into about_db values('w_qual_lab', 'parameter', '', '', 'Measured parameter')
insert into about_db values('w_qual_lab', 'reading_num', '', '', 'Value as real number')
insert into about_db values('w_qual_lab', 'reading_txt', '', '', 'Value as text, incl more than and less than symbols')
insert into about_db values('w_qual_lab', 'unit', '', '', 'Unit')
insert into about_db values('w_qual_lab', 'comment', '', '', 'Comments')
insert into about_db values('zz_flowtype', '*', '', '', 'Possible Flowtypes in table w_flow')
insert into about_db values('zz_flowtype', 'type', '', '', 'Existing types of measurements related to water flow')
insert into about_db values('zz_flowtype', 'explanation', '', '', 'Explanation of the flowtypes')
create table "obs_points" ( "obsid" text not null, "name" text, "place" text, "type" text, "length" double, "drillstop" text, "diam" double, "material" text, "screen" text, "capacity" text, "drilldate" text, "wmeas_yn" integer, "wlogg_yn" integer, "east" double, "north" double, "ne_accur" double, "ne_source" text,  "h_toc" double, "h_tocags" double, "h_gs" double, "h_accur" double, "h_syst" text, "h_source" text, "source" text, "com_onerow" text, "com_html" text, primary key (obsid));
SELECT AddGeometryColumn("obs_points", "Geometry", CHANGETORELEVANTEPSGID, "POINT", "XY", 0);
create table "obs_lines" ("obsid" text  not null, name text, place text, type text, source text, primary key (obsid));
SELECT AddGeometryColumn("obs_lines", "Geometry", CHANGETORELEVANTEPSGID, "LINESTRING", "XY", 0);
create table "w_levels" ("obsid" text not null, "date_time" text not null, "meas" double, "h_toc" double, "level_masl" double not null default -999, "comment" text, primary key (obsid, date_time),  foreign key(obsid) references obs_points(obsid));
create table "w_levels_logger" ("obsid" text not null, "date_time" text not null, "head_cm" double, "temp_degc" double, "cond_mscm" double, "level_masl" double not null default -999, "comment" text, primary key (obsid, date_time),  foreign key(obsid) references obs_points(obsid));
create table "stratigraphy" (obsid text not null, stratid integer not null, depthtop double, depthbot double, geology text, geoshort text, capacity text, development text,  comment text, primary key (obsid, stratid), foreign key(obsid) references obs_points(obsid));
create table "w_qual_field" (obsid text not null, staff text, date_time text not null, instrument text, parameter text not null, reading_num double, reading_txt text, unit text, flow_lpm double, comment text, primary key(obsid, date_time, parameter), foreign key(obsid) references obs_points(obsid) );
create table "w_qual_lab" ("obsid" text not null, "depth" double, "report" text not null, "project" text, "staff" text, "date_time" text, "anameth" text, "parameter" text not null, "reading_num" double, "reading_txt" text, "unit" text, "comment" text, primary key(report, parameter), foreign key(obsid) references obs_points(obsid));
create table "seismic_data" (obsid text not null, length double not null, east double, north double, ground double, bedrock double, gw_table double, primary key (obsid, Length), foreign key (obsid) references obs_lines(obsid));
create table "vlf_data" (obsid text not null, length double not null, east double, north double, real_comp double, imag_comp double, primary key (obsid, Length), foreign key (obsid) references obs_lines(obsid));
create table "zz_flowtype" (type text not null,explanation text, primary key(type));
insert into zz_flowtype(type, explanation) values("Accvol", "Accumulated volume");
insert into zz_flowtype(type, explanation) values("Momflow", "Momentary flow rate");
insert into zz_flowtype(type, explanation) values("Aveflow", "Average flow since last reading");
create table "w_flow" (obsid text not null, instrumentid text not null, flowtype text not null, date_time text not null, reading double, unit text, comment text, primary key (obsid, instrumentid, flowtype, date_time), foreign key(obsid) references obs_points(obsid), foreign key (flowtype) references zz_flowtype(type));
create view obs_p_w_qual_field as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."Geometry" as "Geometry" from "obs_points" as "a" JOIN "w_qual_field" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('obs_p_w_qual_field', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view obs_p_w_qual_lab as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."Geometry" as "Geometry" from "obs_points" as "a" JOIN "w_qual_lab" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('obs_p_w_qual_lab', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view obs_p_w_strat as select distinct "a"."rowid" as "rowid", "a"."obsid" as "obsid", "a"."h_toc" as "h_toc", "a"."h_gs" as "h_gs", "a"."Geometry" as "Geometry" from "obs_points" as "a" JOIN "stratigraphy" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('obs_p_w_strat', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view obs_p_w_lvl as select distinct "a"."rowid" AS "rowid", "a"."obsid" AS "obsid", "a"."Geometry" AS "Geometry" FROM "obs_points" AS "a" JOIN "w_levels" AS "b" USING ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('obs_p_w_lvl', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view "w_lvls_last_geom" as select "b"."rowid" as "rowid", "a"."obsid" as "obsid", MAX("a"."date_time") as "date_time",  "a"."meas" as "meas",  "a"."level_masl" as "level_masl", "b"."Geometry" as "Geometry" from "w_levels" as "a" JOIN "obs_points" as "b" using ("obsid") GROUP BY obsid;
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('w_lvls_last_geom', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view "w_qual_field_geom" as select "w_qual_field"."rowid" as "rowid", "w_qual_field"."obsid" as "obsid", "w_qual_field"."staff" as "staff", "w_qual_field"."date_time" as "date_time", "w_qual_field"."instrument" as "instrument", "w_qual_field"."parameter" as "parameter", "w_qual_field"."reading_num" as "reading_num", "w_qual_field"."reading_txt" as "reading_txt", "w_qual_field"."unit" as "unit", "w_qual_field"."flow_lpm" as "flow_lpm", "w_qual_field"."comment" as "comment", "obs_points"."Geometry" as "Geometry" from "w_qual_field" as "w_qual_field" left join "obs_points" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('w_qual_field_geom', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view "w_qual_field_temp" as select "obsid" as "obsid", "date_time" as "date_time", "reading_num" as "reading_num", "reading_txt" as "reading_txt", "unit" as "unit", "comment" as "comment" from "w_qual_field" where "parameter" = 'temp' or "parameter" = 'Temp' or "parameter" = 'TEMP' or "parameter" = 'temperatur' or "parameter" = 'Temperatur' or "parameter" = 'TEMPERATUR';
create view "w_qual_lab_hco3" as select "a"."obsid" as "obsid", "a"."depth" as "depth", "a"."report" as "report", "a"."staff" as "staff", "a"."date_time" as "date_time", "a"."parameter" as "parameter", "a"."reading_num" as "reading_num", "a"."unit" as "unit" from "w_qual_lab" as "a" where "a"."parameter" = 'Alkalinitet, HCO3';
create view "w_qual_lab_kond" as select "obsid" as "obsid", "depth" as "depth", "report" as "report", "staff" as "staff", "date_time" as "date_time", "parameter" as "parameter", "reading_num" as "reading_num", "unit" as "unit" from "w_qual_lab" where "parameter" = 'Konduktivitet';
create view "w_qual_lab_geom" as select "w_qual_lab".'rowid' as rowid, "w_qual_lab".'obsid', "w_qual_lab".'depth', "w_qual_lab".'report', "w_qual_lab".'staff', "w_qual_lab".'date_time', "w_qual_lab".'anameth', "w_qual_lab".'parameter', "w_qual_lab".'reading_txt', "w_qual_lab".'reading_num', "w_qual_lab".'unit', "obs_points".'Geometry' as Geometry  from "w_qual_lab", "obs_points" where "w_qual_lab".'obsid'="obs_points".'obsid';
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('w_qual_lab_geom', 'Geometry', 'rowid', 'obs_points', 'Geometry');
create view "w_levels_geom" as select "b"."ROWID" as "ROWID", "a"."obsid" as "obsid", "a"."date_time" as "date_time",  "a"."meas" as "meas",  "a"."h_toc" as "h_toc",  "a"."level_masl" as "level_masl", "b"."Geometry" as "Geometry" from "w_levels" as "a" join "obs_points" as "b" using ("obsid");
insert into views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column) values ('w_levels_geom', 'Geometry', 'ROWID', 'obs_points', 'Geometry');
create view "w_qual_lab_dh" as select "obsid" as "obsid", "depth" as "depth", "report" as "report", "staff" as "staff", "date_time" as "date_time", "parameter" as "parameter", "reading_num" as "reading_num", "unit" as "unit" from "w_qual_lab" where "parameter" = 'Hårdhet tyska grader';
create view "w_qual_lab_ph" as select "obsid" as "obsid", "depth" as "depth", "report" as "report", "staff" as "staff", "date_time" as "date_time", "parameter" as "parameter", "reading_num" as "reading_num", "unit" as "unit" from "w_qual_lab" where "parameter" = 'pH';
create view w_flow_momflow as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unit" as "unit", "comment" as "comment" from w_flow where flowtype="Momflow"
create view w_flow_aveflow as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unit" as "unit", "comment" as "comment" from w_flow where flowtype="Aveflow"
create view w_flow_accvol as select "obsid" as "obsid","instrumentid" as "instrumentid","date_time" as "date_time","reading" as "reading", "unit" as "unit", "comment" as "comment" from w_flow where flowtype="Accvol"
