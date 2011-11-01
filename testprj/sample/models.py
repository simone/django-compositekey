__author__ = 'aldaran'

from django.db import models
from compositekey import db

#__all__ = ["Book", "Chapter", "Biografy"]

class Book(models.Model):
    #id = models.CharField(max_length=200, primary_key=True)
    id = db.MultipleFieldPrimaryKey(fields=["author", "name"])
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    #objects = db.CompositeDefaultManager()

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

#class RealBook(Book):
#    text = models.CharField(max_length=100)

#class Library(models.Model):
#    books = models.ManyToManyField(Book)

class Biografy(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["book",])
    #id = models.CharField(max_length=200, primary_key=True)
    book = db.CompositeOneToOneField(Book)
    #book = models.OneToOneField(Book)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)

class MyManager(db.CompositeDefaultManager):
    pass


class AbstractChapter(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["book", "number"])
    #id = models.CharField(max_length=200, primary_key=True)
    #book = models.ForeignKey(Book, related_name="chapter_set")
    book = db.CompositeForeignKey(Book, to_field="id", fields_ext={
            "author": {"db_column" :"b_author", "name" : "_author"},
            "name"  : {"db_column" :"b_name"},
    }, related_name="chapter_set")
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        #ordering = ["book_name",]
        abstract = True

    def __unicode__(self):
        return u"%s (%s) %s" % (self.book_name, self.number, self._author)


class Chapter(AbstractChapter):
    text = models.CharField(max_length=100)
    objects = MyManager()