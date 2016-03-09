# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin handles dates. 
                             -------------------
        begin                : 2016-03-09
        copyright            : (C) 2016 by HenrikSpa
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
import datetime

def find_date_format(datestring):
    """ Parses a string and returns the found working dateformat string 
    
        Can only parse a list of preconfigured datestrings. See the code.
    """
    datestring = str(datestring)
    date_formats_to_try = ['%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y%m%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y%m%d', '%Y-%m-%d']
    found_format = None
    for dateformat in date_formats_to_try:
        try:
            datetime.datetime.strptime(datestring, dateformat)
        except ValueError:
            continue
        else:
            found_format = dateformat
            break
    return found_format
    
def dateshift(adate, n, step_lenght):
    """ Shifts a date n step_lenghts and returns a new date object """
    adate = datestring_to_date(adate)    
    if step_lenght == 'microseconds':
        td = datetime.timedelta(microseconds=n)
    elif step_lenght == 'milliseconds':
        td = datetime.timedelta(milliseconds=n)
    elif step_lenght == 'seconds':
        td = datetime.timedelta(seconds=n)
    elif step_lenght == 'minutes':
        td = datetime.timedelta(minutes=n)
    elif step_lenght == 'hours':
        td = datetime.timedelta(hours=n)
    elif step_lenght == 'days':
        td = datetime.timedelta(days=n)
    elif step_lenght == 'weeks':
        td = datetime.timedelta(weeks=n)       
    new_date = adate + td
    return new_date
    
def datestring_to_date(astring):
    """ Takes a string representing a date and converts it to datetime """
    if isinstance(astring, datetime.date):    
        return astring
    else:
        adate = datetime.datetime.strptime(astring, find_date_format(astring))
    return adate
        