__author__ = 'aldaran'

from django.db import models
from compositekey import db

__all__ = ["Book", "Chapter"]

class Book(models.Model):
    key = db.MultipleFieldPrimaryKey(fields=["author", "name"])
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    objects = db.CompositeDefaultManager()

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class Chapter(models.Model):
    key = db.MultipleFieldPrimaryKey(fields=["number", "title"])
    book = db.CompositeForeignKey(Book, to_field="key", fields_ext={
            "author": {"db_column" :"b_author"},
            "name"  : {"db_column" :"b_name"},
    })
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)

    objects = db.CompositeDefaultManager()
    
    def __unicode__(self):
        return u"* %s ) %s" % (self.number, self.book_name)


