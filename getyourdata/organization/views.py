from django.shortcuts import render

from organization.models import Organization
from organization.forms import NewOrganizationForm


def list_organizations(request):
    organizations = Organization.objects.all()
    return render(
        request, 'organization/list.html',
        {'organizations': organizations})


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
