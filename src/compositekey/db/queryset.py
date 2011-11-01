from compositekey.db.models.sql.query import CompositeQuery

__author__ = 'aldaran'

from django.db.models.query import EmptyQuerySet, QuerySet, RawQuerySet
from compositekey.utils import disassemble_pk

__all__ = ["EmptyCompositeQuerySet", "CompositeQuerySet", "CompositeRawQuerySet"]

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

def _post_actions_composite_query(model, kwargs, name):
    value = kwargs.pop(name)
    print "skip (NOT YET IMPLEMETED) - join with composite key [the results are WRONG :-)]", model, kwargs, name, value
    return lambda query : query

class _HackQuerySet(object):

    def __init__(self, model=None, query=None, using=None):
        super(_HackQuerySet, self).__init__(model=model, query=query, using=using)
        # hack to use a composite query
        self.query.__class__ = CompositeQuery

    def _filter_or_exclude(self, negate, *args, **kwargs):

        opts=self.model._meta
        # need to unpack pk or keyname of composite key in values
        if getattr(opts, "has_composite_primarykeys_field", False):
            _update_filter_from(self.model, kwargs)
            _update_filter_from(self.model, kwargs, pk=opts.pk.attname)

        post_actions = []
        if getattr(opts, "has_composite_foreignkeys_field", False):
            for name in opts.composite_foreignkeys_fields.keys():
                for key in kwargs.keys():
                    if key == name or key.startswith("%s__" % name):
                        post_actions.append(_post_actions_composite_query(self.model, kwargs, key))

        print self.model, "update filters...", args, kwargs
        query = super(_HackQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

        for call in post_actions:
            query = call(query)
        return query



class CompositeQuerySet(_HackQuerySet, QuerySet):
    pass

class CompositeRawQuerySet(_HackQuerySet, RawQuerySet):
    pass

class EmptyCompositeQuerySet(_HackQuerySet, EmptyQuerySet):
    pass
