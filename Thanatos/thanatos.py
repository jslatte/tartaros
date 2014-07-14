####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import inspect
import socket
from binascii import hexlify, unhexlify
from models import *
from testcase import ThanatosTestCase
from collections import OrderedDict
from mapping import METHODS

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
# Objects ##########################################################################################
####################################################################################################
####################################################################################################


class ThanatosLocalTestCase(ThanatosTestCase):

    def get_testcase_data_from_database(self, testcase_id):
        """
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'testcase data' - a dictionary packet containing the testcase data.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'testcase data': {}}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # retrieve test case
            testcase = TestCases.objects.get(pk=testcase_id)

            # determine test data
            result['testcase data'] = OrderedDict([
                ('id', testcase.id),
                ('name', testcase.name),
                ('test', testcase.test_id),
                ('procedure', testcase.procedure),
                ('minimum version', testcase.min_version),
                ('class', testcase.level),
                ('active', testcase.active),
                ('type', testcase.type),
                ('results id', testcase.testrail_id),
            ])

            # update testcase attributes
            self.name = testcase.name
            self.test_id = testcase.test_id
            self.case_results_id = testcase.testrail_id

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        return result

    def get_procedure_step_data_from_database(self, step_id):
        """
        @param step_id: the id of the procedure step.
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'step data' - a dictionary packet containing the step data.
            'function data' - a dictionary packet containing the function data.
            'submodule data' - a dictionary packet containing the submodule data.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'step data': {}, 'function data': {}, 'submodule data': {}}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # retrieve step data
            step = ProcedureSteps.objects.get(pk=step_id)

            # build step data packet
            result['step data'] = OrderedDict([
                ('id', step.id),
                ('name', step.name),
                ('function', step.function_id),
                ('arguments', step.arguments),
                ('verification', str(step.verification)),
            ])

            # retrieve function data
            funct = Functions.objects.get(pk=step.function_id)

            # build function data packet
            result['function data'] = OrderedDict([
                ('id', funct.id),
                ('function', funct.name),
                ('submodule id', funct.product_id),
            ])

            # retrieve product data
            product = Products.objects.get(pk=funct.product_id)

            # build product data packet
            result['submodule data'] = OrderedDict([
                ('id', product.id),
                ('name', product.name),
                ('code', product.code),
                ('results id', product.testrail_id),
            ])

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

####################################################################################################
# Thanatos #########################################################################################
####################################################################################################
####################################################################################################


class Thanatos():
    """ The main library for Cerberus test automation execution.
    """

    def __init__(self, logger, exception_handler):
        """
        @param logger: an initialized Logger() to inherit.
        @param exception_handler: an un-initialized ExceptionHandler() to inherit.
        """

        # instance logger (initialized instance)
        self.log = logger

        # instance exception handler
        self.handle_exception = exception_handler.handle_exception

        # stacktrace
        self.inspect = inspect

        self.log.info("Initializing %s ..." % self.__class__.__name__)

    def TEMPLATE(self):
        """
        :return: a data dictionary containing
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def determine_test_run_request_data(self, request):
        """ Determine the request data.
        @param request: the request object from the client.
        :return: a data dictionary containing
            'successful' - whether the function executed successfully or not.
            'data' - the relevant request data.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'data': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            if request.method == 'POST':
                # log POST data
                data = request.POST
                self.log.trace("Received POST data:")
                for key in data:
                    self.log.trace("%s:\t%s" % (key, data[key]))

                # update result packet
                result['data'] = data

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def determine_test_run_method(self, data):
        """ Determine the method to use.
        @param data: the request data.
        :return: a data dictionary containing
            'successful' - whether the function executed successfully or not.
            'method' - the method to use.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'method': None}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            if data is None:
                raise AssertionError("No data received.")

            else:
                # determine by button pressed
                for entry in METHODS.keys():
                    if METHODS[entry]['widget'] in data:
                        result['method'] = METHODS[entry]
                        self.log.trace("Received '%s' command." % result['method']['name'])
                        break

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def determine_test_run_parameters(self, data, method):
        """ Determine the parameters of the test run.
        @param data: the request data.
        @param method: the method to be executed.
        :return: a data dictionary containing
            'successful' - whether the function executed successfully or not.
            'parameters' - a data dict of all test run parameters.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False,
                  'parameters': {
                      'build': None,
                      'server': None,
                      'testrail plan id': None,
                      'testcases': [],
                  }
        }

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            if data is None:
                pass

            elif method is None:
                raise AssertionError("No method identified.")

            elif method == METHODS['run full regression test']:
                self.log.trace("Processing data '%s' method ..." % method['name'])

                # determine build to test

                # determine testrail plan to publish to

                # determine server to run on
                if data['server'] == '':
                    self.log.trace("No remote server selected. Running test(s) locally ...")
                else:
                    server = RemoteServers.objects.get(pk=data['server'])
                    self.log.trace("%s remote server selected. Running test(s) remotely ..."
                                   % server.name)
                    result['parameters']['server'] = server

                # build testcase list
                self.log.trace("Building list of testcases to run ...")
                testcases = TestCases.objects.all()
                self.log.trace("Testcases to Run:")
                for testcase in testcases:
                    self.log.trace_in_line("\n%s:%s" % (testcase.id, testcase.name))
                result['parameters']['testcases'] = testcases

            else:
                raise AssertionError("Unknown method '%s'." % method)

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def execute_remote_test_run(self, server, testcases, build=None, testrail_plan_id=None):
        """ Execute the test run.
        @param server: the server to execute the test run on.
        @param testcases: a list of testcases to run.
        @param build: (OPTIONAL) the build to test against. If specified, this build will be
            retrieved from the TeamCity build server. If None, will attempt to execute test
            cases against previously installed build.
        @param testrail_plan_id: (OPTIONAL) the ID of the test plan to publish the results to
            in TestRail. If None, will not attempt to publish results to TestRail.
        :return: a data dictionary containing
            'successful' - whether the function executed successfully or not.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            commands = []

            # define default command dictionary for testcase(s)
            cmd_dict = {
                'build':    "'%s'" % build,
                'test name':"'Remote Test",
                'plan id':  testrail_plan_id,
                'module':   None,
                'feature':  None,
                'story':    None,
                'test':     None,
                'case':     None,
                'class':    None,
                'type':     None,
                'dvr ip':   None,
                'mode':     'thanatos',
            }

            # define default command string for testcase(s)
            cmd_temp = "self.run_test(build=%(build)s, test_name=%(test name)s, " \
                  "results_plan_id=%(plan id)s, module=%(module)s, feature=%(feature)s, " \
                  "story=%(story)s, test=%(test)s, case=%(case)s, " \
                  "case_class=%(class)s, case_type=%(type)s, int_dvr_ip=%(dvr ip)s," \
                  "mode='%(mode)s');;"


            # only first test cases will attempt to install a specified build
            if len(testcases) > 0:
                # update command dict for first test case (if any)
                cmd_dict['test name'] = "'Remote Test - %s - %s (%s)'" % (
                    testcases[0].test, testcases[0].name, testcases[0].id)
                cmd_dict['case'] = testcases[0].id

                # add command for first test case
                hex_cmd = hexlify(cmd_temp % cmd_dict)
                commands.append(hex_cmd)

            if len(testcases) > 1:
                # continue with remaining test cases
                cmd_dict['build'] = None
                for testcase in testcases[1:]:
                    # update command dict
                    cmd_dict['test name'] ="'Remote Test - %s - %s (%s)'" % (
                        testcase.test, testcase.name, testcase.id)
                    cmd_dict['case'] = testcase.id

                    # add command
                    hex_cmd = hexlify(cmd_temp % cmd_dict)
                    commands.append(hex_cmd)

            # reverse list of commands (so build testcase executed first)
            commands.reverse()

            if len(commands) > 0:
                # connect to remote client (Hekate)
                client_addr = (server.ip_address, 333)

                self.log.trace("Connecting to remote client at %s ..." % str(client_addr))

                hekate_conn = socket.socket()
                hekate_conn.connect(client_addr)

                self.log.trace("... connected.")

                # send commands to client
                for command in commands:
                    self.log.trace("Sending command:\t'%s'." % unhexlify(command))
                    hekate_conn.send(command)

                # close connection to client
                hekate_conn.close()

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)

        # return
        return result

    def process_test_run_form(self, request):
        """ Process the test run form submission.
        @param request: the request object from the client.
        :return: a data dictionary containing
            'successful' - whether the function executed successfully or not.
            'response' - the server response to the client.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'response': 'Ok'}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine request data
            data = self.determine_test_run_request_data(request)['data']

            # determine method
            method = self.determine_test_run_method(data)['method']

            # process the form submission data
            params = self.determine_test_run_parameters(data, method)['parameters']

            # execute action
            if data is None or method is None:
                pass

            elif method == METHODS['run full regression test']:
                self.log.trace("Executing '%s' method ..." % method['name'])

                # run each testcase
                if params['server'] is None:
                    self.log.trace("Running testcases ...")
                    for testcase in params['testcases']:

                            # run tests locally
                            testcase = ThanatosLocalTestCase(self.log, None, testcase.id)
                            testcase.run()
                else:
                    # run tests remotely
                    server = params['server']
                    testcases = params['testcases']
                    self.execute_remote_test_run(server, testcases)

            self.log.trace("... done %s." % operation.replace('_', ' '))
            result['successful'] = True
        except BaseException, e:
            self.handle_exception(e, operation=operation)
            result['response'] = 'Error occurred.'

        # return
        return result