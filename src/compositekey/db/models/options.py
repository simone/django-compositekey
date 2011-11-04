__author__ = 'aldaran'

from django.db.models.loading import get_models, app_cache_ready
from django.db.models.options import Options

def wrap_init_name_map(ori_init_name_map):

    def init_name_map(self):
        """
        Initialises the field name -> field object mapping.
        """
        #if not getattr(self, "enable_composite", False):
        return ori_init_name_map(self)

        cache = {}
        # We intentionally handle related m2m objects first so that symmetrical
        # m2m accessor names can be overridden, if necessary.
        if getattr(self, "has_composite_primarykeys_field", False):
            cache[self.composite_primarykeys_field.name] = (self.composite_primarykeys_field, self.composite_primarykeys_field.model, True, False)
        if getattr(self, "has_composite_foreignkeys_field", False):
            for name, field in self.composite_foreignkeys_fields.items():
                cache[name] = (field, field.model, True, False)
        for f, model in self.get_all_related_m2m_objects_with_model():
            cache[f.field.related_query_name()] = (f, model, False, True)
        for f, model in self.get_all_related_objects_with_model():
            cache[f.field.related_query_name()] = (f, model, False, False)
        for f, model in self.get_m2m_with_model():
            cache[f.name] = (f, model, True, True)
        for f, model in self.get_fields_with_model():
            cache[f.name] = (f, model, True, False)
        if app_cache_ready():
            self._name_map = cache
        print self, cache.keys
        return cache

    init_name_map._sign = "activate_init_name_map_monkey_patch"
    return init_name_map

def activate_init_name_map_monkey_patch():
    pass
    # monkey patch
#    if not hasattr(Options.init_name_map, "_sign"):
#        print "activate_init_name_map_monkey_patch"
#        Options.init_name_map = wrap_init_name_map(Options.init_name_map)
    