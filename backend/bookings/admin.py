from django.contrib import admin

from .models import Booking, BookingDay


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "unit",
        "booking_type",
        "status",
        "start_date",
        "end_date",
        "payment_deadline",
        "created_at",
    )
    search_fields = (
        "member__full_name",
        "member__membership_no",
        "unit__unit_no",
        "unit__floor__building__name",
    )
    list_filter = ("booking_type", "status", "unit__floor__building__club")
    date_hierarchy = "start_date"


@admin.register(BookingDay)
class BookingDayAdmin(admin.ModelAdmin):
    list_display = ("day", "unit", "booking")
    search_fields = (
        "unit__unit_no",
        "booking__member__full_name",
        "booking__member__membership_no",
    )
    list_filter = ("day", "unit__floor__building__club")
