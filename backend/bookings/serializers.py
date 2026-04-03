from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "member",
            "unit",
            "booking_type",
            "status",
            "start_date",
            "end_date",
            "payment_deadline",
            "notes",
        ]
        read_only_fields = ["id", "payment_deadline"]
