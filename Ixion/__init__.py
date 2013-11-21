###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import socket, os
from time import sleep
from datetime import datetime
from utility import checksum, return_execution_error

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

CONFIG_FILE_PATH = os.getcwdu() + "\\Ixion\\config.txt"
GPS_PORT = 14002

####################################################################################################
# Ixion (GPS Simulation) ###########################################################################
####################################################################################################
####################################################################################################


class Ixion():
    """ Library for GPS simulation. """

    def __init__(self, logger):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # instantialize logger
        self.log = logger

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

        # default latitude and longitude
        self.lat = 4800.00
        self.long = -12167.000
        self.reversed = False
        self.speed = 22.4

        # define targets for GPS simulation
        self.dvrs_for_lan = self.determine_dvrs_for_lan_from_config()['dvrs']

        # run
        #self.run()

    def run(self):

        self.simulate_gps_data_for_addresses()

    def handle_exception(self, e, operation=None):
        """ Handle an exception.
        INPUT
            e: the exception (from BaseException, e).
            operation: the action being attempted (that failed).
        """

        if operation is not None: self.log.error("Failed to %s." % operation)
        self.log.error(str(e))
        self.log.error("Error: %s." % return_execution_error()['error'])

    def determine_dvrs_for_lan_from_config(self):
        """ Read config.txt and determine which dvrs should be sent GPS data via LAN.
        OUPUT
            successful: whether the function executed successfully or not.
            dvrs: the DVRs (ip_address, gps_port) to send simulated GPS data to.
        """

        #self.log.debug("Determining DVRs for LAN-based GPS simulation from config file at %s ..."
        #% CONFIG_FILE_PATH)
        result = {'successful': False, 'dvrs': []}

        try:

            # open config file
            f = open(CONFIG_FILE_PATH, 'r')

            # read lines into temporary list to parse
            configData = f.readlines()

            # look for lan DVR segment in config parameters
            start = 0
            end = None
            for line in configData:
                if "[LAN GPS SITES]" in line:
                    start = int(configData.index(line)) + 1

                    for n in configData[start:]:
                        if "[" in n:
                            end = int(configData.index(n))

            # add to list of DVRs to send GPS data to via LAN
            for address in configData[start:end]:
                result['dvrs'].append((address.replace('\n',''),GPS_PORT))

            #self.log.trace("Determined DVRs for LAN-based GPS simulation.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine DVRs for LAN-based GPS simulation")

        # return
        return result

    def simulate_gps_data_for_addresses(self):
        """ Simulate GPS data and send it via LAN to DVRs.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Simulating GPS Data for target addresses ...")
        result = {'successful': False}

        try:

            # define instance of latitude and longitude
            lat = self.lat
            long = self.long
            speed = self.speed

            # define initial targets
            targets = self.dvrs_for_lan

            # create socket connection to each address and append to list
            self.log.trace("Connecting to target addresses ...")
            connections = []
            unavailable_addresses = []
            for target in targets:
                try:
                    connection = socket.create_connection(target)
                    self.log.trace("Connected to %s." % str(target))
                    connections.append({'connection': connection, 'address': target})
                except BaseException, e:
                    self.log.error(str(e))
                    self.log.error("Failed to connect to %s." % str(target))
                    unavailable_addresses.append(target)

            self.log.trace("Sending GPS data ...")
            while True:

                try:
                    # get current time and date
                    date_time = datetime.utcnow()
                    hour = date_time.hour
                    min = date_time.minute
                    sec = date_time.second
                    day = date_time.day
                    month = date_time.month
                    year = int(str(date_time.year)[2:])
                    # generate string
                    nmea_string = self.generate_nmea_string([hour,min,sec],[day,month,year],lat,
                        long, speed)['string']
                    self.log.trace('%s' % nmea_string)
                    # send GPS data through each connection
                    for connection in connections:
                        dst = connection['connection']
                        address = connection['address']
                        try:
                            dst.send(nmea_string)
                        except BaseException, e:
                            self.log.error(str(e))
                            self.log.error("Failed to send GPS data to %s." % str(address))
                            connections.remove(connection)
                            unavailable_addresses.append(address)
                    # update position (move back and forth)
                    interval = 1
                    # switch direction based on interval limit
                    if lat >= self.lat + interval and long >= self.long + interval\
                    and not self.reversed:
                        self.reversed = True
                    elif self.reversed and lat <= self.lat and long <= self.long:
                        self.reversed = False

                    if not self.reversed:
                        lat += 0.01
                        long += 0.01
                        speed += 0.1
                    else:
                        lat -= 0.01
                        long -= 0.01
                        speed -= 0.1

                    # attempt to connect to any failed connections
                    for address in unavailable_addresses:
                        try:
                            connection = socket.create_connection(address)
                            self.log.trace("Connected to %s." % str(address))
                            connections.append({'connection': connection, 'address': address})
                            unavailable_addresses.remove(address)
                        except BaseException, e:
                            #log(str(e), 'error', Ixion)
                            #log("Failed to connect to %s." % str(address), 'trace', 'Ixion')
                            pass

                    # check config file for any new DVRs added
                    configDVRs = self.determine_dvrs_for_lan_from_config()['dvrs']
                    for DVR in configDVRs:
                        found = False
                        # check successfully connected target list
                        for connection in connections:
                            if connection['address'] == DVR:
                                found = True
                            # check unavailable target list
                        for ipaddress in unavailable_addresses:
                            if ipaddress == DVR:
                                found = True
                            # add to unavailable target list if not found in either list
                        if not found:
                            unavailable_addresses.append(DVR)

                    # check config file for any DVRs removed
                    for connection in connections:
                        found = False
                        # check config data
                        for DVR in configDVRs:
                            if DVR == connection['address']:
                                found = True

                        # remove if not found
                        if not found:
                            self.log.trace("Closing connection to %s ..." % str(connection['address']))
                            try:
                                connection['connection'].close()
                                connections.remove(connection)
                            except BaseException, e:
                                self.log.error(str(e))
                                self.log.error("Failed to close connection to inactive address.")

                    for address in unavailable_addresses:
                        found = False
                        # check config data
                        for DVR in configDVRs:
                            if DVR == address:
                                found = True

                        # remove if not found
                        if not found:
                            self.log.trace("No longer attempting to connectto %s ..." % str(address))
                            try:
                                unavailable_addresses.remove(address)
                            except BaseException, e:
                                self.log.error(str(e))
                                self.log.error("Failed to close connection to inactive address.")

                    # one message per second
                    sleep(1)

                except BaseException, e:
                    self.log.error(str(e))

            # close all active connections
            for connection in connections:
                try:
                    connection['connection'].close()
                except BaseException, e:
                    self.log.error(str(e))

            self.log.trace("Simulated GPS data for target DVRs")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate GPS data for targt DVRs")

        # return
        return result

    def generate_nmea_string(self, time, date, lat, long, speed):
        """ Generate a NMEA string for GPS simulation with given data.
        'time' should be a list of three values, e.g., [hour,minute,second] in 24-hour format
        'date' should be a list of three values, e.g., [day,month,year] in numerical (2-digit)
            format
        """

        result = {'string': ''}

        try:

            # determine time values from list
            hour = str(time[0]) if time[0] > 9 else '0%s' % time[0]
            min = str(time[1]) if time[1] > 9 else '0%s' % time[1]
            sec = str(time[2]) if time[2] > 9 else '0%s' % time[2]
            # determine date values from list
            day = str(date[0]) if date[0] > 9 else '0%s' % date[0]
            month = str(date[1]) if date[1] > 9 else '0%s' % date[1]
            year = str(date[2]) if date[2] > 9 else '0%s' % date[2]
            fixtime = '%s%s%s' %(hour,min,sec)
            fixlat = '%s,N' %lat if lat > 0 else '%s,S' % abs(lat)
            fixlong = '%s,E' %long if long > 0 else '%s,W' % abs(long)
            speed = speed
            angle = '045.0'
            fixdate = '%s%s%s' %(day,month,year)
            #self.log.trace("Fix Date: %s." % fixdate)
            magvar = ','
            base_string = 'GPRMC,%(time)s,A,%(lat)s,%(long)s,%(speed)s,%(angle)s,%(date)s,%(magvar)s*'\
                          % {'time':fixtime,'lat':fixlat,'long':fixlong,'speed':speed,'angle':angle,
                             'date':fixdate,'magvar':magvar}
            chk = checksum(base_string)['checksum']

            result['string'] = '$' + base_string + chk+'\n'

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="generate nmea string")

        # return
        return result