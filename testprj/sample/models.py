__author__ = 'aldaran'

from django.db import models
from compositekey import db

class Book(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["author", "name"])
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class OldBook(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    #id = db.MultipleFieldPrimaryKey(fields=["author", "name"])
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

#class RealBook(Book):
#    text = models.CharField(max_length=100)

class RealOldBook(OldBook):
    text = models.CharField(max_length=100)

class Library(models.Model):
#    books = models.ManyToManyField(Book)
    name = models.CharField(max_length=100)

class Biografy(models.Model):
#    id = db.MultipleFieldPrimaryKey(fields=["book",])
    book = models.OneToOneField(Book)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)

class OldBiografy(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    book = models.OneToOneField(OldBook)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)

class AbstractChapter(models.Model):
#    id = db.MultipleFieldPrimaryKey(fields=["book", "number"])
    book = models.ForeignKey(Book, to_field="id",
#                             fields_ext={
 #           "author": {"db_column" :"b_author", "name" : "_author"},
 #           "name"  : {"db_column" :"b_name"},
#    },
    related_name="chapter_set")
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s (%s) %s" % (self.book_name, self.number, self._author)

class Chapter(AbstractChapter):
    text = models.CharField(max_length=100)
