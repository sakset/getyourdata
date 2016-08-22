from django.template.defaultfilters import truncatechars
from django.db import models

from getyourdata.models import BaseModel


class ServiceFeedback(BaseModel):
    content = models.TextField(max_length=4096)

    origin_url = models.TextField(max_length=512)

    @property
    def short_content(self):
        return truncatechars(self.content, 500)
