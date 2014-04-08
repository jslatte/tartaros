###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from utility import return_execution_error, read_file_into_list
import psutil, os
from os import getcwdu, path, mkdir
from datetime import datetime
from time import sleep
from utc import UTC

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

ROOT_PATH = getcwdu() + '\\Danaides'
CONFIG_FILE_PATH = ROOT_PATH + '\\config.ini'
OUTPUT_FOLDER_PATH = ROOT_PATH + '\\output'

####################################################################################################
# Danaides (Process Monitoring) ####################################################################
####################################################################################################
####################################################################################################


class Danaides():
    """ Library for process monitoring. """

    def __init__(self, logger, database):
        """
        INPUT
            logger: An initialized instance of a logging class to use.
            database: An initialized instance of the Tartaros database.
        """

        # instantialize logger
        self.log = logger

        # instantialize database
        self.database = database

        # instantialize utc
        self.utc = UTC(self.log)

        # default parameters
        self.mode = 'monitor'
        self.vim_connection_lapse_max = 600
        self.vim_connection_diagnostic_start_time = None
        self.vim_connection_diagnostic_end_time = None

        # load configuration
        self.load_config()

        # create output folder if it does not exist
        if not path.exists(OUTPUT_FOLDER_PATH):
            self.log.trace("Output folder path '%s' does not exist. Creating ..." %
                           OUTPUT_FOLDER_PATH)
            mkdir(OUTPUT_FOLDER_PATH)

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

    def handle_exception(self, e, operation=None):
        """ Handle an exception.
        INPUT
            e: the exception (from BaseException, e).
            operation: the action being attempted (that failed).
        """

        if operation is not None:
            self.log.error("Failed to %s." % operation)
        self.log.error(str(e))
        for error in e:
            self.log.error(str(error))
        exception = return_execution_error()['error']
        self.log.error("Error: %s." % exception)

    def TEMPLATE_FUNCTION(self):
        """
        INPUT
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug(" ...")
        result = {'successful': False, 'verified': False}

        try:

            self.log.trace("")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="")

        # return
        return result

    def load_config(self):
        """ Load the configuration file for Tantalus.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Loading configuration ...")
        result = {'successful': False}

        try:
            # read config file data
            config_data = read_file_into_list(CONFIG_FILE_PATH)['list']

            # parse data into configuration
            parameters = []
            for line in config_data:
                if 'mode =' in line.lower():
                    self.mode = line.lower().strip().split('mode = ')[1]
                    parameters.append(['Mode', self.mode])
                elif 'connection_lapse_max =' in line.lower():
                    self.vim_connection_lapse_max = int(line.lower().strip().split(
                        'connection_lapse_max = ')[1])
                    parameters.append(['ViM Connection Lapse Max', self.vim_connection_lapse_max])

                if 'diag_start_time = none' in line.lower():
                    self.vim_connection_diagnostic_start_time = None
                    parameters.append(
                        ['ViM Connection Lapse Max', self.vim_connection_diagnostic_start_time])
                elif 'diag_start_time =' in line.lower():
                    self.vim_connection_diagnostic_start_time = \
                        self.utc.convert_date_string_to_db_time(
                            line.lower().strip().split('diag_start_time = ')[1])['db time']
                    parameters.append(['ViM Connection Lapse Max',
                                       self.vim_connection_diagnostic_start_time])

                if 'diag_end_time = none' in line.lower():
                    self.vim_connection_diagnostic_end_time = None
                    parameters.append(['ViM Connection Lapse Max',
                                       self.vim_connection_diagnostic_end_time])
                elif 'diag_end_time =' in line.lower():
                    self.vim_connection_diagnostic_end_time = \
                        self.utc.convert_date_string_to_db_time(
                            line.lower().strip().split('diag_end_time = ')[1])['db time']
                    parameters.append(['ViM Connection Lapse Max',
                                       self.vim_connection_diagnostic_end_time])

            # log parameters in output
            for param in parameters:
                self.log.trace("CONFIGURATION: %s = %s" % (param[0], param[1]))

            self.log.debug("... DONE loading configuration.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="load configuration")

        # return
        return result

    def run(self):
        self.log.info("Running %s in %s mode ..." % (self.module_name, self.mode))
        if self.mode.lower() == 'monitor':
            self.monitor_memory_usage_of_process("VIM.exe")
        elif self.mode.lower() == 'vim connection diagnostic':
            self.perform_post_mortem_vim_connection_diagnostic()

    def perform_post_mortem_vim_connection_diagnostic(self):
        """ Perform a 'post mortem' ViM connection diagnostic on an existing installation.
        INPUT
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Performing a post mortem ViM connection diagnostic ...")
        result = {'successful': False, 'diagnostics': None}

        try:
            result['diagnostics'] = \
                self.compile_vim_connection_diagnostics(
                    start_time=self.vim_connection_diagnostic_start_time,
                    end_time=self.vim_connection_diagnostic_end_time)['diagnostics']

            self.log.debug("... DONE performing post mortem ViM connection diagnostic.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="perform a post mortem ViM connection diagnostic")

        # return
        return result

    def compile_vim_connection_diagnostics(self, start_time=None, end_time=None, dir=None):
        """ Compile connection diagnostics for ViM.
        INPUT
            start time: optional start time for which to collect diagnostics (in db time format).
            end time: optional end time for which to collect diagnostics (in db time format).
            dir: the folder path containing the VIM.db file.
        OUPUT
            successful: whether the function executed successfully or not.
            diagnostics: a data dictionary including all diagnostic information (per site).
        """

        self.log.debug("Compiling ViM connection diagnostics ")
        if start_time is not None and end_time is not None:
                self.log.trace_in_line("for between %s and %s ..." % (start_time, end_time))
        elif start_time is not None and end_time is None:
            self.log.trace_in_line("for after %s ..." % start_time)
        elif start_time is None and end_time is not None:
            self.log.trace_in_line("for before %s ..." % end_time)
        else:
            self.log.trace_in_line("...")
        result = {'successful': False, 'diagnostics': None}

        try:
            # import ViM submodule (and connect to ViM database)
            from Hestia import Hestia
            if dir is not None:
                hestia = Hestia(self.log, self.database, dir=dir)
            else:
                hestia = Hestia(self.log, self.database)
            hestia.db.connect_to_database()
            hestia.db.db_handle = hestia.db.create_database_handle()['handle']

            self.log.trace("Building data dictionary to track connection data per site ...")

            # query database for sites
            handle = hestia.db.db_handle
            table = "RemoteSites"
            response = hestia.db.query_database_table(handle, table)['response']

            # build data dictionary to track connection data per site
            connection_data = {}
            for entry in response:
                connection_data[str(entry[0])] = {
                    'name': str(entry[4]),
                    'timestamps':   [],
                    'times between connections':    [],
                    'connection frequency': 0,
                    'total number of connections':  0,
                    'long re-connect periods': [],
                }

            # query database for connection timestamps
            table = "ConnectionLog"
            if start_time is not None and end_time is not None:
                addendum = 'WHERE csTimeStamp > %s and csTimeStamp < %s' % (start_time, end_time)
            elif start_time is not None and end_time is None:
                addendum = 'WHERE csTimeStamp > %s' % start_time
            elif start_time is None and end_time is not None:
                addendum = 'WHERE csTimeStamp < %s' % end_time
            else:
                addendum = ''
            response = hestia.db.query_database_table(handle, table, addendum=addendum)['response']

            # determine start and end times (if none given) from connection log
            if start_time is None:
                start_time = response[0][3]
                self.vim_connection_diagnostic_start_time = start_time
            if end_time is None:
                end_time = response[-1][3]
                self.vim_connection_diagnostic_end_time = end_time

            self.log.trace("... DONE building data dictionary to track connection data per site.")

            # build list of connection timestamps from database list for each site
            self.log.trace("Building list of connection timestamps for each site")
            for entry in response:
                connection_data[str(entry[0])]['timestamps'].append(entry[3])

            self.log.trace("... DONE building list of connection timestamps for each site.")

            # build list of time between connections for each site
            self.log.trace("Building list of time between connections for each site ...")
            for entry in connection_data:
                site = connection_data[entry]
                c_timestamp = None
                for timestamp in site['timestamps']:

                    # determine time between connections only if current (previous) timestamp set
                    if c_timestamp is not None:
                        time_between_connections = timestamp - c_timestamp
                        site['times between connections'].append({
                            'time between connections': time_between_connections,
                            'previous connection time': c_timestamp,
                            're-connect time': timestamp})

                    # update current timestamp
                    c_timestamp = timestamp

            self.log.trace("... DONE building list of time between connections for each site.")
                #self.log.trace("Times between Connections for %s:\t%s"
                #               % (site['name'], site['times between connections']))

            # determine connection frequency for each site
            self.log.trace("Determining connection frequency for each site ...")
            for entry in connection_data:
                site = connection_data[str(entry)]

                amalgamated_time_between_connections = 0
                for time_between_connections in site['times between connections']:
                    amalgamated_time_between_connections += \
                        time_between_connections['time between connections']

                try:
                    site['connection frequency'] = \
                        amalgamated_time_between_connections/len(site['times between connections'])
                except ZeroDivisionError:
                    site['connection frequency'] = 0

            self.log.trace("... DONE determining connection frequency for each site.")

            # determine total number of connections made per site
            self.log.trace("Determining total number of connections made for each site ...")
            for entry in connection_data:
                site = connection_data[entry]

                site['total number of connections'] = len(site['timestamps'])

            self.log.trace("... DONE determining total number of connections made for each site.")

            # determine any long re-connect periods for each site
            self.log.trace("Looking for long re-connect periods for each site ...")
            for entry in connection_data:
                site = connection_data[str(entry)]

                for connection_entry in site['times between connections']:
                    if connection_entry['time between connections'] > self.vim_connection_lapse_max:
                        site['long re-connect periods'].append({
                            'previous connection time':
                                connection_entry['previous connection time'],
                            're-connection time': connection_entry['re-connect time'],
                            'time between connections':
                                connection_entry['time between connections'],
                        })

            self.log.debug("... DONE Compiling ViM connection diagnostics.")
            result['diagnostics'] = connection_data
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="compile ViM connection diagnostics")

        # return
        return result

    def monitor_memory_usage_of_process(self, process):
        """ Monitor the memory usage of a process.
        INPUT
            process: the process to monitor (string format for name of process as it
                appears in task manager, e.g., "VIM.exe")
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Monitoring memory usage for %s process ..." % process)
        result = {'successful': False,
                  'current memory used': {'rss': 0, 'vms': 0},
                  'net change in memory usage': {'rss': 0, 'vms': 0},
                  'total memory allocated': {'rss': 0, 'vms': 0},
                  'total memory de-allocated': {'rss': 0, 'vms': 0}}

        try:
            while True:
                # determine process ID of server
                process_id = None
                for p in psutil.process_iter():
                    if process.lower() in str(p.name).lower():
                        process_id = p.pid
                        self.log.trace("Process %s found: ID %d." % (process, process_id))

                if process_id is not None:
                    # define process object for monitoring (using psutil)
                    p = psutil.Process(process_id)

                    # create output file to log to
                    file_path = "%s\\%s-%s-memory_usage_monitoring.log" \
                                % (OUTPUT_FOLDER_PATH,
                                   str(datetime.now()).replace(':', '_').replace(' ', '-').replace(
                                       '.', '_'),
                                   str(process).split('.')[0])
                    output_log = open(file_path, 'w')
                    output_log.close()

                    # determine total physical memory
                    total_mem = float(psutil.virtual_memory().total) / 1000 / 1000
                    log_msg = "Total Memory:\t%f MB" % total_mem
                    self.log.trace(log_msg)
                    with open(file_path, 'a') as output_log:
                        output_log.write('\n%s\t' % datetime.now() + log_msg)

                    # initial memory usage
                    i_mem_usage_info = p.get_memory_info()._asdict()
                    i_working_set = float(i_mem_usage_info['rss']) / 1000000
                    i_private_set = float(i_mem_usage_info['vms']) / 1000000

                    # tracking variables
                    log_msgs = ["Initial Process Memory Usage:",
                                "Resident Set Size:\t%f MB" % i_working_set,
                                "Virtual Memory Size:\t%f MB" % i_private_set,
                                '\n']
                    for log_msg in log_msgs:
                        self.log.trace(log_msg)
                    with open(file_path, 'a') as output_log:
                        for log_msg in log_msgs:
                            output_log.write('\n%s\t' % datetime.now() + log_msg)

                    c_working_set = i_working_set
                    c_private_set = i_private_set

                    i_time = datetime.now()

                    while True:
                        try:
                            # get percent memory usage of process
                            mem_usage_info = p.get_memory_info()._asdict()
                            working_set = float(mem_usage_info['rss']) / 1000000
                            private_set = float(mem_usage_info['vms']) / 1000000

                            sleep(1)

                            if working_set != c_working_set or private_set != c_private_set:
                                c_time = str(datetime.now() - i_time)

                                dif_working_set = working_set - c_working_set
                                dif_private_set = private_set - c_private_set
                                log_msgs = ["Change in Memory Usage (after %s):" % c_time,
                                            "Resident Set Size:\t%f MB to %f MB" % (
                                                dif_working_set, working_set),
                                            "Virtual Memory Size:\t%f MB to %f MB" % (
                                                dif_private_set, private_set),
                                            '\n']
                                for log_msg in log_msgs:
                                    self.log.trace(log_msg)
                                with open(file_path, 'a') as output_log:
                                    for log_msg in log_msgs:
                                        output_log.write('\n%s\t' % datetime.now() + log_msg)

                                # update memory de/allocation accordingly
                                if working_set > c_working_set:
                                    result['total memory allocated']['rss'] += dif_working_set
                                elif working_set < c_working_set:
                                    result['total memory de-allocated']['rss'] += dif_working_set

                                if private_set > c_private_set:
                                    result['total memory allocated']['vms'] += dif_private_set
                                elif private_set < c_private_set:
                                    result['total memory de-allocated']['vms'] += dif_private_set

                                # update current memory usage tracking variable with new value
                                c_working_set = working_set
                                c_private_set = private_set

                                # update total memory usage change
                                result['current memory used'] = {'rss': c_working_set,
                                                                 'vms': c_private_set}
                                result['net change in memory usage'] = {
                                    'rss': (c_working_set - i_working_set),
                                    'vms': (c_private_set - i_private_set)}

                                timestamp = datetime.now()
                                elapsed_time = timestamp - i_time
                                log_msgs = ['\n%s\tNet Change in Memory Usage (after %s):\t%f MB '
                                            '(Resident Set Size),'
                                            ' %f MB (Virtual Memory Size)'
                                            % (timestamp, elapsed_time,
                                               result['net change in memory usage']['rss'],
                                               result['net change in memory usage']['vms']),
                                            '\n%s\tTotal Memory Allocated (after %s):\t%f MB '
                                            '(Resident Set Size),'
                                            ' %f MB (Virtual Memory Size)'
                                            % (timestamp, elapsed_time,
                                               result['total memory allocated']['rss'],
                                               result['total memory allocated']['vms']),
                                            '\n%s\tTotal Memory De-Allocated (after %s):\t%f MB '
                                            '(Resident Set Size),'
                                            ' %f MB (Virtual Memory Size)'
                                            % (timestamp, elapsed_time,
                                               result['total memory de-allocated']['rss'],
                                               result['total memory de-allocated']['vms']),
                                            '\n']
                                # log net change
                                with open(file_path, 'a') as output_log:
                                    for log_msg in log_msgs:
                                        output_log.write(log_msg)

                        except BaseException, e:
                            self.log.warn("Process monitor interrupted.")
                            self.log.warn(str(e))
                            with open(file_path, 'a') as output_log:
                                timestamp = datetime.now()
                                elapsed_time = timestamp - i_time
                                log_msgs = ['\n%s\tNet Change in Memory Usage (after %s):\t%f MB '
                                            '(Resident Set Size),'
                                            ' %f MB (Virtual Memory Size)'
                                            % (timestamp, elapsed_time,
                                               result['net change in memory usage']['rss'],
                                               result['net change in memory usage']['vms']),
                                            '\n%s\tTotal Memory Allocated (after %s):\t%f MB '
                                            '(Resident Set Size),'
                                            ' %f MB (Virtual Memory Size)'
                                            % (timestamp, elapsed_time,
                                               result['total memory allocated']['rss'],
                                               result['total memory allocated']['vms']),
                                            '\n%s\tTotal Memory De-Allocated (after %s):\t%f MB '
                                            '(Resident Set Size),'
                                            ' %f MB (Virtual Memory Size)'
                                            % (timestamp, elapsed_time,
                                               result['total memory de-allocated']['rss'],
                                               result['total memory de-allocated']['vms']),
                                            '\n']
                                # log net change
                                with open(file_path, 'a') as output_log:
                                    for log_msg in log_msgs:
                                        output_log.write(log_msg)

                            self.log.trace("Looking for %s process ..." % process)

                            # result tracking variables
                            result['net change in memory usage'] = {'rss': 0, 'vms': 0}
                            result['total memory allocated'] = {'rss': 0, 'vms': 0}
                            result['total memory de-allocated'] = {'rss': 0, 'vms': 0}

                            i_working_set = 0
                            i_private_set = 0

                            working_set = 0
                            private_set = 0

                            c_working_set = 0
                            c_private_set = 0

                            i_time = 0

                            output_log.close()

                            break

                else:
                    self.log.trace_in_line(".")
                    sleep(5)

            self.log.trace("... DONE monitoring memory usage for %s process." % process)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="monitor memory usage for %s process" % process)

        # return
        return result