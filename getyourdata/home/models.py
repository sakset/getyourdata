from __future__ import unicode_literals

from django.db import models
from django.template.loader import render_to_string

from tinymce import models as tinymce_models

from getyourdata.models import BaseModel


def get_default_content():
    return render_to_string('home/default.html', {})

class HomePage(BaseModel):
    admin_name = models.CharField(max_length=30, default='default', unique=True)
    content = tinymce_models.HTMLField(blank=True, default=get_default_content)

    def __unicode__(self):
        return self.admin_name
