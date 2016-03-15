# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of 
 water level measurements to the database. Also some calculations and calibrations. 
 
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
import unittest
import wlevels_calc_calibr

class Test_calc_best_fit(unittest.TestCase):
    def test_calc_best_fit(self):
        self.assertEqual(wlevels_calc_calibr.calc_best_fit([(5, 2), (-5, 6), (1.5, -6)]), mean([3, 11, 7.5]))

class Test_ts_get(unittest.TestCase):
    def test_ts_get(self):
        alist = [(1, 'a'), (2, 'b'), (3, 'c')]
        ref = [(1, 'a'), (2, 'b'), (3, 'c'), None]
        test_gen = wlevels_calc_calibr.ts_gen(alist)
        
        res = []
        try:
            while True:
                res.append(next(test_gen))
        except:
            pass
        self.assertEqual(ref, test)  
      
      
def test():
    unittest.main()
    
if __name__ == '__main__':
    unittest.main()

