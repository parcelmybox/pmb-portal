from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from .models import ShippingAddress, Shipment, ShipmentItem, TrackingEvent
from .models import Bill
from .admin_views import billing_dashboard
from .admin_index import get_billing_stats

# Get the admin site instance
site = admin.site

@admin.register(ShippingAddress, site=site)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address_line1', 'city', 'state', 'country', 'postal_code', 'is_default')
    list_filter = ('country', 'state', 'is_default')
    search_fields = ('user__username', 'address_line1', 'city', 'postal_code')

@admin.register(Shipment, site=site)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'tracking_number', 'status', 'shipping_date', 'delivery_date', 'shipping_cost')
    list_filter = ('status', 'package_type', 'shipping_date')
    search_fields = ('tracking_number', 'sender_address__address_line1', 'recipient_address__address_line1')
    date_hierarchy = 'created_at'

@admin.register(ShipmentItem, site=site)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'name', 'quantity', 'declared_value')
    list_filter = ('shipment__status',)
    search_fields = ('name', 'description', 'shipment__tracking_number')

@admin.register(TrackingEvent, site=site)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment', 'status', 'location', 'timestamp')
    list_filter = ('status', 'location')
    search_fields = ('shipment__tracking_number', 'description')
    date_hierarchy = 'timestamp'

@admin.register(Bill, site=site)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount', 'status', 'created_at', 'due_date', 'is_overdue')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'description')
    date_hierarchy = 'created_at'
    change_list_template = 'admin/billing_dashboard.html'
    
    def changelist_view(self, request, extra_context=None):
        # Use our custom billing dashboard view for the changelist
        return billing_dashboard(request)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['billing_stats'] = get_billing_stats()
        return super().changelist_view(request, extra_context=extra_context)
