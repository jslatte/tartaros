###################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import CONNECTION_STATE_TO_ID, STATUS_INFO, DISK_INFO
from ctypes import WinDLL, c_int, c_wchar_p, c_bool, c_void_p, POINTER, byref
import inspect

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# SDK ##############################################################################################
####################################################################################################
####################################################################################################


class SDK():
    """ Object for assigning specific SDK connection instances (for connecting to DVRs).
    """

    def __init__(self, logger, exception_handler, sdk_type, sdk_path, testcase=None):
        """
        @param logger: an initialized instance of a logging class to use.
        @param exception_handler: the global exception handler.
        @param sdk_type: the type of SDK to be used (e.g., admin, search, watch, storage).
        @param sdk_path: the filepath to the SDK.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        """

        # instance logger
        self.log = logger

        self.log.info("Initializing %s SDK object ..." % sdk_type)

        # stacktrace
        self.inspect = inspect

        # exception handler
        self.handle_exception = exception_handler

        # define default attributes
        self.sdk_type = sdk_type
        self.sdk_path = sdk_path
        self.testcase = testcase

        # tracked attributes
        self.handle = CONNECTION_STATE_TO_ID['indeterminant']
        self.channel = CONNECTION_STATE_TO_ID['indeterminant']
        self.flag = CONNECTION_STATE_TO_ID['indeterminant']

        # load DLL
        self.dll = WinDLL(self.sdk_path)

    def TEMPLATE(self, handle=None, channel=None):
        """ <NEEDS DESCRIPTION>
        @param handle: a specific handle to use, otherwise defaults self.handle.
        @param channel: a specific channel to use, otherwise defaults to self.channel.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [c_int, c_int]

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if channel is None: channel = self.channel
            params = []

            # execute SDK function
            response = _funct(handle, channel, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def initialize(self):
        """ Initialize the SDK.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
            'handle' - the initialized handle to the SDK.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None, 'handle': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))

            # execute SDK function
            response = _funct()
            self.log.trace("... response: %s ..." % response)
            result['response'] = response
            result['handle'] = response
            self.handle = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def startup(self, max_channels=16, max_callback_channels=5, callback_port=8201):
        """ <DESCRIPTION NEEDED>
        @param max_channels: <DESCRIPTION NEEDED>
        @param max_callback_channels: <DESCRIPTION NEEDED>
        @param callback_port: <DESCRIPTION NEEDED>
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))

            # define SDK function parameters (ctypes)
            handle = self.handle
            params = [max_channels, max_callback_channels, callback_port]

            # execute SDK function
            response = _funct(handle, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def registerCallback(self, message_id, callback_code, handle=None):
        """ <DESCRIPTION NEEDED>
        @param message_id: <DESCRIPTION NEEDED>
        @param callback_code: <DESCRIPTION NEEDED>
        @param handle: (optional) a specific handle to use, otherwise uses default self.handle.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            params = [message_id, callback_code]

            # execute SDK function
            _funct(handle, *params)

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def connect(self, site_name, site_ip, username='admin', password='', admin_port=8200,
                watch_port=8016, search_port=10016, encrypted=False, attachment=None, handle=None):
        """ Registers a connection configuration for connecting to a DVR (does not actually connect).
        @param site_name: the name of the DVR to connect to.
        @param site_ip: the IP address of the DVR to connect to.
        @param username: the login username for accessing the DVR.
        @param password: the login password for accessing the DVR.
        @param admin_port: the admin port of the DVR.
        @param watch_port: the watch port of the DVR.
        @param search_port: the search port of the DVR.
        @param encrypted: <DESCRIPTION NEEDED>
        @param attachment: <DESCRIPTION NEEDED>
        @param handle: (optional) a specific handle to use, otherwise uses default self.handle.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
            'channel' - the channel opened to the DVR.
        NOTE: Takes a few seconds to connect as a subprocess via the DLL.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None, 'channel': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [
                c_int, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int, c_int, c_bool, c_void_p
            ]
            #_funct.restype = c_int

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if self.sdk_type.lower() == 'admin':
                params = [site_name, site_ip, username, password, admin_port, watch_port,
                          encrypted, attachment]
            else:
                raise AssertionError("Not implemented for SDK type '%s'." % self.sdk_type)

            # execute SDK function
            response = _funct(handle, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response
            result['channel'] = response
            self.channel = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def isConnected(self, handle=None, channel=None):
        """ <NEEDS DESCRIPTION>
        @param handle: a specific handle to use, otherwise defaults self.handle.
        @param channel: a specific channel to use, otherwise defaults to self.channel.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
            'connected' - whether the SDK (subprocess) has connected to the DVR or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None, 'connected': False}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [c_int, c_int]
            #_funct.restype = c_bool

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if channel is None: channel = self.channel
            params = []

            # execute SDK function
            response = _funct(handle, channel, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response
            result['connected'] = bool(response)

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def requestStatus(self, handle=None, channel=None):
        """ <NEEDS DESCRIPTION>.
        @param handle: a specific handle to use, otherwise defaults self.handle.
        @param channel: a specific channel to use, otherwise defaults to self.channel.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
            'status' - the status returned by the SDK.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [c_int, c_int]
            #_funct.restype = c_bool

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if channel is None: channel = self.channel
            params = []

            # execute SDK function
            response = _funct(handle, channel, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def getStatus(self, status_info=None, handle=None, channel=None):
        """ <NEEDS DESCRIPTION>
        @param status_info: <NEEDS DESCRIPTION>
        @param handle: a specific handle to use, otherwise defaults self.handle.
        @param channel: a specific channel to use, otherwise defaults to self.channel.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [c_int, c_int, POINTER(STATUS_INFO)]

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if channel is None: channel = self.channel
            if status_info is None: status_info = STATUS_INFO()
            params = [byref(status_info)]

            # execute SDK function
            response = _funct(handle, channel, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def requestRemoteDeviceInfo(self, handle=None, channel=None):
        """ <NEEDS DESCRIPTION>
        @param handle: a specific handle to use, otherwise defaults self.handle.
        @param channel: a specific channel to use, otherwise defaults to self.channel.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [c_int, c_int]

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if channel is None: channel = self.channel
            params = []

            # execute SDK function
            response = _funct(handle, channel, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result

    def getRemoteDiskInfo(self, disk_info, length, rlen, handle=None, channel=None):
        """ <NEEDS DESCRIPTION>
        @param disk_info: an initialized instance of the DISK_INFO structure (see mapping).
        @param length: <NEEDS DESCRIPTION>
        @param rlen: a pointer to a c_int (for?).
        @param handle: a specific handle to use, otherwise defaults self.handle.
        @param channel: a specific channel to use, otherwise defaults to self.channel.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the raw SDK response.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': None}

        try:
            self.log.trace("calling '_%s' ..." % operation.replace('_', ' '))

            # define SDK function(s) to call (by type)
            _funct = eval("self.dll.%s_%s" % (self.sdk_type.lower(), operation))
            _funct.argtypes = [c_int, c_int, POINTER(DISK_INFO), c_int, POINTER(c_int)]

            # define SDK function parameters (ctypes)
            if handle is None: handle = self.handle
            if channel is None: channel = self.channel
            params = [byref(disk_info), length, rlen]

            # execute SDK function
            response = _funct(handle, channel, *params)
            self.log.trace("... response: %s ..." % response)
            result['response'] = response

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if self.testcase is not None: self.testcase.processing = result['successful']
        return result