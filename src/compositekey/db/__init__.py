__author__ = 'aldaran'

from compositekey.db.models import *


try:
    from south.modelsinspector import add_ignored_fields

    add_ignored_fields(["^compositekey\.db\.models\.fields\.multiplekey\.MultiFieldPK$"])
except ImportError:
    pass


