# Generated manually for initial schema
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(max_length=100, verbose_name="الإجراء"),
                ),
                (
                    "object_type",
                    models.CharField(max_length=50, verbose_name="نوع الكيان"),
                ),
                (
                    "object_id",
                    models.CharField(max_length=50, verbose_name="معرف الكيان"),
                ),
                (
                    "message",
                    models.TextField(blank=True, verbose_name="الوصف"),
                ),
                (
                    "metadata",
                    models.JSONField(default=dict, blank=True, verbose_name="بيانات إضافية"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="التاريخ"),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_events",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="المستخدم",
                    ),
                ),
            ],
            options={
                "verbose_name": "حدث تدقيق",
                "verbose_name_plural": "سجل التدقيق",
            },
        ),
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(
                fields=["object_type", "object_id"], name="audit_aud_object__9bb3a4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["created_at"], name="audit_aud_created_0d7e27_idx"),
        ),
    ]
