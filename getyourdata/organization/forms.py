from django import forms
from django.utils.translation import ugettext_lazy as _

from organization.models import Organization

class NewOrganizationForm(forms.ModelForm):
    """
    A form used by a visitor to create a new organization

    Either email contact or postal information fields have to be filled, or both
    """
    class Meta:
        model = Organization
        fields = [
            "name", "email_address", "address_line_one",
            "address_line_two", "postal_code", "country"
        ]

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
