from django import forms
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.forms.models import model_to_dict
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

        authentication_fields = cache.get("auth_fields_name_title")

        if authentication_fields is None:
            authentication_fields = AuthenticationField.objects.all().only(
                "name", "title")
            cache.set("auth_fields_name_title", authentication_fields)

        authentication_field_choices = []

        for field in authentication_fields:
            authentication_field_choices.append([field.pk, field.title])

        self.fields["authentication_fields"] = forms.MultipleChoiceField(
            choices=authentication_field_choices,
            label=_("Authentication fields"),
            help_text=_("What personal details this organizations requires "
                        "for identifying the customer and for "
                        "responding to data requests. For example: postal "
                        "address, social security number, "
                        "loyalty card number, customer number"))


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

        authentication_fields = cache.get("auth_fields_name_title")

        if authentication_fields is None:
            authentication_fields = AuthenticationField.objects.all().only(
                "name", "title")
            cache.set("auth_fields_name_title", authentication_fields)

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
            help_text=_("What personal details this organizations requires for identifying the customer and for"
                        "responding to data requests. For example: postal address, social security number, "
                        "loyalty card number, customer number"))

    def form_has_changes(self, new_authentication_fields):
        """
        Checks if certain form's fields have been changed

        :new_authentication_fields: A list of authentication field IDs from
                                    Form.cleaned_data
                                    Will be modified by this method as it is
                                    checked
        """
        new_organization_raw = self.cleaned_data

        if not new_organization_raw.get("authentication_fields"):
            raise forms.ValidationError("Authentication fields are required")

        del new_organization_raw["authentication_fields"]
        new_organization = Organization(**new_organization_raw)

        new_authentication_fields = self.normalize_authentication_fields(
            new_authentication_fields)

        new_organization = model_to_dict(new_organization)
        organization = model_to_dict(self.organization)

        del new_organization["id"]
        del organization["id"]
        del new_organization["verified"]
        del organization["verified"]

        new_organization["authentication_fields"] = new_authentication_fields

        return new_organization != organization

    def normalize_authentication_fields(self, authentication_fields):
        """
        Convert a list of IDs into integers and sort them so that they are
        identical to what would be in a Organization instance

        :authentication_fields: A list of authentication field IDs from a
                                Form.cleaned_data
        """
        authentication_fields = [int(field) for field in authentication_fields]
        authentication_fields.sort()

        return authentication_fields

    def clean(self):
        new_authentication_fields = self.cleaned_data.get(
            "authentication_fields")
        if self.form_has_changes(new_authentication_fields):
            self.cleaned_data["authentication_fields"] = self.normalize_authentication_fields(
                new_authentication_fields)
            return self.cleaned_data
        else:
            raise forms.ValidationError(
                "Update form needs some changes for it to be sent!")


class CommentForm(forms.ModelForm):
    """
    Form to submit a public comment
    """
    rating = forms.IntegerField(
        error_messages={
            'required': _('Please leave a rating'),
            'min_value': _('Please leave a rating')
        },
        label=_('Rating'),
        required=True,
        min_value=1,
        max_value=5,

    )
    message = forms.CharField(
        error_messages={
            'required': _('Message is required'),
            'max_length': _('Maximum allowed length is 2000 characters')
        },
        label=_('Message'),
        max_length=2000,
        required=True,
    )

    class Meta:
        model = Comment
        fields = ['rating', 'message']
        labels = {
            'rating': _('Rating'),
            'message': _('Message'),
        }
