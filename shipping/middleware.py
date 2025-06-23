from django.utils import timezone
import pytz
from django.utils.deprecation import MiddlewareMixin

class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware to ensure all datetime objects are timezone-aware.
    Converts all naive datetimes to timezone-aware in the project's timezone.
    """
    def process_request(self, request):
        # Only process if not already processed
        if not hasattr(request, '_timezone_processed'):
            request._timezone_processed = True
            # Activate the project's timezone
            timezone.activate(pytz.timezone('America/Los_Angeles'))

    def process_response(self, request, response):
        # Only process if we set the _timezone_processed flag
        if hasattr(request, '_timezone_processed'):
            # Clean up our marker
            delattr(request, '_timezone_processed')
            # Make sure to deactivate the timezone when the response is processed
            timezone.deactivate()
        return response
