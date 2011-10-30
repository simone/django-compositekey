__author__ = 'aldaran'

from django.contrib.admin import site, ModelAdmin
from sample.models import Book, Chapter

class BookAdmin(ModelAdmin):
    list_filter = ("name", "author",)

class ChapterAdmin(ModelAdmin):
    list_filter = ("book_name", "book_author",)

site.register(Book, BookAdmin)
site.register(Chapter, ChapterAdmin)