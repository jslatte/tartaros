####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from HTMLParser import HTMLParser

####################################################################################################
# Email Parser #####################################################################################
####################################################################################################
####################################################################################################

class StatusEmailParser(HTMLParser):

    def __init__(self, log):

        self.log = log

        HTMLParser.__init__(self)

    def convert_html_data_to_string(self,data):
        """ Convert an HTML data object from email to a valid string. """

        # define limits of actual HTML data
        htmlStart = None
        htmlEnd = None
        for datum in data:
            if '<body' in datum.lower(): htmlStart = data.index(datum)
            elif '</body' in datum.lower(): htmlEnd = data.index(datum)
        if htmlStart is not None and htmlEnd is not None:
            self.log.trace("Isolated HTML data.")
            htmlData = data[htmlStart:htmlEnd+1]
        else:
            self.log.error("Failed to isolated HTML data.")
            htmlData = data
            # collate HTML string from data
        htmlString = ''.join(htmlData)
        # clean up string
        htmlString = htmlString.replace('=0=','').replace('o:','').replace('=','')\
        .replace('0A','')
        # strip scripts and attributes from tags
        tags = ['body','div','li','ul','blockquote','p','table','td','tr','hr','th','span']
        rawData = htmlString.split('>')
        htmlData = []
        for line in rawData[:-1]:
            # search for tags and remove scripts/attr
            s = line
            for tag in tags:
                if '<%s '%tag in line:
                    line = '<%s'%tag
                    # re-append stripped carot
                s = (line+'>').strip()
                #print s
            htmlData.append(s)
            # rebuild HTML string
        htmlString = ''.join(htmlData)
        return htmlString

    def handle_starttag(self, tag, attrs):
        #log('<'+tag+'>')
        pass
    def handle_endtag(self, tag):
        #log('</'+tag+'>')
        pass
    def feed(self, data):
        """Feed data to the parser. """

        # data for tracking and return)
        self.data = {
            'reported':       False,
            'dvr health reported':    False,
            'camera health reported': False,
            'server health reported': False,
            'connection status reported': False,
            'no dvr events': False,
            'no camera events': False,
            'no detailed camera events': True,
            'no connection statuses': True,
            'dvr health summary': [],
            'dvr health extended': [],
            'camera health summary': [],
            'camera health extended': [],
            'connection status 24 hour report': [],
            'connection status 48 hour report': [],
            'connection status 72 hour report': [],
            'connection status never connected report': [],
            'storage space available report': [],
            }
        # tracking - used to determine which div/subsection of report is currently being
        #   processed. This allows the framework to lump the correct results together.
        self.tracking = [None,None,None]
        self.subtracking = False
        # counter - used to determine how many data points have been processed for a section.
        #   This allows consolidation of data under the parent element (i.e., site name)
        self.counter = 0
        # clipboard - a temporary list used to store data before it is consolidated and can
        #   be pushed to the results{} dict
        self.clipboard = []
        self.clipboard2 = []
        # original code (from built-in module)
        self.rawdata = self.rawdata + data
        self.goahead(0)
        # reset tracking and clipboard
        self.reset_tracking()
        self.clear_clipboard()
        # return
        return self.data

    def handle_data(self, data):
        #log(data)
        # no events messages
        noDVREventsMsg = 'There were no health events reported for any DVR during this time period.'
        noCamEventsMsg = 'There were no camera events reported for any DVR during this time period.'
        noDetCamHthMsg = 'There was no detailed summary of the reported events.'
        noConnStatMsg  = 'There was no connection status reported for any DVR.'
        # check data for report header details and capture
        # Report Time
        if 'report for' in data.lower():
            self.log.trace("Report time found.")
            self.data['reported'] = True
            # parse start and end time for report period
            s = data.lower().split('report for')[1].split('through')
            self.data['report period start'] = s[0].strip()
            self.data['report period end']   = s[1].split('(')[0].strip()
        # DVR Health Report
        elif 'dvr health' in data.lower():
            self.log.trace("DVR Health report found.")
            self.data['dvr health reported'] = True
            # set tracking for DVR Health Report flag
            self.tracking = ['dvr health report',None,None]
        elif 'reporting health events' in data.lower():
            self.log.trace("DVR Health summary report found.")
            # set tracking for DVR Health summary report flag
            self.tracking[1] = 'dvr health summary'
            self.counter = 0
        elif noDVREventsMsg.lower() in data.lower():
            self.log.trace("No health events reported.")
            self.data['no dvr events'] = True
        # Camera Health Report
        elif 'camera health' in data.lower():
            self.log.trace("Camera Health report found.")
            self.data['camera health reported'] = True
            # set tracking for Camera Health Report flag
            self.tracking = ['camera health report',None,None]
        elif 'reporting camera events' in data.lower():
            self.log.trace("Camera Health summary report found.")
            # set tracking for Camera Health summary report flag
            self.data['no detailed camera events'] = False
            self.tracking[1] = 'camera health summary'
            self.counter = 0
        elif 'camera events by site' in data.lower():
            self.log.trace("Camera Health extended report found.")
            # set tracking for Camera Health extended report flag
            self.tracking[1] = 'camera health extended'
            self.counter = 0
        elif noCamEventsMsg.lower() in data.lower():
            self.log.trace("No camera events reported.")
            self.data['no camera events'] = True
        elif noDetCamHthMsg.lower() in data.lower():
            self.log.trace("No detailed camera events reported.")
            self.data['no detailed camera events'] = True
        # Connection Status Report
        elif 'connection status' in data.lower():
            self.log.trace("Connection Status report found.")
            self.data['connection status reported'] = True
            # set tracking for Connection Status report flag
            self.tracking = ['connection status report',None,None]
        elif 'not connected between 24' in data.lower():
            self.log.trace("Connection Status 24-48 hour report found.")
            self.data['no connection statuses'] = False
            self.tracking[1] = '24 hour report'
            self.counter = 0
        elif 'not connected between 48' in data.lower():
            self.log.trace("Connection Status 48-72 hour report found.")
            self.data['no connection statuses'] = False
            self.tracking[1] = '48 hour report'
            self.counter = 0
        elif 'not connected for more than 72' in data.lower():
            self.log.trace("Connection Status 72+ hour report found.")
            self.data['no connection statuses'] = False
            self.tracking[1] = '72 hour report'
            self.counter = 0
        elif 'never connected' in data.lower():
            self.log.trace("Connection Status never connected report found.")
            self.data['no connection statuses'] = False
            self.tracking[1] = 'never connected report'
        elif noConnStatMsg.lower() in data.lower():
            self.log.trace("No connection status(es) reported.")
            self.data['no connection statuses'] = True
        # ViM Server Health Report
        elif 'vim server health' in data.lower():
            self.log.trace("ViM Server Health report found.")
            self.data['server health reported'] = True
            self.tracking = ['server health report',None,None]
            self.counter = 0
        # Subreport Details
        else: self.handle_subreport_data(data)

    def handle_subreport_data(self,data):
        """ Check for and capture important sub-report details from data. """

        # DVR Health Report
        if self.tracking[0] == 'dvr health report':
            # handle summary report
            if self.tracking[1] == 'dvr health summary':
                if self.get_starttag_text().lower() == '<td>':
                    if self.counter is 0:
                        # parse site name and increment counter
                        self.counter += 1
                        data = data.strip()
                    elif self.counter is 1:
                        # parse number of events and increment counter
                        self.counter = 0
                        data = int(data)
                        # append to clipboard
                    self.clipboard.append(data)
                    # pushed clipboard if complete
                    if len(self.clipboard) is 2 and self.counter is 0:
                        self.data['dvr health summary'].append(self.clipboard)
                        self.clear_clipboard()
        # Camera Health Report
        elif self.tracking[0] == 'camera health report':
            # handle summary report
            if self.tracking[1] == 'camera health summary':
                if self.get_starttag_text().lower() == '<td>':
                    if self.counter is 0:
                        # parse site name and increment counter
                        self.counter += 1
                        data = data.strip()
                    elif self.counter is 1:
                        # parse number of events and increment counter
                        self.counter = 0
                        data = int(data)
                        # append to clipboard
                    self.clipboard.append(data)
                    # pushed clipboard if complete
                    if len(self.clipboard) is 2 and self.counter is 0:
                        self.data['camera health summary'].append(self.clipboard)
                        self.clear_clipboard()
            # handle detailed report
            elif self.tracking[1] == 'camera health extended':
                if self.get_starttag_text().lower() == '<td>':
                    if self.counter is 0:
                        # parse site name and increment counter
                        self.counter += 1
                    elif self.counter is 1:
                        # parse camera and increment counter
                        self.counter += 1
                    elif self.counter is 2:
                        # parse event and reset counter
                        self.counter += 1
                    elif self.counter is 3:
                        # parse number of events and reset counter
                        self.counter = 0
                        # append to clipboard
                    self.clipboard.append(data.strip())
                    # pushed clipboard if complete
                    if len(self.clipboard) is 4 and self.counter is 0:
                        self.data['camera health extended'].append(self.clipboard)
                        self.clear_clipboard()
        # Connection Status Report
        elif self.tracking[0] == 'connection status report':
            # handle 24, 48, and 72 hour reports
            if self.tracking[1] == '24 hour report'\
               or self.tracking[1] == '48 hour report'\
            or self.tracking[1] == '72 hour report':
                if self.get_starttag_text().lower() == '<td>'\
                or self.get_starttag_text() == '<p>':
                    if self.counter is 0:
                        # data should be site name
                        self.counter += 1
                    elif self.counter > 0:
                        # data should be last communicated time
                        self.counter = 0
                        # append data to clipboard
                    self.clipboard.append(data.strip())
                    # push clipboard if complete
                    if len(self.clipboard) is 2 and self.counter is 0:
                        self.data['connection status %s'%self.tracking[1]].append(self.clipboard)
                        self.clear_clipboard()
            # handle never connected report
            elif self.tracking[1] == 'never connected report':
                if self.get_starttag_text() == '<li>'\
                or self.get_starttag_text() == '<b>':
                    # data should be site name
                    siteName = data.strip()
                    # append to report
                    self.data['connection status never connected report'].append(siteName)
        # Server Health Report
        elif self.tracking[0] == 'server health report':
            if self.get_starttag_text().lower() == '<p>'\
            or self.get_starttag_text().lower() == '<td>':
                if self.counter is 0:
                    # parse drive and increment counter
                    self.counter += 1
                    data = data.strip()
                elif self.counter is 1:
                    # parse amount of space and increment counter
                    self.counter = 0
                    data = data.strip()
                    # append to clipboard
                self.clipboard.append(data)
                # pushed clipboard if complete
                if len(self.clipboard) is 2 and self.counter is 0:
                    self.data['storage space available report'].append(self.clipboard)
                    self.clear_clipboard()

    def reset_tracking(self):
        """ Reset all current tracking details. """

        # reset tracking
        self.tracking = None
        self.subtracking = False
        self.counter = 0

    def clear_clipboard(self):
        """ Clear all content from clipboard. """

        # reset clipboard
        self.clipboard = []
        self.clipboard2 = []