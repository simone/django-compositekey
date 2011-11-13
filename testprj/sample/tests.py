"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase
from compositekey.utils import *
from sample.models import *
from compositekey.utils import assemble_pk
from django.forms.models import modelform_factory, modelformset_factory

class ModelTest(TestCase):

    def test_get_by_ck(self):
        Book.objects.create(name="Libro sulle compositeKey", author="Simone")
        book = Book.objects.get(name="Libro sulle compositeKey", author="Simone")
        self.assertIsNotNone(book)

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

    def test_select_join_reverse_fk_old(self):
        book = OldBook.objects.create(id="1", name="Libro sulle compositeKey", author="Simone")
        bio = OldBiografy.objects.create(book=book, text="test")
        self.assertIsNotNone(bio.book.oldbiografy)
        list(OldBook.objects.filter(oldbiografy__text="test"))

    def test_select_join_reverse_fk_composite(self):
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

    def test_select_book_chapter_number(self):
        #opts.get_all_field_names
        com_pk = assemble_pk("Libro sulle compositeKey", "Simone")
        book = Book.objects.create(pk=com_pk)
        for n in range(10):
            book.chapter_set.create(number=n)
        list(Book.objects.filter(chapter_set__number=3))


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

    def test_doc_1(self):
        b = Book.objects.create(name="Orgoglio e Pregiudizio", author="Austen")
        self.assertEqual(b.pk, 'Austen-Orgoglio e Pregiudizio')
        c = b.chapter_set.create(number=1, title="Primo", text="Ciao")
        self.assertEqual(c.pk, 'Austen-Orgoglio e Pregiudizio-1')
        b2 = Book.objects.get(pk=b.pk)
        self.assertEqual(b2.pk, 'Austen-Orgoglio e Pregiudizio')
        c2 = Chapter.objects.get(pk=c.pk)
        self.assertEqual(c2.pk, 'Austen-Orgoglio e Pregiudizio-1')
        c3 = b.chapter_set.get(number=1)
        self.assertEqual(c3.pk, 'Austen-Orgoglio e Pregiudizio-1')

    def test_doc_2(self):
        r = BookReal.objects.create(name='REAL', author='Simone', text='9788877873859')
        self.assertEqual(r.pk, 'Simone-REAL')
        self.assertEqual(len(BookReal.objects.filter(pk=r.pk)), 1)
        self.assertEqual(len(Book.objects.filter(pk=r.pk)), 1)
        self.assertEqual(BookReal.objects.get(pk=r.pk).pk, 'Simone-REAL')

    def test_delete_chapters(self):
        b = Book.objects.create(name="Orgoglio e Pregiudizio", author="Delete")
        b.delete()
        self.assertEqual(0, Book.objects.filter(name="Orgoglio e Pregiudizio", author="Delete").count())
        b = Book.objects.create(name="Orgoglio e Pregiudizio", author="Austen")
        self.assertEqual(b.pk, 'Austen-Orgoglio e Pregiudizio')
        c1 = b.chapter_set.create(number=1, title="Primo", text="Ciao")
        c2 = b.chapter_set.create(number=2, title="Secondo", text="Ciao")
        self.assertEqual(c1.pk, 'Austen-Orgoglio e Pregiudizio-1')
        self.assertEqual(c2.pk, 'Austen-Orgoglio e Pregiudizio-2')
        self.assertEqual(2, b.chapter_set.count())
        c1.delete()
        self.assertEqual(1, b.chapter_set.count())


class UtilsTest(TestCase):

    def test_pk(self):
        self.assertEquals(['TEST'], disassemble_pk('TEST'))
        self.assertEquals(['1', '2'], disassemble_pk(assemble_pk("1", "2")))

    def test_empty(self):
        #self.assertEquals(None, assemble_pk(None))
        self.assertEquals(None, assemble_pk(None))#NONE_CHAR
        self.assertEquals('', assemble_pk(''))
        self.assertEquals([], disassemble_pk(None))
        self.assertEquals([''], disassemble_pk(''))

    def test_reversibility(self):
        # '', None, NOT ammissible
        params = ['ab', 'a'+SEP+'b', 'a'+ESCAPE_CHAR+SEP+'b', '123', 'a'+SEP, 'b'+ESCAPE_CHAR, 'c'+ESCAPE_CHAR+SEP, SEP, ESCAPE_CHAR, ESCAPE_CHAR+SEP, SEP+ESCAPE_CHAR, NONE_CHAR , 'd'+ESCAPE_CHAR+SEP]
        self.assertEquals(params, disassemble_pk(assemble_pk(*params)))

    def test_not_reversibility(self):    
        self.assertEquals([], disassemble_pk(assemble_pk(None, '', 'TEST')))


class AdminTest(TestCase):

#    fixtures = ['admin.json']

    def setUp(self):
        pwd = "secret"
        self.u = User.objects.create_user('test_user', '', pwd)
        self.u.is_staff = True
        self.u.is_superuser = True
        self.u.save()
        self.assertTrue(self.client.login(username=self.u.username, password=pwd))

    def tearDown(self):
        self.client.logout()
        self.u.delete()

    def test_book_chapter_inlines(self):
        author = 'Rudolf Steiner'
        name = 'Theosophy'
        b = Book.objects.create(name=name, author=author)
        b.chapter_set.create(text="xontenuyo cap 1", title="cap 1", number=1)

        response = self.client.get('/admin/sample/book/%s/' % b.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b.pk, response.context['object_id'])
        self.assertEqual("Change book", response.context['title'])

        post_data = {
            'name': name,
            'author': author,
            'chapter_set-TOTAL_FORMS': u'0',
            'chapter_set-INITIAL_FORMS': u'0',
            'chapter_set-MAX_NUM_FORMS': u'',
            '_save': 'Save',
        }

        response = self.client.post('/admin/sample/book/%s/' % b.pk, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], 'http://testserver/admin/sample/book/')

        # Don't change nothing, simple try post data:
        post_data.update({
            'chapter_set-TOTAL_FORMS': u'1',
            'chapter_set-0-book': b.pk,
            'chapter_set-0-number': u'',
            'chapter_set-0-title': u'',
            'chapter_set-0-text': u'',
        })
        response = self.client.post('/admin/sample/book/%s/' % b.pk, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], 'http://testserver/admin/sample/book/')


class FormTest(TestCase):

    def test_empty(self):
        FormSet = modelformset_factory(Chapter)
        formset = FormSet({
            'form-TOTAL_FORMS': u'0',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        })
        formset.save()

    def test_one_without_values(self):
        FormSet = modelformset_factory(Chapter)
        formset = FormSet({
            'form-TOTAL_FORMS': u'1',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
            'form-0-book': u'',
            'form-0-number': u'',
            'form-0-title': u'',
            'form-0-text': u'',
        })
        formset.save()
