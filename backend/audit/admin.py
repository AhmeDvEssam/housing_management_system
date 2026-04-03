from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "actor", "created_at")
    list_filter = ("object_type", "action", "created_at")
    search_fields = ("object_id", "message", "actor__username")
