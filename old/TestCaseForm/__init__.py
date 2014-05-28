###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from wx import Panel, Choice, EVT_CHOICE, Button, BU_EXACTFIT, EVT_BUTTON
from mapping import TARTAROS
from rows import Rows
from choices import Choices
from buttons import Buttons
from custom import Custom

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
CUSTOM_SEL = "Custom"

####################################################################################################
# Testcase Form ####################################################################################
####################################################################################################
####################################################################################################


class TestCaseForm(Rows, Choices, Buttons, Custom):
    """ Form for adding testcases. """

    def build_testcase_form(self):
        """ Build the testcase form.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Building testcase form ...")
        result = {'successful': False}

        try:
            self.build_testcase_form_title_row()
            self.build_testcase_module_row()
            self.build_testcase_feature_row()
            self.build_testcase_user_story_row()
            self.build_testcase_test_row()
            self.build_testcase_results_id_row()
            self.build_testcase_class_row()
            self.build_testcase_minversion_row()
            self.build_testcase_action_buttons_row()
            self.build_testcase_publish_id_row()
            self.build_testcase_procedure_row()

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "build testcase form")

        # return
        return result

    def create_new_input_step(self):
        """ Create a new procedure step input.
        OUTPUT
            successful: whether the function executed successfully or not.
            step: the step input object created.
        """

        self.log.trace("Creating new input step ...")
        result = {'successful': False, 'step': None}

        try:
            # create a new step input object
            self.step_local_x = self.step_global_x + self.label_width
            self.step_local_y = self.step_global_y
            # base step field input (drop-down)
            pos = (self.step_local_x, self.step_local_y)
            size = (self.input_width, self.input_height)
            # check if next step already exists
            n = len(self.procedure_steps)

            # get object placeholder from list and define
            input_step = Choice(self, pos=pos, size=size)
            # append to list of steps
            self.procedure_steps.append(input_step)
            # set selection
            input_step.SetItems(self.step_choices)
            # bind method to dropdown choice action
            EVT_CHOICE(self, input_step.GetId(), lambda evt: self.on_step_choice(evt, n+1))
            # update pos
            if self.step_global_y < (self.step_local_y + size[1]):
                self.step_global_y = (self.step_local_y + size[1])
            self.step_global_y += self.margin

            # update window size
            self.size = (self.size[0], self.size[1] + size[1])

            result['step'] = input_step
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "create new step")

        # return
        return result