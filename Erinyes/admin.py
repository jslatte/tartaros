####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from django.contrib import admin
from models import *
from logger import Logger
from utc import UTC

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

log = Logger()
utc = UTC(log)

####################################################################################################
# Classes ##########################################################################################
####################################################################################################
####################################################################################################


class AdminDVR(admin.ModelAdmin):

    # the field set parameters control the layout of admin pages
    fieldsets = [
        ('Name',        {'fields': ['name']}),
        ('IP Address',  {'fields': ['ip_address']}),
        ('Username',    {'fields': ['username']}),
        ('Password',    {'fields': ['password']})
    ]
    # what to display in the admin table list
    list_display = ('name', 'ip_address')
    # what field(s) to filter the list by (side panel)
    list_filter = ['name', 'ip_address']
    # what field(s) the search field will look in
    search_fields = ['name', 'ip_address']


class AdminSite(admin.ModelAdmin):

    # the field set parameters control the layout of admin pages
    fieldsets = [
        ('Name',        {'fields': ['name']}),
        ('DVR',         {'fields': ['dvr']}),
    ]
    # what to display in the admin table list
    list_display = ('name', 'dvr')
    # what field(s) to filter the list by (side panel)
    list_filter = ['name', 'dvr']
    # what field(s) the search field will look in
    search_fields = ['name', 'dvr']


class AdminConnection(admin.ModelAdmin):

    # the field set parameters control the layout of admin pages
    fieldsets = [
        ('Site',        {'fields': ['site']}),
        ('Start',       {'fields': ['start']}),
        ('End',         {'fields': ['end']}),
        ('Type',        {'fields': ['connection_type']}),
    ]
    # what to display in the admin table list
    list_display = ('site', 'start', 'end', 'connection_type')
    # what field(s) to filter the list by (side panel)
    list_filter = ['site', 'start', 'end', 'connection_type']
    # what field(s) the search field will look in
    search_fields = ['site', 'connection_type']

####################################################################################################
# Register Models ##################################################################################
####################################################################################################
####################################################################################################

models_to_register = [
    (DVR, AdminDVR),
    (Site, AdminSite),
    (Connection, AdminConnection),
    ConnectionType,
]

for model in models_to_register:
    try:
        admin.site.register(model[0], model[1])
    except TypeError:
        admin.site.register(model)