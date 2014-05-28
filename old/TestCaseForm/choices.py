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

BLANK_SEL = "None"
CUSTOM_SEL = "Custom"
DEFAULT_SEL = [BLANK_SEL, CUSTOM_SEL]

####################################################################################################
# Choices ##########################################################################################
####################################################################################################
####################################################################################################


class Choices():
    """ Actions to perform on choices from selection drop-down inputs. """

    def on_step_choice(self, event, placement):
        """ Action performed when user selects a step from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle step selection by user.")
        result = {'successful': False}

        try:
            # check if next step already exists
            n = len(self.procedure_steps)
            if str(n) == str(placement):
                self.log.trace("Next step does not exist. Creating ...")
                self.create_new_input_step()

            else:
                self.log.trace("Next step exists.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle module selection by user")

        # return
        return result

    def on_module_choice(self, event):
        """ Action performed when user selects a module from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle module selection by user.")
        result = {'successful': False}

        try:
            # determine module selected
            module_name = event.GetString()

            self.feature_choices = []
            for selection in DEFAULT_SEL:
                self.feature_choices.append(selection)
            if module_name.lower() == CUSTOM_SEL.lower():
                # set custom flag
                self.custom_module = True
                # show custom input
                self.input_custom_module.Show()
            else:
                # clear custom flag
                self.custom_module = False
                # make sure custom field is hidden
                self.input_custom_module.Hide()
                if module_name.lower() != BLANK_SEL.lower():
                    # return all features for module
                    self.log.trace("Rebuilding feature list for %s module ..." % module_name)
                    features = self.database.return_features_for_module(module_name)['features']

                    # build feature list
                    for feature in features:
                        self.feature_choices.append(feature['name'])

            # set feature choices to selection
            self.input_feature.SetItems(self.feature_choices)
            self._update_feature_input_according_to_custom_module_flag()
            self.log.trace("Feature list for %s module rebuilt." % module_name)

            # reset user story selections
            self.log.trace("Reseting user story list ...")
            self.story_choices = []
            for selection in DEFAULT_SEL:
                self.story_choices.append(selection)
            self.input_story.SetItems(self.story_choices)
            self._update_story_input_according_to_custom_feature_flag()
            self.log.trace("User story list reset.")

            # reset test selections
            self.log.trace("Reseting test list ...")
            self.test_choices = []
            for selection in DEFAULT_SEL:
                self.test_choices.append(selection)
            self.input_test.SetItems(self.test_choices)
            self._update_test_input_according_to_custom_story_flag()
            self.log.trace("Test list reset.")

            # reset testcase selections
            self.log.trace("Reseting test case list ...")
            self.testcase_choices = []
            for selection in DEFAULT_SEL:
                self.testcase_choices.append(selection)
            self.input_testcase.SetItems(self.testcase_choices)
            self._update_testcase_input_according_to_custom_test_flag()
            self.log.trace("Test case list reset.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle module selection by user")

        # return
        return result

    def on_feature_choice(self, event):
        """ Action performed when user selects a feature from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle feature selection by user.")
        result = {'successful': False}

        try:
            # determine feature selected
            module_name=None
            if not self.custom_module: module_name = self.input_module.GetString(self.input_module.GetSelection())
            feature_name = event.GetString()

            self.story_choices = []
            for selection in DEFAULT_SEL:
                self.story_choices.append(selection)
            if feature_name.lower() == CUSTOM_SEL.lower():
                # set custom flag
                self.custom_feature = True
                # show custom input
                self.input_custom_feature.Show()
            else:
                # clear custom flag
                self.custom_feature = False
                # make sure custom field is hidden
                self.input_custom_feature.Hide()
                if feature_name.lower() != BLANK_SEL.lower():
                    # return all features for module
                    self.log.trace("Rebuilding user story list for %s module ..." % feature_name)
                    stories = \
                    self.database.return_user_stories_for_feature(feature_name, module=module_name)['user stories']

                    # build story list
                    for story in stories:
                        self.story_choices.append(story['name'])

            # set feature choices to selection
            self.input_story.SetItems(self.story_choices)
            self._update_story_input_according_to_custom_feature_flag()
            self.log.trace("User Story list for %s feature rebuilt." % feature_name)

            # reset test selections
            self.log.trace("Reseting test list ...")
            self.test_choices = []
            for selection in DEFAULT_SEL:
                self.test_choices.append(selection)
            self.input_test.SetItems(self.test_choices)
            self._update_test_input_according_to_custom_story_flag()
            self.log.trace("Test list reset.")

            # reset testcase selections
            self.log.trace("Reseting test case list ...")
            self.testcase_choices = []
            for selection in DEFAULT_SEL:
                self.testcase_choices.append(selection)
            self.input_testcase.SetItems(self.testcase_choices)
            self._update_testcase_input_according_to_custom_test_flag()
            self.log.trace("Test case list reset.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle feature selection by user")

        # return
        return result

    def on_story_choice(self, event):
        """ Action performed when user selects a story from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle user story selection by user.")
        result = {'successful': False}

        try:
            # determine feature selected
            story_name = event.GetString()

            self.test_choices = []
            for selection in DEFAULT_SEL:
                self.test_choices.append(selection)
            if story_name.lower() == CUSTOM_SEL.lower():
                # set custom flag
                self.custom_story = True
                # show custom input
                self.input_custom_story.Show()
            else:
                # clear custom flag
                self.custom_story = False
                # make sure custom field is hidden
                self.input_custom_story.Hide()
                if story_name.lower() != BLANK_SEL.lower():
                    # return all tests for user story
                    self.log.trace("Rebuilding test list for %s user story ..." % story_name)
                    self.story_id = self.database.return_user_story_id(story_name)['id']
                    tests = self.database.return_tests_for_user_story(self.story_id)['tests']

                    # build test list
                    for test in tests:
                        self.test_choices.append(test['name'])

            # set test choices to selection
            self.input_test.SetItems(self.test_choices)
            self._update_test_input_according_to_custom_story_flag()
            self.log.trace("Test list for %s user story rebuilt." % story_name)

            # reset testcase selections
            self.log.trace("Reseting test case list ...")
            self.testcase_choices = []
            for selection in DEFAULT_SEL:
                self.testcase_choices.append(selection)
            self.input_testcase.SetItems(self.testcase_choices)
            self._update_testcase_input_according_to_custom_test_flag()
            self.log.trace("Test case list reset.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle user story selection by user")

        # return
        return result

    def on_test_choice(self, event):
        """ Action performed when user selects a test from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle test selection by user.")
        result = {'successful': False}

        try:
            # determine test selected
            test_name = event.GetString()

            self.testcase_choices = []
            for selection in DEFAULT_SEL:
                self.testcase_choices.append(selection)
            if test_name.lower() == CUSTOM_SEL.lower():
                # set custom flag
                self.custom_test = True
                # show custom input
                self.input_custom_test.Show()
            else:
                # clear custom flag
                self.custom_test = False
                # make sure custom field is hidden
                self.input_custom_test.Hide()
                if test_name.lower() != BLANK_SEL.lower():
                    # return all testcases for module
                    self.log.trace("Rebuilding test case list for %s module ..." % test_name)
                    self.test_id = self.database.return_test_id(test_name, self.story_id)['id']
                    testcases = self.database.return_testcases_for_test(self.test_id)['testcases']

                    # build feature list
                    for testcase in testcases:
                        self.testcase_choices.append(testcase['name'])

            # set testcase choices to selection
            self.input_testcase.SetItems(self.testcase_choices)
            self._update_testcase_input_according_to_custom_test_flag()
            self.log.trace("Test case list for %s test rebuilt." % test_name)

            # update results ID input
            self.log.trace("Updating results ID ...")
            if test_name.lower() != BLANK_SEL.lower():
                self.results_id = self.database.return_results_id_for_test(self.test_id)['id']
            else:
                self.results_id = ''
            self.input_results.SetValue(str(self.results_id))

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle test selection by user")

        # return
        return result

    def on_testcase_choice(self, event):
        """ Action performed when user selects a test case from dropdown.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Handle test case selection by user.")
        result = {'successful': False}

        try:
            # determine test selected
            case_name = event.GetString()

            if case_name.lower() == CUSTOM_SEL.lower():
                # set custom flag
                self.custom_testcase = True
                # show custom input
                self.input_custom_testcase.Show()

            else:
                # clear custom flag
                self.custom_testcase = False
                # make sure custom field is hidden
                self.input_custom_testcase.Hide()
                if case_name.lower() != BLANK_SEL.lower():
                    # determine test case ID
                    self.case_id = self.database.return_testcase_id(case_name, self.test_id)['id']
                    # return data
                    data = self.database.return_testcase_data(self.case_id)
                    testcase_data = data['testcase data']

                    # set class
                    self.input_testcase_class.SetSelection(
                        self.input_testcase_class.FindString(str(testcase_data['class'])))

                    # set minimum version
                    self.input_minversion.SetValue(str(testcase_data['minimum version']))

                    # parse procedure into IDs
                    step_ids = testcase_data['procedure'].replace(' ', '').split(',')
                    # update base step with first step
                    #self.log.trace("Updating base step ...")
                    #if len(step_ids) >= 1:
                    #    step_data = self.database.return_procedure_step_data(step_ids[0])['step data']
                    #    select_id = self.input_base_step.FindString(str(step_data['name']))
                    #    self.input_base_step.SetSelection(select_id)
                    #else: self.log.trace("No steps found in test case.")
                    # update additional steps
                    if len(step_ids) > 0:
                        for step_id in step_ids:
                            step_data = self.database.return_procedure_step_data(step_id)['step data']
                            # determine if procedure step input already exists
                            index = step_ids.index(step_id)
                            if len(self.procedure_steps) >= index + 1:
                                input = self.procedure_steps[index]
                            else:
                                # create new step
                                input = self.create_new_input_step()['step']

                            # set step input selection
                            select_id = input.FindString(str(step_data['name']))
                            input.SetSelection(select_id)
                    else: self.log.trace("No steps found in test case.")

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "handle test case selection by user")

        # return
        return result