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
    opts.unique_together = unique_together
