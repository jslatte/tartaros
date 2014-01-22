####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Mapping ##########################################################################################
####################################################################################################
####################################################################################################

# the URL of the server
SERVER_URL = "http://172.22.1.190/httpAuth/"

# build suffixes (i.e., dev, rc1, etc. on build artifact)
BUILD_SUFFIXES = ['dev','rc1','gm','rc2','rc3','a1','b1','sp1','sp2','sp3','sp4']

# user authentication
AUTHENTICATION = ['robot','password']

# file paths
FILE_PATHS = {
    'root':                 "C:\\Users\\teamcity\\.BuildServer\\config\\"
}

# BUILD COUNTER MAPS
#   'sharing projects' indicates which projects share the same build counter

# ViM Release project lines
RELEASE = {
    'path':             "ViM (Release)\\",
    'build line':       2,
    'sharing projects': [
        'development',
        'sub-development 1',
        'sub-development 2',
        'sub-development 3',
        'sub-development 4',
        'sub-development 5',
        ]
}
RELEASE_3_2 = {
    'path':             "ViM (Release)\\",
    'build line':       47,
    'sharing projects': []
}
RELEASE_3_3 = {
    'path':             "ViM (Release)\\",
    'build line':       48,
    'sharing projects': []
}
RELEASE_4_0 = {
    'path':             "ViM (Release)\\",
    'build line':       54,
    'sharing projects': []
}

# ViM Development project lines
WIP = {
    'path':             "ViM (WIP)\\",
    'build line':       37,
    'sharing projects': [
        'release',
        'sub-development 1',
        'sub-development 2',
        'sub-development 3',
        'sub-development 4',
        'sub-development 5',
        ]
}
SUB_DEV_1 = {
    'path':             "ViM (WIP)\\",
    'build line':       42,
    'sharing projects': [
        'release',
        'development',
        'sub-development 2',
        'sub-development 3',
        'sub-development 4',
        'sub-development 5',
        ]
}
SUB_DEV_2 = {
    'path':             "ViM (WIP)\\",
    'build line':       43,
    'sharing projects': [
        'release',
        'development',
        'sub-development 1',
        'sub-development 3',
        'sub-development 4',
        'sub-development 5',
        ]
}
SUB_DEV_3 = {
    'path':             "ViM (WIP)\\",
    'build line':       44,
    'sharing projects': [
        'release',
        'development',
        'sub-development 1',
        'sub-development 2',
        'sub-development 4',
        'sub-development 5',
        ]
}
SUB_DEV_4 = {
    'path':             "ViM (WIP)\\",
    'build line':       45,
    'sharing projects': [
        'release',
        'development',
        'sub-development 1',
        'sub-development 2',
        'sub-development 3',
        'sub-development 5',
        ]
}
SUB_DEV_5 = {
    'path':             "ViM (WIP)\\",
    'build line':       46,
    'sharing projects': [
        'release',
        'development',
        'sub-development 1',
        'sub-development 2',
        'sub-development 3',
        'sub-development 4',
        ]
}

# ViM Automated Testing project lines
AUTOMATION = {
    'path':             "Automated Testing\\",
    }
# builds
PROJECTS = {
    'release':          RELEASE,
    'release 3.2':      RELEASE_3_2,
    'release 3.3':      RELEASE_3_3,
    'release 3.4':      RELEASE_4_0,
    'development':      WIP,
    'automated testing':AUTOMATION,
    'sub-development 1':SUB_DEV_1,
    'sub-development 2':SUB_DEV_2,
    'sub-development 3':SUB_DEV_3,
    'sub-development 4':SUB_DEV_4,
    'sub-development 5':SUB_DEV_5,
    }

BUILDING = {
    'trigger path':         'action.html?add2Queue=%s',
    'builds': {
        'tartaros':             'bt55',
        'sisyphus':             'bt52',
        'dashboard':            'bt36',
        'development':          'bt%d'%WIP['build line'],
        'release':              'bt%d'%RELEASE['build line'],
        'release 3.2':          'bt%d'%RELEASE_3_2['build line'],
        'release 3.3':          'bt%d'%RELEASE_3_3['build line'],
        'release 4.0':          'bt%d'%RELEASE_4_0['build line'],
        'sub-development 1':    'bt%d'%SUB_DEV_1['build line'],
        'sub-development 2':    'bt%d'%SUB_DEV_2['build line'],
        'sub-development 3':    'bt%d'%SUB_DEV_3['build line'],
        'sub-development 4':    'bt%d'%SUB_DEV_4['build line'],
        'sub-development 5':    'bt%d'%SUB_DEV_5['build line'],
        },
    'agents': {
        'build agent 1':        4,
        'build agent 2':        3,
        'build server':         1,
        },
    'fields': {
        'trigger build':        'add2Queue',
        'agent':                'agentId'
    },
    'parameters': {
        'test name':            'TEST_NAME',
        'test plan':            'TEST_PLAN',
        'test plan id':         'TEST_PLAN_ID',
        'tags':                 'TAGS',
        'paths':                'PATHS',
        'inclusive':            'INCLUSIVE',
        'build':                'BUILD',
        'mode':                 'MODE',
        'number of sites':      'NUM_SITES',
        'events per site':      'NUM_EVENTS_PER_SITE',
        'clips per site':       'NUM_CLIPS_PER_SITE',
        'database type':        'DB_TYPE',
        'feature':              'FEATURE',
        'module':               'MODULE',
        'user story':           'USER_STORY',
        'test':                 'TEST',
        'test case':            'TEST_CASE',
        'test class':           'TEST_CLASS',
        },
    'test configurations': {
        'regression sanity': [
            ['test name', 'Sanity (Class 0) Regression Test'],
            ['test class', '0']
            ],
        'class 0': [
            ['test name', 'Sanity (Class 0) Regression Test'],
            ['test class', '0']
            ],
        'regression smoke': [
            ['test name', 'Smoke (Class 1) Regression Test'],
            ['test class', '1']
            ],
        'class 1': [
            ['test name', 'Smoke (Class 1) Regression Test'],
            ['test class', '1']
            ],
        'regression validation': [
            ['test name', 'Validation (Class 2) Regression Test'],
            ['test class', '2']
            ],
        'class 2': [
            ['test name','Validation (Class 2) Regression Test'],
            ['test class', '2']
            ],
        'regression functional': [
            ['test name', 'Functional (Class 3) Regression Test'],
            ['test class', '3']
            ],
        'class 3': [
            ['test name', 'Functional (Class 3) Regression Test'],
            ['test class', '3']
            ],
        'class 4': [
            ['test name', 'Class 4 Regression Test'],
            ['test class', '4']
            ],
        'class 5': [
            ['test name', 'Class 5 Regression Test'],
            ['test class', '5']
            ],
        'regression full': [
            ['test name', 'Full Regression Test'],
            ],
        },
    'vcs roots': {
        'release':              14,
        'development':          30,
        },
    'build to project': {
        'tartaros':             AUTOMATION,
        'robot':                AUTOMATION,
        'dashboard':            AUTOMATION,
        }
}