####################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from json import dumps
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError
import base64
import ast
from time import sleep

####################################################################################################
# TestRail API #####################################################################################
####################################################################################################
####################################################################################################

class API():
    """ Functions to interact with TestRail. """

    def post_request_to_server(self, url, data=None, max_attempts=1, json=False):
        """
        INPUT
            url: the HTTP url to use.
            data: a dictionary of data values to encode into the url when posting.
            max attempts: the maximum number of attempts to perform the operation.
            json: whether to post the request using JSON format or not.
        OUPUT
            successful: whether the function executed successfully or not.
            response: the response to the request.
            response dict: the response from the server translated into dict format.
        """

        self.log.debug("Posting HTTP request %s %s ..." % (url, str(data)))
        result = {'successful': False, 'response': None, 'response dict': None}

        attempt = 1
        while not result['successful'] and attempt <= max_attempts:

            try:
                if data is not None:
                    if json:
                        # transform the data object into a form data encoded string (using JSON)
                        data = dumps(data) if data is not None else ''
                    else:
                        # transform the data object into a form data encoded string
                        data = urlencode(data)
                        data = data.replace('+','%20').replace('%28','(').replace('%29',')')
                else: data = ''

                # post the request
                if json:
                    request = Request(url, data)

                    # append JSON content type header
                    self.log.trace("Adding content type header for JSON ...")
                    request.add_header('Content-Type', "application/json")

                    # encode authorization
                    base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
                    request.add_header("Authorization", "Basic %s" % base64string)

                    # post to server
                    response = urlopen(request)
                    result['response'] = response.read().strip()
                    self.log.trace("Posted JSON request.")
                else:
                    result['response'] = urlopen(url, data).read().strip()
                    self.log.trace("Posted HTTP request.")

                self.log.trace("Response: %s" % result['response'])

                if result['response'] is not None and result['response'] != '':
                    # try to convert response to dictionary (update bool values to correct format)
                    try:
                        responseDict = ast.literal_eval(result['response'].replace('false','False')
                        .replace('true','True')
                        .replace('null','None'))
                        self.log.trace("Converted server response to dictionary format.")
                        result['response dict'] = responseDict
                    except BaseException, e:
                        self.log.error(str(e))
                        self.log.error("Failed to convert server response to dictionary.")
                    result['successful'] = True
                    break
                else:
                    self.log.trace("Failed to post HTTP request %s %s (attempt %s). "
                                   "No response received from server."
                                   "Re-attempting in 5 seconds ..." % (url, str(data), attempt))
            except HTTPError, e:
                self.log.trace(str(e))
                self.log.trace("Failed to post HTTP request %s %s (attempt %s). "
                               "Re-attempting in 5 seconds ..." % (url, str(data), attempt))
            except BaseException, e:
                #self.handle_exception(e,
                #                      operation="post HTTP request %s %s (attempt %s)" % (url, str(data), attempt))
                for error in e: self.log.warn(error)
                self.log.trace("Re-attempting in 5 seconds ...")

            if attempt >= max_attempts:
                self.log.error("Failed to post HTTP request to the ViM server.")
                break

            # increment
            attempt += 1
            sleep(5)

        # return
        return result

    def get_request_from_server(self, url, mode='default'):
        """ Make a GET request to the ViM server. """

        self.log.trace("Getting request from server:\t%(request)s"%{'request':str(url)})
        result = {'response':None, 'response dict': {}}

        # add required header to url
        req = Request(url)

        # append JSON content type header
        self.log.trace("Adding content type header for JSON ...")
        req.add_header('Content-Type', "application/json")

        # encode authorization
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)

        # make the request (and strip of whispace)
        try: result['response'] = urlopen(req).read().strip()
        except BaseException: result['response'] = None
        self.log.trace("Server response:\t'%(response)s'"%{'response':result['response']})
        # try to convert response to dictionary (update bool values to correct format)
        if mode.lower == 'debug':
            responseDict = ast.literal_eval(result['response'].replace('false','False')
            .replace('true','True')
            .replace('null','None'))
            self.log.trace("Converted server response to dictionary format.")
            result['response dict'] = responseDict
        else:
            try:
                responseDict = ast.literal_eval(result['response'].replace('false','False')
                .replace('true','True')
                .replace('null','None'))
                self.log.trace("Converted server response to dictionary format.")
                result['response dict'] = responseDict
            except BaseException, e:
                self.log.error(str(e))
                self.log.error("Failed to convert server response to dictionary.")
        # return response
        return result