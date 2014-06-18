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

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

ROOT_PATH = getcwdu() + '\\Erinyes'
CONFIG_FILE_PATH = ROOT_PATH + "\\config.ini"

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
        self.address = address
        self.available = False


class Erinyes():
    """ A library of functions for pinging site availability.
    """

    def __init__(self, logger, exception_handler):
        """
        @param logger: an initialized Logger() to inherit.
        @param exception_handler: an un-initialized ExceptionHandler() to inherit.
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

        # load configuration
        self.load_config()

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

            # loop pinging sites for availability
            while True:
                for site in self.sites:
                    # ping the site
                    response = popen("ping -n 1 %s" % site.address).read()

                    # determine if site responded to ping request
                    responded = False
                    if 'Sent = 1, Received = 1, Lost = 0 (0% loss)' in response:
                        #self.log.trace("Site %s responded." % site.address)
                        responded = True

                    if not site.available and responded:
                        site.available = True
                        self.log.info("Site %s is available." % site.address)

                    elif not site.available and not responded:
                        pass

                    elif site.available and responded:
                        pass

                    elif site.available and not responded:
                        site.available = False
                        self.log.info("Site %s is no longer available." % site.address)

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