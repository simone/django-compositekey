__author__ = 'aldaran'

from django.db import models

from compositekey import __future__

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    id = models.CompositeField(author, name, primary_key=True)
    
    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class BookReal(Book):
    author = models.CharField(max_length=100, db_column="b1_author", name="_author")
    name = models.CharField(max_length=100, db_column="b1_name", name="_name")
    book_ptr = models.OneToOneField(Book, parent_link=True, fields=(author, name), primary_key=True)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"REAL: %s" % unicode(self.book_ptr)

class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book, through="BookLibraryM2M")

    def __unicode__(self):
        return u"Library: %s" % unicode(self.name)

class BookLibraryM2M(models.Model):
    book = models.ForeignKey(Book)
    library = models.ForeignKey(Library)
    id = models.CompositeField(book, library, primary_key=True)

    class Meta:
        auto_created = Library

class Biografy(models.Model):
    book = models.OneToOneField(Book, primary_key=True)
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return u"BIO: %s" % unicode(self.book)



class AbstractChapter(models.Model):
    author = models.CharField(max_length=100, db_column="b1_author", name="_author")
    name = models.CharField(max_length=100, db_column="b1_name", name="_name")
    book = models.ForeignKey(Book, fields=(author, name), related_name="chapter_set")
    num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)
    id = models.CompositeField(book, num, primary_key=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u"%s (%s) %s" % (self._name, self.num, self._author)

class Chapter(AbstractChapter):
    text = models.CharField(max_length=100)


class OldBook(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    id = models.CharField(max_length=200, primary_key=True)

    def __unicode__(self):
        return u"%s (by %s)" % (self.name, self.author)

class OldBookReal(OldBook):
    #oldbook_ptr = models.OneToOneField(OldBook, db_column="pippo_ptr", parent_link=True)
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
    books = models.ManyToManyField(OldBook, through="OldLibraryM2M")

    def __unicode__(self):
        return u"Library: %s" % unicode(self.name)

class OldLibraryM2M(models.Model):
    book = models.ForeignKey(OldBook)
    library = models.ForeignKey(OldLibrary)

    class Meta:
        auto_created = OldLibrary

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
    employee_code = models.IntegerField(db_column = 'code')
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    id = models.CompositeField(employee_code, last_name, primary_key=True)
    
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
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    friends = models.ManyToManyField('self', blank=True)
    id = models.CompositeField(name, age, primary_key=True)

    def __unicode__(self):
        return self.name

class OldAuthor(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    friends = models.ManyToManyField('self', blank=True)

    def __unicode__(self):
        return self.name
