__author__ = 'aldaran'

def django_compositekey_patch():
    from compositekey.db.models.sql.query import activate_add_fields_monkey_patch
    from compositekey.db.models.sql.compiler import activate_get_from_clause_monkey_patch
    from compositekey.db.models.sql.subqueries import activate_delete_monkey_patch
    from compositekey.db.models.sql.where import activate_make_atom_monkey_patch
    from compositekey.db.models.options import activate_get_fields_with_model_monkey_patch
    from compositekey.db.models.manager import activate_insert_query_monkey_patch
    from compositekey.db.models.fields.related import activate_fk_monkey_patch
    from compositekey.db.models.signals import prepare_model_and_meta # do not DELETE

    activate_fk_monkey_patch()
    activate_get_from_clause_monkey_patch()
    activate_delete_monkey_patch()
    activate_make_atom_monkey_patch()
    activate_get_fields_with_model_monkey_patch()
    activate_insert_query_monkey_patch()
    activate_add_fields_monkey_patch()
