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
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
SERVER_MAP = SERVER['map']
SERVER_MAP_QUERY_PATH = SERVER_MAP['query path']
SERVER_MAP_FIELDS = SERVER_MAP['fields']
SERVER_GEOCLIP = SERVER['geo clip']
SERVER_GEOCLIP_REQUEST_PATH = SERVER_GEOCLIP['request path']
SERVER_GEOCLIP_FIELDS = SERVER_GEOCLIP['fields']
DB = HESTIA['database']
DB_GPS = DB['gps']
DB_GPS_TABLE = DB_GPS['table']
DB_GPS_FIELDS = DB_GPS['fields']
DB_AVL = DB['gps last position']
DB_AVL_TABLE = DB_AVL['table']
DB_AVL_FIELDS = DB_AVL['fields']

####################################################################################################
# Events ###########################################################################################
####################################################################################################
####################################################################################################


class GPS():
    """ Sub-library for ViM server GPS and AVL data interaction.
    """

    def generate_gps_event_for_site(self, site_id, disk_id=None, time=None, latitude=47.767365,
                                    longitude=-122.15175, speed=0, course=0, generated=False,
                                    update_avl=False, testcase=None):
        """ Simulate a GPS event for given site.
        @param site_id: the id of the site for which to generate the event.
        @param disk_id: the id of the disk for which to generate the event (leave None to auto-
            determine from site_id).
        @param time: the time for which to generate the event (for manual specification).
        @param latitude: the latitude for which to generate the event (for manual specification).
        @param longitude: the longitude for which to generate the event (for manual specification).
        @param speed: the speed for which to generate the event (for manual specification).
        @param course: the course (degrees) for which to generate the event (for manual specification).
        @param generated: whether the event is part of mass generation (limits logging and other
            functions for noise/speed control).
        @param update_avl: whether to update the avl table or not with this event (as the last event
            add).
        @param testcase: a testcase object supplied when executing function as part of a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'id' - the id of the generated event.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'id': None, 'avl id': None}

        try:
            if not generated:
                self.log.trace("%s ..." % operation.replace('_', ' '))

            # return diskID for site (if none given)
            if disk_id is None:
                disk_id = self.return_drive_for_site(site_id)['drive id']

            # set time to now (if none given)
            if time is None:
                time = self.utc.convert_string_to_time('now')
            else:
                # try to convert time
                try:
                    time = self.utc.convert_string_to_time(time)
                except BaseException:
                    time = time

            # define event entry
            entry = {
                DB_GPS_FIELDS['disk id']:   disk_id,
                DB_GPS_FIELDS['time']:      time,
                DB_GPS_FIELDS['latitude']:  latitude,
                DB_GPS_FIELDS['longitude']: longitude,
                DB_GPS_FIELDS['speed']:     speed,
                DB_GPS_FIELDS['direction']: course,
            }
            # insert event into database
            handle = self.db.db_handle
            if generated:
                self.db.add_entry_to_table(handle, DB_GPS_TABLE, entry)
            else:
                result['id'] = self.db.add_entry_to_table(handle, DB_GPS_TABLE, entry)['id']

            # update avl table (if specified)
            if update_avl:
                # determine if an entry for site already exists
                table = DB_AVL_TABLE
                return_field = DB_AVL_FIELDS['id']
                known_field = DB_AVL_FIELDS['site id']
                known_value = site_id
                exists = self.db.query_database_table_for_single_value(handle, table, return_field,
                                                              known_field, known_value)['value']

                # define base entry
                entry = {
                    DB_AVL_FIELDS['time']:      time,
                    DB_AVL_FIELDS['latitude']:  latitude,
                    DB_AVL_FIELDS['longitude']: longitude,
                    DB_AVL_FIELDS['speed']:     speed,
                    DB_AVL_FIELDS['direction']: course,
                }

                # if entry for site already exists, update
                if exists is not None:
                    avl_id = exists
                    self.db.update_entry_in_table(handle, table, avl_id, entry,
                                                  id_field=DB_AVL_FIELDS['id'])
                    result['avl id'] = avl_id

                # else, create a new entry
                else:
                    entry[DB_AVL_FIELDS['site id']] = site_id
                    result['avl id'] = self.db.add_entry_to_table(handle, table, entry)['id']

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None:
            testcase.gps_id = result['id']
            if result['avl id'] is not None: testcase.avl_id = result['avl id']
            testcase.gps_point = [latitude, longitude]
            testcase.processing = result['successful']
        return result