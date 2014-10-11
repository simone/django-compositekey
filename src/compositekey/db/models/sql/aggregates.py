__author__ = 'aldaran'

import logging

log = logging.getLogger(__name__)
  
def as_sql(self, qn, connection):
    "Return the aggregate, rendered as SQL with parameters."
    params = []

    class AggregateMulticolumn(object):
        def __init__(self, column, aliases=[]):
            self.columns = [tuple(aliases+[c]) for c in column.columns]

        def append(self, obj):
            assert False, "please contact compositekey author"

        def as_sql(self, qn, connection):
            return "||".join(['.'.join([qn(c) for c in column]) for column in self.columns])

    if isinstance(self.col, (list, tuple)):
        # now we are ignoring the rest of the key using only the first column of the key
        col = []
        for c in self.col:
            if hasattr(c, "columns"):
                col = AggregateMulticolumn(c, aliases=col)
            else:
                col.append(c)
        _col = col
    else:
        _col = AggregateMulticolumn(self.col) if hasattr(self.col, "columns") else self.col

    if hasattr(_col, 'as_sql'):
        field_name, params = self.col.as_sql(qn, connection)
    elif isinstance(self.col, (list, tuple)):
        field_name = '.'.join([qn(c) for c in self.col])
    else:
        field_name = self.col

    substitutions = {
        'function': self.sql_function,
        'field': field_name
    }
    substitutions.update(self.extra)

    return self.sql_template % substitutions, params
as_sql._sign = "monkey patch by compositekey"

def activate_as_sql_monkey_patch():
    from django.db.models.sql.aggregates import Aggregate
    # monkey patch
    if not hasattr(Aggregate.as_sql, "_sign"):
        log.debug("activate_as_sql_monkey_patch")
        Aggregate.as_sql = as_sql
