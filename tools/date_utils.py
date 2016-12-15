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
    """
    Parses a string and returns the found working dateformat string
    :param datestring: A string representing a date, ex: '2015-01-01 12:00'
    :return: The dateformat of the string, ex: '%Y-%m-%d %H:%M'

    Can only parse a list of preconfigured datestrings. See the code.

    >>> find_date_format('2015-01-01 01:01:01')
    '%Y-%m-%d %H:%M:%S'
    >>> find_date_format('01-01-2015 01:01:01')
    '%d-%m-%Y %H:%M:%S'
    >>> find_date_format('01:01:01')
    '%H:%M:%S'
    >>> find_date_format('2015-01-01')
    '%Y-%m-%d'
    >>> print(find_date_format('abc'))
    None
    """

    datestring = str(datestring)
    date_formats_to_try = ['%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S',
                           '%Y%m%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y%m%d',
                           '%Y-%m-%d', '%d-%m-%Y', '%H:%M:%S', '%d-%m-%Y %H:%M:%S',
                           '%d-%m-%Y %H:%M', '%d-%m-%Y %H']
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
    """
    Shifts a date n step_lenghts and returns a new date object
    :param adate: A string representing a date or a datetime object.
    :param n: Number of step_lengths to shift the date. It can be positive or negative.
    :param step_lenght: The step_lenght of the shift, for example "days, hours, weeks". See the function for all supported lenghts.
    :return: The dateformat of the string, ex: '%Y-%m-%d %H:%M'

    >>> dateshift('2015-02-01', -5, 'days')
    datetime.datetime(2015, 1, 27, 0, 0)
    >>> dateshift('2016-03-01', -24, 'hours')
    datetime.datetime(2016, 2, 29, 0, 0)
    """
    if isinstance(n, (basestring)):
        n = float(n)
    adate = datestring_to_date(adate)

    step_lenght = step_lenght.lower()
    if not step_lenght.endswith('s'):
        step_lenght += 's'

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
    else:
        return None
    new_date = adate + td
    return new_date

def datestring_to_date(astring, now=datetime.datetime.now()):
    """
    Takes a string representing a date and converts it to datetime
    :param astring: A string or a datetime-object representing a date, ex: '2015-01-01 12:00' or an epoch number.
    :return: A datetime object representing the string/datetime astring

    If astring is a datetime object, it is untouched and returned.

    >>> datestring_to_date('2015-01-01')
    datetime.datetime(2015, 1, 1, 0, 0)
    >>> datestring_to_date('2015-01-01 12:00')
    datetime.datetime(2015, 1, 1, 12, 0)
    >>> datestring_to_date(datetime.datetime(2015, 1, 1, 12, 0))
    datetime.datetime(2015, 1, 1, 12, 0)
    """
    if isinstance(astring, datetime.date):
        return astring
    else:
        format = find_date_format(astring)
        if format is not None:
            adate = datetime.datetime.strptime(astring, find_date_format(astring))
        else:
            splitted = astring.split()
            if len(splitted) == 2:
                n, step_lenght = splitted
                adate = dateshift(now, n, step_lenght)
            else:
                try:
                    adate = datetime.datetime.fromtimestamp(float(astring))
                except:
                    adate = None
    return adate

def long_dateformat(astring):
    return datetime.datetime.strftime(datestring_to_date(astring), '%Y-%m-%d %H:%M:%S')

def date_to_epoch(astring):
    return datestring_to_date(astring) - datetime.datetime(1970, 1, 1)