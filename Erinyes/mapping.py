####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

from collections import OrderedDict
from os import getcwdu

####################################################################################################
# Mapping ##########################################################################################
####################################################################################################
####################################################################################################

ERINYES_DB_PATH = getcwdu() + "\\Erinyes\\erinyes.sqlite"
ERINYES_LOGGING_PATH = getcwdu() +"\\Erinyes\\logs"

ERINYES = {
    'database': {
        'tables': {
            'dvrs':                 'dvrs',
            'sites':                'sites',
            'connection log':       'connection_log',
            'connection statuses':  'connection_statuses',
            'connection types':     'connection_types',
        },
        'dvrs': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('ip address', 'ip_address'),
                ('username', 'username'),
                ('password', 'password'),
            ])
        },
        'sites': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('dvr id', 'dvr id',)
            ])
        },
        'connection log': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('site id', 'site_id'),
                ('start', 'start'),
                ('end', 'end'),
                ('connection type id', 'connection_type_id')
            ])
        },
        'connection types': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name')
            ])
        },
        'connection statuses': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('site id', 'site_id'),
                ('available', 'available'),
                ('last time pinged available', 'last_time_pinged_available'),
                ('last time pinged unavailable', 'last_time_pinged_unavailable')
            ])
        }
    }
}