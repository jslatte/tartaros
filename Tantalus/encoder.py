###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from binascii import hexlify, unhexlify
from datetime import datetime
from time import time
from Ixion import Ixion
from mapping import AdminSDKMap, SearchSDKMap
from random import randint

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Encoder ##########################################################################################
####################################################################################################
####################################################################################################


class Encoder():
    """ Sub-library of functions for encoding DVR responses (to ViM SDK)."""

    def build_gps_event_data_packet(self, iteration, dynamic=False):
        """ Build a packet of GPS event data (100 events).
        INPUT
            iteration: the batch of 100 events (in sequence of entire generation) to be made.
                NOTE: will be multiplied by 100 to determine oldest time value.
            template: a response template for splicing in GPS event data.
        OUPUT
            successful: whether the function executed successfully or not.
            packet: a hex-encoded string of GPS binary data.
        """

        template = '000008036508000000817416ae15e72d01461473003a00000000000000000000000000' \
                   '%(event 1)s' \
                   '000008036508000000857416ae0de82d01a01473003c00000000000000000000000000' \
                   '%(event 2)s' \
                   '0000080365080000008a7416ae01e92d01fc1473003c00000000000000000000000000' \
                   '%(event 3)s' \
                   '0000080365080000008e7416aef5e92d01581573003c00000000000000000000000000' \
                   '%(event 4)s' \
                   '000008036508000000927416aee5ea2d01b41573003c00000000000000000000000000' \
                   '%(event 5)s' \
                   '000008036508000000967416aed1eb2d01101673003c00000000000000000000000000' \
                   '%(event 6)s' \
                   '0000080365080000009a7416aec5ec2d016c1673003c00000000000000000000000000' \
                   '%(event 7)s' \
                   '0000080365080000009e7416aeb9ed2d01c81673003c00000000000000000000000000' \
                   '%(event 8)s' \
                   '000008036508000000a27416aea9ee2d01241773003c00000000000000000000000000' \
                   '%(event 9)s' \
                   '000008036508000000a67416ae9def2d01801773003c00000000000000000000000000' \
                   '%(event 10)s' \
                   '000008036508000000aa7416ae8df02d01dc1773003a00000000000000000000000000' \
                   '%(event 11)s' \
                   '000008036508000000ae7416ae85f12d01361873003c00000000000000000000000000' \
                   '%(event 12)s' \
                   '000008036508000000b27416ae7df22d01921873003c00000000000000000000000000' \
                   '%(event 13)s' \
                   '000008036508000000b67416ae6df32d01ee1873003c00000000000000000000000000' \
                   '%(event 14)s' \
                   '000008036508000000ba7416ae65f42d014a1973003c00000000000000000000000000' \
                   '%(event 15)s' \
                   '000008036508000000c27416ae55f52d01a61973003c00000000000000000000000000' \
                   '%(event 16)s' \
                   '000008036508000000c67416ae49f62d01021a73003c00000000000000000000000000' \
                   '%(event 17)s' \
                   '000008036508000000ca7416ae35f72d015e1a73003c00000000000000000000000000' \
                   '%(event 18)s' \
                   '000008036508000000ce7416ae29f82d01ba1a73003c00000000000000000000000000' \
                   '%(event 19)s' \
                   '000008036508000000d27416ae1df92d01161b73003c00000000000000000000000000' \
                   '%(event 20)s' \
                   '000008036508000000d67416ae11fa2d01721b73003a00000000000000000000000000' \
                   '%(event 21)s' \
                   '000008036508000000da7416aefdfa2d01cc1b73003c00000000000000000000000000' \
                   '%(event 22)s' \
                   '000008036508000000de7416aef5fb2d01281c73003c00000000000000000000000000' \
                   '%(event 23)s' \
                   '000008036508000000e27416aee1fc2d01841c73003c00000000000000000000000000' \
                   '%(event 24)s' \
                   '000008036508000000e77416aed9fd2d01e01c73003c00000000000000000000000000' \
                   '%(event 25)s' \
                   '000008036508000000eb7416aecdfe2d013c1d73003c00000000000000000000000000' \
                   '%(event 26)s' \
                   '000008036508000000ef7416aeb9ff2d01981d73003c00000000000000000000000000' \
                   '%(event 27)s' \
                   '000008036508000000f37416aea9002e01f41d73003c00000000000000000000000000' \
                   '%(event 28)s' \
                   '000008036508000000f77416aea1012e01501e73003c00000000000000000000000000' \
                   '%(event 29)s' \
                   '000008036508000000fb7416ae91022e01ac1e73003c00000000000000000000000000' \
                   '%(event 30)s' \
                   '000008036508000000037516ae81032e01081f73003a00000000000000000000000000' \
                   '%(event 31)s' \
                   '000008036508000000077516ae75042e01621f73003c00000000000000000000000000' \
                   '%(event 32)s' \
                   '0000080365080000000b7516ae69052e01be1f73003c00000000000000000000000000' \
                   '%(event 33)s' \
                   '0000080365080000000f7516ae61062e011a2073003c00000000000000000000000000' \
                   '%(event 34)s' \
                   '000008036508000000137516ae4d072e01762073003c00000000000000000000000000' \
                   '%(event 35)s' \
                   '000008036508000000177516ae3d082e01d22073003c00000000000000000000000000' \
                   '%(event 36)s' \
                   '0000080365080000001b7516ae31092e012e2173003c00000000000000000000000000' \
                   '%(event 37)s' \
                   '0000080365080000001f7516ae250a2e018a2173003c00000000000000000000000000' \
                   '%(event 38)s' \
                   '000008036508000000237516ae150b2e01e62173003c00000000000000000000000000' \
                   '%(event 39)s' \
                   '000008036508000000277516ae090c2e01422273003c00000000000000000000000000' \
                   '%(event 40)s' \
                   '0000080365080000002b7516aef90c2e019e2273003a00000000000000000000000000' \
                   '%(event 41)s' \
                   '0000080365080000002f7516aeed0d2e01f82273003c00000000000000000000000000' \
                   '%(event 42)s' \
                   '000008036508000000337516aedd0e2e01542373003c00000000000000000000000000' \
                   '%(event 43)s' \
                   '000008036508000000377516aed10f2e01b02373003c00000000000000000000000000' \
                   '%(event 44)s' \
                   '0000080365080000003b7516aec1102e010c2473003c00000000000000000000000000' \
                   '%(event 45)s' \
                   '000008036508000000437516aeb1112e01682473003c00000000000000000000000000' \
                   '%(event 46)s' \
                   '000008036508000000477516aea1122e01c42473003c00000000000000000000000000' \
                   '%(event 47)s' \
                   '0000080365080000004b7516ae99132e01202573003c00000000000000000000000000' \
                   '%(event 48)s' \
                   '0000080365080000004f7516ae89142e017c2573003c00000000000000000000000000' \
                   '%(event 49)s' \
                   '000008036508000000537516ae7d152e01d82573003c00000000000000000000000000' \
                   '%(event 50)s' \
                   '000008036508000000577516ae75162e01342673003a00000000000000000000000000' \
                   '%(event 51)s' \
                   '0000080365080000005c7516ae65172e018e2673003c00000000000000000000000000' \
                   '%(event 52)s' \
                   '000008036508000000607516ae59182e01ea2673003c00000000000000000000000000' \
                   '%(event 53)s' \
                   '000008036508000000647516ae4d192e01462773003c00000000000000000000000000' \
                   '%(event 54)s' \
                   '000008036508000000687516ae3d1a2e01a22773003c00000000000000000000000000' \
                   '%(event 55)s' \
                   '0000080365080000006c7516ae311b2e01fe2773003c00000000000000000000000000' \
                   '%(event 56)s' \
                   '000008036508000000707516ae211c2e015a2873003c00000000000000000000000000' \
                   '%(event 57)s' \
                   '000008036508000000747516ae151d2e01b62873003c00000000000000000000000000' \
                   '%(event 58)s' \
                   '000008036508000000787516ae011e2e01122973003c00000000000000000000000000' \
                   '%(event 59)s' \
                   '000008036508000000807516aef51e2e016e2973003c00000000000000000000000000' \
                   '%(event 60)s' \
                   '000008036508000000847516aee51f2e01ca2973003a00000000000000000000000000' \
                   '%(event 61)s' \
                   '000008036508000000887516aed5202e01242a73003c00000000000000000000000000' \
                   '%(event 62)s' \
                   '0000080365080000008c7516aec9212e01802a73003c00000000000000000000000000' \
                   '%(event 63)s' \
                   '000008036508000000907516aeb9222e01dc2a73003c00000000000000000000000000' \
                   '%(event 64)s' \
                   '000008036508000000947516aead232e01382b73003c00000000000000000000000000' \
                   '%(event 65)s' \
                   '000008036508000000987516ae9d242e01942b73003c00000000000000000000000000' \
                   '%(event 66)s' \
                   '0000080365080000009c7516ae8d252e01f02b73003c00000000000000000000000000' \
                   '%(event 67)s' \
                   '000008036508000000a07516ae81262e014c2c73003c00000000000000000000000000' \
                   '%(event 68)s' \
                   '000008036508000000a47516ae71272e01a82c73003c00000000000000000000000000' \
                   '%(event 69)s' \
                   '000008036508000000a87516ae61282e01042d73003c00000000000000000000000000' \
                   '%(event 70)s' \
                   '000008036508000000ac7516ae51292e01602d73003a00000000000000000000000000' \
                   '%(event 71)s' \
                   '000008036508000000b07516ae412a2e01ba2d73003c00000000000000000000000000' \
                   '%(event 72)s' \
                   '000008036508000000b47516ae312b2e01162e73003c00000000000000000000000000' \
                   '%(event 73)s' \
                   '000008036508000000b87516ae252c2e01722e73003c00000000000000000000000000' \
                   '%(event 74)s' \
                   '000008036508000000c07516ae192d2e01ce2e73003c00000000000000000000000000' \
                   '%(event 75)s' \
                   '000008036508000000c47516ae0d2e2e012a2f73003c00000000000000000000000000' \
                   '%(event 76)s' \
                   '000008036508000000c87516aefd2e2e01862f73003c00000000000000000000000000' \
                   '%(event 77)s' \
                   '000008036508000000cc7516aef12f2e01e22f73003c00000000000000000000000000' \
                   '%(event 78)s' \
                   '000008036508000000d07516aee9302e013e3073003c00000000000000000000000000' \
                   '%(event 79)s' \
                   '000008036508000000d47516aed9312e019a3073003c00000000000000000000000000' \
                   '%(event 80)s' \
                   '000008036508000000d87516aed1322e01f63073003a00000000000000000000000000' \
                   '%(event 81)s' \
                   '000008036508000000dc7516aebd332e01503173003c00000000000000000000000000' \
                   '%(event 82)s' \
                   '000008036508000000e07516aead342e01ac3173003c00000000000000000000000000' \
                   '%(event 83)s' \
                   '000008036508000000e57516aea1352e01083273003c00000000000000000000000000' \
                   '%(event 84)s' \
                   '000008036508000000e97516ae91362e01643273003c00000000000000000000000000' \
                   '%(event 85)s' \
                   '000008036508000000ed7516ae85372e01c03273003c00000000000000000000000000' \
                   '%(event 86)s' \
                   '000008036508000000f17516ae75382e011c3373003c00000000000000000000000000' \
                   '%(event 87)s' \
                   '000008036508000000f57516ae6d392e01783373003c00000000000000000000000000' \
                   '%(event 88)s' \
                   '000008036508000000f97516ae613a2e01d43373003c00000000000000000000000000' \
                   '%(event 89)s' \
                   '000008036508000000017616ae4d3b2e01303473003c00000000000000000000000000' \
                   '%(event 90)s' \
                   '000008036508000000057616ae453c2e018c3473003a00000000000000000000000000' \
                   '%(event 91)s' \
                   '000008036508000000097616ae353d2e01e63473003c00000000000000000000000000' \
                   '%(event 92)s' \
                   '0000080365080000000d7616ae253e2e01423573003c00000000000000000000000000' \
                   '%(event 93)s' \
                   '000008036508000000117616ae193f2e019e3573003c00000000000000000000000000' \
                   '%(event 94)s' \
                   '000008036508000000157616ae09402e01fa3573003c00000000000000000000000000' \
                   '%(event 95)s' \
                   '000008036508000000197616aefd402e01563673003c00000000000000000000000000' \
                   '%(event 96)s' \
                   '0000080365080000001d7616aeed412e01b23673003c00000000000000000000000000' \
                   '%(event 97)s' \
                   '000008036508000000217616aee5422e010e3773003c00000000000000000000000000' \
                   '%(event 98)s' \
                   '000008036508000000257616aed9432e016a3773003c00000000000000000000000000' \
                   '%(event 99)s' \
                   '000008036508000000297616aecd442e01c63773003c00000000000000000000000000' \
                   '%(event 100)s'

        if iteration == 1:
            template = 'd4250000726400' + template# + '0000'
            #template = 'ad240000726400' + template + '0000'

        else:
            template = 'ad240000726400' + template + '0000'

        self.log.debug("Building GPS event data packet ...")
        result = {'successful': False, 'packet': ''}

        try:
            # build dictionary of GPS events
            gps_events = {}
            self.ixion = Ixion(self.log)
            num_events = 100
            utc_time_in_seconds = time() + (60 * 60)
            for i in range(1, num_events + 1):
                time_in_seconds = utc_time_in_seconds
                time_in_seconds -= ((num_events * iteration) + 1)
                time_in_seconds += i
                date_time = datetime.utcfromtimestamp(time_in_seconds)

                hour = date_time.hour - 1
                min = date_time.minute
                sec = date_time.second
                day = date_time.day
                month = date_time.month
                year = int(str(date_time.year)[2:])

                # determine lat/long
                if '1' in str(i)[-1:]:
                    lat = 4800.2
                    long = -12167.8

                else:
                    #lat = 4800.23
                    #long = -12167.77
                    lat = float("480%d.%d%d" % (randint(1, 9), randint(1, 9), randint(1, 9)))
                    long = float("-1216%d.%d%d" % (randint(1, 9), randint(1, 9), randint(1, 9)))

                nmea_string = self.ixion.generate_nmea_string([hour, min, sec], [day, month, year], lat,
                                                              long, self.ixion.speed)['string']

                gps_events['event %d' % i] = hexlify(nmea_string.strip())

            # update packet with gps events dict
            packet = template % gps_events
            self.log.trace(packet)
            self.log.trace(len(packet))
            # NOTE: The length of this packet (in template) MUST BE 18778 or ViM will not accept it as
            #       a valid packet of data.

            # update return variables
            result['packet'] = packet

            self.log.trace("Built GPS event data packet.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="build GPS event data packet")

        # return
        return result

    def build_dvr_response_dict_to_admin_sdk(self, site_id):
        """ Build a data dict of DVR responses to the admin SDK to simulate connecting to a DVR admin port.
        INPUT
            site id: a numerical id to distinguish this site from others (not necessarily related to ViM site ID).
        OUTPUT
            successful: whether the function executed successfully or not.
            response dict: data dict of DVR responses.
        """

        self.log.debug("Building DVR response dict for admin SDK for site %s ..." % site_id)
        result = {'successful': False, 'response dict': []}

        try:
            # instance admin sdk mapping object
            admin_sdk_map = AdminSDKMap()

            # translate site id (to fit in hex strings)
            if site_id < 10:
                s_site_id = '000%d' % site_id
            elif site_id < 100:
                s_site_id = '00%d' % site_id
            elif site_id < 1000:
                s_site_id = '0%d' % site_id
            else:
                s_site_id = '%d' % site_id

            # define admin SDK values
            dvr_serial = '0000000%s%s' % (self.instance, s_site_id)
            firmware_version = hexlify("1.5.1")
            drive_serial = hexlify('FFF%s%s' % (self.instance, s_site_id))
            drive_model = hexlify('ST31000525SV')

            # build response dict
            result['response dict'] = {
                admin_sdk_map.dvr_connection_request: [admin_sdk_map.dvr_connection_request_response
                                                       % {'dvr serial': dvr_serial,
                                                          'firmware version': firmware_version}],
                admin_sdk_map.dvr_request_2: [admin_sdk_map.dvr_request_2_response],
                admin_sdk_map.dvr_drive_info_request: [admin_sdk_map.dvr_drive_info_response
                                                       % {'drive serial': drive_serial,
                                                          'drive model': drive_model},
                                                       admin_sdk_map.dvr_syslog_event_pckt
                                                       % {'time': '00000000'}],
                admin_sdk_map.dvr_syslog_event_request: [admin_sdk_map.dvr_syslog_event_pckt],
                admin_sdk_map.dvr_syslog_event_request2: [admin_sdk_map.dvr_syslog_event_pckt],
                admin_sdk_map.dvr_last_request: admin_sdk_map.dvr_last_request_response,
            }

            self.log.trace("Built DVR response dict for admin SDK.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="build DVR response dict for admin SDK")

        # return
        return result

    def build_dvr_response_list_to_search_sdk(self, num_gps_events, site_id=None):
        """ Build a data list of DVR responses to the search SDK to simulate connecting to a DVR search port.
        INPUT
            num gps events: the number of GPS events to be generated.
            site id: a numerical id to distinguish this site from others (not necessarily related to ViM site ID).
        OUTPUT
            successful: whether the function executed successfully or not.
            response dict: data dcit of DVR responses.
        """

        self.log.debug("Building DVR response dict to search SDK for site %s ..." % site_id)
        result = {'successful': False, 'response dict': []}

        try:
            # instance admin sdk mapping object
            search_sdk_map = SearchSDKMap()

            # translate site id (to fit in hex strings)
            if site_id < 10:
                s_site_id = '000%d' % site_id
            elif site_id < 100:
                s_site_id = '00%d' % site_id
            elif site_id < 1000:
                s_site_id = '0%d' % site_id
            else:
                s_site_id = '%d' % site_id

            # define search SDK values
            dvr_serial = '0000000%s%s' % (self.instance, s_site_id)
            firmware_version = hexlify("1.5.1")
            drive_serial = hexlify('FFF%s%s' % (self.instance, s_site_id))
            drive_model = hexlify('ST31000525SV')

            # build response dict
            result['response dict'] = {
                search_sdk_map.dvr_connection_request: [search_sdk_map.dvr_connection_request_response %
                                                        {'dvr serial': dvr_serial,
                                                         'firmware version': firmware_version},
                                                        search_sdk_map.dvr_connection_request_response2],
                search_sdk_map.dvr_connection_request2: [search_sdk_map.dvr_connection_request_response %
                                                        {'dvr serial': dvr_serial,
                                                         'firmware version': firmware_version},
                                                        search_sdk_map.dvr_connection_request_response2],
                search_sdk_map.dvr_request_2:   [search_sdk_map.dvr_request_2_response],
                #search_sdk_map.dvr_request_3:   [],
                search_sdk_map.dvr_request_3b:  [search_sdk_map.dvr_request_3b_response,
                                                 search_sdk_map.dvr_request_3b_response2],
                #search_sdk_map.dvr_request_3c:  [search_sdk_map.dvr_request_3c_response],
                search_sdk_map.dvr_num_gps_events_request:  [search_sdk_map.dvr_num_gps_events_request_response
                                                             % {'num gps events': hex(num_gps_events-100).replace('0x', '')}],
                '': [],
                search_sdk_map.dvr_request_unknown: []
            }

            self.log.trace("Built DVR response dict to search SDK.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="build DVR response dict to search SDK")

        # return
        return result