from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from django.db import transaction

from organization.models import Organization, OrganizationDraft
from organization.forms import ORGANIZATION_FIELDS


def check_organization_draft(request, draft_id):
    """
    Process a report for a paste, allowing the staff member to either
    ignore the suggestion or update the original organization
    """
    if not request.user.is_authenticated or not request.user.has_perm(
         "organization.check_organization_draft"):
        return HttpResponse(
            "You don't have the permission to do this.", status=422)

    organization_draft = OrganizationDraft.objects.select_related(
        "original_organization").get(pk=draft_id)
    original_organization = organization_draft.original_organization

    organization_draft_fields = organization_draft.authentication_fields.all()
    original_organization_fields = original_organization.authentication_fields.all()

    organization_default_fields = ("name", "email_address",
        "address_line_one", "address_line_two", "postal_code",
        "country")

    # Create a list of (field_name, original_value, new_value) tuples
    fields = []
    for field in organization_default_fields:
        fields.append(
            (unicode(original_organization._meta.get_field(field).verbose_name),
             getattr(original_organization, field),
             getattr(organization_draft, field)))

    original_auth_fields = ", ".join(
        original_organization_fields.values_list("title", flat=True))
    new_auth_fields = ", ".join(
        organization_draft_fields.values_list("title", flat=True))

    fields.append(
        (unicode(
            original_organization._meta.get_field("authentication_fields").verbose_name),
         original_auth_fields,
         new_auth_fields))

    if "update" in request.POST:
        with transaction.atomic():
            for field in ORGANIZATION_FIELDS:
                # Replace the fields in the original organization
                # with new ones
                setattr(original_organization, field,
                        getattr(organization_draft, field))

            original_organization.authentication_fields = organization_draft_fields
            original_organization.save()

            organization_draft.updated = True
            organization_draft.checked = True
            organization_draft.save()

        messages.success(
            request, _("The organization %s was updated with new details." %
                       original_organization.name))

        return redirect(
            reverse("admin:organization_organizationdraft_changelist"))
    elif "ignore" in request.POST:
        organization_draft.ignored = True
        organization_draft.checked = True
        organization_draft.save()

        messages.success(
            request, _("The organization draft for %s was ignored." %
                       original_organization.name))

        return redirect(
            reverse("admin:organization_organizationdraft_changelist"))

    return render(request, "organization/admin/check_organization_draft.html",
                  {"organization_draft": organization_draft,
                   "original_organization": original_organization,
                   "organization_draft_fields": organization_draft_fields,
                   "original_organization_fields": original_organization_fields,
                   "fields": fields})
