####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import urllib, urllib2
from maps import BUILDING, FILE_PATHS, BUILD_SUFFIXES

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

TRIGGER_PATH    = BUILDING['trigger path']
BUILDS          = BUILDING['builds']
AGENTS          = BUILDING['agents']
FIELDS          = BUILDING['fields']
PARAMS          = BUILDING['parameters']
VCS_ROOTS       = BUILDING['vcs roots']
ROOT_PATH       = FILE_PATHS['root']
BUILD_TO_PROJ   = BUILDING['build to project']

####################################################################################################
# Building Submodule ###############################################################################
####################################################################################################
####################################################################################################

class Building():
    """ Submodule for interacting with build lines in TeamCity. """

    def download_last_successful_build(self,build,saveLoc=''):
        """ Download the last successful build from specified build line.
        'build' is a string indicating which build to trigger(see BUILDS for valid values).
        'saveLoc' should be the path to save the build to. """

        self.log.trace("Downloading last successful build from %s"%build)
        result = {'successful': False, 'file path':None}

        try:
            # determine build ID
            try: buildID = BUILDS[build.lower()]
            except KeyError:
                self.log.error("Invalid build '%s' specified."%str(build))
                return result
            # download build artifact
            suffixes = BUILD_SUFFIXES
            downloaded = False
            i = 0
            while not downloaded and i < len(suffixes):
                # define suffix
                suffix = suffixes[i]
                # define url
                path = "repository/download/%s/.lastSuccessful/install/en-us/"\
                       "VIMServer-{build.number}-%s.msi"%(buildID,suffix)
                url = self.serverURL+path
                # define save location
                filePath = saveLoc+'VIMServer.msi'
                # encode url
                self.log.trace("Writing target to file ...")
                url = self.add_basic_authentication_to_url(url)['url']
                # open the target file and read it into a variable
                opener = urllib2.build_opener()
                try:
                    target = opener.open(url)
                    target = target.read()
                    downloaded = True
                except Exception:
                    target = None
                i += 1
                # open local file for binary write and save
            try:
                file = open(filePath, "wb")
                file.write(target)
                file.close()
                result['file path'] = filePath
            except BaseException, e:
                self.log.error(e.message)
                self.log.error("Failed to download build.")
                raise AssertionError ("Failed to download build")

            self.log.trace("Downloaded last successful build from %s." % build)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="download last successful build from %s" % build)

        # return
        return result

    def trigger_build(self,build,parameters=[],agent=None):
        """ Trigger specified build line in TeamCity.
        'build' is a string indicating which build to trigger(see BUILDS for valid values).
        'parameters' is a list of lists pairing parameter names and values that should
            correspond to test line parameters (see PARAMS for valid values).
        'agent' is a string indicating which agent to build on(see AGENTS for valid values)."""

        self.log.trace("Triggering build %s ..."%build)
        result = {'successful':False,'response':None}

        try:
            # define build ID to trigger
            try: buildID = BUILDS[build.lower()]
            except KeyError:
                self.log.error("Invalid build '%s' specified."%str(build))
                return result
            # define path for server request
            url = self.serverURL+TRIGGER_PATH%buildID
            # define default data packet for server request
            data = {}
            # add parameters to URL (duplicate keys disallow adding to data{})
            params = ''
            for parameter in parameters:
                try:
                    # include url-encoding and replacement for missed characters
                    params += '&' + urllib.urlencode({
                        'name': PARAMS[parameter[0].lower()],
                        'value':parameter[1]
                    }).replace('+','%20').replace('%28','(').replace('%29',')')
                except KeyError:
                    self.log.warn("Invalid parameter '%s' specified."%str(parameter[0]))
            url += params
            # update with agent if specified
            agentID = None
            if agent is not None:
                try: agentID = AGENTS[agent.lower()]
                except KeyError: self.log.warn("Invalid agent '%s' specified."%str(agent))
            if agentID is not None: data[FIELDS['agent']] = agentID
            # send request to server
            result['response'] = self.send_http_request(url,data)
            # check server response (empty string if successful)
            if result['response'] == '': result['successful'] = True

            self.log.trace("Triggered build %s." % build)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="trigger build %s" % build)

        # return
        return result

    def change_build_line_parameter(self,parameter,build,replacement):
        """ Change the configuration parameter for the specified build.
        'parameter' is the parameter to change in the build configuration.
        'build' is a string indicating which build to trigger(see BUILDS for valid values).
        'replacement' indicates what value to replace the current one with. """

        self.log.trace("Changing %s for build line %s to %s ..."%(parameter,build,replacement))
        result = {'successful':False,'response':None}

        try:
            # determine project configuration
            cfg = BUILD_TO_PROJ[build.lower()]
            # determine full file path and name of configuration to modify
            filePath = ROOT_PATH + cfg['path']
            fileName = "project-config.xml"
            path = filePath + fileName
            self.log.trace("File path:\t%s"%path)
            # determine build ID
            try: buildID = BUILDS[build.lower()]
            except KeyError:
                self.log.error("Invalid build '%s' specified."%str(build))
                return result
            # determine parameter key (to look for to indicate where the field is)
            #   [0] is the string to look for, [1] is the field to replace, [2] is the replacement
            PARAMETER_KEYS = {
                'vcs root':         ['<vcs-entry-ref','root-id','root-id="%d"'],
                'test dependency':  ['<dependency','sourceBuildTypeId','sourceBuildTypeId="%s"']
            }
            paramKey = PARAMETER_KEYS[parameter.lower()]
            # determine replacement value
            try:
                if parameter.lower() == 'vcs root': val = VCS_ROOTS[replacement.lower()]
                elif parameter.lower() == 'test dependency': val = BUILDS[replacement.lower()]
                else:
                    self.log.error("Invalid replacement key %s specified."%replacement)
                    return result
            except KeyError:
                self.log.error("Invalid replacement key %s specified."%replacement,)
                return result
            # open project configuration xml file in read-mode
            f = open(path,'r')
            # read lines in project configuration xml file to list
            lines = []
            for line in f: lines.append(line)
            # close project configuration xml file
            f.close()
            # backup original settings
            f = open(path+'.bak','w')
            for line in lines:
                f.write(line)
            f.close()
            # build new lines list with changes to project configuration
            newLines = []
            inProject = False
            for line in lines:
                # if specified build line found, following lines are its settings
                if 'build-type id="%s"'%buildID in line:
                    self.log.trace("Found build line. Looking for %s ..."%parameter)
                    inProject = True
                # if end of build found, following lines are no longer its settings
                elif inProject and '/build-type' in line:
                    self.log.trace("Build line closed.")
                    inProject = False
                    # if parameter key line found, update for appropriate replacement value
                if inProject and paramKey[0] in line:
                    self.log.trace("%s settings found. Updating ..."%parameter)
                    # split line around replaced field
                    parsedLine = line.strip().split(' ')
                    # check each parameter for replaced field
                    replacedField = None
                    for param in parsedLine:
                        if paramKey[1] in param: replacedField = param
                        # make sure replaced field was found
                    if replacedField is not None:
                        # replace field in line with updated value
                        translatedLine = line.replace(replacedField,paramKey[2]%val)
                    # else, don't change the line
                    else: translatedLine = line
                # else, don't change the line
                else: translatedLine = line
                # append line to new lines list
                newLines.append(translatedLine)
                # write new lines to project configurations xml file
            f = open(path,'w')
            for line in newLines:
                f.write(line)
            f.close()

            self.log.trace("Changed %s for build line %s to %s." % (parameter, build, replacement))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="change %s for build line %s to %s"
                                               % (parameter, build, replacement))

        # return
        return result