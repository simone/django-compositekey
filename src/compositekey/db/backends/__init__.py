from django.db.backends import BaseDatabaseIntrospection

__author__ = 'fabio'


def sequence_list(self):
    "Returns a list of information about all DB sequences for all models in all apps."
    from django.db import models, router

    apps = models.get_apps()
    sequence_list = []

    for app in apps:
        for model in models.get_models(app):
            if not model._meta.managed:
                continue
            if not router.allow_syncdb(self.connection.alias, model):
                continue
            for f in model._meta.local_fields:
                if not getattr(f, "not_in_db", False) and isinstance(f, models.AutoField):
                    sequence_list.append({'table': model._meta.db_table, 'column': f.column})
                    break # Only one AutoField is allowed per model, so don't bother continuing.

            for f in model._meta.local_many_to_many:
                # If this is an m2m using an intermediate table,
                # we don't need to reset the sequence.
                if f.rel.through is None:
                    sequence_list.append({'table': f.m2m_db_table(), 'column': None})

    return sequence_list
sequence_list._sign = "monkey patch by compositekey"

def activate_sequence_list_monkey_patch():
    if not hasattr(BaseDatabaseIntrospection.sequence_list, "_sign"):
        print "activate_sequence_list_monkey_patch"
        BaseDatabaseIntrospection.sequence_list = sequence_list