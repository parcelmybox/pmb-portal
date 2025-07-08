from django import template
import logging
from ..admin_index import get_billing_stats

logger = logging.getLogger(__name__)
logger.info("Loading billing_tags.py")

register = template.Library()

@register.simple_tag(takes_context=True)
def get_admin_billing_stats(context):
    logger.info("get_admin_billing_stats called")
    return get_billing_stats()
