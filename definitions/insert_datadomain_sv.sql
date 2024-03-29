﻿# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line
insert into zz_flowtype(type, explanation) values('Accvol', 'Accumulated volume');
insert into zz_flowtype(type, explanation) values('Momflow', 'Momentary flow rate');
insert into zz_flowtype(type, explanation) values('Aveflow', 'Average flow since last reading');
insert into zz_meteoparam(parameter, explanation) values('precip', 'Precipitation');
insert into zz_meteoparam(parameter, explanation) values('temp', 'Air temperature');
insert into zz_strat(geoshort,strata) values('berg','berg');
insert into zz_strat(geoshort,strata) values('b','berg');
insert into zz_strat(geoshort,strata) values('rock','berg');
insert into zz_strat(geoshort,strata) values('ro','berg');
insert into zz_strat(geoshort,strata) values('grovgrus','grovgrus');
insert into zz_strat(geoshort,strata) values('grg','grovgrus');
insert into zz_strat(geoshort,strata) values('coarse gravel','grovgrus');
insert into zz_strat(geoshort,strata) values('cgr','grovgrus');
insert into zz_strat(geoshort,strata) values('grus','grus');
insert into zz_strat(geoshort,strata) values('gr','grus');
insert into zz_strat(geoshort,strata) values('gravel','grus');
insert into zz_strat(geoshort,strata) values('mellangrus','mellangrus');
insert into zz_strat(geoshort,strata) values('grm','mellangrus');
insert into zz_strat(geoshort,strata) values('medium gravel','mellangrus');
insert into zz_strat(geoshort,strata) values('mgr','mellangrus');
insert into zz_strat(geoshort,strata) values('fingrus','fingrus');
insert into zz_strat(geoshort,strata) values('grf','fingrus');
insert into zz_strat(geoshort,strata) values('fine gravel','fingrus');
insert into zz_strat(geoshort,strata) values('fgr','fingrus');
insert into zz_strat(geoshort,strata) values('grovsand','grovsand');
insert into zz_strat(geoshort,strata) values('sag','grovsand');
insert into zz_strat(geoshort,strata) values('coarse sand','grovsand');
insert into zz_strat(geoshort,strata) values('csa','grovsand');
insert into zz_strat(geoshort,strata) values('sand','sand');
insert into zz_strat(geoshort,strata) values('sa','sand');
insert into zz_strat(geoshort,strata) values('mellansand','mellansand');
insert into zz_strat(geoshort,strata) values('sam','mellansand');
insert into zz_strat(geoshort,strata) values('medium sand','mellansand');
insert into zz_strat(geoshort,strata) values('msa','mellansand');
insert into zz_strat(geoshort,strata) values('finsand','finsand');
insert into zz_strat(geoshort,strata) values('saf','finsand');
insert into zz_strat(geoshort,strata) values('fine sand','finsand');
insert into zz_strat(geoshort,strata) values('fsa','finsand');
insert into zz_strat(geoshort,strata) values('silt','silt');
insert into zz_strat(geoshort,strata) values('si','silt');
insert into zz_strat(geoshort,strata) values('lera','lera');
insert into zz_strat(geoshort,strata) values('ler','lera');
insert into zz_strat(geoshort,strata) values('le','lera');
insert into zz_strat(geoshort,strata) values('clay','lera');
insert into zz_strat(geoshort,strata) values('cl','lera');
insert into zz_strat(geoshort,strata) values('morän','morän');
insert into zz_strat(geoshort,strata) values('moran','morän');
insert into zz_strat(geoshort,strata) values('mn','morän');
insert into zz_strat(geoshort,strata) values('till','morän');
insert into zz_strat(geoshort,strata) values('ti','morän');
insert into zz_strat(geoshort,strata) values('torv','torv');
insert into zz_strat(geoshort,strata) values('t','torv');
insert into zz_strat(geoshort,strata) values('peat','torv');
insert into zz_strat(geoshort,strata) values('pt','torv');
insert into zz_strat(geoshort,strata) values('fyll','fyll');
insert into zz_strat(geoshort,strata) values('fyllning','fyll');
insert into zz_strat(geoshort,strata) values('f','fyll');
insert into zz_strat(geoshort,strata) values('made ground','fyll');
insert into zz_strat(geoshort,strata) values('mg','fyll');
insert into zz_strat(geoshort,strata) values('land fill','fyll');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('torv','#d9bf9e','+','darkGray','NoBrush');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('fyll','white','+','white','DiagCrossPattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('lera','#fff08c','-','#ffeca3','HorPattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('silt','#fff08c','\\','yellow','BDiagPattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('finsand','#ffa852','.','orange','Dense5Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('mellansand','#80ff26','.','green','Dense4Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('sand','#80ff26','*','green','Dense5Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('grovsand','#80ff26','*','green','Dense5Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('fingrus','DarkGreen','o','darkGreen','Dense6Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('mellangrus','DarkGreen','o','darkGreen','Dense6Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('grus','DarkGreen','O','darkGreen','Dense7Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('grovgrus','DarkGreen','O','darkGreen','Dense7Pattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('morän','cyan','/','cyan','CrossPattern');
insert into zz_stratigraphy_plots (strata,color_mplot,hatch_mplot,color_qt,brush_qt) values('berg','red','x','red','DiagCrossPattern');
insert into zz_capacity (capacity,explanation) values('','okant');
insert into zz_capacity (capacity,explanation) values('0','okant');
insert into zz_capacity (capacity,explanation) values('1','ovan gvy');
insert into zz_capacity (capacity,explanation) values('2','ingen');
insert into zz_capacity (capacity,explanation) values('3-','obetydlig');
insert into zz_capacity (capacity,explanation) values('3','obetydlig');
insert into zz_capacity (capacity,explanation) values('3+','obetydlig');
insert into zz_capacity (capacity,explanation) values('4-','mindre god');
insert into zz_capacity (capacity,explanation) values('4','mindre god');
insert into zz_capacity (capacity,explanation) values('4+','mindre god');
insert into zz_capacity (capacity,explanation) values('5-','god');
insert into zz_capacity (capacity,explanation) values('5','god');
insert into zz_capacity (capacity,explanation) values('5+','god');
insert into zz_capacity (capacity,explanation) values('6-','mycket god');
insert into zz_capacity (capacity,explanation) values('6','mycket god');
insert into zz_capacity (capacity,explanation) values('6+','mycket god');
insert into zz_capacity_plots (capacity,color_qt) values('', 'gray');
insert into zz_capacity_plots (capacity,color_qt) values('0', 'gray');
insert into zz_capacity_plots (capacity,color_qt) values('1', 'red');
insert into zz_capacity_plots (capacity,color_qt) values('2', 'magenta');
insert into zz_capacity_plots (capacity,color_qt) values('3-', 'yellow');
insert into zz_capacity_plots (capacity,color_qt) values('3', 'yellow');
insert into zz_capacity_plots (capacity,color_qt) values('3+', 'darkYellow');
insert into zz_capacity_plots (capacity,color_qt) values('4-', 'green');
insert into zz_capacity_plots (capacity,color_qt) values('4', 'green');
insert into zz_capacity_plots (capacity,color_qt) values('4+', 'darkGreen');
insert into zz_capacity_plots (capacity,color_qt) values('5-', 'cyan');
insert into zz_capacity_plots (capacity,color_qt) values('5', 'cyan');
insert into zz_capacity_plots (capacity,color_qt) values('5+', 'darkCyan');
insert into zz_capacity_plots (capacity,color_qt) values('6-', 'blue');
insert into zz_capacity_plots (capacity,color_qt) values('6', 'blue');
insert into zz_capacity_plots (capacity,color_qt) values('6+', 'darkBlue');
