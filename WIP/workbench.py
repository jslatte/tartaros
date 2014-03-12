###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from logger import Logger
from Database import Database
from Hestia import Hestia
from Ixion import Ixion
from Minos import Minos
from Orpheus import Orpheus
from Sisyphus import Sisyphus
from Tantalus import Tantalus
#from Danaides import Danaides
from testcase import HestiaTestCase
from testrun import TestRun
from mapping import TARTAROS, HESTIA
from os import getcwdu
from time import sleep
from utc import UTC
from random import randint

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

# logger instance
log = Logger(logging_level='trace')
# database
database = Database(log)
# utilities
#utc = UTC(log)
# modules
#ixion = Ixion(log)
#minos = Minos(log)
orpheus = Orpheus(log)
#sisyphus = Sisyphus(log)
#tantalus = Tantalus(log, Sisyphus, num_sites=1)
#danaides = Danaides(log, database)
hestia = Hestia(log, database)

####################################################################################################
# Functions ########################################################################################
####################################################################################################
####################################################################################################

def configure_license(license):
    version = hestia.return_vim_server_version()['version']
    hestia.determine_vim_server_release_version(version)
    hestia.log_in_to_vim()
    hestia.configure_vim_license(license)

def activate_all_sites(num_sites):
    for i in range(1, num_sites+1):
        hestia.activate_site(i)

def connect_to_database():
    hestia.db.connect_to_database()
    hestia.db.db_handle = hestia.db.create_database_handle()['handle']

def log_in():
    version = hestia.return_vim_server_version()['version']
    hestia.determine_vim_server_release_version(version)
    hestia.log_in_to_vim()

def reset_db_for_simulation():
    hestia.db.connect_to_database()
    hestia.db.db_handle = hestia.db.create_database_handle()['handle']
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM GPRMC")
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM LastGPRMCofSite")
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM LastGPSRequestForDisk")
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM DvrHistory")
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM DriveHistory")
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM ConnectionLog")
    hestia.db.execute_SQL(hestia.db.db_handle, "DELETE FROM SystemLog")
    hestia.db.execute_SQL(hestia.db.db_handle, "UPDATE MDVRs SET DvrSN = NULL")
    hestia.db.execute_SQL(hestia.db.db_handle, "UPDATE MDVRs SET FirmwareVersion = ''")
    hestia.db.execute_SQL(hestia.db.db_handle, "UPDATE HardDisks SET DiskSN = NULL")

def setup_test_server_with_simulation_sites(num_sites):
    hestia.reset_vim_server()
    connect_to_database()
    log_in()
    hestia.setup_server_for_manual_testing('full')
    num_sites = num_sites
    hestia.add_number_of_fake_sites(num_sites)
    hestia.update_all_sites_to_local_machine_sites()
    hestia.stop_vim_server()
    #hestia.start_vim_server('process')

def add_simulation_sites(num_sites, start_id=1, start_ip=1, ip_schema="172.22.60."):
    connect_to_database()
    log_in()
    hestia.add_number_of_fake_sites(num_sites, start_id=start_id, start_ip=start_ip,
                                    ip_schema=ip_schema)

def convert_binary_data():

    raw = [
        '0a10000000148c8c19060000000100000030313030',
        '283614008e070000148c8c191d00000001000000303230334791566301000000000000000000000000000000000000000000360000000100aa000000400000000100680000004a0000000107580000000400000006000000020c0000000006000000000322078fc502067600000004000000000000000300000000008000000001078e0000000400000009000000020c00000000120000000820501f23270000b41f00002a0200000000020000000000b40000008003bf00000001000000010107cd00000004000000020000000207db0000000400000001000000030005010000e50000000107f30000000400000002000000020c0000000008000000c0d40100c1d4010004071301000004000000dc00000005003a0100001d010000010529010000020000000700020c00000000070000004e4152553830300a005d01000044010000010550010000020000000300020c0000000003000000312e310b008201000067010000010573010000020000000500020c0000000005000000312e352e310c00a90100008c010000010598010000020000000700020c00000000070000004e525531313038280063020000b30100000101be01000001000000010201c901000001000000010301d401000001000000010401df01000001000000010501ea01000001000000010601f50100000100000001070100020000010000000108010b020000010000000109011602000001000000000a012102000001000000000b012c02000001000000010c013702000001000000000d014202000001000000000e014d02000001000000000f0358020000010000000010030000000001000000002900780200006d02000001030000000001000000003c00a30200008202000001018d0200000100000001020198020000010000000003030000000001000000003d00ef020000ad0200000103b802000001000000080203c302000001000000020303ce02000001000000010403d902000001000000080503e4020000010000000206030000000001000000083e0049030000f9020000010304030000010000000602030f030000010000000a03031a03000001000000020403250300000100000000050330030000010000000106033b030000010000000107070000000004000000df3f46003f005e03000053030000010100000000010000000140007e03000068030000010173030000010000000102030000000001000000044100e003000088030000010193030000010000000002019e03000001000000000301a903000001000000000403b403000001000000010501bf03000001000000000601ca03000001000000000703d50300000100000000080300000000010000000042000b040000ea0300000101f50300000100000000020100040000010000000003010000000001000000004300d004000015040000010320040000010000000202032b04000001000000000303360400000100000002040141040000010000000005014c040000010000000106015704000001000000010700c50400006104000001076f0400000400000013000000020c000000004c000000cb0000000100000002000000801a0600030000002c010000a286010064000000400d0300410d0300430d0300450d0300e1930400e293040064ab9041e3930400c900000065ab9041ca000000080300000000010000000044003d050000da0400000103e504000001000000020201f004000001000000010301fb04000001000000010401060500000100000001050111050000010000000106011c05000001000000010701270500000100000001080132050000010000000009010000000001000000004500520500004705000001030000000001000000024600150600005c05000001000a060000660500000107740500000400000023000000020c000000008c00000001000000020000000300000004000000801a0600811a0600e0930400e1930400e2930400e3930400e4930400e5930400e6930400e7930400400d0300410d0300420d0300430d0300440d03002c010000450d03002d010000480d0300c9000000a0860100ca000000a1860100a2860100cb000000a3860100cc00000064ab904165ab9041640000006500000002030000000001000000004700570600001f0600000100000000002906000001073706000004000000010000000200000000004106000001034c0600000100000004030100000000010000000048008e060000610600000100000000006b0600000107790600000400000001000000020000000000830600000103000000000100000007490056070000980600000101a306000001000000010203ae06000001000000020301b906000001000000010401c406000001000000010501cf06000001000000000601da06000001000000000703e506000001000000000803f00600000100000000090013070000fa0600000107080700000400000001000000020c0000000001000000020a011e07000001000000010b032907000001000000000c033407000001000000010d033f07000001000000000e054b0700000200000000000f030000000001000000054a00810700006007000001036b0700000100000002020176070000010000000003010000000001000000004b00000000008b0700000103000000000100000002',
        ]

    for datum in raw:
        # convert from hex back to binary data
        bin_data = binascii.unhexlify(datum)
        log.info('BINARY:\t%s' % bin_data.replace('1.5.1', ))
        # convert binary data into ascii data
        #ascii_data = binascii.b2a_base64(bin_data)
        #log.info('ASCII B64:\t%s' % ascii_data)
        #ascii_data = binascii.b2a_qp(bin_data)
        #log.info('ASCII QP:\t%s' % ascii_data)
        #ascii_data = binascii.b2a_uu(bin_data)
        #log.info('ASCII UU:\t%s' % ascii_data)
        #ascii_s = binascii.b2a_hqx(datum)
        #log.info('ASCII S:\t%s' % ascii_s)
        #decoded_s = datum.decode("hex")
        #log.info('Decoded HEX:\t%s' % decoded_s)

def translate_hex(hex):
    import binascii
    for s in hex:
        try: log.trace("Hexidecimal:\t\t\t%s" % s)
        except BaseException, e: log.trace(e)
        try: log.trace("Char Length:\t\t\t%s" % len(s))
        except BaseException, e: log.trace(e)
        try: log.trace("ASCII:\t\t\t\t\t%s" % binascii.unhexlify(s))
        except BaseException, e: log.trace(e)
        try: log.trace("Decimal:\t\t\t\t%d" % int(s, 16))
        except BaseException, e: log.trace(e)
        try:
            j = ''
            for i in range(1, ((len(s) / 2) + 1)):
                j += str(int(s[(i * 2 - 2):(i * 2)], 16)) + ' '
            log.trace("Decimal Bytes:\t\t\t%s" % j)
        except BaseException, e: log.trace(e)
        try:
            n = s[-2:]
            if len(s) >= 4:
                for m in range(2, ((len(s) / 2) + 1)):
                    n += s[-(m * 2):-(m * 2 - 2)]
            log.trace("Reverse Decimal Bytes:\t%d" % int(n, 16))
        except BaseException, e: log.trace(e)

def translate_gps_to_hex():
    import binascii
    from utility import checksum
    nmea = 'GPRMC,080000,A,4800.97,N,12166.03,W,32.1,045.0,160813,,*'
    s = '$' + nmea + checksum(nmea)['checksum']
    log.trace(s)
    log.trace(binascii.hexlify(s))

def parse_danaides_output(path):

    f = open(path, 'r')
    f_data = f.readlines()

    c_data = []
    for line in f_data:
        if "net change in memory usage" in line.lower():
            # determine elapsed time
            timestamp = line.split('(')[1].split(')')[0].replace('after', '').strip()
            if 'day' in timestamp.lower():
                days = timestamp.split('day')[0].strip()
                timestamp = days + ':' + timestamp.split(',')[1].strip()
            else:
                timestamp = '0:' + timestamp

            # determine memory usage
            mem_usage = line.split('\t')[1].split('MB')[0].strip() + ' MB'

            # append to data
            c_data.append(timestamp + ':\t' + mem_usage)

    r_data = []
    previous_min = 0
    prev_mem_usage = float(0)
    min_interval = 5
    min_mem_usage = 0.008192
    counter = 0
    line_data = {
        'elapsed time':                 '00:00:00',
        'total memory usage':           0,
        'minutes since last action':    0,
        'memory allocation':            [],
    }
    for line in c_data:
        # determine total time in mins
        times = line.split(':')
        days = int(times[0])
        hours = int(times[1])
        minutes = int(times[2])
        seconds = float(times[3])
        tot_min = (((days * 24) + hours) * 60) + minutes
        min_dif = tot_min - previous_min

        # determine memory usage
        tot_mem_usage = float(line.split('\t')[1].replace('MB', '').strip())
        mem_usage = tot_mem_usage - prev_mem_usage

        if min_dif > min_interval:
            # set counter to track next 4 messages
            counter = 5
            r_data.append(line_data)

            # clear previous line data set
            line_data = {
                'elapsed time':                 '00:00:00',
                'total memory usage':           0,
                'minutes since last action':    0,
                'memory allocation':            [0],
            }

        # track only changes greater than minute interval (or if counter active)
        if min_dif > min_interval or counter > 0:
            line_data['memory allocation'].append(mem_usage)

        if min_dif > min_interval:
            line_data['minutes since last action'] = min_dif
            line_data['elapsed time'] = '%d:%d:%d:%d' % (days, hours, minutes, seconds)
            line_data['total memory usage'] = tot_mem_usage

        if counter > 0:
            counter -= 1

        # update previous minutes
        previous_min = tot_min
        prev_mem_usage = tot_mem_usage

        # handle last message
        if (len(c_data) - 1) == c_data.index(line):
            r_data.append(line_data)
            counter = 0

    f2 = open(path + '.dat', 'w')
    f2.write('ELAPSED TIME | MINUTES SINCE LAST CONNECTION | ADMIN CONNECT (Y/N)? | SEARCH CONNECT (Y/N)? | '
             'TOTAL MEMORY | MEMORY ALLOCATIONS')
    for line in r_data[1:]:
        # determine if admin and/or search (probably) connected
        line['admin connect'] = 'N'
        line['search connect'] = 'N'
        for mem_alloc in line['memory allocation']:
            if mem_alloc > 0.008192:
                line['admin connect'] = 'Y'
            if mem_alloc > 0.065536:
                line['search connect'] = 'Y'

        line['memory allocation'] = str(line['memory allocation'])
        msg = '\n%(elapsed time)s' \
              '\t\t%(minutes since last action)s' \
              '\t\t\t\t\t\t\t\t%(admin connect)s' \
              '\t\t\t\t\t\t%(search connect)s' \
              '\t\t\t\t\t%(total memory usage)f' \
              '\t\t%(memory allocation)s' % line

        f2.write(msg)

def parse_vim_logs_for_connection_data(self, logs_folder_path, start_time=None, end_time=None):
    """ Parse the ViM logs for connection data.
    INPUT
        logs folder path: file path to the folder containing all log files.
        start time: optional time to start tracking connection data.
        end time: optional time to stop tracking connection data.
    OUPUT
        successful: whether the function executed successfully or not.
        connection data: connection data returned.
    """

    self.log.debug("Parsing ViM logs for connection data ...")
    result = {'successful': False, 'connection data': None}

    try:
        # make a list of all production log files
        log.debug("Building lists of all log files ...")

        from os import listdir
        log_file_path = logs_folder_path
        log_files = listdir(log_file_path)
        log.trace("Production Log Files:\t")
        for i in range(0, len(log_files)): log.trace("\t%s" % log_files[i])

        log.debug("... DONE building lists of all log files.")

        # construct amalgamated list from log files
        log.debug("Compiling amalgamated lists from log files ...")

        logs = []
        for log_file in log_files:
            i_log = []
            f = open(log_file_path + "\\" + log_file, 'r')
            for line in f:
                if line.strip() != '':
                    i_log.append(line)
            logs.append(i_log)

        log.debug("... DONE compiling amalgamated lists from log files.")

        # determine connection per site statistics
        log.debug("Determining connections per site statistics ...")

        # determine start/end timestamps for diagnostics
        if start_time is not None:
            start_timestamp = utc.convert_date_string_to_db_time(start_time)['db time']
        else:
            start_timestamp = 0

        if end_time is not None:
            end_timestamp = utc.convert_date_string_to_db_time(end_time)['db time']
        else:
            end_timestamp = utc.convert_string_to_time('now')

        connection_data = {}
        for log_file in logs:
            # determine time range
            start = log_file[0].split(',')[0]
            end = log_file[-1].split(',')[0]

            log.trace("Start Time:\t%s" % start)
            log.trace("End Time:\t%s" % end)

            # build connection data per site
            for line in log_file:

                if 'connect' in line.lower():
                    site_name = ''
                    site_exists = False
                    # get site id
                    if 'channel:' in line.lower():
                        site_data = line.split('channel:')[1].strip()

                        if len(site_data.split(' ')) > 3:
                            for s in site_data.split(' ')[1:]:
                                if '(' in s:
                                    break
                                else:
                                    site_name += s + ' '

                            site_name.replace(' ', '')
                        else:
                            site_name = site_data.split(' ')[1].replace(' ', '')

                    elif ' connected ' in line.lower():
                        site_data = line.split(' connected ')[1].strip()
                        site_name = site_data.split('(')[0].strip()

                    elif 'disconnected from' in line.lower():
                        site_data = line.split('disconnected from')[1].strip()
                        site_name = site_data.split('(')[0].strip()

                    else:
                        pass

                    if site_name != '':
                        # add site to list
                        for name in connection_data.keys():
                            if name.lower() in site_name.lower():
                                site_exists = True
                                existing_site_name = name

                        if site_exists:
                            site_name = existing_site_name
                        else:
                            connection_data[site_name] = {
                                'name': site_name,
                                'attempted admin port connections': [],
                                'attempted search port connections': [],
                                'times between admin port connections': [],
                                'times between search port connections': [],
                                'long re-connect periods': [],
                            }

                        # get timestamp in db time
                        date_string = line.split(',')[0].strip()
                        timestamp = utc.convert_date_string_to_db_time(date_string,
                                                                       vim_log=True)['db time']

                        if start_timestamp <= timestamp <= end_timestamp:

                            # determine port connecting to
                            if '> - admin connect' in line.lower()\
                                or ('admin disconnected from' in line.lower()
                                    and ('reason: 13' or 'reason: 2') in line.lower()):
                                connection_data[site_name]['attempted admin port connections'].append(
                                    [timestamp, date_string]
                                )
                            if '> - search connect' in line.lower()\
                                or ('search disconnected from' in line.lower()
                                    and ('reason: 13' or 'reason: 2') in line.lower()):
                                connection_data[site_name]['attempted search port connections'].append(
                                    [timestamp, date_string]
                                )

        # build list of time between connections for each site
        self.log.trace("Building list of time between connections for each site ...")
        for entry in connection_data:
            site = connection_data[entry]

            for port in ['admin', 'search']:

                c_timestamp = None
                for timestamp in site['attempted %s port connections' % port]:

                    # determine time between connections only if current (previous) timestamp set
                    if c_timestamp is not None:
                        time_between_connections = int(timestamp[0]) - c_timestamp
                        site['times between %s port connections' % port].append({
                            'time between connections': time_between_connections,
                            'previous connection time': c_timestamp,
                            're-connect time': timestamp[0]})

                    # update current timestamp
                    c_timestamp = timestamp[0]

                # determine total number of connections made per site
                site['total number of attempted %s port connections' % port] \
                    = len(site['attempted %s port connections' % port])

                # determine any long re-connect periods for each site
                for connection_entry in site['times between %s port connections' % port]:
                    if connection_entry['time between connections'] > self.vim_connection_lapse_max:
                        site['long re-connect periods'].append({
                            'port': port,
                            'previous connection time': connection_entry['previous connection time'],
                            're-connection time': connection_entry['re-connect time'],
                            'time between connections': connection_entry['time between connections'],
                        })

        self.log.trace("... DONE building list of time between connections for each site.")
        #self.log.trace("Times between Connections for %s:\t%s"
        #               % (site['name'], site['times between connections']))

        self.log.debug("... DONE parsing ViM logs for connection data.")
        result['successful'] = True
        result['connection data'] = connection_data
    except BaseException, e:
        self.handle_exception(e, operation="parse ViM logs for connection data")
    return result

def perform_vim_connections_post_mortem():
    from os import getcwdu
    OUTPUT_FOLDER_PATH = getcwdu() + '\\Modules\\Danaides\\output'

    amalgamated_data = {
        'number of sites': 0,
        'number of sites that hung': 0,
        'sites that did not connect': [],
        'number of sites that did not connect': 0,
        'total run time (hrs)': 0,
        'hang times': [],
        'hangs per time slot': [],
    }

    diagnostics = danaides.perform_post_mortem_vim_connection_diagnostic()['diagnostics']

    amalgamated_data['number of sites'] = len(diagnostics)

    for entry in diagnostics:
        site = diagnostics[entry]
        hangs = []

        log.info("Site %s:" % site['name'])
        log.debug("Number of Connections:\t%d" % site['total number of connections'])
        log.debug("Connection Frequency:\t%d" % site['connection frequency'])
        log.debug("Connection Lapses (> %ss):\t%d" % (danaides.vim_connection_lapse_max,
                                                     len(site['long re-connect periods'])))

        if site['total number of connections'] == 0:
            amalgamated_data['sites that did not connect'].append(site['name'])
            amalgamated_data['number of sites that did not connect'] += 1

        if len(site['long re-connect periods']) > 0:
            amalgamated_data['number of sites that hung'] += 1

        for period in site['long re-connect periods']:
            hangs.append("%s (for %ss) -- %d"
                         % (utc.convert_database_time_to_server_date(period['previous connection time']),
                            period['time between connections'],
                            period['previous connection time']))
            amalgamated_data['hang times'].append({'time': period['previous connection time'],
                                                   'elapsed time': period['time between connections']})

        for hang in hangs:
            log.trace(hang)

    log.trace("Start Time:\t%d" % danaides.vim_connection_diagnostic_start_time)
    log.trace("End Time:\t%d" % danaides.vim_connection_diagnostic_end_time)

    hour = 0
    step = 3600
    for i in range(danaides.vim_connection_diagnostic_start_time,
                   danaides.vim_connection_diagnostic_end_time, step):

        start_time = i
        end_time = i + step if (i + step) < danaides.vim_connection_diagnostic_end_time \
            else danaides.vim_connection_diagnostic_end_time

        hangs_per_slot = 0
        average_elapsed_time = 0
        total_elapsed_times = 0
        for hang_time in amalgamated_data['hang times']:
            if hang_time['time'] >= start_time and hang_time['time'] < end_time:
                hangs_per_slot += 1
                total_elapsed_times += hang_time['elapsed time']

        if total_elapsed_times > 0:
            average_elapsed_time = total_elapsed_times/hangs_per_slot

        amalgamated_data['hangs per time slot'].append({'time slot': hour + 1, 'hangs': hangs_per_slot,
                                                        'average elapsed time': average_elapsed_time})

        hour += 1

    amalgamated_data['total run time (hrs)'] = hour

    log.info("Amalgamated Data:")
    log.debug("Sites:")
    log.trace("Total:\t%d" % amalgamated_data['number of sites'])
    log.trace("Amount that Possibly Hung:\t%d" % amalgamated_data['number of sites that hung'])
    log.trace("Amount that Did Not Connect:\t%d" % amalgamated_data['number of sites that did not connect'])
    log.debug("Sites that Did Not Connect:")
    for site in amalgamated_data['sites that did not connect']:
        log.trace("Site %s" % site)
    log.debug("Total Run Time:\t%d hrs" % amalgamated_data['total run time (hrs)'])
    log.debug("Possible Hang Starts Per Hour:")
    for hang in amalgamated_data['hangs per time slot']:
        log.trace("Hour %d:\t%d (%ds average elapsed time" %(hang['time slot'], hang['hangs'],
                                                             hang['average elapsed time']))

def parse_vim_logs_for_total_connections(self, log_folder_path, start, end):

    folder_path = log_folder_path
    connection_data = parse_vim_logs_for_connection_data(danaides, folder_path,
                                                         start_time=start,
                                                         end_time=end)['connection data']

    filename = "%s_%s_to_%s" % (folder_path.split('\\')[-3], start.replace(' ', '_').replace(':','.'),
                                end.replace(' ', '_').replace(':','.'))
    filepath = getcwdu() + "\\Modules\\Danaides\\output\\%s.txt" % filename
    f = open(filepath, 'w')

    f.write("\nSite\t# of Attempted Admin Connections\t# of Attempted Search Connections"
            "\t# of Connection Lapses\tNotes")

    for entry in connection_data:
        site = connection_data[entry]

        lapses = ''
        for lapse in site['long re-connect periods']:
            if lapses != '': lapses += ', '
            lapses += "From %s to %s (%ds)" \
                      % (utc.convert_database_time_to_server_date(int(lapse['previous connection time'])),
                         utc.convert_database_time_to_server_date(int(lapse['re-connection time'])),
                         lapse['time between connections'])

        f.write("\n%(site name)s\t%(admin connections)d\t%(search connections)d\t%(lapses)d\t%(notes)s"
                % {
            'site name': site['name'],
            'admin connections': len(site['attempted admin port connections']),
            'search connections': len(site['attempted search port connections']),
            'lapses': len(site['long re-connect periods']),
            'notes': lapses,
        })

    f.close()

def determine_number_of_failed_connections_over_time(self, folder_path, start, end):

    # determine connection attempts on each port from log files
    logs_path = folder_path + "logs\\"
    connection_attempts = parse_vim_logs_for_connection_data(danaides, logs_path,
                                                         start_time=start,
                                                         end_time=end)['connection data']

    # convert start/end times to database times
    start_time = utc.convert_date_string_to_db_time(start)['db time']
    end_time = utc.convert_date_string_to_db_time(end)['db time']

    # determine successful connections from database
    successful_connections = self.compile_vim_connection_diagnostics(start_time=start_time,
                                                                     end_time=end_time,
                                                                     dir=folder_path)['diagnostics']

    # open output file for writing parsed data to
    filename = "%s_%s_to_%s" % (folder_path.split('\\')[-2], start.replace(' ', '_').replace(':','.'),
                                end.replace(' ', '_').replace(':','.'))
    filepath = getcwdu() + "\\Modules\\Danaides\\output\\%s.txt" % filename
    f = open(filepath, 'w')

    # write header and 0-datapoint data
    f.write("Time"
            "\t# of Sites that Did Not Attempt Admin Connections"
            "\t# of Sites that Did Not Attempt Search Connections"
            "\tSites that Did Not Attempt Connections"
            "\t# of Sites that Did Not Connect"
            "\tSites that Did Not Connect"
    )
    f.write("\n0\t0\t0\t\t0\t")

    # determine number of failed connections over time
    time_slot = 1
    step = self.vim_connection_lapse_max
    c_previous = start_time
    for i in range(start_time + step, end_time, step):

        num_sites_not_attempting_connections = {
            'admin': 0,
            'search': 0,
            'sites': '',
        }
        num_sites_not_connected = 0
        sites_not_connected = ''

        # determine number of sites that did not attempt connections on each port
        for entry in connection_attempts:
            site = connection_attempts[entry]

            for port in ['admin', 'search']:
                site_connected = False

                for timestamp in site['attempted %s port connections' % port]:
                    if c_previous <= timestamp[0] < i:
                        site_connected = True

                if not site_connected:
                    num_sites_not_attempting_connections['%s' % port] += 1

                    if num_sites_not_attempting_connections['sites'] == '':
                        num_sites_not_attempting_connections['sites'] += site['name']
                    else:
                        num_sites_not_attempting_connections['sites'] += ', %s' % site['name']

        # determine number of sites that did not make a successful connection
        for entry in successful_connections:
            site = successful_connections[entry]

            site_connected = False

            for timestamp in site['timestamps']:
                if c_previous <= timestamp < i:
                    site_connected = True

            if not site_connected:
                num_sites_not_connected += 1

                if sites_not_connected == '':
                    sites_not_connected += site['name']
                else:
                    sites_not_connected += ', %s' % site['name']


        f.write("\n%(time)f\t%(admin connections)d\t%(search connections)d\t%(sites not attempted)s"
                "\t%(site connections)d\t%(sites not connected)s"
                % {
            'time': float(time_slot) / 4,
            'admin connections': num_sites_not_attempting_connections['admin'],
            'search connections': num_sites_not_attempting_connections['search'],
            'sites not attempted': num_sites_not_attempting_connections['sites'],
            'site connections': num_sites_not_connected,
            'sites not connected': sites_not_connected,
        })

        # update counters
        c_previous = i
        time_slot += 1

    f.close()

def run_dvr_simulation_test():
    reset_db_for_simulation()
    tantalus.run_in_dvr_response_simulation_mode()

def sync_modules_to_testrail(submodule_id=2):
    # return all modules from the database for given submodule (raw data)
    log.trace("Returning all modules for submodule %s ..." % submodule_id)
    db_module_dat = database.query_database_table(database.db_handle, "modules",
                                    addendum="WHERE submodule_id = '%s'" % submodule_id)['response']

    # determine project id for submodule
    log.trace("Determining project id for submodule %s ..." % submodule_id)
    project_id = 1

    # retrieve all modules for submodule project from TestRail
    log.trace("Retrieving all modules for submodule %s from TestRail ..." % submodule_id)
    tr_module_dat = orpheus.api_client.send_get('get_suites/%s' % project_id)

    # determine results id (suite id) for each module in submodule
    log.trace("Determining results id for each module ...")
    for db_module in db_module_dat:
        db_module_id = db_module[0]
        db_module_name = db_module[1]
        # check for module in those returned from TestRail
        log.trace("Checking for %s module ..." % db_module_name)
        updated = False
        for tr_module in tr_module_dat:
            if db_module_name.lower() in tr_module['name'].lower():
                log.trace("Module %s found. Updating ..." % db_module_name)
                database.update_entry_in_table(database.db_handle, "modules", db_module_id,
                    {'results_id': tr_module['id']})
                updated = True
        # report
        if updated:
            log.trace("Module %s synchronized with TestRail." % db_module_name)
        else:
            log.warn("Failed to synchronize module %s with TestRail." % db_module_name)

def sync_stories_to_testrail():
    # return all stories from the database
    log.trace("Returning all user stories ...")
    db_story_dat = database.query_database_table(database.db_handle, "user_stories")['response']

    # pre-fetch all sections for each suite from TestRail
    project_id = 1
    log.trace("Fetching all section data for each suite in TestRail for project %s ..." % project_id)
    db_module_dat = database.query_database_table(database.db_handle, "modules")['response']
    modules_with_suites = []
    for db_module in db_module_dat:
        # build list of modules with suites
        db_module_id = db_module[0]
        db_module_results_id = db_module[3]
        if db_module_results_id is not None:
            modules_with_suites.append([db_module_id, db_module_results_id])
    # build module to suite sections map
    module_to_suite_sections = {}
    for module in modules_with_suites:
        # retrieve all sections for suite (module) from TestRail
        suite_sections = orpheus.api_client.send_get(
            'get_sections/%(project id)s&suite_id=%(suite id)s'
            % {'project id': project_id, 'suite id': module[1]})
        # add mapping item for module to suite sections
        module_to_suite_sections['%s' % module[0]] = suite_sections

    # determine results id (section id) for each user story
    log.trace("Determining results id for each user story ...")
    for db_story in db_story_dat[1:]:
        db_story_id = db_story[0]
        db_story_name = db_story[3]
        db_story_module_id = db_story[2]

        # determine project id for submodule
        log.trace("Determining project id for story '%s' ..." % db_story_name)
        project_id = 1

        # determine suite (module) for user story
        log.trace("Determining suite id for story '%s' ..." % db_story_name)
        suite_id = database.query_database_table_for_single_value(database.db_handle, "modules",
                                                                  "results_id", "id",
                                                                  db_story_module_id)['value']
        log.trace("Suite ID for story '%s': %s." % (db_story_name, suite_id))

        # retrieve all sections for suite (module) from TestRail
        log.trace("Retrieving all sections for module %s ..." % db_story_module_id)
        tr_story_dat = module_to_suite_sections[str(db_story_module_id)]

        # determine section id for user story
        log.trace("Checking for '%s' story ..." % db_story_name)
        updated = False
        for tr_story in tr_story_dat:
            if db_story_name.lower() in tr_story['name'].lower():
                log.trace("Story '%s' found. Updating ..." % db_story_name)
                database.update_entry_in_table(database.db_handle, "user_stories", db_story_id,
                    {'results_id': tr_story['id']})
                updated = True
        # report
        if updated:
            log.trace("Story '%s' synchronized with TestRail." % db_story_name)
        else:
            log.warn("Failed to synchronize story '%s' with TestRail." % db_story_name)

def sync_testcases_to_testrail():
    # return all testcases from the database
    log.trace("Returning all test cases ...")
    db_cases_dat = database.query_database_table(database.db_handle, "test_cases")['response']

    # update story-level cases
    log.trace("Updating story-level classes ...")
    for db_case_dat in db_cases_dat:
        case_id = int(db_case_dat[0])
        case_level = int(db_case_dat[5])
        updated = False

        if case_level == 2:
            # return story data for test case
            data = database.return_testcase_data(case_id)
            db_test_dat = data['test data']
            db_story_dat = data['user story data']
            # update test case with story results id
            parent_id = db_story_dat['id']
            results_id = db_test_dat['results id']
            log.trace("Updating story-level test case %s ..." % case_id)
            database.update_entry_in_table(database.db_handle, "test_cases", case_id,
                                           {'results_id': results_id, 'parent_id': parent_id})
            updated = True

            # report
            if updated:
                log.trace("Test Case '%s' synchronized with TestRail." % case_id)
            else:
                log.warn("Failed to synchronize test case '%s' with TestRail." % case_id)

def convert_test_to_section_with_testcases_in_testrail(test_id):
    # determine parent section id (story results id in database)
    log.trace("Determining parent section id ...")
    story_id = int(database.query_database_table_for_single_value(database.db_handle, "tests",
                                                                  "user_story_id", "id",
                                                                  test_id)['value'])
    p_sect_id = int(database.query_database_table_for_single_value(database.db_handle, "user_stories",
                                                                   "results_id", "id",
                                                                   story_id)['value'])
    log.trace("Parent Section ID:\t%d." % p_sect_id)

    # determine suite id of parent section
    log.trace("Determining suite id of parent section ...")
    module_id = int(database.query_database_table_for_single_value(database.db_handle, "user_stories",
                                                                   "module_id", "id",
                                                                   story_id)['value'])
    suite_id = int(database.query_database_table_for_single_value(database.db_handle, "modules",
                                                                  "results_id", "id",
                                                                  module_id)['value'])
    log.trace("Suite ID:\t%d" % suite_id)

    # determine project id of parent section (hard-coded for now)
    log.trace("Determining project id ...")
    project_id = 1

    # determine active test cases for test
    log.trace("Determining test cases for test ...")
    testcases = database.return_testcases_for_test(test_id, story_id)['testcases']
    log.trace("Test Cases:")
    for testcase in testcases:
        log.trace("\t%s" % str(testcase['name']))

    # add section to parent (user story) for test
    log.trace("Adding section to parent for test ...")
    test_name = database.query_database_table_for_single_value(database.db_handle, "tests",
                                                               "name", "id", test_id)['value']
    # give unique test name (to avoid issues when attempting to return correct sect id)
    test_name_q = test_name + ' %s' % str(test_id)
    sect_id = orpheus.add_section(test_name_q, suite_id, project_id, parent_id=p_sect_id)['id']

    # return sect name to normal
    orpheus.update_section(sect_id, suite_id, project_id, name=test_name)

    # update test results id
    database.update_table_field_for_entry(database.db_handle, "tests", "results_id", sect_id,
                                          "id", test_id)

    # add test case for each case included in test
    for testcase in testcases:
        case_results_id = orpheus.push_new_case_to_testrail(testcase['id'])['id']

        # update test case results id with new results id
        database.update_table_field_for_entry(
            database.db_handle, "test_cases", "results_id", case_results_id, "id", testcase['id'])

#hestia.check_for_hyphenated_drive_entry()

####################################################################################################
# Workbench ########################################################################################
####################################################################################################
####################################################################################################

#hestia.reset_vim_server()
#connect_to_database()
#hestia.start_vim_server()
log_in()
#hestia.setup_server_for_manual_testing('full')
#configure_license('health')
#hestia.configure_vim_license('streaming server')

#testcase = HestiaTestCase(log, database, 442, debugging=False)
#testcase.run()

#hestia.configure_all_lab_depot_sites()

#hestia.add_number_of_fake_sites(1, start_id=1, ip_schema="172.22.80.", start_ip=1)

#run_dvr_simulation_test()

#tantalus.build_gps_event_data_packet(2)

#perform_vim_connections_post_mortem()

#start = "2013-11-1 00:00:00"
#end = "2013-11-4 23:59:59"
#path = "C:\\Program Files (x86)\\ViM\\log parsing\\Whatcom\\WhatcomTest\\"
#parse_vim_logs_for_total_connections(danaides, path, start, end)
#determine_number_of_failed_connections_over_time(danaides, path, start, end)

#log.trace("SELECT * FROM ConnectionLog WHERE csTimeStamp > %d and csTimeStamp < %d" %(utc.convert_date_string_to_db_time(start)['db time'], utc.convert_date_string_to_db_time(end)['db time']))

#log.trace(orpheus.return_section_data("The server will run as a service", 1, 1))

hestia.configure_lab_depot_site_for_test('mrh8 site', settings=[['dvr model', 'mrh16']])