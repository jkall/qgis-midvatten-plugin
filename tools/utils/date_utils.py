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
from __future__ import absolute_import

import datetime
import re
from builtins import str
import pytz
import numpy as np

from qgis.PyQt.QtCore import QCoreApplication

from midvatten.tools.utils.common_utils import returnunicode as ru, MessagebarAndLog


def find_date_format(datestring, suppress_error_msg=False):
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
                           '%Y%m%d %H:%M:%S', '%Y%m%d %H:%M', '%Y-%m-%d %H:%M', '%Y%m%d',
                           '%Y-%m-%d', '%d-%m-%Y', '%H:%M:%S', '%d-%m-%Y %H:%M:%S',
                           '%d-%m-%Y %H:%M', '%d-%m-%Y %H', '%Y/%m/%d %H:%M',
                           '%Y/%m/%d %H', '%Y%m%d %H%M%S', '%Y%m%d %H%M',
                           '%Y%m%d %H', '%m/%d/%y %H:%M:%S', '%d-%b-%y %H:%M:%S',
                           '%d-%b-%Y %H:%M:%S', '%d-%B-%y %H:%M:%S', '%d-%B-%Y %H:%M:%S',
                           '%d.%m.%Y %H:%M', '%d.%m.%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M']
    found_format = None
    for dateformat in date_formats_to_try:
        try:
            datetime.datetime.strptime(datestring, dateformat)
        except ValueError:
            continue
        else:
            found_format = dateformat
            break

    if found_format is None:
        if not suppress_error_msg:
            MessagebarAndLog.critical(
                bar_msg=QCoreApplication.translate('find_date_format', 'Date parsing failed, see log message panel'),
                log_msg=ru(QCoreApplication.translate('find_date_format', 'Could not find the date format for string "%s"\nSupported date formats:\n%s'))%(ru(datestring), '\n'.join(date_formats_to_try)))

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
    if isinstance(n, (str)):
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

def datestring_to_date(astring, now=datetime.datetime.now(), df=None):
    """
    Takes a string representing a date and converts it to datetime
    :param astring: A string or a datetime-object representing a date, ex: '2015-01-01 12:00' or an epoch number.
    :param: df: a date format
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
        if df is not None:
            format = df
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

def long_dateformat(astring, dateformat=None):
    return datetime.datetime.strftime(datestring_to_date(astring, df=dateformat), '%Y-%m-%d %H:%M:%S')

def date_to_epoch(astring):
    return datestring_to_date(astring) - datetime.datetime(1970, 1, 1)

def reformat_date_time(astring):
    date_format = find_date_format(astring)
    if date_format is None:
        return None

    date = u'-'.join([u'%{}'.format(letter) for letter in [u'Y', u'm', u'd'] if letter in date_format.replace(u'b', u'm').replace(u'B', u'm').replace(u'y', u'Y')]) # fix for rare cases where date_format contains month names instead of month no.
    time = ':'.join(['%{}'.format(letter) for letter in ['H', 'M', 'S'] if letter in date_format])
    outformat = ' '.join([date, time])
    new_datestring = datetime.datetime.strftime(datetime.datetime.strptime(astring, date_format), outformat)
    return new_datestring

def find_time_format(datestring):
    """
    Parses a string and returns the found working dateformat string
    :param datestring: A string representing a time, ex: '12:00'
    :return: The dateformat of the string, ex: ' %H:%M'

    Can only parse a list of preconfigured datestrings. See the code.

    """
    datestring = str(datestring)
    #Length, format
    time_formats_to_try = {4: ['%H%M'],
                           5: ['%H:%M', '%H %M'],
                           6: ['%H%M%S'],
                           8: ['%H:%M:%S', '%H %M %S']}


    found_format = None

    length = len(datestring)

    format_list = time_formats_to_try.get(length, None)
    if format_list is None:
        print('Timeformat not supported for %s'%datestring)
        return None

    for timeformat in format_list:
        try:
            datetime.datetime.strptime(datestring, timeformat)
        except ValueError:
            continue
        else:
            found_format = timeformat
            break

    return found_format

def parse_timezone_to_timedelta(tz_string):
    """

    :param tz_string:
    :return:

    >>> parse_timezone_to_timedelta('GMT+02:00')
    datetime.timedelta(seconds=7200)
    >>> parse_timezone_to_timedelta('GMT')
    datetime.timedelta(0)
    >>> parse_timezone_to_timedelta('GMT00:00')
    datetime.timedelta(0)
    >>> parse_timezone_to_timedelta('GMT-11:00')
    datetime.timedelta(days=-1, seconds=46800)
    >>> parse_timezone_to_timedelta('GMT+14:00')
    datetime.timedelta(seconds=50400)
    >>> parse_timezone_to_timedelta('GMT+2')
    datetime.timedelta(seconds=7200)
    >>> parse_timezone_to_timedelta('GMT+02:35')
    datetime.timedelta(seconds=9300)
    >>> parse_timezone_to_timedelta('UTC+02:00')
    datetime.timedelta(seconds=7200)
    >>> parse_timezone_to_timedelta('UTC')
    datetime.timedelta(0)
    >>> parse_timezone_to_timedelta('UTC00:00')
    datetime.timedelta(0)
    >>> parse_timezone_to_timedelta('UTC-11:00')
    datetime.timedelta(days=-1, seconds=46800)
    >>> parse_timezone_to_timedelta('UTC+14:00')
    datetime.timedelta(seconds=50400)
    >>> parse_timezone_to_timedelta('UTC+2')
    datetime.timedelta(seconds=7200)
    >>> parse_timezone_to_timedelta('UTC+02:35')
    datetime.timedelta(seconds=9300)
    >>> parse_timezone_to_timedelta('01234 UTC+02:35')
    datetime.timedelta(seconds=9300)
    >>> parse_timezone_to_timedelta('01234\tUTC+02:35')
    datetime.timedelta(seconds=9300)
    >>> parse_timezone_to_timedelta('-227495\tUTC+02:35')
    datetime.timedelta(seconds=9300)
    """
    _tz_string = ru(tz_string).lower()
    match = re.match(r'[\-a-zA-Z0-9\ \t]*(gmt|utc)([\+\-]*)([0-9]+)([\:]*[0-9]*)', _tz_string, re.IGNORECASE)
    if match is None:
        if not _tz_string.replace('gmt', '').replace('utc', ''):
            res = ('', '', '', '')
        else:
            raise ValueError(ru(QCoreApplication.translate('parse_timezone_to_timedelta',
                                                           'Timezone string %s could not be parsed!'))%tz_string)
    else:
        res = match.groups()
    if res[1] == '-':
        sign = -1
    else:
        sign = 1
    hours = int(res[2])*sign if res[2] else 0
    minutes = int(res[3].lstrip(':'))*sign if res[3].lstrip(':') else 0
    td = datetime.timedelta(hours=hours, minutes=minutes)
    return td

def change_timezone(date_or_string, from_timezone, to_timezone):
    """
    This function should probably not be used for huge amounts of logger data as it might be rather slow.
    @param date_or_string:
    @param from_timezone:
    @param to_timezone:
    @return:

    # Replace winter time into same utc offset - no change
    >>> change_timezone('2022-03-27 00:00', 'Europe/Stockholm', 'UTC+1')
    '2022-03-27 00:00'
    >>> change_timezone('2022-03-28 00:00', 'Europe/Stockholm', 'UTC+1')
    '2022-03-27 23:00'
    >>> change_timezone('2022-03-27 23:00', 'UTC+1', 'Europe/Stockholm')
    '2022-03-28 00:00'
    >>> change_timezone('2022-10-30 00:00', 'Europe/Stockholm', 'UTC+1')
    '2022-10-29 23:00'
    >>> change_timezone('2022-10-31 00:00', 'Europe/Stockholm', 'UTC+1')
    '2022-10-31 00:00'
    """
    def get_tz_and_timedelta(tz_string):
        if tz_string.lower().startswith('utc'):
            new_tz = pytz.utc
            timedelta = parse_timezone_to_timedelta(tz_string)
        else:
            new_tz = pytz.timezone(tz_string)
            timedelta = None
        return new_tz, timedelta


    tz_naive = datestring_to_date(date_or_string)

    tz, td = get_tz_and_timedelta(from_timezone)
    tz_aware = tz.localize(tz_naive, is_dst=None)
    if td:
        tz_aware = tz_aware - td

    new_tz, new_td = get_tz_and_timedelta(to_timezone)
    new_date = tz_aware.astimezone(new_tz)
    if new_td is not None:
        new_date = new_date + new_td

    if isinstance(date_or_string, str):
        res = new_date.strftime(find_date_format(date_or_string))
    else:
        res = new_date
    return res

def get_pytz_timezones():
    return pytz.all_timezones