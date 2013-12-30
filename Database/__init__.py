###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from Charon import Charon
from mapping import TARTAROS, TARTAROS_DB_PATH
from utility import return_execution_error

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

DB = TARTAROS['database']
DB_TABLES = DB['tables']
MODULE_FIELDS = DB['modules']['fields']
FEATURE_FIELDS = DB['features']['fields']
USERSTORY_FIELDS = DB['user stories']['fields']
TEST_FIELDS = DB['tests']['fields']
TESTCASE_FIELDS = DB['testcases']['fields']
STEP_FIELDS = DB['procedure steps']['fields']
FUNCTION_FIELDS = DB['functions']['fields']
SUBMODULE_FIELDS = DB['submodules']['fields']
LICENSE_FIELDS = DB['licenses']['fields']
SITE_FIELDS = DB['sites']['fields']
DVR_FIELDS = DB['dvrs']['fields']

####################################################################################################
# Database #########################################################################################
####################################################################################################
####################################################################################################


class Database(Charon):
    """ Library for Tartaros database interaction. """

    def __init__(self, logger):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # instantialize logger
        self.log = logger

        # initialize SQLite API library
        db_path = TARTAROS_DB_PATH
        Charon.__init__(self, db_path, self.log)

        # define default database handle
        self.db_handle = self.establish_handle_to_database()['handle']

    def return_root_id_for_vcs_root_name(self, name):
        """ Return the vcs root ID given its name.
        INPUT
            name: name of the vcs root.
        OUTPUT
            id: the id of the vcs root.
        """

        self.log.debug('Returning root id for vcs root %s ...' % name)
        result = {'successful': False, 'id': None}

        try:
            # determine module id
            table = DB_TABLES['modules']
            return_field = MODULE_FIELDS['name']
            known_field = MODULE_FIELDS['id']
            known_value = name
            result['name'] = self.query_database_table_for_single_value(self.db_handle,
                                                                        table, return_field, known_field, known_value)['value']

            self.log.trace("Returned module name.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return module name.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def establish_handle_to_database(self):
        """ Connect to and establish a handle to the database.
        OUTPUT
            handle: the handle to the database established.
        """

        self.log.debug("Establishing a handle to the database ...")
        result = {'successful': False, 'handle': None}

        # connect to database
        self.connect_to_database()

        # create handle
        try:
            result['handle'] = self.create_database_handle()['handle']
        except BaseException, e:
            self.log.error("Failed to create database handle.")
            self.log.error(str(e))

        # verify handle established
        if result['handle'] is not None:
            self.log.trace("Handle to the database established.")
            result['successful'] = True
        else:
            self.log.trace("Failed to establish handle to the database.")
            result['successful'] = False

        # return
        return result

    def return_functions(self):
        """ Return all functions.
        OUTPUT
            functions: list of functions {id, name, submodule id}.
        """

        self.log.debug("Returning functions ...")
        result = {'successful': False, 'functions': []}

        try:
            # query database for all Functions table entries
            table = DB_TABLES['functions']
            response = self.query_database_table(self.db_handle, table)['response']

            # add response items to modules list
            for item in response:
                result['functions'].append({'id': item[0], 'name': str(item[1]),
                                            'submodule id': str(item[2])})
        except BaseException, e:
            self.log.error("Failed to return functions.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_site_data(self, name, testcase=None):
        """
        INPUT
            name the name of the site.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            dvr data: the data returned for the site.
        """

        self.log.debug("Returning site data for %s ..." % name)
        result = {'successful': False, 'site data': {}}

        try:
            # query database for site data
            table = DB_TABLES['sites']
            addendum = 'WHERE %s = "%s"' % (SITE_FIELDS['name'], name.lower())
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for configuration
            site_data = {}
            fields = SITE_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                try: site_data[fields[i]] = int(values[i])
                except ValueError: site_data[fields[i]] = str(values[i])
                except TypeError: site_data[fields[i]] = None
            result['site data'] = site_data

            self.log.trace("Returned site data for %s." % name)
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return site data for %s." % name)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_dvr_data(self, dvr_id, testcase=None):
        """
        INPUT
            dvr id: the id of the DVR.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            dvr data: the data returned for the site.
        """

        self.log.debug("Returning DVR data for %s ..." % dvr_id)
        result = {'successful': False, 'dvr data': {}}

        try:
            # query database for site data
            table = DB_TABLES['dvrs']
            addendum = 'WHERE %s = "%s"' % (DVR_FIELDS['id'], dvr_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for configuration
            dvr_data = {}
            fields = DVR_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                try: dvr_data[fields[i]] = int(values[i])
                except ValueError: dvr_data[fields[i]] = str(values[i])
                except TypeError: dvr_data[fields[i]] = None
            result['dvr data'] = dvr_data

            self.log.trace("Returned DVR data for %s." % dvr_id)
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return DVR data for %s." % dvr_id)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_license_configuration(self, name, testcase=None):
        """
        INPUT
            name: the name of the license configuration.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            configuration: the configuration data returned.
        """

        self.log.debug("Returning license configuration for %s license ..." % name)
        result = {'successful': False, 'configuration': {}}

        try:
            # query database for license configuration
            table = DB_TABLES['licenses']
            addendum = 'WHERE %s = "%s"' % (LICENSE_FIELDS['name'], name)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for configuration
            license_data = {}
            fields = LICENSE_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                try: license_data[fields[i]] = int(values[i])
                except ValueError: license_data[fields[i]] = str(values[i])
            result['configuration'] = license_data

            self.log.trace("Returned license configuration for %s license." % name)
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return license configuration for %s license." % name)
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_submodule_data(self, id):
        """ Return the submodule data given its id.
        INPUT
            id: id of the module.
        OUTPUT
            data: data dict of the submodule.
        """

        self.log.debug('Returning data for submodule %s ...' % id)
        result = {'successful': False, 'data': None}

        try:
            # determine module id
            table = DB_TABLES['submodules']
            known_field = SUBMODULE_FIELDS['id']
            known_value = id
            addendum = "WHERE %s = '%s'" % (known_field, known_value)
            result['data'] = self.query_database_table(self.db_handle,
                table, addendum=addendum)['value']

            self.log.trace("Returned submodule data.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return submodule data.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_module_name(self, id):
        """ Return the module name given its id.
        INPUT
            id: id of the module.
        OUTPUT
            name: the name of the module.
        """

        self.log.debug('Returning name for module %s ...' % id)
        result = {'successful': False, 'name': None}

        try:
            # determine module id
            table = DB_TABLES['modules']
            return_field = MODULE_FIELDS['name']
            known_field = MODULE_FIELDS['id']
            known_value = id
            result['name'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned module name.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return module name.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_module_id(self, name):
        """ Return the module id given its name.
        INPUT
            name: the name of the module.
        OUTPUT
            id: id of the module.
        """

        self.log.debug('Returning ID for module "%s" ...' % name)
        result = {'successful': False, 'id': None}

        try:
            # determine module id
            table = DB_TABLES['modules']
            return_field = MODULE_FIELDS['id']
            known_field = MODULE_FIELDS['name']
            known_value = name
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned module ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return module ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_submodule_for_module(self, module_id):
        """ Return the module id given its name.
        INPUT
            module id: the id of the module.
        OUTPUT
            id: id of the submodule.
        """

        self.log.debug('Returning submodule ID for module %s ...' % module_id)
        result = {'successful': False, 'id': None}

        try:
            # determine module id
            table = DB_TABLES['modules']
            return_field = MODULE_FIELDS['submodule']
            known_field = MODULE_FIELDS['id']
            known_value = module_id
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned submodule ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return submodule ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_modules_for_submodule(self, submodule):
        """ Return all modules for submodule.
        INPUT:
            submodule: either the name or id of the submodule.
        OUTPUT
            modules: list of modules {id, name}.
        """

        self.log.debug("Returning modules for submodule %s ..." % submodule)
        result = {'successful': False, 'modules': []}

        # determine if submodule name or id given
        try:
            submodule_id = int(submodule)
            submodule_name = None
        except BaseException:
            submodule_name = str(submodule)
            submodule_id = None


        # determine submodule id if needed
        if submodule_id is None:
            table = DB_TABLES['submodules']
            return_field = SUBMODULE_FIELDS['id']
            known_field = SUBMODULE_FIELDS['name']
            known_value = submodule_name
            module_id = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

        try:
            # query database for all modules associated with submodule
            table = DB_TABLES['modules']
            addendum = 'WHERE %s = "%s"' % (MODULE_FIELDS['submodule'], submodule_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']

            # add response items to modules list
            for item in response:
                result['modules'].append({'id': item[0], 'name': str(item[1]), 'submodule id': item[2]})

            self.log.trace("Returned modules.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return modules.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def return_module_for_user_story(self, user_story_id):
        """ Return the module id given its user story.
        INPUT
            name: the name of the user story.
        OUTPUT
            id: id of the parent module.
        """

        self.log.debug('Returning module ID for user story %s ...' % user_story_id)
        result = {'successful': False, 'id': None}

        try:
            # determine module id
            table = DB_TABLES['user stories']
            return_field = USERSTORY_FIELDS['module']
            known_field = USERSTORY_FIELDS['id']
            known_value = user_story_id
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned module ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return module ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_features_for_module(self, module):
        """ Return all features for given module.
        INPUT
            module: either the id or name of the module for which to return all features.
        OUTPUT
            features: list of features {id, name, module id}.
        """

        self.log.debug("Returning features for module %s ..." % module)
        result = {'successful': False, 'features': []}

        # determine if module name or id given
        try:
            module_id = int(module)
            module_name = None
        except BaseException:
            module_name = str(module)
            module_id = None

        # determine module id if needed
        if module_id is None:
            table = DB_TABLES['modules']
            return_field = MODULE_FIELDS['id']
            known_field = MODULE_FIELDS['name']
            known_value = module_name
            module_id = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

        try:
            # query database for all features that share a user story with the module
            table = DB_TABLES['user stories']
            addendum = 'WHERE %s = "%s"' % (USERSTORY_FIELDS['module'], module_id)
            response =\
                self.query_database_table(self.db_handle, table, addendum=addendum)['response']

            # create a list of unique feature ids from query response
            feature_ids = []
            for item in response:
                feature_id = item[1]
                if feature_id not in feature_ids:
                    feature_ids.append(feature_id)

            # query database for all features for the module and build list of feature data
            for feature_id in feature_ids:
                table = DB_TABLES['features']
                addendum = 'WHERE %s = "%s"' % (FEATURE_FIELDS['id'], feature_id)
                response =\
                    self.query_database_table(self.db_handle, table, addendum=addendum)['response']

                # add response items to features list
                if len(response) > 0:
                    result['features'].append({'id': response[0][0], 'name': str(response[0][1]),
                                               'submodule': response[0][2]})

            self.log.trace("Returned features.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return features.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def return_feature_id(self, name):
        """ Return the feature id given its name.
        INPUT
            name: the name of the feature.
        OUTPUT
            id: id of the feature.
        """

        self.log.debug('Returning ID for feature "%s" ...' % name)
        result = {'successful': False, 'id': None}

        try:
            # determine feature id
            table = DB_TABLES['features']
            return_field = FEATURE_FIELDS['id']
            known_field = FEATURE_FIELDS['name']
            known_value = name
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned feature ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return feature ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_feature_for_user_story(self, story_id):
        """ Return the feature id of a user story given its id.
        INPUT
            story ID: the id of the user story.
        OUTPUT
            id: id of the parent feature.
        """

        self.log.debug('Returning feature ID for user story %s ...' % story_id)
        result = {'successful': False, 'id': None}

        try:
            # determine module id
            table = DB_TABLES['user stories']
            return_field = USERSTORY_FIELDS['feature']
            known_field = USERSTORY_FIELDS['id']
            known_value = story_id
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned feature ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return feature ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_user_stories_for_feature(self, feature, module=None):
        """ Return all user stories for given feature.
        INPUT
            feature: either the id or name of the feature for which to return all user stories.
            module: optional name of the module of the feature (for multi-module features).
        OUTPUT
            user stories: list of user stories {id, name, feature id}.
        """

        self.log.debug("Returning user stories for feature %s ..." % feature)
        result = {'successful': False, 'user stories': []}

        # determine if feature name or id given
        try:
            feature_id = int(feature)
            feature_name = None
        except BaseException:
            feature_name = str(feature)
            feature_id = None

        # return module id for name (if given)
        try:
            module_id = int(module)
        except BaseException:
            module_id = None

        if module is not None and module_id is None:
            table = DB_TABLES['modules']
            return_field = MODULE_FIELDS['id']
            known_field = MODULE_FIELDS['name']
            known_value = module
            module_id = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

        # determine feature id if needed
        if feature_id is None:
            table = DB_TABLES['features']
            return_field = FEATURE_FIELDS['id']
            known_field = FEATURE_FIELDS['name']
            known_value = feature_name

            feature_id = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

        try:
            # query database for all user stories associated with feature
            table = DB_TABLES['user stories']
            addendum = 'WHERE %s = "%s" AND %s = "%s"' % (USERSTORY_FIELDS['feature'],
                                                          feature_id, USERSTORY_FIELDS['module'],
                                                          module_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']

            # add response items to modules list
            for item in response:
                result['user stories'].append({'id': item[0], 'action': str(item[3]),
                                               'module id': item[2], 'feature id': item[1],
                                               'user type': str(item[4])})

            self.log.trace("Returned user stories.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return user stories.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def return_user_story_id(self, action):
        """ Return the story id given its action.
        INPUT
            name: the action of the user story.
        OUTPUT
            id: id of the user story.
        """

        self.log.debug('Returning user story ID for user story "%s" ...' % action)
        result = {'successful': False, 'id': None}

        try:
            # determine user story id
            table = DB_TABLES['user stories']
            return_field = USERSTORY_FIELDS['id']
            known_field = USERSTORY_FIELDS['action']
            known_value = action
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned story ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return story ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_tests_for_user_story(self, story):
        """ Return all tests for given user story.
        INPUT
            story: either the id or name of the user story for which to return all tests.
        OUTPUT
            tests: list of tests {id, name, user story id}.
        """

        self.log.debug("Returning tests for user story %s ..." % story)
        result = {'successful': False, 'tests': []}

        # determine if user story name or id given
        try:
            story_id = int(story)
            story_name = None
        except BaseException:
            story_name = str(story)
            story_id = None

        # determine user story id if needed
        if story_id is None:
            story_id = self.return_user_story_id(story_name)

        try:
            # query database for all tests associated with user story
            table = DB_TABLES['tests']
            addendum = 'WHERE %s = "%s"' % (TEST_FIELDS['user story'], story_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']

            # add response items to modules list
            for item in response:
                result['tests'].append({'id': item[0], 'name': str(item[1]),
                                        'user story id': item[2]})

            self.log.trace("Returned tests.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return tests.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def return_test_id(self, name, story_id):
        """ Return the test id given its name and story id.
        INPUT
            name: the name of the test.
            story ID: the id of the parent user story.
        OUTPUT
            id: id of the test.
        """

        self.log.debug('Returning test ID for test "%s" ...' % name)
        result = {'successful': False, 'id': None}

        try:
            # determine test id
            table = DB_TABLES['tests']
            return_field = TEST_FIELDS['id']
            addendum = 'WHERE %s = "%s" AND %s = "%s"' % (TEST_FIELDS['name'], name,
                                                          TEST_FIELDS['user story'], story_id)
            response =\
            result['id'] = self.query_database_table(self.db_handle, table, return_field=return_field,
                addendum=addendum)['response'][0][0]

            self.log.trace("Returned test ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return test ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_results_id_for_test(self, test_id):
        """ Return the results id of a test given its id.
        INPUT
            test ID: the id of the test.
        OUTPUT
            id: id of the results.
        """

        self.log.debug('Returning results ID for test %s ...' % test_id)
        result = {'successful': False, 'id': None}

        try:
            # determine results id
            table = DB_TABLES['tests']
            return_field = TEST_FIELDS['results id']
            known_field = TEST_FIELDS['id']
            known_value = test_id
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned results ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return results ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_user_story_for_test(self, test_id):
        """ Return the user story id of a test given its id.
        INPUT
            test ID: the id of the test.
        OUTPUT
            id: id of the parent user story.
        """

        self.log.debug('Returning user story ID for test %s ...' % test_id)
        result = {'successful': False, 'id': None}

        try:
            # determine module id
            table = DB_TABLES['tests']
            return_field = TEST_FIELDS['user story']
            known_field = TEST_FIELDS['id']
            known_value = test_id
            result['id'] = self.query_database_table_for_single_value(self.db_handle,
                table, return_field, known_field, known_value)['value']

            self.log.trace("Returned user story ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return user story ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_module_for_test(self, test_id):
        """ Return the module id of a test given its id.
        INPUT
            test ID: the id of the test.
        OUTPUT
            id: id of the parent module.
        """

        self.log.debug('Returning module ID for test %s ...' % test_id)
        result = {'successful': False, 'id': None}

        try:
            # determine user story
            story_id = self.return_user_story_for_test(test_id)['id']

            # determine module
            module_id = self.return_module_for_user_story(story_id)['id']

            result['id'] = module_id

            self.log.trace("Returned module ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return module ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_testcases_for_test(self, test, story_id=None):
        """ Return all testcases for given test.
        INPUT
            test_id: the id of the test for which to return all testcases.
            story_id: the id of the parent story (needed if using test name).
        OUTPUT
            testcases: list of testcases {id, name, test id}.
        """

        self.log.debug("Returning testcases for test %s ..." % test)
        result = {'successful': False, 'testcases': []}

        # determine if test name or id given
        try:
            test_id = int(test)
            test_name = None
        except BaseException:
            test_name = str(test)
            test_id = None

        # determine test id if needed
        if test_id is None:
            test_id = self.return_test_id(test_name, story_id)

        try:
            # query database for all testcases associated with test
            table = DB_TABLES['testcases']
            addendum = 'WHERE %s = "%s"' % (TESTCASE_FIELDS['test'], test_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']

            # parse response into data dictionary for testcase
            for i in range(len(response)):
                testcase_data = {}
                fields = TESTCASE_FIELDS.keys()
                values = list(response[i])
                for j in range(len(values)):
                    testcase_data[fields[j]] = values[j]
                testcase_data['test id'] = testcase_data['test']
                # add response items to modules list
                result['testcases'].append(testcase_data)

            self.log.trace("Returned testcases.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return testcases.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def return_testcase_id(self, name, test_id):
        """ Return the test case id given its name and test id.
        INPUT
            name: the name of the test case.
            test ID: the id of the parent test.
        OUTPUT
            id: id of the test case.
        """

        self.log.debug('Returning ID for test case "%s" ...' % name)
        result = {'successful': False, 'id': None}

        try:
            # determine test case id
            table = DB_TABLES['testcases']
            return_field = TESTCASE_FIELDS['id']
            addendum = 'WHERE %s = "%s" AND %s = "%s"' % (TESTCASE_FIELDS['name'], name,
                                                          TESTCASE_FIELDS['test'], test_id)
            response =\
            result['id'] = self.query_database_table(self.db_handle, table, return_field=return_field,
                addendum=addendum)['response'][0][0]

            self.log.trace("Returned test case ID.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return test case ID.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])

        # return
        return result

    def return_testcase_data(self, testcase_id):
        """ Return data for testcase with given ID.
        INPUT
            testcase_id: the id of the testcase for which to return data.
        OUTPUT
            testcase data: dictionary of data returned for testcase from database.
            test data: dictionary of data returned for test from database.
            user story data: dictionary of data returned for user story from database.
            feature data: dictionary of data returned for feature from database.
            module data: dictionary of data returned for module from database.
        """

        self.log.debug("Returning data for testcase %s ..." % testcase_id)
        result = {'successful': False, 'testcase data': {}, 'test data': {}, 'user story data': {},
                  'feature data': {}, 'module data': {}}

        try:
            # query database for testcase
            table = DB_TABLES['testcases']
            addendum = 'WHERE %s = "%s"' % (TESTCASE_FIELDS['id'], testcase_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for testcase
            testcase_data = {}
            fields = TESTCASE_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                testcase_data[fields[i]] = values[i]
            result['testcase data'] = testcase_data

            # query database for test
            test_id = testcase_data['test']
            table = DB_TABLES['tests']
            addendum = 'WHERE %s = "%s"' % (TEST_FIELDS['id'], test_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for test
            test_data = {}
            fields = TEST_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                test_data[fields[i]] = values[i]
            result['test data'] = test_data

            # query database for user story
            story_id = test_data['user story']
            table = DB_TABLES['user stories']
            addendum = 'WHERE %s = "%s"' % (USERSTORY_FIELDS['id'], story_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for user story
            story_data = {}
            fields = USERSTORY_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                story_data[fields[i]] = values[i]
            result['user story data'] = story_data

            # query database for feature
            feature_id = story_data['feature']
            table = DB_TABLES['features']
            addendum = 'WHERE %s = "%s"' % (FEATURE_FIELDS['id'], feature_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for feature
            feature_data = {}
            fields = FEATURE_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                feature_data[fields[i]] = values[i]
            result['feature data'] = feature_data

            # query database for module
            module_id = story_data['module']
            table = DB_TABLES['modules']
            addendum = 'WHERE %s = "%s"' % (MODULE_FIELDS['id'], module_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for module
            module_data = {}
            fields = MODULE_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                module_data[fields[i]] = values[i]
            result['module data'] = module_data

            self.log.trace("Returned testcase data.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return testcase data.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result

    def return_procedure_step_data(self, procedure_step_id):
        """ Return data for procedure step with given ID.
        INPUT
            procedure_step_id: the id of the procedure step for which to return data.
        OUTPUT
            data: dictionary of data returned for procedure step from database.
        """

        self.log.debug("Returning data for procedure step %s ..." % procedure_step_id)
        result = {'successful': False, 'step data': {}, 'function data': {},
                  'submodule data': {}}

        try:
            # query database for procedure step
            table = DB_TABLES['procedure steps']
            addendum = 'WHERE %s = "%s"' % (STEP_FIELDS['id'], procedure_step_id)
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for procedure step
            step_data = {}
            fields = STEP_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                step_data[fields[i]] = values[i]
            result['step data'] = step_data

            # query database for procedure step
            table = DB_TABLES['functions']
            addendum = 'WHERE %s = "%s"' % (FUNCTION_FIELDS['id'], step_data['function'])
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for procedure step
            function_data = {}
            fields = FUNCTION_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                function_data[fields[i]] = values[i]
            result['function data'] = function_data

            # query database for procedure step
            table = DB_TABLES['submodules']
            addendum = 'WHERE %s = "%s"' % (SUBMODULE_FIELDS['id'], function_data['submodule id'])
            response =\
            self.query_database_table(self.db_handle, table, addendum=addendum)['response']
            # parse response into data dictionary for procedure step
            submodule_data = {}
            fields = SUBMODULE_FIELDS.keys()
            values = list(response[0])
            for i in range(len(values)):
                submodule_data[fields[i]] = values[i]
            result['submodule data'] = submodule_data

            self.log.trace("Returned procedure step data.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to return procedure step data.")
            self.log.error(str(e))
            self.log.error("Error: %s." % return_execution_error()['error'])
            result['successful'] = False

        # return
        return result