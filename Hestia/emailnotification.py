###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from mapping import HESTIA
from imaplib import IMAP4_SSL
from time import sleep
from HTMLParser import HTMLParser

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

IMAP_ADDRESS = 'by2prd0810.outlook.com'
IMAP_USER = 'vim@avt-usa.net'
IMAP_PSWD = 'p@ssw0rd!'

####################################################################################################
# Email Notification ###############################################################################
####################################################################################################
####################################################################################################

class EmailNotification():
    """ Sub-library for Exchange server email interaction and parsing.
    """

    def verify_clip_download_notification_email_received(self, testcase=None):
        """ Verify that a clip download notification email was received.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
        """

        self.log.debug("Verifying clip download notification email received ...")
        result = {'successful': False, 'verified': False}

        try:
            # verify email received and return data
            data = self.verify_email_received('Clip Download Notification', 120)
            found = data['verified']
            email = data['email']

            if found:
                if "download succeeded" in email[1].lower():
                    self.log.trace("'Download succeeded' found in email subject.")
                    result['verified'] = True
                else:
                    self.log.error("'Download succeeded' not found in email subject '%s'." % email[1])

        except BaseException, e:
            self.handle_exception(e, operation="verify clip download notification email received")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def connect_to_exchange_server(self, testcase=None):
        """ Connect to exchange server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Connecting to exchange server ...")
        result = {'succeeded':False}

        # pass if connection already established
        if self.imap_connection is not None:
            self.log.trace("Connection already established. Resetting ...")
            try: self.disconnect_from_exchange_server()
            except BaseException: pass

        # define connection
        try:
            self.imap_connection = IMAP4_SSL(IMAP_ADDRESS)
            response = self.imap_connection.login(IMAP_USER, IMAP_PSWD)
            self.log.trace("IMAP Response: %s" % str(response))
            # check server response
            if response[0] == "OK" and response[1][0] == "LOGIN completed.":
                self.log.trace("Logged in to exchange server.")
                result['succeeded'] = True
            else:
                self.log.warn("Failed to log in to exchange server.")

        except BaseException, e:
            self.handle_exception(e, operation="connect to exchange server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def disconnect_from_exchange_server(self, testcase=None):
        """ Disconnect from exchange server.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Disconnecting from exchange server ...")
        result = {'successful': False}

        try:
            # close handle to mailbox (if one exists)
            if self.imap_handle is None: pass
            else: self.imap_connection.close()
            # disconnect only if there is an active connection
            if self.imap_connection is None:
                self.log.trace("No connection found.")
                pass
            else:
                self.imap_connection.logout()

            self.log.trace("Disconnected from exchange server.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="disconnect from exchange server")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def open_mailbox(self, mailbox='inbox', readonly=True, testcase=None):
        """ Open specific mailbox.
        If 'readonly' is True, fetched emails will not be marked as read/seen.
        INPUT
            mailbox: the name of the mailbox to open (on imap server).
            readonly: whether the fetched emails should be marked as read/seen.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Opening %s ..." % mailbox)
        result = {'succeeded': False}

        try:
            # state if in readonly mode
            if readonly: self.log.trace("Opening as readonly ...")

            # open specified mailbox
            if mailbox.lower() == 'inbox':
                self.imap_connection.select("INBOX", readonly=readonly)
                self.log.trace("Mailbox %s opened." % mailbox)
                result['succeeded'] = True
            else:
                self.log.error("Invalid mailbox %s specified." % mailbox)


        except BaseException, e:
            self.handle_exception(e, operation="open mailbox %" % mailbox)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def send_test_email(self,type="ViM Status Report"):
        """ Send specified type of test email.
        NOTE: Does not work, currently. """

        self.log.debug("Sending %s test email ..."%type)

        # import modules
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        # header information
        sender      = "vim@avt-usa.net"
        recipient   = "vim@avt-usa.net"
        # create message container - the correct MIME type is multipart/alternative
        msg = MIMEMultipart('multipart')
        msg['Subject']  = "ViM Status Report"
        msg['From']     = sender
        msg['To']       = recipient
        # create body of message
        html = open("ViM\Email\ViMStatusReport.htm")
        body = ''
        for line in html:
            body += line
        body = MIMEText(body,'html')
        # attach body to email
        msg.attach(body)
        # send the message via local SMTP server
        connection = smtplib.SMTP('pod51019.outlook.com','587')
        connection.ehlo()
        connection.starttls()
        connection.ehlo()
        connection.login(sender,'p@ssw0rd!')
        connection.sendmail(sender,recipient,msg.as_string())

    def clean_up_mailbox(self, testcase=None):
        """ Read all emails in mailbox to create clean test environment.
        INPUT
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
        """

        self.log.debug("Cleaning mailbox ...")
        result = {'successful': False}

        try:
            # read all mail
            emailIDs = self.return_emails_with_subject("ALL")['email ids']
            self.fetch_email_data_for_ids(emailIDs)

            self.log.trace("Cleaned mailbox.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="clean mailbox")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def return_emails_with_subject(self, subject, testcase=None):
        """ Return all emails with specified subject.
        INPUT
            subject: type of subject for which to return emails.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            email ids: a list of the ids for the emails returned.
        """

        self.log.debug("Returning emails with subject %s ..." % subject)
        result = {'successful': False, 'email ids': []}

        try:
            if subject.lower() == 'all':
                typ, data = self.imap_connection.search(None, "(UNSEEN)")
            else:
                typ, data = self.imap_connection.search(None, '(UNSEEN SUBJECT "%s")'%subject)
            # determine all IDs of emails found in search
            result['email ids'] = str(data).strip("['").strip("']").split()
            self.log.trace("%d email(s) found." % len(result['email ids']))

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return emails with subject %s" % subject)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def fetch_email_data_for_ids(self, email_ids, testcase=None):
        """
        INPUT
            email ids: a list of email ids for which to fetch the data.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            emails: list of email data objects.
        """

        self.log.debug("Fetch email data for email ids ...")
        result = {'successful': False, 'emails': []}

        try:
            for email_id in email_ids:
                subject = None
                date = None
                # fetch email data
                typ, data = self.imap_connection.fetch(email_id, '(RFC822)')
                #log(str(data))
                data = data[0][1].splitlines()
                #for line in data:
                #    log(line)
                for line in data:
                    if "Subject:" in line: subject = line.split('Subject:')[1].strip()
                    elif "Date:" in line: date = line.split('Date:')[1].strip()
                    # append relevant data to parsed email object
                self.log.trace ("Email: %s" % str([email_id, subject, date, data]))
                result['emails'].append([email_id, subject, date, data])

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="fetch email data for email ids")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_email_received(self, type, wait=90, testcase=None):
        """ Verify specified email was received.
        INPUT
            type: type of email to verify has been received.
            wait: number of seconds to wait for email to be received.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            email: email data dictionary object.
        """

        self.log.debug("Verify %s email was received ..." % type)
        result = {'successful': False, 'verified': False, 'email': {}}

        try:
            processing = True
            # connect to exchange
            if processing:
                connected = self.connect_to_exchange_server()['succeeded']
                if not connected: processing = False
            # open mailbox
            if processing:
                mailboxOpened = self.open_mailbox(readonly=False)['succeeded']
                if not mailboxOpened: processing = False
            # check mailbox
            if processing:
                returned = self.check_mailbox_for_email(type,wait)
                result['verified'] = returned['found']
                result['email'] = returned['email']

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify %s email was received" % type)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def check_mailbox_for_email(self, type="ViM Status Report", wait=180, testcase=None):
        """ Check open mailbox for specified email.
        INPUT
            type: type of email for which to check.
            wait: the number of seconds to wait for the type of email.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            found: whether the email was found or not.
            email: email data dictionary.
        """

        self.log.debug("Checking mailbox for %s email ..." % type)
        result = {'successful': False, 'found': False, 'email': None}

        try:
            # search for email by type for specified time
            i = 0
            found = False
            if wait is 0 or None: wait = 30
            while not found:
                try:
                    if type.lower() == "vim status report": subject = "ViM Status Report"
                    elif type.lower() == "clip download notification": subject = "ALL"
                    elif type.lower() == "connection test": subject = "ALL"
                    else:
                        self.log.error("Invalid email specified.")
                        break
                    # search for emails with subject
                    emailIDs = self.return_emails_with_subject(subject)['email ids']
                    # fetch email data
                    if emailIDs is not None and emailIDs != []:
                        emails = self.fetch_email_data_for_ids(emailIDs)['emails']
                        # verify email data
                        data = self.verify_email(emails,type)
                        found = data['verified']
                        result['email'] = data['email']
                except BaseException, e:
                    self.log.error(str(e))
                    self.log.error("Failed to check mailbox for email.")
                # update iterator processing
                i += 1
                result['found'] = found
                if not result['found'] and i > ((wait/15)-1):
                    self.log.error("Email not found.")
                    break
                elif not result['found']:
                    self.log.trace("Email not found (attempt %d). Retrying in 15 seconds ..." % i)
                    # refresh connection
                    sleep(15)

            self.log.trace("Checked mailbox for %s email." % type)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="check mailbox for %s email" % type)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def verify_email(self, emails, type, testcase=None):
        """ Verify an email of specified type.
        INPUT
            emails: a list of email data objects in which to search and verify.
            type: type of email to look for in list of emails.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            email: email data dictionary object that meets type criteria in list of emails.
        """

        self.log.debug("Verifying %s email data ..." % type)
        result = {'successful': False, 'verified': False, 'email': None}

        try:
            # verify email
            for email in emails:
                subject = False
                # check if subject is status email notification
                if type.lower() == 'vim status report'\
                and 'vim status report' in str(email[1]).lower():
                    self.log.trace("Found email.")
                    # parse relevant data from email body into dict for test-by-test
                    #   verification
                    returned = self.parse_vim_status_report(email[3])
                    verified = returned['verified']
                    data = returned['data']
                    if verified:
                        subject = True
                        # replace raw data with parsed data
                        email.pop()
                        email.append(data)
                    else: self.log.error("Email could not be verified.")
                # check if email is a clip download notification
                elif type.lower() == 'clip download notification'\
                and 'vim clip download' in str(email[1]).lower():
                    self.log.trace("Found email.")
                    subject = True
                # check if email is a connection test
                elif type.lower() == 'connection test'\
                and 'vim notification email test' in str(email[1]).lower():
                    self.log.trace("Found email.")
                    subject = True
                else: self.log.trace("Expected %s, but found %s."%(type.lower(),email[1].lower()))
                # check if all parameters met by email
                if subject:
                    result['email'] = email
            # verify that an email was found matching parameters
            if result['email'] is not None:
                self.log.trace("Valid email found: %s"%str(result['email']))
                result['verified'] = True

            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="verify %s email data" % type)

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result

    def parse_vim_status_report(self, data, testcase=None):
        """
        INPUT
            data: the data from a ViM Status Report email to parse.
            testcase: a testcase object supplied when executing function as part of a testcase step.
        OUPUT
            successful: whether the function executed successfully or not.
            verified: whether the operation was verified or not.
            data: a parsed data dictionary object.
        """

        self.log.debug("Parsing ViM Status Report ...")
        result = {'successful': False, 'verified': False,
                  'data':{
                      'reported':       False,
                      'dvr health reported':    False,
                      'camera health reported': False,
                      'server health reported': False,
                      'connection status reported': False,
                      'no dvr events': False,
                      'no camera events': False,
                      'no detailed camera events': False,
                      'no connection statuses': False,
                      'dvr health summary': [],
                      'dvr health extended': [],
                      'camera health summary': [],
                      'camera health extended': [],
                      'connection status 24 hour report': [],
                      'connection status 48 hour report': [],
                      'connection status 72 hour report': [],
                      'connection status never connected report': [],
                      'storage space available report': [],
                      }}

        try:
            # handle no data exception
            if data is None: self.log.error("No email data found.")
            # convert html/xml data to html string
            htmlString = self.status_email_parser.convert_html_data_to_string(data)
            # parse html data
            result['data'] = self.status_email_parser.feed(htmlString)
            if result['data']['reported']\
               and result['data']['dvr health reported']\
               and result['data']['camera health reported']\
               and result['data']['connection status reported']\
            and result['data']['server health reported']:
                self.log.trace("Verified status report.")
                result['verified'] = True
            elif not result['data']['dvr health reported']:
                self.log.error("Failed to verify DVR Health was reported.")
            elif not result['data']['camera health reported']:
                self.log.error("Failed to verify Camera Health was reported.")
            elif not result['data']['connection status reported']:
                self.log.error("Failed to verify Connection Status was reported.")
            elif not result['data']['server health reported']:
                self.log.error("Failed to verify Server Health was reported.")
            else: self.log.error("Failed to verify email.")

            self.log.trace("Parsed ViM Status Report.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="parse ViM Status Report")

        # return
        if testcase is not None: testcase.processing = result['successful']
        return result