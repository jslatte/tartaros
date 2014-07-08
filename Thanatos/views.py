####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from django.shortcuts import render
from models import *
from logger import Logger
from exceptionhandler import ExceptionHandler
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django import forms

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

log = Logger()

####################################################################################################
# Views ############################################################################################
####################################################################################################
####################################################################################################


def index(request):
    response_data = {
        'products':         None,
    }

    # determine products for "Product" SELECT field
    response_data['products'] = Products.objects.all()

    # render the page
    t = loader.get_template('Thanatos/index.html')
    c = Context(response_data)
    rendered_response = t.render(c)
    return HttpResponse(rendered_response)


def process_test_run_form(request):
    if request.method == 'POST':
        # log POST data
        data = request.POST
        log.trace("Received POST data:")
        for key in data:
            log.trace("%s:\t%s" % (key, data[key]))

    return HttpResponse('Ok')