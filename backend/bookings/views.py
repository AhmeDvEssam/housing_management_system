from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, BookingDay
from .serializers import BookingSerializer


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                detail = exc.message_dict
            else:
                detail = {"detail": exc.messages}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BookingConflictView(APIView):
    def get(self, request):
        unit_id = request.query_params.get("unit_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        booking_id = request.query_params.get("booking_id")

        if not unit_id or not start_date or not end_date:
            return Response(
                {"detail": "الوحدة وتاريخ البداية والنهاية مطلوبة"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            unit_id_int = int(unit_id)
        except ValueError:
            return Response(
                {"detail": "معرف الوحدة غير صالح"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start = datetime.strptime(start_date, "%d-%m-%Y").date()
            end = datetime.strptime(end_date, "%d-%m-%Y").date()
        except ValueError:
            return Response(
                {"detail": "صيغة التاريخ يجب أن تكون DD-MM-YYYY"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if end <= start:
            return Response(
                {"detail": "تاريخ النهاية يجب أن يكون بعد تاريخ البداية"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        days = []
        current = start
        while current < end:
            days.append(current)
            current += timedelta(days=1)

        conflicts = BookingDay.objects.filter(unit_id=unit_id_int, day__in=days)
        if booking_id:
            conflicts = conflicts.exclude(booking_id=booking_id)

        conflict_days = list(conflicts.values_list("day", flat=True))
        conflict_days_formatted = [day.strftime("%d-%m-%Y") for day in conflict_days]

        return Response(
            {
                "unit_id": unit_id_int,
                "start_date": start_date,
                "end_date": end_date,
                "has_conflict": bool(conflict_days_formatted),
                "conflict_days": conflict_days_formatted,
            }
        )
