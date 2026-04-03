from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking, BookingDay
from inventory.models import Unit
from .utils import build_workbook, resolve_date_range, should_export_xlsx, parse_date


class OccupancyReportView(APIView):
    def get(self, request):
        start_date_value = request.query_params.get("start_date")
        end_date_value = request.query_params.get("end_date")

        try:
            start_date = parse_date(start_date_value)
            end_date = parse_date(end_date_value)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        if not start_date or not end_date:
            return Response(
                {"detail": "تاريخ البداية وتاريخ النهاية مطلوبان"}, status=400
            )

        if end_date <= start_date:
            return Response(
                {"detail": "تاريخ النهاية يجب أن يكون بعد تاريخ البداية"}, status=400
            )

        days_count = (end_date - start_date).days
        bookable_units = Unit.objects.filter(is_bookable=True, is_maintenance=False)
        total_units = bookable_units.count()
        total_unit_days = total_units * days_count

        booked_unit_days = (
            BookingDay.objects.filter(day__gte=start_date, day__lt=end_date)
            .filter(unit__in=bookable_units)
            .count()
        )

        occupancy_percent = (
            round((booked_unit_days / total_unit_days) * 100, 2)
            if total_unit_days
            else 0.0
        )

        title = "تقرير نسبة الإشغال"
        filter_text = (
            f"الفترة من {start_date.strftime('%d-%m-%Y')} إلى "
            f"{end_date.strftime('%d-%m-%Y')} (تاريخ النهاية غير شامل)"
        )

        data = {
            "title": title,
            "start_date": start_date.strftime("%d-%m-%Y"),
            "end_date": end_date.strftime("%d-%m-%Y"),
            "days_count": days_count,
            "bookable_units": total_units,
            "total_unit_days": total_unit_days,
            "booked_unit_days": booked_unit_days,
            "occupancy_percent": occupancy_percent,
            "filters": filter_text,
            "note": "تاريخ النهاية غير شامل",
        }

        if should_export_xlsx(request.query_params.get("format")):
            headers = [
                "من تاريخ",
                "إلى تاريخ",
                "عدد الأيام",
                "عدد الوحدات القابلة للحجز",
                "إجمالي أيام الوحدات القابلة للحجز",
                "أيام محجوزة",
                "نسبة الإشغال %",
            ]
            rows = [
                [
                    data["start_date"],
                    data["end_date"],
                    data["days_count"],
                    data["bookable_units"],
                    data["total_unit_days"],
                    data["booked_unit_days"],
                    data["occupancy_percent"],
                ]
            ]
            return build_workbook(
                title=title,
                filter_text=filter_text,
                headers=headers,
                rows=rows,
                sheet_name="نسبة الإشغال",
                filename="occupancy_report.xlsx",
            )

        return Response(data)


class AvailableUnitsReportView(APIView):
    def get(self, request):
        try:
            start_date, end_date = resolve_date_range(
                start_date_value=request.query_params.get("start_date"),
                end_date_value=request.query_params.get("end_date"),
                days_value=request.query_params.get("days"),
                default_days=7,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        units = Unit.objects.filter(is_bookable=True, is_maintenance=False)
        club_id = request.query_params.get("club")
        building_id = request.query_params.get("building")
        floor_id = request.query_params.get("floor")
        orientation = request.query_params.get("orientation")
        capacity_min = request.query_params.get("capacity")

        if club_id:
            units = units.filter(floor__building__club_id=club_id)
        if building_id:
            units = units.filter(floor__building_id=building_id)
        if floor_id:
            units = units.filter(floor_id=floor_id)
        if orientation:
            units = units.filter(orientation=orientation)
        if capacity_min:
            try:
                units = units.filter(capacity__gte=int(capacity_min))
            except ValueError:
                return Response({"detail": "قيمة السعة غير صالحة"}, status=400)

        busy_unit_ids = (
            BookingDay.objects.filter(day__gte=start_date, day__lt=end_date)
            .values_list("unit_id", flat=True)
            .distinct()
        )
        available_units = (
            units.exclude(id__in=busy_unit_ids)
            .select_related("floor", "floor__building", "floor__building__club")
            .order_by("floor__building__name", "floor__level_number", "unit_no")
        )

        title = "تقرير الوحدات المتاحة"
        filter_text = (
            f"الفترة من {start_date.strftime('%d-%m-%Y')} إلى "
            f"{end_date.strftime('%d-%m-%Y')} (تاريخ النهاية غير شامل)"
        )

        units_data = [
            {
                "id": unit.id,
                "unit_no": unit.unit_no,
                "unit_type": unit.unit_type,
                "unit_type_label": unit.get_unit_type_display(),
                "capacity": unit.capacity,
                "orientation": unit.orientation,
                "orientation_label": unit.get_orientation_display()
                if unit.orientation
                else "",
                "club": unit.floor.building.club.name,
                "building": unit.floor.building.name,
                "floor": unit.floor.level_number,
                "floor_label": unit.floor.label or f"دور {unit.floor.level_number}",
            }
            for unit in available_units
        ]

        data = {
            "title": title,
            "start_date": start_date.strftime("%d-%m-%Y"),
            "end_date": end_date.strftime("%d-%m-%Y"),
            "total_available": len(units_data),
            "units": units_data,
            "filters": filter_text,
            "note": "تاريخ النهاية غير شامل",
        }

        if should_export_xlsx(request.query_params.get("format")):
            headers = [
                "رقم الوحدة",
                "نوع الوحدة",
                "السعة",
                "الاتجاه",
                "النادي",
                "المبنى",
                "الدور",
            ]
            rows = [
                [
                    unit["unit_no"],
                    unit["unit_type_label"],
                    unit["capacity"],
                    unit["orientation_label"],
                    unit["club"],
                    unit["building"],
                    unit["floor_label"],
                ]
                for unit in units_data
            ]
            return build_workbook(
                title=title,
                filter_text=filter_text,
                headers=headers,
                rows=rows,
                sheet_name="الوحدات المتاحة",
                filename="available_units_report.xlsx",
            )

        return Response(data)


class OccupiedUnitsReportView(APIView):
    def get(self, request):
        try:
            start_date, end_date = resolve_date_range(
                start_date_value=request.query_params.get("start_date"),
                end_date_value=request.query_params.get("end_date"),
                days_value=request.query_params.get("days"),
                default_days=1,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        status_filter = request.query_params.get("status")
        booking_type = request.query_params.get("booking_type")

        bookings = (
            Booking.objects.filter(days__day__gte=start_date, days__day__lt=end_date)
            .select_related("member", "unit", "unit__floor", "unit__floor__building", "unit__floor__building__club")
            .annotate(
                days_count=Count(
                    "days",
                    filter=Q(days__day__gte=start_date, days__day__lt=end_date),
                    distinct=True,
                )
            )
            .distinct()
        )

        if status_filter:
            bookings = bookings.filter(status=status_filter)
        if booking_type:
            bookings = bookings.filter(booking_type=booking_type)

        title = "تقرير الوحدات المشغولة"
        filter_text = (
            f"الفترة من {start_date.strftime('%d-%m-%Y')} إلى "
            f"{end_date.strftime('%d-%m-%Y')} (تاريخ النهاية غير شامل)"
        )

        bookings_data = [
            {
                "booking_id": booking.id,
                "status": booking.status,
                "status_label": booking.get_status_display(),
                "booking_type": booking.booking_type,
                "booking_type_label": booking.get_booking_type_display(),
                "member": booking.member.full_name,
                "membership_no": booking.member.membership_no,
                "unit_no": booking.unit.unit_no,
                "building": booking.unit.floor.building.name,
                "club": booking.unit.floor.building.club.name,
                "start_date": booking.start_date.strftime("%d-%m-%Y"),
                "end_date": booking.end_date.strftime("%d-%m-%Y"),
                "days_in_range": booking.days_count,
            }
            for booking in bookings
        ]

        data = {
            "title": title,
            "start_date": start_date.strftime("%d-%m-%Y"),
            "end_date": end_date.strftime("%d-%m-%Y"),
            "total_bookings": len(bookings_data),
            "bookings": bookings_data,
            "filters": filter_text,
            "note": "تاريخ النهاية غير شامل",
        }

        if should_export_xlsx(request.query_params.get("format")):
            headers = [
                "رقم الحجز",
                "الحالة",
                "نوع الحجز",
                "اسم العضو",
                "رقم العضوية",
                "رقم الوحدة",
                "المبنى",
                "النادي",
                "من",
                "إلى",
                "عدد الأيام ضمن الفترة",
            ]
            rows = [
                [
                    booking["booking_id"],
                    booking["status_label"],
                    booking["booking_type_label"],
                    booking["member"],
                    booking["membership_no"],
                    booking["unit_no"],
                    booking["building"],
                    booking["club"],
                    booking["start_date"],
                    booking["end_date"],
                    booking["days_in_range"],
                ]
                for booking in bookings_data
            ]
            return build_workbook(
                title=title,
                filter_text=filter_text,
                headers=headers,
                rows=rows,
                sheet_name="الوحدات المشغولة",
                filename="occupied_units_report.xlsx",
            )

        return Response(data)
