from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("membership_no", "full_name", "phone", "is_active", "created_at")
    search_fields = ("membership_no", "full_name", "phone", "email")
    list_filter = ("is_active",)
