from django.db.models.query_utils import QueryWrapper

__author__ = 'aldaran'

from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import Field, AutoField

from compositekey.db.models.fields.wrap import *
from compositekey.db.models.base import patched_model_init
from compositekey.patch import django_compositekey_patch
from compositekey.db.models.sql.column import MultiColumn

__all__ = ['MultiFieldPK',]

class MultiFieldPK(AutoField):
    description = _("Composite Primary Keys")

    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _(u"'%s' value must be a composite key."),
    }
    def __init__(self, *fields, **kwargs):
        django_compositekey_patch()
        self.is_composite_primarykeys_field = True
        kwargs['primary_key'] = True
        self._field_names = fields
        assert isinstance(self._field_names, (list, tuple)) and len(self._field_names) > 0, \
               "%ss must have fields=[..] with at least 2 fields" % self.__class__.__name__
        kwargs['blank'] = True
        kwargs['serialize'] = False
        super(MultiFieldPK, self).__init__(**kwargs)

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        return value

    def validate(self, value, model_instance):
        pass

    def get_prep_value(self, value):
        return value

    def contribute_to_class(self, cls, name):
        super(MultiFieldPK, self).contribute_to_class(cls, name)
        opts = cls._meta
        # skip if not a local field (for inheritance)
        if not self in opts.local_fields: return

        opts.enable_composite = True
        opts.has_auto_field = True # required for inlineformset
        cls._meta._prepare = wrap_meta_prepare(cls._meta, cls._meta._prepare)
        cls._meta.has_composite_primarykeys_field = True
        cls._meta.composite_primarykeys_field = self
        cls._meta.composite_special_fields = getattr(cls._meta, "composite_special_fields", [])
        cls._meta.composite_special_fields.append(self)

        cls.save = wrap_save_model(cls.save) # adding reset PK cache
        cls.__init__ = patched_model_init # change the order of input

        def lazy_init():
            self.fields = self.get_key_fields()
            assert isinstance(self.fields, (list, tuple)) and len(self.fields) > 1, \
               "%s must have a %s with at least 2 fields (%s)" % (cls.__name__, self.__class__.__name__,
                                                                  ",".join([f.name for f in self.fields]))
            names = [f.name for f in self.fields]
            cls._meta.ordering = cls._meta.ordering or names

            # TODO: better add primary key = () and not unique
            # example: PRIMARY KEY (album, disk, posn)

            if names not in cls._meta.unique_together:
                cls._meta.unique_together.append(names)
            for field in self.fields: field.db_index=True

            # get/set PK propery
            setattr(cls, cls._meta.pk.attname, property(get_composite_pk(self.fields), del_composite_pk(), del_composite_pk()))

            # hack db_column for joins see compiler
            self.column = MultiColumn(self.fields)
            self.db_type = nope
            self.db_index = False
            self.not_in_db = True
            self.primary_key = True
            
        cls._meta._lazy_prepare_field_actions.append(lazy_init)


    def get_key_fields(self):
        fields = []
        for f in [self.model._meta.get_field(name) for name in self._field_names]:
            if hasattr(f, "fields"):
                fields += [nf for nf in f.fields]
            else:
                fields.append(f)
        return fields
