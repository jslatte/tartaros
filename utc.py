###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from time import gmtime, localtime, mktime
from calendar import timegm

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

DST = False # should be True if daylight saving time (March - November)

####################################################################################################
# UTC ##############################################################################################
####################################################################################################
####################################################################################################


class UTC():
    """ Sub-library for UTC functions.
    """

    def __init__(self, logger):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # instantialize logger
        self.log = logger

    def convert_date_string_to_db_time(self, date_string, vim_log=False):
        """
        """

        result = {'db time': None}

        # build date/time tuple from time string to convert
        date = date_string.split(' ')[0]
        tm = date_string.split(' ')[1]

        if not vim_log:
            year = int(date.split('-')[0])
            month = int(date.split('-')[1])
            day = int(date.split('-')[2])
        else:
            month = int(date.split('-')[0])
            day = int(date.split('-')[1])
            year = 2000 + int(date.split('-')[2])

        hour = int(tm.split(':')[0])
        min = int(tm.split(':')[1])
        sec = int(tm.split(':')[2])

        date_time = (year, month, day, hour, min, sec,)

        # convert date/time to seconds
        result['db time'] = timegm(date_time) + (7 * 60 *60)

        return result

    def return_day_start_time_for_time(self,time='Now'):
        """ Return the 00:00 time value for day of the given time.
        'time' should be a string of format 'now' or '5 minutes ago'.
        Currently, this is translated in hard code from UTC to PST.
        Daylight saving time must be toggled manually. """

        self.log.debug("Returning day start time for '%s' ..." % str(time))

        # convert string to database time
        databaseTime = self.convert_string_to_time(str(time))
        # convert database time to date dictionary
        dateDic = self.convert_database_time_to_date(databaseTime)
        # update date dictionary to be start of day
        if DST: dateDic['hour']     = 7 # with daylight saving time
        else: dateDic['hour']     = 8
        dateDic['minute']   = 0
        dateDic['second']   = 0
        # convert updated date dictionary back to database time
        startTime = self.convert_date_to_database_time(dateDic)
        # return day start time
        return startTime

    def return_day_end_time_for_time(self,time='Now'):
        """ Return the next 00:00 time value for the day of the given time.
        'time' should be a string of format 'now' or '5 minutes ago'.
        Currently, this is translated in hard code from UTC to PST.
        Daylight saving time must be toggled manually. """

        self.log.debug("Returning day end time for '%s' ..." % str(time))

        # convert string to database time
        databaseTime = self.convert_string_to_time(str(time))
        # convert database time to date dictionary
        dateDic = self.convert_database_time_to_date(databaseTime)
        # update date dictionary to be end of day
        dateDic['day']      = int(dateDic['day']) + 1
        if DST: dateDic['hour']     = 7 # with daylight saving time
        else: dateDic['hour']     = 8
        dateDic['minute']   = 0
        dateDic['second']   = 0
        # convert updated date dictionary back to database time
        endTime = self.convert_date_to_database_time(dateDic)
        # return day end time
        return endTime

    def convert_database_time_to_date(self, databaseTime, timeZone='global'):
        """ Convert a database time value (seconds from 1970) to date string and return dictionary
                containing date values. """

        # process variables
        time = int(databaseTime)
        # variable dictionary
        vars = {'time':str(time)}
        # declaration
        #self.log.debug("Converting database time %(time)s to date ..." % vars)
        # convert seconds to date/time in UTC
        if str(timeZone).lower() == 'local': dateTime = localtime(time)
        else: dateTime = gmtime(time)
        date={}
        # update dictionary with each date/time component
        date['year'] = dateTime.tm_year
        date['month'] = dateTime.tm_mon
        date['day'] = dateTime.tm_mday
        date['hour'] = dateTime.tm_hour
        date['minute'] = dateTime.tm_min
        date['second'] = dateTime.tm_sec
        date['week day'] = dateTime.tm_wday
        date['year day'] = dateTime.tm_yday
        date['dst'] = dateTime.tm_isdst
        # adjust for Daylight Savings Time
        #if DST: date['hour'] += date['dst']
        #self.log.trace('Date/Time: %(week day)s %(month)s %(day)s, '
        #               '%(year)s %(hour)s:%(minute)s:%(second)s' % date)
        # return dictionary containing date data (UTC)
        return date

    def convert_database_time_to_server_date(self,databaseTime,abbrev=False):
        """ Convert a database time value to server date string. """

        # variable dictionary
        vars = {'time':         databaseTime,
                'abbreviated':  abbrev}
        # ancillary variables
        weekDays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        months = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        # declaration
        #self.log.debug('Converting database time %(time)s to server date ...' % vars)
        # convert seconds to date/time dictionary (local)
        dateData = self.convert_database_time_to_date(vars['time'],'local')
        # update date dictionary with returned values
        dateData['week day'] = weekDays[dateData['week day']]
        dateData['month abbr'] = months[dateData['month']]
        dateData['year abbr'] = int(dateData['year'])-2000
        # stringify seconds
        if dateData['second'] is 0: dateData['second'] = '00'
        elif dateData['second'] < 10: dateData['second'] = '0%s'%str(dateData['second'])
        else: dateData['second'] = str(dateData['second'])
        # stringify minutes
        if dateData['minute'] is 0: dateData['minute'] = '00'
        elif dateData['minute'] < 10: dateData['minute'] = '0%s'%str(dateData['minute'])
        else: dateData['minute'] = str(dateData['minute'])
        # stringify hours
        if dateData['hour'] is 0:   dateData['hour']   = '00'
        elif dateData['hour'] < 10: dateData['hour'] = '0%s'%str(dateData['hour'])
        else: dateData['hour'] = str(dateData['hour'])
        # create date/time string in server format
        if abbrev is True:
            date = '%(month)s/%(day)s/%(year abbr)s %(hour)s:%(minute)s:%(second)s'%dateData
        elif abbrev == 'clip status':
            if dateData['month'] < 10: dateData['month'] = '0%d'%dateData['month']
            if dateData['day'] < 10: dateData['day'] = '0%d'%dateData['day']
            date = '%(year)s-%(month)s-%(day)s %(hour)s:%(minute)s:%(second)s'%dateData
        elif DST:
            date = '%(week day)s %(month abbr)s %(day)s %(year)s %(hour)s:%(minute)s:%(second)s '\
                   'GMT-0700 (Pacific Daylight Time)'%dateData
        else:
            date = '%(week day)s %(month abbr)s %(day)s %(year)s %(hour)s:%(minute)s:%(second)s '\
                   'GMT-0800 (Pacific Standard Time)'%dateData
            # Footer
        #self.log.trace('Date: %s'%date)
        return date

    def convert_date_to_database_time(self, date):
        """ Convert a dictionary containing date data to database time value. """

        # Header
        # process variables
        tm_year = date['year']
        tm_mon = date['month']
        tm_mday = date['day']
        tm_hour = date['hour']
        tm_min = date['minute']
        tm_sec = date['second']
        tm_wday = date['week day']
        tm_yday = date['year day']
        tm_isdst = date['dst']
        # variable dictionary
        vars = date
        # declaration
        self.log.debug('''Converting date %(month)s %(day)s,
        %(year)s %(hour)s:%(minute)s:%(second)s to database time ...'''%vars)
        # Determine Database Time
        # build date/time tuple to convert
        dateTime = [tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst,]
        # convert date/time to seconds
        time = timegm(dateTime)
        # Footer
        self.log.debug('Time: %s'%str(time))
        # return time value
        return time

    def convert_string_to_time(self, s, silent=False):
        """ Convert vernacular string containing time value to database time
        """

        # Header
        # variable dictionary
        vars = {'string':s}
        # declaration
        if not silent:
            self.log.debug('Converting statement "%(string)s" to database time ...' % vars)
            # Convert to Time
        # determine if string is actually a time value already
        try:
            time = int(s)
            if not silent:
                self.log.trace('Time is %s.' % time)
            return time
        except Exception: time = None
        # determine if time is 'now'
        if str(s).lower().strip() == 'now': time = int(mktime(localtime()))-60
        # determine if time is past (contains 'ago'
        elif 'ago' in str(s).lower().strip():
            # split statement from 'ago'
            statement = str(s).lower().split('ago')
            # split remaining statement into numeral and measurement
            statement = str(statement[0]).split(' ')
            numeral = int(statement[0])
            measure = str(statement[1])
            if measure == 'second' or measure == 'seconds':
                time = int(mktime(localtime())) - numeral
            elif measure == 'minute' or measure == 'minutes':
                time = int(mktime(localtime())) - (numeral*60)
            elif measure == 'hour' or measure == 'hours':
                time = int(mktime(localtime())) - numeral*60*60
            elif measure == 'day' or measure == 'days':
                time = int(mktime(localtime())) - numeral*24*60*60
            elif measure == 'week' or measure == 'weeks':
                time = int(mktime(localtime())) - numeral*7*24*60*60
            elif measure == 'month' or measure == 'months':
                time = int(mktime(localtime())) - numeral*30*24*60*60
            elif measure == 'year' or measure == 'years':
                time = int(mktime(localtime())) - numeral*365*24*60*60
            else: self.log.error('Invalid time string including "ago" for conversion given.')
        elif 'from now' in str(s).lower().strip():
            # split statement from 'from now'
            statement = str(s).lower().split('from now')
            # split remaining statement into numeral and measurement
            statement = str(statement[0]).split(' ')
            numeral = int(statement[0])
            measure = str(statement[1])
            if measure == 'second' or measure == 'seconds':
                time = int(mktime(localtime())) + numeral
            elif measure == 'minute' or measure == 'minutes':
                time = int(mktime(localtime())) + (numeral*60)
            elif measure == 'hour' or measure == 'hours':
                time = int(mktime(localtime())) + numeral*60*60
            elif measure == 'day' or measure == 'days':
                time = int(mktime(localtime())) + numeral*24*60*60
            elif measure == 'week' or measure == 'weeks':
                time = int(mktime(localtime())) + numeral*7*24*60*60
            elif measure == 'month' or measure == 'months':
                time = int(mktime(localtime())) + numeral*30*24*60*60
            elif measure == 'year' or measure == 'years':
                time = int(mktime(localtime())) + numeral*365*24*60*60
            else: self.log.error('Invalid time string including "ago" for conversion given.')
        else: self.log.error('Invalid time string for conversion given.')
        # account for DST
        #if DST: time = int(time) - 3600
        # Footer
        if not silent:
            self.log.trace('Time is %s.'%time)
            # return time value
        return time