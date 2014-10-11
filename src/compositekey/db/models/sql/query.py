__author__ = 'aldaran'

import logging

from django.db.models.constants import LOOKUP_SEP
from django.core.exceptions import FieldError
from django.db.models.sql.datastructures import MultiJoin
from django.db.models.sql.query import Query
from django.db.models.sql.constants import SelectInfo

log = logging.getLogger(__name__)

def add_fields(self, field_names, allow_m2m=True):
    """
    Adds the given (model) fields to the select set. The field names are
    added in the order specified.
    """
    alias = self.get_initial_alias()
    opts = self.get_meta()

    try:
        for name in field_names:
            field, targets, u2, joins, path = self.setup_joins(
                    name.split(LOOKUP_SEP), opts, alias, None, allow_m2m,
                    allow_explicit_fk=True, outer_if_first=True)

            # Trim last join if possible
            targets, final_alias, remaining_joins = self.trim_joins(targets, joins[-2:], path)
            joins = joins[:-2] + remaining_joins

            self.promote_joins(joins[1:])
            for target in targets:
                col = target.column
                cols = [] if hasattr(col, "columns") else [col]
                for col in cols:
                    print "select", final_alias, col, target
                    self.select.append(SelectInfo((final_alias, col), target))
    except MultiJoin:
        raise FieldError("Invalid field name: '%s'" % name)
    except FieldError:
        if LOOKUP_SEP in name:
            # For lookups spanning over relationships, show the error
            # from the model on which the lookup failed.
            raise
        else:
            names = sorted(opts.get_all_field_names() + list(self.extra)
                           + list(self.aggregate_select))
            raise FieldError("Cannot resolve keyword %r into field. "
                    "Choices are: %s" % (name, ", ".join(names)))
    self.remove_inherited_models()
add_fields._sign = "monkey patch by compositekey"


def deferred_to_columns_cb(self, target, model, fields):
    """
    Callback used by deferred_to_columns(). The "target" parameter should
    be a set instance.
    """
    table = model._meta.db_table
    if table not in target:
        target[table] = set()
    for field in fields:
        if not hasattr(field.column, "columns"):
            target[table].add(field.column)
        else:
            target[table].update(field.column.columns)

def get_loaded_field_names_cb(self, target, model, fields):
    """
    Callback used by get_deferred_field_names().
    """
    names = [f.name for f in fields if not getattr(f, "not_in_db", False)]
    for field in fields:
        if getattr(field, "not_in_db", False):
            names += [f.name for f in field.fields]

    target[model] = set(names)


def activate_add_fields_monkey_patch():
    # monkey patch
    if not hasattr(Query.add_fields, "_sign"):
        log.debug("activate_add_fields_monkey_patch")
        Query.add_fields = add_fields
        Query.deferred_to_columns_cb = deferred_to_columns_cb
        Query.get_loaded_field_names_cb = get_loaded_field_names_cb
