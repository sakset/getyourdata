from django import forms

from captcha.fields import ReCaptchaField

import os

class CaptchaForm(forms.Form):
    """
    A simple CAPTCHA form that's disabled during live browser tests
    """
    def __init__(self, *args, **kwargs):
        super(CaptchaForm, self).__init__(*args, **kwargs)

        if not os.environ.get("SELENIUM_TESTS", None) == 'True':
            self.fields["captcha"] = ReCaptchaField()
