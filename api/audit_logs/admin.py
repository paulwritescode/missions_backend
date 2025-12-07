from django.contrib import admin
from audit_logs.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action_type', 'action_category', 'is_successful', 'flag_suspicious', 'created_at')
    list_filter = ('action_type', 'is_successful', 'flag_suspicious', 'created_at')
    search_fields = ('user__username', 'action_category', 'action_description', 'ip_address')
    readonly_fields = ('user', 'action_type', 'action_category', 'action_description', 'is_successful', 'ip_address', 'flag_suspicious', 'created_at', 'updated_at')
    ordering = ('-created_at',)