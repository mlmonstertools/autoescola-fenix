"""
Utilitario para geracao de PDFs dos relatorios.
"""
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone


def gerar_pdf_html(request, html_content, filename):
    """
    Gera um PDF a partir de conteudo HTML.
    Usa weasyprint se disponivel, senao retorna HTML para impressao.
    """
    try:
        from weasyprint import HTML
        
        # Gerar PDF com weasyprint
        pdf_file = BytesIO()
        HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except ImportError:
        # Se weasyprint nao estiver instalado, retorna HTML para impressao
        return HttpResponse(
            f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{filename}</title>
                <style>
                    @media print {{
                        body {{ margin: 0; }}
                        .no-print {{ display: none !important; }}
                    }}
                </style>
            </head>
            <body>
                <div class="no-print" style="background: #f0f0f0; padding: 10px; margin-bottom: 20px;">
                    <strong>Para salvar como PDF:</strong> Use Ctrl+P e selecione "Salvar como PDF"
                </div>
                {html_content}
                <script>window.print();</script>
            </body>
            </html>
            ''',
            content_type='text/html'
        )


def render_pdf_template(request, template_name, context, filename):
    """
    Renderiza um template como PDF.
    """
    html_content = render_to_string(template_name, context, request=request)
    return gerar_pdf_html(request, html_content, filename)
