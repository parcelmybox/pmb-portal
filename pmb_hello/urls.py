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
from django.urls import path, include
from category import views as category_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shipping/', include('shipping.urls')),
    path('categories/', category_views.category_list, name='category_list'),
    path('shipping-price/', category_views.shipping_price_form, name='shipping_price_form'),
    path('api/shipping-price/', category_views.shipping_price_api, name='shipping_price_api'),
]
