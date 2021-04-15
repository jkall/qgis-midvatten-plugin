CREATE TABLE s_qual_lab /*Soil quality data*/(
                         "obsid" text not null, "depth" double,
                         "report" text not null, "project" text,
                         "staff" text, "date_time" text,
                         "anameth" text, "parameter" text not null,
                         "reading_num" double, "reading_txt" text,
                         "unit" text, "comment" text,
                         primary key(report, parameter),
                         foreign key(obsid)
                         references obs_points(obsid),
                         foreign key(staff) references zz_staff(staff));

CREATE TABLE w_qual_logger /*Water quality from logger measurements*/(
 obsid text NOT NULL --Obsid linked to obs_points.obsid
 , date_time text NOT NULL --Date and Time for the observation
 , instrument text --Instrument ID
 , parameter text NOT NULL --Measured parameter
 , reading_num double --Value as real number
 , unit text --Unit
 , comment text --Comment
 , PRIMARY KEY(obsid, date_time, instrument, parameter, unit)
 , FOREIGN KEY(obsid) REFERENCES obs_points(obsid)
 );
CREATE UNIQUE INDEX w_qual_logger_unit_unique_index_null ON w_qual_logger /* Index to stop duplicate values where unit is null */ (
obsid, date_time, instrument, parameter, COALESCE(unit, '<NULL>')
);
