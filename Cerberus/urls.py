####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from django.conf.urls import patterns, include, url
from django.contrib import admin

####################################################################################################
# URLs #############################################################################################
####################################################################################################
####################################################################################################

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Cerberus.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # point the root URLconf at the erinyes.urls module
    #   NOTE: whenever Django encounters include(), it chops off whatever part of the URL
    #       matched up to the '/' point and sends the remaining string to the included URLconf
    #       for further processing.
    url(r'^Erinyes/', include('Erinyes.urls', namespace="Erinyes"))
)
