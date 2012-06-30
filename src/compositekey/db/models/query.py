import logging
from django.db import connections

from django.db.models.query import get_cached_row, get_klass_info, RawQuerySet
from django.db.models.query_utils import InvalidQuery
from compositekey.db.models.query_utils import new_deferred_class_factory as deferred_class_factory
from compositekey.utils import *

__author__ = 'aldaran'

log = logging.getLogger(__name__)

class RawCompositeQuerySet(RawQuerySet):

    def __iter__(self):
        # Mapping of attrnames to row column positions. Used for constructing
        # the model using kwargs, needed when not all model's fields are present
        # in the query.
        model_init_field_names = {}
        # A list of tuples of (column name, column position). Used for
        # annotation fields.
        annotation_fields = []

        # Cache some things for performance reasons outside the loop.
        db = self.db
        compiler = connections[db].ops.compiler('SQLCompiler')(
            self.query, connections[db], db
        )
        need_resolv_columns = hasattr(compiler, 'resolve_columns')

        query = iter(self.query)

        # Find out which columns are model's fields, and which ones should be
        # annotated to the model.
        for pos, column in enumerate(self.columns):
            if column in self.model_fields:
                model_init_field_names[self.model_fields[column].attname] = pos
            else:
                annotation_fields.append((column, pos))

        # Find out which model's fields are not present in the query.
        skip = set()
        for field in self.model._meta.fields:
            if field.attname not in model_init_field_names:
                if not hasattr(field, "not_in_db"):
                    skip.add(field.attname)
        if skip:
            if self.model._meta.pk.attname in skip:
                raise InvalidQuery('Raw query must include the primary key')
            model_cls = deferred_class_factory(self.model, skip)
        else:
            model_cls = self.model
            # All model's fields are present in the query. So, it is possible
            # to use *args based model instantation. For each field of the model,
            # record the query column position matching that field.
            model_init_field_pos = []
            for field in self.model._meta.fields:
                if not hasattr(field, "not_in_db"):
                    model_init_field_pos.append(model_init_field_names[field.attname])
        if need_resolv_columns:
            fields = [self.model_fields.get(c, None) for c in self.columns]
            # Begin looping through the query values.
        for values in query:
            if need_resolv_columns:
                values = compiler.resolve_columns(values, fields)
                # Associate fields to values
            if skip:
                model_init_kwargs = {}
                for attname, pos in model_init_field_names.iteritems():
                    model_init_kwargs[attname] = values[pos]
                instance = model_cls(**model_init_kwargs)
            else:
                model_init_args = [values[pos] for pos in model_init_field_pos]
                instance = model_cls(*model_init_args)
            if annotation_fields:
                for column, pos in annotation_fields:
                    setattr(instance, column, values[pos])

            instance._state.db = db
            instance._state.adding = False

            yield instance



def iterator(self):
    """
    An iterator over the results from applying this QuerySet to the
    database.
    """
    fill_cache = self.query.select_related
    if isinstance(fill_cache, dict):
        requested = fill_cache
    else:
        requested = None
    max_depth = self.query.max_depth

    extra_select = self.query.extra_select.keys()
    aggregate_select = self.query.aggregate_select.keys()

    only_load = self.query.get_loaded_field_names()
    if not fill_cache:
        fields = self.model._meta.fields

    load_fields = []
    # If only/defer clauses have been specified,
    # build the list of fields that are to be loaded.
    if only_load:
        for field, model in self.model._meta.get_fields_with_model():
            if model is None:
                model = self.model
            try:
                if field.name in only_load[model]:
                    # Add a field that has been explicitly included
                    load_fields.append(field.name)
            except KeyError:
                # Model wasn't explicitly listed in the only_load table
                # Therefore, we need to load all fields from this model
                load_fields.append(field.name)

    index_start = len(extra_select)
    aggregate_start = index_start + len(load_fields or getattr(self.model._meta, "db_fields", self.model._meta.fields))

    skip = None
    if load_fields and not fill_cache:
        # Some fields have been deferred, so we have to initialise
        # via keyword arguments.
        skip = set()
        init_list = []
        for field in fields:
            if field.name not in load_fields:
                skip.add(field.attname)
            else:
                init_list.append(field.attname)
        model_cls = deferred_class_factory(self.model, skip)

    # Cache db and model outside the loop
    db = self.db
    model = self.model
    compiler = self.query.get_compiler(using=db)
    if fill_cache:
        klass_info = get_klass_info(model, max_depth=max_depth,
                                    requested=requested, only_load=only_load)
    for row in compiler.results_iter():
        if fill_cache:
            obj, _ = get_cached_row(row, index_start, db, klass_info,
                                    offset=len(aggregate_select))
        else:
            if skip:
                row_data = row[index_start:aggregate_start]
                obj = model_cls(**dict(zip(init_list, row_data)))
            else:
                # Omit aggregates in object creation.
                obj = model(*row[index_start:aggregate_start])

            # Store the source database of the object
            obj._state.db = db
            # This object came from the database; it's not being added.
            obj._state.adding = False

        if extra_select:
            for i, k in enumerate(extra_select):
                setattr(obj, k, row[i])

        # Add the aggregates to the model
        if aggregate_select:
            for i, aggregate in enumerate(aggregate_select):
                setattr(obj, aggregate, row[i+aggregate_start])

        yield obj
iterator._sign = "monkey patch by compositekey"

def v_iterator(self):
    # Purge any extra columns that haven't been explicitly asked for
    extra_names = self.query.extra_select.keys()
    nodb_names = getattr(self.model._meta, "nodb_names", [])
    field_names = [name for name in self.field_names if name.split("__")[0] not in nodb_names]
    aggregate_names = self.query.aggregate_select.keys()

    names = extra_names + field_names + aggregate_names

    for row in self.query.get_compiler(self.db).results_iter():
        yield dict(zip(names, row))

def vl_iterator(self):
    if self.flat and len(self._fields) == 1:
        for row in self.query.get_compiler(self.db).results_iter():
            yield row[0]
    elif not self.query.extra_select and not self.query.aggregate_select:
        for row in self.query.get_compiler(self.db).results_iter():
            yield tuple(row)
    else:
        # When extra(select=...) or an annotation is involved, the extra
        # cols are always at the start of the row, and we need to reorder
        # the fields to match the order in self._fields.
        extra_names = self.query.extra_select.keys()
        aggregate_names = self.query.aggregate_select.keys()
        nodb_names = getattr(self.model._meta, "nodb_names", [])
        field_names = [f for f in self.field_names if f not in nodb_names]

        names = extra_names + field_names + aggregate_names

        # If a field list has been specified, use it. Otherwise, use the
        # full list of fields, including extras and aggregates.
        if self._fields:
            fields = [f for f in list(self._fields) + filter(lambda f: f not in self._fields, aggregate_names) if f not in nodb_names]
        else:
            fields = names

        for row in self.query.get_compiler(self.db).results_iter():
            data = dict(zip(names, row))
            yield tuple([data[f] for f in fields])

def wrap_update(original):

    def _update(self, _values):
        assert self.query.can_filter(), \
                "Cannot update a query once a slice has been taken."
        values = {}
        for field, model, value in _values:
            if not hasattr(field, "fields"):
                values[field.name] = (field, model, value)
            else:
                for f, v in zip(field.fields, disassemble_pk(value, len(field.fields))):
                    values[f.name] = (f, model, v)
        return original(self, values.values())
    return _update

def activate_iterator_monkey_patch():
    from django.db.models.query import QuerySet, ValuesQuerySet, ValuesListQuerySet
    # monkey patch
    if not hasattr(QuerySet.iterator, "_sign"):
        log.debug("activate_iterator_monkey_patch")
        QuerySet.iterator = iterator
        ValuesQuerySet.iterator = v_iterator
        ValuesListQuerySet.iterator = vl_iterator
        QuerySet._update = wrap_update(QuerySet._update)
