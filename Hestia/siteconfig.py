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
from utility import translate_dict_to_list_parameters, translate_list_parameters_to_dict, \
    return_machine_ip_address
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
SITECON = SERVER['site configuration']
SITECON_QUERY_PATH = SITECON['query path']
SITECON_MODIFY_PATH = SITECON['modify path']
SITECON_TOGGLE_STATUS_PATH = SITECON['de/activation path']
SITECON_FIELDS = SITECON['fields']
SITECON_COLUMNS = SITECON['columns']
SITECON_3_3_COLUMNS = SITECON['columns 3.3']
DB = HESTIA['database']
DB_SITES = DB['sites']
DB_SITES_TABLE = DB_SITES['table']
DB_SITES_FIELDS = DB_SITES['fields']
DB_GROUP = DB['site groups']
DB_GROUP_TABLE = DB_GROUP['table']
DB_GROUP_FIELDS = DB_GROUP['fields']

####################################################################################################
# Site Configuration ###############################################################################
####################################################################################################
####################################################################################################


class SiteConfiguration():
    """ Sub-library for ViM server site configuration.
    """

    def update_all_sites_to_local_machine_sites(self, testcase=None):
        """ Update all sites to a local machine site (pointing to local IP address)
        NOTE: For use with Tantalus DVR simulation.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Updating all sites to local machine sites ...")
        result = {'successful': False, 'verified': False}

        try:
            # determine local machine ip
            local_machine_ip = return_machine_ip_address(self.log)['ip address']

            # update site in database
            handle = self.db.db_handle
            sql = "UPDATE %s SET %s = '%s'" % (DB_SITES_TABLE, DB_SITES_FIELDS['ip address'],
                                                local_machine_ip)

            self.db.execute_SQL(handle, sql)

            self.log.trace("Updated all sites %s to local machine sites.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="update all sites to local machine sites.")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def configure_local_machine_site(self, testcase=None):
        """ Configure a site with the local machine's IP address.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Configuring local machine site ...")
        result = {'successful': False, 'verified': False}

        try:
            # determine local machine IP address
            ip_address = return_machine_ip_address(self.log)['ip address']

            # define custom site settings
            settings = [
                ['site name', 'Local Depot'],
                ['ip address', ip_address],
                ['dvr username', 'admin'],
            ]

            # configure site
            self.configure_remote_site(settings)

            if result['verified']:
                self.log.trace("Configured local machine site.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_site_name_for_site(self, site_id, testcase=None):
        """ Return the site name for given site.
        INPUT
            site id: id of the site for which to return the site name.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            site name: name of the site returned.
        """

        self.log.debug("Returning Site Group Name for site %s ..." % site_id)
        result = {'successful': False, 'site name': None}

        try:
            # determine site name
            handle = self.db.db_handle
            result['site name'] = self.db.query_database_table_for_single_value(handle,
                DB_SITES_TABLE, DB_SITES_FIELDS['site name'], DB_SITES_FIELDS['id'],
                site_id)['value']

            self.log.trace("Returned site name for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return site name for site %s" % site_id)

        # return
        if testcase is not None:
            testcase.site_name = result['site name']
            testcase.processing = result['successful']
        return result

    def add_number_of_fake_sites_with_some_live_sites(self, num_sites, testcase=None):
        """ Add number of fake sites with some live sites (added at the end).
        INPUT
            num sites: the number of sites to add (all of which will be fake but for the last).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Add %s fake sites with some live sites ..." % num_sites)
        result = {'successful': False, 'verified': False}

        try:
            # add fake sites
            self.add_number_of_fake_sites(num_sites, testcase)

            # change some to live sites
            self.change_last_added_sites_to_live_sites(testcase)

            self.log.trace("Added %s fake sites with some live sites." % num_sites)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="add %s fake sites with some live sites" % num_sites)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def add_number_of_fake_sites(self, num_sites, start_id=1, ip_schema='172.22.60.', start_ip=1,
                                 testcase=None):
        """ Add a number of fake sites (IP address points nowhere).
        INPUT
            num sites: number of fake sites to add.
            testcase: a testcase object supplied when executing function as part of a testcase step.
            start id: an optional id with which to start (for adding additional fake sites to a previous list).
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Adding %s fake sites ..." % num_sites)
        result = {'successful': False, 'verified': False}

        try:
            for i in range(start_id, (start_id + num_sites)):

                if i < 10: site_name = 'T-Depot 000%d' % i
                elif 10 <= i < 100: site_name = 'T-Depot 00%d' % i
                elif 100 <= i < 1000: site_name = 'T-Depot 0%d' % i
                elif 1000 <= i < 10000: site_name = 'T-Depot %d' % i

                ip_address = '%s%d' % (ip_schema, start_ip)
                start_ip += 1

                settings = [['site name', site_name], ['ip address', ip_address]]
                self.configure_remote_site(settings)

            self.log.trace("Added %s fake sites." % num_sites)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="add %s fake sites" % num_sites)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def change_last_added_sites_to_live_sites(self, testcase=None):
        """ Change the last sites added from fake to live sites (for use with large amount of dummy sites in
        connectivity testing).
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Changing the last added sites to live sites ...")
        result = {'successful': False}

        try:
            # determine number of sites
            num_sites = self.return_number_of_sites()['num sites']

            # tracking int
            x = 0
            # valid IP suffixes
            ips = [131, 132, 133, 134, 135, 136, 137, 138, 139, 140]

            # add live sites with valid IP suffixes (update last added sites)
            for j in range(num_sites-(len(ips)-1), num_sites+1):

                # determine IP to update
                site_id = j
                ip = ips[x]
                ip_address = '172.22.48.%d' % ip

                # update site
                settings = [['id', site_id], ['ip address', ip_address]]
                self.configure_remote_site(settings)

                # increment
                x += 1

            self.log.trace("Changed the last added sites to live sites.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="change the last added sites to live sites")

        # return
        if testcase is not None:
            testcase.site_id = site_id
            testcase.processing = result['successful']
        return result

    def return_number_of_sites(self, testcase=None):
        """ Return the number of sites added from the server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            num sites: number of sites returned from the server
        """

        self.log.debug("Returning number of sites ...")
        result = {'successful': False, 'num sites': None}

        try:
            # determine site configuration map (per version)
            if float(self.release_version) <= 3.3:
                SERVER_FIELD_NAMES = SITECON_3_3_COLUMNS
            else: SERVER_FIELD_NAMES = SITECON_COLUMNS
            # query server for site settings
            url = self.server_url + SITECON_QUERY_PATH
            response = self.query_server_table(url, SERVER_FIELD_NAMES)['response']

            # number of sites should be first entry in response, with 'id' key
            result['num sites'] = int(response[0]['id'])

            self.log.trace("Returned number of sites: %s." % result['num sites'])
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return number of sites")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_site_group_for_site(self, site_id, testcase=None):
        """ Return the site group for given site.
        INPUT
            site id: id of the site for which to return the site group.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Returning Site Group Name for site %s ..." % site_id)
        result = {'successful': False, 'site group name': None, 'site group id': None}

        try:
            # determine site group ID
            handle = self.db.db_handle
            result['site group id'] = self.db.query_database_table_for_single_value(handle,
                DB_SITES_TABLE, DB_SITES_FIELDS['site group id'], DB_SITES_FIELDS['id'],
                site_id)['value']

            # determine site group name
            result['site group name'] = self.db.query_database_table_for_single_value(handle,
                DB_GROUP_TABLE, DB_GROUP_FIELDS['site group name'], DB_GROUP_FIELDS['id'],
                result['site group id'])['value']

            self.log.trace("Returned site group for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return site group for site %s" % site_id)

        # return
        if testcase is not None:
            testcase.site_group_id = result['site group id']
            testcase.site_group_name = result['site group name']
            testcase.processing = result['successful']
        return result

    def return_bin_timer_for_site(self, site_id, bin, testcase=None):
        """ Return the expiration time for given site.
        INPUT
            site id: id of the site for which to return the bin timer.
            bin: the bin for which to return the timer.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            bin timer: the bin timer returned.
        """

        self.log.debug("Returning expiration time for %s bin of site %s ..." % (bin, site_id))
        result = {'successful': False, 'bin timer': None}

        try:
            # determine site group for site
            siteGroupID = self.return_site_group_for_site(site_id)['site group id']
            # determine given bin timer for site
            handle = self.db.db_handle
            result['bin timer'] = self.db.query_database_table_for_single_value(handle, DB_GROUP_TABLE,
                DB_GROUP_FIELDS[bin.lower()], DB_GROUP_FIELDS['id'], siteGroupID)['value']

            self.log.trace("Returned expiration time for %s bin." % bin)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return expiration time for %s bin" % bin)

        # return
        if testcase is not None:
            testcase.bin_timer = result['bin timer']
            testcase.processing = result['successful']
        return result

    def configure_all_lab_depot_sites(self, testcase=None):
        """ Configure all sites from the lab depot.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Configuring all lab depot sites ...")
        result = {'successful': False, 'verified': False}

        try:
            # track failures
            failures = 0

            for i in range(1, 28):
                # define site settings
                settings = [
                    ['dvr username', 'admin'],
                    ['dvr password', '']
                ]
                name_id = '000%d' % i if i < 10 else '00%d' % i
                settings.append(['site name', 'DEPOT %s' % name_id])
                settings.append(['ip address', '172.22.48.%s' % i])

                # configure site
                verified = self.configure_remote_site(settings)['verified']
                if not verified: failures += 1

            for i in range(128, 141):
                # define site settings
                settings = [
                    ['dvr username', 'admin'],
                    ['dvr password', '']
                ]
                name_id = '0%d' % i
                settings.append(['site name', 'DEPOT %s' % name_id])
                settings.append(['ip address', '172.22.48.%s' % i])

                # configure site
                verified = self.configure_remote_site(settings)['verified']
                if not verified: failures += 1

            # verify
            if failures == 0:
                result['verified'] = True
                self.log.trace("Configured all lab depot sites.")
            else:
                self.log.error("Failed to verify all lab depot sites added.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure all lab depot sites")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def activate_site(self, siteID, testcase=None):
        """ Activate given site.
        INPUT
            site id: the ID of the site to activate.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Activating site %s ..." % siteID)
        result = {'successful': False, 'verified': False}

        try:
            result['verified'] = self.toggle_remote_site_status(siteID,'on')['verified']

            self.log.trace("Site %s activated." % siteID)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="activate site %s" % siteID)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def configure_lab_depot_site_for_test(self, site, settings=[], allowed=True, serial_ids=False,
                                          testcase=None):
        """ Configure a remote site from the lab depot.
        INPUT
            site: the name of a known site (e.g. from Depot - see DVRs table in tartaros database).
            settings: an option list of field/value list pairs (i.e., [['site name', site.name]])
            allowed: whether the operation should be allowed or not.
            serial ids: whether to track all ids for multiple multiple sites added or not (ids increment).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            settings: the full list of site settings used to configure the site.
            site id: the id of the site returned upon adding.
            site name: the name of the site returned upon adding.
        """

        self.log.debug("Configuring Lab Depot site ...")
        result = {'successful': False, 'verified': False,
                  'settings': None, 'site id': None, 'site name': ''}

        try:
            # return site from database
            dvr_id = self.app_db.return_site_data(site)['site data']['dvr id']

            # return site data from database
            dvr_data = self.app_db.return_dvr_data(dvr_id)['dvr data']

            # define default settings for site
            parameters = [
                ['site name', dvr_data['name']],
                ['ip address', dvr_data['ip address']],
                ['dvr username', dvr_data['user']],
                ['dvr password', dvr_data['password']],
                ['dvr model', dvr_data['model']],
                ['recall period', 90]
            ]
            # update settings (if any given)
            for setting in settings:
                # determine if value updates defaults (duplicate)
                for parameter in parameters:
                    if parameter[0].lower() == setting[0].lower():
                        # remove default if duplicate
                        parameters.remove(parameter)
                    # update parameters
                parameters.append(setting)
            # configure site
            returned = self.configure_remote_site(parameters, allowed=allowed)
            # verify site
            verified = returned['verified']
            if not verified:
                self.log.error("Failed to verify configure lab depot site for test added.")
            else:
                # define return variables
                result['verified'] = verified
                self.log.trace("Configured lab depot site for test.")

            result['settings'] = parameters
            result['site id'] = returned['site id']
            result['site name'] = returned['site name']

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure lab depot site for test")

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            # site test variables
            if serial_ids:
                if not hasattr(testcase, 'site_id'):
                    testcase.site_settings = result['settings']
                    testcase.site_id = result['site id']
                    testcase.site_name = result['site name']
                elif hasattr(testcase, 'site_id') and not hasattr(testcase, 'site2_id'):
                    testcase.site2_settings = result['settings']
                    testcase.site2_id = result['site id']
                    testcase.site2_name = result['site name']
                else:
                    testcase.site3_settings = result['settings']
                    testcase.site3_id = result['site id']
                    testcase.site3_name = result['site name']
            else:
                testcase.site_settings = result['settings']
                testcase.site_id = result['site id']
                testcase.site_name = result['site name']

        return result

    def configure_remote_site(self, settings, allowed=True, testcase=None):
        """ Configure a remote site.
        INPUT
            settings: a list pairing fields with expected values.
            allowed: whether the operation should be allowed or not.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            site id: ID of the site configured.
        """

        self.log.debug("Configuring a site ...")
        result = {'successful': False, 'verified': False, 'site id': None}

        try:
            # define default data packet to send to server
            data = {
                SITECON_FIELDS['id']:                    '',
                SITECON_FIELDS['site name']:             '',
                SITECON_FIELDS['ip address']:            '',
                SITECON_FIELDS['dvr username']:          'admin',
                SITECON_FIELDS['dvr password']:          '',
                SITECON_FIELDS['dvr model']:             'MRH8',
                SITECON_FIELDS['events to download']:    0,
                SITECON_FIELDS['clips to download']:     0,
                SITECON_FIELDS['duration for clips']:    0,
                SITECON_FIELDS['video loss to download']:0,
                SITECON_FIELDS['recall period']:         90*86400,
                SITECON_FIELDS['pre-event time all']:    2,
                SITECON_FIELDS['pre-event time 1']:      2,
                SITECON_FIELDS['pre-event time 2']:      2,
                SITECON_FIELDS['pre-event time 3']:      2,
                SITECON_FIELDS['pre-event time 4']:      2,
                SITECON_FIELDS['pre-event time 5']:      2,
                SITECON_FIELDS['pre-event time 6']:      2,
                SITECON_FIELDS['pre-event time 7']:      2,
                SITECON_FIELDS['pre-event time 8']:      2,
                SITECON_FIELDS['post-event time all']:   5,
                SITECON_FIELDS['post-event time 1']:     5,
                SITECON_FIELDS['post-event time 2']:     5,
                SITECON_FIELDS['post-event time 3']:     5,
                SITECON_FIELDS['post-event time 4']:     5,
                SITECON_FIELDS['post-event time 5']:     5,
                SITECON_FIELDS['post-event time 6']:     5,
                SITECON_FIELDS['post-event time 7']:     5,
                SITECON_FIELDS['post-event time 8']:     5
            }

            # for 3.4+ builds, include site group
            if float(self.release_version) >= 3.4:
                data[SITECON_FIELDS['site group name']] = 'default'

            # if site ID given, then editing site (update data with current site settings
            editingSite = False
            siteID = None
            for setting in settings:
                if setting[0].lower() == 'id':
                    editingSite = True
                    siteID = setting[1]
            if editingSite and siteID is not None:
                parameters = self.return_site_configuration(siteID)['parameters']
                for parameter in parameters:
                    data[parameter[0]] = parameter[1]

            # for each item in settings, update data packet with associated value
            for setting in settings:
                self.log.trace("Setting '%(field)s' to '%(value)s' ..."
                               % {'field': setting[0], 'value': str(setting[1])})
                # translate value if necessary
                if SITECON_FIELDS[setting[0].lower()] == SITECON_FIELDS['recall period']:
                    val = int(setting[1])*86400

                elif SITECON_FIELDS[setting[0].lower()] == SITECON_FIELDS['dvr model']:
                    val = setting[1]
                    if val == 'RRH8': val = 'RoadRunner HD8'
                    if val == 'RRH16': val = 'RoadRunner HD16'

                # if field is 'all' for pre-event time, configure all 8 fields
                elif SITECON_FIELDS[setting[0].lower()] == SITECON_FIELDS['pre-event time all']:
                    val = setting[1]
                    data[SITECON_FIELDS['pre-event time 1']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 2']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 3']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 4']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 5']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 6']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 7']] = setting[1]
                    data[SITECON_FIELDS['pre-event time 8']] = setting[1]
                # if field is 'all' for post-event time, configure all 8 fields
                elif SITECON_FIELDS[setting[0].lower()] == SITECON_FIELDS['post-event time all']:
                    val = setting[1]
                    data[SITECON_FIELDS['post-event time 1']] = setting[1]
                    data[SITECON_FIELDS['post-event time 2']] = setting[1]
                    data[SITECON_FIELDS['post-event time 3']] = setting[1]
                    data[SITECON_FIELDS['post-event time 4']] = setting[1]
                    data[SITECON_FIELDS['post-event time 5']] = setting[1]
                    data[SITECON_FIELDS['post-event time 6']] = setting[1]
                    data[SITECON_FIELDS['post-event time 7']] = setting[1]
                    data[SITECON_FIELDS['post-event time 8']] = setting[1]
                else: val = setting[1]
                # update value
                data[SITECON_FIELDS[setting[0].lower()]] = val
            # post request to server
            url = self.server_url + SITECON_MODIFY_PATH
            response = self.post_http_request(url, data)['response']

            # verify site added (and pull id)
            returned = self.verify_remote_site_configuration(settings, allowed=allowed)
            result['verified'] = returned['verified']
            result['site id'] = returned['site id']
            result['site name'] = returned['site name']

            if result['verified'] and allowed:
                self.log.trace("Verified site configured.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure site")

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.site_id = result['site id']
            testcase.site_name = result['site name']
        return result

    def deactivate_site(self, siteID, testcase=None, allowed=True):
        """ Deactivate given site.
        INPUT
            site id: the ID of the site to deactivate.
            testcase: a testcase object supplied when executing function as part of a testcase step.
            allowed: whether or not the function is expected to be allowed.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Deactivating site %s ..." % siteID)
        result = {'successful': False, 'verified': False}

        try:
            result['verified'] = self.toggle_remote_site_status(siteID,'off',
                allowed=allowed)['verified']

            if result['verified'] and allowed:
                self.log.trace("Site %s deactivated." % siteID)
            elif result['verified'] and not allowed:
                self.log.trace("Verified site %s deactivation not allowed." % siteID)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="deactivate site %s" % siteID)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_site_configuration(self, siteID, testcase=None):
        """ Return current site configuration settings.
        INPUT
            site id: the ID of the site for which to return the configuration.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Returning current configuration for site %s ..." % siteID)
        result = {'settings':{}, 'parameters':[]}

        try:
            # determine site configuration map (per version)
            if float(self.release_version) <= 3.3:
                SERVER_FIELD_NAMES = SITECON_3_3_COLUMNS
            else: SERVER_FIELD_NAMES = SITECON_COLUMNS
            # query server for site settings
            url = self.server_url + SITECON_QUERY_PATH
            response = self.query_server_table(url, SERVER_FIELD_NAMES)['response']

            if response != [] and len(response) > 1:
                # find correct entry by site id
                for entry in response[1:]:
                    if str(entry['id']) == str(siteID): configuration = entry

                # translate configuration
                result['parameters'] =\
                translate_dict_to_list_parameters(self.log, configuration,
                    translation=SITECON_FIELDS)['parameters']
                result['settings'] = translate_list_parameters_to_dict(self.log,
                    result['parameters'])['dict']
                self.log.trace("Current site configuration:\t%s" % str(result['settings']))
            else:
                self.log.warn("No site configuration returned for site %s." % siteID)

            self.log.trace("Returned current configuration for site %s." % siteID)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return current configuration for site %s" % siteID)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def toggle_remote_site_status(self, siteID, status, testcase=None, allowed=True):
        """ Toggle the status for a remote site.
        INPUT
            site id: the ID of the site for which to toggle the status.
            status: the status to toggle ('on'/'off').
            testcase: a testcase object supplied when executing function as part of a testcase step.
            allowed: whether or not the function is expected to be allowed.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Toggling remote site status to %s ..." % str(status.lower()))
        result = {'successful': False, 'verified': False}

        try:
            # define data packet to send to server
            data = {SITECON_FIELDS['id']: siteID}
            valid_status = False
            if status.lower() == 'on':
                data['siteActive'] = 1
                valid_status = True
            elif status.lower() == 'off':
                data['siteActive'] = 0
                valid_status = True
            else:
                self.log.error("Invalid site status '%s' specified." % str(status))

            if valid_status:
                # post request to server
                url = self.server_url + SITECON_TOGGLE_STATUS_PATH
                response = self.post_http_request(url, data)['response']

                # verify site status
                if not allowed:
                    # convert to expected
                    if status.lower() == 'on': expected_status = 'off'
                    if status.lower() == 'off': expected_status = 'on'
                    result['verified'] = self.verify_remote_site_status(siteID,
                        expected_status)['verified']
                else:
                    result['verified'] = self.verify_remote_site_status(siteID, status)['verified']

                self.log.trace("Remote site status toggled.")
                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="toggle remote site status to %s" % status)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_remote_site_configuration(self, settings, allowed=True, testcase=None):
        """ Verify remote site configuration.
        "settings" should be a list pairing fields with expected values.
        INPUT
            settings: a list pairing fields with expected values.
            allowed: whether the operation should be allowed or not.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            site id: ID of the site configured.
        """

        self.log.debug("Verifying remote site configuration ...")
        result = {'successful': False, 'verified': False, 'site id': None, 'site name': None}

        try:
            # determine site configuration map (per version)
            if float(self.release_version) <= 3.3:
                SERVER_FIELD_NAMES = SITECON_3_3_COLUMNS
            else: SERVER_FIELD_NAMES = SITECON_COLUMNS

            # query server for remote sites
            url = self.server_url + SITECON_QUERY_PATH
            response = self.query_server_table(url,SERVER_FIELD_NAMES)['response']
            # first entry is the # of sites
            response = response[1:]
            self.log.trace("Parsed server response:\t'%s'" % response)

            if not allowed and response == []:
                self.log.trace("Verified site configuration (adding) not allowed.")
                result['verified'] = True

            else:
                # determine site ID or site name from given settings
                siteID = None
                siteName = None
                for setting in settings:
                    if str(setting[0]) == 'id': siteID = setting[1]
                    elif str(setting[0]) == 'site name':
                        siteName = setting[1]
                        result['site name'] = setting[1]
                if siteID is None and siteName is None:
                    self.log.error("Did not find site ID or name in given settings.")

                # determine correct site in query response using either site ID or name
                if siteID is not None or siteName is not None:
                    entry = None
                    for site in response:
                        if str(site['id']) == str(siteID): entry = site
                        elif site['site name'] == siteName: entry = site
                    if entry is None:
                        self.log.warn("Did not find site in server query response.")

                    else:
                        invalids = 0
                        # for each item in settings, verify against server query response
                        for setting in settings:
                            self.log.trace("Checking '%(field)s' ..." % {'field': setting[0]})

                            # get the value for the setting field being checked
                            serverValue = entry.get(setting[0].lower())
                            expectedValue = setting[1]

                            # translate value if necessary
                            if SITECON_FIELDS[setting[0].lower()] == SITECON_FIELDS['recall period']:
                                expectedValue = int(expectedValue)*86400
                            elif SITECON_FIELDS[setting[0].lower()] == SITECON_FIELDS['dvr model']:
                                if expectedValue == 'RRH8': expectedValue = 'RoadRunner HD8'
                                if expectedValue == 'RRH16': expectedValue = 'RoadRunner HD16'

                            # check against expected value
                            invalids = 0
                            if str(serverValue) != str(expectedValue):
                                self.log.trace("Expected '%(field)s' to be '%(expected)s', "
                                               "but was '%(actual)s'."
                                    %{'field':setting[0], 'expected': expectedValue, 'actual': serverValue})
                                invalids += 1

                            # determine site ID
                            result['site id'] = entry.get('id')

                        if invalids == 0 and allowed:
                            self.log.trace("Verified remote site configured.")
                            result['verified'] = True
                        elif invalids == 0 and not allowed:
                            self.log.trace("Failed to verify remote site configuration not allowed.")
                        elif invalids > 0 and allowed:
                            self.log.trace("Failed to verify remote site configuration.")
                        elif invalids > 0 and not allowed:
                            self.log.trace("Verified remote site configuration not allowed.")
                            result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify remote site configuration")

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.site_id = result['site id']
            testcase.site_name = result['site name']
        return result

    def verify_remote_site_status(self, siteID, status, testcase=None):
        """ Verify the given site's status.
        INPUT
            site id: the ID of the site for which to toggle the status.
            status: the status to toggle ('on'/'off').
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying remote site status is %s ..." % str(status.lower()))
        result = {'successful': False, 'verified': False}

        try:
            # query server for remote sites
            url = self.server_url + SITECON_QUERY_PATH
            response = self.query_server_table(url, SITECON_COLUMNS)['response']

            # first entry is the # of sites
            response = response[1:]
            self.log.trace("Parsed server response:\t'%s'" % response)

            # determine correct site in query response
            entry = None
            for site in response:
                if site['id'] == str(siteID): entry = site
            if entry is None:
                self.log.trace("Did not find site in server query response.")

            # verify site status for site in query resposne
            self.log.trace("Checking site status ...")

            # get the value for the setting field being checked (and parse)
            serverValue = entry.get('site status')
            if str(serverValue) == '0': serverValue = 'off'
            elif str(serverValue) == '1': serverValue = 'on'
            else:
                self.log.error("Invalid site status '%s' returned." % str(serverValue))

            # check against expected value
            if str(serverValue).lower() != str(status).lower():
                self.log.trace("Expected site status to be %(expected)s, but was '%(actual)s'."
                    %{'expected':status,'actual':serverValue})
            # return true and site ID if all verified
            else:
                result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify remote site status")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result