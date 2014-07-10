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
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the test suite.",
    )
    testrail_id = models.IntegerField(
        unique=True,
        help_text="The ID of the corresponding test suite in TestRail.",
    )
    product = models.ForeignKey(
        to=Products,
        help_text="The product with which this test suite is associated.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'test_suites'
        verbose_name_plural = 'Test Suites'


class Features(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the product feature.",
    )
    product = models.ForeignKey(
        to=Products,
        help_text="The product with which this feature is associated.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'features'
        verbose_name_plural = 'Features'


class Sections(models.Model):
    name = models.CharField(
        max_length=200,
        unique=False,
        help_text="The name of the section (e.g., 'Feature Name', 'Story Name', 'Test Name').",
    )
    test_suite = models.ForeignKey(
        to=TestSuites,
        help_text="The test suite in which this section is included."
    )
    feature = models.ForeignKey(
        to=Features,
        help_text="The feature with which this section is associated.",
    )
    parent = models.ForeignKey(
        to='self',
        blank=True,
        null=True,
        help_text="The parent section of this section. "
                  "This section will be considered a sub-section of its parent "
                  "(e.g., a user story section would be a sub-section of a feature section). "
                  "NOTE: leaving this blank will cause the section to be treated as a"
                  "top-level section.",
    )
    testrail_id = models.IntegerField(
        unique=True,
        help_text="The ID of the corresponding section in TestRail.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'sections'
        verbose_name_plural = 'Sections'


class Functions(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the function (no underscores). "
                  "NOTE: this name will be translated on execution by replacing all empty spaces "
                  "with underscore characters and being converted to all lowercase.",
    )
    product = models.ForeignKey(
        to=Products,
        help_text="The product with which this function is associated. NOTE: the code object "
                  "field of the associated product will be used to call the function "
                  "(e.g., product_code.function_name('procedure step arguments ...').",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'functions'
        verbose_name_plural = 'Functions'


class ProcedureSteps(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the procedure step.",
    )
    function = models.ForeignKey(
        to=Functions,
        help_text="The name of the method to execute.",
    )
    arguments = models.CharField(
        max_length=200,
        blank=True,
        help_text="The arguments to send to the function when executing (what will be in the "
                  "method() parenthesis).",
    )
    verification = models.BooleanField(
        help_text="Whether the step will be used for verification. If True, the test case will "
                  "be considered to have failed if this step fails.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'procedure_steps'
        verbose_name_plural = 'Procedure Steps'


class TestTypes(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="The unique name of the type of test.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'test_types'
        verbose_name_plural = 'Test Types'


class TestCases(models.Model):
    name = models.CharField(
        max_length=200,
        unique=False,
        help_text="The name of the test case.",
    )
    test = models.ForeignKey(
        to=Sections,
        help_text="The section in which this test case is included.",
    )
    procedure = models.CommaSeparatedIntegerField(
        max_length=200,
        unique=False,
        help_text="The procedure steps of the test case, organized by procedure step "
                  "ID in comma-delimited format (e.g., '1, 2, 3').",
    )
    min_version = models.DecimalField(
        decimal_places=1,
        max_digits=4,
        help_text="The minimum version of the product against which this test case is valid.",
    )
    level = models.IntegerField(
        help_text="The level of the test case (e.g., a test case for a top-level section is "
                  "a level 0 test case, for a third-level would be a level 2 test case, etc.).",
    )
    active = models.BooleanField(
        help_text="Whether the test case is active or not. If inactive, the test case will "
                  "not be run as a part of any generated test runs.",
    )
    type = models.ManyToManyField(
        to=TestTypes,
        help_text="The type of test (e.g., Regression, Stress, etc.).",
    )
    testrail_id = models.IntegerField(
        unique=True,
        help_text="The ID of the corresponding test case in TestRail.",
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'test_cases'
        verbose_name_plural = 'Test Cases'


class RemoteServers(models.Model):
    name = models.CharField(
        max_length=200,
        unique=False,
        help_text="The name of the remote server.",
    )
    ip_address = models.CharField(
        verbose_name="IP Address",
        max_length=200,
        unique=False,
        help_text="The IP address of the remote server.",
    )

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.ip_address)

    class Meta:
        db_table = 'remote_servers'
        verbose_name_plural = 'Remote Servers'