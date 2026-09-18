from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import WallboardPageView, VacanciesReportView, FaxReportView, CalculatePriceApiView, FaxHistoryView
from dashboard.analytics_views import AnalyticsDashboardView
from housing.apm_system import apm_endpoint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', WallboardPageView.as_view(), name='wallboard'),
    path('dashboard/vacancies/', VacanciesReportView.as_view(), name='vacancies_report'),
    path('dashboard/fax/', FaxReportView.as_view(), name='fax_report'),
    path('dashboard/fax/history/', FaxHistoryView.as_view(), name='fax_history'),
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('api/dashboard/', include('dashboard.api_urls')),
    path('api/calculate-price/', CalculatePriceApiView.as_view(), name='calculate_price_direct'),
    path('apm-endpoint/', apm_endpoint, name='apm_endpoint'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
