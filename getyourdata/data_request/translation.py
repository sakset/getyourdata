from modeltranslation.translator import register, TranslationOptions
from data_request.models import FaqContent, RequestContent
from data_request.models import RequestCopyContent


@register(RequestContent)
class RequestContentTranslationOptions(TranslationOptions):
    fields = ('header', 'content1', 'content2', 'footer')


@register(RequestCopyContent)
class RequestCopyContentTranslationOptions(TranslationOptions):
    fields = ('title', 'content1', 'content2', 'footer')


@register(FaqContent)
class FaqContentTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
