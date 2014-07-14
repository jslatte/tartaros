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
    response = thanatos.process_test_run_form(request)['response']
    return HttpResponse(response)