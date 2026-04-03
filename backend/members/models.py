from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True


class Member(TimeStampedModel):
    membership_no = models.CharField("رقم العضوية", max_length=50, unique=True)
    full_name = models.CharField("اسم العضو", max_length=200)
    phone = models.CharField("رقم الهاتف", max_length=30, blank=True)
    email = models.EmailField("البريد الإلكتروني", blank=True)
    national_id = models.CharField("الرقم القومي", max_length=20, blank=True)
    address = models.CharField("العنوان", max_length=255, blank=True)
    notes = models.TextField("ملاحظات", blank=True)
    is_active = models.BooleanField("نشط", default=True)

    class Meta:
        verbose_name = "عضو"
        verbose_name_plural = "الأعضاء"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.membership_no})"
