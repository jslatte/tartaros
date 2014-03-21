###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import HESTIA, TARTAROS
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

APP_DB = TARTAROS['database']
DB = HESTIA['database']
DB_SITES = DB['sites']
DB_SITES_TABLE = DB_SITES['table']
DB_SITES_FIELDS = DB_SITES['fields']
DB_DVRS = DB['dvrs']
DB_DVRS_TABLE = DB_DVRS['table']
DB_DVRS_FIELDS = DB_DVRS['fields']
DB_DRIVES = DB['drives']
DB_DRIVES_TABLE = DB_DRIVES['table']
DB_DRIVES_FIELDS = DB_DRIVES['fields']
DB_DVRHIST = DB['dvr history']
DB_DVRHIST_TABLE = DB_DVRHIST['table']
DB_DVRHIST_FIELDS = DB_DVRHIST['fields']
DB_DRIVEHIST = DB['drive history']
DB_DRIVEHIST_TABLE = DB_DRIVEHIST['table']
DB_DRIVEHIST_FIELDS = DB_DRIVEHIST['fields']

####################################################################################################
# Drive Status and History #########################################################################
####################################################################################################
####################################################################################################

class DriveStatus():
    """ Sub-library for drive status and history functionality.
    """

    def verify_no_hyphenated_drive_entry(self, testcase=None):
        """ Check the HardDisks table for a duplicate entry due to a hyphenated drive serial.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'found' - whether an abbreviated duplicate entry for a hyphenated drive serial
                was found or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'found': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # return list of all drives
            handle = self.db.db_handle
            table = DB_DRIVES_TABLE
            drives = self.db.query_database_table(handle, table)['response']

            # check if a duplicate copy of any hyphenated serial was entered
            for drive in drives:
                id = int(drive[0])
                serial = str(drive[1])

                # if the serial is hyphenated
                if '-' in serial:
                    abbr_serial = serial.split('-')[1]
                    # check each other drive for abbreviated serial
                    for other_drive in drives:
                        other_id = int(other_drive[0])
                        other_serial = str(other_drive[1])
                        if other_id != id and abbr_serial == other_serial:
                            self.log.trace("Found duplicate entry for hyphenated drive serial.")
                            result['found'] = True

            # verify
            if not result['found']:
                result['verified'] = True

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_dvr_information_retrieved_from_site(self, site_id, timeout=300, testcase=None):
        """
        @param site_id: the id of the site for which to verify information retrieved.
        @param timeout: the total amount of seconds to wait for the information to be retrieved.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine dvr id for site
            dvr_id = self.return_dvr_for_site(site_id)['dvr id']

            if dvr_id is not None:
                # return dvr data for site
                handle = self.db.db_handle
                table = DB_DVRS_TABLE
                dvr_serial = None
                dvr_model = None
                dvr_firmware = None
                interval = 15
                max_attempts = timeout/interval
                attempt = 1

                while dvr_serial is None or dvr_model is None or dvr_firmware is None\
                    or attempt <= max_attempts:
                    dvr_serial = self.db.query_database_table_for_single_value(handle,
                        table, DB_DVRS_FIELDS['serial'], DB_DVRS_FIELDS['id'], dvr_id)['value']
                    dvr_model = self.db.query_database_table_for_single_value(handle,
                        table, DB_DVRS_FIELDS['model'], DB_DVRS_FIELDS['id'], dvr_id)['value']
                    dvr_firmware = self.db.query_database_table_for_single_value(handle,
                        table, DB_DVRS_FIELDS['firmware'], DB_DVRS_FIELDS['id'], dvr_id)['value']

                    self.log.trace("Checking DVR information ...")
                    if dvr_serial is None:
                        self.log.trace("Failed to verify DVR Serial information retrieved. "
                                       "DVR Serial stored was %s." % dvr_serial)
                    if dvr_model is None or dvr_model == '':
                        self.log.trace("Failed to verify DVR Model information retrieved. "
                                       "DVR Model stored was %s." % dvr_model)
                    if dvr_firmware is None or dvr_firmware == '':
                        self.log.trace("Failed to verify DVR Firmware information retrieved. "
                                       "DVR Firmware stored was %s." % dvr_firmware)

                    if dvr_serial is None or dvr_model is None or dvr_firmware is None:
                        self.log.trace("Attempt %d. Re-attempting in %d seconds ..."
                                       % (attempt, interval))
                        attempt += 1
                        sleep(interval)
                    else:
                        self.log.trace("Verified DVR Information retrieved from site.")
                        result['verified'] = True
                        break


            else:
                self.log.error("No DVR found for site.")

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_drive_information_retrieved_from_site(self, site_id, timeout=300, testcase=None):
        """
        @param site_id: the id of the site for which to verify information retrieved.
        @param timeout: the total amount of seconds to wait for the information to be retrieved.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine drive id for site
            drive_id = self.return_drive_for_site(site_id)['drive id']

            if drive_id is not None:
                # return drive id for site
                handle = self.db.db_handle
                table = DB_DRIVES_TABLE
                drive_serial = None
                interval = 15
                max_attempts = timeout/interval
                attempt = 1

                while drive_serial or attempt <= max_attempts:
                    drive_serial = self.db.query_database_table_for_single_value(handle,
                    table, DB_DRIVES_FIELDS['serial'], DB_DRIVES_FIELDS['id'], drive_id)['value']

                    self.log.trace("Checking drive information ...")
                    if drive_serial is None:
                        self.log.trace("Failed to verify drive Serial information retrieved. "
                                       "Drive Serial stored was %s." % drive_serial)

                    if drive_serial is None:
                        self.log.trace("Attempt %d. Re-attempting in %d seconds ..."
                                       % (attempt, interval))
                        attempt += 1
                        sleep(interval)
                    else:
                        self.log.trace("Verified drive Information retrieved from site.")
                        result['verified'] = True
                        break

            else:
                self.log.error("No drive found for site.")

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def simulate_drive_swap_between_two_sites_without_drive_status_tracking(self, site_id, site2_id,
                                                                            testcase=None):
        """ Simulate a drive swap between two sites.
        INPUT
            site id: id of the first site for swapping.
            site 2 id: id of another site for swapping.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Simulating drive swap between site %s and %s ..." % (site_id, site2_id))
        result = {'successful': False}

        try:
            # determine disk ID for each site
            disk_id = self.return_drive_for_site(site_id)['drive id']
            disk2_id = self.return_drive_for_site(site2_id)['drive id']
            # simulate drive history for site 1 having previously had disk 2
            self.simulate_drive_history_for_site(site_id, drive_id=disk2_id,
                end=self.utc.convert_string_to_time('20 minutes ago'))
            self.simulate_drive_history_for_site(site_id, drive_id=disk_id,
                start=self.utc.convert_string_to_time('20 minutes ago'))
            # simulate drive history for site 2 having previously had disk 1
            self.simulate_drive_history_for_site(site2_id, drive_id=disk_id,
                end=self.utc.convert_string_to_time('20 minutes ago'))
            self.simulate_drive_history_for_site(site2_id, drive_id=disk2_id,
                start=self.utc.convert_string_to_time('20 minutes ago'))

            self.log.trace("Simulated drive swap between site %s and %s." % (site_id, site2_id))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate drive swap between site %s and %s"
                                               % (site_id, site2_id))

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def change_drive_in_dvr(self, dvr_id=1, drive_id=1, testcase=None):
        """ Change the current drive in a DVR.
        @param dvr_id: the id of the DVR that will have its drive changed.
        @param drive_id: the id of the drive to assign to the DVR.
        @param testcase: a testcase object supplied when executing function as part of
            a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            # update table
            self.db.update_table_field_for_entry(
                self.db.db_handle, DB_DVRS_TABLE, DB_DVRS_FIELDS['disk id'], drive_id,
                DB_DVRS_FIELDS['id'], dvr_id)

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.dvr_id = dvr_id
            testcase.drive_id = drive_id
        return result

    def simulate_dvr_change_for_site(self, site_id, testcase=None):
        """ Simulate a DVR change for specified site.
        INPUT
            site id: the id of the site for which to simulate a DVR change.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Simulating DVR change for site %s ..." % site_id)
        result = {'successful': False}

        try:
            # stop server
            self.stop_vim_server(mode='process')

            # determine DVR ID of site
            dvr_id = self.return_dvr_for_site(site_id)['dvr id']

            handle = self.db.db_handle

            # change serial
            self.db.update_table_field_for_entry(handle, DB_DVRS_TABLE, DB_DVRS_FIELDS['serial'],
                '00:00:00:00:00:00', DB_DVRS_FIELDS['id'], dvr_id)

            # change model
            self.db.update_table_field_for_entry(handle, DB_DVRS_TABLE, DB_DVRS_FIELDS['model'],
                'MR4', DB_DVRS_FIELDS['id'], dvr_id)

            # change firmware to older version
            self.db.update_table_field_for_entry(handle, DB_DVRS_TABLE, DB_DVRS_FIELDS['firmware'],
                '1.0.0',DB_DVRS_FIELDS['id'], dvr_id)

            # restart server
            self.start_vim_server(mode='service')
            self.log_in_to_vim(self.logged_in_user_name, self.logged_in_user_password)

            self.log.trace("Simulated DVR change for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate DVR change for site %s" % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_dvr_for_site(self, site_id, testcase=None):
        """ Return the ID of the current DVR associated with the given site.
        INPUT
            site id: id of the site for which to return the dvr id.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            dvr id: id of the dvr returned for the site.
        """

        self.log.debug("Returning DVR for site %s ..." % site_id)
        result = {'successful': False, 'dvr id':None}

        try:
            # determine DVR
            result['dvr id'] = self.db.query_database_table_for_single_value(self.db.db_handle,
                DB_SITES_TABLE, DB_SITES_FIELDS['dvr id'], DB_SITES_FIELDS['id'], site_id)['value']

            self.log.trace("Returned DVR for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return DVR for site %s" % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_drive_for_site(self, site_id, testcase=None):
        """ Return the ID of the current drive associated with the given site.
        INPUT
            site id: id of the site for which to return the drive id.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            drive id: id of the drive returned for the site.
        """

        self.log.debug("Returning drive for site %s ..." % site_id)
        result = {'successful': False, 'drive id':None}

        try:
            # determine DVR
            dvr_id = self.db.query_database_table_for_single_value(self.db.db_handle, DB_SITES_TABLE,
                DB_SITES_FIELDS['dvr id'], DB_SITES_FIELDS['id'], site_id)['value']

            # determine hard drive
            result['drive id'] =\
            self.db.query_database_table_for_single_value(self.db.db_handle, DB_DVRS_TABLE,
                DB_DVRS_FIELDS['disk id'], DB_DVRS_FIELDS['id'], dvr_id)['value']

            self.log.trace("Returned drive for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return drive for site %s" % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def simulate_firmware_upgrade_for_site(self, site_id, testcase=None):
        """ Simulate a firmware upgrade for specified site.
        INPUT
            site id: id of the site for which to simulate the firmware upgrade.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Simulating DVR firmware upgrade for site %s ..." % site_id)
        result = {'successful': False}

        try:
            # stop server
            self.stop_vim_server(mode='process')

            # determine DVR ID of site
            dvr_id = self.return_dvr_for_site(site_id)['dvr id']
            # change firmware to older version
            self.db.update_table_field_for_entry(self.db.db_handle, DB_DVRS_TABLE,
                DB_DVRS_FIELDS['firmware'], '1.0.0', DB_DVRS_FIELDS['id'], dvr_id)
            # restart server
            self.start_vim_server(mode='service')
            self.log_in_to_vim(self.logged_in_user_name, self.logged_in_user_password)

            self.log.trace("Simulated DVR firmware upgrade for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate DVR firmware upgrade for site %s" % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def simulate_dvr_history_for_site(self, site_id, dvr_id=None, start=None, end=None, testcase=None):
        """ Simulate DVR history for site.
        INPUT
            site id: id of the site for which to simulate DVR history.
            dvr id: id of DVr for site (if known) - eliminates redundant processing.
            start: the time that the DVR history should start (UTC string format).
            end: the time that the DVR history should end (UTC string format).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Simulating DVR history for site %s ..." % site_id)
        result = {'successful': False}

        try:
            # if no DVR ID given, return from database
            if dvr_id is None:
                dvr_id =\
                self.db.query_database_table_for_single_value(self.db.db_handle, DB_SITES_TABLE,
                    DB_SITES_FIELDS['dvr id'], DB_SITES_FIELDS['id'],site_id)['value']
                # if no start or end times given, set from 0 to now
            if start is None: start = 0
            if end is None: end = self.utc.convert_string_to_time('now')
            if 'ago' in start: start = self.utc.convert_string_to_time(start)
            if 'ago' in end: end = self.utc.convert_string_to_time(end)
            # define drive history parameters
            parameters = {
                DB_DVRHIST_FIELDS['dvr id']:       dvr_id,
                DB_DVRHIST_FIELDS['site id']:      site_id,
                DB_DVRHIST_FIELDS['start']:        start,
                DB_DVRHIST_FIELDS['end']:          end,
            }
            # insert entry into database
            self.db.add_entry_to_table(self.db.db_handle, DB_DVRHIST_TABLE, parameters)

            self.log.trace("Simulated DVR history for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate DVR history for site %s" % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def simulate_drive_history_for_site(self, site_id, dvr_id=None, drive_id=None, start=None,
                                        end=None, testcase=None):
        """ Simulate drive history for site.
        INPUT
            site id: id of the site for which to simulate drive history.
            dvr id: id of DVR for site (if known) - eliminates redundant processing.
            drive id: id of drive for site (if known) - eliminates redundant processing.
            start: the time that the drive history should start (UTC string format).
            end: the time that the drive history should end (UTC string format).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Simulating drive history for site %s ..." % site_id)
        result = {'successful': False}

        try:
            # if no DVR ID given, return from database
            if dvr_id is None:
                dvr_id =\
                self.db.query_database_table_for_single_value(self.db.db_handle, DB_SITES_TABLE,
                    DB_SITES_FIELDS['dvr id'], DB_SITES_FIELDS['id'],site_id)['value']

            # if no disk ID given, return from database
            if drive_id is None:
                drive_id = self.db.query_database_table_for_single_value(self.db.db_handle,
                    DB_DVRS_TABLE, DB_DVRS_FIELDS['disk id'],
                    DB_DVRS_FIELDS['id'], dvr_id)['value']

            # if no start or end times given, set from 0 to now
            if start is None: start = 0
            if end is None: end = self.utc.convert_string_to_time('now')
            try:
                if 'ago' in str(start): start = self.utc.convert_string_to_time(start)
                if 'ago' in str(end): end = self.utc.convert_string_to_time(end)
            except BaseException:
                pass
            # define drive history parameters
            parameters = {
                DB_DRIVEHIST_FIELDS['dvr id']:       dvr_id,
                DB_DRIVEHIST_FIELDS['disk id']:      drive_id,
                DB_DRIVEHIST_FIELDS['start']:        start,
                DB_DRIVEHIST_FIELDS['end']:          end,
                DB_DRIVEHIST_FIELDS['start type']:   0,
                DB_DRIVEHIST_FIELDS['end type']:     0,
            }
            # insert entry into database
            self.db.add_entry_to_table(self.db.db_handle, DB_DRIVEHIST_TABLE, parameters)

            self.log.trace("Simulated drive history for site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate drive history for site %s" % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_site_drive_status(self, site_id, site=None, testcase=None):
        """ Verify the current hard drive status of a site.
        INPUT
            site id: id of the added site for which to verify the drive status.
            site: the type of site to verify (see database Sites table for details). If left
                as None, will attempt to determine site based on site name.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying the current hard drive status of site %s ..." % site_id)
        result = {'successful': False, 'verified': False}

        try:
            # determine dvr id of site
            if site is not None:
                dvr_id = self.app_db.return_site_data(site)['site data']['dvr id']
            else:
                dvr_id = self.app_db.query_database_table_for_single_value(self.app_db.db_handle,
                    APP_DB['tables']['dvrs'], APP_DB['dvrs']['fields']['id'],
                    APP_DB['dvrs']['fields']['name'],
                    testcase.site_name)['value']

            # return dvr data for site type from app database
            dvr_data = self.app_db.return_dvr_data(dvr_id)['dvr data']
            drive_serial = dvr_data['drive serial']

            # determine site drive ID
            disk_id = self.return_drive_for_site(site_id)['drive id']

            # verify current drive status of the site
            attempt = 1
            while attempt <= 5 and not result['verified']:
                # counter to track failed verifications
                invalids = 0

                # verify drive serial
                serial = self.db.query_database_table_for_single_value(self.db.db_handle,
                    DB_DRIVES_TABLE, DB_DRIVES_FIELDS['serial'], DB_DRIVES_FIELDS['id'],
                    disk_id)['value']
                if serial != drive_serial: invalids += 1

                # update result if all verifications succeeded
                if invalids == 0:
                    self.log.trace("Verified current hard drive status for site.")
                    result['verified'] = True
                elif invalids > 0 and attempt < 5:
                    self.log.trace("Failed to verify current hard drive status for site (attempt %s). "
                        "Re-attempting ..." % attempt)
                    sleep(5)
                else:
                    self.log.warn("Failed to verify current hard drive status for site.")
                # increment counter
                attempt += 1

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify the current hard drive status of site %s"
                                               % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_site_dvr_status(self, site_id, site=None, testcase=None):
        """ Verify the current hard drive status of a site.
        INPUT
            site id: id of the added site for which to verify the DVR status.
            site: the type of site to verify (see database Sites table for details). If left
                as None, will attempt to determine site based on site name.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying the current DVR status of site %s ..." % site_id)
        result = {'successful': False, 'verified': False}

        try:
            # determine dvr id of site
            if site is not None:
                dvr_id = self.app_db.return_site_data(site)['site data']['dvr id']
            else:
                dvr_id = self.app_db.query_database_table_for_single_value(self.app_db.db_handle,
                    APP_DB['tables']['dvrs'], APP_DB['dvrs']['fields']['id'],
                    APP_DB['dvrs']['fields']['name'],
                    testcase.site_name)['value']

            # return dvr data for site type from app database
            dvr_data = self.app_db.return_dvr_data(dvr_id)['dvr data']
            dvr_serial = dvr_data['serial']
            dvr_model = dvr_data['model']
            dvr_firmware = dvr_data['firmware']

            # determine site DVR ID
            dvr_id = self.return_dvr_for_site(site_id)['dvr id']

            # verify current DVR status of the site
            attempt = 1
            while attempt <= 5 and not result['verified']:
                # counter to track failed verifications
                invalids = 0

                # verify DVR serial
                serial = self.db.query_database_table_for_single_value(self.db.db_handle,
                    DB_DVRS_TABLE, DB_DVRS_FIELDS['serial'], DB_DVRS_FIELDS['id'],
                    dvr_id)['value']
                if serial != dvr_serial:
                    self.log.warn("Expected serial to be %s, but was %s." % (dvr_serial, serial))
                    invalids += 1

                # verify DVR model
                model = self.db.query_database_table_for_single_value(self.db.db_handle,
                    DB_DVRS_TABLE, DB_DVRS_FIELDS['model'], DB_DVRS_FIELDS['id'],
                    dvr_id)['value']
                if model != dvr_model:
                    self.log.warn("Expected model to be %s, but was %s." % (dvr_model, model))
                    invalids += 1

                # verify DVR firmware
                firmware = self.db.query_database_table_for_single_value(self.db.db_handle,
                    DB_DVRS_TABLE, DB_DVRS_FIELDS['firmware'], DB_DVRS_FIELDS['id'],
                    dvr_id)['value']
                if firmware != dvr_firmware:
                    invalids += 1
                    self.log.warn("Expected firmware to be %s, but was %s." % (dvr_firmware, firmware))
                    invalids += 1

                # update result if all verifications succeeded
                if invalids == 0:
                    self.log.trace("Verified current hard drive status for site.")
                    result['verified'] = True
                elif invalids > 0 and attempt < 5:
                    self.log.trace("Failed to verify current hard drive status for site (attempt %s). "
                                   "Re-attempting ..." % attempt)
                    sleep(5)
                else:
                    self.log.warn("Failed to verify current hard drive status for site.")
                    # increment counter
                attempt += 1

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify the current hard drive status of site %s"
                                               % site_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result