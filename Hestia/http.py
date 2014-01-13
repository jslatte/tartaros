###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from urllib import urlencode
from urllib2 import urlopen, HTTPError, Request
from httplib import IncompleteRead
from time import sleep, clock
from json import dumps
from csv import DictReader
from cStringIO import StringIO
from utility import return_execution_error
from mapping import HESTIA

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

CATEGORIES_PATH = HESTIA['server']['categories']['query path']

####################################################################################################
# HTTP #############################################################################################
####################################################################################################
####################################################################################################


class HTTP():
    """ Sub-library for ViM server interaction via HTTP calls.
    """

    def make_delete_request_to_server(self, url, testcase=None):
        """ Make a DELETE request to the ViM server. """

        self.log.debug("Making DELETE request to server:\t%s"%url)
        result = {'successful': False, 'verified':False, 'response':None}

        try:
            # build request object
            request = DeleteRequest(url)
            try: result['response'] = urlopen(request)
            except HTTPError, e:
                self.log.warn(str(e))
                self.log.warn("Failed to make DELETE request to server.")
            # read the response
            if result['response'] is not None:
                try: result['response'] = result['response'].read().strip()
                except IncompleteRead, e:
                    # if it fails to read (most likely due to JSON PUT) return whatever was read
                    result['response'] = e.partial
            # verify response
            if result['response'].lower() == 'ok' or result['response'].lower() == '':
                self.log.trace("Verified that DELETE request was successful.")
                result['verified'] = True
            else:
                self.log.warn("Failed to verify that DELETE request was successful.")
                self.log.warn("Expected server response to be 'Ok', but was %s."%result['response'])

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="make DELETE request to server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def get_http_request(self, url, testcase=None):
        """
        INPUT
            url: the full url to make the get request from.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Making GET request to server:\t%s ..." % url)
        result = {'successful': False, 'response': None, 'time': None}

        try:
            # begin timing
            t0 = clock()

            attempt = 1
            max_attempts = 5
            while result['response'] is None and attempt <= max_attempts:
                # make the request (and strip of whispace)
                try: result['response'] = urlopen(url).read().strip()
                except HTTPError, e:
                    self.log.trace("Failed to make GET request to server due to HTTP error.")
                    self.log.trace(str(e))
                    # check for 404 Not Found error
                    if str(e).split(':')[0] == 'HTTP Error 404':
                        result['response'] = 'HTTP Error 404'
                    else:
                        for error in e:
                            self.log.trace(str(error))
                    exception = return_execution_error()['error']
                    self.log.trace("Error: %s." % exception)
                    break
                except BaseException, e:
                    if attempt == max_attempts: result['response'] = {}
                    else:
                        self.log.trace("Failed to make GET request to server (attempt %d). "
                                       "Re-attempting in 5 seconds ..." % attempt)
                        self.log.trace(str(e))
                        for error in e:
                            self.log.trace(str(error))
                        exception = return_execution_error()['error']
                        self.log.trace("Error: %s." % exception)
                        sleep(5)

                    # increment
                    attempt += 1

            # end timing
            t = clock()
            # calculate total time
            result['time'] = t - t0

            self.log.trace("Made GET request to server.")
            self.log.trace("Response:\t%s" %result['response'])
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="make GET request to server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def put_http_request(self, url, data, json=False, max_attempts=1, testcase=None):
        """ Make a PUT request to the server.
        @param testcase: a testcase object supplied when executing function as part of a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'response' - the server response to the request.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': ''}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            attempt = 1
            while not result['successful'] and attempt <= max_attempts:

                try:
                    if data is not None:
                        if json:
                            # transform the data object into a form data encoded string (using JSON)
                            s_data = dumps(data) if data is not None else ''
                        else:
                            # transform the data object into a form data encoded string
                            s_data = urlencode(data)
                            s_data = s_data.replace('+','%20').replace('%28','(').replace('%29',')')
                    else: s_data = ''

                    # post the request
                    if json:
                        request = PutRequest(url, s_data, {"Content-Type": "application/json"})
                    else:
                        request = PutRequest(url, s_data)

                    result['response'] = urlopen(request)
                    self.log.trace("PUT HTTP request.")

                    self.log.trace("Response: %s" % result['response'])

                    if result['response'] is not None and result['response'] != '':
                        result['successful'] = True
                        break
                    else:
                        self.log.trace("Failed to PUT HTTP request %s %s (attempt %s). "
                                       "No response received from server."
                                       "Re-attempting in 5 seconds ..." % (url, str(s_data), attempt))
                except HTTPError, e:
                    self.log.trace(str(e))
                    self.log.trace("Failed to PUT HTTP request %s %s (attempt %s). "
                                   "Re-attempting in 5 seconds ..." % (url, str(s_data), attempt))
                except BaseException, e:
                    self.handle_exception(e,
                        operation="post HTTP request %s %s (attempt %s)" % (url, str(s_data), attempt))
                    self.log.trace("Re-attempting in 5 seconds ...")

                if attempt >= max_attempts:
                    self.log.error("Failed to post HTTP request to the ViM server.")
                    break

                # increment
                attempt += 1
                sleep(5)

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def post_http_request(self, url, data=None, testcase=None, max_attempts=1, json=False):
        """
        INPUT
            url: the HTTP url to use.
            data: a dictionary of data values to encode into the url when posting.
            testcase: a testcase object supplied when executing function as part of a testcase step.
            max attempts: the maximum number of attempts to perform the operation.
            json: whether to post the request using JSON format or not.
        OUPUT
            successful: whether the function executed successfully or not.
            response: the response to the request.
        """

        self.log.debug("Posting HTTP request %s %s ..." % (url, str(data)))
        result = {'successful': False, 'response': None}

        attempt = 1
        while not result['successful'] and attempt <= max_attempts:

            try:
                if data is not None:
                    if json:
                        # transform the data object into a form data encoded string (using JSON)
                        s_data = dumps(data) if data is not None else ''
                    else:
                        # transform the data object into a form data encoded string
                        s_data = urlencode(data)
                        s_data = s_data.replace('+','%20').replace('%28','(').replace('%29',')')
                else: s_data = ''

                # post the request
                if json:
                    request = Request(url, s_data, {"Content-Type": "application/json"})
                    result['response'] = urlopen(request).read().strip()
                    self.log.trace("Posted JSON request.")
                else:
                    result['response'] = urlopen(url, s_data).read().strip()
                    self.log.trace("Posted HTTP request.")

                self.log.trace("Response: %s" % result['response'])

                if result['response'] is not None and result['response'] != '':
                    result['successful'] = True
                    break
                else:
                    self.log.trace("Failed to post HTTP request %s %s (attempt %s). "
                                   "No response received from server."
                                   "Re-attempting in 5 seconds ..." % (url, str(s_data), attempt))
            except HTTPError, e:
                self.log.trace(str(e))
                self.log.trace("Failed to post HTTP request %s %s (attempt %s). "
                               "Re-attempting in 5 seconds ..." % (url, str(s_data), attempt))
            except BaseException, e:
                self.handle_exception(e,
                    operation="post HTTP request %s %s (attempt %s)" % (url, str(s_data), attempt))
                self.log.trace("Re-attempting in 5 seconds ...")

            if attempt >= max_attempts:
                self.log.error("Failed to post HTTP request to the ViM server.")
                break

            # increment
            attempt += 1
            sleep(5)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def query_server_table(self, url, columns, data=None, testcase=None):
        """ Query a server table.
        INPUT
            url: the full url to the server table.
            columns: the server table columns names map (see mapping).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            response: the server response to the query.
            time: the elapsed time while executing the query.
        """

        self.log.debug("Querying server table:\t %s ..." % str(url))
        result = {'successful': False, 'response': None, 'time': None}

        try:
            # transform the data object into a form data encoded string
            query = urlencode(data) if data is not None else ''
            self.log.trace("Data to encode: %s" % str(data))
            # build query path
            query = url + '?' + query.replace('+', '%20').replace('%28', '(').replace('%29', ')')
            query = query.replace('%40', '@').replace('%21', '!')
            # get query from server
            data = self.get_http_request(query)
            response = data['response']
            time = data['time']

            invalid_responses = [None, '', {}, 'HTTP Error 404']
            if response not in invalid_responses\
            and url != self.server_url + CATEGORIES_PATH:
                # split into tab-delimited column values
                entries = response.split('\n')
                # build list of entry dicts
                entry_list = []
                for entry in entries:
                    values = entry.split('\t')
                    # rebuild response as dict
                    response_dict = {}
                    for i in range(0, len(columns)):
                        try:
                            response_dict[columns[i]] = values[i]
                        except BaseException, e:
                            #self.handle_exception(e, operation="build response as dict")
                            pass
                    # append to list of entries
                    entry_list.append(response_dict)
                # update response
                response = entry_list
            elif response == 'HTTP Error 404':
                pass
            elif response in invalid_responses:
                response = None
            elif url == self.server_url + CATEGORIES_PATH:
                response = eval(response)
            else:
                response = None
            self.log.trace("Server response:\t%s" % str(response))
            # return response
            result['response'] = response
            result['time'] = time

            self.log.trace("Queried server table.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="query server table")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

class DeleteRequest(Request):
    def get_method(self):
        return "DELETE"


class PutRequest(Request):
    def get_method(self):
        return "PUT"