from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.template.loader import render_to_string

from tinymce import models as tinymce_models

from getyourdata.models import BaseModel


class HomePageManager(models.Manager):
    def create_default(self):
        """
        Create default home pages
        """
        home_page = HomePage()

        for lang_code, lang_name in settings.LANGUAGES:
            setattr(
                home_page, "content_%s" % lang_code,
                render_to_string(
                    "home/default.html", {"lang_code": lang_code}))

        home_page.save()
        return home_page


def get_default_content():
    return ""


class HomePage(BaseModel):
    admin_name = models.CharField(
        max_length=30, default='default', unique=True)
    content = tinymce_models.HTMLField(blank=True, default=get_default_content)

    objects = HomePageManager()

    class Meta:
        verbose_name = 'Home page'
        verbose_name_plural = 'Home page'

    def __unicode__(self):
        return self.admin_name


class FaqContent(BaseModel):
    title = models.CharField(
        max_length=75,
        default="")

    priority = models.IntegerField(default=777)

    content = tinymce_models.HTMLField(blank=True, default='')
