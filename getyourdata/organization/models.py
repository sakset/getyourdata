from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from getyourdata.models import BaseModel


class AuthenticationField(BaseModel):
    # The canonical name of the field (NOT TRANSLATED!)
    name = models.CharField(max_length=255, unique=True, db_index=True)

    # Name of the field displayed to the user (translatable)
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class Organization(BaseModel):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"))

    # Email contact
    email_address = models.EmailField(
        max_length=255, null=True, blank=True,
        default="",
        help_text=_("Email address used by the organization to respond to user data requests"),
        verbose_name=_("Email address"))

    # Postal contact
    address_line_one = models.CharField(
        max_length=255, null=True, blank=True,
        default="",
        verbose_name=_("Address line 1"))
    address_line_two = models.CharField(
        max_length=255, null=True, blank=True,
        default="",
        verbose_name=_("Address line 2"))
    postal_code = models.CharField(
        max_length=64, null=True, blank=True,
        default="",
        verbose_name=_("Postal code"))
    country = models.CharField(
        max_length=64, null=True, blank=True,
        default="",
        verbose_name=_("Country"))

    # Has admin verified this organization as having correct information
    verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Verified organizations are visible to all users"))

    authentication_fields = models.ManyToManyField(AuthenticationField, related_name="+")

    def __unicode__(self):
        return self.name
