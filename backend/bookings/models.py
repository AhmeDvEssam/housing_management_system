from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from audit.utils import log_event
from inventory.models import Unit
from members.models import Member


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True


class BookingStatus(models.TextChoices):
    DRAFT = "DRAFT", "مسودة"
    HELD = "HELD", "محجوز مؤقتًا"
    PENDING_PAYMENT = "PENDING_PAYMENT", "منتظر السداد"
    CONFIRMED = "CONFIRMED", "مؤكد"
    CHECKED_IN = "CHECKED_IN", "مقيم"
    CHECKED_OUT = "CHECKED_OUT", "تم الإخلاء"
    CANCELLED = "CANCELLED", "ملغي"
    EXPIRED = "EXPIRED", "منتهي (عدم سداد)"


class BookingType(models.TextChoices):
    STANDARD = "STANDARD", "حجز عادي"
    LOTTERY = "LOTTERY", "قرعة"


ACTIVE_BOOKING_STATUSES = {
    BookingStatus.PENDING_PAYMENT,
    BookingStatus.CONFIRMED,
    BookingStatus.CHECKED_IN,
}

ALLOWED_TRANSITIONS = {
    BookingStatus.DRAFT: {BookingStatus.HELD, BookingStatus.CANCELLED},
    BookingStatus.HELD: {BookingStatus.PENDING_PAYMENT, BookingStatus.CANCELLED},
    BookingStatus.PENDING_PAYMENT: {
        BookingStatus.CONFIRMED,
        BookingStatus.EXPIRED,
        BookingStatus.CANCELLED,
    },
    BookingStatus.CONFIRMED: {BookingStatus.CHECKED_IN, BookingStatus.CANCELLED},
    BookingStatus.CHECKED_IN: {BookingStatus.CHECKED_OUT},
    BookingStatus.CHECKED_OUT: set(),
    BookingStatus.CANCELLED: set(),
    BookingStatus.EXPIRED: set(),
}


class Booking(TimeStampedModel):
    member = models.ForeignKey(
        Member, verbose_name="العضو", on_delete=models.PROTECT, related_name="bookings"
    )
    unit = models.ForeignKey(
        Unit, verbose_name="الوحدة", on_delete=models.PROTECT, related_name="bookings"
    )
    booking_type = models.CharField(
        "نوع الحجز",
        max_length=20,
        choices=BookingType.choices,
        default=BookingType.STANDARD,
    )
    status = models.CharField(
        "الحالة",
        max_length=30,
        choices=BookingStatus.choices,
        default=BookingStatus.DRAFT,
    )
    start_date = models.DateField("تاريخ البداية")
    end_date = models.DateField("تاريخ النهاية")
    payment_deadline = models.DateField("آخر موعد للسداد", null=True, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        indexes = [
            models.Index(fields=["unit", "start_date", "end_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.member} - {self.unit}"

    def clean(self) -> None:
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError(
                {"end_date": "تاريخ النهاية يجب أن يكون بعد تاريخ البداية"}
            )
        if self.pk:
            previous_status = (
                Booking.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
            self._validate_status_transition(previous_status)
        if (
            self.status in ACTIVE_BOOKING_STATUSES
            and self.unit_id
            and self.start_date
            and self.end_date
        ):
            days = list(self.iter_days())
            if not days:
                raise ValidationError(
                    {"end_date": "يجب أن يغطي الحجز يومًا واحدًا على الأقل"}
                )
            qs = BookingDay.objects.filter(unit=self.unit, day__in=days)
            if self.pk:
                qs = qs.exclude(booking=self)
            conflicts = qs.exists()
            if conflicts:
                raise ValidationError("يوجد تعارض في الأيام المطلوبة")

    def iter_days(self):
        current = self.start_date
        while current < self.end_date:
            yield current
            current += timedelta(days=1)

    def _validate_status_transition(self, previous_status: str | None) -> None:
        if previous_status is None or previous_status == self.status:
            return
        allowed = ALLOWED_TRANSITIONS.get(previous_status, set())
        if self.status not in allowed:
            previous_label = BookingStatus(previous_status).label
            new_label = BookingStatus(self.status).label
            raise ValidationError(
                {"status": f"لا يمكن الانتقال من {previous_label} إلى {new_label}"}
            )

    def _apply_lottery_defaults(self) -> None:
        if self.booking_type != BookingType.LOTTERY:
            return
        if self._state.adding:
            self.status = BookingStatus.PENDING_PAYMENT
        if self.start_date and not self.payment_deadline:
            self.payment_deadline = self.start_date - timedelta(days=14)

    def _set_booking_days(self) -> None:
        days = list(self.iter_days())
        if not days:
            raise ValidationError(
                {"end_date": "يجب أن يغطي الحجز يومًا واحدًا على الأقل"}
            )
        conflicts = (
            BookingDay.objects.filter(unit=self.unit, day__in=days)
            .exclude(booking=self)
            .exists()
        )
        if conflicts:
            raise ValidationError("يوجد تعارض في الأيام المطلوبة")
        BookingDay.objects.filter(booking=self).delete()
        try:
            BookingDay.objects.bulk_create(
                [BookingDay(booking=self, unit=self.unit, day=day) for day in days]
            )
        except IntegrityError as exc:
            raise ValidationError("يوجد تعارض في الأيام المطلوبة") from exc

    def save(self, *args, **kwargs) -> None:
        is_new = self.pk is None
        previous_status = None
        if self.pk:
            previous_status = (
                Booking.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
        self._apply_lottery_defaults()
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.status in ACTIVE_BOOKING_STATUSES:
                self._set_booking_days()
            else:
                BookingDay.objects.filter(booking=self).delete()
        if is_new:
            log_event(
                action="booking_created",
                object_type="Booking",
                object_id=str(self.pk),
                message="تم إنشاء حجز جديد",
                metadata={"status": self.status},
            )
        elif previous_status and previous_status != self.status:
            log_event(
                action="booking_status_changed",
                object_type="Booking",
                object_id=str(self.pk),
                message=(
                    f"تم تغيير حالة الحجز من "
                    f"{BookingStatus(previous_status).label} إلى "
                    f"{BookingStatus(self.status).label}"
                ),
                metadata={"from": previous_status, "to": self.status},
            )


class BookingDay(models.Model):
    booking = models.ForeignKey(
        Booking,
        verbose_name="الحجز",
        on_delete=models.CASCADE,
        related_name="days",
    )
    unit = models.ForeignKey(
        Unit,
        verbose_name="الوحدة",
        on_delete=models.CASCADE,
        related_name="booking_days",
    )
    day = models.DateField("اليوم")

    class Meta:
        verbose_name = "يوم حجز"
        verbose_name_plural = "أيام الحجز"
        constraints = [
            models.UniqueConstraint(
                fields=["unit", "day"], name="unique_booking_day_per_unit"
            )
        ]
        indexes = [models.Index(fields=["day"]), models.Index(fields=["unit", "day"])]

    def __str__(self) -> str:
        return f"{self.unit} - {self.day.strftime('%d-%m-%Y')}"
