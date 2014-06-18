####################################################################################################
#
# Copyright (c) by Jonathan Slattery
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from django.db import models

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
# Classes ##########################################################################################
####################################################################################################
####################################################################################################


class DVR(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the DVR.",
    )
    ip_address = models.CharField(
        verbose_name="IP Address",
        max_length=200,
        unique=False,
        help_text="The IP address of the DVR.",
    )
    username = models.CharField(
        max_length=200,
        unique=False,
        help_text="The name of the user to use to log into the DVR (should have admin privileges).",
    )
    password = models.CharField(
        max_length=200,
        unique=False,
        null=True,
        blank=True,
        help_text="The password of the user to use to log into the DVR.",
    )

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.ip_address)

    class Meta:
        app_label = 'erinyes'
        db_table = 'dvrs'
        verbose_name_plural = 'DVRs'


class Site(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the site.",
    )
    dvr = models.ForeignKey(
        to=DVR,
        help_text="The corresponding DVR of the site."
    )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'erinyes'
        db_table = 'sites'
        verbose_name_plural = 'Sites'


class ConnectionType(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the connection type.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'erinyes'
        db_table = 'connection_types'


class Connection(models.Model):
    site = models.ForeignKey(
        to=Site,
        help_text="The site that made the connection.",
    )
    start = models.IntegerField(
        help_text="The date/time the connection started (UTC in seconds).",
    )
    end = models.IntegerField(
        null=True,
        blank=True,
        help_text="The date/time the connection ended (UTC in seconds).",
    )
    connection_type = models.ForeignKey(
        to=ConnectionType,
        help_text="The type of connection made by the site.",
    )

    def __unicode__(self):
        return "%s (%s to %s)" % (self.site, self.start, self.end)

    class Meta:
        app_label = 'erinyes'
        db_table = 'connection_log'