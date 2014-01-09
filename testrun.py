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
from utility import move_up_windows_path
from os import getcwdu, path, mkdir
from mapping import TARTAROS
from utility import return_execution_error
from testcase import HestiaTestCase
from Orpheus import Orpheus
from Minos import Minos

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

TEST_STATUSES = TARTAROS['test statuses']
SUBMODULE_ID_TO_TESTCASE_OBJ = {
    '1':                None,
    '2':                HestiaTestCase,
    '3':                None,
    '4':                None,
    '5':                None,
    '6':                None,
    '7':                None,
    '8':                None,
}
BLANK_SEL = ""

####################################################################################################
# Test Run #########################################################################################
####################################################################################################
####################################################################################################

class TestRun():
    """ The root test run object class. Includes all root functions and parameters. """

    def __init__(self, logger, database, name, submodule_id, testcases=[], results_plan_id=None,
                 debugging=False):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
            database: database object to use for interacting with Tartaros database (initialized).
            name: the name of the test run.
            submodule id: the submodule to run the test against.
            testcases: a list of test case data dicts for test cases to execute as part of the test run.
            results plan id: the test plan id to publish results to.
            debugging: set to TRUE if debugging the testcase.
        """

        # instance logger
        self.log = logger

        # instance test reporter
        self.reporter = Orpheus(self.log)

        # instance build manager
        self.build_manager = Minos(self.log)

        # database object
        self.database = database

        # define default attributes
        self.name = name
        self.debugging = debugging
        self.id = id
        self.name = name
        self.submodule_id = submodule_id
        self.results_plan_id = results_plan_id
        self.testcases = testcases
        self.duration = 0
        self.results = []
        self.testcase_obj = None

        # instance testcase
        self.initialize()

    def initialize(self):
        """ Instance test run object and assigning associated attributes.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.info("Initializing Test Run %s ..." % self.name)
        result = {'successful': False}

        try:
            # determine test case object submodule type to use
            self.testcase_obj = SUBMODULE_ID_TO_TESTCASE_OBJ[str(self.submodule_id)]

            self.log.trace("Initialized test run.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to initialize test run %s." % self.name)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def run(self):
        """ Execute each test case in the list of testcases.
        """

        self.log.info("Running %s test run ..." % self.name)
        result = {'successful': False, 'verified': False}

        try:
            # send testcase start message to build server
            self.log.build_test_start(self.name)

            # begin timing testcase execution
            t0 = clock()

            # execute test cases
            for testcase in self.testcases:
                testcase = self.testcase_obj(self.log, self.database, testcase['id'],
                    debugging=self.debugging)
                testcase.run()

                # compile results data from execution
                testcase_data = {
                    'name':         testcase.name,
                    'test id':      testcase.test_id,
                    'status':       testcase.status,
                    'version':      testcase.version,
                }
                self.results.append(testcase_data)

            # end timing testcase execution
            self.duration = clock() - t0

            # publish results
            self.publish_results()

            # send testcase end message to build server
            self.log.build_test_end(self.name)

            self.log.trace("Finished running %s test run in %s seconds." % (self.name, self.duration))
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to run test run %s." % self.name)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def translate_results_into_publishing_list(self):
        """ Translate the individual test case results from the test run into a publishable list.
        OUPUT
            successful: whether the function executed successfully or not.
            publishing list: list of [results id, version, module id, status, comment]s
                for each test in run to publish.
        """

        self.log.trace("Translating results into publishing list ...")
        result = {'successful': False, 'publishing list': []}

        try:
            # create list of test ID's to handle
            test_ids = []
            for testcase_result in self.results:
                if testcase_result['test id'] not in test_ids:
                    test_ids.append(testcase_result['test id'])

            # create data dict by result ID to store group results
            test_results = {}
            for test_id in test_ids:
                test_results[str(test_id)] = []

            # associate test case results together with their parent test
            for testcase_result in self.results:
                test_results[str(testcase_result['test id'])].append(
                    {'name': testcase_result['name'], 'status': testcase_result['status'],
                     'version': testcase_result['version']})

            # process status results for each test
            test_ids = test_results.keys()
            for test_id in test_ids:
                # determine results id for test
                results_id = self.database.return_results_id_for_test(int(test_id))['id']

                # determine version of product under test
                version = None
                for testcase in test_results[str(test_id)]:
                    version = testcase['version']

                # determine status of test
                test_status = None
                for testcase in test_results[str(test_id)]:
                    if testcase['status'].lower() == TEST_STATUSES['failed'].lower():
                        test_status = TEST_STATUSES['failed']
                    elif testcase['status'].lower() == TEST_STATUSES['re-test']:
                        test_status = TEST_STATUSES['re-test']
                    elif testcase['status'].lower() == TEST_STATUSES['passed with issues']:
                        test_status = TEST_STATUSES['passed with issues']
                    elif testcase['status'].lower() == TEST_STATUSES['blocked'].lower():
                        test_status = TEST_STATUSES['blocked']
                    else:
                        test_status = TEST_STATUSES['passed']

                # determine module for test
                module_id = self.database.return_module_for_test(test_id)['id']

                # build comment for test
                comment = 'AUTOMATED TEST RESULTS:'
                for testcase in test_results[str(test_id)]:
                    comment += '\n%s:\t%s' %(testcase['name'].upper(), testcase['status'])

                # append to publishing list
                result['publishing list'].append([results_id, version, module_id, test_status, comment])

            self.log.trace("Results translated into publishing list for test run %s." % self.name)
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to translate results into publish list for test run %s." % self.name)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

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
                   'location':          0}
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

    def publish_results(self):
        """ Publish test run results.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Publishing results for test run %s ..." % self.name)
        result = {'successful': False}

        try:
            # translate results into publishing list
            publishing_list = self.translate_results_into_publishing_list()['publishing list']

            for item in publishing_list:
                # determine test run to publish to
                module_id = item[2]
                testRunID = self.determine_test_runs_to_publish_to(module_id)['test run id']

                # publish results to TestRail
                results_id = item[0]
                status = item[3]
                comment = item[4]
                version = item[1]
                self.reporter.add_result_for_testcase_in_test(testRunID, results_id, status,
                    {'comment': comment, 'version': version})

            self.log.trace("Results published.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to publish results for test run %s." % self.name)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def build_testcase_list_for_run(self, module_id='', feature_id='', story_id='',
                                    test_id='', case_id='', case_class=None):
        """ Build testcase list for test run.
        INPUT
            module id: the id of the module being tested (leave blank if all).
            feature id: the id of the feature being tested (leave blank if all).
            story id: the id of the story being tested (leave blank if all).
            test id: the id of the test being run (leave blank if all).
            case id: the id of the test case being run individually (leave blank if all).
        OUPUT
            successful: whether the function executed successfully or not.
            testcases: the list of test cases for the test run.
        """

        self.log.trace("Building test case list for test run ...")
        result = {'successful': False, 'testcases': []}

        try:
            # scope level
            SCOPE_LEVELS = {
                'full':         5,
                'module':       4,
                'feature':      3,
                'user story':   2,
                'test':         1,
                'test case':    0,
            }

            # determine scope of test run
            if str(case_id) is not None and str(case_id) != BLANK_SEL and str(case_id)is not '0':
                scope = SCOPE_LEVELS['test case']
            elif str(test_id) is not None and str(test_id) != BLANK_SEL and str(test_id)is not '0':
                scope = SCOPE_LEVELS['test']
            elif str(story_id) is not None and str(story_id) != BLANK_SEL and str(story_id)is not '0':
                scope = SCOPE_LEVELS['user story']
            elif str(feature_id) is not None and str(feature_id) != BLANK_SEL and str(feature_id)is not '0':
                scope = SCOPE_LEVELS['feature']
            elif str(module_id) is not None and str(module_id) != BLANK_SEL and str(module_id)is not '0':
                scope = SCOPE_LEVELS['module']
            else:
                scope = SCOPE_LEVELS['full']


            # based on scope of test run, build list of test cases to run
            self.log.trace("Scope of test run: %s." % scope)
            # determine pertinent ids
            if scope == 5:
                # determine modules
                modules = self.database.return_modules_for_submodule(2)['modules']
                # append all test cases for product
                for module in modules:
                    # append all test cases for module
                    features = self.database.return_features_for_module(module['id'])['features']
                    for feature in features:
                        # append all test cases for feature
                        stories =\
                        self.database.return_user_stories_for_feature(feature['id'],
                                                                    module=module['id'])['user stories']
                        for story in stories:
                            # append all test cases for user story
                            tests = self.database.return_tests_for_user_story(story['id'])['tests']
                            for test in tests:
                                # append all test cases for test
                                testcases =\
                                self.database.return_testcases_for_test(test['id'])['testcases']
                                for testcase in testcases:
                                    if int(testcase['active']) > 0:
                                        result['testcases'].append({'id': testcase['id']})
            if scope == 4:
                # append all test cases for module
                features = self.database.return_features_for_module(module_id)['features']
                for feature in features:
                    # append all test cases for feature
                    stories =\
                    self.database.return_user_stories_for_feature(feature['id'],
                                                                  module=module_id)['user stories']
                    for story in stories:
                        # append all test cases for user story
                        tests = self.database.return_tests_for_user_story(story['id'])['tests']
                        for test in tests:
                            # append all test cases for test
                            testcases = self.database.return_testcases_for_test(test['id'])['testcases']
                            for testcase in testcases:
                                if int(testcase['active']) > 0:
                                    result['testcases'].append({'id': testcase['id']})
            if scope == 3:
                # append all test cases for feature
                stories = self.database.return_user_stories_for_feature(feature_id,
                                                                        module=module_id)['user stories']
                for story in stories:
                    # append all test cases for user story
                    tests = self.database.return_tests_for_user_story(story['id'])['tests']
                    for test in tests:
                        # append all test cases for test
                        testcases = self.database.return_testcases_for_test(test['id'])['testcases']
                        for testcase in testcases:
                            if int(testcase['active']) > 0:
                                result['testcases'].append({'id': testcase['id']})
            if scope == 2:
                # append all test cases for user story
                tests = self.database.return_tests_for_user_story(story_id)['tests']
                for test in tests:
                    # append all test cases for test
                    testcases = self.database.return_testcases_for_test(test['id'])['testcases']
                    for testcase in testcases:
                        if int(testcase['active']) > 0:
                            result['testcases'].append({'id': testcase['id']})
            if scope == 1:
                # append all test cases for test
                testcases = self.database.return_testcases_for_test(test_id)['testcases']
                for testcase in testcases:
                    if int(testcase['active']) > 0:
                        result['testcases'].append({'id': testcase['id']})
            if scope == 0:
                # determine test case id
                testcase = self.database.return_testcase_data(case_id)['testcase data']
                # append test case
                if int(testcase['active']) > 0:
                    result['testcases'].append({'id': testcase['id']})

            self.log.trace("Built testcase list for test run with %s test cases."
                           % len(result['testcases']))
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to build testcase list for test run.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error(frame=1)['error'])
            result['successful'] = False

        # return
        return result

    def filter_testcases_by_class(self, testcases, testcase_class=''):
        """
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Filtering testcases by class ...")
        result = {'successful': False}

        try:
            if testcase_class.lower() != BLANK_SEL.lower() and testcase_class.lower() != '':
                # filter testcases to run according to class selected
                testcases_to_remove = []
                for testcase in testcases:
                    testcase_data = self.database.return_testcase_data(testcase['id'])['testcase data']
                    if int(testcase_data['class']) != int(testcase_class):
                        testcases_to_remove.append(testcase)
                    if int(testcase_data['active']) == 0:
                        testcases_to_remove.append(testcase)

                # remove testcases filtered out
                for testcase in testcases_to_remove:
                    testcases.remove(testcase)

            self.log.trace("Filtered testcases by class")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to filter testcases by class.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def setup_test_environment(self, build, test_name):
        """ Setup the test environment for the product under test.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Setup test environment ...")
        result = {'successful': False, 'verified': False}

        try:
            if self.submodule_id == 2:
                # set up environment for Hestia test
                from Hestia import Hestia
                self.hestia = Hestia(self.log, self.database)

                # uninstall previous builds
                self.hestia.uninstall_vim_server()

                # determine path to save downloaded build to
                current_directory = getcwdu()
                save_path = move_up_windows_path(current_directory, 2)['path']+"\\artifacts\\"
                if not path.exists(save_path):
                    self.log.trace("Artifacts folders does not exist. Creating ...")
                    mkdir(save_path)

                # download last successful build for specified build line
                file_path = self.build_manager.download_last_successful_build(build,
                    save_path)['file path']

                # install server build under test
                self.hestia.install_vim_server(file_path)

                # check the server version
                version = self.hestia.return_vim_server_version()['version']

                # update test tag in TeamCity
                self.log.build_set_label(version, test_name)

            else:
                self.log.error("Failed to setup test environment. Invalid submodule %s specified."
                               % self.submodule_id)

            self.log.trace("Set up test environment.")
            result['successful'] = True
        except BaseException, e:
            self.hestia.handle_exception(e, operation="setup test environment")

        # return
        self.processing = result['successful']
        return result

    def teardown_test_environment(self):
        """ Teardown the test environment for the product under test.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Tearing down test environment ...")
        result = {'successful': False, 'verified': False}

        try:
            if self.submodule_id == 2:
                # instance Hestia module for use
                from Hestia import Hestia
                self.hestia = Hestia(self.log, self.database)

                # uninstall build
                #self.hestia.uninstall_vim_server(self)

            else:
                self.log.error("Failed to teardown test environment. Invalid submodule %s specified."
                               % self.submodule_id)

            self.log.trace("Tore down test environment.")
            result['successful'] = True
        except BaseException, e:
            self.hestia.handle_exception(e, operation="tear down test environment")

        # return
        self.processing = result['successful']
        return result