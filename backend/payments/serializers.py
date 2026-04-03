from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "amount",
            "status",
            "method",
            "paid_at",
            "reference_no",
            "notes",
        ]
        read_only_fields = ["id", "paid_at"]
