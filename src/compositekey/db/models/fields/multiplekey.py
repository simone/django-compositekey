from compositekey.db.models.sql.column import MultiColumn

__author__ = 'aldaran'

from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import Field

from compositekey.db.models.fields.wrap import *
from compositekey.patch import django_compositekey_patch
from compositekey.utils import disassemble_pk
__all__ = ['MultipleFieldPrimaryKey',]

class MultipleFieldPrimaryKey(Field):
    description = _("Composite Primary Keys")

    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _(u"'%s' value must be an integer."),
    }
    def __init__(self, *args, **kwargs):
        django_compositekey_patch()
        self.is_composite_primarykeys_field = True
        kwargs['primary_key'] = True
        self._field_names = kwargs.pop('fields', [])
        assert isinstance(self._field_names, list) and len(self._field_names) > 0, \
               "%ss must have fields=[..]." % self.__class__.__name__
        kwargs['blank'] = True
        super(MultipleFieldPrimaryKey, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        return value

    def validate(self, value, model_instance):
        pass

    def get_prep_value(self, value):
        return [field.get_prep_value(val) for field, val in zip(self.get_key_fields(), disassemble_pk(value))]

    def contribute_to_class(self, cls, name):
        super(MultipleFieldPrimaryKey, self).contribute_to_class(cls, name)
        opts = cls._meta
        if not self in opts.local_fields: return

        assert not getattr(cls._meta, "has_composite_primarykeys_field", False), \
               "A model can't have more than one MultipleFieldPrimaryKey."
        assert not cls._meta.has_auto_field, \
               "A model can't have one MultipleFieldPrimaryKey or AutoField."

        opts.enable_composite = True
        cls._meta._prepare = wrap_meta_prepare(cls._meta, cls._meta._prepare)
        cls._meta.has_composite_primarykeys_field = True
        cls._meta.composite_primarykeys_field = self
        cls._meta.composite_special_fields = getattr(cls._meta, "composite_special_fields", [])
        cls._meta.composite_special_fields.append(self)

        cls.save = wrap_save_model(cls.save) # adding reset PK cache
        cls.__init__ = wrap_init_model(cls.__init__) # adding reset PK cache

        def lazy_init():
            fields = self.get_key_fields()
            names = [f.name for f in fields]
            cls._meta.ordering = cls._meta.ordering or names

            # TODO: better add primary key = () and not unique
            # example: PRIMARY KEY (album, disk, posn)

            if names not in cls._meta.unique_together:
                cls._meta.unique_together.append(names)
            for field in fields: field.db_index=True

            # get/set PK propery
            setattr(cls, cls._meta.pk.attname, property(get_composite_pk(fields), set_composite_pk(fields)))

            # hack db_column for joins see compiler
            self.column = MultiColumn(fields)
            self.db_type = lambda *args, **kwargs: None
            self.db_index = False
            self.not_in_db = True
            
        cls._meta._lazy_prepare_field_actions.append(lazy_init)



    def formfield(self, **kwargs):
        return None

    def get_key_fields(self):
        fields = []
        for f in [self.model._meta.get_field(name) for name in self._field_names]:
            if hasattr(f, "fields"):
                fields += [nf for nf in f.fields]
            else:
                fields.append(f)
        return fields
