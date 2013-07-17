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
import PyQt4.QtCore
import PyQt4.QtGui

from qgis.core import *
from qgis.gui import *

import midvatten_utils as utils    

class updatecoordinates():

    def __init__(self, observations=[]):
        self.observations = observations

        """check whether there are observations without geometries"""
        sql = r"""select obsid from obs_points where (Geometry is null or Geometry ='') and obsid in """
        sql +=str(self.observations).encode('utf-8').replace('[','(')
        sql2 = sql.replace(']',')')        
        result = utils.sql_load_fr_db(sql2)
        #utils.pop_up_info(sql2)        #debugging
        if len(result)==0:
            self.doit()
        else:
            utils.pop_up_info("Positions (geometries) are missing for\n" + str(result) + "\nCoordinates will not be updated.")
        
    def doit(self):
        """Update coordinates for all observations in self.observations"""
        sql = r"""UPDATE OR IGNORE obs_points SET east=X(Geometry) WHERE obsid IN """
        sql +=str(self.observations).encode('utf-8').replace('[','(')
        sql2 = sql.replace(']',')')
        #utils.pop_up_info(sql2)     #DEBUGGING
        utils.sql_alter_db(sql2)
        sql = r"""UPDATE OR IGNORE obs_points SET north=Y(Geometry) WHERE obsid IN """
        sql +=str(self.observations).encode('utf-8').replace('[','(')
        sql2 = sql.replace(']',')')
        utils.sql_alter_db(sql2)

class updateposition():

    def __init__(self, observations=[]):
        self.observations = observations
        """check whether there are observations without coordinates"""
        sql = r"""select obsid from obs_points where (east is null or east ='' or  north is null or north = '') and obsid in """
        sql +=str(self.observations).encode('utf-8').replace('[','(')
        sql2 = sql.replace(']',')')        
        result = utils.sql_load_fr_db(sql2)
        if len(result)==0:
            self.doit()
        else:
            utils.pop_up_info("Coordinates are missing for\n" + str(result) + "\nPositions (geometry) will not be updated.")
        
    def doit(self):
        """Update positions for all observations in self.observations"""
        # First find EPSG-ID for the CRS
        sql = r"""SELECT srid FROM geometry_columns where f_table_name = 'obs_points'"""
        result = utils.sql_load_fr_db(sql)
        EPSGID= str(result[0][0])
        #Then do the operation
        sql = r"""Update or ignore 'obs_points' SET Geometry=MakePoint(east, north, """
        sql += EPSGID
        sql += """) WHERE obsid IN """
        sql +=str(self.observations).encode('utf-8').replace('[','(')
        sql2 = sql.replace(']',')')
        #utils.pop_up_info(sql2)     #DEBUGGING
        utils.sql_alter_db(sql2)