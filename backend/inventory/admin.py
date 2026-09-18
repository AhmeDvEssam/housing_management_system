from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.admin import helpers
from .models import Club, Building, Floor, Unit, Allocation, AllocationType, PricingRule

@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ["get_clubs", "get_buildings", "get_months", "price_military", "price_family", "price_civilian_af", "price_civilian"]
    save_as = True
    
    # We will override the change_form_template completely for the Custom UI
    change_form_template = "admin/inventory/pricingrule/change_form.html"

    def save_model(self, request, obj, form, change):
        """Override to manually read CharField fields from POST to bypass widget interference."""
        import logging
        logger = logging.getLogger('django')
        logger.warning(f"=== PRICING SAVE DEBUG ===")
        logger.warning(f"POST classifications: {request.POST.get('classifications')}")
        logger.warning(f"POST unit_types: {request.POST.get('unit_types')}")
        logger.warning(f"POST months: {request.POST.get('months')}")
        logger.warning(f"POST clubs: {request.POST.getlist('clubs')}")
        logger.warning(f"POST buildings: {request.POST.getlist('buildings')}")
        logger.warning(f"POST units: {request.POST.getlist('units')}")
        logger.warning(f"POST price_military: {request.POST.get('price_military')}")
        
        obj.classifications = request.POST.get('classifications', '') or ''
        obj.unit_types = request.POST.get('unit_types', '') or ''
        obj.months = request.POST.get('months', '') or ''
        logger.warning(f"OBJ BEFORE SAVE: classifications={obj.classifications}, unit_types={obj.unit_types}")
        super().save_model(request, obj, form, change)
        
        # Verify save by re-reading from DB
        from .models import PricingRule as PR
        saved = PR.objects.get(pk=obj.pk)
        logger.warning(f"DB AFTER SAVE: classifications={saved.classifications}, unit_types={saved.unit_types}")
        logger.warning(f"=== END DEBUG ===")

    def save_related(self, request, form, formsets, change):
        """Override to manually set M2M fields from POST data."""
        super().save_related(request, form, formsets, change)
        obj = form.instance
        
        # Clubs M2M
        club_ids = request.POST.getlist('clubs')
        if club_ids:
            obj.clubs.set(club_ids)
        
        # Buildings M2M
        building_ids = request.POST.getlist('buildings')
        obj.buildings.set(building_ids)  # can be empty = apply to all
        
        # Units M2M
        unit_ids = request.POST.getlist('units')
        obj.units.set(unit_ids)  # can be empty = apply to all

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('get-hierarchy/', self.admin_site.admin_view(self.get_hierarchy_view), name='pricingrule_get_hierarchy'),
        ]
        return custom_urls + urls

    def get_hierarchy_view(self, request):
        from django.http import JsonResponse
        from .models import Club, Building, Unit, UnitType
        
        unit_type_labels = dict(UnitType.choices)
        
        clubs = Club.objects.all().order_by('name')
        
        # Prefetch all units for the clubs to avoid N+1 queries
        all_units = Unit.objects.select_related('floor__building__club').order_by('floor__building__club__name', 'floor__building__name', 'floor__level_number', 'unit_no')
        
        # Group units by building, and buildings by club
        buildings_by_club = {}
        units_by_building = {}
        
        for u in all_units:
            b_id = u.floor.building_id
            c_id = u.floor.building.club_id
            
            if c_id not in buildings_by_club:
                buildings_by_club[c_id] = {}
            if b_id not in buildings_by_club[c_id]:
                buildings_by_club[c_id][b_id] = u.floor.building
                
            if b_id not in units_by_building:
                units_by_building[b_id] = []
            units_by_building[b_id].append(u)
            
        data = []
        for c in clubs:
            club_data = {"id": c.id, "name": c.name, "buildings": []}
            buildings_dict = buildings_by_club.get(c.id, {})
            
            # Sort buildings by name
            buildings = sorted(buildings_dict.values(), key=lambda x: x.name)
            
            for b in buildings:
                b_data = {"id": b.id, "name": b.name, "classifications": []}
                cls_dict = {}
                
                units = units_by_building.get(b.id, [])
                for u in units:
                    cls = u.classification or "بدون تصنيف"
                    u_type = u.unit_type or "APARTMENT_1B"
                    
                    if cls not in cls_dict:
                        cls_dict[cls] = {}
                    if u_type not in cls_dict[cls]:
                        cls_dict[cls][u_type] = []
                        
                    cls_dict[cls][u_type].append({"id": u.id, "name": u.unit_no})
                
                for cls_name, types_dict in cls_dict.items():
                    types_list = []
                    for t_code, t_units in types_dict.items():
                        types_list.append({
                            "code": t_code,
                            "name": unit_type_labels.get(t_code, t_code),
                            "units": t_units
                        })
                    b_data["classifications"].append({"name": cls_name, "unit_types": types_list})
                        
                club_data["buildings"].append(b_data)
            data.append(club_data)
        return JsonResponse({"clubs": data})

    def get_clubs(self, obj):
        return ", ".join([c.name for c in obj.clubs.all()])
    get_clubs.short_description = "النوادي"

    def get_buildings(self, obj):
        if not obj.buildings.exists():
            return "الكل"
        return ", ".join([b.name for b in obj.buildings.all()])
    get_buildings.short_description = "العمارات"

    def get_months(self, obj):
        return obj.months or "طوال العام"
    get_months.short_description = "الأشهر"

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "city"]
    search_fields = ["name"]

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["name", "club", "building_type"]
    list_filter = ["club"]
    search_fields = ["name"]

class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ["level_number", "label", "building"]
    list_filter = ["building__club", "building"]

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["unit_no", "floor", "unit_type", "classification", "view_type", "is_bookable"]
    list_filter = ["unit_type", "is_bookable", "is_maintenance", "floor__building__club"]
    search_fields = ["unit_no", "floor__building__name"]
    actions = ['allocate_units']

    @admin.action(description="تخصيص الوحدات المحددة")
    def allocate_units(self, request, queryset):
        if 'apply' in request.POST:
            allocation_type = request.POST.get('allocation_type')
            allocated_to = request.POST.get('allocated_to')
            count = 0
            for unit in queryset:
                unit.allocation = allocation_type
                unit.save()
                Allocation.objects.create(
                    unit=unit,
                    allocation_type=allocation_type,
                    allocated_to=allocated_to,
                )
                count += 1
            self.message_user(request, f"تم تخصيص {count} وحدة بنجاح.")
            return HttpResponseRedirect(request.get_full_path())
            
        context = {
            'queryset': queryset,
            'allocation_types': AllocationType.choices,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/inventory/unit/allocate_units.html', context)

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ["unit", "allocation_type", "allocated_to", "start_date", "end_date"]
    list_filter = ["allocation_type"]
    search_fields = ["unit__unit_no", "allocated_to"]
    change_list_template = "admin/inventory/allocation/change_list.html"
    actions = ["create_booking_from_allocation"]

    @admin.action(description="إضافة إلى المشغول (إنشاء حجز مؤكد)")
    def create_booking_from_allocation(self, request, queryset):
        from bookings.models import Booking, BookingDay, BookingType, PersonTypeChoices
        from django.contrib import messages
        from django.shortcuts import render
        from django.contrib.admin import helpers
        from datetime import timedelta
        
        is_confirm = request.POST.get('confirm_override') == 'yes'
        conflicts = []

        if not is_confirm:
            for obj in queryset:
                if not obj.start_date or not obj.end_date:
                    continue
                days = [obj.start_date + timedelta(days=i) for i in range((obj.end_date - obj.start_date).days + 1)]
                conflicting_b_days = BookingDay.objects.filter(
                    unit=obj.unit,
                    day__in=days
                ).select_related('booking')
                
                if conflicting_b_days.exists():
                    for bd in conflicting_b_days:
                        conflicting_booking = bd.booking
                        conflict_info = {
                            "unit": obj.unit.unit_no,
                            "old_guest": conflicting_booking.guest_name,
                            "period": f"من {conflicting_booking.start_date} إلى {conflicting_booking.end_date}",
                            "new_guest": obj.allocated_to or dict(AllocationType.choices).get(obj.allocation_type, obj.allocation_type)
                        }
                        if conflict_info not in conflicts:
                            conflicts.append(conflict_info)
            
            if conflicts:
                context = {
                    "conflicts": conflicts,
                    "queryset": queryset,
                    "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
                }
                return render(request, "admin/inventory/allocation/confirm_override.html", context)

        success_count = 0
        error_count = 0
        
        if is_confirm:
            for obj in queryset:
                if not obj.start_date or not obj.end_date:
                    continue
                days = [obj.start_date + timedelta(days=i) for i in range((obj.end_date - obj.start_date).days + 1)]
                conflicting_b_days = BookingDay.objects.filter(
                    unit=obj.unit,
                    day__in=days
                ).select_related('booking')
                for bd in conflicting_b_days:
                    bd.booking.delete()

        for obj in queryset:
            if not obj.start_date or not obj.end_date:
                error_count += 1
                continue
            
            Booking.objects.create(
                unit=obj.unit,
                start_date=obj.start_date,
                end_date=obj.end_date,
                guest_name=obj.allocated_to or dict(AllocationType.choices).get(obj.allocation_type, obj.allocation_type),
                booking_type=BookingType.ALLOCATIONS,
                person_type=PersonTypeChoices.CIVILIAN_GENERAL,
                status="مؤكد",
                notes=obj.notes
            )
            success_count += 1
            
        if success_count > 0:
            messages.success(request, f"تم إنشاء حجز مؤكد لـ {success_count} مخصص بنجاح.")
        if error_count > 0:
            messages.warning(request, f"تم تجاهل {error_count} مخصص لعدم وجود تاريخ بداية ونهاية.")

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view), name='allocation_bulk_add'),
            path('<path:object_id>/edit/', self.admin_site.admin_view(self.edit_allocation_view), name='allocation_edit'),
        ]
        return custom_urls + urls

    def add_view(self, request, form_url='', extra_context=None):
        """الإضافة تروح دايماً على شاشة الـ bulk add"""
        from django.shortcuts import redirect
        return redirect("admin:allocation_bulk_add")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """التعديل يروح على شاشة التعديل المخصصة بدل شاشة Django الافتراضية"""
        from django.shortcuts import redirect
        return redirect("admin:allocation_edit", object_id=object_id)

    def edit_allocation_view(self, request, object_id):
        """شاشة تعديل مخصص فردي بنفس ستايل الـ bulk add مع الشجرة"""
        from django.shortcuts import render, redirect, get_object_or_404
        from django.contrib import messages
        from .models import Unit, AllocationType

        obj = get_object_or_404(Allocation, pk=object_id)

        if request.method == "POST":
            action = request.POST.get("action")

            if action == "delete":
                obj.delete()
                messages.success(request, f"تم حذف المخصص بالكامل بنجاح.")
                return redirect("admin:inventory_allocation_changelist")

            unit_ids = request.POST.getlist("units")
            allocation_type = request.POST.get("allocation_type")
            allocated_to = request.POST.get("allocated_to", "")
            start_date = request.POST.get("start_date") or None
            end_date = request.POST.get("end_date") or None
            notes = request.POST.get("notes", "")

            create_booking = request.POST.get("create_booking") == "1"

            if not unit_ids:
                messages.error(request, "لم يتم اختيار أي وحدة!")
                return redirect("admin:allocation_edit", object_id=object_id)
                
            if create_booking and (not start_date or not end_date):
                messages.error(request, "لإنشاء حجز فعلي، يجب تحديد تاريخ الوصول والمغادرة!")
                return redirect("admin:allocation_edit", object_id=object_id)

            from bookings.models import Booking, BookingDay, BookingType, PersonTypeChoices

            override_conflicts = request.POST.get("override_booking_conflicts") == "1"

            if create_booking and start_date and end_date:
                if not override_conflicts:
                    has_conflicts = False
                    conflict_messages = []
                    for uid in unit_ids:
                        unit = Unit.objects.filter(id=uid).first()
                        if unit:
                            conflicts = BookingDay.objects.filter(
                                unit=unit,
                                day__range=[start_date, end_date]
                            ).select_related('booking')
                            if conflicts.exists():
                                has_conflicts = True
                                c_booking = conflicts.first().booking
                                conflict_messages.append(f"الوحدة {unit.unit_no} محجوزة باسم {c_booking.guest_name}")
                    
                    if has_conflicts:
                        messages.error(request, "توجد تعارضات: " + " | ".join(conflict_messages))
                        messages.warning(request, "يرجى تحديد خيار 'تجاوز التعارض' بالأسفل والمحاولة مرة أخرى إذا كنت متأكداً من رغبتك في حذف الحجوزات السابقة.")
                        context = {
                            **self.admin_site.each_context(request),
                            'opts': self.model._meta,
                            'allocation_types': AllocationType.choices,
                            'obj': obj,
                            'show_override_checkbox': True,
                        }
                        return render(request, "admin/inventory/allocation/edit.html", context)
                else:
                    for uid in unit_ids:
                        unit = Unit.objects.filter(id=uid).first()
                        if unit:
                            conflicting_b_days = BookingDay.objects.filter(
                                unit=unit,
                                day__range=[start_date, end_date]
                            ).select_related('booking')
                            for bd in conflicting_b_days:
                                bd.booking.delete()

            # Delete the original allocation since we might have selected different/multiple units
            obj.delete()

            count = 0
            for uid in unit_ids:
                unit = Unit.objects.filter(id=uid).first()
                if unit:
                    Allocation.objects.create(
                        unit=unit,
                        allocation_type=allocation_type,
                        allocated_to=allocated_to,
                        start_date=start_date,
                        end_date=end_date,
                        notes=notes
                    )
                    unit.allocation = allocation_type
                    unit.save(update_fields=['allocation'])
                    
                    if create_booking:
                        Booking.objects.create(
                            unit=unit,
                            start_date=start_date,
                            end_date=end_date,
                            guest_name=allocated_to or dict(AllocationType.choices).get(allocation_type, allocation_type),
                            booking_type=BookingType.ALLOCATIONS,
                            person_type=PersonTypeChoices.CIVILIAN_GENERAL,
                            status="مؤكد",
                            notes=notes
                        )
                    count += 1

            messages.success(request, f"تم حفظ التعديلات بنجاح وتطبيقها على {count} وحدة.")
            return redirect("admin:inventory_allocation_changelist")

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'allocation_types': AllocationType.choices,
            'obj': obj,
        }
        return render(request, "admin/inventory/allocation/edit.html", context)

    def bulk_add_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from .models import Unit, AllocationType

        if request.method == "POST":
            unit_ids = request.POST.getlist("units")
            allocation_type = request.POST.get("allocation_type")
            allocated_to = request.POST.get("allocated_to", "")
            start_date = request.POST.get("start_date") or None
            end_date = request.POST.get("end_date") or None
            notes = request.POST.get("notes", "")

            create_booking = request.POST.get("create_booking") == "1"

            if not unit_ids:
                messages.error(request, "لم يتم اختيار أي وحدة!")
                return redirect("admin:allocation_bulk_add")

            if create_booking and (not start_date or not end_date):
                messages.error(request, "لإنشاء حجز فعلي، يجب تحديد تاريخ الوصول والمغادرة!")
                return redirect("admin:allocation_bulk_add")

            from bookings.models import Booking, BookingDay, BookingType, PersonTypeChoices
            from datetime import datetime

            override_conflicts = request.POST.get("override_booking_conflicts") == "1"

            if create_booking and start_date and end_date:
                # Check for conflicts
                if not override_conflicts:
                    has_conflicts = False
                    conflict_messages = []
                    for uid in unit_ids:
                        unit = Unit.objects.filter(id=uid).first()
                        if unit:
                            conflicts = BookingDay.objects.filter(
                                unit=unit,
                                day__range=[start_date, end_date]
                            ).select_related('booking')
                            if conflicts.exists():
                                has_conflicts = True
                                c_booking = conflicts.first().booking
                                conflict_messages.append(f"الوحدة {unit.unit_no} محجوزة باسم {c_booking.guest_name}")
                    
                    if has_conflicts:
                        messages.error(request, "توجد تعارضات: " + " | ".join(conflict_messages))
                        messages.warning(request, "يرجى تحديد خيار 'تجاوز التعارض' بالأسفل والمحاولة مرة أخرى إذا كنت متأكداً من رغبتك في حذف الحجوزات السابقة.")
                        context = {
                            **self.admin_site.each_context(request),
                            'opts': self.model._meta,
                            'allocation_types': AllocationType.choices,
                            'show_override_checkbox': True,
                        }
                        return render(request, "admin/inventory/allocation/bulk_add.html", context)
                
                else:
                    # override is True, delete conflicts before creating
                    for uid in unit_ids:
                        unit = Unit.objects.filter(id=uid).first()
                        if unit:
                            conflicting_b_days = BookingDay.objects.filter(
                                unit=unit,
                                day__range=[start_date, end_date]
                            ).select_related('booking')
                            for bd in conflicting_b_days:
                                bd.booking.delete()

            count = 0
            for uid in unit_ids:
                unit = Unit.objects.filter(id=uid).first()
                if unit:
                    Allocation.objects.create(
                        unit=unit,
                        allocation_type=allocation_type,
                        allocated_to=allocated_to,
                        start_date=start_date,
                        end_date=end_date,
                        notes=notes
                    )
                    unit.allocation = allocation_type
                    unit.save(update_fields=['allocation'])

                    if create_booking:
                        Booking.objects.create(
                            unit=unit,
                            start_date=start_date,
                            end_date=end_date,
                            guest_name=allocated_to or dict(AllocationType.choices).get(allocation_type, allocation_type),
                            booking_type=BookingType.ALLOCATIONS,
                            person_type=PersonTypeChoices.CIVILIAN_GENERAL,
                            status="مؤكد",
                            notes=notes
                        )
                    count += 1
            
            messages.success(request, f"تم إنشاء {count} مخصص بنجاح.")
            return redirect("admin:inventory_allocation_changelist")

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'allocation_types': AllocationType.choices,
        }
        return render(request, "admin/inventory/allocation/bulk_add.html", context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # مزامنة حقل allocation في الوحدة
        obj.unit.allocation = obj.allocation_type
        obj.unit.save(update_fields=['allocation'])

    def delete_model(self, request, obj):
        unit = obj.unit
        super().delete_model(request, obj)
        # إذا لم يتبق مخصصات أخرى للوحدة، نفرغ الحقل
        if not Allocation.objects.filter(unit=unit).exists():
            unit.allocation = None
            unit.save(update_fields=['allocation'])

    def delete_queryset(self, request, queryset):
        # جمع الوحدات المتأثرة قبل الحذف
        unit_ids = list(queryset.values_list('unit_id', flat=True).distinct())
        super().delete_queryset(request, queryset)
        # تحديث الوحدات التي لم يتبق لها مخصصات
        
        # Check which units still have allocations
        units_with_allocations = set(Allocation.objects.filter(unit_id__in=unit_ids).values_list('unit_id', flat=True))
        units_to_clear = [uid for uid in unit_ids if uid not in units_with_allocations]
        
        if units_to_clear:
            Unit.objects.filter(id__in=units_to_clear).update(allocation=None)

from .models import Period

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "departure_date", "contract_deadline", "notes"]
    list_editable = ["start_date", "end_date", "departure_date", "contract_deadline"]
    ordering = ["start_date"]
    
    change_list_template = "admin/inventory/period/change_list.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='period_import_excel'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel_view), name='period_export_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        from django.shortcuts import redirect
        from django.contrib import messages
        import pandas as pd
        
        if request.method == 'POST' and request.FILES.get('excel_file'):
            try:
                df = pd.read_excel(request.FILES['excel_file'])
                count = 0
                for _, row in df.iterrows():
                    name = str(row.get('اسم الفوج/الأسبوع', '')).strip()
                    if not name:
                        continue
                    Period.objects.update_or_create(
                        name=name,
                        defaults={
                            'start_date': row.get('تاريخ البداية'),
                            'end_date': row.get('تاريخ النهاية'),
                            'departure_date': row.get('تاريخ المغادرة') if pd.notna(row.get('تاريخ المغادرة')) else None,
                            'contract_deadline': row.get('مهلة السداد') if pd.notna(row.get('مهلة السداد')) else None,
                            'notes': str(row.get('ملاحظات', '')) if pd.notna(row.get('ملاحظات')) else '',
                        }
                    )
                    count += 1
                messages.success(request, f"تم استيراد {count} فوج/أسبوع بنجاح.")
            except Exception as e:
                messages.error(request, f"خطأ أثناء الاستيراد: {e}")
        
        return redirect('..')

    def export_excel_view(self, request):
        from django.http import HttpResponse
        import pandas as pd
        from io import BytesIO
        
        periods = Period.objects.all().order_by('start_date')
        data = []
        for p in periods:
            data.append({
                'اسم الفوج/الأسبوع': p.name,
                'تاريخ البداية': p.start_date,
                'تاريخ النهاية': p.end_date,
                'تاريخ المغادرة': p.departure_date,
                'مهلة السداد': p.contract_deadline,
                'ملاحظات': p.notes,
            })
        
        df = pd.DataFrame(data)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        
        response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="periods_export.xlsx"'
        return response
