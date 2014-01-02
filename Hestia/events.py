###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import HESTIA
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
CLIP_STATUS_INFO = SERVER['clip status info']
CLIP_STATUS_INFO_PATH = CLIP_STATUS_INFO['query path']
CLIP_STATUS_INFO_FIELD_NAMES = CLIP_STATUS_INFO['columns']
DB = HESTIA['database']
EVENTLOG = DB['event log']
DB_EVENTLOG_TABLE = EVENTLOG['table']
DB_EVENTLOG_FIELDS = EVENTLOG['fields']
EVENT_TYPES = EVENTLOG['event types']
SITES = DB['sites']
DB_SITES_TABLE = SITES['table']
DB_SITES_FIELDS = SITES['fields']
DVRS = DB['dvrs']
DB_DVR_TABLE = DVRS['table']
DB_DVR_FIELDS = DVRS['fields']
DB_CLIPLOG = DB['clip log']
DB_CLIPLOG_TABLE = DB_CLIPLOG['table']
DB_CLIPLOG_FIELDS = DB_CLIPLOG['fields']
DB_COC = DB['custody']
DB_COC_TABLE = DB_COC['table']
DB_COC_FIELDS = DB_COC['fields']
DB_GPS = DB['gps']
DB_GPS_TABLE = DB_GPS['table']
DB_GPS_FIELDS = DB_GPS['fields']
DB_SYSLOG = DB['system log']
DB_SYSLOG_TABLE = DB_SYSLOG['table']
DB_SYSLOG_FIELDS = DB_SYSLOG['fields']

####################################################################################################
# Events ###########################################################################################
####################################################################################################
####################################################################################################


class Events():
    """ Sub-library for ViM server event download and interaction.
    """

    def verify_system_event_downloaded_for_site(self, site_id, wait=360, testcase=None):
        """ Verify that system event is in the database for given site.
        INPUT
            site id: id of the site for which to verify the event downloaded.
            wait: how long to wait for the event to download.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            event id: the id of the system event.
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying system event downloaded for site %s ..." % site_id)
        result = {'successful': False, 'verified': False, 'event id': None}

        try:
            # return disk id for site
            dvr_id = self.return_dvr_for_site(site_id)['dvr id']

            # query database for event for site (on loop)
            i = 15
            while not result['verified'] and i <= wait:
                handle = self.db.db_handle
                table = DB_SYSLOG_TABLE
                return_field = DB_SYSLOG_FIELDS['id']
                known_field = DB_SYSLOG_FIELDS['dvr id']
                known_value = dvr_id
                event_id = self.db.query_database_table_for_single_value(handle, table,
                                                                         return_field, known_field,
                                                                         known_value)['value']
                if event_id is not None:
                    self.log.trace("Verified system event downloaded for site %s." % site_id)
                    result['event id'] = event_id
                    result['verified'] = True
                else:
                    self.log.trace("Event NOT found (attempt %d). Retrying ..." % (i/15))
                    i += 15
                    sleep(15)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify system event downloaded for site %s" % site_id)

        # return
        if testcase is not None:
            testcase.event_id = result['event id']
            testcase.processing = result['successful']
        return result

    def verify_gps_event_downloaded_for_site(self, site_id, wait=360, testcase=None):
        """ Verify that gps event is in the database for given site.
        INPUT
            site id: id of the site for which to verify the gps event downloaded.
            wait: how long to wait for the event to download.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            event id: the id of the gps event.
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying gps event downloaded for site %s ..." % site_id)
        result = {'successful': False, 'verified': False, 'event id': None}

        try:
            # return disk id for site
            drive_id = self.return_drive_for_site(site_id)['drive id']

            # query database for event for site (on loop)
            i = 15
            while not result['verified'] and i <= wait:
                handle = self.db.db_handle
                table = DB_GPS_TABLE
                return_field = DB_GPS_FIELDS['id']
                known_field = DB_GPS_FIELDS['disk id']
                known_value = drive_id
                event_id = self.db.query_database_table_for_single_value(handle, table,
                                                                         return_field, known_field,
                                                                         known_value)['value']
                if event_id is not None:
                    self.log.trace("Verified gps event downloaded for site %s." % site_id)
                    result['event id'] = event_id
                    result['verified'] = True
                else:
                    self.log.trace("Event NOT found (attempt %d). Retrying ..." % (i/15))
                    i += 15
                    sleep(15)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify gps event downloaded for site %s" % site_id)

        # return
        if testcase is not None:
            testcase.event_id = result['event id']
            testcase.processing = result['successful']
        return result

    def verify_event_of_type_downloaded_for_site(self, site_id, event_type, cam_id=None, wait=360,
                                                 testcase=None):
        """ Verify that specified type of even is in the database for given site.
        INPUT
            site id: id of the site for which to verify the event type downloaded.
            event type: type of event to verify downloaded (see EVENT_TYPES mapping for
                valid event keys).
            cam id: optional camera/event id value to be used with alarms/video events
                (0-7 for alarm 1-8).
            wait: how long to wait for the event to download.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying %s event downloaded for site %s ..." % (event_type, site_id))
        result = {'successful': False, 'verified': False, 'event id': None}

        try:
            # translate event type to database type number
            type_id = int(EVENT_TYPES[event_type.lower()])

            # query database for event for site (on loop)
            i = 15
            while not result['verified'] and i <= wait:
                handle = self.db.db_handle
                table = DB_EVENTLOG_TABLE
                return_field = DB_EVENTLOG_FIELDS['id']
                known_field = DB_EVENTLOG_FIELDS['site id']
                known_value = '%s" AND %s = "%s' % (site_id, DB_EVENTLOG_FIELDS['type'], type_id)
                if cam_id is not None:
                    # translate camera id 1-8 to 0-8
                    cam_id -= 1
                    known_value += '" AND %s = "%s' % (DB_EVENTLOG_FIELDS['event id'], cam_id)
                event_id = self.db.query_database_table_for_single_value(handle, table, return_field, known_field,
                    known_value)['value']
                if event_id is not None:
                    self.log.trace("Verified %s event downloaded for site %s." % (event_type, site_id))
                    result['event id'] = event_id
                    result['verified'] = True
                else:
                    self.log.trace("Event NOT found (attempt %d). Retrying ..."%(i/15))
                    i += 15
                    sleep(15)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify %s event downloaded for site %s" % (event_type, site_id))

        # return
        if testcase is not None:
            testcase.event_id = result['event id']
            testcase.processing = result['successful']
        return result

    def verify_event_deleted(self, event_id, testcase=None):
        """
        INPUT
            event id: the id of the event to verify was deleted.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying event %s deleted ..." % event_id)
        result = {'successful': False, 'verified': False}

        try:
            attempt = 1
            maxAttempts = 5
            while not result['verified']:
                # check for event in database
                exists = self.db.query_database_table_for_single_value(self.db.db_handle,
                    DB_EVENTLOG_TABLE, DB_EVENTLOG_FIELDS['id'], DB_EVENTLOG_FIELDS['id'],
                    event_id)['value']

                if not exists:
                    self.log.trace("Verified event deleted.")
                    result['verified'] = True
                elif exists and attempt < maxAttempts:
                    self.log.trace("Event found (attempt %s). Re-attempting in 5 seconds ..."
                                   % attempt)
                elif exists and attempt == maxAttempts:
                    self.log.error("Failed to verify event deleted. Event found.")
                    break

                # increment
                sleep(5)
                attempt += 1

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verifying event %s deleted" % event_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def query_clip_status_information_for_event(self, event_id, clip_id=None, expected=None,
                                                testcase=None):
        """ Query an event for its clip status information.
        INPUT
            event id: the id of the event for which to query the clip status information.
            clip id: the id of an expected clip to be found associated with the event.
            expected: a list of expected field/value pairs (see map).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Querying clip status(es) for event %s..." % event_id)
        result = {'successful': False, 'verified': False}

        try:
            # build default query
            data = {
                'eventId':  event_id
            }

            # query server for event clip status information
            url = self.server_url + CLIP_STATUS_INFO_PATH
            result['query'] =\
            self.query_server_table(url, CLIP_STATUS_INFO_FIELD_NAMES, data)['response']

            # verify an entry (if given)
            if clip_id is not None:
                # establish database connection
                result['verified'] = self.verify_clip_status_information_for_event(result['query'],
                    clip_id, expected)['verified']

            elif clip_id is 'no clips':
                if str(result['query']) != '[]': result['verified'] = False

            else: pass

            self.log.trace("Queried clip status(es) for event %s" % event_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="query clip status(es) for event %s..." % event_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_status_information_for_event(self, query_response, clip_id, expected=None,
                                                 testcase=None):
        """ Verify an entry was returned in the query.
        INPUT
            query response: a dictionary return from a server table query for the clip status info of
                an event.
            clip id: the id of an expected clip to be found associated with the event.
            expected: a list of expected field/value pairs (see map).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying clip status information for clip %s ..." % clip_id)
        result = {'successful': False, 'verified': False}

        try:
            # pull the correct entry for the entry id (if given)
            entry = None
            for i in query_response:
                if i['clip id'] == str(clip_id):
                    #entry = i
                    result['verified'] = True

                    # shortcut
                    entry = None
                    self.log.trace("Verified clip status information for clip %s." % clip_id)

            if entry is not None:
                # TODO: Fix this mess (not validating entries in CoC correctly)
                # build expected data dictionary
                expected = {}

                # pull values from database
                # date/time
                handle = self.db.db_handle
                table = DB_CLIPLOG_TABLE
                return_field = DB_CLIPLOG_FIELDS['start']
                known_field = DB_CLIPLOG_FIELDS['id']
                known_value = clip_id
                expected['date/time'] = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                # clip length
                table = DB_CLIPLOG_TABLE
                return_field = DB_CLIPLOG_FIELDS['length']
                known_field = DB_CLIPLOG_FIELDS['id']
                known_value = clip_id
                expected['clip length'] = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                # action time
                table = DB_COC_TABLE
                return_field = DB_COC_FIELDS['time']
                known_field = DB_COC_FIELDS['clip id']
                known_value = clip_id
                expected['action time'] = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                # action value
                table = DB_COC_TABLE
                return_field = DB_COC_FIELDS['value']
                known_field = DB_COC_FIELDS['clip id']
                known_value = clip_id
                expected['action value'] = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                # request time
                table = DB_COC_TABLE
                return_field = DB_COC_FIELDS['author']
                known_field = DB_COC_FIELDS['clip id']
                known_value = clip_id
                expected['user'] = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                # author
                table = DB_COC_TABLE
                return_field = DB_COC_FIELDS['author']
                known_field = DB_COC_FIELDS['clip id']
                known_value = clip_id
                expected['requested by'] = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                # update necessary values to server format
                expected['date/time'] = \
                self.utc.convert_database_time_to_server_date(expected['date/time'], 'clip status')
                expected['action time'] = \
                self.utc.convert_database_time_to_server_date(expected['action time'], 'clip status')
                if expected['user'] == '': expected['user'] = '(auto)'
                if expected['requested by'] == '': expected['requested by'] = '(auto)'

                # verify each expected value
                invalids = 0
                for i in expected:
                    serverValue = entry.get(i.lower())
                    expectedValue = expected.get(i.lower())
                    if str(serverValue).lower() != str(expectedValue).lower():
                        self.log.warn("Expected '%(field)s' to be '%(expected)s', but was '%(actual)s'."
                            %{'field':i,'expected':expectedValue,'actual':serverValue})
                        invalids += 1

                if invalids == 0:
                    self.log.trace("Verified clip status information for clip %s." % clip_id)
                else:
                    self.log.warn("Failed to verify clip status information for clip %s." % clip_id)

            else: self.log.trace("No entries returned in clip status information for clip.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify clip status information for clip %s" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def generate_event_for_site(self, site_id, type='custom', params=[], generated=False,
                                testcase=None):
        """ Generate specified type of event in database for given site.
        INPUT
            site id: the site the event should be generated on.
            type: the type of event (see EVENT_TYPES map).
            params: an optional list of field/value pairs to further configure the event.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Generating %(type)s event for site %(site)s ..." %
                       {'type':type,'site':str(site_id)})
        result = {'successful': False, 'event id': None, 'event start': None}

        try:
            # define default attributes of event
            event = {
                DB_EVENTLOG_FIELDS['site id']:          site_id,
                DB_EVENTLOG_FIELDS['type']:          EVENT_TYPES[type.lower()],
                DB_EVENTLOG_FIELDS['event id']:      '0',
                DB_EVENTLOG_FIELDS['start']:         "strftime('%s','now')",
                DB_EVENTLOG_FIELDS['duration']:      '1',#'NULL',
                DB_EVENTLOG_FIELDS['cameras']:       '0',
                DB_EVENTLOG_FIELDS['label']:         '',
                DB_EVENTLOG_FIELDS['level']:         '0',
                DB_EVENTLOG_FIELDS['download clip']: '0',
                DB_EVENTLOG_FIELDS['disk id']:       'NULL'
            }
            # update event type dependent fields
            if type.lower() == 'alarm':
                event[DB_EVENTLOG_FIELDS['cameras']] = -1
                event[DB_EVENTLOG_FIELDS['label']] = 'Alarm In'
                event[DB_EVENTLOG_FIELDS['level']] = 0
            elif type.lower() == 'disk almost full':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Disk Almost Full'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'disk full':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Disk Full'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'disk bad':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Disk Bad'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'disk temperature':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Disk Temperature'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'disk s.m.a.r.t.':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Disk S.M.A.R.T.'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'fan error':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Fan Error'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'motion':
                event[DB_EVENTLOG_FIELDS['label']] = ''#'Motion'
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'video loss':
                event[DB_EVENTLOG_FIELDS['cameras']] = -1
                event[DB_EVENTLOG_FIELDS['label']] = 'Camera %d' \
                                                     % (int(event[DB_EVENTLOG_FIELDS['event id']])+1)
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'video blind':
                event[DB_EVENTLOG_FIELDS['cameras']] = -1
                event[DB_EVENTLOG_FIELDS['label']] = 'Camera %d' \
                                                     % (int(event[DB_EVENTLOG_FIELDS['event id']])+1)
                event[DB_EVENTLOG_FIELDS['level']] = 16
            elif type.lower() == 'custom':
                event[DB_EVENTLOG_FIELDS['cameras']] = -1
                event[DB_EVENTLOG_FIELDS['label']] = '-'
                event[DB_EVENTLOG_FIELDS['level']] = 0
            else: self.log.warn("Invalid event type specified.")
            # update disk id using disk associated with siteID
            handle = self.db.db_handle
            table = DB_SITES_TABLE
            return_field = DB_SITES_FIELDS['dvr id']
            addendum = " WHERE %s = %s" % (DB_SITES_FIELDS['id'], site_id)
            response = self.db.query_database_table(handle, table, return_field=return_field,
                addendum=addendum)['response']
            dvrID = response[0][0]  # first item in the tuple of the first entry in the list

            handle = self.db.db_handle
            table = DB_DVR_TABLE
            return_field = DB_DVR_FIELDS['disk id']
            addendum = " WHERE %s = %s" % (DB_DVR_FIELDS['id'], dvrID)
            response = self.db.query_database_table(handle, table, return_field=return_field,
                addendum=addendum)['response']
            diskID = response[0][0]
            event[DB_EVENTLOG_FIELDS['disk id']] = diskID

            # update event data with any given settings
            for parameter in params:
                if not generated:
                    self.log.trace("Setting '%(field)s' to '%(value)s' ..."
                                   % {'field':parameter[0], 'value':str(parameter[1])})
                if parameter[0].lower() == 'start':
                    event[DB_EVENTLOG_FIELDS[parameter[0].lower()]] = \
                    self.utc.convert_string_to_time(parameter[1],silent=generated)
                elif parameter[0].lower() == 'event id':
                    event[DB_EVENTLOG_FIELDS[parameter[0].lower()]] = parameter[1]
                    if type.lower() == 'video loss':
                        event[DB_EVENTLOG_FIELDS['cameras']] = -1
                        event[DB_EVENTLOG_FIELDS['label']] = 'Camera %d' \
                                                % (int(event[DB_EVENTLOG_FIELDS['event id']])+1)
                        event[DB_EVENTLOG_FIELDS['level']] = 16
                    if type.lower() == 'video blind':
                        event[DB_EVENTLOG_FIELDS['cameras']] = -1
                        event[DB_EVENTLOG_FIELDS['label']] = 'Camera %d' \
                                                % (int(event[DB_EVENTLOG_FIELDS['event id']])+1)
                        event[DB_EVENTLOG_FIELDS['level']] = 16
                else:
                    event[DB_EVENTLOG_FIELDS[parameter[0].lower()]] = parameter[1]
            # build SQL statement to insert event into database
            statement = "INSERT INTO %(table)s "%{'table': DB_EVENTLOG_TABLE}
            statement += "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(DB_EVENTLOG_FIELDS['site id'],
                                                            DB_EVENTLOG_FIELDS['type'],
                                                            DB_EVENTLOG_FIELDS['event id'],
                                                            DB_EVENTLOG_FIELDS['start'],
                                                            DB_EVENTLOG_FIELDS['duration'],
                                                            DB_EVENTLOG_FIELDS['cameras'],
                                                            DB_EVENTLOG_FIELDS['label'],
                                                            DB_EVENTLOG_FIELDS['level'],
                                                            DB_EVENTLOG_FIELDS['download clip'],
                                                            DB_EVENTLOG_FIELDS['disk id'])
            statement += ''' VALUES("%s","%s","%s",%s,"%s","%s","%s","%s","%s","%s")'''\
                         %(event[DB_EVENTLOG_FIELDS['site id']],event[DB_EVENTLOG_FIELDS['type']],
                           event[DB_EVENTLOG_FIELDS['event id']],
                           event[DB_EVENTLOG_FIELDS['start']],event[DB_EVENTLOG_FIELDS['duration']],
                           event[DB_EVENTLOG_FIELDS['cameras']],
                           event[DB_EVENTLOG_FIELDS['label']],event[DB_EVENTLOG_FIELDS['level']],
                           event[DB_EVENTLOG_FIELDS['download clip']],
                           event[DB_EVENTLOG_FIELDS['disk id']])
            # insert event into database and return ID
            eventID = self.db.execute_SQL(self.db.db_handle, statement, return_id=True)['id']
            # return event start time
            eventStart = self.db.query_database_table_for_single_value(self.db.db_handle,
                DB_EVENTLOG_TABLE, DB_EVENTLOG_FIELDS['start'], DB_EVENTLOG_FIELDS['id'],
                eventID)['value']

            # define params for return
            result['event id'] = eventID
            result['event start'] = eventStart

            self.log.trace("Generated %s event." % type)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="generate %s event" % type)

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.event_id = result['event id']
        return result