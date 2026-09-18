import os
from datetime import timedelta
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Booking, BookingDay, Application, LotteryExclusion, LotteryDraft, Contract, LotteryResult, Companion

class ContractInline(admin.StackedInline):
    model = Contract
    extra = 0
    can_delete = False

class CompanionInline(admin.TabularInline):
    model = Companion
    extra = 1
from .forms import BookingAdminForm
from inventory.models import Unit, Building


class YearListFilter(admin.SimpleListFilter):
    title = "السنة"
    parameter_name = "year"
    
    def lookups(self, request, model_admin):
        from .models import Booking
        from django.db.models.functions import ExtractYear
        years = Booking.objects.annotate(year=ExtractYear('start_date')).values_list('year', flat=True).distinct().order_by('-year')
        valid_years = [y for y in years if y is not None]
        if not valid_years:
            import datetime
            valid_years = [datetime.datetime.now().year]
        return [(y, str(y)) for y in valid_years]
        
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(start_date__year=self.value())
        return queryset


class CustomDatePeriodFilter(admin.ListFilter):
    title = ''
    template = 'admin/filter_empty.html'
    
    def __init__(self, request, params, model, model_admin):
        # Extract the single string values from request.GET
        self.from_date = request.GET.get('from_date', '')
        self.to_date = request.GET.get('to_date', '')
        self.period_id = request.GET.get('period_custom', '')
        
        # Pop from params (which is dict of lists in Django 5) to prevent FieldError / IncorrectLookupParameters redirects
        params.pop('from_date', None)
        params.pop('to_date', None)
        params.pop('period_custom', None)
        
        super().__init__(request, params, model, model_admin)
        
    def has_output(self):
        return True
        
    def choices(self, changelist):
        return []
        
    def expected_parameters(self):
        return ['from_date', 'to_date', 'period_custom']
        
    def queryset(self, request, queryset):
        if self.from_date and self.from_date.strip():
            queryset = queryset.filter(start_date__gte=self.from_date.strip())
        if self.to_date and self.to_date.strip():
            queryset = queryset.filter(end_date__lte=self.to_date.strip())
        return queryset

class SubCategoryFilter(admin.SimpleListFilter):
    title = "تصنيف الحجز"
    parameter_name = "sub_category"
    
    def lookups(self, request, model_admin):
        booking_type = request.GET.get('booking_type__exact')
        if booking_type not in ['ARMIES_REGIONS', 'ALLOCATIONS']:
            return [] # Do not show options if booking_type is not selected or is Standard/Lottery
            
        qs = Booking.objects.filter(booking_type=booking_type).exclude(army_region__isnull=True).exclude(army_region='')
        values = qs.values_list('army_region', flat=True).distinct().order_by('army_region')
        return [(v, v) for v in values]
        
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(army_region=self.value())
        return queryset



class DateRangeListFilter(admin.SimpleListFilter):
    title = 'الفترة التاريخية'
    parameter_name = 'date_range'
    template = 'admin/date_range_filter.html'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.from_date = request.GET.get('from_date', '')
        self.to_date = request.GET.get('to_date', '')

    def lookups(self, request, model_admin):
        return (('dummy', 'dummy'),)

    def queryset(self, request, queryset):
        if self.from_date:
            queryset = queryset.filter(start_date__gte=self.from_date)
        if self.to_date:
            queryset = queryset.filter(end_date__lte=self.to_date)
        return queryset


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_per_page = 25
    form = BookingAdminForm
    autocomplete_fields = ["member"]
    readonly_fields = []
    list_display = ["get_guest_name", "get_membership_no", "get_club", "unit", "get_classification_merged", "start_date", "end_date", "get_colored_status", "get_combined_booking_type", "get_contract_date"]
    list_filter = ["status", "booking_type", SubCategoryFilter, "person_type", "unit__floor__building__club", "unit__classification", YearListFilter, CustomDatePeriodFilter]
    search_fields = ["guest_name", "guest_id_no", "contract_no", "unit__unit_no", "member__full_name", "member__membership_no", "unit__floor__building__name", "unit__floor__building__club__name"]
    list_select_related = ["member", "unit__floor__building__club", "period", "contract_detail"]
    change_list_template = "admin/bookings/booking/change_list.html"

    @method_decorator(cache_page(60))
    def changelist_view(self, request, extra_context=None):
        from inventory.models import Period
        extra_context = extra_context or {}
        # Fetch periods natively and sort them
        periods = list(Period.objects.all())
        import re
        def natural_sort_key(s):
            if not s: return []
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]
        periods.sort(key=lambda p: natural_sort_key(p.name))
        
        extra_context['periods'] = periods
        extra_context['selected_period'] = request.GET.get('period_custom', '')
        extra_context['selected_from'] = request.GET.get('from_date', '')
        extra_context['selected_to'] = request.GET.get('to_date', '')
        
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        js = (
            "admin/js/booking_club_filter.js",
            "admin/js/booking_member_fetch.js",
            "admin/js/reorder_booking_form.js",
        )
        css = {
            'all': ('admin/css/custom_admin_fixes.css',)
        }
    inlines = [CompanionInline]
    def get_membership_no(self, obj):
        if obj.member:
            return obj.member.membership_no
        return obj.guest_id_no or "---"
    get_membership_no.short_description = "رقم العضوية"
    get_membership_no.admin_order_field = 'member__membership_no'

    def get_club(self, obj):
        return obj.unit.floor.building.club.name
    get_club.short_description = "النادي"
    get_club.admin_order_field = 'unit__floor__building__club__name'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "member" and formfield:
            # This attribute tells Jazzmin's change_form.js to SKIP this field
            # so it doesn't destroy Django's AJAX Select2 initialization
            formfield.widget.attrs["data-autocomplete-light-function"] = "select2"
        return formfield

    def get_classification_merged(self, obj):
        unit_type = obj.unit.get_unit_type_display()
        classification = obj.unit.classification
        return f"{unit_type} - {classification}" if unit_type and classification else (unit_type or classification)
    get_classification_merged.short_description = "التصنيف"
    get_classification_merged.admin_order_field = 'unit__classification'

    def get_guest_name(self, obj):
        return obj.guest_name or obj.guest_id_no or "---"
    get_guest_name.short_description = "اسم الحاجز"

    def get_colored_status(self, obj):
        from django.utils.html import format_html
        if obj.status == 'غير مؤكد':
            return format_html('<span style="display:inline-block; min-width:80px; text-align:center; background:#e74c3c; color:white; padding:4px 12px; border-radius:6px; font-weight:bold; white-space:nowrap;">⏳ غير مؤكد</span>')
        elif obj.status == 'ملغي':
            return format_html('<span style="display:inline-block; min-width:80px; text-align:center; background:#95a5a6; color:white; padding:4px 12px; border-radius:6px; white-space:nowrap;">ملغي</span>')
        else:
            return format_html('<span style="display:inline-block; min-width:80px; text-align:center; background:#27ae60; color:white; padding:4px 12px; border-radius:6px; font-weight:bold; white-space:nowrap;">✅ مؤكد</span>')
    get_colored_status.short_description = "الحالة"
    get_colored_status.admin_order_field = 'status'

    def get_contract_date(self, obj):
        if obj.record_date:
            from django.utils.timezone import localtime
            return localtime(obj.record_date).strftime("%Y-%m-%d")
        return "---"
    get_contract_date.short_description = "تاريخ التعاقد"
    get_contract_date.admin_order_field = 'record_date'

    def get_combined_booking_type(self, obj):
        from django.utils.html import format_html
        if obj.booking_type == 'LOTTERY':
            return format_html('<span style="background:#8e44ad; color:white; padding:3px 10px; border-radius:4px; font-weight:bold;">🎲 قرعة</span>')
        elif obj.booking_type == 'STANDARD':
            return format_html('<span style="background:#3498db; color:white; padding:3px 10px; border-radius:4px;">حجز عادي</span>')
        elif obj.booking_type == 'ARMIES_REGIONS':
            return format_html('<span style="background:#f39c12; color:white; padding:3px 10px; border-radius:4px; font-weight:bold;">🎖️ الجيوش والمناطق</span><br><span style="font-size:11px; color:#555;">{}</span>', obj.army_region)
        elif obj.booking_type == 'ALLOCATIONS':
            return format_html('<span style="background:#c0392b; color:white; padding:3px 10px; border-radius:4px; font-weight:bold;">🏛️ مخصصات</span><br><span style="font-size:11px; color:#555;">{}</span>', obj.army_region)
        else:
            return format_html('<span style="background:#f39c12; color:white; padding:3px 10px; border-radius:4px;">{}</span>', obj.get_booking_type_display())
    get_combined_booking_type.short_description = "نوع الحجز والتصنيف"
    get_combined_booking_type.admin_order_field = 'booking_type'

    def get_membership_no_readonly(self, obj):
        if obj and obj.member:
            return obj.member.membership_no
        return (obj.guest_id_no if obj else None) or "---"
    get_membership_no_readonly.short_description = "رقم العضوية (من العضو المرتبط)"

    def get_member_name_readonly(self, obj):
        if obj and obj.member:
            return obj.member.full_name
        return (obj.guest_name if obj else None) or "---"
    get_member_name_readonly.short_description = "الاسم الكامل"

    def get_member_phone_readonly(self, obj):
        if obj and obj.member:
            return getattr(obj.member, 'phone_number', '') or getattr(obj.member, 'phone', '---')
        return "---"
    get_member_phone_readonly.short_description = "رقم الهاتف"

    def get_member_rank_readonly(self, obj):
        if obj and obj.member:
            return obj.member.rank
        return (obj.guest_rank if obj else None) or "---"
    get_member_rank_readonly.short_description = "الرتبة"

    fieldsets = (
        ("بيانات الشخص", {
            'fields': (
                ('person_type',),
                ('member',),
                ('guest_id_no', 'guest_name'),
                ('guest_phone', 'guest_rank'),
                ('beneficiary_relation', 'beneficiary'),
            )
        }),
        ("بيانات الوحدة", {
            'fields': (
                ('club', 'building', 'unit'),
                ('unit_type', 'classification'),
                ('units',),
            )
        }),
        ("بيانات الفترة", {
            'fields': (
                ('period', 'start_date', 'end_date'),
            )
        }),
        ("بيانات الحجز والماليات", {
            'fields': (
                ('booking_type', 'status', 'contract_no'),
                ('total_price', 'payment_deadline'),
                ('is_plus_50', 'discount_percentage'),
            )
        }),
        ("ملاحظات", {
            'fields': ('notes',),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(self.fieldsets)
        if obj:
            # Editing existing booking - remove 'units' from fieldsets
            new_fieldsets = []
            for name, opts in fieldsets:
                new_opts = opts.copy()
                new_fields = []
                for field in opts['fields']:
                    if isinstance(field, (list, tuple)):
                        # Handle nested fields (tuples)
                        new_tuple = tuple(f for f in field if f != 'units')
                        if new_tuple:
                            new_fields.append(new_tuple)
                    elif field != 'units':
                        new_fields.append(field)
                new_opts['fields'] = tuple(new_fields)
                new_fieldsets.append((name, new_opts))
            return tuple(new_fieldsets)
        return fieldsets

    def save_model(self, request, obj, form, change):
        if obj.member:
            member_modified = False
            if obj.guest_name and obj.member.full_name != obj.guest_name:
                obj.member.full_name = obj.guest_name
                member_modified = True
            if obj.guest_rank and obj.member.rank != obj.guest_rank:
                obj.member.rank = obj.guest_rank
                member_modified = True
            if obj.guest_phone and obj.member.phone != obj.guest_phone:
                obj.member.phone = obj.guest_phone
                member_modified = True
            if member_modified:
                obj.member.save()

        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            changes = []
            for field in form.changed_data:
                if not hasattr(old_obj, field):
                    continue
                old_val = getattr(old_obj, field)
                new_val = getattr(obj, field)
                changes.append(f"{field}: {old_val} -> {new_val}")
            
            from audit.utils import log_event
            log_event(
                action="UPDATE",
                object_type="Booking",
                object_id=str(obj.pk),
                message=f"تعديل حجز: {', '.join(changes)}",
                user=request.user
            )
            super().save_model(request, obj, form, change)
        else:
            units = form.cleaned_data.get('units')
            if units and len(units) > 0:
                obj.unit = units[0]
                super().save_model(request, obj, form, change)
                
                # Duplicate for remaining units
                for u in units[1:]:
                    obj.pk = None
                    obj.unit = u
                    super().save_model(request, obj, form, change)
            else:
                super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        from audit.utils import log_event
        log_event(
            action="DELETE",
            object_type="Booking",
            object_id=str(obj.pk),
            message=f"إلغاء حجز نهائياً للمستفيد: {obj.guest_name}",
            metadata={
                "guest_name": obj.guest_name,
                "unit": str(obj.unit),
                "dates": f"{obj.start_date} to {obj.end_date}",
                "id_no": obj.guest_id_no
            },
            user=request.user
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        from audit.utils import log_event
        for obj in queryset:
            log_event(
                action="DELETE",
                object_type="Booking",
                object_id=str(obj.pk),
                message=f"حذف جماعي - إلغاء حجز: {obj.guest_name}",
                metadata={"guest_name": obj.guest_name, "unit": str(obj.unit)},
                user=request.user
            )
        super().delete_queryset(request, queryset)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-buildings-for-club/', self.admin_site.admin_view(self.get_buildings_view), name='get_buildings_by_club'),
            path('get-units-for-building/', self.admin_site.admin_view(self.get_units_view), name='get_units_by_building'),
            path('get-unit-details/', self.admin_site.admin_view(self.get_unit_details_view), name='get_unit_details'),
            path('get-period-dates/', self.admin_site.admin_view(self.get_period_dates_view), name='get_period_dates'),
            path('get-member-details/', self.admin_site.admin_view(self.get_member_details_view), name='get_member_details'),
        ]
        return custom_urls + urls

    def get_buildings_view(self, request):
        club_id = request.GET.get('club_id')
        if club_id:
            builds = Building.objects.filter(club_id=club_id).order_by('name')
            data = [{"id": b.id, "name": b.name} for b in builds]
            return JsonResponse({"buildings": data})
        return JsonResponse({"buildings": []})

    def get_units_view(self, request):
        building_id = request.GET.get('building_id')
        
        if not building_id:
            return JsonResponse({"units": []})

        qs = Unit.objects.filter(
            floor__building_id=building_id,
            is_bookable=True,
            is_maintenance=False
        )
        qs = qs.select_related('floor__building').order_by('floor__level_number', 'unit_no')
        
        data = [{"id": u.id, "name": f"{u.unit_no} - {u.classification}" if u.classification else u.unit_no, "classification": u.classification} for u in qs]
        return JsonResponse({"units": data})

    def get_unit_details_view(self, request):
        unit_id = request.GET.get('unit_id')
        if unit_id:
            try:
                u = Unit.objects.select_related('floor__building__club').get(id=unit_id)
                return JsonResponse({
                    "classification": u.classification,
                    "unit_type": u.get_unit_type_display(),
                    "building_id": u.floor.building_id,
                    "club_id": u.floor.building.club_id
                })
            except Unit.DoesNotExist:
                pass
        return JsonResponse({"error": "Not found"}, status=404)

    def get_period_dates_view(self, request):
        from inventory.models import Period
        period_id = request.GET.get('period_id')
        if period_id:
            try:
                p = Period.objects.get(id=period_id)
                return JsonResponse({
                    "start_date": p.start_date.strftime("%Y-%m-%d"),
                    "end_date": p.end_date.strftime("%Y-%m-%d")
                })
            except Period.DoesNotExist:
                pass
        return JsonResponse({"error": "Not found"}, status=404)

    def get_member_details_view(self, request):
        membership_no = request.GET.get('membership_no')
        if membership_no:
            from members.models import Member
            from django.db.models import Q
            try:
                if membership_no.isdigit():
                    m = Member.objects.filter(Q(membership_no=membership_no) | Q(id=int(membership_no))).first()
                else:
                    m = Member.objects.filter(membership_no=membership_no).first()
                
                if m:
                    dependents = m.family_members.all()
                    deps_data = [{"name": d.name, "relation": d.relation, "national_id": d.national_id} for d in dependents]
                    return JsonResponse({
                        "found": True,
                        "membership_no": m.membership_no,
                        "name": m.full_name,
                        "rank": m.rank,
                        "phone": m.phone,
                        "dependents": deps_data
                    })
            except Exception:
                pass
        return JsonResponse({"found": False})

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["member", "period", "status", "created_at"]
    list_filter = ["status", "period"]
    search_fields = ["member__full_name", "member__membership_no"]
    raw_id_fields = ["member", "wish1", "wish2", "wish3", "wish4", "wish5"]

@admin.register(LotteryExclusion)
class LotteryExclusionAdmin(admin.ModelAdmin):
    list_display = ["member", "period", "reason"]
    list_filter = ["period"]
    search_fields = ["member__full_name"]
    raw_id_fields = ["member"]

@admin.register(LotteryDraft)
class LotteryDraftAdmin(admin.ModelAdmin):
    list_display = ["application", "won_unit", "wish_number", "is_finalized"]
    list_filter = ["is_finalized", "application__period"]
    actions = ["finalize_results"]

    def finalize_results(self, request, queryset):
        # Logic to convert draft results to real bookings would go here
        queryset.update(is_finalized=True)
        self.message_user(request, f"تم اعتماد {queryset.count()} نتيجة بنجاح.")
    finalize_results.short_description = "اعتماد النتائج النهائية"

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["booking", "contract_date", "is_signed"]
    list_filter = ["is_signed"]
    search_fields = ["booking__guest_name", "booking__contract_no"]

@admin.register(LotteryResult)
class LotteryResultAdmin(admin.ModelAdmin):
    list_display = ["membership_no", "member_name", "club_name", "unit_no", "period_no", "is_imported_to_bookings"]
    list_filter = ["period_no", "club_name", "is_imported_to_bookings"]
    search_fields = ["membership_no", "member_name", "unit_no"]
    actions = ["import_from_excel_file_action", "convert_to_booking"]

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='bookings_lotteryresult_import_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        import openpyxl

        if request.method == "POST":
            excel_file = request.FILES.get('excel_file')
            clear_existing = request.POST.get('clear_existing') == '1'
            
            if not excel_file:
                messages.error(request, "لم يتم رفع أي ملف.")
                return redirect('.')
            
            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, "تنسيق الملف غير مدعوم. يجب أن يكون ملف Excel بصيغة .xlsx فقط.")
                return redirect('.')
            
            try:
                wb = openpyxl.load_workbook(excel_file, read_only=True)
                ws = wb.active
                
                if clear_existing:
                    deleted = LotteryResult.objects.count()
                    LotteryResult.objects.all().delete()
                    messages.info(request, f"تم مسح {deleted} سجل قرعة سابق.")

                imported = 0
                updated = 0
                skipped = 0
                
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if len(row) < 7:
                        skipped += 1
                        continue
                    
                    _, mem_no_val, member_name, club_name, unit_desc, unit_no_val, period_val = row[:7]
                    phone_val = row[7] if len(row) > 7 else ''
                    
                    membership_no = str(int(mem_no_val)) if mem_no_val is not None else ''
                    member_name = str(member_name) if member_name else ''
                    club_name = str(club_name) if club_name else ''
                    unit_description = str(unit_desc) if unit_desc else ''
                    unit_no = str(int(unit_no_val)) if unit_no_val is not None else ''
                    period_no = int(period_val) if period_val is not None else 0
                    phone = str(phone_val) if phone_val else ''
                    
                    if phone.endswith('.0'):
                        phone = phone[:-2]

                    if not membership_no or not unit_no:
                        skipped += 1
                        continue

                    _, created = LotteryResult.objects.update_or_create(
                        membership_no=membership_no,
                        club_name=club_name,
                        unit_no=unit_no,
                        period_no=period_no,
                        defaults={
                            'member_name': member_name,
                            'unit_description': unit_description,
                            'phone': phone,
                        }
                    )
                    if created:
                        imported += 1
                    else:
                        updated += 1
                
                wb.close()
                
                # Automatically run the lottery sync to update/create bookings!
                from .services import sync_lottery_results_to_bookings
                total, paid, unpaid, errs = sync_lottery_results_to_bookings()
                
                messages.success(
                    request,
                    f"تمت العملية بنجاح! تم استيراد {imported} سجل جديد، وتحديث {updated} سجل موجود، وتجاوز {skipped} سجل فارغ. "
                    f"وتمت المزامنة لغرف لوحة المتابعة: {paid} حجز قرعة مؤكد (مدفوع)، {unpaid} حجز قرعة منتظر السداد."
                )
                return redirect('..')
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء استيراد الملف: {str(e)}")
                return redirect('.')

        context = self.admin_site.each_context(request)
        context['title'] = "استيراد نتائج القرعة من إكسل"
        return render(request, 'admin/bookings/lotteryresult/import_excel.html', context)

    def import_from_excel_file_action(self, request, queryset):
        from django.shortcuts import redirect
        return redirect('import-excel/')
    import_from_excel_file_action.short_description = "استيراد نتائج قرعة جديدة من ملف إكسل مخصص"

    def convert_to_booking(self, request, queryset):
        from .services import sync_lottery_results_to_bookings
        total, paid, unpaid, errs = sync_lottery_results_to_bookings()
        self.message_user(
            request, 
            f"تمت مزامنة القرعة بنجاح! إجمالي المعالجة: {total} سجل. "
            f"المؤكد (المدفوع): {paid}، والمنتظر (غير المدفوع): {unpaid}. "
            f"التصادمات/الأخطاء المكتشفة: {errs}."
        )
    convert_to_booking.short_description = "تفعيل مزامنة وتحديث القرعة بالكامل في لوحة المتابعة"
