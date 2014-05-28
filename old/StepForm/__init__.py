###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from wx import Panel, EVT_CHOICE, Button, BU_EXACTFIT
from wx import EVT_BUTTON
from mapping import TARTAROS

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
FUNCT_FIELDS = DATABASE['functions']['fields']

####################################################################################################
# Step Form ########################################################################################
####################################################################################################
####################################################################################################


class StepForm(Panel):
    """ Form for adding procedure steps. """

    def build_step_form(self):
        """ Build the step form.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Building step form at %s ..." % str((self.global_x, self.global_y)))
        result = {'successful': False}

        try:
            # build step form title row
            self.local_x = self.global_x + (self.label_width+self.input_width)/2
            self.local_y = self.global_y
            self.build_label_in_row(self, "Step Form")
            self.global_y += self.margin

            # build step name row
            self.local_x = self.global_x
            self.local_y = self.global_y
            self.build_label_in_row(self, "Name")
            self.step_input_name = self.build_input_in_row(self, )['input']
            self.global_y += self.margin

            # build function row
            self.local_x = self.global_x
            self.local_y = self.global_y
            self.build_label_in_row(self, "Function")
            functions = self.database.return_functions()['functions']
            self.step_function_choices = []
            for function in functions:
                self.step_function_choices.append(function['name'])
            # sort function choices
            self.step_function_choices.sort()
            self.step_input_function = self.build_input_in_row(self, type='dropdown',
                selection=self.step_function_choices)['input']
            # bind method to dropdown choice action
            EVT_CHOICE(self, self.step_input_function.GetId(), self.on_function_choice)
            self.global_y += self.margin

            # build arguments row
            self.local_x = self.global_x
            self.local_y = self.global_y
            self.build_label_in_row(self, "Arguments")
            self.step_input_arguments = self.build_input_in_row(self, )['input']
            self.global_y += self.margin

            # build verification row
            self.local_x = self.global_x
            self.local_y = self.global_y
            self.build_label_in_row(self, "Verification Step?")
            self.step_as_verification_cb = self.build_input_in_row(self, type='checkbox')['input']
            self.global_y += self.margin

            # build add step button row
            self.local_x = self.global_x + (self.margin + self.label_width + self.input_width)/2
            self.local_y = self.global_y
            add_step_button_label = "Add Step"
            add_step_button_pos = (self.local_x, self.local_y)
            add_step_button_size = (self.input_width/2, self.input_height)
            self.add_step_button = Button(self, label=add_step_button_label,
                pos=add_step_button_pos, size=add_step_button_size, style=BU_EXACTFIT)
            # bind method to button click action
            EVT_BUTTON(self, self.add_step_button.GetId(),
                self.on_add_step_button_click)
            # update pos
            self.local_x += add_step_button_size[0] + self.margin
            if self.global_y < (self.local_y + add_step_button_size[1]):
                self.global_y = (self.local_y + add_step_button_size[1])
            self.global_y += self.margin

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "build step form")

        # return
        return result

    def on_add_step_button_click(self, event):
        """ Action performed when user clicks the add step button.
        """

        self.log.trace("Handle add step button click by user.")
        result = {'successful': False}

        try:
            # determine test name from input field
            self.log.trace("Getting string from step name input field ...")
            name = self.step_input_name.GetString(0, -1)
            self.log.trace("Returned name: %s." % name)
            # determine results ID from input field
            self.log.trace("Getting string from step arguments input field ...")
            arguments = self.step_input_arguments.GetString(0, -1)
            self.log.trace("Returned arguments: %s" % arguments)
            # determine test path from input fields
            self.log.trace("Getting strings from step functions dropdown lists ...")
            function_name = self.step_input_function.GetString(self.step_input_function.GetSelection())
            self.log.trace("Returned function: %s." % function_name)

            # determine the function id from function name
            self.log.trace("Determining function ID from function name ...")
            handle = self.database.db_handle
            table = TABLES['functions']
            return_field = FUNCT_FIELDS['id']
            known_field = FUNCT_FIELDS['function']
            known_value = function_name
            function_id = self.database.query_database_table_for_single_value(handle,
                table, return_field, known_field, known_value)['value']

            # determine if verification step
            self.log.trace("Determining if step is a verification step ...")
            ver_step = self.step_as_verification_cb.IsChecked()

            # add step
            added = self.add_step(name, function_id, arguments, ver_step)['verified']

            # update all steps in test case form
            if added:
                # rebuild step input
                table = TABLES['procedure steps']
                steps = self.database.query_database_table(self.database.db_handle, table)['response']
                self.step_choices = ['',]
                for step in steps:
                    self.step_choices.append(step[1])

                # sort step choices
                self.step_choices.sort()

                for step in self.procedure_steps:
                    # set selection
                    step.SetItems(self.step_choices)

            result['successful'] = True
            self.log.trace("Handled adding step button click by user.")
        except BaseException, e:
            self.handle_exception(e, "handle add step button click by user")

        # return
        return result

    def on_function_choice(self, event):
        """ Action performed when user selects a function from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle function selection by user.")
        result = {'successful': False}

        try:

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle function selection by user")

        # return
        return result

    def add_step(self, name, function_id, arguments, verification=False):
        """ Add a procedure step.
        INPUT
            name: the name of the step to add.
            function id: the id of the function used in the procedure step.
            arguments: a string arguments passed to the function as they would be written
                parenthetically in the function call (e.g., 'name="Name", testcase=None').
            verification: whether the step is a verification step or not.
        OUTPUT
            successful: whether the function executed successfully or not.
            verified: whether the testcase was verified as added or not.
        """

        self.log.trace("Adding step %s ..." % name)
        result = {'successful': False, 'verified': False}

        try:
            # insert entry into database
            table = TABLES['procedure steps']
            entry = {
                STEP_FIELDS['name']:        name,
                STEP_FIELDS['function']:    function_id,
                STEP_FIELDS['arguments']:   arguments,
                STEP_FIELDS['verification']:str(verification)
            }
            step_id = self.database.add_entry_to_table(self.database.db_handle,
                table, entry)['id']

            # verify testcase added
            returned = self.verify_step_added(step_id, name, function_id, arguments, verification)
            result['verified'] = returned['verified']
            result['successful'] = returned['successful']
            self.log.trace("Procedure step added.")
        except BaseException, e:
            self.handle_exception(e, "add step %s" % name)

        # return
        return result

    def verify_step_added(self, id, name, function_id, arguments, verification):
        """ Verify a step was added.
        INPUT
            id: the id of the step in the database.
            name: the name of the step to add.
            function id: the id of the function used in the procedure step.
            arguments: a string arguments passed to the function as they would be written
                parenthetically in the function call (e.g., 'name="Name", testcase=None').
            verification: whether the step is a verification step or not.
        OUTPUT
            successful: whether the function executed successfully or not.
            verified: whether the testcase was verified as added or not.
        """

        self.log.trace("Verifying step %s added ..." % name)
        result = {'successful': False, 'verified': False}

        try:
            # return testcase data
            step_data = self.database.return_procedure_step_data(id)['step data']
            # verify each data point with given expected values
            failures = False
            if str(name) != str(step_data['name']):
                self.log.error("Expected name to be %s, but was %s."
                               % (name, step_data['name']))
                failures = True
            if int(function_id) != int(step_data['function']):
                self.log.error("Expected function ID to be %s, but was %s."
                               % (function_id, step_data['function']))
                failures = True
            if str(arguments) != str(step_data['arguments']):
                self.log.error("Expected arguments to be %s, but was %s."
                               % (arguments, step_data['arguments']))
                failures = True
            if str(verification) != str(step_data['verification']):
                self.log.error("Expected verification to be %s, but was %s."
                               % (arguments, step_data['verification']))
                failures = True

            if not failures: result['verified'] = True
            self.log.trace("Verified step added.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "verify step %s added" % name)

        # return
        return result