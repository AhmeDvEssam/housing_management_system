from django.contrib import admin
from django.urls import path, include


admin.site.site_header = "منظومة إدارة المصايف"
admin.site.site_title = "لوحة الإدارة"
admin.site.index_title = "لوحة التحكم"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("bookings.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("dashboard.api_urls")),
    path("api/", include("reports.urls")),
    path("dashboard/", include("dashboard.urls")),
]
