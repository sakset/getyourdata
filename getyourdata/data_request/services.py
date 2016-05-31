from django.conf import settings

from xhtml2pdf import pisa

from StringIO import StringIO

def convert_html_to_pdf(html_data):
    """
    Converts a HTML document into a formatted PDF

    Returns the generated PDF file as raw output
    """
    pdf = StringIO()
    pisa.CreatePDF(StringIO(html_data), pdf)

    return pdf.getvalue()
