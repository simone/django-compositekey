__author__ = 'aldaran'

from django.db.models.query import QuerySet
from compositekey.utils import disassemble_pk

__all__ = ["activate_queryset_monkey_patch"]

def _update_filter_from(fields, kwargs, pk="pk"):
    # todo optimize - invert.. for each kwargs... check "nou use pop"
    keys = [f.name for f in fields]
    for op in ["", "__pk"]:
        value = kwargs.pop("%s%s" % (pk, op), None)
        value = value.pk if hasattr(value, "pk") else value
        if value: kwargs.update(zip(keys, disassemble_pk(value)))

    for op in ['regex', 'iregex', 'search',
               'contains', 'icontains', 'iexact', 'startswith', 'istartswith',
               'endswith', 'iendswith', 'isnull',
               'exact', 'gt', 'gte', 'lt', 'lte'
               'month', 'day', 'week_day',]:
        
        value = kwargs.pop("%s__%s" % (pk, op), None)
        if value: kwargs.update(zip(["%s__%s" % (key, op) for key in keys], disassemble_pk(value)))

    for op in ['in', 'range']:
        values = kwargs.pop("%s__%s" % (pk, op), None)
        if values and len(values) > 0:
            kwargs.update(zip(["%s__%s" % (key, op) for key in keys], zip(*[disassemble_pk(value) for value in values])))

def wrap_get_from_clause(ori_filter_or_exclude):

    def _filter_or_exclude(self, negate, *args, **kwargs):
        opts=self.model._meta
        if getattr(opts, "enable_composite", False):
            # need to unpack pk or keyname of composite key in values
            if getattr(opts, "has_composite_primarykeys_field", False):
                fields = self.model._meta.composite_primarykeys_field.get_key_fields()
                _update_filter_from(fields, kwargs)
                _update_filter_from(fields, kwargs, pk=opts.pk.attname)

            if getattr(opts, "has_composite_foreignkeys_field", False):
                for name in opts.composite_foreignkeys_fields.keys():
                    for key in kwargs.keys():
                        if key == name or key.startswith("%s__" % name):
                            _update_filter_from(opts.composite_foreignkeys_fields[name].fields, kwargs, pk=name)
    
            print "updated filters...", self.model, args, kwargs
        return ori_filter_or_exclude(self, negate, *args, **kwargs)

    _filter_or_exclude._sign = "activate_queryset_monkey_patch"
    return _filter_or_exclude


def activate_queryset_monkey_patch():
    # monkey patch
    if not hasattr(QuerySet._filter_or_exclude, "_sign"):
        print "activate_queryset_monkey_patch"
        QuerySet._filter_or_exclude = wrap_get_from_clause(QuerySet._filter_or_exclude)
