# api/admin.py
from django.contrib import admin
from .models import PickupRequest, PackageDetail

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'phone_number',
        'email',
        'city',
        'date',
        'time',
        'package_type',
        'created_at',
    )
    search_fields = ('name', 'email', 'phone_number', 'city')


@admin.register(PackageDetail)
class PackageDetailAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'pickup_id',        # ← updated to your raw integer field
        'weight',
        'dimensions',
        'packaging_status',
        'created_at',
    )
    list_filter = ('packaging_status',)
    search_fields = ('pickup_id', 'dimensions')
