####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

import os
import inspect
import time
import socket
from binascii import hexlify, unhexlify
from django.shortcuts import render
from models import *
from logger import Logger
from exceptionhandler import ExceptionHandler
import inspect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django import forms
from Database import Database
from testcase import ThanatosTestCase
from collections import OrderedDict
from thanatos import Thanatos
from mapping import METHODS

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

log = Logger()
exception_handler = ExceptionHandler(log)
thanatos = Thanatos(log, exception_handler)

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
# Views ############################################################################################
####################################################################################################
####################################################################################################


def index(request):
    """ The default view.
    """

    # define the raw response object expected data
    response_data = {
        'servers':          None,
        'products':         None,
    }

    # determine servers for "Remote Servers" SELECT field
    response_data['servers'] = RemoteServers.objects.all()

    # determine products for "Product" SELECT field
    response_data['products'] = Products.objects.all()

    # render the page
    t = loader.get_template('Thanatos/index.html')
    c = Context(response_data)
    rendered_response = t.render(c)

    # return the rendered page
    return HttpResponse(rendered_response)


def process_test_run_form(request):
    thanatos.process_test_run_form(request)
    return HttpResponse('Ok')


def something_else(request):
    """ Process the test run form submission.
    """

    operation = inspect.stack()[0][3]
    response = 'Ok'

    try:
        log.trace("%s ..." % operation.replace('_', ' '))

        # determine request data
        data = None
        if request.method == 'POST':
            # log POST data
            data = request.POST
            log.trace("Received POST data:")
            for key in data:
                log.trace("%s:\t%s" % (key, data[key]))

        # determine method
        method = None
        if data is None:
            response = "Failed to determine method. No data received."
            log.warn(response)
        else:
            # determine by button pressed
            for entry in METHODS.keys():
                if METHODS[entry]['widget'] in data:
                    method = METHODS[entry]
                    log.trace("Received '%s' command." % method['name'])
                    break

        # process the form submission data
        if data is None:
            pass

        elif method is None:
            response = "Failed to process form submission data. No method identified."
            log.warn(response)

        elif method == METHODS['run full regression test']:
            log.trace("Processing data '%s' method ..." % method['name'])

            # determine built to test
            build = None

            # determine testrail plan to publish to
            testrail_plan_id = None

            # determine server to run on
            if data['server'] == '':
                log.trace("No remote server selected. Running test(s) locally ...")
                server = None
            else:
                server = RemoteServers.objects.get(pk=data['server'])
                log.trace("%s remote server selected. Running test(s) remotely ..." % server.name)

            # build testcase list
            log.trace("Building list of testcases to run ...")
            testcases = TestCases.objects.all()
            log.trace("Testcases to Run:")
            for testcase in testcases:
                log.trace_in_line("\n%s:%s" % (testcase.id, testcase.name))

        # execute action
        if data is None or method is None:
            pass

        elif method == METHODS['run full regression test']:
            log.trace("Executing '%s' method ..." % method['name'])

            # run each testcase
            if server is None:
                log.trace("Running testcases ...")
                for testcase in testcases:

                        # run tests locally
                        testcase = ThanatosLocalTestCase(log, None, testcase.id)
                        testcase.run()
            else:
                # run tests remotely
                commands = []

                for testcase in testcases:
                    # build server command for client
                    cmd_dict = {
                        'build':    "'%s'" % build,
                        'test name':"'Remote Test - %s - %s (%s)'"
                                    % (testcase.test, testcase.name, testcase.id),
                        'plan id':  testrail_plan_id,
                        'module':   None,
                        'feature':  None,
                        'story':    None,
                        'test':     None,
                        'case':     testcase.id,
                        'class':    None,
                        'type':     None,
                        'dvr ip':   None,
                        'mode':     'thanatos',
                    }
                    cmd = "self.run_test(build=%(build)s, test_name=%(test name)s, " \
                      "results_plan_id=%(plan id)s, module=%(module)s, feature=%(feature)s, " \
                      "story=%(story)s, test=%(test)s, case=%(case)s, " \
                      "case_class=%(class)s, case_type=%(type)s, int_dvr_ip=%(dvr ip)s," \
                      "mode='%(mode)s');;" % cmd_dict
                    hex_cmd = hexlify(cmd)
                    commands.append(hex_cmd)

                if len(commands) > 0:
                    # connect to remote client (Hekate)
                    client_addr = (server.ip_address, 333)

                    log.trace("Connecting to remote client at %s ..." % str(client_addr))

                    hekate_conn = socket.socket()
                    hekate_conn.connect(client_addr)

                    log.trace("... connected.")

                    # send commands to client
                    for command in commands:
                        log.trace("Sending command:\t'%s'." % unhexlify(command))
                        hekate_conn.send(command)

                    # close connection to client
                    hekate_conn.close()

        log.trace("... done %s." % operation.replace('_', ' '))
    except BaseException, e:
        exception_handler.handle_exception(e, operation=operation)

    return HttpResponse(response)