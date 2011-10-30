from django.db.models.sql.subqueries import DeleteQuery

from django.core.exceptions import FieldError
from django.db.models.fields import DateField, FieldDoesNotExist
from django.db.models.sql.constants import *
from django.db.models.sql.datastructures import Date
from django.db.models.sql.query import Query
from django.db.models.sql.where import AND, Constraint

__author__ = 'aldaran'

def decore_delete_batch(original_delete_batch):
    from compositekey.db.fields import MultipleFieldPrimaryKey
    from compositekey.db.fields import disassemble_pk
    
    def delete_batch(obj, pk_list, using, field=None):
        """
        Set up and execute delete queries for all the objects in pk_list.

        More than one physical query may be executed if there are a
        lot of values in pk_list.
        """
        if not field:
            field = obj.model._meta.pk

        # original batch delete iof not composite
        if not isinstance(field, MultipleFieldPrimaryKey):
            return original_delete_batch(obj, pk_list, using, field=field)

        # composite PK fields
        #field_keys = [obj.model._meta.get_field_by_name(key)[0] for key in field.keys]
        field_keys = field.get_key_fields()

        for offset in range(0, len(pk_list), GET_ITERATOR_CHUNK_SIZE):
            where = obj.where_class()
            off_list = pk_list[offset : offset + GET_ITERATOR_CHUNK_SIZE]

            values = zip([field for field in field_keys], zip(*[disassemble_pk(value) for value in off_list]))
            for field, oo in values:
                where.add((Constraint(None, field.column, field), 'in', oo), AND)

            obj.do_query(obj.model._meta.db_table, where, using=using)
            from django.db import connection
            print "last query is: ", connection.queries[-1]


    delete_batch._sign = "monkey patch by compositekey"
    return delete_batch

def activate_delete_monkey_path():
    # monkey patch
    if not hasattr(DeleteQuery.delete_batch, "_sign"):
        print "activate_delete_monkey_path"
        DeleteQuery.delete_batch = decore_delete_batch(DeleteQuery.delete_batch)
