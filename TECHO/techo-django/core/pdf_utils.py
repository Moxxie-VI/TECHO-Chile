from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

def render_to_pdf(template_src: str, context: dict) -> bytes | None:
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result, encoding='utf-8')
    if not pdf.err:
        return result.getvalue()
    return None

def pdf_http_response(filename: str, pdf_bytes: bytes, as_attachment: bool = True) -> HttpResponse:
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    disposition = 'attachment' if as_attachment else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response
