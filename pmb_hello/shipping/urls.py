from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    path('tracking/', views.tracking, name='tracking'),
    path('addresses/', views.addresses, name='addresses'),
    path('rates/', views.rates, name='rates'),
]
