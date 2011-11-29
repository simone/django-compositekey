__author__ = 'aldaran'

from django.db.models.query_utils import deferred_class_factory

def new_deferred_class_factory(model, attrs):
    if hasattr(model._meta, "composite_special_fields"):
        attrs = [attr for attr in attrs if attr not in [f.attname for f in model._meta.composite_special_fields]]
    return deferred_class_factory(model, attrs)
new_deferred_class_factory._sign = "monkey patch by compositekey"

def activate_deferred_class_factory_monkey_patch():
    from django.db.models import query_utils, query, base
    # monkey patch
    if not hasattr(query_utils.deferred_class_factory, "_sign"):
        print "activate_deferred_class_factory_monkey_patch"

        # update all namespaces
        query_utils.deferred_class_factory = new_deferred_class_factory
        query.deferred_class_factory = new_deferred_class_factory
        base.deferred_class_factory = new_deferred_class_factory