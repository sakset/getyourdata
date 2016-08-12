from modeltranslation.translator import register, TranslationOptions
from data_request.models import FaqContent, RequestContent
from data_request.models import FeedbackMessageContent


@register(RequestContent)
class RequestContentTranslationOptions(TranslationOptions):
    fields = ('header', 'content1', 'content2', 'footer')


@register(FeedbackMessageContent)
class FeedbackMessageContentTranslationOptions(TranslationOptions):
    fields = ('name', 'header', 'pdf_copy', 'footer')


@register(FaqContent)
class FaqContentTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
