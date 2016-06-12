from django.contrib import admin

from home.models import HomePage


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ['admin_name']
