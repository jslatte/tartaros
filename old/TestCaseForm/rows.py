###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from wx import EVT_CHOICE, Button, BU_EXACTFIT
from wx import EVT_BUTTON
from mapping import TARTAROS

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

DATABASE = TARTAROS['database']
TABLES = DATABASE['tables']
STEP_FIELDS = DATABASE['procedure steps']['fields']
BLANK_SEL = "None"
CUSTOM_SEL = "Custom"
DEFAULT_SEL = [BLANK_SEL, CUSTOM_SEL]

####################################################################################################
# Rows #############################################################################################
####################################################################################################
####################################################################################################


class Rows():
    """ Rows to be built individually in the UI. """

    def build_testcase_form_title_row(self):
        self.local_x = self.global_x + (self.label_width+self.input_width)/2
        self.local_y = self.global_y
        self.build_label_in_row(self, "Test Case Form")
        self.global_y += self.margin

    def build_testcase_module_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Module")
        modules = self.database.return_modules_for_submodule(3)['modules']
        self.module_choices = DEFAULT_SEL
        for module in modules:
            self.module_choices.append(module['name'])
        self.input_module = self.build_input_in_row(self, type='dropdown',
            selection=self.module_choices)['input']
        # bind method to dropdown choice action
        EVT_CHOICE(self, self.input_module.GetId(), self.on_module_choice)
        # custom field
        self.local_x += self.margin
        self.input_custom_module = self.build_input_in_row(self, )['input']
        self.input_custom_module.Hide()
        self.global_y += self.margin

    def build_testcase_feature_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Feature")
        self.feature_choices = DEFAULT_SEL
        self.input_feature = self.build_input_in_row(self, type='dropdown',
            selection=self.feature_choices)['input']
        # bind method to dropdown choice action
        EVT_CHOICE(self, self.input_feature.GetId(), self.on_feature_choice)
        # custom field
        self.local_x += self.margin
        self.input_custom_feature = self.build_input_in_row(self, )['input']
        self.input_custom_feature.Hide()
        self.global_y += self.margin

    def build_testcase_user_story_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "User Story")
        self.story_choices = DEFAULT_SEL
        self.input_story = self.build_input_in_row(self, type='dropdown',
            selection=self.story_choices)['input']
        # bind method to dropdown choice action
        EVT_CHOICE(self, self.input_story.GetId(), self.on_story_choice)
        # custom field
        self.local_x += self.margin
        self.input_custom_story = self.build_input_in_row(self, )['input']
        self.input_custom_story.Hide()
        self.global_y += self.margin

    def build_testcase_test_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Test")
        self.test_choices = DEFAULT_SEL
        self.input_test = self.build_input_in_row(self, type='dropdown',
            selection=self.test_choices)['input']
        # bind method to dropdown choice action
        EVT_CHOICE(self, self.input_test.GetId(), self.on_test_choice)
        # custom field
        self.local_x += self.margin
        self.input_custom_test = self.build_input_in_row(self, )['input']
        self.input_custom_test.Hide()
        self.global_y += self.margin

        # build existing testcases for test row
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Test Case")
        self.testcase_choices = DEFAULT_SEL
        self.input_testcase = self.build_input_in_row(self, type='dropdown',
            selection=self.testcase_choices)['input']
        # bind method to dropdown choice action
        EVT_CHOICE(self, self.input_testcase.GetId(), self.on_testcase_choice)
        # custom field
        self.local_x += self.margin
        self.input_custom_testcase = self.build_input_in_row(self, )['input']
        self.input_custom_testcase.Hide()
        self.global_y += self.margin

    def build_testcase_results_id_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Results ID")
        self.input_results = self.build_input_in_row(self, )['input']
        self.global_y += self.margin

    def build_testcase_minversion_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Minimum Version")
        self.input_minversion = self.build_input_in_row(self, )['input']
        self.input_minversion.SetValue("3.2")
        self.global_y += self.margin

    def build_testcase_class_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Class")
        self.testcase_class_choices = [BLANK_SEL, "0", "1", "2", "3", "4", "5"]
        self.input_testcase_class = self.build_input_in_row(self, type='dropdown',
            selection=self.testcase_class_choices)['input']
        self.input_testcase_class.SetSelection(self.input_testcase_class.FindString("3"))
        self.global_y += self.margin

    def build_testcase_action_buttons_row(self):
        # add testcase
        self.local_x = (self.global_x + self.margin + self.label_width + self.input_width)/4
        self.local_y = self.global_y
        add_testcase_button_label = "Add/Edit Testcase"
        add_testcase_button_pos = (self.local_x, self.local_y)
        add_testcase_button_size = (self.input_width/2, self.input_height)
        self.add_testcase_button = Button(self, label=add_testcase_button_label,
            pos=add_testcase_button_pos, size=add_testcase_button_size, style=BU_EXACTFIT)
        # bind method to button click action
        EVT_BUTTON(self, self.add_testcase_button.GetId(),
            #self.test_on_add_testcase_button_click)
            self.on_add_testcase_button_click)
        # update pos
        self.local_x += add_testcase_button_size[0] + self.margin
        if self.global_y < (self.local_y + add_testcase_button_size[1]):
            self.global_y = (self.local_y + add_testcase_button_size[1])
        self.global_y += self.margin

        # execute testcase
        label_text = "Run Testcase(s)"
        pos = (self.local_x, self.local_y)
        size = (self.input_width/2, self.input_height)
        self.exec_testcase_button = Button(self, label=label_text,
            pos=pos, size=size, style=BU_EXACTFIT)
        # bind method to button click action
        EVT_BUTTON(self, self.exec_testcase_button.GetId(),
            self.on_exec_testcase_button_click)
        # update pos
        self.local_x += size[0] + self.margin
        if self.global_y < (self.local_y + size[1]):
            self.global_y = (self.local_y + size[1])
        self.global_y += self.margin

        # test plan id to publish to
        #self.build_label_in_row(self, "Publish ID")
        #pos = (self.local_x, self.local_y)
        #size = (self.input_width/2, self.input_height)
        #self.input_minversion = self.build_input_in_row(self, pos=pos, size=size)['input']
        #self.input_minversion.SetValue("1062")
        #self.global_y += self.margin

        # add licensing testcases
        label_text = "Add Licensing Testcases"
        pos = (self.local_x, self.local_y)
        size = (self.input_width/2, self.input_height)
        self.add_lic_testcases_button = Button(self, label=label_text,
            pos=pos, size=size, style=BU_EXACTFIT)
        # bind method to button click action
        EVT_BUTTON(self, self.add_lic_testcases_button.GetId(),
            self.on_add_lic_testcases_button_click)
        # update pos
        self.local_x += size[0] + self.margin
        if self.global_y < (self.local_y + size[1]):
            self.global_y = (self.local_y + size[1])
        self.global_y += self.margin

    def build_testcase_publish_id_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Publishing Plan ID")
        self.input_publish_id = self.build_input_in_row(self)['input']
        self.input_publish_id.SetValue("1062")
        self.global_y += self.margin

    def build_testcase_procedure_row(self):
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.build_label_in_row(self, "Procedure")
        self.global_y += self.margin
        # build step input
        table = TABLES['procedure steps']
        steps = self.database.query_database_table(self.database.db_handle, table)['response']
        self.step_choices = ['',]
        for step in steps:
            self.step_choices.append(step[1])
        # sort step choices
        self.step_choices.sort()
        # define object in window
        self.input_base_step = self.build_input_in_row(self, type='dropdown',
            selection=self.step_choices)['input']
        # bind method to dropdown choice action
        EVT_CHOICE(self, self.input_base_step.GetId(), lambda evt:
        self.on_step_choice(evt, 1))
        # define base data for procedure steps
        self.procedure_steps = []
        self.procedure_steps.append(self.input_base_step)
        self.step_global_x = self.global_x
        self.step_global_y = self.global_y