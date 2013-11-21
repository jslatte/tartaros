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

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
SYSCONFIG = SERVER['system configuration']
SYSCONFIG_PATH = SYSCONFIG['path']
SYSCONFIG_FIELDS = SYSCONFIG['fields']
SYSCONFIG_2_0_COLUMNS = SYSCONFIG['columns 2.0']
SYSCONFIG_3_2_COLUMNS = SYSCONFIG['columns 3.2']
SYSCONFIG_COLUMNS = SYSCONFIG['columns']
SYSCONFIG_DEFAULT_SETTINGS = SYSCONFIG['default settings']
SYSCONFIG_DEFAULT_DIAG_SETTINGS = SYSCONFIG['default diagnostics settings']
SYSCONFIG_DEFAULT_EMAIL_SETTINGS = SYSCONFIG['default email settings']
SYSCONFIG_DEFAULT_SS_SETTINGS = SYSCONFIG['default streaming server settings']
EMAIL_TEST = SERVER['email test']
EMAIL_TEST_PATH = EMAIL_TEST['path']
EMAIL_TEST_CFG = EMAIL_TEST['default configuration']
EMAIL_TEST_FIELDS = EMAIL_TEST['fields']
DB = HESTIA['database']
EVENTLOG = DB['event log']
DB_EVENTLOG_TABLE = EVENTLOG['table']
DB_EVENTLOG_FIELDS = EVENTLOG['fields']
DB_CLIPLOG = DB['clip log']
DB_CLIPLOG_TABLE = DB_CLIPLOG['table']
DB_CLIPLOG_FIELDS = DB_CLIPLOG['fields']
DB_GPS = DB['gps']
DB_GPS_TABLE = DB_GPS['table']
DB_GPS_FIELDS = DB_GPS['fields']
DB_GEOCLIP_REQUESTS = DB['geoclip requests']
DB_GEOCLIP_REQUESTS_TABLE = DB_GEOCLIP_REQUESTS['table']
DB_GEOCLIP_REQUESTS_FIELDS = DB_GEOCLIP_REQUESTS['fields']
DB_COC = DB['custody']
DB_COC_TABLE = DB_COC['table']
DB_COC_FIELDS = DB_COC['fields']

####################################################################################################
# System Configuration #############################################################################
####################################################################################################
####################################################################################################


class SystemConfiguration():
    """ Sub-library for ViM server system configuration.
    """

    def age_item_from_site_past_expiration(self, id, type, bin, site_id, testcase=None):
        """
        INPUT
            id: the entry id of the item to age.
            type: the type of entry being aged (i.e., event, clip, gps event, geoclip request).
            site id: the id of the site the item was downloaded from or with which it is associated.
            bin: the bin for which to return the timer.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Aging %s %s from site %s past expiration ..." % (type, id, site_id))
        result = {'successful': False, 'verified': False}

        try:
            # return bin timer for site
            expiration = self.return_bin_timer_for_site(site_id, bin)['bin timer']

            # age item past expiration
            aged = self.age_db_item(id, type, '%s days ago' % (int(expiration) + 1))['successful']

            if aged:
                self.log.trace("Aged %s %s from site %s past expiration." % (type, id, site_id))
                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="aging %s %s from site %s past expiration"
                                               % (type, id, site_id))

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def age_db_item(self, id, type, age):
        """ Age an entry in the database.
        INPUT:
            id: the entry id of the item to age.
            type: the type of entry being aged (i.e., event, clip, gps event, geoclip request).
            age: a string time indicating how much to age the item.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Aging %s %s to %s ..." % (type, id, age))
        result = {'successful':False}

        # import modules for table fields

        # determine less time
        newTime = int(self.utc.convert_string_to_time(age))
        lessTime = int(self.utc.convert_string_to_time('now')) - newTime
        # determine how to age field according to type, and build data dictionary to append to list
        type = type.lower()
        fieldsToAge = []
        if type == 'event':
            fieldsToAge.append(
                {'table':       DB_EVENTLOG_TABLE,
                 'field':       'start',
                 'cfg':         DB_EVENTLOG_FIELDS}
            )
        elif type == 'clip':
            fieldsToAge.append(
                {'table':       DB_CLIPLOG_TABLE,
                 'field':       'download time',
                 'cfg':         DB_CLIPLOG_FIELDS},
            )
        elif type == 'gps event':
            fieldsToAge.append(
                {'table':       DB_GPS_TABLE,
                 'field':       'date/time',
                 'cfg':         DB_GPS_FIELDS}
            )
        elif type == 'geoclip request':
            fieldsToAge.append(
                {'table':       DB_GEOCLIP_REQUESTS_TABLE,
                 'field':       'start time',
                 'cfg':         DB_GEOCLIP_REQUESTS_FIELDS}
            )
            fieldsToAge.append(
                {'table':       DB_GEOCLIP_REQUESTS_TABLE,
                 'field':       'end time',
                 'cfg':         DB_GEOCLIP_REQUESTS_FIELDS}
            )
        else:
            self.log.debug("Unknown entry type '%s' specified." % type)
        # age entry based on list of data dictionaries
        for fieldToAge in fieldsToAge:
            handle = self.db.db_handle
            table = fieldToAge['table']
            field = fieldToAge['cfg'][fieldToAge['field']]
            value = "%s - %s"%(field, lessTime)
            knownField = fieldToAge['cfg']['id']
            knownValue = id
            self.db.update_table_field_for_entry(handle, table, field, value, knownField, knownValue,
                True)
            # handle clip chain of custody updates
        if type == 'clip':
            statement = 'UPDATE %s SET %s = %s WHERE %s = %s'\
                        % (DB_COC_TABLE, DB_COC_FIELDS['time'],
                           newTime, DB_COC_FIELDS['clip id'], id)
            self.db.execute_SQL(self.db.db_handle, statement)
        result['successful'] = True
        # return
        return result

    def configure_vim_system_settings(self, testcase=None, settings=[]):
        """ Configure system setup settings for the ViM server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            settings: a list of field/value pairs [[field, value]] for configuring system settings.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Configuring ViM System Setup ...")
        result = {'successful': False, 'server response': None, 'verified': False,
                  'storage location': None}

        try:
            # define default data packet to send to server
            data = self.return_system_configuration()['settings']

            # for each item in settings, update data packet with associated value
            storage_loc = False
            for setting in settings:
                self.log.trace("Setting %s to %s ..." % (setting[0], setting[1]))
                data[SYSCONFIG_FIELDS[setting[0].lower()]] = setting[1]
                if setting[0].lower() == 'storage location': storage_loc = True

            # update bin timers (translate from days to seconds)
            self.log.trace("Updating bin timers ...")
            data[SYSCONFIG_FIELDS['elrt']] = int(data[SYSCONFIG_FIELDS['elrt']]) * 86400
            data[SYSCONFIG_FIELDS['tsd']]  = int(data[SYSCONFIG_FIELDS['tsd']]) * 86400
            data[SYSCONFIG_FIELDS['ltsd']] = int(data[SYSCONFIG_FIELDS['ltsd']]) * 86400
            data[SYSCONFIG_FIELDS['dgp']]  = int(data[SYSCONFIG_FIELDS['dgp']]) * 86400

            # make sure storage location included
            if not storage_loc: data[SYSCONFIG_FIELDS['storage location']] = self.storage_loc

            # remove blank parameters
            fields = data.keys()
            filtered_data = {}
            for field in fields:
                if data[field] != '' and data[field] is not None:
                    filtered_data[field] = data[field]

            # post request to server
            url = self.server_url + SYSCONFIG_PATH
            result['server response'] = self.post_http_request(url, filtered_data)['response']

            # verify configuration
            result['verified'] = self.verify_vim_system_configuration(settings=data)['verified']
            self.log.trace("System setup configured.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure system setup")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def determine_if_server_url_exists(self, testcase=None):
        """ Check VIM.properties file for server URL value.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            exists: whether the server url has been written to the properties file or not.
        """

        self.log.debug("Determining if server url exists in VIM.properties ...")
        result = {'successful': False, 'exists': False}

        try:
            # open VIM.properties
            path = self.properties_path
            f = open(path, 'r')
            # check each line for server URL field
            for line in f:
                if "VIM.url:".lower() in line.lower():
                    self.log.trace("Server URL found.")
                    result['exists'] = True
            f.close()
            if not result['exists']:
                self.log.trace("Server URL not found.")

            self.log.trace("Determined if server url exists.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine if server url exists")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def determine_system_configuration_map(self, testcase=None):
        """ Determine the system setup map to use when configuring system settings
        (based on version).
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            map: the system setup map to use.
        """

        self.log.debug("Determining system setup map for server version %s ..."
                       % self.release_version)
        result = {'successful': False, 'map': []}

        try:
            # local map variable to build
            map = []

            # check version
            version_nums = str(self.version).split('.')
            full_version = int(version_nums[0]) * 100000 + int(version_nums[1])\
                            * 10000 + int(version_nums[2]) * 1000 + int(version_nums[3])

            # check if server URL should be returned
            url_exists = self.determine_if_server_url_exists()['exists']

            # determine correct field names to use (based on version)
            if 2.0 <= float(self.release_version) < 3.1:
                self.log.trace("Server version %s uses 2.0 system setup mapping."
                               % str(self.release_version))
                for column in SYSCONFIG_2_0_COLUMNS:
                    map.append(column)
            elif 3.1 <= float(self.release_version) < 3.3:
                self.log.trace("Server version %s uses 3.1 system setup mapping."
                               % str(self.release_version))
                for column in SYSCONFIG_3_2_COLUMNS:
                    map.append(column)
            else:
                self.log.trace("Server version %s uses latest system setup mapping."
                                % str(self.release_version))
                for column in SYSCONFIG_COLUMNS:
                    map.append(column)

            # remove serverURL from field names if email has never been configured (3.1+)
            if not url_exists \
                and 3.1 <= float(self.release_version)\
                and SYSCONFIG_FIELDS['server url'] in map:
                self.log.trace("Email Notification never enabled, "
                               "updating server map for System Setup settings.")
                map.remove(SYSCONFIG_FIELDS['server url'])
            elif url_exists and 3.1 <= float(self.release_version) \
            and SYSCONFIG_FIELDS['server url'] not in map:
                self.log.trace("Email Notification enabled, "
                               "but server url not found in map for System Setup.")
                map2 = []
                map2.append(SYSCONFIG_FIELDS['server url'])
                for column in map:
                    map2.append(column)
                map = map2

            result['map'] = map
            self.log.trace("Determined system setup map for server version %s."
                           % self.release_version)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine system setup map")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def disable_diagnostics_reporting(self, testcase=None):
        """ Configure system setup to disable diagnostics reporting.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether diagnostic reporting was disabled or not.
        """

        self.log.debug("Disabling diagnostics reporting ...")
        result = {'successful': False, 'verified': False}

        try:
            # edit system setup to disable diagnostics reporting
            settings = [
                ['diagnostics enabled', 'false']
            ]
            result['verified'] = self.configure_vim_system_settings(settings=settings)['verified']

            if result['verified']:
                self.log.trace("Disabled diagnostic reporting.")
                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="disable diagnostic reporting")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def disable_streaming_server(self, testcase=None):
        """ Configure system setup to disable streaming server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether diagnostic reporting was disabled or not.
        """

        self.log.debug("Disabling streaming server ...")
        result = {'successful': False, 'verified': False}

        try:
            # edit system setup to disable streaming server
            settings = [
                ['live view enabled', 'false'],
                ['live view server', ''],
                ['live view user', ''],
                ['live view password', ''],
            ]
            result['verified'] = self.configure_vim_system_settings(settings=settings)['verified']

            if result['verified']:
                self.log.trace("Disabled streaming server.")
                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="disable streaming server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def disable_email_notification(self, testcase=None):
        """ Configure system setup to disable email notification.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            server response: the response from the server to the operation.
        """

        self.log.debug("Disabling email notification ...")
        result = {'successful': False, 'server response': None, 'verified': False}

        try:
            # edit system setup to disable email
            settings = [
                ['email enabled','false']
            ]
            result['server response'] =\
            returned = self.configure_vim_system_settings(settings=settings)
            result['verified'] = returned['verified']
            result['server response'] = returned['server response']

            self.log.trace("Email notification disabled.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="disable email notification")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def enable_diagnostics_reporting(self, testcase=None):
        """ Configure system setup to enable diagnostics reporting.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether diagnostic reporting was enabled or not.
        """

        self.log.debug("Enabling diagnostics reporting ...")
        result = {'successful': False, 'verified': False}

        try:
            # edit system setup to enable diagnostics reporting (with default settings)
            result['verified'] = \
            self.configure_vim_system_settings(settings=SYSCONFIG_DEFAULT_DIAG_SETTINGS)['verified']

            if result['verified']:
                self.log.trace("Enabled diagnostic reporting.")
                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="enable diagnostic reporting")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def enable_streaming_server(self, testcase=None):
        """ Configure system setup to enable streaming server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether diagnostic reporting was enabled or not.
        """

        self.log.debug("Enabling streaming server ...")
        result = {'successful': False, 'verified': False}

        try:
            # edit system setup to enable streaming server (with default settings)
            result['verified'] = \
                self.configure_vim_system_settings(settings=SYSCONFIG_DEFAULT_SS_SETTINGS)['verified']

            if result['verified']:
                self.log.trace("Enabled streaming server.")
                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="enable streaming server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def enable_email_notification(self, testcase=None):
        """ Configure system setup to enable email.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            server response: the response from the server to the operation.
            settings: any custom settings to configure in addition to enabling email notification.
        """

        self.log.debug("Enabling email notification ...")
        result = {'successful': False, 'server response': None, 'settings': [], 'verified': False}

        try:
            # edit system setup to enable email (with default settings)
            for setting in SYSCONFIG_DEFAULT_EMAIL_SETTINGS:
                result['settings'].append(setting)
            # failsafe for missing server url setting
            if ['server url','http://localhost'] not in result['settings']:
                result['settings'].append(['server url','http://localhost'])
            # enable email notifications
            data = self.configure_vim_system_settings(testcase=None, settings=result['settings'])
            result['server response'] = data['server response']
            result['verified'] = data['verified']
            if not result['verified']:
                self.log.error("Failed to enable email notification.")

            self.log.trace("Email Notification enabled.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="enable email notification")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_system_configuration(self, testcase=None):
        """ Return the current system configuration of the server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            settings: the current system settings.
        """

        self.log.debug("Returning current ViM system configuration ...")
        result = {'successful': False, 'settings': {}}

        try:
            # determine correct field names to use (based on version)
            columns = self.determine_system_configuration_map()['map']
            # query server for system setup settings
            url = self.server_url + SYSCONFIG_PATH
            response = self.query_server_table(url, columns)['response']
            # query should be only item in list returned
            if response != [] and response is not None and response != '' and response != ['']:
                self.log.trace("Current ViM system configuration:\t%s" % str(response))
                result['settings'] = response[0]
            else:
                self.log.trace("No ViM system configuration returned. "
                               "Assuming first time configuration default settings.")
                fields = SYSCONFIG_DEFAULT_SETTINGS.keys()
                values = SYSCONFIG_DEFAULT_SETTINGS.values()
                # rebuild settings dict
                for i in range(0, len(fields)):
                    field = fields[i]
                    value = values[i]
                    result['settings'][field] = value

            self.log.trace("Returned current ViM system configuration.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return current ViM system configuration")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def test_email_settings(self, testcase=None, send_to='vim@avt-usa.net', settings=None):
        """ Test email settings.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            send to: the account that will be used to test by sending an email to it.
            settings: a list of field/value pairs for how to configure test.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Testing email settings ...")
        result = {'successful': False, 'verified':False}

        try:
            # use default settings if none given
            if settings is None: settings = EMAIL_TEST_CFG
            # define data packet
            # ... clean up default email settings (remove 'email enabled')
            for setting in settings:
                if setting[0] == 'email enabled':
                    del settings[settings.index(setting)]
            # ... translate list into data packet
            data = {}
            for setting in settings:
                data[EMAIL_TEST_FIELDS[setting[0]]] = setting[1]
                # ... update data packet with 'send to'
            data[EMAIL_TEST_FIELDS['email to']] = send_to
            #log("%s"%str(data))
            # define url
            url = self.server_url + EMAIL_TEST_PATH
            # post request to server
            response = self.post_http_request(url, data)['response']
            # check response
            if response.lower() == 'ok': result['verified'] = True
            elif response.lower() != 'test failed':
                self.log.warn("Connection test failed, but response was %s." % response)

            self.log.trace("Tested email settings.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="test email settings")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_low_disk_space_warning(self, server_response, low_range, high_range, testcase=None):
        """
        INPUT
            server response: the string response from the server received.
            low range: the lower range limit (>) that the disk size should be in for the warning.
            high range: the higher range limit (<) that the disk size should be in for the warning.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying low disk space warning for '%s' response ..." % server_response)
        result = {'successful': False, 'verified': False}

        try:
            # check response for disk space warning format
            correctFormat = False
            formatIdentifier = 'gb on '
            if formatIdentifier in server_response.lower():
                correctFormat = True
            else:
                self.log.warn("Invalid format for given server response.")

            if correctFormat:

                # parse server response for disk size
                parsedResponse = server_response.lower().split(formatIdentifier)
                diskSize = int(parsedResponse[0].strip())

                # check that disk size falls in expected range
                if low_range < diskSize < high_range:
                    self.log.trace("Verified low disk space warning.")
                    result['verified'] = True
                else:
                    self.log.warn("Failed to verify low disk space warning. "
                                   "Disk space %s did not fall into %s to %s")

            self.log.trace("Verified low disk space warning.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify low disk space warning for '%s' response"
                                               % server_response)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_vim_system_configuration(self, testcase=None, settings=[]):
        """ Verify system setup settings for the ViM server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            settings: a list of field/value pairs [[field, value]] for configuring system settings.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying ViM System Setup ...")
        result = {'successful': False, 'verified': False}

        try:
            # determine correct field names to use
            columns = self.determine_system_configuration_map()['map']

            # query server for system setup settings
            url = self.server_url + SYSCONFIG_PATH
            response = self.query_server_table(url, columns)['response']

            # query should be only item in list returned
            try: response = response[0]
            except BaseException:
                self.log.warn("No configuration returned.")

            # update bin timers (translate from days to seconds)
            self.log.trace("Updating bin timers ...")
            response[SYSCONFIG_FIELDS['elrt']] = int(response[SYSCONFIG_FIELDS['elrt']]) * 86400
            response[SYSCONFIG_FIELDS['tsd']]  = int(response[SYSCONFIG_FIELDS['tsd']]) * 86400
            response[SYSCONFIG_FIELDS['ltsd']] = int(response[SYSCONFIG_FIELDS['ltsd']]) * 86400
            response[SYSCONFIG_FIELDS['dgp']]  = int(response[SYSCONFIG_FIELDS['dgp']]) * 86400

            # convert settings dict to list
            try:
                fields = settings.keys()
                values = settings.values()
                settings = []
                i = 0
                for i in range(len(fields)):
                    settings.append([fields[i], values[i]])
            except BaseException:
                # dealing with list, pass
                pass

            # for each item in settings, very against server query response
            invalids = 0
            for setting in settings:
                self.log.trace("Checking '%(field)s' ..." % {'field': setting[0]})
                # get the value for the setting field being checked
                serverValue = response.get(setting[0])
                # check against expected value
                if str(serverValue) != str(setting[1]):
                    self.log.trace("Expected '%(field)s' to be '%(expected)s', but was '%(actual)s'."
                        %{'field':setting[0], 'expected': setting[1], 'actual': serverValue})
                    invalids += 1

            # if invalid values not found, return true
            if invalids == 0:
                result['verified'] = True
                self.log.trace("Verified ViM system setup settings.")
            else:
                self.log.warn("Failed to verify ViM system setup settings.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify ViM system setup")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result