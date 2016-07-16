from modeltranslation.translator import register, TranslationOptions
from data_request.models import FaqContent, RequestContent


@register(RequestContent)
class RequestContentTranslationOptions(TranslationOptions):
    fields = ('header', 'content1', 'content2', 'footer')


@register(FaqContent)
class FaqContentTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
