from django import template

register = template.Library()

@register.filter
def filter_status(queryset, status):
    """
    Filter a queryset by status.
    Usage in template: {{ shipments|filter_status:'delivered' }}
    """
    if not queryset:
        return queryset.none()
    return queryset.filter(status=status)
