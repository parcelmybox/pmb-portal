from django.apps import AppConfig


class CategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.category'
    label = 'category'  # This is the label used in the database
    verbose_name = 'Category'
