####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from django.conf.urls import patterns, url
import views

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
# URLs #############################################################################################
####################################################################################################
####################################################################################################

urlpatterns = patterns('',
    # the url() function is passed four arguments: (regex, view, (opt) kwargs, (opt) name)
    #   regex: regular expression for matching patterns in strings (url patterns). Django
    #       starts at the first regular expression and makes its way down the list, comparing
    #       the requested URL against each regular expression until it finds one that matches.
    #       NOTE: these regular expressions do not search GET and POST parameters, or domain
    #       name. The regular expressions are compiled the first time the URLconf module
    #       is loaded.
    #   view: when Django finds a regular expression match, it calls the specified view
    #       function with an HttpRequest object as the first argument and any "captured"
    #       values fromt he regular expression as other arguments. With simple captures,
    #       values are passed as positional arguments, named captures as keyword arguments.
    #   kwargs: arbitrary keyword arguments in a dictionary that can be passed to the
    #       target view.
    #   name: an unambiguous name for the URL that lets you refer to it from elsewhere in
    #       Django, especially templates. This allows you to make global changes to the URL
    #       patterns of the project while only touching a single file.

    # ex: /polls/
    #url(r'^$', views.index, name='index'),
    # the 'name' value as called by the {% url %} template tag
    # ex: /polls/5/
    #url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    #url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    #url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote')

    # using generic views
    url(r'^$', views.Index.as_view(), name='index'),
)