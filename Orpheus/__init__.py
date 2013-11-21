###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

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