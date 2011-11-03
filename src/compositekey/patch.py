from compositekey.db.models.fields.related import activate_fk_monkey_patch
from compositekey.db.models.options import activate_init_name_map_monkey_patch
from compositekey.db.models.query import activate_queryset_monkey_patch
from compositekey.db.models.sql.compiler import activate_get_from_clause_monkey_patch
from compositekey.db.models.sql.subqueries import activate_delete_monkey_patch
from compositekey.forms.models import activate_modelform_monkey_patch

__author__ = 'aldaran'

def django_compositekey_patch():
    activate_fk_monkey_patch()
    activate_queryset_monkey_patch()
    activate_get_from_clause_monkey_patch()
    activate_delete_monkey_patch()
    activate_modelform_monkey_patch()
    activate_init_name_map_monkey_patch()
