###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from cookielib import CookieJar
from urllib2 import build_opener, HTTPCookieProcessor, install_opener
from mapping import HESTIA

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

LOGIN_PATH = HESTIA['server']['session']['path']
LOGOUT_PATH = HESTIA['server']['session']['logout path']
SESSION_FIELDS = HESTIA['server']['session']['fields']

####################################################################################################
# Session ##########################################################################################
####################################################################################################
####################################################################################################


class Session():
    """ Sub-library for ViM server user session functionality.
    """

    def log_in_to_vim(self, user_name='admin', password='password', max_attempts=1, testcase=None):
        """ Log in to the ViM server as given user with password.
        INPUT
            user name: the name of the user to log in as.
            password: the password to use when logging in.
            max_attempts: the number of attempts to make to log in.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Logging in to ViM as %s using password '%s' ..." % (user_name, password))
        result = {'successful': False, 'verified': False}

        try:
            # create a new opener with a CookieJar to store the session id
            cj = CookieJar()
            opener = build_opener(HTTPCookieProcessor(cj))
            install_opener(opener)

            # define url and data object
            url = self.server_url + LOGIN_PATH
            data = {
                SESSION_FIELDS['user name']:    user_name,
                SESSION_FIELDS['password']:     password,
            }

            # log in to ViM
            response = self.post_http_request(url, data, max_attempts=max_attempts)['response']

            if response is not None:
                if response == "Incorrect username or password.":
                    self.log.warn("Failed to log in to ViM as %s using password '%s'. "
                                  "The given credentials were invalid." % (user_name, password))
                else:
                    self.log.trace("Logged in.")
                    self.logged_in_user_name = user_name
                    self.logged_in_user_password = password
                    result['verified'] = True
                    result['successful'] = True

        except BaseException, e:
            self.handle_exception(e, operation="log in as %s using password '%s' ..." % (user_name,
                                                                                         password))

        # return
        if testcase is not None:
            testcase.logged_in_user_name = user_name
            testcase.logged_in_user_password = password
            testcase.processing = result['successful']
        return result

    def verify_user_logged_in_to_vim(self, user_name='admin', testcase=None):
        """ Verify given user has been logged in to ViM.
        INPUT
            user name: the name of the user logged in.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying %s logged in ..." % user_name)
        result = {'successful': False, 'verified': False}

        try:

            self.log.trace("")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify user logged in")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def log_out_of_vim(self, testcase=None):
        """ Log current user out of ViM.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Logging out of ViM ...")
        result = {'successful': False, 'verified': False}

        try:
            # log out
            user = self.logged_in_user_name
            url = self.server_url + LOGOUT_PATH
            response = self.get_http_request(url)['response']

            if response is not None:
                if response.lower() == "ok":
                    self.log.trace("The user '%s' logged out of ViM." % user)
                    self.logged_in_user_name = None
                    self.logged_in_user_password = None
                    result['verified'] = True
                else:
                    self.log.warn("Failed to log user '%s' out of ViM." % user)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="log out of ViM")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result