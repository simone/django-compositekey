from django.forms.models import ModelForm
from django.forms import models as module
from django.utils.datastructures import SortedDict

__author__ = 'aldaran'


#class CompositeModelForm(ModelForm):
#    pass


def wrap_construct_instance(original_construct_instance):
    def construct_instance(form, instance, fields=None, exclude=None):
        opts = instance._meta
        if not getattr(opts, "has_composite_foreignkeys_field", False):
            return original_construct_instance(form, instance, fields=fields, exclude=exclude)

        # todo: maybe is possible don't rewrite all function
        from django.db import models
        cleaned_data = form.cleaned_data
        file_field_list = []
        # hack added composite_foreignkeys_fields
        for f in opts.fields + opts.composite_foreignkeys_fields.values():
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
    construct_instance._sign = "composite modelform_monkey_path"
    return construct_instance

def wrap_model_to_dict(original_model_to_dict):
    def model_to_dict(instance, fields=None, exclude=None):
        opts = instance._meta
        if not getattr(opts, "has_composite_foreignkeys_field", False):
            return original_model_to_dict(instance, fields=fields, exclude=exclude)
        # todo: maybe is possible don't rewrite all function

        # avoid a circular import
        from django.db.models.fields.related import ManyToManyField
        data = {}
        # hack added composite_foreignkeys_fields
        for f in opts.fields + opts.many_to_many + opts.composite_foreignkeys_fields.values():
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
    model_to_dict._sign = "composite modelform_monkey_path"
    return model_to_dict


def wrap_fields_for_model(original_fields_for_model):
    def fields_for_model(model, fields=None, exclude=None, widgets=None, formfield_callback=None):
        opts = model._meta

        if not getattr(opts, "has_composite_foreignkeys_field", False):
            return original_fields_for_model(model, fields=fields, exclude=fields, widgets=fields, formfield_callback=fields)

        # todo: maybe is possible don't rewrite all function
        field_list = []
        ignored = []
        # hack added composite_foreignkeys_fields
        for f in sorted(opts.fields + opts.many_to_many + opts.composite_foreignkeys_fields.values()):
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

    fields_for_model._sign = "composite modelform_monkey_path"
    return fields_for_model

def activate_modelform_monkey_path():
    # monkey patch
    if not hasattr(module.fields_for_model, "_sign"):
        print "activate_modelform_monkey_path"
        setattr(module, "fields_for_model", wrap_fields_for_model(module.fields_for_model))
        setattr(module, "model_to_dict", wrap_model_to_dict(module.model_to_dict))
        setattr(module, "construct_instance", wrap_construct_instance(module.construct_instance))
