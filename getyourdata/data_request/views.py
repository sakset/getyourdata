from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from data_request.forms import DataRequestForm
from data_request.models import DataRequest, AuthenticationContent
from organization.models import Organization

from data_request.services import concatenate_pdf_pages


def request_data(request, org_ids=None):
    if org_ids is None:
        org_ids = request.POST.get("org_ids", None)

    if not org_ids:
        return HttpResponse(
            _("No organization ID or organization ID list was provided!"),
            status=400)

    organizations = Organization.objects.filter(id__in=org_ids.split(","))

    if request.method == 'POST':
        form = DataRequestForm(request.POST, organizations=organizations)

        if form.is_valid():
            pdf_pages = []

            for organization in organizations:
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

                # TODO: Create PDF and send email to organization.
                # Note that there will be no reason to save AuthenticationContents in our database.
                # We are doing it here now just for illustration purposes.
                '''
                messages.success(
                    request, _('Your data was successfully requested from %s!'
                    % organization.name))
                '''
                pdf_page = data_request.to_pdf()

                if not pdf_page:
                    messages.error(
                        request, _("The PDF file couldn't be created! Please try again later."))
                    return render(request, 'data_request/request_data.html', {
                        'form': form,
                        'organizations': organizations,
                        'org_ids': org_ids,
                    })

                pdf_pages.append(pdf_page)

            pdf_data = concatenate_pdf_pages(pdf_pages)

            response = HttpResponse(pdf_data, content_type='application/pdf')
            response["Content-Disposition"] = 'attachment; filename="request.pdf"'
            return response
    else:
        form = DataRequestForm(organizations=organizations)

    return render(request, 'data_request/request_data.html', {
        'form': form,
        'organizations': organizations,
        'org_ids': org_ids,
    })
