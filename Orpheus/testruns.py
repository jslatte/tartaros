####################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Test Runs Submodule ###########################################################################
####################################################################################################
####################################################################################################

class TestRuns():
    """ Submodule for adding and querying test runs in TestRail. """

    def add_test_run(self, suiteID, params):
        """ Add a new test run for the given suite to active test runs in TestRail.
        'params' is an optional dictionary with additional parameters:
            'name' - the name of the test run
            'description' - any text to use in the test run description field
            'milestone_id - the TestRail ID of a milestone to associate test run with """

        self.log.trace("Adding test run for suite %s to active test runs ..."%suiteID)
        result = {'server response':None,'succeeded':False,'test run':None}

        # base data packet
        data = {}
        # append any additional parameters to data packet
        data.update(params)
        # post request to server
        url = self.serverURL+"/add_run/%d&key=%d"%(suiteID,self.serverKey)
        result['server response'] = self.post_request_to_server(url,data)['response dict']
        # check response
        if result['server response']['result']: result['succeeded'] = True
        else: self.log.trace("Failed to verify server add test run command received.")
        # parse test run ID from response
        result['test run'] = result['server response']['id']
        self.log.trace("Test Run:\t%d"%result['test run'])
        # return
        return result