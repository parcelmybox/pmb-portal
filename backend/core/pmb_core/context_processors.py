"""
Context processors for the pmb_hello project.
"""
from django.conf import settings

def company_info(request):
    """
    Add company information to the template context.
    """
    return {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'ParcelMyBox'),
        'COMPANY_LOGO': getattr(settings, 'COMPANY_LOGO', '/static/images/logo.png'),
        'COMPANY_ADDRESS': getattr(settings, 'COMPANY_ADDRESS', '123 Shipping Street, Anytown, USA'),
        'COMPANY_PHONE': getattr(settings, 'COMPANY_PHONE', '+1 (555) 123-4567'),
        'COMPANY_EMAIL': getattr(settings, 'COMPANY_EMAIL', 'support@parcelmybox.com'),
        'COMPANY_COPYRIGHT': getattr(settings, 'COMPANY_COPYRIGHT', '© 2025 ParcelMyBox. All rights reserved.'),
    }
