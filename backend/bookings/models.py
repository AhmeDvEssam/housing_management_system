from datetime import date, timedelta
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from audit.utils import log_event
from inventory.models import Unit
from members.models import Member

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True

class BookingType(models.TextChoices):
    STANDARD = "STANDARD", "حجز عادي"
    LOTTERY = "LOTTERY", "قرعة"
    ARMIES_REGIONS = "ARMIES_REGIONS", "الجيوش والمناطق"
    ALLOCATIONS = "ALLOCATIONS", "مخصصات"

class PersonTypeChoices(models.TextChoices):
    CIVILIAN_GENERAL = "CIVILIAN_GENERAL", "مدني عام"
    CIVILIAN_AF = "CIVILIAN_AF", "مدني ق.م"
    MARTYR = "MARTYR", "شهيد/مصاب"
    ACTIVE_MEMBER = "ACTIVE_MEMBER", "عضوية عاملة"
    FAMILY_MEMBER = "FAMILY_MEMBER", "عضوية عائلية"
    MILITARY = "MILITARY", "عسكري"
    VETERAN = "VETERAN", "محارب"

class BeneficiaryRelationChoices(models.TextChoices):
    SON = "SON", "الابن"
    DAUGHTER = "DAUGHTER", "الابنة"
    BROTHER = "BROTHER", "اخ"
    SISTER = "SISTER", "اخت"
    FATHER = "FATHER", "والد"
    MOTHER = "MOTHER", "والدة"
    WIFE = "WIFE", "زوجة"
    SELF = "SELF", "نفسه"

class Booking(TimeStampedModel):
    person_type = models.CharField(
        "نوع الشخص",
        max_length=50,
        choices=PersonTypeChoices.choices,
        default=PersonTypeChoices.CIVILIAN_GENERAL,
        db_index=True
    )
    beneficiary_relation = models.CharField("صلة القرابة للمستفيد", max_length=50, choices=BeneficiaryRelationChoices.choices, blank=True)
    is_plus_50 = models.BooleanField("إضافة 50%", default=False)
    discount_percentage = models.DecimalField("خصم %", max_digits=5, decimal_places=2, default=0, help_text="أدخل نسبة الخصم (مثال: 20 لخصم 20%)")
    base_price = models.DecimalField("إجمالي السعر الأساسي", max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField("إجمالي السعر", max_digits=12, decimal_places=2, default=0)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="اختيار العضو")
    guest_name = models.CharField("الاسم", max_length=200, blank=True)
    guest_rank = models.CharField("الرتبة", max_length=100, blank=True)
    guest_id_no = models.CharField("رقم العضوية / الرقم القومي", max_length=14, blank=True)
    guest_phone = models.CharField("رقم الهاتف", max_length=20, blank=True)
    
    unit = models.ForeignKey(
        Unit, verbose_name="الوحدة", on_delete=models.CASCADE, related_name="bookings"
    )
    period = models.ForeignKey(
        "inventory.Period", verbose_name="الفوج/الأسبوع", on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )
    status = models.CharField(
        "الحالة",
        max_length=100,
        choices=[
            ('مؤكد', 'مؤكد (مدفوع)'),
            ('غير مؤكد', 'غير مؤكد (منتظر الدفع)'),
            ('ملغي', 'ملغي'),
        ],
        default="مؤكد",
        db_index=True
    )
    start_date = models.DateField("تاريخ البداية", db_index=True)
    end_date = models.DateField("تاريخ النهاية", db_index=True)
    booking_type = models.CharField(
        "نوع الحجز",
        max_length=20,
        choices=BookingType.choices,
        default=BookingType.STANDARD,
        db_index=True
    )
    army_region = models.CharField("تصنيف المنطقة/الجيش", max_length=100, blank=True, db_index=True)
    contract_no = models.CharField("رقم العقد", max_length=50, blank=True)
    beneficiary = models.CharField("المستفيد", max_length=200, blank=True)
    payment_deadline = models.DateField("مهلة السداد", null=True, blank=True)
    notes = models.TextField("ملاحظات", blank=True)
    pay_method = models.IntegerField("طريقة الدفع", choices=[(0, 'لم يتم الدفع'), (1, 'فيزا'), (2, 'توريد بنكي')], default=0)
    record_date = models.DateTimeField("تاريخ التسجيل (Oracle)", null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        ordering = ["-start_date"]

    def __str__(self) -> str:
        name = self.guest_name or "حجز بدون اسم"
        return f"{name} - {self.unit} ({self.start_date})"

    def clean(self) -> None:
        # Auto-link Member ForeignKey and auto-fill details if member is selected
        if self.member:
            if not self.guest_id_no:
                self.guest_id_no = self.member.membership_no
            if not self.guest_name:
                self.guest_name = self.member.full_name
            if not self.guest_rank:
                self.guest_rank = self.member.rank
        elif self.guest_id_no:
            from members.models import Member
            try:
                # First try matching by membership_no
                m = Member.objects.get(membership_no=self.guest_id_no)
                self.member = m
                if not self.guest_name:
                    self.guest_name = m.full_name
                if not self.guest_rank:
                    self.guest_rank = m.rank
            except Member.DoesNotExist:
                # If not found, try matching by national_id
                try:
                    m = Member.objects.get(national_id=self.guest_id_no)
                    self.member = m
                    if not self.guest_name:
                        self.guest_name = m.full_name
                    if not self.guest_rank:
                        self.guest_rank = m.rank
                except (Member.DoesNotExist, Member.MultipleObjectsReturned):
                    pass
            except Member.MultipleObjectsReturned:
                pass

        if not self.guest_name and not self.guest_id_no:
            raise ValidationError("يجب إدخال اسم الحاجز أو رقم العضوية/الرقم القومي")

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError(
                {"end_date": "تاريخ النهاية يجب أن يكون بعد تاريخ البداية"}
            )

        # Prevent Overlapping Bookings
        if self.unit and self.start_date and self.end_date:
            overlapping = Booking.objects.filter(
                unit=self.unit,
                start_date__lt=self.end_date,
                end_date__gt=self.start_date
            ).exclude(pk=self.pk).exclude(status="ملغي")
            
            if overlapping.exists():
                raise ValidationError("هذه الوحدة محجوزة بالفعل في هذه الفترة. يرجى اختيار فترة أخرى أو وحدة أخرى.")

    def _apply_lottery_defaults(self) -> None:
        if self.booking_type == BookingType.LOTTERY:
            if self.start_date and not self.payment_deadline:
                self.payment_deadline = self.start_date - timedelta(days=14)

    def iter_days(self):
        current = self.start_date
        while current < self.end_date:
            yield current
            current += timedelta(days=1)

    def _set_booking_days(self):
        BookingDay.objects.filter(booking=self).delete()
        days = []
        for day in self.iter_days():
            days.append(
                BookingDay(
                    booking=self,
                    unit=self.unit,
                    day=day
                )
            )
        BookingDay.objects.bulk_create(days)

    def save(self, *args, **kwargs) -> None:
        if self.base_price == 0 and self.total_price > 0:
            self.base_price = self.total_price
            
        # Automatically set record_date to today if it's confirmed and missing
        if not self.record_date and self.status == 'مؤكد':
            from django.utils import timezone
            self.record_date = timezone.now()
            
        is_new = self.pk is None
        previous_status = None
        if not is_new:
            previous_status = Booking.objects.filter(pk=self.pk).values_list("status", flat=True).first()
        
        self._apply_lottery_defaults()
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.status != "ملغي" and not getattr(self, '_skip_booking_days', False):
                self._set_booking_days()
            else:
                BookingDay.objects.filter(booking=self).delete()

        if is_new:
            log_event(
                action="booking_created",
                object_type="Booking",
                object_id=str(self.pk),
                message=f"تم إنشاء حجز جديد للوحدة {self.unit}",
                metadata={"status": self.status, "unit_id": self.unit_id},
            )
        elif previous_status and previous_status != self.status:
            log_event(
                action="booking_status_changed",
                object_type="Booking",
                object_id=str(self.pk),
                message=(
                    f"تم تغيير حالة الحجز من "
                    f"{previous_status} إلى "
                    f"{self.status}"
                ),
                metadata={"from": previous_status, "to": self.status},
            )

    def update_price_with_companions(self):
        from decimal import Decimal
        if self.base_price == 0 and self.total_price > 0:
            self.base_price = self.total_price
        
        companion_count = self.companions.count()
        if companion_count > 4:
            companion_count = 4
            
        fee_percentage = Decimal('0.375') * companion_count
        self.total_price = self.base_price * (1 + fee_percentage)
        Booking.objects.filter(pk=self.pk).update(
            base_price=self.base_price,
            total_price=self.total_price
        )

    def calculate_live_price(self):
        """Calculates and returns (base_price, total_price) dynamically based on PricingRules and companions."""
        if hasattr(self, '_cached_live_price'):
            return self._cached_live_price

        from inventory.models import PricingRule
        from django.db.models import Q, Count
        from datetime import timedelta
        import math
        from decimal import Decimal

        if not self.unit or not self.start_date or self.end_date <= self.start_date:
            return 0, 0

        rules = PricingRule.objects.filter(clubs=self.unit.floor.building.club)
        rules = rules.annotate(
            units_count=Count('units', distinct=True),
            buildings_count=Count('buildings', distinct=True),
        )
        rules = rules.filter(Q(units=self.unit.id) | Q(units_count=0))
        rules = rules.filter(Q(buildings=self.unit.floor.building.id) | Q(buildings_count=0))
        rules = rules.distinct()

        month_str = str(self.start_date.month)
        candidate_rules = list(rules)
        
        best_rule = None
        best_score = -1

        for r in candidate_rules:
            if r.months:
                allowed_months = [m.strip() for m in r.months.split(',') if m.strip()]
                if allowed_months and month_str not in allowed_months:
                    continue
            if r.classifications:
                allowed_cls = [c.strip() for c in r.classifications.split(',') if c.strip()]
                if allowed_cls and self.unit.classification not in allowed_cls:
                    continue
            if r.unit_types:
                allowed_types = [t.strip() for t in r.unit_types.split(',') if t.strip()]
                if allowed_types and self.unit.unit_type not in allowed_types:
                    continue
            
            rule_price = 0
            if self.person_type == "MARTYR": rule_price = r.price_martyr
            elif self.person_type == "VETERAN": rule_price = r.price_veteran
            elif self.person_type in ["MILITARY", "ACTIVE_MEMBER"]: rule_price = r.price_military
            elif self.person_type == "FAMILY_MEMBER": rule_price = r.price_family
            elif self.person_type == "CIVILIAN_AF": rule_price = r.price_civilian_af
            elif self.person_type == "CIVILIAN_GENERAL": rule_price = r.price_civilian
            
            if not rule_price or rule_price <= 0:
                continue
            
            score = 0
            if r.units.filter(id=self.unit.id).exists(): score += 1000
            if r.buildings.filter(id=self.unit.floor.building.id).exists(): score += 100
            if r.classifications: score += 50
            if r.unit_types: score += 50
            if r.months: score += 20 

            if score > best_score:
                best_score = score
                best_rule = r

        if not best_rule:
            return 0, 0

        base_price = 0
        curr = self.start_date
        while curr < self.end_date:
            daily_price = 0
            if self.person_type == "MARTYR": daily_price = best_rule.price_martyr
            elif self.person_type == "VETERAN": daily_price = best_rule.price_veteran
            elif self.person_type in ["MILITARY", "ACTIVE_MEMBER"]: daily_price = best_rule.price_military
            elif self.person_type == "FAMILY_MEMBER": daily_price = best_rule.price_family
            elif self.person_type == "CIVILIAN_AF": daily_price = best_rule.price_civilian_af
            elif self.person_type == "CIVILIAN_GENERAL": daily_price = best_rule.price_civilian
            
            if self.is_plus_50 and daily_price > 0:
                daily_price = math.ceil((float(daily_price) * 1.5) / 5) * 5

            base_price += Decimal(str(daily_price))
            curr += timedelta(days=1)

        companion_count = len(self.companions.all()) if self.pk else 0
        if companion_count > 4: companion_count = 4
        fee_percentage = Decimal('0.375') * companion_count
        
        total_price = base_price * (1 + fee_percentage)
        
        if getattr(self, 'discount_percentage', 0) > 0:
            total_price = total_price * (1 - (self.discount_percentage / Decimal('100')))
            
        self._cached_live_price = (base_price, total_price)
        return self._cached_live_price

class BookingDay(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_days"
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    day = models.DateField()

    class Meta:
        verbose_name = "يوم حجز"
        verbose_name_plural = "أيام الحجوزات"
        unique_together = ["unit", "day"]
        indexes = [models.Index(fields=["day"])]

    def __str__(self) -> str:
        return f"{self.unit} - {self.day}"

class Application(TimeStampedModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="العضو")
    period = models.ForeignKey("inventory.Period", on_delete=models.CASCADE, verbose_name="الفترة/الفوج")
    wish1 = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="wish1_apps", verbose_name="الرغبة الأولى")
    wish2 = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="wish2_apps", verbose_name="الرغبة الثانية")
    wish3 = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="wish3_apps", verbose_name="الرغبة الثالثة")
    wish4 = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="wish4_apps", verbose_name="الرغبة الرابعة")
    wish5 = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="wish5_apps", verbose_name="الرغبة الخامسة")
    status = models.CharField("الحالة", max_length=50, default="Draft") # Draft, Submitted, Won, Lost
    
    class Meta:
        verbose_name = "استمارة تقديم"
        verbose_name_plural = "استمارات التقديم"
        unique_together = ["member", "period"]

    def __str__(self) -> str:
        return f"استمارة {self.member.full_name} - {self.period.name}"

class LotteryExclusion(TimeStampedModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="العضو")
    period = models.ForeignKey("inventory.Period", on_delete=models.CASCADE, verbose_name="الفترة")
    reason = models.TextField("سبب الاستبعاد")

    class Meta:
        verbose_name = "استبعاد من القرعة"
        verbose_name_plural = "استبعادات القرعة"

    def __str__(self) -> str:
        return f"استبعاد {self.member.full_name} ({self.period.name})"

class LotteryDraft(TimeStampedModel):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, verbose_name="الاستمارة")
    won_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="الوحدة الفائزة")
    wish_number = models.PositiveIntegerField("رقم الرغبة المتحققة")
    is_finalized = models.BooleanField("تم الاعتماد النهائي", default=False)

    class Meta:
        verbose_name = "مسودة نتيجة القرعة"
        verbose_name_plural = "مسودات نتائج القرعة"

    def __str__(self) -> str:
        return f"نتيجة {self.application.member.full_name} - {self.won_unit}"

class Contract(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="contract_detail", verbose_name="الحجز")
    contract_date = models.DateField("تاريخ التعاقد", default=timezone.now, db_index=True)
    legal_terms = models.TextField("الشروط القانونية", blank=True)
    witness_name = models.CharField("اسم الشاهد", max_length=200, blank=True)
    is_signed = models.BooleanField("تم التوقيع", default=False, db_index=True)

    class Meta:
        verbose_name = "عقد"
        verbose_name_plural = "العقود"

    def __str__(self) -> str:
        return f"عقد {self.booking}"

class LotteryResult(TimeStampedModel):
    membership_no = models.CharField("رقم العضوية", max_length=50, db_index=True)
    member_name = models.CharField("اسم العضو", max_length=200)
    club_name = models.CharField("النادي", max_length=100, db_index=True)
    unit_description = models.CharField("الوصف", max_length=200, blank=True)
    unit_no = models.CharField("رقم الوحدة", max_length=50, db_index=True)
    period_no = models.IntegerField("رقم الفترة/الفوج", db_index=True)
    phone = models.CharField("التليفون", max_length=50, blank=True)
    is_imported_to_bookings = models.BooleanField("تم تحويله لحجز", default=False, db_index=True)

    class Meta:
        verbose_name = "نتيجة قرعة مستوردة"
        verbose_name_plural = "نتائج القرعة المستوردة"
        ordering = ["-period_no", "club_name"]

    def __str__(self) -> str:
        return f"{self.member_name} - {self.club_name} - {self.unit_no}"

class Companion(TimeStampedModel):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="companions",
        verbose_name="الحجز"
    )
    name = models.CharField("اسم المرافق", max_length=200)
    national_id = models.CharField("الرقم القومي للمرافق", max_length=14, blank=True)

    class Meta:
        verbose_name = "مرافق"
        verbose_name_plural = "المرافقين"

    def __str__(self) -> str:
        return f"{self.name} (مرافق لـ {self.booking})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not getattr(self, '_skip_price_update', False):
            self.booking.update_price_with_companions()

    def delete(self, *args, **kwargs):
        booking = self.booking
        super().delete(*args, **kwargs)
        booking.update_price_with_companions()

class FaxPrintHistory(TimeStampedModel):
    club = models.ForeignKey("inventory.Club", on_delete=models.CASCADE, verbose_name="النادي")
    period = models.ForeignKey("inventory.Period", on_delete=models.CASCADE, null=True, blank=True, verbose_name="الفترة")
    print_date = models.DateTimeField("تاريخ الطباعة", auto_now_add=True)
    bookings = models.ManyToManyField(Booking, verbose_name="الحجوزات المطبوعة")
    printed_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    supplement_number = models.PositiveIntegerField("رقم الملحق", default=0)

    class Meta:
        verbose_name = "سجل طباعة الفاكس"
        verbose_name_plural = "سجلات طباعة الفاكس"

    def __str__(self):
        s_type = f"ملحق ({self.supplement_number})" if self.supplement_number > 0 else "فاكس رئيسي"
        return f"{self.club} - {s_type} - {self.print_date.strftime('%Y-%m-%d %H:%M')}"
