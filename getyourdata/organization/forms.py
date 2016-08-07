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
        fields = ["address_line_one", "postal_code", "country"]

        if form_has_fields(self.cleaned_data, ["email_address"]) or \
            form_has_fields(self.cleaned_data, fields):
            return self.cleaned_data
        else:
            raise forms.ValidationError(
            _("Organization profile must contain either a valid email address or postal information"))


"""
Checks if form has certain fields
"""
def form_has_fields(form, fields):
    for field in fields:
        if not form.get(field):
            return False
    return True

"""
Checks if Authentication fields have been changed
"""
def authentication_fields_has_changes(cleaned_list, original_list):
    if len(cleaned_list) != len(original_list):
       return True

    for members_value in cleaned_list:
        member = AuthenticationField.objects.get(id = int(members_value))
        if member not in original_list:
            return True
    return False

"""
Checks if certain form's fields have been changed
"""
def form_has_changes(changed_organization, organization, fields):
    for field in fields:
        if (changed_organization.get(field) != getattr(organization,field)):
            return True
    return False

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
        Form must contain email address or postal information and have some changes
        """
        authentication_fields_after = self.cleaned_data.get("authentication_fields")
        authentication_fields_before = self.organization.authentication_fields.all()
        fields = ["name", "email_address", "address_line_one", "address_line_two", "postal_code", "country"]
        postal_address_requirements = ["address_line_one", "postal_code", "country","authentication_fields"]

        if not (form_has_fields(self.cleaned_data, ["email_address", "authentication_fields"]) or form_has_fields(self.cleaned_data, postal_address_requirements)):
            raise forms.ValidationError(_("Organization profile must contain either a valid email address or postal information"))

        if  authentication_fields_has_changes(authentication_fields_after, authentication_fields_before) or \
            form_has_changes(self.cleaned_data, self.organization, fields):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("Update form needs some changes for it to be sent!"))


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
            'max_length':_('Maximum allowed length is 2000 characters')
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
