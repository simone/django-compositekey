__author__ = 'aldaran'


def sequence_reset_sql(self, style, model_list):
    from django.db import models
    output = []
    qn = self.quote_name
    for model in model_list:
        # Use `coalesce` to set the sequence for each model to the max pk value if there are records,
        # or 1 if there are none. Set the `is_called` property (the third argument to `setval`) to true
        # if there are records (as the max pk value is already in use), otherwise set it to false.
        # Use pg_get_serial_sequence to get the underlying sequence name from the table name
        # and column name (available since PostgreSQL 8)

        for f in [f for f in model._meta.local_fields if not getattr(f, "not_in_db", False)]:
            if isinstance(f, models.AutoField):
                output.append("%s setval(pg_get_serial_sequence('%s','%s'), coalesce(max(%s), 1), max(%s) %s null) %s %s;" % \
                    (style.SQL_KEYWORD('SELECT'),
                    style.SQL_TABLE(qn(model._meta.db_table)),
                    style.SQL_FIELD(f.column),
                    style.SQL_FIELD(qn(f.column)),
                    style.SQL_FIELD(qn(f.column)),
                    style.SQL_KEYWORD('IS NOT'),
                    style.SQL_KEYWORD('FROM'),
                    style.SQL_TABLE(qn(model._meta.db_table))))
                break # Only one AutoField is allowed per model, so don't bother continuing.
        for f in model._meta.many_to_many:
            if not f.rel.through:
                output.append("%s setval(pg_get_serial_sequence('%s','%s'), coalesce(max(%s), 1), max(%s) %s null) %s %s;" % \
                    (style.SQL_KEYWORD('SELECT'),
                    style.SQL_TABLE(qn(f.m2m_db_table())),
                    style.SQL_FIELD('id'),
                    style.SQL_FIELD(qn('id')),
                    style.SQL_FIELD(qn('id')),
                    style.SQL_KEYWORD('IS NOT'),
                    style.SQL_KEYWORD('FROM'),
                    style.SQL_TABLE(qn(f.m2m_db_table()))))
    return output
sequence_reset_sql._sign = "monkey patch by compositekey"

def activate_pg_sequence_reset_sql_monkey_patch():
    from django.conf import settings
    def check_database_property(property, value):
        for name in settings.DATABASES:
                if settings.DATABASES[name][property].strip() == value:
                    return True
        return False

    if check_database_property('ENGINE', 'django.db.backends.postgresql_psycopg2'):
        from django.db.backends.postgresql_psycopg2.operations import DatabaseOperations
        # monkey patch
        if not hasattr(DatabaseOperations.sequence_reset_sql, "_sign"):
            print "activate_sequence_reset_sql_monkey_patch"
            DatabaseOperations.sequence_reset_sql = sequence_reset_sql