from django.urls import path

from .views import BookingCreateView, BookingConflictView


urlpatterns = [
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/conflicts", BookingConflictView.as_view(), name="booking-conflicts"),
]
