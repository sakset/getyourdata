from modeltranslation.translator import register, TranslationOptions

from home.models import HomePage, FaqContent


@register(HomePage)
class HomePageTranslationOptions(TranslationOptions):
    fields = ('content',)


@register(FaqContent)
class FaqContentTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
