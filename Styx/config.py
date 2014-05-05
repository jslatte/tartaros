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

####################################################################################################
# Mapping ##########################################################################################
####################################################################################################
####################################################################################################

SDK_PATH = getcwdu() + "\\"

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