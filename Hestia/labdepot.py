####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

gateway = "172.22.48."
testGateway = "172.22.0."
depotGateway = "172.100.1."

####################################################################################################
# Automated Testing Depot DVRs #####################################################################
####################################################################################################
####################################################################################################

class Depot131():

    def __init__(self):
        # properties
        self.name = "DEPOT 131"
        self.ipAddress = gateway+"131"
        self.serial = None
        self.driveSerial = None
        self.model = "MR4"
        self.firmware = None
        self.account = ["robot","12345"]

class Depot132():

    def __init__(self):
        # properties
        self.name = "DEPOT 132"
        self.ipAddress = gateway+"132"
        self.serial = None
        self.driveSerial = None
        self.model = "MR4"
        self.firmware = None
        self.account = ["robot","12345"]

class Depot133():

    def __init__(self):
        # properties
        self.name = "DEPOT 133"
        self.ipAddress = gateway+"133"
        self.serial = None
        self.driveSerial = None
        self.model = "MR8"
        self.firmware = None
        self.account = ["robot","12345"]

class Depot134():

    def __init__(self):
        # properties
        self.name = "DEPOT 134"
        self.ipAddress = gateway+"134"
        self.serial = None
        self.driveSerial = None
        self.model = "MR8"
        self.firmware = None
        self.account = ["robot","12345"]

class Depot135():

    def __init__(self):
        # properties
        self.name = "DEPOT 135"
        self.ipAddress = gateway+"135"
        self.serial = '00:03:22:0A:7A:68'
        self.driveSerial = '6VP0EN1Q'
        self.model = "MRH4"
        self.firmware = "1.4.0"
        self.account = ["robot","12345"]

class Depot136():

    def __init__(self):
        # properties
        self.name = "DEPOT 136"
        self.ipAddress = gateway+"136"
        self.serial = '00:03:22:0A:7A:72'
        self.driveSerial = 'S2WFMYQM'
        self.model = "MRH4"
        self.firmware = "1.5.0"
        self.account = ["robot","12345"]

class Depot137():

    def __init__(self):
        # properties
        self.name = "DEPOT 137"
        self.ipAddress = gateway+"137"
        self.serial = '00:03:22:07:8F:93'
        self.driveSerial = '9VS35R41'
        self.model = "MRH8"
        self.firmware = "1.4.0"
        self.account = ["robot","12345"]

class Depot138():

    def __init__(self):
        # properties
        self.name = "DEPOT 138"
        self.ipAddress = gateway+"138"
        self.serial = '00:03:22:07:8F:F7'
        self.driveSerial = 'JK1171YAG85BES'
        self.model = "MRH8"
        self.firmware = "1.5.0"
        self.account = ["robot","12345"]

class Depot139():

    def __init__(self):
        # properties
        self.name = "DEPOT 139"
        self.ipAddress = gateway+"139"
        self.serial = '00:03:22:07:9F:44'
        self.driveSerial = 'WD-WMAWZ0179768'
        self.model = "MRH16"
        self.firmware = "1.4.0"
        self.account = ["robot","12345"]

class Depot140():

    def __init__(self):
        # properties
        self.name = "DEPOT 140"
        self.ipAddress = gateway+"140"
        self.serial = '00:03:22:07:11:06'
        self.driveSerial = 'Z1F2PT4T'
        self.model = "MRH16"
        self.firmware = "1.5.0"
        self.account = ["robot","12345"]

####################################################################################################
# Test Depot DVRs ##################################################################################
####################################################################################################
####################################################################################################

class TDepot1():

    def __init__(self):
        # properties
        self.name = "T-DEPOT 1"
        self.ipAddress = testGateway+"1"
        self.serial = '00:00:00:00:00:01'
        self.account = ["robot","12345"]
        self.model = "MR8"

class TDepot2():

    def __init__(self):
        # properties
        self.name = "T-DEPOT 2"
        self.ipAddress = testGateway+"2"
        self.serial = '00:00:00:00:00:02'
        self.account = ["robot","12345"]
        self.model = "MR8"

class TDepot3():

    def __init__(self):
        # properties
        self.name = "T-DEPOT 3"
        self.ipAddress = testGateway+"3"
        self.serial = '00:00:00:00:00:03'
        self.account = ["robot","12345"]
        self.model = "MR8"

class TDepot4():

    def __init__(self):
        # properties
        self.name = "T-DEPOT 4"
        self.ipAddress = testGateway+"4"
        self.serial = '00:00:00:00:00:04'
        self.account = ["robot","12345"]
        self.model = "MR8"

class TDepot5():

    def __init__(self):
        # properties
        self.name = "T-DEPOT 5"
        self.ipAddress = testGateway+"5"
        self.serial = '00:00:00:00:00:05'
        self.account = ["robot","12345"]
        self.model = "MR8"

####################################################################################################
# Lab Depot DVRs ###################################################################################
####################################################################################################
####################################################################################################

class LAB_DEPOT_DVR():

    def __init__(self):
        # properties
        self.name = "LAB DEPOT %s"
        self.ipAddress = depotGateway+"%s"
        self.serial = None
        self.account = ["admin",""]
        self.model = None
        self.driveSerial = None
        self.firmware = None
        self.ID = 0

        # set ID
        self.set_ID()

        # update attributes
        self.update_attributes()

    def set_ID(self):
        self.ID = self.__class__.__name__.replace('Depot', '')

    def update_attributes(self):
        self.name = "LAB DEPOT %s" % self.ID
        self.ipAddress = depotGateway+"%s" % self.ID


class LAB_DEPOT_DVR_v2(LAB_DEPOT_DVR):

    def update_attributes(self):
        self.name = "LAB DEPOT %s" % self.ID
        self.ipAddress = gateway+"%s" % self.ID


class Depot3(LAB_DEPOT_DVR): pass


class Depot4(LAB_DEPOT_DVR): pass


class Depot5(LAB_DEPOT_DVR): pass


class Depot9(LAB_DEPOT_DVR): pass


class Depot10(LAB_DEPOT_DVR): pass


class Depot13(LAB_DEPOT_DVR): pass


class Depot14(LAB_DEPOT_DVR): pass


class Depot15(LAB_DEPOT_DVR): pass


class Depot17(LAB_DEPOT_DVR): pass


class Depot19(LAB_DEPOT_DVR): pass


class Depot20(LAB_DEPOT_DVR): pass


class Depot121(LAB_DEPOT_DVR_v2): pass


class Depot123(LAB_DEPOT_DVR_v2): pass


class Depot124(LAB_DEPOT_DVR_v2): pass


class Depot125(LAB_DEPOT_DVR_v2): pass


class Depot127(LAB_DEPOT_DVR_v2): pass


class Depot128(LAB_DEPOT_DVR_v2): pass


class Depot130(LAB_DEPOT_DVR_v2): pass

####################################################################################################
# Testing DVR Map ##################################################################################
####################################################################################################
####################################################################################################


### Clip Downloading ###############################################################################
####################################################################################################

ClipDownloadingMainDepot = Depot140()
ClipDownloadingAltDepot1 = Depot138()
ClipDownloadingAltDepot2 = Depot136()

### Drive Status and History #######################################################################
####################################################################################################

# drive swapping
DriveSwappingMainDepot = Depot134()
DriveSwappingAltDepot1 = Depot132()
DriveSwappingAltDepot2 = Depot133()
# unknown drive swapping
UnknownDriveSwappingMainDepot = Depot132()
# dvr status
DVRStatusMainDepot = Depot140()
DVRStatusAltDepot1 = Depot138()
DVRStatusAltDepot2 = Depot136()

### Event Downloading ##############################################################################
####################################################################################################

AlarmEventDownloadingMainDepot = Depot140()
HealthEventDownloadingDepot = Depot140()
VideoLossEventDownloadingDepot = Depot140()
MultipleVideoLossEventsDownloadingDepot = Depot140()
DiskTemperatureEventDownloadingDepot = Depot140()

### Firmware Testing ###############################################################################
####################################################################################################

MRH_1_3_0_MainDepot = None
MRH_1_2_2_MainDepot = Depot140()
MR_1_2_0_MainDepot  = None

### GPS Downloading ################################################################################
####################################################################################################

# main
GPSDownloadingMainDepot = Depot140()
GPSAltDownloadingDepot1 = Depot138()
GSPAltDownloadingDepot2 = Depot136()
# drive swapping
GPSMRwithGPSData    = Depot134()
GPSMRwithoutGPSData = Depot133()
# firmware versions
GPSLatestFirmwareDepot = None
GPSOldestSupportFirmwareDepot = None
# dvr models
GPSMR4Model = Depot132()
GPSMR8Model = Depot134()
GPSMRH4Model = Depot136()
GPSMRH8Model = Depot138()
GPSMRH16Model = Depot140()

### DVR Model Testing ##############################################################################
####################################################################################################

MR4MainDepot = Depot132()
MR8MainDepot = Depot134()
MRH4MainDepot = Depot136()
MRH8MainDepot = Depot138()
MRH16MainDepot = Depot140()

### Dummy DVRs #####################################################################################
####################################################################################################

DummyDVRMainDepot = TDepot1()
DummyDVRAltDepot1 = TDepot2()
DummyDVRAltDepot2 = TDepot3()
DummyDVRAltDepot3 = TDepot4()
DummyDVRAltDepot4 = TDepot5()