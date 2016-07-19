from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string

from getyourdata.models import BaseModel

import os


def get_default_content():
    with open(os.path.join(
        settings.BASE_DIR,
        'home/templates/home/default_home_template.html'), 'r') as f:
        return f.read()

class HomePage(BaseModel):
    admin_name = models.CharField(max_length=30, default='default', unique=True)
    content = models.TextField(blank=True, default=get_default_content)

    class Meta:
        verbose_name = 'Home page'
        verbose_name_plural = 'Home page'

    def __unicode__(self):
        return self.admin_name
