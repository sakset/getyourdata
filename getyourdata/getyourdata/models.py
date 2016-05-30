from django.db import models

from django_extensions.db.fields import (CreationDateTimeField,
    ModificationDateTimeField)


class BaseModel(models.Model):
    created_on = CreationDateTimeField('Created on')
    updated_on = ModificationDateTimeField('Updated on')

    class Meta:
        abstract = True