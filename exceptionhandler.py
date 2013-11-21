###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from os.path import split as path_split
from sys import exc_info

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Exception Handler ################################################################################
####################################################################################################
####################################################################################################


class ExceptionHandler():
    """ Object for exception handling. """

    def __init__(self, log, e, operation=None):
        """ Initialize the exception handler object.
        @param log: an initialized logger object.
        @param e: the exception (from BaseException, e).
        @param operation: the action being attempted (that failed).
        @return: None.
        """

        # define class attributes
        self.log = log
        self.e = e
        self.operation = operation

        # handle the exception
        self.handle_exception()

        # return
        return

    def return_execution_error(self, frame=1):
        """ Return the current function being executed.
        @param frame: the integer frame in stacktrace to use (e.g., 0 would indicate this function).
        @return
            - function: the function being executed, as well as file name and line being read.
        """

        result = {'error': None}

        # parse info from execution
        exc_type, exc_obj, exc_tb = exc_info()
        fname = path_split(exc_tb.tb_frame.f_code.co_filename)[frame]
        result['error'] = ("%s, %s, %s" % (str(exc_type), str(fname), str(exc_tb.tb_lineno)))

        # return
        return result

    def handle_exception(self):
        """ Handle an exception.
        @return: None.
        """

        if self.operation is not None:
            self.log.error("Failed to %s." % self.operation)
        self.log.error(str(self.e))
        for error in self.e:
            self.log.error(str(error))
        exception = self.return_execution_error()['error']
        self.log.error("Error: %s." % exception)

        # return
        return