###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import HESTIA, HESTIA_PAGE_TO_CONFIG
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

PAGE_CFGS = HESTIA_PAGE_TO_CONFIG
EVENT_TYPES = HESTIA['database']['event log']['event types']
ACTION_VAL_TO_CLIP_STATUS = HESTIA['database']['custody']['action value to clip status']

####################################################################################################
# Page Queries #####################################################################################
####################################################################################################
####################################################################################################


class PageQueries():
    """ Sub-library for ViM server page querying.
    """

    def query_page(self, page, data={}, testcase=None):
        """ Query a page.
        INPUT
            page: the page to be filtered.
            data: a data dictionary that includes optional key/values.
                'results' - number of results to return.
                'sort' - list pair of format: ['field','asc' OR 'desc'].
                'start index' - the entry number to start on when returning results (table pagination).
                'filters' - a list of list pairs of the format: ['field','value']
                    (i.e., [['field1','value1'],['field2','value2']])
                'entry id' - the ID of an entry expected to be in the page query return.
                'expected' - a data dictionary describing values for fields expected for the entry ID
                    expected to return (for thorough verification).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            query response: the server response to the query.
            entry: the expected entry returned.
            time: the elapsed time of the query.
        """

        # declare local variables from data dictionary (if they exist, else set to None)
        #   page
        page = page.lower()
        #   results
        try: results = data['results']
        except KeyError: results = None
        #   sort
        try: sort = data['sort']
        except KeyError: sort = None
        #   start index
        try: startIndex = data['sort']
        except KeyError: startIndex = None
        #   filters
        try: filters = data['filters']
        except KeyError: filters = None
        #   entry ID
        try: entryID = data['entry id']
        except KeyError: entryID = None
        #   expected
        try: expected = data['expected']
        except KeyError: expected = None
        #   where
        try: givenWhere = data['where']
        except KeyError: givenWhere = None
        #   event ID (for clip status info)
        try: eventID = data['event id']
        except KeyError: eventID = None

        self.log.debug("Querying %s page ..." % page)
        result = {'successful': False, 'verified': False, 'query response': [], 'entry': None,
                  'time': None}

        try:
            # determine page and set config for that page
            pageCFG = PAGE_CFGS[page.lower()]
            # define default query parameters
            params = pageCFG['parameters']
            #   translate default date/time filters using yesterday and today (health pages)
            try:
                defaultWhere = params['where']
            except BaseException:
                defaultWhere = None
            if defaultWhere is not None:
                #   translate 'yesterday'
                yesterday = self.utc.return_day_start_time_for_time('1 day ago')
                defaultWhere = defaultWhere.replace('yesterday', str(yesterday))
                #   translate 'today'
                today = self.utc.return_day_end_time_for_time('now')
                defaultWhere = defaultWhere.replace('today', str(today))
                #   translate 'anhourago'
                anHourAgo = self.utc.convert_string_to_time('1 hour ago')
                defaultWhere = defaultWhere.replace('anhourago', str(anHourAgo))
                #   update default parameters
                params['where'] = defaultWhere
                # update number of results to show
            if results is not None:
                params['results'] = results
                # update sort
            if sort is not None:
                params['sort'] = sort
                # update start index
            if startIndex is not None:
                params['start index'] = startIndex
                # update filters to apply
            if filters is not None:
                params['where'] = self.translate_filter_list_to_where_statement(page,filters)['where']
                # override with given where statement, if any
            if givenWhere is not None:
                params['where'] = givenWhere
                # append clip status info event ID (if given)
            if eventID is not None:
                params['eventId'] = eventID
            # query page
            path = pageCFG['query path']
            url = self.server_url + path
            # determine columns for page (based on version)
            if page.lower() == 'sites' and float(self.release_version) < 3.4:
                self.log.trace("Server version %s uses pre-3.4 remote sites page mapping."
                               % str(self.release_version))
                fieldNames = pageCFG['columns 3.3']
            else:
                fieldNames = pageCFG['columns']
            returned = self.query_server_table(url, fieldNames, params)
            result['query response'] = returned['response']
            result['time'] = returned['time']

            # verify page query
            if expected == 'not allowed':
                if result['query response'] == 'HTTP Error 404':
                    self.log.trace("Verified that page was not found.")
                    result['verified'] = True
                elif result['query response'] is None:
                    self.log.trace('No response returned from server.')
                    result['verified'] = True
                else:
                    self.log.error("Failed to verify that the page was not found.")
                    self.log.error("Excepted HTTP Error 404, but server response was '%s'." %
                                    result['query response'])
            elif entryID is not None and result['query response'] is not None:

                # verify page query response entry
                verified = False
                attempt = 1
                maxAttempts = 5
                while not verified and attempt <= maxAttempts:
                    verified = self.verify_page_query_response_entry(page, result['query response'],
                        entryID, expected)['verified']

                    if not verified and attempt < maxAttempts:
                        self.log.trace("Failed to verify page query response entry (attempt %s). "
                            "Re-attempting in 5 seconds ..." % attempt)
                        sleep(5)
                    elif not verified and attempt >= maxAttempts:
                        self.log.warn("Failed to verify page query response entry. ")
                        break
                    elif verified:
                        self.log.trace("Verified page query response entry.")
                        break

                    # increment
                    attempt += 1

                result['verified'] = verified
                # determine entry
                #   determine entry ID field name
                pageCFG = PAGE_CFGS[page.lower()]
                idField = pageCFG['entry id']
                for entry in result['query response']:
                    if str(entry[idField]) == str(entryID):
                        result['entry'] = entry

            elif result['query response'] is None or result['query response'] == 'HTTP Error 404':
                self.log.warn("No response returned from server.")
            else:
                result['verified'] = True

            self.log.trace("Queried %s in %d seconds." % (page, result['time']))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="query %s page" % page)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def translate_filter_list_to_where_statement(self, page, filters, testcase=None):
        """ Translate a list of filters to a where statement for server queries.
        INPUT
            page: the page the filters will be applied to.
            filters: a list of filter/value list pairs of the format:
                [['filter field',value],['filter field 2',value2]].
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            where: the translated WHERE statement to return for querying the page.
        """

        self.log.debug('Translating filter list to where statement ...')
        result = {'successful': False, 'where': ''}

        try:
            # determine page and set config for that page
            pageCFG = PAGE_CFGS[page.lower()]
            serverFields = pageCFG['fields']
            # translate each filter and add to list of translated filters
            translatedFilters = []
            for filter in filters:
                translatedFilter = ''
                filterField = filter[0].lower()
                filterValue = filter[1]
                # handle site filter
                if filterField == 'site id':
                    translatedFilter = "%s='%s'"%(serverFields['site id'],filterValue)
                # handle last communication time filter
                elif filterField == 'last communication time': pass
                # handle created by filter:
                elif filterField == 'created by': pass
                # handle event type filter
                elif filterField == 'event type':
                    # handle camera health log
                    if page == 'camera health log':
                        if type(filterValue) is list:
                            # build parenthetical statement
                            #   handle first entry (as long as there is at least one value)
                            value = filterValue
                            s = "%s in (%s,%s)"%('eventType',EVENT_TYPES[value[0].lower()],
                                                 EVENT_TYPES[value[1].lower()])
                            # clothes the parenthesis when done building statement
                            translatedFilter += s
                    # TODO: handle camera event log
                    # handle multiple event type filters
                    elif type(filterValue) is list:
                        # TODO: handle multiple alarm events
                        # build parenthetical statement
                        #   handle first entry (as long as there is at least one value)
                        if len(filterValue) > 0:
                            # handle alarm event
                            if 'alarm in' in filterValue[0].lower():
                                value = filterValue[0]
                                # determine alarm ID
                                s2 = value.split('alarm in')
                                alarmID = int(s2[1].strip())-1
                                s = "(%s=%s and %s=%s"\
                                    %('eventType',EVENT_TYPES['alarm'],
                                      serverFields['alarm id'],alarmID)
                            else:
                                s = "(%s=%s"%('eventType',EVENT_TYPES[filterValue[0].lower()])
                            translatedFilter += s
                            #   handle additional entries (as long as there are more)
                        if len(filterValue) > 1:
                            for value in filterValue[1:]:
                                # handle alarm event
                                if 'alarm in' in value.lower():
                                    # determine alarm ID
                                    s2 = value.split('alarm in')
                                    alarmID = int(s2[1].strip())-1
                                    s = " or %s=%s and %s=%s"\
                                        %('eventType',EVENT_TYPES['alarm'],
                                          serverFields['alarm id'],alarmID)
                                else:
                                    s = " or %s=%s"%('eventType',EVENT_TYPES[value.lower()])
                                translatedFilter += s
                            # clothes the parenthesis when done building statement
                        translatedFilter += ')'
                    # handle single alarm event type
                    elif 'alarm in' in filterValue.lower():
                        # determine alarm ID
                        s = filterValue.split('alarm in')
                        alarmID = int(s[1].strip())-1
                        translatedFilter = "(%s=%s and %s=%s)"\
                                           %('eventType',EVENT_TYPES['alarm'],
                                             serverFields['alarm id'],alarmID)
                    # handle single event type filter
                    else:
                        translatedFilter = "(%s=%s)"%('eventType',EVENT_TYPES[filterValue.lower()])
                # handle date/time filter
                elif filterField == 'date/time':
                    # from only
                    if filterValue[0] is not None and filterValue[1] is None:
                        s = '%s > %s'%(serverFields['date/time'],
                                       self.utc.convert_string_to_time(filterValue[0]))
                    # to only
                    elif filterValue[1] is not None and filterValue[0] is None:
                        s = '%s < %s'%(serverFields['date/time'],
                                       self.utc.convert_string_to_time(filterValue[1]))
                    # between
                    elif filterValue[0] is not None and filterValue[1] is not None:
                        s = '%s between %s and %s'%(serverFields['date/time'],
                                                    self.utc.convert_string_to_time(filterValue[0]),
                                                    self.utc.convert_string_to_time(filterValue[1]))
                    # else
                    else:
                        self.log.warn("Invalid date/time filter format given %s." % filterValue)
                        s = ''
                    translatedFilter = s
                # handle clip status filter
                elif filterField == 'status': pass
                # add translated filter to list of translated filters
                translatedFilters.append(translatedFilter)
                # build 'where' statement from list of translated filters
            #   handle first entry (as long as there is at least one filter)
            if len(translatedFilters) > 0:
                result['where'] += translatedFilters[0]
                #   handle additional entries (as long as there are more)
            if len(translatedFilters) > 1:
                for translatedFilter in translatedFilters[1:]:
                    # make sure it is not blank
                    if translatedFilter != '':
                        result['where'] += " and %s"%translatedFilter

            self.log.trace("Translated filter list to where statement.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="translate filter list to where statement")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_page_query_response_entry(self, page, query_response, entry_id, expected=None,
                                         testcase=None):
        """ Verify an entry was returned in a page query.
        INPUT
            page: the page that was queried.
            query response: the response from the server page table query.
            entryID: the ID of an entry to be verified was returned by the server
                (i.e., siteID or eventID, etc.).
            expected: a data dictionary of optional field/values to verify match the returned
                values for the given entry ID.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying entry %s in page query response ..." % entry_id)
        result = {'successful': False, 'verified':False}

        try:
            # determine page and set config for that page
            pageCFG = PAGE_CFGS[page.lower()]
            # determine entry ID field name
            idField = pageCFG['entry id']
            # look for the entry matching the entry ID given in the query response
            entry = None
            for i in query_response:
                if i[idField] == str(entry_id): entry = i
            # verify entry was in response
            if entry is not None:
                self.log.trace("Entry found in query response.")
                result['verified'] = True
            else: self.log.trace("Entry NOT found in query response.")
            # verify expected values (if given)
            if expected is not None:
                # pull keys for list of values to verify
                fieldsToVerify = expected.keys()
                # verify each field value
                for field in fieldsToVerify:
                    try:
                        serverValue = entry.get(field.lower())
                        expectedValue = expected[field]
                        # convert clip status values from server to string values (see database maps
                        #   clip actions)
                        if field.lower() == 'clip status':
                            serverValue = ACTION_VAL_TO_CLIP_STATUS[serverValue]
                            # compare values
                        if str(serverValue).lower() == str(expectedValue).lower():
                            self.log.trace("Verified %s field."%field)
                        else:
                            self.log.trace("Failed to verify %(field)s field."\
                                " Expected value to be '%(expected)s', but was '%(actual)s'."
                                %{'field':field,'expected':expectedValue,'actual':serverValue})
                            result['verified'] = False
                    except AttributeError,e:
                        self.log.warn("Failed to get field value.")
                        self.log.warn("%s"%e.message)
                        result['verified'] = False

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify page query response entry")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result