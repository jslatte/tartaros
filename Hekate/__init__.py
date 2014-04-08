###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from utility import return_execution_error, read_file_into_list, return_machine_ip_address
import inspect
from os import getcwdu
from time import sleep
import socket
from binascii import hexlify, unhexlify
from select import select

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

ROOT_PATH = getcwdu() + '\\Hekate'
CONFIG_FILE_PATH = ROOT_PATH + "\\config.ini"

####################################################################################################
# Hekate ###########################################################################################
####################################################################################################
####################################################################################################


class Hekate():
    """ A library of functions for running the client server.
    """

    def __init__(self, logger, exception_handler, sisyphus):
        """
        @param logger: an initialized Logger() to inherit.
        @param exception_handler: an un-initialized ExceptionHandler() to inherit.
        @param sisyphus:
        """

        # instance logger (initialized instance)
        self.log = logger

        # instance exception handler
        self.handle_exception = exception_handler

        # instantialize sisyphus
        self.Sisyphus = sisyphus
        self.sisyphus = self.Sisyphus(self.log)

        # stacktrace
        self.inspect = inspect

        # load configuration
        self.load_config()

        # build client socket
        self.local_ip = return_machine_ip_address(self.log)['ip address']
        self.local_port = 333
        self.local_addr = (self.local_ip, self.local_port)
        self.packet_size = 16284
        self.client = socket.socket()
        self.client.bind(self.local_addr)

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
        """ Load the configuration file for Hekate.
        @return: a dict including
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
                if 'PARAM =' in line.lower():
                    self.PARAM = line.lower().strip().split('PARAM = ')[1]
                    parameters.append(['PARAM', self.PARAM])

            # log parameters in output
            for param in parameters:
                self.log.trace("CONFIGURATION: %s = %s" % (param[0], param[1]))

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="load configuration")

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def receive_incoming_messages_from_socket(self, sock, logging=True):
        """ Receive any incoming messages from specified socket.
        @param sock: the socket from which to receive any incoming messages.
        @param logging: whether the data received by the socket should be logged or not.
        @return: a data dictionary including
            successful: whether the function executed successfully or not.
            communicating: whether the socket is actively communicating or not.
            data: the data received by the socket.
            hex: the data received by the socket, translated into hex.
        """

        operation = inspect.stack()[0][3]
        result = {'successful': False, 'communicating': True, 'data': None, 'hex': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # define the local and remote addresses (for reference)
            try:
                sock_name = str(sock.getpeername())
            except BaseException:
                try:
                    sock_name = str(sock.getsockname())
                except BaseException:
                    sock_name = str(sock)

            if logging: self.log.trace_in_line("%s ..." % sock_name)

            # receive incoming messages to socket
            try:
                buf = sock.recv(self.packet_size)

                # translate hex (if needed)
                try:
                    dat = unhexlify(buf)
                except BaseException:
                    dat = buf

                if logging: self.log.trace("Received Data: %s." % dat)

                # wait until remote client is done communicating
                if len(buf) == 0:
                    if logging: self.log.trace("%s disconnected." % sock_name)
                    result['communicating'] = False

                # update result
                result['data'] = dat

                if logging: self.log.trace("Received incoming messages from socket %s." % sock_name)
                else: self.log.trace_in_line('.')
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
                if logging and not reported:
                    self.handle_exception(
                        self.log, e, operation="receive incoming messages from socket %s" % sock_name)

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def send_binary_data_to_socket(self, sock, data, logging=False):
        """ Send a packet of binary data to specified socket.
        @param sock: the socket to which to send the data.
        @param logging: whether the data sent to the socket should be logged or not.
        @return: a data dictionary including
            successful: whether the function executed successfully or not.
        """

        operation = inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # define the local and remote addresses (for reference)
            try:
                sock_name = str(sock.getpeername())
            except BaseException:
                try:
                    sock_name = str(sock.getsockname())
                except BaseException:
                    sock_name = str(sock)

            if logging: self.log.trace_in_line("%s ..." % sock_name)

             # send binary data to socket
            if logging: self.log.trace("Binary Data: %s." % hexlify(data))
            if logging:
                try:
                    sock.send(data)
                except BaseException:
                    return
            else:
                sock.send(data)

            if logging: self.log.trace("Binary data packet sent to socket %s." % sock_name)
            else: self.log.trace_in_line('.')

            # compile results
            result['successful'] = True

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def listen_to_socket(self, sock, logging=False):
        """ Listen to the socket.
        @param sock: the socket to which to send the data.
        @param logging: whether data should be logged or not.
        @return: a data dictionary including
            successful: whether the function executed successfully or not.
            data: the full data message received (automatically translated from hex).
        """

        operation = inspect.stack()[0][3]
        result = {'successful': False, 'data': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # define the local and remote addresses (for reference)
            try:
                sock_name = str(sock.getpeername())
            except BaseException:
                try:
                    sock_name = str(sock.getsockname())
                except BaseException:
                    sock_name = str(sock)

            if logging: self.log.trace_in_line("%s ..." % sock_name)

            # listen
            sock.listen(1)
            #sock.settimeout(5)
            conn, addr = sock.accept()

            # loop to handle message traffic with socket
            running = True
            data = ''
            while running:

                result = self.receive_incoming_messages_from_socket(conn, logging=logging)
                data += result['data']
                running = result['communicating']

            self.log.trace('Data Received:\t%s' % str(data))

            # compile results
            result['successful'] = True
            result['data'] = data

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def run(self):
        """ Run Hekate.
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%sning ..." % operation.replace('_', ' '))

            while True:

                # DEFINE THREAD: listen for incoming communication
                self.sisyphus.add_process_to_thread_queue(
                    self.listen_to_socket, (self.client, True,)
                )

                # EXECUTE ALL THREADS
                result = self.sisyphus.execute_pending_threads()

                # build list of messages received
                messages = []
                for datum in result['data']:
                    messages.append(datum['data'])

                # handle communication received
                self.handle_server_commands(messages)

            # close sockets
            self.log.trace("Closing open sockets ...")
            self.client.close()

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def handle_server_commands(self, commands):
        """ Handle any commands received from the server (Tartaros).
        @param commands: a list of string commands received from the server.
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            for command in commands:
                self.log.trace(command)

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result