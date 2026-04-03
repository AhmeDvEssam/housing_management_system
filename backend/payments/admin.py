from django.contrib import admin

from .models import Payment, Contract


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "amount",
        "status",
        "method",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "method")
    search_fields = (
        "booking__member__full_name",
        "booking__member__membership_no",
        "booking__unit__unit_no",
        "reference_no",
    )


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_no", "booking", "issued_at", "signed_at", "print_contract")
    search_fields = ("contract_no", "booking__member__full_name")
    list_filter = ("issued_at",)

    def print_contract(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse("contract-detail", args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">طباعة</a>', url)
    print_contract.short_description = "طباعة العقد"
