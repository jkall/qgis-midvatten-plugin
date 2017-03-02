# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin...
(1) updates coordinates from map position or
(2) updates map position from given coordinates 
                             -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
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
import db_utils
import midvatten_utils as utils

"""
PLEASE NOTICE, THIS MODULE IS NO LONGER USED

This module should be removed from the midvatten plugin
"""

class updatecoordinates():

    def __init__(self, observations=[]):#observations is supposed to be a list of unicode strings
        self.observations = observations
        i = 0
        for obs in observations:
                self.observations[i] = obs.encode('utf-8') #turn into a list of python byte strings
                i += 1
        self.sqlpart2 =(str(self.observations).encode('utf-8').replace('[','(')).replace(']',')')#turn list into string and also encode to utf-8 byte string to enable replace
        """check whether there are observations without geometries"""
        sql = r"""select obsid from obs_points where (Geometry is null or Geometry ='') and obsid in """ + self.sqlpart2
        ConnectionOK, result = db_utils.sql_load_fr_db(sql)#ok to send a utf-8 byte string even though unicode is preferred
        if len(result)==0:
            self.do_it()
        else:
            utils.pop_up_info("Positions (geometries) are missing for\n" + result[0][0] + "\nCoordinates will not be updated.")
        
    def do_it(self):
        """Update coordinates for all observations in self.observations"""
        
        sql = r"""UPDATE OR IGNORE obs_points SET east=X(Geometry) WHERE obsid IN """ + self.sqlpart2
        db_utils.sql_alter_db(sql)
        sql = r"""UPDATE OR IGNORE obs_points SET north=Y(Geometry) WHERE obsid IN """ + self.sqlpart2
        db_utils.sql_alter_db(sql)

class updateposition():

    def __init__(self, observations=[]):#observations is supposed to be a list of unicode strings
        self.observations = observations
        i = 0
        for obs in observations:
                self.observations[i] = obs.encode('utf-8') #turn into a list of python byte strings
                i += 1
        self.sqlpart2 =(str(self.observations).encode('utf-8').replace('[','(')).replace(']',')')#turn list into string and also encode to utf-8 byte string to enable replace
        """check whether there are observations without coordinates"""
        sql = r"""select obsid from obs_points where (east is null or east ='' or  north is null or north = '') and obsid in """ + self.sqlpart2
        ConnectionOK, result = db_utils.sql_load_fr_db(sql)
        if len(result)==0:
            self.do_it()
        else:
            utils.pop_up_info("Coordinates are missing for\n" + result[0][0] + "\nPositions (geometry) will not be updated.")
        
    def do_it(self):
        """Update positions for all observations in self.observations"""
        # First find EPSG-ID for the CRS
        sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
        ConnectionOK, result = db_utils.sql_load_fr_db(sql)
        EPSGID= str(result[0][0])
        #Then do the operation
        sql = r"""Update or ignore 'obs_points' SET Geometry=MakePoint(east, north, """
        sql += EPSGID
        sql += """) WHERE obsid IN """ + self.sqlpart2
        db_utils.sql_alter_db(sql)
