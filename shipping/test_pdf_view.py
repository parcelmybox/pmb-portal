from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings

def test_pdf_view(request):
    """A simple view to test PDF generation"""
    # Simple HTML template for testing
    template_path = 'shipping/billing/bill_pdf_simple.html'
    template = get_template(template_path)
    
    # Simple context
    context = {
        'bill': {
            'id': 'TEST123',
            'amount': '100.00',
            'status': 'PENDING',
            'created_at': '2023-01-01',
            'description': 'Test Bill',
            'get_status_display': lambda: 'Pending',
            'items': [
                {'description': 'Test Item', 'quantity': 1, 'unit_price': '100.00', 'total': '100.00'}
            ]
        },
        'company_name': 'ParcelMyBox',
        'company_address': '123 Test St, Test City',
        'company_phone': '(123) 456-7890',
        'company_email': 'test@parcelmybox.com',
        'company_website': 'www.parcelmybox.com',
        'company_tax_id': 'TAX-123-456',
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': str(settings.STATIC_ROOT).replace('\\', '/'),
        'today': '2023-01-01',
        'due_date': '2023-01-15',
        'now': '2023-01-01 12:00:00',
        'subtotal': '100.00',
        'tax_amount': '10.00',
        'tax_rate': '10',
        'total': '110.00',
        'payment_terms': 'Net 15',
        'items': [
            {'description': 'Test Item', 'quantity': 1, 'unit_price': '100.00', 'total': '100.00'}
        ]
    }
    
    # Render the HTML with context
    html = template.render(context)
    
    # Create HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="test_bill.pdf"'
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='UTF-8',
        link_callback=None,
        show_error_as_pdf=True,
        xhtml=False
    )
    
    # Check for errors
    if pisa_status.err:
        return HttpResponse('PDF generation error: %s' % pisa_status.err)
    
    return response
