from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _

from getyourdata.models import BaseModel


class AuthenticationField(BaseModel):
    """
    Authentication field that organizations use to identify people
    eg. email address
    """
    # The canonical name of the field (NOT TRANSLATED!)
    name = models.CharField(max_length=255, unique=True, db_index=True)

    # Name of the field displayed to the user (translatable)
    title = models.CharField(max_length=255)

    order = models.IntegerField(default=777)

    help_text = models.CharField(max_length=255, default="", blank=True)
    validator_regex = models.CharField(
        max_length=1028, default="", blank=True,
        help_text=_("If not blank, this regex is used to validate the field value"))

    def __unicode__(self):
        return self.title

    def required_by(self, organizations):
        return Organization.objects.filter(
            authentication_fields=self,
            id__in=organizations.values_list('id', flat=True)
        )

def form_has_fields(form, fields):
    """
    Checks if form has certain fields
    """
    for field in fields:
        if not getattr(form, field):
            return False
    return True


class OrganizationDetails(BaseModel):
    """
    Base organization details each organization has, whether the model
    is an available organization profile or an edit draft made by an user
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"))

    # Email contact
    email_address = models.EmailField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Email address used by the organization for receiving "
                    "data requests. Leave empty if the "
                    "organization only accepts requests by post."),
        verbose_name=_("Email address"))

    # Postal contact
    address_line_one = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Address line 1"))
    address_line_two = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Address line 2"))
    postal_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Postal code"))
    country = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Country"))

    authentication_fields = models.ManyToManyField(
        AuthenticationField, related_name="+")

    class Meta:
        abstract = True

    def clean(self):
        postal_address_requirements = [
            "address_line_one",
            "postal_code",
            "country"
        ]
        if not (form_has_fields(self, ["email_address"]) or
                form_has_fields(self, postal_address_requirements)):
            raise ValidationError(
                _("Organization profile must contain either a valid email "
                  "address or postal information"))
        return self


class Organization(OrganizationDetails):
    """
    Organization that is accessible to all users
    """
    # Has admin verified this organization as having correct information
    verified = models.BooleanField(
        default=False,
        verbose_name=_("Verified"),
        help_text=_("Verified organizations are visible to all users"))

    class Meta:
        ordering = ('created_on',)

    @property
    def accepts_email(self):
        return self.email_address != ""

    @property
    def accepts_mail(self):
        return self.address_line_one != "" and \
               self.postal_code != "" and \
               self.country != ""

    @property
    def has_registers(self):
        return self.registers(manager='objects').all().exists()

    @property
    def has_comments(self):
        return self.comments(manager='objects').all().exists()

    @property
    def average_rating(self):
        rating = self.comments(manager='objects').all().aggregate(
            avg=Avg('rating'))['avg']

        if rating:
            return format(float(rating), '.1f')
        return '0'

    @property
    def amount_ratings(self):
        return self.comments(manager='objects').all().count()

    def __unicode__(self):
        return self.name


class Register(BaseModel):
    """
    Organization may have multiple registers
    """
    # name of the register
    name = models.CharField(
        max_length=255,
        help_text=_("The name of the register used by the organization. "
                    "Eg. Customer register"),
        verbose_name=_("Name of the person register"))

    # which organization this register belongs to
    organization = models.ForeignKey(
        Organization,
        related_name='registers',
        on_delete=models.CASCADE
    )
    help_text = models.CharField(max_length=255, default="", blank=True)

    def __unicode__(self):
        return self.name


class OrganizationDraft(OrganizationDetails):
    """
    Organization draft created when an user modifies an existing organization
    and submits the suggestions. Only visible to the site staff.
    """
    class Meta:
        verbose_name = "organization edit draft"
        verbose_name_plural = "organization edit drafts"
        ordering = ('updated_on',)

        permissions = (
            ("check_organization_draft",
                _("Can check organization drafts and update the original "
                  "organization")),
        )

    original_organization = models.ForeignKey(
        "organization.Organization", related_name="original_organizations")

    checked = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)


class Comment(BaseModel):
    """
    Public comment posted on an organization profile
    """
    organization = models.ForeignKey(Organization, related_name='comments')
    message = models.TextField(max_length=2000)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3
    )

    class Meta:
        ordering = ('-created_on',)

    def __unicode__(self):
        return 'Comment ' + unicode(self.organization)

