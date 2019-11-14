﻿# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line
SPATIALITE SELECT InitSpatialMetadata(1);
CREATE TABLE about_db /*A status log for the tables in the db*/(
tablename text --Name of a table in the db
, columnname text --Name of column
, data_type text --Data type of the column
, not_null text --1 if NULL-values isn't allowed
, default_value text --The default value of the column
, primary_key text --The primary key order number if column is a primary key
, foreign_key text --"foreign key table(foreign key column)"
, description text --Description for column or table
, upd_date text --Date for last update
, upd_sign text --Person responsible for update
);
INSERT INTO about_db VALUES('*', '*', '', '', '', '', '', 'This db was created by Midvatten plugin CHANGETOPLUGINVERSION, running QGIS version CHANGETOQGISVERSION on top of CHANGETODBANDVERSION', '', '');
INSERT INTO about_db VALUES('*', '*', '', '', '', '', '', 'locale:CHANGETOLOCALE', '', '');
CREATE TABLE zz_staff /*Data domain for field staff used when importing data*/(
staff text NOT NULL--Initials of the field staff
, name text --Name of the field staff
, PRIMARY KEY(staff)
);
CREATE TABLE zz_flowtype /*Data domain for flowtypes in table w_flow*/(
type text NOT NULL --Allowed flowtypes
, explanation text --Explanation of the flowtypes
, PRIMARY KEY(type)
);
CREATE TABLE zz_meteoparam /*Data domain for meteorological parameters in meteo*/(
parameter text NOT NULL --Allowed meteorological parameters
, explanation text --Explanation of the parameters
, PRIMARY KEY(parameter)
);
CREATE TABLE zz_strat /*Data domain for stratigraphy classes*/(
geoshort text NOT NULL --Abbreviation for the strata (stratigraphy class)
, strata text NOT NULL --clay etc
, PRIMARY KEY(geoshort)
);
CREATE TABLE zz_stratigraphy_plots /*Data domain for stratigraphy plot colors and symbols used by the plugin*/(
strata text NOT NULL --clay etc
, color_mplot text NOT NULL --Color codes for matplotlib plots
, hatch_mplot text NOT NULL --Hatch codes for matplotlib plots
, color_qt text NOT NULL --Color codes for Qt plots
, brush_qt text NOT NULL --Brush types for Qt plots
, PRIMARY KEY(strata)
);
CREATE TABLE zz_capacity /*Data domain for capacity classes used by the plugin*/(
capacity text NOT NULL --Water capacity (ex. in the range 1-6)
, explanation text NOT NULL --Description of water capacity classes
, PRIMARY KEY(capacity)
);
CREATE TABLE zz_capacity_plots /*Data domain for capacity plot colors used by the plugin*/(
capacity text NOT NULL --Water capacity (ex. in the range 1-6)
, color_qt text NOT NULL --Hatchcolor codes for Qt plots
, PRIMARY KEY(capacity)
, FOREIGN KEY(capacity) REFERENCES zz_capacity(capacity)
);
CREATE TABLE obs_points /*One of the two main tables. This table holds all point observation objects.*/(
obsid text NOT NULL --ID for the observation point
, name text --Ordinary name for the observation
, place text --Place for the observation. E.g. estate
, type text --Type of observation
, length double --Borehole length from ground surface to bottom (equals to depth if vertical)
, drillstop text --Drill stop (ex "Driven to bedrock")
, diam double --Inner diameter for casing or upper part of borehole
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
, com_onerow text --Onerow comment
, com_html text --Multiline formatted comment in html format
, PRIMARY KEY (obsid)
);
SPATIALITE SELECT AddGeometryColumn('obs_points', 'geometry', CHANGETORELEVANTEPSGID, 'POINT', 'XY', 0);
POSTGIS ALTER TABLE obs_points ADD COLUMN geometry geometry(Point,CHANGETORELEVANTEPSGID);
CREATE TABLE obs_lines /*One of the two main tables. This table holds all line observation objects.*/(
obsid text  NOT NULL --ID for observation line
, name text --Ordinary name for the observation
, place text --Place for the observation
, type text --Type of observation
, source text --The origin for the observation
, PRIMARY KEY (obsid)
);
SPATIALITE SELECT AddGeometryColumn('obs_lines', 'geometry', CHANGETORELEVANTEPSGID, 'LINESTRING', 'XY', 0);
POSTGIS ALTER TABLE obs_lines ADD COLUMN geometry geometry(Linestring,CHANGETORELEVANTEPSGID);
CREATE TABLE w_levels /*Manual water level measurements*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, date_time text NOT NULL --Date and Time for the observation
, meas double --Distance from measuring point to water level
, h_toc double --Elevation (masl) for the measuring point at the particular date_time (measuring point elevation may vary by time)
, level_masl double --Water level elevation (masl) calculated from measuring point and distance from measuring point to water level
, comment text --Comment
, PRIMARY KEY (obsid, date_time)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid)
);
CREATE TABLE w_levels_logger /*Automatic water level readings*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, date_time text NOT NULL --Date and Time for the observation
, head_cm double --Pressure (cm water column) on pressure transducer
, temp_degc double --Temperature degrees C
, cond_mscm double --Electrical conductivity mS/cm
, level_masl double --Corresponding Water level elevation (masl)
, comment text --Comment
, PRIMARY KEY (obsid, date_time)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid)
);
CREATE TABLE stratigraphy /*Stratigraphy information from drillings*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, stratid integer NOT NULL --Stratigraphy layer ID for the OBSID
, depthtop double --Top of the layer in m from ground surface
, depthbot double --Bottom of the layer in m from ground surface
, geology text --Full description of geology
, geoshort text --Short description of geology
, capacity text --Well development at the layer
, development text --Well development - Is the flushed water clear and free of suspended solids?
, comment text --Comment
, PRIMARY KEY (obsid, stratid)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid)
);
CREATE TABLE w_qual_field /*Water quality from field measurements*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, staff text --Field staff
, date_time text NOT NULL --Date and Time for the observation
, instrument text --Instrument ID
, parameter text NOT NULL --Measured parameter
, reading_num double --Value as real number
, reading_txt text --Value as text (ex. can contain '>' and '<')
, unit text --Unit
, depth double --The depth at which the measurement was done
, comment text --Comment
, PRIMARY KEY(obsid, date_time, parameter, unit)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid), FOREIGN KEY(staff) REFERENCES zz_staff(staff)
);
CREATE TABLE w_qual_lab /*Water quality from laboratory analysis*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, depth double --Depth (m below h_gs) from where sample is taken
, report text NOT NULL --Report no from laboratory
, project text --Project number
, staff text --Field staff
, date_time text --Date and Time for the observation
, anameth text --Analysis method
, parameter text NOT NULL --Measured parameter
, reading_num double --Value as real number
, reading_txt text --Value as text (ex. can contain '>' and '<')
, unit text --Unit
, comment text --Comment
, PRIMARY KEY(report, parameter)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid), FOREIGN KEY(staff) REFERENCES zz_staff(staff)
);
CREATE TABLE w_flow /*Water flow*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, instrumentid text NOT NULL --Instrument Id
, flowtype text NOT NULL --Flowtype must correspond to type in flowtypes
, date_time text NOT NULL --Date and Time for the observation
, reading double --Value (real number) reading for the flow rate
, unit text --Unit corresponding to the value reading
, comment text --Comment
, PRIMARY KEY (obsid, instrumentid, flowtype, date_time)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid), FOREIGN KEY (flowtype) REFERENCES zz_flowtype(type)
);
CREATE TABLE meteo /*meteorological observations*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, instrumentid text NOT NULL --Instrument ID
, parameter text NOT NULL --The meteorological parameter
, date_time text NOT NULL --Date and Time for the observation
, reading_num double --Value (real number) reading for the parameter
, reading_txt text --Value as text (ex. can contain '>' and '<')
, unit text --Unit corresponding to the value reading
, comment text --Comment
, PRIMARY KEY (obsid, instrumentid, parameter, date_time)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid), FOREIGN KEY (parameter) REFERENCES zz_meteoparam(parameter)
);
CREATE TABLE seismic_data /*Interpreted data from seismic measurements*/(
obsid text NOT NULL --Obsid linked to obs_lines.obsid
, length double NOT NULL --Length along line
, ground double --Ground surface level
, bedrock double --Interpreted level for bedrock surface
, gw_table double --Interpreted level for limit between unsaturated/saturated conditions
, comment text --Additional info
, PRIMARY KEY (obsid, length)
, FOREIGN KEY (obsid) REFERENCES obs_lines(obsid)
);
CREATE TABLE vlf_data /*Raw data from VLF measurements*/(
obsid text NOT NULL --Obsid linked to obs_lines.obsid
, length double NOT NULL --Length along line
, real_comp double --Raw data real component (in-phase(%))
, imag_comp double --Raw data imaginary component
, comment text --Additional info
, PRIMARY KEY (obsid, length)
, FOREIGN KEY (obsid) REFERENCES obs_lines(obsid)
);
CREATE TABLE comments /*Comments connected to obsids*/(
obsid text NOT NULL --Obsid linked to obs_points.obsid
, date_time text NOT NULL --Date and Time for the comment
, comment text NOT NULL --Comment
, staff text NOT NULL --Staff who made the comment
, PRIMARY KEY(obsid, date_time)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid), FOREIGN KEY(staff) REFERENCES zz_staff(staff)
);
CREATE TABLE interlab4_obsid_assignment /*Assign obsids automatically during interlab4 import*/(
specifik_provplats text NOT NULL --The attribute Specifik Provplats from interlab4 file format.
, provplatsnamn text NOT NULL --The attribute Provplatsnamn from interlab4 file format.
, obsid text NOT NULL --Obsid linked to obs_points.obsid
, PRIMARY KEY(specifik_provplats, provplatsnamn)
, FOREIGN KEY(obsid) REFERENCES obs_points(obsid)
);
SPATIALITE CREATE VIEW obs_p_w_qual_field AS SELECT DISTINCT a.rowid AS rowid, a.obsid AS obsid, a.geometry AS geometry FROM obs_points AS a JOIN w_qual_field AS b using (obsid);
SPATIALITE CREATE VIEW obs_p_w_qual_lab AS SELECT DISTINCT a.rowid AS rowid, a.obsid AS obsid, a.geometry AS geometry FROM obs_points AS a JOIN w_qual_lab AS b using (obsid);
SPATIALITE CREATE VIEW obs_p_w_strat AS SELECT DISTINCT a.rowid AS rowid, a.obsid AS obsid, a.h_toc AS h_toc, a.h_gs AS h_gs, a.geometry AS geometry FROM obs_points AS a JOIN stratigraphy AS b using (obsid);
SPATIALITE CREATE VIEW obs_p_w_lvl AS SELECT DISTINCT a.rowid AS rowid, a.obsid AS obsid, a.geometry AS geometry FROM obs_points AS a JOIN w_levels AS b USING (obsid);
SPATIALITE CREATE VIEW w_lvls_last_geom AS SELECT b.rowid AS rowid, a.obsid AS obsid, MAX(a.date_time) AS date_time, a.meas AS meas, a.level_masl AS level_masl, b.h_tocags AS h_tocags, b.geometry AS geometry FROM w_levels AS a JOIN obs_points AS b using (obsid) GROUP BY obsid;
SPATIALITE CREATE VIEW w_qual_field_geom AS SELECT w_qual_field.rowid AS rowid, w_qual_field.obsid AS obsid, w_qual_field.staff AS staff, w_qual_field.date_time AS date_time, w_qual_field.instrument AS instrument, w_qual_field.parameter AS parameter, w_qual_field.reading_num AS reading_num, w_qual_field.reading_txt AS reading_txt, w_qual_field.unit AS unit, w_qual_field.comment AS comment, obs_points.geometry AS geometry FROM w_qual_field AS w_qual_field left join obs_points using (obsid);
SPATIALITE CREATE VIEW w_qual_lab_geom AS SELECT w_qual_lab.rowid AS rowid, w_qual_lab.obsid, w_qual_lab.depth, w_qual_lab.report, w_qual_lab.staff, w_qual_lab.date_time, w_qual_lab.anameth, w_qual_lab.parameter, w_qual_lab.reading_txt, w_qual_lab.reading_num, w_qual_lab.unit, obs_points.geometry AS geometry  FROM w_qual_lab, obs_points where w_qual_lab.obsid=obs_points.obsid;
SPATIALITE CREATE VIEW w_levels_geom AS SELECT b.rowid AS rowid, a.obsid AS obsid, a.date_time AS date_time,  a.meas AS meas,  a.h_toc AS h_toc,  a.level_masl AS level_masl, b.geometry AS geometry FROM w_levels AS a join obs_points AS b using (obsid);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('obs_p_w_qual_field', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('obs_p_w_qual_lab', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('obs_p_w_strat', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('obs_p_w_lvl', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('w_lvls_last_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('w_qual_field_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('w_qual_lab_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
SPATIALITE INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) VALUES ('w_levels_geom', 'geometry', 'rowid', 'obs_points', 'geometry',1);
POSTGIS CREATE VIEW obs_p_w_qual_field AS SELECT DISTINCT a.obsid AS obsid, a.geometry AS geometry FROM obs_points AS a JOIN w_qual_field AS b using (obsid);
POSTGIS CREATE VIEW obs_p_w_qual_lab AS SELECT DISTINCT a.obsid AS obsid, a.geometry AS geometry FROM obs_points AS a JOIN w_qual_lab AS b using (obsid);
POSTGIS CREATE VIEW obs_p_w_strat AS SELECT DISTINCT a.obsid AS obsid, a.h_toc AS h_toc, a.h_gs AS h_gs, a.geometry AS geometry FROM obs_points AS a JOIN stratigraphy AS b using (obsid);
POSTGIS CREATE VIEW obs_p_w_lvl AS SELECT DISTINCT a.obsid AS obsid, a.geometry AS geometry FROM obs_points AS a JOIN w_levels AS b USING (obsid);
POSTGIS CREATE VIEW w_lvls_last_geom AS SELECT a.obsid AS obsid, a.date_time AS date_time, a.meas AS meas, a.level_masl AS level_masl, c.h_tocags AS h_tocags, c.geometry AS geometry FROM w_levels AS a JOIN (SELECT obsid, max(date_time) as date_time FROM w_levels GROUP BY obsid) as b ON a.obsid=b.obsid and a.date_time=b.date_time JOIN obs_points AS c ON a.obsid=c.obsid;
POSTGIS CREATE VIEW w_qual_field_geom AS SELECT w_qual_field.obsid AS obsid, w_qual_field.staff AS staff, w_qual_field.date_time AS date_time, w_qual_field.instrument AS instrument, w_qual_field.parameter AS parameter, w_qual_field.reading_num AS reading_num, w_qual_field.reading_txt AS reading_txt, w_qual_field.unit AS unit, w_qual_field.comment AS comment, obs_points.geometry AS geometry FROM w_qual_field AS w_qual_field left join obs_points using (obsid);
POSTGIS CREATE VIEW w_qual_lab_geom AS SELECT w_qual_lab.obsid, w_qual_lab.depth, w_qual_lab.report, w_qual_lab.staff, w_qual_lab.date_time, w_qual_lab.anameth, w_qual_lab.parameter, w_qual_lab.reading_txt, w_qual_lab.reading_num, w_qual_lab.unit, obs_points.geometry AS geometry FROM w_qual_lab, obs_points where w_qual_lab.obsid=obs_points.obsid;
POSTGIS CREATE VIEW w_levels_geom AS SELECT a.obsid AS obsid, a.date_time AS date_time,  a.meas AS meas,  a.h_toc AS h_toc,  a.level_masl AS level_masl, b.geometry AS geometry FROM w_levels AS a join obs_points AS b using (obsid);
CREATE VIEW w_flow_momflow AS SELECT obsid AS obsid,instrumentid AS instrumentid,date_time AS date_time,reading AS reading, unit AS unit, comment AS comment FROM w_flow where flowtype='Momflow';
CREATE VIEW w_flow_aveflow AS SELECT obsid AS obsid,instrumentid AS instrumentid,date_time AS date_time,reading AS reading, unit AS unit, comment AS comment FROM w_flow where flowtype='Aveflow';
CREATE VIEW w_flow_accvol AS SELECT obsid AS obsid,instrumentid AS instrumentid,date_time AS date_time,reading AS reading, unit AS unit, comment AS comment FROM w_flow where flowtype='Accvol';
CREATE INDEX idx_wquallab_odtp ON w_qual_lab(obsid, date_time, parameter);
CREATE INDEX idx_wquallab_odtpu ON w_qual_lab(obsid, date_time, parameter, unit);
CREATE INDEX idx_wqualfield_odtpu ON w_qual_field(obsid, date_time, parameter, unit);
