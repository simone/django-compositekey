__author__ = 'aldaran'

from django.db.models.manager import Manager
from compositekey.db.queryset import *

__all__ = ["CompositeDefaultManager"]

class CompositeDefaultManager(Manager):
    use_for_related_fields = True

    def get_empty_query_set(self):
        return EmptyCompositeQuerySet(self.model, using=self._db)

    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        return CompositeQuerySet(self.model, using=self._db)
    
    def raw(self, raw_query, params=None, *args, **kwargs):
        return CompositeRawQuerySet(raw_query=raw_query, model=self.model, params=params, using=self._db, *args, **kwargs)

