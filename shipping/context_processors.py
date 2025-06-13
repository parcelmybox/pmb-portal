from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

def admin_site_info(request):
    """
    Add custom context variables to all admin pages.
    """
    if not request.path.startswith('/admin/'):
        return {}
        
    User = get_user_model()
    
    return {
        'site_title': 'Parcel My Box Admin',
        # Removed site_header to prevent duplicate headers
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '/',
        'user_count': User.objects.count(),
        'current_time': timezone.now(),
        'django_version': settings.VERSION,
    }
