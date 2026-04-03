from django.urls import path

from .views import WallboardPageView


urlpatterns = [
    path("", WallboardPageView.as_view(), name="wallboard"),
]
