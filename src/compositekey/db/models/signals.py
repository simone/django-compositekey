from compositekey.utils import disassemble_pk

__author__ = 'aldaran'

from django.dispatch.dispatcher import receiver
from django.db.models.signals import class_prepared
import operator

@receiver(class_prepared)
def prepare_model_and_meta(sender, **kwargs):
    opts = sender._meta
    unique_together = []
    for field_constraints in opts.unique_together:
        fields = [opts.get_field(name) for name in field_constraints]
        fields = [f.fields if hasattr(f, "fields") else [f] for f in fields]
        fields = reduce(operator.add, fields)
        unique_together.append([f.name for f in fields])
    opts.unique_together = tuple(unique_together)


    # implement automatically the django natural keys
    # if is not yet implemented
    if getattr(sender._meta, "has_composite_primarykeys_field", False):
        
        if not hasattr(sender, 'natural_key'):
            def natural_key(self):
                return disassemble_pk(self.pk, len(self._meta.composite_primarykeys_field.get_key_fields()))
            
            sender.natural_key = natural_key

        if not hasattr(sender._default_manager, 'get_by_natural_key'):

            class NaturalCompositeManager(sender._default_manager.__class__):
                def get_by_natural_key(self, *args):
                    names = [f.name for f in self.model._meta.composite_primarykeys_field.get_key_fields()]
                    return self.get(**dict(zip(names, args)))
                
            sender._default_manager.__class__ = NaturalCompositeManager

    # add special fields to the child
    for parent, field in sender._meta.parents.items():
        if hasattr(parent._meta, "composite_special_fields"):
            sender._meta.composite_special_fields = list(getattr(sender._meta, "composite_special_fields", []))
            sender._meta.composite_special_fields += list(parent._meta.composite_special_fields)
            sender._meta.composite_special_fields = set(sender._meta.composite_special_fields)

#    if getattr(opts, "enable_composite", False):
#        for m2m in opts.local_many_to_many:
#            m2m.rel.through._meta.enable_composite = True

