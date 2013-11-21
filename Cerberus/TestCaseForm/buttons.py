###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import TARTAROS
from testrun import TestRun
from utility import return_execution_error

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

DATABASE = TARTAROS['database']
TABLES = DATABASE['tables']
MODULE_FIELDS = DATABASE['modules']['fields']
FEATURE_FIELDS = DATABASE['features']['fields']
STORY_FIELDS = DATABASE['user stories']['fields']
TEST_FIELDS = DATABASE['tests']['fields']
TESTCASE_FIELDS = DATABASE['testcases']['fields']
STEP_FIELDS = DATABASE['procedure steps']['fields']
BLANK_SEL = "None"
CUSTOM_SEL = "Custom"
DEFAULT_SEL = [BLANK_SEL, CUSTOM_SEL]

####################################################################################################
# Buttons ##########################################################################################
####################################################################################################
####################################################################################################


class Buttons():
    """ Button actions handling. """

    def modify_testcase(self, name, test_id, procedure, minversion, testcase_class, testcase_id=None):
        """ Add a testcase.
        INPUT
            name: the name of the testcase to add.
            test id: the id of the parent test with which the testcase will be associated.
            procedure: a comma-delimited list of procedure step IDs.
            min version: the minimum version required to support the functionality under test.
            testcase class: the class of test case (e.g., 0-5).
            testcase id: the ID of an existing testcase to update
        OUTPUT
            successful: whether the function executed successfully or not.
            verified: whether the testcase was verified as added or not.
        """

        if testcase_id is None: self.log.trace("Adding testcase %s ..." % name)
        else: self.log.trace("Updating testcase %s ..." % testcase_id)
        result = {'successful': False, 'verified': False}

        try:
            # insert entry into database
            table = TABLES['testcases']
            entry = {
                TESTCASE_FIELDS['name']:                name,
                TESTCASE_FIELDS['test']:                test_id,
                TESTCASE_FIELDS['procedure']:           procedure,
                TESTCASE_FIELDS['minimum version']:     minversion,
                TESTCASE_FIELDS['class']:               testcase_class,
            }

            if testcase_id is None:
                testcase_id = self.database.add_entry_to_table(self.database.db_handle,
                    table, entry)['id']
            else:
                self.database.update_entry_in_table(self.database.db_handle, table, testcase_id, entry)

            # verify testcase added/modified
            returned = self.verify_testcase_added(testcase_id, name, test_id, procedure,
                minversion, testcase_class)
            result['verified'] = returned['verified']
            result['successful'] = returned['successful']
            if testcase_id is None:
                self.log.trace("Testcase added.")
            else:
                self.log.trace("Testcase modified.")
        except BaseException, e:
            self.handle_exception(e, "modify testcase %s" % name)

        # return
        return result

    def verify_testcase_added(self, id, name, test_id, procedure, minversion, testcase_class):
        """ Verify a testcase was added.
        INPUT
            id: the id of the testcase in the database.
            name: the name of the testcase to add.
            test id: the id of the parent test with which the testcase will be associated.
            min version: the minimum version required to support the functionality under test.
            testcase class: the class of test case (e.g., 0-5).
            procedure: a comma-delimited list of procedure step IDs.
        OUTPUT
            successful: whether the function executed successfully or not.
            verified: whether the testcase was verified as added or not.
        """

        self.log.trace("Verifying testcase %s added ..." % name)
        result = {'successful': False, 'verified': False}

        try:
            # return testcase data
            testcase_data = self.database.return_testcase_data(id)['testcase data']
            # verify each data point with given expected values
            failures = False
            if str(name) != str(testcase_data['name']):
                self.log.error("Expected name to be %s, but was %s."
                               % (name, testcase_data['name']))
                failures = True
            if int(test_id) != int(testcase_data['test']):
                self.log.error("Expected test ID to be %s, but was %s."
                               % (test_id, testcase_data['test']))
                failures = True
            if str(procedure) != str(testcase_data['procedure']):
                self.log.error("Expected procedure to be %s, but was %s."
                               % (procedure, testcase_data['procedure']))
                failures = True
            if str(minversion) != str(testcase_data['minimum version']):
                self.log.error("Expected minimum version to be %s, but was %s."
                               % (minversion, testcase_data['minimum version']))
                failures = True
            if str(testcase_class) != str(testcase_data['class']):
                self.log.error("Expected class to be %s, but was %s."
                               % (testcase_class, testcase_data['class']))
                failures = True

            if not failures: result['verified'] = True
            self.log.trace("Verified testcase added.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "verify testcase %s added" % name)

        # return
        return result

    def test_on_add_testcase_button_click(self, event):
        """ Test the functionality of the add testcase button.
        """

        self.log.trace("Test handling add testcase button click by user.")
        result = {'successful': False}

        try:
            # hard-coded values
            name = "DEBUG TESCASE"
            test_id = 252
            procedure = "2,1"
            results_id = 0
            # add test case
            result['successful'] = self.modify_testcase(name,
                test_id, procedure, results_id)['verified']
            self.log.trace("Handled adding testcase button click by user.")
        except BaseException, e:
            self.handle_exception(e, "handle add testcase button click by user")

        # return
        return result

    def determine_results_id_from_input_field(self):

        result = {'results id': None}
        # determine results ID from input field
        self.log.trace("Getting string from testcase results ID input field ...")
        result['results id'] = self.input_results.GetString(0, -1)
        self.log.trace("Returned results ID: %s" % result['results id'])

        # return
        return result

    def determine_test_path_from_input_fields(self):

        result = {'module': None, 'feature': None, 'user story': None, 'test': None, 'testcase': None}

        # determine test path from input fields
        self.log.trace("Getting strings from testcase test path dropdown lists ...")
        # determine module name
        if self.custom_module:
            result['module'] = self.input_custom_module.GetString(0, -1)
        else:
            result['module'] = self.input_module.GetString(self.input_module.GetSelection())
        # determine feature name
        if self.custom_feature:
            result['feature'] = self.input_custom_feature.GetString(0, -1)
        else:
            result['feature'] = self.input_feature.GetString(self.input_feature.GetSelection())
        # determine user story name
        if self.custom_story:
            result['user story'] = self.input_custom_story.GetString(0, -1)
        else:
            result['user story'] = self.input_story.GetString(self.input_story.GetSelection())
        # determine test name
        if self.custom_test:
            result['test'] = self.input_custom_test.GetString(0, -1)
        else:
            result['test'] = self.input_test.GetString(self.input_test.GetSelection())
        # determine test case name
        if self.custom_testcase:
            result['testcase'] = self.input_custom_testcase.GetString(0, -1)
        else:
            result['testcase'] = self.input_testcase.GetString(self.input_testcase.GetSelection())
        # log collated test path
        self.log.trace("Returned test path: %s: %s: %s: %s: %s." %
                       (result['module'], result['feature'], result['user story'], result['test'],
                        result['testcase']))

        # return
        return result

    def on_exec_testcase_button_click(self, event):
        """ Action performed when user clicks the run testcase button.
        """

        self.log.trace("Handle run testcase button click by user.")
        result = {'successful': False}

        try:
            self.log.debug("Building test run ...")
            # determine test path from input fields
            data = self.determine_test_path_from_input_fields()
            module_name = data['module']
            feature_name = data['feature']
            story_name = data['user story']
            test_name = data['test']
            case_name = data['testcase']

            # determine publish plan id
            publish_id = self.input_publish_id.GetString(0, -1)

            # build test run
            testrun = TestRun(self.log, self.database, name='Debug Test Run', submodule_id=3,
                testcases=[], results_plan_id=publish_id)
            testcases_to_run = testrun.build_testcase_list_for_run(module_name=module_name,
                feature_name=feature_name, story_name=story_name, test_name=test_name,
                case_name=case_name)['testcases']

            # determine class
            self.log.trace("Getting string from testcase class input field ...")
            testcase_class = self.input_testcase_class.GetString(
                self.input_testcase_class.GetSelection())
            testrun.filter_testcases_by_class(testcases_to_run, testcase_class)

            # execute test case
            testrun.testcases = testcases_to_run
            testrun.run()

            self.log.trace("Handled run testcase button click by user.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle run testcase button click by user")

        # return
        return result

    def on_add_lic_testcases_button_click(self, event):
        """ Action performed when user clicks the add licensing testcases button.
        NOTE: Only handles procedures with configure licensing step as
            second step. Template procedure must be established in UI, as well as
            results ID (can update results ID from a previously added validation test).
        """

        LICENSE_TYPES = ['Demo', 'Basic', 'Full', 'Autoclip', 'Health', 'Clip management', 'Location']

        self.log.trace("Handling add licensing testcase button click by user ...")
        result = {'successful': False}

        # flag for adding licensing tests
        self.add_lic = True

        try:
            # determine results ID from input field
            self.log.trace("Getting string from testcase results ID input field ...")
            results_id = self.determine_results_id_from_input_field()['results id']

            # determine test path from input fields
            data = self.determine_test_path_from_input_fields()
            module_name = data['module']
            feature_name = data['feature']
            story_name = data['user story']
            test_name = 'Licensing'

            # determine the test id from test path
            test_id = self.determine_test_id_from_test_path(module_name, feature_name, story_name,
                test_name, results_id)['test id']

            # hard-coded class
            testcase_class = '4'

            # determine minimum version
            minversion = self.input_minversion.GetString(0, -1)

            # determine template procedure
            procedure = self.determine_procedure_from_inputs()['procedure']

            for lic_type in LICENSE_TYPES:
                # case name per license type
                case_name = lic_type

                # rebuild procedure
                procedure = self.rebuild_procedure_with_lic_config(procedure, lic_type)['procedure']

                # evaluate mimimum version
                if lic_type.lower() == 'location' and float(minversion) < 3.4:
                    minversion = 3.4

                self.modify_testcase(case_name, test_id, procedure, minversion, testcase_class)

                self.log.trace("Handled add licensing testcases button click by user.")
            result['successful'] = True
        except BaseException, e:
            self.log.error("Failed to handle add licensing testcases button click by user.")
            self.log.error(str(e))
            for error in e:
                self.log.error(str(error))
            exception = return_execution_error()['error']
            self.log.error("Error: %s." % exception)

        # switch flag off
        self.add_lic = False

        # return
        return result

    def determine_test_id_from_test_path(self, module_name, feature_name, story_name, test_name,
                                         results_id):

        self.log.trace("Determining test ID from test path ...")
        result = {'successful': False, 'test id': None}

        # determine module id
        if self.custom_module:
            # insert entry into database
            table = TABLES['modules']
            entry = {
                MODULE_FIELDS['name']:        module_name,
            }
            module_id = self.database.add_entry_to_table(self.database.db_handle,
                table, entry)['id']
        else:
            module_id = self.database.return_module_id(module_name)['id']
        # determine feature id
        if self.custom_feature:
            # insert entry into database
            table = TABLES['features']
            entry = {
                FEATURE_FIELDS['name']:         feature_name,
                FEATURE_FIELDS['module']:       module_id,
            }
            feature_id = self.database.add_entry_to_table(self.database.db_handle,
                table, entry)['id']
        else:
            feature_id = self.database.return_feature_id(feature_name)['id']
        # determine user story id
        if self.custom_story:
            # insert entry into database
            table = TABLES['user stories']
            entry = {
                STORY_FIELDS['name']:           story_name,
                STORY_FIELDS['feature']:        feature_id,
            }
            story_id = self.database.add_entry_to_table(self.database.db_handle,
                table, entry)['id']
        else:
            story_id = self.database.return_user_story_id(story_name)['id']
        # determine test id
        if self.custom_test or self.add_lic:
            # insert entry into database
            table = TABLES['tests']
            entry = {
                TEST_FIELDS['name']:            test_name,
                TEST_FIELDS['user story']:      story_id,
                TEST_FIELDS['results id']:      results_id,
            }
            test_id = self.database.add_entry_to_table(self.database.db_handle,
                table, entry)['id']

            # switch flag off if used to detect (only create Licensing test once)
            if self.add_lic: self.add_lic = False
        else:
            test_id = self.database.return_test_id(test_name, story_id)['id']
            # update results id
            table = TABLES['tests']
            entry = {
                TEST_FIELDS['results id']:      results_id,
            }
            self.database.update_entry_in_table(self.database.db_handle, table,
                test_id, entry)

        # update variable for return
        result['test id'] = test_id

        # return
        return result

    def determine_procedure_from_inputs(self):

        self.log.trace("Determining procedure from inputs ...")
        result = {'successful': False, 'procedure': None}

        # determine procedure
        procedure = None
        for step_selection in self.procedure_steps:
            # get step name from selection
            n = self.procedure_steps.index(step_selection)
            self.log.trace("Getting string from step input field %s ..." % n)
            step_name = step_selection.GetString(step_selection.GetSelection())
            self.log.trace("Returned step %s: %s" % (n, step_name))
            # determine step ID
            if step_name != '':
                handle = self.database.db_handle
                table = TABLES['procedure steps']
                return_field = STEP_FIELDS['id']
                addendum = "WHERE %s = '%s'" % (STEP_FIELDS['name'], step_name)
                step_id = self.database.query_database_table(handle, table, return_field,
                    addendum)['response'][0][0]
                # append to procedure string
                if procedure is None:
                    procedure = "%s" % step_id
                else:
                    procedure += ",%s" % step_id

        result['procedure'] = procedure

        # return
        return result

    def rebuild_procedure_with_lic_config(self, procedure, lic_type):
        """ Rebuild the procedure with the specific license configuration.
        INPUT
            procedure: the procedure (in database string format, e.g. "4,5,2,3"
            lic type: the type of license to have configured (e.g. "autoclip", "basic"). See map.
        OUPUT
            successful: whether the function executed successfully or not.
            procedure: the rebuilt procedure
        """

        LIC_TYPE_TO_STEP_ID = {
            'demo':             33,
            'basic':            6,
            'full':             30,
            'autoclip':         25,
            'health':           24,
            'clip management':  26,
            'location':         29,
        }

        self.log.trace("Rebuilding procedure with %s license configuration ..." % lic_type)
        result = {'successful': False, 'procedure': None}

        try:
            steps = procedure.split(',')

            # first step (log in)
            mod_procedure = '%s' % steps[0]

            # second step (license config)
            mod_procedure += ',%s' % LIC_TYPE_TO_STEP_ID[lic_type.lower()]

            # additional steps
            for step in steps[2:]:
                mod_procedure += ',%s' % step

            result['procedure'] = mod_procedure
            self.log.trace("Rebuilt procedure with %s license configuration." % lic_type)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="rebuild procedure with %s license configuration"
                                               % lic_type)

        # return
        return result

    def on_add_testcase_button_click(self, event):
        """ Action performed when user clicks the add testcase button.
        """

        self.log.trace("Handle add testcase button click by user.")
        result = {'successful': False}

        try:
            # determine results ID from input field
            self.log.trace("Getting string from testcase results ID input field ...")
            results_id = self.determine_results_id_from_input_field()['results id']

            # determine test path from input fields
            data = self.determine_test_path_from_input_fields()
            module_name = data['module']
            feature_name = data['feature']
            story_name = data['user story']
            test_name = data['test']
            case_name = data['testcase']

            # determine the test id from test path
            test_id = self.determine_test_id_from_test_path(module_name, feature_name, story_name,
                test_name, results_id)['test id']

            # determine test case id (if modifying existing test case)
            if self.custom_testcase:
                case_id = None
            else:
                case_id = self.database.return_testcase_id(case_name, test_id)['id']

            # determine class
            self.log.trace("Getting string from testcase class input field ...")
            testcase_class = self.input_testcase_class.GetString(
                self.input_testcase_class.GetSelection())
            if testcase_class.lower() == BLANK_SEL.lower(): testcase_class = "3"

            # determine minimum version
            minversion = self.input_minversion.GetString(0, -1)

            # determine procedure
            procedure = self.determine_procedure_from_inputs()['procedure']

            # add test case
            if case_id is None:
                result['successful'] = self.modify_testcase(case_name, test_id, procedure,
                    minversion, testcase_class)['verified']
            else:
                result['successful'] =\
                self.modify_testcase(case_name, test_id, procedure, minversion, testcase_class,
                    testcase_id=case_id)['verified']
            self.log.trace("Handled adding testcase button click by user.")
        except BaseException, e:
            self.handle_exception(e, "handle add testcase button click by user")

        # return
        return result