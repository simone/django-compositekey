from django.db.models.query import EmptyQuerySet, QuerySet, RawQuerySet
from django.db.models.sql import query

from compositekey.db.fields import MultipleFieldPrimaryKey, disassemble_pk

__author__ = 'aldaran'

__all__ = ["EmptyCompositeQuerySet", "CompositeQuerySet", "CompositeRawQuerySet"]

#class CompositeSQLQuery(query.Query):
#    pass

class EmptyCompositeQuerySet(EmptyQuerySet):
    pass

def _update_filter_from(model, kwargs, pk="pk"):
    # todo optimize - invert.. for each kwargs... check "nou use pop"

    fields = model._meta.composite_primarykeys_field.get_key_fields()
    keys = [f.name for f in fields]
    value = kwargs.pop(pk, None)
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




class CompositeQuerySet(QuerySet):

    def __init__(self, model=None, query=None, using=None):
        super(CompositeQuerySet, self).__init__(model=model, query=query, using=using)
        #self.query.__class__ = CompositeSQLQuery

    def _filter_or_exclude(self, negate, *args, **kwargs):
        # need to unpack pk or keyname of composite key in values
        if getattr(self.model._meta, "has_composite_primarykeys_field", False):
            _update_filter_from(self.model, kwargs)
            _update_filter_from(self.model, kwargs, pk=self.model._meta.pk.attname)
        print "update filters...", kwargs
        return super(CompositeQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

class CompositeRawQuerySet(RawQuerySet):
    pass
