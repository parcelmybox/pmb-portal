from django.http import HttpResponse
from django.conf import settings
import os

def test_static(request):
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    exists = os.path.exists(logo_path)
    return HttpResponse(f"Logo exists at {logo_path}: {exists}")

def test_static_url(request):
    static_url = settings.STATIC_URL
    static_dirs = settings.STATICFILES_DIRS
    static_root = settings.STATIC_ROOT
    return HttpResponse(f"""
        <h1>Static Files Test</h1>
        <p>STATIC_URL: {static_url}</p>
        <p>STATICFILES_DIRS: {static_dirs}</p>
        <p>STATIC_ROOT: {static_root}</p>
        <p>Try accessing the logo at: <a href='{static_url}images/logo.png'>{static_url}images/logo.png</a></p>
        <p>Or try the direct URL: <a href='/static/images/logo.png'>/static/images/logo.png</a></p>
    """)
