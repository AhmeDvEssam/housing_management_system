from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Expires lottery bookings past their payment deadline'

    def handle(self, *args, **options):
        today = timezone.localdate()
        expired = Booking.objects.filter(
            booking_type='LOTTERY',
            payment_deadline__lt=today,
        ).exclude(
            status__in=['ملغي', 'مدفوع', 'مؤكد']
        )
        count = expired.count()
        for b in expired:
            b.status = 'ملغي'
            b.save()
        self.stdout.write(self.style.SUCCESS(f'Expired {count} lottery bookings'))
