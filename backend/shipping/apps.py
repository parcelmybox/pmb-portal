from django.apps import AppConfig


class ShippingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shipping'  # Changed from 'apps.shipping' to match the app name in INSTALLED_APPS
