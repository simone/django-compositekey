from django.db.models.manager import Manager

__author__ = 'aldaran'

__all__ = ["activate_insert_query_monkey_patch"]

def wrap_insert_query(original_insert_query):

    def _insert(self, objs, fields, **kwargs):
        fields = [field for field in fields if not getattr(field, "not_in_db", False)]
        return original_insert_query(self, objs, fields, **kwargs)

    _insert._sign = "activate_insert_query_monkey_patch"
    return _insert


def activate_insert_query_monkey_patch():
    # monkey patch
    if not hasattr(Manager._insert, "_sign"):
        print "activate_insert_query_monkey_patch"
        Manager._insert =  wrap_insert_query(Manager._insert)