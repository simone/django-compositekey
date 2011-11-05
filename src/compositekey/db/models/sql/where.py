from django.db.models.fields import Field
from django.db.models.sql.where import EmptyShortCircuit, EmptyResultSet, WhereNode


def wrap_make_atom(original_make_atom):
    def make_atom(self, child, qn, connection):
        """
        Turn a tuple (table_alias, column_name, db_type, lookup_type,
        value_annot, params) into valid SQL.

        Returns the string for the SQL fragment and the parameters to use for
        it.
        """
        _lvalue, _lookup_type, _value_annot, _params_or_value = child
        if hasattr(_lvalue, 'process'):
            try:
                _lvalue, _params = _lvalue.process(_lookup_type, _params_or_value, connection)
            except EmptyShortCircuit:
                raise EmptyResultSet
        else:
            _params = Field().get_db_prep_lookup(_lookup_type, _params_or_value,
                connection=connection, prepared=True)

        if isinstance(_lvalue, tuple):
            # A direct database column lookup.
            table_alias, name, db_type = _lvalue
            if hasattr(name, "sql_for_columns"):
                field_sql = name.sql_for_columns(_lvalue, qn, connection)
                if hasattr(field_sql, "make_atoms"):
                    return field_sql.make_atoms(_params, _lookup_type, _value_annot, qn, connection)

        return original_make_atom(self, child, qn, connection)

    make_atom._sign = "monkey patch by compositekey"
    return make_atom

def activate_make_atom_monkey_patch():
    # monkey patch
    if not hasattr(WhereNode.make_atom, "_sign"):
        print "activate_make_atom_monkey_patch"
        WhereNode.make_atom = wrap_make_atom(WhereNode.make_atom)
