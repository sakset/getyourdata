from __future__ import unicode_literals

from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from getyourdata.models import BaseModel
from data_request.services import convert_html_to_pdf
from organization.models import Organization, AuthenticationField

from tinymce import models as tinymce_models


class RequestContent(BaseModel):
    """
    The text content of a request
    """
    title = models.CharField(max_length=255, default="Default", unique=True)
    header = models.TextField(
        blank=True, default="Dear recipient,")
    content1 = models.TextField(blank=True, default="content first")
    content2 = models.TextField(blank=True, default="content second")
    footer = models.TextField(blank=True, default="Footer here")


class FeedbackMessageContent(BaseModel):
    """
    The text content of an email message sent when user creates any amount
    of data requests
    """
    name = models.TextField(default="Default", unique=True)
    header = models.TextField(
        blank=True, default="Thank you for using [SITE NAME HERE]")
    pdf_copy = models.TextField(
        blank=True, default="A copy of the PDF has been included.",
        help_text=_("Included if user requested a copy of his mail request PDF"))
    footer = models.TextField(blank=True, default="Regards,")


class AuthenticationContent(BaseModel):
    """
    A single entry in user's data request

    This is not saved to the database and only exists during the request
    creation process
    """
    auth_field = models.ForeignKey(AuthenticationField, related_name="+")
    data_request = models.ForeignKey(
        "data_request.DataRequest", related_name="auth_contents")
    content = models.CharField(max_length=255)

    def __unicode__(self):
        return "Authentication content"


class DataRequest(BaseModel):
    """
    User's data request to a single organization

    This is not saved to the database and only exists during the request
    creation process
    """
    organization = models.ForeignKey(
        Organization, related_name="data_requests")

    def to_text(self, html=False):
        """
        Return data request as a HTML-formatted document

        :html: If True, return a HTML-formatted document,
               otherwise return the content in plain-text
        """
        try:
            person_name = self.auth_contents.get(auth_field__name="name")
        except:
            person_name = None

        request_content, created = RequestContent.objects.get_or_create(
            title="Default")

        if html:
            template = "data_request/mail/request.html"
        else:
            template = "data_request/mail_plain/request.html"

        return render_to_string(
            template, {
                "data_request": self,
                "person_name": person_name,
                "request_content": request_content,
                "current_datetime": timezone.now()
            })

    def to_email_body(self):
        """
        Return data request as the text used in the email request
        """
        try:
            person_name = self.auth_contents.get(auth_field__name="name")
        except:
            person_name = None

        request_content, created = RequestContent.objects.get_or_create(
            title="Default")

        return render_to_string(
            "data_request/email_plain/request.html", {
                "data_request": self,
                "request_content": request_content,
                "person_name": person_name
            }
        )

    def to_pdf(self):
        """
        Return data request as a PDF-formatted document
        """
        return convert_html_to_pdf(self.to_text(html=True))

    def __unicode__(self):
        return "Data request for " + self.organization.name
