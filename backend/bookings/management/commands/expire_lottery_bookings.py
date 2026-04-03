from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingStatus, BookingType


class Command(BaseCommand):
    help = "إنهاء حجوزات القرعة غير المسددة بعد انتهاء المهلة"

    def handle(self, *args, **options) -> None:
        today = timezone.localdate()
        queryset = Booking.objects.filter(
            booking_type=BookingType.LOTTERY,
            status=BookingStatus.PENDING_PAYMENT,
            payment_deadline__lt=today,
        )
        expired_count = 0
        with transaction.atomic():
            for booking in queryset:
                booking.status = BookingStatus.EXPIRED
                booking.save()
                expired_count += 1
        self.stdout.write(f"تم إنهاء {expired_count} حجز قرعة")
