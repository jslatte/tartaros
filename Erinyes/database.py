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
from mapping import ERINYES_DB_PATH

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
# Database #########################################################################################
####################################################################################################
####################################################################################################


class Database(Charon):
    """ Library for Erinyes database interaction. """

    def __init__(self, logger, db_path=ERINYES_DB_PATH):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
            db path: the path to the database
        """

        # instantialize logger
        self.log = logger

        # initialize SQLite API library
        db_path = db_path
        Charon.__init__(self, db_path, self.log)

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