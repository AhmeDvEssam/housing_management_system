from django.contrib import admin
from bookings.admin import BookingAdmin, SubCategoryFilter
from .models import DailyBookingReport, FaxReport, VacanciesReport
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import datetime

class RecordDatePeriodFilter(admin.ListFilter):
    title = ''
    template = 'admin/filter_empty.html'
    
    def __init__(self, request, params, model, model_admin):
        self.from_date = request.GET.get('from_date', '')
        self.to_date = request.GET.get('to_date', '')
        
        params.pop('from_date', None)
        params.pop('to_date', None)
        
        super().__init__(request, params, model, model_admin)
        
    def has_output(self):
        return True
        
    def choices(self, changelist):
        return []
        
    def expected_parameters(self):
        return ['from_date', 'to_date']
        
    def queryset(self, request, queryset):
        if self.from_date and self.from_date.strip():
            queryset = queryset.filter(record_date__date__gte=self.from_date.strip())
        if self.to_date and self.to_date.strip():
            queryset = queryset.filter(record_date__date__lte=self.to_date.strip())
        return queryset

@admin.register(DailyBookingReport)
class DailyBookingReportAdmin(BookingAdmin):
    change_list_template = "admin/reports/daily_booking_report/change_list.html"
    
    list_filter = ["booking_type", SubCategoryFilter, "person_type", "unit__floor__building__club", "unit__classification", RecordDatePeriodFilter]
    
    ordering = ["unit__floor__building__club__name", "unit__unit_no"]
    
    list_display = ["get_guest_name", "get_membership_no", "get_club", "get_unit_only", "get_classification_merged", "start_date", "end_date", "get_contract_price_display", "get_combined_booking_type", "get_contract_date_display"]

    def get_unit_only(self, obj):
        return obj.unit.unit_no if obj.unit else "-"
    get_unit_only.short_description = "الوحدة"

    def has_add_permission(self, request):
        return False

    def get_contract_date_display(self, obj):
        if obj.record_date:
            from django.utils.timezone import localtime
            return localtime(obj.record_date).strftime("%Y-%m-%d")
        return "---"
    get_contract_date_display.short_description = "تاريخ الاضافة"
    get_contract_date_display.admin_order_field = 'record_date'

    def get_contract_price_display(self, obj):
        from django.utils.html import format_html
        db_price = int(obj.total_price) if obj.total_price else 0
        _, live_price_val = obj.calculate_live_price()
        live_price = int(live_price_val) if live_price_val else 0
        return format_html(
            '<span class="price-val price-db" data-val="{}">{}</span>'
            '<span class="price-val price-rules" data-val="{}" style="display:none;">{}</span>',
            db_price, db_price, live_price, live_price
        )
    get_contract_price_display.short_description = "قيمة العقد"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('companions')

    @method_decorator(cache_page(60))
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        if from_date is None and to_date is None:
            today_str = datetime.date.today().strftime('%Y-%m-%d')
            extra_context['selected_from'] = today_str
            extra_context['selected_to'] = today_str
            
            q = request.GET.copy()
            q['from_date'] = today_str
            q['to_date'] = today_str
            request.GET = q
        else:
            extra_context['selected_from'] = from_date or ''
            extra_context['selected_to'] = to_date or ''
            
        try:
            cl = self.get_changelist_instance(request)
            qs = cl.get_queryset(request)
            total_db = 0
            total_rules = 0
            for b in qs:
                db_val = int(b.total_price) if b.total_price else 0
                total_db += db_val
                
                rule_val = b.calculate_live_price()[1]
                total_rules += int(rule_val) if rule_val else 0
                
            extra_context['global_total_db'] = total_db
            extra_context['global_total_rules'] = total_rules
        except Exception:
            extra_context['global_total_db'] = 0
            extra_context['global_total_rules'] = 0
            
        return admin.ModelAdmin.changelist_view(self, request, extra_context=extra_context)

@admin.register(FaxReport)
class FaxReportAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('fax_report'))

    def has_add_permission(self, request):
        return False

@admin.register(VacanciesReport)
class VacanciesReportAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('vacancies_report'))

    def has_add_permission(self, request):
        return False

