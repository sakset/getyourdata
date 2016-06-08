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
    try:
        merger = PdfFileMerger()

        for pdf_page in pdf_pages:
            merger.append(StringIO(pdf_page))

        complete_pdf = StringIO()
        merger.write(complete_pdf)

        return complete_pdf.getvalue()
    except:
        return False
