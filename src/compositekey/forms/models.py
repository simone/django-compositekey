__author__ = 'aldaran'

from django.forms import models
from django.utils.datastructures import SortedDict

__all__ = ["activate_modelform_monkey_patch"]

def wrap_construct_instance(original_construct_instance):
    def construct_instance(form, instance, fields=None, exclude=None):
        opts = instance._meta
        if not getattr(opts, "enable_composite", False):
            return original_construct_instance(form, instance, fields=fields, exclude=exclude)

        # todo: maybe is possible don't rewrite all function
        from django.db import models
        cleaned_data = form.cleaned_data
        file_field_list = []
        # hack added composite_foreignkeys_fields
        for f in opts.fields + opts.composite_special_fields:
            if not f.editable or isinstance(f, models.AutoField) \
                    or not f.name in cleaned_data:
                continue
            if fields is not None and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            # Defer saving file-type fields until after the other fields, so a
            # callable upload_to can use the values from other fields.
            if isinstance(f, models.FileField):
                file_field_list.append(f)
            else:
                f.save_form_data(instance, cleaned_data[f.name])

        for f in file_field_list:
            f.save_form_data(instance, cleaned_data[f.name])

        return instance
    construct_instance._sign = "composite modelform_monkey_patch"
    return construct_instance

def wrap_model_to_dict(original_model_to_dict):
    def model_to_dict(instance, fields=None, exclude=None):
        opts = instance._meta
        if not getattr(opts, "enable_composite", False):
            return original_model_to_dict(instance, fields=fields, exclude=exclude)
        # todo: maybe is possible don't rewrite all function

        # avoid a circular import
        from django.db.models.fields.related import ManyToManyField
        data = {}
        # hack added composite_foreignkeys_fields
        for f in opts.fields + opts.many_to_many + opts.composite_special_fields:
            if not f.editable:
                continue
            if fields and not f.name in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ManyToManyField):
                # If the object doesn't have a primary key yet, just use an empty
                # list for its m2m fields. Calling f.value_from_object will raise
                # an exception.
                if instance.pk is None:
                    data[f.name] = []
                else:
                    # MultipleChoiceWidget needs a list of pks, not object instances.
                    data[f.name] = [obj.pk for obj in f.value_from_object(instance)]
            else:
                data[f.name] = f.value_from_object(instance)
        return data
    model_to_dict._sign = "composite modelform_monkey_patch"
    return model_to_dict


def wrap_fields_for_model(original_fields_for_model):
    def fields_for_model(model, fields=None, exclude=None, widgets=None, formfield_callback=None):
        opts = model._meta

        if not getattr(opts, "enable_composite", False):
            return original_fields_for_model(model, fields=fields, exclude=fields, widgets=fields, formfield_callback=fields)

        # todo: maybe is possible don't rewrite all function
        field_list = []
        ignored = []
        # hack added composite_foreignkeys_fields
        for f in sorted(opts.fields + opts.many_to_many + opts.composite_special_fields):
            if not f.editable:
                continue
            if fields is not None and not f.name in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if widgets and f.name in widgets:
                kwargs = {'widget': widgets[f.name]}
            else:
                kwargs = {}

            if formfield_callback is None:
                formfield = f.formfield(**kwargs)
            elif not callable(formfield_callback):
                raise TypeError('formfield_callback must be a function or callable')
            else:
                formfield = formfield_callback(f, **kwargs)

            if formfield:
                field_list.append((f.name, formfield))
            else:
                ignored.append(f.name)
        field_dict = SortedDict(field_list)
        if fields:
            field_dict = SortedDict(
                [(f, field_dict.get(f)) for f in fields
                    if ((not exclude) or (exclude and f not in exclude)) and (f not in ignored)]
            )
        return field_dict

    fields_for_model._sign = "composite modelform_monkey_patch"
    return fields_for_model


def wrap_get_foreign_key(original_get_foreign_key):
    def _get_foreign_key(parent_model, model, fk_name=None, can_fail=False):
        opts = model._meta

        if not getattr(opts, "enable_composite", False):
            return original_get_foreign_key(parent_model, model, fk_name=fk_name, can_fail=can_fail)

        # avoid circular import
        from django.db.models import ForeignKey
        if fk_name:
            fks_to_parent = [f for f in opts.fields+opts.composite_special_fields if f.name == fk_name]
            if len(fks_to_parent) == 1:
                fk = fks_to_parent[0]
                if not isinstance(fk, ForeignKey) or \
                        (fk.rel.to != parent_model and
                         fk.rel.to not in parent_model._meta.get_parent_list()):
                    raise Exception("fk_name '%s' is not a ForeignKey to %s" % (fk_name, parent_model))
            elif len(fks_to_parent) == 0:
                raise Exception("%s has no field named '%s'" % (model, fk_name))
        else:
            # Try to discover what the ForeignKey from model to parent_model is
            fks_to_parent = [
                f for f in opts.fields+opts.composite_special_fields
                if isinstance(f, ForeignKey)
                and (f.rel.to == parent_model
                    or f.rel.to in parent_model._meta.get_parent_list())
            ]
            if len(fks_to_parent) == 1:
                fk = fks_to_parent[0]
            elif len(fks_to_parent) == 0:
                if can_fail:
                    return
                raise Exception("%s has no ForeignKey to %s" % (model, parent_model))
            else:
                raise Exception("%s has more than 1 ForeignKey to %s" % (model, parent_model))
        return fk
    _get_foreign_key._sign = "composite modelform_monkey_patch"
    return _get_foreign_key

def activate_modelform_monkey_patch():
    # monkey patch
    if not hasattr(models.fields_for_model, "_sign"):
        print "activate_modelform_monkey_patch"
        setattr(models, "fields_for_model", wrap_fields_for_model(models.fields_for_model))
        setattr(models, "model_to_dict", wrap_model_to_dict(models.model_to_dict))
        setattr(models, "construct_instance", wrap_construct_instance(models.construct_instance))
        setattr(models, "_get_foreign_key", wrap_get_foreign_key(models._get_foreign_key))
