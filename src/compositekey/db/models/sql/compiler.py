import logging

from django.db.models.sql.constants import MULTI
from django.db.models.sql.query import Query

from compositekey.db.models.sql.wherein import MultipleColumnsIN
from compositekey.utils import assemble_pk

__author__ = 'aldaran'

from django.db.models.sql.compiler import SQLCompiler, SQLUpdateCompiler, SQLInsertCompiler

__all__ = ["activate_get_from_clause_monkey_patch"]

log = logging.getLogger(__name__)

def wrap_get_from_clause(original_get_from_clause):

    def get_from_clause(self):
        """
        Returns a list of strings that are joined together to go after the
        "FROM" part of the query, as well as a list any extra parameters that
        need to be included. Sub-classes, can override this to create a
        from-clause via a "select".

        This should only be called after any SQL construction methods that
        might change the tables we need. This means the select columns,
        ordering and distinct must be done first.
        """
        result = []
        qn = self.quote_name_unless_alias
        qn2 = self.connection.ops.quote_name
        first = True
        for alias in self.query.tables:
            if not self.query.alias_refcount[alias]:
                continue
            try:
                name, alias, join_type, lhs, _lhs_col, _col, nullable = self.query.alias_map[alias]
                lhs_cols, cols = getattr(_lhs_col, "columns", [_lhs_col]), getattr(_col, "columns", [_col])
                #assert len(lhs_cols) == len(cols), "could not join multiple columns with simple column (%s <> %s)" % (lhs_cols, cols)
            except KeyError:
                # Extra tables can end up in self.tables, but not in the
                # alias_map if they aren't in a join. That's OK. We skip them.
                continue
            alias_str = (alias != name and ' %s' % alias or '')
            if join_type and not first:
                if len(lhs_cols) == len(cols):
                    _on_where = " AND ".join(['%s.%s = %s.%s' %
                                              (qn(lhs),qn2(lhs_col), qn(alias), qn2(col))
                                              for lhs_col,col in zip(lhs_cols, cols)
                    ])
                    result.append('%s %s%s ON (%s)'
                            % (join_type, qn(name), alias_str, _on_where))
                else:
                    #assert len(lhs_cols) == len(cols), "could not join multiple columns with simple column (%s <> %s)" % (lhs_cols, cols)
                    c1 = MultipleColumnsIN(lhs_cols, alias=qn(lhs)).inner_sql(qn2, self.connection)
                    c2 = MultipleColumnsIN(cols, alias=qn(alias)).inner_sql(qn2, self.connection)
                    result.append('%s %s%s ON (%s)'
                        % (join_type, qn(name), alias_str, '%s = %s' % (c1, c2)))
            else:
                connector = not first and ', ' or ''
                result.append('%s%s%s' % (connector, qn(name), alias_str))
            first = False
        for t in self.query.extra_tables:
            alias, unused = self.query.table_alias(t)
            # Only add the alias if it's not already present (the table_alias()
            # calls increments the refcount, so an alias refcount of one means
            # this is the only reference.
            if alias not in self.query.alias_map or self.query.alias_refcount[alias] == 1:
                connector = not first and ', ' or ''
                result.append('%s%s' % (connector, qn(alias)))
                first = False
        return result, []

    get_from_clause._sign = "monkey patch by compositekey"
    return get_from_clause

def _setup_joins(self, pieces, opts, alias):
    """
    A helper method for get_ordering and get_distinct. This method will
    call query.setup_joins, handle refcounts and then promote the joins.

    Note that get_ordering and get_distinct must produce same target
    columns on same input, as the prefixes of get_ordering and get_distinct
    must match. Executing SQL where this is not true is an error.
    """
    if not alias:
        alias = self.query.get_initial_alias()
    field, target, opts, joins, _, _ = self.query.setup_joins(pieces,
        opts, alias, False)
    # We will later on need to promote those joins that were added to the
    # query afresh above.
    joins_to_promote = [j for j in joins if self.query.alias_refcount[j] < 2]
    alias = joins[-1]
    col = getattr(target.column, "columns", [target.column])[0] # todo: ordering using only the first column in multicolumns
    if not field.rel:
        # To avoid inadvertent trimming of a necessary alias, use the
        # refcount to show that we are referencing a non-relation field on
        # the model.
        self.query.ref_alias(alias)

    # Must use left outer joins for nullable fields and their relations.
    # Ordering or distinct must not affect the returned set, and INNER
    # JOINS for nullable fields could do this.
    self.query.promote_joins(joins_to_promote)
    return field, col, alias, joins, opts


def pre_sql_setup(self):
    """
    If the update depends on results from other tables, we need to do some
    munging of the "where" conditions to match the format required for
    (portable) SQL updates. That is done here.

    Further, if we are going to be running multiple updates, we pull out
    the id values to update at this point so that they don't change as a
    result of the progressive updates.
    """
    self.query.select_related = False
    self.query.clear_ordering(True)
    super(SQLUpdateCompiler, self).pre_sql_setup()
    count = self.query.count_active_tables()
    if not self.query.related_updates and count == 1:
        return

    # We need to use a sub-select in the where clause to filter on things
    # from other tables.
    query = self.query.clone(klass=Query)
    query.bump_prefix()
    query.extra = {}
    query.select = []
    query.add_fields([query.model._meta.pk.name])
    # Recheck the count - it is possible that fiddling with the select
    # fields above removes tables from the query. Refs #18304.
    count = query.count_active_tables()
    if not self.query.related_updates and count == 1:
        return

    must_pre_select = count > 1 and not self.connection.features.update_can_self_select

    # Now we adjust the current query: reset the where clause and get rid
    # of all the tables we don't need (since they're in the sub-select).
    self.query.where = self.query.where_class()
    if self.query.related_updates or must_pre_select:
        # Either we're using the idents in multiple update queries (so
        # don't want them to change), or the db backend doesn't support
        # selecting from the updating table (e.g. MySQL).
        idents = []
        multiple = hasattr(query.model._meta.pk, "fields")
        if multiple:
            query.select = []
            query.add_fields([f.name for f in query.model._meta.pk.fields])
        for rows in query.get_compiler(self.using).execute_sql(MULTI):
            idents.extend([assemble_pk(*r) if multiple else r[0] for r in rows])
        self.query.add_filter(('pk__in', idents))
        self.query.related_ids = idents
    else:
        # The fast path. Filters and updates in one query.
        self.query.add_filter(('pk__in', query))
    for alias in self.query.tables[1:]:
        self.query.alias_refcount[alias] = 0


def as_sql(self):
    # We don't need quote_name_unless_alias() here, since these are all
    # going to be column names (so we can avoid the extra overhead).
    qn = self.connection.ops.quote_name
    opts = self.query.model._meta
    result = ['INSERT INTO %s' % qn(opts.db_table)]

    has_fields = bool(self.query.fields)
    fields = self.query.fields if has_fields else [opts.pk]
    result.append('(%s)' % ', '.join([qn(f.column) for f in fields]))

    if has_fields:
        params = values = [
        [
        f.get_db_prep_save(getattr(obj, f.attname) if self.query.raw else f.pre_save(obj, True), connection=self.connection)
        for f in fields
        ]
        for obj in self.query.objs
        ]
    else:
        values = [[self.connection.ops.pk_default_value()] for obj in self.query.objs]
        params = [[]]
        fields = [None]
    can_bulk = (not any(hasattr(field, "get_placeholder") for field in fields) and
                not self.return_id and self.connection.features.has_bulk_insert)

    if can_bulk:
        placeholders = [["%s"] * len(fields)]
    else:
        placeholders = [
        [self.placeholder(field, v) for field, v in zip(fields, val)]
        for val in values
        ]
        # Oracle Spatial needs to remove some values due to #10888
        params = self.connection.ops.modify_insert_params(placeholders, params)
    if self.return_id and self.connection.features.can_return_id_from_insert:
        params = params[0]
        if not hasattr(opts.pk.column, "columns"):
            col = "%s.%s" % (qn(opts.db_table), qn(opts.pk.column))
        else:
            col = 1
        result.append("VALUES (%s)" % ", ".join(placeholders[0]))
        r_fmt, r_params = self.connection.ops.return_insert_id()
        # Skip empty r_fmt to allow subclasses to customize behaviour for
        # 3rd party backends. Refs #19096.
        if r_fmt:
            result.append(r_fmt % col)
            params += r_params
        return [(" ".join(result), tuple(params))]
    if can_bulk:
        result.append(self.connection.ops.bulk_insert_sql(fields, len(values)))
        return [(" ".join(result), tuple([v for val in values for v in val]))]
    else:
        return [
            (" ".join(result + ["VALUES (%s)" % ", ".join(p)]), vals)
            for p, vals in zip(placeholders, params)
        ]



def activate_get_from_clause_monkey_patch():
    # monkey patch
    if not hasattr(SQLCompiler.get_from_clause, "_sign"):
        log.debug("activate_get_from_clause_monkey_patch")
        SQLCompiler.get_from_clause = wrap_get_from_clause(SQLCompiler.get_from_clause)
        SQLCompiler._setup_joins = _setup_joins
        SQLUpdateCompiler.pre_sql_setup = pre_sql_setup
        SQLInsertCompiler.as_sql = as_sql
