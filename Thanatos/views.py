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
from django.shortcuts import render
from models import *
from logger import Logger
from exceptionhandler import ExceptionHandler as handle_exception
import inspect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django import forms
from Database import Database
from testcase import TestCase
from collections import OrderedDict

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

log = Logger()
METHODS = {
    'run full regression test': {'id': 1, 'name': 'Run Full Regression Test',
                                 'widget': 'runfregtest_btn'}
}

####################################################################################################
# Objects ##########################################################################################
####################################################################################################
####################################################################################################


class DebugProduct():

    def debug_function(self, debug_argument=True, testcase=None):
        result = {'successful': debug_argument, 'verified': debug_argument}
        if testcase is not None:
            testcase.processing = debug_argument
        return result


class ThanatosTestCase(TestCase):

    def get_testcase_data_from_database(self, testcase_id):
        """
        :return: a data dict containing:
            'successful' - whether the function executed successfully or not.
            'testcase data' - a dictionary packet containing the testcase data.
        """

        operation = self.inspect.stack()[0][3]
        result = {'successful': False, 'testcase data': {}}

        try:
            log.trace("%s ..." % operation.replace('_', ' '))

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

            log.trace("... done %s." % operation.replace('_', ' '))
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

    def setup_for_product(self):
        self.debug_product = DebugProduct()

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

            # instantiate database object for testcases
            log.trace("Instantiating database object for testcases ...")
            database = Database(log, path=os.getcwdu()+'\\tartaros.sqlite')

            # run each testcase
            log.trace("Running testcases ...")
            for testcase in testcases:
                testcase = ThanatosTestCase(log, database, testcase.id)
                testcase.run()

        log.trace("... done %s." % operation.replace('_', ' '))
    except BaseException, e:
        handle_exception(log, e, operation=operation)

    return HttpResponse(response)