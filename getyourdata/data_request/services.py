from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils import timezone

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


def send_data_requests_by_email(data_requests, email_address):
    """
    Send provided data requests as email messages

    :data_requests: A QuerySet of data requests to send an email to
    :email_address: Email address of the person creating the data request
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
            from_email="noreply@getyourdata.org",
            reply_to=(email_address,)
        )
        email_messages.append(email)

    email_conn = get_connection()
    result = email_conn.send_messages(email_messages)

    # If all messages were sent, return True
    return result == len(email_messages)


def send_mail_request_pdf(email_address, mail_organizations, pdf_data):
    """Send a copy of mail request(s) as a PDF to a given email address

    :email_address: Email address to send to
    :mail_organizations: A list of organizations included in the PDF
    :pdf_data: PDF data to send

    """
    from data_request.models import RequestCopyContent

    request_copy_content, created = RequestCopyContent.objects.get_or_create(
        title="Default")
    email_body = render_to_string(
        "data_request/email/mail_request_copy.html", {
            "request_copy_content": request_copy_content,
            "mail_organizations": mail_organizations
        })

    email = EmailMessage(
        subject=_("Copy of mail requests"),
        body=email_body,
        to=(email_address,),
        from_email="noreply@getyourdata.org"
    )

    email.attach("mail_requests.pdf", pdf_data, "application/pdf")

    try:
        email.send()
        return True
    except:
        return False
