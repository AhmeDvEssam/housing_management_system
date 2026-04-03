# Generated manually for initial schema
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Member",
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
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث"),
                ),
                (
                    "membership_no",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="رقم العضوية"
                    ),
                ),
                (
                    "full_name",
                    models.CharField(max_length=200, verbose_name="اسم العضو"),
                ),
                (
                    "phone",
                    models.CharField(blank=True, max_length=30, verbose_name="رقم الهاتف"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="البريد الإلكتروني"),
                ),
                (
                    "national_id",
                    models.CharField(blank=True, max_length=20, verbose_name="الرقم القومي"),
                ),
                (
                    "address",
                    models.CharField(blank=True, max_length=255, verbose_name="العنوان"),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="نشط"),
                ),
            ],
            options={
                "verbose_name": "عضو",
                "verbose_name_plural": "الأعضاء",
            },
        ),
    ]
