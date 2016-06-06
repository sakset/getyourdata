from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from organization.models import Organization
from organization.forms import NewOrganizationForm


def list_organizations(request):
    ORGANIZATIONS_PER_PAGE = 15

    page = request.GET.get("page", 1)
    p = Paginator(Organization.objects.all(), ORGANIZATIONS_PER_PAGE)

    try:
        organizations = p.page(page)
    except PageNotAnInteger:
        organizations = p.page(1)
    except EmptyPage:  # Reached an empty page: redirect to last page
        organizations = p.page(p.num_pages)
    return render(
        request, 'organization/list.html',
        {'organizations': organizations,
         'pag_url': reverse("organization:list_organizations")})


def new_organization(request):
    """
    A view to create a new organization, which will then be verified by site
    staff
    """
    form = NewOrganizationForm(request.POST or None)

    if form.is_valid():
        organization = Organization(**form.cleaned_data)
        organization.save()
        return render(
            request, "organization/new_organization/created.html",
            {"organization": organization})
    else:
        return render(
            request, "organization/new_organization/new.html",
            {"form": form})
