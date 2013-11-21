###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Custom ###########################################################################################
####################################################################################################
####################################################################################################


class Custom():
    """ Handling for custom input fields. """

    def _update_feature_input_according_to_custom_module_flag(self):
        if self.custom_module:
            # set custom flag
            self.custom_feature = True
            # show custom field and default to custom selection
            self.input_feature.SetSelection(0)
            self.input_custom_feature.Show()
        else:
            # clear custom flag
            self.custom_feature = False
            # make sure custom field is hidden
            self.input_custom_feature.Hide()

    def _update_story_input_according_to_custom_feature_flag(self):
        if self.custom_feature:
            # set custom flag
            self.custom_story = True
            # show custom field and default to custom selection
            self.input_story.SetSelection(0)
            self.input_custom_story.Show()
        else:
            # clear custom flag
            self.custom_story = False
            # make sure custom field is hidden
            self.input_custom_story.Hide()

    def _update_test_input_according_to_custom_story_flag(self):
        if self.custom_story:
            # set custom flag
            self.custom_test = True
            # show custom field and default to custom selection
            self.input_custom_test.Show()
            self.input_test.SetSelection(0)
        else:
            # clear custom flag
            self.custom_test = False
            # make sure custom field is hidden
            self.input_custom_test.Hide()

    def _update_testcase_input_according_to_custom_test_flag(self):
        if self.custom_test:
            # set custom flag
            self.custom_testcase = True
            # show custom field and default to custom selection
            self.input_custom_testcase.Show()
            self.input_testcase.SetSelection(0)
        else:
            # clear custom flag
            self.custom_testcase = False
            # make sure custom field is hidden
            self.input_custom_testcase.Hide()