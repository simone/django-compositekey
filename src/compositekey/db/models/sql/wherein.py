from itertools import chain

__author__ = 'aldaran'

from django.conf import settings

SEPARATOR = getattr(settings, "SELECT_IN_SQL_SEPARATOR",   '#')

service = {}

class MultipleColumnsIN(object):
    def __init__(self, cols, values=[], extra='', alias=None):
        self.cols = cols
        self.values = values
        self.extra = extra
        self.alias = alias + "." if alias else ""


    def inner_sql(self, qn, connection):
        return service.get(connection.vendor, UseConcat)(self.cols, self.values, self.extra, self.alias).inner_sql(qn, connection)

    def as_sql(self, qn, connection):
        return service.get(connection.vendor, UseConcat)(self.cols, self.values, self.extra, self.alias).as_sql(qn, connection)


class UseConcat(object):
    """
    Concat columns and values.

    SQLITE note quote(column)
    """
    concat = "||"
    cq = "quote(%s%s)"

    def __init__(self, cols, values, extra, alias):
        self.cols = cols
        self.values = values
        self.extra = extra
        self.alias = alias

    def quote_v(self, value):
        if isinstance(value, int):
            return str(value)
        return "'%s'" % (str(value).replace("'", "''"))

    def inner_sql(self, qn=None, connection=None):
        col_sep = self.quote_v(SEPARATOR).join([self.concat]*2)

        if isinstance(self.cols, (list, tuple)):
            if len(self.cols) > 1:
                # there are more than one column
                column = col_sep.join([self.cq % (self.alias, qn(c)) for c in self.cols])
            else: # multiple, but one only column!
                column = qn(self.cols[0])
        else:
            column = self.cq % (self.alias, qn(self.cols))
        return column

    def as_sql(self, qn=None, connection=None):
        col_sep = self.quote_v(SEPARATOR).join([self.concat]*2)
        params = self.values
        if isinstance(self.cols, (list, tuple)):
            if len(self.cols) > 1:
                # there are more than one column
                column = col_sep.join([self.cq % (self.alias, qn(c)) for c in self.cols])
                if self.extra == '':
                    params = [SEPARATOR.join([self.quote_v(v) for v in val]) for val in self.values]
            else: # multiple, but one only column!
                column = qn(self.cols[0])
                if self.extra == '':
                    params = [self.quote_v(v) for v in zip(*self.values)[0]]
        else:
            column = self.cq % (self.alias, qn(self.cols))
            params = [self.quote_v(v) for v in self.values]
        return '%s IN %s' % (column, self.extra or "(%s)" % ",".join(["%s"] * len(params))), tuple(params or ())


class UseConcatQuote(UseConcat):
    """
    POSTGRES quote_literal
    """
    cq = "quote_literal(%s%s)"

    def quote_v(self, value):
        return "'%s'" % (str(value).replace("'", "''"))


class UseTuple(object):
    """
    ORACLE
    """
    template = '%s IN (%%s)'

    def __init__(self, cols, values, extra, alias):
        self.cols = cols
        self.values = values
        self.extra = extra
        self.alias = alias

    def inner_sql(self, qn=None, connection=None):
        if isinstance(self.cols, (list, tuple)):
            column = "%s" % ",".join([qn(c.strip()) for c in self.cols])
        else:
            column = qn(self.cols.strip())
        return column

    def as_sql(self, qn=None, connection=None):
        params = self.values
        if isinstance(self.cols, (list, tuple)):
            # there are more than one column

            column = "(%s)" % ",".join([qn(c.strip()) for c in self.cols])
            format = self.template % column
            if self.extra == '':
                # fix multiple IN if empty values
                params = chain(*self.values) if self.values else (None,)*len(self.cols)
                format = format % ",".join(["(%s)" % ",".join(("%s",)*len(self.cols))] * max(1, len(self.values)))
            else:
                format = format % self.extra
        else:
            column = qn(self.cols.strip())
            params = self.values
            format = self.template % column

        return format, params


class UseTupleWithDummy(UseTuple):
    """
    MYSQL
    """
    template = '%s IN (%%s, (null,null))'


class UseTupleValues(UseTuple):
    """
    DB2 (with values)
    """
    template = '%s IN (values %%s)'

service["sqlite"] = UseConcat
service["postgresql"] = UseConcatQuote
service["mysql"] = UseTupleWithDummy
service["oracle"] = UseTuple
service["DB2"] = UseTupleValues
