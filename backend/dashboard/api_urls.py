from django.urls import path

from .views import WallboardApiView, UnitStatusApiView


urlpatterns = [
    path("dashboard/wallboard", WallboardApiView.as_view(), name="wallboard-api"),
    path("units/status", UnitStatusApiView.as_view(), name="units-status"),
]
