####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from win32api import GetFileVersionInfo, HIWORD, LOWORD
from win32file import CreateFile, SetFileTime
from win32con import GENERIC_WRITE, FILE_SHARE_READ, FILE_SHARE_WRITE, FILE_SHARE_DELETE
from win32con import OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL
from os import remove, stat, utime, path
from os.path import exists, split as path_split
from sys import exc_info
from re import search as re_search, split as re_split
from time import sleep
from wmi import WMI
from shutil import rmtree

####################################################################################################
# Utilities ########################################################################################
####################################################################################################
####################################################################################################

def return_machine_ip_address(log):
    """ Return the IP address for the local machine.
    INPUT
    OUPUT
        successful: whether the function executed successfully or not.
        verified: whether the operation was verified or not.
    """

    log.debug("Returning machine IP address ...")
    result = {'successful': False, 'ip address': None}

    try:
        # define windows management interface object
        i = WMI()

        # build list of addresses associated with local machine (ipconfig)
        addresses = []

        for interface in i.Win32_NetworkAdapterConfiguration(IPEnabled=1):
            for ip_address in interface.IPAddress:
                addresses.append(ip_address)

        # machine ip address should be the first IP address
        result['ip address'] = addresses[0]

        log.trace("Returned machine IP address: %s." % result['ip address'])
        result['successful'] = True
    except BaseException, e:
        log.error("Failed to return machine ip address.")
        for error in e:
            log.error(str(error))
        log.error("Error at %s." % return_execution_error(2)['function'])

    # return
    return result

def write_list_to_file(path,list):
    """ Write a list of strings to file at specified path. """

    file = open(path,'w')
    file.writelines(list)
    file.close()

def read_file_into_list(path):
    """ Read the contents of a file into a list variable. """

    result = {'list':[]}

    file = open(path,'r')
    result['list'] = file.readlines()
    file.close()
    # return
    return result

def convert_time_string_to_aging_int(log, s):
    """ Convert a time string specifying how to age something to an int.
    's' should be a string of the format '5 seconds ago', '1 minute from now', '12 days ago', ect.
    """

    log.trace("Converting time string '%s' to aging int ..." % s)
    result = {'int': None}

    # determine if string is actually a time value already
    try: aging = int(s)
    except BaseException: aging = None

    # determine if time is 'now'
    if str(s).lower().strip() == 'now': aging = 0

    # determine if time is past (contains 'ago'
    elif 'ago' in str(s).lower().strip():
        # split statement from 'ago'
        statement = str(s).lower().split('ago')
        # split remaining statement into numeral and measurement
        statement = str(statement[0]).split(' ')
        numeral = int(statement[0])
        measure = str(statement[1])
        if measure == 'second' or measure == 'seconds':
            aging = -(numeral)
        elif measure == 'minute' or measure == 'minutes':
            aging = -(numeral*60)
        elif measure == 'hour' or measure == 'hours':
            aging = -(numeral*60*60)
        elif measure == 'day' or measure == 'days':
            aging = -(numeral*24*60*60)
        elif measure == 'week' or measure == 'weeks':
            aging = -(numeral*7*24*60*60)
        elif measure == 'month' or measure == 'months':
            aging = -(numeral*30*24*60*60)
        elif measure == 'year' or measure == 'years':
            aging = -(numeral*365*24*60*60)
        else: log.error('Invalid time string including "ago" for conversion given.')
    elif 'ahead' in str(s).lower().strip():
        # split statement from 'from now'
        statement = str(s).lower().split('ahead')
        # split remaining statement into numeral and measurement
        statement = str(statement[0]).split(' ')
        numeral = int(statement[0])
        measure = str(statement[1])
        if measure == 'second' or measure == 'seconds':
            aging = numeral
        elif measure == 'minute' or measure == 'minutes':
            aging = numeral*60
        elif measure == 'hour' or measure == 'hours':
            aging = numeral*60*60
        elif measure == 'day' or measure == 'days':
            aging = numeral*24*60*60
        elif measure == 'week' or measure == 'weeks':
            aging = numeral*7*24*60*60
        elif measure == 'month' or measure == 'months':
            aging = numeral*30*24*60*60
        elif measure == 'year' or measure == 'years':
            aging = numeral*365*24*60*60
        else: log.error('Invalid time string including "ago" for conversion given.')
    else: log.error('Invalid time string for conversion given.')

    # account for DST
    #if DST: time = int(time) - 3600

    # return
    log.trace('Int is %s.' % aging)
    result['int'] = aging
    return result

def change_file_creation_time(log, path, time):
    """ Change the creation time for a file.
    'path' is the full path to the file.
    'time' is the new windows time to set the file creation time to.
    """

    log.trace("Changing creation time for %s to %s ..." % (path, time))
    result = {}

    # open file
    winfile = CreateFile(
        path, GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None, OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL, None)

    # set new creation time
    SetFileTime(winfile, time, None, None)

    # close file
    winfile.close()

    # return
    return result

def change_file_time(log, path, time):
    """ Change the file with given path by the given time.
    'time' should be a string of the format '5 seconds ago', '1 minute from now', '12 days ago', ect.
    """

    log.trace("Changing %s file by to %s ..." % (path, time))
    result = {}

    # convert time string to int
    agingInt = convert_time_string_to_aging_int(log, time)['int']

    # change file times
    try:
        statbuf = stat(path)
        createdTime = float(statbuf.st_ctime) + agingInt
        accessTime = float(statbuf.st_atime) + agingInt
        modifiedTime = float(statbuf.st_mtime) + agingInt
        # creation time
        change_file_creation_time(log, path, createdTime)
        # access and modified times
        utime(path, (accessTime, modifiedTime))
    except WindowsError:
        log.error("Could not find file %s." % path)

    # return
    return result

def verify_file_does_not_exist(log, file_path):
    """ Verify the file at given path does not exist. """

    log.trace("Verifying %s does not exist ..." % file_path)
    result = {'verified': False}

    # check if file exists
    attempts = 5
    attempt = 1
    exists = True
    while exists and attempts <= attempts:
        exists = path.exists(file_path)

        if exists and attempt < attempts:
            log.trace("File found (attempt %s). Re-attempting in 5 seconds ..." % attempt)
            attempt += 1
            sleep(5)
        elif exists and attempt == attempts:
            log.error("Failed to verify file does not exist. File found.")
            result['verified'] = False
            break
        elif not exists:
            log.trace("Verified file does not exist.")
            result['verified'] = True
            break

    # return
    return result

def move_up_windows_path(path, movements=1):
    """ Move the windows path of given 'path' up.
    INPUT
        path: a string representing the windows path.
        movements: an integer stating how many movements to make.
    OUTPUT
        path: the new path.
    """

    result = {'path':''}

    # split path around '\'
    folders = path.split('\\')

    # reconstruct path less folders equal to movements
    for folder in folders[:-int(movements)]:
        result['path'] += folder+"\\"

    # return
    return result

def return_execution_error(debug=None, frame=1):
    """ Return the current function being executed.
    INPUT
        frame: the integer frame in stacktrace to use (e.g., 0 would indicate this function).
    OUTPUT
        function: the function being executed, as well as file name and line being read.
    """

    result = {'error': None}

    # parse info from execution
    exc_type, exc_obj, exc_tb = exc_info()
    fname = path_split(exc_tb.tb_frame.f_code.co_filename)[frame]
    result['error'] = ("%s, %s, %s" %(str(exc_type), str(fname), str(exc_tb.tb_lineno)))

    # return
    return result

def _lock_file_process(file_path, mode='w'):
    try:
        with open(file_path, mode):
            sleep(99999)
    except IOError, e:
        for error in e: print error
        return

def lock_file(log, file_path, mode='w'):
    """ Lock the file at the given file path.
    INPUT
        log: An initialized instance of a logging class to use.
        file_path: the full windows path to the file to be locked.
    OUTPUT
        lock: the thread upon which the file is lock (end thread to unlock).
    """

    log.trace("Locking file %s ..." % file_path)
    result = {'successful': False, 'lock': None}

    try:
        # import threading object
        from threading import Thread

        # verify file exists
        if exists(file_path):

            # define process to thread
            process = _lock_file_process
            args = [file_path, mode]

            thread = Thread(target=process, args=args)
            result['lock'] = thread
            thread.start()

            log.trace("File locked.")
            result['successful'] = True

        else:
            log.error("File does not exist.")
    except BaseException, e:
        log.error("Failed to unlock file file.")
        log.error(str(e))
        log.error("Error at %s." % return_execution_error(2)['function'])

    # return
    return result

def unlock_file(log, locked_file_thread):
    """ Unlock the given file thread for previously locked file.
    INPUT
        log: An initialized instance of a logging class to use.
        locked file thread: a running thread that is currently locking a file.
    """

    log.trace("Unlocking file ...")
    result = {'successful': False}

    try:
        # kill thread
        locked_file_thread._Thread__stop()

        log.trace("File unlocked.")
        result['successful'] = True
    except BaseException, e:
        log.error("Failed to unlock file file.")
        for error in e: log.error(str(error))
        log.error("Error at %s." % return_execution_error(2)['function'])

    # return
    return result

def delete_file(log, file_path, silent_warnings=False):
    """ Delete the file at the given file path.
    INPUT
        log: An initialized instance of a logging class to use.
        file_path: the full windows path to the file to be deleted.
    OUTPUT
        verified: whether the file was deleted and verified or not.
    """

    if not silent_warnings:
        log.trace("Deleting %s ..." % file_path)
    result = {'verified': False}

    try:
        # verify file exists
        if exists(file_path):
            try:
                # delete file
                remove(file_path)

            except BaseException:
                # delete folder
                rmtree(file_path)

            # verify file deleted
            if not exists(file_path):
                log.trace("File deleted.")
                result['verified'] = True
            else:
                if not silent_warnings:
                    log.warn("Failed to delete file at %s. File was not deleted." % file_path)

        else:
            if not silent_warnings:
                log.warn("Failed to delete file at %s. File not found." % file_path)
                result['verified'] = True

    except BaseException, e:
        if not silent_warnings:
            log.error("Failed to delete file at %s." % file_path)
            log.error(str(e))
            log.error("Error at %s." % return_execution_error(2))

    # return
    return result

def return_file_version(log, path):
    """ Return the version of the file with given path.
    INPUT
        log: An initialized instance of a logging class to use.
        path: the windows path to the file.
    OUTPUT
        version: the windows version of the file.
    """

    fileName = path.split('\\')[-1]
    folder = path.replace('%s' % fileName, '')

    log.trace("Returning version of %s in %s ..." % (fileName, folder))
    result = {'version': None}

    # target file
    info = GetFileVersionInfo(path, '\\')

    # define windows version info for file
    majorVersion = HIWORD(info['FileVersionMS'])
    minorVersion = LOWORD(info['FileVersionMS'])
    buildNumber = HIWORD(info['FileVersionLS'])
    revNumber = LOWORD(info['FileVersionLS'])

    # define version
    result['version'] = "%d.%d.%d.%d" % (majorVersion, minorVersion, buildNumber, revNumber)
    log.trace("%s version is %s." % (fileName, str(result['version'])))

    # return
    return result

def translate_list_parameters_to_dict(log, parameters, dict=None, translation=None):
    """ Translate a list of parameter/value list pairs into a dictionary.
    'parameters' should be of the format ['parameter',value].
    'dict' is an optional dict to update and return.
    'translation' is an optional dict to translate parameter names into valid
        field names (i.e., database or server field names). """

    result = {'dict':dict}

    # if no dict given, declare an empty one
    if result['dict'] is None:
        result['dict'] = {}
        # translate each parameter
    for param in parameters:
        # if translation dict given, translate the key
        if translation is not None:
            param[0] = translation[param[0].lower()]
            # update dict with key [0] and value [1]
        result['dict'][param[0]] = param[1]
        # return
    return result


def translate_dict_to_list_parameters(log, dict, parameters=None, translation=None):
    """ Translate a dictionary into a list of parameter/value list pairs.
    'dict' is the dictionary of values.
    'parameters' is an optional list of parameter/value list pairs to update and return.
    'translation' is an optional dict to translate key names into valid
        field names (i.e., database or server field names). """

    result = {'parameters':parameters}

    # if no parameters given, declare an empty one
    if result['parameters'] is None:
        result['parameters'] = []
        # pull keys and values from dict
    fields = dict.keys()
    values = dict.values()
    # if translation dict given, translate the fields
    if translation is not None:
        for field in fields:
            try:
                fields[fields.index(field)] = translation[field.lower()]
            except Exception, e:
                log.error(str(e))
                log.error("Failed to translate %s field using translator."%field)
        # pair fields and values into parameters
    parameters = []
    for field in fields:
        parameters.append([field,values[fields.index(field)]])
        # remove any invalid parameters (no mapping)
    for parameter in parameters:
        if parameter[0] is not None:
            result['parameters'].append(parameter)
        # return
    return result

def checksum(sentence):
    """ Calculate the checksum for a sentence (e.g. NMEA string). """

    result = {'checksum':None}
    # Remove any newlines
    if re_search("\n$", sentence):
        sentence = sentence[:-1]

    nmeadata,cksum = re_split('\*', sentence)

    calc_cksum = 0
    for s in nmeadata:
        calc_cksum ^= ord(s)

    # Return the nmeadata, the checksum from sentence, and the calculated checksum
    result['checksum'] = hex(calc_cksum)[2:].upper()
    return result