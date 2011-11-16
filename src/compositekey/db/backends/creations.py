from django.db.backends.creation import BaseDatabaseCreation

__author__ = 'fabio'


def sql_create_model(self, model, style, known_models=set()):
    """
    Returns the SQL required to create a single model, as a tuple of:
        (list_of_sql, pending_references_dict)
    """
    opts = model._meta
    if not opts.managed or opts.proxy:
        return [], {}
    final_output = []
    table_output = []
    pending_references = {}
    qn = self.connection.ops.quote_name
    for f in [f for f in opts.local_fields if not getattr(f, "not_in_db", False)]:
        col_type = f.db_type(connection=self.connection)
        tablespace = f.db_tablespace or opts.db_tablespace
        if col_type is None:
            # Skip ManyToManyFields, because they're not represented as
            # database columns in this table.
            continue
        # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
        field_output = [style.SQL_FIELD(qn(f.column)),
            style.SQL_COLTYPE(col_type)]
        if not f.null:
            field_output.append(style.SQL_KEYWORD('NOT NULL'))
        if f.primary_key:
            field_output.append(style.SQL_KEYWORD('PRIMARY KEY'))
        elif f.unique:
            field_output.append(style.SQL_KEYWORD('UNIQUE'))
        if tablespace and f.unique:
            # We must specify the index tablespace inline, because we
            # won't be generating a CREATE INDEX statement for this field.
            tablespace_sql = self.connection.ops.tablespace_sql(tablespace, inline=True)
            if tablespace_sql:
                field_output.append(tablespace_sql)
        if f.rel:
            ref_output, pending = self.sql_for_inline_foreign_key_references(f, known_models, style)
            if pending:
                pending_references.setdefault(f.rel.to, []).append((model, f))
            else:
                field_output.extend(ref_output)
        table_output.append(' '.join(field_output))
    for field_constraints in opts.unique_together:
        table_output.append(style.SQL_KEYWORD('UNIQUE') + ' (%s)' % \
            ", ".join([style.SQL_FIELD(qn(opts.get_field(f).column)) for f in field_constraints]))

    full_statement = [style.SQL_KEYWORD('CREATE TABLE') + ' ' + style.SQL_TABLE(qn(opts.db_table)) + ' (']
    for i, line in enumerate(table_output): # Combine and add commas.
        full_statement.append('    %s%s' % (line, i < len(table_output)-1 and ',' or ''))
    full_statement.append(')')
    if opts.db_tablespace:
        tablespace_sql = self.connection.ops.tablespace_sql(opts.db_tablespace)
        if tablespace_sql:
            full_statement.append(tablespace_sql)
    full_statement.append(';')
    final_output.append('\n'.join(full_statement))

    if opts.has_auto_field:
        # Add any extra SQL needed to support auto-incrementing primary keys.
        auto_column = opts.auto_field.db_column or opts.auto_field.name
        autoinc_sql = self.connection.ops.autoinc_sql(opts.db_table, auto_column)
        if autoinc_sql:
            for stmt in autoinc_sql:
                final_output.append(stmt)

    return final_output, pending_references
sql_create_model._sign = "monkey patch by compositekey"

def sql_indexes_for_model(self, model, style):
        "Returns the CREATE INDEX SQL statements for a single model"
        if not model._meta.managed or model._meta.proxy:
            return []
        output = []
        for f in [f for f in model._meta.local_fields if not getattr(f, "not_in_db", False)]:
            output.extend(self.sql_indexes_for_field(model, f, style))
        return output

def activate_sql_create_model_monkey_patch():
    if not hasattr( BaseDatabaseCreation.sql_create_model, "_sign"):
        print "activate_sql_create_model_monkey_patch"
        BaseDatabaseCreation.sql_create_model = sql_create_model
sql_indexes_for_model._sign = "monkey patch by compositekey"

def activate_sql_indexes_for_model_monkey_patch():
     if not hasattr(  BaseDatabaseCreation.sql_indexes_for_model, "_sign"):
        print "activate_sql_indexes_for_model_monkey_patch"
        BaseDatabaseCreation.sql_indexes_for_model = sql_indexes_for_model