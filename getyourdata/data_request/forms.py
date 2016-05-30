from django import forms
from django.utils.translation import ugettext_lazy as _

from data_request.models import DataRequest


class DataRequestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization')
        super(DataRequestForm, self).__init__(*args, **kwargs)
        for auth_field in self.organization.authentication_fields.all():
            self.fields[auth_field.name] = forms.CharField(
                label=auth_field.name,
                max_length=255,
                required=True
                )
