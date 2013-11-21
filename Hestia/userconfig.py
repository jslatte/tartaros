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
from string import splitfields, atoi
from datetime import datetime

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
USERCON = SERVER['user configuration']
USERCON_QUERY_PATH = USERCON['query path']
USERCON_MODIFY_PATH = USERCON['modify path']
USERCON_FIELDS = USERCON['fields']
USERCON_COLUMNS = USERCON['columns']
LEVEL_TO_GROUPID = USERCON['level to group id']
USERCON_DELETE_PATH = USERCON['delete path']
PASSWORD = SERVER['password modification']
PASSWORD_MODIFY_PATH = PASSWORD['modify path']
PASSWORD_FIELDS = PASSWORD['fields']

####################################################################################################
# User Configuration ###############################################################################
####################################################################################################
####################################################################################################


class UserConfiguration():
    """ Sub-library for ViM server user configuration.
    """

    def add_user_level_user_for_test(self, level, settings=[], testcase=None):
        """ Add a user of specified user level for testing.
        INPUT
            level: the user level of the user (see USERS['level to group id'] map for valid values.
            settings: an optional list of field/value list pairs (i.e., [['user name','user']])
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            user name: the user name of the user created.
            password: the password of the user created
            settings: the settings used to configure the user.
        """

        self.log.debug("Adding user for test ...")
        result = {'successful': False, 'verified':False, 'user name':None,
                  'password':None, 'settings':[]}

        try:
            # define default settings for user
            userName = level.lower()
            password = 'password'
            userLevel = level.lower()
            parameters = [
                ['user name',userName],
                ['password',password],
                ['user level',userLevel]
            ]
            # update settings (if any additional given)
            for setting in settings:
                parameters.append(setting)
            # add user
            returned = self.configure_user(parameters)
            # verify user
            verified = returned['verified']
            if not verified: self.log.error("Failed to add user.")
            # define return variables
            for parameter in parameters:
                if parameter[0].lower() == 'user name': result['user name'] = parameter[1]
                elif parameter[0].lower() == 'password': result['password'] = parameter[1]
            result['verified'] = verified
            result['settings'] = parameters
            # define test variables
            if testcase is not None:
                testcase.user_name = result['user name']
                testcase.password = result['password']
                testcase.user_settings = result['settings']

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="adding user for test")

        # return
        if testcase is not None:
            testcase.user_name = result['user name']
            testcase.password = result['password']
            testcase.processing = result['successful']
        return result

    def configure_user(self, user_name='user', settings=[], testcase=None):
        """ Configure a user.
        INPUT
            settings: a list pairing fields with expected values.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            user name: name of the user added.
            password: password of the user added.
        """

        self.log.debug("Configuring a user ...")
        result = {'successful': False, 'verified': False, 'user name': None, 'password': None}

        try:
            # define default data packet to send to server
            data = {
                USERCON_FIELDS['user name']:         user_name,
                USERCON_FIELDS['first name']:        '',
                USERCON_FIELDS['last name']:         '',
                USERCON_FIELDS['user level']:        3,
                USERCON_FIELDS['email address']:     '',
                USERCON_FIELDS['notification time']: -1,
                USERCON_FIELDS['group id']:          3
            }
            # for each item in settings, update data packet with associated value
            for setting in settings:
                self.log.trace("Setting '%(field)s' to '%(value)s' ..."%{'field':setting[0],
                                                'value':str(setting[1])})
                # translate value if necessary
                if USERCON_FIELDS[setting[0].lower()] == USERCON_FIELDS['user level']:
                    val = LEVEL_TO_GROUPID[setting[1].lower()]
                    data[USERCON_FIELDS['group id']] = val # group id should be the same as user level
                elif USERCON_FIELDS[setting[0].lower()] == USERCON_FIELDS['notification time']:
                    val = self.calculate_notification_time(setting[1])['notification time']
                elif USERCON_FIELDS[setting[0].lower()] == USERCON_FIELDS['password']:
                    val = setting[1]
                    # password verification same as password by default
                    data[USERCON_FIELDS['verification']] = setting[1]
                    result['password'] = setting[1]
                else: val = setting[1]
                # update value
                data[USERCON_FIELDS[setting[0].lower()]] = val
                # check for mandatory fields
            if USERCON_FIELDS['password'] not in data:
                self.log.warn("No password specified.")
                #data[USERCON_FIELDS['password']] = 'password'
                #data[USERCON_FIELDS['verification']] = 'password'
            # post request to server
            url = self.server_url + USERCON_MODIFY_PATH
            response = self.post_http_request(url, data)['response']
            # make sure a user name is in settings (else add the default)
            found = False
            for setting in settings:
                if str(setting[0]) == 'user name': found = True
            if not found: settings.append(['user name','user'])
            # verify user configuration
            returned = self.verify_user_configuration(settings,response)
            result['server response'] = response
            result['verified'] = returned['verified']

            # update global variables
            result['user name'] = user_name

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure user")

        # return
        if testcase is not None:
            testcase.user_name = result['user name']
            if result['password'] is not None: testcase.password = result['password']
            testcase.processing = result['successful']
        return result

    def verify_user_configuration(self, settings, serverResponse=None, testcase=None):
        """ Verify user configuration.
        INPUT
            settings: a list pairing fields with expected values.
            server response: the response of the server to configuring user to be evaluated.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying user configuration ...")
        result = {'successful': False, 'verified':False}

        try:
            # check server response (if given)
            if str(serverResponse) == 'Add user failed':
                self.log.error("Add user failed.")
            else:
                # query server for users
                url = self.server_url + USERCON_QUERY_PATH
                response = self.query_server_table(url, USERCON_COLUMNS)['response']
                # determine user name from given settings
                userName = None
                for setting in settings:
                    if str(setting[0]) == 'user name': userName = setting[1]
                if userName is None:
                    self.log.error("Did not find user name in given settings.")

                # determine correct user in query response using name
                entry = None
                try:
                    for user in response:
                        if user['user name'] == userName: entry = user
                    if entry is None:
                        self.log.error("Did not find user in server query response.")
                except BaseException,e:
                    self.log.error("%s" % str(e))
                    settings = []
                # for each item in settings, verify against server query response
                invalids = False
                for setting in settings:
                    self.log.trace("Checking '%(field)s' ..."%{'field':setting[0]})
                    # get the value for the setting field being checked
                    serverValue = entry.get(setting[0].lower())
                    # translate expected value as needed to match server value format
                    if setting[0].lower() == 'user level':
                        expected = LEVEL_TO_GROUPID[setting[1].lower()]
                    elif setting[0].lower() == 'notification time':
                        expected = self.calculate_notification_time(setting[1])['notification time']
                    elif setting[0].lower() == 'password' or setting[0].lower() == 'verification':
                        continue # don't check password as no server value is returned (security reasons)
                    else: expected = setting[1]
                    # check against expected value
                    if str(serverValue) != str(expected):
                        self.log.error("Expected '%(field)s' to be '%(expected)s', but was '%(actual)s'."
                            %{'field':setting[0],'expected':expected,'actual':serverValue})
                        invalids = True
                if not invalids:
                    self.log.trace('Verified user added')
                    result['verified'] = True
                else:
                    self.log.warn("Failed to verify user added.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify user added")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def calculate_notification_time(self, time, testcase=None):
        """ Converts time values (according to ViM user interface options, 00:00 format)
            from string input to total number of seconds to return for SendAt variable.
        INPUT
            time: the time to translate into a notification time (db time?)
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            notification time: the time returned in notification time format.
        """

        self.log.debug("Calculating notification time ...")
        result = {'successful': False, 'notification time': None}

        try:
            if str(time).lower() == 'never':
                # sendAt should equal -1 if set to Never
                sendAt = -1
            else:
                # Convert time string to array containing hours (00) from before ':'
                # and minutes (00) from after ':'
                time = splitfields(time, ':')
                # Calculate total number of seconds by converting hours and minutes
                # from atime array into integers and multiplying by number of seconds
                # per unit
                totalseconds = (atoi(time[0])*3600)+(atoi(time[1])*60)
                # sendAt should equal total number of seconds
                sendAt = totalseconds
            result['notification time'] = sendAt

            self.log.trace("Calculated notification time.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="calculate notification time")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def determine_soonest_notification_time(self, testcase=None):
        """ Determine the soonest notification time to 'now'.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            time: the returned time in '00:00' notification format.
        """

        self.log.debug("Determining soonest notification time ...")
        result = {'successful': False, 'time': 'never'}

        try:
            # get current system time
            systemTime = datetime.now()
            self.log.trace("Current system time:\t%s"%str(systemTime))
            # determine soonest time for notification
            hour = int(systemTime.hour)
            minute = int(systemTime.minute)
            if minute is 59 or minute is 0:
                hour += 1
                minute = 15
            elif 45 < minute < 59:
                hour += 1
                minute = 0
            elif 30 <= minute < 45: minute = 45
            elif 15 <= minute < 30: minute = 30
            elif  0 <= minute < 15: minute = 15
            # parse into hours and minutes
            if hour is 0 or hour < 10: hour = "0%d"%hour
            else: hour = str(hour)
            if minute is 0 or minute < 10: minute = "0%d"%minute
            result['time'] = "%s:%s"%(hour, minute)
            self.log.trace("Soonest notification time:\t%s"%result['time'])

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine soonest notification time")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def change_user_password(self, oldPassword, newPassword, testcase=None):
        """ Change the current user's password.
        INPUT
            old password: the user's old password.
            new password: the new password for the user.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Changing password for current user from '%s' to '%s' ...")
        result = {'successful': False, 'verified':False}

        try:
            # build data packet
            data = {
                PASSWORD_FIELDS['account']:                     '',
                PASSWORD_FIELDS['new password']:                newPassword,
                PASSWORD_FIELDS['new password verification']:   newPassword,
                PASSWORD_FIELDS['old password']:                oldPassword
            }
            # post request to server
            url = self.server_url + PASSWORD_MODIFY_PATH
            response = self.post_http_request(url,data)['response']
            # verify password reset successful
            if response.lower() == 'ok':
                self.log.trace("Verified password change was successful.")
                result['verified'] = True
            else:
                self.log.warn("Failed to verify password change was successful.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="change user password")

        # return
        if testcase is not None:
            testcase.password = newPassword
            testcase.processing = result['successful']
        return result

    def reset_user_password(self, userName, newPassword, testcase=None):
        """ Reset a user's password.
        INPUT
            user name: the name of the user to change the password for.
            new password: the new password to use.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Reseting password for user '%s' to '%s' ..."%(userName,newPassword))
        result = {'successful': False, 'verified':False}

        try:
            # build data packet
            data = {
                PASSWORD_FIELDS['account']:                     userName,
                PASSWORD_FIELDS['new password']:                newPassword,
                PASSWORD_FIELDS['new password verification']:   newPassword,
            }
            # post request to server
            url = self.server_url + PASSWORD_MODIFY_PATH
            response = self.post_http_request(url,data)['response']
            # verify password reset successful
            if response.lower() == 'ok':
                self.log.trace("Verified password reset was successful.")
                result['verified'] = True
            else:
                self.log.warn("Failed to verify password reset was successful.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="reset user password")

        # return
        if testcase is not None:
            testcase.password = newPassword
            testcase.processing = result['successful']
        return result

    def delete_user(self,userName, testcase=None):
        """ Delete a user.
        INPUT
            user name: the user name of the user to delete.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Deleting user ...")
        result = {'successful': False, 'verified':False}

        try:
            # make delete request
            url = self.server_url + USERCON_DELETE_PATH % {'user name': userName}
            response = self.make_delete_request_to_server(url)['response']
            # verify user was deleted
            verified = self.verify_user_was_deleted(userName)['verified']
            if verified:
                self.log.trace("Verified that user was deleted.")
                result['verified'] = True
            else:
                self.log.warn("Failed to verify that user was deleted.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="delete user")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_user_was_deleted(self,userName, testcase=None):
        """ Verify that a user was deleted.
        INPUT
            user name: the user name of the user to delete.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying that user %s was deleted ..."%userName)
        result = {'successful': False, 'verified':False}

        try:
            # query server table for users
            data = {'entry id': userName}
            found = self.query_page('users',data)['verified']
            if not found:
                self.log.trace("User '%s' not found."%userName)
                result['verified'] = True
            else:
                self.log.warn("User '%s' found."%userName)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify user was deleted")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result