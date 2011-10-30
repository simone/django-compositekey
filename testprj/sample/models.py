__author__ = 'aldaran'

from django.db import models
from compositekey import db

__all__ = ["Book", "Chapter"]

class Book(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["author", "name"])
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    objects = db.CompositeDefaultManager()

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class Chapter(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["book", "number"])
    book = db.CompositeForeignKey(Book, to_field="id", fields_ext={
            "author": {"db_column" :"b_author", "name" : "_author"},
            "name"  : {"db_column" :"b_name"},
    })
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)

    objects = db.CompositeDefaultManager()

#    class Meta:
#        ordering = ["book_name",]

    def __unicode__(self):
        return u"%s (%s) %s" % (self.book_name, self.number, self._author)


