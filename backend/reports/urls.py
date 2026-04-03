from django.urls import path

from .views import OccupancyReportView, AvailableUnitsReportView, OccupiedUnitsReportView


urlpatterns = [
    path("reports/occupancy", OccupancyReportView.as_view(), name="report-occupancy"),
    path("reports/available", AvailableUnitsReportView.as_view(), name="report-available"),
    path("reports/occupied", OccupiedUnitsReportView.as_view(), name="report-occupied"),
]
