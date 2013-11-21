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
from buildcounters import BuildCounters
from building import Building
from maps import SERVER_URL, AUTHENTICATION
from utility import return_execution_error

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER_URL = SERVER_URL
AUTHENTICATION = AUTHENTICATION

####################################################################################################
# Minos (Build Management) #########################################################################
####################################################################################################
####################################################################################################


class Minos(API, BuildCounters, Building):
    """ Library for build management. """

    def __init__(self, logger):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # instantialize logger
        self.log = logger

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

        # properties
        self.serverURL = SERVER_URL
        self.auth = AUTHENTICATION

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
        self.log.error("Error: %s." % return_execution_error()['error'])