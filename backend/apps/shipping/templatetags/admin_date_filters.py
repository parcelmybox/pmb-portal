from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.filter(expects_localtime=True)
def localtime_pst(value):
    """Convert a datetime to PST/PDT based on the current date."""
    if not value:
        return value
    
    # Get the timezone object for Pacific Time
    pacific = pytz.timezone('America/Los_Angeles')
    
    # If value is naive (no timezone), assume it's in UTC
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone=timezone.utc)
    
    # Convert to Pacific Time
    return value.astimezone(pacific)
