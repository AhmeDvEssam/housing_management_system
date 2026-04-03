from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True


class Club(TimeStampedModel):
    name = models.CharField("اسم النادي", max_length=200, unique=True)
    city = models.CharField("المدينة", max_length=100, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "نادي"
        verbose_name_plural = "الأندية"

    def __str__(self) -> str:
        return self.name


class BuildingType(models.TextChoices):
    BUILDING = "BUILDING", "مبنى"
    HOTEL = "HOTEL", "فندق"
    OTHER = "OTHER", "أخرى"


class Building(TimeStampedModel):
    club = models.ForeignKey(
        Club, verbose_name="النادي", on_delete=models.CASCADE, related_name="buildings"
    )
    name = models.CharField("اسم المبنى", max_length=200)
    building_type = models.CharField(
        "نوع المبنى",
        max_length=20,
        choices=BuildingType.choices,
        default=BuildingType.BUILDING,
    )
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "name"], name="unique_building_per_club"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.club.name}"


class Floor(TimeStampedModel):
    building = models.ForeignKey(
        Building,
        verbose_name="المبنى",
        on_delete=models.CASCADE,
        related_name="floors",
    )
    level_number = models.IntegerField("رقم الدور")
    label = models.CharField("اسم الدور", max_length=100, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        constraints = [
            models.UniqueConstraint(
                fields=["building", "level_number"], name="unique_floor_per_building"
            )
        ]

    def __str__(self) -> str:
        name = self.label or f"دور {self.level_number}"
        return f"{name} - {self.building.name}"


class UnitType(models.TextChoices):
    ROOM = "ROOM", "غرفة"
    APARTMENT = "APARTMENT", "شقة"
    SUITE = "SUITE", "جناح"


class Orientation(models.TextChoices):
    BAHARI = "BAHARI", "بحري"
    QIBLI = "QIBLI", "قبلي"
    SEA_VIEW = "SEA_VIEW", "إطلالة بحر"
    BACK_VIEW = "BACK_VIEW", "إطلالة خلفية"


class Unit(TimeStampedModel):
    floor = models.ForeignKey(
        Floor, verbose_name="الدور", on_delete=models.CASCADE, related_name="units"
    )
    unit_no = models.CharField("رقم الوحدة", max_length=50)
    unit_type = models.CharField(
        "نوع الوحدة", max_length=20, choices=UnitType.choices
    )
    capacity = models.PositiveIntegerField("السعة", default=1)
    orientation = models.CharField(
        "الاتجاه", max_length=20, choices=Orientation.choices, blank=True
    )
    is_bookable = models.BooleanField("قابلة للحجز", default=True)
    is_maintenance = models.BooleanField("تحت الصيانة", default=False)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "وحدة"
        verbose_name_plural = "الوحدات"
        constraints = [
            models.UniqueConstraint(
                fields=["floor", "unit_no"], name="unique_unit_per_floor"
            )
        ]

    def __str__(self) -> str:
        return f"{self.unit_no} - {self.floor.building.name}"
