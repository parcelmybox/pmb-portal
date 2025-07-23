from django.utils import timezone
import pytz

class TimezoneAwareRouter:
    """
    Database router that ensures all datetime fields are timezone-aware
    and properly converted to/from the database.
    """
    def db_for_read(self, model, **hints):
        # Just return None - we're not doing any database routing
        return None

    def db_for_write(self, model, **hints):
        # Ensure all datetimes are timezone-aware before saving
        obj = hints.get('instance')
        if obj is not None and not getattr(obj, '_timezone_processed', False):
            try:
                # Mark the object as processed to prevent recursion
                obj._timezone_processed = True
                
                # Process all datetime fields
                for field in obj._meta.fields:
                    if field.get_internal_type() in ('DateTimeField', 'DateField'):
                        value = getattr(obj, field.name, None)
                        if value is not None and timezone.is_naive(value):
                            setattr(obj, field.name, timezone.make_aware(value, timezone=pytz.UTC))
            finally:
                # Clean up our marker
                if hasattr(obj, '_timezone_processed'):
                    delattr(obj, '_timezone_processed')
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None
