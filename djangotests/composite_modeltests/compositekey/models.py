__author__ = 'aldaran'

from django.db import models
from compositekey import db

class Book(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["author", "name"])
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class BookReal(Book):
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"REAL: %s" % unicode(self.book_ptr)

class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book)

    def __unicode__(self):
        return u"Library: %s" % unicode(self.name)


class Biografy(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["book",])
    book = models.OneToOneField(Book)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)

class AbstractChapter(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=["book", "num"])
    book = models.ForeignKey(Book, to_field="id",
        fields_ext={
            "author": {"db_column" :"b_author", "name" : "_author"},
            "name"  : {"db_column" :"b_name"},
        }, related_name="chapter_set")
    num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s (%s) %s" % (self.book_name, self.num, self._author)

class Chapter(AbstractChapter):
    text = models.CharField(max_length=100)


class Auto(models.Model):
    id1 = models.IntegerField()
    id2 = models.CharField(max_length=100)
    id = db.MultipleFieldPrimaryKey(fields=["id1", "id2"])
    fk = models.ForeignKey("self", null=True)
    text = models.TextField()

class RelationAuto(models.Model):
    fk = models.ForeignKey("Auto")
    text = models.TextField()