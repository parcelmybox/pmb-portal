from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms

# Import the custom admin site from shipping
from shipping.admin_index import custom_admin_site as shipping_admin_site

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

# Unregister the default User and Group models first
admin.site.unregister(User)
admin.site.unregister(Group)

# Register User and Group models with the custom admin site
shipping_admin_site.register(User, CustomUserAdmin)
shipping_admin_site.register(Group, GroupAdmin)

# Set the custom admin site as the default admin site
admin.site = shipping_admin_site

# Export the custom admin site for use in URLs
custom_admin_site = shipping_admin_site
