from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _

from getyourdata.forms import CaptchaForm

from organization.models import Organization, OrganizationDraft
from organization.models import AuthenticationField
from organization.forms import NewOrganizationForm, EditOrganizationForm
from organization.forms import CommentForm
from organization.utils import get_objects_paginator


def list_organizations(request):
    """
    View to select organizations for a data request
    """
    page = request.GET.get("page", 1)
    orgs = Organization.objects.filter(verified=True)
    orgs_per_page = settings.ORGANIZATIONS_PER_PAGE
    org_ids = request.POST.getlist("org_ids")

    organizations = get_objects_paginator(page, orgs, orgs_per_page)

    if request.POST.get("create_request", None) and len(org_ids) > 0:
        # User wants to create a request with selected organizations
        return redirect(
            reverse("data_request:request_data", args=(",".join(org_ids),)))

    show_pagination = orgs_per_page < len(orgs)

    return render(
        request, 'organization/list.html',
        {'organizations': organizations,
         'show_pagination': show_pagination,
         'org_ids': org_ids,
         'pag_url': reverse("organization:list_organizations"),
         })


def view_organization(request, org_id):
    """
    View an organization with contact details and probably
    some stats later
    """
    organization = cache.get("organization-%s" % org_id)

    if not organization and organization is not None:
        raise Http404()

    if organization is None:
        try:
            organization = get_object_or_404(Organization, pk=org_id)
        except Http404:
            cache.set("organization-%s" % org_id, False, 30)
            raise Http404()
            return

        cache.set("organization-%s" % org_id, organization, 60)

    page = request.GET.get("page", 1)
    org_comments = organization.comments(manager='objects').all()
    comments_per_page = settings.COMMENTS_PER_PAGE
    comments = get_objects_paginator(page, org_comments, comments_per_page)

    form = CommentForm(request.POST or None)
    captcha_form = CaptchaForm(request.POST or None)

    show_pagination = comments_per_page < len(org_comments)

    if request.method == 'POST':
        if form.is_valid() and captcha_form.is_valid():
            comment = form.save(commit=False)
            comment.organization = organization
            comment.save()
            messages.success(request, _('Thank you for your feedback!'))
            return redirect(reverse('organization:view_organization', args=(organization.id,)))

    return render(request, 'organization/view.html', {
        'organization': organization,
        'comments': comments,
        'form': form,
        'captcha_form': captcha_form,
        'pag_url': reverse("organization:view_organization", args=(org_id,)),
        'show_pagination': show_pagination,
    })


def new_organization(request):
    """
    A view to create a new organization, which will then be verified by site
    staff
    """
    form = NewOrganizationForm(request.POST or None)
    captcha_form = CaptchaForm(request.POST or None)

    if form.is_valid() and captcha_form.is_valid():
        # Get authentication fields from the form
        authentication_field_ids = form.cleaned_data["authentication_fields"]
        authentication_fields = AuthenticationField.objects.filter(
            pk__in=authentication_field_ids)
        del form.cleaned_data["authentication_fields"]

        organization = Organization(**form.cleaned_data)
        organization.save()

        organization.authentication_fields.add(*authentication_fields)
        organization.save()

        messages.success(request,
            _("Organization profile created! Note that the organization profile won't be made visible until it has been verified by the site staff."))
        return redirect(reverse('organization:view_organization', args=(organization.id,)))
    else:
        return render(
            request, "organization/new_organization/new.html",
            {"form": form,
             "captcha_form": captcha_form})


def edit_organization(request, org_id=None):
    """
    Edit an existing organization. The modified organization is saved as an
    OrganizationDraft which can be implemented by staff
    """
    organization = cache.get("org_w_fields-%s" % org_id)

    if not organization and organization is not None:
        raise Http404("Organization not found")

    if organization is None:
        try:
            organization = Organization.objects.prefetch_related(
                "authentication_fields").get(pk=org_id)
            cache.set("org_w_fields-%s" % org_id, organization)
        except ObjectDoesNotExist:
            cache.set("org_w_fields-%s" % org_id, False)
            raise Http404("Organization not found")

    form = EditOrganizationForm(
        request.POST or None, organization=organization)
    captcha_form = CaptchaForm(request.POST or None)

    if form.is_valid() and captcha_form.is_valid():
        # Get authentication fields from the form
        authentication_field_ids = form.cleaned_data["authentication_fields"]
        authentication_fields = AuthenticationField.objects.filter(
            pk__in=authentication_field_ids)
        del form.cleaned_data["authentication_fields"]

        organization_draft = OrganizationDraft(**form.cleaned_data)
        organization_draft.original_organization = organization
        organization_draft.save()

        organization_draft.authentication_fields.add(*authentication_fields)
        organization_draft.save()

        messages.success(request,
            _("An organization profile with your modifications has been sent! The changes won't be made visible until they have been verified by the site staff."))
        return redirect(reverse('organization:view_organization', args=(organization.id,)))

    return render(
        request, "organization/edit_organization/edit.html",
        {"form": form,
         "captcha_form": captcha_form,
         "organization": organization})
