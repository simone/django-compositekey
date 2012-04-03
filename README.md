Django Composite Key
====================

 * Simone Federici <s.federici@gmail.com> 

Links:
------

 * https://github.com/simone/django-compositekey/
 * https://github.com/simone/django-compositekey/wiki
 * http://pypi.python.org/pypi/django-compositekey/


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
CREATE TABLE "sample_book" (
    "name" varchar(100) NOT NULL,
    "author" varchar(100) NOT NULL,
    UNIQUE ("author", "name")
)
;
CREATE TABLE "sample_bookreal" (
    "book_ptr_name" varchar(100) NOT NULL,
    "book_ptr_author" varchar(100) NOT NULL,
    "text" varchar(100) NOT NULL,
    UNIQUE ("book_ptr_author", "book_ptr_name")
)
;
CREATE TABLE "sample_library_books" (
    "id" integer NOT NULL PRIMARY KEY,
    "book_name" varchar(100) NOT NULL,
    "book_author" varchar(100) NOT NULL,
    "library_id" integer NOT NULL,
    UNIQUE ("library_id", "book_author", "book_name")
)
;
CREATE TABLE "sample_library" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL
)
;
CREATE TABLE "sample_biografy" (
    "book_name" varchar(100) NOT NULL,
    "book_author" varchar(100) NOT NULL,
    "text" varchar(100) NOT NULL,
    UNIQUE ("book_author", "book_name")
)
;
CREATE TABLE "sample_chapter" (
    "b_name" varchar(100) NOT NULL,
    "b_author" varchar(100) NOT NULL,
    "num" smallint unsigned NOT NULL,
    "title" varchar(100) NOT NULL,
    "text" varchar(100) NOT NULL,
    UNIQUE ("b_author", "b_name", "num")
)
;
CREATE INDEX "sample_book_52094d6e" ON "sample_book" ("name");
CREATE INDEX "sample_book_a5d5a658" ON "sample_book" ("author");
CREATE INDEX "sample_bookreal_e0e261c0" ON "sample_bookreal" ("book_ptr_name");
CREATE INDEX "sample_bookreal_53afe146" ON "sample_bookreal" ("book_ptr_author");
CREATE INDEX "sample_biografy_569ae18b" ON "sample_biografy" ("book_name");
CREATE INDEX "sample_biografy_2e675f4b" ON "sample_biografy" ("book_author");
CREATE INDEX "sample_chapter_b333d37b" ON "sample_chapter" ("b_name");
CREATE INDEX "sample_chapter_dacfa8b1" ON "sample_chapter" ("b_author");
CREATE INDEX "sample_chapter_3aac1984" ON "sample_chapter" ("num");
COMMIT;
```