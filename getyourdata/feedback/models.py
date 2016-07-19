from getyourdata.models import BaseModel
from django.db import models


class ServiceFeedback(BaseModel):
    content = models.TextField(max_length=4096)
