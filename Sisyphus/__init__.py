###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from threading import Thread
import time

####################################################################################################
# Updated Thread Class #############################################################################
##### handles return values from threads ###########################################################
####################################################################################################


class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Sisyphus (Test Data Generation) ##################################################################
####################################################################################################
####################################################################################################


class Sisyphus():
    """ Library for test data generation. """

    def __init__(self, logger):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
        """

        # instantialize logger
        self.log = logger

        # thread attributes
        self.threads_to_run = []
        self.running_threads = []
        self.data = []
        self.maxThreads = 256

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

    def run(self):

        pass

    def add_process_with_two_hierarchically_incrementing_variables_to_thread_queue(self, process,
                                                                                   primaryVarMaxRange,
                                                                                   secondaryMaxVarRange,
                                                                                   primaryVarMinRange=1,
                                                                                   secondaryMinVarRange=1,
                                                                                   xtraVar=None):

        # add process threads with incrementing primary variable from 1 to range
        for i in range(primaryVarMinRange, primaryVarMaxRange + 1):
            # add process threads with incrementing secondary variable from 1 to range (for each primary
            #   variable increment)
            for j in range(secondaryMinVarRange, secondaryMaxVarRange + 1):
                if xtraVar is not None:
                    self.add_process_to_thread_queue(process, (i, j, xtraVar, ))
                else:
                    self.add_process_to_thread_queue(process, (i, j, ))

    def add_process_with_incrementing_variable_to_thread_queue(self, process, rangeMax, rangeMin=1):

        # add process thread with incremented variable from 1 to range
        for i in range(rangeMin, rangeMax + 1):
            self.add_process_to_thread_queue(process, (i,))

    def add_process_to_thread_queue(self, process, arguments=()):

        # define thread
        t = ThreadWithReturnValue(target=process, args=arguments)

        # add thread to threads to run list
        self.threads_to_run.append(t)

    def execute_pending_threads(self):

        result = {'time':None, 'data':[]}

        # set start timer
        t0 = time.time()

        # execute each thread in threads to run list, de-populating list as they are run
        while len(self.threads_to_run) > 0:

            # limit the number of concurrent running threads to the max threads allowed
            while len(self.running_threads) < self.maxThreads and len(self.threads_to_run) > 0:
                thread = self.threads_to_run.pop()
                self.running_threads.append(thread)
                thread.start()

            # check each running thread to see if it is still running, de-populating list as they are cleared
            while len(self.running_threads) > 0:
                thread = self.running_threads.pop()
                if thread.isAlive():
                    # re-append to list (if not done executing yet)
                    self.running_threads.append(thread)
                else:
                    # append return data from thread
                    self.data.append(thread.join())

        # end timer and report elapsed time
        t = time.time() - t0
        result['time'] = t
        self.log.trace("All threads executed in %s seconds." % t)

        # compile return data
        result['data'] = self.data

        # return
        return result