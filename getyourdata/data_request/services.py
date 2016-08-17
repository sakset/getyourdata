from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

from xhtml2pdf import pisa
from PyPDF2 import PdfFileMerger

from StringIO import StringIO

def convert_html_to_pdf(html_data):
    """
    Converts a HTML document into a formatted PDF

    Returns the generated PDF file as raw output
    """
    pdf = StringIO()
    pisa.CreatePDF(StringIO(html_data), pdf)

    return pdf.getvalue()


def concatenate_pdf_pages(pdf_pages):
    """
    Concatenate multiple PDF pages into one PDF document
    """
    if len(pdf_pages) == 1:
        return pdf_pages[0]

    try:
        merger = PdfFileMerger()

        for pdf_page in pdf_pages:
            merger.append(StringIO(pdf_page))

        complete_pdf = StringIO()
        merger.write(complete_pdf)

        return complete_pdf.getvalue()
    except:
        return False


def send_data_requests_by_email(email_address, data_requests):
    """
    Send provided data requests as email messages

    :email_address: Email address of the person creating the data request
    :data_requests: A QuerySet of data requests to send an email to
    :returns: True if all data requests could be sent, False if not

    """
    email_messages = []

    for data_request in data_requests:
        email_body = data_request.to_email_body()
        email = EmailMessage(
            subject=_("Data request: %s" % data_request.organization.name),
            body=email_body,
            to=(data_request.organization.email_address,),
            cc=(email_address,),
            from_email=settings.NOREPLY_EMAIL_ADDRESS,
            reply_to=(email_address,)
        )
        email_messages.append(email)

    email_conn = get_connection()
    result = email_conn.send_messages(email_messages)

    # If all messages were sent, return True
    return result == len(email_messages)


def send_feedback_message_by_email(email_address, request,
                                   organizations, pdf_data):
    """Send a message detailing organizations the user created a data request for

    :email_address: Email address to send to
    :request: Current request
    :organizations: A list of organizations to be included in the message
    :pdf_data: PDF data to include in the request. If None, no copy
               will be attached

    """
    from data_request.models import FeedbackMessageContent

    feedback_content, created = FeedbackMessageContent.objects.get_or_create(
        name="Default"
    )

    org_ids = [str(organization.id) for organization in organizations]
    org_ids = ",".join(org_ids)

    email_body = render_to_string(
        "data_request/email_plain/thanks.html", {
            "feedback_content": feedback_content,
            "organizations": organizations,
            "org_ids": org_ids,
            "request": request,
            "send_mail_request_copy": True if pdf_data else None
        })

    email_html_body = render_to_string(
        "data_request/email/thanks.html", {
            "feedback_content": feedback_content,
            "organizations": organizations,
            "org_ids": org_ids,
            "request": request,
            "send_mail_request_copy": True if pdf_data else None
        })

    email = EmailMultiAlternatives(
        subject=_("Thank you for using GetYourData"),
        body=email_body,
        to=(email_address,),
        from_email=settings.NOREPLY_EMAIL_ADDRESS)

    email.attach_alternative(email_html_body, 'text/html')

    if pdf_data:
        email.attach("mail_requests.pdf", pdf_data, "application/pdf")

    try:
        email.send()
        return True
    except:
        return False
