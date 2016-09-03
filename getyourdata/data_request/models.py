from __future__ import unicode_literals

from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from getyourdata.models import BaseModel
from data_request.services import convert_html_to_pdf
from organization.models import Organization, AuthenticationField

import uuid


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
        help_text=_(
            "Included if user requested a copy of his mail request PDF"))
    footer = models.TextField(blank=True, default="Regards,")


class AuthenticationContent(object):
    """
    A single entry in user's data request

    This is not saved to the database and only exists during the request
    creation process
    """
    def __init__(self, *args, **kwargs):
        self.auth_field = kwargs.get("auth_field", None)
        self.content = kwargs.get("content", None)

    def __unicode__(self):
        return "Authentication content"


class DataRequest(object):
    """
    User's data request to a single organization

    This is not saved to the database and only exists during the request
    creation process
    """
    def __init__(self, *args, **kwargs):
        """
        Create a DataRequest that contains AuthenticationContent objects
        that make up an individual user's data request
        """
        self.auth_contents = kwargs.get("auth_contents", [])
        self.organization = kwargs.get("organization", None)
        self.user_email_address = kwargs.get("user_email_address", None)

        if self.organization is None:
            raise AttributeError("'%s' requires an Organization object as its organization parameter")

    def add_auth_contents(self, *args):
        """
        Add AuthenticationContent(s) to the data request
        """
        for auth_content in args:
             self.auth_contents.append(auth_content)

    def get_auth_content(self, name):
        """
        Get AuthenticationContent by name

        If found, return the AuthenticationContent, otherwise return None
        """
        for auth_content in self.auth_contents:
            if auth_content.auth_field.name == name:
                return auth_content

        return None

    def to_text(self, html=False):
        """
        Return data request as a HTML-formatted document

        :html: If True, return a HTML-formatted document,
               otherwise return the content in plain-text
        """
        person_name = self.get_auth_content("name")

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
        person_name = self.get_auth_content("name")

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
