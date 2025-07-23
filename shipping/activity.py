from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivityHistory(models.Model):
    """
    Model to track user activities across the application.
    Can be linked to any model using GenericForeignKey.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional data that might be useful
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Activity History'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
    
    @classmethod
    def log_activity(cls, user, action, obj=None, request=None):
        """
        Helper method to log an activity
        """
        activity = cls(user=user, action=action)
        
        if obj is not None:
            activity.content_object = obj
        
        if request:
            activity.ip_address = request.META.get('REMOTE_ADDR')
            activity.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        activity.save()
        return activity
