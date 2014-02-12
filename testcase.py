###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from time import clock
from mapping import TARTAROS
from utility import return_execution_error

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

TEST_STATUSES = TARTAROS['test statuses']

####################################################################################################
# TestCase #########################################################################################
####################################################################################################
####################################################################################################

class TestCase():
    """ The root test case object class. Includes all root functions and parameters. """

    def __init__(self, logger, database, testcase_id, debugging=False, int_dvr_ip=None):
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

    def initialize(self):
        """ Instance test case object by reference ID in database and assigning associated attributes.
        """

        self.log.info("Initializing Testcase %s ..." % self.id)
        result = {'successful': False}

        try:
            # get testcase data from database
            returned = self.database.return_testcase_data(self.id)
            testcase_data = returned['testcase data']
            test_data = returned['test data']
            story_data = returned['user story data']
            feature_data = returned['feature data']
            module_data = returned['module data']

            # assign attributes to testcase
            self.name = str(testcase_data['name'])
            self.test = str(test_data['name'])
            self.test_id = testcase_data['test']
            self.story = str(story_data['action'])
            self.feature = str(feature_data['name'])
            self.module = str(module_data['name'])

            # assign unique name for build server test result tracking
            self.build_test_name = "%s: %s: %s: %s: %s" % (self.module, self.feature, self.story,
                self.test, self.name)

            # assign procedure
            #   parse procedure data
            procedure_data = testcase_data['procedure']
            procedure_raw_list = procedure_data.split(',')
            #   build procedure data list
            procedure_list = []
            for item in procedure_raw_list:
                procedure_list.append(int(item.strip()))
            #   build procedure function list
            for procedure_step_id in procedure_list:
                data = self.database.return_procedure_step_data(procedure_step_id)
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
            self.log.error("Failed to initialize testcase.")
            self.log.error(str(e))
            for error in e:
                self.log.error(str(error))
            exception = return_execution_error()['error']
            self.log.error("Error: %s." % exception)

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
            self.log.info("%s testcase finished in %s seconds with '%s' status." % (self.build_test_name,
                                                                    self.duration, self.status.upper()))

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