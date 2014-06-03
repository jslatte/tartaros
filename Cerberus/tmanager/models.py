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


class Products(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the product.",
    )
    code = models.CharField(
        max_length=200,
        unique=True,
        help_text="The code that will be used to reference the object.",
    )
    testrail_id = models.IntegerField(
        unique=True,
        help_text="The ID of the corresponding project in TestRail.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'products'
        verbose_name_plural = 'products'


class TestSuites(models.Model):
    product = models.ForeignKey(
        to=Products,
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the test suite.",
    )
    testrail_id = models.IntegerField(
        unique=True,
        help_text="The ID of the corresponding project in TestRail.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'test_suites'
        verbose_name_plural = 'Test Suites'