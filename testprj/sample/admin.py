__author__ = 'aldaran'

from django.contrib import admin
from sample.models import *

class ChapterAdmin(admin.ModelAdmin):
    list_filter = ("book__name", "book__author",)

class ChapterInline(admin.TabularInline):
    model = Chapter

class OldChapterInline(admin.TabularInline):
    model = OldChapter

class BookAdmin(admin.ModelAdmin):
    list_filter = ("name", "author",)
    inlines = [
        ChapterInline,
    ]
class OldBookAdmin(admin.ModelAdmin):
    list_filter = ("name", "author",)
    inlines = [
        OldChapterInline,
    ]

admin.site.register(Book, BookAdmin)
admin.site.register(BookReal)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Biografy)
admin.site.register(Library)

admin.site.register(OldBook, OldBookAdmin)
admin.site.register(OldBookReal)
admin.site.register(OldChapter, ChapterAdmin)
admin.site.register(OldBiografy)
admin.site.register(OldLibrary)

admin.site.register(Author)

