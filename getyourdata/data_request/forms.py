from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from data_request.models import DataRequest


class AuthenticationAttributeField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(AuthenticationAttributeField, self).__init__(*args, **kwargs)

    def clean(self, value):
        try:
            super(AuthenticationAttributeField, self).clean(value)
        except ValidationError:
            self.help_text = ""
            raise ValidationError(_("The value for this field was not valid"))

        return value


class DataRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.organizations = kwargs.pop('organizations', None)
        self.contains_email_requests = False
        super(DataRequestForm, self).__init__(*args, **kwargs)

        if not self.organizations:
            raise AttributeError("'%s' requires a list of Organization objects as 'organizations'")

        for organization in self.organizations:
            if organization.accepts_email:
                self.contains_email_requests = True

            for auth_field in organization.authentication_fields.all():
                # Only add each authentication field once
                if auth_field.name in self.fields:
                    continue

                validators = []

                if auth_field.validator_regex != "":
                    validators = [RegexValidator(
                        auth_field.validator_regex,
                        message=_("The value for this field was not valid"))]

                self.fields[auth_field.name] = AuthenticationAttributeField(
                    label=auth_field.title,
                    help_text=auth_field.help_text,
                    max_length=255,
                    validators=validators,
                    required=True)

        # If user is making at least one email request, we'll need his email address
        # as well
        if self.contains_email_requests:
            self.fields["user_email_address"] = forms.EmailField(
                label=_("Sender email address"),
                help_text=_("Your data and further enquiries by organizations will be sent to this address"),
                required=True)
