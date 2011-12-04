from django.db.models.query import get_cached_row, get_klass_info
from compositekey.db.models.query_utils import new_deferred_class_factory as deferred_class_factory
from compositekey.utils import *

__author__ = 'aldaran'


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
        print "activate_iterator_monkey_patch"
        QuerySet.iterator = iterator
        ValuesQuerySet.iterator = v_iterator
        ValuesListQuerySet.iterator = vl_iterator
        QuerySet._update = wrap_update(QuerySet._update)

