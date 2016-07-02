from django import forms
from django.utils.translation import ugettext_lazy as _

from organization.models import Organization, AuthenticationField

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

        for field in authentication_fields:
            authentication_field_choices.append([field.pk, field.title])

        self.fields["authentication_fields"] = forms.MultipleChoiceField(
            choices=authentication_field_choices,
            help_text=_("What authentication fields this organizations requires"))

    class Meta:
        model = Organization
        fields = ORGANIZATION_FIELDS

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
