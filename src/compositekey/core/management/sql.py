from django.core.management import sql
from django.db import models

__author__ = 'fabio'

def sql_delete(app, style, connection):
    "Returns a list of the DROP TABLE SQL statements for the given app."

    # This should work even if a connection isn't available
    try:
        cursor = connection.cursor()
    except:
        cursor = None

    # Figure out which tables already exist
    if cursor:
        table_names = connection.introspection.get_table_list(cursor)
    else:
        table_names = []

    output = []

    # Output DROP TABLE statements for standard application tables.
    to_delete = set()

    references_to_delete = {}
    app_models = models.get_models(app, include_auto_created=True)
    for model in app_models:
        if cursor and connection.introspection.table_name_converter(model._meta.db_table) in table_names:
            # The table exists, so it needs to be dropped
            opts = model._meta
            for f in [f for f in opts.local_fields if not getattr(f, "not_in_db", False)]:
                if f.rel and f.rel.to not in to_delete:
                    references_to_delete.setdefault(f.rel.to, []).append( (model, f) )

            to_delete.add(model)

    for model in app_models:
        if connection.introspection.table_name_converter(model._meta.db_table) in table_names:
            output.extend(connection.creation.sql_destroy_model(model, references_to_delete, style))

    # Close database connection explicitly, in case this output is being piped
    # directly into a database client, to avoid locking issues.
    if cursor:
        cursor.close()
        connection.close()

    return output[::-1] # Reverse it, to deal with table dependencies.
sql_delete._sign = "monkey patch by compositekey"

def activate_sql_delete_monkey_patch():
   if not hasattr(sql.sql_delete, "_sign"):
        print "activate_sql_delete_monkey_patch"
        sql.sql_delete = sql_delete