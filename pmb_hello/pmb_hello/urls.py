"""
URL configuration for pmb_hello project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Main site URLs
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('categories/', include('category.urls', namespace='category')),
    path('shipping/', include('shipping.urls', namespace='shipping')),
    
    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    
    # API URLs - all API endpoints are under /api/
    path('api/', include('api.urls')),  # Includes all API endpoints and documentation
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
