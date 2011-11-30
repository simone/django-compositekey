"""
Tests for forcing insert and update queries (instead of Django's normal
automatic behaviour).
"""
from django.db import models
from compositekey import db

class Counter(models.Model):
    x = db.MultipleFieldPrimaryKey(fields=('name','name2'))
    name = models.CharField(max_length = 10)
    name2 = models.CharField(max_length = 10)
    value = models.IntegerField()

class InheritedCounter(Counter):
    tag = models.CharField(max_length=10)

class ProxyCounter(Counter):
    class Meta:
        proxy = True

class SubCounter(Counter):
    pass

class WithCustomPK(models.Model):
    name = models.IntegerField(primary_key=True)
    value = models.IntegerField()
