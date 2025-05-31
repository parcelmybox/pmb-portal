from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('add/', views.add_category, name='add_category'),
    path('<int:pk>/', views.category_detail, name='category_detail'),
    path('<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('<int:pk>/delete/', views.delete_category, name='delete_category'),
]
