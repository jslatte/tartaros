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

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
LIC_CONFIG = SERVER['license configuration']
LIC_QUERY_PATH = LIC_CONFIG['query path']
LIC_MOD_PATH = LIC_CONFIG['modify path']
LIC_FIELDS = LIC_CONFIG['fields']
LIC_COLUMNS = LIC_CONFIG['columns']

####################################################################################################
# License Configuration ############################################################################
####################################################################################################
####################################################################################################


class LicenseConfiguration():
    """ Sub-library for ViM server license configuration.
    """

    def configure_vim_license(self, license_type, testcase=None):
        """
        INPUT
            license type: the type of license to configure (see licenses in database).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Configuring %s ViM license ..." % license_type)
        result = {'successful': False, 'verified': False}

        try:
            # determine license type parameters
            if 'invalid' in license_type.lower():
                # retrieve key
                cfg = self.app_db.return_license_configuration(license_type.lower())['configuration']
                key = cfg['key']
                # retrieve current module bit and number of sites (should not change)
                cfg = self.return_current_license_configuration()
                modules_bit = cfg['modules bit']
                num_sites = cfg['number of sites']

                # attempt to configure license
                response = self.post_license_key_to_server(key)['response']

                # verify license invalid message
                response_verified = False
                if response == 'This license key is invalid':
                    response_verified = True

                # verify original license key unchanged
                license_unchanged = self.verify_license_configuration(modules_bit,
                    num_sites)['verified']

                # verify
                if response_verified and license_unchanged:
                    result['verified'] = True
                    self.log.trace("Verified invalid license key not allowed.")
                else:
                    self.log.error("Failed to verify invalid license key not allowed.")
            elif license_type.lower() != 'demo':
                cfg = self.app_db.return_license_configuration(license_type.lower())['configuration']
                key = cfg['key']
                modules_bit = cfg['bit']
                num_sites = cfg['number of sites']

                # configure license
                self.post_license_key_to_server(key)

                # verify license configuration
                result['verified'] = self.verify_license_configuration(modules_bit,
                    num_sites)['verified']

                self.log.trace("Configured %s ViM license." % license_type)
            else:
                # demo license already configured (assuming first time configuration)
                result['verified'] = True
                self.log.trace("Configured %s ViM license." % license_type)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="configure %s ViM license" % license_type)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_license_configuration(self, modules_bit, num_sites, testcase=None):
        """
        INPUT
            modules bit: the hex bit of the module configuration (includes all modules).
            num sites: the number of sites to verify being included in the configuration.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying license configuration ...")
        result = {'successful': False, 'verified': False}

        try:
            # return current configuration
            data = self.return_current_license_configuration()
            act_modules_bit = data['modules bit']
            act_num_sites = data['number of sites']

            # compare actual to expected to verify configuration
            failure = False
            if str(act_modules_bit) == str(modules_bit):
                self.log.trace("Verified modules bit.")
            else:
                self.log.warn("Expected modules bit to be %s, but was %s."
                              % (modules_bit, act_modules_bit))
                failure = True
            if str(act_num_sites) == str(num_sites):
                self.log.trace("Verified number of sites.")
            else:
                self.log.warn("Expected number of sites bit to be %s, but was %s."
                              % (num_sites, act_num_sites))
                failure = True

            # verified if no failures
            if not failure:
                self.log.trace("Verified license configuration.")
                result['verified'] = True
            else: self.log.warn("Failed to verify license configuration.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify license configuration")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def post_license_key_to_server(self, key, testcase=None):
        """
        INPUT
            key: the license key to post to server
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            response: the server response.
        """

        self.log.debug("Posting license key %s to server ..." % key)
        result = {'successful': False, 'response': None}

        try:
            # define data packet
            data = {
                LIC_FIELDS['key']:      key,
            }

            # post request to server
            url = self.server_url + LIC_MOD_PATH
            result['response'] = self.post_http_request(url, data)['response']

            self.log.trace("Posted license key %s to server." % key)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="post license key %s to server" % key)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_current_license_configuration(self, testcase=None):
        """
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            configuration: current license configuration
        """

        self.log.debug("Returning current license configuration ...")
        result = {'successful': False, 'modules bit': None, 'number of sites': None}

        try:
            # query server for license configuration
            url = self.server_url + LIC_QUERY_PATH
            cfg = self.query_server_table(url, LIC_COLUMNS)['response'][0]

            # assign values
            result['modules bit'] = cfg.get('modules')
            result['number of sites'] = cfg.get('sites')

            self.log.trace("Returned current license configuration: %s." % str(cfg))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return current license configuration")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result