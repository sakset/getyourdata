from django.contrib import admin

from data_request.models import DataRequest, AuthenticationContent
from data_request.models import FaqContent, RequestContent


@admin.register(RequestContent)
class RequestContentAdmin(admin.ModelAdmin):
    list_display = ["title"]


@admin.register(FaqContent)
class FaqContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority']
