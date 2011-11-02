"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from compositekey.utils import *
from sample.models import *


class ModelTest(TestCase):

    def test_select_all(self):
        list(Book.objects.all())
        list(Chapter.objects.all())

    def test_select_where_fk(self):
        book = Book.objects.create(name="Libro sulle compositeKey", author="Simone")
        list(Chapter.objects.filter(book=book))

    def test_select_join_fk(self):
        book = Book.objects.create(name="Libro sulle compositeKey", author="Simone")
        Biografy.objects.create(book=book, text="test")
        list(Biografy.objects.filter(book__author="Simone"))

    def test_select_join_reverse_fk(self):
        book = OldBook.objects.create(id="1", name="Libro sulle compositeKey", author="Simone")
        bio = OldBiografy.objects.create(book=book, text="test")
        self.assertIsNotNone(bio.book.oldbiografy)
        list(OldBook.objects.filter(oldbiografy__text="test"))

        book = Book.objects.create(name="Libro sulle compositeKey", author="Simone")
        bio = Biografy.objects.create(book=book, text="test")
        self.assertIsNotNone(bio.book.biografy)
        list(Book.objects.filter(biografy__text="test", biografy__text__icontains="es", ))

    def test_create_book(self):
        book = Book.objects.create(name="Libro sulle compositeKey", author="Simone")
        self.assertIsNotNone(book)
        book = Book.objects.get(pk=book.pk)
        self.assertIsNotNone(book)

    def test_create_book_from_pk(self):
        com_pk = assemble_pk("Libro sulle compositeKey", "Simone")
        book = Book.objects.create(pk=com_pk)
        self.assertIsNotNone(book)
        book = Book.objects.get(pk=book.pk)
        self.assertIsNotNone(book)

    def test_create_chapter(self):
        chapter = Chapter(number=1, title="Introduzione")
        chapter.book = Book.objects.get_or_create(name="Libro sulla teoria dei colori", author="Simone")[0]
        chapter.save()
        self.assertIsNotNone(chapter)
        self.assertIsNotNone(chapter.book)
        book = Book.objects.get(pk=chapter.book.pk)
        self.assertIsNotNone(book)
        chapter = Chapter.objects.get(pk=chapter.pk)
        self.assertIsNotNone(chapter)

    def test_create_chapter_direct(self):
        chapter = Chapter(number=1, title="Introduzione", book = Book.objects.get_or_create(name="Libro sulla teoria dei colori", author="Simone")[0])
        chapter.save()
        self.assertIsNotNone(chapter)
        self.assertIsNotNone(chapter.book)
        book = Book.objects.get(pk=chapter.book.pk)
        self.assertIsNotNone(book)
        chapter = Chapter.objects.get(pk=chapter.pk)
        self.assertIsNotNone(chapter)

    def test_chapters_book_reverse(self):
        chapter = Chapter(number=1, title="Introduzione", book = Book.objects.get_or_create(name="Libro sulla teoria dei colori", author="Simone")[0])
        chapter.save()
        chapter.book.chapter_set.all()

    def test_create_biografy(self):
        Biografy.objects.create(book=Book.objects.get_or_create(author="Bio", name="Grafy")[0], text="test...")



class UtilsTest(TestCase):

    def test_pk(self):
        self.assertEquals(['TEST'], disassemble_pk('TEST'))
        self.assertEquals(['1', '2'], disassemble_pk(assemble_pk("1", "2")))

    def test_empty(self):
        self.assertEquals(None, assemble_pk(None))
        self.assertEquals('', assemble_pk(''))
        self.assertEquals([], disassemble_pk(None))
        self.assertEquals([''], disassemble_pk(''))

    def test_reveribility(self):
        params = ['ab', 'a'+SEP+'b', 'a'+ESCAPE_CHAR+SEP+'b', '123', 'a'+SEP, 'b'+ESCAPE_CHAR, 'c'+ESCAPE_CHAR+SEP, SEP, ESCAPE_CHAR, ESCAPE_CHAR+SEP, SEP+ESCAPE_CHAR, '', '', 'd'+ESCAPE_CHAR+SEP]
        self.assertEquals(params, disassemble_pk(assemble_pk(*params)))

        # todo: implement with "NONE_CHAR"
        params.append(None)
        self.assertEquals(params, disassemble_pk(assemble_pk(*params)))
        self.assertEquals([None, '', 'TEST'], disassemble_pk(assemble_pk(None, '', 'TEST')))