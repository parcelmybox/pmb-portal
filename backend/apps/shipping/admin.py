from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.safestring import mark_safe
from .models import ShippingAddress, Shipment, ShipmentItem, TrackingEvent, Bill
from .admin_views import billing_dashboard
from .admin_index import get_billing_stats

# Get the admin instance
site = admin.site

# Inline Models
class ShipmentItemInline(admin.TabularInline):
    model = ShipmentItem
    extra = 1
    fields = ('name', 'quantity', 'description')
    show_change_link = True

class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 1
    readonly_fields = ('timestamp',)
    fields = ('status', 'location', 'description', 'timestamp')

# Register models with the custom admin site
@admin.register(ShippingAddress, site=site)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'formatted_address', 'is_default')
    list_filter = ('country', 'state', 'is_default')
    search_fields = ('user__username', 'first_name', 'last_name', 'address_line1', 'city', 'postal_code', 'phone_number')
    list_select_related = ('user',)
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return mark_safe(f'<a href="{url}">{obj.user.username}</a>')
        return "-"
    user_link.short_description = 'User'
    
    def formatted_address(self, obj):
        return f"{obj.address_line1}, {obj.city}, {obj.state} {obj.postal_code}, {obj.country}"
    formatted_address.short_description = 'Address'

@admin.register(Shipment, site=site)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number_link', 'status_badge', 'sender_info', 'recipient_info', 
                   'shipping_date', 'delivery_date', 'shipping_cost_display', 'created_at')
    list_filter = ('status', 'package_type', 'courier_service', 'shipping_date', 'created_at')
    search_fields = ('tracking_number', 'sender_address__address_line1', 
                    'recipient_address__address_line1', 'sender_first_name', 'recipient_first_name')
    list_select_related = ('sender_address', 'recipient_address')
    date_hierarchy = 'created_at'
    inlines = [ShipmentItemInline, TrackingEventInline]
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Shipment Information', {
            'fields': ('tracking_number', 'status', 'package_type', 'courier_service')
        }),
        ('Sender Details', {
            'fields': ('sender_address', 'sender_first_name', 'sender_last_name')
        }),
        ('Recipient Details', {
            'fields': ('recipient_address', 'recipient_first_name', 'recipient_last_name')
        }),
        ('Package Details', {
            'fields': ('weight', 'length', 'width', 'height', 'shipping_cost')
        }),
        ('Dates', {
            'fields': ('shipping_date', 'delivery_date', 'created_at', 'updated_at')
        }),
    )
    
    def tracking_number_link(self, obj):
        url = reverse('admin:shipping_shipment_change', args=[obj.id])
        return mark_safe(f'<a href="{url}">{obj.tracking_number}</a>')
    tracking_number_link.short_description = 'Tracking #'
    tracking_number_link.admin_order_field = 'tracking_number'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'secondary',
            'processing': 'info',
            'in_transit': 'primary',
            'out_for_delivery': 'warning',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        color = status_colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def sender_info(self, obj):
        return f"{obj.sender_first_name} {obj.sender_last_name}"
    sender_info.short_description = 'Sender'
    
    def recipient_info(self, obj):
        return f"{obj.recipient_first_name} {obj.recipient_last_name}"
    recipient_info.short_description = 'Recipient'
    
    def shipping_cost_display(self, obj):
        return f"${obj.shipping_cost}" if obj.shipping_cost else "-"
    shipping_cost_display.short_description = 'Cost'
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

@admin.register(ShipmentItem, site=site)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment_link', 'name', 'quantity', 'description_short')
    list_filter = ('shipment__status',)
    search_fields = ('name', 'description', 'shipment__tracking_number')
    list_select_related = ('shipment',)
    
    def shipment_link(self, obj):
        url = reverse('admin:shipping_shipment_change', args=[obj.shipment.id])
        return mark_safe(f'<a href="{url}">{obj.shipment.tracking_number}</a>')
    shipment_link.short_description = 'Shipment'
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

@admin.register(TrackingEvent, site=site)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment_link', 'status_badge', 'location', 'timestamp', 'description_short')
    list_filter = ('status', 'location', 'timestamp')
    search_fields = ('shipment__tracking_number', 'description', 'location')
    date_hierarchy = 'timestamp'
    list_select_related = ('shipment',)
    
    def shipment_link(self, obj):
        url = reverse('admin:shipping_shipment_change', args=[obj.shipment.id])
        return mark_safe(f'<a href="{url}">{obj.shipment.tracking_number}</a>')
    shipment_link.short_description = 'Shipment'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'secondary',
            'processing': 'info',
            'in_transit': 'primary',
            'out_for_delivery': 'warning',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        color = status_colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

@admin.register(Bill, site=site)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice_number', 'customer_link', 'amount_display', 'status_badge', 
                   'created_at', 'due_date', 'is_overdue_display')
    list_filter = ('status', 'created_at', 'due_date', 'payment_method')
    search_fields = ('customer__username', 'description', 'invoice_number')
    date_hierarchy = 'created_at'
    change_list_template = 'admin/billing_dashboard.html'
    readonly_fields = ('created_at', 'updated_at', 'paid_at')
    list_select_related = ('customer', 'shipment')
    actions = ['mark_as_paid', 'export_to_csv']
    
    def invoice_number(self, obj):
        return f"INV-{obj.id:06d}"
    invoice_number.short_description = 'Invoice #'
    invoice_number.admin_order_field = 'id'
    
    def customer_link(self, obj):
        if obj.customer:
            url = reverse('admin:auth_user_change', args=[obj.customer.id])
            return mark_safe(f'<a href="{url}">{obj.customer.username}</a>')
        return "-"
    customer_link.short_description = 'Customer'
    
    def amount_display(self, obj):
        return f"${obj.amount:.2f}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        status_colors = {
            'draft': 'secondary',
            'sent': 'info',
            'paid': 'success',
            'overdue': 'warning',
            'cancelled': 'danger'
        }
        color = status_colors.get(obj.status, 'secondary')
        return mark_safe(f'<span class="badge bg-{color}">{obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def is_overdue_display(self, obj):
        if obj.is_overdue():
            return mark_safe('<span class="text-danger">Yes</span>')
        return 'No'
    is_overdue_display.short_description = 'Overdue'
    is_overdue_display.boolean = True
    
    @admin.action(description='Mark selected bills as paid')
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid', paid_at=timezone.now())
        self.message_user(request, f"{updated} bill(s) marked as paid.")
    
    @admin.action(description='Export selected bills to CSV')
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import io
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=bills_export.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Invoice #', 'Customer', 'Amount', 'Status', 'Created', 'Due Date', 'Paid'])
        
        for bill in queryset:
            writer.writerow([
                f"INV-{bill.id:06d}",
                bill.customer.username if bill.customer else '',
                f"${bill.amount:.2f}",
                bill.get_status_display(),
                bill.created_at.strftime('%Y-%m-%d'),
                bill.due_date.strftime('%Y-%m-%d') if bill.due_date else '',
                'Yes' if bill.paid_at else 'No'
            ])
        
        return response
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['billing_stats'] = get_billing_stats()
        return super().changelist_view(request, extra_context=extra_context)
