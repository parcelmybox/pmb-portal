from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

def test_auth(request):
    """
    A simple view to test authentication status.
    Returns a JSON response with the current user's authentication status.
    """
    if request.user.is_authenticated:
        return HttpResponse(f"Authenticated as {request.user.username}")
    return HttpResponse("Not authenticated", status=401)

@login_required
def test_login_required(request):
    """
    A view that requires login to access.
    Used to test the @login_required decorator.
    """
    return HttpResponse(f"This is a protected view. Welcome, {request.user.username}!")
