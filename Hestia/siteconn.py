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
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
DB = HESTIA['database']
DB_SITES = DB['sites']
DB_SITES_TABLE = DB_SITES['table']
DB_SITES_FIELDS = DB_SITES['fields']
DB_CONLOG = DB['connection log']
DB_CONLOG_TABLE = DB_CONLOG['table']
DB_CONLOG_FIELDS = DB_CONLOG['fields']
CONNECTION_STATES = DB_CONLOG['connection states']

####################################################################################################
# Site Connectivity ################################################################################
####################################################################################################
####################################################################################################


class SiteConnectivity():
    """ Sub-library for ViM server site connection functions.
    """

    def verify_site_has_connected(self, site, max_attempts=15, allowed=True, testcase=None):
        """ Verify that a site has connected (at least once).
        INPUT
            site: the ID or name of the site.
            max attempts: the maximum number of attempts to make.
            allowed: whether the site should be able to be connected to or not.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        if allowed: self.log.debug("Verifying that site %s has connected ..." % site)
        else: self.log.debug("Verifying that site %s has not connected ..." % site)
        result = {'successful': False, 'verified': False}

        # determine site id or site name
        site_id = None
        site_name = None
        try: site_id = int(site)
        except BaseException: site_name = str(site)

        if site_id is not None and site_name is None:
            site_name = self.return_site_name_for_site(site_id)['site name']

        try:
            attempt = 1
            connected = False
            while attempt <= max_attempts and not connected:
                # query video status page
                data = {}
                response = self.query_page('video status page', data)['query response'][1:]
                # verify working or available connection status, or re-attempt
                for siteStatuses in response:
                    if (str(siteStatuses['site name']) == site_name
                        and str(siteStatuses['connection status']) == 'working')\
                    or (str(siteStatuses['site name']) == site_name
                        and str(siteStatuses['connection status']) == 'available'):
                        connected = True

                if not connected and attempt < max_attempts:
                    # try to query database
                    self.log.trace("Failed to verify site connected via page query. "
                                   "Checking database ...")
                    response = self.db.query_database_table_for_single_value(
                        self.db.db_handle, DB_CONLOG_TABLE, DB_CONLOG_FIELDS['id'],
                        DB_CONLOG_FIELDS['connection state'], CONNECTION_STATES['available'],
                        max=True
                    )['value']

                    if response is not None:
                        connect = True
                        self.log.trace("Found successful connection logged in database.")
                        break

                    self.log.trace('Failed to verify that site has connected at least once'
                                   ' (attempt %s). Re-attempting in 15 seconds ...' % attempt)
                    sleep(15)
                elif not connected and attempt == max_attempts:
                    break
                # increment
                attempt += 1

            # validate results
            if allowed and connected:
                self.log.trace('Verified that site has connected at least once.')
                result['verified'] = True
            elif allowed and not connected:
                self.log.error('Failed to verify that site has connected at least once.',)
            elif not allowed and connected:
                self.log.error('Failed to verify that site has not connected.',)
            elif not allowed and not connected:
                self.log.trace('Verified that site has not connected.')
                result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify site %s connected" % site)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result