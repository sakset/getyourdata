from modeltranslation.translator import register, TranslationOptions

from django.contrib.flatpages.models import FlatPage


@register(FlatPage)
class FlatPageTranslationOptions(TranslationOptions):
    fields = ('content', 'title')
