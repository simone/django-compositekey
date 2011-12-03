__author__ = 'aldaran'


def django_compositekey_patch():
    from compositekey.db.models.sql.query import activate_add_fields_monkey_patch
    from compositekey.db.models.sql.compiler import activate_get_from_clause_monkey_patch
    from compositekey.db.models.sql.subqueries import activate_delete_monkey_patch
    from compositekey.db.models.sql.where import activate_make_atom_monkey_patch
    from compositekey.db.models.sql.aggregates import activate_as_sql_monkey_patch
    from compositekey.db.models.options import activate_get_fields_with_model_monkey_patch
    from compositekey.db.models.manager import activate_insert_query_monkey_patch
    from compositekey.db.models.fields.related import activate_fk_monkey_patch
    from compositekey.db.models.query_utils import activate_deferred_class_factory_monkey_patch
    from compositekey.db.models.query import activate_iterator_monkey_patch
    from compositekey.db.models.signals import prepare_model_and_meta # do not DELETE

    activate_fk_monkey_patch()
    activate_get_from_clause_monkey_patch()
    activate_delete_monkey_patch()
    activate_make_atom_monkey_patch()
    activate_get_fields_with_model_monkey_patch()
    activate_insert_query_monkey_patch()
    activate_add_fields_monkey_patch()
    activate_as_sql_monkey_patch()
    activate_deferred_class_factory_monkey_patch()
    activate_iterator_monkey_patch()

    #backend patches
    from compositekey.core.management.sql import activate_sql_delete_monkey_patch
    from compositekey.db.backends.__init__ import activate_sequence_list_monkey_patch
    from compositekey.db.backends.creation import activate_sql_create_model_monkey_patch
    from compositekey.db.backends.oracle.base import activate_sequence_reset_sql_monkey_patch
    from compositekey.db.backends.postgresql_psycopg2.operations import activate_pg_sequence_reset_sql_monkey_patch

    activate_sql_delete_monkey_patch()
    activate_sequence_list_monkey_patch()
    activate_sql_create_model_monkey_patch()
    activate_sequence_reset_sql_monkey_patch()
    activate_pg_sequence_reset_sql_monkey_patch()
