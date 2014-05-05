####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import inspect
from utility import return_execution_error
from config import *

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Styx (IDIS SDKs) #################################################################################
####################################################################################################
####################################################################################################


class Styx():
    """ Library for SDK interaction and testing. """

    def __init__(self, logger, dir=SDK_PATH):
        """
        @param logger: an initialized instance of a logging class to use.
        @param dir: the path to the folder containing the SDK(s).
        """

        # instance logger
        self.log = logger

        self.submodule_name = self.__class__.__name__
        self.log.info("Initializing %s submodule ..." % self.submodule_name)

        # stacktrace
        self.inspect = inspect

        # define default attributes
        self.dir = dir
        self.admin_sdk_path = self.dir + "idisadmin.dll"
        self.search_sdk_path = self.dir + "idissearch.dll"
        self.admin_sdk_version = '0.0.0.0'
        self.search_sdk_version = '0.0.0.0'
        self.watch_sdk_version = '0.0.0.0'
        self.storage_sdk_version = '0.0.0.0'

        self.log.trace("... initialized.")

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

    def TEMPLATE_FUNCTION(self, testcase=None):
        """ Description of the purpose of the function.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        @return: a data dict containing:
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
        if testcase is not None: testcase.processing = result['successful']
        return result