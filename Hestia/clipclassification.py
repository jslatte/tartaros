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

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

SERVER = HESTIA['server']
SERVER_CAT = SERVER['categories']
SERVER_CAT_PATH = SERVER_CAT['query path']
SERVER_CAT_MOD_PATH = SERVER_CAT['modify path']
SERVER_CAT_ENTITY_PATH = SERVER_CAT['entity path']
SERVER_CAT_FIELDS = SERVER_CAT['fields']
SERVER_CAT_COL = SERVER_CAT['columns']
SERVER_CAT_VAL = SERVER['category values']
SERVER_CAT_VAL_PATH = SERVER_CAT_VAL['query path']
SERVER_CAT_VAL_MOD_PATH = SERVER_CAT_VAL['modify path']
SERVER_CAT_VAL_FIELDS = SERVER_CAT_VAL['fields']
SERVER_CAT_VAL_ENTITY_PATH = SERVER_CAT_VAL['entity path']
SERVER_CAT_VAL_COL = SERVER_CAT_VAL['columns']
SERVER_CLASS = SERVER['classifications']
SERVER_CLASS_PATH = SERVER_CLASS['path']
SERVER_CLASS_FIELDS = SERVER_CLASS['fields']

####################################################################################################
# Clip Classification ##############################################################################
####################################################################################################
####################################################################################################


class ClipClassification():
    """ Sub-library for ViM server clip classification functionality.
    """

    def classify_clip(self, clip_id, value_id, category_id, testcase=None):
        """ Classify clip with clip classification category value.
        @param clip_id: the id of the clip to be classified.
        @param value_id: the id of the value with which to classify the clip.
        @param category_id: the id of the category of the value with which to classify the clip.
        @param testcase: a testcase object supplied when executing function as part of a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s %s with value %s for category %s ..." % (operation.replace('_', ' '),
                                                                        clip_id, value_id,
                                                                        category_id))

            # build data packet
            data = [str(value_id)]

            # construct url
            url = self.server_url + SERVER_CLASS_PATH % {'clip id': clip_id,
                                                         'category id': category_id}

            # PUT request to server
            result['successful'] = self.put_http_request(url, data=data, json=True)['successful']

            # verify clip classified
            if result['successful']:
                result['verified'] = self.verify_clip_classification(clip_id, value_id,
                                                                     category_id)['verified']
            else:
                result['verified'] = False

            self.log.trace("... done %s." % operation)
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_clip_classification(self, clip_id, value_id, category_id, testcase=None):
        """
        @param clip_id: the id of the clip to verify was classified.
        @param value_id: the id of the value with which the clip was classified.
        @param category_id: the id of the category of the value with which the clip was classified.
        @param testcase: a testcase object supplied when executing function as part of a testcase step.
        @return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'verified' - whether the operation was verified or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # query video clip log for classified clip
            data = {
                'entry id': clip_id,
            }
            video_entry = self.query_page('video clip log', data, max_attempts=1)['entry']

            # attempt to verify clip classification
            clip_exists = False
            if eval(str(video_entry)) is not None:
                if '%s:%s' % (category_id, value_id) in video_entry['classifications']:
                    self.log.trace("Verified clip classified.")
                    result['verified'] = True
                    clip_exists = True
            else:
                # check health clip log if no clip found in video clip log
                health_entry = self.query_page('health clip log', data, max_attempts=1)['entry']
                if eval(str(video_entry)) is not None:
                    if '%s:%s' % (category_id, value_id) in health_entry['classifications']:
                        self.log.trace("Verified clip classified.")
                        result['verified'] = True
                        clip_exists = True

            if not clip_exists:
                self.log.error("Clip not found.")

            self.log.trace("... done %s." % operation)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def delete_category_value(self, value_id, category_id, testcase=None):
        """
        INPUT
            value id: the id of the value to delete.
            category id: the id of the parent category.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Deleting value %s from category %s ..." % (value_id, category_id))
        result = {'successful': False, 'verified': False}

        try:
            # make request to server
            url = self.server_url + SERVER_CAT_VAL_ENTITY_PATH % {'category id': category_id,
                                                                  'id': value_id}
            self.make_delete_request_to_server(url)

            # verify category value deleted
            verified = self.verify_category_value(value_id, category_id,
                expected_failure=True)['verified']

            if not verified:
                self.log.error("Failed to verify category value deleted. Category value found.")
            else:
                self.log.trace("Verified category value deleted.")
                result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="delete category value %s" % value_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def edit_category_value(self, value_id, category_id, field, value, testcase=None):
        """
        INPUT
            value id: the id of the value to edit.
            category id: the id of the parent category.
            field: field of value to edit.
            value: new value for field of value being edited.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Editing value %s of category %s ..." % (value_id, category_id))
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("Changing %s field to %s ..." % (field, value))

            # define data packet to send to server
            data = {
                SERVER_CAT_VAL_FIELDS['id']:           category_id,
                SERVER_CAT_VAL_FIELDS[field]:          value,
            }

            # post request to server (in JSON mode)
            url = self.server_url + SERVER_CAT_VAL_ENTITY_PATH % {'category id': category_id,
                                                              'id': value_id}
            successful = self.post_http_request(url, data=data, json=True)['successful']

            if successful:
                # verify category edited
                settings = [[field, value]]
                result['verified'] = self.verify_category_value(value_id, category_id,
                    settings)['verified']
                self.log.trace("Verified category value %s edited." % value_id)
            else:
                self.log.error("Failed to verify category value %s edited." % value_id)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="edit category value %s" % value_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def add_value_to_category(self, name, category_id, testcase=None):
        """
        INPUT
            name: the name of the value to add.
            category id: the id of the category to which the value will be added.
            settings: an optional list of field/value pairs to configure value.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            value id: the id of the value added.
        """

        self.log.debug("Adding value '%s' to category %s ..." % (name, category_id))
        result = {'successful': False, 'verified': False, 'value id': None}

        try:
            # define default data packet to send to server
            data = {
                SERVER_CAT_VAL_FIELDS['id']:           None,
                SERVER_CAT_VAL_FIELDS['name']:         name,
            }

            # post request to server (in JSON mode)
            url = self.server_url + SERVER_CAT_VAL_MOD_PATH % {'category id': category_id}
            successful = self.post_http_request(url, data=data, json=True)['successful']

            # verify value
            if successful:
                results = self.verify_category_value(name, category_id)
                result['verified'] = results['verified']
                result['value id'] = results['value id']
                self.log.trace("Added value '%s'." % name)
            else:
                result['verified'] = False

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="add value '%s'" % name)

        # return
        if testcase is not None:
            testcase.value_id = result['value id']
            testcase.processing = result['successful']
        return result

    def verify_category_value(self, value_id, category_id, settings=[], expected_failure=False,
                              testcase=None):
        """
        INPUT
            value id: the name or id of the value to verify.
            category id: the id of the parent category.
            settings: an optional list of field/value pairs to verify against value.
            expected failure: whether the function is expected to fail or not (switches verification).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            value id: the id of the value added.
        """

        self.log.debug("Verifying category value %s ..." % value_id)
        result = {'successful': False, 'verified': False, 'value id': None}

        try:
            # query server for categories
            response = self.query_page("Categories")['query response']

            # check server response for category
            invalids = 0
            for category in response:
                if category['id'] == str(category_id):

                    for value in category['values']:
                        if value['name'] == value_id or value['id'] == str(value_id):
                            result['value id'] = value['id']

                            # verify any additional settings
                            for setting in settings:
                                if value[SERVER_CAT_VAL_FIELDS[setting[0]]] == str(setting[1]):
                                    message = "Verified %s field." % setting[0]
                                    if expected_failure: self.log.error(message)
                                    else:
                                        self.log.trace(message)
                                else:
                                    message = "Failed to verify %s field. Expected %s but was %s."\
                                    % (setting[0], str(setting[1]),
                                       value[SERVER_CAT_VAL_FIELDS[setting[0]]])
                                    if expected_failure: self.log.trace(message)
                                    else:
                                        self.log.error(message)
                                        invalids += 1

                            break

            if expected_failure and result['value id'] is None:
                self.log.trace("Verified value does not exist.")
                result['verified'] = True
            elif expected_failure and result['value id'] is not None and invalids > 0:
                self.log.trace("Failed to verify value.")
                result['verified'] = True
            elif result['value id'] is not None and invalids == 0:
                self.log.trace("Verified value %s." % value_id)
                result['verified'] = True
            else:
                self.log.error("Failed to verify value %s." % value_id)
                result['verified'] = False

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify value %s" % value_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def delete_category(self, category_id, testcase=None):
        """
        INPUT
            category id: the id of the category to delete.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Deleting category %s ..." % category_id)
        result = {'successful': False, 'verified': False}

        try:
            # make request to server
            url = self.server_url + SERVER_CAT_ENTITY_PATH % {'id': category_id}
            self.make_delete_request_to_server(url)

            # verify category deleted
            verified = self.verify_category(category_id, expected_failure=True)['verified']

            if not verified:
                self.log.error("Failed to verify category deleted. Category found.")
            else:
                self.log.trace("Verified category deleted.")
                result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="delete category %s" % category_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def edit_category(self, category_id, field, value, testcase=None):
        """
        INPUT
            category id: the id of the category to edit.
            field: field of category to edit.
            value: new value for field of category being edited.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Editing category %s ..." % category_id)
        result = {'successful': False, 'verified': False}

        try:
            self.log.trace("Changing %s field to %s ..." % (field, value))

            # define data packet to send to server
            data = {
                SERVER_CAT_FIELDS['id']:           category_id,
                SERVER_CAT_FIELDS[field]:          value,
            }

            # post request to server (in JSON mode)
            url = self.server_url + SERVER_CAT_ENTITY_PATH % {'id': category_id}
            successful = self.post_http_request(url, data=data, json=True)['successful']

            if successful:
                # verify category edited
                settings = [[field, value]]
                result['verified'] = self.verify_category(category_id, settings)['verified']
                self.log.trace("Verified category %s edited." % category_id)
            else:
                self.log.error("Failed to verify category %s edited." % category_id)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="edit category %s" % category_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def add_category(self, name, settings=[], testcase=None):
        """
        INPUT
            name: the name of the category.
            settings: an optional list of field/value pairs to configure category.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            category id: the id of the category added.
        """

        self.log.debug("Adding category '%s' ..." % name)
        result = {'successful': False, 'verified': False, 'category id': None}

        try:
            # define default data packet to send to server
            data = {
                SERVER_CAT_FIELDS['id']:           None,
                SERVER_CAT_FIELDS['order']:        None,
                SERVER_CAT_FIELDS['name']:         name,
                SERVER_CAT_FIELDS['description']:  ''
            }

            # update packet with any given settings
            for setting in settings:
                data[SERVER_CAT_FIELDS[setting[0]]] = setting[1]

            # post request to server (in JSON mode)
            url = self.server_url + SERVER_CAT_MOD_PATH
            successful = self.post_http_request(url, data=data, json=True)['successful']

            # verify category
            if successful:
                results = self.verify_category(name, settings)
                result['verified'] = results['verified']
                result['category id'] = results['category id']
                self.log.trace("Added category '%s'." % name)
            else:
                result['verified'] = False

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="add category '%s'" % name)

        # return
        if testcase is not None:
            testcase.category_id = result['category id']
            testcase.processing = result['successful']
        return result

    def verify_category(self, category_id, settings=[], expected_failure=False, testcase=None):
        """
        INPUT
            category id: the id or name of the category to verify.
            settings: an optional list of field/value pairs to verify against category.
            expected failure: whether the function is expected to fail or not (switches verification).
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            category id: the id of the category added.
        """

        self.log.debug("Verifying category %s ..." % category_id)
        result = {'successful': False, 'verified': False, 'category id': None}

        try:
            # query server for category
            response = self.query_page("Categories")['query response']

            # check server response for category
            invalids = 0
            for category in response:
                if category['name'] == str(category_id) or category['id'] == str(category_id):
                    result['category id'] = category['id']

                    # verify any additional settings
                    for setting in settings:
                        if category[SERVER_CAT_FIELDS[setting[0]]] == str(setting[1]):
                            message = "Verified %s field." % setting[0]
                            if expected_failure: self.log.error(message)
                            else:
                                self.log.trace(message)
                        else:
                            message = "Failed to verify %s field. Expected %s but was %s." \
                            % (setting[0], str(setting[1]), category[SERVER_CAT_FIELDS[setting[0]]])
                            if expected_failure: self.log.trace(message)
                            else:
                                self.log.error(message)
                                invalids += 1

                    break

            if expected_failure and result['category id'] is None:
                self.log.trace("Verified category does not exist.")
                result['verified'] = True
            elif expected_failure and result['category id'] is not None and invalids > 0:
                self.log.trace("Failed to verify category.")
                result['verified'] = True
            elif result['category id'] is not None and invalids == 0:
                self.log.trace("Verified category %s." % category_id)
                result['verified'] = True
            else:
                self.log.error("Failed to verify category %s." % category_id)
                result['verified'] = False

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify category %s" % category_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def query_values_for_category(self, category_id, testcase=None):
        """
        INPUT
            category id: the id of the category for which to return the values.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            values: the values returned for the clip.
        """

        self.log.debug("Querying server for values of category %s ..." % category_id)
        result = {'successful': False, 'values': [], 'verified': False}

        try:
            # query server categories table for values
            url = self.server_url + SERVER_CAT_VAL_PATH % {'category id': category_id}
            #response = self.query_server_table(url, SERVER_CAT_VAL_COL)['response']
            response = self.query_page('Categories')['query response']

            # parse response into entries
            if response is not None or '':
                result['verified'] = True
                # split response into category data dictionaries
                for category in response:
                    # check for matching category id
                    if int(category['id']) == category_id:
                        # set values of category for query return
                        result['values'] = category['values']

            self.log.trace("Queried server for values of category %s." % category_id)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="query server for values of category %s" % category_id)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result