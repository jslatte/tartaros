###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from utility import return_execution_error, return_machine_ip_address, read_file_into_list
from time import sleep
import socket
from select import select
from binascii import hexlify, unhexlify
from os import getcwdu
from threading import Thread
from encoder import Encoder
from mapping import AdminSDKMap, SearchSDKMap

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

ROOT_PATH = getcwdu() + '\\Tantalus'
OUTPUT_PATH = ROOT_PATH + '\\output\\output.txt'
OUTPUT_PATH_SEARCH = ROOT_PATH + '\\output\\search_output.txt'
OUTPUT_PATH_ADMIN = ROOT_PATH + '\\output\\admin_output.txt'

INPUT_PATH = ROOT_PATH + '\\'
INPUT_PATH_ADMIN = INPUT_PATH + 'admin_input.txt'
INPUT_PATH_SEARCH = INPUT_PATH + 'search_input.txt'

CONFIG_FILE_PATH = ROOT_PATH + "\\config.ini"

setup_virtual_ips = 'FOR /L %A IN (1,1,255) DO netsh interface ipv4 add address "Local Area Connection" 172.22.65.%A 255.255.0.0'
teardown_virtual_ips = 'FOR /L %A IN (1,1,255) DO netsh interface ipv4 delete address "Local Area Connection" addr=172.22.80.%A'

####################################################################################################
# Tantalus (DVR Simulation) ########################################################################
####################################################################################################
####################################################################################################


class Tantalus(Encoder):
    """ Library for DVR simulation and interaction. """

    def __init__(self, logger, sisyphus, num_sites=10, output_on=False):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
            sisyphus: Sisyphus submodule for multi-threading.
            mode: the mode to run in.
        """

        # instantialize logger
        self.log = logger

        # instantialize sisyphus
        self.Sisyphus = sisyphus
        self.sisyphus = self.Sisyphus(self.log)

        # host IPs
        #self.dvr_ip = '172.200.1.106'
        self.dvr_ip = '172.22.48.140'

        # ports
        self.admin_port = 8200
        self.search_port = 10019

        # load configuration
        self.load_config()

        # addresses
        self.local_ip = return_machine_ip_address(self.log)['ip address']
        self.vim_admin_listener_address = (self.local_ip, self.admin_port)
        self.dvr_admin_port_address = (self.dvr_ip, self.admin_port)
        self.vim_search_listener_address = (self.local_ip, self.search_port)
        self.dvr_search_port_address = (self.dvr_ip, self.search_port)

        # virtual ip configuration
        listener_ip_tmp = '%s' % self.ip_schema + '%d'
        self.num_sites = num_sites
        listener_ips = []
        for i in range(1, (self.num_sites + 1)):
            listener_ips.append(listener_ip_tmp % i)
        self.admin_listener_addresses = []
        for ip in listener_ips:
            self.admin_listener_addresses.append((ip, self.admin_port))
        self.search_listener_addresses = []
        for ip in listener_ips:
            self.search_listener_addresses.append((ip, self.search_port))

        # size of data packets to receive
        self.packet_size = 16284

        # set default socket timeout
        #socket.setdefaulttimeout(15)

        # open output file
        self.output_on = output_on
        if self.output_on:
            self.output = open(OUTPUT_PATH, 'w')
            self.search_output = open(OUTPUT_PATH_SEARCH, 'w')
            self.admin_output = open(OUTPUT_PATH_ADMIN, 'w')

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

    def handle_exception(self, e, operation=None):
        """ Handle an exception.
        INPUT
            e: the exception (from BaseException, e).
            operation: the action being attempted (that failed).
        """

        if operation is not None:
            self.log.error("Failed to %s." % operation)
        self.log.error(str(e))
        for error in e:
            self.log.error(str(error))
        exception = return_execution_error()['error']
        self.log.error("Error: %s." % exception)

    def TEMPLATE_FUNCTION(self):
        """
        INPUT
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug(" ...")
        result = {'successful': False, 'verified': False}

        try:

            self.log.trace("")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="")

        # return
        return result

    def load_config(self):
        """ Load the configuration file for Tantalus.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Loading configuration ...")
        result = {'successful': False}

        try:
            # read config file data
            config_data = read_file_into_list(CONFIG_FILE_PATH)['list']

            # parse data into configuration
            parameters = []
            for line in config_data:
                if 'instance =' in line.lower():
                    self.instance = line.lower().strip().split('instance = ')[1]
                    parameters.append(['Instance', self.instance])
                if 'ip_schema = ' in line.lower():
                    self.ip_schema = line.lower().strip().split('ip_schema = ')[1]
                    parameters.append(['IP Schema', self.ip_schema])

            # log parameters in output
            for param in parameters:
                self.log.trace("CONFIGURATION: %s = %s" % (param[0], param[1]))

            self.log.trace("Loaded configuration.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="load configuration")

        # return
        return result

    def run(self):
        # open output file
        self.search_output = open(OUTPUT_PATH_SEARCH, 'w')
        self.admin_output = open(OUTPUT_PATH_ADMIN, 'w')
        self.open_persistent_bridge_to_dvr(self.vim_admin_listener_address, self.vim_search_listener_address, self.dvr_ip)

    def open_persistent_bridge_to_dvr(self, admin_listener, search_listener, dvr_ip):
        """ Open a persistent bridge between local ViM server and a live DVR.
        INPUT
            admin listener: the address (ip, port) to which to listen for communications
                to relay to the dvr admin port.
            search listener: the address (ip, port) to which to listen for communications
                to relay to the dvr admin port.
            dvr ip: the ip address of the DVR to which to connect.
        """

        self.log.debug("Opening persistent bridge between ViM and DVR at %s ..." % dvr_ip)
        result = {}

        try:

            # loop single connection bridge
            while True:

                # add threads for bridging admin port to thread queue
                self.sisyphus.add_process_to_thread_queue(self.bridge_two_addresses,
                    (admin_listener, (dvr_ip, self.admin_port)))

                # add threads for bridging search port to thread queue
                self.sisyphus.add_process_to_thread_queue(self.bridge_two_addresses,
                    (search_listener, (dvr_ip, self.search_port)))

                # execute threads in thread queue
                self.sisyphus.execute_pending_threads()

        except BaseException, e:
            self.handle_exception(e, operation="open persistent bridge between ViM and DVR at %s" % dvr_ip)

        # return
        return result

    def run_in_dvr_response_simulation_mode(self):
        """ Respond to site connections from ViM with canned data responses to simulate a DVR connection.
        """

        self.log.debug("Running in DVR response simulation mode ...")
        result = {}

        try:
            # run mode-specific variables
            self.syslog_event_time_counter = 1

            # define mapping objects
            self.admin_sdk_map = AdminSDKMap()
            self.search_sdk_map = SearchSDKMap()

            # listen for incoming communications (multi-threaded)
            for address in self.admin_listener_addresses:
                self.sisyphus.add_process_to_thread_queue(
                    self.simulate_dvr_responses_at_address, (address,))
            for address in self.search_listener_addresses:
                self.sisyphus.add_process_to_thread_queue(
                    self.simulate_dvr_responses_at_address, (address,))

            # execute threads in thread queue
            self.sisyphus.execute_pending_threads()

        except BaseException, e:
            self.handle_exception(e, operation="")

        # return
        return result

    def simulate_dvr_responses_at_address(self, listener_address):
        """ Simulate DVR responses for all incoming site connections at given address.
        INPUT
            listener address: the network address (ip, port) of the listener.
        """

        self.log.debug("Simulating DVR respones for communcations to %s ..." % str(listener_address))
        result = {}

        try:

            while True:
                # create listener for ViM sites
                self.log.trace("Creating listener for ViM sites at %s ..." % str(listener_address))
                listener = socket.socket()
                listener.bind(listener_address)
                listener.listen(0)

                while True:

                    # wait for a valid connection to a site
                    self.log.trace("Waiting for a valid connection from a site to listener at %s ..."
                                   % str(listener_address))
                    #while True:

                    # listen for incoming communication from site
                    response = listener.accept()
                    if response is not None:
                        site = response[0]
                        site_add = str(response[1])
                        self.log.trace("Received connection from site at %s to listener at %s." %
                                       (site_add, listener_address))
                        site.setblocking(0)

                        t = Thread(target=self.listen_to_socket_and_respond, args=(site,))
                        t.start()


                # close open connections
                self.log.trace("Closing connection to listener at %s ..." % str(listener_address))
                listener.close()

        except BaseException, e:
            self.handle_exception(e, operation="Simulating DVR respones for communcations to %s"
                                               % str(listener_address))

        # return
        return result

    def listen_and_return_sockets(self, listener, timeout=5):
        """ Listen on listener socket and return all socket connections made.
        INPUT
            listener: a socket to which to listen for incoming connections.
            timeout: the time to wait (s) for additional connections after the first is received.
        OUPUT
            sockets: a list of socket objects "heard" by listener.
        """

        listener_name = str(listener.getsockname())
        self.log.debug("Listening on %s and returning sockets ..." % listener_name)
        result = {'sockets': []}

        try:
            # listen for incoming connections
            listener.listen(0)

            # loop socket
            while True:

                try:
                    site = listener.accept()[0]
                    self.log.trace("Received connection from %s." % str(site.getpeername()))
                    site.setblocking(0)
                    result['sockets'].append(site)

                    # update timeout (now that at least one connection made)
                    listener.settimeout(timeout)

                except socket.timeout:
                    self.log.trace("Finished receiving connections to %s." % listener_name)
                    break

            # close listener
            listener.close()

            self.log.trace("Listened on %s and returned sockets." % listener_name)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="listen on %s and return sockets" % listener_name)

        # return
        return result

    def relay_live_dvr_responses_to_all_sockets(self, sockets, dvr_address):
        """ Relay the live DVR responses for multiple incoming "spoofed" connections to all connections.
        INPUT
            sockets: a list of socket objects to eahc of which to clone the live DVR responses.
            dvr address: the network address (ip, port) of the live DVR.
        """

        self.log.debug("Relaying responses from DVR at %s to all sockets ..." % str(dvr_address))
        result = {}


        try:
            # connect to the DVR
            dvr_site = socket.create_connection(dvr_address)
            self.log.trace("DVR (%s) connected." % str(dvr_address))
            dvr_site.settimeout(5)

            # build dvr response list from initial site communication
            self.log.trace("Building DVR response tracking objects ...")

            if len(sockets) > 0:
                first_site = sockets.pop()
                clone_sites = sockets

                # define second instance of Sisyphus (for sub-threading)
                sisyphus = self.Sisyphus(self.log)

                # thread communication between a site and DVR
                sisyphus.add_process_to_thread_queue(self.listen_to_socket_and_bridge_with_dvr,
                    (first_site, dvr_site, clone_sites))

                # thread communication with clone sites
                for site in clone_sites:
                    sisyphus.add_process_to_thread_queue(self.listen_to_socket,
                                                        (site,))

                # execute all threads
                sisyphus.execute_pending_threads()

            self.log.trace("Relayed responses from DVR at %s to all sockets." % str(dvr_address))
        except BaseException, e:
            self.handle_exception(e, operation="relay responses from DVR at %s to all sockets" % str(dvr_address))

        # return
        return result

    def listen_to_socket_and_bridge_with_dvr(self, sock, dvr_socket, clone_sockets=[]):
        """ Listen to the socket and bridge communications between it and the DVR.
        INPUT
            sock: a socket object connected to a site.
            dvr socket: a socket object connected to the DVR.
            clone sockets: a list of sockets to which to clone the DVR responses.
        """

        try:
            sock_name = str(sock.getpeername())
        except BaseException:
            try:
                sock_name = str(sock.getsockname())
            except BaseException:
                sock_name = str(sock)
        self.log.debug("Listening to socket %s and bridge with DVR ..." % sock_name)
        result = {}

        try:
            # set timeout for socket
            sock.settimeout(5)

            # loop to handle message traffic between first site and DVR
            running = True
            while running:

                # handle communications between first site and DVR only
                rlist = select([sock, dvr_socket], [], [])[0]

                # accept communications from first socket
                if sock in rlist:
                    # reset data bin for messages sent to DVR this session

                    # receive site messages
                    result = self.receive_incoming_messages_from_socket(sock)
                    data        = result['data']
                    running     = result['communicating']



                    # relay message to DVR
                    self.send_binary_data_to_socket(dvr_socket, data)

                if dvr_socket in rlist:
                    # reset data bin for messages sent to DVR this session

                    result = self.receive_incoming_messages_from_socket(dvr_socket)
                    data        = result['data']
                    running     = result['communicating']

                    # relay message to site
                    self.send_binary_data_to_socket(sock, data)

                    # relay message to clone sites
                    if len(clone_sockets) > 0:
                        for clone_sock in clone_sockets:
                            self.send_binary_data_to_socket(clone_sock, data)

            # close sockets
            self.log.trace("Closing open sockets ...")
            sock.close()
            dvr_socket.close()

            self.log.trace("Listened to socket %s and bridged with DVR." % sock_name)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="listen to socket %s and bridge with DVR" % sock_name)

        # return
        return result

    def listen_to_socket(self, sock):
        """ Listen to the socket.
        INPUT
            sock: a socket object connected to a site.
        """

        try:
            sock_name = str(sock.getpeername())
        except BaseException:
            try:
                sock_name = str(sock.getsockname())
            except BaseException:
                sock_name = str(sock)
        self.log.debug("Listening to socket %s ..." % sock_name)
        result = {}

        try:
            # set timeout for socket
            sock.settimeout(5)

            # loop to handle message traffic with socket
            running = True
            while running:
                pass

                #  accept communications from socket
                rlist = select([sock], [], [])[0]

                if sock in rlist:
                    # receive socket messages
                    result = self.receive_incoming_messages_from_socket(sock)
                    data        = result['data']
                    running     = result['communicating']

            # close sockets
            self.log.trace("Closing open sockets ...")
            sock.close()

            self.log.trace("Listened to socket %s." % sock_name)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="listen to socket %s" % sock_name)

        # return
        return result

    def listen_to_socket_and_respond(self, site, response_pck=None):
        """ Listen to the socket.
        INPUT
            site: the ViM site connection (socket) to which to listen and respond.
            response pck: a data list of responses in format [[message, message, message],[message]].
        """

        self.log.debug("Listening and responding to %s ..." % str(site.getpeername()))
        result = {}

        try:
            # build response package
            site_add = site.getsockname()

            # determine site ID
            site_id = int(site_add[0].split('.')[3])

            # determine input type
            if site_add[1] == self.admin_port:
                response_pck = self.build_dvr_response_dict_to_admin_sdk(site_id)['response dict']
                expected_admin_requests = response_pck.keys()

            elif site_add[1] == self.search_port:
                # build gps event pack
                num_events = 300

                response_pck = self.build_dvr_response_list_to_search_sdk(num_events, site_id)['response dict']
                expected_search_requests = response_pck.keys()

            else:
                raise AssertionError("No valid input type could be determined from address '%s'."
                                     % str(site.getsockname()))

            # loop to handle message traffic with socket
            running = True
            sent_sys_log = False
            while running:
                # set socket time out
                #site.settimeout((30 * 60))
                site.settimeout(300)

                #  accept communications from socket
                rlist = select([site], [], [])[0]

                if site in rlist:
                    # receive socket messages
                    result = self.receive_incoming_messages_from_socket(site)
                    data        = result['data']
                    running     = result['communicating']
                    #running     = result['successful']

                    # handle search SDK
                    if site.getsockname()[1] == self.search_port:
                        try:
                            responses = []

                            if str(16000000) in hexlify(data):
                                responses = []
                            elif '0d000000' in hexlify(data):
                                responses = ['09000000600d4a000009000000600d46000009000000600d42000009000000600d3e000009000000600d3a000009000000600d36000009000000600d32000009000000600d2e000009000000600d2a000009000000600d26000009000000600d22000009000000600d1e000009000000600d1a000009000000600d16000009000000600d12000009000000600d0e000009000000600d0a000009000000600d0600000900000060cd7d00000900000060cd7900000900000060cd7500000900000060cd7100000900000060cd6d00000900000060cd6900000900000060cd65000009000000604a0e000009000000604a0a000009000000604a0600000500000061']
                            elif '530000' in hexlify(data):
                                responses = [self.search_sdk_map.dvr_request_3b_response,
                                             self.search_sdk_map.dvr_request_3b_response2]
                            elif hexlify(data) == '050000006d':
                                if num_events >= 100:
                                    responses = [self.build_gps_event_data_packet(num_events/100)['packet']]
                                    num_events -= 100
                                else:
                                    break

                            else:
                                responses = response_pck[hexlify(data).strip()]
                        except BaseException:
                            try:
                                for request in expected_search_requests:
                                    if hexlify(data)[:8] in request:
                                        responses = response_pck[request]
                            except BaseException, e:
                                self.handle_exception(e, 'determine response to unknown request %s' % hexlify(data))

                            if responses is []:
                                self.log.warn("Unknown Request Received:\t%s" % hexlify(data))

                    # handle admin SDK
                    else:
                        try:
                            if str(data).strip() == '':
                                responses = []
                                #msg = ''
                                if not sent_sys_log:
                                    msg = response_pck['283665000100000002']
                                    sent_sys_log = False
                                else:
                                    msg = '.'

                                self.send_binary_data_to_socket(site, msg, muted=True)
                            elif self.admin_sdk_map.dvr_drive_info_request_tag in hexlify(data):
                                responses = response_pck[self.admin_sdk_map.dvr_drive_info_request]

                            elif response_pck[hexlify(data)] == response_pck['28367300140000000000000000000000010000000000000000000000']\
                                and not sent_sys_log:
                                # determine hex time
                                self.syslog_event_time_counter += 1
                                thousands = (self.syslog_event_time_counter / 4096)
                                hundreds = ((self.syslog_event_time_counter % 4096) / 256)
                                tens = (((self.syslog_event_time_counter % 4096) % 256) / 16)
                                ones = ((((self.syslog_event_time_counter % 4096) % 256) % 16) % 16)

                                hex_time = '0000%(tens)s%(thousands)s%(ones)s%(hundreds)s' \
                                           % {'thousands': thousands, 'hundreds': hundreds,
                                              'tens': tens, 'ones': ones}

                                # build response list
                                raw_responses = response_pck[hexlify(data).strip()]
                                responses = []
                                for raw_response in raw_responses:
                                    response = raw_response % {'time': hex_time}
                                    responses.append(response)

                                sent_sys_log = True
                            elif response_pck[hexlify(data)] == response_pck['28367300140000000000000000000000010000000000000000000000']\
                                and sent_sys_log:
                                msg = response_pck['283665000100000002']
                                sent_sys_log = False
                                self.send_binary_data_to_socket(site, msg, muted=True)
                                break
                            else:
                                responses = response_pck[hexlify(data).strip()]
                        except BaseException:
                            self.log.warn("Unknown Request Received:\t%s" % hexlify(data))
                            responses = []

                    for response in responses:
                        # loop until message sent successfully
                        sent = False
                        try:
                            msg = unhexlify(response)
                        except BaseException:
                            self.log.error('String:\t%s' % response)

                        while not sent:
                            sent = self.send_binary_data_to_socket(site, msg, muted=True)['successful']

                            if not sent:
                                sleep(1)

            # close sockets
            self.log.trace("Closing open sockets to %s ..." % str(site_add))
            site.close()

            self.log.trace("Listened and responded to %s." % str(site_add))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="listen and respond")

        # return
        return result

    def read_input_into_list(self, input_type, vim_address, dvr_address):
        """ Read the input file for given input type (admin, search) into a data list.
            INPUT
                input type: type of input (port) of message traffic (admin, search).
                vim address: address of ViM listener.
                dvr address: address of DVR.
            OUPUT
                successful: whether the function executed successfully or not.
                list: a list of messages in [source, message] format.
            """

        self.log.trace("Reading %s input into data list ..." % input_type)
        result = {'successful': False, 'list': []}

        try:
            # determine path by input type
            if input_type.lower() == 'admin':
                path = INPUT_PATH_ADMIN
            elif input_type.lower() == 'search':
                path = INPUT_PATH_SEARCH
            else:
                raise AssertionError("Invalid input type %s specified." % input_type)

            # open input file to read
            f = open(path, 'r')

            # read file into list
            input_data = f.readlines()

            # parse list into data list by message source
            i = 1
            for message in input_data:
                message_data = message.split(':')
                source_data = message_data[0]
                message = message_data[1].strip()

                # determine source
                source_data = source_data.split('TO')
                if vim_address in source_data[0]:
                    source = 'vim'
                elif dvr_address in source_data[0]:
                    source = 'dvr'
                else:
                    raise AssertionError("No valid source found in statement: '%s'"
                                         " (line %s)." % (source_data, i))

                # append data to data list
                result['list'].append([source, message])

                # increment line counter
                i += 1

            self.log.trace("Read %s input into data list." % input_type)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="read %s input into data list" % input_type)

        # return
        return result

    def bridge_two_addresses(self, first_add, second_add):
        """ Bridge a connection between two network (ip/port) addresses.
        INPUT
            first add: the address (ip, port) of the first site in the connection.
            second add: the address (ip, port) of the second site in the connection.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Bridging %s and %s ..." % (first_add, second_add))
        result = {}

        try:
            # define TCP/IP socket from first site to bridge
            listener = socket.socket()
            listener.bind(first_add)
            listener.listen(1)
            first_site = listener.accept()[0]
            listener.close()
            self.log.trace("First site (%s) connected." % str(first_add))

            # define TCP/IP socket from second site to bridge
            second_site = socket.create_connection(second_add)
            self.log.trace("Second site (%s) connected." % str(second_add))

            running = True

            while running:

                rlist = select([first_site, second_site], [], [])[0]

                if first_site in rlist:
                    result = self.receive_incoming_messages_from_socket(first_site)
                    data        = result['data']
                    running     = result['communicating']

                    # write received to output
                    if self.output_on:
                        output = "\nFROM %s TO %s:\t%s" % (str(first_add), str(second_add), hexlify(data))
                        if first_add[1] == self.admin_port:
                            self.admin_output.write(output)
                        elif first_add[1] == self.search_port:
                            self.search_output.write(output)
                        else:
                            self.output.write(output)

                    # send message along to DVR
                    self.send_binary_data_to_socket(second_site, data)

                if second_site in rlist:
                    result = self.receive_incoming_messages_from_socket(second_site)
                    data        = result['data']
                    running     = result['communicating']

                    # write received to output
                    if self.output_on:
                        output = "\nFROM %s TO %s:\t%s" % (str(second_add), str(first_add), hexlify(data))
                        if first_add[1] == self.admin_port:
                            self.admin_output.write(output)
                        elif first_add[1] == self.search_port:
                            self.search_output.write(output)
                        else:
                            self.output.write(output)

                    # send message along to ViM Server
                    self.send_binary_data_to_socket(first_site, data)

            try:
                # close open connections
                self.log.trace("Closing open connections to %s and %s ..." % (first_add, second_add))
                first_site.close()
                second_site.close()

            except BaseException:
                pass

        except BaseException, e:
            self.handle_exception(e, operation="bridge %s and %s" % (first_add, second_add))

        # return
        return result

    def send_binary_data_to_socket(self, sock, data, muted=False):
        """ Send a packet of binary data to specified socket.
        INPUT
            sock: the socket to which to send the data.
            data: the binary data to send to the scoket.
            muted: whether to mute exception reporting or not (for message loops)
        OUPUT
            successful: whether the function executed successfully or not.
        """

        try:
            sock_name = str(sock.getpeername())
        except BaseException:
            try:
                sock_name = str(sock.getsockname())
            except BaseException:
                sock_name = str(sock)
        #self.log.trace("Sending binary data packet to socket %s ..." % sock_name)
        result = {'successful': False}

        try:
            # send binary data to socket
            #self.log.trace("Binary Data: %s." % hexlify(data))
            if muted:
                try:
                    sock.send(data)
                except BaseException:
                    return
            else:
                sock.send(data)

            # write received to output
            msg = "\nSENT TO %s:\t%s" % (str(sock.getpeername()), hexlify(data))
            if self.output_on: self.output.write(msg)

            #self.log.trace("Binary data packet sent to socket %s." % sock_name)
            self.log.trace_in_line('.')
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="send binary data packet to socket %s"
                                               % sock_name)

        # return
        return result

    def receive_incoming_messages_from_socket(self, sock, muted=False):
        """ Receive any incoming messages from specified socket.
        INPUT
            sock: socket from which to receive any incoming messages.
        OUPUT
            successful: whether the function executed successfully or not.
            communicating: whether the socket is actively communicating or not.
            data: the data received by the socket.
            hex: the data received by the socket, translated into hex.
        """

        try:
            sock_name = str(sock.getpeername())
        except BaseException:
            try:
                sock_name = str(sock.getsockname())
            except BaseException:
                sock_name = str(sock)
        #self.log.trace("Receiving incoming messages from socket %s ..." % sock_name)
        result = {'successful': False, 'communicating': True, 'data': None, 'hex': None}

        try:
            # receive incoming messages to socket
            buf = sock.recv(self.packet_size)
            hex = hexlify(buf)
            #self.log.trace("Received Data: %s." % hex)

            # wait until remote client is done communicating
            if len(buf) == 0:
                #self.log.trace("%s disconnected." % sock_name)
                result['communicating'] = False

            # update result
            result['data']          = buf
            result['hex']           = hex

            # write received to output
            msg = "\nRECEIVED FROM %s:\t%s" % (str(sock_name), hex)
            if self.output_on: self.output.write(msg)

            #self.log.trace("Received incoming messages from socket %s." % sock_name)
            self.log.trace_in_line('.')
            result['successful'] = True
        except BaseException, e:
            result['data'] = ''
            result['hex'] = 'ff'
            result['successful'] = False
            result['communicating'] = False
            reported = False
            if e.args[0] == 10053:
                self.log.warn("Connection to %s aborted by host." % sock_name)
                reported = True
                try:
                    sock.close()
                except BaseException, e:
                    pass
            if not muted and not reported:
                self.handle_exception(e, operation="receive incoming messages from socket %s"
                                                   % sock_name)

        # return
        return result