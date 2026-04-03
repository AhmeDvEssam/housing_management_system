# Generated manually for initial schema
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Club",
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
                    "name",
                    models.CharField(max_length=200, unique=True, verbose_name="اسم النادي"),
                ),
                (
                    "city",
                    models.CharField(blank=True, max_length=100, verbose_name="المدينة"),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
            ],
            options={
                "verbose_name": "نادي",
                "verbose_name_plural": "الأندية",
            },
        ),
        migrations.CreateModel(
            name="Building",
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
                    "name",
                    models.CharField(max_length=200, verbose_name="اسم المبنى"),
                ),
                (
                    "building_type",
                    models.CharField(
                        choices=[
                            ("BUILDING", "مبنى"),
                            ("HOTEL", "فندق"),
                            ("OTHER", "أخرى"),
                        ],
                        default="BUILDING",
                        max_length=20,
                        verbose_name="نوع المبنى",
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buildings",
                        to="inventory.club",
                        verbose_name="النادي",
                    ),
                ),
            ],
            options={
                "verbose_name": "مبنى",
                "verbose_name_plural": "المباني",
            },
        ),
        migrations.CreateModel(
            name="Floor",
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
                    "level_number",
                    models.IntegerField(verbose_name="رقم الدور"),
                ),
                (
                    "label",
                    models.CharField(blank=True, max_length=100, verbose_name="اسم الدور"),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "building",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="floors",
                        to="inventory.building",
                        verbose_name="المبنى",
                    ),
                ),
            ],
            options={
                "verbose_name": "دور",
                "verbose_name_plural": "الأدوار",
            },
        ),
        migrations.CreateModel(
            name="Unit",
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
                    "unit_no",
                    models.CharField(max_length=50, verbose_name="رقم الوحدة"),
                ),
                (
                    "unit_type",
                    models.CharField(
                        choices=[
                            ("ROOM", "غرفة"),
                            ("APARTMENT", "شقة"),
                            ("SUITE", "جناح"),
                        ],
                        max_length=20,
                        verbose_name="نوع الوحدة",
                    ),
                ),
                (
                    "capacity",
                    models.PositiveIntegerField(default=1, verbose_name="السعة"),
                ),
                (
                    "orientation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("BAHARI", "بحري"),
                            ("QIBLI", "قبلي"),
                            ("SEA_VIEW", "إطلالة بحر"),
                            ("BACK_VIEW", "إطلالة خلفية"),
                        ],
                        max_length=20,
                        verbose_name="الاتجاه",
                    ),
                ),
                (
                    "is_bookable",
                    models.BooleanField(default=True, verbose_name="قابلة للحجز"),
                ),
                (
                    "is_maintenance",
                    models.BooleanField(default=False, verbose_name="تحت الصيانة"),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="ملاحظات"),
                ),
                (
                    "floor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="units",
                        to="inventory.floor",
                        verbose_name="الدور",
                    ),
                ),
            ],
            options={
                "verbose_name": "وحدة",
                "verbose_name_plural": "الوحدات",
            },
        ),
        migrations.AddConstraint(
            model_name="building",
            constraint=models.UniqueConstraint(
                fields=("club", "name"), name="unique_building_per_club"
            ),
        ),
        migrations.AddConstraint(
            model_name="floor",
            constraint=models.UniqueConstraint(
                fields=("building", "level_number"), name="unique_floor_per_building"
            ),
        ),
        migrations.AddConstraint(
            model_name="unit",
            constraint=models.UniqueConstraint(
                fields=("floor", "unit_no"), name="unique_unit_per_floor"
            ),
        ),
    ]
