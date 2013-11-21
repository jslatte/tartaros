###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from time import sleep
from mapping import HESTIA
from utility import return_execution_error, verify_file_does_not_exist
from utc import UTC
from clipclassification import ClipClassification
from clips import Clips
from database import Database
from drivestatus import DriveStatus
from emailnotification import EmailNotification
from events import Events
from http import HTTP
from installer import Installer
from licenseconfig import  LicenseConfiguration
from pagequeries import PageQueries
from server import Server
from session import Session
from software import Software
from siteconfig import SiteConfiguration
from siteconn import SiteConnectivity
from sitegroupconfig import SiteGroupConfiguration
from statusemailparser import StatusEmailParser
from sysconfig import SystemConfiguration
from userconfig import UserConfiguration

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

DEFAULT_BIN_LOC = HESTIA['default bin location']
DEFAULT_STORAGE_LOC = HESTIA['default storage location']
DEFAULT_SERVER_URL = HESTIA['default server url']

####################################################################################################
# Hestia (ViM) #####################################################################################
####################################################################################################
####################################################################################################


class Hestia(ClipClassification, Clips, DriveStatus, EmailNotification, Events, HTTP, Installer,
    LicenseConfiguration, PageQueries, Server, Session, Software, SiteConfiguration, SiteConnectivity,
    SiteGroupConfiguration, SystemConfiguration, UserConfiguration):
    """ Library for ViM interaction and testing. """

    def __init__(self, logger, app_db, dir=DEFAULT_BIN_LOC, storage_loc=DEFAULT_STORAGE_LOC,
                 server_url=DEFAULT_SERVER_URL):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
            app db: An instance of the application database.
            dir: the path to the bin\ installation folder.
            storage_loc: the path to the folder where video is/will be stored.
            server_url: the server url.
        """

        # instance logger
        self.log = logger

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

        # define default attributes
        self.dir = dir
        self.storage_loc = storage_loc
        self.server_url = server_url
        self.version = "1.0.0.0"
        self.release_version = 1.0

        # general-use file paths
        self.server_exe_path = self.dir + "VIM.exe"
        self.database_path = self.dir + "VIM.db"
        self.license_path = self.dir + "VIM.lic"
        self.properties_path = self.dir + "VIM.properties"
        self.log_folder_path = self.dir + "logs\\"
        self.diag_folder_path = self.dir + "Diagnostics\\"

        # session tracking
        self.logged_in_user_name = 'admin'
        self.logged_in_user_password = 'password'

        # site tracking
        self.site_id = None
        self.site_name = None
        self.site_settings = None
        self.site2_id = None
        self.site2_name = None
        self.site2_settings = None

        # imap connection
        self.imap_connection = None
        self.imap_handle = None

        # instance UTC
        self.utc = UTC(self.log)

        # instance application database
        self.app_db = app_db

        # instance ViM database
        self.db = Database(self.log, self.database_path)

        # instance status email aprser
        self.status_email_parser = StatusEmailParser(self.log)

    def setup_server_for_manual_testing(self, license_type='full'):
        """ Set up a server installation for manual testing.
        INPUT
            license type: the type of license of configure for the server.
        """

        # version the instance
        version = self.return_vim_server_version()['version']
        self.determine_vim_server_release_version(version)

        # establish database handle
        self.db.connect_to_database()
        self.db.db_handle = self.db.create_database_handle()['handle']

        # configure initial system settings
        self.log_in_to_vim()
        self.configure_vim_system_settings()

        # configure license
        self.configure_vim_license(license_type)

    def wait(self, seconds, testcase=None):
        sleep(int(seconds))

    def verify_file_does_not_exist(self, path, testcase=None):
        result = {'verified': verify_file_does_not_exist(self.log, str(path))['verified']}
        return result

    def verify_testcase_based_on_processing_status(self, testcase):
        """ Pass the current testcase if it has processed without error.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUTPUT
            verified: whether the operation was verified or not.
        """

        result = {'verified': False}

        if testcase.processing:
            self.log.info("Passing successfully processed test case.")
            result['verified'] = True
        else:
            self.log.error("Failing testcase due to unsuccessful processing.")
            result['verified'] = False

        # return
        return result

    def execute_function_expecting_failure(self, function, arguments): pass

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
        """
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug(" ...")
        result = {'successful': False, 'verified': False}

        try:

            self.log.trace("")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result