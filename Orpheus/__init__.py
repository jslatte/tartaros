###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import inspect
from utility import return_execution_error
from api import API
from testresults import TestResults
from testruns import TestRuns
from mapping import ORPHEUS

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

DEFAULT_SERVER_URL = ORPHEUS['server url']
DEFAULT_SERVER_KEY = ORPHEUS['server key']
USERNAME = ORPHEUS['user name']
PASSWORD = ORPHEUS['password']

####################################################################################################
# Orpheus (Test Reporting) #########################################################################
####################################################################################################
####################################################################################################


class Orpheus(API, TestResults, TestRuns):
    """ Library for test result reporting and management. """

    def __init__(self, logger, server_url=DEFAULT_SERVER_URL, server_key=DEFAULT_SERVER_KEY):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # instantialize logger
        self.log = logger

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

        # properties
        self.serverURL = server_url
        self.serverKey = server_key

        # authorization
        self.username = USERNAME
        self.password = PASSWORD

        # stacktrace
        self.inspect = inspect

    def handle_exception(self, e, operation=None):
        """ Handle an exception.
        INPUT
            e: the exception (from BaseException, e).
            operation: the action being attempted (that failed).
        """

        if operation is not None: self.log.error("Failed to %s." % operation)
        self.log.error(str(e))
        for error in e:
            self.log.error(str(error))
        exception = return_execution_error()['error']
        self.log.error("Error: %s." % exception)

    def TEMPLATE_FUNCTION(self):
        """
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def update_test_case(self, case_id, title=None, type=None, case_class=None, automated=None,
                         procedure=None):
        """ Update a test case in TestRail.
        @param case_id: the id of the test case to be updated.
        @param title: a string to which to change the current case title.
        @param type: a type of test case (see mapping) to which to change the current case.
        @param case_class: the class level (0-5) to which to change the current case.
        @param automated: a boolean indicating whether to change the case status to automated or not.
        @param procedure: a list of lists pairing ['step description', 'expected result].
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result