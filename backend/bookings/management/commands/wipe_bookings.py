import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from django.core.management.base import BaseCommand
from bookings.models import Booking, BookingDay, Companion, Contract, LotteryResult

class Command(BaseCommand):
    help = 'Wipe all imported bookings and reset sync to start fresh.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("سيتم مسح جميع الحجوزات، أيام الحجوزات، المرافقين، والعقود..."))
        
        # 1. Delete all Bookings (Cascade will delete BookingDay, Contract, Companion)
        deleted_count, details = Booking.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(f"تم مسح الحجوزات بنجاح. التفاصيل: {details}"))
        
        # 2. Delete LotteryResults if the user wants them wiped (Optional)
        # Uncomment if we want to wipe lottery too. Since they can wipe it from Excel upload, let's leave it optional.
        # LotteryResult.objects.all().delete()

        # 3. Reset last_sync_date.txt
        sync_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "scripts", "last_sync_date.txt")
        if os.path.exists(sync_file):
            with open(sync_file, "w") as f:
                f.write("2000-01-01 00:00:00")
            self.stdout.write(self.style.SUCCESS("تم تصفير تاريخ المزامنة الذكية (Smart Sync) بنجاح."))
            
        self.stdout.write(self.style.SUCCESS("جاهز الآن لتشغيل python backend/scripts/smart_sync.py من جديد!"))
