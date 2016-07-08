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
                   "original_organization_fields": original_organization_fields})
