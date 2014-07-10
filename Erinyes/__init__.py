####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from utility import read_file_into_list
import inspect
from os import getcwdu, popen
from time import sleep
from logger import Logger
from database import Database
from mapping import ERINYES
from Sisyphus import Sisyphus

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

ROOT_PATH = getcwdu() + '\\Erinyes'
CONFIG_FILE_PATH = ROOT_PATH + "\\config.ini"
DB = ERINYES['database']
DB_TABLES = DB['tables']
DB_CONNLOG = DB['connection log']
DB_CONNLOG_FIELDS = DB_CONNLOG['fields']
DB_SITES = DB['sites']
DB_SITES_FIELDS = DB_SITES['fields']
DB_CONNTYPES = DB['connection types']
DB_CONNTYPES_FIELDS = DB_CONNTYPES['fields']
DB_CONNSTATUS = DB['connection statuses']
DB_CONNSTATUS_FIELDS = DB_CONNSTATUS['fields']

log = Logger()

####################################################################################################
# Main #############################################################################################
####################################################################################################
####################################################################################################


class Site():
    """
    """

    def __init__(self, address):
        """
        """

        # default attributes
        self.site_id = None
        self.address = address
        self.available = False
        self.pinged_at_least_once = False


class Erinyes():
    """ A library of functions for pinging site availability.
    """

    def __init__(self, logger, exception_handler, sisyphus=Sisyphus):
        """
        @param logger: an initialized Logger() to inherit.
        @param exception_handler: an un-initialized ExceptionHandler() to inherit.
        @param sisyphus: an unitialized sisyphus class object.
        """

        # instance logger (initialized instance)
        self.log = logger

        # instance exception handler
        self.handle_exception = exception_handler

        # stacktrace
        self.inspect = inspect

        # define default class attributes
        self.sites_to_ping = []
        self.sites = []
        self.email_recipients = []
        self.traceroute = False
        self.multithreaded = False

        # load configuration
        self.load_config()

        # connect to erinyes database
        self.db = Database(self.log)
        self.db_handle = self.db.establish_handle_to_database()

        # initialize sisyphus
        if self.multithreaded:
            self.sisyphus = sisyphus(self.log)
        else:
            self.sisyphus = None

    def TEMPLATE(self):
        """
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def load_config(self):
        """ Load the configuration file.
        :return: a dict including
            successful - whether the function executed successfully or not.
        """

        operation = inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # read config file data
            config_data = read_file_into_list(CONFIG_FILE_PATH)['list']

            # parse data into configuration
            parameters = []
            for line in config_data:
                if 'SITES = ' in line:
                    sites = line.strip().split('SITES = ')[1].split(',')
                    parameters.append(['SITES', str(sites)])
                    for site in sites:
                        self.sites_to_ping.append(site.strip())
                if 'TRACEROUTE = ' in line:
                    if 'true' in line.lower():
                        parameters.append(['TRACEROUTE', 'True'])
                        self.traceroute = True
                if 'MULTITHREADED = ' in line:
                    if 'true' in line.lower():
                        parameters.append(['MULTITHREADED', 'True'])
                        self.multithreaded = True
                if 'RECIPIENTS = ' in line:
                    recipients = line.strip().split('RECIPIENTS = ')[1].split(',')
                    parameters.append(['RECIPIENTS', str(recipients)])
                    for recipient in recipients:
                        self.email_recipients.append(recipient.strip())

            # log parameters in output
            for param in parameters:
                self.log.trace("CONFIGURATION: %s = %s" % (param[0], param[1]))

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(self.log, e, operation="load configuration")

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def run(self):
        """
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # wrap the check availability method in a loop in case it crashes
            while True:
                self.check_availability_of_sites()
                sleep(1)

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def check_availability_of_site(self, site):
        """
        @param site: a site object that the availability will be checked for.
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            #self.log.trace("%s %s ..." % (operation.replace('_', ' '), site.address))

            while True:
                # ping the site
                if self.traceroute:
                    # using traceroute
                    response = popen('tracert -d -h 15 -w 5 %s' % site.address).read()

                else:
                    # using standard ping
                    response = popen("ping -n 1 %s" % site.address).read()

                # determine if site responded as available to ping request
                if self.traceroute and 'Request timed out.' not in response.splitlines()[-3]:
                    responded = True

                elif not self.traceroute \
                        and 'Sent = 1, Received = 1, Lost = 0 (0% loss)' in response:
                    #self.log.trace("Site %s responded." % site.address)
                    responded = True
                else:
                    responded = False

                # determine availability of site based on ping response

                # case: site pinged for first time but not available
                if not site.available and not responded and not site.pinged_at_least_once:
                    self.log.info("Site %s is not available." % site.address)
                    self.log.trace("Site %s Response:\n%s" % (site.address, str(response)))
                    site.pinged_at_least_once = True

                # case: site pinged for first time and available
                elif not site.available and responded and not site.pinged_at_least_once:
                    site.available = True
                    self.log.info("Site %s is available." % site.address)
                    self.log.trace("Site %s Response:\n%s" % (site.address, str(response)))
                    site.pinged_at_least_once = True

                # case: unavailable site now available
                elif not site.available and responded:
                    site.available = True
                    self.log.info("Site %s is available." % site.address)
                    self.log.trace("Site %s Response:\n%s" % (site.address, str(response)))

                    # log connection


                    # log new connect in database
                    #self.db.add_entry_to_table(
                    #    handle=self.db_handle,
                    #    table=DB_TABLES['connection log'],
                    #    entry={
                    #        'site id':  site.id,
                    #    }
                    #)

                # case: available site still available
                elif not site.available and not responded:
                    pass

                # case: unavailable site still unavailable
                elif site.available and responded:
                    pass

                # case: available site now unavailable
                elif site.available and not responded:
                    site.available = False
                    self.log.info("Site %s is no longer available." % site.address)
                    self.log.trace("Site %s Response:\n%s" % (site.address, str(response)))

                else:
                    self.log.warn("Unknown response '%s' from ping request." % response)

                sleep(1)

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def check_availability_of_sites(self):
        """
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # initialize an object to represent each site
            for address in self.sites_to_ping:
                site = Site(address)
                self.sites.append(site)

            if self.multithreaded:
                # create a thread loop for each site
                for site in self.sites:
                    self.sisyphus.add_process_to_thread_queue(
                        self.check_availability_of_site, (site, )
                    )
                # execute all threads
                self.sisyphus.execute_pending_threads()

            else:
                # loop pinging sites for availability
                for site in self.sites:
                    self.check_availability_of_site(site)

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result