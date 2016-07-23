from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from data_request.forms import DataRequestForm
from data_request.models import DataRequest, AuthenticationContent, FaqContent
from organization.models import Organization

from getyourdata import util
from getyourdata.forms import CaptchaForm

from data_request.services import concatenate_pdf_pages
from data_request.services import send_data_requests_by_email
from data_request.services import send_mail_request_pdf

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

    util.set_autocommit_off()

    response = None

    if request.POST.get("send", None):
        response = send_request(request, org_ids)
    elif request.POST.get("review", None):
        response = review_request(request, org_ids)
    elif request.POST.get("return", None):
        return redirect(reverse("organization:list_organizations"))
    else:
        response = create_request(request, org_ids)

    util.rollback()
    util.set_autocommit_on()

    return response


def create_request(request, org_ids):
    """
    FIRST STEP
    Let user fill any needed authentication fields and other details
    """
    (organizations, email_organizations,
     mail_organizations) = get_organization_tuple(org_ids)

    form = DataRequestForm(
        request.POST or None, organizations=organizations)

    if request.method == 'POST':
        if form.is_valid() and request.POST.get("review", None):
            return review_request(request, org_ids)

    return render(request, 'data_request/request_data.html', {
        'form': form,
        'organizations': organizations,
        'mail_organizations': mail_organizations,
        'email_organizations': email_organizations,
        'org_ids': org_ids,
    })


def review_request(request, org_ids, ignore_captcha=True, prevent_redirect=False):
    """
    SECOND STEP
    Let user review his email requests if he's sending any

    :request: Current request
    :org_ids: List of organization IDs as a comma separated string
    :ignore_captcha: Whether to ignore any CAPTCHA errors
                     The first time user comes to review page he hasn't
                     filled the CAPTCHA, so we don't want to show an error
    :prevent_redirect: Prevent user from being redirected to 'send' page even
                       if the form would be valid
    """
    (organizations, email_organizations,
     mail_organizations) = get_organization_tuple(org_ids)

    if request.method == 'POST':
        form = DataRequestForm(
            request.POST, organizations=organizations, visible=False)

        data_requests = []

        if form.is_valid():
            data_requests = get_data_requests(form, organizations)

            if request.POST.get("send", None) and not prevent_redirect:
                return send_request(request, org_ids)
        else:
            return create_request(request, org_ids)

    captcha_form = None

    if not ignore_captcha:
        captcha_form = CaptchaForm(request.POST or None)
    elif ignore_captcha:
        captcha_form = CaptchaForm()

    return render(request, "data_request/request_data_review.html", {
        "form": form,
        "captcha_form": captcha_form,
        "email_organizations": email_organizations,
        "mail_organizations": mail_organizations,
        "data_requests": data_requests,
        "org_ids": org_ids,
    })


def send_request(request, org_ids):
    """
    Send any email requests and create a PDF from many mail requests

    :request: Current request
    :org_ids: List of organization IDs as a comma separated string
    """
    (organizations, email_organizations,
     mail_organizations) = get_organization_tuple(org_ids)

    # Was a copy of the mail requests sent to an email address
    mail_request_copy_sent = False

    if request.method == 'POST':
        form = DataRequestForm(
            request.POST, organizations=organizations, visible=False)

        captcha_form = CaptchaForm(request.POST or None)

        if form.is_valid() and captcha_form.is_valid():
            cleaned_data = form.cleaned_data

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

                    return review_request(
                        request, org_ids, prevent_redirect=True)

                # Generate email messages
                if organization.accepts_email:
                    email_requests.append(data_request)

            # Generate PDF pages for any mail-only requests
            pdf_data = generate_request_pdf(pdf_pages)

            # Send email requests
            if not send_email_requests(email_requests, form):
                messages.error(
                    request, _("Email requests couldn't be sent! Please try again later."))

                return review_request(request, org_ids, prevent_redirect=True)

            if cleaned_data.get("send_mail_request_copy", None) and \
                cleaned_data.get("user_email_address", None):
                # User wants a copy of mail requests, send them
                if not send_mail_request_pdf(
                     cleaned_data.get("user_email_address"),
                     mail_organizations, pdf_data):
                    messages.error(
                        request,
                        _("A copy of the mail requests couldn't be sent!"))
                else:
                    mail_request_copy_sent = True


            if pdf_data:
                # Encode the PDF data as base64 to be rendered in the view
                pdf_data = base64.b64encode(pdf_data)

            # Request was successful!
            return render(request, "data_request/sent.html", {
                "organizations": organizations,
                "mail_organizations": mail_organizations,
                "email_organizations": email_organizations,
                "pdf_data": pdf_data,
                "org_ids": org_ids,
                "mail_request_copy_sent": mail_request_copy_sent
            })
        else:
            return review_request(
                request, org_ids, False, prevent_redirect=True)

    # Send user back to review page
    # send POST parameter is removed to prevent redirect loop
    return review_request(request, org_ids, prevent_redirect=True)


def give_feedback(request, org_ids):
    """
    Requests have been finished, just show user a link of organization profiles
    to give feedback

    :request: Current request
    :org_ids: A list of Organization objects

    """
    organizations = Organization.objects.filter(
        id__in=org_ids.split(","))

    return render(request, "data_request/request_data_feedback.html", {
        "org_ids": org_ids,
        "organizations": organizations,
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


def get_organization_tuple(org_ids):
    """Return (all_organizations, email_organizations, mail_organizations)
       tuple

    :org_ids: Organization IDs as a comma-separated list
    :returns: (all_organizations, email_organizations, mail_organizations)
              tuple containing organizations
    """
    organizations = Organization.objects.filter(
        id__in=org_ids.split(","))

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

    return (organizations, email_organizations, mail_organizations)


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
