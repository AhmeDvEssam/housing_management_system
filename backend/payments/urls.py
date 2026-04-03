from django.urls import path

from .views import PaymentCreateView, ContractDetailView


urlpatterns = [
    path("payments/", PaymentCreateView.as_view(), name="payment-create"),
    path("contracts/<int:pk>/", ContractDetailView.as_view(), name="contract-detail"),

]
