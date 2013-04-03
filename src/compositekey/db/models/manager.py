import logging

from django.db.models.manager import Manager
from compositekey.db.models.query import RawCompositeQuerySet

__author__ = 'aldaran'
__all__ = ["activate_insert_query_monkey_patch"]

log = logging.getLogger(__name__)

def wrap_insert_query(original_insert_query):

    def _insert(self, objs, fields, **kwargs):
        fields = [field for field in fields if not getattr(field, "not_in_db", False)]
        return original_insert_query(self, objs, fields, **kwargs)

    def _raw(self, raw_query, params=None, *args, **kwargs):
        return RawCompositeQuerySet(raw_query=raw_query, model=self.model, params=params, using=self._db, *args, **kwargs)

    _insert._sign = "activate_insert_query_monkey_patch"
    _insert._raw = "activate_raw_query_monkey_patch"
    return _insert, _raw


def activate_insert_query_monkey_patch():
    # monkey patch
    if not hasattr(Manager._insert, "_sign"):
        log.debug("activate_insert_query_monkey_patch")
        Manager._insert, Manager.raw =  wrap_insert_query(Manager._insert)
        