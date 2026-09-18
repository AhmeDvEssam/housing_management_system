from django.db import models
from bookings.models import Booking

class DailyBookingReport(Booking):
    class Meta:
        proxy = True
        verbose_name = "تقرير الحجوزات عن يوم"
        verbose_name_plural = "تقرير الحجوزات عن يوم"

class FaxReport(Booking):
    class Meta:
        proxy = True
        verbose_name = "تقرير الفاكسات"
        verbose_name_plural = "تقرير الفاكسات"

class VacanciesReport(Booking):
    class Meta:
        proxy = True
        verbose_name = "تقرير الخلوات"
        verbose_name_plural = "تقرير الخلوات"
