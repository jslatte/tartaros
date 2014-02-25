###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from os import path, system
from subprocess import Popen, STDOUT
from win32service import OpenSCManager, SERVICE_WIN32, SERVICE_STATE_ALL, EnumServicesStatus
from win32con import GENERIC_READ
from time import sleep
from utility import read_file_into_list, write_list_to_file
from mapping import HESTIA

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
RUN_CLEANUP_PATH = SERVER['run cleanup path']

####################################################################################################
# Server ###########################################################################################
####################################################################################################
####################################################################################################


class Server():
    """ Sub-library for ViM server interaction and testing.
    """

    def update_number_of_vim_site_connections(self, num_handles, num_channels, testcase=None):
        """ Update the number of handles/channels used in connecting to sites.
            INPUT
                num handles: number of handles to configure.
                num channels: number of channels to configure.
                testcase: a testcase object supplied when executing function as part of a testcase step.
            OUPUT
                successful: whether the function executed successfully or not.
                verified: whether the operation was verified or not.
            """

        self.log.debug("Updating number of ViM site connections with %s handles and %s channels ..."
                       % (num_handles, num_channels))
        result = {'successful': False}

        try:
            # read VIM.properties file into list
            properties_data = read_file_into_list(self.properties_path)['list']

            # read properties data list into updated data list
            updated_data = []
            for line in properties_data:

                # update handles if in line
                if "VIM.handles" in line: line = "VIM.handles: %d\n" % num_handles

                # update channels if in line
                if "VIM.channels" in line: line = "VIM.channels: %d\n" % num_channels

                # write line to updated data list
                updated_data.append(line)

            # write updated data list to properties file
            write_list_to_file(self.properties_path, updated_data)

            self.log.trace("Updated number of ViM site connections.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="update number of ViM site connections")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_server_running_as_service(self, testcase=None):
        """ Verify that the server is running as a service.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying the server is running as a service ...")
        result = {'successful': False, 'verified': False}

        try:
            # check if server running
            running = self.check_if_vim_server_is_running()['service']

            # verify
            if running:
                self.log.trace("Verified the server is running as a service.")
                result['verified'] = True
            else:
                self.log.error("Failed to verify that the server is running as a service.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify server running as a service")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def check_if_vim_server_is_running(self, testcase=None):
        """ Check to see if ViM server is running.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUTPUT
            successful: whether the function executed successfully or not.
            service: whether the server was found running as a server or not (T/F).
            process: whether the server was found running as a process or not (T/F).
        """

        self.log.debug("Checking if ViM server running ...")
        result = {'successful': False, 'service': False, 'process': False}

        try:
            # open service control manager in generic read mode
            hscm = OpenSCManager(None, None, GENERIC_READ)

            # enumerate services of specified type and state
            type = SERVICE_WIN32
            state = SERVICE_STATE_ALL

            statuses = EnumServicesStatus(hscm, type, state)
            for (short_name, desc, status) in statuses:
                # return True if ViM Server found and running
                #   *status shows up as (16, 4, 5, 0, 0, 0, 0) if server is running
                if desc == "ViM Server" and str(status) == "(16, 4, 5, 0, 0, 0, 0)":
                    self.log.trace("ViM Server found running as a service.")
                    result['service'] = True
                # return False if ViM Server found but not running
                elif desc == "ViM Server":
                    self.log.trace("ViM Server process found.")
                    result['process'] = True

            # return False if ViM Server not found and running
            self.log.trace("ViM Server not found and running.")

            self.log.trace("Checked that ViM server was running.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="check that the ViM server is running")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def restart_vim_server(self, testcase=None, mode='service'):
        """ Restart the ViM Server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            mode: the mode to start the server in (e.g., process or service).
        OUTPUT:
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Restarting the ViM server ...")
        result = {'successful': False}

        try:
            # stop server
            self.stop_vim_server(testcase=testcase, mode='process')
            # start server
            self.start_vim_server(testcase=testcase, mode=mode)

            self.log.trace("Restarted the ViM server.")
            result['successful'] = True
        except BaseException, e: self.handle_exception(e, operation="restart the ViM server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def run_cleanup(self, testcase=None):
        """ Run server bin cleanup function.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the bin cleanup was verified as run or not.
        """

        self.log.debug("Running bin cleanup function ...")
        result = {'successful': False, 'verified':False}

        try:
            # run cleanup
            url = self.server_url + RUN_CLEANUP_PATH
            response = self.get_http_request(url)['response']
            # verify cleanup run
            if response.lower() == 'ok':
                self.log.trace("Verified bin cleanup function run.")
                result['verified'] = True
            else:
                self.log.error("Failed to verify bin cleanup function run.")

            self.log.trace("Bin cleanup run.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="run bin cleanup")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def start_vim_server(self, testcase=None, mode='service'):
        """ Start the ViM server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            mode: the mode to start the server in (e.g., process or service).
        OUTPUT:
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Starting the ViM server as a %s ..." % mode)
        result = {'successful': False}

        # start ViM server in specified mode (loop attempts)
        try:
            i = 0
            while i < 5:
                if mode.lower() == 'service':
                    self.log.trace("Starting ViM server as a service ...\n")
                    system("D:\Windows\System32\NET.exe START ViMServer")
                    running = self.check_if_vim_server_is_running()['service']
                elif mode.lower() == 'process':
                    self.log.trace("Starting ViM server as a process ...\n")
                    exe_path = self.dir + "vim.exe"
                    if not path.exists(exe_path):
                        self.log.error('Invalid ViM Path: %s' % path)

                    Popen(exe_path, stderr=STDOUT)
                    running = self.check_if_vim_server_is_running()['process']
                else:
                    self.log.error("Invalid mode specified for starting ViM server. "
                                   "Failed to start server.")
                    break

                # handle attempts in loop
                if running is False and i >= 5:
                    self.log.error("ViM server not found running. Failed to start server.")
                    break
                elif running is False and i < 5:
                    self.log.trace("ViM server not found running (attempt %d). Re-attempting ..." % i)
                    sleep(5)
                    i += 1
                elif running is True:
                    self.log.trace("ViM server found running.")
                    result['successful'] = True
                    break

            self.log.trace("Started the ViM server.")
            result['successful'] = True
        except BaseException, e: self.handle_exception(e, operation="start the ViM server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def stop_vim_server(self, testcase=None, mode='process'):
        """ Stop ViM server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            mode: the mode to start the server in (e.g., process or service).
        OUTPUT:
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Stopping the ViM server ...")
        result = {'successful': False}

        try:
            # stop ViM server in specified mode
            if mode.lower() == 'service':
                running = self.check_if_vim_server_is_running()
                if running:
                    self.log.trace("Stopping ViM server service ...\n")
                    system("C:\Windows\System32\NET.exe STOP ViMServer")
                    running = self.check_if_vim_server_is_running()
                    if running is True:
                        self.log.error("ViM server found running as a service. Failed to stop server.")
                    else:
                        self.log.trace("ViM server not found running as a service.")
                        result['successful'] = True
            elif mode.lower() == 'process':
                self.log.trace("Killing ViM process ...\n")
                system('taskkill /F /IM VIM.exe')
                result['successful'] = True
            else:
                self.log.error("Invalid mode %s specified for stopping ViM server. "
                               "Failed to stop server." % mode)

            self.log.trace("Stopped the ViM server.")
            result['successful'] = True
        except BaseException, e: self.handle_exception(e, operation="stop the ViM server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result