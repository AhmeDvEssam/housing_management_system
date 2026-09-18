from django.contrib import admin
from .models import Payment, Contract

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["booking", "amount", "status", "method", "paid_at"]
    list_filter = ["status", "method"]
    search_fields = ["booking__guest_name", "reference_no"]

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["contract_no", "booking", "issued_at", "signed_at"]
    search_fields = ["contract_no"]
