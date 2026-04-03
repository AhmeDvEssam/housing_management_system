# Generated manually for initial schema
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
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
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=10, verbose_name="المبلغ"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "منتظر السداد"), ("PAID", "تم السداد")],
                        default="PENDING",
                        max_length=20,
                        verbose_name="الحالة",
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("CASH", "نقدي"),
                            ("CARD", "بطاقة"),
                            ("TRANSFER", "تحويل بنكي"),
                            ("OTHER", "أخرى"),
                        ],
                        default="CASH",
                        max_length=20,
                        verbose_name="طريقة السداد",
                    ),
                ),
                (
                    "paid_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="تاريخ السداد"
                    ),
                ),
                (
                    "reference_no",
                    models.CharField(blank=True, max_length=100, verbose_name="رقم المرجع"),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payments",
                        to="bookings.booking",
                        verbose_name="الحجز",
                    ),
                ),
            ],
            options={
                "verbose_name": "سداد",
                "verbose_name_plural": "المدفوعات",
            },
        ),
        migrations.CreateModel(
            name="Contract",
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
                    "contract_no",
                    models.CharField(max_length=50, unique=True, verbose_name="رقم العقد"),
                ),
                (
                    "issued_at",
                    models.DateField(
                        default=django.utils.timezone.localdate, verbose_name="تاريخ الإصدار"
                    ),
                ),
                (
                    "signed_at",
                    models.DateField(
                        blank=True, null=True, verbose_name="تاريخ التوقيع"
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "booking",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contract",
                        to="bookings.booking",
                        verbose_name="الحجز",
                    ),
                ),
            ],
            options={
                "verbose_name": "عقد",
                "verbose_name_plural": "العقود",
            },
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["status"], name="payments_pa_status_5d9b2c_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["paid_at"], name="payments_pa_paid_at_4c0c3b_idx"),
        ),
    ]
