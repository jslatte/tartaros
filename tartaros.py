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

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

# logger instance
log = Logger(logging_level='trace')
database = Database(Logger(logging_level='info'))

####################################################################################################
# Tartaros #########################################################################################
####################################################################################################
####################################################################################################

# default variables
mode = 'default'
build = ''
test_name = ''
results_plan_id = None
module = ''
feature = ''
story = ''
test = ''
testcase = ''
testcase_class = ''

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
elif mode == 'testing':
    # initialize test run object
    testrun = TestRun(log, database, name=test_name, submodule_id=3, results_plan_id=results_plan_id)

    # build testcase list for test run
    testcases = testrun.build_testcase_list_for_run(module_name=module,
        feature_name=feature, story_name=story, test_name=test,
        case_name=testcase)['testcases']

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