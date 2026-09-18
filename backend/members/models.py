from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    class Meta:
        abstract = True

class Member(TimeStampedModel):
    membership_no = models.CharField("رقم العضوية", max_length=50, unique=True)
    full_name = models.CharField("الاسم", max_length=200, db_index=True)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True)
    email = models.EmailField("البريد الإلكتروني", blank=True)
    national_id = models.CharField("الرقم القومي", max_length=14, blank=True, db_index=True)
    rank = models.CharField("الرتبة", max_length=100, blank=True, db_index=True)
    job_type = models.CharField("نوع الوظيفة", max_length=100, blank=True)
    security_clearance = models.CharField("الموقف الأمني", max_length=200, blank=True)
    address = models.TextField("العنوان", blank=True)
    notes = models.TextField("ملاحظات", blank=True)
    is_active = models.BooleanField("نشط", default=True)

    class Meta:
        verbose_name = "عضو"
        verbose_name_plural = "الأعضاء"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.membership_no})"

class FamilyMember(TimeStampedModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="family_members", verbose_name="العضو")
    name = models.CharField("الاسم", max_length=200)
    relation = models.CharField("صلة القرابة", max_length=100)
    national_id = models.CharField("الرقم القومي", max_length=14, blank=True)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "فرد عائلة"
        verbose_name_plural = "أفراد العائلة"

    def __str__(self) -> str:
        return f"{self.name} ({self.relation} - {self.member.full_name})"

class MemberStatusLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="status_logs", verbose_name="العضو")
    old_status = models.CharField("الحالة السابقة", max_length=100)
    new_status = models.CharField("الحالة الجديدة", max_length=100)
    changed_at = models.DateTimeField("تاريخ التغيير", auto_now_add=True)
    changed_by = models.CharField("تم التغيير بواسطة", max_length=100, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        verbose_name = "سجل حالة العضو"
        verbose_name_plural = "سجلات حالة الأعضاء"
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return f"{self.member.full_name}: {self.old_status} -> {self.new_status}"
