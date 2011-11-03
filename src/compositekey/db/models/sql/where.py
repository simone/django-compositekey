from django.conf import settings

SEPARATOR = getattr(settings, "SELECT_IN_SQL_SEPARATOR",   '#s3p#')
CONCAT    = getattr(settings, "SELECT_IN_SQL_CONCATENATE", ' || ' )


class WhereConcat(object):
    """
    Concat columns and values.

    todo:
     * checks escape (QN)
     * check mysql compatibility "+" or group_concat
     * check postgresql ||
     * check oracle ||
     * check M$ ||
     * check DB2 ||
    """
    def __init__(self, cols, values, operation='='):
        self.cols = cols
        self.values = values
        self.operation = operation

    def as_sql(self, qn=None, connection=None):
        col_sep = qn(SEPARATOR).join([CONCAT]*2)

        if isinstance(self.cols, (list, tuple)):
            # there are more than one column
            column = qn(col_sep.join([qn(c) for c in self.cols]))
            param = SEPARATOR.join(self.values)
        else:
            column = qn(self.cols)
            param = self.values

        return '%s %s %%s' % (column, self.operation), param


class WhereConcatIN(object):
    """
    Concat columns and values.
    
    todo:
     * checks escape (QN)
     * check mysql compatibility "+" or group_concat
     * check postgresql ||
     * check oracle ||
     * check M$ ||
     * check DB2 ||
    """
    def __init__(self, cols, values):
        self.cols = cols
        self.values = values

    def as_sql(self, qn=None, connection=None):
        col_sep = qn(SEPARATOR).join([CONCAT]*2)

        if isinstance(self.cols, (list, tuple)):
            # there are more than one column
            column = qn(col_sep.join([qn(c) for c in self.cols]))
            params = [SEPARATOR.join(val) for val in self.values]
        else:
            column = qn(self.cols)
            params = self.values

        return '%s IN (%%s)' % column, tuple(params or ())
