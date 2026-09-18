from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "action_colored", "object_type", "message"]
    list_filter = ["action", "timestamp", "user", "object_type"]
    search_fields = ["message", "object_id", "user__username"]
    readonly_fields = ["timestamp", "user", "action", "object_type", "object_id", "message", "metadata"]
    
    def action_colored(self, obj):
        colors = {
            "CREATE": "green",
            "UPDATE": "blue",
            "DELETE": "red",
            "LOGIN": "gray",
        }
        return format_html('<b style="color: {};">{}</b>', colors.get(obj.action, "black"), obj.get_action_display())
    
    action_colored.short_description = "Ø§Ù„Ø¹Ù…Ù„ÙŠØ©"

    # ØªÙ‚ÙŠÙŠØ¯ Ø§Ù„ÙˆØµÙˆÙ„ Ù„Ù„Ø£Ø¯Ù…Ù† ÙÙ‚Ø· (Superuser)
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False # Ù„Ø§ ÙŠÙ…ÙƒÙ† Ø¥Ø¶Ø§ÙØ© Ø³Ø¬Ù„Ø§Øª ÙŠØ¯ÙˆÙŠØ§Ù‹

    def has_change_permission(self, request, obj=None):
        return False # Ù„Ø§ ÙŠÙ…ÙƒÙ† ØªØ¹Ø¯ÙŠÙ„ Ø§Ù„Ø³Ø¬Ù„Ø§Øª

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser # ÙÙ‚Ø· Ø§Ù„Ø£Ø¯Ù…Ù† ÙŠÙ…Ø³Ø­ Ù„Ùˆ Ø§Ø­ØªØ§Ø¬

    # Ø¥Ø¶Ø§ÙØ© Ù…Ù„Ù CSS Ù„Ù„Ø·Ø¨Ø§Ø¹Ø©
    class Media:
        css = {
            'all': ('admin/css/custom_admin_fixes_v2.css',),
            'print': ('admin/css/print_audit.css',)
        }
