"""
Tests for field subclassing.
"""

from __future__ import absolute_import

from django.db import models
from django.utils.encoding import force_unicode

from .fields import SmallField, SmallerField, JSONField
from compositekey import db

class MyModel(models.Model):
    x = db.MultipleFieldPrimaryKey(fields=('name','data'))
    name = models.CharField(max_length=10)
    data = SmallField('small field')

    def __unicode__(self):
        return force_unicode(self.name)

class OtherModel(models.Model):
    data = SmallerField()

class DataModel(models.Model):
    data = JSONField()
