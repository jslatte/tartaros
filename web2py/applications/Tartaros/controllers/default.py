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

                # determine test options for selection ('0' given if the field should be cleared
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
                selection = self.build_tmanager_dropdown_object(obj_type, options)['select']

                # compile return data
                result = selection

            # return
            self.log.trace("... DONE %s." % operation.replace('_', ' '))
            return result

        except BaseException, e:
            self.handle_exception(self.log, e, operation)
            return False

    def build_tmanager_dropdown_object(self, select_type, options):
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

            # test case drop-down objects
            elif obj_type == object_types['test case']:
                # input data
                #input_data = "['%s']" % obj_type

                # event target
                #on_change_event_target = object_types['test case']

                # build the options list for the selection object
                selections = [OPTION(options[i].name, _value=str(options[i].id))
                              for i in range(len(options))]

                # build jQuery statement
                self.log.trace("... building jQuery statement ...")
                jquery_s = ''#jquery_s_template % object_types['test case']

                # build ajax statement
                self.log.trace("... building AJAX statement ...")
                ajax_s = ''#ajax_s_template % ("['%s']" % obj_type, object_types['test case'])

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
                                   "['%s'], " \
                                   "'%s'); " \
                                   % (select_addr, td_update_addr, select_addr, select_type,
                                      select_addr, td_update_addr)
            div_update = DIV(INPUT(_type='button', _value='Update',
                                   _id=update_button_addr,
                                   _name=update_button_addr,
                                   _onclick=update_button_script,
                                   _class="btn"),
                             _name=div_update_addr,
                             _id=div_update_addr)

            td_update = TD(div_update, _name=td_update_addr, _id=td_update_addr)

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
            tr_selection = TR(td_selection_label, td_selection, td_update, _id='tr_%s_selection' % name)

            # compile return data
            result['object'] = tr_selection
            result['select'] = selection

            # return
            self.log.trace("... DONE %s." % operation.replace('_', ' '))
            return result

        except BaseException, e:
            self.handle_exception(self.log, e, operation)
            return False

    def enable_tmanager_selection_update(self):
        """ Enable the edit field for a Test Manager selection drop-down (test suite).
        @return: edit field and update button.
        """

        operation = inspect.stack()[0][3]

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            result = DIV()

            # define this objects address (name, id)
            div_update_addr = 'td_%s_update_div' % request.vars.selectaddr

            # determine selected value
            raw_val = eval('request.vars.%s' % request.vars.src)

            if int(raw_val) > 0:
                # determine value from database
                tables = {'module':     db.modules,
                          'feature':    db.features,
                          'user story': db.user_stories,
                          'test':       db.tests,
                          'test case':  db.test_cases}
                entry = db(tables[request.vars.type].id == raw_val).select(tables[request.vars.type].ALL)[0]
                if request.vars.type != 'user story':
                    val = entry.name
                else:
                    val = entry.action
            else:
                # value is blank
                val = ''


            # define update field
            update_field_addr = "%s_field" % div_update_addr
            update_field = INPUT(_id="%s" % update_field_addr, _name="%s" % update_field_addr,
                                 _class="string", _type="text", _value=val)

            # define update button
            update_bttn_addr = "%s_bttn" % div_update_addr
            update_bttn_script = "jQuery(%s).remove(); " \
                                 "jQuery(this).remove(); " \
                                 "ajax('update_tmanager_selection?" \
                                 "field=%s" \
                                 "&selectaddr=%s" \
                                 "&type=%s', " \
                                 "['%s'], '%s');" \
                                 % (update_field_addr, update_field_addr, request.vars.selectaddr, request.vars.type,
                                    update_field_addr, request.vars.target)
            update_bttn = INPUT(_id="%s" % update_bttn_addr, _name="%s" % update_bttn_addr,
                                _type="button", _value="Update", _onclick=update_bttn_script,
                                _class="btn")

            # compile return data
            result = DIV(update_field, update_bttn, _name=div_update_addr, _id=div_update_addr)

            # return
            self.log.trace("... DONE %s." % operation.replace('_', ' '))
            return result

        except BaseException, e:
            self.handle_exception(self.log, e, operation)
            return False

    def update_tmanager_selection(self):
        """ Update the Test Manager selection drop down (and refresh update cell).
        @return:
        """

        operation = inspect.stack()[0][3]

        try:
            self.log.trace("%s ..." % operation.replace('_', ' '))
            result = DIV()

            # SELECT() object id
            select_addr = request.vars.selectaddr

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
                                   "['%s'], '%s'); " \
                                   % (select_addr, td_update_addr, select_addr, request.vars.type,
                                      select_addr, td_update_addr)
            div_update = DIV(INPUT(_type='button', _value='Update',
                                   _id=update_button_addr,
                                   _name=update_button_addr,
                                   _onclick=update_button_script,
                                   _class="btn"),
                             _name=div_update_addr,
                             _id=div_update_addr)

            td_update = TD(div_update, _name=td_update_addr, _id=td_update_addr)

            # compile return data
            result = div_update

            # return
            self.log.trace("... DONE %s." % operation.replace('_', ' '))
            return result

        except BaseException, e:
            self.handle_exception(self.log, e, operation)
            return False


####################################################################################################
# Classes ##########################################################################################
####################################################################################################
####################################################################################################

tmanager = TestManager(log, ExceptionHandler)

####################################################################################################
# Default Controller ###############################################################################
####################################################################################################
####################################################################################################


def index():
    """ Initialize Test Manager (as index.html) page. This is the initial page loaded.
    @return: dict tmanager_form containing the initial Test Manager form.
    """

    # build default options for each field
    #   modules and features are dependent on submodule (default to show all available)
    #   all other fields show options dependent on module and feature selected
    modules = db().select(db.modules.ALL)
    features = db().select(db.features.ALL)
    user_stories = []
    tests = []
    test_cases = []

    # build drop-down object(s)
    tr_module_selection = tmanager.build_tmanager_dropdown_object('module', modules)['object']
    tr_feature_selection = tmanager.build_tmanager_dropdown_object('feature', features)['object']
    tr_user_story_selection = tmanager.build_tmanager_dropdown_object('user story', user_stories)['object']
    tr_test_selection = tmanager.build_tmanager_dropdown_object('test', tests)['object']
    tr_test_case_selection = tmanager.build_tmanager_dropdown_object('test case', test_cases)['object']

    # build tmanager form
    tmanager_form = FORM((TABLE(TBODY(tr_module_selection, tr_feature_selection,
                                      tr_user_story_selection, tr_test_selection,
                                      tr_test_case_selection))))

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


def update_tmanager_form():
    return tmanager.update_tmanager_form()


def enable_tmanager_selection_update():
    return tmanager.enable_tmanager_selection_update()


def update_tmanager_selection():
    return tmanager.update_tmanager_selection()