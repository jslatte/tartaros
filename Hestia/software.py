###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from utility import return_file_version, delete_file
from os import listdir, rmdir
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Software #########################################################################################
####################################################################################################
####################################################################################################


class Software():
    """ Sub-library for ViM software package and file interaction and testing.
    """

    def verify_idis_dlls_versions(self, testcase=None):
        """ Verify the version numbers of the IDIS DLL files.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying IDIS DLLs versions ...")
        result = {'successful': False, 'verified': False}

        try:
            # check server version
            if self.release_version < 3.2:
                version = self.return_vim_server_version()['version']
                self.determine_vim_server_release_version(version, testcase=testcase)

            # determine correct DLL version
            exp_admin_ver = None
            exp_search_ver = None
            if 3.2 <= self.release_version < 3.4:
                exp_admin_ver = "2.4.1.3"
                exp_search_ver = "2.4.0.1"
            elif 3.4 <= self.release_version:
                exp_admin_ver = "2.4.1.3"
                exp_search_ver = "2.4.1.3"

            if exp_admin_ver is not None and exp_search_ver is not None:
                self.log.trace("Server version %s uses admin DLL version %s and search DLL version %s."
                               % (self.release_version, exp_admin_ver, exp_search_ver))

                # check admin DLL version
                admin_path = "%sidisadmin.dll" % self.dir
                admin_ver = return_file_version(self.log, admin_path)['version']
                admin_verified = False
                if admin_ver == exp_admin_ver:
                    self.log.trace("Verified admin DLL version. Version %s found." % admin_ver)
                    admin_verified = True
                else:
                    self.log.error("Failed to verify admin DLL version. Version %s found." % admin_ver)

                # check search DLL version
                search_path = "%sidissearch.dll" % self.dir
                search_ver = return_file_version(self.log, search_path)['version']
                search_verified = False
                if search_ver == exp_search_ver:
                    self.log.trace("Verified search DLL version. Version %s found." % search_ver)
                    search_verified = True
                else:
                    self.log.error("Failed to verify search DLL version. Version %s found." % search_ver)

                # compile results
                if admin_verified and search_verified:
                    self.log.trace("Verified IDIS DLL versions.")
                    result['verified'] = True
                else:
                    self.log.error("Failed to verify IDIS DLL versions.")

            else:
                self.log.error("Failed to verify IDIS DLL versions. "
                               "No expected DLL versions for server version %s." % self.release_version)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify IDIS DLLs versions")

        # return
        if testcase is not None:
            testcase.processing = result['successful']
        return result

    def determine_vim_server_release_version(self, version, testcase=None):
        """ Determine the release version number for the ViM server using given version number.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            release version: the X.x formatted version of the server.
        """

        self.log.debug("Determining ViM server release version ...")
        result = {'successful': False, 'release version': None}

        try:
            # determine release version format of version returned
            version_nums = version.split('.')
            result['release version'] = float("%s.%s" % (version_nums[0], version_nums[1]))
            self.log.trace("Release version is %s." % result['release version'])

            # update Hestia variable
            self.release_version = result['release version']

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine the ViM server release version")

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.release_version = result['release version']
        return result

    def reset_storage_location(self, testcase=None):
        """ Empty all downloaded clip files from the storage location.
        INPUT:
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUTPUT:
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Resetting the storage location at %s ..." % self.storage_loc)
        result = {'successful': False}

        try:
            # make list of all files in storage location
            files = listdir(self.storage_loc)
            # remove files in storage location
            for file in files:
                file_path = self.storage_loc + file

                # delete any free-floating files, or clear out directories if not a file
                deleted = delete_file(self.log, file_path, silent_warnings=True)['verified']
                if not deleted:
                    # list files in directory
                    sub_files = listdir(file_path)

                    # delete each file in directory
                    for sub_file in sub_files:
                        sub_file_path = file_path + "\\" + sub_file

                        # delete file
                        delete_file(self.log, sub_file_path)

                    # remove directory
                    try: rmdir(file_path)
                    except BaseException, e:
                        self.handle_exception(e, operation="remove directory %s" % file_path)

            self.log.trace("Storage location reset.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="reset the storage location at %s" % self.storage_loc)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def reset_vim_server(self, testcase=None, max_attempts=5, using_custom_database=False):
        """ Reset the ViM server to freshly installed state.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
            max attempts: the maximum number of attempts to perform the operation.
            using custom database: whether using a custom database or not (should not be deleted).
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Resetting the ViM server to a fresh install state ...")
        result = {'successful': False}

        attempt = 1
        while not result['successful'] and attempt <= max_attempts:
            try:
                # stop the server
                self.stop_vim_server(testcase=testcase)

                # disconnect from database
                self.db.disconnect_from_database()
                self.db.db_handle = None

                # define booleans for all operations needed to be done
                database_deleted = False
                db_shm_deleted = False
                db_wal_deleted = False
                license_deleted = False

                if not using_custom_database:
                    # delete database files
                    database_deleted = delete_file(self.log, self.database_path)['verified']
                    db_shm_deleted = delete_file(self.log, self.database_path
                                                           + "-shm")['verified']
                    db_wal_deleted = delete_file(self.log, self.database_path
                                                           + "-wal")['verified']

                    # delete license
                    license_deleted = delete_file(self.log, self.license_path)['verified']

                # reset files and folders
                storage_reset = self.reset_storage_location()['successful']
                properties_deleted = delete_file(self.log, self.properties_path)['verified']

                if (not using_custom_database and database_deleted and db_shm_deleted
                    and db_wal_deleted and license_deleted and storage_reset and
                    properties_deleted) or (using_custom_database and storage_reset
                                                               and properties_deleted):
                    self.log.trace("Reset the ViM server.")
                    result['successful'] = True

                    # restart the server
                    self.start_vim_server(testcase=testcase)
                    self.db.connect_to_database()
                    self.db.db_handle = self.db.establish_handle_to_database()['handle']

                    # set up initial config
                    sleep(3)
                    self.log_in_to_vim(testcase=testcase, max_attempts=5)
                    self.configure_vim_system_settings(testcase=testcase)

                elif attempt <= max_attempts:
                    self.log.trace("Failed to reset the ViM server (attempt %s). "
                                   "Re-attempting in 5 seconds ..." % attempt)

                    # stop the server
                    self.stop_vim_server(testcase=testcase)


                elif attempt >= max_attempts:
                    self.log.error("Failed to reset the ViM server.")
                    break

            except BaseException, e:
                self.handle_exception(e, operation="reset the ViM server")
                result['successful'] = False

            # increment
            attempt += 1
            sleep(5)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_vim_server_version(self, testcase=None):
        """ Return the version number for the ViM server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            version: the version of the server (e.g., 3.2.12.314).
        """

        self.log.debug("Returning ViM server version ...")
        result = {'successful': False, 'version': None}

        try:
            # determine version of ViM server
            server_file_path = self.dir + "VIM.exe"
            result['version'] = return_file_version(self.log, server_file_path)['version']

            # update Hestia variable
            self.version = result['version']

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return the ViM server version")

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.version = result['version']
        return result