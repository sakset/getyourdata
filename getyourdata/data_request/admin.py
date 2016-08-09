from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from data_request.models import DataRequest, AuthenticationContent
from data_request.models import FaqContent, RequestContent
from data_request.models import RequestCopyContent


@admin.register(RequestContent)
class RequestContentAdmin(TranslationAdmin):
    list_display = ['title']


@admin.register(RequestCopyContent)
class RequestCopyContentAdmin(TranslationAdmin):
    list_display = ['title']


@admin.register(FaqContent)
class FaqContentAdmin(TranslationAdmin):
    list_display = ['title', 'priority']
