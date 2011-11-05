__author__ = 'aldaran'

from compositekey.utils import *

def wrap_meta_prepare(opts, original_prepare):
    if hasattr(original_prepare, "_sign"):
        return original_prepare

    opts._lazy_prepare_field_actions = []
    def _prepare(model):
        for prepare_action in getattr(opts, "_lazy_prepare_field_actions", []): prepare_action()
        opts._lazy_prepare_field_actions = []
        del opts._lazy_prepare_field_actions
        original_prepare(model)
    _prepare._sign = "composite"
    return _prepare

def get_composite_pk(fields, name="pk"):
    cache_name="_composite_%s_cache" % name
    def _get(obj):
        # cache, if change the values you can yet identify thre real record
        if not getattr(obj, cache_name, False):
            setattr(obj, cache_name, assemble_pk(*[getattr(obj, f.name) for f in fields]))
        return getattr(obj, cache_name)
    return _get

def set_composite_pk(fields, name="pk"):
    cache_name="_composite_%s_cache" % name
    def _set(obj, value):
        values = disassemble_pk(value)
        if len(values) <> len(fields):
            values = [None for _ in fields]
        for field, val in zip(fields, values):
            setattr(obj, field.name, val)
        # reset pk cache only you are not deleting the model
        if len(disassemble_pk(value)) == len(fields):
            if hasattr(obj, cache_name):
                delattr(obj, cache_name)
                #getattr(obj, name)
    return _set


def wrap_save_model(original_save):
    if hasattr(original_save, "_sign"):
        return original_save
    def save(obj, force_insert=False, force_update=False, using=None):
        ret = original_save(obj, force_insert=force_insert, force_update=force_update, using=using)
        # reset pk cache
        del obj._composite_pk_cache
        obj.pk
        return ret
    save.alters_data = True
    save._sign = "composite"
    return save

def prepare_hidden_key_field(model, field, ext={}, prefix="composite"):
    default = ext.get(field.name, {})
    import copy
    new_field = copy.deepcopy(field)
    # bk
    new_field.fk_fieldname = new_field.name
    new_field.model = model
    new_field.db_column = default.get("db_column", "%s_%s" % (prefix, new_field.db_column or new_field.name))
    new_field.name = default.get("name", "%s_%s" % (prefix, new_field.name))
    new_field.attname = default.get("attname", "%s_%s" % (prefix, new_field.attname))
    new_field.verbose_name = default.get("verbose_name", "%s %s" % (prefix, new_field.verbose_name))
    new_field.column = default.get("column", "%s_%s" % (prefix, new_field.column))

    # hide formfield (None)
    new_field.formfield = lambda *args, **kwargs : None
    #new_field.formfield = lambda *args, **kwargs : forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly" : True}))
    return new_field

def wrap_setter(original_set, name, fields):
    cache_name="_composite_%s_cache" % name
    def __set__(obj, value):
        original_set(obj, value)
        for field in fields:
            setattr(obj, field.name, getattr(value, field.fk_fieldname, field.default))
        delattr(obj, cache_name)
        getattr(obj, name)
    return __set__
