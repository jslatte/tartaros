###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import os
from time import clock
from datetime import datetime
from mapping import TARTAROS, TARTAROS_LOGGING_PATH
from utility import return_execution_error
from Orpheus import Orpheus
import inspect
from collections import OrderedDict

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

TEST_STATUSES = TARTAROS['test statuses']

####################################################################################################
# TestCase #########################################################################################
####################################################################################################
####################################################################################################


class DebugProduct():

    def debug_function(self, debug_argument=True, testcase=None):
        result = {'successful': debug_argument, 'verified': debug_argument}
        if testcase is not None:
            testcase.processing = debug_argument
        return result


class TestCase():
    """ The root test case object class. Includes all root functions and parameters. """

    def __init__(self, logger, database, testcase_id, debugging=False, int_dvr_ip=None,
                 results_plan_id=None):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
            database: database object to use for interacting with Tartaros database (initialized).
            id: the testcase ID used for referencing in database.
            debugging: set to TRUE if debugging the testcase.
            int_dvr_ip: the ip address of the DVR being used for integration testing.
        """

        # instantialize logger
        self.log = logger

        # database object
        self.database = database

        # instance test reporter
        self.reporter = Orpheus(self.log)

        # define default attributes
        self.debugging = debugging
        self.id = testcase_id
        self.name = None
        self.test_id = None
        self.procedure = []
        self.status = TEST_STATUSES['not tested']
        self.verified = False
        self.verifications = []
        self.duration = 0
        self.version = None
        self.int_dvr_ip = int_dvr_ip
        self.results_plan_id = results_plan_id

        # naming attributes
        self.module = ''
        self.feature = ''
        self.story = ''
        self.test = ''

        # inspection
        self.inspect = inspect

        # instance testcase
        self.initialize()

        # product-specific setup
        self.setup_for_product()

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
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def get_testcase_data_from_database(self, testcase_id):
        """ Get testcase data from the database
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'testcase data'
            'test data'
            'user story data'
            'feature data'
            'module data'
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'testcase data': {}, 'test data': {},
                  'user story data': {}, 'feature data': {}, 'module data': {}}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            returned = self.database.return_testcase_data(self.id)
            result['testcase data'] = returned['testcase data']
            result['test data'] = returned['test data']
            result['story data'] = returned['user story data']
            result['feature data'] = returned['feature data']
            result['module data'] = returned['module data']

            # update testcase attributes
            self.name = str(result['testcase data']['name'])
            self.test = str(result['test data']['name'])
            self.test_id = result['testcase data']['test']
            self.story = str(result['story data']['action'])
            self.feature = str(result['feature data']['name'])
            self.module = str(result['module data']['name'])
            self.module_id = int(result['module data']['id'])
            self.case_results_id = result['testcase data']['results id']

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def get_procedure_step_data_from_database(self, step_id):
        """
        @param step_id: the id of the procedure step.
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'step data'
            'function data'
            'submodule data'
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'step data': {}, 'function data': {}, 'submodule data': {}}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            data = self.database.return_procedure_step_data(step_id)
            result['step data'] = data['step data']
            result['function data'] = data['function data']
            result['submodule data'] = data['submodule data']

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def initialize(self):
        """ Instance test case object by reference ID in database and assigning associated attributes.
        """

        operation = self.inspect.stack()[0][3]
        self.log.info("Initializing Testcase %s ..." % self.id)
        result = {'successful': False}

        try:
            # get testcase data from database
            returned = self.get_testcase_data_from_database(self.id)

            # assign unique name for build server test result tracking
            self.build_test_name = "%s: %s: %s: %s: %s" % (self.module, self.feature, self.story,
                self.test, self.name)

            # assign procedure
            #   parse procedure data
            procedure_data = returned['testcase data']['procedure']
            procedure_raw_list = procedure_data.split(',')
            #   build procedure data list
            procedure_list = []
            for item in procedure_raw_list:
                procedure_list.append(int(item.strip()))
            #   build procedure function list
            for procedure_step_id in procedure_list:
                data = self.get_procedure_step_data_from_database(procedure_step_id)
                # parse the data
                step_data = data['step data']
                function_data = data['function data']
                submodule_data = data['submodule data']
                # translate function call
                function = function_data['function'].lower().replace(' ', '_')
                # handle arguments
                if str(step_data['arguments']).strip() == '': step_data['arguments'] = None
                if step_data['arguments'] is not None:
                    arguments = str(step_data['arguments'])
                    arguments += ','
                else:
                    arguments = ''
                arguments += "testcase=self"
                # handle verification status
                verification = eval(step_data['verification'])
                # combine into one data dict of relevant data
                translated_step_data = {
                    'id':       procedure_step_id,
                    'name':     step_data['name'],
                    'function': "%s.%s(%s)" % (submodule_data['code'], function,
                        arguments),
                    'verification': verification
                }
                self.procedure.append(translated_step_data)

            # report
            self.log.trace("Testcase initialized:")
            self.log.trace("\tName: %s" % self.name)
            self.log.trace("\tBuild Test name: %s" % self.build_test_name)
            self.log.trace("\tProcedure:")
            for step in self.procedure:
                self.log.trace("\t\t%s" % step['name'])
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation)

        # return
        return result

    def execute_step(self, step):
        """ Execute the procedure step.
        INPUT
            step: the step to execute.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.info("Executing step %s ..." % str(step))
        result = {'successful': False}

        try:

            self.log.info('Executing step "%s" ...' % step['name'])
            function = "self.%s" % str(step['function'])
            if self.debugging: self.log.trace("Function Call:\t%s" % function)

            if step['verification']:
                # execute with verification
                function += "['verified']"
                result = eval(function)
                self.verifications.append([step['name'], result])
            else:
                # execute normally
                eval(function)

            self.log.trace("Executed step %s" % step['name'])
            #result['successful'] = True
        except BaseException, e:
            self.handle_step_execution_failure(step, e)

        # return
        return result

    def handle_step_execution_failure(self, step, error):
        """ Handle a procedure step execution failure.
        """

        self.log.error("Failed to execute step %s" % step['name'])
        self.log.error(str(error))
        for e in error:
            self.log.error(str(e))
        exception = return_execution_error()['error']
        self.log.error("Error: %s." % exception)
        self.processing = False

    def determine_result(self):
        """ Determine the final result of the testcase
        """

        # handle processing failures as RE-TEST
        if not self.processing: self.status = TEST_STATUSES['re-test']

        # parse through verifications
        self.verified = False
        verifieds = []
        failures = []
        for verification in self.verifications:
            if verification[1]: verifieds.append(verification[0])
            else: failures.append(verification[0])

        # determine result based on verifications
        if len(verifieds) > 0 and len(failures) == 0: self.verified = True

        if self.verified:
            self.log.info("Test case VERIFIED.")
            self.status = TEST_STATUSES['passed']
        else:
            self.log.error("FAILED to verify test case.")
            self.status = TEST_STATUSES['failed']
            for failure in failures:
                self.log.error("FAILED to %s" % failure)

    def determine_test_runs_to_publish_to(self, module_id):
        """ Determine the correct test run ID to publish to for resutls.
        INPUT
            module id: the id of the module for the product under test.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Determining test run to publish to ...")
        result = {'successful': False, 'test run id': None}

        try:
            # determine test run config for test plan
            # determine submodule for product under test
            submodule_id = self.database.return_submodule_for_module(module_id)['id']
            # determine project id from submodule id
            # TODO: Add field in table to track project id, and parse correctly here
            project_id = 1
            # retrieve test runs for given test plan ID
            key = '&key=%d' % self.reporter.serverKey
            url = self.reporter.serverURL + '/get_plan/%s' % self.results_plan_id + key
            response = self.reporter.get_request_from_server(url)['response dict']
            try: testRuns = response['entries']
            except KeyError:
                self.log.error("Returned no test runs for results plan id %s." % self.results_plan_id)
                testRuns = []
            # build cfg dict from server response
            cfg = {'software':          0,
                   'core':              0,
                   'autoclip':          0,
                   'health':            0,
                   'clip management':   0,
                   'streaming server':  0,
                   'location':          0,
                   'dvr integration':   0,}
            for testRun in testRuns:
                if 'regression test: software' in testRun['name'].lower():
                    cfg['software'] = testRun['runs'][0]['id']
                elif 'regression test: core' in testRun['name'].lower():
                    cfg['core'] = testRun['runs'][0]['id']
                elif 'regression test: autoclip' in testRun['name'].lower():
                    cfg['autoclip'] = testRun['runs'][0]['id']
                elif 'regression test: health' in testRun['name'].lower():
                    cfg['health'] = testRun['runs'][0]['id']
                elif 'regression test: clip management' in testRun['name'].lower():
                    cfg['clip management'] = testRun['runs'][0]['id']
                elif 'regression test: streaming server' in testRun['name'].lower():
                    cfg['streaming server'] = testRun['runs'][0]['id']
                elif 'regression test: location' in testRun['name'].lower():
                    cfg['location'] = testRun['runs'][0]['id']
                elif 'dvr integration test' in testRun['name'].lower():
                    cfg['dvr integration'] = testRun['runs'][0]['id']
                else:
                    self.log.trace("Unidentified test run found:\t%s." %testRun['name'])

            # determine module name
            module_name = self.database.return_module_name(module_id)['name']
            # determine test run to publish to
            if 'core' in str(module_name).lower():
                testRunID = cfg['core']
            elif 'autoclip' in str(module_name).lower():
                testRunID = cfg['autoclip']
            elif 'health' in str(module_name).lower():
                testRunID = cfg['health']
            elif 'clip management' in str(module_name).lower():
                testRunID = cfg['clip management']
            elif 'location' in str(module_name).lower():
                testRunID = cfg['location']
            elif 'streaming server' in str(module_name).lower():
                testRunID = cfg['streaming server']
            elif 'software' in str(module_name).lower():
                testRunID = cfg['software']
            elif 'dvr integration' in str(module_name).lower():
                testRunID = cfg['dvr integration']
            else:
                self.log.error("Failed to determine test run for publication.")
                testRunID = 0

            self.log.trace("Determined test run to publish to.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to determine test run to publish to.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            testRunID = None

        # return
        result['test run id'] = testRunID
        return result

    def log_results(self):
        """ Log testcase results.
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # verify logging folder exists
            if not os.path.exists(TARTAROS_LOGGING_PATH):
                os.mkdir(TARTAROS_LOGGING_PATH)

            # define data to write
            data_to_write = [
                datetime.now(),
                self.id,
                self.name,
                self.test_id,
                self.test,
                self.status,
                self.duration,
            ]
            # convert all data items to strings
            for i in data_to_write:
                data_to_write[data_to_write.index(i)] = str(i)
            # build results data amalgamated string
            results_data_s = '\n' + '\t'.join(data_to_write)

            # write results data
            results_path = TARTAROS_LOGGING_PATH + '\\results.log'
            f = open(results_path, 'a')
            f.write(results_data_s)
            f.close()

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def run(self):
        """ Execute the testcase step-by-step according to its procedure and determine result.
        """

        self.log.info("Running %s testcase ..." % self.name)
        result = {'successful': False, 'verified': False}
        self.processing = True

        try:
            # send testcase start message to build server
            self.log.build_testcase_start(self.build_test_name)

            # begin timing testcase execution
            t0 = clock()

            # execute testcase
            for step in self.procedure:
                if self.processing:
                    if not self.debugging:
                        try: self.execute_step(step)
                        except BaseException, e:
                            self.handle_step_execution_failure(step, e)
                    else: self.execute_step(step)
                else:
                    self.log.error('Could not execute step "%s" due to previous step '
                                   'execution failure.' % step['name'])

            # end timing testcase execution
            self.duration = clock() - t0

            # determine test result
            self.determine_result()

            # report testcase results
            self.log.info("%s testcase finished in %s seconds with '%s' status."
                          % (self.build_test_name, self.duration, self.status.upper()))
            # publish to TestRail if case has individual results id
            if self.case_results_id is not None and self.results_plan_id is not None:
                self.log.trace("Publishing test case results to TestRail ...")
                # determine test run to publish to
                run_id = self.determine_test_runs_to_publish_to(self.module_id)['test run id']

                # publish results to TestRail
                results_id = self.case_results_id
                status = self.status
                comment = ''
                version = self.version
                self.reporter.add_result_for_testcase_in_test(run_id, results_id, status,
                    {'comment': comment, 'version': version})
                self.log.trace("... done.")

            # publish results to results folder
            self.log_results()

            # send testcase end message to build server
            self.log.build_testcase_end(self.build_test_name, self.status, self.duration)

        except BaseException, e:
            self.handle_exception(e, 'run testcase %s' % self.name)
            self.verified = False

        # return
        result['verified'] = self.verified
        return result

    def setup_for_product(self): pass

    def setup_test_environment(self, build, test_name): pass


class ThanatosTestCase(TestCase):

    def get_testcase_data_from_database(self, testcase_id):
        """
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'testcase data' - a dictionary packet containing the testcase data.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'testcase data': {}}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # retrieve test case
            testcase = self.database.query_database_table(
                self.database.db_handle, 'test_cases', addendum='WHERE id = %d' % testcase_id
            )['response'][0]
            #self.log.trace(testcase)

            # determine test data
            result['testcase data'] = OrderedDict([
                ('id', testcase[0]),
                ('name', testcase[1]),
                ('test', testcase[2]),
                ('procedure', testcase[3]),
                ('minimum version', testcase[4]),
                ('class', testcase[5]),
                ('active', testcase[6]),
                ('type', 'regression'),
                ('results id', testcase[7]),
            ])

            # update testcase attributes
            self.name = testcase[1]
            self.test_id = testcase[2]
            self.case_results_id = testcase[7]

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        return result

    def get_procedure_step_data_from_database(self, step_id):
        """
        @param step_id: the id of the procedure step.
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'step data' - a dictionary packet containing the step data.
            'function data' - a dictionary packet containing the function data.
            'submodule data' - a dictionary packet containing the submodule data.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'step data': {}, 'function data': {}, 'submodule data': {}}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # retrieve step data
            step = self.database.query_database_table(
                self.database.db_handle, 'procedure_steps', addendum='WHERE id = %d' % step_id
            )['response'][0]
            #self.log.trace(step)

            # build step data packet
            result['step data'] = OrderedDict([
                ('id', step[0]),
                ('name', step[1]),
                ('function', step[2]),
                ('arguments', step[3]),
                ('verification', step[4]),
            ])
            # translate verification
            if str(step[4]) == '1':
                result['step data']['verification'] = 'True'
            else:
                result['step data']['verification'] = 'False'

            # retrieve function data
            funct = self.database.query_database_table(
                self.database.db_handle, 'functions',
                addendum='WHERE id = %d' % result['step data']['function']
            )['response'][0]
            #self.log.trace(funct)

            # build function data packet
            result['function data'] = OrderedDict([
                ('id', funct[0]),
                ('function', funct[1]),
                ('submodule id', funct[2]),
            ])

            # retrieve product data
            product = self.database.query_database_table(
                self.database.db_handle, 'products',
                addendum='WHERE id = %d' % result['function data']['submodule id']
            )['response'][0]
            #self.log.trace(product)

            # build product data packet
            result['submodule data'] = OrderedDict([
                ('id', product[0]),
                ('name', product[1]),
                ('code', product[2]),
                ('results id', product[3]),
            ])

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def setup_for_product(self):
        self.debug_product = DebugProduct()

class HestiaTestCase(TestCase):

    def setup_for_product(self):

        # establish product submodule instance for use
        from Hestia import Hestia
        self.hestia = Hestia(self.log, self.database, int_dvr_ip=self.int_dvr_ip)

        # establish additional submodules for use

        # associate submodule product version with testcase
        self.hestia.return_vim_server_version(testcase=self)
        self.hestia.determine_vim_server_release_version(self.version, testcase=self)

        # reset environment for test case
        self.hestia.reset_vim_server(testcase=self)