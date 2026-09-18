from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender='inventory.Allocation')
def sync_unit_allocation_on_save(sender, instance, **kwargs):
    """عند حفظ أي مخصص، نحدّث حقل allocation في الوحدة تلقائياً"""
    unit = instance.unit
    if unit.allocation != instance.allocation_type:
        unit.allocation = instance.allocation_type
        unit.save(update_fields=['allocation'])


@receiver(post_delete, sender='inventory.Allocation')
def sync_unit_allocation_on_delete(sender, instance, **kwargs):
    """عند حذف مخصص، نفحص إذا بقيت مخصصات أخرى للوحدة"""
    from inventory.models import Allocation
    unit = instance.unit
    remaining = Allocation.objects.filter(unit=unit).first()
    if remaining:
        unit.allocation = remaining.allocation_type
    else:
        unit.allocation = None
    unit.save(update_fields=['allocation'])
