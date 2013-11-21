###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import base64, urllib, urllib2

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# TeamCity API #####################################################################################
####################################################################################################
####################################################################################################

class API():
    """ Functions to interact with TeamCity. """

    def send_http_request(self, url, data='', mode='default'):
        """ Send an HTTP request to the TeamCity web server.
        'url' must be the full URL of the server and page.
        'data' must be a key/value paired dictionary.
        'mode'  - 'debug' does not send the request. """

        self.log.trace("Sending HTTP request to TeamCity server:\t%s"%(str(url)+' '+str(data)))
        result = {'successful': False, 'response':None,'file path':None}

        try:
            # encode data dictionary
            if data is not None and data is not {} and data is not '':
                data = self.encode_url_data(data)['data']
            else: data = ''
            if mode.lower() != 'debug':
                # add header
                url = self.add_basic_authentication_to_url(url)['url']
                # send HTTP request and return response
                try:
                    if mode.lower() == 'get':
                        response = urllib2.urlopen(url)
                    else:
                        response = urllib2.urlopen(url,data)
                except urllib2.HTTPError, e:
                    for error in e: self.log.error(str(error))
                    self.log.error("Failed to send request to server.")
                    response = e.message
                    # strip the response text of whitespace
                try: result['response'] = response.read().strip()
                except BaseException: result['response'] = response
                self.log.trace("Server response:\t'%(response)s'"%{'response':result['response']})

                result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="send HTTP request to TeamCity server")

        # return
        return result

    def encode_url_data(self,data=''):
        """ Encode a url data dictionary. """

        self.log.trace("Encoding url ...",'debug','TeamCity API')
        result = {'successful': False, 'data':None}

        try:
            # translate the data dictionary into a form data encoded string
            if data is not None and data != {}: data = urllib.urlencode(data)
            else: data = ''
            # replace any characters that failed to format correctly
            data = data.replace('+','%20').replace('%28','(').replace('%29',')')
            self.log.trace("Form-encoded data string:\t'%(data)s'"%{'data':data})
            result['data'] = data

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="encode URL")

        # return
        return result

    def add_basic_authentication_to_url(self,url):
        """ Add a basic authentication header to a url. """

        self.log.trace("Adding authentication header ...")
        result = {'successful': False, 'url':None}

        try:
            # add required header to URL (encode baside authentication)
            req = urllib2.Request(url)
            base64string = base64.encodestring('%s:%s'%(self.auth[0],self.auth[1]))[:-1]
            authheader = "Basic %s"%base64string
            req.add_header("Authorization",authheader)
            result['url'] = req

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="add authentication header")

        # return
        return result