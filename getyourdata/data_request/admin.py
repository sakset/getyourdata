from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from data_request.models import DataRequest, AuthenticationContent, PdfContents, FaqContent


@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    list_display = ['organization', 'created_on']


@admin.register(AuthenticationContent)
class AuthenticationContentAdmin(admin.ModelAdmin):
    list_display = ['auth_field', 'data_request', 'content', 'created_on']


@admin.register(PdfContents)
class PdfContentsAdmin(TranslationAdmin):
    list_display = ['title']


@admin.register(FaqContent)
class FaqContent(TranslationAdmin):
    list_display =['title', 'priority']
