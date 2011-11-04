from compositekey.db.models.sql.column import MultiColumn

__author__ = 'aldaran'

from django.db.models.fields.related import ForeignKey, ManyToManyRel
from compositekey.db.models.fields.wrap import *

__all__ = ['activate_fk_monkey_patch',]

def wrap_fk_monkey_patch(ori_init, ori_contribute_to_class):

    def __init__(self, *args, **kwargs):
        self.fields_ext = kwargs.pop("fields_ext", {})
        ori_init(self, *args, **kwargs)

    def contribute_to_class(self, cls, name):
        opts = cls._meta
        ori_contribute_to_class(self, cls, name)
        if not opts.abstract:
            if self.rel.field_name:
                related_field = self.rel.get_related_field()
                if getattr(related_field, "is_composite_primarykeys_field", False):
                    opts.enable_composite = True
                    opts._prepare = wrap_meta_prepare(opts, opts._prepare)
                    opts.has_composite_foreignkeys_field = True
                    opts.composite_foreignkeys_fields = getattr(opts, "composite_foreignkeys_fields", {})
                    opts.composite_foreignkeys_fields[name]=self
                    opts.composite_special_fields = getattr(opts, "composite_special_fields", [])
                    opts.composite_special_fields.append(self)

                    cls.__init__ = wrap_init_model(cls.__init__) # adding reset PK cache

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
                    self.column = MultiColumn(new_fields)
                    self.not_in_db = True
                    self.db_type = lambda *args, **kwargs: None
                    self.db_index = False

                # hack clear cache in related field, self.rel is not ready to call get_related_field()
                for _cache_name in ["_name_map", "_related_many_to_many_cache", "_related_objects_cache", "_m2m_cache", "_field_cache"]:
                    if hasattr(self.rel.to._meta, _cache_name):
                        delattr(self.rel.to._meta, _cache_name)
                    if hasattr(opts, _cache_name):
                        delattr(opts, _cache_name)

    contribute_to_class._sign = "activate_fk_monkey_patch"
    return __init__, contribute_to_class

def activate_fk_monkey_patch():
    # monkey patch
    if not hasattr(ForeignKey.contribute_to_class, "_sign"):
        print "activate_fk_monkey_patch"
        ForeignKey.__init__, ForeignKey.contribute_to_class = wrap_fk_monkey_patch(ForeignKey.__init__, ForeignKey.contribute_to_class)
