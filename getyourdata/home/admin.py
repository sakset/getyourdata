from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from home.models import HomePage, FaqContent


@admin.register(HomePage)
class HomePageAdmin(TranslationAdmin):
    list_display = ['admin_name']


@admin.register(FaqContent)
class FaqContentAdmin(TranslationAdmin):
    list_display = ['title', 'priority']
