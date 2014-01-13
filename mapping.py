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

### Tartaros #######################################################################################
####################################################################################################

TARTAROS_DB_PATH = getcwdu() + "\\web2py\\applications\\Tartaros\\databases\\tartaros.sqlite"
TARTAROS_WEB_DB_PATH = getcwdu() + "\\applications\\Tartaros\\databases\\tartaros.sqlite"
#TARTAROS_DB_PATH = getcwdu() + "\\tartaros.db"

TARTAROS = {
    'database': {
        'tables': {
            'modules':          'modules',
            'features':         'features',
            'user stories':     'user_stories',
            'tests':            'tests',
            'testcases':        'test_cases',
            'procedure steps':  'procedure_steps',
            'functions':        'functions',
            'submodules':       'submodules',
            'licenses':         'licenses',
            'dvrs':             'dvrs',
            'sites':            'sites',
        },
        'modules': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('submodule', 'submodule_id'),
            ]),
        },
        'features': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('submodule', 'submodule_id'),
            ]),
        },
        'user stories': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('feature', 'feature_id'),
                ('module', 'module_id'),
                ('action', 'action'),
                ('user type', 'user_type')
            ]),
        },
        'tests': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('user story', 'user_story_id'),
                ('results id', 'results_id'),
            ]),
        },
        'testcases': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('test', 'test_id'),
                ('procedure', 'procedure'),
                ('minimum version', 'min_version'),
                ('class', 'test_class'),
                ('active', 'active')
            ]),
        },
        'procedure steps': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('function', 'function_id'),
                ('arguments', 'arguments'),
                ('verification', 'verification'),
            ])
        },
        'functions': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('function', 'function'),
                ('submodule id', 'submodule_id'),
            ]),
        },
        'submodules': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('code', 'code')
        ])
        },
        'licenses': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('key', 'key'),
                ('bit', 'bit_num'),
                ('number of sites', 'num_sites'),
            ])
        },
        'dvrs': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('ip address', 'ip_address'),
                ('serial', 'serial_num'),
                ('drive serial', 'hd_serial_num'),
                ('model', 'model'),
                ('firmware', 'firmware'),
                ('user', 'username'),
                ('password', 'password'),
            ])
        },
        'sites': {
            'fields': OrderedDict([
                ('id', 'id'),
                ('name', 'name'),
                ('dvr id', 'dvr_id'),
            ])
        }
    },
    'test statuses': {
        'passed':           'passed',
        'failed':           'failed',
        'blocked':          'blocked',
        're-test':          're-test',
        'not tested':       'not tested',
        'passed with issues':'passed with issues',
        'invalid due to version':'invalid due to version',
    },
    'modes': {
        'default':          'default',
        'debug':            'debug',
    },

}

HESTIA_DEFAULT_STORAGE_LOC = 'D:\\video\\'
HESTIA = {
    'default bin location':     'C:\\Program Files (x86)\\ViM\\bin\\',
    'default storage location': HESTIA_DEFAULT_STORAGE_LOC,
    'default server url':       'http://localhost:9980',
    'database': {
        'clip log': {
            'table':                        'ClipLog',
            'fields': {
                'id':                       'ClipID',
                'event id':                 'EventLogID',
                'file path':                'FilePath',
                'file name':                'FileName',
                'download time':            'FileTime',
                'file size':                'FileSize',
                'file type':                'FileType',
                'download type':            'DownloadType',
                'length':                   'ClipLength',
                'start':                    'ClipStart',
                'cameras':                  'Cameras',
                'notes':                    'Notes',
                'notify':                   'NotifyUser'
            },
            'download types': {
                'autoclip':                 1,
                'camera clip':              2,
                'video loss':               2,
                'health clip':              2,
                'fan error':                2,
                'custom':                   2,
                'custom clip':              2,
                'custom event clip':        2,
            }
        },
        'custody': {
            'table':                        'ChainOfCustody',
            'fields': {
                'id':                       'rowid',
                'clip id':                  'ClipID',
                'type':                     'ActionType',
                'value':                    'ActionValue',
                'author':                   'ActionBy',
                'time':                     'ActionTime',
                'text':                     'ActionText'
            },
            'action to action value': {
                'request':                 -1,
                'download':                 0,
                'review':                   1,
                'note':                    '1a',
                'save':                     2,
                'preserve':                 3,
                'schedule for delete':      4,
                'delete':                   5,
                'fail to download':         6,
                'cancel':                   7
            },
            'action value to clip status': {
                '-1':                       'requested',
                '0':                        'new',
                '1':                        'reviewed',
                '2':                        'saved',
                '3':                        'preserved',
                '4':                        'scheduled for delete',
                '5':                        'deleted',
                '6':                        'failed to download',
                '7':                        'clip download cancelled'
            },
        },
        'drive history': {
            'table':            'DriveHistory',
            'fields': {
                'id':                       'DriveHistoryID',
                'dvr id':                   'DvrID',
                'disk id':                  'DiskID',
                'start':                    'IntervalStart',
                'end':                      'IntervalEnd',
                'start type':               'IntervalStartType',
                'end type':                 'IntervalEndType',
            },
        },
        'drives': {
            'table':            'HardDisks',
            'fields': {
                'id':                       'DiskID',
                'serial':                   'DiskSN'
            },
        },
        'dvr history': {
            'table':            'DvrHistory',
            'fields': {
                'id':                       'DvrHistoryID',
                'site id':                  'SiteID',
                'dvr id':                   'DvrID',
                'start':                    'IntervalStart',
                'end':                      'IntervalEnd'
            }
        },
        'dvrs': {
            'table':            'MDVRs',
            'fields': {
                'id':                       'DvrID',
                'disk id':                  'DiskID',
                'serial':                   'DvrSN',
                'model':                    'DvrModel',
                'firmware':                 'FirmwareVersion',
            },
        },
        'event log': {
            'table':            'EventLog',
            'fields': {
                'id':                       'EventLogID',
                'site id':                  'SiteID',
                'type':                     'EventType',
                'event id':                 'EventId',
                'start':                    'EventStart',
                'duration':                 'EventDuration',
                'cameras':                  'CameraId',
                'label':                    'EventLabel',
                'level':                    'EventLevel',
                'download clip':            'DownloadClip',
                'disk id':                  'DiskID'
            },
            'event types': {
                'alarm':                '01',
                'disk almost full':     '00',
                'disk full':            '08',
                'disk bad':             '11',
                'disk temperature':     '12',
                'disk s.m.a.r.t.':      '13',
                'fan error':            '23',
                'motion':               '03',
                'video loss':           '04',
                'video blind':          '19',
                'custom':               '32767'
            },
        },
        'geoclip requests': {
            'table':            'GeoClipRequest',
            'fields': {
                'id':                       'GCRID',
                'event id':                 'EventLogID',
                'start time':               'ReqFrmtime',
                'end time':                 'ReqTotime',
                'post time':                'PostTime',
                'pre time':                 'PreTime',
                'minimum latitude':         'MinLatitude',
                'maximum latitude':         'MaxLatitude',
                'minimum longitude':        'MinLongitude',
                'maximum longitude':        'MaxLongitude',
                'download type':            'DownloadType',
                'clip length':              'ClipLenght',
                'cameras':                  'Cameras',
                'label':                    'Label',
                'notes':                    'Notes',
                'notification':             'NotifyUser',
                'author':                   'ActionBy'
            },
        },
        'geoclip requests pending': {
            'table':            'GeoClipRequestPendingForSite',
            'fields': {
                'id':                       'rowid',
                'site id':                  'SiteID',
                'geo request id':           'GCRID',
            },
        },
        'gps': {
            'table':            'GPRMC',
            'fields': {
                'id':                       'rowid',
                'disk id':                  'DiskID',
                'time':                     'FixTime',
                'latitude':                 'Latitude',
                'longitude':                'Longitude',
                'speed':                    'Speed',
                'direction':                'TrueCourse'
            },
        },
        'gps last position': {
            'table':            'LastGPRMCofSite',
            'fields': {
                'id':                       'rowid',
                'site id':                  'SiteID',
                'time':                     'FixTime',
                'latitude':                 'Latitude',
                'longitude':                'Longitude',
                'speed':                    'Speed',
                'direction':                'TrueCourse'
            },
        },
        'sites': {
            'table':            'RemoteSites',
            'fields': {
                'id':                       'SiteID',
                'site group id':            'SiteGroupID',
                'active':                   'SiteActive',
                'site name':                'SiteName',
                'dvr id':                   'DvrID',
                'ip address':               'IpAddress',
                'alt ip':                   'AlternateIpAddress',
                'user':                     'DvrUserName',
                'password':                 'DvrPassword',
                'number of cameras':        'NumCameras',
                'download events':          'EventsOn',
                'download clips':           'AlarmIn',
                'download motion':          'Motion',
                'download video loss':      'VideoLoss',
                'download video blind':     'VideoBlind',
                'download text-in':         'TextIn',
                'camera selection':         'CameraSelection',
                'system filter':            'SystemFilter',
                'download duration':        'DurationOn',
                'pre-event time 1':         'PreTime1',
                'pre-event time 2':         'PreTime2',
                'pre-event time 3':         'PreTime3',
                'pre-event time 4':         'PreTime4',
                'pre-event time 5':         'PreTime5',
                'pre-event time 6':         'PreTime6',
                'pre-event time 7':         'PreTime7',
                'pre-event time 8':         'PreTime8',
                'post-event time 1':        'PostTime1',
                'post-event time 2':        'PostTime2',
                'post-event time 3':        'PostTime3',
                'post-event time 4':        'PostTime4',
                'post-event time 5':        'PostTime5',
                'post-event time 6':        'PostTime6',
                'post-event time 7':        'PostTime7',
                'post-event time 8':        'PostTime8',
                'recall period':            'LookBackPeriod'
            },
        },
        'site groups': {
            'table':            'SiteGroups',
            'fields': {
                'id':                       'SiteGroupID',
                'site group name':          'SiteGroupName',
                'storage location':         'RootDataFolder',
                'elrt':                     'EventLogRetention',
                'tsd':                      'ClipRetention',
                'ltsd':                     'SavedClipRetention',
                'dgp':                      'DeleteGracePeriod'
            },
        },
        'system log': {
            'table':            'SystemLog',
            'fields': {
                'id':                       'SyslogID',
                'dvr id':                   'DvrID',
                'time':                     'SyslogTime',
                'type':                     'SyslogType',
                'data':                     'SyslogData',
                'author':                   'CreatedBy'
            },
            'event type to type id': {
                'remote log in':            '102',
                'remote log out':           '103',
            },
            'author to author id': {
                'non-vim':                  '0',
                'vim':                      '1',
            }
        }
    },
    'dvr models': [
        'MR4',
        'MR8',
        'MRH4',
        'MRH8',
        'MRH16',
        'RRH8',
        'RRH16',
    ],
    'server': {
        'camera event log': {
            'query path':               '/cameventlog',
            'entry id':                     'event id',
            'parameters': {
                'results':                  20,
                'sort':                     'eventStart desc',
                'startIndex':               0,
                'where':                    'eventType=4 and eventStart between yesterday and today'
            },
            'fields': {
                'site id':                  'siteId',
                'site name':                'siteName',
                'type':                     'eventType',
                'event type':               'eventDescription',
                'camera id':                'eventId',
                'event label':              'eventLabel',
                'date/time':                'eventStart',
                'event duration':           'eventDuration',
                'downloaded clips':         'ClipsAvailable',
                'pending clips':            'ClipsPending',
                'failed clips':             'ClipsFailed',
                'canceled clips':           None
            },
            'columns': [
                'event id',
                'site id',
                'site name',
                'event type',
                'date/time',
                'downloaded clips',
                'pending clips',
                'failed clips',
                'canceled clips',
                'event label',
                'event duration',
                'cameras'
            ],
            'columns v3.1': [
                'event id',
                'unknown1',
                'site name',
                'event type',
                'date/time',
                'downloaded clips',
                'pending clips',
                'failed clips',
                'event label',
                'event duration',
                'cameras'
            ]
        },
        'camera health log': {
            'query path':               '/camhealth',
            'entry id':                     'site name',
            'parameters': {
                'group':                    'siteID',
                'results':                  -1,
                'sort':                     'siteName asc',
                'startIndex':               0,
                'where':                    'eventType=4 and eventStart between yesterday and today'
            },
            'filters': [
                ['event type','video loss'],
                ['start date/time','yesterday'],
                ['end date/time','today']
            ],
            'fields': {
                'site id':                  'siteId',
                'site name':                'siteName',
                'type':                     'eventType',
                'date/time':                'eventStart',
                'camera 1 events':          None,
                'camera 2 events':          None,
                'camera 3 events':          None,
                'camera 4 events':          None,
                'camera 5 events':          None,
                'camera 6 events':          None,
                'camera 7 events':          None,
                'camera 8 events':          None,
                'camera 9 events':          None,
                'camera 10 events':         None,
                'camera 11 events':         None,
                'camera 12 events':         None,
                'camera 13 events':         None,
                'camera 14 events':         None,
                'camera 15 events':         None,
                'camera 16 events':         None,
                },
            'columns': [
                'site id',
                'site name',
                'unknown1',
                'unknown2',
                'camera 1 events',
                'camera 2 events',
                'camera 3 events',
                'camera 4 events',
                'camera 5 events',
                'camera 6 events',
                'camera 7 events',
                'camera 8 events',
                'camera 9 events',
                'camera 10 events',
                'camera 11 events',
                'camera 12 events',
                'camera 13 events',
                'camera 14 events',
                'camera 15 events',
                'camera 16 events',
                ]
        },
        'categories': {
            'query path':               '/categories',
            'modify path':              '/categories',
            'entity path':              '/categories/%(id)s',
            'parameters': {},
            'fields': {
                'id':                       'id',
                'order':                    'order',
                'name':                     'name',
                'description':              'desc',
                'values':                   'values',
                },
            'columns': []
        },
        'category values': {
            'query path':               '/categories/%(category id)s/values',
            'modify path':              '/categories/%(category id)s/values',
            'entity path':              '/categories/%(category id)s/values/%(id)s',
            'parameters': {},
            'fields': {
                'id':                       'id',
                'category id':              'category',
                'order':                    'order',
                'name':                     'name',
                'description':              'desc'
            },
            'columns': []
        },
        'classifications': {
            'path':                     '/clips/%(clip id)s/categories/%(category id)s',
            'fields': {
                'clip id':                  'clipid',
                'value id':                 'valueid',
                }
        },
        'clip actions': {
            'cancel path':              '/cancelClipDownload',
            'preserve path':            '/cliplog?archiveClip=%s',
            'schedule for delete path': '/cliplog?deleteClip=%s',
        },
        'clip notations': {
            'path':                     '/cliplog?',
            'fields': {
                'clip id':                  'clipId',
                'notation':                 'notes',
                }
        },
        'clip request': {
            'path':                     '/vimcustomclip',
            'fields': {
                'site id':                  'SiteID',
                'site name':                'SiteName',
                'event id':                 'EventLogID',
                'start':                    'StartTime',
                'start date/time':          'ClipStartDateTime',
                'end date/time':            'ClipEndDateTime',
                'event start':              'EventStart',
                'time buffer':              'TimeBuffer',
                'duration':                 'Duration',
                'event duration':           'EventDuration',
                'event type':               'EventType',
                'event type id':            'EventId',
                'event label':              'EventLabel',
                'camera label':             'CameraLabel',
                'cameras':                  'CameraSelection',
                'notes':                    'Notes',
                'notification':             'NotifyUser',
            },
        },
        'clip status info': {
            'query path':               '/clipStatusInfo',
            'entry id':                 None,
            'parameters': {},
            'fields': {},
            'columns': [
                'clip id',
                'date/time',
                'clip length',
                'requested by',
                'requested at',
                'action value',
                'user',
                'action time',
                ]
        },
        'custody': {
            'query path':               '/custody/%(id)s',
            'parameters':   {},
            'fields': {
                'unknown':                  None,
                'author':                   None,
                'value':                    None,
                'text':                     None,
                'unknown2':                 None,
                'time':                     None,
            },
            'columns': [
                'unknown',
                'author',
                'value',
                'text',
                'unknown 2',
                'time'
            ],
        },
        'dvr health log': {
            'query path':                   '/dvreventlog',
            'entry id':                     'event id',
            'parameters': {
                'results':                  20,
                'sort':                     'eventStart desc',
                'startIndex':               0,
                'where':                    'eventStart between yesterday and today'
            },
            'fields': {
                'site id':                  'siteId',
                'site name':                'siteName',
                'event type':               'eventDescription',
                'event label':              'eventLabel',
                'date/time':                'eventStart',
                'event duration':           'eventDuration',
                'downloaded clips':         'ClipsAvailable',
                'pending clips':            'ClipsPending',
                'failed clips':             'ClipsFailed',
                'canceled clips':           None
            },
            'columns': [
                'event id',
                'site id',
                'site name',
                'event type',
                'date/time',
                'downloaded clips',
                'pending clips',
                'failed clips',
                'canceled clips',
                'event label',
                'event duration',
                'cameras'
            ],
            'columns v3.1': [
                'event id',
                'unknown1',
                'site name',
                'event type',
                'date/time',
                'downloaded clips',
                'pending clips',
                'failed clips',
                'event label',
                'event duration',
                'cameras'
            ]
        },
        'email': {
            'send status email path':   '/sendStatus',
        },
        'email test': {
            'path':     '/vimadmtestemail',
            'fields': {
                'server url':               'serverUrl',
                'email server':             'smtpHost',
                'email port':               'smtpPort',
                'email secure':             'smtpSecure',
                'email account':            'smtpLogin',
                'email password':           'smtpWrd',
                'email from':               'smtpFrom',
                'email to':                 'to',
                },
            'default configuration': [
                ['server url','http://localhost'],
                ['email enabled','true'],
                ['email server','pod51019.outlook.com'],
                ['email port','587'],
                ['email secure','true'],
                ['email account','vim@avt-usa.net'],
                ['email password','p@ssw0rd!'],
                ['email from','vim@avt-usa.net']
            ],
        },
        'geo clip': {
            'request path':             '/vimGeoClip?',
            'fields': {
                'start':                    'StartTime',
                'end':                      'EndTime',
                'start date/time':          'FromTime',
                'end date/time':            'ToTime',
                'ne latitude':              'NELatitude',
                'ne longitude':             'NELongitude',
                'sw latitude':              'SWLatitude',
                'sw longitude':             'SWLongitude',
                'cameras':                  'CameraSelection',
                'event label':              'EventLabel',
                'notes':                    'Notes',
                'notification':             'Notify',
                }
        },
        'health clip log': {
            'query path':               '/hthcliplog',
            'entry id':                     'clip id',
            'parameters': {
                'results':                  20,
                'sort':                     'eventStart desc',
                'startIndex':               0,
                'where':                    'eventStart between yesterday and today'
            },
            'fields': {
                'clip id':                  'clipId',
                'site id':                  'siteId',
                'site name':                'siteName',
                'event type':               'eventDescription',
                'event label':              'eventLabel',
                'date/time':                'eventStart',
                'clip length':              'clipLength',
                'clip status':              'clipStatus',
                'last viewer':              'lastReviewed',
                'classifications':          'Classification',
                'download time':            'downloadTime',
                'file size':                'fileSize',
                'classification status':    'categories',
                'clip status change author':None
            },
            'columns': [
                'clip id',
                'unknown1',
                'site name',
                'file name',
                'date/time',
                'download time',
                'file size',
                'unknown2',
                'event type',
                'event label',
                'clip status',
                'clip status change author',
                'action time',
                'last viewer',
                'classifications',
                'classification status',
                'notation',
                'length',
                'unknown4',
                'unknown5',
                'unknown6',
                'unknown7',
                'event id',
                'site id'
            ]
        },
        'health status page': {
            'query path':               '/hthstatus',
            'entry id':                     'site name',
            'parameters': {
                'results':                  20,
                'sort':                     'siteName asc',
                'startIndex':               0,
                'where':                    'eventStart between yesterday and today'
            },
            'fields': {
                'site id':                  'siteId',
                'site name':                'siteName',
                'last communication time':  'lastCommunicated',
                'last event processed time':'LastEventProcessed',
                'number of camera events':  'numCamEvents',
                'number of dvr events':     'numDvrEvents',
                'number of pending clips':  'numPendingClips',
                'number of new clips':      'numNewEvents'
            },
            'columns': [
                'site name',
                'cs time stamp',
                'last event processed time',
                'number of pending clips',
                'number of new clips',
                'number of camera events',
                'number of dvr events',
                'last communication time',
                'unknown',
                'connection status', #working, available, unavailable
                'unknown2'
            ]
        },
        'license configuration': {
            'query path':               '/license',
            'modify path':              '/license',
            'fields': {
                'key':                      'lic',
            },
            'columns': [
                'id',
                'key',
                'numactive',
                'sites',
                'machineid',
                'modules'
            ],
        },
        'map': {
            'query path':               '/latestGpsForSites',
            'entry id':                     'site name',
            'parameters': {
                'results':                  -1,
                'sort':                     'siteId desc',
                'startIndex':               0,
                'where':                    'LastFixTime >= anhourago'
            },
            'fields': {
                'site id':                  'siteId',
                'date/time':                'LastFixTime',
                },
            'columns': [
                'site name',
                'date/time',
                'latitude',
                'longitude',
                'unknown',
                'unknown2',
                'unknown3',
                ]
        },
        'password modification': {
            'modify path':          '/vimadmpwd',
            'fields': {
                'account':                      'acct',
                'new password':                 'new',
                'new password verification':    'new2',
                'old password':                 'old',
                },
        },
        'run cleanup path':         '/runCleanup',
        'session': {
            'path':                 '/login',
            'logout path':          '/logout',
            'fields': {
                'user name':                'username',
                'password':                 'password',
            },
        },
        'site configuration': {
            'query path':               '/siteInfo',
            'modify path':              '/vimadmsites',
            'de/activation path':       '/sites',
            'entry id':                     'id',
            'parameters': {
                'results':                  -1,
                'sort':                     'SiteName asc',
                'startIndex':               0,
            },
            'fields': {
                'id':                       'SiteID',
                'site group name':          'SiteGroupName',
                'site group id':            'SiteGroupId',
                'site status':              'siteActive',
                'site name':                'SiteName',
                'ip address':               'IpAddress',
                'dvr username':             'DvrUserName',
                'dvr password':             'DvrPassword',
                'dvr model':                'DvrModel',
                'cameras':                  None,
                'events to download':       'EventsOn',
                'clips to download':        'AlarmIn',
                'duration for clips':       'DurationOn',
                'motion to download':       None,
                'video loss to download':   'VideoLoss',
                'video blind to download':  None,
                'text in':                  None,
                'camera selection':         None,
                'recall period':            'LookBackPeriod',
                'pre-event time all':       'PreTime',
                'pre-event time 1':         'PreTime1',
                'pre-event time 2':         'PreTime2',
                'pre-event time 3':         'PreTime3',
                'pre-event time 4':         'PreTime4',
                'pre-event time 5':         'PreTime5',
                'pre-event time 6':         'PreTime6',
                'pre-event time 7':         'PreTime7',
                'pre-event time 8':         'PreTime8',
                'post-event time all':      'PostTime',
                'post-event time 1':        'PostTime1',
                'post-event time 2':        'PostTime2',
                'post-event time 3':        'PostTime3',
                'post-event time 4':        'PostTime4',
                'post-event time 5':        'PostTime5',
                'post-event time 6':        'PostTime6',
                'post-event time 7':        'PostTime7',
                'post-event time 8':        'PostTime8'
            },
            'columns 3.3': [
                'id',
                'site status',
                'site name',
                'ip address',
                'dvr username',
                'dvr password',
                'dvr model',
                'cameras',
                'events to download',
                'clips to download',
                'duration for clips',
                'motion to download',
                'video loss to download',
                'video blind to download',
                'text in',
                'camera selection',
                'recall period',
                'pre-event time 1',
                'pre-event time 2',
                'pre-event time 3',
                'pre-event time 4',
                'pre-event time 5',
                'pre-event time 6',
                'pre-event time 7',
                'pre-event time 8',
                'post-event time 1',
                'post-event time 2',
                'post-event time 3',
                'post-event time 4',
                'post-event time 5',
                'post-event time 6',
                'post-event time 7',
                'post-event time 8'
            ],
            'columns': [
                'id',
                'site group name',
                'site group id',
                'site status',
                'site name',
                'ip address',
                'dvr username',
                'dvr password',
                'dvr model',
                'cameras',
                'events to download',
                'clips to download',
                'duration for clips',
                'motion to download',
                'video loss to download',
                'video blind to download',
                'text in',
                'camera selection',
                'recall period',
                'pre-event time 1',
                'pre-event time 2',
                'pre-event time 3',
                'pre-event time 4',
                'pre-event time 5',
                'pre-event time 6',
                'pre-event time 7',
                'pre-event time 8',
                'post-event time 1',
                'post-event time 2',
                'post-event time 3',
                'post-event time 4',
                'post-event time 5',
                'post-event time 6',
                'post-event time 7',
                'post-event time 8'
            ],
        },
        'site groups': {
            'query path':               '/siteGroups',
            'modify path':              '/vimadmsitegroups',
            'entry id':                 'site group name',
            'parameters': {
                'results':                  -1,
                'sort':                     'SiteGroupName asc',
                'startIndex':               0,
            },
            'fields': {
                'id':                       'SiteGroupID',
                'site group name':          'SiteGroupName',
                'storage location':         'RootDataFolder',
                'elrt':                     'EventLogRetention',
                'tsd':                      'ClipRetention',
                'ltsd':                     'SavedClipRetention',
                'dgp':                      'DeleteGracePeriod',
            },
            'columns': [
                'id',
                'site group name',
                'storage location',
                'elrt',
                'tsd',
                'ltsd',
                'dgp'
            ],
        },
        'system configuration': {
            'path':                 '/vimadmapp',
            'fields': {
                'server url':               'serverUrl',
                'email enabled':            'emailEnabled',
                'email server':             'smtpHost',
                'email port':               'smtpPort',
                'email secure':             'smtpSecure',
                'email account':            'smtpLogin',
                'email password':           'smtpWrd',
                'email from':               'smtpFrom',
                'diagnostics enabled':      'diagnosticsEnabled',
                'organization':             'organizationIdentifier',
                'storage location':         'storagePath',
                'elrt':                     'eventLogTime',
                'tsd':                      'bin1Time',
                'ltsd':                     'bin2Time',
                'dgp':                      'gracePeriod',
                'default location':         'address',
                'default latitude':         'lat',
                'default longitude':        'lng',
                'live view server':         'liveView Server',
                'live view user':           'liveView User',
                'live view password':       'liveView Password',
                'live view enabled':        'streamingServerEnabled',
            },
            'columns': [
                'serverUrl',
                'emailEnabled',
                'smtpHost',
                'smtpPort',
                'smtpSecure',
                'smtpLogin',
                'smtpWrd',
                'smtpFrom',
                'address',
                'lat',
                'lng',
                'streamingServerEnabled',
                'liveView Server',
                'liveView User',
                'liveView Password',
                'diagnosticsEnabled',
                'organizationIdentifier',
                'storagePath',
                'eventLogTime',
                'bin1Time',
                'bin2Time',
                'gracePeriod',
            ],
            'columns 2.0': [
                'serverUrl',
                'emailEnabled',
                'smtpHost',
                'smtpPort',
                'smtpLogin',
                'smtpWrd',
                'smtpFrom',
                'storagePath',
                'eventLogTime',
                'bin1Time',
                'bin2Time',
                'gracePeriod',
            ],
            'columns 3.2': [
                'serverUrl',
                'emailEnabled',
                'smtpHost',
                'smtpPort',
                'smtpSecure',
                'smtpLogin',
                'smtpWrd',
                'smtpFrom',
                'diagnosticsEnabled',
                'organizationIdentifier',
                'storagePath',
                'eventLogTime',
                'bin1Time',
                'bin2Time',
                'gracePeriod',
            ],
            'default settings': {
                'storagePath':         HESTIA_DEFAULT_STORAGE_LOC,
                'eventLogTime':        365,
                'bin2Time':            365,
                'bin1Time':            15,
                'gracePeriod':         7
            },
            'default diagnostics settings': [
                ['diagnostics enabled','true'],
                ['organization','ViM Automated Testing']
            ],
            'default location settings': [
                ['default location','Bothell, WA'],
                ['default latitude','47.7623'],
                ['default longitude','-122.205']
            ],
            'default email settings': [
                ['server url','http://localhost'],
                ['email enabled','true'],
                ['email server','pod51019.outlook.com'],
                ['email port','587'],
                ['email secure','true'],
                ['email account','vim@avt-usa.net'],
                ['email password','p@ssw0rd!'],
                ['email from','vim@avt-usa.net'],
            ],
            'default streaming server settings': [
                ['live view enabled', 'true'],
                ['live view server', 'ETS-INEX-TEST'],
                ['live view user', 'admin'],
                ['live view password', '12345678'],
            ],
        },
        'system log': {
            'query path':           '/syslog',
            'entry id':             'id',
            'parameters':{
                'results':              20,
                'sort':                 'syslogTime desc',
                'startIndex':           0,
                'where':                "siteId='1' and createdBy in (0)"
            },
            'fields': {
                'id':                   None,
                'site id':              'siteId',
                'date/time':            'syslogTime',
                'event type':           None,
                'event data':           None,
                'created by':           'createdBy'
            },
            'columns': [
                'id',
                'site id',
                'date/time',
                'event type',
                'event data',
                'created by'
            ]
        },
        'user configuration': {
            'query path':           '/users',
            'modify path':          '/vimadmusers',
            'delete path':          '/users/%(user name)s',
            'entry id':                 'user name',
            'parameters':{
                'results':              -1,
                'sort':                 'userName asc',
                'startIndex':           0
            },
            'fields': {
                'user name':            'userName',
                'first name':           'firstName',
                'last name':            'lastName',
                'email address':        'emailAddress',
                'user level':           'userGroupID',
                'password date':        'passwordDate',
                'notification time':    'sendAt',
                'password':             'password',
                'verification':         'password2',
                'group id':             'groupID',
                },
            'columns': [
                'user name',
                'first name',
                'last name',
                'email address',
                'user level',
                'password date',
                'notification time'
            ],
            'level to group id': {
                'admin':        1,
                'administrator':1,
                'supervisor':   2,
                'reviewer':     3
            },
        },
        'video clip log': {
            'query path':               '/autcliplog',
            'entry id':                     'clip id',
            'parameters': {
                'results':                  20,
                'sort':                     'eventStart desc',
                'startIndex':               0,
                },
            'fields': {
                'clip id':                  'clipId',
                'site id':                  'siteId',
                'site name':                'siteName',
                'event type':               'eventDescription',
                'event label':              'eventLabel',
                'alarm id':                 'eventId',
                'date/time':                'eventStart',
                'clip length':              'clipLength',
                'clip status':              'clipStatus',
                'last viewer':              'lastReviewed',
                'classifications':          'Classification',
                'download time':            'downloadTime',
                'file size':                'fileSize',
                'classification status':    'categories',
                'clip status change author':None
            },
            'columns': [
                'clip id',
                'unknown1',
                'site name',
                'file name',
                'date/time',
                'download time',
                'file size',
                'unknown2',
                'event type',
                'event label',
                'clip status',
                'clip status change author',
                'action time',
                'last viewer',
                'classifications',
                'classification status',
                'notation',
                'length',
                'unknown4',
                'unknown5',
                'unknown6',
                'unknown7',
                'event id',
                'site id'
            ]
        },
        'video event log': {
            'query path':               '/auteventlog',
            'entry id':                     'event id',
            'parameters': {
                'results':                  20,
                'sort':                     'eventStart desc',
                'startIndex':               0,
                },
            'fields': {
                'site id':                  'siteId',
                'site name':                'siteName',
                'event type':               'eventDescription',
                'event label':              'eventLabel',
                'alarm id':                 'eventId',
                'date/time':                'eventStart',
                'event duration':           'eventDuration',
                'downloaded clips':         'ClipsAvailable',
                'pending clips':            'ClipsPending',
                'failed clips':             'ClipsFailed',
                'canceled clips':           None
            },
            'columns': [
                'event id',
                'unknown1',
                'site name',
                'event type',
                'date/time',
                'downloaded clips',
                'pending clips',
                'failed clips',
                'canceled clips',
                'event label',
                'event duration',
                'cameras'
            ],
            'columns v3.1': [
                'event id',
                'unknown1',
                'site name',
                'event type',
                'date/time',
                'downloaded clips',
                'pending clips',
                'failed clips',
                'event label',
                'event duration',
                'cameras'
            ]
        },
        'video status page': {
            'query path':               '/status',
            'entry id':                     'site name',
            'parameters': {
                'results':                  20,
                'sort':                     'siteName asc',
                'startIndex':               0,
                },
            'fields': {
                'site id':                  'siteId',
                'site name':                'siteName',
                'last communication time':  'lastCommunicated',
                'last event processed time':'LastEventProcessed',
                'number of pending clips':  'numPendingClips',
                'number of new clips':      'numNewEvents'
            },
            'columns': [
                'site name',
                'cs time stamp',
                'last event processed time',
                'number of pending clips',
                'number of new clips',
                'unknown1',
                'unknown2'
                'last communication time',
                'unknown3',
                'unknown4',
                'connection status', #working, available, unavailable
                'unknown5'
            ]
        },
    },
}

HESTIA_PAGE_TO_CONFIG = {
    'system setup':         HESTIA['server']['system configuration'],
    'users':                HESTIA['server']['user configuration'],
    'sites':                HESTIA['server']['site configuration'],
    'video status page':    HESTIA['server']['video status page'],
    'video clip log':       HESTIA['server']['video clip log'],
    'video event log':      HESTIA['server']['video event log'],
    'health status page':   HESTIA['server']['health status page'],
    'camera health log':    HESTIA['server']['camera health log'],
    'camera event log':     HESTIA['server']['camera event log'],
    'dvr health log':       HESTIA['server']['dvr health log'],
    'health clip log':      HESTIA['server']['health clip log'],
    'system log':           HESTIA['server']['system log'],
    'map':                  HESTIA['server']['map'],
    'site groups':          HESTIA['server']['site groups'],
    'categories':           HESTIA['server']['categories'],
    'category values':      HESTIA['server']['category values'],
    'custody':              HESTIA['server']['custody'],
    'clip status info':     HESTIA['server']['clip status info'],
}

HESTIA_PAGE_TO_PAGE_FIELDS = {
    'system setup':         HESTIA_PAGE_TO_CONFIG['system setup']['fields'],
    'users':                HESTIA_PAGE_TO_CONFIG['users']['fields'],
    'sites':                HESTIA_PAGE_TO_CONFIG['sites']['fields'],
    'video status page':    HESTIA_PAGE_TO_CONFIG['video status page']['fields'],
    'video clip log':       HESTIA_PAGE_TO_CONFIG['video clip log']['fields'],
    'video event log':      HESTIA_PAGE_TO_CONFIG['video event log']['fields'],
    'health status page':   HESTIA_PAGE_TO_CONFIG['health status page']['fields'],
    'camera health log':    HESTIA_PAGE_TO_CONFIG['camera health log']['fields'],
    'camera event log':     HESTIA_PAGE_TO_CONFIG['camera event log']['fields'],
    'dvr health log':       HESTIA_PAGE_TO_CONFIG['dvr health log']['fields'],
    'health clip log':      HESTIA_PAGE_TO_CONFIG['health clip log']['fields'],
    'system log':           HESTIA_PAGE_TO_CONFIG['system log']['fields'],
    'map':                  HESTIA_PAGE_TO_CONFIG['map']['fields'],
    'site groups':          HESTIA_PAGE_TO_CONFIG['site groups']['fields'],
    'categories':           HESTIA_PAGE_TO_CONFIG['categories']['fields'],
    'category values':      HESTIA_PAGE_TO_CONFIG['category values']['fields'],
    'custody':              HESTIA_PAGE_TO_CONFIG['custody']['fields'],
    'clip status info':     HESTIA_PAGE_TO_CONFIG['clip status info']['fields'],
}

ORPHEUS = {
    'server url':           "http://172.22.2.93:80/index.php?/api/v2",
    'server key':           12345,
    'user name':            'Jonathan.Slattery@avt-usa.com',
    'password':             'Nikmik21',
    'test status to id': {
        'passed':           1,
        'blocked':          2,
        're-test':          4,
        'failed':           5
    },
    'test id to status': {
        '1':                'passed',
        '2':                'blocked',
        '4':                're-test',
        '5':                'failed'
    }
}

MINOS = {
    'api url':              "http://172.22.1.190/httpAuth/",
    'rest api url':         "http://172.22.1.190/httpAuth/app/rest/",
}