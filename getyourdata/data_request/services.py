from django.template.loader import render_to_string
from django.utils import timezone

from data_request.models import DataRequest, AuthenticationContent
from organization.models import AuthenticationField

import subprocess

def convert_data_request_to_pdf(data_request):
    """
    Converts a valid DataRequest into a formatted PDF ready for printing

    Returns the generated PDF file as raw output
    """
    # Person's name making the request is optional
    try:
        person_name = AuthenticationContent.objects.get(data_request=data_request,
                                                        auth_field__name="name")
    except:
        person_name = None

    html_body = render_to_string(
        "data_request/mail/request.html", {"data_request": data_request,
                                           "person_name": person_name,
                                           "current_datetime": timezone.now()})

    # Pipe HTML input to htmldoc, and retrieve PDF output from stdout
    htmldoc = subprocess.Popen(
        ["/usr/bin/htmldoc", "-t", "pdf", "--webpage", "--size", "a4",
         "-"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = htmldoc.communicate(html_body)

    # If process returned 0, we succeeded in printing the PDF output
    if htmldoc.returncode == 0:
        return stdout
    else:
        return None
