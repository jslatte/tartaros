###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from logger import Logger
from exceptionhandler import ExceptionHandler
import inspect
from collections import OrderedDict
from time import sleep
from testcase import HestiaTestCase
from Database import Database
from testrun import TestRun

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

log = Logger()

####################################################################################################
# Test Manager #####################################################################################
####################################################################################################
####################################################################################################


class TestManager():
    """ A library of functions to be used by the Test Manager app.
    """

    def __init__(self, log, exception_handler):
        """
        @param log: an initialized Logger() to inherit.
        @param exception handler: an un-initialized ExceptionHandler() to inherit.
        """

        # inherit logger (initialized instance)
        self.log = log

        # inherit exception handler
        self.handle_exception = exception_handler

        # define class attributes
        self.tables = {'module':     db.modules,
                       'feature':    db.features,
                       'user story': db.user_stories,
                       'test':       db.tests,
                       'test case':  db.test_cases}

    def TEMPLATE(self):
        """
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def update_tmanager_form(self):
        """ Update the tmanager form (when an item is selected from a drop-down list).
        @return: a SELECT() object to replace the previous drop-down list.
        """

        operation = inspect.stack()[0][3]

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            result = SELECT(OPTION(''))

            # generate correct selection object (by input data)
            # if module or feature field changed, then update the user story field
            if request.vars.module_selection or request.vars.feature_selection:
                self.log.trace("Updating user story field ...")

                # determine object type
                obj_type = 'user story'

                # determine user story options for selection
                options = db(db.user_stories.module_id == request.vars.module_selection).select(db.user_stories.ALL)

                # filter by selected feature
                options.exclude(lambda entry: str(entry.feature_id) != str(request.vars.feature_selection))

            # if user story field changed, then update the test field
            elif request.vars.user_story_selection:
                self.log.trace("Updating test field ...")

                # determine object type
                obj_type = 'test'

                # determine test options for selection ('0' given if the field should be cleared
                #   due to a parent selection being updated or reset)
                if str(request.vars.user_story_selection) is '0':
                    options = []
                else:
                    options =  db(db.tests.user_story_id == request.vars.user_story_selection).select(db.tests.ALL)

            # if test field changed, then update the test case field
            elif request.vars.test_selection:
                self.log.trace("Updating test case field ...")

                # determine object type
                obj_type = 'test case'

                # determine test case options for selection ('0' given if the field should be cleared
                #   due to a parent selection being updated or reset)
                if str(request.vars.test_selection) == '0':
                    options = []
                else:
                    options = db(db.test_cases.test_id
                                 == request.vars.test_selection).select(db.test_cases.ALL)

            # unknown field changed
            else:
                self.log.warn("No valid field changed.")
                obj_type = None
                options = None

            if obj_type is not None and options is not None:
                # define new selection object
                selection = self.build_tmanager_ts_dropdown_object(obj_type, options)['select']

                # compile return data
                result = selection

            # return
            self.log.trace("... DONE %s." % operation.replace('_', ' '))
            return result

        except BaseException, e:
            self.handle_exception(self.log, e, operation)
            return False

    def update_test_attribute_field(self, field):
        """ Update the test attribute field (if test dropdown changed).
        @param field: the field to update (e.g., 'test results id', 'test case class', 'test case minimum version').
        @return: LABEL() containing test results id for selected test.
        """

        operation = inspect.stack()[0][3]
        result = LABEL()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine test results id for selected test
            result = self.build_test_attribute_field(field)['div']

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def update_test_case_procedure_table(self):
        """ Update the test case procedure table on test case selection
        @return: a TBODY() containing the update table data to replace inside the procedure TABLE().
        """

        operation = inspect.stack()[0][3]
        result = TABLE()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine test case procedure
            try:
                steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure

            except IndexError:
                log.trace("Cannot determine procedure. No test case selected.")
                steps=None

            # build updated test case procedure table (body)
            tbody_proc = self.build_procedure_table(steps=steps)['table']

            # compile results
            result = tbody_proc

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        return result

    def update_tmanager_selection(self):
        """ Update the Test Manager selection drop down (and refresh update cell).
        @return: test manager DIV() (to fully update form).
        """

        operation = inspect.stack()[0][3]
        result = DIV()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            log.trace(str(request.vars))

            # SELECT() object id
            select_addr = request.vars.selectaddr

            # field value
            input_val = eval("request.vars.%s" % request.vars.field)
            user_type = eval("request.vars.%s_user_type" % request.vars.field)

            # update field in database
            log.trace("Updating %s table: changing %s %s to %s ..." % (request.vars.type, request.vars.type,
                                                                       request.vars.id, input_val))
            if request.vars.type == "user story":
                db(self.tables[request.vars.type].id
                   == request.vars.id).update(action=input_val)
                db(self.tables[request.vars.type].id
                   == request.vars.id).update(user_type=user_type)
            elif request.vars.type in self.tables.keys():
                db(self.tables[request.vars.type].id
                   == request.vars.id).update(name=input_val)
            else:
                response.flash("Failed to update entry.")
                val = "N/A"

            # rebuild selection
            select = self.build_tmanager_ts_dropdown_object(select_addr.replace('_selection', '').replace('_', ' '))['select']

            # compile return data
            result = select

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def add_procedure_step_to_test_case(self, step_id, test_case_id):
        """ Add a procedure step to a test case.
        @param step_id: the id of the procedure step to add.
        @param test_case_id: the id of the test case to which to add the procedure step.
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # get the current procedure for the test case
            procedure = db(db.test_cases.id == test_case_id).select()[0].procedure

            # update the procedure for the test case
            procedure += ',%s' % step_id
            db(db.test_cases.id == test_case_id).update(procedure=procedure)

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def modify_procedure_step_for_test_case(self, row, test_case_id, action, step_id=None,
                                            name=None, funct=None, args=None, vrf=None):
        """ Add a procedure step to a test case.
        @param row: the row for which the procedure step is being changed.
        @param step_id: the id of the procedure step to add.
        @param test_case_id: the id of the test case to which to add the procedure step.
        @param action: the action to perform ('change', 'delete').
        @param name: the name with which to update the step.
        @param funct: the function id with which to update the step.
        @param args: the arguments with which to update the step.
        @param vrf: the verification status with which to update the step.
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # get the current procedure for the test case
            procedure = db(db.test_cases.id == test_case_id).select()[0].procedure

            # translate the procedure into a list of steps that corresponds to the rows
            proc_steps = procedure.split(',')

            if action == 'change' and step_id is not None:
                # change the procedure step
                proc_steps[int(row)] = step_id

            elif action == 'delete':
                del proc_steps[int(row)]

            # rebuild the procedure string
            if action == 'change' or action == 'delete':
                procedure = ''
                if len(proc_steps) > 0:
                    procedure += proc_steps[0]

                if len(proc_steps) > 1:
                    for step in proc_steps[1:]:
                        procedure += ',%s' % step

                # update the procedure for the test case
                db(db.test_cases.id == test_case_id).update(procedure=procedure)

            elif action == 'edit':
                # determine step id
                step_id = proc_steps[int(row)]

                # return step from database
                proc_step = db(db.procedure_steps.id == step_id).select()[0]

                # determine new values for each step field
                if name is None:
                    name = proc_step.name
                if funct is None:
                    funct = proc_step.function_id
                if args is None:
                    args = proc_step.arguments
                if vrf is None:
                    vrf = proc_step.verification

                # update procedure step in database.
                db(db.procedure_steps.id == step_id).update(
                    name=name,
                    function_id=funct,
                    arguments=args,
                    verification=vrf
                )

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def add_new_procedure_step(self, name, funct, args, vrf):
        """ Add new procedure step.
        @param name: the name of the step.
        @param funct: the function id of the step.
        @param args: the arguments of the step.
        @param vrf: the verification status of the step.
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # insert new procedure step into database
            db.procedure_steps.insert(
                name=name,
                function_id=funct,
                arguments=args,
                verification=vrf
            )

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_td_add_ts_entry(self, select_addr):
        """ Build the add new test suite (selection) entry object.
        @param select_addr: the HTML id of the test suite selection object (for adding new entries to it).
        @return: a dict containing:
            'div' - the DIV() container for the button.
            'td' - the TD() containing the DIV().
        """

        operation = inspect.stack()[0][3]
        result = {'div': DIV(), 'td': TD()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine the suite type (e.g., module, feature, test case, etc.)
            suite_type = select_addr.replace('_selection', '')

            # define the "Add New" button
            btn_add_ts_entry_addr = 'td_%s_add_ts_entry_btn' % select_addr
            div_add_ts_entry_addr = 'td_%s_add_ts_entry_div' % select_addr
            td_add_ts_entry_addr = 'td_%s_add_ts_entry' % select_addr
            btn_add_script = "ajax('enable_ts_add?selectaddr=%(selectaddr)s&container=%(container)s&type=%(type)s', " \
                             "%(values)s, '%(target)s'); " \
                             "jQuery(%(div addr)s).remove();" % {'selectaddr': select_addr,
                                                                 'container': td_add_ts_entry_addr,
                                                                 'type': suite_type,
                                                                 'values': "['module_selection', 'feature_selection',"
                                                                           "'user_story_selection', 'test_selection',"
                                                                           "'test_case_selection']",
                                                                 'target': td_add_ts_entry_addr,
                                                                 'div addr': div_add_ts_entry_addr}
            btn_add_ts_entry = INPUT(_type='button', _value='+', _id=btn_add_ts_entry_addr, _class='btn',
                                     _onclick=btn_add_script)
            div_add_ts_entry = DIV(btn_add_ts_entry, _id=div_add_ts_entry_addr)
            td_add_ts_entry = TD(div_add_ts_entry, _id=td_add_ts_entry_addr)

            # compile results
            result['div'] = div_add_ts_entry
            result['td'] = td_add_ts_entry

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_td_confirm_add_ts_entry(self, select_addr, container, suite_type):
        """ Build the add new test suite (selection) entry input and confirm/cancel object.
        @param select_addr: the HTML id of the test suite selection object (for adding new entries to it).
        @param container: the TD() container object for the original add button (used to get here).
        @param suite_type: the type of suite object (e.g., module, feature, test case, etc.).
        @return: a dict containing:
            'div' - the DIV() container for the button.
        """

        operation = inspect.stack()[0][3]
        result = {'div': DIV(), 'td': TD()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # define the add new entry confirmation object addresses (ids)
            inp_new_name_addr = 'inp_new_%s_name' % suite_type
            inp_new_action_addr = 'inp_new_user_story_action'
            inp_new_user_type_addr = 'inp_new_user_story_user_type'
            inp_new_results_id_addr = 'inp_new_test_results_id'
            btn_cnf_add_ts_entry_addr = 'td_%s_cnf_add_ts_entry_btn' % select_addr
            btn_cnc_add_ts_entry_addr = 'td_%s_cnc_add_ts_entry_btn' % select_addr
            div_cnf_add_ts_entry_addr = 'td_%s_cnf_add_ts_entry_div' % select_addr
            td_cnf_add_ts_entry_addr = 'td_%s_add_ts_entry' % select_addr

            # build inputs (to be included based on type of suite to be added)
            inp_new_name_label = LABEL("Name:")
            inp_new_name = INPUT(_id=inp_new_name_addr, _name=inp_new_name_addr,
                                 _class="string", _type="text")
            inp_new_action_label = LABEL(" will ")
            inp_new_action = INPUT(_id=inp_new_action_addr, _name=inp_new_action_addr,
                                   _class="string", _type="text")
            inp_new_user_type_label = LABEL("A/The ")
            options = db().select(db.user_types.ALL)
            inp_new_user_type = SELECT(_id=inp_new_user_type_addr, _name=inp_new_user_type_addr,
                                       *[OPTION(options[i].name, _value=str(options[i].id))
                                         for i in range(len(options))])
            inp_new_results_id_label = LABEL("Test Results ID")
            inp_new_results_id = INPUT(_id=inp_new_results_id_addr, _name=inp_new_results_id_addr,
                                       _class="string", _type="text")

            # build add new entry confirmation button
            btn_cnf_add_ts_entry_script = "ajax('%(function)s?type=%(type)s', %(values)s, '%(target)s');" \
                                          "jQuery(%(remove)s).remove();" % {'function': 'add_ts_entry',
                                                                            'type': suite_type,
                                                                            'values': "['%s', 'module_selection',"
                                                                                      "'feature_selection', "
                                                                                      "'user_story_selection',"
                                                                                      "'test_selection',"
                                                                                      "'test_case_selection',"
                                                                                      "'inp_new_user_story_action',"
                                                                                      "'inp_new_user_story_user_type',"
                                                                                      "'inp_new_test_results_id']"
                                                                                      % inp_new_name_addr,
                                                                            'target': 'td_%s' % select_addr,
                                                                            'remove': '%s' % select_addr}
            btn_cnf_add_ts_entry_script += "ajax('%(function)s?selectaddr=%(selectaddr)s', %(vars)s, '%(target)s');" \
                                           "jQuery(%(remove obj)s).remove();" \
                                           % {'function':    'restore_ts_add_new_cell',
                                              'selectaddr':  select_addr,
                                              'vars':        "[]",
                                              'target':      '%s' % td_cnf_add_ts_entry_addr,
                                              'remove obj':  div_cnf_add_ts_entry_addr}
            btn_cnf_add_ts_entry = INPUT(_id=btn_cnf_add_ts_entry_addr, _type='button', _value='Add', _class='btn',
                                         _onclick=btn_cnf_add_ts_entry_script)

            # build add new entry cancel button
            btn_cnc_add_ts_entry_script = "ajax('%(function)s?selectaddr=%(selectaddr)s', %(values)s, '%(target)s');" \
                                          "jQuery(%(div addr)s).remove();" % {'function': 'cancel_add_ts_entry',
                                                                              'selectaddr': select_addr,
                                                                              'values': '[]',
                                                                              'target': container,
                                                                              'div addr': div_cnf_add_ts_entry_addr}
            btn_cnc_add_ts_entry = INPUT(_id=btn_cnc_add_ts_entry_addr, _type='button', _value='Cancel', _class='btn',
                                         _onclick=btn_cnc_add_ts_entry_script)

            # build entire object (by input type)
            if request.vars.type == "user_story":
                div_cnf_add_ts_entry = FORM(inp_new_user_type_label, inp_new_user_type,
                                           inp_new_action_label, inp_new_action,
                                           btn_cnf_add_ts_entry, btn_cnc_add_ts_entry,
                                       _id=div_cnf_add_ts_entry_addr)
            elif request.vars.type == "test":
                div_cnf_add_ts_entry = FORM(inp_new_name_label, inp_new_name,
                                           inp_new_results_id_label, inp_new_results_id,
                                           btn_cnf_add_ts_entry, btn_cnc_add_ts_entry,
                                           _id=div_cnf_add_ts_entry_addr)
            else:
                div_cnf_add_ts_entry = FORM(inp_new_name_label, inp_new_name,
                                           btn_cnf_add_ts_entry, btn_cnc_add_ts_entry,
                                           _id=div_cnf_add_ts_entry_addr)

            # compile results
            result['div'] = div_cnf_add_ts_entry

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_test_attribute_field(self, field):
        """ Build the table cell for a test/test case attribute (e.g., test results id, test class, etc.).
        @param field: the field to create (e.g., 'test results id', 'test case class', 'test case minimum version').
        @return: a dict containing:
            'tr' - the TR() object.
            'td' - the TD() object.
            'div' - a subcontainter DIV() with the cell data.
        """

        operation = inspect.stack()[0][3]
        result = {'td': TD(), 'div': DIV(), 'tr': TR()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine value of field
            try:
                if field == 'test results id':
                    val = db(db.tests.id == request.vars.test_selection).select()[0].results_id

                elif field == 'test case class':
                    val = db(db.test_cases.id == request.vars.test_case_selection).select()[0].test_class

                elif field == 'test case minimum version':
                    val = db(db.test_cases.id == request.vars.test_case_selection).select()[0].min_version

                elif field == 'test case active':
                    active = db(db.test_cases.id == request.vars.test_case_selection).select()[0].active
                    if str(active) == '1':
                        val = "Yes"
                    else:
                        val = "No"

                else:
                    val = "N/A"

            except IndexError or TypeError:
                if field == 'test results id':
                    val = "No test selected."
                else:
                    val = "No test case selected."

            # determine field label by field type
            field_label = field.replace('test ', '').replace('case ', '').upper() + ":"

            # determine object ids by field type
            obj_id = field.lower().replace(' ', '_')
            test_attribute_val_addr = '%s_val' % obj_id
            div_test_attribute_val_addr = 'div_%s_val' % obj_id
            td_test_attribute_val_addr = 'td_%s_val' % obj_id
            tr_test_attribute_addr = 'tr_%s' % obj_id

            # build the onclick script
            script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                     "jQuery(%(remove)s).remove();" \
                     % {'function': 'enable_%s_edit' % obj_id,
                        'values': "['%s']" % test_attribute_val_addr,
                        'target': '%s' % td_test_attribute_val_addr,
                        'remove': '%s' % div_test_attribute_val_addr}

            # build the object
            test_attribute_val = LABEL(val,
                                       _id=test_attribute_val_addr, _name=test_attribute_val_addr,
                                       _onclick=script)
            div_test_attribute_val = DIV(test_attribute_val,
                                         _id=div_test_attribute_val_addr)
            td_test_attribute_val = TD(div_test_attribute_val,
                                       _id=td_test_attribute_val_addr)
            td_test_attribute_label = TD(LABEL(field_label))
            tr_test_attribute = TR(
                td_test_attribute_label,
                td_test_attribute_val,
                _id=tr_test_attribute_addr
            )

            # compile results
            result['tr'] = tr_test_attribute
            result['td'] = td_test_attribute_val
            result['div'] = div_test_attribute_val

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_edit_test_attribute_field(self, field, c_value=None):
        """ Build the edit field cell for a test/test case attribute (e.g., test results id, test class, etc.).
        @param field: the field to edit (e.g., 'test results id', 'test case class', 'test case minimum version').
        @param c_value: the value in the field when clicking to edit
        @return: a dict containing:
            'form' - a subcontainter FORM() with the cell data.
        """

        operation = inspect.stack()[0][3]
        result = {'form': FORM()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            self.log.warn(request.vars)

            # determine object ids by field type
            obj_id = field.lower().replace(' ', '_')
            test_attribute_val_addr = '%s_edit_val' % obj_id
            div_test_attribute_val_addr = 'div_%s_edit_val' % obj_id
            td_test_attribute_val_addr = 'td_%s_val' % obj_id

            # build the input field
            if field == 'test case active':
                test_attribute_edit = SELECT(*[OPTION('Yes', _value='1'), OPTION('No', _value='0')],
                                             _id=test_attribute_val_addr, _name=test_attribute_val_addr)
            elif field == 'test case class':
                test_attribute_edit = SELECT(*[
                    OPTION('0', _value='0'),
                    OPTION('1', _value='1'),
                    OPTION('2', _value='2'),
                    OPTION('3', _value='3'),
                    OPTION('4', _value='4'),
                    OPTION('5', _value='5'),
                ],
                                            _id=test_attribute_val_addr, _name=test_attribute_val_addr)
            else:
                test_attribute_edit = INPUT(_class="string", _type="text", _value=c_value,
                                            _id=test_attribute_val_addr, _name=test_attribute_val_addr)

            # build confirmation button
            btn_cnf_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                             % {'function': 'edit_%s_field' % obj_id,
                                'values': "['%s', 'test_selection', 'test_case_selection']" % test_attribute_val_addr,
                                'target': ''}
            restore_script = "jQuery(%(remove)s).remove();" \
                             "ajax('%(function)s', %(values)s, '%(target)s');" \
                             % {'function': 'restore_%s_field' % obj_id,
                                'values': "['test_selection', 'test_case_selection']",
                                'target': '%s' % td_test_attribute_val_addr,
                                'remove': '%s' % div_test_attribute_val_addr}
            btn_cnf_script += restore_script
            btn_cnf = INPUT(_type='button', _value='Update', _class='btn',
                            _onclick=btn_cnf_script)

            # build cancel button
            btn_cnc_script = restore_script
            btn_cnc = INPUT(_type='button', _value='Cancel', _class='btn',
                            _onclick=btn_cnc_script)

            # build form
            f_test_attribute_edit = DIV(test_attribute_edit, btn_cnf, btn_cnc,
                                         _id=div_test_attribute_val_addr)

            # compile results
            result['form'] = f_test_attribute_edit

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_tmanager_ts_dropdown_object(self, select_type=None, options=None):
        """
        @param select_type: the selection type of drop-down list (e.g., module, feature, etc.).
        @param options: the options for the drop-down list.
        @return: a dict including
            - a TR() containing the drop-down object(s)
            - a SELECT() with the drop-down
        """

        operation = inspect.stack()[0][3]

        try:
            self.log.trace("%s: (type='%s') ..." % (operation.replace('_', ' '), select_type))
            result = {'object': TR(), 'select': SELECT()}

            # determine select type (if None)
            if select_type is None:
                select_type = request.vars.type

            # determine options (if None)
            if options is None:

                # regenerate selections with only items within parent suite (if possible)
                if select_type == 'module' or select_type == 'feature':
                    options = db().select(self.tables[select_type].ALL)

                elif select_type == 'user story' \
                    and (request.vars.module_selection is not None and str(request.vars.module_selection) != '0') \
                    and (request.vars.feature_selection is not None and str(request.vars.module_selection) != '0'):
                    # determine user story options for selection
                    options = db(db.user_stories.module_id == request.vars.module_selection).select(db.user_stories.ALL)

                    # filter by selected feature
                    options.exclude(lambda entry: str(entry.feature_id) != str(request.vars.feature_selection))

                elif select_type == 'test' \
                    and (request.vars.user_story_selection is not None and str(request.vars.user_story_selection) != '0'):

                    options =  db(db.tests.user_story_id == request.vars.user_story_selection).select(db.tests.ALL)

                elif select_type == 'test case' \
                    and (request.vars.test_selection is not None and str(request.vars.test_selection) != '0'):

                    options = db(db.test_cases.test_id == request.vars.test_selection).select(db.test_cases.ALL)

                # otherwise, default to grabbing all items from db table
                else:
                    options = []

            # determine object type (by dict)
            object_types = OrderedDict([
                ('module', 'module'),
                ('feature', 'feature'),
                ('user story', 'user_story'),
                ('test', 'test'),
                ('test case', 'test_case')]
            )
            obj_type = object_types[select_type.lower()]

            # define general variables (non-type-specific)
            name = obj_type
            ajax_s_template = "ajax('update_tmanager_form', %s, 'td_%s_selection'); "
            ajax_s_template2 = "ajax('update_tmanager_form?%s_selection=0', %s, 'td_%s_selection'); "
            jquery_s_template = "jQuery(%s_selection).remove(); "
            update_tproc_script = "jQuery(tbody_proc).remove(); " \
                                  "ajax('update_test_case_procedure_table', ['%s_selection'], 't_proc');" %\
                                  object_types['test case']
            update_test_results_id_script = "jQuery(div_test_results_id_val).remove(); " \
                                            "ajax('update_test_results_id_field', " \
                                            "['%s_selection'], 'td_test_results_id_val');" %object_types['test']
            update_test_case_class_script = "jQuery(div_test_case_class_val).remove(); " \
                                            "ajax('update_test_case_class_field', " \
                                            "['%s_selection'], 'td_test_case_class_val');" % object_types['test case']
            update_test_case_minver_script = "jQuery(div_test_case_minimum_version_val).remove(); " \
                                             "ajax('update_test_case_minver_field', " \
                                             "['%s_selection'], 'td_test_case_minimum_version_val');" \
                                             % object_types['test case']
            update_test_case_active_script = "jQuery(div_test_case_active_val).remove(); " \
                                             "ajax('update_test_case_active_field', " \
                                             "['%s_selection'], 'td_test_case_active_val');" \
                                             % object_types['test case']

            # customize drop-down variables based on type
            self.log.trace("... building %s drop-down object ..." % obj_type)

            # module or feature drop-down objects
            if obj_type == object_types['module'] or obj_type == object_types['feature']:
                # input data determines the selection object values to send to the tmanager update
                #   function when the selection is changed (e.g., 'module' is the name of the
                #   module selection object, telling tmanager update that the module field was
                #   updated.
                input_data = "['module_selection', 'feature_selection']"

                # on change event target is the selection object that should be updated when
                #   this selection object is changed (e.g., for 'module' or 'feature', the 'user story'
                #   object is the target to update.
                on_change_event_target = object_types['user story']

                # build the options list for the selection object by enumerating each option using
                #   the list of options given on initializing the function
                selections = [OPTION(options[i].name, _value=str(options[i].id))
                              for i in range(len(options))]

                # build jQuery statement (includes removing all cascading drop-down lists)
                self.log.trace("... building jQuery statement ...")
                jquery_s = jquery_s_template % object_types['user story']
                jquery_s += jquery_s_template % object_types['test']
                jquery_s += jquery_s_template % object_types['test case']

                # build ajax statement (includes all AJAX calls to tmanager update to rebuild the
                #   cascading lists correctly. ajax_s_template is the update of the subsequent field
                #   to update (input data indicates field to update, target is the field to update).
                #   ajax_s_template2 is for clearing additional cascading fields (e.g., test case when
                #   updating user story, because the test needs to be selected first). First substitution
                #   is the same as the input field (the parent field of the target field).
                self.log.trace("... building AJAX statement ...")
                ajax_s = ajax_s_template % (input_data, object_types['user story'])
                ajax_s += ajax_s_template2 % (object_types['user story'],
                                              "['%s_selection']" % object_types['user story'],
                                              object_types['test'])
                ajax_s += ajax_s_template2 % (object_types['test'],
                                              "['%s_selection']" % object_types['test'],
                                              object_types['test case'])

                # add update test attributes statements
                ajax_s += update_test_results_id_script
                ajax_s += update_test_case_class_script
                ajax_s += update_test_case_minver_script
                ajax_s += update_test_case_active_script

                # add update test case procedure statement (will clear)
                ajax_s += update_tproc_script

            # user story drop-down objects
            elif obj_type == object_types['user story']:
                # input data
                input_data = "['%s']" % obj_type

                # event target
                on_change_event_target = object_types['test']

                # build selection list
                shown_vals = []
                for i in range(len(options)):
                    # build displayed value from user type and action. This puts together the action
                    #   with the user type and some prepositional phrases to make it readable (unlike
                    #   the other fields, which just use the name).
                    self.log.trace("... building displayed value from user type and action ...")
                    user_type = db(db.user_types.id == options[i].user_type).select()[0]['name']
                    if str(options[i].user_type) == '2':
                        shown_val = "The %s will %s." % (user_type, options[i].action)
                    else:
                        shown_val = "A %s can %s." % (user_type, options[i].action)

                    shown_vals.append(shown_val)

                # build the options list for the selection object
                selections = [OPTION(shown_vals[i], _value=str(options[i].id))
                                   for i in range(len(options))]


                # build jQuery statement
                self.log.trace("... building jQuery statement ...")
                jquery_s = jquery_s_template % object_types['test']
                jquery_s += jquery_s_template % object_types['test case']

                # build ajax statement
                self.log.trace("... building AJAX statement ...")
                ajax_s = ajax_s_template % ("['%s_selection']" % obj_type, object_types['test'])
                ajax_s += ajax_s_template2 % (object_types['test'],
                                              "['%s_selection']" % object_types['test'],
                                              object_types['test case'])

                # add update test attributes statements
                ajax_s += update_test_results_id_script
                ajax_s += update_test_case_class_script
                ajax_s += update_test_case_minver_script
                ajax_s += update_test_case_active_script

                # add update test case procedure statement (will clear)
                ajax_s += update_tproc_script

            # test drop-down objects
            elif obj_type == object_types['test']:
                # input data
                input_data = "['%s']" % obj_type

                # event target
                on_change_event_target = object_types['test case']

                # build the options list for the selection object
                selections = [OPTION(options[i].name, _value=str(options[i].id))
                              for i in range(len(options))]

                # build jQuery statement
                self.log.trace("... building jQuery statement ...")
                jquery_s = jquery_s_template % object_types['test case']

                # build ajax statement
                self.log.trace("... building AJAX statement ...")
                ajax_s = ajax_s_template % ("['%s_selection']" % obj_type, object_types['test case'])

                # add update test attributes statements
                ajax_s += update_test_results_id_script
                ajax_s += update_test_case_class_script
                ajax_s += update_test_case_minver_script
                ajax_s += update_test_case_active_script

                # add update test case procedure statement (will clear)
                ajax_s += update_tproc_script

            # test case drop-down objects
            elif obj_type == object_types['test case']:
                # build the options list for the selection object
                selections = [OPTION(options[i].name, _value=str(options[i].id))
                              for i in range(len(options))]

                # build jQuery statement
                self.log.trace("... building jQuery statement ...")
                jquery_s = ''

                # build ajax statement
                self.log.trace("... building AJAX statement ...")
                ajax_s = ''

                # add update test attributes statements
                ajax_s += update_test_case_class_script
                ajax_s += update_test_case_minver_script
                ajax_s += update_test_case_active_script

                # add update test case procedure statement
                ajax_s += update_tproc_script

            # unknown drop-down objects
            else:
                self.log.warn("Invalid object type '%s' specified." % obj_type)
                selections = OPTION()
                ajax_s = ''
                jquery_s = ''

            # set first option value (blank option) to '0'
            selections.insert(0, OPTION('', _value='0'))

            # SELECT() object id
            select_addr = '%s_selection' % name

            # define edit/update field components
            update_button_addr = 'td_%s_update_button' % select_addr
            div_update_addr = 'td_%s_update_div' % select_addr
            td_update_addr = 'td_%s_update' % select_addr
            update_button_script = "jQuery(this).remove(); " \
                                   "ajax('enable_tmanager_selection_update?" \
                                   "src=%s" \
                                   "&target=%s" \
                                   "&selectaddr=%s" \
                                   "&type=%s', " \
                                   "['module_selection', 'feature_selection', 'user_story_selection'," \
                                   "'test_selection', 'test_case_selection'], " \
                                   "'%s'); " \
                                   % (select_addr, td_update_addr, select_addr, select_type, td_update_addr)
            div_update = DIV(INPUT(_type='button', _value='Update',
                                   _id=update_button_addr,
                                   _name=update_button_addr,
                                   _onclick=update_button_script,
                                   _class="btn"),
                             _name=div_update_addr,
                             _id=div_update_addr)

            td_update = TD(div_update, _name=td_update_addr, _id=td_update_addr)

            # define the "Add New" button
            td_add_ts_entry = self.build_td_add_ts_entry(select_addr)['td']


            # build drop-down object components based on object-specific data determined above.
            #   All objects should return a label, select, table data cell for the label, table
            #   data cell for the select, and a table row containing both data cells.
            self.log.trace("... building drop-down object components ...")
            selection_label = LABEL('%s:' % name.upper().replace('_', ' '))
            selection = SELECT(_name=select_addr, _id=select_addr,
                               _onchange=jquery_s + ajax_s,
                               *[selections])
            td_selection_label = TD(selection_label, _id='td_%s_selection_label' % name)
            td_selection = TD(selection, _id='td_%s_selection' % name)

            # build test case-specific TR() for including test runner div
            if obj_type == object_types['test case']:
                tr_selection = TR(td_selection_label, td_selection, td_update, td_add_ts_entry,
                                  self.build_test_runner_div()['div'],
                                  _id='tr_%s_selection' % name)
            else:
                tr_selection = TR(td_selection_label, td_selection, td_update, td_add_ts_entry,
                                  _id='tr_%s_selection' % name)

            # compile return data
            result['object'] = tr_selection
            result['select'] = selection
            result['update cell'] = div_update

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_add_procedure_step_form(self, row):
        """ Build the add procedure step field form (for adding a new step to test case procedure).
        @param row: the row number in which the form will be created.
        @return: a dict containing:
            'form' - the add procedure step form.
        """

        operation = inspect.stack()[0][3]
        result = {'form': FORM()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine object ids by row
            sel_add_proc_step_addr = 'sel_add_proc_step'
            f_add_proc_step_addr = 'f_add_proc_step_%s' % row
            td_add_proc_addr = 'td_proc_step_%s' % row
            t_proc_addr = 't_proc'
            div_proc_addr = 'div_test_case_procedure'

            # determine options for procedure steps select
            options = db().select(db.procedure_steps.ALL)
            options = options.sort(lambda x: x.name)
            selections = [OPTION(options[i].name, _value=str(options[i].id))
                          for i in range(len(options))]

            # build the input field
            sel_add_proc_step = SELECT(*selections, _id=sel_add_proc_step_addr, _name=sel_add_proc_step_addr)

            # build confirmation button
            btn_cnf_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                             "jQuery(%(remove)s).remove();" \
                             % {'function': 'add_procedure_step_to_test_case',
                                'values': "['%s', 'test_case_selection']" % sel_add_proc_step_addr,
                                'target': '%s' % div_proc_addr,
                                'remove': '%s' % t_proc_addr}
            restore_script = "jQuery(%(remove)s).remove();" \
                             "ajax('%(function)s', %(values)s, '%(target)s');" \
                             % {'function': 'rebuild_test_case_procedure_table',
                                'values': "['test_case_selection']",
                                'target': '%s' % div_proc_addr,
                                'remove': '%s' % t_proc_addr}
            btn_cnf = INPUT(_type='button', _value='Add', _class='btn',
                            _onclick=btn_cnf_script)

            # build cancel button
            btn_cnc_script = restore_script
            btn_cnc = INPUT(_type='button', _value='Cancel', _class='btn',
                            _onclick=btn_cnc_script)

            # build form
            f_add_proc_step = FORM(sel_add_proc_step, btn_cnf, btn_cnc,
                                   _id=f_add_proc_step_addr)

            # compile results
            result['form'] = f_add_proc_step

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_change_procedure_step_form(self, row):
        """ Build the change procedure step field form (for changing step in the test case procedure).
        @param row: the row number of the step to change.
        @return: a dict containing:
            'form' - the change procedure step form.
        """

        operation = inspect.stack()[0][3]
        result = {'form': FORM()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine object ids by row
            sel_edit_proc_step_addr = 'sel_edit_proc_step'
            f_edit_proc_step_addr = 'f_edit_proc_step_%s' % row
            td_proc_addr = 'td_proc_step_%s' % row
            t_proc_addr = 't_proc'
            div_proc_addr = 'div_test_case_procedure'

            # determine options for procedure steps select
            options = db().select(db.procedure_steps.ALL)
            options = options.sort(lambda x: x.name)
            selections = [OPTION(options[i].name, _value=str(options[i].id))
                          for i in range(len(options))]

            # build the input field
            sel_edit_proc_step = SELECT(*selections, _id=sel_edit_proc_step_addr, _name=sel_edit_proc_step_addr)

            # build confirmation button
            btn_cnf_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                             "jQuery(%(remove)s).remove();" \
                             % {'function': 'change_procedure_step_for_test_case?row=%s' % row,
                                'values': "['%s', 'test_case_selection']" % sel_edit_proc_step_addr,
                                'target': '%s' % div_proc_addr,
                                'remove': '%s' % t_proc_addr}
            restore_script = "jQuery(%(remove)s).remove();" \
                             "ajax('%(function)s', %(values)s, '%(target)s');" \
                             % {'function': 'rebuild_test_case_procedure_table',
                                'values': "['test_case_selection']",
                                'target': '%s' % div_proc_addr,
                                'remove': '%s' % t_proc_addr}
            btn_cnf = INPUT(_type='button', _value='Change', _class='btn',
                            _onclick=btn_cnf_script)

            # build cancel button
            btn_cnc_script = restore_script
            btn_cnc = INPUT(_type='button', _value='Cancel', _class='btn',
                            _onclick=btn_cnc_script)

            # build form
            f_add_proc_step = FORM(sel_edit_proc_step, btn_cnf, btn_cnc,
                                   _id=f_edit_proc_step_addr)

            # compile results
            result['form'] = f_add_proc_step

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_edit_procedure_step_form(self, row, test_case_id, create=False):
        """ Build the edit procedure step field form (for editing step in the test case procedure).
        @param row: the row number of the step to edit.
        @param test_case_id: the id of the test case currently being edited.
        @param create: whether a new procedure step is being created or not.
        @return: a dict containing:
            'form' - the edit procedure step form.
        """

        operation = inspect.stack()[0][3]
        result = {'form': FORM()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine object ids by row
            inp_desc_addr = 'inp_edit_proc_step_%s_desc' % row
            inp_funct_addr = 'sel_edit_proc_step_%s_funct' % row
            inp_args_addr = 'inp_edit_proc_step_%s_args' % row
            inp_vrf_addr = 'sel_edit_proc_step_%s_vrf' % row
            f_edit_proc_step_addr = 'f_edit_proc_step_%s' % row
            td_proc_addr = 'td_proc_step_%s' % row
            t_proc_addr = 't_proc'
            div_proc_addr = 'div_test_case_procedure'

            if not create:
                # determine step id
                procedure = db(db.test_cases.id == test_case_id).select()[0].procedure
                proc_steps = procedure.split(',')
                step_id = proc_steps[int(row)]

                # return step from database
                proc_step = db(db.procedure_steps.id == step_id).select()[0]

                # determine canned values for fields
                desc = proc_step.name
                args = proc_step.arguments

            else:
                # determine canned values for fields
                desc = ''
                args = ''

            # build the input fields
            lbl_desc = LABEL("Description")
            inp_desc = INPUT(_value=desc, _id=inp_desc_addr, _name=inp_desc_addr,
                             _class="string", _type="text")

            # function
            lbl_funct = LABEL("Function")
            # build list of function options
            funct_options = []
            # append current function as a duplicate first option
            if not create:
                funct_options.append(OPTION(db(db.functions.id == proc_step.function_id).select()[0].function,
                                            _value=db(db.functions.id == proc_step.function_id).select()[0].id))
            # build sorted list of functions
            functions = db().select(db.functions.ALL)
            functions = functions.sort(lambda x: x.function)
            # add all available options
            for option in functions:
                funct_options.append(OPTION(option.function, _value=option.id))
            # define select object for functions
            sel_funct = SELECT(_id=inp_funct_addr, _name=inp_funct_addr,
                               *[funct_options])

            lbl_args = LABEL("Arguments")
            inp_args = INPUT(_value=args, _id=inp_args_addr, _name=inp_args_addr,
                             _class="string", _type="text")

            # verification step status
            lbl_vrf = LABEL("Verification Step?")
            vrf_options = []
            if not create:
                if proc_step.verification == "True":
                    vrf_options.append(OPTION('Yes', _value='True'))
                    vrf_options.append(OPTION('No', _value='False'))
                else:
                    vrf_options.append(OPTION('No', _value='False'))
                    vrf_options.append(OPTION('Yes', _value='True'))
            else:
                    vrf_options.append(OPTION('No', _value='False'))
                    vrf_options.append(OPTION('Yes', _value='True'))
            sel_vrf = SELECT(_id=inp_vrf_addr, _name=inp_vrf_addr,
                             *vrf_options)

            # build confirmation button
            if not create:
                cnf_funct = 'edit_procedure_step_for_test_case?row=%s' % row
            else:
                cnf_funct = 'create_new_step?row=%s' % row
            btn_cnf_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                             "jQuery(%(remove)s).remove();" \
                             % {'function': cnf_funct,
                                'values': "['test_case_selection', '%s', "
                                          "'%s', '%s', '%s']" % (inp_desc_addr, inp_funct_addr,
                                                                 inp_args_addr, inp_vrf_addr),
                                'target': '%s' % div_proc_addr,
                                'remove': '%s' % t_proc_addr}
            restore_script = "jQuery(%(remove)s).remove();" \
                             "ajax('%(function)s', %(values)s, '%(target)s');" \
                             % {'function': 'rebuild_test_case_procedure_table',
                                'values': "['test_case_selection']",
                                'target': '%s' % div_proc_addr,
                                'remove': '%s' % t_proc_addr}
            btn_cnf = INPUT(_type='button', _value='Change' if not create else 'Add', _class='btn',
                            _onclick=btn_cnf_script)

            # build cancel button
            btn_cnc_script = restore_script
            btn_cnc = INPUT(_type='button', _value='Cancel', _class='btn',
                            _onclick=btn_cnc_script)

            # build form
            f_edit_proc_step = FORM(lbl_desc, inp_desc,
                                    lbl_funct, sel_funct,
                                    lbl_args, inp_args,
                                    lbl_vrf, sel_vrf,
                                    btn_cnf, btn_cnc,
                                    _id=f_edit_proc_step_addr)

            # compile results
            result['form'] = f_edit_proc_step

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_add_procedure_step_button(self, row):
        """ Build an add procedure step button.
        @param row: the row number in which the button will be created.
        @return: a dict containing:
            'button' - the add procedure step button.
            'div' - the div containing the button.
            'td' - the table cell containing the div.
            'tr' - the table row containing the cell.
        """

        operation = inspect.stack()[0][3]
        result = {'button': INPUT(_type='button'), 'div': DIV(), 'td': TD(), 'tr': TR()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine object ids by row
            add_proc_button_addr = 'proc_step_%s_add_btn' % row
            div_add_proc_button_addr = 'div_proc_step_%s' % row
            td_add_proc_button_addr = 'td_proc_step_%s' % row
            tr_add_proc_button_addr = 'tr_proc_step_%s' % row

            # build the onclick script
            script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                     "jQuery(%(remove)s).remove();" \
                     % {'function': 'enable_add_proc_step?row=%s' % row,
                        'values': "[]",
                        'target': '%s' % td_add_proc_button_addr,
                        'remove': '%s' % div_add_proc_button_addr}

            # build the object
            add_proc_button = INPUT(_type='button', _value="Add New Step", _class='btn',
                                    _id=add_proc_button_addr, _name=add_proc_button_addr,
                                    _onclick=script)
            div_add_proc_button = DIV(add_proc_button,
                                      _id=div_add_proc_button_addr)
            td_add_proc_button = TD(div_add_proc_button,
                                    _id=td_add_proc_button_addr)
            tr_add_proc_button = TR(
                TD(),
                td_add_proc_button,
                _id=tr_add_proc_button_addr
            )

            # compile results
            result['tr'] = tr_add_proc_button
            result['td'] = td_add_proc_button
            result['div'] = div_add_proc_button

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_modify_procedure_step_buttons(self, row):
        """ Build the modify procedure step buttons.
        @param row: the row number in which the buttons will be created.
        @return: a dict containing:
            'td' - the cell containing the div.
            'div' - the DIV() containing the buttons
        """

        operation = inspect.stack()[0][3]
        result = {'td': TD()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine object ids by row
            change_proc_button_addr = 'btn_proc_step_%s_change' % row
            del_proc_button_addr = 'btn_proc_step_%s_del' % row
            edit_proc_button_addr = 'btn_proc_step_%s_edit' % row
            create_proc_button_addr = 'btn_proc_step_%s_create' % row
            div_mod_buttons_addr = 'div_proc_step_%s_mod_buttons' % row
            td_mod_buttons_addr = 'td_proc_step_%s_mod_buttons' % row
            t_proc_addr = 't_proc'
            div_proc_addr = 'div_test_case_procedure'

            # build the onclick scripts
            c_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                       "jQuery(%(remove)s).remove();" \
                       % {'function': 'enable_change_proc_step?row=%s' % row,
                          'values': "['test_case_selection']",
                          'target': '%s' % td_mod_buttons_addr,
                          'remove': '%s' % div_mod_buttons_addr}

            d_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                       "jQuery(%(remove)s).remove();" \
                       % {'function': 'delete_proc_step?row=%s' % row,
                          'values': "['test_case_selection']",
                          'target': '%s' % div_proc_addr,
                          'remove': '%s' % t_proc_addr}

            e_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                       "jQuery(%(remove)s).remove();" \
                       % {'function': 'enable_edit_proc_step?row=%s' % row,
                          'values': "['test_case_selection']",
                          'target': '%s' % td_mod_buttons_addr,
                          'remove': '%s' % div_mod_buttons_addr}

            n_script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                       "jQuery(%(remove)s).remove();" \
                       % {'function': 'enable_create_proc_step?row=%s' % row,
                          'values': "['test_case_selection']",
                          'target': '%s' % td_mod_buttons_addr,
                          'remove': '%s' % div_mod_buttons_addr}

            # build the object
            change_proc_button = INPUT(_type='button', _value="Change", _class='btn',
                                     _id=change_proc_button_addr, _name=change_proc_button_addr,
                                     _onclick=c_script)

            del_proc_button = INPUT(_type='button', _value="Delete", _class='btn',
                                    _id=del_proc_button_addr, _name=del_proc_button_addr,
                                    _onclick=d_script)

            edit_proc_button = INPUT(_type='button', _value="Edit", _class='btn',
                                     _id=edit_proc_button_addr, _name=edit_proc_button_addr,
                                     _onclick=e_script)

            create_proc_button = INPUT(_type='button', _value="+", _class='btn',
                                       _id=create_proc_button_addr, _name=create_proc_button_addr,
                                       _onclick=n_script)

            div_mod_buttons = DIV(change_proc_button, del_proc_button, edit_proc_button, create_proc_button,
                                  _id=div_mod_buttons_addr)
            td_mod_buttons = TD(div_mod_buttons, _id=td_mod_buttons_addr)

            # compile results
            result['div'] = div_mod_buttons
            result['td'] = td_mod_buttons

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_procedure_table(self, steps=None):
        """ Build the test case procedure table.
        @param steps: a list of the procedure steps.
        @return: a dict containing:
            'div' - the DIV() containing the table.
            'table' - the TABLE() containing everything.
        """

        operation = inspect.stack()[0][3]
        result = {'table': TABLE(), 'form': FORM()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # determine the steps for the table
            if steps is None:
                steps = [
                    {'id': 0, 'step': 'No test case selected.'}
                ]

                # add proc step flag
                add_proc_step = False

            else:
                # translate the procedure list string into an actual list
                raw_steps = eval('[%s]' % steps)

                # add proc step flag
                add_proc_step = True

                # build a list of step data dicts using the ids in the procedure list
                steps = []
                for step_id in raw_steps:
                    step_desc = db(db.procedure_steps.id == step_id).select()[0].name
                    steps.append({'id': step_id, 'step': step_desc})

            # build the table rows
            rows = []
            for i in range(0, len(steps)):
                if steps[i]['step'] == 'No test case selected.':
                    row = TR(TD(), TD(LABEL(steps[i]['step'], _id='td_proc_step_%d_val' % i),
                                      _id='td_proc_step_%d' % i),
                             _id='tr_proc_step_%d' % i)
                else:
                    row = TR(TD(), TD(LABEL(steps[i]['step'], _id='td_proc_step_%d_val' % i,
                                            _name='td_proc_step_%d_val' % i, _value=steps[i]['id']),
                                      _id='td_proc_step_%d' % i),
                             self.build_modify_procedure_step_buttons(i)['td'],
                             _id='tr_proc_step_%d' % i)
                rows.append(row)
            if add_proc_step:
                # build add procedure step button row
                add_proc_step_row = self.build_add_procedure_step_button(len(steps))['tr']
                rows.append(add_proc_step_row)

            # build the table
            proc_table_body = TBODY(
                rows,
                _id='tbody_proc'
            ),
            proc_table = TABLE(
                proc_table_body,
                _id='t_proc'
            )
            proc_div = DIV(
                H3("Test Case Procedure"),
                proc_table,
                _id='div_test_case_procedure'
            )

            # compile results
            result['table'] = proc_table
            result['div'] = proc_div

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        return result

    def build_tmanager_form(self):
        """ Build the Test Manager form.
        @return: a dict containing:
            'form' - the FORM() object.
            'table' - the TABLE() object (within the FORM()).
            'div' - the DIV() object containing the tmanager table.
            't_proc' - the procedures table object.
            't_attributes - the test attributes table object.
        """

        operation = inspect.stack()[0][3]
        result = {'form': FORM(), 'table': TABLE()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # build default options for each field
            #   modules and features are dependent on submodule (default to show all available)
            #   all other fields show options dependent on module and feature selected
            modules = db().select(db.modules.ALL)
            features = db().select(db.features.ALL)
            user_stories = []
            tests = []
            test_cases = []

            # build test suite/case dropdown objects
            tr_module_selection = self.build_tmanager_ts_dropdown_object('module', modules)['object']
            tr_feature_selection = self.build_tmanager_ts_dropdown_object('feature', features)['object']
            tr_user_story_selection = self.build_tmanager_ts_dropdown_object('user story', user_stories)['object']
            tr_test_selection = self.build_tmanager_ts_dropdown_object('test', tests)['object']
            tr_test_case_selection = self.build_tmanager_ts_dropdown_object('test case', test_cases)['object']

            # build test attribute objects
            tr_test_results_id = self.build_test_attribute_field('test results id')['tr']
            tr_test_case_class = self.build_test_attribute_field('test case class')['tr']
            tr_test_case_minver = self.build_test_attribute_field('test case minimum version')['tr']
            tr_test_case_active = self.build_test_attribute_field('test case active')['tr']
            t_attributes = TABLE(tr_test_results_id, tr_test_case_class, tr_test_case_minver, tr_test_case_active,
                                 _id='t_attributes')

            # build test case procedure objects
            t_proc = self.build_procedure_table()['div']

            # build tmanager form
            tmanager_table = TABLE(
                TBODY(
                    tr_module_selection, tr_feature_selection, tr_user_story_selection, tr_test_selection,
                    tr_test_case_selection
                ),
                _id='tmanager_form_table')

            div_tmanager = DIV(tmanager_table, t_attributes, HR(), t_proc, _id='div_tmanager')
            tmanager_form = FORM(div_tmanager, _id='tmanager_form')

            # compile results
            result['table'] = tmanager_table
            result['form'] = tmanager_form
            result['div'] = div_tmanager
            result['t_proc'] = t_proc
            result['t_attributes'] = t_attributes

            # return
            return result

        except BaseException, e:
            self.handle_exception(self.log, e, operation)
            return False

    def enable_ts_add(self):
        """ Enable the add new entry field for a Test Manager selection drop-down (test suite).
        @return: DIV() containing the add new entry field and confirmation/cancel buttons
        """

        operation = inspect.stack()[0][3]
        result = DIV()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # build enable add new entry field
            div_cnf_add_new_ts_entry = self.build_td_confirm_add_ts_entry(request.vars.selectaddr,
                                                                          request.vars.container,
                                                                          request.vars.type)['div']

            # compile results
            result = div_cnf_add_new_ts_entry

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def edit_test_attribute_field(self, field, value, parent_suite_id):
        """ Add a new entry to the given test suite selection drop down (using input).
        @param field: the field to edit (e.g., 'test results id', 'test case class', 'test case minimum version').
        @param value: the value with which to update the field.
        @param parent_suite_id: the id of the parent suite (test or test case).
        @return: a DIV() containing the rebuilt tmanager form data.
        """

        operation = inspect.stack()[0][3]
        result = DIV()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # update the test attribute for the test/case in database by field
            if field == 'test results id':
                db(db.tests.id == parent_suite_id).update(results_id=value)
            elif field == 'test case class':
                db(db.test_cases.id == parent_suite_id).update(test_class=value)
            elif field == 'test case minimum version':
                db(db.test_cases.id == parent_suite_id).update(min_version=value)
            elif field == 'test case active':
                db(db.test_cases.id == parent_suite_id).update(active=value)
            else:
                log.error("Invalid field %s specifed." % field)

            # compile results
            result = self.build_test_attribute_field(field)['div']

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def add_ts_entry(self):
        """ Add a new entry to the given test suite selection drop down (using input).
        @return: a DIV() containing the rebuilt tmanager form data.
        """

        operation = inspect.stack()[0][3]
        result = TABLE()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # update the test suite in database by type
            if request.vars.type == 'module':
                db.modules.insert(
                    name=request.vars.inp_new_module_name,
                    submodule_id=2  # hard-coded to ViM (hestia)
                )
            elif request.vars.type == 'feature':
                db.features.insert(
                    name=request.vars.inp_new_feature_name,
                    submodule_id=2  # hard-coded to ViM (hestia)
                )
            elif request.vars.type == 'user_story':
                db.user_stories.insert(
                    action=request.vars.inp_new_user_story_action,
                    user_type=request.vars.inp_new_user_story_user_type,
                    feature_id=request.vars.feature_selection,
                    module_id=request.vars.module_selection
                )
            elif request.vars.type == 'test':
                db.tests.insert(
                    name=request.vars.inp_new_test_name,
                    user_story_id=request.vars.user_story_selection,
                    results_id=request.vars.inp_new_test_results_id
                )
            elif request.vars.type == 'test_case':
                db.test_cases.insert(
                    name=request.vars.inp_new_test_case_name,
                    test_id=request.vars.test_selection,
                    procedure='4',
                    min_version='1',
                    test_class=5,
                    active=1,
                )
            else:
                log.error("Invalid test suite type %s specifed." % request.vars.type)

            # rebuild TS select object
            select = self.build_tmanager_ts_dropdown_object(request.vars.type.replace('_', ' '))['select']

            # compile results
            result = select

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def cancel_add_ts_entry(self):
        """ Cancel adding a new test suite selection entry.
        @return: a DIV() containing the original add new ts entry button.
        """

        operation = inspect.stack()[0][3]
        result = DIV()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # rebuild add new ts entry button
            div_add_ts_entry = self.build_td_add_ts_entry(request.vars.selectaddr)['div']

            # compile results
            result = div_add_ts_entry

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def enable_tmanager_selection_update(self):
        """ Enable the edit field for a Test Manager selection drop-down (test suite).
        @return: edit field and update button.
        """

        operation = inspect.stack()[0][3]
        result = DIV()

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # define this objects address (name, id)
            div_update_addr = 'td_%s_update_div' % request.vars.selectaddr

            # determine selected value
            raw_val = eval('request.vars.%s' % request.vars.src)

            if int(raw_val) > 0:
                # determine value from database
                tables = self.tables
                entry = db(tables[request.vars.type].id == raw_val).select(tables[request.vars.type].ALL)[0]
                if request.vars.type != 'user story':
                    val = entry.name
                else:
                    val = entry.action
            else:
                # value is blank
                val = ''


            # define update field
            update_user_type_field_label = LABEL("A/The ")
            update_user_type_field_addr = "%s_field_user_type" % div_update_addr
            options = db().select(db.user_types.ALL)
            update_user_type_field = SELECT(_id=update_user_type_field_addr, _name=update_user_type_field_addr,
                                   *[OPTION(options[i].name, _value=str(options[i].id))
                                     for i in range(len(options))])
            update_action_field_label = LABEL(" will ")
            update_field_addr = "%s_field" % div_update_addr
            update_field = INPUT(_id="%s" % update_field_addr, _name="%s" % update_field_addr,
                                 _class="string", _type="text", _value=val)

            # define update button
            update_bttn_addr = "%s_bttn" % div_update_addr
            update_bttn_script = "ajax('update_tmanager_selection?" \
                                 "field=%s" \
                                 "&selectaddr=%s" \
                                 "&type=%s" \
                                 "&id=%s', " \
                                 "['%s', '%s'], 'td_%s'); " \
                                 "jQuery(%s).remove();" \
                                 % (update_field_addr, request.vars.selectaddr, request.vars.type,
                                    raw_val, update_field_addr, update_user_type_field_addr,
                                    request.vars.selectaddr, request.vars.selectaddr)
            update_bttn_script += "ajax('%(function)s?type=%(type)s', %(vars)s, '%(target)s');" \
                                  "jQuery(%(remove obj)s).remove();" \
                                  % {'function':    'restore_ts_update_cell',
                                     'type':        request.vars.type,
                                     'vars':        '[]',
                                     'target':      'td_%s_update' % request.vars.selectaddr,
                                     'remove obj':  div_update_addr}
            update_bttn = INPUT(_id="%s" % update_bttn_addr, _name="%s" % update_bttn_addr,
                                _type="button", _value="Update", _onclick=update_bttn_script,
                                _class="btn")

            # compile return data
            if request.vars.type == 'user story':
                div_update = FORM(update_user_type_field_label, update_user_type_field,
                                 update_action_field_label, update_field, update_bttn,
                                 _name=div_update_addr, _id=div_update_addr)
            else:
                div_update = FORM(update_field, update_bttn, _name=div_update_addr, _id=div_update_addr)

            # compile results
            result = div_update

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_test_runner_div(self):
        """ Build the test runner div.
        @return: a dict containing:
            'btn' - the test run button.
            'div' - the div containing the button and additional fields.
        """

        operation = inspect.stack()[0][3]
        result = {'div': DIV(), 'btn': INPUT(_class='btn')}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # define object ids
            btn_run_test_addr = 'btn_run_test'
            inp_plan_id_addr = 'inp_plan_id'
            div_test_runner_addr = 'div_test_runner'

            # build the onclick scripts
            script = "ajax('%(function)s', %(values)s, '%(target)s');" \
                     "jQuery(%(remove)s).remove();" \
                     % {'function': 'run_test',
                        'values': "['%s', 'module_selection', 'feature_selection', "
                                  "'user_story_selection', 'test_selection', "
                                  "'test_case_selection']" % inp_plan_id_addr,
                        'target': '',
                        'remove': ''}

            # build the objects
            btn_run_test = INPUT(_type='button', _value="Run Test", _class='btn',
                                 _id=btn_run_test_addr, _name=btn_run_test_addr,
                                 _onclick=script)
            lbl_plan_id = LABEL("TEST PLAN ID: ")
            inp_plan_id = INPUT(_type='string',
                                _id=inp_plan_id_addr, _name=inp_plan_id_addr)

            div_test_runner = DIV(lbl_plan_id, inp_plan_id, btn_run_test,
                                  _id=div_test_runner_addr)

            # compile results
            result['div'] = div_test_runner
            result['btn'] = btn_run_test

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result


####################################################################################################
# Step Manager #####################################################################################
####################################################################################################
####################################################################################################


class StepManager():
    """ A library of functions to be used by the Step Manager app.
    """

    def __init__(self, log, exception_handler):
        """
        @param log: an initialized Logger() to inherit.
        @param exception_handler: an un-initialized ExceptionHandler() to inherit.
        """

        # inherit logger (initialized instance)
        self.log = log

        # inherit exception handler
        self.handle_exception = exception_handler

    def TEMPLATE(self):
        """
        """

        operation = inspect.stack()[0][3]
        result = None

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            # compile results
            result = None

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result

    def build_smanager_form(self):
        """ Build the Steps Manager form.
        @return: a dict containing:
            'form' - the FORM() object.
        """

        operation = inspect.stack()[0][3]
        result = {'form': FORM()}

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))

            #

            # compile results
            result['form'] = FORM()

        except BaseException, e:
            self.handle_exception(self.log, e, operation)

        # return
        self.log.trace("... DONE %s." % operation.replace('_', ' '))
        return result


####################################################################################################
# Classes ##########################################################################################
####################################################################################################
####################################################################################################

tmanager = TestManager(log, ExceptionHandler)
#smanager = StepManager(log, ExceptionHandler)

####################################################################################################
# Default Controller ###############################################################################
####################################################################################################
####################################################################################################


def index():
    """ Initialize Test Manager (as index.html) page. This is the initial page loaded.
    @return: dict tmanager_form containing the initial Test Manager form.
    """

    # build tmanager form
    tmanager_form = build_tmanager_form()['form']

    # build smanager form
    #smanager_form = smanager.build_smanager_form()['form']

    # handle add crafting material form submission
    if tmanager_form.process(keepvalues=True).accepted:
        # insert record into database
        try:
            pass

            #response.flash = ''

        except BaseException:
            response.flash = 'Failed to submit.'

    elif tmanager_form.errors:
        response.flash = 'Failed to submit due to errors.'

    else:
        pass

    return dict(tmanager_form=tmanager_form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


def build_tmanager_form():
    return tmanager.build_tmanager_form()


def build_tmanager_ts_dropdown_object():
    return tmanager.build_tmanager_ts_dropdown_object()['select']


def update_tmanager_form():
    return tmanager.update_tmanager_form()


def update_tmanager_selection():
    return tmanager.update_tmanager_selection()


def update_test_results_id_field():
    return tmanager.update_test_attribute_field('test results id')


def update_test_case_class_field():
    return tmanager.update_test_attribute_field('test case class')


def update_test_case_minver_field():
    return tmanager.update_test_attribute_field('test case minimum version')


def update_test_case_active_field():
    return tmanager.update_test_attribute_field('test case active')


def update_test_case_procedure_table():
    return tmanager.update_test_case_procedure_table()


def enable_tmanager_selection_update():
    return tmanager.enable_tmanager_selection_update()


def enable_ts_add():
    return tmanager.enable_ts_add()


def cancel_add_ts_entry():
    return tmanager.cancel_add_ts_entry()


def add_ts_entry():
    return tmanager.add_ts_entry()


def restore_ts_update_cell():
    return tmanager.build_tmanager_ts_dropdown_object(request.vars.type)['update cell']


def restore_ts_add_new_cell():
    return tmanager.build_td_add_ts_entry(request.vars.selectaddr)['div']


def restore_test_results_id_field():
    return tmanager.build_test_attribute_field('test results id')['div']


def restore_test_case_class_field():
    return tmanager.build_test_attribute_field('test case class')['div']


def restore_test_case_minimum_version_field():
    return tmanager.build_test_attribute_field('test case minimum version')['div']


def restore_test_case_active_field():
    return tmanager.build_test_attribute_field('test case active')['div']


def edit_test_results_id_field():
    return tmanager.edit_test_attribute_field('test results id',
                                              request.vars.test_results_id_edit_val,
                                              request.vars.test_selection)['div']


def edit_test_case_class_field():
    return tmanager.edit_test_attribute_field('test case class',
                                              request.vars.test_case_class_edit_val,
                                              request.vars.test_case_selection)['div']


def edit_test_case_minimum_version_field():
    return tmanager.edit_test_attribute_field('test case minimum version',
                                              request.vars.test_case_minimum_version_edit_val,
                                              request.vars.test_case_selection)['div']


def edit_test_case_active_field():
    return tmanager.edit_test_attribute_field('test case active',
                                              request.vars.test_case_active_edit_val,
                                              request.vars.test_case_selection)['div']


def enable_test_results_id_edit():
    return tmanager.build_edit_test_attribute_field('test results id',
                                                    c_value=request.vars.test_results_id_val)['form']


def enable_test_case_class_edit():
    return tmanager.build_edit_test_attribute_field('test case class',
                                                    c_value=request.vars.test_case_class_val)['form']


def enable_test_case_minimum_version_edit():
    return tmanager.build_edit_test_attribute_field('test case minimum version',
                                                    c_value=request.vars.test_case_minimum_version_val)['form']


def enable_test_case_active_edit():
    return tmanager.build_edit_test_attribute_field('test case active',
                                                    c_value=request.vars.test_case_active_val)['form']


def enable_add_proc_step():
    return tmanager.build_add_procedure_step_form(request.vars.row)['form']


def add_procedure_step_to_test_case():
    tmanager.add_procedure_step_to_test_case(request.vars.sel_add_proc_step, request.vars.test_case_selection)
    steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure
    return tmanager.build_procedure_table(steps)['table']


def rebuild_test_case_procedure_table():
    steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure
    return tmanager.build_procedure_table(steps)['table']


def enable_change_proc_step():
    return tmanager.build_change_procedure_step_form(request.vars.row)['form']


def change_procedure_step_for_test_case():
    tmanager.modify_procedure_step_for_test_case(request.vars.row, request.vars.test_case_selection,
                                                 'change', request.vars.sel_edit_proc_step)
    steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure
    return tmanager.build_procedure_table(steps)['table']


def delete_proc_step():
    tmanager.modify_procedure_step_for_test_case(request.vars.row, request.vars.test_case_selection,
                                                 'delete')
    steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure
    return tmanager.build_procedure_table(steps)['table']


def enable_edit_proc_step():
    return tmanager.build_edit_procedure_step_form(request.vars.row,
                                                   request.vars.test_case_selection)['form']


def edit_procedure_step_for_test_case():
    name = eval("request.vars.inp_edit_proc_step_%s_desc" % request.vars.row)
    funct = eval("request.vars.sel_edit_proc_step_%s_funct" % request.vars.row)
    args = eval("request.vars.inp_edit_proc_step_%s_args" % request.vars.row)
    vrf = eval("request.vars.sel_edit_proc_step_%s_vrf" % request.vars.row)
    tmanager.modify_procedure_step_for_test_case(request.vars.row, request.vars.test_case_selection,
                                                 'edit', name=name, funct=funct, args=args, vrf=vrf)
    steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure
    return tmanager.build_procedure_table(steps)['table']


def enable_create_proc_step():
    return tmanager.build_edit_procedure_step_form(request.vars.row, request.vars.test_case_selection,
                                                   create=True)['form']


def create_new_step():
    name = eval("request.vars.inp_edit_proc_step_%s_desc" % request.vars.row)
    funct = eval("request.vars.sel_edit_proc_step_%s_funct" % request.vars.row)
    args = eval("request.vars.inp_edit_proc_step_%s_args" % request.vars.row)
    vrf = eval("request.vars.sel_edit_proc_step_%s_vrf" % request.vars.row)
    tmanager.add_new_procedure_step(name, funct, args, vrf)
    steps = db(db.test_cases.id == request.vars.test_case_selection).select()[0].procedure
    return tmanager.build_procedure_table(steps)['table']


def run_test():
    # instance database
    from mapping import TARTAROS_WEB_DB_PATH
    database = Database(log, path=TARTAROS_WEB_DB_PATH)

    # determine test plan id
    plan_id = request.vars.inp_plan_id

    # determine test suite values
    module_id = request.vars.module_selection
    feature_id = request.vars.feature_selection
    user_story_id = request.vars.user_story_selection
    test_id = request.vars.test_selection
    test_case_id = request.vars.test_case_selection

    if plan_id is None and test_case_id != '0':
        # create test case object
        testcase = HestiaTestCase(log, database, test_case_id, debugging=False)

        # run test case
        testcase.run()

    else:
        # initialize test run object
        testrun = TestRun(log, database, name="Cerberus Run", submodule_id=2,
                          results_plan_id=plan_id)

        # build testcase list for test run
        testcases = testrun.build_testcase_list_for_run(module_id=module_id,
            feature_id=feature_id, story_id=user_story_id, test_id=test_id,
            case_id=test_case_id)['testcases']

        # set testcase list for test run
        testrun.testcases = testcases

        # execute test run
        testrun.run()

    # disconnect from database
    #database.disconnect_from_database()