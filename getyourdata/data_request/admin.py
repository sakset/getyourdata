from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from data_request.models import DataRequest, AuthenticationContent
from data_request.models import FaqContent, RequestContent


@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    list_display = ['organization', 'created_on']


@admin.register(AuthenticationContent)
class AuthenticationContentAdmin(admin.ModelAdmin):
    list_display = ['auth_field', 'data_request', 'content', 'created_on']


@admin.register(RequestContent)
class RequestContentAdmin(TranslationAdmin):
    list_display = ['title']


@admin.register(FaqContent)
class FaqContentAdmin(TranslationAdmin):
    list_display = ['title', 'priority']
