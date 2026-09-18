from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from audit.utils import log_event
from bookings.models import Booking

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True

class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "منتظر السداد"
    PAID = "PAID", "تم السداد"

class PaymentMethod(models.TextChoices):
    CASH = "CASH", "نقدي"
    CARD = "CARD", "بطاقة"
    TRANSFER = "TRANSFER", "تحويل بنكي"
    OTHER = "OTHER", "أخرى"

class Payment(TimeStampedModel):
    booking = models.ForeignKey(Booking, verbose_name="الحجز", on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField("المبلغ", max_digits=10, decimal_places=2)
    status = models.CharField("الحالة", max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    method = models.CharField("طريقة السداد", max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    paid_at = models.DateTimeField("تاريخ السداد", null=True, blank=True)
    reference_no = models.CharField("رقم المرجع", max_length=100, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "سداد"
        verbose_name_plural = "المدفوعات"

    def __str__(self) -> str:
        return f"{self.booking} - {self.amount}"

    def clean(self) -> None:
        if self.amount is None or self.amount <= 0:
            raise ValidationError({"amount": "المبلغ يجب أن يكون أكبر من صفر"})

    def _apply_paid_logic(self) -> None:
        if self.status == PaymentStatus.PAID and not self.paid_at:
            self.paid_at = timezone.now()
        if self.status != PaymentStatus.PAID:
            self.paid_at = None

    def _confirm_booking_if_needed(self) -> None:
        if self.status != PaymentStatus.PAID:
            return
        if self.booking.status == "منتظر السداد" or self.booking.status == "مسودة":
            self.booking.status = "مدفوع"
            self.booking.save()

    def save(self, *args, **kwargs) -> None:
        is_new = self.pk is None
        self._apply_paid_logic()
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            self._confirm_booking_if_needed()
        if is_new:
            log_event(action="payment_created", object_type="Payment", object_id=str(self.pk), message="تم تسجيل سداد جديد", metadata={"status": self.status, "booking_id": self.booking_id})

class Contract(TimeStampedModel):
    booking = models.OneToOneField(Booking, verbose_name="الحجز", on_delete=models.PROTECT, related_name="contract")
    contract_no = models.CharField("رقم العقد", max_length=50, unique=True)
    issued_at = models.DateField("تاريخ الإصدار", default=timezone.localdate)
    signed_at = models.DateField("تاريخ التوقيع", null=True, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "عقد"
        verbose_name_plural = "العقود"

    def __str__(self) -> str:
        return f"{self.contract_no}"
