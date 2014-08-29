Django Composite Key
====================

Allows to use Django with (legacy) databases that have composite multicolumn primary keys and multiple foreignkeys.


NOTE:
=====
MASTER is not "STABLE"


Version 1.6 is in development
=============================

 * For django 1.4.x compatibility checkout the 1.4.x stable branch
 * For django 1.5.x compatibility checkout the 1.5.x stable branch

Author
------

 * Simone Federici <s.federici@gmail.com> 

Links:
------

 * https://github.com/simone/django-compositekey/
 * https://github.com/simone/django-compositekey/wiki
 * http://pypi.python.org/pypi/django-compositekey/

Running the Test Suite
----------------------

Clone the django-compositekey repository (in case you havn't done this already):

    $ git clone git://github.com/simone/django-compositekey.git

Checkout the Git Submodule containing Django:

    $ cd django-compositekey
    django-compositekey$ git submodule init
    django-compositekey$ git submodule update

Update the Django clone to the version you want to test with:

    django-compositekey$ cd django_src
    django-compositekey/django_src$ git checkout stable/1.6
    django-compositekey$ cd ..

Create a new [virtualenv](http://www.virtualenv.org/) for the project and activate it.

Now install `django-compositekey` inside the virtualenv:

    (django-compositekey) django-compositekey$ pip install --editable .

And install Django too:

    (django-compositekey) django-compositekey$ cd django_src
    (django-compositekey) django-compositekey/django_src$ pip install --editable .
    (django-compositekey) django-compositekey$ cd ..

Use the `Makefile` to run the composite test suite:

    (django-compositekey) django-compositekey$ make test-composite

Composite PK
------------
```python
from django.db import models
from compositekey import db

class Book(models.Model):
    id = db.MultiFieldPK("author", "name")
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
```

Inheritance
-----------
```python
class BookReal(Book):
    text = models.CharField(max_length=100)
```

Many To Many 
------------
```python
class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book)
```

One To One + Composite PK related
---------------------------------
```python
class Biografy(models.Model):
    id = db.MultiFieldPK("book")
    book = models.OneToOneField(Book)
    text = models.CharField(max_length=100)
```

Abstract ForeignKey + field extensions syntax
---------------------------------------------
```python
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
```

ForeignKey Implementation
-------------------------
```python
class Chapter(AbstractChapter):
    text = models.CharField(max_length=100)
```

SQLALL sqlite example
---------------------
```sql
BEGIN;
CREATE TABLE "sample_book" (
    "name" varchar(100) NOT NULL,
    "author" varchar(100) NOT NULL,
    UNIQUE ("author", "name"),
    PRIMARY KEY ("author", "name")
)
;
CREATE TABLE "sample_bookreal" (
    "book_ptr_name" varchar(100) NOT NULL,
    "book_ptr_author" varchar(100) NOT NULL,
    "text" varchar(100) NOT NULL,
    UNIQUE ("book_ptr_author", "book_ptr_name"),
    FOREIGN KEY ("book_ptr_author", "book_ptr_name") REFERENCES sample_book ("author", "name")
)
;
CREATE TABLE "sample_library_books" (
    "id" serial NOT NULL PRIMARY KEY,
    "book_name" varchar(100) NOT NULL,
    "book_author" varchar(100) NOT NULL,
    "library_id" integer NOT NULL,
    UNIQUE ("library_id", "book_author", "book_name"),
    FOREIGN KEY ("book_author", "book_name") REFERENCES sample_book ("author", "name")
)
;
CREATE TABLE "sample_library" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL
)
;
ALTER TABLE "sample_library_books" ADD CONSTRAINT "library_id_refs_id_646b9dae" FOREIGN KEY ("library_id") REFERENCES "sample_library" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "sample_biografy" (
    "book_name" varchar(100) NOT NULL,
    "book_author" varchar(100) NOT NULL,
    "text" varchar(100) NOT NULL,
    UNIQUE ("book_author", "book_name"),
    PRIMARY KEY ("book_author", "book_name"),
    FOREIGN KEY ("book_author", "book_name") REFERENCES sample_book ("author", "name")
)
;
CREATE TABLE "sample_chapter" (
    "b_name" varchar(100) NOT NULL,
    "b_author" varchar(100) NOT NULL,
    "num" smallint CHECK ("num" >= 0) NOT NULL,
    "title" varchar(100) NOT NULL,
    "text" varchar(100) NOT NULL,
    UNIQUE ("b_author", "b_name", "num"),
    PRIMARY KEY ("b_author", "b_name", "num"),
    FOREIGN KEY ("b_author", "b_name") REFERENCES sample_book ("author", "name")
)
;
CREATE TABLE "sample_employee" (
    "code" integer NOT NULL,
    "first_name" varchar(20) NOT NULL,
    "last_name" varchar(20) NOT NULL,
    UNIQUE ("code", "last_name"),
    PRIMARY KEY ("code", "last_name")
)
;
CREATE TABLE "sample_business_employees" (
    "id" serial NOT NULL PRIMARY KEY,
    "employee_code" integer NOT NULL,
    "employee_last_name" varchar(20) NOT NULL,
    "business_id" varchar(20) NOT NULL,
    UNIQUE ("business_id", "employee_code", "employee_last_name"),
    FOREIGN KEY ("employee_code", "employee_last_name") REFERENCES sample_employee ("code", "last_name")
)
;
CREATE TABLE "sample_business" (
    "name" varchar(20) NOT NULL PRIMARY KEY
)
;
ALTER TABLE "sample_business_employees" ADD CONSTRAINT "business_id_refs_name_2205e04d" FOREIGN KEY ("business_id") REFERENCES "sample_business" ("name") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "sample_author_friends" (
    "id" serial NOT NULL PRIMARY KEY,
    "from_author_name" varchar(100) NOT NULL,
    "to_author_name" varchar(100) NOT NULL,
    "from_author_age" integer NOT NULL,
    "to_author_age" integer NOT NULL,
    UNIQUE ("from_author_name", "from_author_age", "to_author_name", "to_author_age")
)
;
CREATE TABLE "sample_author" (
    "name" varchar(100) NOT NULL,
    "age" integer NOT NULL,
    UNIQUE ("name", "age"),
    PRIMARY KEY ("name", "age")
)
;
ALTER TABLE "sample_author_friends" ADD CONSTRAINT "from_author_name_from_author_age_refs_name_age_7b9b87e7" FOREIGN KEY ("from_author_name", "from_author_age") REFERENCES "sample_author" ("name", "age") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "sample_author_friends" ADD CONSTRAINT "to_author_name_to_author_age_refs_name_age_7b9b87e7" FOREIGN KEY ("to_author_name", "to_author_age") REFERENCES "sample_author" ("name", "age") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "sample_book_name" ON "sample_book" ("name");
CREATE INDEX "sample_book_name_like" ON "sample_book" ("name" varchar_pattern_ops);
CREATE INDEX "sample_book_author" ON "sample_book" ("author");
CREATE INDEX "sample_book_author_like" ON "sample_book" ("author" varchar_pattern_ops);
CREATE INDEX "sample_bookreal_book_ptr_name" ON "sample_bookreal" ("book_ptr_name");
CREATE INDEX "sample_bookreal_book_ptr_name_like" ON "sample_bookreal" ("book_ptr_name" varchar_pattern_ops);
CREATE INDEX "sample_bookreal_book_ptr_author" ON "sample_bookreal" ("book_ptr_author");
CREATE INDEX "sample_bookreal_book_ptr_author_like" ON "sample_bookreal" ("book_ptr_author" varchar_pattern_ops);
CREATE INDEX "sample_biografy_book_name" ON "sample_biografy" ("book_name");
CREATE INDEX "sample_biografy_book_name_like" ON "sample_biografy" ("book_name" varchar_pattern_ops);
CREATE INDEX "sample_biografy_book_author" ON "sample_biografy" ("book_author");
CREATE INDEX "sample_biografy_book_author_like" ON "sample_biografy" ("book_author" varchar_pattern_ops);
CREATE INDEX "sample_chapter_b_name" ON "sample_chapter" ("b_name");
CREATE INDEX "sample_chapter_b_name_like" ON "sample_chapter" ("b_name" varchar_pattern_ops);
CREATE INDEX "sample_chapter_b_author" ON "sample_chapter" ("b_author");
CREATE INDEX "sample_chapter_b_author_like" ON "sample_chapter" ("b_author" varchar_pattern_ops);
CREATE INDEX "sample_chapter_num" ON "sample_chapter" ("num");
CREATE INDEX "sample_employee_code" ON "sample_employee" ("code");
CREATE INDEX "sample_employee_last_name" ON "sample_employee" ("last_name");
CREATE INDEX "sample_employee_last_name_like" ON "sample_employee" ("last_name" varchar_pattern_ops);
CREATE INDEX "sample_author_name" ON "sample_author" ("name");
CREATE INDEX "sample_author_name_like" ON "sample_author" ("name" varchar_pattern_ops);
CREATE INDEX "sample_author_age" ON "sample_author" ("age");
COMMIT;


```
EUROPYTHON 2012 Support for Future API of CompositeField 
=====================================


Composite PK
------------
```python
from django.db import models
from compositekey import __future__

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    id = models.CompositeField(author, name, primary_key=True)
```

Inheritance
-----------
```python
class BookReal(Book):
    text = models.CharField(max_length=100)
```

Many To Many 
------------
```python
class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book)
```

One To One + Composite PK related
---------------------------------
```python
class Biografy(models.Model):
    book = models.OneToOneField(Book)
    text = models.CharField(max_length=100)
    id = models.ComositeField(book, primary_key=True)
```

Abstract ForeignKey + field extensions syntax
---------------------------------------------
```python

class AbstractChapter(models.Model):
    author = models.CharField(max_length=100, db_column="b1_author", name="_author")
    name = models.CharField(max_length=100, db_column="b1_name", name="_name")
    book = models.ForeignKey(Book, fields=(author, name), related_name="chapter_set")
    num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)
    id = models.CompositeField(book, num, primary_key=True)

    class Meta:
        abstract = True
```

Customize the ManyToMany Intermediate Model/Table
-------------------------
```python
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
```
