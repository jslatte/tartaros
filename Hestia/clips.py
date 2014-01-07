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
from os import listdir, path, system, mkdir
from time import sleep, time
from utility import lock_file, unlock_file, change_file_time
from random import randint

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
CLIPREQ = SERVER['clip request']
CLIPREQ_PATH = CLIPREQ['path']
CLIPREQ_FIELDS = CLIPREQ['fields']
SERVER_COC = SERVER['custody']
SERVER_COC_PATH = SERVER_COC['query path']
SERVER_COC_FIELDS = SERVER_COC['fields']
SERVER_COC_COLUMNS = SERVER_COC['columns']
DB = HESTIA['database']
DB_CLIPLOG = DB['clip log']
DB_CLIPLOG_TABLE = DB_CLIPLOG['table']
DB_CLIPLOG_FIELDS = DB_CLIPLOG['fields']
CLIP_DOWNLOAD_TYPES = DB_CLIPLOG['download types']
DB_COC = DB['custody']
DB_COC_TABLE = DB_COC['table']
DB_COC_FIELDS = DB_COC['fields']
ACTION_TO_ACTION_VAL = DB_COC['action to action value']
ACTION_VAL_TO_CLIP_STATUS = DB_COC['action value to clip status']
DB_SITEGROUPS = DB['site groups']
DB_SITEGROUPS_TABLE = DB_SITEGROUPS['table']
DB_SITEGROUPS_FIELDS = DB_SITEGROUPS['fields']
DB_SITES_TABLE = HESTIA['database']['sites']['table']
DB_SITES_FIELDS = HESTIA['database']['sites']['fields']
DB_EVENTLOG_TABLE = HESTIA['database']['event log']['table']
DB_EVENTLOG_FIELDS = HESTIA['database']['event log']['fields']
CLIPACT = SERVER['clip actions']
CLIPACT_SCHEDULE_DELETE = CLIPACT['schedule for delete path']
CLIPACT_PRESERVE = CLIPACT['preserve path']
CLIPACT_CANCEL = CLIPACT['cancel path']
NOTES = SERVER['clip notations']
NOTES_FIELDS = NOTES['fields']
NOTES_PATH = NOTES['path']

####################################################################################################
# Clips ############################################################################################
####################################################################################################
####################################################################################################


class Clips():
    """ Sub-library for ViM server clip requests and download functionality.
    """

    def add_note_to_clip(self, clip_id, note, clip_type=None, testcase=None):
        """ Add a note to specified clip.
        @param clip_id: the id of the clip to which to add a note.
        @param note: the string to add as a note to the clip.
        @param clip_type: the type of clip (e.g., custom, custom video event, location, alarm,
            custom health event).
        @param testcase: a testcase object supplied when executing function as part of a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # build data packet to send to server
            packet = {
                NOTES_FIELDS['clip id']:       clip_id,
                NOTES_FIELDS['notation']:      note,
            }

            # send data packet to server
            url = self.server_url + NOTES_PATH
            response = self.post_http_request(url, packet)['response']

            # verify post was successful
            if response == 'Ok':
                result['successful'] = True
            else:
                self.log.warn("Failed to send request to server.")

            # verify note added to clip
            if result['successful']:
                result['verified'] = self.verify_note_added_to_clip(clip_id, note,
                                                                    clip_type)['verified']

            self.log.trace("... done %s." % operation)
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_note_added_to_clip(self, clip_id, note, clip_type=None, testcase=None):
        """ Verify that specified note was added to specified clip.
        @param clip_id: the id of the clip to which the note was added.
        @param note: the string to which the note was added.
        @param clip_type: the type of clip (e.g., custom, custom video event, location, alarm,
            custom health event).
        @param testcase: a testcase object supplied when executing function as part of a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine page to query
            if clip_type is not None:
                if clip_type.lower() == 'custom'\
                    or clip_type.lower() == 'custom video event'\
                    or clip_type.lower() == 'location'\
                    or clip_type.lower() == 'alarm':
                    page = 'video clip log'
                elif clip_type.lower() == 'custom health event':
                    page = 'health clip log'
                else:
                    page = 'video clip log'
            else:
                page = 'video clip log'

            # url encode note (for comparison)
            note = note.replace(' ', '%20').replace('(', '%28').replace(')', '%29')

            # query page for clip, expecting note
            expected = {'notation': note}
            parameters = {
                'entry id': clip_id,
                'expected': expected,
                }
            result['verified'] = self.query_page(page, data=parameters)['verified']

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def age_simulated_orphaned_clip_file_for_site_past_expiration(self, path, site_id,
                                                                  testcase=None):
        """
        INPUT
            path: windows path to the clip file.
            site id: id of the site of the orphaned clip file.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Aging orphaned clip file %s past expiration ..." % path)
        result = {'successful': False}

        try:
            # age orphaned clip file
            age = int(self.return_bin_timer_for_site(site_id, 'DGP')['bin timer'])
            age += 1
            age = '%d days ago' % age
            change_file_time(self.log, path, age)

            self.log.trace("Aged orphaned clip file %s past expiration." % path)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="age orphaned clip file %s past expiration"
                                               % path)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_action_for_clip(self, clipID, action, testcase=None):
        """ Verify that a clip action entry exists for given clip.
        INPUT
            action: any a valid clip action from ACTIONS map.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying %s custody entry exists for %s ..." % (action, clipID))
        result = {'successful': False, 'verified': False}

        try:
            # query chain of custody for clip download failure entry
            actionValue = ACTION_TO_ACTION_VAL[action.lower()]
            attempt = 1

            while not result['verified']:
                # query clip log for entry with correct id and action value
                handle = self.db.db_handle
                table = DB_COC_TABLE
                return_field = DB_COC_FIELDS['id']
                addendum = "WHERE %s = '%s' AND " % (DB_COC_FIELDS['clip id'], clipID)\
                    + "%s = '%s'" % (DB_COC_FIELDS['value'], actionValue)
                try:
                    entry = self.db.query_database_table(handle, table, return_field=return_field,
                        addendum=addendum)['response'][0][0]
                except IndexError:
                    entry = None

                if entry is not None:
                    result['verified'] = True
                    self.log.trace("Entry for value %s found." % actionValue)
                else:
                    self.log.trace("Entry not found.")

                # if verifying clip deleted, check file
                if actionValue == ACTION_TO_ACTION_VAL['delete']:
                    table = DB_CLIPLOG_TABLE
                    return_field = DB_CLIPLOG_FIELDS['file path']
                    known_field = DB_CLIPLOG_FIELDS['id']
                    known_value = clipID
                    clipPath = self.db.query_database_table_for_single_value(handle, table,
                        return_field, known_field, known_value)['value']

                    # check if file exists
                    exists = path.exists(clipPath)
                    if exists:
                        result['verified'] = False
                        self.log.trace("Expected clip file to be deleted from local storage, "
                                       "but was found.")
                    else:
                        self.log.trace("Verified clip file does not exist.")

                # re-attempt or break
                if attempt < 5 and not result['verified']:
                    self.log.trace("Failed to verify clip action for clip (attempt %s). "
                                   "Re-attempting in 5 seconds ..." % attempt)
                    sleep(5)
                elif attempt == 5 and not result['verified']:
                    self.log.error("Failed to verify clip action for clip.")
                    break

                # increment
                attempt += 1

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify %s custody entry exists for %s"
                                               % (action, clipID))

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def cancel_pending_clips_for_event(self, event_id, testcase=None):
        """
        INPUT
            event id: id of the event for which to cancel pending clips.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Canceling pending clips for event %s ..." % event_id)
        result = {'successful': False, 'verified': False}

        try:
            # post request to server
            url = self.server_url + CLIPACT_CANCEL
            response = self.post_http_request(url, {'eventId': event_id})['response']

            # verify clips were canceled
            result['verified'] = self.verify_pending_clips_for_event_canceled(event_id)['verified']

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="cancel pending clips for event %s" % event_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_pending_clips_for_event_canceled(self, event_id, testcase=None):
        """
        INPUT
            event id: the event for which to verify clips were canceled.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying pending clips canceled for event %s ..." % event_id)
        result = {'successful': False, 'verified': False}

        try:
            # query clip log for clips for event
            handle = self.db.db_handle
            table = DB_CLIPLOG_TABLE
            return_field = DB_CLIPLOG_FIELDS['id']
            addendum = "WHERE %s = %s" % (DB_CLIPLOG_FIELDS['event id'], event_id)
            response = self.db.query_database_table(handle, table,
                return_field=return_field, addendum=addendum)['response']
            # parse clip ids into list
            clip_ids = []
            for raw_clip_id in response:
                clip_id = raw_clip_id[0]
                clip_ids.append(clip_id)

            # verify clips that have not downloaded or failed to download are canceled
            failures = False
            for clip_id in clip_ids:
                data = self.verify_clip_canceled(clip_id)
                canceled = data['verified']
                action_val = data['action value']

                # check if downloaded or failed already
                if not canceled and action_val >= 0:
                    self.log.trace("Clip %s already downloaded or failed to download." % clip_id)
                elif not canceled and action_val < 0:
                    self.log.trace("Clip %s was not canceled." % clip_id)
                    failures = True
                else:
                    self.log.trace("Clip %s canceled." % clip_id)

            if failures:
                self.log.trace("Failed to verify pending clips canceled for event %s." % event_id)
            else:
                self.log.trace("Verified pending clips canceled for event %s." % event_id)
                result['verified'] = True
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify clips canceled for event %s" % event_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_canceled(self, clip_id, testcase=None):
        """
        INPUT
            clip id: id of the clip to verify has been canceled.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying clip %s canceled ..." % clip_id)
        result = {'successful': False, 'verified': False, 'action value': None}

        try:
            # query clip log for clip download type
            handle = self.db.db_handle
            table = DB_CLIPLOG_TABLE
            return_field = DB_CLIPLOG_FIELDS['download type']
            known_field = DB_CLIPLOG_FIELDS['id']
            known_value = clip_id
            download_type = self.db.query_database_table_for_single_value(handle, table,
                return_field, known_field, known_value)['value']
            # if download type is between -99 and -200, clip was canceled
            if -200 < int(download_type) <= -100: clip_log_verified = True
            elif 100 <= int(download_type) < 200:
                self.log.warn("Clip canceled during download.")
                self.log.warn("Server processed command, but clip will still download.")
                clip_log_verified = True
            else:
                self.log.error("Failed to verify clip download type as canceled.")
                clip_log_verified = False

            # query chain of custody for canceled entry
            table = DB_COC_TABLE
            return_field = DB_COC_FIELDS['value']
            known_field = DB_COC_FIELDS['clip id']
            known_value = clip_id
            action_val = self.db.query_database_table_for_single_value(handle, table,
                return_field, known_field, known_value, max=True)['value']
            # if action value is canceled, clip was canceled
            if int(action_val) == ACTION_TO_ACTION_VAL['cancel']: coc_verified = True
            else:
                self.log.error("Failed to verify canceled custody entry for clip.")
                coc_verified = False

            if clip_log_verified and coc_verified:
                self.log.trace("Verified clip %s canceled." % clip_id)
                result['verified'] = True

            result['action value'] = action_val
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify clip %s canceled" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def preserve_clip(self, clip_id, testcase=None):
        """
        INPUT
            clip id: id of the clip to preserve.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Preserving clip %s ..." % clip_id)
        result = {'successful': False, 'verified': False}

        try:
            # post request to server
            url = self.server_url + CLIPACT_PRESERVE % clip_id
            response = self.get_http_request(url)['response']

            # verify clip was preserved
            if response.lower() == 'ok':
                result['successful'] = True
                result['verified'] = self.verify_clip_action_for_clip(clip_id,
                                                                      'preserve')['verified']
            else:
                result['successful'] = False
        except BaseException, e:
            self.handle_exception(e, operation="preserve clip %s" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def schedule_clip_for_delete(self, clip_id, testcase=None):
        """
        INPUT
            clip id: id of the clip to schedule for delete.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Scheduling clip %s for delete ..." % clip_id)
        result = {'successful': False, 'verified': False}

        try:
            # post request to server
            url = self.server_url + CLIPACT_SCHEDULE_DELETE % clip_id
            response = self.get_http_request(url)['response']

            # verify clip was scheduled for delete
            if response.lower() == 'ok':
                self.log.trace("Scheduled clip %s for delete." % clip_id)
                result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="schedule clip %s for delete" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def generate_clip_for_site(self, site_id, clip_type='custom', testcase=None):
        """
        INPUT
            site id: the id of the site for which to generate the clip.
            clip type: the type of clip to generate.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            clip id: the id of the clip generated.
            event id: the id of the event generated.
        """

        self.log.debug("Generating %s clip for site %s ..." % (clip_type, site_id))
        result = {'successful': False, 'verified': False}

        try:
            # generate event
            returned = self.generate_event_for_site(site_id, type=clip_type)
            event_id = returned['event id']
            event_start = returned['event start']

            # simulate clip request for event
            clip_id = self.simulate_clip_request_for_event(event_id, clip_type=clip_type,
                request_time='5 minutes ago')['clip id']

            # simulate clip download
            self.simulate_clip_download(clip_id)

            # assign results
            result['event id'] = event_id
            result['clip id'] = clip_id
            result['event start'] = event_start

            self.log.trace("Generated %s clip for site %s." % (clip_type, site_id))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="generate %s clip for site %s" % (clip_type, site_id))

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.event_id = result['event id']
            testcase.clip_id = result['clip id']
        return result

    def generate_clip_for_event(self, event_id, clip_type='custom', testcase=None):
        """
        INPUT
            event id: the id of the event for which to generate the clip.
            clip type: the type of clip to generate.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            clip id: the id of the clip generated.
            event id: the id of the event generated.
        """

        self.log.debug("Generating %s clip for event %s ..." % (clip_type, event_id))
        result = {'successful': False, 'verified': False}

        try:
            # determine clip start (from event start)
            handle = self.db.db_handle
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['start']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = event_id
            event_start = self.db.query_database_table_for_single_value(handle, table, return_field,
                                                                        known_field, known_value)['value']

            # simulate clip request for event
            clip_id = self.simulate_clip_request_for_event(event_id, clip_type=clip_type,
                                                           request_time='5 minutes ago')['clip id']

            # simulate clip download
            self.simulate_clip_download(clip_id)

            # assign results
            result['event id'] = event_id
            result['clip id'] = clip_id
            result['event start'] = event_start

            self.log.trace("Generated %s clip for event %s." % (clip_type, event_id))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="generate %s clip for event %s" % (clip_type, event_id))

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.event_id = result['event id']
            testcase.clip_id = result['clip id']
        return result

    def simulate_orphaned_clip_download_for_requested_clip(self, clip_id, testcase=None):
        """
        INPUT
            clip_id: id of the requested clip (with no files yet associated).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            path: the path to the simulated orphaned clip file.
        """

        self.log.debug("Simulating orphaned clip download for clip %s ..." % clip_id)
        result = {'successful': False, 'path': None}

        try:
            # return storage location
            storage_loc = self.return_storage_location_for_clip(clip_id)['storage loc']
            # return file name
            handle = self.db.db_handle
            table = DB_CLIPLOG_TABLE
            return_field = DB_CLIPLOG_FIELDS['file name']
            known_field = DB_CLIPLOG_FIELDS['id']
            known_value = clip_id
            file_name = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']

            # verify directory exists
            dirExists = path.exists(storage_loc)
            if not dirExists:
                self.log.trace("Directory does not exist, creating ...")
                mkdir(storage_loc)

            # create dummy BIN file
            file_name += ".bin"
            statement = 'copy NUL "%s%s"' % (storage_loc, file_name)
            system(statement)
            # update path to full
            file_path = '%s%s' % (storage_loc, file_name)
            # write some dummy data to file (so not 0 bytes)
            f = open(file_path, 'w')
            f.write('***SIMULATION***\nTHIS IS AN ORPHANED CLIP FILE.\n***SIMULATION***')
            f.close()

            result['path'] = file_path
            self.log.trace("Simulated orphaned clip download for clip %s." % clip_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate orphaned clip download for clip %s" % clip_id)

        # return
        if testcase is not None:
            testcase.orphaned_clip_path = result['path']
            testcase.processing = result['successful']
        return result

    def simulate_clip_download(self, clip_id, time=None, testcase=None):
        """
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Simulating clip download %s ...")
        result = {'successful': False, 'verified': False}

        try:
            # update clip file size, download type and time
            self.log.trace("Updating clip file size, download type, and time ...")
            fileSize = randint(48757, 148757)
            if time is not None:
                timeVal = self.utc.convert_string_to_time(time)
            else:
                timeVal = "strftime('%s','now')"
            statement = '''UPDATE %(table)s SET %(file time field)s = %(time val)s,
                    %(file size field)s=%(file size)s,%(file type field)s='1'
                    WHERE %(id field)s = %(id)s'''\
                        %{'table': DB_CLIPLOG_TABLE,
                          'file time field': DB_CLIPLOG_FIELDS['download time'],
                          'file size field': DB_CLIPLOG_FIELDS['file size'],
                          'file size': str(fileSize),
                          'file type field': DB_CLIPLOG_FIELDS['file type'],
                          'id field': DB_CLIPLOG_FIELDS['id'],
                          'id': str(clip_id), 'time val': timeVal}
            handle = self.db.db_handle
            self.db.execute_SQL(handle, statement)

            # query clip log for clip file name and event ID
            table = DB_CLIPLOG_TABLE
            return_field = DB_CLIPLOG_FIELDS['file name']
            known_field = DB_CLIPLOG_FIELDS['id']
            known_value = clip_id
            fileName = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            return_field = DB_CLIPLOG_FIELDS['event id']
            eventID = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']

            # query site groups for storage location
            storageLoc = self.return_storage_location_for_clip(clip_id)['storage loc']
            # query event log for disk ID
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['disk id']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = eventID
            diskID = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            # update ClipLog with FilePath
            self.log.trace('Updating clip file path ...')
            statement = '''UPDATE %(table)s SET %(file path field)s=%(file path)s
                                WHERE %(id field)s = %(id)s'''\
                        %{'table': DB_CLIPLOG_TABLE,
                          'file path field': DB_CLIPLOG_FIELDS['file path'],
                          'file path': str("'" + storageLoc + fileName + ".exe'"),
                          'id field': DB_CLIPLOG_FIELDS['id'],
                          'id': clip_id}
            self.db.execute_SQL(handle, statement)

            # create dummy clip file
            self.log.trace('Simulating clip file ...')
            # verify directory exists
            dirExists = path.exists(storageLoc)
            if not dirExists:
                self.log.trace("Directory does not exist, creating ...")
                mkdir(storageLoc)
            statement = 'copy NUL "%s%s"' % (storageLoc, fileName + ".exe")
            system(statement)

            # determine data for download action text
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['site id']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = eventID
            siteID = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            table = DB_SITES_TABLE
            return_field = DB_SITES_FIELDS['site name']
            known_field = DB_SITES_FIELDS['id']
            known_value = siteID
            siteName = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']

            # insert chain of custody request action
            self.log.trace('Updating clip action text ...')
            statement = '''INSERT INTO %(table)s (%(clip id field)s, %(type field)s,
                                %(value field)s, %(time field)s, %(text field)s)
                    VALUES ('%(clip id)s', 0, 0, %(time val)s,'%(disk id)s:%(site name)s');'''\
                        %{'table':DB_COC_TABLE,'clip id field':DB_COC_FIELDS['clip id'],
                          'type field':DB_COC_FIELDS['type'],
                          'value field':DB_COC_FIELDS['value'],
                          'time field':DB_COC_FIELDS['time'],
                          'text field':DB_COC_FIELDS['text'],
                          'clip id':clip_id,'disk id':diskID,'site name':siteName,'time val': timeVal}
            self.db.execute_SQL(handle, statement)

            self.log.trace("Simulated clip download for clip %s." % clip_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate clip download for clip %s" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def query_custody_for_clip(self, clip_id, testcase=None, not_allowed=False):
        """
        INPUT
            clip id: the id of the clip to return the chain of custody for.
            testcase: a testcase object supplied when executing function as part of a testcase step.
            not allowed: whether the action should be allowed or not.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the function was verified or not.
            entries: the custody entries returned for the clip.
        """

        self.log.debug("Querying server for custody of clip %s ..." % clip_id)
        result = {'successful': False, 'entries': [], 'verified': False}

        try:
            # query server chain of custody table for clip
            url = self.server_url + SERVER_COC_PATH % {'id': clip_id}
            response = self.query_server_table(url, SERVER_COC_COLUMNS)['response']

            # parse response into entries
            if response is not None or '':
                result['entries'] = response[1:]
                result['verified'] = True
            elif response == 'HTTP Error 404':
                if not_allowed:
                    self.log.trace("Verified querying custody for clip %s not allowed." % clip_id)
                    result['verified'] = True
                else:
                    self.log.error("Failed to verify querying custody for clip %s not allowed."
                                   % clip_id)
                    self.log.error("Expected response to be 'HTTP Error 404', but was %s." % response)

            self.log.trace("Queried server for custody of clip %s." % clip_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="query server for custody of clip %s" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def simulate_clip_request_for_event(self, event_id, clip_type='custom clip', author='admin',
                                        request_time=None, testcase=None):
        """ Simulate a clip request for given event.
        INPUT
            event id: the id of the event for which to generate a clip request.
            clip type: the type of clip to request.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            clip id: the id of the clip generated by the request.
        """

        self.log.debug("Simulating clip request for event %s ..." % event_id)
        result = {'successful': False, 'verified': False, 'clip id': None}

        try:
            # define default handle
            handle = self.db.db_handle

            # insert default clip entry into ClipLog
            statement = '''
            INSERT INTO %(table)s ('%(id field)s','%(event id field)s', '%(file name field)s')
                VALUES (NULL,'%(event id)s','')
            ''' % {'table':DB_CLIPLOG_TABLE, 'id field': DB_CLIPLOG_FIELDS['id'],
                 'file name field': DB_CLIPLOG_FIELDS['file name'],
                 'event id field': DB_CLIPLOG_FIELDS['event id'], 'event id': event_id}
            clip_id = self.db.execute_SQL(handle, statement, return_id=True)['id']

            # update clip download type
            download_type = CLIP_DOWNLOAD_TYPES[clip_type.lower()]
            statement = '''
            UPDATE %(table)s SET %(type field)s = '%(type)s'
                WHERE %(id field)s = '%(id)s'
            ''' % {'table': DB_CLIPLOG_TABLE, 'type field': DB_CLIPLOG_FIELDS['download type'],
                   'type': download_type, 'id field': DB_CLIPLOG_FIELDS['id'], 'id': clip_id}
            self.db.execute_SQL(handle, statement)

            # update clip length
            # return site ID for event
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['site id']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = event_id
            site_id = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            if clip_type.lower() == 'autoclip':
                # return event id from event (alarm in #)
                table = DB_EVENTLOG_TABLE
                return_field = DB_EVENTLOG_FIELDS['event id']
                known_field = DB_EVENTLOG_FIELDS['id']
                known_value = event_id
                alarm_id = self.db.query_database_table_for_single_value(handle, table, return_field,
                    known_field, known_value)['value']
                alarm_id = int(alarm_id)+1
                # return pre and post event time from remote sites table
                table = DB_SITES_TABLE
                return_field = DB_SITES_FIELDS['pre-event time %s' % alarm_id]
                known_field = DB_SITES_FIELDS['id']
                known_value = site_id
                pre_time = int(self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value'])
                return_field = DB_SITES_FIELDS['pre-event time %s' % alarm_id]
                post_time = int(self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value'])
            else:
                pre_time = 0
                post_time = 0
            # return event duration from event log
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['duration']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = event_id
            duration = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            # make sure duration is not None (if no event duration)
            if duration is None or '': duration = 0
            # calculate final clip length
            length = int(pre_time) + int(duration) + int(post_time)
            if length is 0: length = 1 # minimum length
            # update table
            statement = '''
            UPDATE %(table)s SET %(length field)s = '%(type)s'
                WHERE %(id field)s = '%(id)s'
            ''' % {'table': DB_CLIPLOG_TABLE, 'length field': DB_CLIPLOG_FIELDS['length'],
                         'type': length, 'id field': DB_CLIPLOG_FIELDS['id'], 'id': clip_id}
            self.db.execute_SQL(handle, statement)

            # update clip start time
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['start']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = event_id
            event_start = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            # handle autoclips
            if clip_type.lower() == 'autoclip':
                event_start -= pre_time
            # update table
            statement = '''
            UPDATE %(table)s SET %(start field)s = '%(type)s'
                WHERE %(id field)s = '%(id)s'
            ''' % {'table': DB_CLIPLOG_TABLE, 'start field': DB_CLIPLOG_FIELDS['start'],
                   'type': event_start, 'id field': DB_CLIPLOG_FIELDS['id'], 'id': clip_id}
            self.db.execute_SQL(handle, statement)

            # update cameras
            table = DB_EVENTLOG_TABLE
            return_field = DB_EVENTLOG_FIELDS['cameras']
            known_field = DB_EVENTLOG_FIELDS['id']
            known_value = event_id
            cameras = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_value)['value']
            statement = '''
            UPDATE %(table)s SET %(cameras field)s = '%(type)s'
                WHERE %(id field)s = '%(id)s'
            ''' % {'table': DB_CLIPLOG_TABLE, 'cameras field': DB_CLIPLOG_FIELDS['cameras'],
                   'type': cameras, 'id field': DB_CLIPLOG_FIELDS['id'], 'id': clip_id}
            self.db.execute_SQL(handle, statement)

            # insert request into chain of custody
            if request_time is not None:
                time_val = self.utc.convert_string_to_time(request_time)
            else:
                time_val = "strftime('%s','now')"
            statement = '''
            INSERT INTO %(table)s (%(clip id field)s, %(type field)s, %(value field)s,
                %(author field)s,%(time field)s,%(text field)s)
                VALUES ('%(clip id)s',0,-1,'%(author)s',%(time val)s, '');
            ''' % {'table': DB_COC_TABLE, 'clip id field': DB_COC_FIELDS['clip id'],
                    'type field': DB_COC_FIELDS['type'], 'value field': DB_COC_FIELDS['value'],
                    'author field': DB_COC_FIELDS['author'], 'author': author,
                    'time field': DB_COC_FIELDS['time'], 'text field': DB_COC_FIELDS['text'],
                    'clip id': clip_id, 'time val': time_val}
            self.db.execute_SQL(handle, statement)

            result['clip id'] = clip_id
            self.log.trace("Simulated clip request for event %s." % event_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="simulate clip request for event %s" % event_id)

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.clip_id = result['clip id']
        return result

    def continuously_request_clips_from_sites_over_time(self, num_sites, duration=60, testcase=None):
        """
        INPUT
            num sites: the number of sites being tested (requests will correspond to num = site id).
            duration: the number of seconds the test should run for.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Requesting clips for %s sites for an elapsed time of %s seconds ..."
                  % (num_sites, duration))
        result = {'successful': False, 'verified': False}

        try:

            running = True
            end_time = time() + duration
            while running:

                # serially handle each site
                for i in range(1, num_sites+1):

                    # determine random clip length (up to 10 seconds)
                    length = randint(1, 10)

                    # determine random request time (within 3 days)
                    start = "%d minutes ago" % randint(5, 4320)

                    # request clip from site
                    request_succeeded = self.request_custom_clip(i, start_time=start,
                        length=length)['verified']

                    if not request_succeeded:
                        # check if the server crashed
                        running = self.check_if_vim_server_is_running(testcase=testcase)['service']

                    if not running:
                        self.log.error("Server crashed.")
                        break

                # check if elapsed time is over
                current_time = time()
                if current_time >= end_time:
                    # check if operation succeeded
                    if running:
                        self.log.trace("Successfully completed clip request loop for duration.")
                        result['verified'] = True

                    # end loop
                    break

            self.log.trace("Finished requesting clips for elapsed time.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="request clips for elapsed time")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def lock_clip_file(self, clip_id, file_type='bin', file_name=None, generate=True, testcase=None):
        """ Lock the file for the given clip.
        INPUT
            clip id: the id of the clip that will have its file locked.
            file type: the type of file to lock (extension).
            file name: an override for the clip file name to use instead of querying the database.
                This is useful for anticipating a clip file before request and download.
            generate: whether to generate the file or not (if it does not exist). This can be used to
                create a bin file before a clip downloads, then lock it to create write-lock.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            lock: the file thread locking the file (can be unlocked/stopped).
            root file name: the base (no file suffix), original name of the clip. This is
                useful in verifying modified clip file downloads due to write-lock errors during
                download.
        """

        self.log.debug("Locking %s file for clip %s ..." % (file_type, clip_id))
        result = {'successful': False, 'lock': None, 'root file name': None}

        try:
            # determine file name for clip
            if file_name is None:
                handle = self.db.db_handle
                table = DB_CLIPLOG_TABLE
                return_field = DB_CLIPLOG_FIELDS['file name']
                known_field = DB_CLIPLOG_FIELDS['id']
                known_val = clip_id
                file_name = self.db.query_database_table_for_single_value(handle, table, return_field,
                    known_field, known_val)['value']
                result['root file name'] = file_name
                file_name = str(file_name) + ".%s" % file_type
            else:
                result['root file name'] = file_name

            # determine storage path
            storage_loc = self.return_storage_location_for_clip(clip_id)['storage loc']
            file_path = storage_loc + file_name

            # determine if file already exists (and generate if needed)
            if not path.exists(storage_loc) and generate:
                self.log.trace("Storage location does not exist. Generating ...")
                mkdir(storage_loc)

                if not path.exists(file_path) and generate:
                    self.log.trace("File %s does not exist. Generating ..." % file_path)
                    statement = 'copy NUL "%s"' % file_path
                    system(statement)

                    # wait to lock clip
                    #sleep(5)

            # lock file
            data = lock_file(self.log, file_path)
            locked = data['successful']
            lock = data['lock']

            if locked:
                self.log.trace("Locked %s file for clip %s." % (file_type, clip_id))
                result['successful'] = True
                result['lock'] = lock
            else:
                raise AssertionError("Failed to lock clip file.")
        except BaseException, e:
            self.handle_exception(e, operation="lock %s file for clip %s" % (file_type, clip_id))

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.locked_clip_file_thread = result['lock']
            testcase.root_clip_file_name = result['root file name']
        return result

    def unlock_clip_file(self, locked_clip_file_thread=None, testcase=None):
        """ Unlock the given file thread for previously locked clip file.
        INPUT
            locked clip file thread: a running thread that is currently locking a file.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Unlocking clip file ...")
        result = {'successful': False}

        try:
            if locked_clip_file_thread is None and testcase is not None:
                locked_clip_file_thread = testcase.locked_clip_file_thread
            elif locked_clip_file_thread is None and testcase is None:
                self.log.error("No clip file thread specified.")

            # unlock file
            unlock_file(self.log, locked_clip_file_thread)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="unlock clip file")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def request_custom_clip(self, site_id, start_time=None, length=1, settings=[], event_id=None,
                            max_attempts=5, testcase=None):
        """
        INPUT
            site id: the id of the site to request the clip from.
            start time: the time from which to request the video in string format
                (e.g. "5 minutes ago").
            length: the length of the clip in seconds.
            settings: any additional settings in [field, value] format.
            event id: id of an event (used when requesting custom event clip).
                NOTE: only custom event clips (for video events) currently supported.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            clip id: the clip id of the clip requested.
        """

        self.log.debug("Requesting custom clip from site %s ..." % site_id)
        result = {'successful': False, 'verified': False, 'clip id': None}

        try:
            # define default data packet to send to server
            data = {}
            data[CLIPREQ_FIELDS['site id']] = site_id
            data[CLIPREQ_FIELDS['site name']] = site_id
            data[CLIPREQ_FIELDS['start']] = self.utc.convert_string_to_time(start_time) \
                if start_time is not None else self.utc.convert_string_to_time("5 minutes ago")
            data[CLIPREQ_FIELDS['duration']] = length
            data[CLIPREQ_FIELDS['start date/time']] = self.utc.convert_database_time_to_server_date(
                data[CLIPREQ_FIELDS['start']]
            )
            data[CLIPREQ_FIELDS['end date/time']] = self.utc.convert_database_time_to_server_date(
                data[CLIPREQ_FIELDS['start']] + length
            )
            data[CLIPREQ_FIELDS['event label']] = '-'
            data[CLIPREQ_FIELDS['cameras']] = -1
            data[CLIPREQ_FIELDS['notification']] = 'false'
            data[CLIPREQ_FIELDS['notes']] = ''

            # update data packet with event parameters if event id given
            if event_id is not None:
                data['event duration'] = '00:00:01'
                data['event type id'] = -1
                data['event id'] = event_id
                data['event type'] = 32767

                # determine event time
                handle = self.db.db_handle
                table = DB_EVENTLOG_TABLE
                return_field = DB_EVENTLOG_FIELDS['start']
                known_field = DB_EVENTLOG_FIELDS['id']
                known_value = event_id
                event_time = self.db.query_database_table_for_single_value(handle, table,
                    return_field, known_field, known_value)['value']

                data['event start'] = event_time

            # update data packet with any additional parameters given
            for setting in settings:
                self.log.trace("Setting '%(field)s' to '%(value)s' ..."%{'field':setting[0],
                                                              'value':str(setting[1])})
                data[CLIPREQ_FIELDS[setting[0].lower()]] = setting[1]

            successful = False
            attempt = 1
            while not successful and attempt <= max_attempts:
                # send data packet to server
                url = self.server_url + CLIPREQ_PATH
                response = self.post_http_request(url, data, testcase=testcase)['response']

                # verify clip request successful
                if response is not None:
                    if response.lower() == 'ok':
                        self.log.trace("Verified clip request was successful.")
                        successful = True
                        result['verified'] = True
                    else:
                        self.log.warn("Failed to verify clip request was successful. Expect server "
                                      "response to be 'Ok', but was %s." % response)
                else:
                    self.log.warn("Failed to verify clip request was successful. No response.")

                # re-attempt
                wait = 5
                if not successful:
                    self.log.trace("Re-attempting in %s seconds ..." % wait)
                    attempt += 1
                    sleep(5)

            # determine clip ID
            if result['verified']:
                self.log.trace("Determining clip ID ...")
                response = self.db.query_database_table(self.db.db_handle,
                    DB_CLIPLOG_TABLE, return_field=DB_CLIPLOG_FIELDS['id'], max=True)['response']
                if response is not None:
                    result['clip id'] = response[0][0]
                    self.log.trace("Clip ID is %s." % result['clip id'])
                else:
                    result['verified'] = False
                    self.log.warn("No clip found.")

            self.log.trace("Requested custom clip from site %s." % site_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="request custom clip from site %s" % site_id)

        # return
        if testcase is not None:
            testcase.processing = result['successful']
            testcase.clip_id = result['clip id']
        return result

    def return_storage_location_for_clip(self, clip_id, site_id=None, event_id=None, testcase=None):
        """ Return storage location for clip with given id.
        INPUT
            clip id: the id of the clip to verify has downloaded.
            event id: the id of the event of the clip to verify has downloaded (reduced queries by 1).
            site id: the id of the site of the clip to verify has downloaded (reduced queries by 2).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Determining storage location for clip %s ..." % str(clip_id))
        result = {'successful': False, 'storage loc': None}

        try:
            # determine clip file parent folder
            if site_id is None:
                if event_id is None:
                    handle = self.db.db_handle
                    table = DB_CLIPLOG_TABLE
                    return_field = DB_CLIPLOG_FIELDS['event id']
                    known_field = DB_CLIPLOG_FIELDS['id']
                    known_val = clip_id
                    event_id = self.db.query_database_table_for_single_value(handle, table,
                        return_field, known_field, known_val)['value']

                handle = self.db.db_handle
                table = DB_EVENTLOG_TABLE
                return_field = DB_EVENTLOG_FIELDS['site id']
                known_field = DB_EVENTLOG_FIELDS['id']
                known_val = event_id
                site_id = self.db.query_database_table_for_single_value(handle, table, return_field,
                    known_field, known_val)['value']

            handle = self.db.db_handle
            table = DB_SITES_TABLE
            return_field = DB_SITES_FIELDS['site group id']
            known_field = DB_SITES_FIELDS['id']
            known_val = site_id
            site_group_id = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_val)['value']

            handle = self.db.db_handle
            table = DB_SITEGROUPS_TABLE
            return_field = DB_SITEGROUPS_FIELDS['storage location']
            known_field = DB_SITEGROUPS_FIELDS['id']
            known_val = site_group_id
            storage_loc = self.db.query_database_table_for_single_value(handle, table, return_field,
                known_field, known_val)['value']

            if storage_loc is not None:
                # TODO: need to include disk ID, not site ID
                result['storage loc'] = storage_loc + str(site_id) + '\\'
                self.log.trace("Determined storage location for clip %s." % clip_id)
                result['successful'] = True

            else:
                raise AssertionError("No storage location returned.")
        except BaseException, e:
            self.handle_exception(e, operation="determine storage location for clip %s" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_downloaded_with_suffix(self, clip_id, suffix, site_id=None, event_id=None,
                                           testcase=None):
        """ Verify that a clip downloaded successfully as file with given suffix.
        INPUT
            clip id: the id of the clip to verify has downloaded.
            suffix: the suffix expected of the clip file on download (e.g., 'a', 'b', 'c', etc.)
            event id: the id of the event of the clip to verify has downloaded (reduced queries by 1).
            site id: the id of the site of the clip to verify has downloaded (reduced queries by 2).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying that clip %s downloaded with %s suffix ..." % (clip_id, suffix))
        result = {'successful': False, 'verified': False}

        try:
            # determine clip file name to verify (for override)
            file_name = testcase.root_clip_file_name + str(suffix) + '.exe'

            # verify clip file downloaded
            result['verified'] = self.verify_clip_downloaded(clip_id, site_id=site_id,
                event_id=event_id, file_name=file_name, testcase=testcase)['verified']

            if result['verified']:
                self.log.trace("Verified that clip %s downloaded with %s suffix." % (clip_id, suffix))

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify that clip %s downloaded with %s suffix"
                                               % (clip_id, suffix))

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_downloaded_for_event(self, event_id, autoclip=False, wait=300, testcase=None):
        """ Verify that a clip has downloaded for event.
        INPUT
            event id: id of the event for which to verify a clip has downloaded.
            autoclip: whether the type of clip downloaded should be verified as an AutoClip or not.
            wait: the amount of time (seconds) to check for the downloaded clip.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying clip downloaded for event %s ..." % event_id)
        result = {'successful': False, 'verified': False}

        try:
            # define loop for checking for clip download
            attempt = 1
            interval = 5
            max_attempts = wait/interval
            while not result['verified'] and attempt <= max_attempts:
                # query clip log for clips associated with event
                handle = self.db.db_handle
                table = DB_CLIPLOG_TABLE
                addendum = 'WHERE %s = "%s" AND %s = "%s"' % (DB_CLIPLOG_FIELDS['event id'], event_id,
                    DB_CLIPLOG_FIELDS['file type'], 1)
                if autoclip: addendum += ' AND %s = "%s"' % (DB_CLIPLOG_FIELDS['download type'], 1)
                data = self.db.query_database_table(handle, table, addendum=addendum)['response']

                # build list of clip IDs from data returned
                clip_ids = []
                if data is not None and data != []:
                    result['verified'] = True
                    self.log.trace("Verified clip downloaded for event %s." % event_id)
                    for clip in data:
                        clip_id = clip[0]
                        clip_ids.append(clip_id)
                elif attempt < max_attempts:
                    self.log.trace("Failed to verify clip downloaded for event %s (attempt %s). "
                                   "Re-attempting in %s seconds ..." % (event_id, attempt, interval))
                    attempt +=1
                    sleep(interval)
                else:
                    self.log.error("Failed to verify clip downloaded for event %s. " % event_id)
                    break

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify clip downloaded for event %s" % event_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_downloaded(self, clip_id, site_id=None, event_id=None, file_name=None,
                               testcase=None, wait=100, from_site_id=None):
        """ Verify that a clip downloaded successfully.
        INPUT
            clip id: the id of the clip to verify has downloaded.
            event id: the id of the event of the clip to verify has downloaded (reduced queries by 1).
            site id: the id of the site of the clip to verify has downloaded (reduced queries by 2).
            file name: an override for the clip file name to use instead of querying the database.
                This is useful for verifying a specific file name associated with the clip without
                having to wait for said file name to be updated on download.
            testcase: a testcase object supplied when executing function as part of a testcase step.
            wait: the number of times to check for the clip download (x5 secs).
            from site: id of site to verify the clip was downloaded from (e.g. drive status testing).
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying that clip %s downloaded ..." % str(clip_id))
        result = {'successful': False, 'verified': False}

        try:
            # determine clip file name
            if file_name is None:
                handle = self.db.db_handle
                table = DB_CLIPLOG_TABLE
                return_field = DB_CLIPLOG_FIELDS['file name']
                known_field = DB_CLIPLOG_FIELDS['id']
                known_val = clip_id
                file_name = self.db.query_database_table_for_single_value(handle, table, return_field,
                    known_field, known_val)['value']
                file_name = str(file_name) + ".exe"

            # determine clip file parent folder
            storage_loc = self.return_storage_location_for_clip(clip_id, site_id=site_id,
                event_id=event_id)['storage loc']

            # determine site folder and find file
            if file_name is not None:
                filePath = None
                i = 1
                while i < wait and filePath is None:
                    if path.exists(storage_loc):
                        clipFiles = listdir(storage_loc)
                        if clipFiles is None: clipFiles = []
                        for clipFile in clipFiles:
                            if file_name in clipFile:
                                filePath = storage_loc + file_name
                        if filePath is not None:
                            self.log.trace("Clip file path:\t%s" % filePath)
                            # don't verify if a check for correct download site is needed
                            if from_site_id is None: result['verified'] = True
                            break
                        else:
                            # check if download failed
                            failed = self.check_if_clip_download_failed(clip_id)['failed']
                            if failed:
                                self.log.warn("Clip download failed.")
                                i = wait

                    if i == wait and filePath is None:
                        self.log.warn("File NOT found.")
                    else:
                        self.log.trace("Downloaded clip file not found (attempt %d). "
                                       "Retrying in 5 seconds ..." % i)
                        sleep(5)
                        i += 1

                # if testing downloaded from site
                if from_site_id is not None:
                    self.log.trace("Verifying clip downloaded from site %s ..." % from_site_id)

                    # return disk ID and name of site clip should be downloaded from
                    from_disk_id = self.return_drive_for_site(from_site_id)['drive id']
                    from_site_name = self.db.query_database_table_for_single_value(self.db.db_handle,
                        DB_SITES_TABLE, DB_SITES_FIELDS['site name'], DB_SITES_FIELDS['id'],
                        from_site_id)['value']

                    # return action text from downloaded clip
                    action_text = self.db.query_database_table_for_single_value(self.db.db_handle,
                        DB_COC_TABLE, DB_COC_FIELDS['text'],DB_COC_FIELDS['clip id'],
                        '%s" and %s = "%s'%(clip_id, DB_COC_FIELDS['value'],
                                            ACTION_TO_ACTION_VAL['download']))['value']

                    # check if download text is correct (diskID:site name)
                    expected = "%s:%s" % (from_disk_id, from_site_name)
                    if expected == action_text:
                        self.log.trace("Verified clip downloaded from site.")
                        result['verified'] = True
                    else:
                        self.log.warn("Expected %s, but found %s."%(expected, action_text))
                        self.log.warn("Failed to verify clip downloaded from site.")

            else:
                self.log.warn("No clip found with given ID.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify clip %s downloaded" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def check_if_clip_download_failed(self, clip_id, testcase=None):
        """ Check if given clip scheduled to download failed.
        INPUT
            clip id: the id of the clip to check for download failure.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            failed: whether the clip failed to download or not.
        """

        self.log.trace("Checking if clip %d download failed ..." % clip_id)
        result = {'successful': False, 'failed': False, 'reason': None}

        try:
            # query chain of custody for clip download failure entry
            failedValue = ACTION_TO_ACTION_VAL['fail to download']
            handle = self.db.db_handle
            table = DB_COC_TABLE
            return_field = DB_COC_FIELDS['text']
            addendum = "WHERE %s = '%s' AND %s = '%s'" % (DB_COC_FIELDS['clip id'], clip_id,
                                                          DB_COC_FIELDS['value'], failedValue)
            entry = self.db.query_database_table(handle, table, return_field, addendum)['response']
            if entry is not None and entry != []: result['failed'] = True

            self.log.trace("Checked if clip %s download failed." % clip_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="check if clip %d download failed" % clip_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result