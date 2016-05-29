from django.contrib import admin

from data_request.models import DataRequest, AuthenticationContent


@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    list_display = ['organization']


@admin.register(AuthenticationContent)
class AuthenticationContentAdmin(admin.ModelAdmin):
    list_display = ['auth_field', 'data_request', 'content']