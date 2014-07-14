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

    def __init__(self, log, e=None, operation=None):
        """ Initialize the exception handler object.
        @param log: an initialized logger object.
        @param e: the exception (from BaseException, e).
        @param operation: the action being attempted (that failed).
        @return: None.
        """

        # define class attributes
        self.log = log

        # handle the exception
        if e is not None or operation is not None:
            self.handle_exception(e, operation)

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

    def handle_exception(self, e=None, operation=None):
        """ Handle an exception.
        @return: None.
        """

        if operation is not None:
            self.log.error("Failed to %s." % operation)
        self.log.error(str(e))
        if e is not None:
            for error in e:
                self.log.error(str(error))
        exception = self.return_execution_error()['error']
        self.log.error("Error: %s." % exception)

        # return
        return