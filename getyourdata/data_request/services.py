from django.conf import settings

import subprocess
import random
import string
import os

def generate_random_string():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

def convert_html_to_pdf(html_data):
    """
    Converts a valid DataRequest into a formatted PDF ready for printing

    File is generated using HTMLDOC utility, which is called using
    subprocess.Popen

    Returns the generated PDF file as raw output
    """
    # A random ID for the generated request
    file_id = generate_random_string()

    html_path = "%s/request_html" % settings.MEDIA_ROOT
    pdf_path = "%s/request_pdf" % settings.MEDIA_ROOT

    html_file_path = "%s/%s.html" % (html_path, file_id)
    pdf_file_path = "%s/%s.pdf" % (pdf_path, file_id)

    html_file = open(html_file_path, 'w')
    html_file.write(html_data)
    html_file.close()

    # Pipe HTML input to htmldoc, and retrieve PDF output from stdout
    htmldoc = subprocess.Popen(
        ["/usr/bin/htmldoc", "-t", "pdf", "--webpage", "--size", "a4",
         "--outfile", pdf_file_path, html_file_path]
    )
    htmldoc.wait()

    pdf_file = open(pdf_file_path, 'r')
    pdf_data = pdf_file.read()
    pdf_file.close()

    os.remove(html_file_path)
    os.remove(pdf_file_path)

    # If process returned 0, we succeeded in printing the PDF output
    if htmldoc.returncode == 0:
        return pdf_data
    else:
        return None
