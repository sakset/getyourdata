from __future__ import unicode_literals

from django.apps import AppConfig


class DataRequestConfig(AppConfig):
    name = 'data_request'
    verbose_name = 'Data requests'

    def ready(self):
        """
        Deleting all user related data. Just in case.
        """
        from data_request.models import AuthenticationContent, DataRequest
        AuthenticationContent.objects.all().delete()
        DataRequest.objects.all().delete()
