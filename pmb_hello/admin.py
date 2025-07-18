from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserCreationForm

# Custom User Creation Form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
    )

# Import the custom admin site from shipping
from shipping.admin_index import custom_admin_site as shipping_admin_site

# Set the custom admin site as the default admin site
admin.site = shipping_admin_site

# Unregister the default UserAdmin
admin.site.unregister(User)

# Register models with the custom admin site
shipping_admin_site.register(Group, GroupAdmin)
shipping_admin_site.register(User, CustomUserAdmin)

# Export the custom admin site for use in URLs
custom_admin_site = shipping_admin_site
