from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from data_request.models import DataRequest, AuthenticationContent
from data_request.models import FaqContent, RequestContent
from data_request.models import FeedbackMessageContent


@admin.register(RequestContent)
class RequestContentAdmin(TranslationAdmin):
    list_display = ['title']


@admin.register(FeedbackMessageContent)
class FeedbackMessageContentAdmin(TranslationAdmin):
    list_display = ['name']


@admin.register(FaqContent)
class FaqContentAdmin(TranslationAdmin):
    list_display = ['title', 'priority']
