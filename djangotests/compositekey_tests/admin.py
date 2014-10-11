__author__ = 'aldaran'

from django.contrib import admin
from .models import *

class ChapterAdmin(admin.ModelAdmin):
    list_filter = ("book__name", "book__author",)

class ChapterInline(admin.TabularInline):
    model = Chapter

class BookAdmin(admin.ModelAdmin):
    list_filter = ("name", "author",)
    inlines = [
        ChapterInline,
    ]

site = admin.AdminSite(name="admin")

site.register(Book, BookAdmin)
site.register(BookReal)
site.register(Chapter, ChapterAdmin)
site.register(Biografy)
site.register(Library)
