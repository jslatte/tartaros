###################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from config import *
from ctypes import WinDLL
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

    def __init__(self, logger, sdk_type, sdk_path, dvr_name, dvr_ip, testcase=None):
        """
        @param logger: an initialized instance of a logging class to use.
        @param sdk_type: the type of SDK to be used (e.g., admin, search, watch, storage).
        @param sdk_path: the filepath to the SDK.
        @param dvr_name: the name of the DVR being connected to.
        @param dvr_ip: the IP address of the DVR being connected to.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        """

        # instance logger
        self.log = logger

        self.log.info("Configuring %s connection to %s ..." % (sdk_type, str((dvr_name, dvr_ip))))

        # define default attributes
        self.sdk_type = sdk_type
        self.sdk_path = sdk_path
        self.dvr_name = dvr_name
        self.dvr_ip = dvr_ip

        # load DLL
        self.dll = WinDLL(self.sdk_path)

    def method1(self): pass
    def method2(self): pass