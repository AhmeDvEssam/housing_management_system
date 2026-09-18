from django.urls import path
from .views import WallboardApiView, UnitStatusApiView, UnitBookingsApiView, CalculatePriceApiView
from .analytics_views import AnalyticsDataApiView

urlpatterns = [
    path('wallboard/', WallboardApiView.as_view(), name='wallboard_api'),
    path('unit-status/', UnitStatusApiView.as_view(), name='unit_status_api'),
    path('unit-bookings/', UnitBookingsApiView.as_view(), name='unit_bookings_api'),
    path('calculate-price/', CalculatePriceApiView.as_view(), name='calculate_price_api'),
    path('analytics-data/', AnalyticsDataApiView.as_view(), name='analytics_data_api'),
]
