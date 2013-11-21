####################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import ORPHEUS

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

TEST_STATUS_TO_ID = ORPHEUS['test status to id']

####################################################################################################
# Test Results Submodule ###########################################################################
####################################################################################################
####################################################################################################

class TestResults():
    """ Submodule for updating test results in TestRail. """

    def add_result_to_testcase(self, testID, status, params=[]):
        """ Add test result to specified test of an active test run.
        'testID' must be the TestRail ID for the test being updated.
        'params' is an optional dictionary with additional parameters:
            'comment' - any text to add to the status update
            'version' - the version of the software under test
            'elapsed' - the duration of the test (in 5m/1h format) """

        self.log.trace("Adding '%s' result to test %s ..."%(status,str(testID)))
        result = {'server response':None,'succeeded':False}

        # base data packet
        data = {
            'status_id':    TEST_STATUS_TO_ID[status.lower()]
        }
        # append any additional parameters to data packet
        data.update(params)
        # post request to server
        url = self.serverURL+"/add_result/%d&key=%d"%(testID,self.serverKey)
        result['server response'] = self.post_request_to_server(url,data,json=True)['response']
        # check response
        if result['server response'] is not None: result['succeeded'] = True
        else: self.log.trace("Failed to verify server test update command received.")
        # return
        return result

    def add_result_for_testcase_in_test(self, testRunID, testID, status, params=[]):
        """ Add test result to specified test in test run based on the
        root test ID in the library (not the instance ID in the test run).
        'testRunID' must be the TestRail ID for the test run (not test plan) containing the test.
        'testID' must be the TestRail test ID for the test being updated.
        'params' is an optional dictionary with additional parameters:
            'comment' - any text to add to the status update
            'version' - the version of the software under test
            'elapsed' - the duration of the test (in 5m/1h format)"""

        self.log.trace("Adding '%s' result to test %s in test run %s ..."%(status,str(testID),
                                                                str(testRunID)))
        result = {'server response':None,'succeeded':False}

        # base data packet
        data = {
            'status_id':    TEST_STATUS_TO_ID[status.lower()]
        }
        # append any additional parameters to data packet
        data.update(params)
        # post request to server
        url = self.serverURL+"/add_result_for_case/%d/%d&key=%d"%(testRunID,testID,
                                                                  self.serverKey)
        result['server response'] = self.post_request_to_server(url, data, json=True)['response dict']
        # check response
        if result['server response'] is not None: result['succeeded'] = True
        else: self.log.error("Failed to verify server test update command received.")
        # return
        return result

