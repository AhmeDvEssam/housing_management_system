from datetime import datetime, timedelta
import datetime as dt_module
from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# صلاحية مخصصة للوحة المتابعة
dashboard_access = user_passes_test(lambda u: u.is_superuser or u.has_perm('dashboard.view_wallboard'))
vacancies_report_access = user_passes_test(lambda u: u.is_superuser or u.has_perm('reports.view_vacanciesreport'))
fax_report_access = user_passes_test(lambda u: u.is_superuser or u.has_perm('reports.view_faxreport'))
from bookings.models import BookingType, BookingDay, Booking, FaxPrintHistory
from inventory.models import Club, Building, Floor, Unit, Allocation, UnitType, AllocationType, Period

STATUS_LABELS = {
    "AVAILABLE": "متاح",
    "OCCUPIED": "مشغول",
    "RESERVED": "محجوز",
    "LOTTERY_PENDING": "قرعة غير مؤكدة",
    "LOTTERY_CONFIRMED": "قرعة مؤكدة",
    "ALLOCATED": "مخصصات",
    "MAINTENANCE": "تحت الصيانة",
    "NOT_BOOKABLE": "غير قابل للحجز",
    "HOSPITALITY": "ضيافة",
}



def parse_date(value: str | None) -> dt_module.date:
    if not value:
        return timezone.localdate()
    # Normalize slashes to dashes and handle multiple common formats
    val_clean = value.strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val_clean, fmt).date()
        except ValueError:
            continue
    raise ValueError("صيغة التاريخ يجب أن تكون DD-MM-YYYY أو YYYY-MM-DD")

def compute_unit_status(unit: Unit, booking, target_date) -> str:
    if unit.is_maintenance:
        return "MAINTENANCE"
    if booking:
        if booking.booking_type == BookingType.LOTTERY:
            if booking.status == "غير مؤكد":
                return "LOTTERY_PENDING"
            else:
                return "LOTTERY_CONFIRMED"
        if booking.start_date <= target_date <= booking.end_date:
            return "OCCUPIED"
        return "RESERVED"
    if unit.allocation:
        return "ALLOCATED"
    if not unit.is_bookable:
        return "NOT_BOOKABLE"
    return "AVAILABLE"

def apply_unit_filters(units_qs, request):
    club_id = request.query_params.get("club")
    building_id = request.query_params.get("building")
    floor_id = request.query_params.get("floor")
    view_type = request.query_params.get("view_type")
    capacity_min = request.query_params.get("capacity")
    classification = request.query_params.get("classification")
    unit_type = request.query_params.get("unit_type")
    allocation = request.query_params.get("allocation")

    if club_id:
        units_qs = units_qs.filter(floor__building__club_id=club_id)
    if building_id:
        units_qs = units_qs.filter(floor__building_id=building_id)
    if floor_id:
        units_qs = units_qs.filter(floor_id=floor_id)
    if view_type:
        units_qs = units_qs.filter(view_type=view_type)
    if capacity_min:
        try:
            capacity_value = int(capacity_min)
            units_qs = units_qs.filter(capacity__gte=capacity_value)
        except ValueError:
            return units_qs, "قيمة السعة غير صالحة"
    if classification:
        units_qs = units_qs.filter(classification=classification)
    if unit_type:
        units_qs = units_qs.filter(unit_type=unit_type)
    if allocation:
        units_qs = units_qs.filter(allocation=allocation)

    return units_qs, None

import re

def natural_sort_key(s):
    if not s: return []
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]

def get_sorted_periods():
    """Return periods sorted naturally by their name number (الأسبوع 1, 2, ... 10, 11, ...)"""
    periods = list(Period.objects.all())
    periods.sort(key=lambda p: natural_sort_key(p.name))
    return periods

@method_decorator(cache_page(120), name='dispatch')
@method_decorator(dashboard_access, name='dispatch')
class WallboardPageView(APIView):
    def get(self, request):
        clubs = list(Club.objects.all())
        clubs.sort(key=lambda c: natural_sort_key(c.name))
        
        buildings = list(Building.objects.select_related("club").all())
        buildings.sort(key=lambda b: (natural_sort_key(b.club.name), natural_sort_key(b.name)))
        
        from bookings.models import PersonTypeChoices
        context = {
            "clubs": clubs,
            "buildings": buildings,
            "floors": Floor.objects.select_related("building").order_by("level_number"),
            "view_types": Unit.objects.exclude(view_type="").values_list("view_type", flat=True).distinct(),
            "classifications": Unit.objects.exclude(classification="").values_list("classification", flat=True).distinct(),
            "unit_types": [
                (code, label) for code, label in UnitType.choices 
                if code in Unit.objects.values_list("unit_type", flat=True).distinct()
            ],
            "allocations": AllocationType.choices,
            "armies_regions": [c[0] for c in Booking.objects.exclude(army_region="").values_list("army_region").distinct()],
            "status_labels": STATUS_LABELS,
            "periods": get_sorted_periods(),
            "person_types": PersonTypeChoices.choices,
        }
        # Add metadata for frontend cascading filters
        units_metadata = list(Unit.objects.values(
            "floor__building__club_id", 
            "floor__building_id", 
            "floor_id",
            "classification",
            "unit_type"
        ).distinct())
        import json
        context["units_metadata_json"] = json.dumps(units_metadata)
        return render(request, "dashboard/wallboard.html", context)

@method_decorator(cache_page(60), name='dispatch')
@method_decorator(dashboard_access, name='dispatch')
class WallboardApiView(APIView):
    def get(self, request):
        try:
            start_date = parse_date(request.query_params.get("date"))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        end_date_param = request.query_params.get("end_date")
        
        if end_date_param:
            try:
                end_date = parse_date(end_date_param)
                days = (end_date - start_date).days + 1
                if days < 1: days = 1
                if days > 45: days = 45 # Limit range for performance
            except ValueError:
                days = 7
                end_date = start_date + timedelta(days=days-1)
        else:
            days = 7
            end_date = start_date + timedelta(days=days-1)

        dates = [start_date + timedelta(days=i) for i in range(days)]

        units_qs = Unit.objects.select_related(
            "floor", "floor__building", "floor__building__club"
        ).prefetch_related("allocations")
        status_filter = request.query_params.get("status")
        booking_type_filter = request.query_params.get("booking_type")

        units_qs, error = apply_unit_filters(units_qs, request)
        if error:
            return Response({"detail": error}, status=400)

        units = list(units_qs)
        # Apply natural sorting: Unit No (Small to Big), then Building, then Floor
        units.sort(key=lambda u: (
            natural_sort_key(u.unit_no),
            natural_sort_key(u.floor.building.name),
            u.floor.level_number
        ))

        if not units:
            return Response(
                {
                    "start_date": start_date.strftime("%d-%m-%Y"),
                    "days": days,
                    "dates": [day.strftime("%d-%m-%Y") for day in dates],
                    "units": [],
                }
            )

        bookings = Booking.objects.filter(
            unit__in=units, 
            start_date__lte=end_date, 
            end_date__gte=start_date,
            status__in=["مؤكد", "مبدئي", "غير مؤكد", "مكتمل"]
        ).select_related("member")

        bookings_map = {unit.id: {} for unit in units}
        for booking in bookings:
            curr = booking.start_date
            while curr <= booking.end_date:
                if start_date <= curr <= end_date:
                    bookings_map[booking.unit_id][curr] = booking
                curr += timedelta(days=1)

        from django.db.models import Count
        unit_ids = [u.id for u in units]
        future_bookings_qs = Booking.objects.filter(
            unit_id__in=unit_ids,
            start_date__gt=start_date,
            status__in=["مؤكد", "مبدئي", "غير مؤكد"]
        ).values('unit_id').annotate(count=Count('id'))
        future_bookings_map = {item['unit_id']: item['count'] for item in future_bookings_qs}

        # Calculate lottery counts in backend for the selected units across the entire year
        lottery_summary_qs = Booking.objects.filter(
            unit_id__in=unit_ids,
            booking_type=BookingType.LOTTERY,
            start_date__year=start_date.year
        )
        lottery_summary = {
            "total": lottery_summary_qs.count(),
            "confirmed": lottery_summary_qs.filter(status='مؤكد').count(),
            "pending": lottery_summary_qs.filter(status='غير مؤكد').count()
        }

        # Bulk query for lottery bookings to avoid N+1 queries when filtering by lottery status
        lottery_unit_ids = set()
        if status_filter in ('LOTTERY_ALL', 'LOTTERY_CONFIRMED', 'LOTTERY_PENDING'):
            lottery_qs = Booking.objects.filter(
                unit_id__in=unit_ids,
                booking_type=BookingType.LOTTERY,
                start_date__year=start_date.year
            )
            if status_filter == 'LOTTERY_CONFIRMED':
                lottery_qs = lottery_qs.filter(status='مؤكد')
            elif status_filter == 'LOTTERY_PENDING':
                lottery_qs = lottery_qs.filter(status='غير مؤكد')
            lottery_unit_ids = set(lottery_qs.values_list('unit_id', flat=True))

        unit_rows = []
        kpis = {
            "total": len(units),
            "available": 0,
            "occupied": 0,
            "reserved": 0,
            "alloc_total": 0,
            "alloc_free": 0,
            "alloc_busy": 0,
        }

        for unit in units:
            day_statuses = []
            
            # KPI Calculation over the entire selected period
            unit_days_map = bookings_map.get(unit.id, {})
            is_occupied_in_period = False
            for day in dates:
                if unit_days_map.get(day):
                    is_occupied_in_period = True
                    break
            
            if is_occupied_in_period:
                kpis["occupied"] += 1
            else:
                if unit.is_bookable and not unit.is_maintenance:
                    kpis["available"] += 1

            # Future reservations count (Count how many units are reserved, not how many future bookings exist)
            if future_bookings_map.get(unit.id, 0) > 0:
                kpis["reserved"] += 1

            if unit.allocation:
                kpis["alloc_total"] += 1
                if is_occupied_in_period:
                    kpis["alloc_busy"] += 1
                else:
                    kpis["alloc_free"] += 1
            
            current_booking = unit_days_map.get(start_date)
            current_status = compute_unit_status(unit, current_booking, start_date)

            current_booking_type = (current_booking.booking_type if current_booking else None)

            # Filtering logic
            if status_filter:
                if status_filter == 'ALLOCATED_ALL':
                    if not unit.allocation: continue
                elif status_filter == 'ALLOCATED_FREE':
                    if not unit.allocation or current_status not in ('ALLOCATED', 'AVAILABLE'): continue
                elif status_filter == 'ALLOCATED_BUSY':
                    if not unit.allocation or current_status not in ('OCCUPIED', 'RESERVED'): continue
                elif status_filter == 'RESERVED':
                    if current_status != 'RESERVED' and future_bookings_map.get(unit.id, 0) == 0:
                        continue
                elif status_filter in ('LOTTERY_ALL', 'LOTTERY_CONFIRMED', 'LOTTERY_PENDING'):
                    if unit.id not in lottery_unit_ids:
                        continue
                elif current_status != status_filter:
                    continue
            if booking_type_filter:
                if not current_booking or current_booking.booking_type != booking_type_filter:
                    continue
            
            army_region_filter = request.query_params.get("army_region")
            if army_region_filter:
                if not current_booking or current_booking.army_region != army_region_filter:
                    continue
            
            # Rank Filter (simplified)
            # Person Type Filter
            person_type_filter = request.query_params.get("guest_rank")
            if person_type_filter:
                if not current_booking or current_booking.person_type != person_type_filter:
                    continue

            for day in dates:
                booking = bookings_map.get(unit.id, {}).get(day)
                status = compute_unit_status(unit, booking, day)
                
                display_rank = None
                if booking:
                    display_rank = booking.guest_rank
                    if not display_rank or display_rank in ['---', 'بدون رتبة']:
                        display_rank = booking.member.rank if booking.member else None
                    if display_rank in ['---', 'بدون رتبة']:
                        display_rank = None

                day_statuses.append(
                    {
                        "date": day.strftime("%d-%m-%Y"),
                        "status": status,
                        "label": STATUS_LABELS.get(status, status),
                        "booking_id": booking.id if booking else None,
                        "booking_type": booking.booking_type if booking else None,
                        "booking_guest": f"{display_rank} / {booking.guest_name}" if display_rank and booking.guest_name else (booking.guest_name if booking else None),
                        "booking_rank": booking.get_person_type_display() if booking and booking.person_type else (booking.guest_rank if booking else None),
                        "booking_member_no": booking.member.membership_no if (booking and booking.member) else (booking.guest_id_no if booking else None),
                        "booking_start": booking.start_date.strftime("%d-%m-%Y") if booking else None,
                        "booking_end": booking.end_date.strftime("%d-%m-%Y") if booking else None,
                        "booking_status": booking.status if booking else None,
                        "payment_deadline": booking.payment_deadline.strftime("%d-%m-%Y") if (booking and booking.payment_deadline) else None,
                    }
                )

            unit_rows.append(
                {
                    "id": unit.id,
                    "unit_no": unit.unit_no,
                    "unit_type": unit.unit_type,
                    "unit_type_label": unit.get_unit_type_display(),
                    "classification": unit.classification,
                    "capacity": unit.capacity,
                    "orientation": unit.view_type,
                    "orientation_label": unit.view_type,
                    "club_name": unit.floor.building.club.name,
                    "building": unit.floor.building.name,
                    "floor": unit.floor.level_number,
                    "floor_label": unit.floor.label or f"دور {unit.floor.level_number}",
                    "is_bookable": unit.is_bookable,
                    "is_maintenance": unit.is_maintenance,
                    "statuses": day_statuses,
                    "current_status": current_status,
                    "current_label": STATUS_LABELS.get(current_status, current_status),
                    "current_booking_type": current_booking_type,
                    "allocation": unit.allocation,
                    "allocation_label": dict(AllocationType.choices).get(unit.allocation, unit.allocation) if unit.allocation else "",
                    "allocation_guest": unit.allocations.first().allocated_to if (unit.allocation and unit.allocations.exists()) else "",
                    "future_bookings_count": future_bookings_map.get(unit.id, 0),
                }
            )

        return Response(
            {
                "start_date": start_date.strftime("%d-%m-%Y"),
                "days": days,
                "dates": [day.strftime("%d-%m-%Y") for day in dates],
                "units": unit_rows,
                "lottery_summary": lottery_summary,
                "kpis": kpis,
            }
        )

@method_decorator(cache_page(60), name='dispatch')
@method_decorator(dashboard_access, name='dispatch')
class UnitBookingsApiView(APIView):
    def get(self, request):
        unit_id = request.query_params.get("unit_id")
        if not unit_id:
            return Response({"detail": "رقم الوحدة مطلوب"}, status=400)
            
        date_str = request.query_params.get("date")
        bookings = Booking.objects.filter(
            unit_id=unit_id,
            status__in=["مؤكد", "مبدئي", "غير مؤكد", "مكتمل"]
        )
        if date_str:
            try:
                selected_date = parse_date(date_str)
                bookings = bookings.filter(end_date__gte=selected_date, start_date__year=selected_date.year)
            except (ValueError, TypeError):
                bookings = bookings.filter(start_date__year=timezone.localdate().year)
        else:
            bookings = bookings.filter(start_date__year=timezone.localdate().year)
        bookings = bookings.select_related('member').order_by("start_date")
        
        data = []
        for b in bookings:
            member_no = b.guest_id_no
            phone = ""
            rank = b.guest_rank
            if b.member:
                member_no = b.member.membership_no
                phone = b.member.phone_number if hasattr(b.member, 'phone_number') else getattr(b.member, 'phone', '')
                if not rank:
                    rank = b.member.rank
            
            data.append({
                "id": b.id,
                "guest_name": f"{rank} / {b.guest_name}" if (rank and rank not in ['---', 'بدون رتبة'] and b.guest_name) else (b.guest_name or (b.member.full_name if b.member else "حجز بدون اسم")),
                "membership_no": member_no or "---",
                "phone": phone or "---",
                "rank": rank or "---",
                "booking_type": b.get_booking_type_display(),
                "status": b.status,
                "start_date": b.start_date.strftime("%d-%m-%Y"),
                "end_date": b.end_date.strftime("%d-%m-%Y"),
                "payment_deadline": b.payment_deadline.strftime("%d-%m-%Y") if b.payment_deadline else "---",
                "notes": b.notes or "",
            })
            
        return Response({"bookings": data})

@method_decorator(dashboard_access, name='dispatch')
class UnitStatusApiView(APIView):
    def get(self, request):
        date_value = request.query_params.get("date")
        if not date_value:
            return Response({"detail": "التاريخ مطلوب"}, status=400)
        try:
            target_date = parse_date(date_value)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        units_qs = Unit.objects.select_related(
            "floor", "floor__building", "floor__building__club"
        )
        status_filter = request.query_params.get("status")
        booking_type_filter = request.query_params.get("booking_type")

        units_qs, error = apply_unit_filters(units_qs, request)
        if error:
            return Response({"detail": error}, status=400)

        units = list(units_qs)
        units.sort(key=lambda u: (
            natural_sort_key(u.unit_no),
            natural_sort_key(u.floor.building.name),
            u.floor.level_number
        ))

        bookings = Booking.objects.filter(
            unit__in=units,
            start_date__lte=target_date,
            end_date__gte=target_date,
            status__in=["مؤكد", "مبدئي", "غير مؤكد", "مكتمل"]
        ).select_related("member")
        
        bookings_map = {booking.unit_id: booking for booking in bookings}

        unit_rows = []
        for unit in units:
            booking = bookings_map.get(unit.id)
            status = compute_unit_status(unit, booking, target_date)
            booking_type = booking.booking_type if booking else None

            if status_filter:
                if status_filter == 'LOTTERY_ALL':
                    if status not in ('LOTTERY_PENDING', 'LOTTERY_CONFIRMED'): continue
                elif status_filter == 'LOTTERY_CONFIRMED':
                    if status != 'LOTTERY_CONFIRMED': continue
                elif status_filter == 'LOTTERY_PENDING':
                    if status != 'LOTTERY_PENDING': continue
                elif status != status_filter:
                    continue
            if booking_type_filter:
                if not booking or booking.booking_type != booking_type_filter:
                    continue

            unit_rows.append(
                {
                    "id": unit.id,
                    "unit_no": unit.unit_no,
                    "unit_type": unit.unit_type,
                    "unit_type_label": unit.get_unit_type_display(),
                    "capacity": unit.capacity,
                    "orientation": unit.view_type,
                    "orientation_label": unit.view_type,
                    "club": unit.floor.building.club.name,
                    "building": unit.floor.building.name,
                    "floor": unit.floor.level_number,
                    "floor_label": unit.floor.label or f"دور {unit.floor.level_number}",
                    "status": status,
                    "label": STATUS_LABELS[status],
                    "booking_id": booking.id if booking else None,
                    "booking_type": booking_type,
                }
            )

        return Response(
            {
                "date": target_date.strftime("%d-%m-%Y"),
                "units": unit_rows,
            }
        )

from django.views import View

@method_decorator(cache_page(120), name='dispatch')
@method_decorator(vacancies_report_access, name='dispatch')
class VacanciesReportView(View):
    def get(self, request):
        date_from = None
        date_to = None
        period_id = request.GET.get("period")
        if period_id:
            try:
                period = Period.objects.get(id=period_id)
                date_from = period.start_date
                date_to = period.end_date
            except Period.DoesNotExist:
                pass

        if not date_from:
            try:
                d_from_str = request.GET.get("from")
                if d_from_str:
                    date_from = parse_date(d_from_str)
                else:
                    date_from = timezone.localdate()
                d_to_str = request.GET.get("to")
                date_to = parse_date(d_to_str) if d_to_str else date_from
                if date_from > date_to: date_from, date_to = date_to, date_from
            except ValueError as exc:
                from django.http import HttpResponseBadRequest
                return HttpResponseBadRequest(str(exc))
            
        club_id = request.GET.get("club")
        if not club_id:
            return render(request, "dashboard/vacancies_report.html", {"clubs": Club.objects.all(), "periods": get_sorted_periods()})
            
        club = Club.objects.get(id=club_id)
        buildings_qs = Building.objects.filter(club=club)
        buildings = list(buildings_qs)
        buildings.sort(key=lambda b: natural_sort_key(b.name))
        
        # Prefetch data
        bookings = Booking.objects.filter(
            unit__floor__building__club=club,
            start_date__lte=date_to,
            end_date__gte=date_from,
            status__in=["مؤكد", "مبدئي", "غير مؤكد", "مكتمل"]
        ).select_related("member")
        
        bookings_map = {}
        for b in bookings:
            bookings_map[b.unit_id] = b
        
        buildings_data = []
        
        # Fetch all units in one query and sort naturally
        all_units = list(Unit.objects.filter(floor__building__in=buildings).select_related('floor__building'))
        all_units.sort(key=lambda u: (
            natural_sort_key(u.unit_no),
            natural_sort_key(u.floor.building.name),
            u.floor.level_number
        ))
        units_by_building = {}
        for u in all_units:
            units_by_building.setdefault(u.floor.building_id, []).append(u)
            
        for b in buildings:
            available = []
            reserved = []
            
            units = units_by_building.get(b.id, [])
            for u in units:
                booking = bookings_map.get(u.id)
                status = compute_unit_status(u, booking, date_from)
                
                alloc_display = dict(AllocationType.choices).get(u.allocation, u.allocation) if u.allocation else ("مشغول" if status=="OCCUPIED" else STATUS_LABELS.get(status, status))
                is_commander = (u.allocation == 'COMMANDER') or (booking and booking.booking_type == 'COMMANDER')
                
                info = {
                    "unit_no": u.unit_no,
                    "type": u.get_unit_type_display(),
                    "classification": u.classification,
                    "status": STATUS_LABELS.get(status, status),
                    "allocation_info": alloc_display,
                    "allocation": u.allocation,
                    "is_commander": is_commander,
                }
                
                if status == "AVAILABLE":
                    available.append(info)
                else:
                    reserved.append(info)
            
            buildings_data.append({
                "building": b,
                "available_units": available,
                "allocated_units": reserved
            })

        context = {
            "clubs": Club.objects.all(),
            "periods": get_sorted_periods(),
            "selected_club": club,
            "date_from": date_from.strftime("%d-%m-%Y"),
            "date_to": date_to.strftime("%d-%m-%Y"),
            "buildings_data": buildings_data
        }
        return render(request, "dashboard/vacancies_report.html", context)

@method_decorator(cache_page(120), name='dispatch')
@method_decorator(fax_report_access, name='dispatch')
class FaxReportView(View):
    def get(self, request):
        club_id = request.GET.get("club")
        date_from = request.GET.get("from")
        date_to = request.GET.get("to")
        period_id = request.GET.get("period")
        
        context_base = {
            "clubs": Club.objects.all(),
            "periods": get_sorted_periods()
        }
        
        history_id = request.GET.get("history_id")
        
        if history_id:

            history = FaxPrintHistory.objects.get(id=history_id)
            bookings = list(history.bookings.all().select_related("unit", "member"))
            is_addendum = True
            supplement_number = history.supplement_number
            club = history.club
            period_id = history.period_id
            if history.period:
                date_from = history.period.start_date.strftime("%d-%m-%Y")
                date_to = history.period.end_date.strftime("%d-%m-%Y")
                d_from = history.period.start_date
                d_to = history.period.end_date
            else:
                date_from = ""
                date_to = ""
                d_from = None
                d_to = None
        else:
            if not club_id or not date_from or not date_to:
                return render(request, "dashboard/fax_report.html", context_base)
                
            try:
                d_from = parse_date(date_from)
                d_to = parse_date(date_to)
            except ValueError as exc:
                from django.http import HttpResponseBadRequest
                return HttpResponseBadRequest(str(exc))
                
            club = Club.objects.get(id=club_id)
            bookings = list(Booking.objects.filter(
                unit__floor__building__club=club,
                start_date__lte=d_to,
                end_date__gte=d_from,
                status__in=["مؤكد", "مكتمل"]
            ).select_related("unit", "member"))

            is_addendum = request.GET.get("is_addendum") == "1"
            printed_booking_ids = set()
            supplement_number = 0
            
            histories = FaxPrintHistory.objects.filter(club=club, period_id=period_id).order_by('print_date')
            if histories.exists():
                supplement_number = histories.last().supplement_number + 1
                for h in histories:
                    printed_booking_ids.update(h.bookings.values_list('id', flat=True))
            
            if is_addendum:
                bookings = [b for b in bookings if b.id not in printed_booking_ids]

        # Natural sort by unit number then start_date
        bookings.sort(key=lambda b: (natural_sort_key(b.unit.unit_no), b.start_date))

        for b in bookings:
            if b.contract_no:
                b.contract_display = b.contract_no
            else:
                duration = (b.end_date - b.start_date).days
                if duration < 7:
                    b.contract_display = "فردي"
                else:
                    b.contract_display = ""
            
            if b.guest_name and '/' in b.guest_name:
                b.guest_name = b.guest_name.split('/', 1)[-1].strip()
        
        commander_units_qs = Unit.objects.filter(floor__building__club=club, allocation='COMMANDER').order_by('unit_no')
        
        if 'd_from' in locals() and 'd_to' in locals() and d_from and d_to:
            all_booked_units = Booking.objects.filter(
                unit__floor__building__club=club,
                start_date__lte=d_to,
                end_date__gte=d_from,
                status__in=["مؤكد", "مكتمل"]
            ).values_list('unit__unit_no', flat=True)
            booked_unit_nos = {str(u) for u in all_booked_units}
        else:
            booked_unit_nos = {str(b.unit.unit_no) for b in bookings}
            
        commander_units = [str(u.unit_no) for u in commander_units_qs if str(u.unit_no) not in booked_unit_nos]
        
        context = {
            **context_base,
            "selected_club": club,
            "date_from": date_from,
            "date_to": date_to,
            "bookings": bookings,
            "today": timezone.localdate().strftime("%d-%m-%Y"),
            "commander_units": commander_units,
            "selected_period": period_id,
            "supplement_number": supplement_number if is_addendum else 0,
            "is_addendum": is_addendum
        }
        return render(request, "dashboard/fax_report.html", context)

    def post(self, request):
        import json
        try:
            data = json.loads(request.body)
            club_id = data.get("club_id")
            period_id = data.get("period_id")
            booking_ids = data.get("booking_ids", [])
            
            if not club_id or not booking_ids:
                from django.http import JsonResponse
                return JsonResponse({"error": "Missing data"}, status=400)
                

            
            # Find the next supplement number
            histories = FaxPrintHistory.objects.filter(club_id=club_id, period_id=period_id).order_by('print_date')
            supplement_number = 0
            if histories.exists():
                supplement_number = histories.last().supplement_number + 1
                
            history = FaxPrintHistory.objects.create(
                club_id=club_id,
                period_id=period_id,
                supplement_number=supplement_number,
                printed_by=request.user if request.user.is_authenticated else None
            )
            history.bookings.set(booking_ids)
            
            from django.http import JsonResponse
            return JsonResponse({"success": True, "supplement_number": supplement_number})
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({"error": str(e)}, status=500)

class CalculatePriceApiView(APIView):
    def get(self, request):
        unit_id = request.query_params.get("unit_id")
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")
        person_type = request.query_params.get("person_type")
        is_plus_50 = request.query_params.get("is_plus_50") == "true"
        
        if not all([unit_id, start_date_str, end_date_str, person_type]):
            return Response({"total_price": 0, "error": "Missing parameters"})
            
        def flexible_parse_date(val):
            """Parse date in various common formats"""
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(val, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {val}")

        try:
            start_date = flexible_parse_date(start_date_str)
            end_date = flexible_parse_date(end_date_str)
            unit = Unit.objects.select_related("floor__building__club").get(id=unit_id)
        except Exception as e:
            return Response({"total_price": 0, "error": str(e)})

        from inventory.models import PricingRule
        from django.db.models import Q, Count

        # Find the appropriate PricingRule
        # 1. Match Club (ManyToManyField)
        rules = PricingRule.objects.filter(clubs=unit.floor.building.club)
        
        # Annotate with counts to check if M2M fields are empty
        rules = rules.annotate(
            units_count=Count('units', distinct=True),
            buildings_count=Count('buildings', distinct=True),
        )
        
        # 2. Match Unit (if rule specifies units, it must contain this unit; if empty, match all)
        rules = rules.filter(Q(units=unit.id) | Q(units_count=0))

        # 3. Match Building (if rule specifies buildings, it must contain this unit's building; if empty, match all)
        building_id = unit.floor.building.id
        rules = rules.filter(Q(buildings=building_id) | Q(buildings_count=0))
        
        # Remove duplicates from M2M joins
        rules = rules.distinct()

        month_str = str(start_date.month)

        candidate_rules = list(rules)
        
        best_rule = None
        best_score = -1

        for r in candidate_rules:
            # Check month compatibility
            if r.months:
                allowed_months = [m.strip() for m in r.months.split(',') if m.strip()]
                if allowed_months and month_str not in allowed_months:
                    continue # This rule doesn't apply to this month
            
            # Check Classification
            if r.classifications:
                allowed_cls = [c.strip() for c in r.classifications.split(',') if c.strip()]
                if allowed_cls and unit.classification not in allowed_cls:
                    continue
            
            # Check Unit Type
            if r.unit_types:
                allowed_types = [t.strip() for t in r.unit_types.split(',') if t.strip()]
                if allowed_types and unit.unit_type not in allowed_types:
                    continue
            
            # Ensure the rule actually has a price for the requested person type
            rule_price = 0
            if person_type == "MARTYR": rule_price = r.price_martyr
            elif person_type == "VETERAN": rule_price = r.price_veteran
            elif person_type in ["MILITARY", "ACTIVE_MEMBER"]: rule_price = r.price_military
            elif person_type == "FAMILY_MEMBER": rule_price = r.price_family
            elif person_type == "CIVILIAN_AF": rule_price = r.price_civilian_af
            elif person_type == "CIVILIAN_GENERAL": rule_price = r.price_civilian
            
            if not rule_price or rule_price <= 0:
                continue
            
            score = 0
            if r.units.filter(id=unit.id).exists(): score += 1000  # Unit match is strongest
            if r.buildings.filter(id=building_id).exists(): score += 100 # Building match
            if r.classifications: score += 50
            if r.unit_types: score += 50
            if r.months: score += 20 

            if score > best_score:
                best_score = score
                best_rule = r

        if not best_rule:
            return Response({"total_price": 0, "error": "لا توجد قاعدة تسعير مرتبطة بهذه الوحدة"})

        matrix = best_rule
        base_price = 0
        
        curr = start_date
        while curr < end_date:
            daily_price = 0

            if person_type == "MARTYR":
                daily_price = matrix.price_martyr
            elif person_type == "VETERAN":
                daily_price = matrix.price_veteran
            elif person_type in ["MILITARY", "ACTIVE_MEMBER"]:
                daily_price = matrix.price_military
            elif person_type == "FAMILY_MEMBER":
                daily_price = matrix.price_family
            elif person_type == "CIVILIAN_AF":
                daily_price = matrix.price_civilian_af
            elif person_type == "CIVILIAN_GENERAL":
                daily_price = matrix.price_civilian
            
            if is_plus_50 and daily_price > 0:
                import math
                daily_price = math.ceil((float(daily_price) * 1.5) / 5) * 5

            base_price += daily_price
            curr += timedelta(days=1)

        return Response({"total_price": base_price, "base_price": base_price})

@method_decorator(fax_report_access, name='dispatch')
class FaxHistoryView(View):
    def get(self, request):

        from inventory.models import Club
        
        club_id = request.GET.get('club')
        
        histories = FaxPrintHistory.objects.select_related('club', 'period', 'printed_by').order_by('-print_date')
        if club_id:
            histories = histories.filter(club_id=club_id)
            
        context = {
            'histories': histories,
            'clubs': Club.objects.all(),
            'selected_club': club_id
        }
        return render(request, 'dashboard/fax_history.html', context)
