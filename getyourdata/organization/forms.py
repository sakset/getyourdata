from django import forms
from django.utils.translation import ugettext_lazy as _

class NewOrganizationForm(forms.Form):
    """
    A form used by a visitor to create a new organization

    Either email contact or postal information fields have to be filled, or both
    """
    name = forms.CharField(
        max_length=255,
        required=True,
        label=_("Name"),
        help_text=_("Name of the organization"))

    email_address = forms.EmailField(
        required=False,
        label=_("Email address"),
        help_text=_("Email address used by the organization that responds to user data requests"))

    address_line_one = forms.CharField(
        max_length=255,
        required=False,
        label=_("Address line 1"))

    address_line_two = forms.CharField(
        max_length=255,
        required=False,
        label=_("Address line 2"))

    postal_code = forms.CharField(
        max_length=64,
        required=False,
        label=_("Postal code"))

    country = forms.CharField(
        max_length=64,
        required=False,
        label=_("Country"))

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
