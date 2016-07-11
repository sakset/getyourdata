from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.utils.translation import ugettext as _

from organization.models import Organization, OrganizationDraft
from organization.models import AuthenticationField
from organization.forms import NewOrganizationForm, EditOrganizationForm, CommentForm


def list_organizations(request):
    """
    View to select organizations for a data request
    """
    ORGANIZATIONS_PER_PAGE = 15

    page = request.GET.get("page", 1)

    org_ids = request.POST.getlist("org_ids")

    p = Paginator(
        Organization.objects.filter(verified=True),
        ORGANIZATIONS_PER_PAGE)

    try:
        organizations = p.page(page)
    except PageNotAnInteger:
        organizations = p.page(1)
    except EmptyPage:  # Reached an empty page: redirect to last page
        organizations = p.page(p.num_pages)

    if request.POST.get("create_request", None) and len(org_ids) > 0:
        # User wants to create a request with selected organizations
        return redirect(
            reverse("data_request:request_data", args=(",".join(org_ids),)))

    return render(
        request, 'organization/list.html',
        {'organizations': organizations,
         'org_ids': org_ids,
         'pag_url': reverse("organization:list_organizations")})


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

    comments = organization.comments(manager='objects').all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.organization = organization
            comment.save()
            messages.success(request, _('Thank you for your feedback!'))
            return redirect(reverse('organization:view_organization', args=(organization.id,)))
    else:
        form = CommentForm()
    return render(request, 'organization/view.html', {
        'organization': organization,
        'comments': comments,
        'form': form,
    })


def new_organization(request):
    """
    A view to create a new organization, which will then be verified by site
    staff
    """
    form = NewOrganizationForm(request.POST or None)

    if form.is_valid():
        # Get authentication fields from the form
        authentication_field_ids = form.cleaned_data["authentication_fields"]
        authentication_fields = AuthenticationField.objects.filter(
            pk__in=authentication_field_ids)
        del form.cleaned_data["authentication_fields"]

        organization = Organization(**form.cleaned_data)
        organization.save()

        organization.authentication_fields.add(*authentication_fields)
        organization.save()

        return render(
            request, "organization/new_organization/created.html",
            {"organization": organization})
    else:
        return render(
            request, "organization/new_organization/new.html",
            {"form": form})


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

    if form.is_valid():
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

        return render(request, "organization/edit_organization/done.html", {
            "organization": organization})

    return render(
        request, "organization/edit_organization/edit.html",
        {"form": form,
         "organization": organization})
