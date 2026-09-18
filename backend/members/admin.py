from django.contrib import admin
from .models import Member, FamilyMember, MemberStatusLog

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1

class MemberStatusLogInline(admin.TabularInline):
    model = MemberStatusLog
    readonly_fields = ["changed_at", "changed_by"]
    extra = 0
    can_delete = False

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["membership_no", "full_name", "rank", "phone", "is_active"]
    search_fields = ["membership_no", "full_name", "national_id"]
    list_filter = ["is_active", "rank", "job_type"]
    ordering = ["-id"]
    inlines = [FamilyMemberInline, MemberStatusLogInline]

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "relation", "member"]
    search_fields = ["name", "member__full_name"]

@admin.register(MemberStatusLog)
class MemberStatusLogAdmin(admin.ModelAdmin):
    list_display = ["member", "old_status", "new_status", "changed_at"]
    readonly_fields = ["changed_at"]
