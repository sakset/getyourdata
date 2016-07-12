from django import forms
from django.utils.translation import ugettext_lazy as _

from organization.models import Organization, AuthenticationField, Comment

from captcha.fields import ReCaptchaField

ORGANIZATION_FIELDS = [
    "name", "email_address", "address_line_one",
    "address_line_two", "postal_code", "country",
]


class NewOrganizationForm(forms.ModelForm):
    """
    A form used by a visitor to create a new organization

    Either email contact or postal information fields have to be filled, or both
    """
    class Meta:
        model = Organization
        fields = ORGANIZATION_FIELDS

    def __init__(self, *args, **kwargs):
        super(NewOrganizationForm, self).__init__(*args, **kwargs)

        authentication_fields = AuthenticationField.objects.all().only(
            "name", "title")

        authentication_field_choices = []

        for field in authentication_fields:
            authentication_field_choices.append([field.pk, field.title])

        self.fields["authentication_fields"] = forms.MultipleChoiceField(
            choices=authentication_field_choices,
            label=_("Authentication fields"),
            help_text=_("What authentication fields this organizations requires"))

    def clean(self):
        """
        Form must contain email address or postal information
        """
        if self.cleaned_data.get("email_address"):
            return self.cleaned_data

        if self.cleaned_data.get("address_line_one") and \
           self.cleaned_data.get("postal_code") and \
           self.cleaned_data.get("country"):
            return self.cleaned_data

        raise forms.ValidationError(
            _("Organization profile must contain either a valid email address or postal information"))


class EditOrganizationForm(forms.ModelForm):
    """
    A form to edit an existing organization and to save it as a draft
    """
    class Meta:
        model = Organization
        fields = ORGANIZATION_FIELDS

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super(EditOrganizationForm, self).__init__(*args, **kwargs)

        if not self.organization:
            raise AttributeError(
                "'%s' requires an existing Organization as 'organization'")

        for field in ORGANIZATION_FIELDS:
            self.fields[field].initial = getattr(self.organization, field)

        authentication_fields = AuthenticationField.objects.all().only(
            "name", "title")

        authentication_field_choices = []
        selected_field_choices = []

        for field in authentication_fields:
            authentication_field_choices.append([field.pk, field.title])

        for field in self.organization.authentication_fields.all():
            selected_field_choices.append(field.pk)

        self.fields["authentication_fields"] = forms.MultipleChoiceField(
            initial=selected_field_choices,
            choices=authentication_field_choices,
            label=_("Authentication fields"),
            help_text=_("What authentication fields this organizations requires"))


    def clean(self):
        """
        Form must contain email address or postal information
        """
        if self.cleaned_data.get("email_address"):
            return self.cleaned_data

        if self.cleaned_data.get("address_line_one") and \
           self.cleaned_data.get("postal_code") and \
           self.cleaned_data.get("country"):
            return self.cleaned_data

        raise forms.ValidationError(
            _("Organization profile must contain either a valid email address or postal information"))


class CommentForm(forms.ModelForm):
    """
    Form to submit a public comment
    """
    rating = forms.IntegerField(error_messages={
        'required': _('Please leave a rating'),
        'min_value': _('Please leave a rating')
    })
    message = forms.CharField(error_messages={
        'required': _('Message is required')
    })

    captcha = ReCaptchaField()

    class Meta:
        model = Comment
        fields = ['rating', 'message']
        labels = {
            'rating': _('Rating'),
            'message': _('Message'),
        }
