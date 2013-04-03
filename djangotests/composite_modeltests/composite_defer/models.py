"""
Tests for defer() and only().
"""

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from compositekey import db


class Secondary(models.Model):
    id = db.MultiFieldPK("first","second")
    first = models.CharField(max_length=50)
    second = models.CharField(max_length=50)

@python_2_unicode_compatible
class Primary(models.Model):
    id = db.MultiFieldPK("pk1","value")
    pk1 = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    related = models.ForeignKey(Secondary)

    def __str__(self):
        return self.name

class Child(Primary):
    pass

class BigChild(Primary):
    other = models.CharField(max_length=50)

class ChildProxy(Child):
    class Meta:
        proxy=True
