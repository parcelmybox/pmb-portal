from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import ShippingAddress, Shipment, ShipmentItem, TrackingEvent, Bill, SupportRequest, SupportRequestHistory
from django.utils import timezone
from .admin_index import custom_admin_site
from .admin_views import billing_dashboard
from .admin_index import get_billing_stats

# Use our custom admin site instance
site = custom_admin_site

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


class SupportRequestHistoryInline(admin.TabularInline):
    model = SupportRequestHistory
    extra = 0
    readonly_fields = ('user', 'action', 'details', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(SupportRequest, site=site)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'subject', 'name', 'contact_info', 'request_type_display', 'status_display', 'assigned_to_display', 'created_at')
    list_filter = ('status', 'request_type', 'created_at', 'assigned_to')
    search_fields = ('ticket_number', 'subject', 'name', 'email', 'phone', 'message')
    list_select_related = ('assigned_to', 'created_by', 'shipment')
    date_hierarchy = 'created_at'
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'resolved_at')
    inlines = [SupportRequestHistoryInline]
    actions = ['assign_to_me', 'mark_in_progress', 'mark_resolved', 'mark_closed']
    list_per_page = 20
    change_form_template = 'admin/shipping/supportrequest/change_form.html'
    
    def request_type_display(self, obj):
        """Display the request type with a badge"""
        type_map = {
            'general': 'secondary',
            'technical': 'info',
            'billing': 'warning',
            'shipment': 'primary',
            'other': 'success'
        }
        badge_class = type_map.get(obj.request_type, 'secondary')
        display_text = obj.get_request_type_display()
        return mark_safe(f'<span class="badge bg-{badge_class}">{display_text.capitalize()}</span>')
    request_type_display.short_description = 'Type of Support Request'
    request_type_display.admin_order_field = 'request_type'
    
    fieldsets = (
        ('Request Information', {
            'classes': ('wide', 'extrapretty', 'two-columns'),
            'fields': [
                ('ticket_number', 'status'),
                ('assigned_to', 'request_type'),
                ('name', 'email'),
                ('phone', 'shipment'),
                'subject',  # Full width field
                'message',  # Full width field
                'attachment',  # Full width field
            ]
        }),
        ('Resolution', {
            'classes': ('wide', 'extrapretty', 'two-columns'),
            'fields': [
                'resolution_notes',  # Full width field
                ('created_at', 'updated_at'),
                'resolved_at'
            ]
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Add custom CSS class to the first fieldset for two-column layout
        if fieldsets and fieldsets[0] and fieldsets[0][0] == 'Request Information':
            fieldsets = list(fieldsets)
            fieldsets[0] = list(fieldsets[0])
            fieldsets[0][1]['classes'] = list(fieldsets[0][1].get('classes', [])) + ['two-columns']
        return fieldsets
    
    def status_display(self, obj):
        status_colors = {
            'open': 'gray',
            'in_progress': 'blue',
            'resolved': 'green',
            'closed': 'black',
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 4px; text-align: center; display: inline-block; white-space: nowrap;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def assigned_to_display(self, obj):
        if not obj.assigned_to:
            return 'Unassigned'
        return obj.assigned_to.get_full_name() or obj.assigned_to.username or str(obj.assigned_to)
    assigned_to_display.short_description = 'Assigned To'
    
    def created_by_display(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else 'System'
    created_by_display.short_description = 'Created By'
    
    def contact_info(self, obj):
        if obj.phone:
            return f"{obj.phone} / {obj.email}" if obj.email else obj.phone
        return obj.email if obj.email else '-'
    contact_info.short_description = 'Mobile No/Email'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only filter by assigned_to if the user is not a staff member
        if request.user.is_superuser or request.user.is_staff:
            return qs
        return qs.filter(assigned_to=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_to':
            # Only show staff users in the assigned_to dropdown
            kwargs['queryset'] = get_user_model().objects.filter(is_staff=True).order_by('first_name', 'last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New ticket
            obj.created_by = request.user
        
        # Create history entry for status changes
        if change and 'status' in form.changed_data:
            action = f'Status changed to {obj.get_status_display()}'
            SupportRequestHistory.objects.create(
                support_request=obj,
                user=request.user,
                action=action,
                details=f'Status was changed from {form.initial.get("status", "unknown")} to {obj.status}.'
            )
        
        # Create history entry for assignment changes
        if change and 'assigned_to' in form.changed_data:
            old_assignee = form.initial.get('assigned_to')
            new_assignee = obj.assigned_to
            action = f'Assigned to {new_assignee.get_full_name() if new_assignee else "Unassigned"}'
            details = f'Changed from {old_assignee.get_full_name() if old_assignee else "Unassigned"} to {new_assignee.get_full_name() if new_assignee else "Unassigned"}'
            SupportRequestHistory.objects.create(
                support_request=obj,
                user=request.user,
                action=action,
                details=details
            )
        
        super().save_model(request, obj, form, change)
    
    # Custom actions
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        for ticket in queryset:
            SupportRequestHistory.objects.create(
                support_request=ticket,
                user=request.user,
                action='Assigned to me',
                details=f'Ticket was assigned to {request.user.get_full_name()}'
            )
        self.message_user(request, f'Successfully assigned {updated} ticket(s) to you.')
    assign_to_me.short_description = 'Assign selected tickets to me'
    
    def mark_in_progress(self, request, queryset):
        updated = 0
        for ticket in queryset:
            if ticket.status != 'in_progress':
                ticket.status = 'in_progress'
                ticket.save()
                updated += 1
                SupportRequestHistory.objects.create(
                    support_request=ticket,
                    user=request.user,
                    action='Marked as In Progress',
                    details='Ticket status changed to In Progress'
                )
        self.message_user(request, f'Successfully marked {updated} ticket(s) as In Progress.')
    mark_in_progress.short_description = 'Mark selected tickets as In Progress'
    
    def mark_resolved(self, request, queryset):
        updated = 0
        for ticket in queryset:
            if ticket.status != 'resolved':
                ticket.status = 'resolved'
                ticket.resolved_at = timezone.now()
                ticket.save()
                updated += 1
                SupportRequestHistory.objects.create(
                    support_request=ticket,
                    user=request.user,
                    action='Marked as Resolved',
                    details='Ticket status changed to Resolved'
                )
        self.message_user(request, f'Successfully marked {updated} ticket(s) as Resolved.')
    mark_resolved.short_description = 'Mark selected tickets as Resolved'
    
    def mark_closed(self, request, queryset):
        updated = 0
        for ticket in queryset:
            if ticket.status != 'closed':
                ticket.status = 'closed'
                if not ticket.resolved_at:
                    ticket.resolved_at = timezone.now()
                ticket.save()
                updated += 1
                SupportRequestHistory.objects.create(
                    support_request=ticket,
                    user=request.user,
                    action='Marked as Closed',
                    details='Ticket status changed to Closed'
                )
        self.message_user(request, f'Successfully closed {updated} ticket(s).')
    mark_closed.short_description = 'Close selected tickets'
    
    def get_readonly_fields(self, request, obj=None):
        # Make certain fields read-only based on user permissions
        if obj:  # Editing an existing object
            readonly_fields = list(self.readonly_fields)
            if not request.user.is_superuser:
                readonly_fields.extend(['status', 'assigned_to'])
            return readonly_fields
        return self.readonly_fields
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # Only show assign to me action for non-superusers
            return {'assign_to_me': actions.get('assign_to_me')}
        return actions
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_close_button'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
        
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/calendar.js',
            'admin/js/admin/DateTimeShortcuts.js',
        )
        
        @property
        def media(self):
            media = super().media
            media._css = media._css or {}
            media._css['all'] = media._css.get('all', []) + [
                'shipping/css/admin_supportrequest.css',
            ]
            return media

# The SupportRequest model is registered using the @admin.register decorator above
