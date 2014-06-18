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

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
# Classes ##########################################################################################
####################################################################################################
####################################################################################################


class ProductsAdmin(admin.ModelAdmin):

    # the field set parameters control the layout of admin pages
    fieldsets = [
        ('Name',        {'fields': ['name']}),
        ('Code',        {'fields': ['code']}),
        ('TestRail ID', {'fields': ['testrail_id']})
    ]
    # what to display in the admin table list
    list_display = ('name', 'code', 'testrail_id')
    # what field(s) to filter the list by (side panel)
    list_filter = ['name']
    # what field(s) the search field will look in
    search_fields = ['name']


class TestSuitesAdmin(admin.ModelAdmin):

    # the field set parameters control the layout of admin pages
    fieldsets = [
        ('Name',        {'fields': ['name']}),
        ('Product',     {'fields': ['code']}),
        ('TestRail ID', {'fields': ['testrail_id']})
    ]
    # what to display in the admin table list
    list_display = ('name', 'code', 'testrail_id')
    # what field(s) to filter the list by (side panel)
    list_filter = ['name']
    # what field(s) the search field will look in
    search_fields = ['name']

####################################################################################################
# Register Models ##################################################################################
####################################################################################################
####################################################################################################

models_to_register = [
    (Products, ProductsAdmin),
    Features,
    TestSuites,
    Sections,
    TestCases,
    ProcedureSteps,
    Functions,
    TestTypes,
]

for model in models_to_register:
    try:
        admin.site.register(model[0], model[1])
    except TypeError:
        admin.site.register(model)