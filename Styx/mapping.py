####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

from os import getcwdu
from ctypes import Structure, Array, c_uint64
from ctypes import c_ubyte, c_uint, c_void_p, c_int, c_char, c_ulong, c_ushort, c_long, c_bool

####################################################################################################
# IDIS Structures ##################################################################################
####################################################################################################
####################################################################################################


class PARAM_DISCONNECT(Structure):

    _fields_ = [("reason", c_uint),
                ("attachment", c_void_p)]

    def send(self):
        return buffer(self)[:]

class PARAMS_LOGINFO(Structure):
    # MAX_CAMERA = 16
    # MAX_LEN_LOG_LABEL = 32
    # MAX_TRANS_NUM = 16

    _fields_ = [#('_type_disk', c_int32),
                ('_seqNum', c_int),
                ('_version', c_char * 2),
                ('_eventType', c_char),
                ('_eventId', c_char),
                ('_time', c_ulong),
                ('_msec', c_int),
                ('_camId', c_uint),
                ('_preDwell', c_ushort * 16 ), #MAX_CAMERA),
                ('_postDwell', c_ushort * 16), # MAX_CAMERA),
                ('_label', c_char * 32), #MAX_LEN_LOG_LABEL),
                ('_transNum', c_char * 17), # (MAX_TRANS_NUM + 1)),
                ('_level', c_char),
                ('_reserved', c_char * 2)]

    def camId2IntBasedZero(self):
        for i in range(self.MAX_CAMERA):
            if self._camId & (1 << i):
                return i
        return -1

    def send(self):
        return buffer(self)[:]

class EVENT_QUERY_CONDITION(Structure):
    # MAX_SYS_CAMERA32 = 32

    _fields_ = [('seqNum', c_int),
                ('begin', c_long),
                ('end', c_long),
                ('alarmIn', c_bool * 32), # MAX_SYS_CAMERA32),
                ('motion', c_bool * 32), #MAX_SYS_CAMERA32),
                ('objectTracker', c_bool * 32), #MAX_SYS_CAMERA32),
                ('videoLoss', c_bool * 32), #MAX_SYS_CAMERA32),
                ('videoBlind', c_bool * 32), #MAX_SYS_CAMERA32),
                ('textIn', c_bool * 32), #MAX_SYS_CAMERA32),
                ('cameras', c_bool * 32), #MAX_SYS_CAMERA32),
                ('system', c_bool * 32), #MAX_SYS_CAMERA32),
                ('reload', c_bool),
                ('alarmDwellTime', c_int),
                ('motionDwellTime', c_int),
                ('objectDwellTime', c_int)]

    def __init__(self):
        self.seqNum = -1
        self.begin = -1
        self.end = -1
        for i in range(32):
            self.alarmIn[i] = True
            self.motion[i] = False
            self.objectTracker[i] = False
            self.videoLoss[i] = True
            self.videoBlind[i] = True
            self.textIn[i] = False
            self.cameras[i] = False
            self.system[i] = True
        self.reload = True
        self.alarmDwellTime = 10
        self.motionDwellTime = 10
        self.objectDwellTime = 10

class SYSTEM_CHECK(Structure):
    _fields_ = [('camera', c_ubyte * 16),
                ('alarm', c_ubyte * 16),
                ('record', c_long)]
    def send(self):
        return buffer(self)[:]

class DISK_STATUS(Structure):
    _fields_ = [('bad', c_ubyte),
                ('overTemperature', c_ubyte),
                ('smartError', c_ubyte)]
    def send(self):
        return buffer(self)[:]

class STATUS_INFO(Structure):
    _fields_ = [('motion', c_ubyte * 16),
                ('alarm_in', c_ubyte * 16),
                ('text_in', c_ubyte * 16),
                ('sys_check', SYSTEM_CHECK),
                ('recording', c_ubyte * 16),
                ('alarm_out', c_ubyte * 16),
                ('record_begin', c_long),
                ('record_end', c_long),
                ('playback', c_int),
                ('version', c_char * 24),
                ('nAlarmOut', c_int),
                ('objectTracker', c_ubyte * 16),
                ('videoBlind', c_ubyte * 16),
                ('diskStatus', DISK_STATUS * 16),

                # for 32 channels:
                ('motion32', c_ubyte * 16),
                ('alarm_in32', c_ubyte * 16),
                ('recording32', c_ubyte * 16),
                ('sys_check32', SYSTEM_CHECK),
                ('struct_size', c_uint),
                ('packet_version', c_uint),
                ('alarm_out32', c_ubyte * 16),
                ('terrorism', c_ubyte * 32),
                ('nCameraNum', c_int),
                ('nSensorNum', c_int),
                ('nPosNum', c_int),
                ('nAudioNum', c_int),
                ('reserved', c_int * 4),
                ('audio_in', c_ubyte * 32),
                ('videoBlind32', c_ubyte * 16),
                ('reserved1', c_ubyte * 32),
                ('reserved2', c_ubyte * 32),
                ('reserved3', c_ubyte * 256)
                ]
    def send(self):
        return buffer(self)[:]

class SYSTEM_LOG_EX(Structure):
    _fields_ = [('time', c_long),
                ('type', c_int),
                ('data', c_char * 32)]
    def send(self):
        return buffer(self)[:]

class VERSION(Array):
    _type_ = c_char
    _length_ = 5
    def send(self):
        return buffer(self)[:]

class VERSION_INFO(Structure):
    _fields_ = [('classInfo', c_int),
                ('typeInfo', c_int),
                ('version', c_char * 5)]
    def send(self):
        return buffer(self)[:]

class DISK_SMART_ATTRIBUTE(Structure):
    _fields_ = [('id', c_ubyte),
                ('attributeName', c_char * 48),
                ('current', c_ubyte),
                ('worst', c_ubyte),
                ('threshold', c_ubyte)]
    def send(self):
        return buffer(self)[:]

class DISK_INFO(Structure):
    _fields_ = [('diskModel', c_char * 48),
                ('diskSerial', c_char * 48),
                ('diskSmartAttribute', DISK_SMART_ATTRIBUTE * 32),
                ('freespace', c_uint64)]
    def send(self):
        return buffer(self)[:]

class EVENT_LOG_EX(Structure):
    _fields_ = [('time', c_ulong),
                ('type', c_char),
                ('label', c_char * 32)]
    def send(self):
        return buffer(self)[:]

class REMOTE_LOG_EVENT(Structure):
    _fields_ = [('MAX_LEN_DATA', c_uint),
                ('MAX_LEN_TYPESTRING', c_uint),
                ('_type', c_int),
                ('_time', c_long),
                ('_typeString', c_char * 128),
                ('_label', c_char * 32)]

    def _init_(self):
        self.MAX_LEN_DATA = 32
        self.MAX_LEN_TYPESTRING = 128

    def send(self):
        return buffer(self)[:]

####################################################################################################
# Mapping ##########################################################################################
####################################################################################################
####################################################################################################

SDK_PATH = getcwdu() + "\\"

CONNECTION_STATE_TO_ID = {
    'error':            -1,
    'indeterminant':    -1,
    'connected':        0,
    'disconnected':     1,
}

CONNECTION_ID_TO_STATE = {
    '-1':   'unknown',
    '0':    'connected',
    '1':    'disconnected',
}

CALLBACK_ADMIN = {
    'ONCONNECTED'                       :0,
    'ONDISCONNECTED'                    :1,
    'STATUSLOADED'                      :2,
    'SYSTEMLOGLOADED'                   :3,
    'EVENTLOGLOADED'                    :4,
    'EMERGENCYINFO'                     :5,
    'EMERGENCYINFOEX'                   :6,
    'EMERGENCYINFOIDR'                  :7,
    'SETUPDLLLOADED'                    :8,
    'REMOTECONFIGURATION'               :9,
    'REMOTECONFIGURATION_RESULT'        :10,
    'DEVICEDATETIMELOADED'              :11,
    'SUCCESSSETDEVICEDATETIME'          :12,
    'REMOTEDEVICEINFOLOADED'            :13,
    'SETUPDLLAPPLYSUCCESS'              :14,
    'SETUPDLLAPPLYFAIL'                 :15,
    'SETUPDLLLOADPROGRESS'              :16,
    'MAX_LISTENER'                      :17
}

CALLBACK_WATCH = {
    'ONCONNECTED'                       :0,
    'ONDISCONNECTED'                    :1,
    'FRAMELOADED'                       :2,
    'EVENTLOADED'                       :3,
    'STATUSLOADED'                      :4,
    'RECVPTZPRESET'                     :5,
    'RECVG2PTZPRESET'                   :6,
    'RECVPTZPRESETIDR'                  :7,
    'RECVIDRTEXTIN'                     :8,
    'RECVIDRTEXTINDATA'                 :9,
    'IDRTITLECHANGED'                   :10,
    'RECVTEXTIN'                        :11,
    'RECVPTZADVMENU'                    :12,
    'IDRSTATUSLOADED'                   :13,
    'DEVICESTATUSLOADED'                :14,
    'AUDIOOUTOPENRESULT'                :15,
    'AUDIOCAPTURED'                     :16,
    'AUDIOSTREAMCLOSED'                 :17,
    'AUDIOCAPTURESTARTED'               :18,
    'AUDIOCAPTUREFINISHED'              :19,
    'MAX_LISTENER'                      :20
}

CALLBACK_STORAGE = {
    'ONCONNECTED'                       :0,
    'ONDISCONNECTED'                    :1,
    'ONOPENED'                          :2,
    'ONCLOSED'                          :3,
    'ONRECORDEDDATELOADED'              :4,
    'ONRECORDEDHOURLOADED'              :5,
    'ONRECORDEDTIMELOADED'              :6,
    'ONRECEIVECLIPDATASCOPE'            :7,
    'ONRECEIVECLIPDATASCOPEEND'         :8,
    'ONSCOPELISTLOADED'                 :9,
    'ONSPOTLISTLOADED'                  :10,
    'ONRECEIVEEVENTLOGLIST'             :11,
    'ONRECEIVEEVENTLOG'                 :12,
    'ONRECEIVETEXTINLIST'               :13,
    'ONRECEIVETEXTIN'                   :14,
    'ONRECEIVEGPSDATALIST'              :15,
    'ONRECEIVEGPSDATA'                  :16,
    'ONFRAMELOADED'                     :17,
    'ONNOFRAMELOADED'                   :18,
    'ONENDOFPLAY'                       :19,
    'ONPLAYSPEEDCHANGED'                :20,
    'ONRECEIVECLIPCOPYSCOPELIST'        :21,
    'ONRECEIVECANCELCLIPCOPY'           :22,
    'ONRECEIVEMEASURECLIPCOPYSIZE'      :23,
    'ONRECEIVECLIPCOPYSIZE'             :24,
    'ONRECEIVECLIPCOPY'                 :25,
    'ONRECEIVEDEVICELIST'               :26,
    'ONRECEIVEDEVICEINFO'               :27,
    'ONRECEIVEDCLIPPASSWORDUSED'        :28,
    'ONRECEIVEDCLIPWRONGPASSWORD'       :29,
    'MAX_LISTENER'                      :30
}

PRODUCT_INFO = {
    1: c_ubyte,
    2: c_ubyte,
    3: c_ubyte,
    4: c_ubyte,
    5: c_ubyte,
    6: c_ubyte,
    7: c_bool,
    8: c_bool,
    21: c_char,
    22: c_char,
    23: c_char,
    24: c_bool,
    25: c_bool,
    26: c_bool,
    27: c_bool,
    28: c_ushort,
    29: c_ushort,
    30: c_ushort,
    31: c_ushort,
    32: c_uint,
    33: c_ubyte,
    34: c_char,
    35: c_ubyte,
    36: c_bool,
    37: c_ubyte
}

CLIP_PLAYER_TYPE = {
    'CLIP_PLAYER' :0,
    'G2CLIP_PLAYER' :1
}

CLIP_PLAYER_SOURCE = {
    'FROM_CURRENT_PROCESS'  :0,
    'FROM_DEFINED_PATH'     :1
}

RETURN_STATUS_ID_TO_REASON = {
    '0': "unknown reason",
    '1': "normal logout (base->post)",
    '2': "Site Busy - deny connection because all of server channels are used (base<-post)",
    '3': "invalid product version (base->post)",
    '4': "Invalid User ID or Password (base<-post)",
    '5': "Disconnected - admin close the current connection forcibly (base<-post)", #ADMIN_CLOSE
    '6': "Diconnected - timeout (base<-post)",	#ADMIN_TIMEOUT
    '7': "Site Shutdown - post system shutdown (base<-post)",	#SYS_SHUTDOWN
    '8': "Site Busy - can't connect - all of my network channels are used",	#NO_CHANNEL
    '10': "Site Not Responding - can't connect - no server module (sock. err=10061)",	#NO_SERVER
    '11': "Network is down - network is down (sock. err=10050)",	#NET_DOWN
    '12': "Site Not Available - network is unreachable (sock. err=10051)",	#NET_UNREACHABLE
    '13': "Site Not Available - connection time out (sock. err=10060)",	#CONN_TIMEOUT
    '14': "Disconnected- connection reset by peer (sock. err=10054)",	#CONN_RESET
    '15': "Site Not Available - host is down (sock. err=10064)",	#HOST_DOWN
    '16': "Site Not Available - no route to host (sock. err=10065)",	#HOST_UNREACHABLE
    '17': "Connection was aborted - connection aborted (sock. err=10053)",	#CONN_ABORTED
    '20': "Connection was canceled by user - connection has been canceled by user.",	#CONN_CANCEL
    '21': "Site Not Available - the peer host does not respond.",	#NET_NORESPONSE
    '22': "Network is down, too noisy - network is too noisy.",	#NET_NOISY
    '23': "Network is down, queue overflow - sending queue overflow.",	#SEND_OVERFLOW
    '24': "Invalid OEM number - invalid oem number (base->post)",	#INVALID_OEM
    '25': "User not authorized for search",	#NO_AUTHORITY
    '26': "Port in use - the port is already in use.",	#PORT_USED
    '27': "SSL connection failed",	#SSL_CONNECTION_FAILED
    '28': "Network timed out",	#NET_TIMEOUT
    '29': "Host timed out",	#HOST_TIMEOUT
    '30': "Host cannot support RTP over TCP", #NOT_SUPPORT_RTP_TCP
}