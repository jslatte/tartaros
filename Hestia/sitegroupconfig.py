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
from utility import translate_dict_to_list_parameters

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
SITEGROUPCON = SERVER['site groups']
SITEGROUPCON_QUERY_PATH = SITEGROUPCON['query path']
SITEGROUPCON_MODIFY_PATH = SITEGROUPCON['modify path']
SITEGROUPCON_FIELDS = SITEGROUPCON['fields']
SITEGROUPCON_COLUMNS = SITEGROUPCON['columns']

####################################################################################################
# Site Group Configuration #########################################################################
####################################################################################################
####################################################################################################


class SiteGroupConfiguration():
    """ Sub-library for ViM server site group configuration.
    """

    def return_site_group_configuration(self, group_id, testcase=None):
        """ Return current configuration for given site group ID.
        INPUT
            group id: id of site group for which to return the configuration.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            settings: the configuration of the site group returned.
        NOTE: settings are returned with fields already translated into server format.
        """

        self.log.debug("Returning current configuration for site group %s ..." % group_id)
        result = {'successful': False, 'settings':[]}

        try:
            # query server for site group settings
            response = self.query_page('Site Groups')['query response']

            # find settings for given site group
            siteGroup = None
            for entry in response:
                if str(entry['id']) == str(group_id):
                    self.log.trace("Site Group %s found." % group_id)
                    siteGroup = entry
            if siteGroup is not None:
                result['settings'] = translate_dict_to_list_parameters(self.log, siteGroup, None,
                    SITEGROUPCON_FIELDS)['parameters']
                self.log.trace("Returned current configuration for site group %s." % group_id)
            else:
                self.log.error("Site Group %s not found." % group_id)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return current configuration for site group %s"
                                               % group_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def configure_site_group(self, entry_id, settings=[], testcase=None):
        """ Configure a site group.
        INPUT
            entry id: the name (for adding new) or id (for editing existing) of the site group.
            settings: a list of field/value list pairs to configure site group
                (e.g., [[field, value]])
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            site group id: id of the site group (added).
            site group name: name of the site group.
        """

        self.log.debug("Configuring Site Group '%s' ..." % entry_id)
        result = {'successful': False, 'verified': False, 'site group id': None,
                  'site group name': None}

        try:
            # define default data packet to send to server
            data = {
                SITEGROUPCON_FIELDS['id']:                       '',
                SITEGROUPCON_FIELDS['site group name']:          '',
                SITEGROUPCON_FIELDS['storage location']:         self.storage_loc,
                SITEGROUPCON_FIELDS['elrt']:                     '365',
                SITEGROUPCON_FIELDS['tsd']:                      '15',
                SITEGROUPCON_FIELDS['ltsd']:                     '365',
                SITEGROUPCON_FIELDS['dgp']:                      '7',
            }

            # update data packet with current site group settings (if group ID given as entry ID)
            name = None
            try:
                data[SITEGROUPCON_FIELDS['id']] = int(entry_id)
                self.log.trace("Editing existing site.")

                currentSettings = self.return_site_group_configuration(entry_id)['settings']
                for setting in currentSettings:
                    data[setting[0]] = setting[1]

                    # determine group name
                    if setting[0].lower() == SITEGROUPCON_FIELDS['site group name'].lower():
                        name = setting[1]


            except BaseException:
                data[SITEGROUPCON_FIELDS['site group name']] = entry_id
                name = entry_id
                self.log.trace("Adding new site group.")

            # update data packet with given settings
            for setting in settings:
                data[SITEGROUPCON_FIELDS[setting[0]]] = setting[1]

                # if group name, update
                if setting[0].lower() == 'site group name':
                    name = setting[1]

            # post request to server
            url = self.server_url + SITEGROUPCON_MODIFY_PATH
            successful = self.post_http_request(url, data)['successful']

            # verify site group
            if successful and name is not None:
                results = self.verify_site_group(name, settings)
                result['verified'] = results['verified']
                result['site group id'] = results['site group id']
                result['site group name'] = name
                self.log.trace("Verified site group")
            else:
                self.log.error("Failed to verify site group.")
                result['verified'] = False

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure site group")

        # return
        if testcase is not None:
            testcase.site_group_id = result['site group id']
            testcase.site_group_name = result['site group name']
            testcase.processing = result['successful']
        return result

    def verify_site_group(self, name, settings=[], testcase=None):
        """ Verify
        INPUT
            settings: a list of field/value list pairs to verify against the site group
                (e.g., [[field, value]])
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            site group id: id of the site group (added).
        """

        self.log.debug("Verifying Site Group '%s' ..." % name)
        result = {'successful': False, 'verified': False, 'site group id': None}

        try:
            # update server query data with expected settings
            expected = {}
            for setting in settings:
                expected[setting[0]] = setting[1]
            # define server query data
            page = "Site Groups"
            data = {'entry id': name,
                    'expected': expected}
            # query server for site groups
            results = self.query_page(page, data)
            result['verified'] = results['verified']
            try:
                result['site group id'] = results['entry']['id']
            except BaseException, e:
                for error in e: self.log.error(error)
                self.log.error("Failed to return site group ID.")

            self.log.trace("Verified site group %s." % name)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify site group %s" % name)

        # return
        if testcase is not None:
            testcase.site_group_id = result['site group id']
            testcase.processing = result['successful']
        return result