# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin with mocks used for testing.

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
import mock

class MockUsingReturnValue(object):
    def __init__(self, v=None):
        self.v =  v
    def get_v(self, *args, **kwargs):
        return self.v

class MockReturnUsingDict(object):
    def __init__(self, adict, args_idx):
        self.adict = adict
        self.args_idx = args_idx

    def get_v(self, *args, **kwargs):
        arg = args[self.args_idx]
        return_value = self.adict[arg]
        return return_value
