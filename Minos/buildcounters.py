####################################################################################################
#
# Copyright (c) by Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from maps import PROJECTS, FILE_PATHS

####################################################################################################
# Mapping ##########################################################################################
####################################################################################################
####################################################################################################

rootPath = FILE_PATHS['root']

####################################################################################################
# Build Counters ###################################################################################
####################################################################################################
####################################################################################################

class BuildCounters():
    """ Submodule for interacting with TeamCity build counters. """

    def update_build_counters_on_compile(self,build,reset=False,newRelease=False):
        """ Update all appropriate build counters among builds that share the same build
        number as the specified build. This should be done before the build line for the project
        has finished compiling a new build.
        'reset' designates whether build and all sharing builds should be reset,
            in which case, builds will have their counters reset to 1. """

        self.log.trace("Updating build counters for %s ..."%build)
        result = {'successful': False, 'current build':None,'next build':None}

        try:
            # determine latest build number
            currBuilds = []
            cfg = PROJECTS[build.lower()]
            # use development builds to determine build number if new release
            if newRelease:
                cfg['sharing projects'] = PROJECTS['development']['sharing projects']
                cfg['sharing projects'].append('development')
            # read own build number (only if not new release, otherwise go by sharing builds)
            else:
                path = self.determine_build_line_properties_path(build,cfg['build line'])['file path']
                currBuild = self.return_build_line_counter(path)['build number']
                currBuilds.append(currBuild-1)
                # read each build number
            for proj in cfg['sharing projects']:
                # determine properties file path
                path = self.determine_build_line_properties_path(proj,
                    PROJECTS[proj.lower()]['build line'])['file path']
                # determine build number
                currBuild = self.return_build_line_counter(path)['build number']
                # append to list
                currBuilds.append(currBuild)
                # sort list
            currBuilds.sort(None,None,True)
            # first item in list is the most recent build number
            result['current build'] = currBuilds[0] + 1
            result['next build'] = result['current build'] + 1
            # update current build (make sure it has correct, latest build number)
            print "\n##teamcity[buildNumber '%d']"%result['current build']
            # update current build line to have next build number
            self.change_build_line_next_build_number(build,cfg['build line'],result['next build'])
            # update all sharing builds
            if reset: result['next build'] = 1
            self.update_build_counters_for_sharing_builds(cfg['sharing projects'],result['next build'])

            self.log.trace("Updated build counters for %s"%build)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="update build counters for %s" % build)

        # return
        return result

    def update_build_counters_for_sharing_builds(self,builds,number):
        """ Update the build counters for all sharing builds.
        'builds' should be a list of builds to update (see maps.py for valid build names).
        'number' is the build number to update the builds too (for next build). """

        self.log.trace("Updating build counters for sharing builds ...")
        result = {'successful': False}

        try:
            # update opposite project's build line to have same next build number
            for proj in builds:
                projCFG = PROJECTS[proj.lower()]
                self.change_build_line_next_build_number(proj,projCFG['build line'],number)

            self.log.trace("Updated build counters for sharing builds.")
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="update build counters for sharing builds")

        # return
        return result

    def reset_test_counters_on_compile(self, project):
        """ Reset all test counters for specified project. """

        self.log.trace("Resetting test counters for %s ..."%project)
        result = {'successful': False}

        try:
            # reset all test lines for project to 1
            cfg = PROJECTS[project.lower()]
            for testLine in cfg['test lines']:
                self.change_build_line_next_build_number(project,testLine[1],1)

            self.log.trace("Reset test counters for %s." % project)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="reset test counters for %s" % project)

        # return
        return result

    def change_build_line_next_build_number(self, project, lineID, newCounter):
        """ Change the next build number for specified build line of project to new counter. """

        self.log.trace("Changing next build number for line %d of %s to %d"%(lineID,project,newCounter))
        result = {'successful': False}

        try:
            # determine file path
            filePath = self.determine_build_line_properties_path(project, lineID)['file path']
            # read build line properties
            lines = self.read_build_line_properties(filePath)['lines']
            # find and change build counter in list
            self.log.trace("Changing build counter to %d ..."%newCounter)
            newLines = []
            for line in lines:
                if 'next.build' in line: newLine = 'next.build=%d'%newCounter
                else: newLine = line
                newLines.append(newLine)
                # rewrite properties file
            f = open(filePath,'w')
            for newLine in newLines:
                f.write(newLine)
            f.close()

            self.log.trace("Changed next build nubmer for line %d of %s to %d." % (lineID, project,
                newCounter))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="change next build number for line %d of %s to %d" %
                (lineID, project, newCounter))

        # return
        return result

    def determine_build_line_properties_path(self, project, lineID):
        """ Determine the build line properties file path. """

        self.log.trace("Determining build line properties file path for line %d of %s"%(lineID,project))
        result = {'successful': False, 'file path': None}

        try:
            # determine full file path and name
            cfg = PROJECTS[project.lower()]
            filePath = rootPath + cfg['path']
            fileName = "bt%d.buildNumbers.properties"%lineID
            result['file path'] = filePath + fileName
            self.log.trace("File path:\t%s"%result['file path'])

            self.log.trace("Determined build line properties file path for line %d of %s."
                           % (lineID, project))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="determine build line properties file path for line %d"
                                               "of %s" % (lineID, project))

        # return
        return result

    def read_build_line_properties(self, path):
        """ Read the build line properties file into a list. """

        self.log.trace("Reading build properties file ...")
        result = {'successful': False, 'lines':[]}

        try:
            # open build number properties file
            self.log.trace("Opening build number properties file at %s..."%path)
            f = open(path)
            # read lines into list
            self.log.trace("Reading file ...")
            for line in f:
                result['lines'].append(line)
            self.log.trace("Lines:\t%s"%str(result['lines']))

            self.log.trace("Opened build number properties file at %s." % path)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="open build number properties file at %s" % path)

        # return
        return result

    def return_build_line_counter(self, path):
        """ Return the current build number for specified project line. """

        self.log.trace("Returning current build number from %s ..."%path)
        result = {'successful': False, 'build number':None}

        try:
            # read build line properties
            lines = self.read_build_line_properties(path)['lines']
            # look for count
            for line in lines:
                if 'next.build' in line:
                    parsed = line.split('=')
                    result['build number'] = int(parsed[1]) - 1
            self.log.trace("Build number:\t%d"%result['build number'])

            self.log.trace("Returned current build number from %s." % path)
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation="return current build number from %s" % path)

        # return
        return result

