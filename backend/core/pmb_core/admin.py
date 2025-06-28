from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group, User

# Import the custom admin site from shipping
from shipping.admin_index import custom_admin_site as shipping_admin_site

# Set the custom admin site as the default admin site
admin.site = shipping_admin_site

# Register models with the custom admin site
shipping_admin_site.register(Group, GroupAdmin)
shipping_admin_site.register(User, UserAdmin)

# Export the custom admin site for use in URLs
custom_admin_site = shipping_admin_site
