from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import os


def user_avatar_path(instance, filename):
    """Generate upload path for user avatars"""
    ext = filename.split('.')[-1]
    filename = f'user_{instance.id}_avatar.{ext}'
    return os.path.join('avatars', filename)


class Permission(models.Model):
    """Custom Permission model for fine-grained access control"""
    
    PERMISSION_CATEGORIES = (
        ('user', 'User Management'),
        ('menu', 'Menu Management'),
        ('order', 'Order Management'),
        ('billing', 'Billing Management'),
        ('table', 'Table Management'),
        ('reservation', 'Reservation Management'),
        ('staff', 'Staff Management'),
        ('customer', 'Customer Management'),
        ('report', 'Reports & Analytics'),
        ('settings', 'System Settings'),
    )
    
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=PERMISSION_CATEGORIES, default='user')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_permission_custom'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category}: {self.name}"


class Role(models.Model):
    """Custom Role model with permissions"""
    
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')
    is_system = models.BooleanField(default=False)  # System roles cannot be deleted
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_role'
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class User(AbstractUser):
    """Custom User model for Restaurant ERP"""
    
    USER_ROLES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('cashier', 'Cashier'),
        ('chef', 'Chef'),
    )

    role = models.CharField(max_length=10, choices=USER_ROLES, default='staff')
    custom_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path, 
        blank=True, 
        null=True,
        help_text="User profile picture"
    )
    avatar_url = models.URLField(max_length=500, blank=True, null=True, help_text="External avatar URL (Google)")
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    
    # Google OAuth fields
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Google OAuth ID")
    auth_provider = models.CharField(max_length=20, default='local', help_text="Authentication provider: local, google")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def get_avatar_url(self):
        """Return avatar URL or default"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        return '/static/images/default-avatar.png'
    
    @property
    def is_locked(self):
        """Check if user account is locked"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def get_all_permissions(self):
        """Get all permissions for this user"""
        if self.is_superuser:
            return Permission.objects.filter(is_active=True)
        
        if self.custom_role:
            return self.custom_role.permissions.filter(is_active=True)
        
        return Permission.objects.none()
    
    def has_permission(self, permission_code):
        """Check if user has specific permission"""
        if self.is_superuser or self.role == 'admin':
            return True
        
        if self.custom_role:
            return self.custom_role.permissions.filter(code=permission_code, is_active=True).exists()
        
        return False
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserActivityLog(models.Model):
    """Log user activities for audit trail"""
    
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('profile_update', 'Profile Update'),
        ('avatar_upload', 'Avatar Upload'),
        ('avatar_delete', 'Avatar Delete'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('role_change', 'Role Change'),
        ('permission_change', 'Permission Change'),
        ('user_create', 'User Created'),
        ('user_update', 'User Updated'),
        ('user_delete', 'User Deleted'),
        ('user_activate', 'User Activated'),
        ('user_deactivate', 'User Deactivated'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    old_data = models.JSONField(blank=True, null=True)  # Store old values for audit
    new_data = models.JSONField(blank=True, null=True)  # Store new values for audit
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_logs')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_user_activity_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.action} - {self.created_at}"


class LoginHistory(models.Model):
    """Track login history"""
    
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    failure_reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_login_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.created_at}"