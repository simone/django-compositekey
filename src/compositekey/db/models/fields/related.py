__author__ = 'aldaran'

from django.db.models.fields.related import ForeignKey
from compositekey.db.models.fields.wrap import *

__all__ = ['activate_fk_monkey_patch',]

def wrap_fk_monkey_patch(ori_init, ori_contribute_to_class):

    from compositekey.db import MultipleFieldPrimaryKey

    def __init__(self, *args, **kwargs):
        self.fields_ext = kwargs.pop("fields_ext", {})
        ori_init(self, *args, **kwargs)

    def contribute_to_class(self, cls, name):
        opts = cls._meta
        ori_contribute_to_class(self, cls, name)
        related_field = self.rel.get_related_field()

        if isinstance(related_field, MultipleFieldPrimaryKey):
            opts._prepare = wrap_meta_prepare(opts, opts._prepare)
            opts.has_composite_foreignkeys_field = True
            opts.composite_foreignkeys_fields = getattr(opts, "composite_foreignkeys_fields", {})
            opts.composite_foreignkeys_fields[name]=self
            opts.composite_special_fields = getattr(opts, "composite_special_fields", [])

            # needs to remove esplicit from fields (really is not a field)
            opts.local_fields.remove(self)
            opts.add_virtual_field(self)
            opts.composite_special_fields.append(self)

            cls._meta.get_field = wrap_get_field(cls._meta, cls._meta.get_field)
            cls._meta.get_field_by_name = wrap_get_field_by_name(cls._meta, cls._meta.get_field_by_name)

            cls.__init__ = wrap_init_model(cls.__init__) # adding reset PK cache

            # add the real composition fields
                # in the inheritance, child models doesn't have to create more fields
            if not opts.abstract:
                new_fields = [prepare_hidden_key_field(cls, f, self.fields_ext, prefix=name) for f in related_field.get_key_fields()]
                for f in new_fields: cls.add_to_class(f.name, f)
                self.fields = new_fields

                # get/set _id propery
                setattr(cls, "%s_id" % name, property(get_composite_pk(new_fields, name=name), set_composite_pk(new_fields, name=name)))

                # hack add wrap setter related
                reverse_desc = getattr(cls, name)
                reverse_desc.__set__ = wrap_setter(reverse_desc.__set__, name, new_fields)

                if self.unique:
                    names = [f.name for f in new_fields]
                    if names not in opts.unique_together:
                        opts.unique_together.append([f.name for f in new_fields])

                # hack db_column for joins
                self.column = ",".join([f.column for f in new_fields])


    contribute_to_class._sign = "activate_fk_monkey_patch"
    return __init__, contribute_to_class

def activate_fk_monkey_patch():
    # monkey patch
    if not hasattr(ForeignKey.contribute_to_class, "_sign"):
        print "activate_fk_monkey_patch"
        ForeignKey.__init__, ForeignKey.contribute_to_class = wrap_fk_monkey_patch(ForeignKey.__init__, ForeignKey.contribute_to_class)
