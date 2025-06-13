from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def is_staff(user):
    return user.is_staff

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('account_login')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('shipping:shipping_home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
