from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner of the object or admin.
        # Check for both user and created_by fields for backward compatibility
        is_owner = False
        if hasattr(obj, 'user') and obj.user:
            is_owner = obj.user == request.user
        elif hasattr(obj, 'created_by') and obj.created_by:
            is_owner = obj.created_by == request.user
            
        return is_owner or request.user.is_staff

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff
