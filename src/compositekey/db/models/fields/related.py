from django.db.models import signals
import operator

__author__ = 'aldaran'

from django.db.models.fields.related import ForeignKey, ManyToManyRel
from compositekey.db.models.fields.wrap import *
from compositekey.db.models.base import patched_model_init
from compositekey.db.models.sql.column import MultiColumn

__all__ = ['activate_fk_monkey_patch',]

def identity(self, value): return value

def wrap_fk_monkey_patch(ori_init, ori_contribute_to_class):

    def __init__(self, *args, **kwargs):
        self.fields_ext = kwargs.pop("fields_ext", {})
        ori_init(self, *args, **kwargs)

    def contribute_to_class(self, cls, name):
        opts = cls._meta
        ori_contribute_to_class(self, cls, name)
        if not opts.abstract:
            # STR check if is a lazy relationship
            def lazy_init():
                if not isinstance(self.rel.to, str) and getattr(self.rel.to._meta, "has_composite_primarykeys_field", False):
                    related_field = self.rel.to._meta.composite_primarykeys_field
                    opts.enable_composite = True
                    opts.has_composite_foreignkeys_field = True
                    opts.composite_foreignkeys_fields = getattr(opts, "composite_foreignkeys_fields", {})
                    opts.composite_foreignkeys_fields[name]=self
                    opts.composite_special_fields = getattr(opts, "composite_special_fields", [])
                    opts.composite_special_fields.append(self)

                    cls.__init__ = patched_model_init # adding reset PK cache

                    new_fields = [prepare_hidden_key_field(cls, f, self.blank, self.null, self.fields_ext, prefix=name) for f in related_field.get_key_fields()]
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
                    self.column = MultiColumn(new_fields)
                    self.not_in_db = True
                    self.db_type = nope
                    self.db_index = False
                    self.get_prep_value = identity
                    #self.primary_key = True # ERROR in inlineforms (unique)

            # if the class is an autocreated class, the FK contrib_to_class need to be lazy after the "creation contrib_to_class()"
            if opts.auto_created:
                opts.auto_created._meta._prepare = wrap_meta_prepare(opts.auto_created._meta, opts.auto_created._meta._prepare)
                opts.auto_created._meta._lazy_prepare_fk_actions.append(lazy_init)

                def recheck_unique_together():
                    unique_together = []
                    for field_constraints in opts.unique_together:
                        fields = [opts.get_field(name) for name in field_constraints]
                        fields = [f.fields if hasattr(f, "fields") else [f] for f in fields]
                        fields = reduce(operator.add, fields)
                        unique_together.append([f.name for f in fields])
                    opts.unique_together = tuple(unique_together)
                opts.auto_created._meta._lazy_prepare_fk_actions.append(recheck_unique_together)

            else:
                if isinstance(self.rel.to, str) and self.rel.to in ("self", cls.__name__):
                    # force here the self relationship and pospone the FM multiple check after all prepare other fields
                    self.rel.to = cls
                    opts._prepare = wrap_meta_prepare(opts, opts._prepare)
                    opts._lazy_prepare_fk_actions.append(lazy_init)
                else:
                    lazy_init()

    contribute_to_class._sign = "activate_fk_monkey_patch"
    return __init__, contribute_to_class

def activate_fk_monkey_patch():
    # monkey patch
    if not hasattr(ForeignKey.contribute_to_class, "_sign"):
        print "activate_fk_monkey_patch"
        ForeignKey.__init__, ForeignKey.contribute_to_class = wrap_fk_monkey_patch(ForeignKey.__init__, ForeignKey.contribute_to_class)
