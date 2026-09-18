from django.db import models
from django.conf import settings

class AuditAction(models.TextChoices):
    CREATE = "CREATE", "إضافة"
    UPDATE = "UPDATE", "تعديل"
    DELETE = "DELETE", "حذف"
    LOGIN = "LOGIN", "تسجيل دخول"

class AuditLog(models.Model):
    timestamp = models.DateTimeField("التوقيت", auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="المستخدم"
    )
    action = models.CharField("العملية", max_length=100, choices=AuditAction.choices)
    object_type = models.CharField("نوع البيانات", max_length=100, blank=True)
    object_id = models.CharField("رقم السجل", max_length=50, blank=True)
    message = models.TextField("التفاصيل")
    metadata = models.JSONField("بيانات إضافية", null=True, blank=True)

    class Meta:
        verbose_name = "سجل الرقابة"
        verbose_name_plural = "سجلات الرقابة"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.timestamp} - {self.get_action_display()} - {self.user}"
