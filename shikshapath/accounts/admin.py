from django.contrib import admin
from .models import CustomUser, AuditLog

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_suspended', 'created_at')
    list_filter = ('role', 'is_suspended', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'suspended_at')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('personal info', {'fields': ('first_name', 'last_name', 'bio', 'phone_number', 'profile_picture')}),
        ('Account Status', {'fields': ('is_suspended', 'suspended_at')}),
        ('permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_login')}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor_email', 'target_user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor_email', 'target_user__email')
    readonly_fields = ('timestamp', 'actor', 'actor_email', 'action', 'details')

def has_add_permission(self, request):
        # Disable add permission
        return False

def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False