from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField("الإجراء", max_length=100)
    object_type = models.CharField("نوع الكيان", max_length=50)
    object_id = models.CharField("معرف الكيان", max_length=50)
    message = models.TextField("الوصف", blank=True)
    metadata = models.JSONField("بيانات إضافية", default=dict, blank=True)
    created_at = models.DateTimeField("التاريخ", auto_now_add=True)

    class Meta:
        verbose_name = "حدث تدقيق"
        verbose_name_plural = "سجل التدقيق"
        indexes = [
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} - {self.object_type}"
