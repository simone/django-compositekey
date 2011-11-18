__author__ = 'aldaran'

from django.db.models.sql.subqueries import DeleteQuery
from django.db.models.sql.constants import *
from django.db.models.sql.where import AND

from compositekey.db.models.sql.wherein import MultipleColumnsIN
from compositekey.utils import *

__all__ =["activate_delete_monkey_patch"]

def wrap_delete_batch(original_delete_batch):
    from compositekey.utils import disassemble_pk

    def delete_batch(obj, pk_list, using, field=None):
        opts=obj.model._meta
        if not field:
            field = opts.pk

        # original batch delete iof not composite
        if not getattr(field, "is_composite_primarykeys_field", False):
            return original_delete_batch(obj, pk_list, using, field=field)

        # composite PK fields
        field_keys = field.get_key_fields()

        for offset in range(0, len(pk_list), GET_ITERATOR_CHUNK_SIZE):
            where = obj.where_class()
            off_list = pk_list[offset : offset + GET_ITERATOR_CHUNK_SIZE]

            # delete where in using concatenate features
            values = [disassemble_pk(value, len(field_keys)) for value in off_list]
            values = [[field.get_prep_value(part) for field, part in zip(field_keys, value)] for value in values]
            where.add(MultipleColumnsIN([f.column for f in field_keys], values), AND)

            obj.do_query(obj.model._meta.db_table, where, using=using)


    delete_batch._sign = "monkey patch by compositekey"
    return delete_batch

def activate_delete_monkey_patch():
    # monkey patch
    if not hasattr(DeleteQuery.delete_batch, "_sign"):
        print "activate_delete_monkey_patch"
        DeleteQuery.delete_batch = wrap_delete_batch(DeleteQuery.delete_batch)
