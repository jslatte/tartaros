###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from wx import Frame, TextCtrl, StaticText, ALIGN_CENTER, Choice
from wx import TE_CENTER, CheckBox
from utility import return_execution_error
from Database import Database
from MenuBar import MenuBar
from StepForm import StepForm
from TestCaseForm import TestCaseForm

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Main Window ######################################################################################
####################################################################################################
####################################################################################################


class MainWindow(Frame, TestCaseForm, StepForm):
    """ Main window frame for user interface. """

    def __init__(self, logger):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # initialize the MainWindow instance as inheriting the parent
        #   wx.Frame.__init__() function, and extending
        super(MainWindow, self).__init__(parent=None)

        # define attributes
        self.height = 500
        self.width = 900
        self.title = 'Tartaros'

        # instantiate logger
        self.log = logger

        # initialize database object
        self.database = Database(self.log)

        # define attributes
        self.label_width = 100
        self.label_height = 20
        self.input_width = 2 * self.label_width
        self.input_height = 20
        self.margin = 5

        # GUI tracking variables
        self.global_x = 0
        self.global_y = 20
        self.local_x = self.global_x
        self.local_y = self.global_y
        self.step_global_x = 0
        self.step_global_y = 0
        self.step_local_x = self.step_global_x
        self.step_local_y = self.step_global_y

        # size of frame
        width = self.margin*2 + self.label_width + self.input_width
        height = self.margin*2 + self.global_y
        self.size = (width, height)

        # custom test form fields tracking
        self.custom_module = False
        self.custom_feature = False
        self.custom_story = False
        self.custom_test = False
        self.custom_testcase = False

        # flag for adding licensing tests
        self.add_lic = False

        # initialize window
        self.Initialize()

    def Initialize(self):
        """ Initialize the main window.
        """

        self.log.debug("Initializing main window ...")
        result = {'successful': False}

        try:
            # build menu bar
            self.MenuBar = MenuBar(self, self.log)

            # build testcase form
            self.build_testcase_form()

            # build step form
            self.global_x = (self.label_width + 2 * self.input_width + self.margin * 4)
            self.global_y = 20
            self.build_step_form()

            # set attributes of main window
            self.SetAttributes()

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "initialize main window")

        # return
        return result

    def handle_exception(self, e, operation=None):
        """ Handle an exception.
        INPUT
            e: the exception (from BaseException, e).
            operation: the action being attempted (that failed).
        """

        if operation is not None: self.log.error("Failed to %s." % operation)
        self.log.error(str(e))
        self.log.error("Error: %s." % return_execution_error()['error'])

    def SetAttributes(self):
        """ Set the attributes of the main window.
        """

        self.log.debug("Setting main window attributes ...")
        result = {'successful': False}

        try:
            # determine size to make window
            self.size = (self.width, self.height)

            # set attributes
            self.SetSize(self.size)
            self.SetTitle(self.title)
            self.Centre()
            self.Show(True)

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "set main window attributes")

        # return
        return result

    def build_label_in_row(self, frame, text, pos=None, size=None):
        """ Build a standard text label in a row.
        INPUT
            frame: the parent frame to build the label in.
            text: the text to show in the label.
            pos: the (x, y) position to put the label at.
            size: the (width, height) size of the label.
        OUTPUT
            successful: whether the function executed successfully or not.
        """

        self.log.trace("Building label %s at %s ..." % (text, str((self.local_x, self.local_y))))
        result = {'successful': False}

        try:
            # determine if default needed
            if pos is None:
                pos = (self.local_x, self.local_y)
            if size is None:
                size = (self.label_width, self.label_height)
                # define object
            StaticText(frame, label=text, pos=pos, size=size, style=ALIGN_CENTER)
            # update local tracking to re-position beyond label object space in UI
            self.local_x += size[0]
            # update global tracking to re-position beyond label object space in UI
            if self.global_y < (self.local_y + size[1]):
                self.global_y = (self.local_y + size[1])

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "build label %s" % text)

        # return
        return result

    def build_input_in_row(self, frame, type='text', pos=None, size=None, selection=[]):
        """ Build an input object in a row.
        INPUT
            frame: the parent frame to build the input in.
            type: the type of input to build.
            pos: the (x, y) position to put the input at.
            size: the (width, height) size of the input.
            selection: for type 'dropdown', the selectable items
        OUTPUT
            successful: whether the function executed successfully or not.
            input: the input object created.
        """

        self.log.trace("Building %s input at %s ..." % (type, str((self.local_x, self.local_y))))
        result = {'successful': False, 'input': None}

        try:
            # determine if default needed
            if pos is None:
                pos = (self.local_x, self.local_y)
            if size is None:
                size = (self.input_width, self.input_height)
                # define object
            if type.lower() == 'text':
                result['input'] = TextCtrl(frame,  pos=pos, size=size, style=TE_CENTER)
            elif type.lower() == 'dropdown':
                result['input'] = Choice(frame, pos=pos, size=size)
                # add to selection
                result['input'].SetItems(selection)
            elif type.lower() == 'checkbox':
                result['input'] = CheckBox(frame, pos=pos, size=size)
            else:
                self.log.error("Invalid type %s specified. Failed to build input." % type)
                # update local tracking to re-position beyond label object space in UI
            self.local_x += size[0]
            # update global tracking to re-position beyond label object space in UI
            if self.global_y < (self.local_y + size[1]):
                self.global_y = (self.local_y + size[1])

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, "build %s input" % input)

        # return
        return result