__author__ = 'aldaran'

from django.db.models.sql.compiler import SQLCompiler

__all__ = ["activate_get_from_clause_monkey_patch"]

def wrap_get_from_clause(original_get_from_clause):

    def get_from_clause(self):
        opts=self.query.model._meta
        if not getattr(opts, "enable_composite", False):
            return original_get_from_clause(self)

        result = []
        qn = self.quote_name_unless_alias
        qn2 = self.connection.ops.quote_name
        first = True
        for alias in self.query.tables:
            if not self.query.alias_refcount[alias]:
                continue
            try:
                name, alias, join_type, lhs, _lhs_col, _col, nullable = self.query.alias_map[alias]
                #print name, alias, join_type, lhs, _lhs_col, _col, nullable
                lhs_cols, cols = _lhs_col.columns if _lhs_col else [],_col.columns if _col else []
            except KeyError:
                # Extra tables can end up in self.tables, but not in the
                # alias_map if they aren't in a join. That's OK. We skip them.
                continue
            alias_str = (alias != name and ' %s' % alias or '')
            if join_type and not first:
                _on_where = " AND ".join(['%s.%s = %s.%s' %
                                          (qn(lhs),qn2(lhs_col), qn(alias), qn2(col))
                                          for lhs_col,col in zip(lhs_cols, cols)
                ])
                result.append('%s %s%s ON (%s)'
                        % (join_type, qn(name), alias_str, _on_where))
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

def activate_get_from_clause_monkey_patch():
    # monkey patch
    if not hasattr(SQLCompiler.get_from_clause, "_sign"):
        print "activate_get_from_clause_monkey_patch"
        SQLCompiler.get_from_clause = wrap_get_from_clause(SQLCompiler.get_from_clause)
