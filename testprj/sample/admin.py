__author__ = 'aldaran'

from django.contrib import admin
from sample.models import Book, Chapter, Biografy, RealBook

class ChapterAdmin(admin.ModelAdmin):
    list_filter = ("book_name", "_author",)

class ChapterInline(admin.TabularInline):
    model = Chapter

class BookAdmin(admin.ModelAdmin):
    list_filter = ("name", "author",)
    inlines = [
        ChapterInline,
    ]

admin.site.register(Book, BookAdmin)
admin.site.register(RealBook)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Biografy)