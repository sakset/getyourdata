from modeltranslation.translator import register, TranslationOptions

from home.models import HomePage


@register(HomePage)
class HomePageTranslationOptions(TranslationOptions):
    fields = ('content',)