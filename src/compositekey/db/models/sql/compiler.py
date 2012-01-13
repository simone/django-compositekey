from django.core.exceptions import FieldError
from django.db.models.sql.constants import LHS_JOIN_COL, LHS_ALIAS, RHS_JOIN_COL, TABLE_NAME, JOIN_TYPE, LOOKUP_SEP
from django.db.models.sql.query import get_order_dir
from compositekey.db.models.sql.wherein import MultipleColumnsIN

__author__ = 'aldaran'

from django.db.models.sql.compiler import SQLCompiler

__all__ = ["activate_get_from_clause_monkey_patch"]

def wrap_get_from_clause(original_get_from_clause):

    def get_from_clause(self):
        """
        Returns a list of strings that are joined together to go after the
        "FROM" part of the query, as well as a list any extra parameters that
        need to be included. Sub-classes, can override this to create a
        from-clause via a "select".

        This should only be called after any SQL construction methods that
        might change the tables we need. This means the select columns and
        ordering must be done first.
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

def find_ordering_name(self, name, opts, alias=None, default_order='ASC',
        already_seen=None):
    """
    Returns the table alias (the name might be ambiguous, the alias will
    not be) and column name for ordering by the given 'name' parameter.
    The 'name' is of the form 'field1__field2__...__fieldN'.
    """
    name, order = get_order_dir(name, default_order)
    pieces = name.split(LOOKUP_SEP)
    if not alias:
        alias = self.query.get_initial_alias()
    field, target, opts, joins, last, extra = self.query.setup_joins(pieces,
            opts, alias, False)
    alias = joins[-1]
    col = getattr(target.column, "columns", [target.column])[0] # todo: ordering using only the first column in multicolumns
    if not field.rel:
        # To avoid inadvertent trimming of a necessary alias, use the
        # refcount to show that we are referencing a non-relation field on
        # the model.
        self.query.ref_alias(alias)

    # Must use left outer joins for nullable fields and their relations.
    self.query.promote_alias_chain(joins,
        self.query.alias_map[joins[0]][JOIN_TYPE] == self.query.LOUTER)

    # If we get to this point and the field is a relation to another model,
    # append the default ordering for that model.
    if field.rel and len(joins) > 1 and opts.ordering:
        # Firstly, avoid infinite loops.
        if not already_seen:
            already_seen = set()
        join_tuple = tuple([self.query.alias_map[j][TABLE_NAME] for j in joins])
        if join_tuple in already_seen:
            raise FieldError('Infinite loop caused by ordering.')
        already_seen.add(join_tuple)

        results = []
        for item in opts.ordering:
            results.extend(self.find_ordering_name(item, opts, alias,
                    order, already_seen))
        return results

    if alias:
        # We have to do the same "final join" optimisation as in
        # add_filter, since the final column might not otherwise be part of
        # the select set (so we can't order on it).
        while 1:
            join = self.query.alias_map[alias]
            if col != join[RHS_JOIN_COL]:
                break
            self.query.unref_alias(alias)
            alias = join[LHS_ALIAS]
            col = join[LHS_JOIN_COL]
    return [(alias, col, order)]



def activate_get_from_clause_monkey_patch():
    # monkey patch
    if not hasattr(SQLCompiler.get_from_clause, "_sign"):
        print "activate_get_from_clause_monkey_patch"
        SQLCompiler.get_from_clause = wrap_get_from_clause(SQLCompiler.get_from_clause)
        SQLCompiler.find_ordering_name = find_ordering_name
