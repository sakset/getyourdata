from modeltranslation.translator import register, TranslationOptions
from data_request.models import RequestContent
from data_request.models import FeedbackMessageContent


@register(RequestContent)
class RequestContentTranslationOptions(TranslationOptions):
    fields = ('header', 'content1', 'content2', 'content3', 'footer')


@register(FeedbackMessageContent)
class FeedbackMessageContentTranslationOptions(TranslationOptions):
    fields = ('name', 'header', 'pdf_copy', 'footer')
