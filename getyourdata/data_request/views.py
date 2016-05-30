from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from data_request.forms import DataRequestForm
from data_request.models import DataRequest, AuthenticationContent
from organization.models import Organization


def request_data(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    if request.method == 'POST':
        form = DataRequestForm(request.POST, organization=organization)
        if form.is_valid():
            data_request = DataRequest.objects.create(organization=organization)
            auth_fields = organization.authentication_fields.all()
            auth_contents = []
            for auth_field in auth_fields:
                auth_contents.append(AuthenticationContent(
                    auth_field=auth_field,
                    data_request=data_request,
                    content=form.cleaned_data[auth_field.name]
                    ))
            AuthenticationContent.objects.bulk_create(auth_contents)
            messages.success(request, _('Your data was successfully requested from %s!' \
                % organization.name))
            return redirect(reverse('organization:list_organizations'))
    else:
        form = DataRequestForm(organization=organization)
    return render(request, 'data_request/request_data.html', {
        'form': form,
        'organization': organization,
    })