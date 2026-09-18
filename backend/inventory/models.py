from django.db import models
from django.core.exceptions import ValidationError

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True

class Club(TimeStampedModel):
    name = models.CharField("اسم النادي", max_length=200, unique=True)
    city = models.CharField("المدينة", max_length=200, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "نادي"
        verbose_name_plural = "الأندية"

    def __str__(self) -> str:
        return self.name

class Building(TimeStampedModel):
    club = models.ForeignKey(Club, verbose_name="النادي", on_delete=models.CASCADE, related_name="buildings")
    name = models.CharField("اسم المبنى / الفندق", max_length=200, db_index=True)
    building_type = models.CharField("نوع المبنى", max_length=100, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"
        constraints = [
            models.UniqueConstraint(fields=["club", "name"], name="unique_building_per_club")
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.club})"

class Floor(TimeStampedModel):
    building = models.ForeignKey(Building, verbose_name="المبنى", on_delete=models.CASCADE, related_name="floors")
    level_number = models.IntegerField("رقم الدور")
    label = models.CharField("تسمية الدور", max_length=100, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        constraints = [
            models.UniqueConstraint(fields=["building", "level_number"], name="unique_floor_per_building")
        ]

    def __str__(self) -> str:
        return f"{self.label or f'دور {self.level_number}'} - {self.building}"

class UnitType(models.TextChoices):
    APARTMENT_1B = "APARTMENT_1B", "شقة 1 غرفة"
    APARTMENT_2B = "APARTMENT_2B", "شقة 2 غرفة"
    APARTMENT_3B = "APARTMENT_3B", "شقة 3 غرفة"
    ROOM = "ROOM", "غرفة"
    SUITE = "SUITE", "جناح"

class PricingRule(TimeStampedModel):
    clubs = models.ManyToManyField(Club, verbose_name="النوادي")
    buildings = models.ManyToManyField(Building, verbose_name="العمارات المطبق عليها (اختياري)", blank=True, help_text="إذا لم تختر عمارات، سيتم تطبيق السعر على كل عمارات النادي")
    units = models.ManyToManyField("Unit", verbose_name="الوحدات المطبق عليها (اختياري)", blank=True, help_text="إذا لم تختر وحدات، سيتم تطبيق السعر على كل وحدات العمارة/النادي")
    months = models.CharField("الأشهر (اختياري)", max_length=100, blank=True, help_text="أرقام الأشهر مفصولة بفاصلة (مثال: 7,8,9). إذا تركته فارغاً سيتم تطبيقه طوال العام")
    
    unit_types = models.CharField("أنواع الوحدات (اختياري)", max_length=500, null=True, blank=True, help_text="قيم مفصولة بفاصلة")
    classifications = models.CharField("التصنيفات (اختياري)", max_length=500, null=True, blank=True, help_text="قيم مفصولة بفاصلة (مكيف, عادي)")
    view_types = models.CharField("الإطلالات (اختياري)", max_length=500, null=True, blank=True, help_text="قيم مفصولة بفاصلة (بحرى, قبلى)")

    # Base Prices (per night)
    price_military = models.DecimalField("عسكري", max_digits=10, decimal_places=2, default=0)
    price_family = models.DecimalField("عضوية عائلية", max_digits=10, decimal_places=2, default=0)
    price_civilian_af = models.DecimalField("مدنى ق.م", max_digits=10, decimal_places=2, default=0)
    price_civilian = models.DecimalField("مدني عام", max_digits=10, decimal_places=2, default=0)
    
    price_martyr = models.DecimalField("شهيد", max_digits=10, decimal_places=2, default=0)
    price_veteran = models.DecimalField("محارب", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "قاعدة تسعير"
        verbose_name_plural = "قواعد التسعير"

    def __str__(self) -> str:
        parts = ["تسعيرة مجمعة"]
        if self.months: parts.append(f"أشهر: {self.months}")
        if self.unit_types: parts.append(self.unit_types)
        if self.classifications: parts.append(self.classifications)
        return " - ".join(parts)

class Unit(TimeStampedModel):
    floor = models.ForeignKey(Floor, verbose_name="الدور", on_delete=models.CASCADE, related_name="units")
    unit_no = models.CharField("رقم الوحدة", max_length=20, db_index=True)
    unit_type = models.CharField("نوع الوحدة", max_length=20, choices=UnitType.choices, default=UnitType.APARTMENT_1B, db_index=True)
    classification = models.CharField("التصنيف", max_length=100, blank=True, db_index=True)
    view_type = models.CharField("الإطلالة", max_length=100, blank=True)
    allocation = models.CharField("المخصصات", max_length=100, blank=True, null=True)
    base_price = models.DecimalField("السعر الأساسي لليلة", max_digits=10, decimal_places=2, default=0)
    capacity = models.PositiveIntegerField("السعة", default=1)
    rooms_count = models.PositiveIntegerField("عدد الغرف", default=1)
    is_bookable = models.BooleanField("قابلة للحجز", default=True, db_index=True)
    is_maintenance = models.BooleanField("تحت الصيانة", default=False, db_index=True)
    is_air_conditioned = models.BooleanField("تكييف", default=False)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "وحدة"
        verbose_name_plural = "الوحدات"
        constraints = [
            models.UniqueConstraint(fields=["floor", "unit_no"], name="unique_unit_per_floor")
        ]

    def __str__(self) -> str:
        if self.classification:
            return f"{self.unit_no} - {self.floor.building.name} ({self.classification})"
        return f"{self.unit_no} - {self.floor.building.name}"

class AllocationType(models.TextChoices):
    ADMINISTRATIVE = "ADMINISTRATIVE", "اسكان اداري"
    COMMANDER = "COMMANDER", "مخصصات القائد"
    COMPANY = "COMPANY", "اسكان شركات"
    PERMANENT = "PERMANENT", "اسكان دائم عقود"
    OTHER = "OTHER", "أخرى"

class Allocation(TimeStampedModel):
    unit = models.ForeignKey(Unit, verbose_name="الوحدة", on_delete=models.CASCADE, related_name="allocations")
    allocation_type = models.CharField("نوع المخصص", max_length=20, choices=AllocationType.choices)
    allocated_to = models.CharField("الجهة المخصص لها", max_length=200, blank=True)
    start_date = models.DateField("تاريخ البداية (اختياري)", null=True, blank=True)
    end_date = models.DateField("تاريخ النهاية (اختياري)", null=True, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "مُخصص"
        verbose_name_plural = "المخصصات"

    def __str__(self) -> str:
        allocated = self.allocated_to or self.get_allocation_type_display()
        return f"{allocated} - {self.unit}"

class Period(TimeStampedModel):
    name = models.CharField("اسم الفوج/الأسبوع", max_length=100, db_index=True)
    start_date = models.DateField("تاريخ البداية", db_index=True)
    end_date = models.DateField("تاريخ النهاية", db_index=True)
    departure_date = models.DateField("تاريخ المغادرة", null=True, blank=True)
    contract_deadline = models.DateField("اخر توقيت التعاقد", null=True, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "فوج/أسبوع"
        verbose_name_plural = "الأفواج والأسابيع"
        ordering = ["start_date"]

    def __str__(self) -> str:
        return self.name
