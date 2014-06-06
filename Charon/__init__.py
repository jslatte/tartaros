###################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from apsw import Connection
from time import sleep

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################



####################################################################################################
# Charon (SQLite) ##################################################################################
####################################################################################################
####################################################################################################


class Charon():
    """ API Library for interacting with a SQLite database. """

    def __init__(self, db_path, logger):
        """
        INPUT
            db_path: The file path to the database.
            logger: An initialized instance of a logging class to use.
        """

        # define default attributes
        self.db_path = db_path
        self.connection = None
        self.handles = []

        # instantiate logger
        self.log = logger

        self.module_name = self.__class__.__name__
        self.log.info("Initializing %s module ..." % self.module_name)

    def connect_to_database(self):
        """ Connect to the database.
        """

        self.log.debug("Connecting to database %s ..." % self.db_path)
        result = {'successful': False}

        # define connection
        if self.connection is None:
            try:
                self.connection = Connection(self.db_path)
                result['successful'] = True
            except BaseException, e:
                self.log.error("Failed to connect to database.")
                self.log.error(str(e))
        else:
            self.log.trace("Connection to database already established.")

        # return
        return result

    def create_database_handle(self):
        """ Create a new database handle.
        """

        self.log.debug("Creating new database handle ...")
        result = {'successful': False, 'handle': None}

        # define handle (database cursor)
        if self.connection is not None:
            try:
                handle = self.connection.cursor()
                result['successful'] = True

                # add handle to list of active handles
                self.handles.append(handle)
            except BaseException, e:
                self.log.error("Failed to create handle.")
                self.log.error(str(e))
                handle = None
        else:
            self.log.warn("Failed to create handle. No connection to database established.")
            handle = None

        # turn on pragma foreign_keys (keeps entries without required data from being entered)
        if handle is not None:
            handle.execute("pragma foreign_keys=on")

        # return
        result['handle'] = handle
        return result

    def close_handle(self, handle):
        """ Close handle to the database.
        INPUT
            handle: an active handle to the database.
        """

        self.log.debug("Closing handle %s ..." % handle)
        result = {'deleted': False}

        # remove handle
        try:
            # remove handle from list of active handles
            self.handles.remove(handle)

            # delete handle
            handle = None
            result['successful'] = True

        except BaseException, e:
            self.log.error("Failed to close handle.")
            self.log.error(str(e))

        # return
        return result

    def disconnect_from_database(self):
        """ Disconnect from the database.
        """

        self.log.debug("Disconnecting from database %s ..." % self.db_path)
        result = {'successful': False}

        # disconnect from database
        if self.connection is not None:
            # close all active handles
            try:
                for handle in self.handles:
                    del handle
                    #self.handles.remove(handle)

            except BaseException, e:
                self.log.error("Failed to close all active handles to database.")
                self.log.error(str(e))

            # close connection
            try:
                self.connection.close()
                self.connection = None

            except BaseException, e:
                self.log.error("Failed to disconnect from database.")
                self.log.error(str(e))
        else:
            self.log.trace("No connection established.")

        # return
        return result

    def execute_SQL(self, handle, statement, return_id=False, return_ex='', max_attempts=5):
        """ Execute the given SQL statement.
        @param handle: an active handle to the database.
        @param statement: a line of SQL code to execute.
        @return: a dict containing:
            response: the response from the database.
            id: if return_id is True, the id of the entry inserted.
        """

        self.log.trace("Executing SQL %s ..." % statement)
        result = {'response': None, 'id': None}

        response = None
        while response is None:
            try:
                # execute SQL
                statement = statement.replace('"NULL"', 'NULL').replace("'NULL'", 'NULL')
                statement += ';'
                response = handle.execute(statement) # system-wide crash caused when using 3.8.1.2
                # return row id
                if return_id:
                    statement = "SELECT last_insert_rowid() " + return_ex + ";"
                    self.log.trace("Executing:\t%s" % statement)
                    result['id'] = handle.execute(statement).next()[0]
                    self.log.trace("Returned ID:\t%s" % result['id'])
            except BaseException, e:
                self.log.error("Failed to execute SQL.")
                self.log.error(str(e))
                if str(e) == 'BusyError: database is locked':
                    sleep(1)
                    continue
                else:
                    response = None
                    sleep(1)
                    break

        # return
        result['response'] = response
        return result

    def query_database_table(self, handle, table, return_field=None, addendum='', max=False):
        """ Query a database table. """

        self.log.debug("Querying database table %s ..." % table)
        result = {'response': [[None]]}

        # Translate 'NULL' value so that SQL can recognize the db item
        addendum = addendum.replace('NULL', '')

        # Construct SQL statement to pass to database
        if max:
            query = "SELECT MAX(%(returnValueType)s) FROM %(table)s"\
                    % {'returnValueType': return_field, 'table': table}
        elif return_field is None:
            query = "SELECT * FROM %(table)s"\
                    % {'returnValueType': return_field, 'table': table}
        else:
            query = "SELECT %(returnValueType)s FROM %(table)s"\
                    % {'returnValueType': return_field, 'table': table}
        query += " " + addendum

        # execute query and fetch all results
        try:
            response = self.execute_SQL(handle, query)['response'].fetchall()
            if response is []: response = [[None]]
            # convert response to list
            response = list(response)
        except BaseException, e:
            self.log.error("Failed to query database table.")
            self.log.error(str(e))
            response = [[None]]

        # return query response
        #self.log.trace("Query response: %s" % response)
        result['response'] = response
        return result

    def query_database_table_for_single_value(self, handle, table, return_field, known_field,
                                              known_value, addendum='', max=False):
        """ Query a database table for a single value, given a known field and its value.
        """

        self.log.debug("Querying %s for %s given that %s = %s ..." % (table,return_field,known_field,
                                                                 known_value))
        result = {'value':None}

        # query database table
        response = self.query_database_table(handle, table, return_field,
            'WHERE %s = "%s"' % (known_field, known_value) + addendum, max)['response']

        # get value from response
        try:
            result['value'] = response[0][0]
        except BaseException, e:
            self.log.trace("No value returned.")
            result['value'] = None
        # return
        return result

    def update_entry_in_table(self, handle, table, id, entry, id_field='ID'):
        """ Updated entry in given table in database.
        INPUT
            handle: an active handle to the database.
            table: the table to update (see maps).
            id: the id of the entry.
            entry: a data dictionary pairing table fields with the entry value.
        """

        self.log.debug("Updating entry %s with %s in %s table ..." % (id, entry, table))
        result = {}

        # create fields to update list
        fields = list(entry.keys())
        # create values to update list
        values = list(entry.values())

        # create SQL statement to execute
        template = "UPDATE %s SET %s = '%s' WHERE %s = %s"
        for n in range(0, len(fields)):
            # build statement
            sql = template % (str(table), str(fields[n]), str(values[n]), id_field, str(id))
            # execute SQL statement
            self.execute_SQL(handle, sql)

        # return
        return result

    def add_entry_to_table(self, handle, table, entry):
        """ Add entry to given table in database.
        INPUT
            handle: an active handle to the database.
            table: the table to update (see maps).
            entry: a data dictionary pairing table fields with the entry value.
        OUTPUT
            id: the ID of the entry added to the database table
        """

        self.log.debug("Adding entry %s to %s table ..." % (entry, table))
        result = {'id': None}

        # build insert fields statement by adding each key, comma-delimited
        fields = list(entry.keys())
        insert_fields = None
        # add first field (if any)
        if len(fields) > 0:
            insert_fields = '"%s"' % fields[0]
        else:
            self.log.error("No fields specified. Cannot add entry.")
            # add additional fields (if any)
        if insert_fields is not None\
        and len(fields) > 1:
            for field in fields[1:]:
                insert_fields += ',"%s"' % field
            # update final sub-statement to proper format
        if insert_fields is not None:
            insert_fields = '(%s)' % insert_fields

        # build insert field values sub-statement by adding each value, comma-delimited
        values = list(entry.values())
        insert_values = None
        # add first value (if any)
        if len(values) > 0:
            insert_values = '"%s"'%values[0]
            if values[0] is None:
                value = 'NULL'
            elif 'strftime' in str(values[0]).lower():
                value = values[0]
            else:
                value = '"%s"' % values[0]
            insert_values = "%s" % value
        else:
            self.log.error("No fields specified. Cannot insert entry.")
            # add additional values (if any)
        if insert_values is not None\
        and len(values) > 1:
            for value in values[1:]:
                # translate misc value types
                if value is None:
                    value = 'NULL'
                elif 'strftime' in str(value).lower():
                    value = value
                else:
                    value = '"%s"' % value
                insert_values += ",%s" % value
            # update final sub-statement to proper format
        if insert_values is not None:
            insert_values = 'VALUES (%s)' % insert_values

        # collate SQL statement and execute
        statement = 'INSERT INTO %s %s %s' % (table, insert_fields, insert_values)
        entryID = self.execute_SQL(handle, statement, return_id=True)['id']

        # return
        result['id'] = entryID
        return result

    def update_table_field_for_entry(self, handle, table, field, value, knownField, knownValue,
                                     math=False):
        """ Update the value for an entry in the database.
        'field' is the field to update for the entry.
        'value' is the value to update the field with for the entry.
        'known field' and 'known value' indicate which entry to update.
        'math' is whether or not the updated value includes a mathematical operations,
            which requires no ' quotations around the value to be processed. """

        self.log.debug("Updating %s table ..." % table)
        result = {}

        # define statement
        if math:
            statement = '''UPDATE %(table)s SET %(field)s = %(value)s '''\
                        % {'table': table, 'field': field, 'value': value}
        else:
            statement = '''UPDATE %(table)s SET %(field)s = '%(value)s' '''\
                        % {'table': table, 'field': field, 'value': value}
        statement += '''WHERE %(known field)s = '%(known value)s' '''\
                     % {'known field': knownField, 'known value': knownValue}

        # update database table
        self.execute_SQL(handle, statement)

        # return
        return result

    def empty_database_table(self, handle, table):
        """ Delete all entries from a database table. """

        self.log.debug("Emptying %s table ..." % table)
        result = {}

        # empty database table
        statement = "DELETE FROM %s" % table
        self.execute_SQL(handle, statement)
        # return
        return result

    def remove_entries_from_table_for_known_field(self, handle, table, knownField, value):
        """ Delete all entries from a database table associated with given known field. """

        self.log.debug("Removing all entries from %s where %s is %s ..." % (table, knownField, value))
        result = {}

        # delete entries from table
        statement = "DELETE FROM %s WHERE %s = %s"%(table, knownField.lower(), value)
        self.execute_SQL(handle, statement)
        # return
        return result

    def return_number_of_rows(self, handle, table, addendum=''):
        """ Return the number of rows from a database table. """

        self.log.debug("Returning number of rows from %s table ..." % table)
        result = {'number of rows': None}

        # execute SQL statment
        statement = 'SELECT COUNT(*) FROM %s' % table
        statement += addendum
        result['number of rows'] = self.execute_SQL(handle, statement).next()[0]

        # return
        return result

    def analyze_database(self, handle):
        """ Run SQLite Analyze command on database to optimize query speeds.
        """

        self.log.debug("Analyzing database ...")
        result = {'successful': False}

        try:
            self.execute_SQL(handle, 'Analyze')
            result['successful'] = True
        except BaseException, e:
            self.log.error(str(e))
            self.log.error("Failed to analyze database.")

        # return
        return result