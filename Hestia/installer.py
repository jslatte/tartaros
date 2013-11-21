###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import HESTIA
from os import getcwdu, listdir, system, path
from utility import move_up_windows_path
from wmi import WMI
from shutil import rmtree

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Installer ########################################################################################
####################################################################################################
####################################################################################################


class Installer():
    """ Sub-library for ViM server installer.
    """

    def determine_vim_server_msi_path(self, version=None, testcase=None):
        """ Determine the path to the ViM server MSI file.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            path: the path to the MSI file.
            build: the build number of the MSI file.
        """

        self.log.debug("Determining file path of ViM Server MSI ...")
        result = {'successful': False, 'path': None, 'build': None}

        try:
            # determine file path
            currentDirectory = getcwdu()
            if version is None:
                # use default testing artifact (from compiled development build)
                filePath = move_up_windows_path(currentDirectory,2)['path']+"\\artifacts\\"
            else:
                # use specified version in test resources folder
                filePath = "C:\\Program Files (x86)\\ViM\\test resources\\ViM Releases\\Server\\"
                # determine name of server MSI file
            fileName = None
            self.log.trace("Determining file name of ViM Server MSI ...")
            files = listdir(filePath)
            self.log.trace("Files found:\t%s"%str(files))
            if files is not None and files != []:
                for f in files:
                    # if looking for only ViM server MSI in artifacts folder
                    if version is None and "VIMServer" in str(f): fileName = f
                    # if looking for specified version MSI in test resources folder
                    if version is not None and str(version) in str(f): fileName = f
                self.log.trace("MSI File Path:\t%s%s"%(filePath,fileName))
            else:
                self.log.trace("VIM Server MSI file not found.")
                return {'path':None,'build':None}
            # parse file name to determine version/build number (split along '-' character in file name)
            if version is None:
                # return build only if using default testing artifact (to update test line number)
                try:
                    build = fileName.split('-')[1]
                    self.log.trace("Build:\t%s"%build)
                except BaseException, e:
                    self.log.trace("Failed to determine build number from MSI file.")
                    build = None
            else: build = None
            # return file path
            if filePath is not None and fileName is not None:
                result['path'] = "%s%s"%(filePath,fileName)
                result['build'] = build
            else:
                self.log.warn("VIM Server MSI file not found.")

            self.log.trace("Determined file path of ViM server MSI.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine file path of ViM server MSI")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def install_vim_server(self, path=None, build=None, version=None, testcase=None):
        """ Install ViM server MSI in given path with specified version/build number.
        If no path given, will use default testing path and build.
        If build given (or determined using default), will send message to TeamCity
            to update test line number.
        INPUT
            path: the path to the MSI server installer file.
            build: the override build number to use when declaring build under test.
            version: the release version of the software to use.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        # determine file path if not specified
        if path is None:
            response = self.determine_vim_server_msi_path(version)
            path = response['path']
            build = response['build']

        self.log.debug("Installing ViM Server from %s ..."%path)
        result = {'successful': False, 'verified': False}

        try:
            if path is not None and path is not False:
                # install ViM server through dos command
                system('C:\Windows\System32\MSIEXEC.exe /I "%s" /QN /norestart'%path)
                # verify ViM installed
                self.build = self.return_vim_server_version()['version']
                self.version = self.build
                self.release_version = \
                    self.determine_vim_server_release_version(self.version)['release version']
                if version is not None:
                    # verify against given version if specified
                    result['verified'] = self.verify_vim_installed(version)['verified']
                else:
                    result['verified'] = self.verify_vim_installed(self.build)['verified']

                if result['verified']: self.log.trace("Installed ViM server %s." % self.version)

            else:
                self.log.error("Failed to install ViM Server. Installer not found.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="install ViM server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_vim_installed(self, version=None, testcase=None):
        """ Verify that the ViM server is installed.
        INPUT
            version: the version of the software to verify as installed.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying ViM Server installed ...")
        result = {'successful': False, 'verified':False}

        try:
            # check for server application (by checking server version)
            if self.version is not None:
                self.log.trace("Verified ViM Server installed.")
                if version is not None and str(version) in str(self.version):
                    self.log.trace("Verified correct ViM Server version installed.")
                    result['verified'] = True
                elif version is None:
                    result['verified'] = True
                else:
                    self.log.error("Failed to verify that the correct ViM Server was installed.")
                    result['verified'] = False
            else:
                self.log.error("Failed to verify ViM Server was installed.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify ViM installed")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def uninstall_vim_server(self, testcase=None):
        """ Uninstall the ViM server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Uninstalling ViM Server ...")
        result = {'successful': False, 'verified': False}

        try:
            # stop server
            self.stop_vim_server()

            # uninstall server (through wmi)
            c = WMI()
            productName = "ViM Server"
            self.log.trace("Searching for installed copies of ViM Server ...")
            for product in c.Win32_Product(Name = productName):
                self.log.trace("ViM Server installation found. Uninstalling ...")
                product.Uninstall()
            # verify ViM was uninstalled
            result['verified'] = self.verify_vim_uninstalled()['verified']

            # if failed to uninstall, try doing it using build number in expected location
            if not result['verified']:
                self.log.warn("Failed to uninstall ViM server. Re-attempting using server package.")
                path = move_up_windows_path(getcwdu(),2)['path']+"\\artifacts\\"
                path += "VIMServer.msi"
                system('C:\Windows\System32\MSIEXEC.exe /x "%s" /QN /norestart'%path)
                # verify ViM was uninstalled
                result['verified'] = self.verify_vim_uninstalled()['verified']

            # clean up files
            self.cleanup_installed_files()

            if result['verified']: self.log.trace("Uninstalled ViM server.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="uninstall ViM server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_vim_uninstalled(self, testcase=None):
        """ Verify ViM is not installed.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying ViM Server uninstalled ...")
        result = {'successful': False, 'verified':False}

        try:
            # check for server application (by checking server executable)
            if not path.exists(self.server_exe_path):
                self.log.trace("Verified ViM Server uninstalled.")
                result['verified'] = True
            else:
                self.log.error("Failed to verify ViM Server was uninstalled.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify ViM uninstalled")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def cleanup_installed_files(self, testcase=None):
        """ Cleanup any leftover files in installation folder.
        """

        self.log.debug("Cleaning up installed files ...")
        result = {'successful': False}

        try:
            # delete logs folder
            if path.exists(self.log_folder_path):
                rmtree(self.log_folder_path)
                self.log.trace("Log files removed.")
            else: self.log.trace("Log files folder not found.")

            # delete Diagnostics folder
            if path.exists(self.diag_folder_path):
                rmtree(self.diag_folder_path)
                self.log.trace("Diagnostic files removed.")
            else: self.log.trace("Diagnostic files folder not found.")

            self.log.trace("Cleaned up installed files.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="clean up installed files")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result