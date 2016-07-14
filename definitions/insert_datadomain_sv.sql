# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line
insert into zz_flowtype(type, unit, explanation) values("Accvol", "m3", "Accumulated volume");
insert into zz_flowtype(type, unit, explanation) values("Momflow", "l/s", "Momentary flow rate");
insert into zz_flowtype(type, unit, explanation) values("Aveflow", "l/s", "Average flow since last reading");
insert into zz_meteoparam(parameter, explanation) values("precip", "Precipitation");
insert into zz_meteoparam(parameter, explanation) values("temp", "Air temperature");
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('okänt','white','','white','NoBrush','not in (''berg'',''b'',''rock'',''ro'',''grovgrus'',''grg'',''coarse gravel'',''cgr'',''grus'',''gr'',''gravel'',''mellangrus'',''grm'',''medium gravel'',''mgr'',''fingrus'',''grf'',''fine gravel'',''fgr'',''grovsand'',''sag'',''coarse sand'',''csa'',''sand'',''sa'',''mellansand'',''sam'',''medium sand'',''msa'',''finsand'',''saf'',''fine sand'',''fsa'',''silt'',''si'',''lera'',''ler'',''le'',''clay'',''cl'',''morän'',''moran'',''mn'',''till'',''ti'',''torv'',''t'',''peat'',''pt'',''fyll'',''fyllning'',''f'',''made ground'',''mg'',''land fill'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('berg','red','x','red','DiagCrossPattern','in (''berg'',''b'',''rock'',''ro'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('grovgrus','DarkGreen','O','darkGreen','Dense7Pattern','in (''grovgrus'',''grg'',''coarse gravel'',''cgr'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('grus','DarkGreen','O','darkGreen','Dense7Pattern','in (''grus'',''gr'',''gravel'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('mellangrus','DarkGreen','o','darkGreen','Dense6Pattern','in (''mellangrus'',''grm'',''medium gravel'',''mgr'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('fingrus','DarkGreen','o','darkGreen','Dense6Pattern','in (''fingrus'',''grf'',''fine gravel'',''fgr'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('grovsand','green','*','green','Dense5Pattern','in (''grovsand'',''sag'',''coarse sand'',''csa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('sand','green','*','green','Dense5Pattern','in (''sand'',''sa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('mellansand','green','.','green','Dense4Pattern','in (''mellansand'',''sam'',''medium sand'',''msa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('finsand','DarkOrange','.','orange','Dense5Pattern','in (''finsand'',''saf'',''fine sand'',''fsa'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('silt','yellow','\\','yellow','BDiagPattern','in (''silt'',''si'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('lera','yellow','-','yellow','HorPattern','in (''lera'',''ler'',''le'',''clay'',''cl'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('morän','cyan','/','yellow','CrossPattern','in (''morän'',''moran'',''mn'',''till'',''ti'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('torv','DarkGray','+','darkGray','NoBrush','in (''torv'',''t'',''peat'',''pt'')');
insert into "zz_strat" (strat,color_mplot,hatch_mplot,color_qt,brush_qt,geoshorts) values('fyll','white','+','white','DiagCrossPattern','in (''fyll'',''fyllning'',''f'',''made ground'',''mg'',''land fill'')');
insert into "zz_capacity" (capacity,explanation,color_qt) values('','okänt', 'gray');
insert into "zz_capacity" (capacity,explanation,color_qt) values(' ','okänt', 'gray');
insert into "zz_capacity" (capacity,explanation,color_qt) values('0','okänt', 'gray');
insert into "zz_capacity" (capacity,explanation,color_qt) values('0 ','okänt', 'gray');
insert into "zz_capacity" (capacity,explanation,color_qt) values('1','ovan gvy', 'red');
insert into "zz_capacity" (capacity,explanation,color_qt) values('1 ','ovan gvy', 'red');
insert into "zz_capacity" (capacity,explanation,color_qt) values('2','ingen', 'magenta');
insert into "zz_capacity" (capacity,explanation,color_qt) values('2 ','ingen', 'magenta');
insert into "zz_capacity" (capacity,explanation,color_qt) values('3-','obetydlig', 'yellow');
insert into "zz_capacity" (capacity,explanation,color_qt) values('3','obetydlig', 'yellow');
insert into "zz_capacity" (capacity,explanation,color_qt) values('3 ','obetydlig', 'yellow');
insert into "zz_capacity" (capacity,explanation,color_qt) values('3+','obetydlig', 'darkYellow');
insert into "zz_capacity" (capacity,explanation,color_qt) values('4-','mindre god', 'green');
insert into "zz_capacity" (capacity,explanation,color_qt) values('4','mindre god', 'green');
insert into "zz_capacity" (capacity,explanation,color_qt) values('4 ','mindre god', 'green');
insert into "zz_capacity" (capacity,explanation,color_qt) values('4+','mindre god', 'darkGreen');
insert into "zz_capacity" (capacity,explanation,color_qt) values('5-','god', 'cyan');
insert into "zz_capacity" (capacity,explanation,color_qt) values('5','god', 'cyan');
insert into "zz_capacity" (capacity,explanation,color_qt) values('5 ','god', 'cyan');
insert into "zz_capacity" (capacity,explanation,color_qt) values('5+','god', 'darkCyan');
insert into "zz_capacity" (capacity,explanation,color_qt) values('6-','mycket god', 'blue');
insert into "zz_capacity" (capacity,explanation,color_qt) values('6','mycket god', 'blue');
insert into "zz_capacity" (capacity,explanation,color_qt) values('6 ','mycket god', 'blue');
insert into "zz_capacity" (capacity,explanation,color_qt) values('6+','mycket god', 'darkBlue');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('DO', 'DO', '%', 'syremättnad');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('DO', 'DO', 'mg/L', 'löst syre');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('konduktivitet', 'kond', 'µS/cm', 'förmåga att leda elektricitet (ett mått på innehåll av joner i en lösning)');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('pH', 'pH', NULL, 'negativ logaritm av vätejonaktivitet');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('redoxpotential', 'redox', 'mV', 'förmåga att ta upp elektroner');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('temperatur', 'temp', 'grC', 'vattentemperatur');
insert into "zz_w_qual_field_parameters" (parameter, shortname, unit, explanation) values('turbiditet', 'turb', 'FNU', 'suspension av olösta partiklar');
<<<<<<< HEAD
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('DO', '%', 'quality');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('DO', 'mg/L', 'quality');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('konduktivitet', 'µS/cm', 'quality');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('pH', NULL, 'quality');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('redoxpotential', 'mV', 'quality');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('temperatur', 'grC', 'quality');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('turbiditet', 'FNU', 'sample');
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('temperatur', 'grC', 'sample');
=======
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('DO', '%', 'quality')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('DO', 'mg/L', 'quality')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('konduktivitet', 'µS/cm', 'quality')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('pH', NULL, 'quality')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('redoxpotential', 'mV', 'quality')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('temperatur', 'grC', 'quality')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('turbiditet', 'FNU', 'sample')
insert into "zz_w_qual_field_parameter_groups" ("parameter", "unit", "groupname") values('temperatur', 'grC', 'sample')
>>>>>>> fe469d489001cd40bc6fc15d696771bef992680c
