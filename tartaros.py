###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from sys import argv
from logger import Logger
from testrun import TestRun
from Database import Database
from Hestia import Hestia
from Ixion import Ixion
from Minos import Minos
from Orpheus import Orpheus
from Sisyphus import Sisyphus
from Tantalus import Tantalus
from mapping import TARTAROS_WEB_DB_PATH, MINOS

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

# logger instance
log = Logger(logging_level='trace')

minos = Minos(log)
TEST_CONFIGURATIONS = MINOS['test configurations']

db = Database(log)

####################################################################################################
# Tartaros #########################################################################################
####################################################################################################
####################################################################################################

# default variables
mode = None
build = ''
test_name = ''
results_plan_id = None
module = ''
feature = ''
story = ''
test = ''
testcase = ''
testcase_class = None

# test scheduling variables
tests_to_schedule = []

# read system arguments
params = []
if argv is not None:
    for arg in argv:
        # mode
        if 'mode=' in arg:
            mode = arg.split('mode=')[1].lower()
            params.append('Mode:\t%s' % mode)
        elif 'build=' in arg:
            s_build = arg.split('build=')[1]
            for string in s_build[0:]:
                build += str(string)
            params.append('Build:\t%s' % build)
        elif 'testname=' in arg:
            test_name_s = arg.split('testname=')[1]
            for string in test_name_s[0:]:
                test_name += str(string)
            params.append('Test Name:\t%s' % test_name)
        elif 'resultsplanid=' in arg:
            results_plan_id = arg.split('resultsplanid=')[1].lower()
            params.append('Results Plan ID:\t%s' % results_plan_id)
        elif 'testingmodule=' in arg:
            s_module = arg.split('testingmodule=')[1]
            for string in s_module[0:]:
                module += str(string)
            params.append('Testing Module:\t%s' % module)
        elif 'testingfeature=' in arg:
            s_feature = arg.split('testingfeature=')[1]
            for string in s_feature[0:]:
                feature += str(string)
            params.append('Testing Feature:\t%s' % feature)
        elif 'testingstory=' in arg:
            s_story = arg.split('testingstory=')[1]
            for string in s_story[0:]:
                story += str(string)
            params.append('Testing Story:\t%s' % story)
        elif 'testingtest=' in arg:
            s_test = arg.split('testingtest=')[1]
            for string in s_test[0:]:
                test += str(string)
            params.append('Testing Test:\t%s' % test)
        elif 'testingtestcase=' in arg:
            s_testcase = arg.split('testingtestcase=')[1]
            for string in s_testcase[0:]:
                testcase += str(string)
            params.append('Testing Test Case:\t%s' % testcase)
        elif 'testcaseclass=' in arg:
            testcase_class = arg.split('testcaseclass=')[1]
            params.append('Testing Test Case Class:\t%s' % testcase_class)
        elif 'teststoschedule=' in arg:
            tests = arg.split('teststoschedule=')[1].split(',')
            for test in tests:
                if test.strip() != 'None':
                    tests_to_schedule.append(test.strip())

    # log parameters
    log.trace("Parameters modified:")
    for param in params:
        params[params.index(param)] = param.replace('"', '').replace("'", '')
        log.trace("\t%s" % param)

# execute according to system arguments
if mode == 'cerberus':
    pass
elif mode == 'ixion':
    ixion = Ixion(log)
    ixion.run()

elif mode == 'testscheduling':
    # trigger each test
    for test in tests_to_schedule:
        try:
            # determine parameters
            if test.lower().strip() == 'regression full (by feature)':
                # determine all features
                features = db.return_features_for_submodule(2)['features']

                # add a test run for each feature (exclude debug)
                for feature in features[1:]:
                    # build parameters list for feature test run
                    params = []
                    params.append(['test name', '%s Regression Test' % feature['name']])
                    params.append(['feature', '%s' % feature['name']])

                    # update parameters (with build and test plan)
                    params.append(['test plan id', results_plan_id])
                    params.append(['build', build])

                    # trigger test
                    minos.trigger_build('tartaros', params)
            else:
                params = TEST_CONFIGURATIONS[test.lower()]

                # update parameters (with build and test plan)
                params.append(['test plan id', results_plan_id])
                params.append(['build', build])

                # trigger test
                minos.trigger_build('tartaros', params)

        except KeyError, e:
            log.error("Invalid test %s specified." % test)

elif mode == 'testing':
    # instance database for TeamCity testing
    database = Database(Logger(logging_level='info'))

    # initialize test run object
    testrun = TestRun(log, database, name=test_name, submodule_id=2, results_plan_id=results_plan_id)

    # build testcase list for test run
    testcases = testrun.build_testcase_list_for_run(module_id=module,
        feature_id=feature, story_id=story, test_id=test,
        case_id=testcase, case_class=testcase_class)['testcases']

    # filter by class
    testrun.filter_testcases_by_class(testcases, testcase_class)

    # set testcase list for test run
    testrun.testcases = testcases

    if build is not None:
        # setup test environment
        testrun.setup_test_environment(build, test_name)

        # execute test run
        testrun.run()

        # teardown test environment
        testrun.teardown_test_environment()

    else:
        log.error("Failed to setup test environment. %s is not a valid build." % build)

elif mode == 'webtesting':
    # instance with trace logging and correct db path for Cerberus (web2py) testing
    database = Database(Logger(logging_level='trace'), path=TARTAROS_WEB_DB_PATH)

    # initialize test run object
    testrun = TestRun(log, database, name=test_name, submodule_id=2, results_plan_id=results_plan_id)

    # build testcase list for test run
    testcases = testrun.build_testcase_list_for_run(module_id=module,
        feature_id=feature, story_id=story, test_id=test,
        case_id=testcase)['testcases']

    # filter by class
    if testcase_class is not None:
        testrun.filter_testcases_by_class(testcases, testcase_class)

    # set testcase list for test run
    testrun.testcases = testcases

    # execute test run
    testrun.run()

elif mode is None:
    log.error("No run mode specified.")

else:
    log.error("Invalid mode %s specified." % mode)