import datetime
from itertools import chain
from compositekey.db.models.sql.wherein import MultipleColumnsIN
from compositekey.utils import *
__author__ = 'aldaran'


class Atoms(object):
    def __init__(self, fields, sql_colums):
        self.fields = fields
        self.sql_colums = sql_colums

    def make_atoms(self, params, lookup_type, value_annot, qn, connection):
        if hasattr(params, 'as_sql'):
            extra, params = params.as_sql(qn, connection)
        else:
            extra = ''

        if extra == '': # if is not a subquery params
            params = [disassemble_pk(v, len(self.fields)) for v in params]
            params  = [[field.get_prep_value(part) for field, part in zip(self.fields, value)] for value in params]

        # regolarize params
        #if len(params)>0 and len(params[0]) < len(self.sql_colums):
        #    params = params[0]

        if lookup_type == 'in':
            return MultipleColumnsIN(self.sql_colums, params, extra).as_sql(qn, connection)

        atoms = zip(*[self.make_atom(field_sql, extra, param, lookup_type, value_annot, qn, connection) for field_sql, param in zip(self.sql_colums, zip(*params))])
        if not atoms: return "", []
        sql, new_params = atoms

        return " AND ".join(sql), chain(*new_params)

    def make_atom(self, field_sql, extra, params, lookup_type, value_annot, qn, connection):
        if value_annot is datetime.datetime:
            cast_sql = connection.ops.datetime_cast_sql()
        else:
            cast_sql = '%s'

        if (len(params) == 1 and params[0] == '' and lookup_type == 'exact'
            and connection.features.interprets_empty_strings_as_nulls):
            lookup_type = 'isnull'
            value_annot = True

        if lookup_type in connection.operators:
            format = "%s %%s %%s" % (connection.ops.lookup_cast(lookup_type),)
            return (format % (field_sql,
                              connection.operators[lookup_type] % cast_sql,
                              extra), params)

        if lookup_type in ('range', 'year'):
            return ('%s BETWEEN %%s and %%s' % field_sql, params)
        elif lookup_type in ('month', 'day', 'week_day'):
            return ('%s = %%s' % connection.ops.date_extract_sql(lookup_type, field_sql),
                    params)
        elif lookup_type == 'isnull':
            return ('%s IS %sNULL' % (field_sql,
                (not value_annot and 'NOT ' or '')), ())
        elif lookup_type == 'search':
            return (connection.ops.fulltext_search_sql(field_sql), params)
        elif lookup_type in ('regex', 'iregex'):
            return connection.ops.regex_lookup(lookup_type) % (field_sql, cast_sql), params

        raise TypeError('Invalid lookup_type: %r' % lookup_type)

class MultiColumn(object):
    def __init__(self, fields):
        self.fields = fields
        self.columns = [f.column for f in fields]

    def as_sql(self, qn, connection):
        return MultipleColumnsIN(self.columns).inner_sql(qn, connection)

    def sql_for_columns(self, data, qn, connection):
        """
        "WHERE ...
        T1.foo = 6.
        T1.bar = 4
        """
        table_alias, _name, db_type = data

        fun = connection.ops.field_cast_sql

        if table_alias:
            lhs = [fun(f.db_type(connection)) % '%s.%s' % (qn(table_alias), qn(f.column)) for f in self.fields]
        else:
            lhs = [fun(f.db_type(connection)) % qn(f.column) for f in self.fields]
        return Atoms(self.fields, lhs)

    def __repr__(self):
        return "MultiColumn(%s)" % ",".join(self.columns)

    def startswith(self, _):
        # hack for don't see errors
        raise Exception("Trying to 'quote' a multiple key FIELD. Operation not supported yet. Please fix it", self.fields, self.columns)

    endswith = startswith