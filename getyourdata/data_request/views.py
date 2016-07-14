from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from data_request.forms import DataRequestForm
from data_request.models import DataRequest, AuthenticationContent, FaqContent
from organization.models import Organization

from getyourdata import util
from getyourdata.forms import CaptchaForm

from data_request.services import concatenate_pdf_pages
from data_request.services import send_data_requests_by_email

import base64


def request_data(request, org_ids=None):
    """
    View to create data requests for chosen organizations

    The process has three steps:
    1. entering the details
    2. reviewing the email requests, if any
    3. creating the PDF (for mail requests) and sending email messages
       (for email requests)
    """
    if org_ids is None:
        org_ids = request.POST.get("org_ids", None)

    if not org_ids:
        # If there are no org IDs, the user probably switched the language
        # or came back to this page after submitting a request
        return render(request, "data_request/expired.html")

    organizations = Organization.objects.filter(
        id__in=org_ids.split(","))

    if request.POST.get("action", None) == "review":
        # Review the form first
        return review_request(
            request, org_ids, organizations)

    # Add organizations into only one of the following lists
    # email is preferred if organization supports it, otherwise
    # fallback to normal mail
    mail_organizations = []
    email_organizations = []

    for organization in organizations:
        if organization.accepts_email:
            email_organizations.append(organization)
        elif organization.accepts_mail:
            mail_organizations.append(organization)

    # Is the user sending the request or reviewing it
    action = request.POST.get("action", None)

    if request.method == 'POST':
        form = DataRequestForm(
            request.POST or None, organizations=organizations)

        captcha_form = None

        if len(email_organizations) > 0:
            captcha_form = CaptchaForm(request.POST or None)

        # To make sure we don't store any data, do everything
        # inside a transaction which is rolled back instead of being
        # committed
        util.set_autocommit_off()

        if captcha_form and not captcha_form.is_valid():
            # If form validation failed, user didn't fill CAPTCHA correctly
            # Redirect to review page
            return review_request(request, org_ids, organizations, False)
        elif not form.is_valid():
            return render(request, 'data_request/request_data.html', {
                'form': form,
                'organizations': organizations,
                'mail_organizations': mail_organizations,
                'email_organizations': email_organizations,
                'org_ids': org_ids,
            })
        elif form.is_valid():
            if action == "send":
                pdf_pages = []
                email_requests = []

                for organization in organizations:
                    data_request = get_data_request(organization, form)

                    # Generate PDF pages for mail requests
                    try:
                        pdf_page = generate_pdf_page(data_request)
                        if pdf_page:
                            pdf_pages.append(pdf_page)
                    except RuntimeError:
                        messages.error(
                            request, _("The PDF file couldn't be created! Please try again later."))
                        return render(request, 'data_request/request_data.html', {
                            'form': form,
                            'organizations': organizations,
                            'mail_organizations': mail_organizations,
                            'email_organizations': email_organizations,
                            'org_ids': org_ids,
                        })

                    # Generate email messages
                    if organization.accepts_email:
                        email_requests.append(data_request)

                # Generate PDF pages for any mail-only requests
                pdf_data = generate_request_pdf(pdf_pages)

                # Send email requests
                if not send_email_requests(email_requests, form):
                    messages.error(
                        request, _("Email requests couldn't be sent! Please try again later."))

                    util.rollback()

                    return render(request, "data_request/request_data.html", {
                        'form': form,
                        'organizations': organizations,
                        'mail_organizations': mail_organizations,
                        'email_organizations': email_organizations,
                        'org_ids': org_ids
                    })

                # Cancel transaction to clear everything from memory
                util.rollback()
                util.set_autocommit_on()

                return render(request, 'data_request/sent.html', {
                    'organizations': organizations,
                    'mail_organizations': mail_organizations,
                    'email_organizations': email_organizations,
                    'pdf_data': pdf_data
                    })
    else:
        form = DataRequestForm(organizations=organizations)

    return render(request, 'data_request/request_data.html', {
        'form': form,
        'organizations': organizations,
        'mail_organizations': mail_organizations,
        'email_organizations': email_organizations,
        'org_ids': org_ids,
    })


def review_request(request, org_ids, organizations, ignore_captcha=True):
    """
    Let user review his email requests if he's sending any

    :request: Current request
    :org_ids: List of organization IDs as a comma separated string
    :organizations: A list of Organization objects
    :ignore_captcha: Whether to ignore any errors thrown by CAPTCHA
                     The first time the user enters the page the user hasn't
                     filled the captcha; this parameter prevents an
                     error from showing up
    """
    # Add organizations into only one of the following lists
    # email is preferred if organization supports it, otherwise
    # fallback to normal mail
    mail_organizations = []
    email_organizations = []

    for organization in organizations:
        if organization.accepts_email:
            email_organizations.append(organization)
        elif organization.accepts_mail:
            mail_organizations.append(organization)

    if request.method == 'POST':
        form = DataRequestForm(
            request.POST, organizations=organizations, visible=False)

        captcha_form = CaptchaForm(
            request.POST if not ignore_captcha else None)

        data_requests = []

        if not form.is_valid() and ignore_captcha:
            # Ignore any errors in CAPTCHA while still reviewing
            del captcha_form._errors["captcha"]

        if form.is_valid():
            data_requests = get_data_requests(form, organizations)

    return render(request, "data_request/request_data_review.html", {
        "form": form,
        "captcha_form": captcha_form,
        "email_organizations": email_organizations,
        "mail_organizations": mail_organizations,
        "data_requests": data_requests,
        "org_ids": org_ids,
    })


def get_data_requests(form, organizations):
    """
    Get a list of every data request

    :form: A filled DataRequestForm
    :email_organizations: A list of organizations that accept email requests
    :mail_organizations: A list of organizations that only accept mail requests
    """
    data_requests = []

    for organization in organizations:
        data_request = get_data_request(organization, form)
        data_requests.append(data_request)

    return data_requests


def generate_pdf_page(data_request):
    """Generate a PDF page from a given data request if it's mail-only

    :returns: PDF data if successful
              False if the data request doesn't need a PDF
    :raises: RuntimeError if page couldn't be generated
    """
    if data_request.organization.accepts_email:
        return False

    pdf_page = data_request.to_pdf()

    if not pdf_page:
        raise RuntimeError("PDF page couldn't be generated!")

    return pdf_page


def generate_request_pdf(pdf_pages):
    """Create a single PDF from multiple PDF pages

    :returns: The created PDF as base64 encoded data to be included
              in the view
              None if no PDF pages were provided

    """
    if len(pdf_pages) > 0:
        pdf_data = concatenate_pdf_pages(pdf_pages)
        pdf_data = base64.b64encode(pdf_data)
    else:
        pdf_data = None

    return pdf_data


def send_email_requests(email_requests, form):
    """Send all provided email requests

    :email_requests: A list of DataRequests to be sent as email requests
    :form: The current DataRequestForm
    :returns: True if all email requests could be sent or no email requests
              were provided
              False if at least one email request couldn't be sent

    """
    if len(email_requests) > 0 and not send_data_requests_by_email(
         data_requests=email_requests,
         email_address=form.cleaned_data["user_email_address"]):
        return False
    else:
        return True


def get_data_request(organization, form):
    """Get a temporary data request containing user's authentication details

    :organization: Organization of the data request
    :form: The view's DataRequestForm
    :returns: A DataRequest with details filled

    """
    data_request = DataRequest.objects.create(
        organization=organization)
    auth_fields = organization.authentication_fields.all()
    auth_contents = []

    for auth_field in auth_fields:
        auth_contents.append(AuthenticationContent(
            auth_field=auth_field,
            data_request=data_request,
            content=form.cleaned_data[auth_field.name]
            ))
    AuthenticationContent.objects.bulk_create(auth_contents)

    return data_request

def faq(request):
    faqs = FaqContent.objects.order_by("priority")
    return render(request, 'data_request/faq/faq.html', {"faqs": faqs})
