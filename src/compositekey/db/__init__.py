__author__ = 'aldaran'

from compositekey.db.models import *


try:
    from south.modelsinspector import add_ignored_fields

    add_ignored_fields(["^compositekey\.db\.models\.fields\.multiplekey\.MultiFieldPK$"])
    add_ignored_fields(["^compositekey\.db\.models\.fields\.multiplekey\.OneToOneField$"])
    add_ignored_fields(["^compositekey\.db\.models\.fields\.multiplekey\.ForeignKey$"])
except ImportError:
    pass


