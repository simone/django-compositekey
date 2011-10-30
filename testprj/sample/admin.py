from django import forms
from django.forms.models import modelform_factory

__author__ = 'aldaran'

from django.contrib.admin import site, ModelAdmin

from sample.models import Book, Chapter


class MyAdmin(ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        """
        no non mi piace intervenire qui.... bisogna lavorare sulla modelform_factory
        monkey patch credo :-)
        """
        Form = super(MyAdmin, self).get_form(request, obj=obj, **kwargs)
        #class CompositeForm(Form):
        #    book = forms.ModelChoiceField(None)

        return modelform_factory(self.model, form=Form)

    def queryset(self, request):
        print self.model, self.model._default_manager
        return super(MyAdmin, self).queryset(request)


site.register(Book, MyAdmin)
site.register(Chapter, MyAdmin)