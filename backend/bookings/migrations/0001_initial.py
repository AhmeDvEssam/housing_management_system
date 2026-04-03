# Generated manually for initial schema
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("inventory", "0001_initial"),
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
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
                    "booking_type",
                    models.CharField(
                        choices=[("STANDARD", "حجز عادي"), ("LOTTERY", "قرعة")],
                        default="STANDARD",
                        max_length=20,
                        verbose_name="نوع الحجز",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "مسودة"),
                            ("HELD", "محجوز مؤقتًا"),
                            ("PENDING_PAYMENT", "منتظر السداد"),
                            ("CONFIRMED", "مؤكد"),
                            ("CHECKED_IN", "مقيم"),
                            ("CHECKED_OUT", "تم الإخلاء"),
                            ("CANCELLED", "ملغي"),
                            ("EXPIRED", "منتهي (عدم سداد)"),
                        ],
                        default="DRAFT",
                        max_length=30,
                        verbose_name="الحالة",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(verbose_name="تاريخ البداية"),
                ),
                (
                    "end_date",
                    models.DateField(verbose_name="تاريخ النهاية"),
                ),
                (
                    "payment_deadline",
                    models.DateField(
                        blank=True, null=True, verbose_name="آخر موعد للسداد"
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bookings",
                        to="members.member",
                        verbose_name="العضو",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bookings",
                        to="inventory.unit",
                        verbose_name="الوحدة",
                    ),
                ),
            ],
            options={
                "verbose_name": "حجز",
                "verbose_name_plural": "الحجوزات",
            },
        ),
        migrations.CreateModel(
            name="BookingDay",
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
                    "day",
                    models.DateField(verbose_name="اليوم"),
                ),
                (
                    "booking",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="days",
                        to="bookings.booking",
                        verbose_name="الحجز",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="booking_days",
                        to="inventory.unit",
                        verbose_name="الوحدة",
                    ),
                ),
            ],
            options={
                "verbose_name": "يوم حجز",
                "verbose_name_plural": "أيام الحجز",
            },
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(
                fields=["unit", "start_date", "end_date"], name="bookings_bo_unit_id_8184b4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["status"], name="bookings_bo_status_77cc5b_idx"),
        ),
        migrations.AddConstraint(
            model_name="bookingday",
            constraint=models.UniqueConstraint(
                fields=("unit", "day"), name="unique_booking_day_per_unit"
            ),
        ),
        migrations.AddIndex(
            model_name="bookingday",
            index=models.Index(fields=["day"], name="bookings_bo_day_2a68d5_idx"),
        ),
        migrations.AddIndex(
            model_name="bookingday",
            index=models.Index(
                fields=["unit", "day"], name="bookings_bo_unit_id_7d9aa5_idx"
            ),
        ),
    ]
