__author__ = 'fabio'

def sequence_reset_sql(self, style, model_list):
    from django.db import models
    from django.db.backends.oracle.base import _get_sequence_reset_sql
    output = []
    query = _get_sequence_reset_sql()
    for model in model_list:
        for f in [f for f in model._meta.local_fields if not getattr(f, "not_in_db", False)]:
            if isinstance(f, models.AutoField):
                table_name = self.quote_name(model._meta.db_table)
                sequence_name = self._get_sequence_name(model._meta.db_table)
                column_name = self.quote_name(f.column)
                output.append(query % {'sequence': sequence_name,
                                       'table': table_name,
                                       'column': column_name})
                # Only one AutoField is allowed per model, so don't
                # continue to loop
                break
        for f in model._meta.many_to_many:
            if not f.rel.through:
                table_name = self.quote_name(f.m2m_db_table())
                sequence_name = self._get_sequence_name(f.m2m_db_table())
                column_name = self.quote_name('id')
                output.append(query % {'sequence': sequence_name,
                                       'table': table_name,
                                       'column': column_name})
    return output
sequence_reset_sql._sign = "monkey patch by compositekey"

def activate_sequence_reset_sql_monkey_patch():
    from django.conf import settings
    def check_database_property(property, value):
        for name in settings.DATABASES:
                if settings.DATABASES[name][property].strip() == value:
                    return True
        return False
    
    if check_database_property('ENGINE', 'django.db.backends.oracle'):
        from django.db.backends.oracle.base import DatabaseOperations
        # monkey patch
        if not hasattr(DatabaseOperations.sequence_reset_sql, "_sign"):
            print "activate_sequence_reset_sql_monkey_patch"
            DatabaseOperations.sequence_reset_sql = sequence_reset_sql