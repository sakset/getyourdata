from django import forms
from django.utils.translation import ugettext_lazy as _

from feedback.models import ServiceFeedback


class NewFeedbackForm(forms.ModelForm):
    content = forms.CharField(
        error_messages={
            'required': _('Message is required'),
            'max_length': _('Maximum allowed length is 4096 characters')
        },
        label=_('Message'),
        max_length=4096,
        required=True,
    )

    class Meta:
        model = ServiceFeedback
        fields = ["content"]
