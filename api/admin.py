from django.contrib import admin
from .models import PickupRequest, SupportRequest

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'date', 'time', 'package_type', 'created_at')
    search_fields = ('name', 'city', 'phone_number', 'email')
    list_filter = ('package_type', 'city', 'date')
    ordering = ('-created_at',)

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'created_at')
    search_fields = ('subject', 'message')
    ordering = ('-created_at',)
