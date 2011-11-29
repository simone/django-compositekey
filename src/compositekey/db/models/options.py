import itertools

__author__ = 'aldaran'

from django.db.models.loading import app_cache_ready
from django.db.models.options import Options

def get_fields_with_model(self):
    return [(field, model) for field, model in self._get_fields_with_model() if not getattr(field, "not_in_db", False)]
get_fields_with_model._sign = "activate_get_fields_with_model_monkey_patch"

def init_name_map(self):
    """
    Initialises the field name -> field object mapping.
    """
    cache = {}
    # We intentionally handle related m2m objects first so that symmetrical
    # m2m accessor names can be overridden, if necessary.
    for f, model in self.get_all_related_m2m_objects_with_model():
        cache[f.field.related_query_name()] = (f, model, False, True)
    for f, model in self.get_all_related_objects_with_model():
        cache[f.field.related_query_name()] = (f, model, False, False)
    for f, model in self.get_m2m_with_model():
        cache[f.name] = (f, model, True, True)
    for f, model in self._get_fields_with_model():
        cache[f.name] = (f, model, True, False)
    if app_cache_ready():
        self._name_map = cache
    return cache

def _fill_fields_cache(self):
    cache = []
    for parent in self.parents:
        for field, model in parent._meta._get_fields_with_model():
            if model:
                cache.append((field, model))
            else:
                cache.append((field, parent))
    cache.extend([(f, None) for f in self.local_fields])
    self._field_cache = tuple(cache)
    self._field_name_cache = [x for x, _ in cache]

def nodb_names(self):
    names = list(itertools.chain(*[(f.name, f.attname) for f in self.local_fields if getattr(f, "not_in_db", False)]))
    if hasattr(self.pk, "is_composite_primarykeys_field"):
        names += ["pk"]
    return names

def activate_get_fields_with_model_monkey_patch():
    # monkey patch
    if not hasattr(Options.get_fields_with_model, "_sign"):
        print "activate_get_fields_with_model_monkey_patch"
        Options._get_fields_with_model = Options.get_fields_with_model
        Options.get_fields_with_model = get_fields_with_model
        Options.init_name_map = init_name_map
        Options._fill_fields_cache = _fill_fields_cache

        # setup DB/fields
        Options.db_fields = property(lambda self: [f for f in self.fields if not getattr(f, "not_in_db", False)])
        Options.nodb_names = property(nodb_names)
