###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from testrail import *
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
SERVER_IP_ADDRESS = ORPHEUS['server ip address']
USERNAME = ORPHEUS['user name']
PASSWORD = ORPHEUS['password']
TEST_TYPE_TO_ID = ORPHEUS['test type to id']
CASE_FIELDS = ORPHEUS['case fields']
SUITE_FIELDS = ORPHEUS['suite fields']
SECT_FIELDS = ORPHEUS['section fields']

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

        # define connection via built-in API
        self.api_client = APIClient(SERVER_IP_ADDRESS)
        self.api_client.user = self.username
        self.api_client.password = self.password

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

    def update_test_case(self, case_id, title=None, case_type=None, case_class=None, automated=None,
                         procedure=None):
        """ Update a test case in TestRail.
        @param case_id: the id of the test case to be updated.
        @param title: a string to which to change the current case title.
        @param case_type: a type of test case (see mapping) to which to change the current case.
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

            # return current test case configuration
            current_cfg = self.api_client.send_get('get_case/%s' % case_id)

            # build POST data packet for test case
            data = {
                CASE_FIELDS['title']:     current_cfg[CASE_FIELDS['title']],
                CASE_FIELDS['type']:      current_cfg[CASE_FIELDS['type']],
                CASE_FIELDS['class']:     current_cfg[CASE_FIELDS['class']],
                CASE_FIELDS['automated']: current_cfg[CASE_FIELDS['automated']],
                CASE_FIELDS['procedure']: current_cfg[CASE_FIELDS['procedure']]
            }

            # update given parameters
            if title is not None: data[CASE_FIELDS['title']] = title
            if case_type is not None: data[CASE_FIELDS['type']] = TEST_TYPE_TO_ID[case_type.lower()]
            if case_class is not None: data[CASE_FIELDS['class']] = case_class
            if automated is not None: data[CASE_FIELDS['automated']] = automated
            if procedure is not None:
                # translate list pairs into data packet format
                t_procedure = []
                for step in procedure:
                    t_step = {'content': step[0], 'expected': step[1]}
                    t_procedure.append(t_step)

                # update procedure in data packet
                data[CASE_FIELDS['procedure']] = t_procedure
            self.log.trace("Data Packet: %s" % str(data))

            # sent POST to server
            url = "update_case/%s" % case_id
            self.api_client.send_post(url, data)

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def add_suite(self, name, project_id, description=''):
        """ Add a suite to given project.
        @param name: the name of the suite to add.
        @param project_id: the id of the project to which the suite will be added.
        @param description: an optional description of the suite to add.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'id' - the id of the suite.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'id': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            # build suite data packet
            data = {
                SUITE_FIELDS['name']:   name,
                SUITE_FIELDS['desc']:   description,
            }

            # send POST to server
            url = 'add_suite/%s' % project_id
            self.api_client.send_post(url, data)

            # retrieve id of suite
            result['id'] = self.return_suite_data(name, project_id)['id']

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def return_suite_data(self, identifier, project_id):
        """ Return server data for a suite.
        @param identifier: the name or id of the suite.
        @param project_id: the project id of the suite.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'id' - the id of the suite.
            'name' - the name of the suite.
            'desc' - the description of the suite.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'id': None, 'name': None, 'desc': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # return all suites for the project
            url = 'get_suites/%s' % project_id
            suites = self.api_client.send_get(url)

            # look for suite with given name
            for suite in suites:
                if suite[SUITE_FIELDS['name']].lower() == str(identifier).lower()\
                    or str(suite[SUITE_FIELDS['id']]) == str(identifier):
                    result['id'] = suite[SUITE_FIELDS['id']]
                    result['name'] = suite[SUITE_FIELDS['name']]
                    result['desc'] = suite[SUITE_FIELDS['desc']]

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def return_section_data(self, identifier, suite_id, project_id):
        """ Return server data for a section.
        @param identifier: the name or id of the section.
        @param suite_id: the suite id of the section.
        @param project_id: the project id of the suite.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'id' - the id of the suite.
            'name' - the name of the suite.
            'parent id' - the id of the parent section (returns None if top-level section).
            'depth' - the depth of the section (0 is top-level section).
            'order' - the position of the section (down the page) (1 is the first,
                top-level section displayed on the page).
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'id': None, 'name': None, 'parent id': None,
                  'depth': None, 'order': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # return all sections for the suite
            url = 'get_sections/%(project id)s&suite_id=%(suite id)s' \
                  % {'project id': project_id,'suite id': suite_id}
            suites = self.api_client.send_get(url)

            # look for suite with given name
            for suite in suites:
                if suite[SECT_FIELDS['name']].lower() == str(identifier).lower()\
                    or str(suite[SECT_FIELDS['id']]) == str(identifier):
                    result['id'] = suite[SECT_FIELDS['id']]
                    result['name'] = suite[SECT_FIELDS['name']]
                    result['order'] = suite[SECT_FIELDS['order']]
                    result['parent id'] = suite[SECT_FIELDS['parent id']]
                    result['depth'] = suite[SECT_FIELDS['depth']]

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result