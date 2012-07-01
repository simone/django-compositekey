__author__ = 'aldaran'

from django.db import models
from compositekey import db

class Book(models.Model):
    id = db.MultiFieldPK("author", "name")
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
    id = db.MultiFieldPK("book")
    book = models.OneToOneField(Book)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)

class AbstractChapter(models.Model):
    id = db.MultiFieldPK("book", "num")
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


class OldBook(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class OldBookReal(OldBook):
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"REAL: %s" % unicode(self.oldbook_ptr)

class OldBiografy(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    book = models.OneToOneField(OldBook)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)

class OldLibrary(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(OldBook)

    def __unicode__(self):
        return u"Library: %s" % unicode(self.name)

class AbstractOldChapter(models.Model):
    book = models.ForeignKey(OldBook, to_field="id")
    num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s (%s) %s" % (self.book.name, self.num, self.book.author)

class OldChapter(AbstractOldChapter):
    text = models.CharField(max_length=100)

class Employee(models.Model):
    id = db.MultiFieldPK("employee_code", "last_name")
    employee_code = models.IntegerField(db_column = 'code')
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    class Meta:
        ordering = ('last_name', 'first_name')

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

class Business(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    employees = models.ManyToManyField(Employee)
    class Meta:
        verbose_name_plural = 'businesses'

    def __unicode__(self):
        return self.name

class Author(models.Model):
    id = db.MultiFieldPK("name","age")
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    friends = models.ManyToManyField('self', blank=True)

    def __unicode__(self):
        return self.name