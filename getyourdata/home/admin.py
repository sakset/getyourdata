from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from home.models import HomePage


@admin.register(HomePage)
class HomePageAdmin(TranslationAdmin):
    list_display = ['admin_name']
