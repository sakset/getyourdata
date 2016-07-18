from __future__ import unicode_literals

from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'
    def ready(self):
        HomePage = self.get_model('HomePage')
        page, created = HomePage.objects.get_or_create()