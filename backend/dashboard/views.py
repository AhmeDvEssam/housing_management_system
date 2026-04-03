from datetime import datetime, timedelta

from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import BookingStatus, BookingType, BookingDay
from inventory.models import Club, Building, Floor, Unit


STATUS_LABELS = {
    "AVAILABLE": "متاح",
    "OCCUPIED": "مشغول",
    "RESERVED": "محجوز",
    "LOTTERY_PENDING": "قرعة – منتظر السداد",
    "MAINTENANCE": "تحت الصيانة",
    "NOT_BOOKABLE": "غير قابل للحجز",
}


def parse_date(value: str | None) -> datetime.date:
    if not value:
        return timezone.localdate()
    try:
        return datetime.strptime(value, "%d-%m-%Y").date()
    except ValueError as exc:
        raise ValueError("صيغة التاريخ يجب أن تكون DD-MM-YYYY") from exc


def compute_unit_status(unit: Unit, booking) -> str:
    if unit.is_maintenance:
        return "MAINTENANCE"
    if not unit.is_bookable:
        return "NOT_BOOKABLE"
    if not booking:
        return "AVAILABLE"
    if booking.status == BookingStatus.CHECKED_IN:
        return "OCCUPIED"
    if booking.status == BookingStatus.CONFIRMED:
        return "RESERVED"
    if booking.status == BookingStatus.PENDING_PAYMENT:
        if booking.booking_type == BookingType.LOTTERY:
            return "LOTTERY_PENDING"
        return "RESERVED"
    return "RESERVED"


def apply_unit_filters(units_qs, request):
    club_id = request.query_params.get("club")
    building_id = request.query_params.get("building")
    floor_id = request.query_params.get("floor")
    orientation = request.query_params.get("orientation")
    capacity_min = request.query_params.get("capacity")

    if club_id:
        units_qs = units_qs.filter(floor__building__club_id=club_id)
    if building_id:
        units_qs = units_qs.filter(floor__building_id=building_id)
    if floor_id:
        units_qs = units_qs.filter(floor_id=floor_id)
    if orientation:
        units_qs = units_qs.filter(orientation=orientation)
    if capacity_min:
        try:
            capacity_value = int(capacity_min)
            units_qs = units_qs.filter(capacity__gte=capacity_value)
        except ValueError:
            return units_qs, "قيمة السعة غير صالحة"

    return units_qs, None


class WallboardPageView(APIView):
    def get(self, request):
        context = {
            "clubs": Club.objects.all().order_by("name"),
            "buildings": Building.objects.select_related("club").order_by("name"),
            "floors": Floor.objects.select_related("building").order_by("level_number"),
            "status_labels": STATUS_LABELS,
        }
        return render(request, "dashboard/wallboard.html", context)


class WallboardApiView(APIView):
    def get(self, request):
        try:
            start_date = parse_date(request.query_params.get("date"))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        days_param = request.query_params.get("days", "7")
        try:
            days = int(days_param)
        except ValueError:
            days = 7
        if days < 1:
            days = 1
        if days > 14:
            days = 14

        end_date = start_date + timedelta(days=days)
        dates = [start_date + timedelta(days=i) for i in range(days)]

        units_qs = Unit.objects.select_related(
            "floor", "floor__building", "floor__building__club"
        )
        status_filter = request.query_params.get("status")
        booking_type_filter = request.query_params.get("booking_type")

        units_qs, error = apply_unit_filters(units_qs, request)
        if error:
            return Response({"detail": error}, status=400)

        units = list(units_qs.order_by("floor__building__name", "floor__level_number", "unit_no"))
        if not units:
            return Response(
                {
                    "start_date": start_date.strftime("%d-%m-%Y"),
                    "days": days,
                    "dates": [day.strftime("%d-%m-%Y") for day in dates],
                    "units": [],
                }
            )

        booking_days = (
            BookingDay.objects.filter(unit__in=units, day__gte=start_date, day__lt=end_date)
            .select_related("booking")
            .order_by("day")
        )

        bookings_map: dict[int, dict[datetime.date, object]] = {
            unit.id: {} for unit in units
        }
        for booking_day in booking_days:
            bookings_map[booking_day.unit_id][booking_day.day] = booking_day.booking

        unit_rows = []
        for unit in units:
            day_statuses = []
            current_booking = bookings_map.get(unit.id, {}).get(start_date)
            current_status = compute_unit_status(unit, current_booking)
            current_booking_type = (
                current_booking.booking_type if current_booking else None
            )

            if status_filter and current_status != status_filter:
                continue
            if booking_type_filter:
                if not current_booking or current_booking.booking_type != booking_type_filter:
                    continue

            for day in dates:
                booking = bookings_map.get(unit.id, {}).get(day)
                status = compute_unit_status(unit, booking)
                day_statuses.append(
                    {
                        "date": day.strftime("%d-%m-%Y"),
                        "status": status,
                        "label": STATUS_LABELS[status],
                        "booking_id": booking.id if booking else None,
                        "booking_type": booking.booking_type if booking else None,
                    }
                )

            unit_rows.append(
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
                    "is_bookable": unit.is_bookable,
                    "is_maintenance": unit.is_maintenance,
                    "statuses": day_statuses,
                    "current_status": current_status,
                    "current_label": STATUS_LABELS[current_status],
                    "current_booking_type": current_booking_type,
                }
            )

        return Response(
            {
                "start_date": start_date.strftime("%d-%m-%Y"),
                "days": days,
                "dates": [day.strftime("%d-%m-%Y") for day in dates],
                "units": unit_rows,
            }
        )


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

        units = list(
            units_qs.order_by(
                "floor__building__name", "floor__level_number", "unit_no"
            )
        )
        booking_days = (
            BookingDay.objects.filter(unit__in=units, day=target_date)
            .select_related("booking")
            .order_by("day")
        )
        bookings_map = {booking_day.unit_id: booking_day.booking for booking_day in booking_days}

        unit_rows = []
        for unit in units:
            booking = bookings_map.get(unit.id)
            status = compute_unit_status(unit, booking)
            booking_type = booking.booking_type if booking else None

            if status_filter and status != status_filter:
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
                    "orientation": unit.orientation,
                    "orientation_label": unit.get_orientation_display()
                    if unit.orientation
                    else "",
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
