from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipping_form, name='shipping_form'),
    path('result/', views.result_page, name='result_page'),
    path('result/<int:order_id>/', views.result_page, name='result_page'),
    path('api/orders/', views.orders_api, name='orders_api'),


]
