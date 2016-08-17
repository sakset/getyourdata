from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from captcha.fields import ReCaptchaField

from data_request.models import DataRequest


class AuthenticationAttributeField(forms.CharField):
    """
    A helper field to be used for authentication fields in DataRequestForm
    """
    def __init__(self, *args, **kwargs):
        super(AuthenticationAttributeField, self).__init__(*args, **kwargs)

    def clean(self, value):
        try:
            super(AuthenticationAttributeField, self).clean(value)
        except ValidationError:
            raise ValidationError(_("The value for this field was not valid"))

        return value


class DataRequestForm(forms.Form):
    """
    Data request form filled with required authentication fields in order
    to send a data request to each selected organization
    """

    def __init__(self, *args, **kwargs):
        self.organizations = kwargs.pop('organizations', None)
        self.visible = kwargs.pop('visible', True)

        self.contains_email_requests = False
        self.contains_mail_requests = False

        super(DataRequestForm, self).__init__(*args, **kwargs)

        if not self.organizations:
            raise AttributeError("'%s' requires a list of Organization objects as 'organizations'")

        for organization in self.organizations:
            if organization.accepts_email:
                self.contains_email_requests = True
            if organization.accepts_mail and not organization.accepts_email:
                self.contains_mail_requests = True

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
                    required=True,
                    widget=forms.TextInput(attrs={"placeholder": ""}))

        self.fields["user_email_address"] = forms.EmailField(
            label=_("Receiving email address"),
            help_text=_(
                "Optional - A copy of your mail requests can be sent to "
                "this email address if filled"),
            required=False,
            widget=forms.TextInput(attrs={"placeholder": ""}))

        # If user is creating only mail requests, we don't need a
        # checkbox when user wants a copy of his PDF; just entering
        # the email address is enough
        if self.contains_mail_requests:
            self.fields["send_mail_request_copy"] = forms.BooleanField(
                label=_("Send a copy of mail requests"),
                initial=False,
                help_text=_(
                    "If checked, a copy of your mail requests will be "
                    "sent to the receiving email address"),
                required=False)

        if self.contains_email_requests:
            self.fields["user_email_address"].help_text = _(
                "Your data and further enquiries by organizations will be sent to this address")
            self.fields["user_email_address"].required = True

        # Make the fields invisible if needed
        if not self.visible:
            for name, field in self.fields.iteritems():
                self.fields[name].widget = forms.HiddenInput()

    def clean(self):
        """
        If user has checked 'send mail request copy to email' but hasn't entered
        an email address, throw an error
        """
        cleaned_data = super(DataRequestForm, self).clean()

        # If user is creating only mail requests and wants a copy of his requests
        # to his email address, require that email address is provided
        if self.contains_mail_requests:
            if cleaned_data.get("send_mail_request_copy", False) and \
                    not cleaned_data.get("user_email_address", None):
                self.add_error("user_email_address", "\n%s" % _(
                    "You must enter a receiving email address if you want a "
                    "copy of your mail requests as an email message."))


class OrganizationRatingForm(forms.Form):
    """
    A form for posting ratings and comments (feedback) regarding organizations
    """

    def __init__(self, *args, **kwargs):
        self.organizations = kwargs.pop('organizations', None)

        super(OrganizationRatingForm, self).__init__(*args, **kwargs)

        # organization IDs shall be passed as POST variable
        org_ids = [str(organization.id) for organization in self.organizations]
        org_ids = ",".join(org_ids)

        self.fields['org_ids'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=org_ids,
        )

        for organization in self.organizations:
            self.fields['rating_%i' % organization.id] = forms.IntegerField(
                error_messages={
                    'required': _('Please leave a rating'),
                    'min_value': _('Please leave a rating')
                },
                label=_('Rating'),
                required=False,
                min_value=1,
                max_value=5,
            )

            self.fields['message_%i' % organization.id] = forms.CharField(
                error_messages={
                    'required': _('Message is required'),
                    'max_length': _('Maximum allowed length is 2000 characters')
                },
                label=_('Message'),
                max_length=2000,
                required=False,
            )


    def clean(self):
        cleaned_data = super(OrganizationRatingForm, self).clean()

        # we'll loop through the organizations included in the form (org_ids form field)
        # and see which ones have been rated
        for organization in self.organizations:
            rating_key = "rating_%s" % organization.id
            message_key = "message_%s" % organization.id

            # if a rating was given, we'll make sure that there shall also be a message,
            # otherwise an error message is displayed
            if rating_key in cleaned_data:
                if cleaned_data.get(rating_key) != 0 and (not cleaned_data.get(message_key) or
                                                              cleaned_data.get(message_key).isspace()):
                    self.add_error(message_key, _('Message is required'))
                    # the rating and organization id shall be removed from the list of valid input
                    cleaned_data.pop(rating_key, None)

        return cleaned_data
