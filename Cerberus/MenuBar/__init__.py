###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import wx
from debug import DebugMenu
from file import FileMenu

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Menu Bar #########################################################################################
####################################################################################################
####################################################################################################


class MenuBar(wx.MenuBar):
    """ Menu bar for the main window. """

    def __init__(self, window, logger):
        """
        INPUT
            window: the main window into which the menu bar will be built.
            logger: An initialized instance of a logging class to use.
        """

        # initialize the instance as inheriting the parent, and extending
        super(MenuBar, self).__init__()

        # define attributes
        self.window = window

        # instantiate logger
        self.log = logger

        # build
        self.build_menu_bar()

    def build_menu_bar(self):
        """ Build the menu bar for the main window.
        """

        self.log.debug("Building menu bar ...")
        result = {'successful': False}

        try:
            # build file menu
            self.FileMenu = FileMenu(self.window, self.log)

            # build file menu
            self.DebugMenu = DebugMenu(self.window, self.log)

            # build all menus into menu bar
            self.Append(self.FileMenu, '&File')
            self.Append(self.DebugMenu, '&Debug')

            # build menu bar
            self.window.SetMenuBar(self)

            result['successful'] = True
        except BaseException, e:
            self.log.error(str(e))
            self.log.error("Failed to build menu bar.")

        # return
        return result